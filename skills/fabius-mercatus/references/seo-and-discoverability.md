# Fabius Mercatus — SEO & discoverability

Organic discovery is a channel, not a sprinkle — it earns the same mercatus discipline as the rest: scout the demand, strike the one query that converts. The frameworks and funnel map live in [marketing-playbook.md](marketing-playbook.md); the per-surface copy lives in [channel-swipe-library.md](channel-swipe-library.md). This file is how to make a page *findable* without softening its message. **Scout wide, strike narrow.** Tool versions below are an early-2026 snapshot — encode the decision, re-verify the version.

---

## 1 · SEO is a channel, not a sprinkle

Don't "add some keywords" to a finished page. Decide up front: is organic search how this buyer arrives? If yes, it gets a target query, a matched intent, and a structured-data pass — the same rigor as an ad or an email. If no, skip it; an SEO pass on a page nobody searches for is wasted craft (`fabius-parcus`).

The four layers, each a decision the reader makes:

| Layer | The decision | Failure mode |
|---|---|---|
| **Keyword / intent** | the ONE query a buyer actually types, matched to awareness | targeting volume, not intent |
| **On-page** | one focused intent per page; title/meta/H1 carry it honestly | keyword-stuffing; two intents on one page |
| **Technical** | crawlable, fast, mobile-first — the floor below which nothing ranks | shipping a page engines can't read |
| **Content clusters** | a pillar + supporting pages, interlinked, earning depth | one thin page trying to rank for everything |

Worked example: **Claude SEO** (an ARGAZ-catalogued tool) packages this as ~19 sub-skills across exactly these layers — keyword research, on-page, technical audit, schema, content clusters. Use it as the map; the decisions below are what to keep regardless of which tool runs them.

## 2 · Keyword / intent — match the query to the awareness level

A keyword is a question with an awareness level baked in. The buyer who types *"why are my support tickets piling up"* is problem-aware; *"best ticket automation tool"* is solution-aware; *"[your product] pricing"* is product-aware. Target the query, then lead with the awareness it carries (playbook §2 — the same Schwartz table).

| Intent | The query shape | Lead the page with |
|---|---|---|
| **Informational** | "how to / why / what is" | name + frame the problem; soft path to the offer |
| **Commercial** | "best / vs / review / alternative" | your difference, proof, the comparison you win |
| **Transactional** | "buy / pricing / [brand] + signup" | the offer, the price, the one CTA — get out of the way |
| **Navigational** | "[brand name]" | own it cleanly; don't fight yourself for the click |

**The decision:** pick ONE primary query per page, matched to the awareness the page is built to convert. Commercial-intent queries convert; informational queries feed the cluster (§5). A page chasing two intents ranks for neither — the same "two asks ≈ no ask" law as the funnel.

## 3 · On-page — carry the query honestly

One focused intent per page. The query appears where it belongs, never stuffed:

| Element | Carries the query as | Watch for |
|---|---|---|
| **Title tag** | the exact intent, ~50–60 chars, the promise first | clickbait the page doesn't pay off |
| **Meta description** | the proof + the one CTA (it's ad copy, not a summary) | a generated sentence nobody clicks |
| **H1** | one per page, the same promise as the title | multiple H1s; an H1 that fights the title |
| **Headings (H2/H3)** | the sub-questions the query implies | heading-as-decoration with no structure |
| **Body** | the answer, proof-first (§4) | keyword density games; thin filler |

**Structured data (JSON-LD)** so engines and AI answer-boxes can parse the page without guessing. Match the schema to the page:

```
Article / BlogPosting  → editorial, guides, the cluster pages
FAQPage                → an objections/FAQ block (playbook §6) made machine-readable
Product + Offer        → a product/pricing page (price, availability, rating)
BreadcrumbList         → the path, so engines render the hierarchy
Organization           → the brand entity, once, site-wide
```

Validate it (Schema.org / Rich Results test) — invalid JSON-LD is silently ignored, which looks like it's working. The honest-claim rule (§4) applies inside schema too: a `Rating` or `Review` field must be a real, defensible number, not a decoration.

## 4 · Proof over adjectives — earn the citation

Same honest-claim discipline as the rest of mercatus (playbook §3), now load-bearing for ranking and for AI answers. An adjective doesn't get cited; a number, a demo, or a named source does. *"The fastest tool"* is unrankable and unquotable. *"Renders in 0.3s, p95 — measured"* is both. Write claims an engine — and an AI answer-box — can lift verbatim and attribute. (Same posture as fabius's own benchmark line: lead with the proven figure, never the inflated one.)

## 5 · Content clusters — depth earns authority

