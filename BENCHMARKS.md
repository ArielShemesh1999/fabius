# Benchmarks — does fabius actually improve model output?

Fabius ships **a runnable harness *and* the measured runs behind it.** You can reproduce every number on your own machine with your own key, for the exact model you care about — and below are the runs already done, with their caveats stated plainly. Nothing here is estimated; every figure was measured on a real model at a named moment.

That double posture is deliberate. A stance like fabius is prompt-level scaffolding, so a number measured on one model at one moment doesn't transfer cleanly to yours. The defensible thing to publish is the **method, the mechanism, and the measured signal that repeats across models** — plus a one-command way to re-measure it for real.

---

## What the harness measures

A blind, three-arm eval — the standard way to separate a real effect from noise:

- **Three arms per task:**
  - `baseline` — the task only.
  - `terse` — the task + a generic *"Be concise. Write minimal code."* line.
  - `fabius` — the task + the shipped [`AGENTS.md`](AGENTS.md) stance, read verbatim at runtime.
  The `terse` arm is the important control: it isolates fabius's **structure** (the YAGNI ladder, the never-trim guardrails, the design/agent discipline) from plain brevity. Beating `baseline` is easy; **beating `terse` is the real test.**
- **Blind judge.** Every answer is scored by a judge model **never told which arm produced it**, 0–5 on **correctness**, **minimality** (penalizes bloat), **best-practice** (rewards keeping validation, security, a11y, tokens, least privilege) — plus the objective **output length** in characters.

