# Panduan langkah demi langkah (±6 minggu)

Setiap fase punya **Hasil (Definition of Done)**. Jangan lanjut sebelum hasilnya ada.

## Fase 0 — Persiapan (hari 1–2)
**Pasang:** Python 3.11+, Git, VS Code, DBeaver, Tableau Public Desktop (gratis), dan Docker Desktop
*atau* PostgreSQL 16 biasa. Buat akun GitHub.

1. Buat repositori GitHub baru `daya-voc`, salin isi proyek ini ke dalamnya (`git init`, `git add .`, `git commit`).
2. Salin `docs/BRD_template.md` → isi bagian 1–6 (latar belakang, tujuan, pertanyaan, ruang lingkup, KPI).
3. Jalankan tes: `python -m unittest discover -s tests -v` (harus semua OK).

**Hasil:** repo dengan commit pertama, BRD draf v0.1.

## Fase 1 — Inventaris aplikasi & audit fitur (hari 2–4)
1. Di Google Play (browser), cari: **Daya Auto**, **Wanda (Wahana Honda)**, **BromPit**, dan **Motorku X**.
   Aplikasi main dealer Honda lain yang kamu temukan boleh ditambahkan. Aplikasi yang tidak ada di Play Store (mis. HSO) dilewati.
2. Untuk tiap aplikasi catat: **package ID** (di URL, `...details?id=XXXX`), jumlah install, jumlah ulasan, skor, tanggal update terakhir.
   Isi `package_id` di `data/apps.csv`. Jangan menebak package ID; salin dari URL.
3. **Cek volume ulasan.** Target ≥ ~500 ulasan ber-teks per aplikasi untuk Jan 2024–sekarang. Jika Daya Auto kurang,
   pertimbangkan memperpanjang periode ke 2023 (ubah `--since`) atau menambah aplikasi pembanding.
4. **Audit fitur:** install tiap aplikasi, buka menu-menunya, lalu isi `data/feature_audit.csv`
   (`available` = true/false, `notes` singkat, `audited_at`). Ambil tangkapan layar untuk bukti (simpan di luar repo publik).
5. Cari peristiwa yang bisa dijelaskan sumbernya (rilis fitur baru, redesain, gangguan besar) dari berita/halaman resmi.
   Isi `data/events.csv` (**wajib** `source_url`). Kosong pun tidak apa-apa.

**Hasil:** `apps.csv` terisi, tabel inventaris (di BRD bagian 7), `feature_audit.csv` terisi.

