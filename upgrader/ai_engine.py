import os
import json
from upgrader.logger import log

def load_env():
    base     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

def analyze_with_groq(scan_result: dict) -> dict:
    try:
        from groq import Groq
        groq_key = os.environ.get("GROQ_API_KEY")
        if not groq_key:
            return _manual_analysis(scan_result)

        client = Groq(api_key=groq_key)

        prompt = f"""
You are a senior Python developer analyzing this project scan:

Project Stats:
- Total Files: {scan_result['stats']['total_files']}
- Python Files: {scan_result['stats']['python_files']}
- Total Lines: {scan_result['stats']['total_lines']}
- Issues Found: {scan_result['stats']['issues_found']}

Issues Detected:
{json.dumps(scan_result['issues'][:10], indent=2)}

Missing Files:
{json.dumps(scan_result['missing_files'], indent=2)}

Give me exactly 5 improvement suggestions in this JSON format:
{{
  "suggestions": [
    {{
      "id": 1,
      "title": "Short title",
      "description": "What to improve",
      "priority": "high/medium/low",
      "type": "bug_fix/feature/performance/security",
      "safe_to_auto_apply": true/false
    }}
  ],
  "overall_health": "good/needs_attention/critical",
  "health_score": 85
}}

Return ONLY valid JSON, nothing else.
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )

        text = response.choices[0].message.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        result = json.loads(text)
        log(f"AI analysis complete: {len(result.get('suggestions', []))} suggestions")
        return result

    except Exception as e:
        log(f"AI analysis failed: {str(e)} — using manual analysis", "WARNING")
        return _manual_analysis(scan_result)

def _manual_analysis(scan_result: dict) -> dict:
    suggestions = []
    score       = 100

    # Issues ke basis pe suggestions
    for issue in scan_result.get("issues", [])[:5]:
        suggestions.append({
            "id":               len(suggestions) + 1,
            "title":            f"Fix: {issue['issue']}",
            "description":      issue.get("fix", "Fix this issue"),
            "priority":         "medium",
            "type":             "bug_fix",
            "safe_to_auto_apply": False,
            "file":             issue.get("file", "")
        })
        score -= 5

    # Missing files
    for f in scan_result.get("missing_files", []):
        suggestions.append({
            "id":               len(suggestions) + 1,
            "title":            f"Missing: {f}",
            "description":      f"Create {f} file",
            "priority":         "high",
            "type":             "bug_fix",
            "safe_to_auto_apply": False
        })
        score -= 10

    # Performance suggestions
    suggestions.append({
        "id":               len(suggestions) + 1,
        "title":            "Add response caching",
        "description":      "Cache repeated API responses to save tokens",
        "priority":         "medium",
        "type":             "performance",
        "safe_to_auto_apply": False
    })

    health = (
        "good" if score >= 80
        else "needs_attention" if score >= 60
        else "critical"
    )

    return {
        "suggestions":    suggestions[:5],
        "overall_health": health,
        "health_score":   max(0, score)
    }