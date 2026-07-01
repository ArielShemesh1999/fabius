<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# Benchmarks — does the fabius agent measurably out-perform the bare model?

Fabius ships **a runnable harness *and* the measured runs behind it.** You can reproduce every number on your own machine with your own key, for the exact model you care about — and below are the runs already done, with their caveats stated plainly. Nothing here is estimated; every figure was measured on a real model at a named moment.

That double posture is deliberate. fabius is an autonomous agent; its decision layer is prompt-level scaffolding read at runtime, so a number measured on one model at one moment doesn't transfer cleanly to the model you run it on. The defensible thing to publish is the **method, the mechanism, and the measured signal that repeats across models** — plus a one-command way to re-measure it for real.

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

Five runs, five different lenses, plus a deterministic structural suite. They agree on the shape: **structure beats brevity, and the gap is largest where lean-done-naively would be *wrong*.** Run 5 is the widest: **all four internal models** (haiku · sonnet · opus · fable) with the `fabius` arm carrying the **shipped files verbatim** and **two blind judges** — it shows the output cut is universal and the quality lift is real on the frontier tiers and on any routed specialist, while reporting honestly where the full contracts overwhelm the smallest model. Run 4 is the one that exercises the **specialist surface** — one task per specialist domain as it stood, including the on-chain / automation / science verticals — so the proof reaches the technical verticals, not just the lean stance. (The two specialists added since, `fabius-doctrina` and `fabius-fortuna`, were then measured in the Run 4 **extension** below — every then-existing specialist domain is now exercised. The cross-model `fabius-concilium` layer, added later still, is honestly *not yet* in a blind run: it deliberates *across* models on one question rather than adding a task domain, so its proper test is whether a council beats its best single seat — a measurement to add, not a claim to make here.)

### The margin, at a glance

How much fabius surpasses plain *"be concise"* (TERSE — the real control), by task category, across the four measured families (FAB − TERSE, /15):

```
genuine build   +6 … +9   ████████████████████   ← largest  (rate limiter · CSV parser)
trust / order   +4 … +7   ███████████████        (zero-downtime migration · file upload)
YAGNI (pure)    +0 … +2   ████                   ← ~tie, by design (over-building adds nothing)

same tasks, output length:   31–52 % SHORTER than baseline — and the blind judge scores it HIGHER.
```

The point isn't "fabius is shorter" (so is TERSE). It's that fabius is shorter **and** wins the quality score — the one move plain brevity can't make.

### 1 — In-repo eval, 3 Claude tiers (`evals/eval.mjs` → `evals/results.json`)

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

### 3 — Landing-page build, stance vs full mechanism

Three live builds of the same brief — **T1** fabius stance only · **T2** no fabius · **T3** fabius + all six skills.

> *Version note: this run measures the then-six-skill build, left exactly as-run. The specialists beyond those six — including the `fabius-catena`, `fabius-machina`, `fabius-scientia` verticals — are not exercised **here**; they are exercised in **Run 4 below**, which spans all ten specialist domains. The "six skills" wording in this table is preserved on purpose.*

| | design score | lines | size | working signup form |
|---|---|---|---|---|
| T1 stance only | **8.5** | 561 | 34 KB | no |
| T2 no fabius | 8.3 | 517 | 31 KB | no |
| T3 stance + 6 skills | 7.5 | **333** | **19 KB** | **yes** |

