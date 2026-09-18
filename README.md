# Lao-tzu's Taoteching — Persian Translation Project

این مخزن شامل فرآیند ترجمه و مستندات کتاب *Lao-tzu's Taoteching* (ترجمه و شرح Red Pine / Bill Porter با گزیده تفسیرهای دو هزار سال گذشته) به زبان فارسی است.

## ساختار پروژه (Repository Structure)

- `fa/`: ترجمه فارسی فصل‌ها، پیش‌گفتارها و بخش‌های کتاب با فرانت‌متر مشخص و ساختار پاراگرافی همگام.
- `source/`: متن مرجع انگلیسی قطعه‌بندی‌شده بر اساس فصل‌ها و بخش‌ها (در فایل‌های محلی).
- `tools/`: ابزارهای خط فرمان برای بررسی توازی ساختاری (`check_parity`)، نرمال‌سازی خط فارسی (`normalize`)، کنترل اصطلاحات و اسامی مفسران (`check_terms`) و سنتینل‌های فرامتنی (`apparatus`).
- `specs/`: مشخصات فنی، مستندات معماری، تصمیمات سبکی و نقشه راه پروژه.
- `media/`: تصاویر، خطاطی‌های چینی، نقشه‌ها و نشان‌های کتاب برای استفاده در نسخه ترجمه فارسی.

## نقشه راه پروژه (Specs Roadmap)

جزئیات کامل معماری و گام‌های پیاده‌سازی در [`specs/README.md`](specs/README.md) در دسترس است:

| #   | مشخصه (Spec)                                                      | وابستگی | وضعیت (Status) |
|-----|-------------------------------------------------------------------|---------|----------------|
| 000 | [Overview & Shared Context](specs/000-overview.md)                | —       | ✅ Done        |
| 001 | [Apparatus, Sentinels & Tooling](specs/001-apparatus-and-tooling.md) | 000  | ✅ Done        |
| 002 | [Style Decisions & Terminology](specs/002-style-and-terminology.md) | 000   | ✅ Done        |
| 003 | [Front Matter](specs/003-front-matter.md)                         | 001, 002| ✅ Done        |
| 004 | [Book One: The Tao (Verses 1–37)](specs/004-book-one-tao.md)      | 001, 002| ✅ Done        |
| 005 | [Book Two: The Te (Verses 38–81)](specs/005-book-two-te.md)       | 004     | 🟨 Ready       |
| 006 | [Back Matter & Glossary](specs/006-back-matter.md)                | 004, 005| 🟨 Ready       |
| 007 | [Quarto Typesetting & Publication](specs/007-quarto-and-publication.md) | 003–006 | 🟨 Ready |

## مجوز و کپی‌رایت (License & Copyright Notice)

به دلیل رعایت حقوق نشر و مجوز متن انگلیسی کتاب اصلی، فایل متن کامل انگلیسی، فایل منبع کتاب الکترونیکی (`.epub`) و نسخه‌های پشتیبان در مخزن گیت نگهداری نشده و در فایل `.gitignore` مسدود شده‌اند. این مخزن صرفاً جهت توسعه و نگهداری ترجمه فارسی این اثر در نظر گرفته شده است.
