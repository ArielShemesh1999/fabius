<!-- © 2026 shear559 · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->
<!-- fabius-release: 2.6.5 -->
# The fabius benchmark

One dated benchmark, with its misses intact: **Panel A improved three of four measured Claude tiers while shortening all four; Panel B's historical model-operated executed-code score records tied at ceiling and its model-graded factual-check track improved; Panel C recorded positive blind-judge demos across four external families; Panel D contains both gains and regressions.**

One test, four panels, one canonical aggregate: [`evals/results.benchmark.json`](evals/results.benchmark.json). Every published number came from a named run, but the historical evidence is not complete: v5/v6/v7 retain scores rather than candidate answers; v6 omits generated files and raw stdout/stderr; Panel C's raw portable receipt was never committed. A rerun creates a new measurement on moving endpoints — it cannot reconstruct those missing artifacts. `node evals/verify-receipts.mjs` deterministically replays every aggregate the committed score receipts can support and refuses silent drift. Panel D executes the evaluation contract of [IDENTITY.md](IDENTITY.md) on the versioned **Fabius Benchmark Suite** (`evals/suite/`, FBS v1.0) with **BASE → FAB → FAB_MEMORY**.

## The three arms

Every task in every panel is answered three ways:

- **`baseline`** — the task only.
- **`terse`** — the task + a generic *"Be concise. Write minimal code."* line. **This is the real test.** Beating a bare model is easy; the control isolates fabius's *structure* (the YAGNI ladder, the never-trim guardrails, the routed specialist contracts) from plain brevity.
- **`fabius`** — the task + the **shipped `AGENTS.md` stance and the routed specialist's `SKILL.md` contract, verbatim** — the actual files the agent ships, not a paraphrase.

The honest miss is printed, not hidden: Panel B's mixed score rises on every model because its model-graded checklist track rises; its executed-code track is tied. On Panel A three of four tiers gain and Haiku dips overall, with further category regressions visible in the receipt.

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

1. **Output fell 20% to 35% on each of these four measured models.** This is a dated panel result, not an every-model guarantee.
2. **On the measured Fable 5, Opus 4.8, and Sonnet 5 rows, fabius beats *both* the bare model *and* the "be concise" control** while cutting output ~20–34%. On Sonnet 5 the lift (**+0.43**) is the largest of the four tiers.
3. **Where a specialist contract is routed, the lift is large even on the smallest model.** Split Haiku's tasks by kind: on its **twelve specialist tasks the average delta is +0.71** — security route **9.0 → 14.5**, on-chain SPL balance **10.5 → 14.5**, CSS **12.5 → 14.0**, ML ship-decision **13.0 → 14.0**. The contract adds real domain rigor a small model doesn't supply on its own. (The full per-domain `byCat` table is in the receipt.)

**The honest miss, and why it's instructive.** Haiku's overall −0.33 is driven by its **three trivial one-liner tasks**, where its average delta is **−4.50**. The category table also records negative pooled deltas for build, accessibility and game tasks. Those observations support testing a leaner route; they do not prove the router fixes the regression. The receipt has every score cell, but not the original answer text.

Raw data: [`evals/results.v5.json`](evals/results.v5.json).

---

## Panel B — Mixed historical verification: model-operated execution + model-graded factual checks

Panel A ends in a blind quality score. Panel B changes the rubric, but the historical run did **not** remove models from verification. Four code tasks were extracted, written, executed and reported by a tool-using Workflow agent against hidden tests. Five domain deliverables (SQL route, RNA-seq, Solana, webhook, threat-model) were interpreted against fixed factual checklists by two model graders. The current harness replaces the code operator with a deterministic local runner and preserves answers, hashes, stdout/stderr and individual votes; the 2026-07-02 receipt predates that evidence schema.

Mixed score = deterministic test pass rate + model-graded checklist pass rate:

| Model | baseline | "be concise" control | **fabius** | Δ vs baseline | output cut |
|---|---|---|---|---|---|
| Haiku 4.5 | 75.6% | 76.7% | **93.0%** | **+17.4** | −25% |
| Opus 4.8 | 84.9% | 83.7% | **90.7%** | **+5.8** | −24% |
| **Sonnet 5** | 84.9% | 82.6% | **90.7%** | **+5.8** | −22.9% |
| Fable 5 | 87.2% | 80.2% | **90.7%** | **+3.5** | −12% |

