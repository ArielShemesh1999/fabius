<div align="center">

# The thinking behind fabius

### How fabius decides — grounded in the agent-research canon, stated honestly.

</div>

fabius is a stance, but a stance is only as good as the decisions it makes: *which* layer to route to, *when* to spend a tool call or a second agent, *how long* to keep refining, *what* to load from memory. This document is the reasoning behind those decisions. Each principle is drawn from the agent-research literature, turned into an operational rule in [`routing-policy.md`](skills/fabius/references/routing-policy.md), and — where a relationship is worth seeing — illustrated with a figure.

**The honesty stance, up front.** fabius's quality bar is *measured, not claimed*. Some of the sharpest decision heuristics here are borrowed from a different field — the sampling mathematics of generative models (flow matching, diffusion, classifier-free guidance). Those results are proven about **numerical sampling of learned vector fields and image fidelity**, never about agents. Where fabius uses one, it takes the *shape* of the idea, not a measured agent result, and says so. Every such mapping is tagged **analogy** with its caveat. The full ledger is at the end. The figures are **illustrative shapes of documented principles — not fabius's own measurements** (for those, see [BENCHMARKS.md](BENCHMARKS.md)).

The reading list each rule draws from is summarized in [`agent-research.md`](skills/fabius/references/agent-research.md).

---

## 1 · Route by classification, then climb one rung

Specialist selection should be reproducible, not vibes. fabius opens every non-trivial task by naming its load on three axes — **Memory, Tools/Action, Planning** — the universal capability axes from Wang et al.'s survey of autonomous agents (Profile/Memory/Planning/Action). Memory→`archivum`, Tools→`cohors`, Planning→`disciplina`, none→the lean `parcus` core. The classification *is* the routing rationale **(R1, direct).**

Then it climbs a capability ladder one rung at a time — `inline → one tool → retrieval → plan → single subagent → swarm` — adding the smallest rung the classification demands and stopping **(R2).** The efficiency surveys describe a cost–capability frontier where machinery buys capability with steep diminishing returns; fabius operates at the *knee*, not the tail.

<div align="center">
<img src="assets/fig-capability-ladder.svg" alt="Concave capability-vs-cost curve; fabius stops at the knee, the swarm/long-chain region is over-spend" width="78%" />
</div>

> **Figure 1 — analogy.** The diminishing-returns shape is asserted *directionally* by the efficiency surveys; this exact curve and knee are not fitted to fabius. fabius targets the knee qualitatively and measures real cost per task. The swarm gate is owned by cohors's decomposability test, not by this curve.

---

## 2 · A call must earn its place

Every tool call, sub-agent, or specialist hop is overhead until proven otherwise. Toolformer learned *when* to call a tool with a self-supervised filter: keep a call only if its result **lowers loss on the continuation** — a call that doesn't reduce expected error is dropped. fabius can't run that metric (it's a training-time criterion against the gold answer), so it borrows the spirit and makes it answerable at routing time: **route only when you can name the specific wrong answer the call prevents** — stale state, a computation you'd botch, an independent reviewer, context past one window **(R3, analogy).**

<div align="center">
<img src="assets/fig-tool-value-gate.svg" alt="Step function: route to the call only when expected error-reduction exceeds a threshold; below it is pure overhead" width="78%" />
</div>

> **Figure 2 — analogy.** Toolformer computes ΔL against the gold continuation at training time, which fabius does not have at routing time. The step is conceptual: fabius cannot run this metric, so it asks *"can I name the wrong answer this prevents?"* instead.

When the right route is genuinely unclear, fabius doesn't guess on turn one — it keeps **2–3 candidate routes alive** and lets cheap scouting evidence average them, collapsing to one only as the signal sharpens **(R4, analogy** — the shape of "the marginal is the average of the conditionals" from flow matching; the honest core is fabius's own *scout wide, strike narrow***)**.

---

## 3 · Ground every action; plan in placeholders

Two failure modes haunt multi-step work: reasoning that hallucinates because nothing checks it, and tool-spam that thrashes because nothing plans it. ReAct's answer — **Thought → Action → Observation**, where the next thought must incorporate the *real* observation — is fabius's per-action gate: **never act on an assumed result; read the real one first** (re-plan after ~3 stalled cycles) **(R5, direct).**

