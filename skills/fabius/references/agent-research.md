# Fabius — agent-research foundations

The research notes behind fabius's [routing policy](routing-policy.md) — what our own research pass read for context, finding by finding. The rules themselves are fabius's own: derived from its decision-theoretic core and adversarially verified ([RESEARCH.md](../../../RESEARCH.md) · whitepaper §4). One entry per source: its single strongest pattern, the fabius rule it informed, and where the finding was measured. Loaded on demand — the operational rules ride in context; these notes are pulled only when a decision wants the reading behind it. The *why* of each rule — its derivation, its proof and its ledger label — lives in RESEARCH.md and [routing-policy.md](routing-policy.md), not here.

**Honesty key.** Each note says plainly where its finding was measured. **in-setting** = measured on LLM agents / reasoning / memory, or on routing itself. **adjacent-setting** = measured elsewhere (generative-model sampling math, single-turn QA, a non-agent setting) — read as context for the shape a rule takes, applied as a default, never as a law, and re-checked on the model in hand. A source informs a rule; it does not own it. The rule ledger itself — **derived** / **heuristic** / **measured** per rule — is in [routing-policy.md](routing-policy.md) and [RESEARCH.md](../../../RESEARCH.md).

## The sources — what the research pass read, mapped

The literature our research pass read, at a glance; each row is detailed below, listed against the fabius rule it informed. **foundation** = math background read for the adjacent-setting notes · **reference** = a living index. Rules R1–R13 / M1–M9 are the proven core (all twenty-two derived and adversarially verified, coherence established over the full set); R14–R16 / M10–M13 are the researched frontier layer, held at the working edge. Every arXiv id below was checked against the abstract it cites.

| Source | arXiv | Informed | Setting |
|---|---|---|---|
| ReAct | 2210.03629 | R5 | in-setting |
| Toolformer | 2302.04761 | R3 · M1 | adjacent-setting |
| Reflexion | 2303.11366 | R8 · M4 | in-setting |
| Self-Refine | 2303.17651 | R8 (soft tier) | in-setting |
| Tree of Thoughts | 2305.10601 | R7 | in-setting |
| Reasoning via Planning (RAP) | 2305.14992 | R7 | in-setting |
| Graph of Thoughts | 2308.09687 | M2 | adjacent-setting |
| Chain of Abstraction | 2401.17464 | R6 | adjacent-setting |
| MemGPT | 2310.08560 | R9 · M7 | in-setting |
| LongMem | 2306.07174 | R9 | in-setting |
| Generative Agents | 2304.03442 | M8 | adjacent-setting |
| Voyager | 2305.16291 | M6 | in-setting |
| DSPy | 2310.03714 | M5 | in-setting |
| Autonomous-Agents survey (Wang) | — | R1 | in-setting |
| Toward Efficient Agents (Yang et al., survey) | 2601.14192 | R2 · R11 · M3 | in-setting |
| Memory for Autonomous LLM Agents (Du, survey) | 2603.07670 | R9 · M7 · M8 · M9 | in-setting |
| "Ralph" autonomous-loop technique (Huntley) | github (ralph-claude-code, frankbria) | R12 | in-setting |
| Flow Matching | 2210.02747 | R4 | adjacent-setting |
| Consistency Models | 2303.01469 | M3 | adjacent-setting |
| Classifier-Free Guidance | 2207.12598 | R10 | adjacent-setting |
| MIT diffusion course | diffusion.csail.mit.edu | R4 · M3 · R10 (math) | foundation |
| LLMAgentPapers · awesome-agent-papers · awesome-ai-agents | github | next-rule sourcing | reference |

---

## Tier 1 — The core agent loop

