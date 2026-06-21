# Fabius Decor — token vocabulary & brand reference points

Loaded on demand by `fabius-decor`. The skill has the laws; this file has the concrete token contract and four worked brand reference points to aim at. Lift the *principle*, never the pixels.

## The token contract

Define these once per project — CSS custom properties, a tokens file, or a theme object. Components reference tokens; they never inline a hex or a px.

```
color/
  primary           the one interactive accent (the only "click me" color)
  primary-strong    a slightly brighter sibling — focus rings only
  ink               near-black for text (#1d1d1f, not #000)
  muted             secondary text
  canvas            the white background
  canvas-alt        one off-white for section rhythm (#f5f5f7)
  hairline          1px border tone (#e6e6e6)
  on-primary        text that sits on the accent
type/
  display-xl / lg / md   600 weight, negative tracking (-0.02 to -0.04em)
  body                   400, 16–17px, line-height ~1.5
  caption                14px
  weights                300 / 400 / 600 / 700  (skip 500 unless the brand uses it)
space/   4  8  12  16  24  32  48  80          (base 8; section padding 64–80)
radius/  none  8  12  18  pill(9999)            (one grammar per element type)
shadow/  none  +  at most ONE elevation shadow, reserved for product/imagery
motion/  press scale(0.97)  ·  ease ~180ms  ·  transform & opacity only
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
