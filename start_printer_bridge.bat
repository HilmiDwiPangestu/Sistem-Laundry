@echo off
setlocal
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo Virtual environment belum ditemukan.
  echo Jalankan setup_windows.bat terlebih dahulu.
  pause
  exit /b 1
)
venv\Scripts\python.exe printer_bridge.py
pause
