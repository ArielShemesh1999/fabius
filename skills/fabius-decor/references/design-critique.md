<!-- © 2026 shear559 · fabius · reference depth for skills/fabius-decor/SKILL.md -->

# Fabius Censura — the censor's floor: review vocabulary, generated-UI tells, bounded verdicts

Loaded on demand by `fabius-decor`. The skill's "Review before ship" section ([`../SKILL.md`](../SKILL.md)) is the contract; this file is the office behind it: how a surface is judged, which mechanical tells disqualify it, when judging stops. fabius supplies vocabulary and discipline; the harness runs whatever scanner or browser a review needs; the model reads. One law outranks everything below, catalogue included: **the brief wins**. A pinned aesthetic, era, material, face or palette beats any saturated-pattern warning; bending a clear brief toward the reviewer's taste is the failure.

## 1 · Surface modes — per surface, never per product

Name the mode before picking a verb; it states what counts as success for the visitor on *this* surface and is recorded with that surface's brief only. A tool's landing page is Persuade while its app is Operate.

| Mode | Success | Surfaces | Expression may never obscure |
|---|---|---|---|
| **Persuade** | decides and acts | landing, marketing, campaign, pricing | the hook in one line, the primary action visible, the reading order legible |
| **Operate** | finishes a task | app UI, dashboards, editors, settings, admin and internal tools | task, state, familiar affordance; brand lives in precise details |
| **Read** | understands | docs, articles, guides, help, changelogs | comprehension and wayfinding |
| **Experience** | is inside the work | portfolios, galleries, showcases | the work, leading from the first viewport; the interface recedes |

