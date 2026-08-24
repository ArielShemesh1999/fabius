---
name: fabius-cohors
description: >
  fabius's agent-engineering layer — how to DEFINE and ORCHESTRATE other agents: the definition
  schema, the permission model, the single-vs-multi-agent decision, and the five orchestration
  patterns (sequential / parallel / hierarchical / human-in-the-loop / swarm). Use when the user wants to
  build an agent, a subagent, a tool-using assistant, a multi-agent system, a swarm, or an
  orchestration workflow. A copy-from schema and proven agent shapes live in
  references/agent-patterns.md; the full production agent catalog (200+ agents across 17 domains
  + Python/Go/Java/Kotlin/Android/TypeScript packs, with a fabius-vec.db memory index) lives in
  references/agents/, indexed by references/agent-catalog.md. (Deterministic service-to-service
  wiring — n8n/Zapier-class "build a workflow" — is fabius-machina, not here.)
when_to_use: >
  "tool-calling assistant", "agent team", "hand this off between agents", "what permissions
  should the agent get", "evaluate my agent", "agent benchmark".
license: UNLICENSED
metadata:
  author: Ariel Shemesh
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/shear559/fabius -->

# Fabius Cohors — build agents that actually work

*Cohors* — the cohort, the tactical unit of a Roman legion. Most "agent" requests need ONE good cohort member, not a legion: reach for multi-agent only when the work genuinely splits. The lean question (`fabius-parcus`) comes first — *does the second agent need to exist?*

## The definition — every agent needs these four

```yaml
---
description: what it does AND when to dispatch it   # the dispatcher reads this — make it precise
mode: subagent | primary | all
model: provider/model-id        # cheap tier for mechanical work, strong tier for judgment
temperature: 0.0–1.0            # low for tools/code, higher for creative
permission:
  read: allow | ask | deny
  edit: allow | ask | deny
  bash: allow | ask | deny      # or a per-command map: {"*":"ask","git status *":"allow"}
tools: [only the tools it actually needs]
---
<system prompt: role, the 3–5 operating rules that matter, the output contract>
```

Four things make an agent reliable:

- **A precise `description`** — this is how a dispatcher picks it. Vague description → never invoked, or invoked for the wrong job.
- **A tight tool allowlist** — the minimum tools for the task. A read-only agent gets no `edit` or `bash`.
- **An explicit output contract** — state exactly what it returns: a table, a JSON schema, a diff, a verdict. The caller depends on the shape.
- **Least privilege** — `ask` or `deny` on anything destructive; default-deny `bash` for anything that doesn't need a shell.

## One agent vs many

Stay single unless one of these is true:

- The work splits into **independent** pieces that can run in parallel (fan-out).
- A step needs an **independent reviewer** — a second agent that didn't write the code, to check it.
- The context is **too large for one window** — split by file or subsystem.

None of those hold → one well-scoped agent with the right tools beats a swarm every time.

## Spend an agent only when it earns it

Before scaling the fleet, the orchestration rules from the routing policy ([routing-policy.md](../fabius/references/routing-policy.md)):

- **Name the error a second agent prevents (M1).** Stay single unless the work splits into independent pieces, needs an independent reviewer who didn't write the artifact, or overflows one window. Can't name the wrong answer it prevents → don't spawn it. *(Toolformer-spirit)*
- **Tree vs graph by whether partials merge (M2).** Combinable sub-results (synthesis, audit union, sort/merge, dedup) → parallel workers + a reducer agent. Competing branches → best-of-k, no merge machinery. *(Graph of Thoughts)*
- **Verification depth from measured failure (M3).** Set corrector/verify scaffolding from a route's *measured* pass rate — more where it has been failing, none on routes that never fail (drop the corrector, YAGNI). Re-measure from each outcome.
- **Reflect-then-retry, escalate when hypotheses run out (M4).** On a verifiable failure, prepend a one-paragraph reflection to the retry; if it repeats the prior cause with no new hypothesis, escalate to a human (cap ~3). *(Reflexion)*
- **Agents are contracts; rewrites need a metric delta (M5).** Accept a prompt change only when a checkable metric on held-out real examples improves — never on better-sounding wording. *(DSPy)*

## The five orchestration patterns

1. **Sequential** — A → B → C, each consuming the prior output. For pipelines (research → draft → publish). Simplest; the default for ordered work.
2. **Parallel (fan-out, then gather)** — N agents on disjoint slices at once, then merge. For breadth (review 8 files, search 4 ways). Use a barrier only when the merge genuinely needs all results together.
3. **Hierarchical** — a coordinator decomposes a goal, dispatches specialists, integrates the results. For open-ended goals where the sub-tasks aren't known up front (triage → investigate → respond).
4. **Human-in-the-loop** — the agent pauses at a defined gate for human input or approval before continuing. For irreversible or high-stakes actions.
5. **Swarm** — a coordinator over a tight team of 6–8 specialized workers with shared memory and worktree isolation, for work too big for one window that splits many ways. The heaviest tool; earn it. Full shape below.

