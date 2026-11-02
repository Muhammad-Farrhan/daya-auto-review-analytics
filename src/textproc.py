"""Pembersihan & normalisasi teks ulasan berbahasa Indonesia.

Murni Python (tanpa database / library berat) supaya mudah diuji.

Dua keluaran teks:
- text_clean : untuk dibaca manusia (URL dibuang, data pribadi disamarkan: [EMAIL], [PHONE], [ID])
- text_norm  : untuk analisis (huruf kecil, tanpa emoji/tanda baca, huruf berulang diringkas,
               singkatan/bahasa gaul dinormalisasi lewat data/normalization.csv)
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

URL_RE = re.compile(r"https?://\S+|www\.\S+")
EMAIL_RE = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+62|62|0)8\d{7,12}(?!\d)")
LONGNUM_RE = re.compile(r"(?<!\d)\d{8,}(?!\d)")
PLACEHOLDER_RE = re.compile(r"\[(?:phone|email|id|url)\]", re.IGNORECASE)
EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"   # emoji & piktograf
    "\U00002600-\U000027BF"   # simbol misc + dingbats
    "\U0000FE00-\U0000FE0F"   # variation selector
    "\U0000200D"              # zero-width joiner
    "]+"
)
REPEAT_RE = re.compile(r"([a-z])\1{2,}")      # 'bagusss' -> 'bagus'
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")
SPACE_RE = re.compile(r"\s+")

ID_STOP = {
    "yang", "dan", "di", "ini", "itu", "tidak", "saya", "untuk", "dengan", "bisa", "ada",
    "aplikasi", "nya", "sudah", "belum", "tapi", "karena", "kalau", "jadi", "dari", "sama",
    "masih", "terus", "banget", "sekali", "lebih", "kurang", "mau", "harus", "saat", "atau",
    "tolong", "mohon", "sangat", "bagus", "servis", "motor", "honda", "ga", "gak", "gk",
    "tdk", "udah", "udh", "yg", "dgn", "bgt", "aja", "saja", "lagi", "kok", "nih", "deh",
}
EN_STOP = {
    "the", "is", "are", "was", "this", "that", "it", "not", "very", "good", "bad", "great",
    "nice", "cannot", "cant", "please", "fix", "why", "doesnt", "dont", "work", "works",
    "but", "for", "you", "with", "have", "has", "when", "too", "so", "really", "useful",
    "easy", "slow",
}


def mask_pii(text: str) -> str:
    """Buang URL dan samarkan email / nomor telepon / deretan angka panjang."""
    t = URL_RE.sub(" ", text)
    t = EMAIL_RE.sub("[EMAIL]", t)
    t = PHONE_RE.sub("[PHONE]", t)
    t = LONGNUM_RE.sub("[ID]", t)
    return SPACE_RE.sub(" ", t).strip()


def load_slang(path: str | Path) -> dict[str, str]:
    """Baca kamus normalisasi (kolom: raw,normal)."""
    mapping: dict[str, str] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            raw = (row.get("raw") or "").strip().lower()
            normal = (row.get("normal") or "").strip().lower()
            if raw and normal:
                mapping[raw] = normal
    return mapping


def _base_tokens(text: str) -> list[str]:
    """Teks -> token huruf kecil (belum dipetakan lewat kamus gaul)."""
    t = text.lower()
    t = PLACEHOLDER_RE.sub(" ", t)
    t = URL_RE.sub(" ", t)
    t = EMOJI_RE.sub(" ", t)
    t = REPEAT_RE.sub(r"\1", t)
    t = NON_ALNUM_RE.sub(" ", t)
    return t.split()


def normalize_text(text: str | None, slang: dict[str, str] | None = None) -> str:
    if not text:
        return ""
    tokens = _base_tokens(text)
    if slang:
        tokens = [slang.get(tok, tok) for tok in tokens]
    return " ".join(" ".join(tokens).split())


def guess_language(text: str | None) -> str:
    """Tebakan kasar: 'id', 'en', atau 'unk' (terlalu pendek). Cukup untuk menandai ulasan berbahasa Inggris."""
    if not text:
        return "unk"
    tokens = [re.sub(r"[^a-z']", "", tok.replace("'", "")) for tok in text.lower().split()]
    tokens = [t for t in tokens if t]
    id_hits = sum(t in ID_STOP for t in tokens)
    en_hits = sum(t in EN_STOP for t in tokens)
    if en_hits >= 2 and en_hits > id_hits:
        return "en"
    if len(tokens) < 3 and id_hits == 0:
        return "unk"
    return "id"


def process_text(text: str | None, slang: dict[str, str] | None = None) -> dict:
    """Satu ulasan -> dict kolom teks untuk tabel clean.review."""
    raw = text or ""
    text_clean = mask_pii(raw)
    text_norm = normalize_text(text_clean, slang)
    n_words = len(text_norm.split()) if text_norm else 0
    return {
        "text_clean": text_clean,
        "text_norm": text_norm,
        "n_words": n_words,
        "has_text": len(text_norm) >= 3,
        "lang_flag": guess_language(text_clean),
    }
