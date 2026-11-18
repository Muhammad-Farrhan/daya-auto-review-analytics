# Actionable Recommendations: User Stories Prioritas

Sebagai seorang *Business Analyst*, tugas saya tidak berhenti pada menemukan masalah di dalam grafik. Saya harus menerjemahkan temuan data tersebut menjadi bahasa yang bisa dieksekusi oleh tim *developer* dan *Product Owner*. 

Menggunakan kerangka **RICE (Reach, Impact, Confidence, Effort)**, saya menyusun 5 *User Story* prioritas. *User Story* ini disusun agar setiap perbaikan memiliki tujuan yang jelas, kriteria penerimaan (*acceptance criteria*) yang terukur, dan metrik keberhasilan yang bisa dipantau kembali melalui ulasan pengguna setelah rilis.

Berikut adalah rinciannya:

---

### US-01: Menyelamatkan Pengalaman Pengguna dari Aplikasi yang Lambat
**Topik:** Performa Lambat (Performance Slow)
**Priority Rank:** 1 | **Priority Score:** 86.8 | **RICE Score:** 900

*   **Bukti Data:** Topik ini adalah "biang kerok" utama. Sebanyak 67.05% dari ulasan yang membahas topik ini bernada negatif, dengan rating rata-rata terjun bebas ke angka 2.12. Tren 90 hari terakhir menunjukkan penurunan keluhan (-81.7%), namun ini tetap menjadi masalah #1 yang paling merusak pengalaman.
*   **User Story:**
    *   **Sebagai** pengguna aplikasi Daya Auto yang ingin melakukan servis,
    *   **Saya ingin** aplikasi bisa dibuka dan diakses dalam waktu kurang dari 3 detik tanpa hambatan,
    *   **Agar** saya tidak perlu menunggu lama, tidak emosi, dan tidak beralih mencari bengkel non-resmi.
*   **Acceptance Criteria:** Waktu muat (*loading time*) aplikasi turun minimal 50% pada perangkat *entry-level* (RAM 3GB). 
*   **Metrik Keberhasilan:** Persentase ulasan negatif bertopik "Performa lambat" turun minimal 15% dalam 3 bulan setelah *update* dirilis.
*   **Asumsi/Risiko:** Memerlukan usaha (*effort*) tinggi (3 orang-bulan) karena harus membenahi arsitektur *backend* dan *caching*.
*   **RICE Detail:** Reach=1000, Impact=3, Confidence=0.9, Effort=3.

---

### US-02: Perbaikan Sistem Login & OTP (Strategi "Quick-Win")
**Topik:** Login & OTP
**Priority Rank:** 3 | **Priority Score:** 43.0 | **RICE Score:** 1,350 (Tertinggi)

*   **Bukti Data:** Meskipun peringkat keluhannya ada di bawah performa, 70.27% ulasan pada topik ini bernada negatif (rating 1.8). Ini adalah masalah "gerbang masuk". Jika pengguna gagal masuk, mereka tidak bisa menggunakan fitur apa pun.
*   **User Story:**
    *   **Sebagai** pengguna baru atau pengguna yang lupa sandi,
    *   **Saya ingin** menerima kode OTP dalam waktu kurang dari 30 detik dan bisa meminta kirim ulang dengan mudah,
    *   **Agar** saya tidak terkunci di luar aplikasi dan bisa segera menggunakan layanan Daya Auto.
*   **Acceptance Criteria:** OTP terkirim ≤ 30 detik pada ≥ 95% permintaan. Tombol "Kirim Ulang" aktif setelah 30 detik dan dibatasi maksimal 3 kali.
*   **Metrik Keberhasilan:** Ulasan negatif topik Login/OTP turun di bawah 20% dalam 1 bulan.
*   **Asumsi/Risiko:** Memiliki RICE Score tertinggi karena *Effort*-nya sangat rendah (hanya 1 orang-bulan). Ini adalah prioritas "murah" yang berdampak masif.
*   **RICE Detail:** Reach=500, Impact=3, Confidence=0.9, Effort=1.

---

### US-03: Menjinakkan "Bug" dan Aplikasi *Crash*
**Topik:** Bug, error & crash
**Priority Rank:** 2 | **Priority Score:** 64.6 | **RICE Score:** 1,080

