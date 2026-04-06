import os
import json
import importlib
from upgrader.logger import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {
    'venv', '__pycache__', 'node_modules',
    '.git', 'backups', 'logs', 'dist'
}

IMPORTANT_FILES = [
    'main.py', '.env', 'requirements.txt',
    'web_app.py', 'run.bat', 'start.bat'
]

def scan_project() -> dict:
    log("Project scan shuru...")

    result = {
        "base_dir":      BASE_DIR,
        "python_files":  [],
        "js_files":      [],
        "other_files":   [],
        "missing_files": [],
        "large_files":   [],
        "issues":        [],
        "stats":         {}
    }

    total_lines = 0
    total_files = 0

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, BASE_DIR)
            size     = os.path.getsize(filepath)

            if size > 500 * 1024:  # 500KB se bada
                result["large_files"].append(rel_path)

            if file.endswith('.py'):
                try:
                    with open(filepath, 'r', encoding='utf-8',
                              errors='ignore') as f:
                        lines = f.readlines()
                    line_count = len(lines)
                    total_lines += line_count
                    result["python_files"].append({
                        "path":  rel_path,
                        "lines": line_count,
                        "size":  size
                    })
                    # Issues check karo
                    content = "".join(lines)
                    if "except:" in content:
                        result["issues"].append({
                            "file":  rel_path,
                            "issue": "Bare except clause found",
                            "fix":   "Use specific exceptions"
                        })
                    if "print(" in content and rel_path != "main.py":
                        result["issues"].append({
                            "file":  rel_path,
                            "issue": "print() found — use logger instead",
                            "fix":   "Replace with log()"
                        })
                except Exception as e:
                    result["issues"].append({
                        "file":  rel_path,
                        "issue": f"Cannot read: {str(e)}",
                        "fix":   "Check file encoding"
                    })

            elif file.endswith(('.jsx', '.js')):
                result["js_files"].append(rel_path)

            else:
                result["other_files"].append(rel_path)

            total_files += 1

    # Missing important files check
    for imp_file in IMPORTANT_FILES:
        if not os.path.exists(os.path.join(BASE_DIR, imp_file)):
            result["missing_files"].append(imp_file)

    # Check .env has required keys
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
        if "GROQ_API_KEY" not in env_content:
            result["issues"].append({
                "file":  ".env",
                "issue": "GROQ_API_KEY missing",
                "fix":   "Add GROQ_API_KEY to .env"
            })
    else:
        result["issues"].append({
            "file":  ".env",
            "issue": ".env file missing",
            "fix":   "Create .env with API keys"
        })

    result["stats"] = {
        "total_files":   total_files,
        "python_files":  len(result["python_files"]),
        "js_files":      len(result["js_files"]),
        "total_lines":   total_lines,
        "issues_found":  len(result["issues"]),
        "missing_files": len(result["missing_files"])
    }

    log(f"Scan complete: {total_files} files, {len(result['issues'])} issues found")
    return result

def check_dependencies() -> dict:
    log("Dependencies check kar raha hun...")
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    required = {}
    missing  = []
    installed = []

    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg = line.split('>=')[0].split('==')[0].strip()
                    required[pkg] = line
    
    for pkg, version in required.items():
        try:
            importlib.import_module(
                pkg.replace('-', '_').replace('python_dotenv', 'dotenv')
            )
            installed.append(pkg)
        except ImportError:
            missing.append(pkg)

    return {
        "required":  list(required.keys()),
        "installed": installed,
        "missing":   missing
    }