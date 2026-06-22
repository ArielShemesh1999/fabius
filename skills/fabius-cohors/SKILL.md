---
name: fabius-cohors
description: >
  fabius's agent-engineering layer — how to DEFINE and ORCHESTRATE other agents: the definition
  schema, the permission model, the single-vs-multi-agent decision, and the four orchestration
  patterns (sequential / parallel / hierarchical / human-in-the-loop). Use when the user wants to
  build an agent, a subagent, a tool-using assistant, a multi-agent system, a swarm, or an
  orchestration workflow. A copy-from schema and proven agent shapes live in
  references/agent-patterns.md; the full production agent catalog (200+ agents across 15 domains
  + Python/Go/Java/Kotlin/Android/TypeScript packs, with a ruvector.db memory index) lives in
  references/agents/, indexed by references/agent-catalog.md.
---

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

## The four orchestration patterns

1. **Sequential** — A → B → C, each consuming the prior output. For pipelines (research → draft → publish). Simplest; the default for ordered work.
2. **Parallel (fan-out, then gather)** — N agents on disjoint slices at once, then merge. For breadth (review 8 files, search 4 ways). Use a barrier only when the merge genuinely needs all results together.
3. **Hierarchical** — a coordinator decomposes a goal, dispatches specialists, integrates the results. For open-ended goals where the sub-tasks aren't known up front (triage → investigate → respond).
4. **Human-in-the-loop** — the agent pauses at a defined gate for human input or approval before continuing. For irreversible or high-stakes actions.

Compose them: a hierarchical coordinator whose investigate phase fans out in parallel, with a human gate before it ships.

## Reliability patterns

- **Adversarial verify** — for a finding or a claim, spawn an independent skeptic prompted to *refute* it. Majority-refute kills it. This is what stops plausible-but-wrong output from surviving.

More shapes — grounded/cited RAG, a safety guard that screens for prompt injection before execution, cross-session memory, an eval harness that scores skill-vs-baseline — are in `references/agent-patterns.md`. The full catalog of production agents to copy and adapt (by domain and by language) is in `references/agents/`; start from `references/agent-catalog.md`. Grounding and memory lean on `fabius-archivum`.

## Build loop

1. Write the `description` and the output contract **first** — they define success.
2. Minimum tools, least privilege.
3. Single agent unless the work truly splits.
4. Test against real inputs; check the output matches the contract (`fabius-disciplina`).
5. Multi-agent? draw the pattern (sequential / parallel / hierarchical / HITL) before you wire anything.

Pairs with: `fabius-disciplina` (test the agent's behavior, prove it), `fabius-archivum` (grounding and cross-session memory), `fabius-parcus` (don't over-build the fleet).
