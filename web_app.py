import os
import sys
import logging

# Path fix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask, request, jsonify, redirect, session, send_from_directory

# Import your modules
from core.assistant import Assistant
from core.token_tracker import get_token_summary
from core.budget_manager import check_budget_status, get_savings_report
from core.chat_history import get_recent_history
from database.db import initialize_db, get_usage_history

# 🔥 STATIC CONFIG
app = Flask(__name__, static_folder='web_frontend/dist', static_url_path='')

# 🔐 SECRET KEY (SAFE)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_123")

assistant = Assistant()
initialize_db()

print("NEW VERSION RUNNING")
# =========================
# 🔐 LOGIN SYSTEM
# =========================

users = {
    "admin": "123456"
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/")
        else:
            return "❌ Invalid login"

    return '''
    <h2>🔐 Login</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect("/login")

# =========================
# 🔒 MAIN UI
# =========================

@app.route('/')
def home():
    if "user" not in session:
        return redirect("/login")

    return send_from_directory('web_frontend/dist', 'index.html')

# =========================
# 🔥 STATIC + ASSETS FIX
# =========================

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('web_frontend/dist/assets', filename)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web_frontend/dist', path)

# =========================
# 🔒 AUTH CHECK
# =========================

def check_auth():
    return "user" in session

# =========================
# 🔒 API
# =========================

@app.route('/api/chat', methods=['POST'])
def chat():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message empty!'}), 400

    result = assistant.chat(message)
    return jsonify(result)

@app.route('/api/stats')
def stats():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    summary = get_token_summary()
    status  = check_budget_status()
    savings = get_savings_report()
    history = get_usage_history(7)

    return jsonify({
        'today': summary['today'],
        'monthly': summary['monthly'],
        'status': status,
        'savings': savings,
        'history': history
    })

@app.route('/api/history')
def history():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    recent = get_recent_history(20)
    return jsonify({'history': recent})

@app.route('/api/clear', methods=['POST'])
def clear():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    result = assistant.clear_history()
    return jsonify({'message': result})

# =========================
# ▶ RUN (DEPLOY FIXED)
# =========================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # 🔥 IMPORTANT
    logger.info(f"🌐 Running on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
