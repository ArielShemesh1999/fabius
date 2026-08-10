# Fabius Cohors — schema & proven agent shapes

Loaded on demand by `fabius-cohors`. The skill has the decision rules; this file has the copy-from schema, the recurring shapes, the least-privilege defaults, and the harness mechanics a production loop runs on.

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
inputs:                     # declared I/O — what the caller must supply
  - { name: target_file, io_type: file_path, required: true, description: the file to work on }
outputs:                    # what the agent returns, by name and type
  - { name: findings, io_type: json, required: true, description: findings list in the contract shape }
---
You are <role>.
Operating rules: <the 3–5 that actually matter>.
Output contract: <exactly what you return — a schema, a table, a diff, a verdict>.
```

The `inputs`/`outputs` blocks are the output-contract rule made checkable: each entry carries `name`, `io_type`, `required`, `description`, so the harness can reject a dispatch missing a required input and a return missing a declared output — before any prose is read. They also make pipelines contract-chained: agent A's declared `output_file` is agent B's declared `input_file`, so the wiring between stages is a typed graph the harness can validate, not an agreement in prose.

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

A swarm is the hierarchical shape at scale: one coordinator, 6–8 specialized workers, shared memory, worktree isolation for parallel writers — and a worktree merges back explicitly: nothing a worker writes lands in the main tree until the coordinator merges it. Built from native tools (the Workflow tool drives it, the Agent/Task tool spawns workers) — no external runtime.

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
isolation: worktree           # only when writing in parallel with siblings; merge back explicitly
---
You are the <architect | coder | reviewer | researcher> worker.
Rules:
- Read the shared spec from memory before starting; don't re-derive what a sibling already settled.
- Do only your assigned task — staying in your lane is the anti-drift rule.
- Write your result back to memory and return your contract.
Output contract: <the exact shape — a diff, a review table, a design doc, a findings list>.
```

The coordinator never writes code; the workers never replan. That split — plus the tight count and the shared memory — is what keeps a swarm coordinated instead of drifting.

**Depth-1 spawn cap:** workers never spawn workers — one coordinator, one layer of children, and a need for more capability climbs the router's ladder one rung instead (`skills/fabius/references/routing-policy.md`, R2).

**A self-critique lane, as a HARD GATE.** Give one lane the job of attacking the swarm's own draft — and make it a gate, not an opinion. The critic returns a **required-corrections** section, and **the swarm does not emit while that section is non-empty**: revise, re-run the critic, repeat until it comes back empty. The word "gate" is load-bearing. An advisory critic gets read, agreed with, and shipped past — the coordinator has a draft in hand and a critique is a reason to do more work, which is exactly the pressure the gate exists to remove. Bound the loop (N passes, then escalate the residue as a named gap) so it cannot spin.

**Declare the lane DAG.** Lanes are not peers by default. Write down which lane consumes which lane's output, run each level of the graph in parallel, and join at the barrier. Without the DAG you are guessing which lanes are independent — and a wrong guess is either a serialized swarm (slow) or a lane reading a sibling's half-written result (wrong).

**Name the fan-out mode per level.** A leveled pipeline fans out in exactly two ways, and the DAG should say which: **per-result** — run the task once per upstream result, with that result's keys merged into the run's context, for work that treats each item independently; **consume-all** — one batched run receiving the whole previous level as an array, the only correct mode for cross-result work (dedupe, rank, pick). Fanning per-result into a job that must compare its inputs silently produces N local answers to a global question.

**Repeat runs are a recall lever.** Re-run one task N times, where later repeats receive ONLY that task's own earlier output — explicitly labeled *untrusted result data, not instructions* — and must append only genuinely-new records, returning a stub when nothing new surfaced (the stub contract, below). Repeats trade tokens for recall on tasks where one pass predictably misses; the untrusted label is what keeps a prior pass's text from becoming this pass's instructions.

