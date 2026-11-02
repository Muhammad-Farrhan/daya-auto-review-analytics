"""Jalankan file SQL ke database (alternatif psql, cocok untuk Windows).

Contoh:
  python src/init_db.py                       # 01_schema.sql lalu 02_marts.sql
  python src/init_db.py sql/02_marts.sql      # hanya perbarui view
"""
import sys
from pathlib import Path

from db import get_engine

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILES = ["sql/01_schema.sql", "sql/02_marts.sql"]


def run_sql_file(engine, path: Path):
    sql = path.read_text(encoding="utf-8")
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.execute(sql)          # tanpa parameter -> tanda % di SQL tidak diinterpretasi
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()
    print(f"OK  {path.relative_to(ROOT)}")


def main():
    files = sys.argv[1:] or DEFAULT_FILES
    engine = get_engine()
    for f in files:
        p = (ROOT / f) if not Path(f).is_absolute() else Path(f)
        if not p.exists():
            raise SystemExit(f"File tidak ditemukan: {p}")
        run_sql_file(engine, p)


if __name__ == "__main__":
    main()
