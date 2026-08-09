# evals/

The measurement behind **the fabius benchmark** ([`../BENCHMARKS.md`](../BENCHMARKS.md)) — one test, four panels, one canonical receipt: [`results.benchmark.json`](results.benchmark.json). No estimated numbers — this folder is the receipt. Each harness below serves one of the benchmark's panels (or the structural suite); the supporting harnesses and raw receipts are listed below.

| File | What it is |
|---|---|
| `results.benchmark.json` | **THE canonical receipt** — the panels (A quality / B objective / C external demos / D the FBS run) consolidated, with per-panel pointers to the raw files below. Committed. |
| [`suite/`](suite/) | **The Fabius Benchmark Suite (FBS v1.0)** — the versioned evaluation framework from [`../IDENTITY.md`](../IDENTITY.md): 100 neutral tasks in three tiers (20 smoke / 50 core / 30 stress) across ten categories A–J, a fixed 7-dimension 0–4 rubric, three modes **BASE / FAB / FAB_MEMORY**, plus its own deterministic validator (`node evals/suite/validate.mjs`, 9/9). |
| `harness.v7.workflow.js` | **Panel D harness — the FBS run**: the committed suite × 3 modes; the FAB mode carries the shipped files verbatim, the FAB_MEMORY mode adds the task's committed memory snapshot as recalled `fabius-archivum` memory; **two blind judges** (Opus + Fable) on the 7-dim rubric + a strict objective grader per answer over the task's `automatic_checks`. |
| `results.v7.json` | **Panel D raw** — per-task 7-dimension scores per mode, automatic-check pass rates, per-tier and per-category aggregates, BASE→FAB→FAB_MEMORY deltas. Committed. |
| `structural.mjs` | The benchmark's **deterministic structural suite** — no model, no key, no network. Proves the *system* is well-formed: fifteen single-owner contracts, every `SKILL.md` under budget, every flattened `description` ≤ 1024 chars, frontmatter keys canonical (`description` + `when_to_use` ≤ 1536 chars flattened; `license` / `metadata.author` coherent when declared), every reference live (markdown links **and** backtick-quoted mentions), no sealed-set drift (manifest file list == on-disk set), the content-bound seal verifiable. 23/23 must pass (the seal hash-match goes red mid-edit, green on re-seal). `node evals/structural.mjs` |
| `harness.v5.workflow.js` | **Panel A harness** — quality, blind, the four Claude models current at the 2026-07-01 run: 15 tasks × 4 models × 3 arms with the shipped skill files injected **verbatim**, **two blind judges** (Opus + Fable, inter-judge gap 0.72/15). |
| `results.v5.json` | **Panel A raw** — per-cell scores from both judges, lengths, per-model and per-domain deltas. Committed. |
| `harness.v6.workflow.js` | **Panel B harness** — objective, no judge taste: generated code **executed against hidden test suites** + domain deliverables graded against a **factual checklist** by two strict graders. 9 deliverables × 4 models × 3 arms. |
| `results.v6.json` | **Panel B raw** — per-task pass rates (tests + checks) per cell. Committed. |
| `portable_eval.py` | **Panel C harness** — vendor-agnostic, stdlib only, no pip. Same 3-arm design against **OpenAI (GPT/Codex), Grok-compatible, Mistral, Anthropic, Gemini**, judged blind cross-family. Writes `results.portable.json` on run. |
| `harness.v3.workflow.js` | Supporting receipt — specialist-domain coverage: 13 tasks (one per specialist domain, incl. the on-chain / automation / science verticals) × 3 arms × 2 tiers, blind Opus judge, condensed contract transcriptions. |
| `harness.v3-ext.workflow.js` | Supporting receipt — the same method over the verticals `doctrina` (ML eval) + `fortuna` (trading backtest), so every specialist domain is exercised (the `fabius-concilium` layer deliberates across models, not a task domain — not yet in a blind run). |
| `results.v3.json` | Raw receipt for the specialist-coverage run — per-cell scores, length, per-domain deltas. Committed. |
| `harness.workflow.js` | Base Claude-Code harness. 3 arms × 6 tasks, blind Opus judge. Supporting receipt. |
| `eval.mjs` | Node harness — clean **no-system-prompt** API baseline (the strictest baseline). `--selftest` checks wiring with no key. The no-key selftest entry point of the arm design. |
| `results.json` | Raw output `eval.mjs` writes on a run — gitignored. |