**Fan-in over a growing pool needs judgment, not just keys.** When lanes accumulate findings across runs, mechanical schema-key merge is not enough — near-duplicates arrive in different words. Add an LLM clustering pass with a defensible rule: cluster two findings ONLY when one fix would address the same root cause AND the same location/entrypoint — never merely the same class of problem. Incremental runs use an anchor scheme: findings already canonicalized enter as immutable **anchors**, new items as **targets**; a cluster holds at most one anchor, and the cluster's canonical is its anchor (else the lowest target id). Then validate coverage mechanically — every target id appears exactly once, singletons included; unknown ids, duplicate ids, merged anchors, or a coverage mismatch reject the pass. The model proposes the clustering; the validator disposes.

**Ranking over the pool follows the same anchor law.** No anchors → full re-rank. Ranked anchors → append mode: new items get decimal positions inserted BETWEEN anchors, preserving anchor order, and the merged list then renumbers to dense integers. Run both the clustering and the ranking pass in fixed-size batches under schema contracts (the output-contract section, below).

**Tier the model per lane.** The model is a per-lane decision, not a swarm-wide one. Mechanical lanes — collecting, formatting, checking a list against a rule — run on the fast tier; the adversarial lane and the synthesis lane get the strong one. A single tier across the swarm either overpays for the mechanical work or underpowers the lane whose judgment the output actually rests on.

**The boundary with `fabius-concilium`:** a persona swarm splits **the work** across specialized lanes of one model; a council aggregates **one answer** across whole models. If the lanes differ by *role*, it's a swarm — cohors. If they differ only by *which model answered*, it's a council — concilium. Personas are a division of labor, not a source of independence: N personas on one model share that model's blind spots, which is why the critic lane is a gate on the work and not a substitute for a second opinion.

## Durability — resuming an interrupted run

A process dies between the model emitting a tool call and the tool returning. On restart you hold a transcript whose last assistant turn has tool calls and no results. **You can never prove a tool never started** — the crash is evidence about your process, not about the side effect. The charge may have posted. The email may have sent. The row may be written.

