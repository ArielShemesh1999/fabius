# Fabius Decor — token vocabulary & brand references

Loaded on demand by `fabius-decor`. The skill has the laws; this file has the concrete vocabulary and three worked brand reference points distilled from 69 real-brand teardowns.

## The token contract

Define these once per project (CSS custom properties, a tokens file, or a theme object). Components reference tokens — never inline hex/px.

```
color/
  primary            one interactive accent (the ONLY "click me" color)
  primary-strong     higher-contrast sibling, focus rings only  · DERIVED from primary
  ink                near-black for text (#1d1d1f, not #000)
  muted              secondary text                             · DERIVED from ink
  canvas             the page background
  canvas-alt         one off-white for section rhythm (#f5f5f7)
  hairline           1px border tone (#e6e6e6)                  · DERIVED from ink
  on-primary         text on the accent                         · DERIVED from primary
type/
  display-xl/lg/md   600 weight, negative tracking (-0.02 to -0.04em)
  body               400, 16–17px, line-height ~1.5
  caption            14px
  weights            300 / 400 / 600 / 700  (skip 500 unless the brand uses it)
  wrap               text-wrap: balance on display/headings — set the ragging, never a <br>
space/  4 8 12 16 24 32 48 80           (base 8; section padding 64–80)
radius/ none 8 12 18 pill(9999)         (one grammar per element type)
shadow/ none + ONE product/elevation shadow at most
```

The values above are the *light* reading of the contract, not a light-only system. Both themes ship from **one** declaration each — `color-scheme: light dark` on `:root` (widely available) plus `light-dark(<light>, <dark>)` per token (Baseline *newly*, so keep the literal value on the line above it) — and `on-primary` / `primary-strong` / `muted` / `hairline` are **derived** from `primary` and `ink` with `contrast-color()` and `color-mix()`, never hand-picked. Mechanism, fallbacks and the dark-palette caveats → `references/design-tokens.md`, which is the canonical contract: where this summary and that file differ, that file wins.

## Three reference points (lift principles, not pixels)

**Apple — photography-first, near-invisible chrome.**
One accent `#0066cc`. Ink `#1d1d1f` (never pure black). Canvas white + parchment `#f5f5f7`, the color change IS the section divider. SF Pro / Inter, display 600 with negative tracking, body **17px**. Weight ladder 300/400/600/700, 500 absent. Exactly ONE drop-shadow in the whole system, reserved for product imagery. Radius: `sm 8` utility, `lg 18` cards, `pill` CTAs. Press state `scale(0.98)` (the teardown's own `components.html`). Lesson: restraint reads as premium.

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

## The material & direction references (page in on demand)

Alongside the token contract, these sourced, license-verified libraries carry the parts a brand target doesn't:

- **Fabius Iconarium** — the icon-system map (line/solid/duotone systems, animated icons, brand marks, emoji, flags), one-family/one-stroke law, token + a11y integration → `references/icons.md`.
- **Fabius Motus** — the motion-library map over the fabius-motion/fabius-frames bundles: the native-first ladder, JS engines, and easing-token recipes → `references/motion-libraries.md`.
- **Fabius Materia** — design raw materials: illustrations, 3D, textures/gradients/shadows/glass, self-hosted fonts, color tooling, and the HuggingFace generative-imagery pipeline → `references/design-assets.md`.
- **Fabius Bidi** — right-to-left & bidirectional layout (Hebrew · Arabic · Persian · Urdu …): logical-first CSS, bidi isolation, icon mirroring, `Intl` numerals, per-script fonts → `references/rtl-bidi.md`.
- **Fabius Yisrael** — the Israeli-market layer on top of Bidi: accessibility *law* (IS 5568), anti-spam (Chok HaSpam), privacy (Amendment 13), Israeli formats (ת"ז · VAT · ₪ · phone) and Hebrew i18n (one/two/other plurals, doc-bidi) → `references/israel-localization.md`.
- **The platform floor** — which browser mechanism carries each law now (container queries, `:has()`, subgrid, `text-wrap`, `light-dark()`, `<dialog>`/`popover`) and the WCAG 2.2 AA contrast/focus gate → `references/platform-baseline.md`.
