@echo off
chcp 65001 >nul
title HK_AI_Launcher

set "PY_PATH=C:\Users\ShenCongwen\AppData\Local\Programs\Python\Python311\python.exe"

echo ======================================================
echo   Launching Hollow Knight Vision AI Agent...
echo   (This terminal will minimize to keep game clean)
echo ======================================================

cd /d "%~dp0"

powershell -Command "Start-Process '%PY_PATH%' -ArgumentList 'main.py' -WindowStyle Minimized"

exit
