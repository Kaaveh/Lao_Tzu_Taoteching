# 007 — Quarto Typesetting & Publication

This specification defines the multi-format publishing infrastructure (HTML, PDF, EPUB) using Quarto, LuaLaTeX Persian typesetting, and release automation.

---

## 1. Publishing Architecture

Following the proven infrastructure of *The Zen Teachings of Master Lin-chi*, the book is compiled from the single source tree in `fa/` into three distinct formats:
1. **Interactive RTL Web Book**: Published online with responsive navigation and search.
2. **Typeset Persian PDF**: Professional book layout rendered via **LuaLaTeX** using Persian typography.
3. **EPUB E-book**: Standard digital reader format with embedded calligraphy plates.

---

## 2. Quarto Configuration (`_quarto.yml`)

The Quarto book organizes the 87 files into logical parts:
```yaml
project:
  type: book
  output-dir: _book

book:
  title: "دائو د جینگ لائوتزو"
  subtitle: "با گزیده تفسیرهای دو هزار سال گذشته — ترجمه و شرح رِد پاین"
  author: "کاوه"

  repo-url: https://github.com/Kaaveh/taoteching-farsi
  repo-branch: main
  repo-actions: [edit, issue]
  downloads: [pdf, epub]
  search: true

  sidebar:
    style: docked
    collapse-level: 1

  chapters:
    - index.md
    - fa/title-page.md
    - fa/preface.md
    - fa/translators-introduction.md
    - part: "دفتر یکم: دائو (بخش‌های ۱ تا ۳۷)"
      chapters:
        - fa/01.md
        - fa/02.md
        # ... through fa/37.md
    - part: "دفتر دوم: دِ / فضیلت (بخش‌های ۳۸ تا ۸۱)"
      chapters:
        - fa/38.md
        - fa/39.md
        # ... through fa/81.md
    - fa/glossary.md
    - fa/about-the-translator.md
    - fa/colophon.md
```

---

## 3. PDF Engine: Why LuaLaTeX over XeLaTeX

As established in the Lin-chi project (`tex/preamble.tex`):
- Under XeLaTeX, Babel's `bidi=default` reverses Latin-script runs when embedded inside Persian text (e.g. English titles, Pinyin names, or dates).
- **LuaLaTeX (`lualatex`) correctly handles bidirectional text runs** without corrupting mixed Latin/Persian sentences.
- **Font Selection**: Primary text uses *Vazirmatn* (or Persian serif font), with poetry styling and Nastaliq accents where appropriate.

---

## 4. Build Automation (`justfile`)

We define task recipes in a root `justfile`:

```makefile
# Run all linters and checkers
check:
    python3 -m tools.check_parity
    python3 -m tools.normalize --check
    python3 tools.apparatus --check

# Auto-correct orthography
fix:
    python3 -m tools.normalize --fix

# Build all formats
build:
    quarto render

# Live web preview
serve:
    quarto preview
```

---

## 5. Acceptance Criteria

- [x] `_quarto.yml` created and all 87 chapters registered in order.
- [x] `index.md` created with Persian book overview, version, date, and license metadata.
- [x] `tex/preamble.tex` configured for LuaLaTeX RTL typesetting.
- [x] `justfile` created with `check`, `fix`, `build`, and `serve` commands.
- [x] `quarto render` succeeds locally without errors for HTML, PDF, and EPUB.
