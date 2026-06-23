# Fabius — agent-research foundations

The Core Knowledge Base behind fabius's [routing policy](routing-policy.md). One entry per paper: its single strongest pattern, how fabius uses it, and an honest tag. Loaded on demand — the operational rules ride in context; this is the *why*, pulled when a decision needs its grounding.

**Honesty key.** **direct** = the agent-research paper makes this claim about LLM agents / reasoning / memory. **analogy** = the shape is borrowed from another domain (generative-model sampling math, or a non-agent setting) and the paper does not claim it about agents — fabius takes the shape, not a measured agent result. The full ledger is in [RESEARCH.md](../../../RESEARCH.md).

---

## Tier 1 — The core agent loop

### Toolformer (Schick et al., 2023) · analogy · backs R3, M1
A self-supervised filter for *when* a tool call is worth making, with no human labels: the model samples candidate API calls in text, executes them, and **keeps a call only if its result lowers next-token loss on the gold continuation** versus not calling. Calls that don't reduce loss are dropped as overhead. The transferable principle is the loss-reduction gate — a tool or sub-agent earns its invocation only by reducing expected error, not by appearing diligent.
→ **fabius:** the routing test (R3) and cohors's single-vs-multi gate (M1) — route only when you can *name the wrong answer the call prevents*. **Analogy:** Toolformer computes the filter against the gold continuation at *training* time; fabius lacks that at inference, so it borrows the spirit, not a runnable metric.

### ReAct (Yao et al., 2022) · direct · backs R5
Interleaving reasoning with grounded actions beats either alone. Reason-only hallucinates (nothing checks it against the world); act-only thrashes (no plan). ReAct alternates **Thought → Action → Observation**, and each next thought must incorporate the real observation before proceeding. Grounding reduces hallucination and makes the trajectory steerable.
→ **fabius:** the per-action grounding gate (R5) — never emit an action on an assumed result; one Thought → one Action → read the real Observation. The two failure modes map to two guardrails; the cycle cap mirrors disciplina's 3-strike re-plan. This is the literature behind fabius's Scout→Strike→Prove loop at per-action granularity.

### Reflexion (Shinn et al., 2023) · direct · backs R8, M4
An agent improves **without weight updates** by keeping verbal self-reflections: an Actor attempts → an Evaluator scores (ideally an external, verifiable signal) → a Self-Reflection model writes a post-mortem appended to context for the next attempt. The "learning" lives in the prompt, which is why it works for a frozen model. Success rises across trials but saturates — value is front-loaded in the first few retries.
→ **fabius:** reflect-then-retry with escalation (M4) and the signal-gated loop (R8) — structured reflection prepended to the retry, hard cap ~3, stop when a reflection yields no new hypothesis. Lessons accumulate in [`failures.md`](failures.md).

### Generative Agents (Park et al., 2023) · analogy · backs M8
A memory-stream loop: observations append to a stream; retrieval scores each memory by **recency** (exponential decay) · **importance** (LLM-assigned 1–10) · **relevance** (embedding similarity), top-k. Reflection: when accumulated importance crosses a threshold, the agent synthesizes higher-level insights written back as retrievable memories. Produces believable long-horizon behavior that flat keyword recall can't.
→ **fabius:** the archivum recency + load-bearingness tie-break and the synthesize-grown-logs move (M8). **Analogy:** the scheme is for a simulated agent's *observation stream*, not a curated markdown engineering wiki — fabius keeps the recency tie-break and **drops** the numeric importance tag and threshold counter as over-engineering.

---

## Tier 2 — Memory

### MemGPT (Packer et al., 2023) · direct · backs R9, M7
Treat the LLM like an **OS managing a memory hierarchy**: a small fast main context (the window) backed by a large external store, with the model issuing function calls to page across the boundary. On overflow it **EVICTS** (summarize/persist + free the window); on a miss it **RECALLS** (deliberate retrieval). Paging is an explicit, logged action; eviction is lossless because the store is addressable. Beats stuff-everything once the corpus exceeds the window.
→ **fabius:** archivum two-tier paging (R9, M7) — working context = main, the wiki = external store; `write = EVICT`, `read = RECALL`, everything addressable by `[[slug]]`; over-budget → summarize-then-link.

