# 004 — Book One: The Tao (Verses 1–37)

**`fa/01.md` – `fa/37.md` · 37 sections · ~136,500 characters · 37 calligraphy plates**

---

## 1. Context

Book One (the *Tao Ching* or کتابِ دائو) encompasses the first 37 chapters of the *Taoteching*. It lays down the metaphysical, cosmological, and spiritual foundation of the Tao:
- The nameless origin of Heaven and Earth (Verse 1).
- The relativity of opposites and effortless action (Verse 2).
- The empty vessel that never fills (Verse 4).
- The valley spirit and the dark womb (Verse 6).
- The virtue of water seeking the lowest place (Verse 8).
- The hub of the wheel, clay vessel, and doors/windows (Verse 11).
- The nebulous, mother-like primordial reality (Verse 25).
- Non-contention, humility, and the feminine (Verses 28, 36).

Every chapter contains:
1. Level-1 Verse heading (`# ۱` or `# ۱ — راهی که به راه می‌آید`).
2. Calligraphy plate (`![Verse N Calligraphy](media/images/fXXXX-01.jpg)`).
3. The Taoist poetic verse lines.
4. Classical commentaries (averaging 8 to 12 commentators per verse).
5. Red Pine's textual commentary.

---

## 2. The Pilot: Verses 01 through 09

Before translating all 37 sections, **Verses 01 to 09 serve as the pilot**.
- **Goal**: Test the interaction between `apparatus.py`, `gTranslator -w --raw`, and `normalize.py` on real text.
- **Why 01–09?**:
  - Verse 1 contains 10 commentators and key metaphysical terminology (Immortal Way, Maiden, Mother, Dark beyond dark).
  - Verse 2 contains 9 commentators, contrasting pairs, and effortless action (*wu-wei*).
  - Verse 8 exercises water metaphors and ethical registers.
- **Parity offset on `01.md`**:
  `source/01.md` begins with `## Lao-tzu's Taoteching` above `### Verse 1`. In `fa/01.md`, this is represented as `# ۱`, declaring `<!-- parity: offset -1 -->` if needed.

---

## 3. Section Checklist (Book One: The Tao)

### Pilot Phase (01–09)
- [x] `01.md` — The way that becomes a way (10 commentators)
- [x] `02.md` — All the world knows beauty (9 commentators)
- [x] `03.md` — Bestowing no honors (9 commentators)
- [x] `04.md` — The Tao is so empty (10 commentators)
- [x] `05.md` — Heaven and Earth are heartless (10 commentators)
- [x] `06.md` — The valley spirit that doesn’t die (11 commentators)
- [x] `07.md` — Heaven is eternal and Earth is immortal (13 commentators)
- [x] `08.md` — The best are like water (11 commentators)
- [x] `09.md` — Instead of pouring in more (8 commentators)

### Main Tao Sequence (10–37)
- [x] `10.md` — Can you keep your crescent soul from wandering (8 commentators)
- [x] `11.md` — Thirty spokes converge on a hub (10 commentators)
- [x] `12.md` — The five colors make our eyes blind (7 commentators)
- [x] `13.md` — Favor and disgrace come with a warning (9 commentators)
- [x] `14.md` — We look but don’t see it (9 commentators)
- [x] `15.md` — The great masters of ancient times (5 commentators)
- [x] `16.md` — Keeping emptiness as their limit (8 commentators)
- [x] `17.md` — During the High Ages people knew they were there (8 commentators)
- [x] `18.md` — When the Great Way disappears (11 commentators)
- [x] `19.md` — Get rid of wisdom and reason (8 commentators)
- [x] `20.md` — Get rid of learning and problems will vanish (8 commentators)
- [x] `21.md` — The appearance of Empty Virtue (10 commentators)
- [x] `22.md` — The incomplete become whole (10 commentators)
- [x] `23.md` — Whispered words are natural (9 commentators)
- [x] `24.md` — Those who tiptoe don’t stand (7 commentators)
- [x] `25.md` — Imagine a nebulous thing (7 commentators)
- [x] `26.md` — Heavy is the root of light (11 commentators)
- [x] `27.md` — Good walking leaves no tracks (8 commentators)
- [x] `28.md` — Recognize the male (9 commentators)
- [x] `29.md` — Trying to govern the world with force (12 commentators)
- [x] `30.md` — Use the Tao to assist your lord (8 commentators)
- [x] `31.md` — Weapons are not auspicious tools (7 commentators)
- [x] `32.md` — The Tao remains unnamed (11 commentators)
- [x] `33.md` — Those who know others are perceptive (12 commentators)
- [x] `34.md` — The Tao drifts (10 commentators)
- [x] `35.md` — Hold up the Great Image (10 commentators)
- [x] `36.md` — What you would shorten (7 commentators)
- [x] `37.md` — The Tao makes no effort at all (8 commentators)

---

## 4. Acceptance Criteria

- [x] All 37 sections processed through the single-file pipeline (`strip` → `gtranslate` → `restore`).
- [x] All 37 files written to `fa/01.md` .. `fa/37.md` with `status: reviewed`.
- [x] Every section carries its calligraphy plate with valid relative path `media/images/...`.
- [x] Commentator attributions match the canonical table in `002-style-and-terminology.md`.
- [x] `check_parity.py` reports 100% block parity across all 37 sections.
- [x] `normalize.py` confirms clean Persian typography.
