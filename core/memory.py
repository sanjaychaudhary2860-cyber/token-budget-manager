import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "memory.json"
)

def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "user_name": None,
        "user_interests": [],
        "user_language": "hindi",
        "important_facts": [],
        "last_seen": None,
        "total_conversations": 0
    }

def save_memory(memory: dict):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def update_memory(user_message: str, ai_response: str):
    memory = load_memory()
    message_lower = user_message.lower()

    # Naam yaad karo
    name_triggers = [
        "mera naam", "my name is", "main hun",
        "i am", "mujhe bulao", "call me"
    ]
    for trigger in name_triggers:
        if trigger in message_lower:
            words = user_message.split()
            for i, word in enumerate(words):
                if trigger.split()[-1] in word.lower() and i + 1 < len(words):
                    memory["user_name"] = words[i + 1].strip(".,!?")
                    break

    # Interest yaad karo
    interest_triggers = [
        "mujhe pasand hai", "i like", "i love",
        "mera favorite", "my favorite", "mujhe achha lagta"
    ]
    for trigger in interest_triggers:
        if trigger in message_lower:
            words = user_message.replace(trigger, "").strip()
            if words and words not in memory["user_interests"]:
                memory["user_interests"].append(words[:50])

    # Important facts yaad karo
    fact_triggers = [
        "yaad rakho", "remember", "important",
        "mat bhulna", "note karo"
    ]
    for trigger in fact_triggers:
        if trigger in message_lower:
            fact = user_message.replace(trigger, "").strip()
            if fact and fact not in memory["important_facts"]:
                memory["important_facts"].append({
                    "fact": fact[:100],
                    "date": datetime.now().strftime("%Y-%m-%d")
                })

    # Language detect karo
    hindi_words = ["kya", "hai", "mera", "mujhe", "batao", "karo"]
    if any(w in message_lower for w in hindi_words):
        memory["user_language"] = "hindi"
    else:
        memory["user_language"] = "english"

    # Stats update karo
    memory["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    memory["total_conversations"] = memory.get("total_conversations", 0) + 1

    save_memory(memory)
    return memory

def get_memory_context() -> str:
    memory = load_memory()
    context_parts = []

    if memory.get("user_name"):
        context_parts.append(f"User ka naam: {memory['user_name']}")

    if memory.get("user_interests"):
        interests = ", ".join(memory["user_interests"][:3])
        context_parts.append(f"User ki interests: {interests}")

    if memory.get("important_facts"):
        facts = [f["fact"] for f in memory["important_facts"][-3:]]
        context_parts.append(f"Important facts: {'; '.join(facts)}")

    if memory.get("last_seen"):
        context_parts.append(f"Last seen: {memory['last_seen']}")

    if context_parts:
        return "📝 Memory:\n" + "\n".join(context_parts)
    return ""

def forget_memory():
    memory = {
        "user_name": None,
        "user_interests": [],
        "user_language": "hindi",
        "important_facts": [],
        "last_seen": None,
        "total_conversations": 0
    }
    save_memory(memory)
    return "✅ Sab bhool gaya!"

def show_memory() -> str:
    memory = load_memory()
    if not any([
        memory.get("user_name"),
        memory.get("user_interests"),
        memory.get("important_facts")
    ]):
        return "🧠 Abhi kuch yaad nahi hai!"

    lines = ["🧠 Mujhe Yeh Yaad Hai:"]

    if memory.get("user_name"):
        lines.append(f"👤 Naam: {memory['user_name']}")

    if memory.get("user_interests"):
        lines.append(f"❤️ Interests: {', '.join(memory['user_interests'][:5])}")

    if memory.get("important_facts"):
        lines.append("📌 Important Facts:")
        for fact in memory["important_facts"][-5:]:
            lines.append(f"   • {fact['fact']}")

    if memory.get("total_conversations"):
        lines.append(f"💬 Total Conversations: {memory['total_conversations']}")

    if memory.get("last_seen"):
        lines.append(f"🕐 Last Seen: {memory['last_seen']}")

    return "\n".join(lines)