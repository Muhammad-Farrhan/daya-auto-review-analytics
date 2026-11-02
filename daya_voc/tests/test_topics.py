import csv
import unittest

import _path  # noqa: F401
from textproc import load_slang, normalize_text
from topics import classify, load_lexicon

SLANG = load_slang(_path.ROOT / "data" / "normalization.csv")
RULES = load_lexicon(_path.ROOT / "data" / "topic_lexicon.csv")


def run(text):
    return classify(normalize_text(text, SLANG), RULES)


class TopicTests(unittest.TestCase):
    def test_login_otp(self):
        primary, allt = run("Gak bisa login terus, OTP gak masuk-masuk")
        self.assertEqual(primary, "login_otp")

    def test_booking_beats_praise(self):
        primary, allt = run("Aplikasi bagus, booking servis gampang, tidak perlu antri")
        self.assertEqual(primary, "booking_service")
        self.assertIn("general_praise", allt)

    def test_bug_primary_and_multilabel(self):
        primary, allt = run("Aplikasi lemot dan sering crash habis update")
        self.assertEqual(primary, "app_bug_crash")
        self.assertIn("performance_slow", allt)

    def test_kpb(self):
        primary, _ = run("Klaim KPB gratis oli susah, ditolak terus")
        self.assertEqual(primary, "kpb_claim")

    def test_pure_praise(self):
        primary, allt = run("Bagus banget, sangat membantu")
        self.assertEqual(primary, "general_praise")

    def test_negated_praise_is_not_praise(self):
        primary, allt = run("tidak bagus")
        self.assertEqual(primary, "other")

    def test_dealer(self):
        primary, _ = run("Mekanik di AHASS ramah tapi antrian lama")
        self.assertEqual(primary, "dealer_workshop")

    def test_notification(self):
        primary, _ = run("Notifikasi pengingat servis tidak muncul")
        self.assertEqual(primary, "notification_reminder")

    def test_no_false_positive_lag_in_lagi(self):
        primary, allt = run("saya coba lagi nanti")
        self.assertNotIn("performance_slow", allt)

    def test_suffix_tolerance(self):
        primary, _ = run("loginnya susah")
        self.assertEqual(primary, "login_otp")

    def test_empty(self):
        self.assertEqual(classify("", RULES), ("other", ["other"]))
        self.assertEqual(classify(None, RULES), ("other", ["other"]))

    def test_lexicon_topics_match_schema_seed(self):
        schema = (_path.ROOT / "sql" / "01_schema.sql").read_text(encoding="utf-8")
        used = {r.topic for r in RULES}
        for t in used:
            self.assertIn(f"'{t}'", schema, f"topik {t} tidak ada di 01_schema.sql")


class LexiconFileTests(unittest.TestCase):
    def test_columns_and_flags(self):
        with open(_path.ROOT / "data" / "topic_lexicon.csv", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 100)
        for r in rows:
            self.assertIn(r["exact"], ("0", "1"))
            self.assertIn(r["negatable"], ("0", "1"))
            self.assertEqual(r["keyword"], r["keyword"].strip().lower())


if __name__ == "__main__":
    unittest.main()
