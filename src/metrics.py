"""Metrik evaluasi klasifikasi tanpa dependensi eksternal (akurasi, precision/recall/F1, macro-F1)."""
from __future__ import annotations

from collections import Counter


def classification_report(y_true, y_pred, labels=None) -> dict:
    if len(y_true) != len(y_pred):
        raise ValueError("Panjang y_true dan y_pred harus sama")
    if not y_true:
        raise ValueError("Data evaluasi kosong")
    labels = list(labels) if labels is not None else sorted(set(y_true) | set(y_pred))
    n = len(y_true)
    correct = sum(t == p for t, p in zip(y_true, y_pred))
    per_label = {}
    for lab in labels:
        tp = sum(t == lab and p == lab for t, p in zip(y_true, y_pred))
        fp = sum(t != lab and p == lab for t, p in zip(y_true, y_pred))
        fn = sum(t == lab and p != lab for t, p in zip(y_true, y_pred))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_label[lab] = {"precision": prec, "recall": rec, "f1": f1, "support": tp + fn}
    present = [l for l in labels if per_label[l]["support"] > 0]
    macro_f1 = sum(per_label[l]["f1"] for l in present) / len(present) if present else 0.0
    return {"n": n, "accuracy": correct / n, "macro_f1": macro_f1, "per_label": per_label}


def top_confusions(y_true, y_pred, k: int = 5) -> list[tuple[str, str, int]]:
    c = Counter((t, p) for t, p in zip(y_true, y_pred) if t != p)
    return [(t, p, n) for (t, p), n in c.most_common(k)]


def format_report(title: str, rep: dict) -> str:
    lines = [f"== {title} ==", f"n={rep['n']}  accuracy={rep['accuracy']:.3f}  macro_F1={rep['macro_f1']:.3f}"]
    lines.append(f"{'label':<24}{'prec':>7}{'rec':>7}{'f1':>7}{'n':>6}")
    for lab, m in rep["per_label"].items():
        lines.append(f"{lab:<24}{m['precision']:>7.2f}{m['recall']:>7.2f}{m['f1']:>7.2f}{m['support']:>6}")
    return "\n".join(lines)