### Toolformer (Schick et al., 2023) · adjacent-setting · informed R3, M1
A self-supervised filter for *when* a tool call is worth making, with no human labels: the model samples candidate API calls in text, executes them, and **keeps a call only if its result lowers next-token loss on the gold continuation** versus not calling. Calls that don't reduce loss are dropped as overhead. The transferable principle is the loss-reduction gate — a tool or sub-agent earns its invocation only by reducing expected error, not by appearing diligent.
→ **fabius:** the routing test (R3) and cohors's single-vs-multi gate (M1) — route only when you can *name the wrong answer the call prevents*. **Setting:** Toolformer computes the filter against the gold continuation at *training* time; there is no gold answer at routing time, so R3 is fabius's own value-of-information gate with the named prevented error as its operational proxy — the source confirms the shape, it does not supply the metric.

### ReAct (Yao et al., 2022) · in-setting · informed R5
Interleaving reasoning with grounded actions beats either alone. Reason-only hallucinates (nothing checks it against the world); act-only thrashes (no plan). ReAct alternates **Thought → Action → Observation**, and each next thought must incorporate the real observation before proceeding. Grounding reduces hallucination and makes the trajectory steerable.
→ **fabius:** the per-action grounding gate (R5) — never emit an action on an assumed result; one Thought → one Action → read the real Observation. The two failure modes map to two guardrails; the cycle cap mirrors disciplina's 3-strike re-plan. It confirms, in-setting, the per-action granularity of fabius's Scout→Strike→Prove loop.

### Reflexion (Shinn et al., 2023) · in-setting · informed R8, M4
An agent improves **without weight updates** by keeping verbal self-reflections: an Actor attempts → an Evaluator scores (ideally an external, verifiable signal) → a Self-Reflection model writes a post-mortem appended to context for the next attempt. The "learning" lives in the prompt, which is why it works for a frozen model. Success rises across trials but saturates — value is front-loaded in the first few retries.
→ **fabius:** reflect-then-retry with escalation (M4) and the signal-gated loop (R8) — structured reflection prepended to the retry, hard cap ~3, stop when a reflection yields no new hypothesis. Lessons accumulate in [`failures.md`](failures.md).

### Generative Agents (Park et al., 2023) · adjacent-setting · informed M8
A memory-stream loop: observations append to a stream; retrieval scores each memory by **recency** (exponential decay) · **importance** (LLM-assigned 1–10) · **relevance** (embedding similarity), top-k. Reflection: when accumulated importance crosses a threshold, the agent synthesizes higher-level insights written back as retrievable memories. Produces believable long-horizon behavior that flat keyword recall can't.
→ **fabius:** the archivum recency + load-bearingness tie-break and the synthesize-grown-logs move (M8). **Setting:** the scheme is measured on a simulated agent's *observation stream*, not a curated markdown engineering wiki — M8 keeps the recency tie-break (a heuristic, order-only after relevance) and **drops** the numeric importance tag and threshold counter as over-engineering (the shortest-description criterion).

---

## Tier 2 — Memory

### MemGPT (Packer et al., 2023) · in-setting · informed R9, M7
Treat the LLM like an **OS managing a memory hierarchy**: a small fast main context (the window) backed by a large external store, with the model issuing function calls to page across the boundary. On overflow it **EVICTS** (summarize/persist + free the window); on a miss it **RECALLS** (deliberate retrieval). Paging is an explicit, logged action; eviction is lossless because the store is addressable. Beats stuff-everything once the corpus exceeds the window.
→ **fabius:** archivum two-tier paging (R9, M7) — working context = main, the wiki = external store; `write = EVICT`, `read = RECALL`, everything addressable by `[[slug]]`; over-budget → summarize-then-link.

### LongMem (Wang et al., 2023; arXiv 2306.07174) · in-setting · informed R9
The long-context problem reframed: rather than stretch the window, attach a **decoupled external memory** that is written to and retrieved from on demand, so recall cost doesn't scale with the prompt. Confirms the architectural split fabius already runs — the wiki + vector index is the long-term store; the window holds only the working slice.
→ **fabius:** reinforces retrieve-on-demand (R9) and the archivum split — don't pay for context you can page.

