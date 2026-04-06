import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chat_history.json"
)

def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_message(role: str, message: str, model: str = "", tokens: int = 0):
    try:
        history = load_history()
        history.append({
            "role":      role,
            "message":   message,
            "model":     model,
            "tokens":    tokens,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date":      datetime.now().strftime("%Y-%m-%d")
        })
        if len(history) > 500:
            history = history[-500:]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_today_history() -> list:
    history = load_history()
    today   = datetime.now().strftime("%Y-%m-%d")
    return [h for h in history if h.get("date") == today]

def get_recent_history(limit: int = 20) -> list:
    history = load_history()
    return history[-limit:] if history else []

def search_history(keyword: str) -> list:
    history       = load_history()
    keyword_lower = keyword.lower()
    results = [
        h for h in history
        if keyword_lower in h.get("message", "").lower()
    ]
    return results[-10:]

def clear_history():
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return "✅ Chat history clear ho gayi!"
    except Exception:
        return "❌ History clear nahi ho saki!"

def get_history_stats() -> dict:
    history    = load_history()
    today      = datetime.now().strftime("%Y-%m-%d")
    today_msgs = [h for h in history if h.get("date") == today]
    return {
        "total_messages": len(history),
        "today_messages": len(today_msgs),
        "total_tokens":   sum(h.get("tokens", 0) for h in history),
        "today_tokens":   sum(h.get("tokens", 0) for h in today_msgs),
    }

def show_history_summary() -> str:
    stats = get_history_stats()
    lines = [
        "💾 Chat History Stats:",
        f"  📝 Total Messages : {stats['total_messages']}",
        f"  📅 Aaj Messages   : {stats['today_messages']}",
        f"  ⚡ Total Tokens   : {stats['total_tokens']}",
        f"  🔢 Aaj Tokens     : {stats['today_tokens']}",
    ]
    return "\n".join(lines)

def get_all_dates() -> list:
    history = load_history()
    dates   = sorted(set(h.get("date", "") for h in history), reverse=True)
    return [d for d in dates if d]

def get_history_by_date(date: str) -> list:
    history = load_history()
    return [h for h in history if h.get("date") == date]