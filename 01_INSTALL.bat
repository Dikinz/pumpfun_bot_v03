@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" "app\launcher.py" install
if errorlevel 1 goto failed
pause
exit /b 0
:failed
echo Failed. Keep this window and copy the error text.
pause
exit /b 1
