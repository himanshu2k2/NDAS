@echo off
cd /d "%~dp0\.."
echo Initializing NDAOMS on Atlas using Python 3.12...
if exist ".venv312\Scripts\python.exe" (
  ".venv312\Scripts\python.exe" "scripts\init_db.py"
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "scripts\init_db.py"
) else (
  echo No venv found. Create one first.
  pause
  exit /b 1
)
echo.
pause