### Memory for Autonomous LLM Agents — survey (Du, 2026; arXiv 2603.07670) · in-setting · informed R9, M7, M8, M9
Formalizes agent memory as a **write → manage → read loop** coupled to perception and action, over a three-axis taxonomy (temporal scope · representational substrate · control policy). Five mechanism families: **context-resident compression, retrieval-augmented stores, reflective self-improvement, hierarchical virtual context, policy-learned management** — and the engineering realities fabius lives in: write-path filtering, contradiction handling, latency budgets. Names memory as the differentiator for coding agents and open-world games specifically.
→ **fabius:** the whole archivum backbone — write/manage/read = Ingest/Lint/Query; hierarchical virtual context = MemGPT paging (R9, M7); reflective self-improvement = the failures loop (M4, M8); and the externalize-the-corpus rule (**M9**) is exactly *context-resident compression + retrieval store + write-path filtering* applied to fabius's own packaging. Retrieve-not-stuff; build the vector engine only when corpus size or semantic queries demand it (parcus).

---

## Tier 3 — Planning

### Tree of Thoughts (Yao et al., 2023) · in-setting · informed R7
Deliberate search over a tree of thoughts with a **value function that scores partial solutions**, enabling lookahead, evaluation, and backtracking. Four knobs: decompose, generate k, evaluate (value or vote), search (BFS/DFS + prune top-k). The decisive point: **branching pays only where a half-finished candidate can be judged** (Game-of-24: ~4% with chain-of-thought → ~74% with ToT). Cost ≈ branching-factor × tokens, so it's a *worse* default than a single chain without an evaluator.
→ **fabius:** the branch-on-evaluability gate (R7) — single-path by default, escalate to a scored tree only when a partial-state evaluator exists and early mistakes are costly; cohors runs generate→score→prune→expand under a budget cap.

### Reasoning via Planning — RAP (Hao et al., 2023; arXiv 2305.14992) · in-setting · informed R7
Repurposes one LLM as **both world model and reasoning agent**, then runs **Monte-Carlo Tree Search** over the reasoning space: the agent proposes a step, the world-model LLM predicts the resulting state and a task reward, and MCTS expands high-reward branches under an explicit exploration/exploitation balance. It confirms ToT's lesson with a stronger search — branching pays when a **reward/value signal can rank partial states**, and RAP's reward *is* that evaluator (RAP-LLaMA-33B > CoT-GPT-4 on plan generation, +33% relative).
→ **fabius:** the branch-on-evaluability gate (R7) — escalate to a scored tree only when a partial-state evaluator (a reward, a test, a vote) exists; cohors's generate→score→prune→expand is the MCTS shape under a budget cap. The world-model framing also underwrites disciplina's `step → verify` — predict the state a step should reach, then check it against reality.

### Graph of Thoughts (Besta et al., 2023) · adjacent-setting · informed M2
Generalizes ToT to an arbitrary **directed graph**: thoughts are vertices, edges are transformations — crucially **aggregation** (merge several thoughts) and **refinement** (improve in place). Unlocks map-reduce reasoning: fan out, then fuse. Measured on sorting *inside one LLM's reasoning* (~62% quality over ToT, >31% cheaper) — not on multi-agent orchestration.
→ **fabius:** cohors topology choice (M2) — combinable sub-results → parallel workers + a reducer (a graph); competing branches → best-of-k (a tree). **Setting:** the sorting numbers are intra-LLM thought-graph results, not multi-agent measurements; M2 rests on fabius's own associativity argument (a parallel reduction equals the serial fold iff the merge is associative), not on these figures.

### Chain of Abstraction (Gao et al., 2024) · adjacent-setting · informed R6
Decouple **planning from tool-binding**: write a complete reasoning chain with abstract placeholders for tool results, then a separate step fills them by calling tools. The tool-free skeleton means calls stop serializing the reasoning — independent calls parallelize (~1.4× faster), with accuracy gains on multi-step math and Wiki-QA; a wrong tool result invalidates only its placeholder.
→ **fabius:** disciplina's "plan in placeholders, bind tools last" (R6); lets cohors parallelize and re-run one failed tool without re-planning. **Setting:** the 1.4× was on single-tool tasks, not agent-spawning fan-out; R6 rests on fabius's own critical-path bound, and the size of the parallel win on a given task is what the bound predicts, not a figure measured here.

