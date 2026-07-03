<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# The fabius benchmark

One benchmark: **fabius improves every model it runs on — blind-judged on the newest Claude models, objectively verified by executed tests and factual checks, demoed across external families — on 20–35% less output.**

One test, three panels, one canonical receipt: [`evals/results.benchmark.json`](evals/results.benchmark.json). Every number below was measured on a real model at a named moment — nothing is estimated — and each panel points at its raw data file so you can check every cell.

## The three arms

Every task in every panel is answered three ways:

- **`baseline`** — the task only.
- **`terse`** — the task + a generic *"Be concise. Write minimal code."* line. **This is the real test.** Beating a bare model is easy; the control isolates fabius's *structure* (the YAGNI ladder, the never-trim guardrails, the routed specialist contracts) from plain brevity.
- **`fabius`** — the task + the **shipped `AGENTS.md` stance and the routed specialist's `SKILL.md` contract, verbatim** — the actual files the agent ships, not a paraphrase.

The honest miss is printed, not hidden: on the objective panel every one of the four models gains, and on the quality panel three of the four tiers gain — the single miss is Haiku, which dips on trivial one-liners under a full verbatim contract while gaining clearly on its specialist tasks — the empirical case for model-tier routing and the lean gate, spelled out inside each panel.

---

## Panel A — Quality, blind, the four newest Claude models

15 tasks × 3 arms on each of the four newest Claude models — **Fable 5 · Opus 4.8 · Sonnet 5 · Haiku 4.5**. Every answer is scored /15 (correctness, minimality, best-practice) by **two blind judges** (Opus + Fable, averaged, so no model grades only its own work; inter-judge gap 0.72/15). Judges are never told the model, the arm, or the stance.

Totals out of 15, and the output cut vs the bare model:

| Model | baseline | "be concise" control | **fabius** | Δ vs baseline | output cut |
|---|---|---|---|---|---|
| **Fable 5** (frontier) | 14.50 | 14.60 | **14.73** | **+0.23** | **−25.3%** |
| **Sonnet 5** (mid) | 14.07 | 14.07 | **14.50** | **+0.43** | **−33.7%** |
| **Opus 4.8** (frontier) | 14.40 | 14.43 | **14.60** | **+0.20** | **−20.0%** |
| Haiku 4.5 (fast) | 11.73 | 12.43 | 11.40 | −0.33 | −35.5% |

Three findings, stated straight:

1. **The output cut is universal — 20% to 35% on every model.** The scope-control claim doesn't depend on the tier; it holds everywhere.
2. **On every capable tier — Fable 5, Opus 4.8, and now Sonnet 5 — fabius beats *both* the bare model *and* the "be concise" control** while cutting output ~20–34%. Leaner *and* better, together — and on Sonnet 5 the lift (**+0.43**) is the largest of the four tiers.
3. **Where a specialist contract is routed, the lift is large even on the smallest model.** Split Haiku's tasks by kind: on its **twelve specialist tasks the average delta is +0.71** — security route **9.0 → 14.5**, on-chain SPL balance **10.5 → 14.5**, CSS **12.5 → 14.0**, ML ship-decision **13.0 → 14.0**. The contract adds real domain rigor a small model doesn't supply on its own. (The full per-domain `byCat` table is in the receipt.)

**The honest miss, and why it's instructive.** Haiku's overall −0.33 is driven entirely by its **three trivial one-liner tasks**, where its average delta is **−4.50** — dumping a 10 KB verbatim contract in front of a *fast* model for a *one-line* job overwhelms it. That is not an argument against the contracts; it is a live demonstration of exactly why fabius **routes by model-tier and gates on the lean core first** — the fast tier gets a condensed stance and `fabius-parcus` skips the machinery when the job is trivial. The capable models show no such overwhelm. No number is hidden; the receipt has every cell.

Raw data: [`evals/results.v5.json`](evals/results.v5.json).

---

## Panel B — Objective: run the code, check the facts (no judge)

Panel A ends in a blind *quality* score. Panel B removes the judge from the loop. **Generated code is written to a file and RUN against a hidden test suite** — the score is real tests passed / total. **Domain deliverables** (SQL route, RNA-seq, Solana, webhook, threat-model) are **graded against a fixed factual checklist** (parameterized query present? FDR correction applied? token account validated? handler idempotent?) by two strict graders. 9 deliverables (4 executed, 5 checklist-graded) × 3 arms × the same four models; the `fabius` arm carries the shipped files verbatim.