## Fase 2 — Lingkungan & uji dengan data sintetis (hari 4–6)
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                                   # Windows: copy .env.example .env
docker compose up -d                                   # tunggu ±10 detik
python src/init_db.py                                  # membuat skema + 12 view
python src/seed_demo_data.py --n 600
python src/clean_reviews.py
python src/label_reviews.py
python src/export_tableau.py --include-demo
```
1. Buka DBeaver → koneksi `localhost:5432`, db `daya_voc`, user `voc_user`, sandi `voc_pass`. Jelajahi skema `ref/raw/clean/nlp/mart`.
2. Buka folder `exports/` di Tableau dan **rancang layout dashboard** dengan data demo (lihat `docs/TABLEAU_GUIDE.md`).
3. Jika ada error, salin pesan lengkapnya dan perbaiki. (Skrip database belum diuji pembuatnya terhadap PostgreSQL asli.)
4. **Hapus data demo:** `python src/seed_demo_data.py --purge`. Jangan pernah memublikasikan apa pun dari data demo.

**Hasil:** pipeline berjalan ujung ke ujung; kerangka dashboard Tableau ada; database bersih dari data demo.

## Fase 3 — Pengambilan data asli (hari 6–8)
```bash
python src/load_reference.py          # ref.app (butuh package_id), events, feature_audit, rice_inputs
python src/fetch_app_meta.py          # snapshot install/skor/versi (ulangi tiap bulan)
python src/scrape_playstore.py --all --since 2024-01-01
```
- Proses bisa lama (jeda 1,5 detik per 200 ulasan). Jika terputus, jalankan ulang; data yang sama tidak terduplikasi.
- Jika hasil 0 baris: cek package ID, koneksi, dan apakah aplikasi punya ulasan berbahasa Indonesia (`--lang id --country id`).
- Catat tanggal pengambilan data (`ops.scrape_log`) di BRD.

**Hasil:** `raw.playstore_review` terisi; jumlah ulasan per aplikasi tercatat.

## Fase 4 — Cleaning & quality assurance (hari 8–10)
```bash
python src/clean_reviews.py
```
Lalu buka `sql/03_quality_checks.sql` di DBeaver dan jalankan tiap query. Catat di BRD bagian 7:
volume & rentang tanggal per aplikasi, bulan kosong/lonjakan, proporsi tanpa teks/Inggris/duplikat,
kelengkapan versi & balasan, nilai `raw_not_cleaned` (harus 0).
- Bandingkan rata-rata rating ulasan (query 8) dengan skor toko. Selisih besar → periksa periode/sampling.
- Baca ±50 ulasan acak per aplikasi dengan mata sendiri sebelum mempercayai angka apa pun.

**Hasil:** laporan kualitas data (1 halaman), tidak ada anomali yang belum dijelaskan.

## Fase 5 — Pelabelan & validasi (hari 10–16)
1. **Baca sampel** ulasan negatif Daya Auto (±200) dan catat topik yang muncul. Sesuaikan `ref.topic` (di `sql/01_schema.sql`)
   dan `data/topic_lexicon.csv` bila perlu (tambah/hapus kata kunci; kolom `exact=1` untuk kata pendek yang rawan salah cocok).
   Jika menambah topik baru: tambahkan di `01_schema.sql`, jalankan `python src/init_db.py`.
2. `python src/label_reviews.py` → topik per ulasan. Cek query 7 di quality checks: bila `other` > ~30%, perkaya kamus.
3. **Gold set:** `python src/make_gold_sample.py --n-per-app 100` → buka `data/gold/gold_sample.csv`, isi `gold_sentiment`
   (negative/neutral/positive) dan `gold_topic` (salah satu dari `ref.topic`). Label berdasarkan **isi teks**, bukan bintang.
   Cukup ±300 baris total, tapi sebaiknya kamu sendiri yang melabeli (dan catat di `labeler`).
4. `python src/load_gold.py` lalu `python src/evaluate_labels.py` → baca akurasi, macro-F1, dan salah klasifikasi terbanyak.
5. Perbaiki kamus → `python src/label_reviews.py --relabel` → evaluasi ulang. Ulangi 2–3 kali. Simpan laporan di `reports/`.
6. (Opsional) Sentimen teks: `pip install -r requirements-nlp.txt` lalu `python src/label_reviews.py --text-sentiment`;
   cek apakah `evaluate_labels.py` menunjukkan model teks lebih baik dari aturan rating pada gold set. Jika tidak, tetap pakai rating.

**Hasil:** akurasi topik & sentimen terukur dan tercatat; kamus versi final (commit di Git).

## Fase 6 — Analisis (hari 16–22)
```bash
python src/init_db.py sql/02_marts.sql     # setelah mengubah view
```
Jalankan di DBeaver dan catat temuan untuk tiap topik:

**Topik 1 (VoC):** `SELECT * FROM mart.v_topic_summary WHERE app_key='daya_auto' ORDER BY share_of_negative_pct DESC;`
dan `mart.v_topic_month` (apakah topik tertentu naik dari bulan ke bulan?). Catat 3 keluhan teratas dan 2 pujian teratas, beserta angkanya.

**Topik 2 (update):** `SELECT * FROM mart.v_version_window WHERE app_key='daya_auto' ORDER BY rollout_proxy_date;`
Perhatikan `delta_rating`, `delta_pct_negative`, dan `has_overlapping_release`. Tulis hati-hati: "berkorelasi dengan", bukan "menyebabkan".
Cocokkan dengan `ref.event` bila ada rilis/gangguan yang diketahui.

**Topik 3 (benchmark):** `SELECT * FROM mart.v_benchmark;` + `mart.v_topic_summary` untuk semua aplikasi + `mart.v_feature_matrix`.
Bandingkan **persentase** (mention rate, % negatif, reply rate), bukan jumlah. Tulis konteks wilayah & fitur.

**Topik 4 (prioritas):** `SELECT * FROM mart.v_priority_topic WHERE app_key='daya_auto' ORDER BY priority_rank;`
Ubah bobot lewat `UPDATE ref.setting SET value='0.4' WHERE key='w_freq';` (dan w_sev, w_eng; jumlah bobot = 1) lalu
lihat apakah 3 besar berubah (uji kepekaan). Isi `data/rice_inputs.csv` (reach, impact, confidence, effort; tulis asumsi di `notes`),
jalankan `python src/load_reference.py`, lalu bandingkan peringkat skor prioritas vs RICE.

**Hasil:** dokumen temuan (angka + interpretasi + batasan) per topik.

## Fase 7 — Dashboard Tableau (hari 22–30)
```bash
python src/export_tableau.py              # tambahkan --review-level bila perlu
```
Ikuti `docs/TABLEAU_GUIDE.md`: 5 halaman, calculated field, parameter bobot prioritas, dashboard action, tooltip dengan n.
Beri judul berupa kesimpulan, tambahkan footer sumber & batasan.

**Hasil:** workbook Tableau (.twbx) lokal + tangkapan layar.

## Fase 8 — Rekomendasi (hari 30–34)
1. Pilih 5 topik teratas. Tulis 5 user story dengan acceptance criteria (`docs/USER_STORIES_template.md`).
2. Setiap story harus punya **bukti angka** dari dashboard, **metrik keberhasilan** yang bisa dipantau lagi lewat ulasan, dan asumsi/risiko.
3. Tulis ringkasan 1 halaman: pertanyaan → temuan (3–5 poin) → rekomendasi → batasan.

**Hasil:** `docs/RINGKASAN_INSIGHT.md` (buat sendiri), 5 user story.

## Fase 9 — Dokumentasi & publikasi (hari 34–40)
1. README publik: tujuan, pertanyaan, metode (diagram alur), temuan utama, batasan, cara menjalankan. **Tanpa data mentah.**
2. Pastikan `.gitignore` aktif (`.env`, `data/gold/`, `exports/`, `reports/`). Periksa riwayat Git tidak memuat data/rahasia.
3. Publikasikan dashboard ke Tableau Public (data agregat; nonaktifkan unduh data bila bisa). Pastikan tidak ada `demo_*`.
4. Bullet CV contoh (isi angka asli): "Menganalisis N ulasan dari 4 aplikasi layanan main dealer Honda (2024–2026) memakai
   Python, PostgreSQL, dan Tableau; membangun klasifikasi topik dengan akurasi X% pada gold set; menyusun backlog prioritas
   berbasis skor frekuensi–keparahan dan 5 user story."
5. Siapkan jawaban interview 2 menit: masalah → data → metode → temuan terpenting → rekomendasi → keterbatasan.
   Siapkan juga jawaban untuk: "bagaimana kamu memastikan klasifikasinya akurat?", "kenapa rating dipakai sebagai sentimen?",
   "kenapa dampak update bukan sebab-akibat?", "apa yang akan kamu lakukan dengan data internal?".

**Hasil:** repo publik, dashboard publik, ringkasan insight, bahan interview.

## Pemecahan masalah singkat
| Gejala | Kemungkinan penyebab / solusi |
|---|---|
| `DATABASE_URL belum diatur` | `.env` belum dibuat dari `.env.example` |
| Gagal konek ke PostgreSQL | Docker belum jalan (`docker compose up -d`) atau port 5432 terpakai |
| `psycopg2` gagal dipasang | Pakai `psycopg2-binary` (sudah di requirements) dan Python 3.11/3.12 |
| `package_id` kosong dilewati | Isi `data/apps.csv` dari URL Play Store |
| Scraping 0 baris | Package ID salah, aplikasi tanpa ulasan `id`, atau struktur Play Store berubah (update `google-play-scraper`) |
| View error "cannot change name of view column" | Jalankan ulang `python src/init_db.py sql/02_marts.sql` (file sudah melakukan DROP lebih dulu) |
| Topik `other` terlalu banyak | Perkaya `topic_lexicon.csv` dari ulasan yang tidak terklasifikasi, `--relabel` |
| Karakter aneh di Tableau | Gunakan CSV hasil ekspor (UTF-8 BOM), pilih encoding UTF-8 saat memuat |
| Rating di Tableau tidak cocok dengan SQL | Gunakan rata-rata berbobot (lihat TABLEAU_GUIDE bagian 2) |
