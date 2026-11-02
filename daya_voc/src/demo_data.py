"""Generator ulasan SINTETIS untuk menguji pipeline dan merancang layout dashboard sebelum data asli ada.

PENTING: data ini fiktif. Jangan pernah dipublikasikan atau dijadikan temuan analisis.
Aplikasi demo memakai app_key berawalan 'demo_' dan otomatis dikeluarkan dari ekspor Tableau.
"""
from __future__ import annotations

import hashlib
import random
from datetime import date, datetime, timedelta, timezone

DEMO_APPS = [
    # app_key, nama, dealer, wilayah, role, package_id, bobot topik (override)
    ("demo_focus", "Demo Focus App", "Demo Dealer A", "Wilayah A", "focus", "demo.focus",
     {"login_otp": 4.0, "booking_service": 3.0, "kpb_claim": 2.5, "app_bug_crash": 2.0}),
    ("demo_peer_a", "Demo Peer A", "Demo Dealer B", "Wilayah B", "peer", "demo.peer_a",
     {"parts_homeservice": 3.0, "ui_ux": 2.5, "booking_service": 2.0}),
    ("demo_peer_b", "Demo Peer B", "Demo Dealer C", "Wilayah C", "peer", "demo.peer_b",
     {"notification_reminder": 3.0, "promo_points": 2.5, "performance_slow": 2.0}),
]

VERSIONS = [("2.0.0", date(2024, 1, 1)), ("2.1.0", date(2024, 5, 15)), ("2.2.0", date(2024, 10, 10)),
            ("3.0.0", date(2025, 3, 1)), ("3.1.0", date(2025, 9, 1)), ("3.2.0", date(2026, 3, 10))]
START, END = date(2024, 1, 1), date(2026, 9, 30)

TEXTS = {
    "login_otp": (["gk bisa login terus, otp gak masuk masuk", "Lupa password tapi kode verifikasi tidak dikirim",
                   "login gagal terus padahal nomor sudah benar"],
                  ["login gampang, otp cepat masuk"]),
    "account_data": (["data motor saya tidak muncul di aplikasi", "nomor rangka tidak sesuai, susah tambah motor"],
                     ["daftar akun mudah, data motor langsung muncul"]),
    "booking_service": (["booking servis sering gagal, jadwal tidak tersedia", "sudah booking tapi tetap antri lama di bengkel"],
                        ["booking servis praktis, tidak perlu antri"]),
    "kpb_claim": (["klaim kpb gratis oli ditolak terus", "servis gratis kpb susah diklaim lewat aplikasi"],
                  ["klaim kpb mudah banget tinggal tunjukkan hp"]),
    "insurance_digital": (["status asuransi tidak update", "polis asuransi tidak muncul"],
                          ["fitur asuransi digital membantu"]),
    "parts_homeservice": (["pesanan sparepart tidak diproses", "home service susah dipesan, pembayaran gagal"],
                          ["beli parts asli lewat aplikasi praktis"]),
    "promo_points": (["poin hangus tanpa pemberitahuan", "promo diskon servis tidak bisa dipakai"],
                     ["banyak promo dan voucher menarik"]),
    "app_bug_crash": (["aplikasi error terus setelah update", "sering crash, layar putih saat dibuka"],
                      ["tidak ada error, lancar"]),
    "performance_slow": (["aplikasi lemot banget, loading lama", "berat dan sering lag"],
                         ["ringan dan cepat"]),
    "ui_ux": (["tampilan membingungkan, menu ribet", "fitur kurang jelas, susah digunakan"],
              ["tampilan bagus, mudah digunakan"]),
    "notification_reminder": (["notifikasi pengingat servis tidak muncul", "tidak ada notif kpb habis"],
                              ["pengingat servis sangat membantu"]),
    "dealer_workshop": (["mekanik di bengkel kurang ramah, pelayanan lambat", "cs susah dihubungi"],
                        ["pelayanan bengkel ramah dan cepat"]),
    "general_praise": ([], ["bagus banget aplikasinya mantap", "sangat membantu, terima kasih", "oke recommended"]),
}
TOPICS = list(TEXTS)
SUFFIXES = ["", "", "", " tolong diperbaiki", " mohon perbaikan", " bgt", "!!!", " 😡"]


def version_on(d: date) -> str:
    current = VERSIONS[0][0]
    for v, start in VERSIONS:
        if start <= d:
            current = v
    return current


def generate_reviews(app_key: str, n: int, seed: int, topic_boost: dict | None = None) -> list[dict]:
    rng = random.Random(f"{seed}-{app_key}")
    boost = topic_boost or {}
    weights = [boost.get(t, 1.0) for t in TOPICS]
    span = (END - START).days
    rows = []
    for i in range(n):
        d = START + timedelta(days=rng.randrange(span + 1))
        ts = datetime(d.year, d.month, d.day, rng.randrange(24), rng.randrange(60), tzinfo=timezone.utc)
        version = version_on(d)
        p_neg = 0.45
        if version == "3.0.0" and (d - date(2025, 3, 1)).days < 45:   # gelombang keluhan setelah rilis besar
            p_neg = 0.8
        topic = rng.choices(TOPICS, weights=weights, k=1)[0]
        neg_texts, pos_texts = TEXTS[topic]
        negative = bool(neg_texts) and rng.random() < p_neg
        if negative:
            content = rng.choice(neg_texts) + rng.choice(SUFFIXES)
            score = rng.choice([1, 1, 1, 2, 2, 3])
        else:
            content = rng.choice(pos_texts or neg_texts)
            score = rng.choice([4, 5, 5, 5])
        reply, replied_at = None, None
        if negative and rng.random() < 0.25:
            reply = "Mohon maaf atas ketidaknyamanannya. Silakan hubungi layanan pelanggan kami."
            replied_at = ts + timedelta(hours=rng.expovariate(1 / 30))
        rid = hashlib.md5(f"{app_key}-{i}-{seed}".encode()).hexdigest()[:16]
        rows.append({
            "review_id": f"demo-{app_key}-{rid}", "app_key": app_key, "content": content, "score": score,
            "thumbs_up": rng.choice([0, 0, 0, 0, 1, 2, 5]) if negative else 0,
            "app_version": version, "reviewed_at": ts, "reply_content": reply, "replied_at": replied_at,
        })
    return rows
