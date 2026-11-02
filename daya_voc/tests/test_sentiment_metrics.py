import unittest

import _path  # noqa: F401
from metrics import classification_report, top_confusions
from sentiment import map_label, rating_sentiment


class SentimentTests(unittest.TestCase):
    def test_rating_rule(self):
        self.assertEqual(rating_sentiment(1), ("negative", -1.0))
        self.assertEqual(rating_sentiment(2)[0], "negative")
        self.assertEqual(rating_sentiment(3), ("neutral", 0.0))
        self.assertEqual(rating_sentiment(4)[0], "positive")
        self.assertEqual(rating_sentiment(5), ("positive", 1.0))
        self.assertIsNone(rating_sentiment(None))
        self.assertIsNone(rating_sentiment(float("nan")))

    def test_map_label(self):
        self.assertEqual(map_label("Positive"), "positive")
        self.assertEqual(map_label("NEGATIVE"), "negative")
        self.assertEqual(map_label("neutral"), "neutral")
        with self.assertRaises(ValueError):
            map_label("LABEL_0")


class MetricsTests(unittest.TestCase):
    def test_report(self):
        rep = classification_report(["a", "a", "b", "b"], ["a", "b", "b", "b"])
        self.assertAlmostEqual(rep["accuracy"], 0.75)
        self.assertAlmostEqual(rep["per_label"]["a"]["precision"], 1.0)
        self.assertAlmostEqual(rep["per_label"]["a"]["recall"], 0.5)
        self.assertAlmostEqual(rep["per_label"]["b"]["precision"], 2 / 3)
        self.assertAlmostEqual(rep["per_label"]["b"]["recall"], 1.0)
        self.assertAlmostEqual(rep["per_label"]["a"]["f1"], 2 * 1.0 * 0.5 / 1.5)

    def test_confusions(self):
        c = top_confusions(["a", "a", "b"], ["b", "b", "a"], k=2)
        self.assertEqual(c[0], ("a", "b", 2))

    def test_errors(self):
        with self.assertRaises(ValueError):
            classification_report([], [])
        with self.assertRaises(ValueError):
            classification_report(["a"], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
