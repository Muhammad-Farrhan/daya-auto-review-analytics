# Template user story untuk prioritas perbaikan

Tulis 5 user story untuk 5 topik dengan skor prioritas tertinggi (`exports/priority_topic.csv`).

```
ID        : US-01
Topik     : login_otp            Peringkat prioritas: 1   Skor: (isi)
Bukti     : (mis.) 23% ulasan negatif menyebut topik ini; rata-rata rating 1,8; tren 90 hari terakhir +12%
Sebagai   : pengguna Daya Auto yang ingin booking servis
Saya ingin: menerima kode OTP dalam waktu singkat dan punya opsi kirim ulang
Agar      : bisa login tanpa mengulang berkali-kali
Acceptance criteria:
  1. OTP terkirim ≤ 30 detik pada ≥ 95% permintaan (ukur dari log; target = asumsi)
  2. Tombol "kirim ulang" aktif setelah 30 detik, maksimal 3 kali
  3. Pesan error menjelaskan penyebab (nomor salah / batas kirim / gangguan) dan langkah berikutnya
Metrik keberhasilan: % ulasan negatif bertopik login_otp turun ≥ X poin dalam 90 hari setelah rilis
Asumsi/Risiko: (mis.) penyebab bisa di penyedia SMS, bukan di aplikasi
RICE: reach=(isi) impact=(0.25|0.5|1|2|3) confidence=(0..1) effort=(orang-bulan, ASUMSI)
```

Tips: satu story = satu hasil yang bisa diuji; hindari menulis solusi teknis kecuali memang dibutuhkan;
selalu cantumkan metrik yang bisa dipantau lagi lewat ulasan setelah rilis.
