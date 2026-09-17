"""Unit tests for tools.normalize."""

import unittest
from tools import normalize

CONFIG = normalize.DEFAULTS


class TestNormalize(unittest.TestCase):
    def test_arabic_yeh_kaf(self):
        text = "كتاب يزدان"
        out, findings = normalize.normalize_text("test.md", text, CONFIG)
        self.assertEqual(out, "کتاب یزدان")
        self.assertEqual(len(findings), 2)

    def test_zwnj_mi_and_plural(self):
        text = "می رود و کتاب ها را می خواند."
        out, _ = normalize.normalize_text("test.md", text, CONFIG)
        self.assertEqual(out, "می‌رود و کتاب‌ها را می‌خواند.")

    def test_quotes_to_guillemets(self):
        text = 'او گفت: "این یک آزمون است."'
        out, _ = normalize.normalize_text("test.md", text, CONFIG)
        self.assertEqual(out, "او گفت: «این یک آزمون است.»")

    def test_protected_spans(self):
        text = 'متن فارسی `كتاب يزدان` و ```\nكتاب يزدان\n```'
        out, _ = normalize.normalize_text("test.md", text, CONFIG)
        self.assertIn("`كتاب يزدان`", out)
        self.assertIn("```\nكتاب يزدان\n```", out)

    def test_bidi_override_detected(self):
        # Text with Unicode RLO (U+202E)
        text = "متن عادی \u202e متن معکوس"
        _, findings = normalize.normalize_text("test.md", text, CONFIG)
        bidi = [f for f in findings if f.rule == "bidi"]
        self.assertEqual(len(bidi), 1)


if __name__ == "__main__":
    unittest.main()
