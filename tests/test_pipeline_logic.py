"""Uji alur murni: data demo -> cleaning -> pelabelan topik -> sampling gold -> validasi gold."""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import _path  # noqa: F401
from clean_reviews import CLEAN_COLUMNS, process_dataframe
from demo_data import DEMO_APPS, END, START, generate_reviews, version_on
from label_reviews import build_topic_rows
from csvio import read_csv_records
from sampling import stratified_sample, validate_gold
from textproc import load_slang
from topics import load_lexicon

SLANG = load_slang(_path.ROOT / "data" / "normalization.csv")
RULES = load_lexicon(_path.ROOT / "data" / "topic_lexicon.csv")


def raw_df(app_key="demo_focus", n=300, seed=1):
    boost = next(a[6] for a in DEMO_APPS if a[0] == app_key)
    return pd.DataFrame(generate_reviews(app_key, n, seed, boost))


class DemoDataTests(unittest.TestCase):
    def test_generator_shape_and_privacy(self):
        df = raw_df()
        self.assertEqual(len(df), 300)
        self.assertTrue(df["review_id"].is_unique)
        self.assertTrue(df["review_id"].str.startswith("demo-").all())
        self.assertTrue(df["score"].between(1, 5).all())
        self.assertNotIn("userName", df.columns)
        d = df["reviewed_at"].dt.date
        self.assertTrue(((d >= START) & (d <= END)).all())

    def test_generator_is_deterministic(self):
        a = raw_df(seed=3)
        b = raw_df(seed=3)
        self.assertTrue(a.equals(b))

    def test_versions(self):
        self.assertEqual(version_on(START), "2.0.0")
        self.assertEqual(version_on(END), "3.2.0")


class CleanAndLabelTests(unittest.TestCase):
    def test_clean_columns_and_flags(self):
        clean = process_dataframe(raw_df(), SLANG)
        self.assertEqual(list(clean.columns), CLEAN_COLUMNS)
        self.assertEqual(len(clean), 300)
        self.assertTrue(clean["has_text"].all())
        self.assertTrue((clean["lang_flag"] != "en").all())

    def test_topics_recovered_on_synthetic_text(self):
        """Teks sintetik dibuat per topik; kamus harus menemukan topiknya kembali (bukan 'other')."""
        from demo_data import TEXTS
        clean = []
        for topic, (neg, pos) in TEXTS.items():
            for sent in neg:
                clean.append({"review_id": f"{topic}|{sent}", "text_norm": process_dataframe(
                    pd.DataFrame([{"review_id": "x", "app_key": "a", "content": sent, "score": 1, "thumbs_up": 0,
                                   "app_version": "1", "reviewed_at": None, "replied_at": None}]), SLANG
                ).loc[0, "text_norm"], "expected": topic})
        rows = build_topic_rows(pd.DataFrame(clean), RULES, "lexicon_v1")
        primary = {r["review_id"]: r["topic"] for r in rows if r["is_primary"]}
        ok = sum(primary[c["review_id"]] == c["expected"] for c in clean)
        accuracy = ok / len(clean)
        wrong = [(c["review_id"], primary[c["review_id"]]) for c in clean if primary[c["review_id"]] != c["expected"]]
        self.assertGreaterEqual(accuracy, 0.85, f"salah: {wrong}")

    def test_exactly_one_primary_per_review(self):
        clean = process_dataframe(raw_df(n=120), SLANG)
        rows = build_topic_rows(clean, RULES, "lexicon_v1")
        per_review = pd.DataFrame(rows).groupby("review_id")["is_primary"].sum()
        self.assertTrue((per_review == 1).all())
        self.assertEqual(set(per_review.index), set(clean["review_id"]))


class GoldTests(unittest.TestCase):
    def test_stratified_sample(self):
        frames = [process_dataframe(raw_df(k, 400, 2), SLANG) for k in ("demo_focus", "demo_peer_a")]
        df = pd.concat(frames)
        s = stratified_sample(df, n_per_app=50, seed=1)
        self.assertLessEqual(len(s), 100)
        self.assertEqual(set(s["app_key"]), {"demo_focus", "demo_peer_a"})
        self.assertTrue(s["review_id"].is_unique)
        self.assertEqual(s.groupby("app_key").size().max(), 50)

    def test_validate_gold(self):
        df = pd.DataFrame({
            "review_id": ["1", "2", "3", "4"],
            "gold_sentiment": ["negative", "bad", "", "Positive "],
            "gold_topic": ["login_otp", "login_otp", "", "ui_ux"],
        })
        ok, errors = validate_gold(df, {"login_otp", "ui_ux"})
        self.assertEqual(list(ok["review_id"]), ["1", "4"])
        self.assertEqual(len(errors), 1)
        self.assertIn("2", errors[0])

    def test_validate_gold_unknown_topic(self):
        df = pd.DataFrame({"review_id": ["1"], "gold_sentiment": ["neutral"], "gold_topic": ["typo_topic"]})
        ok, errors = validate_gold(df, {"login_otp"})
        self.assertTrue(ok.empty)
        self.assertEqual(len(errors), 1)


class ReferenceCsvTests(unittest.TestCase):
    def test_blank_cells_become_none(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.csv"
            p.write_text("a,b\n1,\n,2\n", encoding="utf-8")
            recs = read_csv_records(p)
        self.assertEqual(recs, [{"a": "1", "b": None}, {"a": None, "b": "2"}])

    def test_shipped_reference_files(self):
        apps = read_csv_records(_path.ROOT / "data" / "apps.csv")
        self.assertEqual(sum(a["role"] == "focus" for a in apps), 1, "harus ada tepat satu aplikasi focus")
        self.assertEqual(read_csv_records(_path.ROOT / "data" / "events.csv"), [])

    def test_package_ids_are_valid(self):
        """Package ID wajib terisi dan berformat benar (bukan URL mentah, bukan kosong)."""
        apps = read_csv_records(_path.ROOT / "data" / "apps.csv")
        for a in apps:
            pkg = a.get("package_id") or ""
            self.assertTrue(pkg, f"{a['app_key']}: package_id kosong")
            self.assertNotIn("&", pkg, f"{a['app_key']}: package_id masih mengandung '&' (hapus '&hl=id')")
            self.assertNotIn("?", pkg, f"{a['app_key']}: package_id masih mengandung '?'")
            self.assertFalse(pkg.startswith("id="), f"{a['app_key']}: package_id diawali 'id=' (hapus prefiks)")
            # minimal 2 titik pemisah, mis. id.co.dayagroup
            self.assertGreaterEqual(pkg.count("."), 2, f"{a['app_key']}: package_id '{pkg}' formatnya aneh")
            self.assertNotIn(" ", pkg, f"{a['app_key']}: package_id tidak boleh ada spasi")


if __name__ == "__main__":
    unittest.main()
