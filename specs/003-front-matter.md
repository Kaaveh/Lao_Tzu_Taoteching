# 003 — Front Matter

**`fa/title-page.md`, `fa/preface.md`, `fa/translators-introduction.md` · 3 files · ~33,700 characters**

---

## 1. Context

The front matter sets the stage for the book and provides vital historical, cultural, and sinological background:
- **`title-page.md`**: Outer presentation: Cover image, book title, subtitle, translator credit, personal dedication (*for Ku Lien-chang*), and full-page map of ancient China.
- **`preface.md`**: Red Pine's *Preface to the Revised Edition*, recounting the 1993 discovery of the Kuotien bamboo slips.
- **`translators-introduction.md`**: Red Pine's extensive *Introduction to the 1996 Edition* (31,563 characters). Discusses the lunar origin of the Tao, the biographical account of Lao-tzu in Ssu-ma Ch'ien's *Shihchi*, the journey west to Hanku Pass and Loukuantai, the Mawangtui silk discovery, and the tradition of Chinese commentators.

---

## 2. Requirements & Challenges

### 2.1 Multi-Chunk Processing for the Introduction
- At 31,563 characters, `translators-introduction.md` exceeds Google Translate's 5,000-character cap by more than 6x.
- `gtranslate.py` will split the file into **7 to 8 chunks** at paragraph boundaries.
- **Sentinel Discipline**:
  - The introduction contains several mid-sentence and standalone image tags:
    - `c1.jpg`, `c2.jpg`, `c3.jpg` (Tao, Head, and Go calligraphy graphs)
    - `f0xii-01.jpg` (Taijitu symbol)
    - `fxvii-01.jpg` (Hanku Pass photograph by Bill Porter)
    - `fxviii-01.jpg` (Loukuantai tile depiction by Bill Porter)
    - `f00xx-01.jpg` (Mawangtui Text A on silk)
  - `apparatus.py strip` must isolate each image into a numbered sentinel (`⟦IMG:1⟧` ... `⟦IMG:7⟧`) before chunking, so no image tag is bisected across a chunk boundary.

### 2.2 Poetic & Chinese Dates
Red Pine signs both prefaces with traditional Chinese calendar formulations:
- *Autumn at the Gate, Year of the Ox / Port Townsend, Washington*  
  → **پاییز در دروازه، سالِ گاو نر / پورت تاونزند، واشینگتن**
- *First Quarter, Last Moon, Year of the Pig / Port Townsend, Washington*  
  → **تربیع اول، آخرین ماه، سالِ خوک / پورت تاونزند، واشینگتن**

---

## 3. Execution Checklist

- [ ] `title-page.md`: Translated and formatted with cover and map images preserved.
- [ ] `preface.md`: Processed through `gTranslator` (`-w --raw`), restored, and normalized.
- [ ] `translators-introduction.md`:
  - [ ] Stripped via `apparatus.py`.
  - [ ] Translated via `gTranslator` (`-w --raw`).
  - [ ] Sentinels restored via `apparatus.py restore`.
  - [ ] Checked for smooth transitions across chunk seams.
  - [ ] All 7 embedded images verified visible and pointing to `media/images/...`.

---

## 4. Acceptance Criteria

- [ ] All 3 files written to `fa/` with YAML frontmatter `status: reviewed`.
- [ ] `tools/check_parity.py` validates block count parity for all 3 files.
- [ ] `tools/normalize.py` passes with zero orthographical warnings.
- [ ] All image references point correctly to existing files in `media/images/`.
