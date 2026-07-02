@echo off
cd /d "%~dp0copilot_app"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\run.ps1"
pause
