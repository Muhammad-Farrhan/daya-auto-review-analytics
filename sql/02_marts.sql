-- =====================================================================
-- View analitik (mart) untuk Tableau. Jalankan setelah 01_schema.sql.
-- Aman dijalankan ulang: python src/init_db.py sql/02_marts.sql
-- Sentimen utama = dari rating (1-2 negatif, 3 netral, 4-5 positif).
-- Waktu dikonversi ke WIB (Asia/Jakarta).
-- =====================================================================

-- Hapus dulu (urutan dependensi dijamin CASCADE) agar definisi view boleh berubah kolomnya.
DROP VIEW IF EXISTS mart.v_review CASCADE;
DROP VIEW IF EXISTS mart.v_feature_matrix CASCADE;
DROP VIEW IF EXISTS mart.v_event_window CASCADE;

-- ---------- Dasar: satu baris per ulasan (tanpa duplikat teks panjang) ----------
CREATE OR REPLACE VIEW mart.v_review AS
SELECT r.review_id,
       r.app_key, a.app_name, a.role, a.main_dealer, a.region,
       (r.reviewed_at AT TIME ZONE 'Asia/Jakarta')::date                          AS review_date,
       date_trunc('month', r.reviewed_at AT TIME ZONE 'Asia/Jakarta')::date       AS review_month,
       r.rating, r.thumbs_up, r.app_version, r.n_words, r.has_text, r.lang_flag,
       CASE WHEN r.rating <= 2 THEN 'negative'
            WHEN r.rating = 3  THEN 'neutral'
            ELSE 'positive' END                                                    AS sentiment,
       (r.replied_at IS NOT NULL)                                                  AS has_reply,
       CASE WHEN r.replied_at IS NOT NULL AND r.replied_at >= r.reviewed_at
            THEN extract(epoch FROM (r.replied_at - r.reviewed_at)) / 3600.0 END   AS reply_hours,
       l.sentiment                                                                 AS text_sentiment
FROM clean.review r
JOIN ref.app a ON a.app_key = r.app_key
LEFT JOIN nlp.review_label l ON l.review_id = r.review_id AND l.model_name = 'text_model_v1'
WHERE NOT r.is_dup_long;

-- ---------- Topik per ulasan (memakai model topik aktif di ref.setting) ----------
CREATE OR REPLACE VIEW mart.v_review_topic AS
SELECT t.review_id, t.topic, t.is_primary, tp.label_id AS topic_label, tp.is_issue,
       v.app_key, v.app_name, v.role, v.review_date, v.review_month,
       v.rating, v.thumbs_up, v.sentiment, v.app_version
FROM nlp.review_topic t
JOIN ref.setting s ON s.key = 'topic_model' AND s.value = t.model_name
JOIN ref.topic tp  ON tp.topic = t.topic
JOIN mart.v_review v ON v.review_id = t.review_id;

-- ---------- Topik 1: KPI bulanan per aplikasi ----------
CREATE OR REPLACE VIEW mart.v_monthly_kpi AS
SELECT app_key, app_name, role, review_month,
       count(*)                                                       AS n_reviews,
       round(avg(rating), 2)                                          AS avg_rating,
       round(100.0 * avg((sentiment = 'negative')::int), 1)           AS pct_negative,
       round(100.0 * avg((sentiment = 'positive')::int), 1)           AS pct_positive,
       round(100.0 * avg((sentiment = 'positive')::int)
           - 100.0 * avg((sentiment = 'negative')::int), 1)           AS nps_style,
       round(100.0 * avg(has_reply::int), 1)                          AS pct_replied,
       round(100.0 * count(*) FILTER (WHERE sentiment = 'negative' AND has_reply)
             / NULLIF(count(*) FILTER (WHERE sentiment = 'negative'), 0), 1) AS pct_negative_replied,
       round((percentile_cont(0.5) WITHIN GROUP (ORDER BY reply_hours)
              FILTER (WHERE reply_hours IS NOT NULL))::numeric, 1)    AS median_reply_hours
FROM mart.v_review
GROUP BY app_key, app_name, role, review_month;

-- ---------- Topik 1: topik per bulan ----------
CREATE OR REPLACE VIEW mart.v_topic_month AS
WITH den AS (
    SELECT app_key, review_month, count(*) AS n_text_reviews
    FROM mart.v_review WHERE has_text GROUP BY app_key, review_month
)
SELECT t.app_key, t.app_name, t.role, t.review_month, t.topic, t.topic_label, t.is_issue,
       count(*)                                           AS n_mentions,
       count(*) FILTER (WHERE t.sentiment = 'negative')   AS n_negative_mentions,
       round(avg(t.rating), 2)                            AS avg_rating,
       d.n_text_reviews,
       round(100.0 * count(*) / NULLIF(d.n_text_reviews, 0), 1) AS mention_rate_pct
