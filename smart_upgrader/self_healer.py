import os
import sys
import subprocess
from smart_upgrader.logger import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_missing_library(lib: str) -> bool:
    try:
        log(f"Installing: {lib}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", lib, "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log(f"Installed: {lib}")
        return True
    except Exception as e:
        log(f"Install failed: {lib} — {e}", "ERROR")
        return False

def fix_gitignore() -> bool:
    path    = os.path.join(BASE_DIR, ".gitignore")
    content = """.env
venv/
__pycache__/
*.db
*.pyc
*.bak
backups/
logs/
node_modules/
dist/
*.log
"""
    try:
        with open(path, 'w') as f:
            f.write(content)
        log(".gitignore fixed")
        return True
    except Exception as e:
        log(f".gitignore fix failed: {e}", "ERROR")
        return False

def fix_init_files() -> int:
    fixed = 0
    for folder in ['core', 'database', 'ui', 'upgrader', 'defender']:
        init = os.path.join(BASE_DIR, folder, "__init__.py")
        if not os.path.exists(os.path.join(BASE_DIR, folder)):
            continue
        if not os.path.exists(init):
            with open(init, 'w') as f:
                f.write("")
            log(f"Created: {folder}/__init__.py")
            fixed += 1
    return fixed

def auto_heal(scan_result: dict) -> dict:
    log("Self-healing shuru kar raha hun...")
    healed = []
    failed = []

    # Fix missing libraries
    for lib in scan_result["deps"]["missing"]:
        if fix_missing_library(lib):
            healed.append(f"Installed: {lib}")
        else:
            failed.append(f"Failed: {lib}")

    # Fix __init__.py files
    count = fix_init_files()
    if count > 0:
        healed.append(f"Created {count} __init__.py files")

    # Fix security issues
    for issue in scan_result["security"]["issues"]:
        if ".gitignore" in issue["issue"]:
            if fix_gitignore():
                healed.append("Fixed: .gitignore")

    log(f"Self-heal done: {len(healed)} fixed, {len(failed)} failed")
    return {
        "healed": healed,
        "failed": failed
    }