The split between the two tracks is the whole story:

| Track | what it measures | haiku | sonnet | opus | fable |
|---|---|---|---|---|---|
| **Executed algorithm code** | reported hidden-test pass rate | 100 → **100** | 100 → **100** | 100 → **100** | 100 → **100** |
| **Domain deliverables** | model-graded factual-checklist % | 58 → **88** | 74 → **84** | 74 → **84** | 78 → **84** |

- **On pure algorithmic code the historical score records are tied at 100%.** Because v6 did not retain source files or stdout/stderr, this is a reported score rather than an independently replayable execution receipt.
- **On domain deliverables the two model graders marked more fixed checklist items present.** That is useful model-mediated evidence, not a deterministic correctness proof (baseline → fabius, all models pooled):

```
SQL route (parameterized query, not string-concat)   67.5%  ->  100.0%  +32.5  ← real injection risk removed
webhook   (idempotency, auth, retry, secret-in-env)  40.0%  ->   67.5%  +27.5
Solana    (account exists/owner/mint validation)     47.5%  ->   57.5%  +10.0  ← untrusted-input money safety
RNA-seq / threat-model                                100%  ->    100%  (already at ceiling)
```

**Which mixed score rises, and how much.** Haiku +17.4, Opus +5.8, Sonnet 5 +5.8, Fable +3.5, with 12–25% less output. The executed-code component contributes zero lift; all measured lift is in the model-graded factual-check component. That distinction is part of the result.

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

**All four published family aggregates are positive.** The aggregate receipt reports these per-task cells (fabius − control, /15):

| Task | category | Grok | Mistral | GPT | Claude |
|---|---|---|---|---|---|
| A1 migration | trust/order | +7 | +4 | +6 | +6 |
| A2 upload | trust/security | +7 | +5 | +5 | +7 |
| B1 exporter | YAGNI | +1 | +2 | +1 | +1 |
| B2 USD format | YAGNI | 0 | 0 | 0 | 0 |
| C1 rate limiter | genuine build | +8 | +1 | +6 | +6 |
| C2 CSV parser | genuine build | +9 | +4 | +8 | +8 |

The committed aggregate reports the same shape in each family: larger positive cells at trust/order/build boundaries and ~zero on pure YAGNI. Because the raw portable receipt and answer text were not committed, this is a dated reported pattern, not independently replayable proof of the mechanism.

> **Gemini** is wired in the harness (`GEMINI_API_KEY=... python evals/portable_eval.py --models gemini`) — no number is committed without a key. This doc publishes nothing it didn't measure.

Historical raw receipt: **not committed**. A new run writes `evals/results.portable.json`, but cannot reconstruct the published 2026-06-22 answers.

---

## Panel D — the FBS run: BASE → FAB → FAB_MEMORY on the versioned suite

Panel D executes the evaluation contract fixed in [IDENTITY.md](IDENTITY.md): does the exact same model achieve better outcomes with less waste? The **Fabius Benchmark Suite** has 100 production-shaped tasks — 20 smoke / 50 core / 30 stress across A–J — each with 3–6 fixed factual checks and, where memory matters, a committed snapshot. Modes: **BASE** · **FAB** · **FAB_MEMORY**. Two blind model judges score the seven-dimension rubric; another model grader interprets the fixed factual checks from answer text. Run 2026-07-05.

**Sonnet 5 — the full 100-task suite:**

| Mode | rubric /28 | model-graded factual checks | mean output | vs BASE |
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

