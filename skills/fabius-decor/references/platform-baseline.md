# Fabius Decor — the platform floor

Loaded on demand by `fabius-decor`. The skill states the laws; this file names the mechanism that carries each one *now*. One rule underneath all of it: **if the browser ships the behavior, hand-rolling it is a defect, not craft.** A JS class toggle mirroring DOM state, a fixed card height to fake alignment, a `<br>` to fix a headline, a `position:fixed` div pretending to be a modal — same mistake, four costumes.

*(Baseline status as of 2026-08 — re-check before a sealed build. **Widely available** = no fallback branch needed; **newly available** = ship it, keep the degradation graceful; **limited** = progressive enhancement only.)*

## The mechanism map

| Law it serves | Mechanism | Baseline | Verdict |
|---|---|---|---|
| Mobile-first / responsive | `container-type: inline-size` + `@container` | **widely** (interop Feb 2023 · widely 2025-08-14) | The component-level unit. Viewport breakpoints are a *page* tool. |
| Design the states | `:has()` | **widely** (2026-06-19) | Style a parent from its children's real state — before any JS toggle. |
| Consistency / alignment | `grid-template-rows: subgrid` | **widely** (2026-03-15) | Cards in a row share one grid, never a fixed height. |
| Type / hierarchy | `text-wrap: balance` | **newly** (2024-05-13) | Set the raggedness on headings; never a `<br>`. |
| Type / hierarchy | `text-wrap: pretty` | **limited** (Chromium and Safari 26+; not Firefox) | Free upgrade on body copy; degrades to `auto`. |
| Tokens / dark mode | `color-scheme` + `light-dark()` | **widely** (2024-08-03) + **newly** (2024-05-13) | One token, both themes → `design-tokens.md`. |
| Tokens / derived color | `contrast-color()` · `color-mix()` | **newly** (2026-04-10) · **widely** (2025-11-09) | Derive the siblings off the one accent → `design-tokens.md`. |
| Overlays | `<dialog>` · `popover` attribute | **widely** (2024-09-14) · **newly** (2025-01-27) | Pick the element before animating it → `motion-libraries.md`. |
| Overlay placement | `anchor-name` / `position-area` / `@position-try` | not yet widely — Chrome 125+, Safari 26+ (incl. iOS), Firefox 147+ (`position-anchor` 151) | Cross-engine but young: enhancement over a positioned fallback. |

## Size off the container, not the viewport

A breakpoint knows the window; it does not know that *this* card is in a sidebar. That is the exact failure container queries were shipped to fix, and it is the failure a viewport-only strategy keeps producing.

- Any component that appears in **more than one slot** gets `container-type: inline-size` on its wrapper and `@container (width >= 30rem)` for its own layout switch. The same card then reads right in a sidebar, a modal and a full-bleed grid with no new breakpoint.
- Keep the viewport ladder (~640 · ~834 · ~1068 · ~1440) for the **page shell** and section rhythm only — that is what it is good at.
- Query units (`cqi`, `cqw`) let type and spacing scale off the container too — one clamp, no per-slot override.
- `container-type: inline-size` makes the element a containment context: it can no longer be sized by its own children in the inline axis. Put it on the wrapper, not on the thing you are styling.

Container queries are Widely available. A viewport-only responsive strategy is now a choice you justify, not a default.

## Set the raggedness

The one-word last line is the loudest amateur tell on a hero, and the `<br>` that "fixes" it breaks on the next copy edit or the next locale.

- `text-wrap: balance` on **headings, blockquotes, card titles, pull quotes** — evens the line lengths. The engines cap it (six lines or fewer in Chromium, ten or fewer in Firefox) because balancing is expensive, so it self-limits to exactly the short blocks you want it on.
- `text-wrap: pretty` on **body copy** — a slower line-breaker that suppresses orphans. Chromium and Safari 26+, not Firefox: a free upgrade that falls back to `auto`, never a load-bearing rule.
- Never fake either with `<br>`, a non-breaking space, or a hand-tuned `max-width` on a headline. Those are frozen guesses about one string in one language.

## State comes from the DOM

- `:has()` styles a parent from its children's real state: `.field:has(:invalid)`, `.card:has(img)`, `label:has(input:checked)`, `nav:has([popover]:popover-open)`. A JS class toggle re-encodes state the DOM already carries, so it can desync; `:has()` cannot.
- Cost is real on huge, deeply-invalidating selectors — scope it (`.card:has(> img)`), don't hang it off `body`.
- Rows of cards line up with **subgrid**: give the row one grid and let each card inherit it with `grid-template-rows: subgrid` spanning its own tracks. Title, body and CTA then align across the row whatever the copy length — a fixed height only *looks* aligned until the copy changes.
- Both are Widely available. No `@supports` branch, no fallback path to maintain.

## The contrast and focus gate — WCAG 2.2 Level AA

Body text at 4.5:1 is one third of the contrast job, and this layer's own aesthetic — hairline borders, muted chart series, icon-only controls, sticky blurred headers — walks straight into the other two.

- **1.4.11 Non-text Contrast (AA) — 3:1.** Applies to whatever *identifies* a UI component or its state (focus ring, input border, toggle on/off, the glyph in an icon-only button) and to any graphical object needed to understand the content — every chart series, meaningful hairline, status dot. A 1px `#e6e6e6` hairline that carries meaning fails; a decorative one does not.
- **2.4.11 Focus Not Obscured, Minimum (AA).** A focused component must not be *entirely* hidden by author content. Sticky headers, cookie bars and bottom-docked toolbars are the usual culprits. Fix it with `scroll-margin-block-start` equal to the sticky height (and `scroll-padding` on the scroll container), not with a bigger focus ring.
- **2.5.8 Target Size, Minimum (AA) — 24×24 CSS px**, or undersized targets spaced so 24px circles don't intersect. The 44×44 rule in the skill is the *design* floor (2.5.5 is AAA); 24×24 is the legal one — clear both.
- **2.5.7 Dragging Movements (AA)** — every drag interaction needs a single-pointer alternative (a click target, a menu). Reorderable lists and sliders fail this by default.
- **3.3.8 Accessible Authentication, Minimum (AA)** — no cognitive-function test (transcription, puzzle) with no alternative; do not block paste into an OTP or password field.
- WCAG 2.2 **removed 4.1.1 Parsing**. It is obsolete — don't carry it forward from an old audit template as a finding.

Both contrast criteria are checkable in CI on rendered pixels; the focus one needs a keyboard pass at the real sticky offset.

## Where the rest lives

Dark-mode and derived-color tokens → `references/design-tokens.md`. Overlay elements and the animation ladder → `references/motion-libraries.md`. Logical properties, `dir` and isolation → `references/rtl-bidi.md`. The Israeli legal floor on top of WCAG → `references/israel-localization.md`.
