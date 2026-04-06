import os
from core.model_selector import select_model
from core.calculator import is_math_query, extract_and_calculate
from core.memory import update_memory, get_memory_context, show_memory, forget_memory
from core.chat_history import save_message
from groq import Groq
import anthropic
from core.token_tracker import track_request, compress_context, optimize_prompt
from core.budget_manager import check_budget_status, get_alert_message
from core.web_search import search_web, should_search

def load_env():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

groq_key      = os.environ.get("GROQ_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

GROQ_SYSTEM = (
    "You are an intelligent, friendly AI assistant. "
    "STRICT RULES: "
    "1. CALCULATOR: give ONLY answer in 1 line. Example: 25*4=100. "
    "2. NEWS/CURRENT EVENTS: ONLY use data from [Web Search Result]. "
    "   If no web data, say: Mujhe abhi real data nahi mila. "
    "   NEVER make up news, scores, prices or current events. "
    "3. Normal questions — answer freely and naturally. "
    "4. Always respond in SAME language as user. "
    "5. Hindi ke liye seedha Hindi mein likho. "
    "6. English ke liye seedha English mein likho. "
    "7. Write naturally like a human — clear and readable. "
    "8. Be warm and friendly. "
    "9. Remember user details from memory."
)

CLAUDE_SYSTEM = (
    "You are an intelligent AI assistant. "
    "Give detailed, helpful, accurate answers. "
    "For coding — write clean, working code with explanations. "
    "Always respond in same language as user. "
    "Be warm, friendly and thorough. "
    "Write naturally — clear and readable always."
)

class Assistant:
    def __init__(self):
        self.conversation_history = []
        self.use_groq    = bool(groq_key)
        self.use_claude  = bool(anthropic_key)
        self.current_model = "llama-3.1-8b-instant"

        if self.use_groq:
            self.groq_client = Groq(api_key=groq_key)
        if self.use_claude:
            self.claude_client = anthropic.Anthropic(
                api_key=anthropic_key
            )

    def _should_use_claude(self, query_type: str) -> bool:
        claude_tasks = ["coding", "complex"]
        return self.use_claude and query_type in claude_tasks

    def chat(self, user_message: str) -> dict:
        optimized = optimize_prompt(user_message)

        # Smart model select
        model_info         = select_model(user_message)
        self.current_model = model_info["model"]
        query_type         = model_info.get("query_type", "normal")
        use_claude         = self._should_use_claude(query_type)

        # Web search — sources bhi lo
        web_sources = []
        if should_search(user_message):
            web_data = search_web(user_message)
            if web_data.get("text") and "❌" not in web_data["text"]:
                optimized = (
                    f"{optimized}\n\n"
                    f"[Web Search Result:\n{web_data['text']}]"
                )
                web_sources = web_data.get("sources", [])

        # Calculator
        if is_math_query(user_message):
            calc_result = extract_and_calculate(user_message)
            if calc_result and "❌" not in calc_result:
                optimized = (
                    f"{optimized}\n\n"
                    f"[Calculator Result: {calc_result}]"
                )

        # Memory
        memory_context = get_memory_context()
        if memory_context:
            optimized = f"{memory_context}\n\nUser: {optimized}"

        self.conversation_history.append({
            "role":    "user",
            "content": optimized
        })

        compressed = compress_context(
            self.conversation_history, max_tokens=1500
        )

        response_text = None
        model_used    = None

        # Claude ya Groq
        if use_claude:
            response_text, model_used = self._claude_chat(compressed)

        if response_text is None and self.use_groq:
            response_text, model_used = self._groq_chat(compressed)

        if response_text is None:
            response_text = (
                "❌ Koi API kaam nahi kar rahi. "
                ".env file mein keys check karo."
            )
            model_used = "none"

        self.conversation_history.append({
            "role":    "assistant",
            "content": response_text
        })

        update_memory(user_message, response_text)

        full_prompt = " ".join([m["content"] for m in compressed])
        stats = track_request(model_used, full_prompt, response_text)
        alert = get_alert_message()

        save_message("user", user_message)
        save_message(
            "assistant",
            response_text,
            model=model_used,
            tokens=stats.get("total_tokens", 0)
        )

        return {
            "response": response_text,
            "model":    model_used,
            "stats":    stats,
            "alert":    alert,
            "sources":  web_sources
        }

    def _claude_chat(self, messages: list):
        try:
            claude_messages = []
            for msg in messages:
                if msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role":    msg["role"],
                        "content": msg["content"]
                    })

            if not claude_messages:
                return None, None

            response = self.claude_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=CLAUDE_SYSTEM,
                messages=claude_messages
            )
            return response.content[0].text, "claude-sonnet-4-6"

        except Exception:
            return None, None

    def _groq_chat(self, messages: list):
        try:
            all_messages = [
                {"role": "system", "content": GROQ_SYSTEM}
            ] + messages

            response = self.groq_client.chat.completions.create(
                model=self.current_model,
                messages=all_messages,
                max_tokens=800,
                temperature=0.5,
                top_p=0.9,
            )
            return (
                response.choices[0].message.content,
                self.current_model
            )

        except Exception:
            try:
                all_messages_fallback = [
                    {"role": "system", "content": GROQ_SYSTEM}
                ] + messages

                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=all_messages_fallback,
                    max_tokens=800,
                    temperature=0.5,
                    top_p=0.9,
                )
                return (
                    response.choices[0].message.content,
                    "llama-3.1-8b-instant"
                )
            except Exception as e2:
                return f"❌ Groq Error: {str(e2)}", "error"

    def clear_history(self):
        self.conversation_history = []
        return "✅ History clear — tokens bachaye!"

    def get_status(self):
        return check_budget_status()

    def show_memory(self):
        return show_memory()

    def forget_memory(self):
        return forget_memory()