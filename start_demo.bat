@echo off
cd /d "%~dp0"
echo Starting AI bidding multi-agent demo...
echo URL: http://127.0.0.1:8000
echo Please keep this window open.
echo.
set "BUNDLED_PY=C:\Users\ymzbc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%BUNDLED_PY%" (
  "%BUNDLED_PY%" -u server.py
) else (
  python -u server.py
  if errorlevel 1 (
    echo.
    echo System python not found. Trying py...
    py -u server.py
  )
)
pause
