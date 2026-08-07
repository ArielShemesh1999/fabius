# Fabius Mercatus — SEO & discoverability

Organic discovery is a channel, not a sprinkle — it earns the same mercatus discipline as the rest: scout the demand, strike the one query that converts. The frameworks and funnel map live in [marketing-playbook.md](marketing-playbook.md); the per-surface copy lives in [channel-swipe-library.md](channel-swipe-library.md). This file is how to make a page *findable* without softening its message. **Scout wide, strike narrow.** Tool versions and the dated vendor rules below are a 2026 snapshot — encode the decision, re-verify the date. Rich results, crawler tokens and AI-answer surfaces are the fastest-rotting facts in this file.

---

## 1 · SEO is a channel, not a sprinkle

Don't "add some keywords" to a finished page. Decide up front: is organic search how this buyer arrives? If yes, it gets a target query, a matched intent, and a structured-data pass — the same rigor as an ad or an email. If no, skip it; an SEO pass on a page nobody searches for is wasted craft (`fabius-parcus`).

The four layers, each a decision the reader makes:

| Layer | The decision | Failure mode |
|---|---|---|
| **Keyword / intent** | the ONE query a buyer actually types, matched to awareness | targeting volume, not intent |
| **On-page** | one focused intent per page; title/meta/H1 carry it honestly | keyword-stuffing; two intents on one page |
| **Technical** | crawlable + indexable is absolute; fast + mobile-first is the tiebreaker above it | shipping a page engines can't reach — or stalling copy behind a Lighthouse score |
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

**Name the thing in the language the buyer types.** On a non-English page the local primary term and its Latin/English equivalent are *different strings* to a search engine and to an answer engine. A site that writes `AI` on every screen has nothing for a query in `בינה מלאכותית` to match — while every local competitor ranking for that offer leads with the local phrase. Same for feature names: the market searches the words it says out loud, not the industry abbreviation. The fix is not stuffing — spell the primary term out **once, at first mention, in ordinary technical prose** (`בינה מלאכותית (AI)`) and again in the title, the meta description and the schema. Keep the Latin term as well; local technical writing uses both. Measure it with a term-coverage grep across every page, before and after — that is what turns "improve SEO" into a checkable number. (Reading direction and `dir` mechanics are **→ `fabius-decor`**; the *term choice* is this layer's, because it is the query match of §2.)

**Structured data (JSON-LD)** so an engine renders the page as a rich result instead of a plain blue link. That is the whole payoff: schema is a **rich-result** lever, not an AI-answer lever (§7). Match the schema to the page:

```
Article / BlogPosting  → editorial, guides, the cluster pages
Product + Offer        → a product/pricing page (price, availability, rating)
BreadcrumbList         → the path, so engines render the hierarchy
Organization           → the brand entity, once, site-wide
Event · Recipe · SoftwareApplication · Q&A · Video → when the page IS that thing
```

**Ship no type you haven't checked against the live gallery.** Low-usage rich results get retired on a rolling basis, and retired markup stays *valid* schema.org — nothing errors, it just never renders, which is indistinguishable from a bug you can't find. `FAQPage` is the current example: it stopped rendering in Google results on **7 May 2026**, and the documentation, the Search Console report, the search-appearance filter and Rich Results Test support were pulled on **15 June 2026** — `HowTo` went the same way back in September 2023. Keep the FAQ *block* on the page; it still disarms the top three objections (playbook §6) and it still answers the sub-questions of §2. Just stop paying markup for a SERP feature that no longer renders one.

Validate it (Schema.org / Rich Results test) — invalid JSON-LD is silently ignored, which looks like it's working. The honest-claim rule (§4) applies inside schema too, and it needs an **audit**, not just an assertion: the rendering code and the structured-data emitter are usually written together, so a page that synthesizes ratings or reviews for its cards emits them again as `Review` nodes and an `aggregateRating` — handing a search engine fabricated review data as fact, which is a policy violation, not a copy nit. So **grep the JSON-LD, not just the prose** — `aggregateRating`, `reviewCount`, `ratingValue`, `"@type":"Review"` — then check whether the numbers are **load-bearing**: a rating that also drives a shop filter, a sort order, a card chip or a "most-loved" rail makes removing it the owner's product decision, not an edit you make quietly.

**One description, every surface — diff them together.** A page's description ships in four places: `<meta name="description">`, `og:description`, `twitter:description` and the JSON-LD `description`. Edit one and the other three silently disagree, so the SERP, the social card and the answer-box quote three different promises. Grep every surface the page actually emits and diff the strings rather than counting them — `twitter:*` is optional and falls back to `og:*`. Same rule for the one quotable brand sentence: repeat it **verbatim** in the copy, the JSON-LD, any `llms.txt`, and any chat agent's grounding file, or the agent and the schema drift away from the page. And re-check the schema's entity lists (`knowsAbout` and friends) against the **current** offer — they are the first thing to rot after a repositioning, and they belong rebuilt from the site's own offer list so nothing is invented.

## 4 · Proof over adjectives — earn the citation

Same honest-claim discipline as the rest of mercatus (playbook §3), now load-bearing for ranking and for AI answers. An adjective doesn't get cited; a number, a demo, or a named source does. *"The fastest tool"* is unrankable and unquotable. *"Renders in 0.3s, p95 — measured"* is both. Write claims an engine — and an AI answer-box — can lift verbatim and attribute. (Same posture as fabius's own benchmark line: lead with the proven figure, never the inflated one.)