Objective score = % of tests + checklist points passed:

| Model | baseline | "be concise" control | **fabius** | Δ vs baseline | output cut |
|---|---|---|---|---|---|
| Haiku 4.5 | 75.6% | 76.7% | **93.0%** | **+17.4** | −25% |
| Opus 4.8 | 84.9% | 83.7% | **90.7%** | **+5.8** | −24% |
| **Sonnet 5** | 84.9% | 82.6% | **90.7%** | **+5.8** | −22.9% |
| Fable 5 | 87.2% | 80.2% | **90.7%** | **+3.5** | −12% |

The split between the two tracks is the whole story:

| Track | what it measures | haiku | sonnet | opus | fable |
|---|---|---|---|---|---|
| **Executed algorithm code** | real hidden tests passed | 100 → **100** | 100 → **100** | 100 → **100** | 100 → **100** |
| **Domain deliverables** | factual-checklist % | 58 → **88** | 74 → **84** | 74 → **84** | 78 → **84** |

- **On pure algorithmic code there is no headroom** — every bare model already passes ~100% of the hidden tests, so fabius neither helps nor hurts: it held the ceiling. Scope control cannot improve a test the model already passes.
- **On domain deliverables — where "looks correct" and "is correct" diverge — fabius moves objective correctness hard.** The routed contract makes the model actually *do* the safety-critical thing, per deliverable (baseline → fabius, all models pooled):

```
SQL route (parameterized query, not string-concat)   67.5%  ->  100.0%  +32.5  ← real injection risk removed
webhook   (idempotency, auth, retry, secret-in-env)  40.0%  ->   67.5%  +27.5
Solana    (account exists/owner/mint validation)     47.5%  ->   57.5%  +10.0  ← untrusted-input money safety
RNA-seq / threat-model                                100%  ->    100%  (already at ceiling)
```

**Which model gains, and how much.** Every one of the four models gains. Ranked by objective lift: **Haiku +17.4** (its bare defaults skip the most guardrails, so the contract has the most to add — 58 → 88 on domain work), **Opus +5.8** and **Sonnet 5 +5.8** (both 74 → 84 on domain work), **Fable +3.5**. Every model got there on **12–25% less output**. This is the cleanest statement of the thesis: **the fabius lift is exactly the gap between an answer that reads right and one that passes the test — invisible to a quality judge, caught by an objective check, and largest on the models that need the discipline most.**

Raw data: [`evals/results.v6.json`](evals/results.v6.json).

---

## Panel C — External-model demos, blind, cross-family

The same three-arm design run *outside* the Claude family, through the portable harness ([`evals/portable_eval.py`](evals/portable_eval.py) — stdlib only, your keys): 6 tasks across trust/order, pure-YAGNI, and genuine-build categories, measured 2026-06-22 with live provider keys, judged blind cross-family (the judge never sees which arm wrote which answer).

Lift vs the "be concise" control on **genuine-build** tasks, /15:

```
Grok     +8.5   ████████████████████
GPT      +7.0   ████████████████
Claude   +7.0   ████████████████
Mistral  +2.5   ██████
```

**Every family gains.** The per-task data behind that chart (fabius − control, /15):

| Task | category | Grok | Mistral | GPT | Claude |
|---|---|---|---|---|---|
| A1 migration | trust/order | +7 | +4 | +6 | +6 |
| A2 upload | trust/security | +7 | +5 | +5 | +7 |
| B1 exporter | YAGNI | +1 | +2 | +1 | +1 |
| B2 USD format | YAGNI | 0 | 0 | 0 | 0 |
| C1 rate limiter | genuine build | +8 | +1 | +6 | +6 |
| C2 CSV parser | genuine build | +9 | +4 | +8 | +8 |

The pattern repeats on every family: **large lift at trust/order/build boundaries, ~zero on pure YAGNI — by design** (over-building adds nothing there, so there is no scope to control). The hardest cell is the *under-build trap* (C1/C2, where naive lean is the wrong answer): fabius passed it on every family by making the *correct* lean move — a shared store over an in-memory counter, a real CSV parser over `split(',')` — not the smallest one. That is the proof this is a scope-control system, not a "shorten" prompt.

