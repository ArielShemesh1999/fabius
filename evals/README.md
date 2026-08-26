# evals/

The measurement behind **the fabius benchmark** ([`../BENCHMARKS.md`](../BENCHMARKS.md)) — one dated test, four panels, one canonical aggregate: [`results.benchmark.json`](results.benchmark.json). `node verify-receipts.mjs` replays every aggregate the committed score rows can support. Historical limitations are explicit: v5/v6/v7 omit candidate answer text, v6 omits execution files/stdout, and Panel C's raw portable receipt was not committed.

| File | What it is |
|---|---|
| `results.benchmark.json` | Canonical aggregate and evidence-limit declaration. Committed; deterministically checked against v5/v6/v7 where those receipts permit. |
| [`suite/`](suite/) | **The Fabius Benchmark Suite (FBS v1.0)** — the versioned evaluation framework from [`../IDENTITY.md`](../IDENTITY.md): 100 neutral tasks in three tiers (20 smoke / 50 core / 30 stress) across ten categories A–J, a fixed 7-dimension 0–4 rubric, three modes **BASE / FAB / FAB_MEMORY**, plus its own deterministic validator (`node evals/suite/validate.mjs`, 9/9). |
| `harness.v7.workflow.js` | **Panel D harness — the FBS run**: committed suite × 3 modes; two blind rubric judges + fixed factual checks interpreted from answer text by a model grader. New runs retain answers/digests, check evidence and full judge votes. |
| `results.v7.json` | Historical Panel D score rows and aggregates. Candidate answers/check evidence were not retained. |
| `structural.mjs` | Deterministic structural suite — no model, key or network. Recursively proves the install surface is exactly the fifteen declared top-level contracts, then checks budgets, frontmatter, references and the content-bound seal. The command derives its live invariant count. |
| `verify-receipts.mjs` | Deterministically recomputes Panel A/B aggregates and Panel D projections from committed score rows; rejects canonical drift and undeclared evidence gaps. |
| `harness.v5.workflow.js` | Panel A future-run harness: two blind judges, now retaining candidate answers/digests and full votes. Historical inter-judge gap: 0.72/15. |
| `results.v5.json` | Historical Panel A score rows; no candidate answers. |
| `harness.v6.workflow.js` | Panel B future-run harness: deterministic local code extraction/execution with content-addressed evidence + two model graders over fixed factual checklists. |
| `results.v6.json` | Historical Panel B bounded score rows. The old run used a model tool operator and retained no code/stdout or individual checklist votes. |
| `portable_eval.py` | Panel C harness — vendor-agnostic, stdlib only. A new run writes `results.portable.json`; the historical published raw file is missing and cannot be reconstructed. |
| `harness.v3.workflow.js` | Supporting receipt — specialist-domain coverage: 13 tasks (one per specialist domain, incl. the on-chain / automation / science verticals) × 3 arms × 2 tiers, blind Opus judge, condensed contract transcriptions. |
| `harness.v3-ext.workflow.js` | Supporting receipt — the same method over the verticals `doctrina` (ML eval) + `fortuna` (trading backtest), so every specialist domain is exercised (the `fabius-concilium` layer deliberates across models, not a task domain — not yet in a blind run). |
| `results.v3.json` | Raw receipt for the specialist-coverage run — per-cell scores, length, per-domain deltas. Committed. |
| `harness.workflow.js` | Base Claude-Code harness. 3 arms × 6 tasks, blind Opus judge. Supporting receipt. |
| `eval.mjs` | Node harness — clean **no-system-prompt** API baseline (the strictest baseline). `--selftest` checks wiring with no key. The no-key selftest entry point of the arm design. |
| `results.json` | Raw output `eval.mjs` writes on a run — gitignored. |

## Structural suite (no key, no network)

```bash
node evals/structural.mjs            # derives invariant count; exits non-zero on any FAIL
node evals/structural.mjs --json     # also writes evals/structural.json
node evals/verify-receipts.mjs       # replay committed score aggregates
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
- **Modes (Panel D / FBS):** `BASE` (bare model) · `FAB` (shipped stance + routed contract, verbatim) · `FAB_MEMORY` (FAB + the task's committed memory snapshot injected as recalled `fabius-archivum` memory) — scored on the suite's 7-dimension rubric plus fixed factual checks interpreted from answer text by a model grader.
- **Models:** the four Claude models current at the 2026-07-01 run — Fable 5 (`claude-fable-5`), `claude-opus-4-8`, `claude-sonnet-5`, `claude-haiku-4-5` — each actually run via per-agent model override (Panel A/B). (Date the roster; never claim it is the newest — Opus 5 shipped 2026-07-24, after these runs.) Panel C carries the same arms cross-family (GPT / Grok / Mistral / Gemini) through `portable_eval.py`.
- **Judge:** Panel A uses two blind model judges. Panel B's current code track is deterministic local execution, while its fixed factual checklists are still interpreted by two model graders. The historical v6 execution was operated and reported by a tool-using model agent.
- **Objective metric:** average output length (chars) — bias-free.

## Run it yourself

```
# Panel D — the FBS run (validate first, then execute the committed suite)
node evals/suite/validate.mjs
Workflow({ scriptPath: "evals/harness.v7.workflow.js", args: { tasks: [/* evals/suite/*.jsonl */], model: "sonnet" } })

# the base harness
Workflow({ scriptPath: "evals/harness.workflow.js" })
```

New runs must retain candidate answers, hashes, execution stdout/stderr and individual votes. Add tasks, raise n per cell, average over seeds and add a non-Anthropic judge; never overwrite a dated historical result with a rerun.
