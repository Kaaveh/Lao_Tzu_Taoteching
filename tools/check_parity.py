"""Catch dropped paragraphs by comparing block counts between source/ and fa/.

Blocks are blank-line-delimited runs, with fenced code held together.
Files are paired by filename across source/ and fa/.

Skipped:
  * any fa/ file marked `status: untranslated`
  * any fa/ file containing <!-- parity: skip -->

Structural divergence is declared with:
    <!-- parity: offset N -->     fa/ has N blocks relative to source/

Usage:
    python3 -m tools.check_parity --check
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from . import _md

REPO = _md.REPO
EXCLUDE = set(_md.config("book").get("exclude", []))


@dataclass(frozen=True)
class Finding:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def parse_offset(body: str) -> int:
    """Value of <!-- parity: offset N -->, or 0."""
    for value in _md.directives(body, "parity"):
        parts = value.split()
        if len(parts) == 2 and parts[0] == "offset":
            try:
                return int(parts[1])
            except ValueError:
                raise ValueError(f"bad parity offset: {value!r}")
    return 0


def is_skipped(body: str) -> bool:
    return any(v.strip() == "skip" for v in _md.directives(body, "parity"))


def compare(source_dir: Path, fa_dir: Path, exclude: set[str] | None = None) -> tuple[list[Finding], int, int]:
    """Returns (findings, compared, skipped)."""
    findings: list[Finding] = []
    compared = skipped = 0

    source_names = {p.name for p in source_dir.glob("*.md")} - (
        EXCLUDE if exclude is None else exclude
    )
    fa_names = {p.name for p in fa_dir.glob("*.md")}

    for name in sorted(source_names - fa_names):
        findings.append(Finding(f"fa/{name}", "missing — source/ has it, fa/ does not"))
    for name in sorted(fa_names - source_names):
        findings.append(Finding(f"fa/{name}", "orphan — no counterpart in source/"))

    for name in sorted(source_names & fa_names):
        fa_doc = _md.read(fa_dir / name)

        if fa_doc.status == "untranslated":
            skipped += 1
            continue
        if is_skipped(fa_doc.body):
            skipped += 1
            continue

        try:
            offset = parse_offset(fa_doc.body)
        except ValueError as exc:
            findings.append(Finding(f"fa/{name}", str(exc)))
            continue

        source_doc = _md.read(source_dir / name)
        source_count = len(_md.iter_blocks(source_doc))
        fa_count = len(_md.iter_blocks(fa_doc))
        compared += 1

        actual = fa_count - source_count
        if actual != offset:
            detail = f"{fa_count} blocks, source has {source_count}"
            if offset:
                detail += f" (offset {offset:+d} declared, actual {actual:+d})"
            findings.append(Finding(f"fa/{name}", detail))

    return findings, compared, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true", default=True)
    parser.add_argument("--source", type=Path, default=REPO / "source")
    parser.add_argument("--fa", type=Path, default=REPO / "fa")
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="source/ filenames with no translation to pair against",
    )
    args = parser.parse_args(argv)

    if not args.source.is_dir():
        print(
            f"parity: skipped — {args.source}/ is not present.\n"
            "This is expected in CI: the source text is licensed to the maintainer "
            "for translation, not for redistribution. Run this locally."
        )
        return 0

    findings, compared, skipped = compare(
        args.source, args.fa, None if args.exclude is None else set(args.exclude)
    )

    for finding in findings:
        print(finding)

    if findings:
        print(f"\n{len(findings)} parity problem(s)", file=sys.stderr)
        return 1

    print(f"parity: {compared} file(s) match, {skipped} skipped (untranslated or exempt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
