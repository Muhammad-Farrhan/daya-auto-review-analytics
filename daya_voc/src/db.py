"""Koneksi database & helper kecil. Hanya dipakai oleh skrip CLI (bukan modul murni)."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL belum diatur. Salin .env.example menjadi .env lalu sesuaikan.")
    return create_engine(url, future=True)


def records(df):
    """DataFrame -> list of dict dengan NaN/NaT diganti None dan tipe numpy diganti tipe Python."""
    return df.astype(object).where(df.notna(), None).to_dict("records")


def log_run(engine, source, target, fetched, new, note=None):
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO ops.scrape_log (source, target, rows_fetched, rows_new, note)
                    VALUES (:s, :t, :f, :n, :note)"""),
            {"s": source, "t": target, "f": fetched, "n": new, "note": note},
        )
