<!-- © 2026 Ariel Shemesh · fabius · reference depth for skills/fabius-decor/SKILL.md -->

# Decks, infographics, and visual reports — the presentation concern

Three deliverables under one decor discipline: `slides.create` (a deck), `visual.infographic`
(one graphic that carries one message), and `document.create` (a visual report). All three are
design surfaces — the token laws, the one-accent rule, and figura's data-ink discipline apply
unchanged. What this file adds is the *composition* doctrine for each.

**Native format: HTML first.** fabius's presentation deliverable is a self-contained HTML
page (inline CSS, self-hosted or system fonts) — renderable in any browser, exportable to PDF
or PNG through headless Chrome (the established render pipeline), theme-aware, and editable as
text. When a recipient demands a vendor format, that conversion is the user's own step from
the PDF/PNG export — a vendor format is never the working medium.

## 1 · Decks — the narrative comes before the pixels

- **Outline first.** Write the argument as a one-line-per-slide outline and get it agreed
  before designing anything (ambiguity → grill one question at a time, disciplina's job). A
  deck whose outline doesn't stand is not rescued by design.
- **One idea per slide.** The slide headline states the idea as a claim ("Retention doubled
  after onboarding v2"), never a category label ("Retention"). If a slide needs two claims,
  it is two slides.
- **A deck is an argument, not a document.** Prose goes in the report; the deck carries the
  spine: problem → evidence → decision → ask. Few slides, big type — if a slide can't be read
  from the back of the room, it is a handout pretending to be a slide.
- **Data slides are figura charts** — data-ink rules, one highlighted series, the claim in the
  headline and the chart as its proof. Never paste a screenshot of numbers.
- **Deck-level tokens.** One accent, one type scale, one grid, consistent slide margins —
  defined once at the top of the file, used everywhere; brand tokens slot in when the user has
  a brand ([`design-tokens.md`](design-tokens.md)).

## 2 · Infographics — one message, measured

- **One message per graphic.** The headline stat or claim leads; everything else supports it.
  An infographic that needs a paragraph of explanation failed as an infographic.
- **Hierarchy in three beats:** the hook (the number or claim, largest) → the support (the
  2–4 facts that ground it) → the source line (where every number comes from, smallest but
  present). No number without a source; no invented statistics, ever.
- **Clarify before generating** when the request is one line: audience, the single message,
  and the brand (if any) — three questions, one at a time, then build.
- **Composition rules carry over:** one accent on a neutral field, real hierarchy by size and
  weight (not by rainbow), icons from one family ([`icons.md`](icons.md)), charts by figura
  rules ([`visualization.md`](visualization.md)). Export: headless-Chrome render → PNG/WebP at
  the target's native ratio.

## 3 · Visual reports — every number is measured

The report is decor executing archivum-grade honesty: a masthead that states scope and date, a
figures strip of the headline numbers, sections that each answer one question, and tables that
carry proof columns. The law that makes it a *fabius* report: **every number on the page is
re-derived from the system it describes** — measured at write time, dated, and traceable — and
a claim that couldn't be measured says so instead of estimating. A report whose numbers can't
be re-derived is marketing, not reporting.

## 4 · The seam with the other layers

Mercatus owns what the deck *says* to a market (positioning, the ask); decor owns that it
lands visually. A pitch deck runs as a studio: mercatus leads the narrative, decor executes
the surface. A meeting record that becomes a deck starts from archivum's filed record —
nothing is re-derived from memory of the meeting.
