# Fabius Bidi — right-to-left & bidirectional layout

Loaded on demand by `fabius-decor`. The skill has the visual laws; this file is the discipline for building **correct** surfaces (and prose) in right-to-left scripts — Hebrew, Arabic, Persian, Urdu and the rest — and for the **bidirectional** reality where an RTL sentence contains an LTR run (an English brand name, a URL, a phone number, a code token). Direction is a *design* concern, not an afterthought: get it wrong and the layout reads broken to a native reader even when every color and font is right.

**When this fires.** Any time the content — UI *or* prose — is in an RTL language, or mixes RTL and LTR. Not only when "building an RTL site": the same discipline applies to an email, a slide, a chart label, a PDF, a chat reply. If the primary language is RTL, the primary direction is RTL.

## The one law: author *logical*, mirror is a fallback

Never hardcode `left`/`right`, `margin-left`, `text-align:right`, `padding-left`. Author with **logical properties** that follow the reading direction, then set direction **once** at the root. A logical-first stylesheet is direction-agnostic — the *same* CSS serves LTR and RTL, and the layout mirrors itself when `dir` flips. Machine-flipping physical CSS after the fact (rtlcss / stylis-plugin-rtl) is a *retrofit* for code you don't control, not the way to write new code.

```html
<html lang="he" dir="rtl">   <!-- set BOTH: lang for the engine, dir for layout -->
```

- `lang` drives hyphenation, font selection, screen-reader voice, `:lang()` — set it to the real language (`he`, `ar`, `fa`, `ur`), not a generic.
- `dir="rtl"` on the root cascades to the whole tree. Set it on `<html>`, not just `<body>`, so form controls, scrollbars, and the UA mirror too.
- For a mostly-LTR page with an RTL island (or vice-versa), set `dir` on the *island's* container, not the root.

## The RTL scripts — set `dir` and pick a font that covers the glyphs

| Script | Major languages (BCP-47) | Notes |
|---|---|---|
| **Hebrew** | Hebrew `he`, Yiddish `yi`, Ladino `lad` | pure RTL; digits and Latin run LTR inside it |
| **Arabic** | Arabic `ar`, Persian/Farsi `fa`, Urdu `ur`, Pashto `ps`, Sindhi `sd`, Uyghur `ug`, Kurdish-Sorani `ckb`, Kashmiri `ks` | **cursive** — letters join and change shape by position; needs a font with contextual forms |
| **Thaana** | Divehi/Maldivian `dv` | RTL |
| **N'Ko** | Manding languages `nqo` | RTL, West Africa |
| **Syriac / Mandaic / Samaritan / Adlam** | liturgical & regional | RTL; rare on the web but real |

"RTL" is the base direction; **numbers are always visually left-to-right**, and embedded Latin runs LTR — which is exactly why bidi *isolation* below is not optional.

## Bidirectional text — isolate every foreign-direction run

The browser runs the **Unicode Bidirectional Algorithm** (UBA) automatically, classifying each character as strong (a letter — carries a direction), weak (digits, most punctuation), or neutral (spaces, symbols). Neutrals take the direction of their surroundings — which is where it breaks. The classic bug: a phone number, price, `@handle`, or English product name dropped into a Hebrew/Arabic sentence renders with its punctuation on the wrong side (`+972 3-555` becomes `555-3 972+`), because the neutral characters resolve against the RTL base.

**Fix: isolate the run so its bidi is computed independently.**

- In markup, wrap user-supplied or opposite-direction runs in **`<bdi>`** — "bidi isolate." It's the correct element for a name, a username, a value of unknown direction (its `dir` defaults to `auto` and doesn't inherit). Never trust interpolated data to be the base direction. Prefer semantic `<bdi>` over `<span style="unicode-bidi:isolate">` — a browser may ignore the CSS, never the element.
- For a run whose direction you genuinely don't know, `dir="auto"` picks the base from the **first strong character** (first-strong). The UBA already **mirrors bracket pairs** `()[]{}⟨⟩` on its own — never hardcode reversed brackets or quotes.
- `<bdo dir="ltr">` **overrides** direction (rare — use only to force, e.g. displaying raw bidi-control demos).
- In CSS, `unicode-bidi: isolate` (paired with `direction`) does the same for a styled span; `isolate-override` forces order within the isolate.
- When you build strings in JS (not the DOM), wrap runs in the isolate control characters: `⁦` (LRI) / `⁧` (RLI) / `⁨` (FSI, first-strong auto) … closed by `⁩` (PDI). `Intl` formatters can emit these for you (below).