FROM mart.v_review_topic t
JOIN den d ON d.app_key = t.app_key AND d.review_month = t.review_month
GROUP BY t.app_key, t.app_name, t.role, t.review_month, t.topic, t.topic_label, t.is_issue, d.n_text_reviews;

-- ---------- Topik 1 & 3: ringkasan topik per aplikasi ----------
CREATE OR REPLACE VIEW mart.v_topic_summary AS
WITH app_tot AS (
    SELECT app_key,
           count(*) FILTER (WHERE has_text)                              AS n_text_reviews,
           count(*) FILTER (WHERE has_text AND sentiment = 'negative')   AS n_negative_text_reviews
    FROM mart.v_review GROUP BY app_key
)
SELECT t.app_key, t.app_name, t.role, t.topic, t.topic_label, t.is_issue,
       count(*)                                                           AS n_mentions,
       count(*) FILTER (WHERE t.sentiment = 'negative')                   AS n_negative_mentions,
       round(100.0 * count(*) / NULLIF(a.n_text_reviews, 0), 1)           AS mention_rate_pct,
       round(100.0 * count(*) FILTER (WHERE t.sentiment = 'negative')
             / NULLIF(a.n_negative_text_reviews, 0), 1)                   AS share_of_negative_pct,
       round(avg(t.rating), 2)                                            AS avg_rating,
       round(avg(t.thumbs_up), 2)                                         AS avg_thumbs_up
FROM mart.v_review_topic t
JOIN app_tot a ON a.app_key = t.app_key
GROUP BY t.app_key, t.app_name, t.role, t.topic, t.topic_label, t.is_issue,
         a.n_text_reviews, a.n_negative_text_reviews;

-- ---------- Topik 3: benchmark antar aplikasi ----------
CREATE OR REPLACE VIEW mart.v_benchmark AS
WITH snap AS (
    SELECT DISTINCT ON (app_key) app_key, snapshot_date, installs_text, installs_min,
           score AS store_score, ratings_count, current_version, last_updated
    FROM ref.app_snapshot
    ORDER BY app_key, snapshot_date DESC
)
SELECT v.app_key, v.app_name, v.role, v.main_dealer, v.region,
       count(*)                                                        AS n_reviews,
       min(v.review_date)                                              AS first_review,
       max(v.review_date)                                              AS last_review,
       round(avg(v.rating), 2)                                         AS avg_rating,
       round(100.0 * avg((v.sentiment = 'negative')::int), 1)          AS pct_negative,
       round(100.0 * avg((v.sentiment = 'positive')::int), 1)          AS pct_positive,
       round(100.0 * avg(v.has_reply::int), 1)                         AS pct_replied,
       round(100.0 * count(*) FILTER (WHERE v.sentiment = 'negative' AND v.has_reply)
             / NULLIF(count(*) FILTER (WHERE v.sentiment = 'negative'), 0), 1) AS pct_negative_replied,
       round((percentile_cont(0.5) WITHIN GROUP (ORDER BY v.reply_hours)
              FILTER (WHERE v.reply_hours IS NOT NULL))::numeric, 1)   AS median_reply_hours,
       s.snapshot_date, s.installs_text, s.installs_min, s.store_score,
       s.ratings_count, s.current_version, s.last_updated
FROM mart.v_review v
LEFT JOIN snap s ON s.app_key = v.app_key
GROUP BY v.app_key, v.app_name, v.role, v.main_dealer, v.region,
         s.snapshot_date, s.installs_text, s.installs_min, s.store_score,
         s.ratings_count, s.current_version, s.last_updated;

-- ---------- Topik 2: statistik per versi ----------
CREATE OR REPLACE VIEW mart.v_version_stats AS
SELECT app_key, app_name, app_version,
       count(*)                                                AS n_reviews,
       min(review_date)                                        AS first_seen,
       max(review_date)                                        AS last_seen,
       round(avg(rating), 2)                                   AS avg_rating,
       round(100.0 * avg((sentiment = 'negative')::int), 1)    AS pct_negative,
       (count(*) >= 30)                                        AS enough_data
FROM mart.v_review
WHERE app_version IS NOT NULL AND app_version <> ''
GROUP BY app_key, app_name, app_version;

