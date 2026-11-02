"""Ekspor view mart.* ke CSV untuk Tableau (UTF-8 dengan BOM agar rapi di Excel & Tableau).

  python src/export_tableau.py                  # hanya data agregat
  python src/export_tableau.py --review-level   # + satu baris per ulasan (tanpa teks & tanpa identitas)
  python src/export_tableau.py --include-demo   # sertakan aplikasi demo (hanya untuk uji coba layout)

Tidak ada teks ulasan di file ekspor. Aplikasi demo (app_key 'demo_*') dikeluarkan secara default.
"""
import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

EXPORTS = {
    "kpi_monthly": "mart.v_monthly_kpi",
    "topic_month": "mart.v_topic_month",
    "topic_summary": "mart.v_topic_summary",
    "benchmark": "mart.v_benchmark",
    "version_stats": "mart.v_version_stats",
    "version_window": "mart.v_version_window",
    "priority_topic": "mart.v_priority_topic",
    "event_window": "mart.v_event_window",
    "feature_matrix": "mart.v_feature_matrix",
}
REVIEW_LEVEL = {"review_level": "mart.v_review_export"}


def drop_demo(df: pd.DataFrame) -> pd.DataFrame:
    if "app_key" in df.columns:
        return df[~df["app_key"].astype(str).str.startswith("demo_")]
    return df


def main():
    from sqlalchemy import text

    from db import get_engine

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "exports"))
    ap.add_argument("--review-level", action="store_true")
    ap.add_argument("--include-demo", action="store_true")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    targets = dict(EXPORTS)
    if a.review_level:
        targets.update(REVIEW_LEVEL)

    engine = get_engine()
    lines = [f"Ekspor {datetime.now():%Y-%m-%d %H:%M}"]
    with engine.connect() as conn:
        for name, view in targets.items():
            df = pd.read_sql(text(f"SELECT * FROM {view}"), conn)
            if not a.include_demo:
                df = drop_demo(df)
            df.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
            lines.append(f"{name}.csv  <- {view}  ({len(df)} baris)")
            print(lines[-1])
    (out / "_README_export.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
