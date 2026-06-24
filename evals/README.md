# evals/

The real measurement behind [`../BENCHMARKS.md`](../BENCHMARKS.md). No estimated numbers — this folder is the receipt.

| File | What it is |
|---|---|
| `harness.workflow.js` | Claude-Code harness (Workflow tool). 4 Claude-family models × 3 arms × 8 tasks, blind Opus judge. |
| `results.json` | Raw measured output the harness writes on a run (per-cell scores + length + deltas) — gitignored; the transcribed numbers live in [`../BENCHMARKS.md`](../BENCHMARKS.md). |
| `portable_eval.py` | **Vendor-agnostic** harness — stdlib only, no pip. Same 3-arm design against **OpenAI (GPT/Codex), Mistral, and Anthropic**. This is how you get real Codex/Mistral numbers. |

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

- **Arms:** `baseline` (task only) · `terse` (task + generic "be concise, write minimal code") · `fabius` (task + the full fabius stance). The `terse` arm is the control that separates fabius's **structure** from plain brevity.
- **Models:** `claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5` — each actually run via per-agent model override.
- **Judge:** `claude-opus-4-8`, **blind** (never told which arm wrote which answer), scoring correctness / minimality / best-practice, 0–5 each.
- **Objective metric:** average output length (chars) — bias-free.

## Run it yourself

```
Workflow({ scriptPath: "evals/harness.workflow.js" })
```

Make it more rigorous: add tasks, raise n per cell, average over several seeds, add a second non-Anthropic judge. See the caveats in `../BENCHMARKS.md`.
