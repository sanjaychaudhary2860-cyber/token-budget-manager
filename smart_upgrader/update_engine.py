import os
import shutil
import subprocess
import sys
from smart_upgrader.logger import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def safe_write(path: str, content: str) -> bool:
    try:
        # Backup copy
        if os.path.exists(path):
            shutil.copy2(path, path + ".bak")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        # Remove backup
        bak = path + ".bak"
        if os.path.exists(bak):
            os.remove(bak)
        log(f"Updated: {os.path.relpath(path, BASE_DIR)}")
        return True
    except Exception as e:
        # Restore backup on failure
        bak = path + ".bak"
        if os.path.exists(bak):
            shutil.copy2(bak, path)
            os.remove(bak)
        log(f"Update failed: {e}", "ERROR")
        return False

def install_lib(lib: str) -> bool:
    try:
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

def apply(suggestion: dict) -> bool:
    stype = suggestion.get("type", "")
    title = suggestion.get("title", "")
    log(f"Applying: {title}")

    if stype == "dependency":
        lib = title.replace("Install: ", "").strip()
        return install_lib(lib)

    elif stype == "security":
        if "gitignore" in title.lower():
            path = os.path.join(BASE_DIR, ".gitignore")
            return safe_write(path, ".env\nvenv/\n__pycache__/\n*.db\n*.pyc\n")

    log(f"Manual fix needed: {title}", "WARN")
    return False