-- ---------- Topik 2: 30 hari sebelum vs sesudah "rilis" tiap versi ----------
-- Tanggal rilis TIDAK tersedia langsung; proksinya = tanggal ulasan ke-5 dari versi itu.
-- Hanya versi dengan >= 30 ulasan. Hasilnya KORELASI, bukan sebab-akibat.
CREATE OR REPLACE VIEW mart.v_version_window AS
WITH ranked AS (
    SELECT review_id, app_key, app_name, app_version, review_date,
           row_number() OVER (PARTITION BY app_key, app_version ORDER BY review_date, review_id) AS rn,
           count(*)     OVER (PARTITION BY app_key, app_version)                                  AS n_ver
    FROM mart.v_review
    WHERE app_version IS NOT NULL AND app_version <> ''
),
ver AS (
    SELECT app_key, app_name, app_version,
           max(n_ver) AS n_version_reviews,
           min(review_date) FILTER (WHERE rn = 5) AS rollout_proxy_date
    FROM ranked
    GROUP BY app_key, app_name, app_version
    HAVING max(n_ver) >= 30
),
win AS (
    SELECT v.app_key, v.app_name, v.app_version, v.rollout_proxy_date, v.n_version_reviews,
           count(*) FILTER (WHERE r.review_date <  v.rollout_proxy_date) AS n_before,
           count(*) FILTER (WHERE r.review_date >= v.rollout_proxy_date) AS n_after,
           round(avg(r.rating) FILTER (WHERE r.review_date <  v.rollout_proxy_date), 2) AS avg_rating_before,
           round(avg(r.rating) FILTER (WHERE r.review_date >= v.rollout_proxy_date), 2) AS avg_rating_after,
           round(100.0 * avg((r.sentiment = 'negative')::int)
                 FILTER (WHERE r.review_date <  v.rollout_proxy_date), 1) AS pct_neg_before,
           round(100.0 * avg((r.sentiment = 'negative')::int)
                 FILTER (WHERE r.review_date >= v.rollout_proxy_date), 1) AS pct_neg_after
    FROM ver v
    JOIN mart.v_review r
      ON r.app_key = v.app_key
     AND r.review_date >= v.rollout_proxy_date - 30
     AND r.review_date <  v.rollout_proxy_date + 30
    WHERE v.rollout_proxy_date IS NOT NULL
    GROUP BY v.app_key, v.app_name, v.app_version, v.rollout_proxy_date, v.n_version_reviews
)
SELECT w.*,
       (w.avg_rating_after - w.avg_rating_before) AS delta_rating,
       (w.pct_neg_after - w.pct_neg_before)       AS delta_pct_negative,
       EXISTS (SELECT 1 FROM ver v2
               WHERE v2.app_key = w.app_key AND v2.app_version <> w.app_version
                 AND v2.rollout_proxy_date IS NOT NULL
                 AND abs(v2.rollout_proxy_date - w.rollout_proxy_date) < 30) AS has_overlapping_release
FROM win w;

-- ---------- Topik 4: skor prioritas perbaikan per topik keluhan ----------
-- Skor = 100 * (w_freq*frekuensi + w_sev*keparahan + w_eng*keterlibatan), tiap komponen
-- dinormalisasi min-max per aplikasi. Bobot ada di ref.setting. Topik dengan < 5 mention negatif diabaikan.
CREATE OR REPLACE VIEW mart.v_priority_topic AS
WITH w AS (
    SELECT max(value::numeric) FILTER (WHERE key = 'w_freq') AS w_freq,
           max(value::numeric) FILTER (WHERE key = 'w_sev')  AS w_sev,
           max(value::numeric) FILTER (WHERE key = 'w_eng')  AS w_eng
    FROM ref.setting
    WHERE key IN ('w_freq', 'w_sev', 'w_eng')
),
base AS (
    SELECT app_key, app_name, role, topic, topic_label, n_mentions, n_negative_mentions,
           share_of_negative_pct AS freq_pct,
           (5 - avg_rating)      AS severity,
           avg_thumbs_up         AS engagement
    FROM mart.v_topic_summary
    WHERE is_issue AND n_negative_mentions >= 5
),
norm AS (
    SELECT b.*,
           (b.freq_pct   - min(b.freq_pct)   OVER p) / NULLIF(max(b.freq_pct)   OVER p - min(b.freq_pct)   OVER p, 0) AS freq_n,
           (b.severity   - min(b.severity)   OVER p) / NULLIF(max(b.severity)   OVER p - min(b.severity)   OVER p, 0) AS sev_n,
           (b.engagement - min(b.engagement) OVER p) / NULLIF(max(b.engagement) OVER p - min(b.engagement) OVER p, 0) AS eng_n
    FROM base b
    WINDOW p AS (PARTITION BY b.app_key)
),
mx AS (
    SELECT app_key, max(review_date) AS max_date FROM mart.v_review GROUP BY app_key
),
trend AS (
    SELECT t.app_key, t.topic,
           count(*) FILTER (WHERE t.sentiment = 'negative' AND t.review_date >  m.max_date - 90) AS neg_last90,
           count(*) FILTER (WHERE t.sentiment = 'negative' AND t.review_date <= m.max_date - 90
                                  AND t.review_date > m.max_date - 180)                          AS neg_prev90
    FROM mart.v_review_topic t
    JOIN mx m ON m.app_key = t.app_key
    GROUP BY t.app_key, t.topic
),
scored AS (
    SELECT n.app_key, n.app_name, n.role, n.topic, n.topic_label, n.n_mentions, n.n_negative_mentions,
           n.freq_pct, round(n.severity, 2) AS severity, n.engagement,
           coalesce(n.freq_n, 0) AS freq_n, coalesce(n.sev_n, 0) AS sev_n, coalesce(n.eng_n, 0) AS eng_n,
           round(100 * (w.w_freq * coalesce(n.freq_n, 0)
                      + w.w_sev  * coalesce(n.sev_n, 0)
                      + w.w_eng  * coalesce(n.eng_n, 0)), 1) AS priority_score,
           tr.neg_last90, tr.neg_prev90
    FROM norm n
    CROSS JOIN w
    LEFT JOIN trend tr ON tr.app_key = n.app_key AND tr.topic = n.topic
)
SELECT s.*,
       rank() OVER (PARTITION BY s.app_key ORDER BY s.priority_score DESC)         AS priority_rank,
       round(100.0 * (s.neg_last90 - s.neg_prev90) / NULLIF(s.neg_prev90, 0), 1)  AS trend_pct,
       ri.reach, ri.impact, ri.confidence, ri.effort,
       CASE WHEN ri.effort > 0
            THEN round(ri.reach * ri.impact * ri.confidence / ri.effort, 2) END    AS rice_score