So the law is: **on resume, repair the partial batch — never re-execute it.** Synthesize one tool result per orphaned call carrying an honest *unknown outcome* marker — "this tool was interrupted; it may or may not have run; verify the state before calling it again" — and let the model proceed from there. The repair does two jobs at once: it makes the transcript well-formed (most APIs reject an assistant turn whose tool calls have no answering results, so an unrepaired batch doesn't resume at all — it 400s), and it hands the model the true fact instead of a convenient one.

**Re-execution of a side-effecting tool is a correctness bug, not a retry.** "Retry" is a word for a call that provably didn't happen; applying it here smuggles in an assumption you cannot check (`fabius-parcus`: assume less). A resumed agent that re-sends is not resilient — it is duplicating, and the traces look identical to a healthy run. What the model does with the unknown marker is what a careful operator does: read the state back before acting (`fabius-disciplina`: assert the *result state*, never the return code), then decide. That is the only correct move, and it's only available to a model that was told the truth about the interruption.

**Where this bites in practice:** any scheduler that re-picks stale tasks on a fixed interval — the synapse console's cron sweeps stale tasks every 10 minutes — is running this law's live surface on every sweep. Each stale task it picks up is a partially-executed batch by definition; a resume path that re-issues the batch turns a routine sweep into a duplicate-side-effect engine.

**RESUME_FROM context inheritance — a different mechanism from crash-resume.** The law above repairs an *interrupted* run; RESUME_FROM continues a *completed* one: a second agent starts from the first agent's full transcript and tool state instead of a fresh context. Three constraints make it safe — the source agent completed (so there is no partial batch to repair), same session, same agent type (the inherited transcript was produced under the same instructions and tool contract the successor runs with). Within those bounds it is the cheap path for staged work: the successor sees everything the predecessor saw, versus summarize-and-respawn, which pays an extra summarization call and loses whatever the summary dropped.

Two more properties belong to the same runtime concern:

- **Terminate with a report.** Arm a **wall-clock deadline** at dispatch. When it fires, stop admitting new tool calls and force one final turn whose only job is to deliver what the agent has. An agent with no deadline has no failure mode that *produces output* — it doesn't fail, it just never returns, and the caller learns nothing. A partial report at the deadline beats a complete one that never arrives.
- **Cap the tool-call step's output tokens.** A step whose entire job is to emit a tool call has no reason to be long. Uncapped, a step that degenerates — repeating a token, restating the plan, talking itself in a circle — burns the whole budget and produces no call. Cap it at the size of the largest legitimate call the agent can make; the cap costs nothing on a healthy step and converts a silent budget fire into a fast, visible failure.

## Harness mechanics — the contracts a production loop runs on

These sit under whichever agent definition runs on top: how a loop knows it's done, how approvals persist, how modes switch, how tool results stay out of the window, how the agent curates itself, how generated code earns trust, and what to demand of a pipeline runtime. Contracts to demand, not libraries to adopt.

### Loop-until-done — how the loop knows it is done

The dual exit gate (`references/agent-evaluation-and-durability.md` §2) says a loop must exit on done-or-stuck; this is the completion-signal menu that tells it *done*: (1) a completion-marker string, with a templated "keep working, emit the marker when done" nudge between iterations; (2) an open-todo count reaching zero; (3) background-task drain; (4) an AI judge — a bare chat client, no tools, no session, returning a structured done/not-done verdict; (5) an arbitrary delegate. Bounded by default (~10 iterations); unbounded is an explicit opt-in, never a silent default.

- **Judge fallback markers must be non-overlapping.** Choose DONE/MORE strings where neither is a substring of the other nor of any JSON field name — otherwise a malformed `{"answered": false}` can be misparsed as done. Ambiguity resolves to MORE — the fail-safe direction, since the iteration cap catches runaways.
- **Cross-iteration state is a progress log, not accumulated history.** Snapshot the session before the loop, restore it between iterations, and inject only the original task plus the per-pass feedback entries — the loop's memory is what it decided, not everything it said.
- **A pending tool-approval stops the loop.** If an iteration surfaces one, the loop STOPS and hands it to the caller — it never spins past a human gate.

### Standing approvals — "do not ask again" without a wildcard

Two scopes only: **approve-this-tool** (name-wide) and **approve-these-exact-arguments** — arguments compared as canonical sorted-key JSON, so key ordering can neither dodge nor forge a match. A no-argument approval stores `{}` and matches only future no-argument calls — it never becomes a wildcard. Rules also match on the tool's SERVER boundary: the same tool name exposed by a different MCP server is NOT covered by an existing approval.

**Evaluation order**: standing rules → heuristic auto-approve callbacks (e.g., known read-only tools) → prompt the human. Drain queued approvals one at a time; auto-re-invoke when everything in a response was auto-approved.

**The name-collision trap.** A name-based auto-approve rule matches ANY local tool with that name — a rule written for one provider's read-only tool silently approves an unrelated collider, bypassing the approval boundary. Audit for collisions whenever a rule is added (same family as permission-rule gotcha 4's missing word boundary, below).

### A promptable plan/execute mode machine

**Modes as a context provider.** A mode map plus get/set-mode tools, with the current mode interpolated into the system context every turn — the state machine is legible to the model, not implied by prompt history. Switching happens only on explicit user consent, and the switch injects a "mode changed X→Y, adjust behavior" notification so the model registers the transition instead of inferring it.

**Plan mode**: build todos; explore only enough to sharpen questions; ask clarifications ONE at a time, each with concrete options to pick from; write the plan to a memory FILE so compaction cannot eat it — then present for approval and switch.

**Execute mode**: classify the ask — a simple question just gets answered; anything else runs autonomously: never ask, choose the most reasonable option on ambiguity and note the choice, tick todos as you go, keep working until done.

**The boundary**: this is an agent-definition pattern for agents cohors defines. fabius's OWN plan process stays `fabius-disciplina` — the mode machine is something you give an agent, not how fabius plans.

### Programmatic tool calling — the script calls the tools, the results skip the window

