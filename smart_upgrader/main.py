import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_upgrader.logger      import log, save_report
from smart_upgrader.scanner     import full_scan
from smart_upgrader.decision_engine  import analyze_with_ai, filter_safe_suggestions
from smart_upgrader.backup_manager   import create_backup, restore_latest, list_backups, cleanup_old_backups
from smart_upgrader.self_healer      import auto_heal
from smart_upgrader.update_engine    import apply
from smart_upgrader.resource_monitor import show_resources, is_safe_to_run, install_psutil

def ask(question: str) -> bool:
    while True:
        ans = input(f"\n{question} (yes/no): ").strip().lower()
        if ans in ['yes', 'y', 'haan', 'ha']:
            return True
        elif ans in ['no', 'n', 'nahi', 'na']:
            return False
        print("Sirf 'yes' ya 'no' likho!")

def show_banner():
    print("\n" + "="*55)
    print("🤖  SMART AI UPGRADER SYSTEM")
    print("    Dev Token Budget Manager")
    print("="*55)

def run_upgrade():
    show_banner()
    install_psutil()

    # Resource check
    safe, msg = is_safe_to_run()
    show_resources()
    if not safe:
        print(f"\n⚠️  {msg}")
        if not ask("Phir bhi chalana hai?"):
            return

    # Step 1 — Scan
    print("\n📁 Step 1: Project scan kar raha hun...")
    scan = full_scan()
    s    = scan["files"]["stats"]
    print(f"   ✅ Files  : {s['total_files']}")
    print(f"   ✅ Lines  : {s['total_lines']}")
    print(f"   ⚠️  Issues : {s['issues']}")
    print(f"   🔒 Security: {len(scan['security']['issues'])} issues")
    if scan["deps"]["missing"]:
        print(f"   ❌ Missing : {', '.join(scan['deps']['missing'])}")

    # Step 2 — Auto heal
    print("\n🔧 Step 2: Self-healing...")
    heal = auto_heal(scan)
    for h in heal["healed"]:
        print(f"   ✅ {h}")
    for f in heal["failed"]:
        print(f"   ❌ {f}")

    # Step 3 — AI Analysis
    print("\n🧠 Step 3: AI analysis kar raha hun...")
    analysis = analyze_with_ai(scan)
    score    = analysis.get("health_score", 0)
    status   = analysis.get("health_status", "unknown")
    icon     = "✅" if score >= 80 else "⚠️" if score >= 60 else "🔴"
    print(f"   {icon} Health: {status.upper()} ({score}/100)")

    suggestions = analysis.get("suggestions", [])
    print(f"   💡 Suggestions: {len(suggestions)}")

    if not suggestions:
        print("\n✅ Sab theek hai!")
        save_report({"scan": s, "health": score}, "upgrade_report")
        return

    # Step 4 — Show suggestions
    print("\n💡 Step 4: Suggestions:")
    for s in suggestions:
        icon = "🔴" if s["priority"] == "high" else "🟡" if s["priority"] == "medium" else "🟢"
        print(f"\n   {icon} [{s['type'].upper()}] {s['title']}")
        print(f"      {s['description']}")
        print(f"      Reason: {s['reason']}")
        print(f"      Risk: {s['risk']}")

    # Auto-apply safe ones
    safe_ones = filter_safe_suggestions(suggestions)
    if safe_ones:
        print(f"\n✅ {len(safe_ones)} safe auto-apply suggestions hain")
        if ask("Auto-apply karna hai?"):
            for s in safe_ones:
                apply(s)

    # Step 5 — Backup
    print("\n💾 Step 5: Backup...")
    if ask("Backup banana hai?"):
        path = create_backup()
        cleanup_old_backups(keep=5)
        print(f"   ✅ Backup: {os.path.basename(path)}")

    # Step 6 — Manual suggestions
    manual = [s for s in suggestions if not s.get("auto_apply")]
    if manual:
        print(f"\n🔧 Step 6: {len(manual)} manual suggestions hain")
        for s in manual:
            icon = "🔴" if s["priority"] == "high" else "🟡"
            print(f"\n   {icon} {s['title']}")
            print(f"      {s['description']}")
            if ask("   Apply karna hai?"):
                result = apply(s)
                print(f"   {'✅ Done' if result else '❌ Manual fix needed'}")

    # Report save karo
    report = {
        "health_score": score,
        "suggestions":  len(suggestions),
        "healed":       heal["healed"],
        "scan":         scan["files"]["stats"]
    }
    save_report(report, "upgrade_report")

    print("\n" + "="*55)
    print("✅ UPGRADE COMPLETE!")
    print("="*55 + "\n")

def quick_scan():
    show_banner()
    print("\n📁 Quick Scan...")
    scan = full_scan()
    s    = scan["files"]["stats"]
    print(f"Files: {s['total_files']}")
    print(f"Lines: {s['total_lines']}")
    print(f"Issues: {s['issues']}")
    for issue in scan["files"]["issues"][:5]:
        print(f"  ⚠️  {issue['file']}: {issue['issue']}")
    for sec in scan["security"]["issues"]:
        print(f"  🔒 Security: {sec['issue']}")

def rollback():
    show_banner()
    backups = list_backups()
    if not backups:
        print("❌ Koi backup nahi mila!")
        return
    print(f"\n📦 Latest backup: {backups[0]['name']}")
    print(f"   Files: {backups[0]['files']}")
    if ask("Rollback karna hai?"):
        restore_latest()
        print("✅ Rollback complete!")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if cmd == "scan":
        quick_scan()
    elif cmd == "rollback":
        rollback()
    else:
        run_upgrade()