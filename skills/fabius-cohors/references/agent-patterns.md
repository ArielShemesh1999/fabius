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
| **Swarm** | a coordinator over 6–8 specialized workers, shared memory, worktree isolation, for big work that splits many ways | hierarchical + parallel |
| **Approval concierge** | pauses at a gate for human sign-off before an irreversible step | human-in-the-loop |
| **Grounded Q&A (RAG)** | answers only from retrieved, cited sources — never free recall | single + retrieval |
| **Memory-bank agent** | persists user facts and preferences across sessions | single + memory layer |
| **Safety-guarded agent** | screens input and tool calls (prompt-injection defense) before execution | middleware / pre-hook |
| **Eval harness** | scores an agent against a fixed task set; reports skill-vs-baseline delta | sequential |

## Swarm — coordinator + worker templates

A swarm is the hierarchical shape at scale: one coordinator, 6–8 specialized workers, shared memory, worktree isolation for parallel writers. Built from native tools (the Workflow tool drives it, the Agent/Task tool spawns workers) — no external runtime.

**Coordinator** (owns the plan, writes no code):
```yaml
---
description: Decompose the goal into a task list, assign each task to the right specialist, integrate results, reassign stalled work.
mode: primary
permission: { read: allow, edit: deny, bash: ask }
tools: [read, grep, glob]      # plans and integrates; workers do the writing
---
You are the swarm coordinator.
Rules:
- Keep the team to 6–8 workers, each ONE specialized non-overlapping role (architect / coder / reviewer / researcher).
- Maintain ONE shared task list + spec in the fabius-archivum memory namespace; it is the single source of truth.
- Assign → collect each worker's contract → verify before integrating → reassign anything stalled or failed.
- File the coordination outcome back to memory so the next swarm starts smarter.
Output contract: the integrated result + a one-line-per-task status table (task · worker · pass/fail).
```

**Worker** (one slice, one contract):
```yaml
---
description: Implement exactly one assigned slice of the swarm's task list and return its contract.
mode: subagent
permission: { read: allow, edit: allow, bash: ask }   # edit scoped to its worktree
tools: [read, edit, grep, glob, bash]
isolation: worktree           # only when writing in parallel with siblings
---
You are the <architect | coder | reviewer | researcher> worker.
Rules:
- Read the shared spec from memory before starting; don't re-derive what a sibling already settled.
- Do only your assigned task — staying in your lane is the anti-drift rule.
- Write your result back to memory and return your contract.
Output contract: <the exact shape — a diff, a review table, a design doc, a findings list>.
```

The coordinator never writes code; the workers never replan. That split — plus the tight count and the shared memory — is what keeps a swarm coordinated instead of drifting.

## Least-privilege defaults

- **Read-only agent** (locator, reviewer, researcher): `read: allow`, `edit: deny`, `bash: deny`.
- **Builder agent**: `edit: allow` scoped to its files, `bash: ask` unless it must run commands.
- **Anything touching money, production, or an external send**: a human gate, or `ask`. Never `allow` a destructive `bash` by default.

## The output contract is the interface

The caller doesn't read the agent's reasoning — it consumes the return value. So pin the shape:

- A reviewer returns `path:line: <severity>: <problem>. <fix>.` — one line per finding, no prose.
- A classifier returns one of a fixed enum, nothing else.
- A structured extractor returns JSON matching a named schema (and the harness validates it, so the agent retries on a mismatch instead of returning malformed data).

A vague contract ("summarize your findings") forces the caller to parse free text — that's where multi-agent pipelines break. Two failure modes hide in the handoff, and both are contract bugs:

- **The consensus illusion.** Two agents "agree" in natural language ("you take the data, I'll wait for the results") and mean different things — the handshake succeeds, the work fails. The fix is the contract: a handoff is **concrete state — a schema, an id, a file path, a typed value — never a natural-language agreement.** If it can be misread, it isn't a contract.
- **Reject at the worker boundary.** A fan-out turns negative the moment one worker emits an invalid value (a `NaN`, a null, a malformed row) and the reducer keeps it — retries multiply the poison while the traces show a busy fleet producing arithmetic graffiti. Validate each worker's output **at the boundary it leaves**, before it enters the merge (the coordinator *verifies before integrating*, above) — and a schema'd contract makes the reject automatic, since the harness retries on a mismatch instead of passing malformed data downstream.

## When NOT to add an agent

Before spawning a second agent, ask the lean question (`fabius-parcus`): does it need to exist? A single agent with the right tools beats a swarm unless the work is genuinely independent (parallel), needs an independent reviewer (a checker that didn't write the code), or won't fit one context window. A swarm that could be one prompt is over-engineering with extra latency.
