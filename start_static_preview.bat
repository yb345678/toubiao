@echo off
cd /d "%~dp0"
set "PORT=8099"
set "BUNDLED_PY=C:\Users\ymzbc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
echo Starting static preview at http://127.0.0.1:%PORT%
echo Keep this window open while previewing.
if exist "%BUNDLED_PY%" (
  start "" "http://127.0.0.1:%PORT%/"
  "%BUNDLED_PY%" -m http.server %PORT% --bind 127.0.0.1
) else (
  start "" "http://127.0.0.1:%PORT%/"
  python -m http.server %PORT% --bind 127.0.0.1
)
pause
