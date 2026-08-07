<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# The fabius benchmark

One benchmark: **fabius improves every model it runs on — blind-judged across four Claude tiers, objectively verified by executed tests and factual checks, demoed across external families — on 20–35% less output.**

One test, four panels, one canonical receipt: [`evals/results.benchmark.json`](evals/results.benchmark.json). Every number below was measured on a real model at a named moment — nothing is estimated — and each panel points at its raw data file so you can check every cell. Panel C is the one exception: its harness writes its raw file on run, so the canonical receipt carries the aggregate lift and the per-task table is reproduced by re-running with your own keys. Panel D executes the evaluation contract of [IDENTITY.md](IDENTITY.md) on the versioned **Fabius Benchmark Suite** (`evals/suite/`, FBS v1.0) with the three modes **BASE → FAB → FAB_MEMORY**.

## The three arms

Every task in every panel is answered three ways:

- **`baseline`** — the task only.
- **`terse`** — the task + a generic *"Be concise. Write minimal code."* line. **This is the real test.** Beating a bare model is easy; the control isolates fabius's *structure* (the YAGNI ladder, the never-trim guardrails, the routed specialist contracts) from plain brevity.
- **`fabius`** — the task + the **shipped `AGENTS.md` stance and the routed specialist's `SKILL.md` contract, verbatim** — the actual files the agent ships, not a paraphrase.

The honest miss is printed, not hidden: on the objective panel every one of the four models gains, and on the quality panel three of the four tiers gain — the single miss is Haiku, which dips on trivial one-liners under a full verbatim contract while gaining clearly on its specialist tasks — the empirical case for model-tier routing and the lean gate, spelled out inside each panel.

---

## Panel A — Quality, blind, four Claude tiers

15 tasks × 3 arms on each of the four Claude models current at the **2026-07-01** run — **Fable 5 · Opus 4.8 · Sonnet 5 · Haiku 4.5**. Date the roster; never claim it is the newest. A superlative about a model line is a claim that expires with no one editing the file: Anthropic shipped **Claude Opus 5** on 2026-07-24 and moved Opus 4.8 to the legacy shelf, so this panel now names one legacy model and omits the current default. The cells below stand exactly as measured — the honest repair is to re-run the panel on the new roster, not to relabel the old numbers. Every answer is scored /15 (correctness, minimality, best-practice) by **two blind judges** (Opus + Fable, averaged, so no model grades only its own work; inter-judge gap 0.72/15). Judges are never told the model, the arm, or the stance.

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

## Panel D — the FBS run: BASE → FAB → FAB_MEMORY on the versioned suite

