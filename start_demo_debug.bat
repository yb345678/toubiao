@echo off
cd /d "%~dp0"
if not exist outputs mkdir outputs
set "BUNDLED_PY=C:\Users\ymzbc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
echo Starting local demo server. Please keep this window open.
echo URL: http://127.0.0.1:8000
echo Logs: outputs\server.log and outputs\server.err.log
echo.
if exist "%BUNDLED_PY%" (
  "%BUNDLED_PY%" -u server.py > outputs\server.log 2> outputs\server.err.log
) else (
  python -u server.py > outputs\server.log 2> outputs\server.err.log
)
echo.
echo Server exited. Error log:
type outputs\server.err.log
pause
