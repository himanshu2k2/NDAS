@echo off
cd /d "%~dp0\.."
if not exist ".venv\Scripts\python.exe" (
  echo No venv found. Create one first: python -m venv .venv
  pause
  exit /b 1
)
cd backend
echo Starting NDAOMS backend on http://127.0.0.1:8000 ...
"..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
