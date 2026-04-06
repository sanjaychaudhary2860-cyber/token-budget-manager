import os
import shutil
import json
from datetime import datetime
from smart_upgrader.logger import log

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

SKIP = {
    'venv', '__pycache__', 'node_modules',
    '.git', 'backups', 'logs', 'dist'
}

def create_backup() -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"backup_{ts}"
    path = os.path.join(BACKUP_DIR, name)

    log(f"Backup bana raha hun: {name}")

    def ignore(d, files):
        return [f for f in files if f in SKIP]

    shutil.copytree(BASE_DIR, path, ignore=ignore)

    count = sum(
        len(files)
        for _, _, files in os.walk(path)
    )

    info = {
        "name":      name,
        "timestamp": ts,
        "path":      path,
        "files":     count
    }
    with open(os.path.join(path, "info.json"), 'w') as f:
        json.dump(info, f, indent=2)

    log(f"Backup complete: {count} files")
    return path

def list_backups() -> list:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    result = []
    for name in sorted(os.listdir(BACKUP_DIR), reverse=True):
        info_path = os.path.join(BACKUP_DIR, name, "info.json")
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                result.append(json.load(f))
    return result

def restore_latest() -> bool:
    backups = list_backups()
    if not backups:
        log("Koi backup nahi mila!", "ERROR")
        return False

    latest = backups[0]
    src    = latest["path"]
    log(f"Restore kar raha hun: {latest['name']}")

    restored = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            if f.endswith(('.py', '.env', '.json', '.txt', '.jsx', '.js', '.css')):
                src_path = os.path.join(root, f)
                rel      = os.path.relpath(src_path, src)
                dst_path = os.path.join(BASE_DIR, rel)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                restored += 1

    log(f"Restore complete: {restored} files")
    return True

def cleanup_old_backups(keep: int = 5):
    backups = list_backups()
    if len(backups) > keep:
        for old in backups[keep:]:
            try:
                shutil.rmtree(old["path"])
                log(f"Old backup deleted: {old['name']}")
            except Exception as e:
                log(f"Backup delete failed: {e}", "WARN")