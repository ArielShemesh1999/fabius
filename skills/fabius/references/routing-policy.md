# Fabius — routing policy

The decision policy. How fabius chooses a route — which layer / sub-agent, when, and why — and how much machinery to deploy. **Scout wide, strike narrow. YAGNI.**

Loaded on demand by `fabius` (the router). It is small on purpose: every rule here is *operational* — it changes a real decision. Background reading (the papers each rule is drawn from) lives in [`agent-research.md`](agent-research.md) and is pulled only when needed. The lesson log [`failures.md`](failures.md) grows from real incidents, never from anticipation.

> **Honesty.** Each rule names its source. **direct** = the cited agent-research paper makes this claim. **analogy** = the shape is translated from another domain (generative-model sampling math, or a non-agent setting) and the paper does *not* claim it about agents — fabius borrows the shape, not a measured result. Analogy rules carry their caveat inline. Figures (`assets/fig-*.svg`, explained in [RESEARCH.md](../../../RESEARCH.md)) are illustrative shapes, not fabius measurements.

---

## Decision rules — how to route

### R1 · Classify on three axes before routing
Open every non-trivial task by naming its load on three axes, then route each loaded axis to its layer:
- **Memory** — spans sessions, or a fact/decision worth keeping? → `fabius-archivum`
- **Tools / Action** — needs external state, or a computation the model botches? → `fabius-cohors` (a tool; a *second agent* only when work splits)
- **Planning** — multi-step with dependencies? → `fabius-disciplina`

Zero axes loaded → stay in the lean `fabius-parcus` core. Publish the classification as the routing rationale.
*Fires: first move on any non-trivial task, before picking a layer or spawning anything.*
*Source: Wang et al., survey of LLM autonomous agents (Profile/Memory/Planning/Action) — **direct**.*

### R2 · Climb the capability ladder one rung; never jump to the top
Add the smallest capability rung the classification demands and stop:
`parcus inline → one tool call → archivum retrieval → disciplina plan → single subagent → cohors swarm`.
Never instantiate rung N+1 until rung N is shown insufficient on **this** task. (Figure: `fig-capability-ladder.svg`.)
*Fires: choosing how much machinery to deploy — especially when tempted to open a swarm.*
*Source: efficiency surveys (cost–capability frontier) — **analogy**. The diminishing-returns shape is directional; the knee is qualitative, not fitted. Measure real cost per task; defer the swarm gate to cohors's decomposability test, not to cost.*

### R3 · Call a tool/sub-agent only when it measurably beats inline
Route to a tool, sub-agent, or specialist only when you can **name the specific wrong answer the call prevents**: stale/external state, a computation you'd get wrong, an independent reviewer who didn't write the artifact, or context past one window. If the model already knows it reliably, answer inline. (Figure: `fig-tool-value-gate.svg`.)
*Fires: any routing decision — tool vs inline, spawn vs do-it-yourself, escalate vs handle in core.*
*Source: Toolformer — **analogy**. Toolformer's loss-reduction filter is computed against the gold continuation at training time, which fabius lacks at routing time. Borrow the spirit (a call must lower expected error), not a runnable metric.*

### R4 · Scout wide before committing the route
On an ambiguous task, keep **2–3 candidate routes alive** and let cheap scouting evidence average them; collapse to one route only once the signal sharpens. Don't guess the route on turn one.
*Fires: the single correct specialist isn't knowable up front.*
*Source: Flow Matching (marginal velocity = posterior average of conditional velocities) — **analogy**. That identity is sampling math about learned vector fields; the paper never transfers it to route selection. The honest core is fabius's own maxim: scout wide, strike narrow.*

### R5 · Reason → act → observe; never act on an assumed result
In multi-step tool/sub-agent work, gate every action on the **actual observation** before it: one Thought (why this action, what would confirm it) → one Action → read the real result → next Thought. Never stack a second action on an assumed result. After ~3 cycles with no movement toward the verify condition, stop and re-plan.
*Fires: any task interleaving thinking with tool calls / dispatch / lookups where a later step depends on an earlier real result.*
*Source: ReAct — **direct**. This is the per-step gate (catches mid-chain hallucination); `fabius-disciplina`'s prove-before-done is the terminal gate.*

### R6 · Plan in placeholders; bind tool calls only after the plan is fixed
For any task that will call ≥2 tools/agents, finish a **tool-free plan** that names each tool *output* as an abstract placeholder before binding a single call. Then: the skeleton can be grilled up front, independent calls fan out in parallel, and a wrong result invalidates only its placeholder (re-run that one tool, keep the plan). (Figure: `fig-plan-then-bind.svg`.)
*Fires: planning a task that will call ≥2 tools/agents, especially with cross-step dependencies.*
*Source: Chain of Abstraction — **analogy**. The ~1.4× speedup was measured on single-tool math/QA, not multi-agent fan-out. The decoupling is sound; the transferred parallel benefit is unmeasured here.*

### R7 · Branch only when a cheap evaluator can rank unfinished candidates
Spawn a branch-score-prune search (a scored tree) **only when a cheap evaluator can rank half-finished candidates** — a test, a lookahead, a value heuristic, an "is this promising?" vote. Absent that evaluator, no branching factor helps: collapse to a single chain-of-thought / plan pass. The cost of a wrong commit sets only *how wide/deep* to search, not *whether* to branch. (Figure: `fig-branching-accuracy.svg`.)
*Fires: deciding single-path vs branching swarm in planning/brainstorm.*
*Source: Tree of Thoughts — **direct** (Game-of-24: 4%→74% via partial-solution scoring). The accuracy-vs-b curve in the figure is a constructed illustration ToT does not publish.*