1. **On the measured fast-tier aggregate the two layers stack monotonically.** Haiku's model-judged rubric rises +0.73 from the stance and another +0.73 from memory — +1.46 total on ~11–14% less output, with single-task jumps like **13.5 → 25.5** and **16.0 → 24.5**. These are score-receipt observations; the missing answer text prevents independent re-judgment.
2. **On the mid tier, the rubric holds near 93% while output falls 10–12%.** By tier: smoke **+0.55 (FAB) / +1.33 (FAB_MEMORY)**; stress **+0.50 (FAB)** with the model-graded factual-check rate up **89.9% → 93.7%**. The core tier is the honest miss: FAB_MEMORY −0.60; FAB reads −0.48 until you look at the receipt —
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
| Recursive discovery finds exactly those fifteen contracts and no nested `SKILL.md` | **PASS** |
| Frontmatter `name` matches directory; declares `name` + `description` | **PASS** |
| Every flattened frontmatter `description` ≤ 1024 bytes (discovery budget) | **PASS** |
| Frontmatter key policy — canonical keys only; `description` + `when_to_use` ≤ 1536 bytes flattened; `license` / `metadata.author` coherent when declared | **PASS** |
| Progressive disclosure — every `SKILL.md` ≤ 12000 B (depth lives in `references/`) | **PASS** (maximum and headroom are computed in live output) |
| Provenance `fab1-` fingerprint embedded in all 15 contracts | **PASS** |
| Reference integrity — every linked **and backtick-quoted** `references/` path resolves | **PASS** |
| Plugin manifest skill list == recursive discovery set; version is valid semver (`2.6.5`) | **PASS** |
| No sealed-set drift — seal-manifest file list == skills on disk + ARCHITECTURE/CORPUS/AGENTS | **PASS** |
| Content-bound seal — 18 sealed files hash-match + Merkle root recomputes | **PASS** |
| Count coherence — README / ARCHITECTURE / AGENTS all state "fifteen" | **PASS** |

All structural invariants pass once the seal is recomputed; the command derives and prints the current count. This is the structural complement to the behavioral panels: it proves the declared install surface, budgets, references and content-bound seal, not behavioral quality.

---

## The mechanism — why the structure should help

Each fabius rule counters a *documented* default tendency of current code models:

| Common model default | The fabius rule that counters it |
|---|---|
| Over-explains; adds unrequested boilerplate; hedges | Lean output + the YAGNI ladder + surgical changes |
| Over-engineers an under-specified task (a framework for one flag) | The ladder's first rung: *does this need to exist at all?* |
| Concise models that skip guardrails (validation, a11y, error handling) | The never-trim list — non-negotiable |
| Builds *too little* when lean-naive is wrong (in-memory limiter, `split(',')`) | "Strike narrow" = the *correct* lean rung, not the smallest |

A good result is shorter answers that survive stronger verification. Here, Panel B's SQL checklist moved from 67.5% to 100% under model grading; it is directional evidence that needs answer-level replay before it can be called deterministic proof.

---

## What this does and doesn't test