---

## Tier 4 — Sampling & decision math (all adjacent-setting)

> These are **generative-model sampling math**, not agent research — read for context on the decision shapes R4, M3 and R10 take. The source papers prove their claims about numerical sampling of learned vector fields and image fidelity/diversity — **never** about agents, routing, or verification budgets. The rules themselves are fabius's own (R4 and R10 are stated heuristics; M3 is a derived inspection gate); every note below is labelled adjacent-setting with its caveat.
>
> **Math background:** this math is taught rigorously in the **MIT diffusion course** (*diffusion.csail.mit.edu* — lecture notes on flow matching, score/consistency sampling, and guidance). fabius cites it as the background reading for these notes; nothing below is claimed as an agent measurement.

### Flow Matching (Lipman et al., 2023) · adjacent-setting · informed R4
The intractable **marginal velocity equals the posterior average of tractable conditional velocities** — i.e., defer the hard commitment and average candidates until the signal sharpens.
→ **fabius:** scout-wide-before-committing (R4). **Setting:** an identity about learned vector fields; the paper never transfers it to route selection. R4 is fabius's own maxim, scout wide / strike narrow — a stated heuristic; the identity is context for the shape, not its source.

### Consistency Models (Song et al., 2023) · adjacent-setting · informed M3
A one-shot map to the clean sample, plus a bounded few-step dial: **overhead is a function of measured insufficiency, not ritual.** The mental model: an optimal amount of correction exists *only because the base map is imperfect* — so spend correction where imperfection is measured.
→ **fabius:** verification depth scaled to measured per-route failure (M3) — more correction on routes that fail, none on routes that never do. **Setting:** measured on image sampling; M3 is fabius's own convex inspection gate — an optimal overhead exists only because the route is imperfect.

### Classifier-Free Guidance (Ho & Salimans, 2022) · adjacent-setting · informed R10
Extrapolating toward the conditional (guidance weight **w > 1**) raises fidelity but cuts diversity — a measured fidelity/diversity trade with a sweet spot at modest w.
→ **fabius:** instruction emphasis ≈ guidance weight (R10) — hard-steer narrow contracts, say-it-once on breadth tasks. **Setting:** CFG measures Inception-Score-up / recall-down in *image* sampling; "emphasis ≈ w" is fabius's own heuristic reading, stated as such. The verifiable core: emphasis trades breadth for adherence — measure both.

---

## Tier 5 — Self-improvement

### Self-Refine (Madaan et al., 2023) · in-setting · informed R8
One frozen LLM improves its output via **generate → self-critique → refine**, same model for all three roles, no oracle. Because the signal is self-critique with no external check, gains can plateau or regress — **most lift lands in the first 1–2 passes**, and the critique must be specific and actionable to help at all.
→ **fabius:** the SOFT-signal tier of R8 — cap self-critique at 1–2 passes and require a specific cited critique. Where a HARD oracle exists, prefer the Reflexion path; where no signal exists, parcus blocks the loop and routes to human review.

### Voyager (Wang et al., 2023) · in-setting · informed M6
Lifelong skill acquisition via a growing **library of executable, documented, retrieval-keyed skills**: solved tasks are stored and composed by future tasks instead of re-derived, so capability compounds. The hard gate: a skill is added **only after self-verification** confirms it works; failures yield feedback, not a library entry.
→ **fabius:** archivum as a skill library (M6) — verify-then-store, retrieve-before-plan, supersede-don't-duplicate; failures leave anti-pattern notes. Turns per-task reflection into compounding cross-session leverage. The closest paper to fabius's own skills model.

