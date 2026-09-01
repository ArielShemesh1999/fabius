---
name: fabius-decor
description: >
  fabius's ship-grade design layer — gives the agent a token vocabulary, the universal laws that
  separate amateur UI from shipped UI, and a quality checklist. Use when building or reviewing any
  UI — a landing page (visual execution; the message and copy are fabius-mercatus), a component, a
  screen, an email, a slide, a brand surface, a chart, a diagram, a data visualization — when the
  user references a brand look, or asks to make something "look good", "more polished",
  "production quality", "chart this", "graph this", or "visualize this data". Also covers
  generating images (for image models) and explanatory diagrams that teach a system: "generate an
  image", "diagram this", "explain this codebase visually". Also owns responsive/mobile-first
  layout and a finished design's accessibility — focus states, contrast, ARIA-only — plus icon
  choice, motion libraries, design assets (illustrations · 3D · textures · fonts · color ·
  HuggingFace) and right-to-left / bidirectional layout (RTL, Hebrew/Arabic).
when_to_use: >
  "make it beautiful", "it looks amateur", "match the brand", "make it responsive", "fix the
  focus states", spacing/typography/color calls, dashboards, hero sections, dark mode, mobile
  breakpoints, contrast checks, "critique this UI", "audit the design", "does this look
  AI-generated", "polish it before ship".
license: UNLICENSED
metadata:
  author: shear559
---
<!-- © 2026 shear559 · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->

# Fabius Decor — what good actually looks like

*Decor* — what is fitting, what becomes the thing. Good design is fitness to purpose, not decoration. Across dozens of teardowns of shipped brands, the same short list of laws holds. Amateur UI breaks them; shipped UI obeys them. Pick one brand as a concrete target from the 69-brand library in `references/design/` (one `DESIGN-<brand>.md` each), then enforce the laws below.

## Define the tokens before you style anything

Never inline a raw hex or px. Name a token once, reference it everywhere:

- **Color** — `primary` (the ONE interactive accent — usually exactly one), `ink`/`body` (near-black, not `#000` — e.g. `#1d1d1f`, which reads photographic), `canvas`/`surface` (white plus one off-white for rhythm), `muted` (secondary text), `hairline` (1px borders).
- **Type scale** — a fixed ladder of sizes and weights (e.g. 300/400/600/700; skip 500 if the brand does). Display sizes carry **negative letter-spacing** for the tight modern feel; body runs 16–17px with generous line-height (~1.5). Set the ragging too — `text-wrap: balance` on headings, never a `<br>`.
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
7. **Consistency over novelty.** One spacing rhythm, one radius grammar, one type ladder across every screen — the same language at different volumes. A card row aligns with `subgrid`, not a fixed height.
8. **Design the states.** Default, hover, focus, active, disabled — don't leave them to the browser. A focus ring is accessibility, not decoration. Style state from the DOM with `:has()` before a JS class toggle.

## Mobile-first, always

Design and verify the **mobile** layout first — it's the hardest constraint. Desktop tends to fall out right once mobile is right; the reverse fails. Breakpoints that actually matter: ~640 (phone), ~834 (tablet), ~1068 (small desktop), ~1440 (content lock). Touch targets ≥ 44×44px. But breakpoints are a *page* tool — a component landing in more than one slot sizes off its **container** (`container-type: inline-size` + `@container`), not the viewport. The platform floor these laws assume — container queries, `:has()`, subgrid, `text-wrap`, the WCAG 2.2 AA contrast/focus gate → `references/platform-baseline.md`.

## Icons · motion · materials · direction

License-verified libraries for what a brand target doesn't — page in the one you need:

- **Icons** — one family, one stroke, `currentColor`→token, static by default; systems, animated icons, brand marks, emoji, flags → `references/icons.md`.
- **Motion** — climb the native ladder (`@starting-style` · View Transitions · scroll-driven · WAAPI) before a JS engine; reduced-motion default-on → `references/motion-libraries.md`.
- **Materials** — illustration, 3D, texture, gradient, fonts, color tooling, HuggingFace pipeline; recolor to accent, license-honest → `references/design-assets.md`.
- **Right-to-left / bidirectional** (Hebrew · Arabic · Persian · Urdu) — author *logical* not physical, `dir` on root, isolate every LTR run (`<bdi>`), mirror directional icons only → `references/rtl-bidi.md`.

## Visualize data — charts, graphs, diagrams

A chart is a design artifact, not a different discipline — the same tokens and the same restraint apply, plus one rule above all: **maximize the data-ink, delete the rest.**

