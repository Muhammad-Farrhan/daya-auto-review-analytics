"""Pembaca CSV referensi (murni, tanpa database)."""
from pathlib import Path

import pandas as pd

TRUE = {"true", "1", "yes", "ya", "y"}


def read_csv_records(path: Path) -> list[dict]:
    """Baca CSV; sel kosong menjadi None."""
    path = Path(path)
    if not path.exists():
        return []
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df.astype(object).where(df != "", None)
    return df.to_dict("records")


def to_bool(v, default=True):
    return default if v is None else str(v).strip().lower() in TRUE


def to_num(v):
    return None if v is None else float(v)
