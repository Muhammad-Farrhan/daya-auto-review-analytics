# Business Requirements Document (ringkas)

**Judul:** Voice of Customer Daya Auto: dari ulasan pengguna ke prioritas perbaikan
**Penulis:** Muhammad Farhan  **Versi/Tanggal:** v0.1 / 3 November 2026

## 1\. Latar belakang

Daya Auto adalah aplikasi layanan pelanggan milik PT Daya Adicipta Motora, main dealer Honda untuk wilayah Jawa Barat, Sulawesi Utara, Maluku, dan Gorontalo. Lewat aplikasi ini pengguna bisa booking servis, klaim Kartu Perawatan Berkala (KPB), mengakses asuransi digital, hingga memesan suku cadang. Singkatnya, aplikasi ini adalah "wajah digital" dealer di depan pelanggan — titik pertama yang mereka sentuh sebelum datang ke bengkel, bukan sekadar pelengkap.



Masalahnya, di bisnis purnajual motor, pengalaman digital seperti ini punya dampak yang sering diremehkan. Pelanggan yang gagal booking sekali, atau tidak menerima kode OTP dua kali, cenderung tidak kembali. Mereka bukan pindah ke aplikasi lain — mereka pindah ke bengkel lain, atau lebih buruk lagi, berhenti servis di jaringan resmi. Padahal retensi servis adalah salah satu sumber pendapatan paling stabil bagi main dealer. Di sisi lain, main dealer Honda lain seperti Wahana (Wanda), Mitra Pinasthika Mulia (BromPit), juga bergerak ke arah yang sama: membangun aplikasi layanan sendiri. Artinya, pengalaman pengguna bukan lagi soal "nice to have", tapi sudah masuk wilayah kompetisi.



Masalah klasiknya: untuk tahu apa yang sebenarnya dikeluhkan pengguna, saya sebagai analis biasanya bergantung pada data internal — tiket customer service, survei kepuasan, atau log aplikasi. Ketiganya tidak tersedia untuk publik, dan sebagai kandidat dari luar perusahaan, saya tidak punya akses ke sana. Tapi ada satu sumber yang terbuka dan sering diabaikan: ulasan Google Play. Setiap hari, pengguna menulis keluhan, pujian, dan saran di sana secara spontan — tanpa diminta, tanpa filter. Mereka menulis saat paling kesal dan paling puas, dan itulah justru momen paling jujur.



Proyek ini berangkat dari sana: mengubah ulasan publik menjadi sinyal yang bisa ditindaklanjuti. Saya mengumpulkan ulasan Daya Auto dan tiga aplikasi main dealer Honda pembanding (Wanda, BromPit, Motorku X) untuk periode 2024–2026, membersihkan dan mengklasifikasikan topiknya, lalu menyusunnya menjadi dashboard yang bisa dipakai tim produk untuk memutuskan apa yang perlu diperbaiki lebih dulu. Saya juga membandingkan posisi Daya Auto terhadap pembanding, dan melihat apakah rilis versi tertentu berkorelasi dengan perubahan rating.



Yang perlu saya tegaskan sejak awal: ini bukan analisis data internal Daya, dan bukan pengganti riset pengguna yang serius. Ini adalah latihan yang saya kerjakan secara independen, memakai data yang bisa diakses siapa pun, dengan metodologi yang saya dokumentasikan terbuka — termasuk semua batasannya. Kalau hasilnya berguna, itu bonus. Kalau tidak, setidaknya saya belajar bagaimana membangun pipeline analisis dari nol, dan itu sendiri sudah jadi alasan proyek ini ada.2. Tujuan bisnis

* (mis.) Mengidentifikasi 3–5 masalah pengalaman pengguna yang paling sering dan paling mengganggu.
* (mis.) Mengetahui apakah rilis versi tertentu berkorelasi dengan perubahan kepuasan.
* (mis.) Membandingkan pengalaman Daya Auto dengan aplikasi main dealer Honda lain.
* (mis.) Menyusun urutan prioritas perbaikan yang bisa dipakai tim produk.

## 2\. Tujuan bisnis

Ada empat hal yang ingin saya jawab lewat proyek ini.

