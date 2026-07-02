# evals/

The measurement behind **the fabius benchmark** ([`../BENCHMARKS.md`](../BENCHMARKS.md)) — one test, three panels, one canonical receipt: [`results.benchmark.json`](results.benchmark.json). No estimated numbers — this folder is the receipt. Each harness below serves one of the benchmark's panels (or the structural suite); the older harnesses are the method iterations kept as raw history.

| File | What it is |
|---|---|
| `results.benchmark.json` | **THE canonical receipt** — the three panels (A quality / B objective / C external demos) consolidated, with per-panel pointers to the raw files below. Committed. |
| `structural.mjs` | The benchmark's **deterministic structural suite** — no model, no key, no network. Proves the *system* is well-formed: fifteen single-owner contracts, every `SKILL.md` under budget, every flattened `description` ≤ 1024 chars, every reference live (markdown links **and** backtick-quoted mentions), no sealed-set drift (manifest file list == on-disk set), the content-bound seal verifiable. 19/19 must pass (the seal hash-match goes red mid-edit, green on re-seal). `node evals/structural.mjs` |
| `harness.v5.workflow.js` | **Panel A harness** — quality, blind, the four newest Claude models: 15 tasks × 4 models × 3 arms with the shipped skill files injected **verbatim**, **two blind judges** (Opus + Fable, inter-judge gap 0.72/15). |
| `results.v5.json` | **Panel A raw** — per-cell scores from both judges, lengths, per-model and per-domain deltas. Committed. |
| `harness.v6.workflow.js` | **Panel B harness** — objective, no judge taste: generated code **executed against hidden test suites** + domain deliverables graded against a **factual checklist** by two strict graders. 9 deliverables × 4 models × 3 arms. |
| `results.v6.json` | **Panel B raw** — per-task pass rates (tests + checks) per cell. Committed. |
| `portable_eval.py` | **Panel C harness** — vendor-agnostic, stdlib only, no pip. Same 3-arm design against **OpenAI (GPT/Codex), Grok-compatible, Mistral, Anthropic, Gemini**, judged blind cross-family. Writes `results.portable.json` on run. |
| `harness.v3.workflow.js` | Method history — specialist-domain coverage: 13 tasks (one per specialist domain, incl. the on-chain / automation / science verticals) × 3 arms × 2 tiers, blind Opus judge, condensed contract transcriptions. The iteration that led to Panel A's shipped-files-verbatim arm. |
| `harness.v3-ext.workflow.js` | Method history — same method extended to the two later verticals `doctrina` (ML eval) + `fortuna` (trading backtest), so every then-existing specialist domain was exercised (the later `fabius-concilium` layer deliberates across models, not a task domain — not yet in a blind run). |
| `results.v3.json` | Raw receipt for the specialist-coverage iteration — per-cell scores, length, per-domain deltas. Committed. |
| `harness.workflow.js` | Earlier Claude-Code harness. 3 arms × 6 tasks, blind Opus judge. Method history. |
| `eval.mjs` | Node harness — clean **no-system-prompt** API baseline (the strictest baseline). `--selftest` checks wiring with no key. The first version of the benchmark's arm design. |
| `results.json` | Raw output `eval.mjs` writes on a run — gitignored. |

## Structural suite (no key, no network)

```bash
node evals/structural.mjs            # 19/19 invariants — exits non-zero on any FAIL
node evals/structural.mjs --json     # also writes evals/structural.json
```

Behavioral runs ask *does fabius act better*; this asks *is fabius built right* — single-owner/zero-overlap, progressive-disclosure budgets, reference integrity, and the SHA-256 + Merkle content-bound seal, all recomputable from the repo files.

## Cross-vendor run (OpenAI / Mistral / your keys)

```bash
export OPENAI_API_KEY=...      # GPT/Codex family
export MISTRAL_API_KEY=...     # mistral-large-latest
export ANTHROPIC_API_KEY=...   # claude models
python3 evals/portable_eval.py            # runs every vendor whose key is set
python3 evals/portable_eval.py --models openai mistral   # subset
python3 evals/portable_eval.py --selftest # verify harness logic, no key needed
```

Writes `results.portable.json`. No fabrication — rows appear only for vendors you actually run.

## Design (three-arm, blind)

- **Arms:** `baseline` (task only) · `terse` (task + generic "be concise, write minimal code") · `fabius` (task + the fabius stance). The Panel A/B harnesses (`harness.v5` / `harness.v6`) and `eval.mjs` load the shipped `AGENTS.md` (+ routed `SKILL.md`) **verbatim**; the older `harness.v3` iteration injected a faithful condensed transcription instead. The `terse` arm is the control that separates fabius's **structure** from plain brevity — the real test.
- **Models:** the four newest Claude models — Fable 5 (`claude-fable-5`), `claude-opus-4-8`, `claude-sonnet-5`, `claude-haiku-4-5` — each actually run via per-agent model override (Panel A/B). The Sonnet tier was re-run on **Sonnet 5** on 2026-07-02 (it had previously run on `claude-sonnet-4-6`). Panel C carries the same arms cross-family (GPT / Grok / Mistral / Gemini) through `portable_eval.py`.
- **Judge:** Panel A uses **two** blind judges (Opus + Fable, averaged; inter-judge gap 0.72/15); the older single-judge iterations used `claude-opus-4-8`, **blind** (never told which arm wrote which answer), scoring correctness / minimality / best-practice, 0–5 each. Panel B removes the judge entirely — executed tests + factual checklists.
- **Objective metric:** average output length (chars) — bias-free.

## Run it yourself

```
Workflow({ scriptPath: "evals/harness.workflow.js" })
```

Make it more rigorous: add tasks, raise n per cell, average over several seeds, add a second non-Anthropic judge. See the caveats in `../BENCHMARKS.md`.
