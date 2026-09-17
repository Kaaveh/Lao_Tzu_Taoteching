# 000 — Overview & Shared Context

This document establishes the architecture, tooling pipeline, and core constraints for translating *Lao-tzu's Taoteching* (translated and annotated by Red Pine) from English into Persian.

---

## 1. Project Goal & Philosophy

To produce a faithful, elegant Persian translation of Red Pine’s seminal edition of the *Taoteching*, preserving:
1. **The Poetic Verses**: Lao-tzu's original 81 poems in terse, evocative, mystical Persian.
2. **The Calligraphy Plates**: The original calligraphy images accompanying each verse.
3. **The Classical Commentary Tradition**: Selected insights from over 2,000 years of Chinese hermeneutics (Wang Pi, Ho-shang Kung, Su Ch'e, Te-ch'ing, etc.).
4. **The Textual Scholarship**: Red Pine's sinological apparatus documenting variations from the Mawangtui silk manuscripts, Kuotien bamboo slips, and Fuyi editions.

Like its sibling project (*The Zen Teachings of Master Lin-chi*), translation is performed chapter-by-chapter using an automated, high-fidelity pipeline driven by `gTranslator`, backed by Google Translate's Advanced (Gemini) model, followed by automated orthographical normalization and structural parity verification.

---

## 2. Deep Dive: The `gTranslator` Engine

The translation engine is hosted at:
`/Users/kaavehmohamedi/Project/Backend/gTranslator`

Its operational characteristics and mechanisms dictate how this project must interact with it:

### The Two Models: Classic vs. Advanced (Gemini)
Google Translate operates two drastically different translation backends:
- **Classic (NMT)**: The legacy neural machine translation engine. Translates phrase-by-phrase or clause-by-clause. Produces flat, mechanical, often ungrammatical Persian.
- **Advanced ("Built with Gemini")**: Available on the web interface. Reads the entire context, understands poetic and philosophical registers, adds proper *ezafe*, and re-orders clauses naturally.

### The Headless Gate (User-Agent Detection)
As documented in `gTranslator/README.md`, **Google denies the Advanced model to any client identifying as `HeadlessChrome`**.
- Default HTTP APIs (`translate_a`, Cloud Translation API v2) **never** serve the Advanced model.
- Chromium running headless by default sends `HeadlessChrome` in its User-Agent string, causing Google to silently downgrade the session to Classic.
- `gTranslator` solves this by driving real Chrome via Playwright with an explicit, overridden Desktop Chrome User-Agent.

> [!WARNING]
> **Silent Failure Mode**
> Even when Google silently downgrades a session to Classic, the UI menu still displays `aria-checked="true"` for "Advanced". Never trust the picker; judge by the output quality.

### Line Breaks & The `--raw` Flag
By default, `gTranslator` attempts to undo line wraps (designed for scanned PDFs). In *Lao-tzu's Taoteching*, verse lines are intentional poetic units.
- **The `--raw` flag is mandatory.** It instructs `gtranslate.py` to preserve source line breaks as-is, which the Advanced model honors.

### Rate Limits & Character Caps
- The web interface caps single inputs at **5,000 characters**.
- `gtranslate.py` enforces internal chunking at **4,500 characters**, splitting on paragraph or sentence boundaries.
- Individual verses in this book are 3,000 to 4,200 characters, meaning nearly every verse processes in a single chunk with zero seam distortion.
- Longer documents (`translators-introduction.md` at 31.5k chars, `glossary.md` at 44.8k chars) split into 7–10 chunks.

---

## 3. The Translation Loop

Translation is strictly executed **one file at a time**. Never batch-concatenate files.

```
┌─────────────────┐
│  source/NN.md   │  (English Source)
└────────┬────────┘
         │
         ▼  tools/apparatus.py strip
┌─────────────────┐
│  /tmp/NN.en.md  │  (Images & commentators replaced with sentinels)
└────────┬────────┘
         │
         ▼  gTranslator (.venv/bin/python gtranslate.py -f ... -t fa -w --raw)
┌─────────────────┐
│  /tmp/NN.fa.md  │  (Raw Persian with sentinels preserved)
└────────┬────────┘
         │
         ▼  tools/apparatus.py restore
┌─────────────────┐
│    fa/NN.md     │  (Restored markdown with Persian headings & images)
└────────┬────────┘
         │
         ▼  normalize & verify (just fix / just check)
┌─────────────────┐
│ Final Edition   │  status: reviewed
└─────────────────┘
```

### The Shell Command
```bash
GT=~/Project/Backend/gTranslator

# 1. Strip images & apparatus into protected sentinels
python3 tools/apparatus.py strip source/01.md -o /tmp/01.en.md

# 2. Translate with Advanced (Gemini) model in raw mode
"$GT/.venv/bin/python" "$GT/gtranslate.py" \
    -f /tmp/01.en.md -t fa -w --raw -o /tmp/01.fa.md

# 3. Restore images, headers, and standard commentator attributions
python3 tools/apparatus.py restore source/01.md /tmp/01.fa.md -o fa/01.md

# 4. Normalize orthography & check parity
python3 -m tools.normalize fa/01.md
python3 -m tools.check_parity fa/01.md
```

---

## 4. The Markup Hazard in Taoteching

Unlike *Lin-chi* (which had inline footnote anchors `<a id="m2-2">`), *Taoteching* contains:
1. **Calligraphy & Plates**: `![Verse 1 Calligraphy](media/images/f0002-01.jpg)`.
2. **Commentator Headers**: `**HO-SHANG KUNG** says, “...”` or `**WANG PI** says, “...”`.
3. **Chinese Characters & Maps**: Inline references like `![Tao](media/images/c1.jpg)` and ancient China map plates.

If sent raw to Google Translate:
- Markdown image syntax is either deleted or altered into plain text brackets.
- Image paths (`media/images/...`) may get translated or broken.
- Commentator names are translated inconsistently (e.g. "Wang Pi" rendered as وانگ پی in one paragraph and وانگ بی or پادشاه پی in another).

**Spec 001** defines `tools/apparatus.py` to extract these into bracketed sentinels (`⟦IMG:1⟧`, `⟦COMM:WANG_PI⟧`) and restore them deterministically.

---

## 5. Repository Layout & File Conventions

```
Lao-tzu's Taoteching/
├── .gitignore             # source/ is ignored
├── pyproject.toml         # Tooling configuration & title maps
├── media/images/          # Calligraphy, maps, and illustrations
├── source/                # 87 English source files + README.md (Git ignored)
│   ├── title-page.md
│   ├── preface.md
│   ├── translators-introduction.md
│   ├── 01.md ... 81.md
│   ├── glossary.md
│   ├── about-the-translator.md
│   ├── colophon.md
│   └── README.md
├── fa/                    # 87 Persian translated files (Git tracked)
│   ├── title-page.md
│   ├── preface.md
│   ├── ...
│   └── 81.md
├── specs/                 # Roadmap and execution specs
└── tools/                 # Parity checkers, apparatus, normalization
```

### Front Matter in `fa/`
Every file in `fa/` opens with YAML front matter:
```markdown
---
status: reviewed
---
```
Only two states are used:
- `untranslated`: Initial stub generated by `make_stubs.py`.
- `reviewed`: Successfully processed through `restore`, normalized, and verified.
