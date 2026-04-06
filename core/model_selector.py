from database.db import get_today_usage

MODELS = {
    "fast":     "llama-3.1-8b-instant",
    "smart":    "llama-3.3-70b-versatile",
    "balanced": "llama-3.1-70b-versatile",
}

DAILY_LIMIT       = 1500
SMART_MODEL_LIMIT = 500

def get_query_type(message: str) -> str:
    message_lower = message.lower()

    simple_keywords = [
        "hello", "hi", "namaste", "kya hal",
        "thanks", "shukriya", "ok", "theek hai",
        "haan", "nahi", "acha", "bye", "alvida",
        "good morning", "good night"
    ]
    if any(w in message_lower for w in simple_keywords):
        return "simple"

    math_keywords = [
        "calculate", "kitna hai", "percent",
        "sqrt", "factorial", "+", "-", "*", "/",
        "jodo", "ghatao", "multiply", "divide"
    ]
    if any(w in message_lower for w in math_keywords):
        return "math"

    coding_keywords = [
        "code", "program", "function", "class",
        "debug", "error fix", "python", "javascript",
        "algorithm", "database", "api", "implement",
        "develop", "build app", "create website"
    ]
    if any(w in message_lower for w in coding_keywords):
        return "coding"

    complex_keywords = [
        "explain in detail", "detail mein batao",
        "compare karo", "difference between",
        "analyze", "essay", "story likho",
        "translate", "summarize", "research",
        "philosophy", "theory", "why does",
        "kyun hota hai", "kaise kaam karta"
    ]
    if any(w in message_lower for w in complex_keywords):
        return "complex"

    search_keywords = [
        "news", "score", "weather", "price",
        "latest", "aaj ka", "abhi kya"
    ]
    if any(w in message_lower for w in search_keywords):
        return "search"

    return "normal"

def check_budget_for_model() -> str:
    try:
        usage         = get_today_usage()
        requests_today = usage.get("request_count", 0)
        if requests_today >= DAILY_LIMIT * 0.9:
            return "fast"
        elif requests_today >= SMART_MODEL_LIMIT:
            return "balanced"
        return "any"
    except Exception:
        return "any"

def select_model(message: str) -> dict:
    query_type    = get_query_type(message)
    budget_status = check_budget_for_model()

    if budget_status == "fast":
        return {
            "model":      MODELS["fast"],
            "reason":     "Budget limit — Fast model",
            "icon":       "⚡",
            "query_type": query_type
        }

    if query_type == "simple":
        return {
            "model":      MODELS["fast"],
            "reason":     "Simple query — Fast model",
            "icon":       "⚡",
            "query_type": query_type
        }
    elif query_type == "math":
        return {
            "model":      MODELS["fast"],
            "reason":     "Math query — Fast model",
            "icon":       "🧮",
            "query_type": query_type
        }
    elif query_type == "search":
        return {
            "model":      MODELS["fast"],
            "reason":     "Search query — Fast model",
            "icon":       "🌐",
            "query_type": query_type
        }
    elif query_type == "coding":
        if budget_status == "balanced":
            return {
                "model":      MODELS["fast"],
                "reason":     "Coding — Budget save mode",
                "icon":       "💻",
                "query_type": query_type
            }
        return {
            "model":      MODELS["smart"],
            "reason":     "Coding query — Smart model",
            "icon":       "💻",
            "query_type": query_type
        }
    elif query_type == "complex":
        if budget_status == "balanced":
            return {
                "model":      MODELS["fast"],
                "reason":     "Complex — Budget save mode",
                "icon":       "🧠",
                "query_type": query_type
            }
        return {
            "model":      MODELS["smart"],
            "reason":     "Complex query — Smart model",
            "icon":       "🧠",
            "query_type": query_type
        }

    return {
        "model":      MODELS["fast"],
        "reason":     "Normal query — Fast model",
        "icon":       "🤖",
        "query_type": query_type
    }

def get_model_info(model: str) -> str:
    models = {
        "llama-3.1-8b-instant":    "⚡ Fast Model (8B)",
        "llama-3.3-70b-versatile": "🧠 Smart Model (70B)",
        "llama-3.1-70b-versatile": "⚖️ Balanced Model (70B)",
    }
    return models.get(model, model)