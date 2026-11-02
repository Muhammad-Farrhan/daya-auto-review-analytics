"""Muat label manual (gold set) yang sudah kamu isi ke nlp.gold_label.

  python src/load_gold.py                       # default data/gold/gold_sample.csv
"""
import argparse
from pathlib import Path

import pandas as pd

from sampling import validate_gold

ROOT = Path(__file__).resolve().parent.parent


def main():
    from sqlalchemy import text

    from db import get_engine, records

    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(ROOT / "data" / "gold" / "gold_sample.csv"))
    a = ap.parse_args()

    df = pd.read_csv(a.file, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    engine = get_engine()
    with engine.connect() as c:
        valid_topics = {r[0] for r in c.execute(text("SELECT topic FROM ref.topic"))}
    ok, errors = validate_gold(df, valid_topics)
    for e in errors[:20]:
        print("PERIKSA:", e)
    if errors:
        print(f"{len(errors)} baris bermasalah dilewati.")
    if ok.empty:
        raise SystemExit("Tidak ada baris valid yang sudah diisi.")
    rows = records(ok[["review_id", "gold_sentiment", "gold_topic", "labeler"]])
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO nlp.gold_label (review_id, sentiment, topic, labeler)
            VALUES (:review_id, :gold_sentiment, :gold_topic, :labeler)
            ON CONFLICT (review_id) DO UPDATE SET
              sentiment = EXCLUDED.sentiment, topic = EXCLUDED.topic, labeler = EXCLUDED.labeler,
              labeled_at = now()"""), rows)
    print(f"{len(rows)} label manual dimuat.")


if __name__ == "__main__":
    main()