1. **Chart fits the question.** Trend → line; comparison → bar; part-of-whole → stacked/100% bar (rarely a pie, never >5 slices); correlation → scatter; distribution → histogram/box. Pick by the question, not by what looks busy.
2. **One accent carries the signal.** The series that matters gets `primary`; everything else is `muted`/`hairline`. Color encodes meaning, never decoration (and stays colorblind-safe — don't lean on red/green alone).
3. **Strip the chart-junk.** No gridline thicket, no 3-D, no drop-shadows, no redundant legend when you can label the line directly. Axes start at zero for bars; annotate the one number the reader should leave with.
4. **Label directly, title with the takeaway.** The title states the finding ("Signups doubled after launch"), not the dimensions ("Signups by month").
5. **Reproducible, tokenized SVG.** Prefer generated SVG from data over a screenshot — versionable, themeable, crisp. The repo's `assets/charts/` (`svgplot.py` · `render_figures.py`) is the numpy→SVG path; figures re-render from source, never hand-edited.

Figura depth (chart table, data-ink, color, SVG helpers) → `references/visualization.md`. Decks and reports → `references/decks-and-infographics.md`; diagram-as-code pairs with `fabius-disciplina`.

## Explanatory diagrams — teach the system, don't just draw it

A diagram that *explains* (a codebase, a domain, a flow) is pedagogy, not drawing — three moves: **extract deterministically, then add meaning** (a parser yields the reproducible facts; the model adds only semantic judgment); **make the artifact a typed graph** (a small fixed node/edge vocabulary, stable ids, weighted edges); **order by topology, teach by narrative** (fan-in ranks importance, the entry point opens the tour, BFS depth sets step order).

Full method → `references/explanatory-diagrams.md`.

## Generative imagery — prompt the image, don't wish for it

An image prompt is a **structured slot fill** under the same restraint, not a freeform sentence:

1. **Slots, not a sentence.** Ordered: subject → detail → styling → expression → **lighting** → scene → technical/quality. Required slots get an intelligent default; optional ones stay empty, never padded.
2. **Lighting is mandatory.** The highest-leverage lever and the widest amateur-vs-pro gap — always name a style (cinematic · neon · natural). Never omit it.
3. **Cascade from one signal.** Era/setting sets makeup *and* hair *and* wardrobe together — derive coupled attributes, don't ask for each.
4. **Conflict pass before emitting.** Cultural, temporal, biological, stylistic — explain the clash, show the correction, let the user override. *Style* ≠ *identity*: "anime" is a render technique, not an ethnicity.
5. **Library + free-text.** Curated recipes (lighting, camera/lens, palettes) + the open-set content only the model supplies; end on a completeness check.

Slot schema, lighting/era tables, conflict rules, palette recipe → `references/generative-imagery.md`.

## Using a brand spec as a target

1. Pick the closest brand in `references/design/` (69 systems — `DESIGN-apple.md`, `DESIGN-stripe.md` …) as the visual DNA; token contract → `references/design-tokens.md`; the entry doc CORPUS.md designates (vocabulary + three worked brands) → `references/design-system.md`. Bundled libraries there are reference corpora, not public skills.
2. Lift its **principles**, not its pixels — the type ratios, the accent discipline, the spacing rhythm, the do/don'ts.
3. Re-map to the project's own brand color and font. Keep the structure, swap the identity.
4. Substitute fonts honestly: name the closest open-source match (Inter for SF Pro, Manrope for Gilroy) and nudge tracking and leading to match.

## Review before ship — the censor's floor

Review is a vocabulary, not a vibe. Name the surface mode (persuade · operate · read · experience), pick the verb (critique · audit · polish · bolder · quieter · distill · harden · clarify · adapt), run the **deterministic anti-pattern scan first** — the ~60 generated-UI tells (gray on color, nested cards, icon tiles, gradient text, bounce easing …) — then judge: heuristics /40, P0–P3, personas. **Bounded passes:** build fully → one batched desktop + mobile inspection → one fix batch → at most one more round → stop. Refinement preserves, redesign replaces, the brief wins → `references/design-critique.md`.

## Ship-quality checklist

Before calling UI done:

- [ ] One accent; every interactive element uses it.
- [ ] All values are tokens — no inline hex or px in components.
- [ ] Type ladder consistent; display sizes have tight tracking; body ≥16px.
- [ ] Spacing snaps to the base unit everywhere.
- [ ] Mobile layout designed first and actually checked at ~375px.
- [ ] Focus-visible, never obscured; **≥ 4.5:1** body text, **≥ 3:1** UI parts, icons, chart series (WCAG 2.2 AA).
- [ ] Motion calm, one language, transform/opacity only.
- [ ] Verified **live** in a browser, not just read in the code (`fabius-disciplina`'s prove rule).

After final design, use ARIA-only repairs only when semantics and keyboard behavior already exist. ARIA creates no behavior. If conformance needs a semantic element or interaction, preserve the look with CSS or surface that change for owner sign-off.

Pairs with: `fabius-disciplina` (brainstorm the layout, prove it live), `fabius-parcus` (the smallest CSS that holds the look), `fabius-mercatus` (on a landing page, the message and copy are mercatus's; this layer owns the visual execution).
