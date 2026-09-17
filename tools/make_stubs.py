"""Mirror source/ into fa/ as translation stubs.

Filenames match byte-for-byte across source/ and fa/.
Each stub opens with:
    ---
    status: untranslated
    ---

    # [عنوان]

    <!-- TODO: translate -->

Usage:
    python3 -m tools.make_stubs                 # create missing fa/ stubs
    python3 -m tools.make_stubs --force         # overwrite existing stubs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import _md
from ._md import to_persian_digits

REPO = _md.REPO
DEFAULT_EXCLUDE = set(_md.config("book").get("exclude", []))
DEFAULT_TITLES = _md.config("book").get("titles", {})


def heading_for(name: str, titles: dict[str, str]) -> str:
    """Placeholder heading for a stub, by filename."""
    if name in titles:
        return titles[name]
    stem = Path(name).stem
    if stem.isdigit():
        return to_persian_digits(int(stem))
    return stem


def fa_stub(name: str, titles: dict[str, str]) -> str:
    return (
        "---\n"
        "status: untranslated\n"
        "---\n"
        "\n"
        f"# {heading_for(name, titles)}\n"
        "\n"
        "<!-- TODO: translate -->\n"
    )


def source_names(source: Path, exclude: set[str]) -> list[str]:
    if not source.is_dir():
        raise FileNotFoundError(f"{source} does not exist")
    names = [p.name for p in source.iterdir() if p.suffix == ".md" and p.name not in exclude]
    return sorted(
        names,
        key=lambda n: (
            not Path(n).stem.isdigit(),
            int(Path(n).stem) if Path(n).stem.isdigit() else 0,
            n,
        ),
    )


def load_titles(path: Path | None, base: dict[str, str] | None = None) -> dict[str, str]:
    """The title table from base config overlaid with optional TSV."""
    titles = dict(DEFAULT_TITLES if base is None else base)
    if path:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, _, title = line.partition("\t")
            if not title:
                raise ValueError(f"expected 'filename<TAB>title', got: {line!r}")
            titles[name.strip()] = title.strip()
    return titles


def sync(source: Path, target: Path, titles: dict[str, str], exclude: set[str], force: bool):
    """Returns (written, skipped, orphans)."""
    names = source_names(source, exclude)
    target.mkdir(parents=True, exist_ok=True)

    written = skipped = 0
    for name in names:
        path = target / name
        if path.exists() and not force:
            skipped += 1
            continue
        path.write_text(fa_stub(name, titles), encoding="utf-8")
        written += 1

    expected = set(names)
    orphans = sorted(
        p.name for p in target.iterdir() if p.suffix == ".md" and p.name not in expected
    )
    return written, skipped, orphans


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--source", type=Path, default=REPO / "source")
    parser.add_argument("--target", type=Path, default=REPO / "fa")
    parser.add_argument("--titles", type=Path, help="TSV of 'filename<TAB>Persian heading'")
    parser.add_argument("--exclude", nargs="*", default=sorted(DEFAULT_EXCLUDE))
    parser.add_argument("--force", action="store_true", help="overwrite existing stubs")
    args = parser.parse_args(argv)

    try:
        titles = load_titles(args.titles)
        written, skipped, orphans = sync(
            args.source, args.target, titles, set(args.exclude), args.force
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {written} stub(s), skipped {skipped} existing")
    if orphans:
        print(
            f"\n{len(orphans)} file(s) in {args.target}/ have no counterpart in {args.source}/:",
            file=sys.stderr,
        )
        for name in orphans:
            print(f"  {name}", file=sys.stderr)
        print("parity cannot check these. Rename or remove them.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
