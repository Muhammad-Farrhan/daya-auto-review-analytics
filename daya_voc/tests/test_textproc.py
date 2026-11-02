import unittest

import _path  # noqa: F401
from textproc import guess_language, load_slang, mask_pii, normalize_text, process_text

SLANG = load_slang(_path.ROOT / "data" / "normalization.csv")


class TextProcTests(unittest.TestCase):
    def test_normalize_slang_repeat_emoji_punct(self):
        out = normalize_text("Bagusssss bangeeet 😍😍 yg ini, gk bisa login!!!", SLANG)
        self.assertEqual(out, "bagus banget yang ini tidak bisa login")

    def test_service_mapped_to_servis(self):
        self.assertEqual(normalize_text("Booking service gampang", SLANG), "booking servis gampang")

    def test_pii_masked(self):
        t = mask_pii("hubungi 081234567890 atau a.b@mail.com nomor rangka 12345678901 https://x.co/abc")
        self.assertIn("[PHONE]", t)
        self.assertIn("[EMAIL]", t)
        self.assertIn("[ID]", t)
        self.assertNotIn("081234567890", t)
        self.assertNotIn("http", t)

    def test_placeholders_not_leaking_into_norm(self):
        r = process_text("telp 081234567890 error terus", SLANG)
        self.assertNotIn("phone", r["text_norm"])
        self.assertEqual(r["text_norm"], "telp error terus")

    def test_empty_and_none(self):
        for v in (None, "", "   ", "😀😀"):
            r = process_text(v, SLANG)
            self.assertFalse(r["has_text"])
            self.assertEqual(r["n_words"], 0)

    def test_language_flag(self):
        self.assertEqual(guess_language("this app is very good but cannot login"), "en")
        self.assertEqual(guess_language("aplikasi bagus tapi tidak bisa login"), "id")
        self.assertEqual(guess_language("ok"), "unk")

    def test_process_text_fields(self):
        r = process_text("Mantap, booking servis gampang", SLANG)
        self.assertTrue(r["has_text"])
        self.assertEqual(r["n_words"], 4)
        self.assertEqual(r["lang_flag"], "id")


if __name__ == "__main__":
    unittest.main()
