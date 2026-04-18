@echo off
title Dev Token Budget Manager

cd /d %~dp0

if not exist main.py (
    echo main.py not found!
    pause
    exit
)

if exist venv (
    call venv\Scripts\activate
) else (
    echo Warning: venv not found
)

cls
echo Starting app...
python main.py

pause