**Invented proof rides in the pixels too.** A cover shot, OG card, poster or tour video captured from your own demo product carries THAT product's marketing copy forward as your claim — and the prose on a case study gets fact-checked while the imagery never does. A demo's landing page is built to look like a real business, so it is full of invented ratings, user counts, client logos and prices. Before shipping any capture, map the product's sections and shoot only the ones that show the **product** — tool grids, editors, real flows — never the hero, the social-proof band or the pricing table. Then pull frames out of the *encoded* video and sweep their text nodes against a banned-pattern list (star glyphs, `n/5`, user counts, "trusted by", currency, "per month", "reviews") — stronger than OCR. Structurally excluding the banned bands from the composite beats hoping they stay off-frame. (The capture pipeline is **→ `fabius-decor`**; the claim it asserts is this layer's.)

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

## 6 · Technical — one absolute floor, one tiebreaker above it

**Split them; they are not the same rule.** Crawlability and indexability are absolute — an unindexed page can't rank, can't earn a snippet, and therefore can't be quoted in an AI answer either (§7). No copy fixes that, so fix it first. Speed and layout stability are *not* absolute: the most relevant content still gets shown when the page experience is sub-par, and Core Web Vitals earn their weight mainly when several equally relevant answers compete for the same query. So never stall content work behind a Lighthouse number — and never ship a page engines can't reach.

| Check | The decision | Tool (early-2026 snapshot) |
|---|---|---|
| **Crawlability** | clean `sitemap.xml`, honest `robots.txt`, one `canonical` per page | Search Console; the engine's own inspector |
| **Core Web Vitals** | LCP ≤2.5s, INP ≤200ms (it replaced FID), CLS ≤0.1 — a tiebreaker, not a gate | field data (`web-vitals` / CrUX); Lighthouse is the lab proxy |
| **Mobile-first** | the page is indexed as its mobile self — verify mobile first | Lighthouse mobile profile |
| **Indexability** | no accidental `noindex`, no orphan pages, no broken canonicals | Search Console coverage report |

Speed and CLS are *built*, not configured — the implementation (responsive images, no font-swap jank, no immutable-cache staleness) routes to **→ `fabius-decor`**. Verify the live page, not the local build (`fabius-disciplina`): a clean Lighthouse score on localhost can hide a production CSP or cache regression.

**Read the floor off the live host in one pass.** `fabius recon <domain>` (in `runtime/`, no key, no account) returns the discoverability half of this table alongside the security half: `<title>`, meta description, `canonical`, `og:image`, the `viewport` tag, `lang` on `<html>`, whether a sitemap exists, and what `robots.txt` actually says — each as a finding with the fix. Two of those are ranking-relevant in a way that is easy to miss: **no `viewport`** means the page is judged as its mobile self and fails, and **no `lang`** breaks both screen readers and right-to-left rendering. The security findings from the same scan are `fabius-praesidium`'s to action (→ `../../fabius-praesidium/references/external-recon.md`); this layer owns the discoverability reading of them.

**`robots.txt` is not the whole gate — read it, then test it.** A CDN or WAF rule can return `403` to a crawler the file explicitly allows, and that rule lives in a dashboard, not in the repo, so it is invisible to every code-side check. The crawl test is therefore a **live fetch carrying the crawler's own user-agent**, not a read of the rules. Which crawlers have to get through, and the edge categories that decide it, are §7.

## 7 · AI-answer visibility — be the cited source (the 2026 layer)

Increasingly the click is replaced by an AI answer that cites a source. The new game is not "rank #1" — it's *be the thing the answer quotes and attributes*. Same discipline, sharper. But **check the gate before you touch a word of the copy**: a page the engine can't fetch is absent from the answer no matter how well it's written, and the permissions are granted **per purpose, not per vendor** — they do not travel together.

| Gate | The rule | What blocking it actually costs |
|---|---|---|
| `OAI-SearchBot` | allow it, or you are not in ChatGPT's search answers | opted-out sites can still appear as navigational links, never as the cited answer |
| `GPTBot` | training-only — a licensing decision, not a visibility one | disallowing it costs zero search visibility; allowing it buys zero |
| `Claude-SearchBot` | the Claude-side equivalent of `OAI-SearchBot` | disabling it reduces the site's visibility and accuracy in user search results |
| `ChatGPT-User` · `Claude-User` | live, user-triggered fetches | the assistant can't open your page for the person who asked for it |
| Googlebot | there is **no AI token to allow** — AI Overviews and AI Mode ride Googlebot | `noindex`, `nosnippet`, `data-nosnippet` and `max-snippet` quietly remove you from them |
| `Google-Extended` | governs Gemini-app training and grounding only | nothing in Search or its AI features — it is not an inclusion or ranking signal |
| Search Console → *generative AI features* | the site has to be **included** to be eligible at all | opting out zeroes AI impressions and traffic while leaving core rankings untouched |