One thin page can't out-rank a topic. Build a **pillar** (the broad, high-intent page) plus **supporting pages** (each a specific sub-query), interlinked both ways. The pillar earns authority from the cluster; the cluster earns relevance from the pillar.

```
[PILLAR]            the broad commercial-intent page (the money page)
   ├── [support]    "how to [sub-task]"        (informational, links up)
   ├── [support]    "[product] vs [alt]"       (commercial, links up)
   ├── [support]    "[use-case] guide"         (informational, links up)
   └── ...          each links to the pillar; the pillar links to each
```

**The decision:** don't spawn 20 thin pages — ship the pillar plus the 3–5 supporting pages that answer the queries a buyer actually asks on the path to the pillar. Each page keeps ONE intent (§2). YAGNI on the long tail until the core cluster ranks (`fabius-parcus`).

## 6 · Technical — the floor below which nothing ranks

This is the never-trim floor of the channel: a page engines can't crawl, can't read fast, or can't use on mobile does not rank, no matter how good the copy. Don't optimize content on a page that fails here first.

| Check | The decision | Tool (early-2026 snapshot) |
|---|---|---|
| **Crawlability** | clean `sitemap.xml`, honest `robots.txt`, one `canonical` per page | Search Console; the engine's own inspector |
| **Core Web Vitals** | LCP fast, CLS near-zero, no layout jank | Lighthouse / PageSpeed Insights |
| **Mobile-first** | the page is indexed as its mobile self — verify mobile first | Lighthouse mobile profile |
| **Indexability** | no accidental `noindex`, no orphan pages, no broken canonicals | Search Console coverage report |

Speed and CLS are *built*, not configured — the implementation (responsive images, no font-swap jank, no immutable-cache staleness) routes to **→ `fabius-decor`**. Verify the live page, not the local build (`fabius-disciplina`): a clean Lighthouse score on localhost can hide a production CSP or cache regression.

## 7 · AI-answer visibility — be the cited source (the 2026 layer)

Increasingly the click is replaced by an AI answer that cites a source. The new game is not "rank #1" — it's *be the thing the answer quotes and attributes*. Same discipline, sharper:

- **Quotable facts.** A clear, standalone claim with a number is liftable. An adjective-laden paragraph is not. Write sentences that survive being pulled out of context.
- **Structured data (§3).** Schema is how a model parses your claim without inference. FAQPage and Product schema feed answer-boxes directly.
- **One clear claim per block.** The same "one idea per line" law (playbook §5) — a block doing two jobs gets cited for neither.
- **Proof-over-adjectives (§4) is the whole game.** A model cites a defensible figure and a named source; it skips marketing prose. The honest claim is the citable claim.

The decision: optimize the page to *answer*, not just to *rank* — because the answer is increasingly where the buyer stops. Tactics here move fast (answer-box formats, which engines cite); encode the principle — structured, quotable, proven — and re-verify the tactic.

## 8 · Funnel link — SEO feeds the top, not a competing CTA

Organic search is the top of the one-action funnel (playbook §7): **search → landing → the single CTA.** An SEO page is still a funnel surface, so it keeps the one-action law — don't let "rank for more" sprout a second button, a newsletter box, *and* a demo link competing on one page. The query sets the awareness; the page leads with that awareness and points at the one next step. A page that ranks but offers five exits converts like a page with none.

```
search query  → the page that matches its intent (§2)
the page      → leads with the matched awareness, proof-first (§4)
the one CTA   → the single next step (signup / buy / book — pick one)
```

## When NOT to optimize

- **Don't SEO a page nobody searches for.** No real query volume → no channel here. Validate the demand first (`fabius-parcus`).
- **Don't chase volume over intent.** A high-volume informational query that never converts is a vanity ranking. Strike the commercial-intent query that moves the funnel.
- **Don't game density or stuff schema.** Keyword stuffing and fake ratings get penalized and erode trust — and a claim that won't survive scrutiny (§4) costs more than the ranking it buys.
- **Don't spawn the long tail before the core cluster ranks.** Ship the pillar + 3–5 supports; expand only when they earn it.

---

**Boundary.** This layer owns the *message and its findability* — the query match, the honest on-page claim, the cluster strategy, the funnel link. The page's visual build, Core-Web-Vitals implementation, and RTL/`dir` mechanics are **`fabius-decor`**. Demand-validation and live-verification are **`fabius-disciplina`**. Prose-trim and the YAGNI long-tail call are **`fabius-parcus`**. Named tools (Claude SEO and its sub-skills, Lighthouse, Search Console) are capabilities fabius *applies*, not runtime it bundles — fabius ships no runtime; the optional live tier is in ARCHITECTURE.md. The user's brand and instruction always win; `stop fabius` drops the stance.
