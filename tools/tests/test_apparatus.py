"""Unit tests for tools.apparatus."""

import unittest
from pathlib import Path
from tools import apparatus

REPO = Path(__file__).resolve().parent.parent.parent


class TestApparatus(unittest.TestCase):
    def test_strip_and_restore_images(self):
        source = (
            "### Verse 1 — The Way\n\n"
            "![Verse 1 Calligraphy](media/images/f0002-01.jpg)\n\n"
            "The way that becomes a way\n\n"
            "**WANG PI** says, “From the infinitesimal all things develop.”\n"
        )
        stripped = apparatus.strip("01.md", source)
        self.assertIn("⟦1:HDR:1⟧ The Way", stripped)
        self.assertIn("media/images/f0002-01.jpg", source)
        self.assertNotIn("media/images/f0002-01.jpg", stripped)
        self.assertIn("⟦2:IMG:VERSE_1_CALLIGRAPHY", stripped)
        self.assertIn("⟦3:COMM:WANG_PI", stripped)

        restored = apparatus.restore("01.md", source, stripped)
        self.assertIn("---\nstatus: reviewed\n---", restored)
        self.assertIn("# ۱ — The Way", restored)
        self.assertIn("![Verse 1 Calligraphy](media/images/f0002-01.jpg)", restored)
        self.assertIn("**وانگ پی** می‌گوید:", restored)

    def test_refusal_on_dropped_sentinel(self):
        source = (
            "### Verse 1 — The Way\n\n"
            "![Verse 1 Calligraphy](media/images/f0002-01.jpg)\n\n"
            "**WANG PI** says, “Hello.”\n"
        )
        # Dropping sentinel 2 (the image)
        draft = (
            "⟦1:HDR:1⟧ راهی که می‌رود\n\n"
            "⟦3:COMM:WANG_PI⟧ «درود.»\n"
        )
        with self.assertRaises(ValueError) as ctx:
            apparatus.restore("01.md", source, draft)
        self.assertIn("dropped sentinel", str(ctx.exception))
        self.assertIn("⟦2⟧", str(ctx.exception))

    def test_bare_index_recovery(self):
        source = (
            "### Verse 1 — The Way\n\n"
            "![Verse 1 Calligraphy](media/images/f0002-01.jpg)\n\n"
            "**WANG PI** says, “Hello.”\n"
        )
        # Translator dropped long tag, user placed bare ⟦2⟧
        draft = (
            "⟦1⟧ راه\n\n"
            "⟦2⟧\n\n"
            "⟦3⟧ «درود.»\n"
        )
        restored = apparatus.restore("01.md", source, draft)
        self.assertIn("![Verse 1 Calligraphy](media/images/f0002-01.jpg)", restored)
        self.assertIn("**وانگ پی** می‌گوید:", restored)

    def test_duplicate_sentinel_refusal(self):
        source = (
            "### Verse 1 — The Way\n\n"
            "**WANG PI** says, “Hello.”\n"
        )
        draft = (
            "⟦1:HDR:1⟧ راه\n\n"
            "⟦2:COMM:WANG_PI⟧ سلام\n\n"
            "⟦2:COMM:WANG_PI⟧ سلام دوباره\n"
        )
        with self.assertRaises(ValueError) as ctx:
            apparatus.restore("01.md", source, draft)
        self.assertIn("duplicate sentinel", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
