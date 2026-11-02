# Business Requirements Document (ringkas)

**Judul:** Voice of Customer Daya Auto: dari ulasan pengguna ke prioritas perbaikan
**Penulis:** (namamu)  **Versi/Tanggal:** v0.1 / (isi)

## 1. Latar belakang
Daya Auto adalah aplikasi layanan pelanggan main dealer Honda (booking servis, klaim KPB, asuransi digital, dll.).
Ulasan publik di Google Play adalah sumber umpan balik yang tersedia tanpa data internal. (Tambahkan 2–3 kalimat
konteks bisnis: persaingan layanan purnajual, retensi servis, dll. Cantumkan sumber.)

## 2. Tujuan bisnis
- (mis.) Mengidentifikasi 3–5 masalah pengalaman pengguna yang paling sering dan paling mengganggu.
- (mis.) Mengetahui apakah rilis versi tertentu berkorelasi dengan perubahan kepuasan.
- (mis.) Membandingkan pengalaman Daya Auto dengan aplikasi main dealer Honda lain.
- (mis.) Menyusun urutan prioritas perbaikan yang bisa dipakai tim produk.

## 3. Stakeholder (fiktif, sebagai persona)
| Peran | Kebutuhan |
|---|---|
| Product owner aplikasi | Prioritas perbaikan berbasis bukti |
| Tim operasional bengkel | Tahu keluhan yang berasal dari layanan offline |
| Manajemen | Ringkasan tren dan posisi dibanding pembanding |

## 4. Pertanyaan analisis
1. Topik keluhan apa yang dominan dan bagaimana tren bulanannya?
2. Apakah rating/persentase negatif berubah setelah rilis versi tertentu?
3. Di topik apa Daya Auto lebih baik/lebih buruk dari aplikasi pembanding?
4. Apa urutan prioritas perbaikan menurut frekuensi, keparahan, dan keterlibatan?

## 5. Ruang lingkup
**Termasuk:** ulasan Google Play Jan 2024 – (tanggal akhir), aplikasi: Daya Auto + (daftar pembanding).
**Tidak termasuk:** data internal, App Store iOS, media sosial, analisis kausal.

## 6. KPI & definisi
| KPI | Definisi |
|---|---|
| Rating rata-rata | rata-rata bintang per bulan (dibobot jumlah ulasan saat diagregasi) |
| % negatif | ulasan 1–2 bintang / seluruh ulasan |
| NPS-style | % positif (4–5) − % negatif (1–2) |
| Mention rate topik | ulasan menyebut topik / ulasan ber-teks |
| Share of negative | ulasan negatif yang menyebut topik / seluruh ulasan negatif ber-teks |
| Skor prioritas | 100 × (0,5·frekuensi + 0,3·keparahan + 0,2·keterlibatan), dinormalisasi min–max per aplikasi |
| Reply rate / median waktu balas | persentase ulasan yang dibalas / median jam sampai balasan |

## 7. Sumber data & kualitas
(Daftar sumber, tanggal pengambilan, jumlah ulasan per aplikasi, hasil `03_quality_checks.sql`.)

## 8. Asumsi & batasan
(Salin dan sesuaikan dari ETIKA_DAN_BATASAN.md.)

## 9. Keluaran (deliverables)
Dashboard Tableau (5 halaman), repositori GitHub, ringkasan insight 1 halaman, daftar user story prioritas.

## 10. Kriteria sukses
- Akurasi klasifikasi topik pada gold set dilaporkan (target awal: ≥ 70% akurasi, ≥ 0,65 macro-F1; sesuaikan).
- Setiap rekomendasi ditautkan ke angka di dashboard.
