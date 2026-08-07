# Fabius Mercatus — the marketing & discoverability toolkit

Loaded on demand by `fabius-mercatus`. Marketing tooling is *noisy* — this is a hard-filtered set (2026): every entry is open or genuinely free, maintained, and widely adopted, with licenses flagged honestly. The **message** is always mercatus's job (positioning, copy that converts); these are the instruments that measure and distribute it. For the **Israeli market**, campaign compliance (Chok HaSpam opt-in, "פרסומת" label) lives in **Fabius Yisrael**.

## Analytics — the launch-loop feedback signal

| Tool | License | Note |
|---|---|---|
| **Umami** | MIT | Simplest self-hosted, cookie-free analytics — referrers/UTM/custom events for a landing page. No copyleft. |
| **Plausible** (CE) | ⚠️ AGPL-3.0 | Privacy-first, lightweight (tracker snippet is MIT). Aggregate-only; server copyleft. |
| **PostHog** | MIT (core) | Funnels + session replay + **A/B experiments** — the *why-isn't-this-converting* engine. Full self-host (ClickHouse/Kafka) is heavy; generous free cloud. *(ee/ source-available.)* |
| **Matomo** | ⚠️ GPL-3.0 | Fullest GA-parity OSS (search-keyword reports, goals) — heaviest to run; best features are paid plugins. |
| **GrowthBook** | MIT (core) | Warehouse-native A/B testing + feature flags with a rigorous stats engine (CUPED/Bayesian/SRM) — honest experimentation without PostHog's stack. |
| **web-vitals** (GoogleChrome) | Apache-2.0 | ~2KB real-user (field) LCP/INP/CLS — the actual Core-Web-Vitals ranking signal (Lighthouse is only a lab score). |

## SEO & discoverability

- **Google Search Console** (free service) — the **ground truth** for what queries a site ranks for, CTR, index coverage, rich-result eligibility, and now the only first-party read on AI visibility: the **Generative AI performance report** (launched June 2026) counts impressions in AI Overviews and AI Mode, broken down by page, country, device and date. Read its limit into every promise made from it — **impressions only, no clicks and no queries** — so AI visibility cannot yet be attributed to traffic or revenue: say *seen*, never *drove*. Check the **generative-AI opt-out** setting in the same console before diagnosing a mysterious zero; a site has to be *included* in Search generative AI features to be eligible at all, and opting out removes those impressions while leaving core rankings untouched. Pair with Bing Webmaster + the open **IndexNow** protocol.
- **Lighthouse** (Apache-2.0) — automatable SEO + perf audit gate in CI (indexability, meta, crawlability). The SEO category is on-page health, not a ranking predictor.
- **schema.org structured data (JSON-LD)** (CC-BY-SA vocab / open W3C) — the machine-readable signal for **rich results**, and *not* the lever for AI citation: Google states plainly that structured data isn't required for generative AI search and that there is no special markup for it. Validate with the Rich Results Test and ship only types in the current supported-types gallery — **HowTo** was retired in September 2023 and **FAQ** stopped rendering on **7 May 2026** (docs, Search Console report and Rich Results Test support pulled 15 June 2026). A retired type raises no error — it just never renders, which reads exactly like a bug you can't find.
- **Open Graph** (`ogp.me`) + Twitter Cards — control the share-preview card (often the first impression) across LinkedIn/X/Slack/WhatsApp.
- **Sitemaps XML** + **advertools** (MIT) — discoverability hygiene + the Python workhorse for SEO/SEM audits (crawl, parse sitemaps/robots, build keyword lists).
- **llms.txt** — present as an **experiment, not a lever**: ~10% adoption after 18 months and **Google confirmed it does not use it**. Cheap to add, unproven payoff — don't oversell it.

## Copy utilities

- **textstat** (MIT) — readability metrics (Flesch/SMOG) to enforce a reading-grade target (high-converting web copy ~grade 6–8). A clarity proxy, not persuasion. *(English-centric.)*
- **KeyBERT** (MIT) + **ml6team/keyphrase-extraction-kbir-inspec** (MIT) — unsupervised + supervised keyword extraction for SEO briefs/titles/meta (no SERP volume data).
- **humanizer** (`blader/humanizer`, **MIT**) — a **prompt-only** skill (~33 AI-writing tells drawn from Wikipedia's "Signs of AI writing") that audits and strips AI-isms from copy in a two-pass pass, and — fed a writing sample — **rewrites to match your voice** instead of generic "clean" prose. Run it as a **de-tell lint** over any landing/ad/email/post before ship. **Honest limits:** it's a heuristic instruction set, **not a detector-evasion guarantee** — "humanized" text can still trip GPTZero/Originality, so never pitch it as *beating detectors*; the real cure for AI-slop is a genuine voice, and this only nudges toward it (output quality tracks the host model). Overlaps `fabius-parcus`'s strip-the-bloat trim and `fabius-disciplina`'s writing craft.

## HF models — sentiment & summarization

| Model (HF id) | License | Note |
|---|---|---|
| **cardiffnlp/twitter-roberta-base-sentiment-latest** | CC-BY-4.0 | 3-class sentiment tuned on social/marketing text — channel-listening. Commercial OK **with attribution**. |
| **nlptown/bert-base-multilingual-uncased-sentiment** | MIT | Multilingual (EN/NL/DE/FR/ES/IT) 1–5-star *product-review* sentiment — the multilingual gap the Twitter model can't cover; no attribution. |
| **facebook/bart-large-cnn** | MIT | Abstractive summarization → first-draft meta descriptions / social blurbs. News-biased, ~1024-token cap — **always human-edit**. **sshleifer/distilbart-cnn-12-6** (Apache) is the lighter at-scale option. |

*(Avoid **YAKE** for a proprietary pipeline — it's AGPL-3.0.)*

## Pairs with

`fabius-mercatus` (the message — positioning + copy — is the point; these measure/distribute it), **Fabius Yisrael** (Israeli email/SMS campaign compliance — Chok HaSpam), `fabius-decor` (the landing page's visual build), and `fabius-parcus` (Umami/one-script-tag over a heavy stack when a small site is all you have).