The biggest context-cost lever a harness has: an execute-code tool where the model writes ONE script that calls the harness's own tools through generated RPC stubs. A multi-step chain collapses into a single inference turn, every intermediate tool result stays out of the window, and only stdout returns.

- **Two transports**: local — a Unix socket with an RPC dispatcher thread in the parent; remote sandboxes — file-based RPC, request/response files polled by the parent.
- **Guardrails**: a fixed small sandbox tool allowlist intersected with session-enabled tools; caps on tool-call count and wall time; stdout capped with a head/tail split.
- **Truncation is structured metadata** — bytes-omitted fields, never only a textual marker: a marker alone can be re-truncated away by a client layer, leaving no evidence anything was cut.
- **Env scrubbing runs blocklist-first**: a secret-substring blocklist, THEN a narrow safe-prefix allowlist — a broad project-prefix passthrough leaks config that doesn't look like a secret.
- **Refund the script's internal tool iterations to the loop budget** so programmatic calls do not consume loop quota — the loop counts decisions, not plumbing.

Where the script runs is governed by the sandbox law — `references/agent-evaluation-and-durability.md` §4.

### The self-improvement fork — provenance-gated curation

After a turn, a background FORK of the agent replays the conversation and asks "should any skill or memory be saved or updated?" — with a tool whitelist limited to memory + skill management, so the fork can curate but not act. The main conversation and its prompt cache are never touched.

**Cost policy by model**: same model as the parent → replay the FULL transcript (warm cache reads ≈ free); a cheaper model → replay a compact digest, because it cannot reuse the parent's cache and a full replay would cold-write it.

**Write-origin provenance**: stamp what the fork creates as agent-created; anything the USER asked to save is never auto-curated. Agent sediment and user property are separate populations, and only the first is the curator's to touch.

**Curator invariants**: triggered by inactivity — idle ≥ ~2h AND ≥ ~7d since the last run, no cron daemon; touches agent-created items only, via a usage sidecar (use/view/patch counts); stale at ~30d, archive at ~90d; pinned items are exempt from EVERY auto-transition; it NEVER deletes — archive plus a pre-run snapshot is the maximum destructive act; the opinionated LLM consolidation pass is opt-in while the deterministic prune always runs.

Same idle-trigger idea over a different store: `fabius-archivum`'s consolidation gates (`skills/fabius-archivum/references/external-recall.md`) — link, don't restate.

### Verified codegen — typed gates, per-type repair

Generated code passes ORDERED gates, cheapest first: syntax parse → execute against the real input → schema-validate the output → semantic compare against an independent reference answer (exact deep-compare first; an LLM equivalence judge only on mismatch).

- **The reference-answer oracle**: produce the expensive direct-LLM answer over the same input once, beforehand; the cheap deterministic code must reproduce it.
- **Type the errors** — syntax / execution / validation / semantic — and give each type its own focused analysis prompt and its own focused regeneration prompt, instead of one generic "fix it".
- **Bound and hard-fail**: cap per-gate retries (~3) AND overall iterations (~10); any gate failure re-enters from the top; exhaustion hard-fails — never ship unverified code.
- **The execution gate runs under the sandbox law** (`references/agent-evaluation-and-durability.md` §4) — a bare exec namespace is NOT containment; never describe it as one.

### Lightweight pipeline runtime — three contracts to demand

Do not adopt a bespoke runtime for this — LangGraph already owns the graph/state-machine row in `references/agent-frameworks.md`. These are contracts to demand of whichever runtime you use:

1. **Declarative input expressions.** Nodes declare inputs as a boolean expression over state keys — e.g. `prompt & (chunks | parsed_doc | doc)` — where OR-chains resolve to the FIRST satisfied alternative, so one node definition transparently consumes the best-available upstream artifact and one graph serves many pipeline variants.
2. **Validated conditionals.** A conditional node has exactly two outgoing edges, checked at graph build; the condition evaluates in a sandboxed expression evaluator — never raw eval; returning a node name not in the graph is a hard error, not a fallthrough.
3. **A per-node cost ledger** — tokens, prompt/completion split, request count, spend, wall time — with a TOTAL row; on any exception, log the failing node's name with the partial ledger. Every failure and every dollar is attributable to a node — this extends `references/local-agent-runtime.md`'s budget walls with attribution.

