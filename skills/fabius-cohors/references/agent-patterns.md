# Fabius Cohors — schema & proven agent shapes

Loaded on demand by `fabius-cohors`. The skill has the decision rules; this file has the copy-from schema, the recurring shapes, and the least-privilege defaults.

## Copy-from agent definition

```yaml
---
description: one precise sentence — what it does AND when to dispatch it
mode: subagent          # subagent | primary | all
model: provider/model-id
temperature: 0.2
permission:
  read: allow
  edit: ask             # allow | ask | deny
  bash: deny
tools: [read, grep, glob]   # the minimum the job needs
---
You are <role>.
Operating rules: <the 3–5 that actually matter>.
Output contract: <exactly what you return — a schema, a table, a diff, a verdict>.
```

A Claude Code subagent uses the same idea in its own format: a `description` (how the dispatcher picks it), a tool allowlist, and a system prompt that ends in an output contract. The frontmatter keys differ by harness; the four reliability properties don't.

## Recurring shapes — pick the closest, then adapt

| Shape | What it is | Orchestration |
|---|---|---|
| **Single specialist** | one role, tight tools, one clear output (reviewer, refiner, classifier) | single |
| **Research → write → publish** | gather sources, draft, format and ship | sequential |
| **Fan-out reviewers** | N agents review disjoint files or dimensions, then merge findings | parallel + barrier on merge |
| **Find → adversarial-verify** | finders surface candidates; independent skeptics try to refute them | pipeline |
| **Coordinator + specialists** | decompose an open goal, dispatch, integrate (triage, incident, adjudication) | hierarchical |
| **Approval concierge** | pauses at a gate for human sign-off before an irreversible step | human-in-the-loop |
| **Grounded Q&A (RAG)** | answers only from retrieved, cited sources — never free recall | single + retrieval |
| **Memory-bank agent** | persists user facts and preferences across sessions | single + memory layer |
| **Safety-guarded agent** | screens input and tool calls (prompt-injection defense) before execution | middleware / pre-hook |
| **Eval harness** | scores an agent against a fixed task set; reports skill-vs-baseline delta | sequential |

## Least-privilege defaults

- **Read-only agent** (locator, reviewer, researcher): `read: allow`, `edit: deny`, `bash: deny`.
- **Builder agent**: `edit: allow` scoped to its files, `bash: ask` unless it must run commands.
- **Anything touching money, production, or an external send**: a human gate, or `ask`. Never `allow` a destructive `bash` by default.

## The output contract is the interface

The caller doesn't read the agent's reasoning — it consumes the return value. So pin the shape:

- A reviewer returns `path:line: <severity>: <problem>. <fix>.` — one line per finding, no prose.
- A classifier returns one of a fixed enum, nothing else.
- A structured extractor returns JSON matching a named schema (and the harness validates it, so the agent retries on a mismatch instead of returning malformed data).

A vague contract ("summarize your findings") forces the caller to parse free text — that's where multi-agent pipelines break.

## When NOT to add an agent

Before spawning a second agent, ask the lean question (`fabius-parcus`): does it need to exist? A single agent with the right tools beats a swarm unless the work is genuinely independent (parallel), needs an independent reviewer (a checker that didn't write the code), or won't fit one context window. A swarm that could be one prompt is over-engineering with extra latency.
