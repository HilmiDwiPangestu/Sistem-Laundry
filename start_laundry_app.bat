@echo off
setlocal
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
  echo Virtual environment belum dibuat.
  echo Jalankan setup_windows.bat terlebih dahulu.
  pause
  exit /b 1
)

powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/login/' -TimeoutSec 1; exit 0 } catch { if ($_.Exception.Response) { exit 0 } else { exit 1 } }" >nul 2>&1
if errorlevel 1 (
  echo Menjalankan server Sani Laundry...
  start "Sani Laundry Server" /min "%~dp0venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
  timeout /t 2 /nobreak >nul
)

set "APP_URL=http://127.0.0.1:8000/login/redirect/"

if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
  start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app=%APP_URL% --start-maximized
  exit /b 0
)
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
  start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" --app=%APP_URL% --start-maximized
  exit /b 0
)
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app=%APP_URL% --start-maximized
  exit /b 0
)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --app=%APP_URL% --start-maximized
  exit /b 0
)

start "" %APP_URL%
exit /b 0
