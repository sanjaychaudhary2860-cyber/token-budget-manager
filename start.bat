@echo off
title Dev Token Budget Manager

echo Starting Backend...
start cmd /k "cd /d %~dp0 && if exist venv (venv\Scripts\activate) && python web_app.py"

timeout /t 3

echo Starting Frontend...
start cmd /k "cd /d %~dp0web_frontend && npm run dev"

timeout /t 3

echo Opening Browser...
start http://localhost:5173
