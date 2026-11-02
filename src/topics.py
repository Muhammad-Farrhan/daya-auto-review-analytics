"""Klasifikasi topik ulasan berbasis kamus kata kunci (mudah dijelaskan & diaudit).

- Satu ulasan boleh punya banyak topik (multi-label); 'primary' = topik dengan kecocokan terbanyak.
- Topik keluhan didahulukan daripada 'general_praise' saat menentukan primary.
- Kata kunci yang bertanda negatable=1 diabaikan bila didahului kata negasi (mis. 'tidak bagus').
- Kata kunci non-exact boleh diikuti imbuhan pendek (login -> loginnya, booking -> bookingan).
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PRAISE_TOPICS = {"general_praise"}
NEGATORS = {"tidak", "bukan", "kurang", "belum", "jangan", "tanpa"}


@dataclass(frozen=True)
class Rule:
    topic: str
    keyword: str
    negatable: bool
    pattern: re.Pattern


def load_lexicon(path: str | Path) -> list[Rule]:
    rules: list[Rule] = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            kw = (row.get("keyword") or "").strip().lower()
            topic = (row.get("topic") or "").strip()
            if not kw or not topic or kw.startswith("#"):
                continue
            exact = str(row.get("exact", "0")).strip() == "1"
            negatable = str(row.get("negatable", "0")).strip() == "1"
            body = re.escape(kw).replace(r"\ ", r"\s+")
            tail = "" if exact else r"[a-z]{0,4}"
            pat = re.compile(r"(?<![a-z0-9])" + body + tail + r"(?![a-z0-9])")
            rules.append(Rule(topic, kw, negatable, pat))
    if not rules:
        raise ValueError(f"Leksikon kosong: {path}")
    return rules


def _negated(text: str, start: int) -> bool:
    prev = text[:start].split()[-2:]
    return any(tok in NEGATORS for tok in prev)


def classify(text_norm: str | None, rules: list[Rule]) -> tuple[str, list[str]]:
    """Return (primary_topic, all_topics). Tanpa kecocokan -> ('other', ['other'])."""
    if not text_norm:
        return "other", ["other"]
    order: dict[str, int] = {}
    for r in rules:
        order.setdefault(r.topic, len(order))
    hits: dict[str, int] = defaultdict(int)
    for r in rules:
        for m in r.pattern.finditer(text_norm):
            if r.negatable and _negated(text_norm, m.start()):
                continue
            hits[r.topic] += 1
    if not hits:
        return "other", ["other"]
    issue_hits = {t: c for t, c in hits.items() if t not in PRAISE_TOPICS}
    pool = issue_hits or dict(hits)
    primary = max(pool, key=lambda t: (pool[t], -order[t]))
    all_topics = sorted(hits, key=lambda t: (-hits[t], order[t]))
    return primary, all_topics