For any task that will call ≥2 tools, fabius finishes a **tool-free plan with abstract placeholders** for each tool's output *before* binding a single call (Chain of Abstraction). The skeleton can be grilled up front, independent calls fan out in parallel instead of serializing the reasoning, and a wrong result invalidates only its placeholder **(R6, analogy).**

<div align="center">
<img src="assets/fig-plan-then-bind.svg" alt="Serial chain latency rises linearly with tool calls; plan-then-bind stays nearly flat by overlapping independent calls" width="78%" />
</div>

> **Figure 3 — analogy.** Chain of Abstraction measured ~1.4× on single-tool math/Wiki-QA, not on agent-spawning fan-out. The flat curve is the model's prediction, unmeasured in fabius's multi-agent setting; the two lines converge when every call strictly depends on the previous one.

---

## 4 · Branch only when you can score a half-finished idea

Branching search (Tree of Thoughts) is the most over-reached tool in the agent toolbox. ToT's decisive finding: branching pays **only where a partial solution can be judged** — Game-of-24 leaps from ~4% to ~74% *because* a half-built expression is scorable. Without that evaluator, paying b× the tokens buys nothing. So fabius defaults to a single chain and escalates to a scored tree **only when a cheap evaluator can rank unfinished candidates** **(R7, direct).** The cost of being wrong sets how *wide* to search — never *whether* to.

<div align="center">
<img src="assets/fig-branching-accuracy.svg" alt="With an informative evaluator, accuracy peaks at an interior branching factor; without one, more branching only loses depth" width="78%" />
</div>

> **Figure 4 — illustrative.** ToT demonstrates the evaluator-gated benefit empirically, but does not publish this accuracy-versus-branching curve; the interior optimum is a constructed model. No evaluator → stay single-path.

---

## 5 · Refine on a real signal, and know when to stop

Reflexion showed an agent can improve **without fine-tuning** by writing a verbal post-mortem and prepending it to the next attempt — but the gains saturate fast, so the value is front-loaded. Self-Refine showed the same loop with *self*-critique (no oracle) plateaus or regresses after 1–2 passes. fabius reads both as one rule: **enter a refine loop only on an attributable critique** (cite the exact locus + fix), and let the signal type set the budget — a HARD oracle (test, compiler, schema) licenses ~3 aggressive iterations, a SOFT self-critique caps at 1–2, and **no signal means ship once and route to human review** **(R8, direct).** Failed routes leave a lesson in [`failures.md`](skills/fabius/references/failures.md) — the system learns in the prompt, not the weights.

<div align="center">
<img src="assets/fig-reflection-iteration.svg" alt="A hard-oracle reflection curve keeps rising and saturates late; a soft self-critique curve plateaus and dips after two passes" width="78%" />
</div>

> **Figure 5 — empirical shape.** The diminishing-returns curves are Reflexion's and Self-Refine's own reported finding. The specific caps (~2 soft, ~3 hard) are fabius's operational heuristics, not derived constants.

---

## 6 · Memory is paged, not stuffed

MemGPT framed the LLM as an **operating system over a memory hierarchy**: a small fast window backed by a large addressable store, with explicit `EVICT` (flush to a page under pressure) and `RECALL` (retrieve on a miss). The memory surveys add the governing decision — *retrieval-on-demand beats context-stuffing* once the corpus exceeds the window, with hybrid symbolic-then-dense as the scalable default. fabius's `archivum` is exactly this: read the **index** first, page in only the matching slice, and if it still overflows the budget, **summarize-then-link** rather than inlining — never `cat` a directory "just in case" **(R9, M7, direct).**

<div align="center">
<img src="assets/fig-recall-context.svg" alt="Recall rises fast as the matching slice loads then plateaus; stuffing everything degrades past the context window" width="78%" />
</div>

> **Figure 6 — illustrative.** MemGPT shows paging beats stuffing once the corpus exceeds the window. The exact inflection is conceptual; fabius has no measured recall curve of its own.

