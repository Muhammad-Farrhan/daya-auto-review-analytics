"""Ambil ulasan Google Play -> raw.playstore_review

Contoh:
  python src/scrape_playstore.py --all --since 2024-01-01
  python src/scrape_playstore.py --app-key daya_auto --since 2024-01-01 --max 20000

Catatan:
- Memakai library tidak resmi `google-play-scraper`. Cek ketentuan layanan Google Play, ambil hanya data
  publik, beri jeda, dan JANGAN mempublikasikan ulang data mentah (publikasikan kode + data agregat).
- Nama pengguna & foto profil sengaja tidak disimpan (privasi).
"""
import argparse
import logging
import time
from datetime import datetime, timezone

from google_play_scraper import Sort, reviews
from sqlalchemy import text

from db import get_engine, log_run

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

INSERT_SQL = text("""
    INSERT INTO raw.playstore_review
        (review_id, app_key, content, score, thumbs_up, app_version, reviewed_at, reply_content, replied_at)
    VALUES
        (:review_id, :app_key, :content, :score, :thumbs_up, :app_version, :reviewed_at, :reply_content, :replied_at)
    ON CONFLICT (review_id) DO NOTHING
""")


def _utc(dt):
    # Library mengembalikan datetime naive; di sini diasumsikan UTC (verifikasi dengan membandingkan
    # beberapa ulasan terbaru di Play Store). Selisih jam tidak memengaruhi analisis bulanan.
    return dt.replace(tzinfo=timezone.utc) if dt else None


def to_row(r, app_key):
    return {
        "review_id": r["reviewId"], "app_key": app_key, "content": r.get("content"),
        "score": r.get("score"), "thumbs_up": r.get("thumbsUpCount"),
        "app_version": r.get("appVersion") or r.get("reviewCreatedVersion"),
        "reviewed_at": _utc(r.get("at")),
        "reply_content": r.get("replyContent"), "replied_at": _utc(r.get("repliedAt")),
    }


def fetch_page(package_id, lang, country, count, token, retries=3):
    for attempt in range(1, retries + 1):
        try:
            return reviews(package_id, lang=lang, country=country, sort=Sort.NEWEST,
                           count=count, continuation_token=token)
        except Exception as exc:
            logging.warning("Percobaan %d/%d gagal: %s", attempt, retries, exc)
            time.sleep(5 * attempt)
    raise RuntimeError("Gagal mengambil ulasan setelah beberapa percobaan")


def fetch_batches(package_id, since, max_reviews, lang, country, batch=200, pause=1.5):
    """Generator: ulasan terbaru -> terlama sampai batas tanggal / jumlah."""
    token, total = None, 0
    while total < max_reviews:
        result, token = fetch_page(package_id, lang, country, min(batch, max_reviews - total), token)
        if not result:
            break
        if since:
            result = [r for r in result if r["at"] >= since]
            if not result:
                break
        total += len(result)
        yield result
        if token is None:
            break
        time.sleep(pause)


def count_rows(engine, app_key):
    with engine.connect() as c:
        return c.execute(text("SELECT count(*) FROM raw.playstore_review WHERE app_key = :k"),
                         {"k": app_key}).scalar()


def scrape_app(engine, app_key, package_id, since, max_reviews, lang, country):
    before, fetched = count_rows(engine, app_key), 0
    for batch in fetch_batches(package_id, since, max_reviews, lang, country):
        rows = [to_row(r, app_key) for r in batch]
        with engine.begin() as conn:
            conn.execute(INSERT_SQL, rows)
        fetched += len(rows)
        logging.info("%s: %d ulasan diambil", app_key, fetched)
    new = count_rows(engine, app_key) - before
    log_run(engine, "playstore", app_key, fetched, new, f"since={since.date() if since else None}")
    logging.info("%s selesai: %d diambil, %d baru", app_key, fetched, new)


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--app-key")
    g.add_argument("--all", action="store_true")
    p.add_argument("--since", default="2024-01-01", help="YYYY-MM-DD (default 2024-01-01)")
    p.add_argument("--max", type=int, default=20000)
    p.add_argument("--lang", default="id")
    p.add_argument("--country", default="id")
    a = p.parse_args()

    since = datetime.strptime(a.since, "%Y-%m-%d")
    engine = get_engine()
    q = "SELECT app_key, package_id FROM ref.app WHERE active AND left(app_key, 5) <> 'demo_'"
    params = {}
    if not a.all:
        q += " AND app_key = :k"
        params["k"] = a.app_key
    with engine.connect() as c:
        apps = c.execute(text(q), params).all()
    if not apps:
        raise SystemExit("App tidak ditemukan di ref.app. Isi package_id di data/apps.csv lalu jalankan load_reference.py.")
    for app_key, package_id in apps:
        scrape_app(engine, app_key, package_id, since, a.max, a.lang, a.country)


if __name__ == "__main__":
    main()
