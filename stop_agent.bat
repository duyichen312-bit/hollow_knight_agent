@echo off
chcp 65001 >nul
echo Stopping Hollow Knight AI Agent...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Administrator: Hollow Knight*" 2>nul
taskkill /F /IM python.exe 2>nul
echo AI Agent stopped successfully.
pause
