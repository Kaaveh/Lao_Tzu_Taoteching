# Specs Roadmap — taoteching-farsi

Roadmap and specifications for translating Red Pine's English translation and commentary of *Lao-tzu's Taoteching* into Persian.

Shared architectural context and tooling pipeline: [`000-overview.md`](./000-overview.md).

## Status Table

| #   | Spec                                                              | Depends on | Status         |
|-----|-------------------------------------------------------------------|------------|----------------|
| 000 | [Overview & Shared Context](./000-overview.md)                    | —          | ✅ Done        |
| 001 | [Apparatus, Sentinels & Tooling](./001-apparatus-and-tooling.md)   | 000        | ✅ Done        |
| 002 | [Style Decisions & Terminology](./002-style-and-terminology.md)   | 000        | ✅ Done        |
| 003 | [Front Matter](./003-front-matter.md)                             | 001, 002   | ✅ Done        |
| 004 | [Book One: The Tao (Verses 1–37)](./004-book-one-tao.md)          | 001, 002   | ✅ Done        |
| 005 | [Book Two: The Te (Verses 38–81)](./005-book-two-te.md)           | 004        | ✅ Done        |
| 006 | [Back Matter & Glossary](./006-back-matter.md)                    | 004, 005   | 🟨 Ready       |
| 007 | [Quarto Typesetting & Publication](./007-quarto-and-publication.md)| 003–006    | 🟨 Ready       |

## Recommended Execution Order

```
001 → 002 → 004 (Pilot 01–09) → 004 (Rest of Tao 10–37) → 005 (Te 38–81) → 003 (Front) → 006 (Back) → 007 (Publish)
tooling style      pilot                    body                       body            intro          glossary      ship
```

- **001 (Tooling & Sentinels) comes first.** Machine translation mangles inline markdown image tags and commentator headers. The `strip` / `restore` apparatus adapter must be working before translating a single file.
- **002 (Style & Terminology) next.** Settles the canonical Persian names for all 25+ classical commentators (Wang Pi, Ho-shang Kung, Su Ch'e, etc.) and core philosophical terms (Tao, Te, Wu-wei, Sage, P’u, Xuan).
- **004 (Verses 1–9 as Pilot).** The first 9 verses test the duality of poetic verse vs. scholarly commentary in real text before scaling to the rest of the book.
- **004 & 005 (The 81 Verses).** The core of the work. Each chapter contains the verse poem, the calligraphy plate, the commentaries, and Red Pine's textual notes.
- **003 (Front Matter) late.** The 1996 Introduction is 31,500 characters of dense historical sinology — translating it after the main body ensures terminology consistency.
- **006 (Back Matter) after the body.** The 45,000-character glossary contains biographies of all commentators; its headwords must mirror the exact forms used across the body chapters.
- **007 (Quarto & Publication).** LuaLaTeX PDF typesetting, RTL web reader, EPUB generation, and release automation.

## Corpus Scale

| Section Group                  | Files  | Characters (EN) | Description / Contents |
|--------------------------------|-------:|----------------:|------------------------|
| Front matter                   |      3 |          33,703 | Title page, Preface, 1996 Introduction (with maps & calligraphy) |
| Book One: The Tao (01–37)      |     37 |         136,547 | Verses 1 through 37 (Poem + Commentaries + Notes) |
| Book Two: The Te (38–81)       |     44 |         150,976 | Verses 38 through 81 (Poem + Commentaries + Notes) |
| Back matter                    |      3 |          47,356 | Glossary (44.8k), About Translator, Colophon |
| **Total**                      | **87** |     **368,582** | Full book corpus |

## Definition of Done (Every Spec)

- [ ] Every item in the spec's **Acceptance Criteria** is checked and true.
- [ ] Source files processed strictly one by one through `gTranslator` using `-w --raw` and the sentinel apparatus.
- [ ] No dropped lines, images, commentator attributions, or paragraphs (`check_parity` passes).
- [ ] Persian orthography normalized (ZWNJ discipline, Persian digits, `«...»` quotes, no Arabic Yeh/Kaf).
- [ ] Commentator names strictly adhere to the canonical table in `002-style-and-terminology.md`.
- [ ] `status:` front matter in `fa/` set to `reviewed`.