## Least-privilege defaults

**Coarse capability modes are the first cut.** Before any per-tool grant, pick one of four modes: **read-only** (analyze, never mutate) · **read-write-no-shell** (edit files, no command execution) · **execute-no-edits** (run commands — a test-runner, a prober — but mutate no files) · **all**. The mode states the blast radius in one word a reviewer can check at a glance; per-tool grants then narrow within the mode, never widen past it.

- **Read-only agent** (locator, reviewer, researcher): `read: allow`, `edit: deny`, `bash: deny`.
- **Builder agent**: `edit: allow` scoped to its files, `bash: ask` unless it must run commands.
- **Anything touching money, production, or an external send**: a human gate, or `ask`. Never `allow` a destructive `bash` by default.

**Inheritance is not a default — it's a decision, and it splits by field class.** When a parent agent spawns a child, every field in the child's definition is one of two kinds, and they inherit in opposite directions:

- **Capability and identity fields NEVER inherit** — `tools`, `skills`, `instructions`, `subagents`. **Omitted means NONE**, not "whatever the parent had." These fields answer *what may this agent touch, and who is it* — and a privilege the definition doesn't name is a privilege nobody reviewed. A child that silently receives the parent's tool list is a privilege escalation with no diff behind it: the child's definition reads as harmless, and the running agent isn't.
- **Environment fields DO inherit** — `model`, thinking level, compaction. These answer *how is this run executed*, not *what may it touch*. Inheriting them carries no privilege consequence and saves the caller from restating the obvious; a child that quietly drops to a different model is a surprise with no security content.

**Construct the child from an explicit allow-list of copied fields — never `{...parent, ...overrides}`.** The spread reads as convenience and is actually a standing decision about code that doesn't exist yet: *every capability field added in the future inherits by default*. The day someone adds one, every child agent in the system silently gains it, no child definition changes, and no review sees anything. An allow-list fails the other way — a new field is invisible to children until someone names it, and the symptom is a child that can't do its job, discovered in the first run. Both shapes have a failure mode; only one of them announces itself. Pick the direction the bug runs.

### Permission-rule gotchas

Four ways a rule set that reads correct evaluates wrong:

1. **Chained-command asymmetry.** Deny and ask rules are checked against each segment of a chained command AND against the whole string; allow rules match the whole string only. So an allow like `Bash(git *)` auto-approves `git status && rm -rf /` — the chain starts with `git`, the allow matches, and no segment is ever re-examined. Narrow allows must pair with explicit denies for the dangerous segments, and a matcher must split chains itself and fall back to a prompt on command substitution, backgrounding, and subshells it cannot inspect.
2. **Severity merge.** Rules from every scope merge into one set, and deny > ask > allow regardless of which scope a rule came from — a global deny is unoverridable by any local allow. The corollary: deny-by-default needs a *mode*, not a catch-all deny rule, because a `deny *` outranks every allow you would add under it.
3. **Dangerous-command re-prompt.** A fixed list — `rm`, `chmod`/`chown`, `kill*`, `git push` — re-prompts above implicit and remembered grants. But an explicit allow rule still approves them: the re-prompt tier sits above convenience grants, not above the rule set. A true never-tier needs deny rules; there is no third state.
4. **Wrapper peeling.** Deny and ask rules peel env-prefixes, `timeout`, and `nice` to check the inner command, and are also checked inside `bash -c` scripts; `sudo`, `xargs`, and `nohup` are not peeled and need their own explicit rules. Allow rules get NO peeling — a wrapped command falls through to a prompt, which is the fail-safe direction. And prefix matching has no word boundary: an allow for `git` also matches `gitleaks`.

Hardening beyond the rule set — sandboxing, secrets hygiene, injection screening — is `fabius-praesidium`'s layer.

## The output contract is the interface

