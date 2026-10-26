## v31 — Thermal Printer Bridge + Android BLE

Pembaruan ini menambahkan tiga jalur cetak tanpa menghapus jalur lama:

1. **Driver Windows / Browser** — pilihan paling kompatibel untuk printer USB atau Bluetooth yang sudah dipasangkan di Windows. Gunakan tombol Cetak biasa dan pilih printer di dialog browser.
2. **Printer Bridge Windows (ESC/POS RAW)** — layanan lokal pada komputer kasir untuk mengirim data ESC/POS langsung ke antrean Windows. Printer harus mendukung ESC/POS RAW; hasilnya berupa teks tanpa logo. Ini bukan pengganti driver untuk semua model printer.
3. **Bluetooth Android (BLE)** — integrasi Web Bluetooth untuk printer BLE yang menyediakan karakteristik GATT tulis dan menerima perintah ESC/POS. Perlu Chrome Android dan halaman HTTPS atau localhost. Bluetooth klasik/SPP tidak dapat diakses langsung oleh browser; gunakan aplikasi layanan cetak/vendor atau aplikasi Android native yang sesuai.

### Menyiapkan Printer Bridge di Windows

1. Pastikan printer USB atau Bluetooth sudah terpasang di Windows dan muncul pada **Settings → Bluetooth & devices → Printers & scanners**.
2. Jalankan `setup_windows.bat` agar dependency Windows termasuk `pywin32` terpasang.
3. Jalankan `start_printer_bridge.bat` di komputer kasir. Biarkan jendela tersebut tetap terbuka.
4. Salin token yang ditampilkan di jendela Printer Bridge.
5. Buka **Control Center → Printer Lokal Windows**, tempel token, tekan **Periksa Koneksi**, pilih printer, lalu tekan **Simpan Pengaturan Lokal**.
6. Pada halaman struk, gunakan **Cetak Langsung (Kasir)**. Jika printer tidak memahami hasilnya, gunakan **Cetak via Driver/Browser**.

Printer Bridge hanya bind ke `127.0.0.1` dan memerlukan token acak. Token disimpan di file lokal `.printer_bridge_token` dan tidak perlu dimasukkan ke repository. Jangan membagikan token. Bridge mengirim data RAW; sebagian driver raster atau printer non-ESC/POS tidak mendukung cara ini.

### Menyiapkan Bluetooth Android

1. Buka aplikasi dari Chrome Android melalui alamat HTTPS.
2. Buka halaman preview struk dan tekan **Bluetooth Android (BLE)**.
3. Pilih printer BLE pada dialog sistem. Printer harus menerima ESC/POS dan menyediakan karakteristik tulis yang kompatibel.
4. Jika printer tidak muncul, gagal tersambung, atau menggunakan Bluetooth klasik/SPP, gunakan aplikasi layanan cetak Android/vendor. Browser/PWA tidak memiliki API universal untuk Bluetooth klasik.

Mode Bluetooth BLE mengirim teks ESC/POS sederhana; logo tidak ikut tercetak. Dukungan GATT dan kode halaman karakter berbeda antar-model, jadi pengujian pada printer fisik tetap diperlukan.

---


## v30 — Landing Page Dinamis & Elegan

Landing page publik didesain ulang agar lebih modern, profesional, dan responsif tanpa menambah library frontend berat. Konten teks, harga layanan, identitas usaha, alamat, dan WhatsApp tetap dinamis dari Admin Center/database. Ditambahkan navigasi mobile, animasi ringan berbasis IntersectionObserver, kartu layanan yang lebih rapi, ringkasan harga dinamis, CTA kontak, dan floating WhatsApp.

# Sani Laundry v29 — Admin Operasional + Laporan Download + Responsive

Project Django + PostgreSQL untuk Sani Laundry dengan **3 bagian** dan **2 aktor**.

## Struktur sistem

1. **Landing Page Publik** — `/`
   - Website yang dilihat konsumen.
   - Konten, layanan, CTA, harga, identitas usaha, dan informasi kontak dikelola admin secara dinamis.

2. **Panel Karyawan** — `/karyawan/`
   - Fokus operasional: buat nota, daftar nota, pelanggan, input rincian pakaian, status, dan cetak struk.
   - **Tidak menampilkan laporan/rekap keuangan.**
   - Ringkasan pendapatan di dashboard dan daftar nota dihilangkan.

3. **Admin Center** — `/admin-panel/`
   - Dashboard sistem.
   - Landing page dinamis.
   - Pengelolaan akun karyawan.
   - Harga layanan, identitas usaha, struk, dan printer.
   - **Layanan Operasional Admin** untuk nota dan pelanggan tanpa berpindah ke panel karyawan.
   - **Laporan & Keuangan** khusus admin.
   - Download laporan bulanan atau harian dalam format CSV (langsung dapat dibuka di Excel).

## Perubahan utama v29

