from database.db import get_budget, update_budget, get_monthly_usage, get_today_usage

FREE_LIMITS = {
    "gemini-1.5-flash": {
        "requests_per_day": 1500,
        "requests_per_minute": 15
    },
    "llama3-8b-8192": {
        "requests_per_day": 14400,
        "requests_per_minute": 30
    }
}

def check_budget_status() -> dict:
    monthly = get_monthly_usage()
    today = get_today_usage()

    return {
        "monthly_tokens_used": monthly["total_tokens"],
        "today_tokens_used": today["total_tokens"],
        "monthly_requests": monthly["request_count"],
        "today_requests": today["request_count"],
        "status": "ok"
    }

def get_alert_message():
    status = check_budget_status()
    today_req = status["today_requests"]

    if today_req >= 1450:
        return "🔴 ALERT: Gemini daily limit almost full! (1500/day)"
    if today_req >= 1200:
        return "🟡 WARNING: 80% Gemini daily requests used!"
    return None

def get_best_model(task_type: str = "normal") -> str:
    if task_type == "complex":
        return "llama3-70b-8192"
    return "gemini-1.5-flash"

def set_budget(monthly_usd: float, alert_threshold: float = 0.8):
    update_budget(monthly_usd, alert_threshold)
    return f"Budget set: ${monthly_usd}/month — {int(alert_threshold*100)}% alert"

def get_savings_report() -> dict:
    monthly = get_monthly_usage()
    total_used = monthly["total_tokens"]
    estimated_without = total_used * 3
    saved = estimated_without - total_used

    return {
        "tokens_used": total_used,
        "estimated_without_optimization": estimated_without,
        "tokens_saved": saved,
        "efficiency_percent": round(
            (saved / estimated_without * 100) if estimated_without > 0 else 0, 1
        )
    }