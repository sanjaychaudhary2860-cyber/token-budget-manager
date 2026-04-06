import os
import json
from datetime import datetime
from upgrader.logger import log

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(BASE_DIR, "version_history.json")

def load_versions() -> dict:
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_version": "1.0.0",
        "versions": []
    }

def save_versions(data: dict):
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_current_version() -> str:
    return load_versions().get("current_version", "1.0.0")

def bump_version(upgrade_type: str = "patch") -> str:
    data    = load_versions()
    current = data.get("current_version", "1.0.0")
    parts   = current.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if upgrade_type == "major":
        major += 1
        minor  = 0
        patch  = 0
    elif upgrade_type == "minor":
        minor += 1
        patch  = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    data["versions"].append({
        "version":   current,
        "upgraded_to": new_version,
        "timestamp": datetime.now().isoformat(),
    })
    data["current_version"] = new_version
    save_versions(data)

    log(f"Version bumped: {current} → {new_version}")
    return new_version

def show_version_history():
    data = load_versions()
    print(f"\n📦 Current Version: {data['current_version']}")
    print("📜 History:")
    for v in data.get("versions", [])[-5:]:
        print(f"  {v['version']} → {v['upgraded_to']}  ({v['timestamp'][:10]})")