### The "Ralph" autonomous-loop technique (Geoff Huntley) · in-setting · informed R12
Not a paper — a practitioner technique: run one agent through the same task prompt in a bounded loop, letting each cycle make incremental verified progress until an explicit completion condition holds. The point is the gate, not the loop: an exit condition, a cycle cap, and checkpoints are what separate "autonomous" from "infinite". Credited in [credits/README.md](../../../credits/README.md) via **ralph-claude-code** (frankbria).
→ **fabius:** the long-horizon `step → verify` loop with a dual exit gate (R12) — completion condition *and* explicit done-signal must both hold, cycles are hard-capped, a stuck loop escalates (M4) instead of spinning. **In-setting** on the loop-plus-gate shape; the dual exit gate is fabius's own optimal-stopping derivation and the specific caps are its operational settings.

---

## Tier 6 — Architecture & surveys

### Wang et al. — A Survey on LLM-Based Autonomous Agents · in-setting · informed R1
Decomposes an autonomous agent into four modules — **Profile, Memory, Planning, Action** — of which Memory / Planning / Action are the universal capability axes (Profile is configuration). A descriptive, field-wide spine, not one author's preference.
→ **fabius:** the three-axis routing taxonomy (R1) — Memory→archivum, Tools/Action→cohors, Planning→disciplina, Profile→cohors's agent schema, zero axes→parcus. Converts specialist selection into a reproducible classification published as the routing rationale.

### DSPy (Khattab et al., 2023) · in-setting · informed M5
Program with LLMs **declaratively**: each step is a typed **signature** (in→out), with a **metric** and real examples; a compiler searches prompt configs (instructions + bootstrapped demos) to maximize the metric on held-out data. Prompt text becomes a compiled, replaceable artifact — improvements measured, not vibes.
→ **fabius:** cohors's contract-first + the metric-delta gate (M5) — accept a prompt change only on a measured held-out improvement. Enforces fabius's "measured, not claimed" bar on prompt engineering itself, and grounds the eval harness's skill-vs-baseline pattern.

### Toward Efficient Agents — survey (Yang et al., 2026; arXiv 2601.14192) · in-setting · informed R2, R11, M3
Studies agent efficiency across **memory, tool learning, and planning** under real costs (latency, tokens, steps), and frames it as a **Pareto frontier between effectiveness and cost** — same effectiveness at lower cost, or more effectiveness per fixed budget. Converging principles across the field: **bound context via compression/management, design rewards that minimize tool invocation, and use controlled search**. Efficient design = the smallest config clearing the bar.
→ **fabius:** the capability ladder (R2: `inline < one tool < retrieval < plan < single subagent < swarm`, add the lowest sufficient rung), the cheapest-model-tier rule (**R11** — match capability to difficulty, escalate on a miss), and verification overhead scaled to need (M3). **In-setting** on the frontier and the principle; the concave ladder is fabius's own derived form (no curve is fitted) — fabius targets the knee and measures real cost per task.

### Living indexes — the reading list, kept current · reference
Community-maintained catalogs fabius treats as the lint backstop and reading list: **zjunlp/LLMAgentPapers** and **luo-junyu/awesome-agent-papers** (the agent literature, organized by capability) and **e2b-dev/awesome-ai-agents** (production agent *implementations*, the bridge from paper to shipped system). When a real failure exposes a gap rules R1–R13 / M1–M9 don't cover, these are where the research pass reads next — and a new rule is derived, verified and added to [`routing-policy.md`](routing-policy.md) only then (never from anticipation; `failures.md` is the trigger).

## The 2026-07 frontier pass — sources admitted after honesty audit

**Cuadron et al. 2025 — The Danger of Overthinking (arXiv:2502.08235).** LLM-judged overthinking scores on 4,018 SWE-bench Verified trajectories predict failure: favoring internal simulation over environment interaction (analysis paralysis, rogue action batches, premature disengagement) correlates with lower resolution, and two low-effort samples with the less-overthinking one selected reached 27.3% at 43% less compute than one high-effort run. fabius takes: in tool loops, make the cheap call instead of reasoning past it — the anchor of R14.