- Tombol/menu **Layanan Operasional** sekarang tetap berada di Admin Center.
- Admin memiliki halaman sendiri untuk:
  - Kelola Nota
  - Buat/Edit/Detail/Hapus Nota
  - Ubah status Nota
  - Kelola Pelanggan
  - Laporan & Keuangan
- Karyawan tidak lagi memiliki menu atau akses laporan keuangan.
- URL laporan versi lama otomatis diarahkan ke Admin Center dan hanya dapat dibuka admin.
- Layout Admin, Karyawan, dan Landing Page diperbarui agar responsif di desktop, tablet, Android, iPhone, iPad, dan layar kecil.
- Dukungan safe-area iPhone/iOS, touch target minimal, input 16px untuk mencegah auto-zoom Safari, dan navigasi bawah responsif.
- Tidak ada migration database baru dari v27 ke v29.

## Setup Windows

```powershell
.\setup_windows.bat
```

Pastikan `.env` berisi koneksi PostgreSQL, contoh:

```env
DJANGO_SECRET_KEY=ganti-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,.ngrok-free.dev,.ngrok-free.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.ngrok-free.dev,https://*.ngrok-free.app

DB_NAME=Laundry
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Karena versi sebelumnya sudah memiliki migration landing page, tetap aman menjalankan:

```powershell
python manage.py migrate
```

### Buat Admin

```powershell
python manage.py create_admin admin --name "Admin Sani Laundry"
```

### Buat Karyawan

Bisa dari Admin Center, atau terminal:

```powershell
python manage.py create_employee kasir1 --name "Hilmi"
```

## Menjalankan

```powershell
python manage.py runserver
```

atau:

```powershell
.\start_laundry.bat
```

Akses:

- Website: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Karyawan: `http://127.0.0.1:8000/karyawan/`
- Admin Center: `http://127.0.0.1:8000/admin-panel/`
- Operasional Admin: `http://127.0.0.1:8000/admin-panel/operasional/`
- Laporan Admin: `http://127.0.0.1:8000/admin-panel/laporan/`

## Harga awal

- Express: Rp10.000/kg
- Reguler Cuci + Setrika: Rp7.000/kg
- Reguler Cuci + Lipat: Rp6.000/kg
- Reguler Setrika Saja: Rp5.000/kg

Harga dapat diubah Admin Center dan nota lama tetap mempertahankan harga saat transaksi dibuat.

## Download laporan PDF (v29)
Admin sekarang dapat mengunduh laporan dalam format **CSV maupun PDF** dari menu **Laporan & Keuangan**. PDF tersedia untuk rekap bulanan dan detail per tanggal, memakai format A4 formal dengan identitas Sani Laundry, ringkasan total, dan tabel transaksi. Dependency baru: `reportlab==4.4.9`; jalankan `pip install -r requirements.txt` setelah update source.

## Input pakaian dengan keranjang (v32)

Di halaman detail nota, kasir sekarang dapat memilih beberapa jenis pakaian sekaligus melalui **Keranjang Pakaian**. Tombol pakaian yang sering dipakai tersedia langsung; jenis lain dapat dicari dari daftar lengkap atau dimasukkan dengan nama sendiri. Jumlah tiap jenis bisa diatur sebelum tombol **Simpan ... jenis ke nota** ditekan satu kali. Data keranjang disimpan dalam satu transaksi database, dan jenis yang sama tanpa catatan akan digabung ke baris yang sudah ada. Fitur yang sama tersedia dari detail nota di Admin Center.

### Perbaikan Printer Bridge Windows (v41)

Jika `GET /printers` menghasilkan HTTP 500 padahal `/health` merespons 200, gunakan `printer_bridge.py` versi terbaru. Daftar printer kini menangani format hasil `win32print.EnumPrinters(..., 2)` yang berupa dictionary maupun tuple. Jika masih gagal, periksa pesan `[printer-bridge] /printers failed` di jendela bridge.


## v53 - Konsistensi cetak kasir dengan driver Windows

Tombol `Cetak Langsung (Kasir · Driver Windows)` pada halaman nota dan tes struk sekarang menggunakan jalur cetak browser/driver yang sama seperti cetak via driver sebelumnya. Ini sengaja membuka dialog cetak Windows agar CSS `@media print` diterapkan secara native, sehingga hasil tidak melewati raster ESC/POS yang digunakan Bluetooth. Pilih printer RONGTA dan ukuran kertas 58 mm pada dialog cetak. Bluetooth BLE tetap merupakan jalur terpisah dan dapat memiliki perbedaan tampilan.


## v54 — Cetak bertahap per struk

Fitur cetak semua struk kini mengirim atau membuka dialog cetak satu struk pada satu waktu. Setelah setiap struk diproses, kasir diminta menyobek/memisahkan struk dan memilih OK untuk melanjutkan atau Batal untuk menghentikan. Berlaku untuk cetak browser/driver, Printer Bridge, dan Bluetooth BLE. Untuk cetak via driver, dialog browser muncul terpisah per struk; pastikan memilih printer dan mengonfirmasi dialog cetak masing-masing.
