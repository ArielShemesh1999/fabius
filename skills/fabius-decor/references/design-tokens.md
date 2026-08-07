# Fabius Decor — token vocabulary & brand reference points

Loaded on demand by `fabius-decor`. The skill has the laws; this file has the concrete token contract and four worked brand reference points to aim at. Lift the *principle*, never the pixels.

## The token contract

Define these once per project — CSS custom properties, a tokens file, or a theme object. Components reference tokens; they never inline a hex or a px.

```
color/
  primary           the one interactive accent (the only "click me" color)
  primary-strong    higher-contrast sibling — focus rings only   · DERIVED from primary
  ink               near-black for text (#1d1d1f, not #000)
  muted             secondary text                               · DERIVED from ink
  canvas            the page background
  canvas-alt        one off-white for section rhythm (#f5f5f7)
  hairline          1px border tone (#e6e6e6)                    · DERIVED from ink
  on-primary        text that sits on the accent                 · DERIVED from primary
type/
  display-xl / lg / md   600 weight, negative tracking (-0.02 to -0.04em)
  body                   400, 16–17px, line-height ~1.5
  caption                14px
  weights                300 / 400 / 600 / 700  (skip 500 unless the brand uses it)
  wrap                   text-wrap: balance on display/headings · pretty on body (upgrade only)
space/   4  8  12  16  24  32  48  80          (base 8; section padding 64–80)
radius/  none  8  12  18  pill(9999)            (one grammar per element type)
shadow/  none  +  at most ONE elevation shadow, reserved for product/imagery
motion/  press scale(0.97)  ·  ease ~180ms  ·  transform & opacity only
```

## Dark mode is a token concern, not a second stylesheet

Two declarations carry both themes. A duplicated palette inside a `prefers-color-scheme` block is drift waiting to happen — the day someone re-maps the accent, one copy moves and the other doesn't.

1. **`color-scheme: light dark` on `:root`.** The browser then repaints form controls, scrollbars, the default canvas and the UA text color for you — the chrome you don't own. Baseline **widely available**: declare it unconditionally, no fallback branch.
2. **Author each color token *once* as `light-dark(<light>, <dark>)`.** One line per token, both themes, no second block to keep in sync. The function reads the *used* `color-scheme`, so it does nothing useful unless step 1 declared one. It is Baseline **newly** available (May 2024) — cross-engine already, but the 30-month clock to *widely* available only runs out in November 2026, so precede each token with its literal light value. The pair is not a duplicated palette; it's the cascade doing the feature detection.

```css
:root {
  color-scheme: light dark;

  --canvas: #ffffff;                          /* the literal is the fallback …        */
  --canvas: light-dark(#ffffff, #0b0b0c);     /* … the function wins where it parses  */

  --ink:       light-dark(#1d1d1f, #f2f2f4);  /* pair every color token the same way  */
  --canvas-alt:light-dark(#f5f5f7, #151517);
  --hairline:  light-dark(#e6e6e6, #2a2a2d);
}
[data-theme="dark"]  { color-scheme: dark; }   /* an explicit user choice */
[data-theme="light"] { color-scheme: light; }  /* both directions, or the toggle only works once */
```

Pair *every* color token, not just the ones you remember: an unparsed `light-dark()` in a custom property doesn't degrade to a sensible color, it drops out at computed-value time and takes the declaration that used it with it.

An explicit `[data-theme]` toggle stays possible: re-declare `color-scheme` on that scope and every `light-dark()` token follows. Do not pair it with a hand-maintained dark palette — pick one mechanism.

`light-dark()` resolves **colors**, and only colors. A logo, an illustration, a texture or a mask still needs a real swap — keep those on `prefers-color-scheme` or on the `[data-theme]` rule, and prefer an SVG driven by `currentColor` so there is nothing to swap.

Dark is not the light palette inverted: raise `ink` off pure white, drop `canvas` off pure black (`#0b0b0c`, not `#000`), and re-check the accent — a color that clears contrast on white often fails on near-black. Elevation flips too: in dark UI depth comes from a *lighter* surface, not a heavier shadow.

## Derive the siblings, don't pick them

