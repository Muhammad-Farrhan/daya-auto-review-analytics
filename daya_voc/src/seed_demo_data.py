"""Isi database dengan data SINTETIS untuk uji coba, atau hapus semuanya.

  python src/seed_demo_data.py --n 600      # buat 3 aplikasi demo x 600 ulasan fiktif
  python src/seed_demo_data.py --purge      # hapus semua data demo (WAJIB sebelum memakai data asli)

Setelah seeding: clean_reviews.py -> label_reviews.py -> export_tableau.py --include-demo
Data demo TIDAK boleh dipublikasikan.
"""
import argparse

from demo_data import DEMO_APPS, generate_reviews


def purge(conn, text):
    sub_apps = "SELECT app_key FROM ref.app WHERE left(app_key, 5) = 'demo_'"
    sub_reviews = "SELECT review_id FROM raw.playstore_review WHERE left(app_key, 5) = 'demo_'"
    for stmt in (
        f"DELETE FROM nlp.gold_label WHERE review_id IN ({sub_reviews})",
        f"DELETE FROM nlp.review_topic WHERE review_id IN ({sub_reviews})",
        f"DELETE FROM nlp.review_label WHERE review_id IN ({sub_reviews})",
        "DELETE FROM clean.review WHERE left(app_key, 5) = 'demo_'",
        "DELETE FROM raw.playstore_review WHERE left(app_key, 5) = 'demo_'",
        f"DELETE FROM ref.app_snapshot WHERE app_key IN ({sub_apps})",
        f"DELETE FROM ref.feature_audit WHERE app_key IN ({sub_apps})",
        f"DELETE FROM ref.event WHERE app_key IN ({sub_apps})",
        "DELETE FROM ref.app WHERE left(app_key, 5) = 'demo_'",
    ):
        conn.execute(text(stmt))


def main():
    from sqlalchemy import text

    from db import get_engine, records
    import pandas as pd

    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--purge", action="store_true")
    a = ap.parse_args()

    engine = get_engine()
    with engine.begin() as conn:
        purge(conn, text)
        if a.purge:
            print("Semua data demo dihapus.")
            return
        for app_key, name, dealer, region, role, pkg, boost in DEMO_APPS:
            conn.execute(text("""
                INSERT INTO ref.app (app_key, app_name, main_dealer, region, role, package_id, active)
                VALUES (:k, :n, :d, :r, :role, :p, false)"""),
                {"k": app_key, "n": name, "d": dealer, "r": region, "role": role, "p": pkg})
            rows = records(pd.DataFrame(generate_reviews(app_key, a.n, a.seed, boost)))
            for i in range(0, len(rows), 1000):
                conn.execute(text("""
                    INSERT INTO raw.playstore_review
                        (review_id, app_key, content, score, thumbs_up, app_version, reviewed_at, reply_content, replied_at)
                    VALUES (:review_id, :app_key, :content, :score, :thumbs_up, :app_version, :reviewed_at,
                            :reply_content, :replied_at)
                    ON CONFLICT (review_id) DO NOTHING"""), rows[i:i + 1000])
            print(f"{app_key}: {len(rows)} ulasan sintetis")
    print("Selesai. Jalankan: python src/clean_reviews.py && python src/label_reviews.py")


if __name__ == "__main__":
    main()
