"""Ukur kualitas label otomatis terhadap gold set (label manual).

Membandingkan:
- sentimen dari rating (aturan 1-2/3/4-5) vs label manual
- sentimen dari teks (model, bila ada) vs label manual
- topik utama (kamus) vs label manual
Hasil dicetak dan disimpan di reports/.

  python src/evaluate_labels.py
"""
from datetime import datetime
from pathlib import Path

import pandas as pd

from metrics import classification_report, format_report, top_confusions
from sentiment import rating_sentiment

ROOT = Path(__file__).resolve().parent.parent
SENT_LABELS = ["negative", "neutral", "positive"]

QUERY = """
SELECT g.review_id, g.sentiment AS gold_sentiment, g.topic AS gold_topic, c.rating,
       (SELECT t.topic FROM nlp.review_topic t
          JOIN ref.setting s ON s.key = 'topic_model' AND s.value = t.model_name
         WHERE t.review_id = g.review_id AND t.is_primary LIMIT 1) AS pred_topic,
       (SELECT l.sentiment FROM nlp.review_label l
         WHERE l.review_id = g.review_id AND l.model_name = 'text_model_v1') AS pred_text_sentiment
FROM nlp.gold_label g
JOIN clean.review c ON c.review_id = g.review_id
"""


def main():
    from sqlalchemy import text

    from db import get_engine

    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(QUERY), conn)
    if df.empty:
        raise SystemExit("Gold set kosong. Jalankan make_gold_sample.py, isi labelnya, lalu load_gold.py.")

    out_lines = [f"Evaluasi {datetime.now():%Y-%m-%d %H:%M}  (gold n={len(df)})", ""]

    df["pred_rating_sentiment"] = df["rating"].map(lambda r: (rating_sentiment(r) or (None,))[0])
    rep = classification_report(df["gold_sentiment"].tolist(), df["pred_rating_sentiment"].tolist(), SENT_LABELS)
    out_lines += [format_report("Sentimen dari RATING vs manual", rep), ""]

    has_text_model = df["pred_text_sentiment"].notna()
    if has_text_model.any():
        sub = df[has_text_model]
        rep = classification_report(sub["gold_sentiment"].tolist(), sub["pred_text_sentiment"].tolist(), SENT_LABELS)
        out_lines += [format_report("Sentimen dari TEKS (model) vs manual", rep), ""]

    sub = df[df["pred_topic"].notna()]
    if len(sub):
        rep = classification_report(sub["gold_topic"].tolist(), sub["pred_topic"].tolist())
        out_lines += [format_report("Topik utama (kamus) vs manual", rep), "", "Salah klasifikasi terbanyak (gold -> prediksi):"]
        out_lines += [f"  {t} -> {p}: {n}x" for t, p, n in top_confusions(sub["gold_topic"].tolist(), sub["pred_topic"].tolist(), 8)]
        out_lines += ["", "Saran: tambahkan kata kunci untuk topik yang recall-nya rendah di data/topic_lexicon.csv,",
                      "lalu jalankan: python src/label_reviews.py --relabel"]

    text_out = "\n".join(out_lines)
    print(text_out)
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / f"eval_{datetime.now():%Y%m%d_%H%M}.txt").write_text(text_out, encoding="utf-8")


if __name__ == "__main__":
    main()
