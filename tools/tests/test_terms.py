"""Unit tests for tools.check_terms."""

import unittest
from pathlib import Path
import tempfile

from tools import check_terms

TEST_CONFIG_COMMENTATORS = {
    "WANG PI": "وانگ پی",
    "HO-SHANG KUNG": "هو-شانگ کونگ",
    "SU CH’E": "سو چِه",
    "TE-CH’ING": "ده‌چینگ",
}

TEST_CONFIG_DISALLOWED = {
    r"(?<!\p{Arabic})تائو(?!\p{Arabic})": {
        "reason": "تائو disallowed; use canonical transliteration «دائو»",
        "replacement": "دائو",
    },
    r"(?<!\p{Arabic})تقوا(?!\p{Arabic})": {
        "reason": "تقوا disallowed for Te (Virtue); use «دِ» or «فضیلت»"
    },
    r"انفعال[ \t]+محض": {
        "reason": "انفعال محض disallowed for Wu-wei; use «بی‌عملی»",
        "replacement": "بی‌عملی",
    },
    r"کنده[ \t]+درخت": {
        "reason": "کنده درخت disallowed for P’u; use «چوب نتراشیده»",
        "replacement": "چوب نتراشیده",
    },
    r"عرش[ \t]+و[ \t]+فرش": {
        "reason": "عرش و فرش disallowed for Heaven and Earth; use «آسمان و زمین»",
        "replacement": "آسمان و زمین",
    },
    r"ده[ \t]+هزار[ \t]+شی(?:ء|ء|ی)": {
        "reason": "ده هزار شیء disallowed for Ten thousand things; use «ده‌هزار موجود»",
        "replacement": "ده‌هزار موجود",
    },
    r"راه[ \t]+فناناپذیر": {
        "reason": "راه فناناپذیر disallowed for Immortal Way; use «راه جاودان»",
        "replacement": "راه جاودان",
    },
    r"ده[ \t]+هزار": {
        "reason": "Missing ZWNJ in compound number «ده‌هزار»",
        "replacement": "ده‌هزار",
    },
    r"دست[ \t]+نوشته": {
        "reason": "Missing ZWNJ in compound «دست‌نوشته»",
        "replacement": "دست‌نوشته",
    },
}


class TestCheckTerms(unittest.TestCase):
    def setUp(self):
        self.canonical_names = set(TEST_CONFIG_COMMENTATORS.values())
        self.compiled_disallowed = check_terms.compile_disallowed(TEST_CONFIG_DISALLOWED)

    def test_clean_text_passes(self):
        text = (
            "# ۱\n\n"
            "راهی که بتوان آن را پیمود، راه جاودان نیست.\n\n"
            "**وانگ پی** می‌گوید:\n\n"
            "دائو فراتر از نام‌هاست. انسان فرزانه در بی‌عملی می‌زید.\n"
            "آسمان و زمین و ده‌هزار موجود از چوب نتراشیده زاده می‌شوند.\n"
        )
        comm_findings = check_terms.check_commentators(
            "test.md", text, self.canonical_names, TEST_CONFIG_COMMENTATORS
        )
        term_findings = check_terms.check_disallowed_terms(
            "test.md", text, self.compiled_disallowed
        )
        self.assertEqual(comm_findings, [])
        self.assertEqual(term_findings, [])

    def test_disallowed_terms_detected(self):
        text = (
            "راه فناناپذیر همان تائو است.\n"
            "عرش و فرش و ده هزار شیء با تقوا پدید می‌آیند.\n"
            "پو همان کنده درخت است و وو-وی یعنی انفعال محض.\n"
        )
        findings = check_terms.check_disallowed_terms("test.md", text, self.compiled_disallowed)
        rules = [f.message for f in findings]
        self.assertTrue(any("تائو" in m for m in rules))
        self.assertTrue(any("راه فناناپذیر" in m for m in rules))
        self.assertTrue(any("عرش و فرش" in m for m in rules))
        self.assertTrue(any("ده هزار شیء" in m for m in rules))
        self.assertTrue(any("تقوا" in m for m in rules))
        self.assertTrue(any("کنده درخت" in m for m in rules))
        self.assertTrue(any("انفعال محض" in m for m in rules))

    def test_commentator_attributions(self):
        # 1. English name left in draft
        text_en = "**WANG PI** says,\n\nدائو حقیقت است."
        findings_en = check_terms.check_commentators("test.md", text_en, self.canonical_names, TEST_CONFIG_COMMENTATORS)
        self.assertTrue(any(f.rule == "commentator_en" for f in findings_en))

        # 2. Non-canonical name
        text_noncanon = "**پادشاه پی** می‌گوید:\n\nدائو حقیقت است."
        findings_nc = check_terms.check_commentators("test.md", text_noncanon, self.canonical_names, TEST_CONFIG_COMMENTATORS)
        self.assertTrue(any(f.rule == "commentator_canonical" for f in findings_nc))

        # 3. Non-standard action formula
        text_formula = "**وانگ پی** چنین روایت کرد:\n\nدائو حقیقت است."
        findings_form = check_terms.check_commentators("test.md", text_formula, self.canonical_names, TEST_CONFIG_COMMENTATORS)
        self.assertTrue(any(f.rule == "commentator_formula" for f in findings_form))

    def test_compound_zwnj(self):
        text = "دست نوشته های ماوانگ‌دوی حاوی ده هزار کلمه است."
        findings = check_terms.check_disallowed_terms("test.md", text, self.compiled_disallowed)
        self.assertTrue(any("دست‌نوشته" in f.message for f in findings))
        self.assertTrue(any("ده‌هزار" in f.message for f in findings))

    def test_protected_spans_ignored(self):
        text = (
            "متن فارسی.\n\n"
            "`تائو و تقوا در کد`\n\n"
            "<!-- تائو در کامنت -->\n\n"
            "```\nکنده درخت در بلوک کد\n```\n"
        )
        findings = check_terms.check_disallowed_terms("test.md", text, self.compiled_disallowed)
        self.assertEqual(findings, [])

    def test_fix_terms(self):
        text = "کتاب تائو پیرامون عرش و فرش، کنده درخت، و ده هزار موجود است."
        fixed = check_terms.fix_terms(text, self.compiled_disallowed, TEST_CONFIG_COMMENTATORS)
        self.assertEqual(
            fixed,
            "کتاب دائو پیرامون آسمان و زمین، چوب نتراشیده، و ده‌هزار موجود است."
        )


if __name__ == "__main__":
    unittest.main()
