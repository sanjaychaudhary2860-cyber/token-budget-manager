import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upgrader.logger import log, log_json
from upgrader.scanner import scan_project, check_dependencies
from upgrader.ai_engine import analyze_with_groq
from upgrader.backup_system import (
    create_backup, list_backups,
    restore_backup, get_latest_backup
)
from upgrader.approval_system import (
    ask_approval, show_suggestions_menu, ask_backup_approval
)
from upgrader.update_engine import apply_suggestion
from upgrader.version_manager import (
    get_current_version, bump_version, show_version_history
)

def run_full_upgrade():
    print("\n" + "="*55)
    print("🤖  DEV TOKEN MANAGER — AI UPGRADER SYSTEM")
    print(f"📦  Current Version: {get_current_version()}")
    print("="*55)

    # Step 1 — Scan
    print("\n📁 Step 1: Project scan kar raha hun...")
    scan = scan_project()
    deps = check_dependencies()

    print(f"  ✅ Files found   : {scan['stats']['total_files']}")
    print(f"  ✅ Python files  : {scan['stats']['python_files']}")
    print(f"  ✅ Total lines   : {scan['stats']['total_lines']}")
    print(f"  ⚠️  Issues found  : {scan['stats']['issues_found']}")

    if deps["missing"]:
        print(f"  ❌ Missing libs  : {', '.join(deps['missing'])}")
    else:
        print(f"  ✅ All libraries : Installed")

    # Step 2 — AI Analysis
    print("\n🧠 Step 2: AI analysis kar raha hun...")
    analysis = analyze_with_groq(scan)
    health   = analysis.get("overall_health", "unknown")
    score    = analysis.get("health_score", 0)

    health_icon = (
        "✅" if health == "good"
        else "⚠️" if health == "needs_attention"
        else "🔴"
    )
    print(f"  {health_icon} Health : {health.upper()}")
    print(f"  📊 Score  : {score}/100")

    suggestions = analysis.get("suggestions", [])
    print(f"  💡 Suggestions: {len(suggestions)}")

    if not suggestions:
        print("\n✅ Sab theek hai — koi update nahi chahiye!")
        return

    # Step 3 — Backup
    print("\n💾 Step 3: Backup...")
    if ask_backup_approval():
        backup_path = create_backup()
        print(f"  ✅ Backup ready: {os.path.basename(backup_path)}")
    else:
        print("  ⚠️ Backup skip kiya — risky hai!")

    # Step 4 — Show & Approve
    print("\n💡 Step 4: Suggestions review karo...")
    approved = show_suggestions_menu(suggestions)

    if not approved:
        print("\n❌ Koi suggestion approve nahi hua — exit.")
        return

    # Step 5 — Apply
    print(f"\n🔧 Step 5: {len(approved)} updates apply kar raha hun...")
    success = 0
    failed  = 0

    for s in approved:
        result = apply_suggestion(s)
        if result:
            success += 1
            print(f"  ✅ {s['title']}")
        else:
            failed += 1
            print(f"  ❌ {s['title']} — manual fix needed")

    # Step 6 — Version bump
    if success > 0:
        new_version = bump_version("patch")
        print(f"\n📦 Version updated: {new_version}")

    # Step 7 — Report
    report = {
        "version":    get_current_version(),
        "scan":       scan["stats"],
        "health":     health,
        "score":      score,
        "approved":   len(approved),
        "success":    success,
        "failed":     failed,
    }
    log_json(report, "upgrade_report")

    print("\n" + "="*55)
    print(f"✅ UPGRADE COMPLETE!")
    print(f"   Success : {success}")
    print(f"   Failed  : {failed}")
    print(f"   Version : {get_current_version()}")
    print("="*55 + "\n")

def quick_scan():
    print("\n📁 Quick Scan...")
    scan = scan_project()
    print(f"Files: {scan['stats']['total_files']}")
    print(f"Issues: {scan['stats']['issues_found']}")
    for issue in scan['issues'][:5]:
        print(f"  ⚠️  {issue['file']}: {issue['issue']}")

def rollback():
    latest = get_latest_backup()
    if not latest:
        print("❌ Koi backup nahi mila!")
        return
    if ask_approval("Rollback", f"Restore backup: {latest}"):
        restore_backup(latest)
        print("✅ Rollback complete!")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "upgrade"

    if cmd == "scan":
        quick_scan()
    elif cmd == "rollback":
        rollback()
    elif cmd == "history":
        show_version_history()
    else:
        run_full_upgrade()