Two more memory rules compound it: solved-and-**verified** sub-problems are promoted to a reusable named skill and **retrieved before planning** the next task (Voyager's skill library, M6), and relevance ties break by recency + load-bearingness with grown logs folded up into synthesis pages (Generative Agents, M8 — analogy; fabius keeps the recency tie-break and drops the numeric importance machinery).

---

## 7 · Steer narrow contracts hard; say breadth tasks once

Classifier-free guidance trades fidelity for diversity: extrapolating harder toward the condition (weight w > 1) sharpens adherence but collapses variety. fabius reads instruction-emphasis the same way — **piling on emphasis buys adherence at the cost of breadth and over-literalness.** So it hard-steers narrow contracts (format, security, output shape) and says breadth tasks (brainstorm, scout, design-explore) *once*; when a route turns rigid, it *loosens* rather than adds **(R10, analogy).** This is scout-wide / strike-narrow expressed as a control knob.

<div align="center">
<img src="assets/fig-emphasis-tradeoff.svg" alt="As instruction emphasis rises, adherence increases and breadth falls; their product peaks at modest emphasis" width="78%" />
</div>

> **Figure 7 — analogy.** Classifier-free guidance measures Inception-Score-up / recall-down in *image* sampling; the papers make no claim about prompts or agents. The verifiable core is only that emphasis trades breadth for adherence — measure both.

---

## 8 · Orchestration — the management rules

The same discipline governs how fabius runs other agents (`fabius-cohors`):

- **Spawn only to prevent a named error** (M1, Toolformer-spirit) — single agent unless work splits, needs an independent reviewer, or overflows one window.
- **Tree vs graph by whether partials merge** (M2, Graph of Thoughts) — combinable results get a reducer; competing branches get best-of-k.
- **Verification depth from measured failure** (M3, Consistency-Models analogy) — more correction where a route has been failing, none where it never fails (YAGNI).
- **Reflect-then-retry, escalate when hypotheses run out** (M4, Reflexion).
- **Agents are contracts; accept rewrites only on a metric delta** (M5, DSPy) — fabius's "measured, not claimed" bar applied to prompt engineering itself.

---

## Honesty ledger

**Direct mappings** (the source paper makes a claim about LLM agents / reasoning / memory that fabius applies almost verbatim): ReAct's reason→act→observe grounding contract (R5); Tree of Thoughts' branch-only-when-partials-are-judgeable gate (R7); Reflexion + Self-Refine's verifiable-signal reflection loop with diminishing returns (R8, M4); Voyager's verify-then-store skill library with retrieve-before-plan (M6); DSPy's contract-first + metric-delta gate (M5); MemGPT's explicit paging / evict–recall and retrieve-over-stuff (R9, M7); the agent-memory surveys' read/write/reflect/forget operations and the Wang Profile/Memory/Planning/Action taxonomy that anchors the three-axis router (R1).

**Analogy mappings** (the source proves something about a *different* domain — generative-model sampling math or a non-agent setting — and fabius transfers the shape, not a measured agent result): Toolformer's loss-reduction filter is a training-time criterion against the gold continuation, uncomputable at fabius's routing time, so R3/M1 borrow only its spirit; the efficiency surveys assert diminishing returns directionally but fit no curve for fabius, so the capability-ladder knee (R2, Fig 1) is qualitative; Chain of Abstraction measured ~1.4× on single-tool math/QA, not agent-spawning fan-out, so R6/Fig 3's parallel benefit is unmeasured here; Graph of Thoughts' ~62% / −31% numbers are intra-LLM thought-graph sorting results transplanted to agent topology (M2); Generative Agents' recency·importance·relevance + reflection-threshold is for a simulated observation stream, not a curated wiki, so M8 keeps only the recency tie-break and drops the numeric tag; R4 borrows flow matching's *marginal = average of conditionals*; and the three generative-model rules — Consistency Models for verification depth (M3), Flow Matching for scout-wide averaging (R4), Classifier-Free Guidance for instruction emphasis (R10) — are **all** analogies, because those papers prove their claims about numerical sampling of learned vector fields and image fidelity/diversity, and say nothing about agents, routing, or verification budgets.

Every figure caption repeats this: Figures 4 and 6 are illustrative shapes of empirical findings (no fabius measurements); Figure 5 is the empirical shape from Reflexion's and Self-Refine's own results; and Figures 1, 2, 3, 7 are explicitly analogical curves fabius cannot run as metrics. The bar held throughout: **measured where a paper measured it in-domain, analogy everywhere the transfer crosses domains — labelled so no claim is overstated.**

---

## Reproduce the figures

The figures are computed, not drawn — `numpy` → SVG, no external services:

```bash
python3 assets/charts/render_figures.py   # writes assets/fig-*.svg
```

The decision policy itself is [`skills/fabius/references/routing-policy.md`](skills/fabius/references/routing-policy.md); the papers behind it are in [`skills/fabius/references/agent-research.md`](skills/fabius/references/agent-research.md).
