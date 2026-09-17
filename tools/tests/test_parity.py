"""Unit tests for tools.check_parity."""

import tempfile
import unittest
from pathlib import Path
from tools import check_parity


class TestParity(unittest.TestCase):
    def test_parity_match_and_skip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            fa_dir = Path(tmpdir) / "fa"
            source_dir.mkdir()
            fa_dir.mkdir()

            # 01.md: untranslated (should be skipped)
            (source_dir / "01.md").write_text("Block 1\n\nBlock 2\n")
            (fa_dir / "01.md").write_text("---\nstatus: untranslated\n---\n\n# ۱\n")

            # 02.md: reviewed and matching blocks
            (source_dir / "02.md").write_text("Block 1\n\nBlock 2\n")
            (fa_dir / "02.md").write_text("---\nstatus: reviewed\n---\n\nبند اول\n\nبند دوم\n")

            findings, compared, skipped = check_parity.compare(source_dir, fa_dir)
            self.assertEqual(len(findings), 0)
            self.assertEqual(compared, 1)
            self.assertEqual(skipped, 1)

    def test_parity_offset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            fa_dir = Path(tmpdir) / "fa"
            source_dir.mkdir()
            fa_dir.mkdir()

            # Source has 3 blocks, fa has 2 blocks and declares offset -1
            (source_dir / "01.md").write_text("Header\n\nVerse\n\nComm\n")
            (fa_dir / "01.md").write_text(
                "---\nstatus: reviewed\n---\n\n<!-- parity: offset -1 -->\n\nشعر\n\nتفسیر\n"
            )

            findings, compared, skipped = check_parity.compare(source_dir, fa_dir)
            self.assertEqual(len(findings), 0)
            self.assertEqual(compared, 1)


if __name__ == "__main__":
    unittest.main()
