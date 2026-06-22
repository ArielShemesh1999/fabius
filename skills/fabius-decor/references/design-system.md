# Fabius Decor — token vocabulary & brand references

Loaded on demand by `fabius-decor`. The skill has the laws; this file has the concrete vocabulary and three worked brand reference points distilled from 69 real-brand teardowns.

## The token contract

Define these once per project (CSS custom properties, a tokens file, or a theme object). Components reference tokens — never inline hex/px.

```
color/
  primary            one interactive accent (the ONLY "click me" color)
  primary-focus      slightly brighter sibling, focus rings only
  ink                near-black for text (#1d1d1f, not #000)
  body-muted         secondary text
  canvas             white background
  canvas-alt         one off-white for section rhythm (#f5f5f7)
  hairline           1px border tone (#e0e0e0)
  on-primary         text on the accent
type/
  display-xl/lg/md   600 weight, negative tracking (-0.02 to -0.04em)
  body               400, 16–17px, line-height ~1.5
  caption            14px
  weights            300 / 400 / 600 / 700  (skip 500 unless the brand uses it)
space/  4 8 12 16 24 32 48 80           (base 8; section padding 64–80)
radius/ none 8 12 18 pill(9999)         (one grammar per element type)
shadow/ none + ONE product/elevation shadow at most
```

## Three reference points (lift principles, not pixels)

**Apple — photography-first, near-invisible chrome.**
One accent `#0066cc`. Ink `#1d1d1f` (never pure black). Canvas white + parchment `#f5f5f7`, the color change IS the section divider. SF Pro / Inter, display 600 with negative tracking, body **17px**. Weight ladder 300/400/600/700, 500 absent. Exactly ONE drop-shadow in the whole system, reserved for product imagery. Radius: `sm 8` utility, `lg 18` cards, `pill` CTAs. Press state `scale(0.95)`. Lesson: restraint reads as premium.

**Stripe / Linear-class SaaS — dense, crisp, gradient-accent.**
A tight, slightly-tighter type scale; generous but efficient spacing; a single saturated accent over near-neutral grays; subtle elevation on cards; motion is fast and small. Lesson: hierarchy from type weight + spacing, not borders everywhere.

**Revolut / fintech — confident color blocks, big numbers.**
Bold accent fields, large display numerals, high-contrast cards, rounded geometry. Lesson: when the product is a number, make the number the hero; everything else recedes.

## Substituting fonts honestly

System/proprietary fonts won't load off-platform. Name the closest open-source match and tune:
- SF Pro → **Inter** (weight 600, `font-feature-settings:"ss03"`, nudge `letter-spacing:-0.01em` on display, tighten body line-height ~0.03).
- Helvetica/Neue → Inter or Arimo. Circular/Gilroy → Manrope. Söhne → Inter. Serif editorial → Charter / Source Serif.

## The full set

For deeper per-brand detail (color, type, spacing, components, do/don'ts, responsive), reference a full brand teardown, pick the closest as a target, lift its discipline, and re-map to the project's identity.