Pertama, saya ingin tahu **apa yang sebenarnya paling sering dikeluhkan pengguna** — bukan berdasarkan dugaan, tapi berdasarkan berapa kali topik itu muncul dan seberapa parah dampaknya terhadap rating. Target saya: 3–5 topik yang paling dominan, lengkap dengan angka.

Kedua, saya ingin melihat **apakah rilis versi tertentu meninggalkan jejak di rating**. Kalau ada versi yang rating-nya jatuh setelah rilis, itu sinyal awal yang berguna bagi tim produk — bukan bukti kausal, tapi cukup untuk memicu pertanyaan lebih lanjut.

Ketiga, saya ingin **menempatkan Daya Auto dalam konteks**. Sendirian, angka rating tidak berarti banyak. Tapi kalau saya bandingkan persentase keluhan Daya Auto dengan aplikasi main dealer Honda lain, barulah kelihatan mana yang perlu diperbaiki dan mana yang sudah kompetitif.

Keempat, saya ingin **mengubah semua temuan itu menjadi urutan prioritas yang bisa dieksekusi** — bukan sekadar daftar keluhan, tapi backlog yang mempertimbangkan frekuensi, keparahan, dan seberapa banyak pengguna lain ikut merasakan masalah yang sama (thumbs-up).


## 3\. Stakeholder (fiktif, sebagai persona)

|Peran|Kebutuhan|
|-|-|
|Product owner aplikasi|Prioritas perbaikan berbasis bukti|
|Tim operasional bengkel|Tahu keluhan yang berasal dari layanan offline|
|Manajemen|Ringkasan tren dan posisi dibanding pembanding|
|Tim Marketing|Memahami efektivitas promosi dalam aplikasi|

## 4\. Pertanyaan analisis

1. Topik keluhan apa yang dominan dan bagaimana tren bulanannya?
2. Apakah rating/persentase negatif berubah setelah rilis versi tertentu?
3. Di topik apa Daya Auto lebih baik/lebih buruk dari aplikasi pembanding?
4. Apa urutan prioritas perbaikan menurut frekuensi, keparahan, dan keterlibatan?

## 5\. Ruang lingkup

**Termasuk:** ulasan Google Play Januari 2024 – tanggal pengambilan data
(akan dicatat di Bagian 7), aplikasi:

- Daya Auto (aplikasi fokus)
- Wahana Honda (WANDA) — pembanding, wilayah Jakarta–Tangerang
- BromPit — pembanding, wilayah Jawa Timur & NTT
- Motorku X — pembanding, aplikasi Honda nasional (skala berbeda dengan main dealer regional)



**Tidak termasuk:** data internal, App Store iOS, media sosial, analisis kausal.

## 6\. KPI \& definisi

|KPI|Definisi|
|-|-|
|Rating rata-rata|rata-rata bintang per bulan (dibobot jumlah ulasan saat diagregasi)|
|% negatif|ulasan 1–2 bintang / seluruh ulasan|
|NPS-style|% positif (4–5) − % negatif (1–2)|
|Mention rate topik|ulasan menyebut topik / ulasan ber-teks|
|Share of negative|ulasan negatif yang menyebut topik / seluruh ulasan negatif ber-teks|
|Skor prioritas|100 × (0,5·frekuensi + 0,3·keparahan + 0,2·keterlibatan), dinormalisasi min–max per aplikasi|
|Reply rate / median waktu balas|persentase ulasan yang dibalas / median jam sampai balasan|

## 7\. Sumber data \& kualitas

(Daftar sumber, tanggal pengambilan, jumlah ulasan per aplikasi, hasil `03\_quality\_checks.sql`.)

## 8\. Asumsi \& batasan

(Salin dan sesuaikan dari ETIKA\_DAN\_BATASAN.md.)

## 9\. Keluaran (deliverables)

Dashboard Tableau (5 halaman), repositori GitHub, ringkasan insight 1 halaman, daftar user story prioritas.

## 10\. Kriteria sukses

* Akurasi klasifikasi topik pada gold set dilaporkan (target awal: ≥ 70% akurasi, ≥ 0,65 macro-F1; sesuaikan).
* Setiap rekomendasi ditautkan ke angka di dashboard.

