#!/usr/bin/env python3
"""check_terms.py — Style, Terminology, and Commentator Name Checker for taoteching-farsi.

Enforces Spec 002 (Style Decisions & Terminology):
  * Canonical commentator transliterations from [tool.book.commentators]
  * Standard commentary introduction formulas (**[مفسر]** می‌گوید:)
  * Disallowed terminology patterns configured in [tool.book.disallowed_terms]
  * ZWNJ discipline in canonical compounds (ده‌هزار, دست‌نوشته, بی‌عملی)

Usage:
    python3 -m tools.check_terms --check          # exit non-zero on findings
    python3 -m tools.check_terms --fix            # rewrite fixable terms in place
    python3 -m tools.check_terms --check fa/01.md # check specific file
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import regex

from . import _md

REPO = Path.cwd()

# Regex for commentator attribution lines:
# e.g., **وانگ پی** می‌گوید: or **HO-SHANG KUNG** says,
RE_COMM_LINE = regex.compile(
    r"^\*\*(?P<name>[^*]+)\*\*,?\s*(?P<action>[^\n]*)$", regex.MULTILINE
)

# Canonical commentator introduction verbs / formulas
ALLOWED_ACTION_PREFIXES = (
    "می‌گوید:",
    "گفت:",
    "همچنین می‌گوید:",
    "این بند را «در ستایش تاریکی» نام نهاده و می‌گوید:",
    "این بند را چنین نام نهاده است:",
    "از تسو-کونگ پرسید:",
    "از منسیوس پرسید:",
    "پرسید:",
    "به گوئو ین گفت:",
    "آه کشید و گفت:",
    "به نقل از منسیوس (۷B.۷) می‌گوید:",
    "با بازنویسی سخن سون‌تزو در پینگ‌فا (۲.۱) می‌گوید:",
    "نزد یو جوئو رفت و گفت:",
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.message}"


def load_config(path: Path | None = None) -> tuple[dict[str, str], dict, dict]:
    """Load commentator mappings, terminology, and disallowed terms."""
    path = path or REPO / "pyproject.toml"
    commentators: dict[str, str] = {}
    terminology: dict[str, str] = {}
    disallowed: dict[str, dict] = {}

    if path.is_file():
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        book_cfg = data.get("tool", {}).get("book", {})
        commentators = book_cfg.get("commentators", {})
        terminology = book_cfg.get("terminology", {})
        disallowed = book_cfg.get("disallowed_terms", {})

    return commentators, terminology, disallowed


def is_protected_span(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    """Check if the given [start, end) span intersects any protected span."""
    for p_start, p_end in spans:
        if max(start, p_start) < min(end, p_end):
            return True
    return False


def check_commentators(
    path: str, text: str, canonical_names: set[str], en_to_fa: dict[str, str]
) -> list[Finding]:
    """Verify that all commentator attributions in text match canonical names and formulas."""
    findings: list[Finding] = []
    prot = _md.protected_spans(text)

    for m in RE_COMM_LINE.finditer(text):
        if is_protected_span(m.start(), m.end(), prot):
            continue

        raw_name = m.group("name").strip().rstrip(",")
        action = m.group("action").strip()
        line_no = _md.line_of(text, m.start())

        # Check if the name is an English commentator name left untranslated
        if raw_name in en_to_fa:
            canonical_persian = en_to_fa[raw_name]
            findings.append(
                Finding(
                    path,
                    line_no,
                    "commentator_en",
                    f"English commentator name left in draft: '**{raw_name}**'. "
                    f"Must be canonical Persian: '**{canonical_persian}**'.",
                )
            )
            continue

        # Check if the action looks like a commentator attribution
        is_comm_action = (
            any(action.startswith(prefix) for prefix in ALLOWED_ACTION_PREFIXES)
            or action.endswith(":")
            or any(kw in action for kw in ("می‌گوید", "گفت", "پرسید", "says", "said"))
        )

        if is_comm_action:
            if raw_name not in canonical_names:
                findings.append(
                    Finding(
                        path,
                        line_no,
                        "commentator_canonical",
                        f"Non-canonical commentator transliteration: '**{raw_name}**'. "
                        "Must match canonical name table in specs/002-style-and-terminology.md.",
                    )
                )

            if not any(action == prefix or action.startswith(prefix) for prefix in ALLOWED_ACTION_PREFIXES):
                findings.append(
                    Finding(
                        path,
                        line_no,
                        "commentator_formula",
                        f"Non-standard commentator attribution formula: '{action}'. "
                        "Expected standard formula such as '**[نام مفسر]** می‌گوید:'.",
                    )
                )

    return findings


def check_disallowed_terms(
    path: str, text: str, disallowed_patterns: list[tuple[regex.Pattern, str, str | None]]
) -> list[Finding]:
    """Scan text for disallowed terminology patterns."""
    findings: list[Finding] = []
    prot = _md.protected_spans(text)

    for pat, reason, _ in disallowed_patterns:
        for m in pat.finditer(text):
            if is_protected_span(m.start(), m.end(), prot):
                continue
            line_no = _md.line_of(text, m.start())
            matched_str = m.group(0)
            findings.append(
                Finding(
                    path,
                    line_no,
                    "disallowed_term",
                    f"{reason} (found '{matched_str}')",
                )
            )

    return findings


def fix_terms(
    text: str,
    disallowed_patterns: list[tuple[regex.Pattern, str, str | None]],
    en_to_fa: dict[str, str],
) -> str:
    """Safely apply automated fixes for known fixable terms and commentators."""
    updated = text

    # 1. Fix English commentator headers to canonical Persian
    for en_name, fa_name in en_to_fa.items():
        pat = regex.compile(rf"^\*\*{regex.escape(en_name)}\*\*,?\s*", regex.MULTILINE)
        updated = _md.apply_outside_protected(updated, lambda s: pat.sub(f"**{fa_name}** ", s))

    # 2. Fix disallowed terms that have a defined replacement
    for pat, _, replacement in disallowed_patterns:
        if replacement is not None:
            updated = _md.apply_outside_protected(
                updated, lambda s: pat.sub(replacement, s)
            )

    return updated


def compile_disallowed(disallowed_cfg: dict) -> list[tuple[regex.Pattern, str, str | None]]:
    """Compile regex patterns from disallowed_terms config."""
    compiled = []
    for pat_str, details in disallowed_cfg.items():
        if isinstance(details, dict):
            reason = details.get("reason", f"Disallowed term: {pat_str}")
            replacement = details.get("replacement")
        else:
            reason = str(details)
            replacement = None
        compiled.append((regex.compile(pat_str), reason, replacement))
    return compiled


def process(
    paths: list[Path],
    commentators: dict[str, str],
    disallowed_cfg: dict,
    fix: bool,
) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    canonical_names = set(commentators.values())
    compiled_disallowed = compile_disallowed(disallowed_cfg)
    rewritten = 0

    for p in paths:
        if not p.is_file():
            continue

        doc = _md.read(p)
        # Skip untranslated stubs
        if doc.status == "untranslated":
            continue

        original = p.read_text(encoding="utf-8")
        current_text = original

        if fix:
            current_text = fix_terms(current_text, compiled_disallowed, commentators)
            if current_text != original:
                p.write_text(current_text, encoding="utf-8")
                rewritten += 1

        # Check for remaining findings
        comm_findings = check_commentators(str(p), current_text, canonical_names, commentators)
        term_findings = check_disallowed_terms(str(p), current_text, compiled_disallowed)

        findings.extend(comm_findings)
        findings.extend(term_findings)

    return findings, rewritten


def default_paths() -> list[Path]:
    return sorted((REPO / "fa").glob("*.md"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report issues and exit non-zero if found")
    mode.add_argument("--fix", action="store_true", help="safely fix known terms in place")
    parser.add_argument("paths", nargs="*", type=Path, help="files to check (default: fa/*.md)")
    parser.add_argument("--config", type=Path, help="path to pyproject.toml")
    args = parser.parse_args(argv)

    paths = args.paths or default_paths()
    commentators, _, disallowed = load_config(args.config)

    findings, rewritten = process(paths, commentators, disallowed, fix=args.fix)

    for f in sorted(findings, key=lambda x: (x.path, x.line, x.rule)):
        print(f)

    if args.fix:
        print(f"\ncheck_terms: auto-fixed {rewritten} file(s)")
        if findings:
            print(f"check_terms: {len(findings)} issue(s) remain requiring manual edit", file=sys.stderr)
            return 1
        return 0

    if findings:
        print(
            f"\ncheck_terms: {len(findings)} issue(s) in {len({f.path for f in findings})} file(s)",
            file=sys.stderr,
        )
        return 1

    print(f"check_terms: {len(paths)} file(s) clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
