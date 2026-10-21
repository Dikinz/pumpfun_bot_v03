@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run 01_INSTALL.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "app\launcher.py" settings
if errorlevel 1 goto failed
pause
exit /b 0
:failed
echo Failed. Keep this window and copy the error text.
pause
exit /b 1