Compose them: a hierarchical coordinator whose investigate phase fans out in parallel, with a human gate before it ships.

## The swarm — a coordinated cohort at scale

When the work is too big for one context window **and** splits into many parallel pieces (a migration across 40 files, an audit across a codebase, a from-scratch build), promote the hierarchical pattern to a **swarm**: one coordinator over a tight team of specialized workers. It's the heaviest tool here — earn it with the lean question first (`fabius-parcus`: does this need a swarm, or one good agent?).

**The shape (fabius-native — no external runtime to install):**

- **Coordinator** — decomposes the goal into a shared task list, assigns each task to the right specialist, integrates results, reassigns stalled work. Owns the plan; writes no code itself.
- **A small, specialized team** — each worker gets ONE non-overlapping role: `architect` (contracts + boundaries first), `coder` (implements one slice), `reviewer` (independent — didn't write it), `researcher` (locates prior art). Keep it **6–8 workers max** — past that, coordination cost eats the parallelism.
- **Shared memory** — workers don't re-derive each other's context: the coordinator files the spec and decisions into a `fabius-archivum` memory namespace; each worker reads it before starting and writes its result back. The wiki is the shared blackboard.
- **Isolation for parallel writes** — when workers edit files at once, give each its own git **worktree** so they don't collide; merge on completion. Read-only fan-out needs no isolation.

**Run it with the native tools — nothing to install:**

- The **Workflow tool** is the swarm engine: `parallel()` for a fan-out barrier, `pipeline()` for find → build → verify with no barrier, a coordinator loop for assign → integrate. Deterministic control flow, not model-improvised.
- The **Agent / Task tool** spawns each worker (`agentType` for a specialist, `isolation: "worktree"` for parallel writers, `run_in_background` for concurrency).
- A worker's `description` + output contract is still the law — a swarm is N well-defined cohort members, not N vague ones.

**Anti-drift — what keeps a swarm from thrashing:**

1. Tight count (6–8) and **specialized, non-overlapping roles** — overlap is where swarms drift.
2. One shared spec / task-list everyone reads; the coordinator is the single source of truth.
3. Every worker returns a checkable contract; the coordinator verifies before integrating (pair with adversarial-verify for findings).
4. File the coordination outcome back to memory so the next swarm starts smarter (`fabius-archivum`).

Still lean: if the task list is short and serial, it's a pipeline, not a swarm. Reach for the swarm only when breadth × depth genuinely exceeds one agent's reach.

## Reliability patterns

- **Adversarial verify** — for a finding or a claim, spawn an independent skeptic prompted to *refute* it. Majority-refute kills it. This is what stops plausible-but-wrong output from surviving.

More shapes — grounded/cited RAG, a safety guard that screens for prompt injection before execution, cross-session memory, an eval harness that scores skill-vs-baseline — are in `references/agent-patterns.md`. The full catalog of production agents to copy and adapt (by domain and by language) is in `references/agents/`; start from `references/agent-catalog.md`. Grounding and memory lean on `fabius-archivum`. The operational tier — scoring an agent on a ground-truth benchmark, surviving long-horizon runs (checkpoint + dual exit gate), acquiring tools via MCP at least privilege, and sandboxing agent-written code — is in `references/agent-evaluation-and-durability.md`. The framework + tool-caller map — agent frameworks per orchestration pattern, the function-calling eval (BFCL / τ²), and open tool-callers with the Llama-community-license trap flagged → `references/agent-frameworks.md`.

**Running an agent on the user's own machine** is a different design: the blast radius stops being a container and becomes their laptop. Capability-per-tool over a working-directory jail (symlink-resolved) and an unconditional secret deny-list; read-only default, acting opt-in, autonomy a second flag — with irreversible actions (`git push`, `--prod`, `rm -rf`, `sudo`) held even under autonomy; no TTY means an approval prompt DENIES rather than hangs; the model call is injectable so the whole loop tests with no key; verification runs the artifact locally and a non-zero exit overrules the judge; a money wall beside the step wall. Also how the agent is REACHED — the three channel-ownership models and the allow-list/opt-in-acting/untrusted-inbound rules → `references/local-agent-runtime.md`. Working implementation: `runtime/` in this repository.

## Build loop

1. Write the `description` and the output contract **first** — they define success.
2. Minimum tools, least privilege.
3. Single agent unless the work truly splits.
4. Test against real inputs; check the output matches the contract (`fabius-disciplina`).
5. Multi-agent? draw the pattern (sequential / parallel / hierarchical / HITL) before you wire anything.

Pairs with: `fabius-disciplina` (test the agent's behavior, prove it), `fabius-archivum` (grounding and cross-session memory), `fabius-parcus` (don't over-build the fleet).