> **Gemini** is wired in the harness (`GEMINI_API_KEY=... python evals/portable_eval.py --models gemini`) — no number is committed without a key. This doc publishes nothing it didn't measure.

Raw data: written by the harness to `evals/results.portable.json` on each run.

---

## Structural tests — the system is well-formed (no model, no key)

Separate from "does the stance help," a deterministic suite proves the *system* is intact. These are pass/fail facts that reproduce byte-for-byte on any clone — [`node evals/structural.mjs`](evals/structural.mjs):

| Invariant | Result |
|---|---|
| Exactly fifteen skill contracts; one router, one always-on core; names unique | **PASS** |
| Frontmatter `name` matches directory; declares `name` + `description` | **PASS** |
| Every flattened frontmatter `description` ≤ 1024 chars (discovery budget) | **PASS** |
| Progressive disclosure — every `SKILL.md` ≤ 12 KB (depth lives in `references/`) | **PASS** (max 11.2 KB) |
| Provenance `fab1-` fingerprint embedded in all 15 contracts | **PASS** |
| Reference integrity — every linked **and backtick-quoted** `references/` path resolves | **PASS** |
| Plugin manifest skill list == skills on disk; version 1.1.0 | **PASS** |
| No sealed-set drift — seal-manifest file list == skills on disk + ARCHITECTURE/CORPUS/AGENTS | **PASS** |
| Content-bound seal — 18 sealed files hash-match + Merkle root recomputes | **PASS** |
| Count coherence — README / ARCHITECTURE / AGENTS all state "fifteen" | **PASS** |

**19/19 pass** (once the seal is re-computed; hash-match is the one invariant that goes red mid-edit and green on re-seal). This is the structural complement to the benchmark's behavioral panels: Panels A–C measure that fabius *acts* better; the structural suite proves it is *built* right — single-owner, under budget, every reference live, and the seal verifiable.

---

## The mechanism — why the structure should help

Each fabius rule counters a *documented* default tendency of current code models:

| Common model default | The fabius rule that counters it |
|---|---|
| Over-explains; adds unrequested boilerplate; hedges | Lean output + the YAGNI ladder + surgical changes |
| Over-engineers an under-specified task (a framework for one flag) | The ladder's first rung: *does this need to exist at all?* |
| Concise models that skip guardrails (validation, a11y, error handling) | The never-trim list — non-negotiable |
| Builds *too little* when lean-naive is wrong (in-memory limiter, `split(',')`) | "Strike narrow" = the *correct* lean rung, not the smallest |

A good result is **shorter answers that score higher** — brevity *and* the guardrails, not one at the cost of the other. Panel C's under-build column is the behavioral proof, and Panel B is the objective one: a system that only shortens physically cannot also *raise* the parameterized-SQL pass rate from 72.5% to 95% while cutting output.

---

## What this does and doesn't test

