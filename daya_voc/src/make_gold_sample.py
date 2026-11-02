"""Buat file sampel untuk PELABELAN MANUAL (gold set).

  python src/make_gold_sample.py --n-per-app 100
Buka data/gold/gold_sample.csv di Excel/Google Sheets, isi kolom gold_sentiment (negative/neutral/positive)
dan gold_topic (salah satu dari ref.topic), simpan sebagai CSV, lalu jalankan load_gold.py.

File ini berisi teks ulasan -> jangan di-commit atau dipublikasikan (sudah ada di .gitignore).
"""
import argparse
from pathlib import Path

import pandas as pd

from sampling import stratified_sample

ROOT = Path(__file__).resolve().parent.parent


def main():
    from sqlalchemy import text

    from db import get_engine

    ap = argparse.ArgumentParser()
    ap.add_argument("--n-per-app", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(ROOT / "data" / "gold" / "gold_sample.csv"))
    ap.add_argument("--force", action="store_true", help="timpa file yang sudah ada")
    a = ap.parse_args()

    out = Path(a.out)
    if out.exists() and not a.force:
        raise SystemExit(f"{out} sudah ada (mungkin sudah kamu isi). Pakai --force jika ingin menimpa.")

    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT review_id, app_key, rating, text_clean FROM clean.review
            WHERE has_text AND NOT is_dup_long AND left(app_key, 5) <> 'demo_'
        """), conn)
        valid_topics = [r[0] for r in conn.execute(text("SELECT topic FROM ref.topic ORDER BY sort_order"))]
    sample = stratified_sample(df, a.n_per_app, a.seed)
    for col in ("gold_sentiment", "gold_topic", "labeler", "notes"):
        sample[col] = ""
    out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Sampel {len(sample)} ulasan -> {out}")
    print("Nilai gold_sentiment: negative | neutral | positive")
    print("Nilai gold_topic    :", " | ".join(valid_topics))


if __name__ == "__main__":
    main()