Read the live `robots.txt` first and match it against that table. A blanket disallow written during the 2023–24 anti-training panic is the most common cause of a well-written page that is never quoted — and the second most common is that nobody knew the opt-out toggle was flipped. No rewrite fixes a `403`.

**The edge decides too, and its defaults are not neutral.** Bot management now sorts AI traffic into three independently controlled categories — **Search**, **Agent** and **Training** — each set to block on all pages, block only on ad-bearing pages, or not block at all; on Cloudflare this reaches every plan including Free, and from **15 September 2026** newly onboarded domains get Training and Agent blocked on ad-bearing pages while Search stays allowed. Rule the three deliberately rather than inheriting them: allow **Search** if you want to be cited, and treat **Agent** as the decision about whether an assistant may complete a task on your site. **Training is not the free lever it looks like.** The big crawlers are multi-purpose — Googlebot, Applebot and BingBot crawl for search *and* for training from the same agent — and the edge resolves a bot matching several categories under the **most restrictive** rule that applies. So blocking Training blocks Googlebot outright and deindexes the site: the licensing question and the visibility question are the same question at this layer, whatever the category names suggest. Only a genuinely single-purpose agent (`GPTBot` in `robots.txt`, say) can be refused at zero search cost. Change one category at a time and re-check indexing after each. Then prove the ruling from outside — fetch the live URL with the crawler's user-agent (§6), because `robots.txt` can say yes while the WAF says `403`, and only the `403` is real.

Once the gate is open, the writing:

- **Quotable facts.** A clear, standalone claim with a number is liftable. An adjective-laden paragraph is not. Write sentences that survive being pulled out of context.
- **Structured data is not the AI-answer lever (§3).** There is no special schema.org markup, no AI text file and no requirement to chop content into pieces for generative answers. On Google the whole eligibility rule is narrower than the folklore: the page must be indexed and allowed to show a snippet — that is the rule, in full. Ship schema for the rich results it still earns — never as an AI-visibility play. Treating markup as the citation mechanism is the most expensive piece of current folklore, because it spends the budget that being *retrievable* and *the most complete source on the question* would have earned.
- **One clear claim per block.** The same "one idea per line" law (playbook §5) — a block doing two jobs gets cited for neither.
- **Proof-over-adjectives (§4) is the whole game.** A model cites a defensible figure and a named source; it skips marketing prose. The honest claim is the citable claim.

The decision: optimize the page to *answer*, not just to *rank* — but **price the move**, because most of what circulates as AI-answer tactics does not survive measurement. Only two levers reproduce across the evidence: **topical relevance**, and **position in the context the engine retrieves** — moving a source higher in that context beats almost every rewrite. Rewriting the body to sound quotable is not free: measured citation-oriented rewrites cut top-20 retrieval presence ~9%, post-rerank top-10 presence ~16% and final citation ~6% — you can win the quote and lose the retrieval that would have produced it. Keyword stuffing transfers *negatively* from classic SEO, and any generic tactic decays as competitors adopt it. And treat AI visibility as a **distribution, not a rank**: repeated runs at temperature zero flip 9–28% of decisions, and month-to-month page overlap runs ~18% for AI Overviews against ~45% for organic. So one spot-check proves nothing — measure ~7–8 repetitions across 3–5 paraphrases against an untreated control, or make no claim at all. (The circulating "~40% visibility gain" is a relative maximum on one metric under one configuration; don't quote it, and don't let a client quote it back.)

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
- **Don't mass-produce the cluster.** *Scaled content abuse* — many pages generated mainly to catch rankings rather than to help someone — is an enforced spam policy that names generative-AI tooling as an explicit example, and **how the page was produced is irrelevant to the judgement**: the absence of added value is the violation. The same policies now cover attempts to manipulate generative-AI answers, so a page written to game an answer box (§7) is in scope too, and *site reputation abuse* — third-party content parked on your domain for its ranking signals — is the same family. This matters more here than in a human-authored playbook, because fabius is the thing that would generate those pages: pillar + 3–5 supports (§5) is a **safety limit**, not a preference. Every support page answers a question a buyer actually asks, or it is a liability on the whole domain.
- **Don't spawn the long tail before the core cluster ranks.** Ship the pillar + 3–5 supports; expand only when they earn it.

---

**Boundary.** This layer owns the *message and its findability* — the query match, the honest on-page claim, the cluster strategy, the funnel link. The page's visual build, Core-Web-Vitals implementation, and RTL/`dir` mechanics are **`fabius-decor`**. Demand-validation and live-verification are **`fabius-disciplina`**. Prose-trim and the YAGNI long-tail call are **`fabius-parcus`**. Named tools (Claude SEO and its sub-skills, Lighthouse, Search Console) are capabilities fabius *applies*, not runtime it bundles — fabius ships no runtime; the optional live tier is in ARCHITECTURE.md. The user's brand and instruction always win; `stop fabius` drops the stance.
