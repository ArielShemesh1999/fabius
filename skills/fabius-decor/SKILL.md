---
name: fabius-decor
description: >
  fabius's ship-grade design layer — gives the agent a token vocabulary, the universal laws that
  separate amateur UI from shipped UI, and a quality checklist. Use when building or reviewing any
  UI — a landing page (visual execution; the message and copy are fabius-mercatus), a component, a
  screen, an email, a slide, a brand surface, a chart, a graph, a diagram, a data visualization —
  when the user references a brand look, or asks to make something "look good", "more polished",
  "production quality", "chart this", "graph this", or "visualize this data". Also covers
  generating images (for image models) and explanatory diagrams that teach a system: "generate an
  image", "diagram this", "explain this codebase visually". Also owns icon choice, motion
  libraries, design assets (illustrations · 3D · textures · fonts · color · HuggingFace) and
  right-to-left / bidirectional layout (RTL, Hebrew/Arabic). The
  fabius-design/-motion/-frames/-uiux/uiverse bundles live in references/design/; entry doc
  references/design-system.md.
when_to_use: >
  "make it beautiful", "it looks amateur", "match the brand", spacing/typography/color calls,
  dashboards, hero sections, dark mode.
license: UNLICENSED
metadata:
  author: Ariel Shemesh
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

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

Depth — chart-type decision table, the data-ink checklist, accessible color ramps, and the SVG recipes (the **fabius-figura** corpus library) → `references/visualization.md`, paged in on demand (R9 · M9). The diagram-as-code path (flowcharts, architecture) pairs with `fabius-disciplina`.

## Explanatory diagrams — teach the system, don't just draw it

A diagram that *explains* (a codebase, a domain, a flow) is a pedagogy problem, not a drawing one — and the method is repeatable in three moves: **extract deterministically, then add meaning** (a parser produces the reproducible facts; the model adds only semantic judgment, never re-deriving structure); **make the artifact a typed graph** (a small fixed vocabulary of node/edge types, stable ids, weighted edges); **order by topology, teach by narrative** (fan-in ranks importance, the entry point starts the tour, BFS depth maps to step order — a guided tour, not a node dump).

The full method — concept-map structuring, the typed-graph schema pattern, and the topology-to-tour algorithm → `references/explanatory-diagrams.md`.

## Generative imagery — prompt the image, don't wish for it

Generating an image is a *design* act under the same restraint as everything else here — and an image prompt is a **structured slot fill**, not a freeform sentence:

1. **Slots, not a sentence.** Fill ordered slots — subject → facial/detail → styling → expression → **lighting** → scene → technical/quality. Fill the required ones with intelligent defaults even when the user is silent; leave optional ones empty rather than padding noise.
2. **Lighting is mandatory.** It is the single highest-leverage lever and the biggest amateur-vs-pro gap — always specify it (map "cinematic" → cinematic, neon/cyberpunk → neon, unspecified → natural). Never omit it.
3. **Cascade from one signal.** A high-level cue should propagate: era/setting sets makeup *and* hair *and* wardrobe together — derive the coupled attributes instead of asking for each.
4. **Run a conflict pass before emitting.** Check cultural, temporal, and biological consistency; on a clash, explain it, show the auto-correction, and let the user override. Keep *style* separate from *identity* — "anime" is a render technique, not an ethnicity; a style keyword must not silently overwrite an attribute slot.
5. **Library + free-text.** Keep recombinable elements (lighting recipes, camera/lens, palettes) as a reusable set; let the model supply the open-set content it can't enumerate (named characters, specific materials); merge both into one coherent prompt. End on a completeness check: subject, lighting, explicit style, quality/technical tags.

The slot schema, the lighting/era mapping tables, the conflict-resolution rules, and the structured-palette recipe → `references/generative-imagery.md`.

## Using a brand spec as a target

1. Pick the closest brand in `references/design/` (69 systems — `DESIGN-apple.md`, `DESIGN-stripe.md`, `DESIGN-linear.app.md` …) as the visual DNA; the token contract is in `references/design-tokens.md`. The fabius-design library's entry doc — the token vocabulary plus three worked brand reference points — is `references/design-system.md` (the entry CORPUS.md designates); the bundled animation and component libraries (`fabius-design`, `fabius-motion`, `fabius-frames`, `fabius-uiux`, `uiverse`) sit alongside the teardowns in `references/design/`.
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

Pairs with: `fabius-disciplina` (brainstorm the layout, prove it live), `fabius-parcus` (the smallest CSS that holds the look), `fabius-mercatus` (on a landing page, the message and copy are mercatus's; this layer owns the visual execution).
