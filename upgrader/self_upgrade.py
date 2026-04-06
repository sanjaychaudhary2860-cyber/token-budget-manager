import os
import sys
import subprocess
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

UPGRADE_LOG = os.path.join(BASE_DIR, "upgrade_log.json")

LATEST_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]

REQUIRED_LIBRARIES = [
    "groq", "rich", "python-dotenv",
    "tiktoken", "colorama", "requests", "schedule"
]

REQUIRED_FILES = [
    "main.py",
    ".env",
    "requirements.txt",
    os.path.join("core", "assistant.py"),
    os.path.join("core", "token_tracker.py"),
    os.path.join("core", "budget_manager.py"),
    os.path.join("core", "web_search.py"),
    os.path.join("core", "memory.py"),
    os.path.join("core", "calculator.py"),
    os.path.join("core", "model_selector.py"),
    os.path.join("database", "db.py"),
    os.path.join("ui", "terminal_ui.py"),
    os.path.join("upgrader", "self_upgrade.py"),
]

def load_upgrade_log() -> dict:
    if os.path.exists(UPGRADE_LOG):
        with open(UPGRADE_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_upgrade": None,
        "total_upgrades": 0,
        "upgrades_done": [],
        "issues_fixed": []
    }

def save_upgrade_log(log: dict):
    with open(UPGRADE_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def check_files() -> list:
    missing = []
    for f in REQUIRED_FILES:
        full = os.path.join(BASE_DIR, f)
        if not os.path.exists(full):
            missing.append(f)
    return missing

def check_libraries() -> list:
    missing = []
    for lib in REQUIRED_LIBRARIES:
        try:
            __import__(lib.replace("-", "_").replace("python_dotenv", "dotenv"))
        except ImportError:
            missing.append(lib)
    return missing

def install_missing_libs(libs: list) -> str:
    if not libs:
        return "✅ Sab libraries installed hain!"
    installed = []
    for lib in libs:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", lib],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            installed.append(lib)
        except:
            pass
    if installed:
        return f"✅ Install ho gayi: {', '.join(installed)}"
    return "⚠️ Kuch libraries install nahi ho payi!"

def check_env_keys() -> list:
    issues = []
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        issues.append("❌ GROQ_API_KEY missing hai!")
    elif len(groq_key) < 20:
        issues.append("❌ GROQ_API_KEY bahut chhoti hai!")
    else:
        issues.append("✅ GROQ_API_KEY sahi hai!")
    return issues

def check_model_update() -> str:
    assistant_path = os.path.join(BASE_DIR, "core", "assistant.py")
    selector_path = os.path.join(BASE_DIR, "core", "model_selector.py")

    old_models = ["llama3-8b-8192", "llama2-70b-4096"]
    updated = []

    for path in [assistant_path, selector_path]:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False
        for old in old_models:
            if old in content:
                content = content.replace(old, "llama-3.1-8b-instant")
                changed = True
                updated.append(old)

        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

    if updated:
        return f"✅ Models updated: {', '.join(updated)}"
    return "✅ Sab models latest hain!"

def check_performance() -> dict:
    try:
        sys.path.insert(0, BASE_DIR)
        from database.db import get_today_usage, get_monthly_usage
        today = get_today_usage()
        monthly = get_monthly_usage()
        return {
            "today_tokens": today.get("total_tokens", 0),
            "today_requests": today.get("request_count", 0),
            "monthly_tokens": monthly.get("total_tokens", 0),
            "monthly_requests": monthly.get("request_count", 0),
            "status": "good" if today.get("request_count", 0) < 1000 else "high"
        }
    except:
        return {"status": "unknown"}

def auto_fix_common_issues() -> list:
    fixes = []

    # Fix 1 — __init__.py check karo
    for folder in ["core", "database", "ui", "upgrader"]:
        init_path = os.path.join(BASE_DIR, folder, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write("")
            fixes.append(f"✅ {folder}/__init__.py banaya")

    # Fix 2 — .gitignore check karo
    gitignore_path = os.path.join(BASE_DIR, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write(".env\nvenv/\n__pycache__/\n*.db\n*.pyc\n")
        fixes.append("✅ .gitignore banaya")

    # Fix 3 — memory.json check karo
    memory_path = os.path.join(BASE_DIR, "memory.json")
    if not os.path.exists(memory_path):
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump({
                "user_name": None,
                "user_interests": [],
                "user_language": "hindi",
                "important_facts": [],
                "last_seen": None,
                "total_conversations": 0
            }, f, ensure_ascii=False, indent=2)
        fixes.append("✅ memory.json banaya")

    return fixes if fixes else ["✅ Koi issue nahi mila!"]

def run_full_upgrade():
    print("\n" + "="*50)
    print("🔄 SMART UPGRADER — CHAL RAHA HAI")
    print("="*50 + "\n")

    log = load_upgrade_log()
    upgrade_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    issues_fixed = []

    # Step 1 — Files check
    print("📁 Step 1: Files check kar raha hun...")
    missing_files = check_files()
    if missing_files:
        for f in missing_files:
            print(f"  ❌ Missing: {f}")
            issues_fixed.append(f"Missing file: {f}")
    else:
        print("  ✅ Sab files present hain!")

    # Step 2 — Libraries check
    print("\n📦 Step 2: Libraries check kar raha hun...")
    missing_libs = check_libraries()
    if missing_libs:
        print(f"  ⚠️ Missing: {missing_libs}")
        result = install_missing_libs(missing_libs)
        print(f"  {result}")
        issues_fixed.append(f"Libraries installed: {missing_libs}")
    else:
        print("  ✅ Sab libraries installed hain!")

    # Step 3 — API Keys check
    print("\n🔑 Step 3: API Keys check kar raha hun...")
    key_issues = check_env_keys()
    for issue in key_issues:
        print(f"  {issue}")

    # Step 4 — Model update
    print("\n🤖 Step 4: Models check kar raha hun...")
    model_result = check_model_update()
    print(f"  {model_result}")

    # Step 5 — Auto fixes
    print("\n🔧 Step 5: Auto fixes kar raha hun...")
    fixes = auto_fix_common_issues()
    for fix in fixes:
        print(f"  {fix}")
        if "banaya" in fix:
            issues_fixed.append(fix)

    # Step 6 — Performance check
    print("\n📊 Step 6: Performance check kar raha hun...")
    perf = check_performance()
    if perf.get("status") == "good":
        print(f"  ✅ System healthy hai!")
        print(f"  📊 Aaj: {perf.get('today_requests', 0)} requests, "
              f"{perf.get('today_tokens', 0)} tokens")
    elif perf.get("status") == "high":
        print(f"  ⚠️ Aaj bahut requests ho gayi hain!")
        print(f"  💡 Tip: Chhote queries ke liye fast model use karo")
    else:
        print("  ℹ️ Performance data nahi mila")

    # Log update karo
    log["last_upgrade"] = upgrade_time
    log["total_upgrades"] = log.get("total_upgrades", 0) + 1
    log["upgrades_done"].append(upgrade_time)
    if issues_fixed:
        log["issues_fixed"].extend(issues_fixed)
    save_upgrade_log(log)

    print("\n" + "="*50)
    print(f"✅ UPGRADE COMPLETE!")
    print(f"🕐 Time: {upgrade_time}")
    print(f"🔢 Total Upgrades Done: {log['total_upgrades']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_full_upgrade()