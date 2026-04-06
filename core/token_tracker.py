import tiktoken
from database.db import log_usage, get_today_usage, get_monthly_usage

def count_tokens(text: str) -> int:
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(str(text)))
    except Exception:
        return len(str(text)) // 4

def track_request(model: str, prompt: str, response: str) -> dict:
    input_tokens = count_tokens(prompt)
    output_tokens = count_tokens(response)
    total_tokens = input_tokens + output_tokens

    log_usage(model, input_tokens, output_tokens, prompt)

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }

def get_token_summary() -> dict:
    return {
        "today": get_today_usage(),
        "monthly": get_monthly_usage()
    }

def compress_context(messages: list, max_tokens: int = 2000) -> list:
    if not messages:
        return messages

    total = sum(count_tokens(m.get("content", "")) for m in messages)

    if total <= max_tokens:
        return messages

    compressed = []

    if messages and messages[0].get("role") == "system":
        compressed.append(messages[0])
        messages = messages[1:]

    compressed.extend(messages[-4:])
    return compressed

def optimize_prompt(prompt: str) -> str:
    return " ".join(prompt.split())