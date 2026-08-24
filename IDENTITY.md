<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/shear559/fabius -->
# fabius — identity & evaluation alignment

The canonical statement of **what fabius is** and **how it must be judged**. Every surface of the system — the fifteen skill contracts, the benchmark suite, the whitepaper, the landing — is required to agree with this page. Where a surface disagrees, this page wins and the surface is drift.

---

## What fabius is

fabius is **not a model**. Not a prompt collection. Not a wrapper.

fabius is an **intelligence amplification layer** — an agentic control layer that operates on top of existing LLMs. The underlying model still generates, still reasons, still produces the output. fabius governs the *process behind* that reasoning: structure, discipline, decision frameworks, skills, heuristics, execution patterns, validation mechanisms, operational guidance.

It does not change model weights. It changes **behavior, process, and execution** — it helps a model find, organize, and apply capabilities it already has but does not naturally deploy. Latent capability → practical capability.

Concretely, fabius provides: reusable skills · workflows · heuristics · operational patterns · validation systems · execution strategies · memory practices · planning approaches · optimization mechanisms. Fifteen coordinated, zero-overlap layers ([ARCHITECTURE.md](ARCHITECTURE.md)), one stance: **scout wide, strike narrow.**

## Core objective

Maximize:

- output quality · task-completion quality
- instruction adherence · execution confidence
- capability utilization · first-pass success · consistency

While minimizing:

- hallucinations · token waste · unnecessary reasoning
- over-engineering · under-building · irrelevant exploration
- unnecessary agent creation · repeated work · avoidable iterations

**Produce better outcomes with less waste.** That is the whole objective.

## Philosophy

More reasoning is not always better. More tokens do not automatically create more value. More agents do not automatically improve execution. More context is not always beneficial.

fabius continuously evaluates: does this action improve the result? Does this reasoning justify its cost? Does this exploration create measurable value? Is this process helping the task — or merely consuming resources?

**Every token should contribute. Every step should have purpose. Every decision should move the task forward.** This is the same maxim the stance already carries — *scout wide* (cheap to investigate, expensive to be wrong) and *strike narrow* (deliver the smallest correct artifact) — stated as an economics: the highest possible **capability-to-cost ratio**.

## How fabius must be evaluated

The benchmark question is never *"is fabius smarter?"* — it cannot be; the weights are identical. The question is:

> **Can the exact same model achieve better outcomes with less waste when operating through fabius?**

Higher quality outputs. Fewer correction cycles. Better instruction adherence. Tighter scope. Fewer hallucinations. Less token consumption. Greater capability utilization. Preserved safety. Those are the metrics that matter — correctness alone is not enough; fabius is evaluated on **efficiency, discipline, consistency, and amplification**.

### The three evaluation modes

Same model, same task, fresh context, no context leakage. Only the orchestration changes:

| Mode | What runs |
|---|---|
| **BASE** | the bare model — no fabius, no skills, no memory |
| **FAB** | the same model + the fabius stance and the routed skill contract, shipped files verbatim — no persistent memory |
| **FAB_MEMORY** | FAB + persistent memory enabled — knowledge reuse, retrieval, lesson recall (`fabius-archivum`) |

If outcomes improve while waste decreases as you move BASE → FAB → FAB_MEMORY, fabius is succeeding.

### What gets measured

Output quality · instruction obedience · scope control · token efficiency · hallucination reduction · skill utilization · capability amplification · tool discipline · memory usage · security preservation · error recovery · agent coordination · task-completion reliability.

The executable form of this contract is the **Fabius Benchmark Suite** (`FBS v1`) — 100 neutral tasks in three tiers across ten categories, a fixed 0–4 rubric on seven dimensions, versioned and reproducible: [`evals/suite/`](evals/suite/). Measured results live in [BENCHMARKS.md](BENCHMARKS.md); nothing there is estimated.

## Success definition

fabius succeeds when it consistently enables models to think better, plan better, execute better, deliver better outputs — while consuming fewer unnecessary resources and staying on the objective.

**Maximize capability. Minimize waste. Every token should justify its existence.**
