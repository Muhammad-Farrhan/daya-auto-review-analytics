"""Sentimen.

1) rating_sentiment : sentimen dari bintang (1-2 negatif, 3 netral, 4-5 positif). Ini label utama di mart.
2) TransformerSentiment (opsional) : sentimen dari TEKS memakai model Hugging Face. Dipakai untuk
   pembanding/validasi, bukan pengganti rating. Perlu `pip install -r requirements-nlp.txt`.
"""
from __future__ import annotations

DEFAULT_MODEL = "w11wo/indonesian-roberta-base-sentiment-classifier"  # cek ketersediaan di Hugging Face


def rating_sentiment(score) -> tuple[str, float] | None:
    """Return (label, skor -1..1) atau None bila rating kosong."""
    if score is None or score != score:      # None / NaN
        return None
    s = int(score)
    if s <= 2:
        return "negative", (s - 3) / 2
    if s == 3:
        return "neutral", 0.0
    return "positive", (s - 3) / 2


def map_label(label: str) -> str:
    low = str(label).strip().lower()
    if "neg" in low:
        return "negative"
    if "pos" in low:
        return "positive"
    if "neu" in low:
        return "neutral"
    raise ValueError(
        f"Label model tidak dikenali: {label!r}. Buka model card di Hugging Face dan sesuaikan map_label()."
    )


class TransformerSentiment:
    def __init__(self, model_name: str = DEFAULT_MODEL, batch_size: int = 32):
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("Jalankan: pip install -r requirements-nlp.txt") from exc
        self.batch_size = batch_size
        self.pipe = pipeline("text-classification", model=model_name, truncation=True, max_length=256)

    def predict(self, texts: list[str]) -> list[tuple[str, float]]:
        outputs = self.pipe(list(texts), batch_size=self.batch_size)
        return [(map_label(o["label"]), float(o["score"])) for o in outputs]
