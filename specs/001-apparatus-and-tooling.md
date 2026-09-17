# 001 — Apparatus, Sentinels & Tooling

This specification establishes the mechanical apparatus and checking tools required to run automated, lossless machine translation across the book without losing images, commentary structures, or formatting.

---

## 1. The Problem: What Machine Translation Destroys

When markdown text is translated through Google Translate's Advanced (Gemini) model:
1. **Markdown Images**: `![Verse 1 Calligraphy](media/images/f0002-01.jpg)` is routinely stripped entirely or converted into mangled prose like `[Verse 1 Calligraphy] (media / images / ...)`.
2. **Commentator Headings**: `**WANG PI** says, ...` is rendered arbitrarily across different chapters (e.g. `وانگ پی می‌گوید`, `وانگ پی بیان می‌کند`, `پادشاه پی گفت`), corrupting cross-chapter consistency.
3. **Verse Headings**: `### Verse 1 — The way that becomes a way` gets translated redundantly rather than using the standardized Persian heading structure `# ۱`.
4. **Dividers**: `![divider](media/images/common.jpg)` is often lost.

---

## 2. The Solution: `tools/apparatus.py`

`tools/apparatus.py` acts as a pre- and post-processor adapter around `gTranslator`:

### 2.1 The `strip` Phase
Before sending to `gTranslator`, `apparatus.py strip` replaces volatile tokens with inert Unicode bracketed sentinels (`⟦...⟧`) that Google Translate's Advanced model reliably preserves in-place:

| Source Token | Sentinel Form |
|---|---|
| `![Verse N Calligraphy](media/images/...)` | `⟦IMG:CALLIGRAPHY⟧` |
| `![divider](media/images/common.jpg)` | `⟦IMG:DIVIDER⟧` |
| `![Map ...](media/images/...)` | `⟦IMG:MAP⟧` |
| `**HO-SHANG KUNG** says,` | `⟦COMM:HO_SHANG_KUNG:SAYS⟧` |
| `**WANG PI** says,` | `⟦COMM:WANG_PI:SAYS⟧` |
| `**HO-SHANG KUNG** titles this verse:` | `⟦COMM:HO_SHANG_KUNG:TITLES⟧` |
| `### Verse N — Title` | `⟦HDR:N:Title⟧` |

### 2.2 The `restore` Phase
After translation returns from `gTranslator`, `apparatus.py restore` matches sentinels and re-emits:
- The exact original image path (`media/images/...`).
- The canonical Persian commentator name and verb (e.g. `**وانگ پی** می‌گوید:`).
- Standardized level-1 Persian verse headings (e.g. `# ۱ — راهی که به راه می‌آید`).
- YAML frontmatter with `status: reviewed`.

### 2.3 Refusal & Lost Sentinel Detection
If Google Translate drops or duplicates a sentinel:
- `restore` must **refuse to write the output file**.
- It reports the exact lost sentinel and quotes the line in `source/` where it originated.
- The user can place a bare sentinel `⟦...⟧` in `/tmp/NN.fa.md` and re-run `restore`.

---

## 3. Imported Checking Tools

We adopt the modular checkers established in the Lin-chi project, configured via `pyproject.toml`:

### 3.1 `tools/normalize.py` (Orthography Checker & Fixer)
Enforces Iranian Persian typographic standards:
- Replaces Arabic Yeh (`ي`) and Kaf (`ك`) with Persian `ی` and `ک`.
- Corrects ZWNJ (Zero-Width Non-Joiner) placement for prefixes (`می‌`, `نمی‌`) and suffixes (`ها`, `ای`, `تر`).
- Converts Western ASCII digits (`0-9`) to Persian digits (`۰-۹`) in headings and prose where appropriate.
- Normalizes English quotes (`"..."`, `“...”`) to Persian guillemets (`«...»`).
- Detects and flags dangerous Unicode bidirectional overrides.

### 3.2 `tools/check_parity.py` (Block Parity Verifier)
- Compares paragraph block counts between `source/` and `fa/`.
- Ensures no paragraphs or commentaries were dropped during chunk stitching.
- Supports `<!-- parity: offset -1 -->` where structural headings (e.g. `## Lao-tzu's Taoteching` on `01.md`) are handled at the Quarto book level.

### 3.3 `tools/make_stubs.py` (Initial Stub Generator)
- Reads all files in `source/` (excluding `README.md`).
- Generates corresponding initial stubs in `fa/` with:
  ```markdown
  ---
  status: untranslated
  ---

  # ۱

  <!-- TODO: translate -->
  ```

---

## 4. Acceptance Criteria

- [ ] `tools/apparatus.py` implemented with `strip`, `restore`, and `--check` commands.
- [ ] Round-trip test on `source/01.md` and `source/38.md`: stripping and restoring without translation produces 100% valid tokens.
- [ ] `tools/normalize.py`, `tools/check_parity.py`, and `tools/make_stubs.py` ported and operating cleanly.
- [ ] `pyproject.toml` created with `[tool.book]`, `[tool.normalize]`, and commentator mapping table.
- [ ] `make_stubs.py` successfully populates `fa/` with 87 initial `untranslated` stubs.