### R8 · Reflect on a verifiable signal, not on vibes; signal type sets the budget
Enter a generate→improve loop **only when an evaluator yields a specific, attributable critique** (cites the exact locus + the fix). Let the signal set the budget:
- **HARD oracle** (test / compiler / linter / schema) → iterate aggressively (cap ~3).
- **SOFT self-critique** → cap at 1–2 passes, and only with a specific cited critique.
- **No critique signal** → ship once, route to human review. Don't manufacture iterations.
(Figure: `fig-reflection-iteration.svg`.)
*Fires: deciding whether a refine loop is justified and how long.*
*Source: Reflexion + Self-Refine — **direct**. Both are agent self-improvement papers; the diminishing-returns shape is their own finding. The caps (~2 soft, ~3 hard) are operational heuristics.*

### R9 · Retrieve on demand — read the index, page in only the matching slice
On any `fabius-archivum` read, narrow through the index to the matching slice and load **only those pages**. If the narrowed set still exceeds the context budget, **summarize-then-link** rather than inlining. Never `cat` a whole page or directory "just in case." (Figure: `fig-recall-context.svg`.)
*Fires: any memory read — session start, a query against a growing base, "what did we decide about X" — and the moment you're tempted to cat a `wiki/` dir.*
*Source: MemGPT + agent-memory surveys — **direct**. Read-the-index-first already ships in archivum; the load-bearing addition is the over-budget handler (summarize-then-link).*

### R10 · State a constraint once on breadth; hard-steer only narrow contracts
Steering a sub-agent *harder* (repeat / stack / rubric-load a constraint) buys tighter adherence to one axis at the cost of breadth and over-literalness. So on **breadth tasks** (brainstorm, scout, design-explore, fan-out) say it once; reserve hard steering for **narrow contracts** (format, security, output shape). When a route turns rigid, *loosen* the emphasis rather than add more. (Figure: `fig-emphasis-tradeoff.svg`.)
*Fires: tempted to strengthen instruction-following by piling on emphasis — especially after a specialist ignored a constraint once.*
*Source: classifier-free guidance (the w>1 fidelity/diversity trade) — **analogy**. CFG measures image-sampling fidelity vs diversity; "instruction emphasis ≈ guidance weight" is a translation, no agent claim. The verifiable core: emphasis trades breadth for adherence — measure both. Maps to scout-wide (low) / strike-narrow (high).*

---

## Orchestration & memory rules — how to manage

These extend the routing decision into `fabius-cohors` (orchestration) and `fabius-archivum` (memory).

- **M1 · Spawn a second agent only when it prevents a named error.** Stay single unless work splits into independent parallel pieces, a step needs an independent reviewer who didn't write the artifact, or context exceeds one window. Name the wrong answer the second agent prevents; if you can't, don't spawn. *(cohors · Toolformer-spirit analogy + cohors single-vs-multi gate)*
- **M2 · Tree vs graph — add a reducer only when partials MERGE.** Combinable sub-results (research synthesis, audit union, sort/merge, dedup) → parallel workers + an explicit reducer/synthesis agent. Competing branches → best-of-k, skip the merge. *(cohors · Graph of Thoughts — analogy; its sorting numbers are intra-LLM, not multi-agent)*
- **M3 · Scale verification depth to MEASURED per-route failure.** Set corrector/verify scaffolding from a specialist's measured pass rate — more where it has been failing, none on routes that never fail (drop the corrector, YAGNI). Update the rate from each verified outcome. *(cohors · Consistency-Models / sampling-σ analogy: "an optimal overhead exists only because the model is imperfect")*
- **M4 · Reflect-then-retry, escalate when hypotheses run out.** On a verifiable failure, write a one-paragraph reflection (what was tried · the failure signal · inferred cause · one changed action) and prepend it to the retry. If a reflection repeats the prior cause with no new hypothesis, stop and escalate to a human (hard cap ~3). *(cohors/disciplina · Reflexion — direct)*
- **M5 · Specify agents as contracts; accept rewrites only on a metric delta.** Treat any agent/skill prompt as replaceable behind its typed signature + success metric. Accept a prompt rewrite only when a checkable metric on held-out real examples improves — never on better-sounding wording. Prefer bootstrapped demonstrations over long hand-written instructions. *(cohors · DSPy — direct)*
- **M6 · Promote verified solutions to a reusable skill library.** After a self-contained sub-problem is solved **and verified**, promote it to archivum as a named, interface-typed reusable skill; failures leave an anti-pattern note. On every new task, query archivum first and compose existing skills before planning from scratch; supersede, don't duplicate. *(archivum/cohors · Voyager — direct)*
- **M7 · Page memory explicitly — write only decision-changing facts.** `write = EVICT` (flush durable facts to a page + log line under window pressure / at session end); `read = RECALL` (explicit index→page read on a miss, logged as QUERY). Everything addressable by `[[slug]]`. *(archivum · MemGPT + memory surveys — direct)*
- **M8 · Rank ties by recency and load-bearingness; synthesize grown logs.** When many index entries tie on relevance, break the tie by `updated` date and how load-bearing the page is. Fold a grown batch of un-synthesized log lines up into a synthesis page — no numeric importance tag, no threshold counter. *(archivum · Generative Agents — analogy: proposed for a simulated observation stream, not a curated wiki; fabius drops the numeric machinery)*

---

## Out of scope for this file (on purpose)

- **The papers themselves** → [`agent-research.md`](agent-research.md), pulled on demand. Not here.
- **The memory substrate** (storage, eviction mechanics, vector index) → architecture, not policy. The only memory this file touches is the lesson loop (R8, M4).
- **A new rule** → added only when a real failure in [`failures.md`](failures.md) proves rules R1–R10 / M1–M8 didn't cover it.
