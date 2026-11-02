"""Muat data referensi dari CSV (diisi manual) ke tabel ref.*

- data/apps.csv           -> ref.app            (baris tanpa package_id dilewati)
- data/events.csv         -> ref.event
- data/feature_audit.csv  -> ref.feature_audit  (baris tanpa 'available' dilewati)
- data/rice_inputs.csv    -> ref.rice_input     (baris tanpa 'reach' dilewati)

Jalankan: python src/load_reference.py
"""
import logging
from pathlib import Path

from sqlalchemy import text

from csvio import read_csv_records, to_bool, to_num
from db import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
DATA = Path(__file__).resolve().parent.parent / "data"


def load_apps(conn):
    rows = read_csv_records(DATA / "apps.csv")
    valid = [r for r in rows if r.get("package_id")]
    skipped = len(rows) - len(valid)
    if skipped:
        logging.warning("%d aplikasi dilewati: package_id kosong (isi dari URL Play Store ?id=...)", skipped)
    for r in valid:
        role = (r.get("role") or "peer").strip().lower()
        if role not in ("focus", "peer", "reference"):
            raise SystemExit(f"role tidak valid untuk {r['app_key']}: {role}")
        conn.execute(text("""
            INSERT INTO ref.app (app_key, app_name, main_dealer, region, role, package_id, active)
            VALUES (:app_key, :app_name, :main_dealer, :region, :role, :package_id, :active)
            ON CONFLICT (app_key) DO UPDATE SET
              app_name = EXCLUDED.app_name, main_dealer = EXCLUDED.main_dealer, region = EXCLUDED.region,
              role = EXCLUDED.role, package_id = EXCLUDED.package_id, active = EXCLUDED.active
        """), {**r, "role": role, "active": to_bool(r.get("active"))})
    logging.info("ref.app: %d aplikasi", len(valid))


def load_events(conn):
    rows = [r for r in read_csv_records(DATA / "events.csv") if r.get("event_date")]
    for r in rows:
        if not r.get("source_url") or not r.get("description"):
            raise SystemExit("events.csv: description dan source_url wajib diisi (jejak sumber).")
        conn.execute(text("""
            INSERT INTO ref.event (event_date, event_type, app_key, description, source_url)
            VALUES (:event_date, :event_type, :app_key, :description, :source_url)
            ON CONFLICT DO NOTHING
        """), r)
    logging.info("ref.event: %d peristiwa", len(rows))


def load_feature_audit(conn):
    rows = [r for r in read_csv_records(DATA / "feature_audit.csv") if r.get("available") is not None]
    for r in rows:
        conn.execute(text("""
            INSERT INTO ref.feature_audit (app_key, feature, available, notes, audited_at)
            VALUES (:app_key, :feature, :available, :notes, :audited_at)
            ON CONFLICT (app_key, feature) DO UPDATE SET
              available = EXCLUDED.available, notes = EXCLUDED.notes, audited_at = EXCLUDED.audited_at
        """), {**r, "available": to_bool(r["available"])})
    logging.info("ref.feature_audit: %d baris", len(rows))


def load_rice(conn):
    rows = [r for r in read_csv_records(DATA / "rice_inputs.csv") if r.get("reach") is not None]
    for r in rows:
        conn.execute(text("""
            INSERT INTO ref.rice_input (topic, reach, impact, confidence, effort, notes)
            VALUES (:topic, :reach, :impact, :confidence, :effort, :notes)
            ON CONFLICT (topic) DO UPDATE SET
              reach = EXCLUDED.reach, impact = EXCLUDED.impact, confidence = EXCLUDED.confidence,
              effort = EXCLUDED.effort, notes = EXCLUDED.notes
        """), {**r, "reach": to_num(r["reach"]), "impact": to_num(r.get("impact")),
               "confidence": to_num(r.get("confidence")), "effort": to_num(r.get("effort"))})
    logging.info("ref.rice_input: %d baris", len(rows))


def main():
    engine = get_engine()
    with engine.begin() as conn:
        load_apps(conn)
        load_events(conn)
        load_feature_audit(conn)
        load_rice(conn)
    logging.info("Data referensi dimuat.")


if __name__ == "__main__":
    main()
