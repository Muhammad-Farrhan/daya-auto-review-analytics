"""raw.playstore_review -> clean.review (bersih, ternormalisasi, ditandai bahasa & duplikat).

Aman dijalankan berulang: hanya memproses ulasan yang belum ada di clean.review.
  python src/clean_reviews.py
"""
import logging
from pathlib import Path

import pandas as pd

from textproc import load_slang, process_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
DATA = Path(__file__).resolve().parent.parent / "data"

CLEAN_COLUMNS = ["review_id", "app_key", "text_clean", "text_norm", "n_words", "has_text", "lang_flag",
                 "rating", "thumbs_up", "app_version", "reviewed_at", "replied_at"]


def process_dataframe(raw: pd.DataFrame, slang: dict[str, str]) -> pd.DataFrame:
    """Murni (tanpa database): DataFrame raw -> DataFrame untuk clean.review."""
    out = []
    for rec in raw.to_dict("records"):
        t = process_text(rec.get("content"), slang)
        out.append({
            "review_id": rec["review_id"], "app_key": rec["app_key"], **t,
            "rating": rec.get("score"), "thumbs_up": rec.get("thumbs_up"),
            "app_version": rec.get("app_version"),
            "reviewed_at": rec.get("reviewed_at"), "replied_at": rec.get("replied_at"),
        })
    return pd.DataFrame(out, columns=CLEAN_COLUMNS)


SELECT_NEW = """
    SELECT r.review_id, r.app_key, r.content, r.score, r.thumbs_up, r.app_version, r.reviewed_at, r.replied_at
    FROM raw.playstore_review r
    WHERE NOT EXISTS (SELECT 1 FROM clean.review c WHERE c.review_id = r.review_id)
"""

INSERT_SQL = """
    INSERT INTO clean.review (review_id, app_key, text_clean, text_norm, n_words, has_text, lang_flag,
                              rating, thumbs_up, app_version, reviewed_at, replied_at)
    VALUES (:review_id, :app_key, :text_clean, :text_norm, :n_words, :has_text, :lang_flag,
            :rating, :thumbs_up, :app_version, :reviewed_at, :replied_at)
    ON CONFLICT (review_id) DO NOTHING
"""

# Tandai duplikat teks panjang (>= 6 kata) dalam satu aplikasi; kemunculan pertama dianggap asli.
FLAG_DUPLICATES = """
    UPDATE clean.review c
    SET is_dup_long = d.is_dup
    FROM (
        SELECT review_id,
               (row_number() OVER (PARTITION BY app_key, text_norm ORDER BY reviewed_at, review_id) > 1) AS is_dup
        FROM clean.review
        WHERE n_words >= 6
    ) d
    WHERE c.review_id = d.review_id AND c.is_dup_long IS DISTINCT FROM d.is_dup
"""


def main():
    from sqlalchemy import text

    from db import get_engine, log_run, records

    engine = get_engine()
    slang = load_slang(DATA / "normalization.csv")
    with engine.connect() as conn:
        raw = pd.read_sql(text(SELECT_NEW), conn)
    logging.info("Ulasan baru untuk dibersihkan: %d", len(raw))
    if len(raw):
        clean = process_dataframe(raw, slang)
        rows = records(clean)
        with engine.begin() as conn:
            for i in range(0, len(rows), 1000):
                conn.execute(text(INSERT_SQL), rows[i:i + 1000])
    with engine.begin() as conn:
        res = conn.execute(text(FLAG_DUPLICATES))
        logging.info("Penanda duplikat diperbarui: %d baris", res.rowcount)
    log_run(engine, "clean", "clean.review", len(raw), len(raw))


if __name__ == "__main__":
    main()
