@echo off
cd /d "%~dp0"
py launcher.py desktop
if errorlevel 1 pause
