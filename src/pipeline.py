"""Jalankan beberapa langkah pipeline berurutan.

  python src/pipeline.py --steps init,ref,meta,scrape,clean,label,export
  python src/pipeline.py --steps clean,label,export      # setelah data mentah sudah ada

Langkah: init (skema+view) | ref (data referensi) | meta (metadata aplikasi) | scrape (ulasan)
         clean | label | export (CSV untuk Tableau)
Pelabelan manual & evaluasi dijalankan terpisah (make_gold_sample, load_gold, evaluate_labels).
"""
import argparse
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
STEPS = {
    "init": ["init_db.py"],
    "ref": ["load_reference.py"],
    "meta": ["fetch_app_meta.py"],
    "scrape": ["scrape_playstore.py", "--all", "--since", "2024-01-01"],
    "clean": ["clean_reviews.py"],
    "label": ["label_reviews.py"],
    "export": ["export_tableau.py"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="ref,meta,scrape,clean,label,export")
    a = ap.parse_args()
    chosen = [s.strip() for s in a.steps.split(",") if s.strip()]
    unknown = [s for s in chosen if s not in STEPS]
    if unknown:
        raise SystemExit(f"Langkah tidak dikenal: {unknown}. Pilihan: {list(STEPS)}")
    for step in chosen:
        cmd = [sys.executable, str(SRC / STEPS[step][0]), *STEPS[step][1:]]
        print(f"\n=== {step}: {' '.join(STEPS[step])}")
        subprocess.run(cmd, check=True, cwd=SRC.parent)
    print("\nSelesai.")


if __name__ == "__main__":
    main()
