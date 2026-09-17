#!/usr/bin/env python3
"""apparatus.py — Pre- and post-processing adapter for gTranslator.

Protects volatile Markdown structures across machine translation:
  * Markdown images (![...](media/images/...))
  * Classical commentator headings (**WANG PI** says, ...)
  * Verse headings (### Verse N — Title)
  * Book structural headings (## Lao-tzu's Taoteching)

Pipeline usage:
    python3 tools/apparatus.py strip source/01.md -o /tmp/01.en.md
    "$GT/.venv/bin/python" "$GT/gtranslate.py" -f /tmp/01.en.md -t fa -w --raw -o /tmp/01.fa.md
    python3 tools/apparatus.py restore source/01.md /tmp/01.fa.md -o fa/01.md
    python3 tools/apparatus.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Add project root to sys.path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import regex
from tools import _md
from tools._md import to_persian_digits

EXCLUDE = set(_md.config("book").get("exclude", []))
TITLES = _md.config("book").get("titles", {})
COMMENTATORS = _md.config("book").get("commentators", {})

FINAL_STATUS = "reviewed"
WINDOW = 240

# Sentinel format: ⟦<index>:<kind>:<tag>⟧
SENTINEL_RE = regex.compile(r"⟦(?P<full>(?P<idx>\d+)(?::(?P<tag>[^⟧]+))?|(?P<bare_tag>[A-Z0-9_:\*]+))⟧")


@dataclass
class Token:
    index: int
    kind: str
    tag: str
    original: str
    restored: str
    sentinel: str


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.replace("*", "")).strip()
    return re.sub(r"[-\s]+", "_", cleaned).upper()[:24]


def translate_action(action: str) -> str:
    """Translate standard English commentator actions into Persian."""
    act = action.strip()
    if act in ("says,", "says"):
        return "می‌گوید:"
    if act in ("said,", "said"):
        return "گفت:"
    if act in ("also says,", "also says"):
        return "همچنین می‌گوید:"
    if "titles" in act or "entitles" in act:
        if "In Praise of the Dark" in act:
            return "این بند را «در ستایش تاریکی» نام نهاده و می‌گوید:"
        return "این بند را چنین نام نهاده است:"
    if act.startswith("asked"):
        if "Tzu-kung" in act:
            return "از تسو-کونگ پرسید:"
        if "Mencius" in act:
            return "از منسیوس پرسید:"
        return "پرسید:"
    if act.startswith("told"):
        if "Kuo Yen" in act:
            return "به گوئو ین گفت:"
        return "گفت:"
    if act.startswith("sighed"):
        return "آه کشید و گفت:"
    if "Mencius" in act and "quoting" in act:
        return "به نقل از منسیوس (۷B.۷) می‌گوید:"
    if "Suntzu Pingfa" in act and "paraphrasing" in act:
        return "با بازنویسی سخن سون‌تزو در پینگ‌فا (۲.۱) می‌گوید:"
    if "approached" in act:
        return "نزد یو جوئو رفت و گفت:"
    return "می‌گوید:"


def commentator_fa(name: str, action: str) -> str:
    """Return the Persian form for a commentator attribution."""
    clean_name = name.strip().rstrip(",")
    fa_name = COMMENTATORS.get(clean_name, clean_name)
    fa_act = translate_action(action)
    return f"**{fa_name}** {fa_act}"


def extract_tokens(name: str, source_text: str) -> list[Token]:
    """Scan source text and extract all structural tokens to be shielded."""
    tokens: list[Token] = []
    idx = 1

    # Pre-compile patterns
    re_book_title = regex.compile(r"^## Lao-tzu's Taoteching\s*$", regex.MULTILINE)
    re_verse_hdr = regex.compile(r"^### Verse (?P<num>\d+)(?:\s*—\s*(?P<title>[^\n]+))?$", regex.MULTILINE)
    re_named_hdr = regex.compile(r"^#{1,3}\s+(?P<title>[^\n]+)$", regex.MULTILINE)
    re_image = regex.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)")
    re_comm = regex.compile(
        r"^\*\*(?P<name>(?:[^*]|\*[^*]+\*)+?)\*\*,?\s*"
        r"(?P<action>(?:also\s+says|says?|said|asked|told|sighed|titles|entitles|quoting[^\n]*?says|paraphrasing[^\n]*?says|approached[^\n]*?:)[^,\n]*?[,:]?)",
        regex.MULTILINE,
    )

    # Find matches with spans to sort by appearance order
    matches = []

    for m in re_book_title.finditer(source_text):
        matches.append((m.start(), m.end(), "BOOK_TITLE", m.group(0), "", "BOOK_TITLE"))

    for m in re_verse_hdr.finditer(source_text):
        num = m.group("num")
        title = m.group("title") or ""
        tag = f"HDR:{num}"
        # Verse heading in Persian: "# ۱" (title gets translated after sentinel)
        restored = f"# {to_persian_digits(num)}" + (" —" if title else "")
        matches.append((m.start(), m.end(), "HDR", m.group(0), restored, tag))

    if name in TITLES and not any(t[2] == "HDR" for t in matches):
        for m in re_named_hdr.finditer(source_text):
            matches.append((m.start(), m.end(), "NAMED_HDR", m.group(0), f"# {TITLES[name]}", f"HDR:{slugify(name)}"))
            break

    for m in re_image.finditer(source_text):
        alt = m.group("alt")
        src = m.group("src")
        tag = f"IMG:{slugify(alt or 'IMAGE')}"
        matches.append((m.start(), m.end(), "IMG", m.group(0), f"![{alt}]({src})", tag))

    for m in re_comm.finditer(source_text):
        c_name = m.group("name")
        c_act = m.group("action")
        fa_text = commentator_fa(c_name, c_act)
        tag = f"COMM:{slugify(c_name)}"
        matches.append((m.start(), m.end(), "COMM", m.group(0), fa_text, tag))

    # Sort matches by start position
    matches.sort(key=lambda x: x[0])

    for _, _, kind, orig, restored, tag in matches:
        tokens.append(Token(
            index=idx,
            kind=kind,
            tag=tag,
            original=orig,
            restored=restored,
            sentinel=f"⟦{idx}:{tag}⟧",
        ))
        idx += 1

    return tokens


def strip(name: str, source_text: str) -> str:
    """Replace apparatus tokens with sentinels for machine translation."""
    tokens = extract_tokens(name, source_text)
    out = source_text

    # Replace from back to front to preserve string indices
    # We locate matches in reverse order
    for tok in reversed(tokens):
        # For HDR with title, replace the '### Verse N — ' prefix so title can be translated
        if tok.kind == "HDR":
            m = re.match(r"^### Verse \d+\s*—\s*", tok.original)
            if m:
                out = out.replace(tok.original, f"{tok.sentinel} " + tok.original[m.end():], 1)
            else:
                out = out.replace(tok.original, tok.sentinel, 1)
        else:
            out = out.replace(tok.original, tok.sentinel, 1)

    return out


def find_sentinel_in_draft(draft: str, tok: Token) -> tuple[int, int] | None:
    """Look for a sentinel in draft text (exact, indexed, or bare numeric)."""
    # 1. Exact full sentinel: ⟦idx:tag⟧
    full_pat = regex.compile(rf"⟦{tok.index}:[^⟧]+⟧")
    m = full_pat.search(draft)
    if m:
        return m.span()

    # 2. Bare index: ⟦idx⟧
    idx_pat = regex.compile(rf"⟦{tok.index}⟧")
    m = idx_pat.search(draft)
    if m:
        return m.span()

    # 3. Tag only: ⟦tag⟧
    tag_esc = regex.escape(tok.tag)
    tag_pat = regex.compile(rf"⟦{tag_esc}⟧")
    m = tag_pat.search(draft)
    if m:
        return m.span()

    return None


def restore(name: str, source_text: str, draft: str) -> str:
    """Restore apparatus tokens from source into the translated draft."""
    tokens = extract_tokens(name, source_text)
    stripped = strip(name, source_text)

    # Validate that all sentinels exist in draft
    dropped = []
    positions = []

    for tok in tokens:
        span = find_sentinel_in_draft(draft, tok)
        if span is None:
            dropped.append(tok)
        else:
            positions.append((tok, span))

    if dropped:
        report = [f"error: {name}: the model dropped sentinel(s):"]
        for dt in dropped:
            # Quote line from stripped source
            quote = ""
            for line in stripped.splitlines():
                if dt.sentinel in line:
                    quote = line.strip()
                    break
            report.append(f"  ⟦{dt.index}⟧  {dt.sentinel}\n       Source context: {quote[:WINDOW]}")
        raise ValueError("\n".join(report))

    # Check for duplicate sentinels
    found_indices = []
    for m in SENTINEL_RE.finditer(draft):
        idx_str = m.group("idx")
        if idx_str:
            found_indices.append(int(idx_str))
    duplicates = [i for i in set(found_indices) if found_indices.count(i) > 1]
    if duplicates:
        raise ValueError(f"error: {name}: duplicate sentinel(s) found in draft: {duplicates}")

    # Perform replacement
    # Sort positions by start descending to replace in reverse
    positions.sort(key=lambda x: x[1][0], reverse=True)
    body = draft
    for tok, (start, end) in positions:
        repl = tok.restored
        body = body[:start] + repl + body[end:]

    # Remove any extra empty lines left by dropped headers (like book title)
    body = re.sub(r"\n{3,}", "\n\n", body.strip())

    return f"---\nstatus: {FINAL_STATUS}\n---\n\n{body}\n"


def check_files(paths: list[Path]) -> int:
    """Verify that fa/ files have no leaked sentinels and valid front matter."""
    errors = 0
    checked = 0
    for p in paths:
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        checked += 1

        # Check for un-restored sentinels
        leaked = list(SENTINEL_RE.finditer(text))
        if leaked:
            print(f"error: {p.name}: contains {len(leaked)} un-restored sentinel(s):", file=sys.stderr)
            for lk in leaked:
                line_no = text.count("\n", 0, lk.start()) + 1
                print(f"  Line {line_no}: {lk.group(0)}", file=sys.stderr)
            errors += 1

        # Check frontmatter
        doc = _md.read(p)
        if doc.status not in ("reviewed", "untranslated"):
            print(f"error: {p.name}: invalid front matter status: {doc.status!r}", file=sys.stderr)
            errors += 1

    if errors:
        print(f"\napparatus check: {errors} error(s) in {checked} file(s)", file=sys.stderr)
        return 1
    print(f"apparatus check: {checked} file(s) clean")
    return 0


def roundtrip_test(paths: list[Path]) -> int:
    """Run an identity round-trip (strip then restore without MT) on source files."""
    for p in paths:
        src = p.read_text(encoding="utf-8")
        name = p.name
        stripped = strip(name, src)
        restored = restore(name, src, stripped)

        # Check that no sentinels remain in restored text
        if SENTINEL_RE.search(restored):
            print(f"FAIL: round-trip left sentinels in {name}", file=sys.stderr)
            return 1

        # Check that frontmatter status is reviewed
        if "status: reviewed" not in restored:
            print(f"FAIL: round-trip did not set status: reviewed in {name}", file=sys.stderr)
            return 1

        print(f"PASS: round-trip test on {name} clean")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true", help="check fa/ files for sentinel leakage")

    sub = parser.add_subparsers(dest="command")

    # strip command
    p_strip = sub.add_parser("strip", help="strip apparatus tokens into sentinels")
    p_strip.add_argument("source", type=Path, help="source markdown file")
    p_strip.add_argument("-o", "--output", type=Path, help="output stripped file")

    # restore command
    p_restore = sub.add_parser("restore", help="restore apparatus tokens into translated draft")
    p_restore.add_argument("source", type=Path, help="original source markdown file")
    p_restore.add_argument("draft", type=Path, help="translated draft file with sentinels")
    p_restore.add_argument("-o", "--output", type=Path, help="output restored file")

    # check subcommand
    p_check = sub.add_parser("check", help="check fa/ files for sentinel leakage")
    p_check.add_argument("paths", nargs="*", type=Path, help="files to check (default: fa/*.md)")

    # roundtrip-test command
    p_test = sub.add_parser("roundtrip-test", help="run identity strip+restore test on source files")
    p_test.add_argument("paths", nargs="+", type=Path, help="source files to test")

    args = parser.parse_args(argv)

    if args.check:
        paths = sorted((REPO / "fa").glob("*.md"))
        return check_files(paths)

    if args.command == "check":
        paths = args.paths or sorted((REPO / "fa").glob("*.md"))
        return check_files(paths)

    if args.command == "strip":
        src_text = args.source.read_text(encoding="utf-8")
        out_text = strip(args.source.name, src_text)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out_text, encoding="utf-8")
        else:
            sys.stdout.write(out_text)
        return 0

    if args.command == "restore":
        src_text = args.source.read_text(encoding="utf-8")
        draft_text = args.draft.read_text(encoding="utf-8")
        try:
            out_text = restore(args.source.name, src_text, draft_text)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out_text, encoding="utf-8")
        else:
            sys.stdout.write(out_text)
        return 0

    if args.command == "roundtrip-test":
        return roundtrip_test(args.paths)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
