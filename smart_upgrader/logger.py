import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR  = os.path.join(BASE_DIR, "logs")

def ensure_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def log(msg: str, level: str = "INFO"):
    ensure_dir()
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry    = f"[{ts}] [{level}] {msg}"
    log_file = os.path.join(
        LOG_DIR,
        datetime.now().strftime("%Y-%m-%d") + "_smart_upgrade.log"
    )
    print(entry)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry + "\n")

def save_report(data: dict, name: str = "report"):
    ensure_dir()
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(LOG_DIR, f"{name}_{ts}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"Report saved: {path}")
    return path