`primary-strong`, `on-primary`, the muted tones and the hairlines are *functions of* the accent and the ink — hand-picked values silently break the moment the accent is re-mapped to a project's brand, which is the exact re-map this file mandates. Hand-picking stays legitimate where the brand's real behavior contradicts the formula — Apple's blue button *lightens* on hover (`#0071e3` → `#0077ed` in `references/design/fabius-design/design-systems/apple/tokens.css`), so a mix toward black would fight the brand. Then say so in the token file, so the next reader knows it is a decision and not a leftover.

```css
--on-primary:     contrast-color(var(--primary));                 /* black or white, whichever wins */
--primary-strong: light-dark(color-mix(in oklab, var(--primary), black 12%),
                             color-mix(in oklab, var(--primary), white 14%));
--muted:          color-mix(in oklab, var(--ink), var(--canvas) 45%);
--hairline:       color-mix(in oklab, var(--ink), var(--canvas) 88%);
```

- `color-mix()` is Widely available — mix **in `oklab`/`oklch`**, not sRGB, or the midpoints go muddy and the lightness steps stop being even.
- Mix the focus sibling **away from the canvas**, not toward white by reflex. On a white page a lighter accent has *less* contrast against it, and a focus indicator owes 3:1 to what sits next to it (WCAG 1.4.11) — so mix toward black (or raise chroma) on a light canvas and toward white on a dark one. That is why the token is the *stronger* sibling, not the brighter one.
- `contrast-color()` is Baseline **newly** available as of April 2026 (Chrome/Edge 147, Firefox 146, Safari 26) — its widely-available bar is 30 months out, so the `@supports` pair below is the ship path for years, not a nicety. It returns whichever of black/white contrasts *better* against the accent — it maximizes, it does not promise 4.5:1. A mid-tone accent (royal blue, mid green) can win that vote and still read badly, so keep the measured check; if neither black nor white clears, change the accent, not the text.
- Ship it with a literal fallback so an older engine gets a chosen value, not an invalid declaration:

```css
--on-primary: #fff;
@supports (color: contrast-color(red)) { --on-primary: contrast-color(var(--primary)); }
```

## Four reference points (aim at the principle)

**Apple — photography-first, near-invisible chrome.**
One accent (`#0066cc`). Ink `#1d1d1f`, never pure black. Canvas white plus parchment `#f5f5f7`, where the color change itself *is* the section divider. SF Pro / Inter, display 600 with negative tracking, body **17px**. Weight ladder 300/400/600/700, no 500. Exactly one drop-shadow in the whole system, kept for product imagery. Radius `8` for utility, `18` for cards, `pill` for CTAs. Press `scale(0.97)`. **Lesson: restraint reads as premium.**

**Stripe / Linear-class SaaS — dense, crisp, one saturated accent.**
A tight, slightly compressed type scale; spacing that's generous but efficient; a single saturated accent over near-neutral grays; subtle elevation on cards only; motion fast and small. **Lesson: hierarchy comes from type weight and spacing, not borders everywhere.**

**Revolut / fintech — confident color blocks, big numbers.**
Bold accent fields, oversized display numerals, high-contrast cards, rounded geometry. **Lesson: when the product *is* a number, make the number the hero and let everything else recede.**

**Editorial / news — type as the entire system.**
A serif display paired with a clean sans for body, a strict baseline grid, almost no color beyond ink and one link accent, rules and whitespace doing all the structuring. **Lesson: with a real type scale and a grid, you need almost no other UI.**

## Substituting fonts honestly

System and proprietary fonts won't load off-platform. Name the closest open-source match and tune it:

- **SF Pro → Inter** (weight 600, `font-feature-settings:"ss03"`, nudge `letter-spacing:-0.01em` on display, tighten body line-height ~0.03).
- **Helvetica / Neue → Inter** or Arimo.
- **Circular / Gilroy → Manrope.**
- **Söhne → Inter.**
- **Serif editorial → Charter** or Source Serif.

Don't claim the brand font is present when it isn't — name the substitute and match its metrics.

## Going deeper

For a specific brand, study its live surface directly — color, type ramp, spacing rhythm, component shapes, the do's and don'ts — pick the closest reference point above as your structural target, lift its discipline, and re-map everything to the project's own identity. The laws in the skill are the invariant; the brand is the costume.