The caller doesn't read the agent's reasoning — it consumes the return value. So pin the shape:

- A reviewer returns `path:line: <severity>: <problem>. <fix>.` — one line per finding, no prose.
- A classifier returns one of a fixed enum, nothing else.
- A structured extractor returns JSON matching a named schema (and the harness validates it, so the agent retries on a mismatch instead of returning malformed data).

A vague contract ("summarize your findings") forces the caller to parse free text — that's where multi-agent pipelines break. Two failure modes hide in the handoff, and both are contract bugs:

- **The consensus illusion.** Two agents "agree" in natural language ("you take the data, I'll wait for the results") and mean different things — the handshake succeeds, the work fails. The fix is the contract: a handoff is **concrete state — a schema, an id, a file path, a typed value — never a natural-language agreement.** If it can be misread, it isn't a contract.
- **Reject at the worker boundary.** A fan-out turns negative the moment one worker emits an invalid value (a `NaN`, a null, a malformed row) and the reducer keeps it — retries multiply the poison while the traces show a busy fleet producing arithmetic graffiti. Validate each worker's output **at the boundary it leaves**, before it enters the merge (the coordinator *verifies before integrating*, above) — and a schema'd contract makes the reject automatic, since the harness retries on a mismatch instead of passing malformed data downstream.

For a fan-out of reviewers or critics, two specifics turn N outputs into one aggregatable result instead of N essays:

- **A closed verdict set.** The top-level judgment is one member of a fixed enum — `APPROVE` · `APPROVE-WITH-COMMENTS` · `REQUEST-CHANGES` · `BLOCK` — and nothing else. A closed set is **countable**: the coordinator tallies it, gates on it, and routes on it without reading a word. An open verdict ("looks mostly fine, though I'd note…") is a sentence that a human must adjudicate — times N lanes, every run. The enum is also what makes the critic lane's gate mechanical: *non-empty required-corrections* is a check, not a judgment call.
- **A mandated finding schema.** Every finding, from every lane, carries the same fields — **Risk** (what breaks) · **Evidence** (the `path:line` or trace that proves it) · **Fix** (the concrete change) · **Blocks-merge** (boolean). Same fields → findings from different lanes sort, dedupe, and merge into one ranked list mechanically. Without the schema each lane returns its own prose and merging means re-reading everything: the aggregation cost lands on the coordinator, which is the one place in a swarm that must stay cheap. **Evidence** carries a second job — it's the anti-confabulation lever. A finding that cannot name the line it lives on isn't a finding, and requiring the field is what makes that rejectable at the boundary rather than arguable in review.

### Make "nothing found" a first-class result — the stub contract

Under "find X" framing, agents invent findings to avoid returning empty — the frame implies X exists, and an empty answer reads as failure. The counter is an output contract where empty is a valid, machine-checkable SUCCESS: a top-level found-nothing flag, an explanation, and a results array.

- **Exactly two legal combinations**, enforced by schema PLUS post-checks: flag true ⇒ empty results + non-empty explanation; flag false ⇒ ≥1 result + empty explanation. Flag false with empty results fails the attempt; so does flag true with results riding along.
- **State the anti-fabrication rule explicitly in the prompt** — tell the model, in your own words, that a no-finding response counts as a valid successful outcome and that inventing a result to avoid one is the failure. The schema makes empty expressible; the sentence makes it permissible.
- **Pin the keys**: stamp `additionalProperties: false` and `required` on every field so keys cannot drift; cap the results array when the step is single-output, and re-check the cap after parsing.

This removes the *pressure* to fabricate; the **Evidence** requirement above rejects the fabricated positives that still slip through. The repeat-run lever in the swarm section returns exactly this stub when a later pass finds nothing new.

## When NOT to add an agent

Before spawning a second agent, ask the lean question (`fabius-parcus`): does it need to exist? A single agent with the right tools beats a swarm unless the work is genuinely independent (parallel), needs an independent reviewer (a checker that didn't write the code), or won't fit one context window. A swarm that could be one prompt is over-engineering with extra latency.
