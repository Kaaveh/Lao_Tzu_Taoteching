# 006 — Back Matter & Glossary

**`fa/glossary.md`, `fa/about-the-translator.md`, `fa/colophon.md` · 3 files · ~47,300 characters**

---

## 1. Context

The back matter contains the critical reference apparatus that anchors Red Pine's edition:
1. **`glossary.md`**: An extensive biographical, textual, and conceptual dictionary (44,881 characters). It documents over 80 commentators, historical figures (Yellow Emperor, Shun, Confucius), ancient Chinese classics (*Yiching*, *Shuching*, *Shihching*, *Shuowen*), and archaeological sites (Mawangtui, Kuotien, Tunhuang). Each entry includes Wade-Giles and Pinyin spellings and Chinese calligraphy character images.
2. **`about-the-translator.md`**: Biographical profile of Bill Porter / Red Pine and a list of his translated works.
3. **`colophon.md`**: Special Thanks (Copper Canyon Press pressmark) and Major Support acknowledgments.

---

## 2. Requirements & Challenges

### 2.1 The Glossary Chunking Protocol
- At ~44,881 characters, `glossary.md` will be segmented into **10 to 11 chunks** by `gtranslate.py`.
- **The Entry Structure**:
  ```markdown
  WANG PI / WANG BI / ![WANG PI](media/images/f0178-08.jpg) (226–249). Famous for the quickness of his mind...
  ```
- **Sentinel Requirements**:
  - The glossary contains over 80 inline calligraphy graphics (`media/images/f0165-01.jpg` through `f0181-02.jpg`).
  - `apparatus.py strip` must isolate every single image token into a unique sentinel (`⟦IMG:GLOSS_01⟧`, etc.) so that Google Translate does not delete or alter them across chunk boundaries.
  - `restore` must verify that every single entry retains its calligraphy image and dates.

### 2.2 Harmonizing Headwords
- The Persian headwords in `fa/glossary.md` must strictly correspond to the canonical forms established in `002-style-and-terminology.md`.
- Example:
  ```markdown
  وانگ پی / WANG PI / WANG BI / ![WANG PI](media/images/f0178-08.jpg) (۲۲۶–۲۴۹ م.)
  ```

### 2.3 About the Translator & Colophon
- Translates Bill Porter's journey from Columbia University to Taiwan monasteries and Port Townsend.
- Bibliography titles should give the Persian descriptive title alongside the English/Chinese original.
- Colophon reproduces the Copper Canyon Pressmark (`f0186-01.jpg`) and Major Support (`f0187-01.jpg`).

---

## 3. Acceptance Criteria

- [ ] `glossary.md` translated via multi-chunk `gTranslator` with 100% of images preserved.
- [ ] Every commentator headword in `fa/glossary.md` matches the canonical spellings in `fa/01.md`–`fa/81.md`.
- [ ] `about-the-translator.md` and `colophon.md` translated, formatted, and verified.
- [ ] `check_parity.py` passes for all 3 files.
- [ ] All 3 files marked `status: reviewed`.