Operate depth (upstream's figures): one type family; rem scale 1.125–1.2; prose 65–75ch, tables fine at 120ch+; transitions 150–250 ms, no page-load choreography; skeletons over spinners; overlays via `<dialog>` or popover ([`platform-baseline.md`](platform-baseline.md)).

Accessibility is judged under `audit` against decor's WCAG 2.2 AA gate (platform-baseline.md); upstream's own site baseline is 2.1 AA, and its craft floor carries no a11y check: upstream's `CLAUDE.md` records that a model reminded of accessibility at design time retreats into underdesigned output, so the check lives in `audit` and in the Sam persona. This file keeps that split.

## 2 · Three laws before any verb

1. **The brief wins.** Above.
2. **Refinement preserves; redesign replaces.** Refining keeps incumbent identity, behavior and copy, touches nothing outside scope, asks before replacing factual copy or adding a claim. Redesign carries over product truth, content, function and constraints; the old look becomes evidence about the subject and a thing to steer away from, never a target. A look being discarded is never polished.
3. **Visual authority is evidence, not a filename.** A missing DESIGN.md does not make a project greenfield; a coherent identity already in code is inherited and documented. A component added inside an established surface inherits it.

## 3 · Review verbs — fabius vocabulary

Every refine, enhance and fix verb except `overdrive` ends by handing the surface to `polish`; `overdrive` closes on its own four tests (wow · removal · device · context). `bolder`, `quieter`, `colorize` and `typeset` retune an identity and never replace one (that is redesign). Figures are upstream's playbook numbers.

| Verb | Changes | Preserves |
|---|---|---|
| **shape** | the brief: 2–3 related questions per round, one round by default | no CSS values, canned lane or code |
| **critique** | nothing; judges only (§6) | the design review is written before the scan output is opened |
| **audit** | nothing; five dimensions 0–4 (/20): a11y, performance, theming, responsive, integrity; every detector hit verified | documents, never fixes |
| **polish** | drift, narrowest first: blocked tasks → missing states → flow, hierarchy, responsive, tokens → visual, motion → cleanup | the concept; a wrong one is reported, not smuggled out |
| **bolder** | a flat section, up to its neighbors' strongest moves | the system's vocabulary; no new colors, faces, radii, shadows or primitives unasked; louder everywhere is flat again |
| **quieter** | saturation to ~70–85%, weights one step down (900→600, 700→500), motion to 10–20px ease-out-quart, color near 10% | some hierarchy, some color; never all of either removed |
| **distill** | one goal, one next action, 1–2 colors plus neutrals, one family (3–4 sizes, 2–3 weights), sentences halved twice | a11y; a complex domain's depth |
| **harden** | extremes: 100+ char names, emoji, RTL and CJK, billions, 1000+ items, empty, ten rapid submits; 30–40% translation room | validation server-side too |
| **onboard** | time-to-value: 1–3 concepts, a 3–7 step skippable tour, empty states that say what belongs here and how to start | never shown twice |
| **animate** | one authored moment: 100–150 ms feedback, 150–300 state, 300–500 layout or view, 500–800 focal entrance; exits faster than entrances | content visible before any script; reduced motion drops spatial movement and keeps the opacity and state feedback that carries meaning (mechanism: no-motion default, opt in under `no-preference`, [`motion-libraries.md`](motion-libraries.md)) |
| **colorize** | lightness steps, chroma reduced near white and black (OKLCH for a new web palette); dark elevation designed, never inverted | AA contrast; color never the only code |
| **typeset** | 45–75ch measure, 16px body floor, light-on-dark compensated in leading, tracking and one weight step | the type scan stays apart from the judgment |
| **layout** | squint-proof reading order, a 4-unit base scale, `gap` for sibling rhythm, container-aware components | DOM and focus order match the visual order |
| **delight** | one thesis a neighbor could not reuse, scaled to frequency and consequence | completion never delayed; no jokes about loss, money, privacy, blocked work |
| **overdrive** | 2–3 directions, the user's pick before code, 60 fps, progressive enhancement | no sound without opt-in |
| **clarify** | the whole path: what failed, why, how to recover; buttons name the action, never Yes/No/OK | factual or legal copy asks first; progress never invented |
| **adapt** | re-layout, not scaling: 44×44 targets, 16px mobile text, `pointer`/`hover` queries, safe-area insets, mobile-first `min-width` | one real iPhone and one real Android checked |
| **optimize** | only what measured slow: LCP < 2.5 s, INP < 200 ms, CLS < 0.1 | nothing above the fold lazy-loaded; measured before and after on real devices |

## 4 · The craft floor — verify the built result

Checks on what rendered, from the one batched capture of §7. Where decor's SKILL.md holds the law (one accent, tokens, mobile-first, the WCAG gate) this list points there.

- **Contrast**: decor's gate; on a colored surface tint secondary text from the hue, never gray.
- **Depth**: elevation is an offset plus blur; a centred tinted glow is ornament.
- **Spacing**: tight inside a group, generous between, more air above a heading than below — judged on rendered values, not authored ones.
- **Type**: a 65–75ch body measure, display capped at 6rem, tracking never tighter than −0.04em, balanced headings, real copy at every breakpoint with nothing overflowing.
- **Motion**: one authored moment from an already-visible default, not one entrance repeated per section.
- **States**: hover, disabled, loading, error, empty; working controls; keyboard focus.
- **Browser surfaces**: selection, caret, scrollbars, focus ring, underline offset, tabular numerals, themed from the palette.
- **Copy and coverage**: controls name what they do; errors name the fault and the way out; every brief requirement findable in seconds.

**Refuse by default** (the brief can earn any back, with one exception): the hero-metric block, a modal by reflex, sparklines and rings as content, mono as a "technical" costume, a system display face as an own-world voice, emoji or glyphs as icons, glass and blur as decoration, hard zero-blur offset shadows outside a neobrutalist world, light or dark picked by category instead of by use scene (who, where, under what light); the rest are §5 ids. **The one true ban:** a kicker or eyebrow above a heading; no brief earns it back. The floor holds mechanics and never picks direction; with the mechanics green, the page belongs to the committed world.

## 5 · The generated-UI catalogue — scan runs first, judgment is written first

Same principle as [`explanatory-diagrams.md`](explanatory-diagrams.md): a parser yields facts, the model adds meaning. Run order and read order differ: the harness runs the scan first (cheap, deterministic); the model writes its design judgment before opening the scan output, then merges the two, because deterministic findings anchor whatever is read after them. Same order as decor's SKILL.md — two contexts, one verdict.

The parser is impeccable's detector: 61 rule ids in its engine registry (`cli/engine/registry/antipatterns.mjs`), matched by the shipped `plugin/` copy and by README's own count; one generated harness mirror (`.agent/skills/`) lags at 59, lacking `organic-clip-path` and `buried-raster`; read at commit `94b7f34`. Reference implementation: `npx impeccable detect <dir|file|url>` runs the rules deterministically — no model call, no key (`npx impeccable install` installs the skill, a different command); its browser extension runs the same rules. The harness runs it; fabius carries the catalogue and the reading order. A clean scan is a floor, never proof of quality; a hook already running makes a second pass waste.

Grouped by fabius family; upstream's `skillSection` field groups differently. One "why" serves every slop id: a reflex the training data rewards, so its presence says a decision was skipped. Where the id names its own tell, only the fix is given.

| id | tell | fix |
|---|---|---|
| **Color & surface** | | |
| `gradient-text` | | solid; emphasis by weight or size |
| `ai-color-palette` | purple-violet or cyan; hue 260–310 or 160–200 on headings or text ≥20px | a palette from the subject's world |
| `cream-palette` | cream or beige as the reflex "tasteful" ground | same |
| `dark-glow` · `radial-halo` · `radial-spotlight-glow` | zero-offset chromatic halo or radial wash on dark | ground the surface; offset + blur if depth is needed |
| `gray-on-color` | | a darker shade of the hue, or near-white |
| `low-contrast` | under 4.5:1 body, 3:1 large (24px, or 18.67px bold) | decor's gate |
| `side-tab` | thick one-side colored border | hairline or spacing |
| `border-accent-on-rounded` | ≥2px accent border on a rounded box | drop it |
| `gpt-thin-border-wide-shadow` | hairline under a wide soft shadow | border or shadow, once |
| `repeating-stripes-gradient` | | |
| `codex-grid-background` | | only over a real canvas, map or blueprint |
| **Type** | | |
| `overused-font` | Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk and kin; brand fonts exempt on their own domain | a face chosen for the subject |
| `flat-type-hierarchy` | | fewer sizes, ≥1.25 ratio |
| `italic-serif-display` | oversized italic serif hero | roman or another face; an editorial register may earn it |
| `hero-eyebrow-chip` · `kicker-above-heading` | | delete; the heading carries itself |
| `oversized-h1` | full-sentence headline at display size | shorter or smaller |
| `extreme-negative-tracking` | | optical tightening only |
| `all-caps-body` | | caps for short labels |
| `tiny-text` | <12px | ≥14, 16 ideal |
| `undersized-ui-text` | functional text <11px, even on DESIGN.md's ramp | 10px only for non-interactive legal smallprint |
| `tight-leading` | <1.3 | 1.5–1.7 |
| `wide-tracking` | >0.05em on body | |
| `justified-text` | | left-align or `hyphens: auto` |
| `line-length` | past ~80ch | 65–75ch |
| `skipped-heading` | | |
| **Layout** | | |
| `nested-cards` | | dividers and type |
| `icon-tile-stack` | rounded-square icon box above a heading | icon beside the heading, or in flow with no box of its own |
| `monotonous-spacing` | one value over 60% of ≥10 spacings, ≤3 distinct | tight groups, generous separations |
| `numbered-section-labels` | | delete unless the sequence informs |
| `text-occlusion` · `text-overflow` · `clipped-overflow-container` | words under a layer, past their box, cut by `overflow: hidden` | room, wrapping, the positioned layer out of the clip |
| `first-viewport-column-overflow` | | balance or cap the tall column |
| `heading-rhythm` | | more space above than below |
| `cramped-padding` | | ≥8px, ideally 12–16, inside bordered boxes |
| `edge-flush-cards` | | consistent inset |
| `body-text-viewport-edge` | | ≥16px, ideally 24–32, side padding |
| **Motion** | | |
| `bounce-easing` | | ease-out-quart/quint/expo |
| `pulsing-dot` · `blinking-cursor` | | motion only for data that changes |
| `marquee` | hides half its content | the reader sets the pace |
| `layout-transition` | width/height/padding/margin animated | transform and opacity; upstream also allows `grid-template-rows` for height, decor's law 6 does not — here it stays a finding |
| `image-hover-transform` | | feedback on the container, never the picture |
| **Imagery** | | |
| `shape-assembled-illustration` | a "scene" of ≥8 primitives | a real illustration or none |
| `organic-clip-path` | many-vertex polygon faking a torn edge | an alpha matte from the real image |
| `buried-raster` | image under a near-opaque wash or at near-zero opacity | let the material show, or delete the file |
| **Copy** | | |
| `em-dash-overuse` | ≥8 dashes and about one per 500 characters (advisory: listed, never counted) | |
| `marketing-buzzword` | streamline, empower, supercharge, world-class, enterprise-grade | say what it does |
| `aphoristic-cadence` | sections closing on "X. No Y." | |
| `theater-slop-phrase` | dismissing something as "theater" | |
| `repeated-container-text` | one string 3+ times in a card | once |
| **Drift & integrity** | | |
| `design-system-radius` · `design-system-font` · `design-system-font-size` · `design-system-color` | off DESIGN.md's documented step (font size: ±0.5px) | the token or step; adding one is a design decision |
| `script-error` · `content-hidden-at-rest` | error severity; a large share of the text still at opacity 0 after reveal handlers ran | fix the exception before judging anything; content visible by default, JS enhances the entrance |
| `broken-image` | | a real asset or no tag |

## 6 · Critique scoring

**Specificity verdict first**, written before the scan output is opened: could an unrelated product ship this surface unchanged? If yes, nothing else scores well enough to matter. Then:

- **Nielsen's 10 heuristics**, 0–4 each, /40: 36–40 Excellent · 28–35 Good · 20–27 Acceptable · 12–19 Poor · 0–11 Critical. Most real interfaces land 20–32.
- **Mode applicability**: heuristics 7 (flexibility) and 10 (help) may be `n/a` on Persuade and Experience. Renormalize to the applicable max, read the band off the percentage (90/70/50/30), never print /40 over a partial set, record which were `n/a`.
- **Severity**: P0 blocking · P1 major (fix before release; audit adds any WCAG AA violation) · P2 minor with a workaround · P3 polish. Tie-break: would a user contact support about it? Then at least P1.
- **Cognitive load**, 8 checks: single focus · chunks ≤4 · grouping · hierarchy · one decision at a time · ≤4 visible options per decision · no cross-screen recall · progressive disclosure. 0–1 failures low · 2–3 moderate · 4+ high.
- **Working memory** ≤4 items (Cowan 2001; 5–7 strained, 8+ overloaded): 1 primary + 1–2 secondary actions, the rest in a menu; ≤5 nav items; ≤4 sidebar siblings per level; one decision per gallery screen.

Persona lens: five fixed reviewers, chosen by interface type (upstream keys on the interface, not the mode); project personas only from recorded product truth, never invented.

| Persona | Breaks on | Chosen for |
|---|---|---|
| Alex, impatient power user | core task over 60 s, no shortcuts, Esc not dismissing | dashboard/admin, data-heavy |
| Jordan, confused first-timer | first action unclear within 5 s, unlabeled icons | landing, checkout, onboarding, forms |
| Sam, accessibility-dependent | keyboard-only, screen reader, 4.5:1, 200% zoom | dashboard/admin, data-heavy, forms |
| Riley, deliberate stress tester | 0 and 1000 items, refresh mid-flow, paste from a spreadsheet | landing, checkout |
| Casey, distracted mobile | thumb zone, slow network, lost state, 44×44 targets | landing, checkout, onboarding, forms |

A critique whose design review and scan evidence share one context is degraded and says so in its first line; one that ends without its questions to the user (or a stated reason for skipping them) is incomplete.

## 7 · Bounded verification and the finish

Two rounds is the ceiling for screenshots, scans, micro-edits and rebuilds alike (upstream scopes the cap to unattended runs; fabius applies it to both and lets the user, not the model, buy a third).

1. Build fully; no screenshot trips mid-build.
2. One batched capture: desktop (1440 wide, full page) and mobile (390 wide upstream; decor's checklist says ~375 — either phone width, the same one every round) together, plus the user's actual viewport when the harness reports one: whichever width breaks is the first they meet. Validity first: settle or disable entrance motion (a hidden-by-timing element reads as missing and gets "repaired" into a regression), shoot from the document top, open every file and confirm it shows what its name says.
3. Fix everything the round showed, in one batch.
4. At most one confirming round. Then stop: open-ended self-QA spends the user's money doing worse what a fresh reviewer does better.

**The finish reviewer inherits nothing.** It receives the request, artifact, captures and direction contract, never the build transcript (`fabius-disciplina`'s strengthened oracle, [`../../fabius-disciplina/SKILL.md`](../../fabius-disciplina/SKILL.md)). It returns one of four words — **recapture** (the evidence failed), **rebuild** (fidelity failed wholesale), **ship**, **fix** (one batch, at most one rebuild, recapture, verdict) — and a verdict scores only the listed fixes; "no material issues remain" is a claim it cannot make. The user's own evidence (a screenshot, a named mismatch) outranks every capture and reopens a full review.

## 8 · Durable truth — three stores: two before code, one at finish

- **Product truth** (PRODUCT.md-class): users, purpose, positioning, operating context, capabilities and constraints, brand commitments, evidence on hand *and its stated absences*, 3–5 principles, accessibility. Never palettes, faces, components, a visitor mode, or invented testimonials, customers, benchmarks, pricing. Written at init from confirmed facts; repository evidence is a hypothesis, not approval; init asks no aesthetic question.
- **Visual system** (DESIGN.md-class): tokens, type roles, spacing, elevation, shapes, components, do/don't. Written at *finish*, from the built world: a rulebook drafted before the build gets defended against what got built. A new world with no DESIGN.md is unfinished; an ordinary extension does not rewrite it.
- **Surface brief**: the mode and the direction contract, written before code; nothing product-wide.

The direction contract: six blocks, 150 words at most — THESIS · OWN-WORLD · STORY · FIRST VIEWPORT · FORM · FINISH; a block that reads like a mood is undecided. **Leak ban:** it never enters any shipped byte — markup, comments, hidden DOM, data attributes, serialized state, bundles, metadata and JSON-LD, screen-reader-only text, sidecar files; minification is not a boundary. Where these stores live in a fabius project is `fabius-archivum`'s contract ([`memory-schema.md`](../../fabius-archivum/references/memory-schema.md)). "Unattended" is proven by a real question round that goes unanswered, never assumed from a system prompt.

## 9 · Calibration — the looks every model converges on

Three saturated looks appear regardless of subject: **cream ground + high-contrast serif display + terracotta or signal-red accent**; **near-black + one neon accent + glowing edges**; **broadsheet hairlines + italic display serif + small tracked mono labels**. Each is legitimate when the brief asks for it. When the brief leaves the aesthetic free, self-check: if the category alone, or the category plus what you avoided, predicts the aesthetic, rework until neither does. Two corollaries: a negative constraint bans named devices, never energy itself; warmth, books or a child audience licences no cream (a rendition prior upstream records about its own output).

Training-data default faces (upstream's design-time list; naming one needs a reason no other face satisfies, and "books want a serif" is not one): Cormorant, Crimson, DM Sans, DM Serif, Fraunces, IBM Plex, Instrument Sans, Inter as display, Lora, Newsreader, Outfit, Playfair Display, Plus Jakarta Sans, Space Grotesk, Space Mono, Syne. The detector's `overused-font` set differs (§5). System stacks and workhorse UI faces serve Operate and Read well.

**Color-strategy ladder, reconciled with decor's one-accent law (fabius's framing).** Restrained (neutrals plus one accent; the Operate/Read default) · Committed (one saturated color, 30–60% of the surface in upstream's band) · Full palette (three or four colors, each with a named job) · Drenched (the surface *is* the color). Decor's law holds on every rung: `primary` stays the one color every "click me" wears. The ladder governs how much of the *surface* the palette owns, at page scale, in fields that hold whole regions rather than accents sprinkled on a neutral ground. Persuade and Experience may climb; an Operate surface climbs one rung for one surface at a time (a report's category color, a welcome screen) and returns to Restrained, its floor.

**Truth binds claims, not demonstrations.** Greenfield work authors illustrative material at full fidelity, marks it synthetic at every point where a visitor might read it as real, and hands over the replacement list. Uninventable: prices, customers, testimonials, benchmarks, endpoints, capabilities the product lacks; the same line `fabius-mercatus` draws in [`seo-and-discoverability.md`](../../fabius-mercatus/references/seo-and-discoverability.md) §3–4, pixels and JSON-LD included. Refusing a bold direction because its demo data does not exist yet is timidity.

## Pairs with

`fabius-decor` (the laws this office enforces; tokens in [`design-tokens.md`](design-tokens.md)), `fabius-disciplina` (the separate reviewer is its strengthened oracle; prove live), `fabius-archivum` (where product truth, visual system and surface briefs persist), `fabius-mercatus` (a Persuade surface's message and proof are its; the visual verdict is this file's), `fabius-parcus` (two rounds, one batch, stop), `fabius-cohors` (a reviewer spawned with no inherited context).

Informed by **impeccable** (pbakaus/impeccable, Paul Bakaus, Apache-2.0; commit 94b7f34, 2026-09-01, npm CLI 3.6.1 · skill/plugin 4.1.2) — studied for its surface modes, review verbs, craft floor, deterministic anti-pattern registry, critique scoring and bounded verification, re-expressed in fabius's own voice; no upstream files bundled; the iOS/Android material (third-party-derived) was not carried. See credits/README.md.
