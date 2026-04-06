import os
import json
from datetime import datetime

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "logs"
)

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def log(message: str, level: str = "INFO"):
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file  = os.path.join(
        LOG_DIR,
        datetime.now().strftime("%Y-%m-%d") + "_upgrade.log"
    )
    entry = f"[{timestamp}] [{level}] {message}"
    print(entry)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry + "\n")

def log_json(data: dict, filename: str = "upgrade_report"):
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath  = os.path.join(LOG_DIR, f"{filename}_{timestamp}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"Report saved: {filepath}")
    return filepath

def get_all_logs() -> list:
    ensure_log_dir()
    logs = []
    for f in sorted(os.listdir(LOG_DIR)):
        if f.endswith('.log'):
            logs.append(f)
    return logs