@echo off
cd /d "%~dp0"
set "PORT=8001"
set "BUNDLED_PY=C:\Users\ymzbc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
echo Starting local demo server on http://127.0.0.1:8001
echo Please keep this window open.
echo.
if exist "%BUNDLED_PY%" (
  "%BUNDLED_PY%" -u server.py
) else (
  python -u server.py
)
pause
