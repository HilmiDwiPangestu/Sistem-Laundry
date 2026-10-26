@echo off
cd /d "%~dp0"
if exist venv\Scripts\python.exe (
  venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
) else (
  echo Virtual environment belum dibuat. Jalankan setup_windows.bat terlebih dahulu.
)
pause
