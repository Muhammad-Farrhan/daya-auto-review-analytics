-- =====================================================================
-- Pengecekan kualitas data. Jalankan di DBeaver/psql, baca hasilnya, catat di README.
-- =====================================================================

-- 1) Volume & rentang tanggal per aplikasi (target: >= ~500 ulasan teks per aplikasi untuk analisis topik)
SELECT app_key, count(*) AS n_reviews, count(*) FILTER (WHERE has_text) AS n_with_text,
       min(reviewed_at)::date AS first_review, max(reviewed_at)::date AS last_review
FROM clean.review GROUP BY app_key ORDER BY app_key;

-- 2) Jumlah ulasan per bulan (cari bulan kosong / lonjakan mencurigakan)
SELECT app_key, date_trunc('month', reviewed_at)::date AS month, count(*) AS n
FROM clean.review GROUP BY 1, 2 ORDER BY 1, 2;

-- 3) Proporsi teks kosong, bahasa, dan duplikat
SELECT app_key,
       round(100.0 * avg((NOT has_text)::int), 1)              AS pct_no_text,
       round(100.0 * avg((lang_flag = 'en')::int), 1)          AS pct_english,
       round(100.0 * avg(is_dup_long::int), 1)                 AS pct_dup_long
FROM clean.review GROUP BY app_key ORDER BY app_key;

-- 4) Kelengkapan versi aplikasi & balasan developer
SELECT app_key,
       round(100.0 * avg((app_version IS NULL OR app_version = '')::int), 1) AS pct_version_missing,
       round(100.0 * avg((replied_at IS NOT NULL)::int), 1)                  AS pct_with_reply
FROM clean.review GROUP BY app_key ORDER BY app_key;

-- 5) Ulasan mentah yang belum dibersihkan (harus 0 setelah clean_reviews.py)
SELECT count(*) AS raw_not_cleaned
FROM raw.playstore_review r
WHERE NOT EXISTS (SELECT 1 FROM clean.review c WHERE c.review_id = r.review_id);

-- 6) Ulasan ber-teks yang belum punya label topik (harus 0 setelah label_reviews.py)
SELECT count(*) AS text_review_without_topic
FROM clean.review c
WHERE c.has_text AND NOT EXISTS (
    SELECT 1 FROM nlp.review_topic t
    JOIN ref.setting s ON s.key = 'topic_model' AND s.value = t.model_name
    WHERE t.review_id = c.review_id);

-- 7) Porsi topik 'other' (jika lebih dari sekitar 30 persen, perkaya data/topic_lexicon.csv)
SELECT v.app_key,
       round(100.0 * count(*) FILTER (WHERE v.topic = 'other') / count(*), 1) AS pct_other_primary
FROM mart.v_review_topic v WHERE v.is_primary GROUP BY v.app_key ORDER BY v.app_key;

-- 8) Konsistensi: rating vs jumlah ulasan per aplikasi (bandingkan dengan skor di Play Store)
SELECT v.app_key, round(avg(v.rating), 2) AS avg_rating_reviews,
       (SELECT s.score FROM ref.app_snapshot s WHERE s.app_key = v.app_key
        ORDER BY s.snapshot_date DESC LIMIT 1) AS store_score_latest
FROM mart.v_review v GROUP BY v.app_key ORDER BY v.app_key;

-- 9) Riwayat pengambilan data
SELECT source, target, started_at, rows_fetched, rows_new, note
FROM ops.scrape_log ORDER BY run_id DESC LIMIT 30;