Rule of thumb: **any value whose direction you didn't author is a bidi hazard — isolate it.**

## CSS logical properties — the swap table

Replace physical properties with flow-relative ones. `inline-start` = where the line *starts* (right, in RTL); `inline-end` = where it ends (left, in RTL). `block` is the vertical axis (unchanged by `dir`).

| Physical (don't) | Logical (do) |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `border-left` / `border-right` | `border-inline-start` / `border-inline-end` |
| `left: 0` / `right: 0` | `inset-inline-start: 0` / `inset-inline-end: 0` (or `inset-inline`) |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `float: left` / `right` | `float: inline-start` / `inline-end` |
| `border-radius` corners | `border-start-start-radius` … `border-end-end-radius` |
| fixed `width`/`height` | `inline-size` / `block-size` (bonus: writing-mode-safe) |
| `top`/`bottom` (vertical) | `inset-block-start` / `inset-block-end` |

Flexbox and grid are **already logical**: `flex-direction: row` follows `dir`, so a row of buttons reverses on its own — do **not** hand-reverse it with `row-reverse` (that double-flips). `justify-content: flex-start` maps to the inline start. `gap` is direction-safe.

**What has NO logical equivalent yet — these need a manual `[dir="rtl"]` override:**

- **`box-shadow` / `text-shadow`** offsets — a shadow throwing right must throw left in RTL. Flip the `x` offset under `[dir="rtl"]`.
- **`transform: translateX()`**, and any `transform` with a horizontal component (slide-in menus, carousels) — negate `x` in RTL.
- **`background-position`** (`left`/`right` keywords), **linear-gradient** angles / directional `to right`.
- **directional icons** (see mirroring) and background SVGs baked with a direction.
- Scroll math (`scrollLeft` is negative or reversed in RTL across engines — use `scrollIntoView` or logical scroll APIs; test).

Pattern for the exceptions — target with the **`:dir(rtl)`** pseudo-class (baseline, cleaner) or `[dir="rtl"]`, and override only the physical axis:

```css
.card { box-shadow: 8px 8px 24px rgba(0,0,0,.12); }      /* LTR default */
.card:dir(rtl) { box-shadow: -8px 8px 24px rgba(0,0,0,.12); }  /* flip X only */
/* older-engine fallback: [dir="rtl"] .card { ... } */
```

## Icon & asset mirroring — flip meaning, not identity

Direction-bearing glyphs must mirror; identity- or reality-bearing ones must **not**. Flipping a clock or a checkmark is a tell that a machine did the RTL, not a person.

| Flip in RTL (`transform: scaleX(-1)`) | Never flip |
|---|---|
| back / forward, next / previous arrows | play / pause / stop (media transport is universal) |
| chevrons, breadcrumb separators, "expand" carets pointing inline | checkmark ✓, ✗ |
| send / reply, undo ↩ / redo ↪ | clock / watch faces, hourglass |
| list bullets, indentation, quote marks, progress/steppers | numbers on a die, keyboard keys |
| tab/indent, "read more →", pagination | logos & brand marks (they have a fixed form) |
| skip-forward / rewind seek arrows | phone handset, most object icons (cart, gear, user, heart) |

Prefer an icon set that ships **directional variants** or logical names over blind `scaleX(-1)` (which also mirrors any embedded text or asymmetric shading). See **Fabius Iconarium** for sets with RTL-aware icons; mirror via a `[dir="rtl"] .icon-directional { transform: scaleX(-1); }` utility, not per-icon inline styles.

## Numbers, dates, currency — let `Intl` place them

- **Digits stay LTR.** Western Arabic numerals (0-9) and Eastern Arabic-Indic numerals (٠-٩, used in some `ar` locales) both render left-to-right inside RTL text. Don't fight it.
- Format with the locale, never by hand — it gets numeral system, grouping, currency-symbol side, and bidi marks right:

```js
new Intl.NumberFormat('ar-EG', { style: 'currency', currency: 'EGP' }).format(1234.5); // ١٬٢٣٤٫٥٠ ج.م.‏
new Intl.DateTimeFormat('he-IL', { dateStyle: 'long' }).format(new Date());
new Intl.RelativeTimeFormat('fa').format(-3, 'day');
```

- Currency symbol side and the thousands/decimal separators differ per locale — `Intl` knows; a hardcoded `$1,234.50` is wrong in most RTL locales.
- A bare number next to RTL text (a price in a table, a stat) is a neutral-boundary hazard — isolate it (`<bdi>` or the formatter's marks) so `12%` doesn't become `%12`.

## Fonts — a Latin webfont will not render Hebrew or Arabic

Most Latin webfonts have **no Hebrew/Arabic glyphs**; the browser silently falls back to a system font, so your careful type scale evaporates for exactly the readers who matter. Pick a font that covers the script (and verify glyph coverage — Chromium hides missing-glyph fallback that WebKit/iOS Safari exposes).

- **Hebrew (open-source):** Rubik, Heebo, Assistant, Alef, Noto Sans Hebrew, IBM Plex Sans Hebrew; editorial serif → Frank Ruhl Libre, David Libre.
- **Arabic/Persian/Urdu (open-source):** Noto Naskh Arabic & Noto Kufi Arabic, Cairo, Tajawal, IBM Plex Sans Arabic, Vazirmatn (Persian, variable), Amiri (Naskh serif); Urdu Nastaʿlīq → Noto Nastaliq Urdu.
- **Dual-script pairs** (one family, Latin + the script — best for mixed UI): Rubik & Assistant (Hebrew+Latin), IBM Plex Sans Arabic/Hebrew, Noto families, Vazirmatn.
- Arabic needs contextual joining and ligatures — use a real Arabic font (not a "supports Arabic" afterthought) and keep `font-feature-settings` defaults on; don't disable `liga`/`calt`.
- Self-host for reliability/CSP (see **Fabius Materia** → fonts). Match line-height generously; Hebrew/Arabic ascenders/marks want air.

## Framework realities

- **Plain HTML/CSS:** logical properties + root `dir` is the whole game; near-zero JS.
- **Tailwind:** use the logical utilities — `ms-*`/`me-*` (margin-inline), `ps-*`/`pe-*` (padding-inline), `start-*`/`end-*` (inset-inline), `text-start`/`text-end` — and the `rtl:` / `ltr:` variants for the exceptions (`rtl:-translate-x-4`, `rtl:[box-shadow:...]`). Set `dir` on `<html>`; Tailwind v3+ reads it. Avoid `ml-*`/`pl-*`/`left-*` in RTL-capable code.
- **React / Vue / Svelte:** `dir` is a normal attribute — set it on the root and let it cascade; no per-component prop needed. Watch portals/modals rendered at `document.body` — they inherit the body's `dir`, which is what you want if the root is set.
- **Retrofitting code you don't control** (a third-party LTR stylesheet, a design-system build): `rtlcss` (PostCSS), `postcss-rtlcss` (emits both directions under `[dir]` selectors — no runtime swap needed), or `stylis-plugin-rtl` for CSS-in-JS (Emotion/styled-components/MUI). These *flip physical properties*; they can't fix hardcoded content or wrong icons. Treat them as a bridge, not the design.

## The RTL ship checklist — the failure modes to kill

Before calling an RTL surface done (these are exactly where an LLM-generated or ported UI breaks):

- [ ] `dir` set on the **root** (`<html>`), and `lang` set to the real language.
- [ ] **No** `margin-left/right`, `padding-left/right`, `left/right`, `text-align:left/right` in components — logical properties only.
- [ ] Flex/grid rows are **not** hand-reversed (`row-reverse`); they mirror from `dir`.
- [ ] Every opposite-direction / user-supplied run (names, phones, prices, URLs, code, `@handles`) is **isolated** (`<bdi>` or `Intl` marks) — the "mixed English/number in RTL" bug is gone.
- [ ] Directional icons mirror; clocks/checkmarks/media/logos do **not**.
- [ ] Shadows, `translateX`, gradient/background directions flipped under `[dir="rtl"]`.
- [ ] A font that actually **renders the script** is loaded and verified for glyph coverage (test on WebKit/iOS, not only Chrome).
- [ ] Numbers/dates/currency via `Intl` with the real locale; numerals read LTR and don't invert.
- [ ] Verified **live** with real RTL content (not lorem-ipsum, not one Hebrew word) — mixed sentences, long paragraphs, forms, tables — in a browser (`fabius-disciplina`'s prove rule).

## Pairs with

`fabius-decor` (the visual laws — direction is one of them), **Fabius Iconarium** (RTL-aware icon sets), **Fabius Materia** (script-covering open fonts), `fabius-mercatus` (RTL copy reads differently — the message is theirs; the direction is here), and `fabius-parcus` (logical-first is also the *smallest* CSS — one stylesheet, both directions).

For the **Israeli market** specifically — the accessibility *law* (IS 5568 / ת"י 5568), anti-spam (Chok HaSpam), privacy (Amendment 13), and Israeli data formats (ת"ז, VAT, ₪, phone) that sit *on top* of RTL mechanics → **Fabius Yisrael** (`references/israel-localization.md`).