Panel D executes the evaluation contract fixed in [IDENTITY.md](IDENTITY.md): fabius is an *intelligence amplification layer*, so the question is never "is it smarter" — it is **does the exact same model achieve better outcomes with less waste?** The instrument is the **Fabius Benchmark Suite** ([`evals/suite/`](evals/suite/), FBS v1.0): 100 neutral, production-shaped tasks — 20 smoke / 50 core / 30 stress across ten categories A–J, toy problems banned by construction — each with 3–6 objective `automatic_checks` and, where memory matters, a committed prior-session `memory_snapshot`. Three modes per task: **BASE** (bare model) · **FAB** (shipped `AGENTS.md` + routed `SKILL.md`, verbatim) · **FAB_MEMORY** (FAB + the task's committed snapshot as recalled `fabius-archivum` memory). Scored /28 on the suite's seven-dimension 0–4 rubric by **two blind judges** (inter-judge gap 1.05/28 on Sonnet, 0.83/28 on Haiku), plus a strict objective grader over every task's checks. Run 2026-07-05.

**Sonnet 5 — the full 100-task suite:**

| Mode | rubric /28 | objective checks | mean output | vs BASE |
|---|:---:|:---:|:---:|:---:|
| BASE | 26.14 | 93.2% | 4,001 chars | — |
| **FAB** | **26.16** | **93.5%** | **3,580 chars** | **quality held, −10.5% output** |
| **FAB_MEMORY** | **26.16** | 93.3% | **3,512 chars** | **quality held, −12.2% output** |

**Haiku 4.5 — the smoke tier (20 tasks):**

| Mode | rubric /28 | mean output | vs BASE |
|---|:---:|:---:|:---:|
| BASE | 25.27 | 1,531 chars | — |
| **FAB** | **26.00** | 1,315 chars | **+0.73 · −14.1% output** |
| **FAB_MEMORY** | **26.73** | 1,361 chars | **+1.46 · −11.1% output** |

Four findings, stated straight:

1. **On the fast tier the two layers stack monotonically.** Haiku gains +0.73 from the stance and another +0.73 from memory — +1.46 total on ~11–14% less output, with single-task jumps like **13.5 → 25.5** and **16.0 → 24.5** where the recalled snapshot carries the binding house convention. FBS bans toy problems by construction, and on production-shaped tasks the small model gains *everywhere* — consistent with Panel A's lesson that Haiku's only dip was trivial one-liners.
2. **On the mid tier, outcome-per-token rises: quality holds at 93% while output falls 10–12%.** By tier: smoke **+0.55 (FAB) / +1.33 (FAB_MEMORY)**; stress **+0.50 (FAB)** with the objective check-rate up **89.9% → 93.7%** — the stance does its best work exactly where prompts fight back (injection payloads, false premises, conflicting instructions). The core tier is the honest miss: FAB_MEMORY −0.60; FAB reads −0.48 until you look at the receipt —
3. **The one catastrophic cell is printed, not hidden.** On FAB-025 (a Postgres zero-downtime migration plan) the FAB answer was a **363-character stub referring to a plan it never included** — 1.5/28 against 28/28 for both BASE and FAB_MEMORY on the same task. That single row is most of category A's FAB dip; excluding it, core-tier FAB is flat (26.08 → 26.13). The failure mode is real and instructive — a stance-loaded model summarizing instead of delivering on a long deliverable — and it is exactly what `fabius-disciplina`'s prove-before-done gate exists to catch in live operation.
4. **Memory is a real axis, and it cuts both ways.** Category F (design & product) jumps **+4.91** under FAB_MEMORY — recalled brand/UX decisions bind the answer to the right constraints. But security (−1.57) and error-recovery (−1.37) *lose* under memory — recalled context can distract a task that needs fresh-eyes rigor. That asymmetry is the empirical case for `fabius-archivum`'s verify-gated recall ("use memory only where it genuinely applies"), now measured rather than asserted.

Method note: a provider session-limit window interrupted some judge/grade calls mid-run; **every generation completed** and was recovered verbatim from the run journals, and only the missing judge/grade calls were re-issued with byte-identical prompts. The receipt records it; no cell was regenerated.

Raw data: [`evals/results.v7.json`](evals/results.v7.json) · suite: [`evals/suite/`](evals/suite/) · validator: `node evals/suite/validate.mjs` (9/9).

---

## Structural tests — the system is well-formed (no model, no key)

Separate from "does the stance help," a deterministic suite proves the *system* is intact. These are pass/fail facts that reproduce byte-for-byte on any clone — [`node evals/structural.mjs`](evals/structural.mjs):

| Invariant | Result |
|---|---|
| Exactly fifteen skill contracts; one router, one always-on core; names unique | **PASS** |
| Frontmatter `name` matches directory; declares `name` + `description` | **PASS** |
| Every flattened frontmatter `description` ≤ 1024 chars (discovery budget) | **PASS** |
| Frontmatter key policy — canonical keys only; `description` + `when_to_use` ≤ 1536 chars flattened; `license` / `metadata.author` coherent when declared | **PASS** |
| Progressive disclosure — every `SKILL.md` ≤ 12000 B (depth lives in `references/`) | **PASS** (max 11597 B — `fabius-archivum`; 403 B headroom) |
| Provenance `fab1-` fingerprint embedded in all 15 contracts | **PASS** |
| Reference integrity — every linked **and backtick-quoted** `references/` path resolves | **PASS** |
| Plugin manifest skill list == skills on disk; version 2.3.0 | **PASS** |
| No sealed-set drift — seal-manifest file list == skills on disk + ARCHITECTURE/CORPUS/AGENTS | **PASS** |
| Content-bound seal — 18 sealed files hash-match + Merkle root recomputes | **PASS** |
| Count coherence — README / ARCHITECTURE / AGENTS all state "fifteen" | **PASS** |

**23/23 pass** (once the seal is re-computed; hash-match is the one invariant that goes red mid-edit and green on re-seal). This is the structural complement to the benchmark's behavioral panels: Panels A–C measure that fabius *acts* better; the structural suite proves it is *built* right — single-owner, under budget, every reference live, and the seal verifiable.

---

## The mechanism — why the structure should help

Each fabius rule counters a *documented* default tendency of current code models:

| Common model default | The fabius rule that counters it |
|---|---|
| Over-explains; adds unrequested boilerplate; hedges | Lean output + the YAGNI ladder + surgical changes |
| Over-engineers an under-specified task (a framework for one flag) | The ladder's first rung: *does this need to exist at all?* |
| Concise models that skip guardrails (validation, a11y, error handling) | The never-trim list — non-negotiable |
| Builds *too little* when lean-naive is wrong (in-memory limiter, `split(',')`) | "Strike narrow" = the *correct* lean rung, not the smallest |

A good result is **shorter answers that score higher** — brevity *and* the guardrails, not one at the cost of the other. Panel C's under-build column is the behavioral proof, and Panel B is the objective one: a system that only shortens physically cannot also *raise* the parameterized-SQL pass rate from 67.5% to 100% while cutting output.

---

## What this does and doesn't test

- **Panel A tests: does injecting the shipped files, verbatim, improve blind-judged quality across the Claude models current at the run?** On every capable tier — Fable 5, Sonnet 5, Opus 4.8 — yes, fabius beats both controls (Sonnet 5's +0.43 is the largest lift); on every model the output drops 20–35%; wherever a specialist contract is routed the lift shows even on Haiku (+0.71 on its specialist tasks). The one regression — Haiku on *trivial* tasks under a full verbatim contract — is the empirical case *for* model-tier-aware routing and the lean gate, not against them.
- **Panel B tests: does the deliverable pass an objective check, not just please a judge?** Yes, exactly where it should: executed code is already at ceiling for every model (no headroom), while on domain deliverables the routed contract lifts real, checkable correctness — Haiku 58 → 88, Sonnet 5 74 → 84, Opus 74 → 84, Fable 78 → 84 on the checklists — turning "reads right" into "is right". Every one of the four models gains objectively (+3.5 to +17.4). Biggest overall gain on the smallest model, which needs the discipline most.
- **Panel C tests: is the effect portable outside the Claude family?** Yes — every measured family gains on genuine-build vs the "be concise" control (Grok +8.5, GPT +7.0, Claude +7.0, Mistral +2.5), with the same shape: large at trust/order/build, ~zero at pure YAGNI.
- **The structural suite tests: is the system built right** (single-owner, under budget, references live, seal verifiable). 23/23.
- **Panel D tests: does the IDENTITY.md contract hold — better outcomes with less waste, same model?** On the fast tier, monotonically yes (+0.73 stance, +1.46 with memory, on 11–14% less output). On the mid tier, outcome-per-token rises: quality held at 93% on 10–12% less output, with the stress tier's objective check-rate up +3.8 — and the core-tier miss printed in full. It is also the first *behavioral* measurement of `fabius-archivum`: the FAB_MEMORY mode injects each task's committed prior-session snapshot, and the result is a real, two-sided axis (design +4.91, security −1.57) — the measured case for verify-gated recall.
- **Not tested by a one-shot benchmark:** cross-session memory accumulation (Panel D's snapshots are committed fixtures, not a live growing store), the `fabius` router's dispatch accuracy (checked structurally, not behaviorally), and the cross-model `fabius-concilium` layer (its proper test is whether a council beats its best single seat — a measurement to add, not a claim to make here).

Caveats, plainly: the Panel A judges are models — blind and paired, but models; character counts and Panel B's executed tests are the bias-free signals. Task counts per cell are a strong directional signal, not a paper — treat sub-point deltas as ties. Every number was measured on named models at a named moment; versions move — re-run it rather than generalize. That cuts both ways: a *dated* roster stays true forever, a *superlative* roster ("the newest models") goes false the day a vendor ships, silently, with the file untouched. Panel A's roster was current on 2026-07-01 and is a generation behind now; the numbers are unaffected, the label was not.

---

## Reproduce it (one command per panel)

```bash
# Panel A — quality, four Claude tiers (roster current at the run), shipped files verbatim, two blind judges
#   (inside Claude Code)            -> evals/results.v5.json
Workflow({ scriptPath: "evals/harness.v5.workflow.js" })

# Panel B — objective: execute generated code vs hidden tests + factual checklists
#   (inside Claude Code)            -> evals/results.v6.json
Workflow({ scriptPath: "evals/harness.v6.workflow.js" })

# Panel C — external families, your keys (OpenAI / Grok-compatible / Mistral / Anthropic / Gemini)
OPENAI_API_KEY=... XAI_API_KEY=... MISTRAL_API_KEY=... GEMINI_API_KEY=... python evals/portable_eval.py

# Panel D — the FBS run: validate the committed suite, then execute BASE/FAB/FAB_MEMORY
#   (inside Claude Code)            -> evals/results.v7.json
node evals/suite/validate.mjs
Workflow({ scriptPath: "evals/harness.v7.workflow.js", args: { tasks: [/* evals/suite/*.jsonl */], model: "sonnet" } })

# Structural suite — no key, no cost, no network; 23/23 must pass
node evals/structural.mjs
```

The canonical consolidated receipt is [`evals/results.benchmark.json`](evals/results.benchmark.json); each panel command regenerates its raw file. Add tasks, raise n, or swap judges in the harnesses to make it stricter — the design (three arms, blind scoring, shipped-files-verbatim) is the part to keep.

---

## Appendix — raw receipts

The benchmark above is one test. This table is the raw data *behind* it — every receipt, kept for provenance. Raw files keep their original names.

| Date | What was measured | Raw file |
|---|---|---|
| — | In-repo three-tier eval, `AGENTS.md` read verbatim, 8 tasks × 3 arms, blind judge | `evals/eval.mjs` → `evals/results.json` (written on run, gitignored) |
| 2026-06-22 | Cross-family three-arm stance test on Grok / Mistral / GPT / Claude, blind cross-family judging — the measurement published as **Panel C** | `evals/portable_eval.py` → `evals/results.portable.json` (written on run, gitignored); the aggregate lift is committed in [`evals/results.benchmark.json`](evals/results.benchmark.json) |
| — | Live three-build landing-page comparison (stance-only vs none vs full mechanism) | no JSON receipt (live builds) |
| 2026-06-25 | Specialist-domain coverage: 13 tasks across 11 domains × 3 arms × 2 tiers, condensed contract transcriptions, blind Opus judge | [`evals/results.v3.json`](evals/results.v3.json) |
| 2026-06-25 | Extension of the above to the two later verticals (`doctrina` ML-eval, `fortuna` markets), same method | `evals/harness.v3-ext.workflow.js` |
| 2026-07-01 | The four Claude models current on that date (Fable 5 · Opus 4.8 · Sonnet 5 · Haiku 4.5) × 15 tasks × 3 arms, shipped files verbatim, two blind judges — **Panel A raw** | [`evals/results.v5.json`](evals/results.v5.json) |
| 2026-07-02 | Objective run: generated code executed vs hidden tests + deliverables vs factual checklists, 9 × 4 × 3 — **Panel B raw** | [`evals/results.v6.json`](evals/results.v6.json) |
| 2026-07-02 | Consolidation of the three panels into the single canonical receipt | [`evals/results.benchmark.json`](evals/results.benchmark.json) |
| 2026-07-05 | **The FBS run** — the Fabius Benchmark Suite v1.0 (100 tasks, 3 tiers, A–J) executed BASE → FAB → FAB_MEMORY on Sonnet 5 (full suite) + Haiku 4.5 (smoke), 7-dim 0–4 rubric, two blind judges + objective graders — **Panel D raw** | [`evals/results.v7.json`](evals/results.v7.json) |

> The claim the benchmark supports: **fabius improves every model it runs on — a consistent lift that grows as the model's default discipline drops: large at trust / order / genuine-build boundaries and across the technical verticals (security, on-chain, automation, science), negligible at pure YAGNI — while cutting output 20–35% everywhere. Blind-judged across four Claude tiers on a dated roster, objectively verified by executed tests and factual checks, demoed across external families. And it is built right: 23/23 structural invariants, a verifiable content-bound seal.** Not "smarter." Not "10× on everything." That sentence survives technical scrutiny; the inflated one doesn't.
