---
name: fabius-decor
description: >
  fabius's ship-grade design layer — gives the agent a token vocabulary, the universal laws that
  separate amateur UI from shipped UI, and a quality checklist. Use when building or reviewing any
  UI — a landing page, a component, a screen, an email, a slide, a brand surface — when the user
  references a brand look, or asks to make something "look good", "more polished", or "production
  quality". The token contract lives in references/design-tokens.md; the full 69-brand teardown
  library (DESIGN-apple.md, DESIGN-stripe.md, DESIGN-linear.app.md …) plus the fabius-design,
  GSAP-animation, fabius-frames and fabius-uiux bundles live in references/design/.
---

# Fabius Decor — what good actually looks like

*Decor* — what is fitting, what becomes the thing. Good design is fitness to purpose, not decoration. Across dozens of teardowns of shipped brands, the same short list of laws holds. Amateur UI breaks them; shipped UI obeys them. Pick one brand as a concrete target from the 69-brand library in `references/design/` (one `DESIGN-<brand>.md` each), then enforce the laws below.

## Define the tokens before you style anything

Never inline a raw hex or px. Name a token once, reference it everywhere:

- **Color** — `primary` (the ONE interactive accent — usually exactly one), `ink`/`body` (near-black, not `#000` — e.g. `#1d1d1f`, which reads photographic), `canvas`/`surface` (white plus one off-white for rhythm), `muted` (secondary text), `hairline` (1px borders).
- **Type scale** — a fixed ladder of sizes and weights (e.g. 300/400/600/700; skip 500 if the brand does). Display sizes carry **negative letter-spacing** for the tight modern feel; body runs 16–17px with generous line-height (~1.5).
- **Spacing** — one base unit (8px); every structural step snaps to it (8 / 12 / 16 / 24 / 32 / 48 / 80). Section padding runs large (64–80px).
- **Radius** — a small fixed set (e.g. sm / md / lg / pill). One grammar per element type; don't mix radii at random.
- **Elevation** — minimal. Many top brands use almost no shadow; depth comes from a surface-color change and backdrop-blur, not drop-shadows scattered everywhere.

## The laws — break these and it reads amateur

1. **One accent color.** Every "click me" is the same `primary`. A second brand accent fragments the eye. Add a color only when it has a job.
2. **Tokens, never inline values.** Change a token once and the whole surface follows. Inline hex is where drift begins.
3. **Type carries the hierarchy, not boxes.** Size + weight + spacing set the rank. Reach for a border or a background only after type has failed.
4. **Whitespace is a feature.** Crowded reads as cheap. Give headlines air (≥48–64px), keep content off the edges, let the primary thing breathe.
5. **Rhythm by alternation.** Alternate white / off-white (or light / dark) sections — the color change *is* the divider, no extra chrome required.
6. **Restraint in motion.** One micro-interaction language (e.g. `scale(0.97)` on press). Calm — no looping pulse or heartbeat. Animate transform and opacity, never layout.
7. **Consistency over novelty.** One spacing rhythm, one radius grammar, one type ladder across every screen — the same language at different volumes.
8. **Design the states.** Default, hover, focus, active, disabled — don't leave them to the browser. A focus ring is accessibility, not decoration.

## Mobile-first, always

Design and verify the **mobile** layout first — it's the hardest constraint. Desktop tends to fall out right once mobile is right; the reverse fails. Breakpoints that actually matter: ~640 (phone), ~834 (tablet), ~1068 (small desktop), ~1440 (content lock). Touch targets ≥ 44×44px.

## Using a brand spec as a target

1. Pick the closest brand in `references/design/` (69 systems — `DESIGN-apple.md`, `DESIGN-stripe.md`, `DESIGN-linear.app.md` …) as the visual DNA; the token contract is in `references/design-tokens.md`.
2. Lift its **principles**, not its pixels — the type ratios, the accent discipline, the spacing rhythm, the do/don'ts.
3. Re-map to the project's own brand color and font. Keep the structure, swap the identity.
4. Substitute fonts honestly: name the closest open-source match (Inter for SF Pro, Manrope for Gilroy) and nudge tracking and leading to match.

## Ship-quality checklist

Before calling UI done:

- [ ] One accent; every interactive element uses it.
- [ ] All values are tokens — no inline hex or px in components.
- [ ] Type ladder consistent; display sizes have tight tracking; body ≥16px.
- [ ] Spacing snaps to the base unit everywhere.
- [ ] Mobile layout designed first and actually checked at ~375px.
- [ ] Focus-visible states present; body-text contrast ≥ 4.5:1.
- [ ] Motion calm, one language, transform/opacity only.
- [ ] Verified **live** in a browser, not just read in the code (`fabius-disciplina`'s prove rule).

When a design is declared final, accessibility work is **ARIA-attribute-only** — don't swap tags (div→table, h4→fieldset), which pulls in UA default styles and breaks the design even with no CSS change.

Pairs with: `fabius-disciplina` (brainstorm the layout, prove it live), `fabius-parcus` (the smallest CSS that holds the look).
