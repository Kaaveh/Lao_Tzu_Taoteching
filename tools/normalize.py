"""Persian orthographic normalization for taoteching-farsi.

Enforces Iranian Persian typographic standards:
  * Replaces Arabic Yeh (ي) and Kaf (ك) with Persian ی and ک
  * Corrects ZWNJ (Zero-Width Non-Joiner) placement for prefixes (می‌/نمی‌) and suffixes (ها, تر, ترین)
  * Converts Western ASCII digits (0-9) to Persian digits (۰-۹) where configured
  * Normalizes quotes to Persian guillemets («...»)
  * Strips tatweel/kashida (ـ)
  * Normalizes punctuation (، ؛ ؟)
  * Detects and reports dangerous Unicode bidirectional overrides (LRE, RLE, etc.)

Rules are individually toggleable in [tool.normalize] in pyproject.toml, and regions
can be exempted with:
    <!-- normalize: off -->
    ...
    <!-- normalize: on -->

Usage:
    python3 -m tools.normalize --check          # exit non-zero, print report
    python3 -m tools.normalize --fix            # rewrite in place
    python3 -m tools.normalize --check fa/01.md
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import regex

from . import _md
from ._md import ZWNJ

REPO = Path.cwd()

# Bidi overrides and isolates. Always an error, never auto-fixed.
BIDI_OVERRIDES = regex.compile(r"[‪-‮⁦-⁩]")

BIDI_NAMES = {
    "‪": "LRE U+202A",
    "‫": "RLE U+202B",
    "‬": "PDF U+202C",
    "‭": "LRO U+202D",
    "‮": "RLO U+202E",
    "⁦": "LRI U+2066",
    "⁧": "RLI U+2067",
    "⁨": "FSI U+2068",
    "⁩": "PDI U+2069",
}

ARABIC = r"\p{Arabic}"

DEFAULTS = {
    "arabic_yeh": True,
    "arabic_kaf": True,
    "arabic_digits": True,
    "latin_digits": False,
    "tatweel": True,
    "punctuation": True,
    "zwnj_mi": True,
    "zwnj_plural": True,
    "zwnj_comparative": True,
    "zwnj_collapse": True,
    "zwnj_trim": True,
    "quotes": True,
    "harakat": "preserve",
}

ARABIC_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹")
LATIN_TO_PERSIAN = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
ASCII_PUNCT = {",": "،", ";": "؛", "?": "؟"}

RE_MI = regex.compile(rf"(?<![{ARABIC}‌])(ن?می)[ \t]+(?=[{ARABIC}])")
RE_PLURAL = regex.compile(rf"(?<=[{ARABIC}])[ \t]+(ها(?:ی|یی|یم|یت|یش|یمان|یتان|یشان)?)(?![{ARABIC}])")
RE_COMPARATIVE = regex.compile(rf"(?<=[{ARABIC}])[ \t]+(تر(?:ین)?)(?![{ARABIC}])")
RE_ZWNJ_RUN = regex.compile("‌{2,}")
RE_ZWNJ_LOOSE = regex.compile(rf"(?<![{ARABIC}])‌|‌(?![{ARABIC}])")
RE_ASCII_PUNCT = regex.compile(rf"(?<=[{ARABIC}])([,;?])")
RE_HARAKAT = regex.compile(r"[ً-ْ]")
RE_STRAIGHT_QUOTES = regex.compile(r'"([^"\n]*)"')
RE_CURLY_QUOTES = regex.compile(r"“([^”\n]*)”")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.message}"


def load_config(path: Path | None = None) -> dict:
    config = dict(DEFAULTS)
    path = path or REPO / "pyproject.toml"
    if path.is_file():
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        config.update(data.get("tool", {}).get("normalize", {}))
    return config


def _rules(config: dict):
    rules = [
        ("arabic_yeh", "Arabic Yeh U+064A should be Farsi Yeh U+06CC",
         lambda s: s.replace("ي", "ی")),
        ("arabic_kaf", "Arabic Kaf U+0643 should be Keheh U+06A9",
         lambda s: s.replace("ك", "ک")),
        ("arabic_digits", "Arabic-Indic digits should be Persian U+06F0-U+06F9",
         lambda s: s.translate(ARABIC_INDIC)),
        ("latin_digits", "Latin digits should be Persian U+06F0-U+06F9",
         lambda s: s.translate(LATIN_TO_PERSIAN)),
        ("tatweel", "Tatweel/Kashida U+0640 should be removed",
         lambda s: s.replace("ـ", "")),
        ("punctuation", "ASCII punctuation after Persian should be Persian",
         lambda s: RE_ASCII_PUNCT.sub(lambda m: ASCII_PUNCT[m.group(1)], s)),
        ("quotes", "ASCII quotes should be Persian guillemets",
         lambda s: RE_CURLY_QUOTES.sub(r"«\1»", RE_STRAIGHT_QUOTES.sub(r"«\1»", s))),
        ("zwnj_collapse", "repeated ZWNJ should collapse to one",
         lambda s: RE_ZWNJ_RUN.sub(ZWNJ, s)),
        ("zwnj_trim", "ZWNJ outside a word should be removed",
         lambda s: RE_ZWNJ_LOOSE.sub("", s)),
        ("zwnj_mi", "mi/nemi prefix should join with ZWNJ",
         lambda s: RE_MI.sub(rf"\1{ZWNJ}", s)),
        ("zwnj_plural", "plural haa should join with ZWNJ",
         lambda s: RE_PLURAL.sub(rf"{ZWNJ}\1", s)),
        ("zwnj_comparative", "comparative tar/tarin should join with ZWNJ",
         lambda s: RE_COMPARATIVE.sub(rf"{ZWNJ}\1", s)),
    ]
    enabled = [(name, desc, fn) for name, desc, fn in rules if config.get(name, False)]

    if config.get("harakat", "preserve") == "strip":
        enabled.append(("harakat", "harakat should be stripped", lambda s: RE_HARAKAT.sub("", s)))
    return enabled


def _editable_chunks(text: str):
    """Yield (start, end) spans that normalization may rewrite."""
    disabled = _md.toggle_regions(text, "normalize")
    cursor = 0
    for start, end in disabled:
        if start > cursor:
            yield cursor, start
        cursor = end
    if cursor < len(text):
        yield cursor, len(text)


def apply_rule(text: str, func) -> str:
    """Apply func only outside disabled regions and protected spans."""
    out = []
    cursor = 0
    for start, end in _editable_chunks(text):
        out.append(text[cursor:start])
        out.append(_md.apply_outside_protected(text[start:end], func))
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def changed_lines(before: str, after: str) -> list[int]:
    """1-based line numbers that differ."""
    a, b = before.split("\n"), after.split("\n")
    return [i for i, (x, y) in enumerate(zip(a, b), start=1) if x != y]


def normalize_text(path: str, text: str, config: dict) -> tuple[str, list[Finding]]:
    findings: list[Finding] = []

    # Bidi overrides first
    for match in BIDI_OVERRIDES.finditer(text):
        char = match.group()
        findings.append(
            Finding(
                path,
                _md.line_of(text, match.start()),
                "bidi",
                f"bidi override {BIDI_NAMES.get(char, repr(char))} — remove it by hand, "
                "never auto-fixed",
            )
        )

    for name, description, func in _rules(config):
        updated = apply_rule(text, func)
        if updated != text:
            for line in changed_lines(text, updated):
                findings.append(Finding(path, line, name, description))
            text = updated

    return text, findings


def process(paths: list[Path], config: dict, fix: bool) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    rewritten = 0
    for path in paths:
        original = path.read_text(encoding="utf-8")
        updated, found = normalize_text(str(path), original, config)
        findings.extend(found)
        if fix and updated != original:
            path.write_text(updated, encoding="utf-8")
            rewritten += 1
    return findings, rewritten


def default_paths() -> list[Path]:
    return sorted((REPO / "fa").glob("*.md"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report and exit non-zero")
    mode.add_argument("--fix", action="store_true", help="rewrite files in place")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--config", type=Path, help="pyproject.toml to read [tool.normalize] from")
    args = parser.parse_args(argv)

    paths = args.paths or default_paths()
    config = load_config(args.config)
    findings, rewritten = process(paths, config, fix=args.fix)

    bidi = [f for f in findings if f.rule == "bidi"]
    other = [f for f in findings if f.rule != "bidi"]

    for finding in sorted(findings, key=lambda f: (f.path, f.line, f.rule)):
        print(finding)

    if args.fix:
        print(f"\nnormalized {rewritten} file(s)")
        if bidi:
            print(f"{len(bidi)} bidi override(s) left in place — remove by hand", file=sys.stderr)
            return 1
        return 0

    if findings:
        print(
            f"\n{len(other)} orthography issue(s), {len(bidi)} bidi override(s) "
            f"in {len({f.path for f in findings})} file(s)",
            file=sys.stderr,
        )
        return 1

    print(f"normalize: {len(paths)} file(s) clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
