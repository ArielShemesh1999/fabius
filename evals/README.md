# evals/

The real measurement behind [`../BENCHMARKS.md`](../BENCHMARKS.md). No estimated numbers — this folder is the receipt.

| File | What it is |
|---|---|
| `structural.mjs` | **Deterministic** structural suite — no model, no key, no network. Proves the *system* is well-formed: fifteen single-owner contracts, every `SKILL.md` under budget, every flattened `description` ≤ 1024 chars, every reference live (markdown links **and** backtick-quoted mentions), no sealed-set drift (manifest file list == on-disk set), the content-bound seal verifiable. 19/19 must pass (the seal hash-match goes red mid-edit, green on re-seal). `node evals/structural.mjs` |
| `harness.v3.workflow.js` | Claude-Code harness for **Run 4** — 13 tasks (one per specialist domain, incl. the on-chain / automation / science verticals) × 3 arms × 2 tiers, blind Opus judge. The `fabius` arm injects the stance **+ the relevant specialist contract**. This is the specialist-domain behavioral proof. |
| `harness.v3-ext.workflow.js` | **Run 4 extension** — same method, the two later verticals `doctrina` (ML eval) + `fortuna` (trading backtest). Markets +2.0, ML eval +0.5 vs baseline; now every then-existing specialist domain is exercised (the later `fabius-concilium` layer deliberates across models, not a task domain — not yet in a blind run). |
| `results.v3.json` | The published Run 4 receipt — per-cell scores, length, per-domain deltas. Committed (the one raw receipt that ships). |
| `harness.workflow.js` | Earlier Claude-Code harness. 3 arms × 6 tasks, blind Opus judge. |
| `eval.mjs` | Node harness — clean **no-system-prompt** API baseline (the strictest baseline). `--selftest` checks wiring with no key. |
| `results.json` | Raw output `eval.mjs` writes on a run — gitignored; transcribed numbers live in [`../BENCHMARKS.md`](../BENCHMARKS.md). |
| `portable_eval.py` | **Vendor-agnostic** harness — stdlib only, no pip. Same 3-arm design against **OpenAI (GPT/Codex), Mistral, Anthropic, Gemini**. This is how you get real Codex/Mistral numbers. |

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

- **Arms:** `baseline` (task only) · `terse` (task + generic "be concise, write minimal code") · `fabius` (task + the fabius stance). `eval.mjs` reads the shipped `AGENTS.md` **verbatim**; the Run 4 workflow injects a **faithful condensed transcription** of the stance plus the routed specialist's operative contract, hand-transcribed into the harness. The `terse` arm is the control that separates fabius's **structure** from plain brevity.
- **Models:** `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5` — each actually run via per-agent model override.
- **Judge:** `claude-opus-4-8`, **blind** (never told which arm wrote which answer), scoring correctness / minimality / best-practice, 0–5 each.
- **Objective metric:** average output length (chars) — bias-free.

## Run it yourself

```
Workflow({ scriptPath: "evals/harness.workflow.js" })
```

Make it more rigorous: add tasks, raise n per cell, average over several seeds, add a second non-Anthropic judge. See the caveats in `../BENCHMARKS.md`.
