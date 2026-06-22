# Fabius Cohors — proven shapes & schema reference

Loaded on demand by `fabius-cohors`. The skill has the decision rules; this file has the copy-from schema and the catalog of agent shapes that recur across a large set of production agent definitions.

## OpenCode agent definition (copy this)

```yaml
---
description: One precise sentence — what it does AND when to dispatch it.
mode: subagent          # subagent | primary | all
model: provider/model-id
temperature: 0.2
permission:
  read: allow
  edit: ask             # allow | ask | deny
  bash: deny
tools: [read, grep, glob]   # minimum needed
---
You are <role>.
Operating rules: <the 3–5 rules that matter>.
Output contract: <exactly what you return — schema/table/diff/verdict>.
```

Claude Code subagents use the same idea: a `description` (how the dispatcher picks it), a tool allowlist, and a system prompt with an output contract.

## Recurring agent shapes (pick the closest, adapt)

| Shape | What it is | Pattern |
|---|---|---|
| **Single specialist** | one role, tight tools, clear output (reviewer, refiner, classifier) | single |
| **Research → write → publish** | gather sources, draft, format/ship | sequential |
| **Fan-out reviewers** | N agents review disjoint files/dimensions, merge findings | parallel + barrier-on-merge |
| **Find → adversarial-verify** | finders surface candidates; independent skeptics refute | pipeline |
| **Coordinator + specialists** | decompose open goal, dispatch, integrate (triage, incident, claim adjudication) | hierarchical |
| **HITL concierge** | pauses at a gate for human approval before an irreversible step | HITL |
| **Grounded Q&A (RAG)** | answers only from retrieved+cited sources, never free-recall | single + retrieval |
| **Memory-bank agent** | persists user prefs/facts across sessions | single + knowledge layer |
| **Safety-guarded agent** | input/tool-call screening (prompt-injection defense) before execution | middleware/plugin |
| **Eval/benchmark harness** | scores an agent against a fixed task set; skill-vs-baseline delta | sequential |

## Least-privilege defaults

- Read-only agent (locator, reviewer, researcher): `read: allow`, `edit: deny`, `bash: deny`.
- Builder agent: `edit: allow` scoped to its files, `bash: ask` unless it must run.
- Anything touching money, prod, or external sends: HITL gate or `ask`.

## The full set

For a deeper catalog of production agent definitions across SDKs and orchestration frameworks, port a proven system prompt + role into your harness's agent format and add the frontmatter above.
