MONITOR NOTA REAL-TIME - ADMIN CENTER

URL halaman:
  /admin-panel/monitor-nota/

API polling:
  /admin-panel/monitor-nota/data/?tanggal=YYYY-MM-DD

Fitur:
- Khusus akun admin/staff melalui decorator admin_required.
- Hanya untuk pemantauan; tidak ada aksi edit/hapus di halaman monitor.
- Memperbarui data otomatis setiap 5 detik.
- Default tanggal adalah hari ini.
- Jika hari berganti saat halaman tetap terbuka dan pengguna sedang mengikuti tanggal hari ini, tanggal otomatis berganti ke hari baru.
- Admin dapat memilih tanggal sebelumnya; data untuk tanggal pilihan tetap dipantau secara otomatis.
- Filter tanggal menggunakan field Nota.tgl yang sudah ada, jadi tidak membutuhkan migrasi database.
- Menampilkan maksimal 200 nota terbaru berdasarkan ID. Ringkasan total nota, pendapatan, status selesai/belum, berat, jenis/layanan dan jumlah item.

Catatan:
- Real-time menggunakan polling browser tiap 5 detik, bukan WebSocket.
- Data dikelompokkan berdasarkan tanggal nota (Nota.tgl), bukan waktu pembuatan timestamp, karena model Nota saat ini belum memiliki created_at.
