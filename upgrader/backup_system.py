import os
import shutil
import json
from datetime import datetime
from upgrader.logger import log

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

SKIP_DIRS = {
    'venv', '__pycache__', 'node_modules',
    '.git', 'backups', 'logs', 'dist'
}

def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup() -> str:
    ensure_backup_dir()
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    log(f"Creating backup: {backup_name}")

    def ignore_dirs(dir, files):
        return [f for f in files if f in SKIP_DIRS]

    shutil.copytree(
        BASE_DIR,
        backup_path,
        ignore=ignore_dirs
    )

    # Backup info save karo
    info = {
        "backup_name": backup_name,
        "timestamp":   timestamp,
        "backup_path": backup_path,
        "files_backed_up": count_files(backup_path)
    }
    info_path = os.path.join(backup_path, "backup_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)

    log(f"Backup complete: {info['files_backed_up']} files saved")
    return backup_path

def count_files(path: str) -> int:
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        total  += len(files)
    return total

def restore_backup(backup_name: str) -> bool:
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        log(f"Backup not found: {backup_name}", "ERROR")
        return False

    log(f"Restoring backup: {backup_name}")

    # Python files restore karo
    for root, dirs, files in os.walk(backup_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for file in files:
            if file.endswith(('.py', '.env', '.json', '.txt', '.jsx', '.js')):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, backup_path)
                dst_path = os.path.join(BASE_DIR, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)

    log("Restore complete!")
    return True

def list_backups() -> list:
    ensure_backup_dir()
    backups = []
    for name in sorted(os.listdir(BACKUP_DIR), reverse=True):
        path = os.path.join(BACKUP_DIR, name)
        if os.path.isdir(path):
            info_file = os.path.join(path, "backup_info.json")
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    info = json.load(f)
                backups.append(info)
    return backups

def get_latest_backup() -> str:
    backups = list_backups()
    if backups:
        return backups[0]["backup_name"]
    return ""