### LongMem / external-memory for LLMs · direct · backs R9
The long-context problem reframed: rather than stretch the window, attach a **decoupled external memory** that is written to and retrieved from on demand, so recall cost doesn't scale with the prompt. Confirms the architectural split fabius already runs — the wiki + vector index is the long-term store; the window holds only the working slice.
→ **fabius:** reinforces retrieve-on-demand (R9) and the archivum split — don't pay for context you can page.

### A Survey on Memory for LLM Agents · direct · backs R9, M7
Frames the central decision: short-term (in-context) vs long-term (persisted), and **retrieval-on-demand vs context-stuffing**. Catalogs operations (write / read / manage-forget) and retrieval strategies (symbolic vs dense vs **hybrid**), arguing the architecture is governed by corpus size and query type — not by maximizing what's loaded. Hybrid *symbolic-narrow-then-dense-rerank* is the scalable default.
→ **fabius:** the archivum backbone — retrieve-not-stuff, "symbolic first, dense-rerank only the slice," and parcus's "don't build the vector engine until corpus size or semantic queries demand it."

---

## Tier 3 — Planning

### Tree of Thoughts (Yao et al., 2023) · direct · backs R7
Deliberate search over a tree of thoughts with a **value function that scores partial solutions**, enabling lookahead, evaluation, and backtracking. Four knobs: decompose, generate k, evaluate (value or vote), search (BFS/DFS + prune top-k). The decisive point: **branching pays only where a half-finished candidate can be judged** (Game-of-24: ~4% with chain-of-thought → ~74% with ToT). Cost ≈ branching-factor × tokens, so it's a *worse* default than a single chain without an evaluator.
→ **fabius:** the branch-on-evaluability gate (R7) — single-path by default, escalate to a scored tree only when a partial-state evaluator exists and early mistakes are costly; cohors runs generate→score→prune→expand under a budget cap.

### Graph of Thoughts (Besta et al., 2023) · analogy · backs M2
Generalizes ToT to an arbitrary **directed graph**: thoughts are vertices, edges are transformations — crucially **aggregation** (merge several thoughts) and **refinement** (improve in place). Unlocks map-reduce reasoning: fan out, then fuse. Measured on sorting *inside one LLM's reasoning* (~62% quality over ToT, >31% cheaper) — not on multi-agent orchestration.
→ **fabius:** cohors topology choice (M2) — combinable sub-results → parallel workers + a reducer (a graph); competing branches → best-of-k (a tree). **Analogy:** the sorting numbers are intra-LLM thought-graph results, transplanted to agents.

### Chain of Abstraction (Gao et al., 2024) · analogy · backs R6
Decouple **planning from tool-binding**: write a complete reasoning chain with abstract placeholders for tool results, then a separate step fills them by calling tools. The tool-free skeleton means calls stop serializing the reasoning — independent calls parallelize (~1.4× faster), with accuracy gains on multi-step math and Wiki-QA; a wrong tool result invalidates only its placeholder.
→ **fabius:** disciplina's "plan in placeholders, bind tools last" (R6); lets cohors parallelize and re-run one failed tool without re-planning. **Analogy:** the 1.4× was on single-tool tasks, not agent-spawning fan-out — the orchestration transfer is unmeasured here.

---

## Tier 4 — Flow & decision math (all analogy)

> These are **generative-model sampling math**, not agent research. fabius borrows the *shapes* as decision heuristics. The source papers prove their claims about numerical sampling of learned vector fields and image fidelity/diversity — **never** about agents, routing, or verification budgets. Every rule below is labelled analogy with its caveat.

### Flow Matching (Lipman et al., 2023) · analogy · backs R4
The intractable **marginal velocity equals the posterior average of tractable conditional velocities** — i.e., defer the hard commitment and average candidates until the signal sharpens.
→ **fabius:** scout-wide-before-committing (R4). **Analogy:** an identity about learned vector fields; the paper never transfers it to route selection. fabius's honest core for R4 is its own maxim, scout wide / strike narrow.

### Consistency Models (Song et al., 2023) · analogy · backs M3
A one-shot map to the clean sample, plus a bounded few-step dial: **overhead is a function of measured insufficiency, not ritual.** The mental model: an optimal amount of correction exists *only because the base map is imperfect* — so spend correction where imperfection is measured.
→ **fabius:** verification depth scaled to measured per-route failure (M3) — more correction on routes that fail, none on routes that never do.

