# taoteching-farsi — Persian Translation of Red Pine's *Lao-tzu's Taoteching*

Persian translation of Red Pine's (Bill Porter) English rendering and annotated edition of *Lao-tzu's Taoteching* (道德經), with selected commentaries of the past 2,000 years.

Pandoc Markdown, one file per section (87 sections total across Front matter, Book One: The Tao, Book Two: The Te, and Back matter), built by Quarto into HTML, PDF (LuaLaTeX), and EPUB.

---

## Core Rules & Constraints

- **Never invent a Persian rendering and present it as settled.** Terminology must strictly adhere to [`specs/002-style-and-terminology.md`](specs/002-style-and-terminology.md). Commentator names must follow the canonical table (Wang Pi = وانگ پی, Ho-shang Kung = هو-شانگ کونگ, Su Ch'e = سو چِه, etc.).
- **Never commit source text to this repository.** `source/` is gitignored because the English text and apparatus are copyrighted. It is present locally for translation and parity checks only.
- **Translate with `gTranslator`, strictly one file at a time.** It lives at `~/Project/Backend/gTranslator`. Never concatenate files.
  
  ```bash
  GT=~/Project/Backend/gTranslator
  python3 tools/apparatus.py strip source/01.md -o /tmp/01.en.md
  "$GT/.venv/bin/python" "$GT/gtranslate.py" \
      -f /tmp/01.en.md -t fa -w --raw -o /tmp/01.fa.md
  python3 tools/apparatus.py restore source/01.md /tmp/01.fa.md -o fa/01.md
  python3 -m tools.normalize fa/01.md
  python3 -m tools.check_parity fa/01.md
  ```

- **The `-w` and `--raw` flags are mandatory.**
  - `-w` drives real Chrome via Playwright with a desktop User-Agent to bypass Google's headless detection and ensure the Advanced (Gemini) model is served.
  - `--raw` instructs `gtranslate.py` to preserve poetic line breaks as-is.
  - *Silent Failure Mode*: Google may silently serve Classic NMT while the UI claims "Advanced". Judge strictly by the output quality, never the picker.
- **Always process through `tools/apparatus.py`.** Sent raw, machine translation strips calligraphy plates (`media/images/...`), mangles commentator headers, and drops dividers.
- **When `restore` refuses due to dropped sentinels:**
  - Google Translate may drop or duplicate a sentinel (e.g. `⟦IMG:CALLIGRAPHY⟧` or `⟦COMM:WANG_PI:SAYS⟧`).
  - `restore` refuses to write the output and reports which sentinel was dropped and the matching source line.
  - Insert the missing bare sentinel `⟦...⟧` into `/tmp/NN.fa.md` at the corresponding location in the Persian text and re-run `restore`.
  - Never edit `fa/` directly for sentinel repair — always repair in `/tmp/NN.fa.md` and let `restore` validate and write to `fa/`.
- **Frontmatter in `fa/`:**
  - Every file in `fa/` opens with YAML front matter:
    ```markdown
    ---
    status: reviewed
    ---
    ```
  - Only two statuses are valid: `untranslated` (initial stubs) and `reviewed` (pipeline-verified).
- **One sentence per line in everything under `fa/`.** Facilitates readable right-to-left git diffs and pinpoint error reporting.
- **Persian Typography & Orthography:**
  - Persian digits (`۰-۹`) in headings and prose.
  - Persian quotes: `«...»`.
  - Proper ZWNJ (نیم‌فاصله) discipline (`می‌شود`, `کتاب‌ها`, `بی‌عملی`).
  - Persian `ی` (U+06CC) and `ک` (U+06A9) only; no Arabic forms.

---

## Repository Layout

```
Lao-tzu's Taoteching/
├── .gitignore             # source/ and build artifacts ignored
├── CLAUDE.md              # Project instructions and rules
├── pyproject.toml         # Tooling configuration & commentator maps
├── media/images/          # Calligraphy, maps, and illustrations
├── source/                # 87 English source files + README.md (Git ignored)
├── fa/                    # 87 Persian translated files (Git tracked)
├── specs/                 # Roadmap and execution specs
└── tools/                 # Parity checkers, apparatus, normalization
```

---

## Quality Bar

- `python3 -m tools.check_parity` and `python3 -m tools.normalize --check` clean before every commit.
- Parity between `source/` and `fa/` block counts verified.
- Canonical commentator names verified against `specs/002-style-and-terminology.md`.
- Commit convention: `translate(chNN):`, `revise(chNN):`, `term:`, `tools:`, `docs:`, `build:`.
