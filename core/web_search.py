import requests
import xml.etree.ElementTree as ET

def get_news() -> dict:
    try:
        url      = "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi"
        response = requests.get(url, timeout=8)
        root     = ET.fromstring(response.content)
        results  = []
        sources  = []
        items    = root.findall('.//item')[:5]

        for item in items:
            title = item.find('title')
            link  = item.find('link')
            if title is not None and title.text:
                clean = title.text.split(' - ')[0]
                results.append(f"🔹 {clean}")
                if link is not None and link.text:
                    sources.append({
                        "title": clean[:50],
                        "url":   link.text,
                        "site":  "Google News"
                    })

        if results:
            return {
                "text":    "📰 Aaj Ki Khabar:\n" + "\n".join(results),
                "sources": sources
            }
        return {"text": "", "sources": []}

    except Exception:
        return {"text": "", "sources": []}

def get_cricket_score_api() -> dict:
    try:
        url = (
            "https://news.google.com/rss/search"
            "?q=cricket+score+today&hl=hi&gl=IN&ceid=IN:hi"
        )
        response = requests.get(url, timeout=8)
        root     = ET.fromstring(response.content)
        results  = []
        sources  = []
        items    = root.findall('.//item')[:4]

        for item in items:
            title = item.find('title')
            link  = item.find('link')
            if title is not None and title.text:
                clean = title.text.split(' - ')[0]
                results.append(f"🏏 {clean}")
                if link is not None and link.text:
                    sources.append({
                        "title": clean[:50],
                        "url":   link.text,
                        "site":  "Google News"
                    })

        if results:
            return {
                "text":    "🏏 Cricket News:\n" + "\n".join(results),
                "sources": sources
            }
        return {"text": "", "sources": []}

    except Exception:
        return {"text": "", "sources": []}

def get_wikipedia(query: str) -> dict:
    try:
        clean_query = query.replace(" ", "_")
        url         = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + clean_query
        )
        response = requests.get(url, timeout=8)
        data     = response.json()

        if data.get("extract"):
            page_url = (
                data.get("content_urls", {})
                    .get("desktop", {})
                    .get("page", "")
            )
            return {
                "text": "📖 " + data["extract"][:300],
                "sources": [{
                    "title": data.get("title", query),
                    "url":   page_url or
                             f"https://en.wikipedia.org/wiki/{clean_query}",
                    "site":  "Wikipedia"
                }]
            }
        return {"text": "", "sources": []}

    except Exception:
        return {"text": "", "sources": []}

def search_web(query: str) -> dict:
    query_lower = query.lower()

    cricket_words = [
        "cricket", "score", "match", "ipl",
        "test", "odi", "t20", "runs", "wicket"
    ]
    if any(w in query_lower for w in cricket_words):
        result = get_cricket_score_api()
        if result["text"]:
            return result

    news_words = [
        "news", "khabar", "aaj", "today",
        "latest", "abhi", "current", "kal"
    ]
    if any(w in query_lower for w in news_words):
        result = get_news()
        if result["text"]:
            return result

    result = get_wikipedia(query)
    if result["text"]:
        return result

    return {"text": "", "sources": []}

def should_search(message: str) -> bool:
    search_keywords = [
        "kya hai", "what is", "batao", "tell me",
        "news", "khabar", "today", "aaj", "latest",
        "abhi", "price", "weather", "mausam",
        "who is", "kaun hai", "kahan hai", "where is",
        "search", "find", "current", "2026", "live",
        "score", "cricket", "match", "ipl", "kal",
        "hua tha", "kaun sa", "kya hua", "result",
        "winner", "t20", "odi", "test match"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in search_keywords)