"""Ambil metadata publik aplikasi (install, rating toko, versi terakhir) -> ref.app_snapshot.

Jalankan berkala (mis. tiap bulan) agar kamu punya riwayat snapshot.
  python src/fetch_app_meta.py
"""
import logging
import time
from datetime import date, datetime, timezone

from google_play_scraper import app as gp_app
from sqlalchemy import text

from db import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def to_date(epoch):
    if not epoch:
        return None
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc).date()


def main():
    engine = get_engine()
    with engine.connect() as c:
        apps = c.execute(text(
            "SELECT app_key, package_id FROM ref.app WHERE active AND left(app_key, 5) <> 'demo_'")).all()
    if not apps:
        raise SystemExit("Belum ada aplikasi di ref.app. Isi package_id di data/apps.csv lalu jalankan load_reference.py")
    for app_key, package_id in apps:
        try:
            d = gp_app(package_id, lang="id", country="id")
        except Exception as exc:    # aplikasi dihapus / nama paket salah
            logging.error("%s (%s): gagal ambil metadata: %s", app_key, package_id, exc)
            continue
        row = {
            "app_key": app_key, "snapshot_date": date.today(),
            "installs_text": d.get("installs"), "installs_min": d.get("realInstalls"),
            "score": d.get("score"), "ratings_count": d.get("ratings"), "reviews_count": d.get("reviews"),
            "current_version": d.get("version"), "last_updated": to_date(d.get("updated")),
        }
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO ref.app_snapshot (app_key, snapshot_date, installs_text, installs_min, score,
                    ratings_count, reviews_count, current_version, last_updated)
                VALUES (:app_key, :snapshot_date, :installs_text, :installs_min, :score,
                    :ratings_count, :reviews_count, :current_version, :last_updated)
                ON CONFLICT (app_key, snapshot_date) DO UPDATE SET
                    installs_text = EXCLUDED.installs_text, installs_min = EXCLUDED.installs_min,
                    score = EXCLUDED.score, ratings_count = EXCLUDED.ratings_count,
                    reviews_count = EXCLUDED.reviews_count, current_version = EXCLUDED.current_version,
                    last_updated = EXCLUDED.last_updated
            """), row)
        logging.info("%s: install=%s, skor toko=%s, ulasan=%s", app_key,
                     row["installs_text"], row["score"], row["reviews_count"])
        time.sleep(1.5)


if __name__ == "__main__":
    main()