- **Panel A tests: does injecting the shipped files, verbatim, improve blind-model-judged quality on this dated Claude roster?** Fable 5, Sonnet 5, and Opus 4.8 beat both controls; Haiku falls overall while its specialist-task subset rises. Output drops 20–35% on all four rows. The regression motivates testing model-tier routing and a leaner route; it does not prove either mechanism fixes it.
- **Panel B tests two different things.** Historical executed-code score records tie at 100% but lack replayable artifacts. Two model graders mark more factual checklist items in the fabius domain answers. The combined score rises +3.5 to +17.4; that is not equivalent to a judge-free correctness gain.
- **Panel C reports cross-family demos outside the Claude family.** Its four published genuine-build aggregates are positive vs the "be concise" control (Grok +8.5, GPT +7.0, Claude +7.0, Mistral +2.5), but the absent raw receipt prevents independent replay or answer-level verification.
- **The structural suite tests: is the declared system built right** (recursive install surface, ownership, budgets, references, seal). Its live output derives the invariant count.
- **Panel D tests the same-model outcome/waste contract through model grading plus deterministic length.** The fast-tier rubric rises (+0.73 stance, +1.46 with memory) on 11–14% less output. On the mid tier the rubric stays near 93% on 10–12% less output, with explicit core-tier and memory regressions. This is directional, not an objective oracle.
- **Not tested by a one-shot benchmark:** cross-session memory accumulation (Panel D's snapshots are committed fixtures, not a live growing store), the `fabius` router's dispatch accuracy (checked structurally, not behaviorally), and the cross-model `fabius-concilium` layer (its proper test is whether a council beats its best single seat — a measurement to add, not a claim to make here).

Caveats, plainly: Panel A and Panel C are model-judged; Panel B's checklist half and its historical execution operator are model-mediated; Panel D's automatic checks are interpreted from answer text by a model grader. Character counts are deterministic. Historical receipts retain scores, not answers; Panel C retains only aggregates. Treat sub-point deltas as ties and every roster as dated. A rerun is a new result, not recovery of missing evidence.

---

## Reproduce it (one command per panel)

```bash
# Panel A — quality, four Claude tiers (roster current at the run), shipped files verbatim, two blind judges
#   (inside Claude Code)            -> evals/results.v5.json
Workflow({ scriptPath: "evals/harness.v5.workflow.js" })

# Panel B — deterministic local code execution + model-graded fixed factual checklists
#   (inside Claude Code)            -> evals/results.v6.json
Workflow({ scriptPath: "evals/harness.v6.workflow.js" })

# Panel C — external families, your keys (OpenAI / Grok-compatible / Mistral / Anthropic / Gemini)
OPENAI_API_KEY=... XAI_API_KEY=... MISTRAL_API_KEY=... GEMINI_API_KEY=... python evals/portable_eval.py

# Panel D — the FBS run: validate the committed suite, then execute BASE/FAB/FAB_MEMORY
#   (inside Claude Code)            -> evals/results.v7.json
node evals/suite/validate.mjs
Workflow({ scriptPath: "evals/harness.v7.workflow.js", args: { tasks: [/* evals/suite/*.jsonl */], model: "sonnet" } })

# Structural suite + committed-receipt replay — no key, no cost, no network
node evals/structural.mjs
node evals/verify-receipts.mjs

# Whole development artifact (versions, package truth, provenance, runtime, receipts)
bash scripts/verify-all.sh --mode=dev
```

The canonical consolidated receipt is [`evals/results.benchmark.json`](evals/results.benchmark.json). New harness runs use richer answer/evidence schemas, but they do not retroactively fill historical gaps. Add tasks, raise n, swap judges, and preserve content-addressed answers and execution artifacts.

---

## Appendix — raw receipts

The benchmark above is one test. This table inventories what survives. “Raw” means the lowest-level committed score rows available here; it does not imply original answer text or execution logs.

| Date | What was measured | Raw file |
|---|---|---|
| — | In-repo three-tier eval, `AGENTS.md` read verbatim, 8 tasks × 3 arms, blind judge | `evals/eval.mjs` → `evals/results.json` (written on run, gitignored) |
| 2026-06-22 | Cross-family three-arm stance test on Grok / Mistral / GPT / Claude, blind cross-family judging — **Panel C** | Raw `results.portable.json` was not committed; only aggregate lifts survive. Not independently replayable. |
| — | Live three-build landing-page comparison (stance-only vs none vs full mechanism) | no JSON receipt (live builds) |
| 2026-06-25 | Specialist-domain coverage: 13 tasks across 11 domains × 3 arms × 2 tiers, condensed contract transcriptions, blind Opus judge | [`evals/results.v3.json`](evals/results.v3.json) |
| 2026-06-25 | Extension of the above to the two later verticals (`doctrina` ML-eval, `fortuna` markets), same method | `evals/harness.v3-ext.workflow.js` |
| 2026-07-01 | The four Claude models current on that date × 15 tasks × 3 arms, shipped files verbatim, two blind judges — **Panel A score rows** | [`evals/results.v5.json`](evals/results.v5.json); no candidate answers |
| 2026-07-02 | Model-operated code execution + model-graded fixed checklists, 9 × 4 × 3 — **Panel B score rows** | [`evals/results.v6.json`](evals/results.v6.json); no candidate source/stdout or individual votes |
| 2026-07-02 | Consolidation of the three panels into the single canonical receipt | [`evals/results.benchmark.json`](evals/results.benchmark.json) |
| 2026-07-05 | **The FBS run** — 100 tasks BASE → FAB → FAB_MEMORY on Sonnet 5 + Haiku smoke, two blind judges + a model factual-check grader — **Panel D score rows** | [`evals/results.v7.json`](evals/results.v7.json); no candidate answers or check evidence |

> The claim these receipts support: **on the dated Panel A roster, fabius improved three of four tiers while shortening all four; Panel B's model-graded factual checks improved while executed-code scores tied; Panel C recorded positive aggregate demos across four families but lacks its raw receipt; Panel D contains small gains and explicit regressions. The deterministic structural and receipt gates verify artifact coherence, not universal model quality.**
