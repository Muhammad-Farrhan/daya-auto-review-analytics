# Etika, privasi, dan batasan

## Etika & privasi
- Ambil **hanya data publik**; cek ketentuan layanan Google Play sebelum scraping; beri jeda antar request
  (sudah ada di skrip). Library `google-play-scraper` tidak resmi dan bisa berhenti bekerja sewaktu-waktu.
- **Nama pengguna dan foto profil tidak disimpan** (tidak ada kolomnya).
- Data pribadi di teks (email, telepon, deretan angka panjang) disamarkan di `clean.review.text_clean`.
- **Jangan memublikasikan data mentah** (teks ulasan, file `data/gold/`, `exports/review_level.csv`).
  Tableau Public memungkinkan pengunjung mengunduh data di balik workbook: publikasikan hanya data agregat
  atau matikan opsi unduh data.
- Kalau mengutip ulasan di portofolio, pilih sedikit, singkat, dan tanpa identitas.
- Data demo (`demo_*`) adalah fiktif: jangan pernah dipublikasikan atau dijadikan temuan.

## Batasan analisis (tulis juga di README/portofolio publikmu)
1. **Bias ulasan**: yang menulis ulasan cenderung paling puas atau paling kesal. Hasil tidak mewakili seluruh pengguna.
2. **Rating sebagai sentimen**: bintang adalah penilaian pengguna sendiri, tapi bisa tidak sejalan dengan isi teks
   (mis. 5 bintang dengan keluhan). Karena itu ada sentimen teks opsional dan evaluasi gold set.
3. **Topik berbasis kamus**: sederhana dan bisa dijelaskan, tapi tidak menangkap sarkasme dan bisa salah pada
   kalimat bernegasi. Akurasinya harus diukur (evaluate_labels.py), bukan diasumsikan.
4. **Dampak update = korelasi**: tanggal rilis versi tidak tersedia; dipakai proksi (ulasan ke-5 versi itu).
   Faktor lain (musim servis, gangguan server, promosi) bisa ikut memengaruhi rating.
5. **Benchmark antar wilayah**: tiap main dealer melayani wilayah berbeda dengan basis pengguna dan fitur berbeda.
   Bandingkan persentase, bukan jumlah; jangan menyimpulkan "siapa lebih baik" tanpa konteks.
6. **Rentang waktu**: ulasan lama bisa tidak mencerminkan aplikasi saat ini.
7. **Nilai RICE** (reach, impact, effort) adalah asumsi kamu, bukan data internal. Tulis asumsinya.
8. **Bahasa**: ulasan berbahasa Inggris/campuran hanya ditandai kasar (`lang_flag`) dan tidak dianalisis khusus.

## Nada penyajian
Aplikasi ini milik perusahaan yang mungkin kamu lamar. Bingkai temuan sebagai **peluang perbaikan**
berbasis bukti, bukan kritik. Tunjukkan juga apa yang sudah berjalan baik (topik positif).