**HAL — Holistic Agent Leaderboard (arXiv:2510.11977).** 21,730 rollouts across 9 models × 9 benchmarks: higher reasoning effort REDUCED accuracy in the majority of runs, scaffold costs vary wildly and go unreported, and many published agent results are irreproducible due to harness bugs. fabius takes: standard effort is the default; raise one step only on a verified reasoning-shaped miss, and price every escalation.

**METR time horizons (arXiv:2503.14499 + TH1.1, 2026) and Ord's half-life refit (arXiv:2505.05115).** The 50%-success time horizon grows exponentially (~131-day doubling post-2023; longest measured frontier horizon ~14.5h, unreliable above ~16h), and success vs duration fits a near-constant per-minute failure hazard. fabius takes: R12 segment sizing — autonomous segments sit well inside the current model's measured horizon, re-checked per model generation, with verification frequency scaling with elapsed work.

**SWE-ABS (arXiv:2603.00520).** Adversarially strengthening the test suites of half of SWE-bench Verified rejected 19.7% of previously passing top-30 agent patches (top score −16.6pp; leaderboard reordered). fabius takes: a green from an unaudited oracle is PLAUSIBLE, not CONFIRMED — audit and strengthen the gate before trusting it (R15).

**Limits of Inference Scaling Through Resampling (arXiv:2411.17501).** With any verifier false-positive rate, resampling saturates at a hard ceiling; the optimal sample count is often under 10, and no resampling budget lets a weak model match a stronger model's single shot. fabius takes: bound every gated retry loop small; when it keeps failing, fix the check or escalate the generator, never raise N.

**TDAD (arXiv:2603.17973).** An AST impact map linking source files to covering tests, queried before each patch, cut agent regressions 70% (6.08%→1.82%) and lifted resolution — while generic TDD procedural prompting WITHOUT the mapped context increased regressions to 9.94%, worse than nothing. fabius takes: test-first works only when bound to concrete covering tests; TDD slogans come out of prompt templates (R16).

**TDFlow (arXiv:2510.23761).** With human-written ground-truth tests defining the target, a narrow propose→debug→revise test-driven workflow reaches 94.3% SWE-bench Verified; the measured bottleneck is writing valid reproduction tests, not solving them. fabius takes: surplus verification budget goes to authoring/validating the reproduction test.

**When To Solve, When To Verify (arXiv:2504.01005).** Compute-matched, self-consistency voting beats generative verification at most practical budgets; a GenRM verifier only catches up at ~8x the inference compute, and compute-optimal scaling grows solutions faster than verifications. fabius takes: for votable outputs the free evaluator wins; pay for a verifier only on unvotable outputs or very large budgets.

**DeepVerifier (arXiv:2601.15808).** Rubrics derived from an automatically built failure taxonomy (5 major / 13 sub-categories) beat vanilla agent-as-judge by 12–48% meta-eval F1, and as a feedback-and-refine gate add 8–11% end-to-end accuracy on hard GAIA/XBench-DeepSearch subsets. fabius takes: prose deliverables get an item-by-item failure-taxonomy rubric gate, not a one-line judge (M11).

**The Verification Horizon (arXiv:2606.26300).** Four verifier constructions for coding agents: every verifier is a proxy for intent, optimization widens the proxy gap (reward hacking, saturation), and easier-to-verify-than-generate inverts for strong agents; partly internal-benchmark/position evidence. fabius takes: gates decay — tighten them when green streaks lengthen and on every generator upgrade.

**Self-MoA (arXiv:2502.00674).** Ensembling N samples of the single best model beat mixed-model MoA (+6.6 AlpacaEval 2.0, +3.8 avg across MMLU/CRUX/MATH); mixing weaker models into the pool lowers quality. fabius takes: the council default is self-samples of the strongest model; a heterogeneous council only on correlated error (M10).

