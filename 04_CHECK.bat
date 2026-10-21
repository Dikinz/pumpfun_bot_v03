@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run 01_INSTALL.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "app\launcher.py" check
set "CHECK_CODE=%errorlevel%"
if "%CHECK_CODE%"=="2" goto time_warning
if not "%CHECK_CODE%"=="0" goto failed
echo Technical tests and device time check PASSED.
pause
exit /b 0
:time_warning
echo Technical tests passed, but time check needs attention.
echo See app\data\time_check.txt. Keep this report before the next test.
echo No clock correction was performed. Trading tolerance is unchanged.
pause
exit /b 2
:failed
echo Technical check failed. Keep this window and copy the error text.
pause
exit /b 1