FROM scored s
LEFT JOIN ref.rice_input ri ON ri.topic = s.topic;

-- ---------- Peristiwa: 30 hari sebelum vs sesudah ----------
CREATE OR REPLACE VIEW mart.v_event_window AS
SELECT e.event_id, e.event_date, e.event_type, e.description, e.app_key AS event_app_key,
       v.app_key, v.app_name,
       count(*) FILTER (WHERE v.review_date >= e.event_date - 30 AND v.review_date <  e.event_date)      AS n_before,
       count(*) FILTER (WHERE v.review_date >= e.event_date      AND v.review_date <  e.event_date + 30) AS n_after,
       round(avg(v.rating) FILTER (WHERE v.review_date >= e.event_date - 30 AND v.review_date < e.event_date), 2) AS avg_rating_before,
       round(avg(v.rating) FILTER (WHERE v.review_date >= e.event_date AND v.review_date < e.event_date + 30), 2) AS avg_rating_after,
       round(100.0 * avg((v.sentiment = 'negative')::int)
             FILTER (WHERE v.review_date >= e.event_date - 30 AND v.review_date < e.event_date), 1) AS pct_neg_before,
       round(100.0 * avg((v.sentiment = 'negative')::int)
             FILTER (WHERE v.review_date >= e.event_date AND v.review_date < e.event_date + 30), 1) AS pct_neg_after
FROM ref.event e
JOIN mart.v_review v
  ON (e.app_key IS NULL OR v.app_key = e.app_key)
 AND v.review_date >= e.event_date - 30
 AND v.review_date <  e.event_date + 30
GROUP BY e.event_id, e.event_date, e.event_type, e.description, e.app_key, v.app_key, v.app_name;

-- ---------- Topik 3: matriks fitur (hasil audit manual) ----------
CREATE OR REPLACE VIEW mart.v_feature_matrix AS
SELECT f.app_key, a.app_name, a.role, f.feature, f.available, f.notes, f.audited_at
FROM ref.feature_audit f
JOIN ref.app a ON a.app_key = f.app_key;

-- ---------- Ekspor tingkat-ulasan (tanpa teks, tanpa ID ulasan, tanpa identitas) ----------
CREATE OR REPLACE VIEW mart.v_review_export AS
SELECT v.app_key, v.app_name, v.role, v.review_date, v.review_month, v.rating, v.sentiment,
       v.text_sentiment, v.app_version, v.has_text, v.has_reply, v.reply_hours, v.thumbs_up,
       pt.topic AS primary_topic, pt.topic_label AS primary_topic_label
FROM mart.v_review v
LEFT JOIN (
    SELECT t.review_id, t.topic, tp.label_id AS topic_label
    FROM nlp.review_topic t
    JOIN ref.setting s ON s.key = 'topic_model' AND s.value = t.model_name
    JOIN ref.topic tp ON tp.topic = t.topic
    WHERE t.is_primary
) pt ON pt.review_id = v.review_id;