### Classifier-Free Guidance (Ho & Salimans, 2022) · analogy · backs R10
Extrapolating toward the conditional (guidance weight **w > 1**) raises fidelity but cuts diversity — a measured fidelity/diversity trade with a sweet spot at modest w.
→ **fabius:** instruction emphasis ≈ guidance weight (R10) — hard-steer narrow contracts, say-it-once on breadth tasks. **Analogy:** CFG measures Inception-Score-up / recall-down in *image* sampling; "emphasis ≈ w" is a translation. The verifiable core: emphasis trades breadth for adherence — measure both.

---

## Tier 5 — Self-improvement

### Self-Refine (Madaan et al., 2023) · direct · backs R8
One frozen LLM improves its output via **generate → self-critique → refine**, same model for all three roles, no oracle. Because the signal is self-critique with no external check, gains can plateau or regress — **most lift lands in the first 1–2 passes**, and the critique must be specific and actionable to help at all.
→ **fabius:** the SOFT-signal tier of R8 — cap self-critique at 1–2 passes and require a specific cited critique. Where a HARD oracle exists, prefer the Reflexion path; where no signal exists, parcus blocks the loop and routes to human review.

### Voyager (Wang et al., 2023) · direct · backs M6
Lifelong skill acquisition via a growing **library of executable, documented, retrieval-keyed skills**: solved tasks are stored and composed by future tasks instead of re-derived, so capability compounds. The hard gate: a skill is added **only after self-verification** confirms it works; failures yield feedback, not a library entry.
→ **fabius:** archivum as a skill library (M6) — verify-then-store, retrieve-before-plan, supersede-don't-duplicate; failures leave anti-pattern notes. Turns per-task reflection into compounding cross-session leverage. The closest paper to fabius's own skills model.

---

## Tier 6 — Architecture & surveys

### Wang et al. — A Survey on LLM-Based Autonomous Agents · direct · backs R1
Decomposes an autonomous agent into four modules — **Profile, Memory, Planning, Action** — of which Memory / Planning / Action are the universal capability axes (Profile is configuration). A descriptive, field-wide spine, not one author's preference.
→ **fabius:** the three-axis routing taxonomy (R1) — Memory→archivum, Tools/Action→cohors, Planning→disciplina, Profile→cohors's agent schema, zero axes→parcus. Converts specialist selection into a reproducible classification published as the routing rationale.

### DSPy (Khattab et al., 2023) · direct · backs M5
Program with LLMs **declaratively**: each step is a typed **signature** (in→out), with a **metric** and real examples; a compiler searches prompt configs (instructions + bootstrapped demos) to maximize the metric on held-out data. Prompt text becomes a compiled, replaceable artifact — improvements measured, not vibes.
→ **fabius:** cohors's contract-first + the metric-delta gate (M5) — accept a prompt change only on a measured held-out improvement. Enforces fabius's "measured, not claimed" bar on prompt engineering itself, and grounds the eval harness's skill-vs-baseline pattern.

### Toward Efficient Agents (efficiency surveys) · analogy · backs R2
The **cost–capability frontier**: capability scales sub-linearly with machinery — bigger models, more agents, more tool calls, longer chains buy capability with steeply diminishing returns while cost (tokens, latency, coordination) climbs. Flags multi-agent orchestration and long deliberation as the highest-cost, most over-used rungs. Efficient design = the smallest config clearing the bar (the **knee**, not the tail).
→ **fabius:** parcus's economic trim and the capability ladder (R2) — `inline < one tool < retrieval < plan < single subagent < swarm`; add the lowest sufficient rung. **Analogy:** the concave shape is directional only; fabius targets the knee qualitatively and measures real cost per task.

### LLM-Agent-Papers / Awesome-Agent-Papers (living indexes) · reference
Community-maintained catalogs of the agent literature, organized by capability. fabius treats them as the lint backstop: when a real failure exposes a gap rules R1–R10 / M1–M8 don't cover, these are where the next pattern is sourced — and the new rule is added to [`routing-policy.md`](routing-policy.md) only then.