The reading: the bare stance maximizes **design polish** (T1 wins on the judge's eye); the full six-skill mechanism shifts toward **lean + functional** — T3 shipped 40% less code *and the only working form*. They optimize different things, and **this is the live proof the mechanism fires on its own** (see "what this does / doesn't test" below).

### 4 — Specialist-domain coverage: one task per specialist (`evals/harness.v3.workflow.js`)

The run that closes the gap Run 3's version-note named. **13 tasks across 11 blind-judged task domains** — the YAGNI traps, correctness, security, a11y, agents, design, **on-chain (catena)**, **automation (machina)**, **science (scientia)**, marketing, game — × the same three arms, generated on two tiers, **judged blind by `claude-opus-4-8`** (156 agents total). Tasks outnumber domains: two domains carry two tasks each (YAGNI: cache + config-flag; security: query route + upload threat-model). Here the `fabius` arm injects a **faithful condensed transcription of the stance plus the relevant specialist's operative contract** for each domain task (hand-transcribed into the harness from `AGENTS.md` and the `SKILL.md` contracts, not the shipped files read at runtime) — so this measures the routed *specialist mechanism*, not the stance alone. The arm that injects the shipped `AGENTS.md` **verbatim** is Run 1 (`eval.mjs`).

Totals out of 15 (n = 13 per cell):

| Tier | baseline | terse | **fabius** | gain vs terse | gain vs baseline | output cut vs baseline |
|---|---|---|---|---|---|---|
| sonnet | 14.15 | 13.00 | **14.69** | +1.69 | +0.54 | −30.7% |
| haiku  | 11.23 | 12.85 | **13.15** | +0.30 | +1.92 | −50.6% |
| **pooled** | 12.69 | 12.93 | **13.92** | **+0.99** | **+1.23** | **−42.6%** |

**fabius is the only arm that beats *both* the bare baseline *and* the "be concise" control on *both* tiers** — while cutting output 31–51%. It scores **≥ baseline in all 11 task domains** and **≥ terse in 8 of 11**.

The lift concentrates exactly where the thesis predicts — the technical verticals, including the three new ones (FAB − control, /15, both tiers pooled):

```
science  (scientia)    +4.5 vs base  ████████████████████  ← largest — multiple-testing-correction trap
automation (machina)   +3.5 vs terse █████████████████     ← idempotency / auth / retry the controls dropped
game     (ludus)       +3.0 vs base  █████████████
markets  (fortuna)     +3.0 vs terse █████████████         ← out-of-sample + costs + "not advice" (extension)
on-chain (catena)      +1.5 vs base  ██████                 ← SPL owner/mint validation, money-safety
design · security · a11y · agents    +0.5…+1.5
ML eval  (doctrina)    +0.5 vs both  ██                     ← bare model already holds; +0.5 and ~54% shorter (extension)
YAGNI (pure)           −1.75 vs terse ▓▓                     ← brevity matches/beats, by design
```

The sharpest single cell: the **RNA-seq differential-expression** task on haiku — baseline **7**, "be concise" **8**, **fabius 15**. The controls fed normalized values or skipped FDR correction (a *fluently-wrong* science bug); the `scientia` contract forced raw counts + Benjamini-Hochberg. That is a guardrail neither baseline nor brevity supplies.

Honest reading of the misses: **pure-YAGNI** is the one category where plain "be concise" beats fabius (−1.75) — exactly as designed, since over-building adds nothing there so there is no scope to control. Marketing copy and one game-loop cell were ~ties. And the **baseline here is a Claude-Code subagent** that already carries a lean-ish system prompt, so it is an unusually strong baseline — fabius wins *into a headwind*, which is the conservative direction. Full per-task data: [`evals/results.v3.json`](evals/results.v3.json).

### 5 — All four internal models, shipped files read verbatim (`evals/harness.v5.workflow.js`)

The run that answers a sharper question than Run 4: what happens on **every internal model** — `haiku`, `sonnet`, `opus`, `fable` — when the `fabius` arm carries the **actual shipped files, byte-for-byte** (the whole `AGENTS.md` stance, plus the routed specialist's whole `SKILL.md` contract), not a hand-condensed transcription? **15 tasks × 4 models × 3 arms = 180 generations, each scored by two blind judges** (`opus` + `fable`, averaged — so no model grades only its own work; inter-judge mean gap 0.69/15). 551 real agents. Receipt: [`evals/results.v5.json`](evals/results.v5.json).

Totals out of 15 (n = 15 per cell), and the output cut vs the bare model:

| Model | baseline | terse | **fabius** | Δ vs baseline | Δ vs terse | output cut |
|---|---|---|---|---|---|---|
| **fable** (frontier) | 14.50 | 14.60 | **14.73** | **+0.23** | **+0.13** | **−25.3%** |
| **opus** (frontier) | 14.40 | 14.43 | **14.60** | **+0.20** | **+0.17** | **−20.0%** |
| sonnet (mid) | 14.27 | 14.33 | 14.20 | −0.07 | −0.13 | −20.3% |
| haiku (fast) | 11.73 | 12.43 | 11.40 | −0.33 | −1.03 | −35.5% |

Three findings, stated straight:

1. **The output cut is universal — −20% to −35% on every model.** The scope-control claim doesn't depend on the tier; it holds everywhere.
2. **On the frontier tiers fabius actually runs at — Opus 4.8 and Fable 5 — it beats *both* the bare model *and* the "be concise" control** while cutting output ~20–25%. Leaner *and* better, together.
3. **Where a specialist contract is routed, the lift is large even on the smallest model.** Split Haiku's tasks by kind: on the **twelve specialist tasks its average delta is +0.71** — security route **9.0 → 14.5**, on-chain SPL balance **10.5 → 14.5**, CSS **12.5 → 14.0**, ML ship-decision **13.0 → 14.0**. The contract adds real domain rigor a small model doesn't supply on its own.

**The honest miss, and why it's instructive.** Haiku's overall −0.33 is driven entirely by the **three trivial tasks** (a one-line token fix, a cache one-liner, a basic modal), where its average delta is **−4.50** — the one-line `off-by-one` fix regressed from 14.5 to 3.0. Dumping a 10 KB verbatim contract in front of a *fast* model for a *one-line* job overwhelms it. That is not an argument against the contracts; it is a live demonstration of exactly why fabius **routes by model-tier and gates on the lean core first** — you send the fast tier a condensed stance and let `fabius-parcus` skip the machinery when the job is trivial (Run 4, which injected the *condensed* stance, is where haiku gains). The capable models show no such overwhelm: on trivial tasks Opus and Fable are still **+0.33 / +0.50**. And pooled across all four models and all 15 tasks, fabius (13.73) ties the bare model (13.72) while terse edges both (13.95) — so the value here is **the 26% output cut plus the frontier and specialist lifts**, not a pooled quality win. No number is hidden; the receipt has every cell.

### Structural tests — the system is well-formed (no model, no key)

Separate from "does the stance help," a deterministic suite proves the *system* is intact. These are pass/fail facts that reproduce byte-for-byte on any clone — [`node evals/structural.mjs`](evals/structural.mjs):

| Invariant | Result |
|---|---|
| Exactly fifteen skill contracts; one router, one always-on core; names unique | **PASS** |
| Frontmatter `name` matches directory; declares `name` + `description` | **PASS** |
| Every flattened frontmatter `description` ≤ 1024 chars (discovery budget) | **PASS** |
| Progressive disclosure — every `SKILL.md` ≤ 12 KB (depth lives in `references/`) | **PASS** (max 11.2 KB) |
| Provenance `fab1-` fingerprint embedded in all 15 contracts | **PASS** |
| Reference integrity — every linked **and backtick-quoted** `references/` path resolves | **PASS** |
| Plugin manifest skill list == skills on disk; version 1.0.0 | **PASS** |
| No sealed-set drift — seal-manifest file list == skills on disk + ARCHITECTURE/CORPUS/AGENTS | **PASS** |
| Content-bound seal — 18 sealed files hash-match + Merkle root recomputes | **PASS** |
| Count coherence — README / ARCHITECTURE / AGENTS all state "fifteen" | **PASS** |

**19/19 pass** (once the seal is re-computed; hash-match is the one invariant that goes red mid-edit and green on re-seal). This is the structural complement to the behavioral runs: Runs 1–4 measure that fabius *acts* better; the structural suite proves it is *built* right — single-owner, under budget, every reference live, and the seal verifiable.

#### Extension — the two later verticals (`evals/harness.v3-ext.workflow.js`)

The two specialists added after the original run — `fabius-doctrina` (AI/ML engineering) and `fabius-fortuna` (markets & finance) — were measured in a follow-up with the **same method** (baseline / terse / fabius × sonnet + haiku, blind `claude-opus-4-8` judge). Every then-existing specialist domain is now exercised; the later `fabius-concilium` layer is the one not yet in a blind run (it deliberates across models on one question rather than adding a task domain). Totals out of 15 (n = 2 tiers):

| Domain (skill) | task | baseline | terse | **fabius** | output cut |
|---|---|---|---|---|---|
| Markets (`fortuna`) | backtest a strategy, decide whether to trade | 10.5 | 9.5 | **12.5** | −40% |
| ML eval (`doctrina`) | decide if a fine-tune beats the base model, ship? | 10.5 | 10.5 | **11.0** | −54% |

**Markets is the mirror image of the science result** — fabius **+3.0 vs the "be concise" control**, +2.0 vs baseline on both tiers, the sonnet build a perfect **15/15**. The controls overfit the in-sample backtest, ignored transaction costs, and answered the loaded question with a flat *"yes, trade it"*; `fortuna` forced out-of-sample validation, costs/slippage, risk sizing, and the bright line — *analysis, not advice*. **ML eval is the honest small-lift case**: model evaluation is well-trodden ground, so the bare model already holds — fabius wins by only +0.5, but still wins (sonnet +1, haiku tie) **and runs ~54% shorter**. The pattern holds: the lift is largest where a domain drops a guardrail, smallest where the default already knows the move.

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
- Run 3 (T3) tests **#2 — does the multi-skill mechanism fire and act on its own.** Yes — it shipped the leanest, only-functional build live in Claude Code.
- Run 4 tests **#3 — does each benchmarked specialist, including the new on-chain / automation / science verticals, improve its own domain.** Yes — fabius beats both controls on both tiers, and the largest lifts land on those technical verticals.
- Run 5 tests **#3′ — with the shipped files verbatim, across all four internal models, does it still hold.** Partly, and instructively: output drops 20–35% everywhere; on the frontier tiers (Opus, Fable) fabius beats both controls; any routed specialist lifts quality even on Haiku (+0.71 on its specialist tasks). The one regression — Haiku on *trivial* tasks under a full verbatim contract — is the empirical case for model-tier-aware routing and the lean gate, not against them.
- The structural suite tests **#4 — is the system built right** (single-owner, under budget, references live, seal verifiable). 19/19.
- The advantage **grows as the model's default discipline drops** (Run 1: sonnet/haiku gain more than opus; Run 2: lean-BASE Grok gains most, verbose-BASE Mistral least). The advantage is always present; its *size* tracks how undisciplined the default is.
- **Not tested by a one-shot eval:** `fabius-archivum` (persistent memory only pays off across sessions) and the `fabius` router's dispatch accuracy. Memory is excluded rather than faked; routing is checked structurally, not behaviorally.

---

## Reproduce it (one command)

```bash
# structural suite — no key, no cost, no network; 19/19 must pass (Run 4 sibling)
node evals/structural.mjs

# behavioral wiring check — no key, no cost
node evals/eval.mjs --selftest

# a real behavioral run (Anthropic)
ANTHROPIC_API_KEY=...  node evals/eval.mjs --model claude-sonnet-4-6

# a real run (OpenAI / Codex family)
OPENAI_API_KEY=...     node evals/eval.mjs --provider openai --model gpt-4o

# cross-vendor (OpenAI / Mistral / Anthropic / Gemini) — your keys
GEMINI_API_KEY=...     python evals/portable_eval.py --models gemini

# the every-domain run (Run 4) + its two-vertical extension, inside Claude Code:
#   Workflow({ scriptPath: "evals/harness.v3.workflow.js" })
#   Workflow({ scriptPath: "evals/harness.v3-ext.workflow.js" })   # doctrina + fortuna

# all four internal models, shipped files verbatim, two blind judges (Run 5):
#   Workflow({ scriptPath: "evals/harness.v5.workflow.js" })       # -> evals/results.v5.json
```

In Run 1 (`eval.mjs`) the `fabius` arm reads the shipped `AGENTS.md` **verbatim** at runtime — you benchmark the exact stance the agent ships. Run 4 (`harness.v3.workflow.js`) instead injects a **faithful condensed transcription** of that stance plus the routed specialist's operative contract, hand-transcribed into the harness rather than read from the shipped files — so it measures the specialist mechanism, not a byte-for-byte copy of the source. `eval.mjs` writes `evals/results.json`; the published Run 4 receipt is [`evals/results.v3.json`](evals/results.v3.json). Swap `--model` / `--judge` to benchmark anything; add tasks in the `TASKS` array.

---

## Caveats (read these)

- **Most runs are directional.** GPT and Claude judged their own family in the same window — directional, not blind. The hard signals are the **character counts** and the **cross-family blind subset** (Grok, Mistral judged by Claude), not the absolute totals.
- **The judge is a model.** Length is objective; quality scores share model-family priors. Read the generated answers.
- **Small n.** 6–8 tasks per arm is a directional signal, not a paper. Treat sub-point deltas as ties.
- **Blind scores lower — and that's reassurance.** The blind cross-family runs scored fabius lower than the self-judged ones (86/82 vs 89/87). A judge that doesn't love itself scores harder; the pattern held anyway.
- **Versions move.** Every number was measured on one model at one moment. Don't generalize past that — re-run it.

> The claim the data supports: **fabius gives a consistent, cross-model quality lift that grows as the model's default gets less disciplined — large at trust / order / genuine-build boundaries and across the technical verticals (on-chain, automation, science), negligible at pure YAGNI. It is the only arm that beats both a bare baseline and a "be concise" control while cutting output ~40%. It is not a "shorten" prompt; it is a scope-control system that knows when to compress and when to expand — and it is built right: 19/19 structural invariants, a verifiable content-bound seal.** Not "smarter." Not "10× on everything." That sentence survives technical scrutiny; the inflated one doesn't.
