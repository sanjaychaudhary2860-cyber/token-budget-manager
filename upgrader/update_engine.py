import os
import shutil
from datetime import datetime
from upgrader.logger import log
from upgrader.backup_system import create_backup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def safe_write_file(filepath: str, content: str) -> bool:
    try:
        # Pehle backup copy banao
        if os.path.exists(filepath):
            backup = filepath + ".bak"
            shutil.copy2(filepath, backup)

        # File likho
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Backup hata do
        bak = filepath + ".bak"
        if os.path.exists(bak):
            os.remove(bak)

        log(f"File updated: {os.path.relpath(filepath, BASE_DIR)}")
        return True

    except Exception as e:
        log(f"File update failed: {str(e)}", "ERROR")
        # Restore backup
        bak = filepath + ".bak"
        if os.path.exists(bak):
            shutil.copy2(bak, filepath)
            os.remove(bak)
            log("Backup restored after failure")
        return False

def fix_requirements():
    req_path = os.path.join(BASE_DIR, "requirements.txt")
    content  = """groq>=0.5.0
anthropic>=0.25.0
rich>=13.0.0
python-dotenv>=1.0.0
tiktoken>=0.6.0
requests>=2.31.0
colorama>=0.4.6
schedule>=1.2.0
flask>=3.0.0
flask-cors>=4.0.0
SpeechRecognition>=3.10.0
pyaudio>=0.2.13
"""
    return safe_write_file(req_path, content)

def create_gitignore():
    gitignore_path = os.path.join(BASE_DIR, ".gitignore")
    content = """.env
venv/
__pycache__/
*.db
*.pyc
*.bak
backups/
logs/
node_modules/
dist/
*.log
"""
    return safe_write_file(gitignore_path, content)

def apply_suggestion(suggestion: dict) -> bool:
    stype = suggestion.get("type", "")
    title = suggestion.get("title", "")

    log(f"Applying: {title}")

    if "requirements" in title.lower():
        return fix_requirements()
    elif "gitignore" in title.lower():
        return create_gitignore()
    else:
        log(f"Manual fix needed: {title}", "WARNING")
        return False