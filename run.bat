@echo off
cd /d "%~dp0"
py launcher.py run
if errorlevel 1 pause
