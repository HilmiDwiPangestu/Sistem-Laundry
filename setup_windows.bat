@echo off
setlocal
cd /d "%~dp0"

if not exist .env (
  echo Membuat file konfigurasi .env...
  copy /Y .env.example .env >nul
  echo File .env dibuat. Jika password PostgreSQL Anda bukan "postgres", edit .env terlebih dahulu.
  echo.
)

if not exist venv\Scripts\python.exe (
  echo Membuat virtual environment...
  python -m venv venv || goto :error
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip || goto :error
python -m pip install -r requirements.txt || goto :error

echo.
echo Mengecek koneksi PostgreSQL dan menjalankan migrasi...
python manage.py migrate || goto :error

echo.
echo Setup selesai menggunakan PostgreSQL.
echo Database default: Laundry
 echo User default    : postgres
echo.
echo Buat akun admin dengan perintah:
echo   python manage.py create_admin admin --name "Admin Sani Laundry"
echo.
echo Akun karyawan dapat dibuat dari Admin Center atau dengan:
echo   python manage.py create_employee kasir1 --name "Nama Karyawan"
echo.
pause
exit /b 0

:error
echo.
echo Setup gagal. Periksa pesan error di atas.
echo Pastikan PostgreSQL aktif dan konfigurasi .env benar.
pause
exit /b 1
