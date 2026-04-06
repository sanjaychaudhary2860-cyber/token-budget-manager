import os
import json
from smart_upgrader.logger import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

def analyze_with_ai(scan_result: dict) -> dict:
    try:
        from groq import Groq
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            return _local_analysis(scan_result)

        client = Groq(api_key=key)
        stats  = scan_result["files"]["stats"]
        issues = scan_result["files"]["issues"][:8]
        sec    = scan_result["security"]["issues"]
        deps   = scan_result["deps"]["missing"]

        prompt = f"""
You are a Python code review expert.
Analyze this project scan and give exactly 5 suggestions.

Stats:
- Files: {stats['total_files']}
- Lines: {stats['total_lines']}
- Issues: {stats['issues']}

Code Issues: {json.dumps(issues[:5], indent=2)}
Security Issues: {json.dumps(sec, indent=2)}
Missing Libraries: {deps}

Return ONLY this JSON format, nothing else:
{{
  "health_score": 85,
  "health_status": "good",
  "suggestions": [
    {{
      "id": 1,
      "title": "Short title",
      "description": "What and why",
      "reason": "Explain decision in simple words",
      "priority": "high",
      "type": "bug_fix",
      "risk": "low",
      "auto_apply": false
    }}
  ]
}}
"""
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.2
        )
        text = resp.choices[0].message.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        result = json.loads(text)
        log(f"AI analysis done: score={result.get('health_score',0)}")
        return result

    except Exception as e:
        log(f"AI analysis failed: {e} — local analysis use kar raha hun", "WARN")
        return _local_analysis(scan_result)

def _local_analysis(scan_result: dict) -> dict:
    suggestions = []
    score       = 100
    issues      = scan_result["files"]["issues"]
    sec_issues  = scan_result["security"]["issues"]
    missing     = scan_result["deps"]["missing"]

    # Security issues — highest priority
    for issue in sec_issues:
        score -= 15
        suggestions.append({
            "id":          len(suggestions) + 1,
            "title":       f"Security: {issue['issue'][:40]}",
            "description": issue.get("fix", "Fix this security issue"),
            "reason":      "Security issues can expose your API keys",
            "priority":    "high",
            "type":        "security",
            "risk":        "low",
            "auto_apply":  False
        })

    # Missing deps
    for lib in missing[:2]:
        score -= 10
        suggestions.append({
            "id":          len(suggestions) + 1,
            "title":       f"Install: {lib}",
            "description": f"pip install {lib}",
            "reason":      f"{lib} required but not installed",
            "priority":    "high",
            "type":        "dependency",
            "risk":        "low",
            "auto_apply":  True
        })

    # Code issues
    for issue in issues[:2]:
        score -= 5
        suggestions.append({
            "id":          len(suggestions) + 1,
            "title":       f"Fix: {issue['issue'][:40]}",
            "description": f"In {issue['file']}: {issue['issue']}",
            "reason":      "Code quality improvement",
            "priority":    "medium",
            "type":        "code_quality",
            "risk":        "medium",
            "auto_apply":  False
        })

    # Default suggestion
    if len(suggestions) < 3:
        suggestions.append({
            "id":          len(suggestions) + 1,
            "title":       "Add error logging",
            "description": "Add proper error logging throughout",
            "reason":      "Better debugging and monitoring",
            "priority":    "low",
            "type":        "improvement",
            "risk":        "low",
            "auto_apply":  False
        })

    status = (
        "good"            if score >= 80
        else "attention"  if score >= 60
        else "critical"
    )

    return {
        "health_score":  max(0, score),
        "health_status": status,
        "suggestions":   suggestions[:5]
    }

def filter_safe_suggestions(suggestions: list) -> list:
    safe = []
    for s in suggestions:
        if s.get("risk") == "low" and s.get("auto_apply"):
            safe.append(s)
    return safe