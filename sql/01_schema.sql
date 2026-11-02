-- =====================================================================
-- Skema: Voice of Customer aplikasi layanan main dealer Honda (Daya Auto + pembanding)
-- Lapisan: ref (referensi) -> raw (mentah) -> clean -> nlp (label) -> mart (view analitik)
-- Aman dijalankan berulang (idempoten).
-- Jalankan: python src/init_db.py   (atau psql -f sql/01_schema.sql)
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS clean;
CREATE SCHEMA IF NOT EXISTS nlp;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS ops;

-- ---------------------------------------------------------------- REF
CREATE TABLE IF NOT EXISTS ref.app (
    app_key      text PRIMARY KEY,                 -- mis. 'daya_auto', 'wanda'
    app_name     text NOT NULL,
    main_dealer  text,
    region       text,
    role         text NOT NULL DEFAULT 'peer' CHECK (role IN ('focus', 'peer', 'reference')),
    package_id   text UNIQUE NOT NULL,             -- dari URL Play Store (?id=...)
    active       boolean NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS ref.app_snapshot (
    app_key         text NOT NULL REFERENCES ref.app(app_key),
    snapshot_date   date NOT NULL,
    installs_text   text,
    installs_min    bigint,
    score           numeric,
    ratings_count   bigint,
    reviews_count   bigint,
    current_version text,
    last_updated    date,
    PRIMARY KEY (app_key, snapshot_date)
);

CREATE TABLE IF NOT EXISTS ref.topic (
    topic        text PRIMARY KEY,
    label_id     text NOT NULL,                    -- label tampilan (Bahasa Indonesia) untuk Tableau
    description  text,
    is_issue     boolean NOT NULL DEFAULT true,    -- false = bukan keluhan (pujian / lainnya)
    sort_order   integer
);
INSERT INTO ref.topic (topic, label_id, description, is_issue, sort_order) VALUES
 ('login_otp',             'Login & OTP',                      'Gagal login, OTP tidak masuk, lupa password',          true, 1),
 ('account_data',          'Akun & data kendaraan',            'Pendaftaran, data motor/nomor rangka tidak sesuai',    true, 2),
 ('booking_service',       'Booking servis',                   'Booking, jadwal, antrian',                             true, 3),
 ('kpb_claim',             'Klaim KPB / servis gratis',        'Klaim kartu perawatan berkala',                        true, 4),
 ('insurance_digital',     'Asuransi digital',                 'Status/polis asuransi',                                true, 5),
 ('parts_homeservice',     'Suku cadang, home service & bayar','Pesanan sparepart, home service, pembayaran',          true, 6),
 ('promo_points',          'Promo & poin',                     'Promo, voucher, poin, hadiah',                         true, 7),
 ('app_bug_crash',         'Bug, error & crash',               'Error, crash, layar putih, gangguan server',           true, 8),
 ('performance_slow',      'Performa lambat',                  'Lemot, loading lama, boros baterai',                   true, 9),
 ('ui_ux',                 'Tampilan & kemudahan pakai',       'Desain, menu, alur membingungkan',                     true, 10),
 ('notification_reminder', 'Notifikasi & pengingat',           'Notifikasi/pengingat servis',                          true, 11),
 ('dealer_workshop',       'Layanan bengkel/dealer & CS',      'Mekanik, kasir, pelayanan, customer service',          true, 12),
 ('general_praise',        'Pujian umum',                      'Pujian tanpa topik spesifik',                          false, 13),
 ('other',                 'Lainnya',                          'Tidak cocok kategori mana pun',                        false, 14)
ON CONFLICT (topic) DO UPDATE SET
    label_id = EXCLUDED.label_id, description = EXCLUDED.description,
    is_issue = EXCLUDED.is_issue, sort_order = EXCLUDED.sort_order;

CREATE TABLE IF NOT EXISTS ref.setting (
    key          text PRIMARY KEY,
    value        text NOT NULL,
    description  text
);
INSERT INTO ref.setting (key, value, description) VALUES
 ('topic_model', 'lexicon_v1', 'model_name di nlp.review_topic yang dipakai view mart'),
 ('w_freq',      '0.5',        'Bobot frekuensi keluhan pada skor prioritas'),
 ('w_sev',       '0.3',        'Bobot keparahan (5 - rata-rata rating topik)'),
 ('w_eng',       '0.2',        'Bobot keterlibatan (rata-rata thumbs-up)')
ON CONFLICT (key) DO NOTHING;

CREATE TABLE IF NOT EXISTS ref.event (
    event_id     bigserial PRIMARY KEY,
    event_date   date NOT NULL,
    event_type   text NOT NULL,                    -- 'release','redesign','new_feature','outage','campaign'
    app_key      text REFERENCES ref.app(app_key), -- NULL = berlaku untuk semua aplikasi
    description  text NOT NULL,
    source_url   text NOT NULL,                    -- wajib: jejak sumber
    UNIQUE (event_date, event_type, description)
);

CREATE TABLE IF NOT EXISTS ref.feature_audit (
    app_key      text NOT NULL REFERENCES ref.app(app_key),
    feature      text NOT NULL,
    available    boolean NOT NULL,
    notes        text,
    audited_at   date,
    PRIMARY KEY (app_key, feature)
);

CREATE TABLE IF NOT EXISTS ref.rice_input (
    topic        text PRIMARY KEY REFERENCES ref.topic(topic),
    reach        numeric,                          -- perkiraan pengguna terdampak (skala bebas, konsisten)
    impact       numeric,                          -- 0.25 / 0.5 / 1 / 2 / 3
    confidence   numeric,                          -- 0..1
    effort       numeric,                          -- orang-bulan (ASUMSI kamu; tulis di notes)
    notes        text
);

-- ---------------------------------------------------------------- RAW
CREATE TABLE IF NOT EXISTS raw.playstore_review (
    review_id     text PRIMARY KEY,
    app_key       text NOT NULL REFERENCES ref.app(app_key),
    content       text,
    score         smallint CHECK (score BETWEEN 1 AND 5),
    thumbs_up     integer,
    app_version   text,
    reviewed_at   timestamptz,
    reply_content text,
    replied_at    timestamptz,
    scraped_at    timestamptz NOT NULL DEFAULT now()
    -- sengaja TIDAK menyimpan nama pengguna / foto profil (privasi)
);
CREATE INDEX IF NOT EXISTS ix_raw_review_app_date ON raw.playstore_review (app_key, reviewed_at);

-- ---------------------------------------------------------------- CLEAN
CREATE TABLE IF NOT EXISTS clean.review (
    review_id    text PRIMARY KEY REFERENCES raw.playstore_review(review_id),
    app_key      text NOT NULL REFERENCES ref.app(app_key),
    text_clean   text,                              -- terbaca manusia, data pribadi disamarkan
    text_norm    text,                              -- ternormalisasi untuk analisis
    n_words      integer NOT NULL DEFAULT 0,
    has_text     boolean NOT NULL DEFAULT false,
    lang_flag    text,                              -- 'id' | 'en' | 'unk'
    rating       smallint,
    thumbs_up    integer,
    app_version  text,
    reviewed_at  timestamptz,
    replied_at   timestamptz,
    is_dup_long  boolean NOT NULL DEFAULT false     -- duplikat teks panjang (>= 6 kata)
);
CREATE INDEX IF NOT EXISTS ix_clean_review_app_date ON clean.review (app_key, reviewed_at);

-- ---------------------------------------------------------------- NLP
CREATE TABLE IF NOT EXISTS nlp.review_topic (
    review_id   text NOT NULL REFERENCES clean.review(review_id),
    topic       text NOT NULL REFERENCES ref.topic(topic),
    model_name  text NOT NULL,                      -- mis. 'lexicon_v1'
    is_primary  boolean NOT NULL DEFAULT false,
    labeled_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (review_id, topic, model_name)
);
CREATE INDEX IF NOT EXISTS ix_review_topic_model ON nlp.review_topic (model_name, topic);

CREATE TABLE IF NOT EXISTS nlp.review_label (       -- sentimen dari TEKS (opsional, pembanding rating)
    review_id        text NOT NULL REFERENCES clean.review(review_id),
    model_name       text NOT NULL,                 -- 'text_model_v1'
    sentiment        text NOT NULL CHECK (sentiment IN ('negative', 'neutral', 'positive')),
    sentiment_score  numeric,
    labeled_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (review_id, model_name)
);

CREATE TABLE IF NOT EXISTS nlp.gold_label (         -- label manual (acuan evaluasi)
    review_id   text PRIMARY KEY REFERENCES clean.review(review_id),
    sentiment   text NOT NULL CHECK (sentiment IN ('negative', 'neutral', 'positive')),
    topic       text NOT NULL REFERENCES ref.topic(topic),
    labeler     text,
    labeled_at  timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------- OPS
CREATE TABLE IF NOT EXISTS ops.scrape_log (
    run_id        bigserial PRIMARY KEY,
    source        text NOT NULL,
    target        text,
    started_at    timestamptz NOT NULL DEFAULT now(),
    rows_fetched  integer,
    rows_new      integer,
    note          text
);