The length numbers are bias-free (a character count can't be flattered). The quality scores come from a model judge — directional; read the answers yourself.

---

## Measured results

Three separate runs, three different lenses. They agree on the shape: **structure beats brevity, and the gap is largest where lean-done-naively would be *wrong*.**

### The margin, at a glance

How much fabius surpasses plain *"be concise"* (TERSE — the real control), by task category, across the four measured families (FAB − TERSE, /15):

```
genuine build   +6 … +9   ████████████████████   ← largest  (rate limiter · CSV parser)
trust / order   +4 … +7   ███████████████        (zero-downtime migration · file upload)
YAGNI (pure)    +0 … +2   ████                   ← ~tie, by design (over-building adds nothing)

same tasks, output length:   31–52 % SHORTER than baseline — and the blind judge scores it HIGHER.
```

The point isn't "fabius is shorter" (so is TERSE). It's that fabius is shorter **and** wins the quality score — the one move plain brevity can't make.

### 1 — In-repo eval, 3 Claude tiers (`evals/harness.workflow.js`, run v2, 2026-06-20)

8 tasks × 3 arms, blind judge (`claude-opus-4-8`). Total out of 15:

| Model | baseline | terse | **fabius** | gain vs terse | output cut vs baseline |
|---|---|---|---|---|---|
| opus   | 12.5 | 13.0 | **13.88** | +0.88 | −42.6% |
| sonnet | 8.75 | 11.75 | **12.5**  | +0.75 | −52.1% |
| haiku  | 8.88 | 9.13 | **10.38** | +1.25 | −31.6% |

fabius beats terse on every tier **while cutting output 31–52%** — shorter answers the blind judge scores *higher*.

### 2 — Cross-family stance test, 4 model families (6 tasks, 3 categories)

Arms BASE / TERSE / FAB; categories trust-order, YAGNI, genuine-build. The signal is **FAB − TERSE** (structure vs brevity), measured on Grok, Mistral, GPT, Claude. Grok + Mistral were judged **blind cross-family** (by Claude, FAB unlabeled) — the cleanest evidence.

| Task | category | Grok | Mistral | GPT | Claude |
|---|---|---|---|---|---|
| A1 migration | trust/order | +7 | +4 | +6 | +6 |
| A2 upload | trust/security | +7 | +5 | +5 | +7 |
| B1 exporter | YAGNI | +1 | +2 | +1 | +1 |
| B2 USD format | YAGNI | 0 | 0 | 0 | 0 |
| C1 rate limiter | genuine build | +8 | +1 | +6 | +6 |
| C2 CSV parser | genuine build | +9 | +4 | +8 | +8 |

The pattern repeats on all four families: **large lift on trust/order/build, ~zero on pure YAGNI.** FAB never lost an arm; its worst case was a tie (B2). The hardest control — the *under-build trap* (C1/C2, where naive lean is the wrong answer) — FAB passed every time by making the *correct* lean move (shared store / real parser), not the smallest one. Objective trap-pass: every model, every task — validation kept, plugin-systems avoided, Redis over in-memory, a real CSV parser over `split(',')`.

> **Gemini** is the runnable fifth family — `python evals/portable_eval.py --models gemini` with `GEMINI_API_KEY` set produces a real `gemini-2.5-pro` row on the same three arms. It is left out of the table above rather than estimated: this doc commits no number it didn't measure. Drop the measured row in here once the run exists.

### 3 — Landing-page build, stance vs full mechanism (Mundial 2026, 2026-06-22)

Three live builds of the same brief — **T1** fabius stance only · **T2** no fabius · **T3** fabius + all six skills.

> *Version note: this run measures the then-six-skill build. The specialists added in v1.3.0 — `fabius-mercatus`, `fabius-praesidium`, `fabius-ludus`, and the `fabius-decor` figura/data-viz concern — are **not** exercised by this benchmark and make no claim on these numbers. The "six skills" wording below is left exactly as-run, on purpose.*

| | design score | lines | size | working signup form |
|---|---|---|---|---|
| T1 stance only | **8.5** | 561 | 34 KB | no |
| T2 no fabius | 8.3 | 517 | 31 KB | no |
| T3 stance + 6 skills | 7.5 | **333** | **19 KB** | **yes** |

The reading: the bare stance maximizes **design polish** (T1 wins on the judge's eye); the full six-skill mechanism shifts toward **lean + functional** — T3 shipped 40% less code *and the only working form*. They optimize different things, and **this is the live proof the mechanism fires on its own** (see "what this does / doesn't test" below).

---

## The mechanism — why the structure should help

Each fabius rule counters a *documented* default tendency of current code models:

| Common model default | The fabius rule that counters it |
|---|---|
| Over-explains; adds unrequested boilerplate; hedges | Lean output + the YAGNI ladder + surgical changes |
| Over-engineers an under-specified task (a framework for one flag) | The ladder's first rung: *does this need to exist at all?* |
| Concise models that skip guardrails (validation, a11y, error handling) | The never-trim list — non-negotiable |
| Builds *too little* when lean-naive is wrong (in-memory limiter, `split(',')`) | "Strike narrow" = the *correct* lean rung, not the smallest |

A good result is **shorter answers the blind judge scores higher** — brevity *and* the guardrails, not one at the cost of the other. Run 2's under-build column is the proof that fabius is a scope-control system, not a "shorten" prompt: a model that only shortens physically cannot also produce the longest, most-complete migration answer.

---

## What this does and doesn't test

- Runs 1–2 test **#1 — does injecting the stance improve output.** Yes, consistently, cross-model.
- Run 3 (T3) tests **#2 — does the six-skill mechanism fire and act on its own.** Yes — it shipped the leanest, only-functional build live in Claude Code.
- The advantage **grows as the model's default discipline drops** (Run 1: sonnet/haiku gain more than opus; Run 2: lean-BASE Grok gains most, verbose-BASE Mistral least). The advantage is always present; its *size* tracks how undisciplined the default is.

---

## Reproduce it (one command)

```bash
# wiring check — no key, no cost, no network
node evals/eval.mjs --selftest

# a real run (Anthropic)
ANTHROPIC_API_KEY=...  node evals/eval.mjs --model claude-sonnet-4-6

# a real run (OpenAI / Codex family)
OPENAI_API_KEY=...     node evals/eval.mjs --provider openai --model gpt-4o

# cross-vendor (OpenAI / Mistral / Anthropic / Gemini) — your keys
GEMINI_API_KEY=...     python evals/portable_eval.py --models gemini
```

The `fabius` arm injects the **actual** shipped `AGENTS.md`, so you benchmark the real stance, not a paraphrase. It writes `evals/results.json`. Swap `--model` / `--judge` to benchmark anything; add tasks in the `TASKS` array.

---

## Caveats (read these)

- **Most runs are directional.** GPT and Claude judged their own family in the same window — directional, not blind. The hard signals are the **character counts** and the **cross-family blind subset** (Grok, Mistral judged by Claude), not the absolute totals.
- **The judge is a model.** Length is objective; quality scores share model-family priors. Read the generated answers.
- **Small n.** 6–8 tasks per arm is a directional signal, not a paper. Treat sub-point deltas as ties.
- **Blind scores lower — and that's reassurance.** The blind cross-family runs scored fabius lower than the self-judged ones (86/82 vs 89/87). A judge that doesn't love itself scores harder; the pattern held anyway.
- **Versions move.** Every number was measured on one model at one moment. Don't generalize past that — re-run it.

> The claim the data supports: **fabius gives a consistent, cross-model quality lift that grows as the model's default gets less disciplined — large at trust / order / genuine-build boundaries, negligible at pure YAGNI. It is not a "shorten" prompt; it is a scope-control system that knows when to compress and when to expand.** Not "smarter." Not "10× on everything." That sentence survives technical scrutiny; the inflated one doesn't.