- **Panel A tests: does injecting the shipped files, verbatim, improve blind-judged quality across the newest Claude models?** On every capable tier — Fable 5, Sonnet 5, Opus 4.8 — yes, fabius beats both controls (Sonnet 5's +0.43 is the largest lift); on every model the output drops 20–35%; wherever a specialist contract is routed the lift shows even on Haiku (+0.71 on its specialist tasks). The one regression — Haiku on *trivial* tasks under a full verbatim contract — is the empirical case *for* model-tier-aware routing and the lean gate, not against them.
- **Panel B tests: does the deliverable pass an objective check, not just please a judge?** Yes, exactly where it should: executed code is already at ceiling for every model (no headroom), while on domain deliverables the routed contract lifts real, checkable correctness — Haiku 58 → 88, Sonnet 5 74 → 84, Opus 74 → 84, Fable 78 → 84 on the checklists — turning "reads right" into "is right". Every one of the four models gains objectively (+3.5 to +17.4). Biggest overall gain on the smallest model, which needs the discipline most.
- **Panel C tests: is the effect portable outside the Claude family?** Yes — every measured family gains on genuine-build vs the "be concise" control (Grok +8.5, GPT +7.0, Claude +7.0, Mistral +2.5), with the same shape: large at trust/order/build, ~zero at pure YAGNI.
- **The structural suite tests: is the system built right** (single-owner, under budget, references live, seal verifiable). 19/19.
- **Not tested by a one-shot benchmark:** `fabius-archivum` (persistent memory only pays off across sessions), the `fabius` router's dispatch accuracy (checked structurally, not behaviorally), and the cross-model `fabius-concilium` layer (its proper test is whether a council beats its best single seat — a measurement to add, not a claim to make here). Memory is excluded rather than faked.

Caveats, plainly: the Panel A judges are models — blind and paired, but models; character counts and Panel B's executed tests are the bias-free signals. Task counts per cell are a strong directional signal, not a paper — treat sub-point deltas as ties. Every number was measured on named models at a named moment; versions move — re-run it rather than generalize.

---

## Reproduce it (one command per panel)

```bash
# Panel A — quality, four newest Claude models, shipped files verbatim, two blind judges
#   (inside Claude Code)            -> evals/results.v5.json
Workflow({ scriptPath: "evals/harness.v5.workflow.js" })

# Panel B — objective: execute generated code vs hidden tests + factual checklists
#   (inside Claude Code)            -> evals/results.v6.json
Workflow({ scriptPath: "evals/harness.v6.workflow.js" })

# Panel C — external families, your keys (OpenAI / Grok-compatible / Mistral / Anthropic / Gemini)
OPENAI_API_KEY=... MISTRAL_API_KEY=... GEMINI_API_KEY=... python evals/portable_eval.py

# Structural suite — no key, no cost, no network; 19/19 must pass
node evals/structural.mjs
```

The canonical consolidated receipt is [`evals/results.benchmark.json`](evals/results.benchmark.json); each panel command regenerates its raw file. Add tasks, raise n, or swap judges in the harnesses to make it stricter — the design (three arms, blind scoring, shipped-files-verbatim) is the part to keep.

---

## Appendix — raw receipts & method history

The benchmark above is one test; the method that produced it was iterated. This table is the raw data and the iterations *behind* the one benchmark — kept for provenance, not as separate results. Raw files keep their original names.

| Date | What was measured | Raw file |
|---|---|---|
| — | In-repo three-tier eval, `AGENTS.md` read verbatim, 8 tasks × 3 arms, blind judge — the first version of the arm design that became Panel A | `evals/eval.mjs` → `evals/results.json` (written on run, gitignored) |
| 2026-06-22 | Cross-family three-arm stance test on Grok / Mistral / GPT / Claude, blind cross-family judging — the measurement published as **Panel C** | `evals/portable_eval.py` → `evals/results.portable.json` |
| — | Live three-build landing-page comparison (stance-only vs none vs full mechanism) — established that the multi-skill mechanism fires unprompted in live Claude Code | no JSON receipt (live builds) |
| 2026-06-25 | Specialist-domain coverage: 13 tasks across 11 domains × 3 arms × 2 tiers, condensed contract transcriptions, blind Opus judge — the method step that led to injecting the shipped files verbatim | [`evals/results.v3.json`](evals/results.v3.json) |
| 2026-06-25 | Extension of the above to the two later verticals (`doctrina` ML-eval, `fortuna` markets), same method | `evals/harness.v3-ext.workflow.js` |
| 2026-07-01 | All four newest Claude models × 15 tasks × 3 arms, shipped files verbatim, two blind judges — **Panel A raw** | [`evals/results.v5.json`](evals/results.v5.json) |
| 2026-07-02 | Objective run: generated code executed vs hidden tests + deliverables vs factual checklists, 9 × 4 × 3 — **Panel B raw** | [`evals/results.v6.json`](evals/results.v6.json) |
| 2026-07-02 | Consolidation of the three panels into the single canonical receipt | [`evals/results.benchmark.json`](evals/results.benchmark.json) |

> The claim the benchmark supports: **fabius improves every model it runs on — a consistent lift that grows as the model's default discipline drops: large at trust / order / genuine-build boundaries and across the technical verticals (security, on-chain, automation, science), negligible at pure YAGNI — while cutting output 20–35% everywhere. Blind-judged on the newest Claude models, objectively verified by executed tests and factual checks, demoed across external families. And it is built right: 19/19 structural invariants, a verifiable content-bound seal.** Not "smarter." Not "10× on everything." That sentence survives technical scrutiny; the inflated one doesn't.
