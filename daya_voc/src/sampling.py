"""Sampel pelabelan manual (gold set) & validasi hasil pelabelan."""
from __future__ import annotations

import math

import pandas as pd

VALID_SENTIMENTS = {"negative", "neutral", "positive"}


def stratified_sample(df: pd.DataFrame, n_per_app: int = 100, seed: int = 42) -> pd.DataFrame:
    """Ambil ±n_per_app ulasan per aplikasi, dibagi rata per rating (1-5) agar semua kelas terwakili.

    Catatan: ini sengaja TIDAK proporsional (rating langka ikut terambil), jadi pakai hanya untuk
    mengukur akurasi model, bukan untuk menghitung distribusi sebenarnya.
    """
    parts = []
    per_rating = math.ceil(n_per_app / 5)
    for _app, g in df.groupby("app_key"):
        chunks = []
        for _rating, gr in g.groupby("rating"):
            chunks.append(gr.sample(n=min(len(gr), per_rating), random_state=seed))
        if chunks:
            app_sample = pd.concat(chunks)
            parts.append(app_sample.sample(n=min(len(app_sample), n_per_app), random_state=seed))
    if not parts:
        return df.head(0).copy()
    return pd.concat(parts).sample(frac=1.0, random_state=seed).reset_index(drop=True)


def validate_gold(df: pd.DataFrame, valid_topics: set[str]) -> tuple[pd.DataFrame, list[str]]:
    """Ambil baris yang sudah diisi; kembalikan (baris valid, daftar pesan error)."""
    errors: list[str] = []
    work = df.copy()
    for col in ("gold_sentiment", "gold_topic"):
        work[col] = work[col].fillna("").astype(str).str.strip().str.lower()
    filled = work[(work["gold_sentiment"] != "") | (work["gold_topic"] != "")]
    ok_rows = []
    for _, r in filled.iterrows():
        rid = r["review_id"]
        if r["gold_sentiment"] not in VALID_SENTIMENTS:
            errors.append(f"{rid}: gold_sentiment '{r['gold_sentiment']}' tidak valid {sorted(VALID_SENTIMENTS)}")
        elif r["gold_topic"] not in valid_topics:
            errors.append(f"{rid}: gold_topic '{r['gold_topic']}' tidak ada di ref.topic")
        else:
            ok_rows.append(r)
    ok = pd.DataFrame(ok_rows, columns=work.columns) if ok_rows else work.head(0)
    return ok, errors
