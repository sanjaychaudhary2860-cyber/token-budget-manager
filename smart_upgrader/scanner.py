import os
import sys
import json
import importlib
from smart_upgrader.logger import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP = {
    'venv', '__pycache__', 'node_modules',
    '.git', 'backups', 'logs', 'dist',
    'smart_upgrader', 'upgrader'
}

REQUIRED_FILES = [
    'main.py', '.env', 'requirements.txt',
    'web_app.py',
    os.path.join('core', 'assistant.py'),
    os.path.join('core', 'token_tracker.py'),
    os.path.join('core', 'budget_manager.py'),
    os.path.join('database', 'db.py'),
    os.path.join('ui', 'terminal_ui.py'),
]

REQUIRED_LIBS = [
    'groq', 'rich', 'dotenv', 'tiktoken',
    'requests', 'flask', 'anthropic'
]

def scan_files() -> dict:
    log("Files scan kar raha hun...")
    result = {
        "python_files": [],
        "other_files":  [],
        "missing":      [],
        "issues":       [],
        "stats":        {}
    }

    total_files = 0
    total_lines = 0

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            path     = os.path.join(root, f)
            rel      = os.path.relpath(path, BASE_DIR)
            size     = os.path.getsize(path)
            total_files += 1

            if f.endswith('.py'):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        lines   = fh.readlines()
                        content = "".join(lines)
                    lc = len(lines)
                    total_lines += lc

                    file_issues = []

                    # Issue checks
                    if "except:" in content:
                        file_issues.append("Bare except — specify exception type")
                    if "TODO" in content or "FIXME" in content:
                        file_issues.append("TODO/FIXME found — incomplete code")
                    if lc > 300:
                        file_issues.append(f"File too large ({lc} lines) — consider splitting")
                    if "password" in content.lower() and "os.environ" not in content:
                        file_issues.append("Possible hardcoded credential")

                    result["python_files"].append({
                        "path":   rel,
                        "lines":  lc,
                        "size":   size,
                        "issues": file_issues
                    })

                    for issue in file_issues:
                        result["issues"].append({
                            "file":     rel,
                            "issue":    issue,
                            "severity": "medium"
                        })
                except Exception as e:
                    result["issues"].append({
                        "file":     rel,
                        "issue":    f"Cannot read: {str(e)}",
                        "severity": "low"
                    })
            else:
                result["other_files"].append(rel)

    # Missing files check
    for req in REQUIRED_FILES:
        full = os.path.join(BASE_DIR, req)
        if not os.path.exists(full):
            result["missing"].append(req)
            result["issues"].append({
                "file":     req,
                "issue":    "Required file missing",
                "severity": "high"
            })

    result["stats"] = {
        "total_files":  total_files,
        "python_files": len(result["python_files"]),
        "total_lines":  total_lines,
        "issues":       len(result["issues"]),
        "missing":      len(result["missing"])
    }

    log(f"Scan done: {total_files} files, {len(result['issues'])} issues")
    return result

def scan_dependencies() -> dict:
    log("Dependencies check kar raha hun...")
    missing   = []
    installed = []

    for lib in REQUIRED_LIBS:
        try:
            importlib.import_module(lib)
            installed.append(lib)
        except ImportError:
            missing.append(lib)

    # requirements.txt check
    req_path = os.path.join(BASE_DIR, "requirements.txt")
    req_libs = []
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    req_libs.append(line.split('>=')[0].split('==')[0])

    return {
        "installed": installed,
        "missing":   missing,
        "in_requirements": req_libs
    }

def scan_security() -> dict:
    log("Security check kar raha hun...")
    issues = []

    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        issues.append({
            "type":    "critical",
            "issue":   ".env file missing",
            "fix":     "Create .env with API keys"
        })
    else:
        with open(env_path, 'r') as f:
            env = f.read()
        if "GROQ_API_KEY" not in env:
            issues.append({
                "type":  "high",
                "issue": "GROQ_API_KEY missing in .env",
                "fix":   "Add GROQ_API_KEY"
            })

    gitignore = os.path.join(BASE_DIR, ".gitignore")
    if os.path.exists(gitignore):
        with open(gitignore, 'r') as f:
            gi = f.read()
        if ".env" not in gi:
            issues.append({
                "type":  "high",
                "issue": ".env not in .gitignore — API key leak risk!",
                "fix":   "Add .env to .gitignore"
            })

    return {"issues": issues}

def full_scan() -> dict:
    log("Full project scan shuru...")
    return {
        "files":    scan_files(),
        "deps":     scan_dependencies(),
        "security": scan_security()
    }