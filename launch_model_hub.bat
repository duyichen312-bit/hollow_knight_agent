@echo off
chcp 65001 >nul
title Model_Hub_Manager

set "PY_PATH=C:\Users\ShenCongwen\AppData\Local\Programs\Python\Python311\python.exe"

cd /d "%~dp0"

start "" "%PY_PATH%" model_hub_gui.py

exit