**Talk Isn't Always Cheap (arXiv:2509.05396, ICML MAS Workshop).** Debate accuracy decreases over rounds even when stronger models outnumber weaker ones; models flip correct→incorrect to agree with persuasive but wrong peers. fabius takes: cap debate at one verified round; never mix capability tiers in a debate pool.

**MAST (arXiv:2503.13657).** First empirical multi-agent failure taxonomy: 14 modes in 3 classes (specification, inter-agent misalignment, task verification) from 1600+ traces across 7 frameworks, κ=0.88 — most failures are design/coordination, not capability. fabius takes: M1's "named error" now has a measured vocabulary, and spec-shaped errors mean fix the contract, not add agents.

**Experience-following (arXiv:2505.16067).** Controlled ADD/DELETE experiments on LLM-agent memory: agents reproduce retrieved records — errors included — and polluted stores compound as contaminated outputs re-enter memory; selective addition plus outcome-labeled deletion beats add-everything. fabius takes: writes get outcome gates, reads get match+provenance checks (M7, M12) — and it is the mechanism behind Run 7's measured memory cost on security routes.

**Memory-R1 (arXiv:2508.19828).** An RL-trained ADD/UPDATE/DELETE/NOOP memory gate plus answer-side filtering of retrieved candidates beats heuristic pipelines on LoCoMo; unfiltered retrieval passed wholesale measurably distracts. fabius takes: retrieved ≠ injected — prune candidates before the prompt sees them.

**The Complexity Trap (arXiv:2508.21433, JetBrains).** On SWE-bench Verified across 5 model configs, replacing stale tool observations with placeholders (keeping the reasoning-action spine) matched or slightly beat LLM summarization at roughly half the cost of raw retention. fabius takes: mechanical masking is compaction rung one; pay a summarizer only for spans masking provably loses (M13).

**Less Context, Better Agents (arXiv:2606.10209).** 50-task enterprise tool-agent benchmark: full history retention 71% task completion, pruning to the last 5 tool interactions 79%, prune+summarize 91.6% — each rung also cutting tokens. fabius takes: full retention is the measured-worst context strategy on accuracy AND cost.

**Du et al. — Context Length Alone Hurts (arXiv:2510.05381, EMNLP 2025 Findings).** Even with provably perfect retrieval, performance degrades 13.9–85% as raw input grows — persisting under whitespace substitution and attention masking; recitation before solving recovers only ~4%. fabius takes: length itself is an accuracy tax — slice narrow before paging in (R9).

**Bouchard — Is Escalation Worth It? (arXiv:2605.06350).** Decision-theoretic characterization of LLM cascades validated on five benchmarks/eight models: a lightweight pre-generation router beat the best cascade on 4/5 datasets because cascades structurally pay the cheap model before deciding. fabius takes: with a confident difficulty read, route directly; reserve try-then-escalate for reusable cheap drafts (R11).

**AgentProp-Bench (arXiv:2604.16706).** On tool-using-agent traces with a human-validated subset: substring judging agrees with humans at chance (κ=0.049) while a three-LLM ensemble reaches κ=0.432 with conservative bias; parameter-level injected errors propagate to wrong final answers with p≈0.62. fabius takes: never string-match agent traces; use small cross-family judge ensembles (R8).

**REFLECT (arXiv:2605.19196).** Meta-evaluation of LLM judges on controlled research-agent failure interventions: even the best judges stay below 55% accuracy, weakest on evidence verification. fabius takes: a judge verdict is a tier-3 signal that may localize a failure but never solely close an evidence route.

**ABC — Agentic Benchmark Checklist (arXiv:2507.02825).** Audits of popular agentic benchmarks found flawed task/reward designs (null responses counted as success, insufficient tests) mis-estimating performance by up to 100% relative; checklist application cut CVE-Bench overestimation 33%. fabius takes: null-agent probes and test-adequacy review before any pass rate feeds M3's depth or routing decisions.