## Structural suite (no key, no network)

```bash
node evals/structural.mjs            # 23/23 invariants — exits non-zero on any FAIL
node evals/structural.mjs --json     # also writes evals/structural.json
```

Behavioral runs ask *does fabius act better*; this asks *is fabius built right* — single-owner/zero-overlap, progressive-disclosure budgets, reference integrity, and the SHA-256 + Merkle content-bound seal, all recomputable from the repo files.

## Cross-vendor run (OpenAI / Mistral / your keys)

```bash
export OPENAI_API_KEY=...      # GPT/Codex family
export XAI_API_KEY=...         # grok family
export MISTRAL_API_KEY=...     # mistral-large-2512
export ANTHROPIC_API_KEY=...   # claude models
python3 evals/portable_eval.py            # runs every vendor whose key is set
python3 evals/portable_eval.py --models openai mistral   # subset
python3 evals/portable_eval.py --selftest # verify harness logic, no key needed
```

Writes `results.portable.json`. No fabrication — rows appear only for vendors you actually run.

## Design (three-arm, blind)

- **Arms:** `baseline` (task only) · `terse` (task + generic "be concise, write minimal code") · `fabius` (task + the fabius stance). The Panel A/B harnesses (`harness.v5` / `harness.v6`) and `eval.mjs` load the shipped `AGENTS.md` (+ routed `SKILL.md`) **verbatim**; the `harness.v3` coverage harness injects a faithful condensed transcription instead. The `terse` arm is the control that separates fabius's **structure** from plain brevity — the real test.
- **Modes (Panel D / FBS):** `BASE` (bare model) · `FAB` (shipped stance + routed contract, verbatim) · `FAB_MEMORY` (FAB + the task's committed memory snapshot injected as recalled `fabius-archivum` memory) — the three evaluation modes fixed in [`../IDENTITY.md`](../IDENTITY.md), scored on the suite's 7-dimension 0–4 rubric plus objective per-task automatic checks.
- **Models:** the four Claude models current at the 2026-07-01 run — Fable 5 (`claude-fable-5`), `claude-opus-4-8`, `claude-sonnet-5`, `claude-haiku-4-5` — each actually run via per-agent model override (Panel A/B). (Date the roster; never claim it is the newest — Opus 5 shipped 2026-07-24, after these runs.) Panel C carries the same arms cross-family (GPT / Grok / Mistral / Gemini) through `portable_eval.py`.
- **Judge:** Panel A uses **two** blind judges (Opus + Fable, averaged; inter-judge gap 0.72/15); the single-judge supporting harnesses used `claude-opus-4-8`, **blind** (never told which arm wrote which answer), scoring correctness / minimality / best-practice, 0–5 each. Panel B removes the judge entirely — executed tests + factual checklists.
- **Objective metric:** average output length (chars) — bias-free.

## Run it yourself

```
# Panel D — the FBS run (validate first, then execute the committed suite)
node evals/suite/validate.mjs
Workflow({ scriptPath: "evals/harness.v7.workflow.js", args: { tasks: [/* evals/suite/*.jsonl */], model: "sonnet" } })

# the base harness
Workflow({ scriptPath: "evals/harness.workflow.js" })
```

Make it more rigorous: add tasks, raise n per cell, average over several seeds, add a second non-Anthropic judge. See the caveats in `../BENCHMARKS.md`.
