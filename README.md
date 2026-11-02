# Daya Auto Voice of Customer

**Dari Ulasan Pengguna ke Prioritas Perbaikan: Analisis Aplikasi Layanan Main Dealer Honda (2024–2026)**

Proyek portofolio business analyst: mengumpulkan ulasan Google Play aplikasi **Daya Auto** dan beberapa aplikasi
main dealer Honda lain, mengolahnya di PostgreSQL + Python, lalu menyajikannya di **Tableau**.

Empat topik yang dijawab:

| # | Topik | Pertanyaan | Keluaran utama |
|---|---|---|---|
| 1 | Voice of Customer | Apa keluhan & pujian utama pengguna Daya Auto? | `topic_summary`, `topic_month`, `kpi_monthly` |
| 2 | Dampak update | Apakah versi tertentu mengubah rating? | `version_stats`, `version_window` |
| 3 | Benchmark | Di mana Daya Auto unggul/tertinggal dari main dealer lain? | `benchmark`, `feature_matrix`, `topic_summary` |
| 4 | Prioritas perbaikan | Apa yang sebaiknya diperbaiki lebih dulu? | `priority_topic` (+ RICE & user story) |

> Ini analisis independen dari ulasan publik. Bukan data internal Daya Group.

## Struktur

```
data/        apps.csv (ISI package_id), topic_lexicon.csv, normalization.csv, events.csv,
             feature_audit.csv, rice_inputs.csv, gold/ (label manual, tidak di-commit)
sql/         01_schema.sql  02_marts.sql  03_quality_checks.sql
src/         skrip Python (lihat urutan di bawah)
tests/       unit test (python -m unittest discover -s tests)
docs/        PANDUAN_LANGKAH.md  BRD_template.md  USER_STORIES_template.md
             TABLEAU_GUIDE.md  DATA_DICTIONARY.md  ETIKA_DAN_BATASAN.md
exports/     CSV untuk Tableau (dibuat otomatis, tidak di-commit)
```

## Mulai cepat

```bash
# 1. lingkungan
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                 # Windows: copy .env.example .env

# 2. database (Docker, atau PostgreSQL biasa dengan database bernama daya_voc)
docker compose up -d
python src/init_db.py                # membuat skema + view

# 3. uji alur memakai DATA SINTETIS (opsional tapi sangat disarankan)
python src/seed_demo_data.py --n 600
python src/clean_reviews.py
python src/label_reviews.py
python src/export_tableau.py --include-demo      # CSV demo untuk merancang layout Tableau
python src/seed_demo_data.py --purge             # WAJIB: hapus data demo sebelum data asli

# 4. data asli
#    isi package_id di data/apps.csv (dari URL Play Store: ...details?id=PACKAGE_ID)
python src/load_reference.py
python src/fetch_app_meta.py
python src/scrape_playstore.py --all --since 2024-01-01
python src/clean_reviews.py
python src/label_reviews.py

# 5. validasi label (gold set manual, ±100 ulasan per aplikasi)
python src/make_gold_sample.py --n-per-app 100
#    isi gold_sentiment & gold_topic di data/gold/gold_sample.csv
python src/load_gold.py
python src/evaluate_labels.py
#    perbaiki data/topic_lexicon.csv -> python src/label_reviews.py --relabel

# 6. ekspor untuk Tableau
python src/export_tableau.py
```

Atau jalankan beberapa langkah sekaligus: `python src/pipeline.py --steps clean,label,export`.

Panduan lengkap per minggu: **docs/PANDUAN_LANGKAH.md**.

## Status verifikasi (jujur)

- 36 unit test untuk logika murni (normalisasi teks, kamus topik, metrik, sampling, data demo) **lulus**:
  `python -m unittest discover -s tests -v`
- Skrip yang menyentuh database / Play Store (`init_db`, `scrape_playstore`, `fetch_app_meta`, `load_reference`,
  `clean_reviews`, `label_reviews`, view di `sql/02_marts.sql`, dll.) **belum pernah dijalankan** terhadap PostgreSQL
  sungguhan oleh pembuatnya (lingkungan pembuat tidak punya database maupun internet). Karena itu langkah 3 di atas
  (uji dengan data sintetis) adalah smoke test: jika ada error SQL/Python, salin pesan errornya dan perbaiki
  sebelum scraping data asli.
- Kamus topik (`topic_lexicon.csv`) adalah titik awal. Sesuaikan setelah membaca ulasan asli dan mengukur akurasi
  dengan gold set.
