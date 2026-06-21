# Benchmarks — does fabius actually improve model output?

Fabius ships a **runnable benchmark, not a claimed number.** This repo bundles no result table. You run the harness with your own key and get your own honest numbers — for the exact model you care about. Nothing here is estimated, and nothing is printed that wasn't measured on your machine.

That is a deliberate choice. A stance like fabius is prompt-level scaffolding, so a number measured on one model at one moment doesn't transfer cleanly to yours. The defensible thing to publish is the **method and the mechanism**, plus a one-command way to measure it for real.

---

## What the harness measures

A blind, three-arm eval — the standard way to separate a real effect from noise:

- **Three arms per model:**
  - `baseline` — the task only.
  - `terse` — the task + a generic *"Be concise. Write minimal code."* line.
  - `fabius` — the task + the shipped [`AGENTS.md`](AGENTS.md) stance, read verbatim at runtime.
  The `terse` arm is the important control: it isolates fabius's **structure** (the YAGNI ladder, the never-trim guardrails, the design/agent discipline) from plain brevity. Beating `baseline` is easy; beating `terse` is the real test.
- **Eight tasks** spanning the skill domains: two over-engineering traps (cache a one-line function, a single boolean flag), an off-by-one auth bug, SaaS button + card CSS, a least-privilege PR-review subagent, a connection-pooling explanation, an Express route taking a query param (validation / security), and an accessible modal (a11y).
- **Blind judge.** Every answer is scored by a judge model that is **never told which arm produced it**, 0–5 on three axes — **correctness**, **minimality** (penalizes bloat and over-engineering), **best-practice** (rewards keeping validation, security, a11y, design tokens, least privilege) — plus the objective **output length** in characters.

`3 arms × 8 tasks = 24 generations + 24 blind judgements per model.`

The length numbers are bias-free (a character count can't be flattered). The quality scores come from a model judge, so treat them as directional and read the answers yourself.

---

## The mechanism — why the structure should help

Beyond the measured run, there's a mechanism argument: each fabius rule counters a *documented* default tendency of current code models.

| Common model default | The fabius rule that counters it |
|---|---|
| Over-explains; adds unrequested boilerplate and scaffolding; hedges | Lean output + the YAGNI ladder + surgical changes — ship the minimum, cut the preamble |
| Over-engineers an under-specified task (a framework for one flag) | The ladder's first rung: *does this need to exist at all?* — exactly what the `cache` and `flag` tasks bait |
| Concise models that skip the guardrails (validation, a11y, error handling) | The never-trim list: validation at trust boundaries, security, accessibility are non-negotiable |
| Verbose model-default prose | Lean output — the measurable length cut |

The two guardrail tasks (`route` = an unvalidated query param, `modal` = accessibility) exist specifically to catch a stance that cut too much. A good result is **shorter answers that the blind judge scores higher** — brevity *and* the guardrails, not one at the cost of the other.

---

## Reproduce it (one command)

```bash
# wiring check — no key, no cost, no network
node evals/eval.mjs --selftest

# a real run (Anthropic)
ANTHROPIC_API_KEY=...  node evals/eval.mjs --model claude-sonnet-4-6

# a real run (OpenAI / Codex family)
OPENAI_API_KEY=...     node evals/eval.mjs --provider openai --model gpt-4o
```

It prints a per-arm table (total /15 and average length, with the delta vs baseline) and writes `evals/results.json`. The `fabius` arm injects the **actual** shipped `AGENTS.md`, so you are benchmarking the real stance, not a paraphrase. Swap `--model` / `--judge` to benchmark anything; add tasks by editing the `TASKS` array in `evals/eval.mjs`.

---

## Caveats (read these)

- **Small n.** Eight tasks per arm is a directional signal, not a paper. Expect noise on the totals; treat sub-point deltas as ties.
- **The judge is a model.** The length numbers are objective; the quality scores share model-family priors. Read the generated answers, don't just trust the score.
- **One run is one run.** Re-run it; sampling moves the numbers. The robust result to look for is *structure beating plain terseness*, repeatably — not a specific magnitude.
- **This is the mechanism + method.** The number is whatever your own run prints. That's the honest version, and it's the one fabius ships.