*   **Bukti Data:** 63.27% ulasan pada topik ini adalah keluhan (rating 2.20). Tren 90 hari terakhir justru menunjukkan kenaikan keluhan sebesar 15.4%, menandakan ada *bug* baru atau regresi kode yang belum tertangani.
*   **User Story:**
    *   **Sebagai** pengguna aktif aplikasi Daya Auto,
    *   **Saya ingin** aplikasi tidak menutup sendiri (*force close*) atau menampilkan layar putih saat saya sedang menggunakannya,
    *   **Agar** saya tidak kehilangan data yang sedang saya input dan tetap percaya pada keandalan aplikasi.
*   **Acceptance Criteria:** Angka *crash rate* aplikasi di Play Console turun di bawah 1%.
*   **Metrik Keberhasilan:** Penurunan persentase ulasan negatif terkait *bug* sebesar 20% pada kuartal berikutnya.
*   **Asumsi/Risiko:** Butuh investigasi menyeluruh (2 orang-bulan) karena *bug* mungkin bersifat spesifik pada tipe perangkat tertentu.
*   **RICE Detail:** Reach=800, Impact=3, Confidence=0.9, Effort=2.

---

### US-04: Menghidupkan Kembali Fitur Pengingat Servis
**Topik:** Notifikasi & Pengingat
**Priority Rank:** 4 | **Priority Score:** 39.3 | **RICE Score:** 320

*   **Bukti Data:** 46.15% ulasan bernada negatif (rating 2.02). Pengguna merasa fitur ini tidak berfungsi sebagaimana mestinya (tidak muncul notifikasi).
*   **User Story:**
    *   **Sebagai** pemilik motor Honda yang sibuk,
    *   **Saya ingin** mendapatkan notifikasi pengingat servis berkala dan info promo secara *real-time*,
    *   **Agar** saya tidak melewatkan jadwal perawatan motor dan bisa mendapatkan harga servis yang lebih hemat.
*   **Acceptance Criteria:** Notifikasi terkirim tepat waktu sesuai jadwal servis. Pengguna dapat mengatur preferensi waktu notifikasi (misal: pagi/sore).
*   **Metrik Keberhasilan:** Peningkatan *Click-Through Rate* (CTR) notifikasi sebesar 10% dan penurunan ulasan negatif topik ini sebesar 15%.
*   **RICE Detail:** Reach=400, Impact=0.5, Confidence=0.8, Effort=0.5. *(Ini adalah Quick-Win kecil karena tim hanya perlu membenahi Cron Job).*

---

### US-05: Merapikan Tampilan (UI/UX)
**Topik:** Tampilan & Kemudahan Pakai (UI/UX)
**Priority Rank:** 5 | **Priority Score:** 33.0 | **RICE Score:** 105

*   **Bukti Data:** 28.69% ulasan bernada negatif. Pengguna merasa kebingungan dengan alur navigasi atau kesulitan menemukan fitur.
*   **User Story:**
    *   **Sebagai** pengguna yang baru pertama kali mengunduh aplikasi,
    *   **Saya ingin** antarmuka yang bersih, menu yang intuitif, dan teks yang mudah dibaca,
    *   **Agar** saya bisa menemukan fitur Booking Servis tanpa harus menebak-nebak.
*   **Acceptance Criteria:** Dilakukan perbaikan berdasarkan hasil *Usability Testing* (misal: tombol diperbesar, kontras warna diperbaiki).
*   **Metrik Keberhasilan:** Penurunan persentase ulasan negatif topik UI/UX sebesar 10% dalam 6 bulan.
*   **Asumsi/Risiko:** Butuh waktu paling lama (4 orang-bulan) karena melibatkan riset desain ulang dari awal, sehingga ditunda setelah perbaikan teknis kritis selesai.
*   **RICE Detail:** Reach=600, Impact=1, Confidence=0.7, Effort=4.

---

**Catatan Penutup:**
Daftar *backlog* ini disusun bukan hanya berdasarkan apa yang paling banyak dikeluhkan, tetapi juga mempertimbangkan seberapa besar usaha (*effort*) yang dibutuhkan tim *developer* untuk menyelesaikannya. 

Sebagai contoh, isu **Login & OTP (US-02)** tidak berada di peringkat 1 keluhan, tetapi memiliki nilai RICE tertinggi. Artinya, memperbaiki fitur ini adalah strategi **"Quick-Win"** yang paling cerdas untuk segera dilakukan, sebelum tim masuk ke perbaikan berat seperti **Performa (US-01)**.