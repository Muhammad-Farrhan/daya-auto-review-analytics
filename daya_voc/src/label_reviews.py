"""Beri label topik (kamus kata kunci) dan, opsional, sentimen dari teks (model Hugging Face).

  python src/label_reviews.py                      # topik: lexicon_v1
  python src/label_reviews.py --relabel            # hitung ulang setelah kamu mengubah topic_lexicon.csv
  python src/label_reviews.py --text-sentiment     # + sentimen teks (perlu requirements-nlp.txt)

Sentimen utama di dashboard = dari rating bintang (lihat mart.v_review). Sentimen teks hanya pembanding.
"""
import argparse
import logging
from pathlib import Path

import pandas as pd

from topics import classify, load_lexicon

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
DATA = Path(__file__).resolve().parent.parent / "data"
TEXT_MODEL_NAME = "text_model_v1"     # harus sama dengan nama di sql/02_marts.sql


def build_topic_rows(df: pd.DataFrame, rules, model_name: str) -> list[dict]:
    """Murni: DataFrame (review_id, text_norm) -> baris untuk nlp.review_topic."""
    rows = []
    for rec in df.to_dict("records"):
        primary, all_topics = classify(rec["text_norm"], rules)
        for t in all_topics:
            rows.append({"review_id": rec["review_id"], "topic": t,
                         "model_name": model_name, "is_primary": t == primary})
    return rows


def main():
    from sqlalchemy import text

    from db import get_engine, log_run

    ap = argparse.ArgumentParser()
    ap.add_argument("--model-name", default="lexicon_v1")
    ap.add_argument("--lexicon", default=str(DATA / "topic_lexicon.csv"))
    ap.add_argument("--relabel", action="store_true", help="hapus label topik lama untuk model ini lalu hitung ulang")
    ap.add_argument("--activate", action="store_true", help="jadikan model ini sumber topik di mart (ref.setting)")
    ap.add_argument("--text-sentiment", action="store_true", help="juga hitung sentimen dari teks (opsional)")
    a = ap.parse_args()

    engine = get_engine()
    rules = load_lexicon(a.lexicon)

    with engine.connect() as c:
        valid = {r[0] for r in c.execute(text("SELECT topic FROM ref.topic"))}
    unknown = {r.topic for r in rules} - valid
    if unknown:
        raise SystemExit(f"Topik di leksikon belum ada di ref.topic: {sorted(unknown)}. Tambahkan di sql/01_schema.sql.")

    if a.relabel:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM nlp.review_topic WHERE model_name = :m"), {"m": a.model_name})
        logging.info("Label lama untuk %s dihapus", a.model_name)

    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT c.review_id, c.text_norm FROM clean.review c
            WHERE c.has_text AND NOT EXISTS (
                SELECT 1 FROM nlp.review_topic t WHERE t.review_id = c.review_id AND t.model_name = :m)
        """), conn, params={"m": a.model_name})
    rows = build_topic_rows(df, rules, a.model_name)
    with engine.begin() as conn:
        for i in range(0, len(rows), 2000):
            conn.execute(text("""
                INSERT INTO nlp.review_topic (review_id, topic, model_name, is_primary)
                VALUES (:review_id, :topic, :model_name, :is_primary)
                ON CONFLICT DO NOTHING"""), rows[i:i + 2000])
    logging.info("Topik: %d ulasan diberi label (%d baris)", len(df), len(rows))
    log_run(engine, "label_topic", a.model_name, len(df), len(rows))

    if a.activate:
        with engine.begin() as conn:
            conn.execute(text("UPDATE ref.setting SET value = :m WHERE key = 'topic_model'"), {"m": a.model_name})
        logging.info("ref.setting.topic_model = %s", a.model_name)

    if a.text_sentiment:
        from sentiment import TransformerSentiment
        with engine.connect() as conn:
            todo = pd.read_sql(text("""
                SELECT c.review_id, c.text_clean FROM clean.review c
                WHERE c.has_text AND NOT EXISTS (
                    SELECT 1 FROM nlp.review_label l WHERE l.review_id = c.review_id AND l.model_name = :m)
            """), conn, params={"m": TEXT_MODEL_NAME})
        logging.info("Sentimen teks: %d ulasan", len(todo))
        if len(todo):
            model = TransformerSentiment()
            preds = model.predict(todo["text_clean"].tolist())
            out = [{"review_id": rid, "model_name": TEXT_MODEL_NAME, "sentiment": lab, "score": sc}
                   for rid, (lab, sc) in zip(todo["review_id"], preds)]
            with engine.begin() as conn:
                for i in range(0, len(out), 2000):
                    conn.execute(text("""
                        INSERT INTO nlp.review_label (review_id, model_name, sentiment, sentiment_score)
                        VALUES (:review_id, :model_name, :sentiment, :score)
                        ON CONFLICT DO NOTHING"""), out[i:i + 2000])


if __name__ == "__main__":
    main()
