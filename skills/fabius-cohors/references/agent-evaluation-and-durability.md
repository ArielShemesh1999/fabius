# Fabius Cohors — evaluate, endure, equip, sandbox

Loaded on demand by `fabius-cohors`. The skill defines and orchestrates agents; this file is the operational tier — how to *score* an agent, *survive* a run that outlives one context, *give* it tools, and *contain* the code it writes. These are capabilities fabius **applies**, drawn from named ecosystem tools — not runtime fabius bundles. The optional live tier (MCP, sandboxes) is in [ARCHITECTURE.md](../../../ARCHITECTURE.md). Tool names, protocol revisions and versions below are a mid-2026 snapshot — encode the decision, re-verify the version before you wire it.

## 1. Evaluate agents — don't trust vibes

**An agent you can't score, you can't improve.** Before you scale a fleet, build a ground-truth benchmark: a labeled task set with expected outputs, scored automatically.

- **The artifact** — a JSON task set: `{ input, expected, check }` per case. `check` is exact-match, schema-match, or a rubric an LLM-judge applies. Run the agent, compute a **pass-rate**, diff against the prior run.
- **Per-role suites** — a reviewer suite (does it catch the planted bug?), a debugger suite (does it find the real root cause?), an executor suite (does the output match the contract?). One agent, one suite; the suite *is* the spec.
- **The rule** — define the eval *before* scaling. No benchmark → no claim that v2 beats v1; "sounds better" is not a metric (M5, `fabius-disciplina`).
- **Ecosystem to copy from**: oh-my-claudecode's benchmark suite, gstack evals, ralph-claude-code's 784-test gate. Port the harness shape — labeled set + automated scorer + pass-rate delta — into your stack.

→ The eval **is the prove step** for an agent (`fabius-disciplina`). A held-out real-example set, not a vibe check.

## 2. Survive long-horizon runs

A loop that exceeds one context window is a different machine. **A long autonomous loop with no checkpoint and no stop condition is a runaway, not an agent.** Make it durable:

- **Session continuity / resume** — persist run state so a killed or context-exhausted run picks up where it stopped, not from zero.
- **Checkpointing** — snapshot progress at each completed unit; resume from the last good checkpoint.
- **Git backup of work** — commit the agent's output as it goes, so a crash loses one step, not the run.
- **Log rotation** — bound the log so a multi-hour run doesn't drown its own context or disk.
- **Dry-run mode** — a no-write rehearsal that proves the plan before the loop touches anything real.
- **Dual exit gate** — stop on **done OR no-progress**. A loop that can only exit on "done" never exits when it's stuck. Cap retries (~3), then escalate to a human (M4, `fabius-disciplina`).
- **Resume must not re-run a completed side effect.** Restarting is the moment a run duplicates the email it already sent, the row it already inserted, the release it already cut. Checkpoint the *effect*, not just the plan.
- **Ecosystem to copy from**: ralph-claude-code (resume, checkpoint, git-backup, log-rotation, dry-run, the done-or-no-progress gate). Take the durability scaffolding; keep your own agent definition.

**Or attach an engine instead of hand-rolling the scaffolding.** Durable execution is a tier you bolt onto an agent now. The engine journals each completed step and replays the journal on restart, so a resumed run *replays* the tool calls it already made instead of re-issuing them — the rule above, enforced by the runtime rather than by the operator's memory. **Temporal, DBOS and Prefect attach directly to a Pydantic-AI agent** (Restate integrates through its own SDK); **DBOS wraps an OpenAI-Agents runner** with `@DBOS.workflow` / `@DBOS.step` and needs only Postgres — SQLite in development — so there is no new infrastructure to stand up; **LangGraph** has the property natively through checkpointers plus an explicit durability setting. Reach for the engine when the run is long, asynchronous, or human-gated. Keep the hand-built checkpoint only when adding a database is genuinely the heavier cost.

For the swarm's own durability — shared task list as source of truth, coordinator reassigning stalled work — see SKILL.md and `references/agent-patterns.md`.

## 3. Acquire tools via MCP

Agents get capabilities through **MCP servers** — the standard for tool acquisition. **fabius bundles no MCP**; this is the optional live tier (→ ARCHITECTURE.md). Three ways in:

- **Official reference servers** — filesystem, git, fetch, memory. The smallest trusted surface; start here.
- **Managed OAuth catalogs** — Composio (~1000+ tools, OAuth-managed). Reach for it when the agent needs SaaS reach (calendars, issue trackers, email) you don't want to credential by hand.
- **A bridge** — langchain-mcp-adapters wires stdio/HTTP MCP servers into an agent framework. Use when your harness isn't natively MCP.

**MCP went stateless — that is a wiring decision, not a vocabulary change:**

- **No handshake, no session header.** The `initialize` exchange and `Mcp-Session-Id` are gone; every request carries its own protocol version and client capabilities in `_meta`, and `server/discover` — which servers MUST implement — advertises what a server speaks.
- **Cross-call state is a server-minted handle passed as an ordinary tool argument.** Which puts a new attack in scope: **possession of a handle is not authentication.** Bind each handle to the caller it was minted for, or a leaked one is a session somebody else drives.
- **Streams are not resumable.** Streamable HTTP is the live transport (HTTP+SSE is formally deprecated) and `Last-Event-ID` redelivery went with it: a broken response stream loses the in-flight request and the client **re-issues it as a new request**. That is a re-execution hazard aimed straight at §2 — give every side-effecting tool an idempotency key, or the transport duplicates the effect for you.
- **Don't build on the deprecated surface:** Roots, Sampling and Logging (pass paths as tool parameters; call the provider API directly; log to stderr or OpenTelemetry), and OAuth Dynamic Client Registration (use Client ID Metadata Documents). Long-running work moved out of core into the official `io.modelcontextprotocol/tasks` extension, polled rather than blocking.
- **Pin the protocol revision you target and re-read the changelog before you wire.** A twelve-month deprecation window is policy now, not courtesy — long enough that a server you adopted still works while everything written about it goes stale.

**Least-privilege still rules** (same floor as `references/agent-patterns.md`):

- Grant the **smallest tool scope** — one server, the few tools the task needs, not the whole catalog.
- **Prefer read-only** — a fetch/read server over one that can also write or send.
- **Scope every credential** — narrowest OAuth scope, per-agent token, never a shared god-key.
- A tool that can spend money, hit prod, or send externally goes behind a human gate or `ask` — never `allow` by default.

## 4. Sandbox agent-written code

**Never run code an agent generated on the host.** This is non-negotiable — same tier as `fabius-parcus`'s never-trim security floor. Generated code is untrusted input; the host is not a sandbox.

| Sandbox | Use when |
|---|---|
| **E2B** | hosted code-interpreter sandbox; quick to wire, ephemeral per-run |
| **Modal** | serverless containers; heavier compute, scales out |
| **Docker** | local isolation you fully control; no-network, read-only-FS flags |
| **QuickJS-WASM** | in-process JS with **no host file/network access** — the tightest, for pure compute |

- **Default deny** — no host filesystem, no host network, no host credentials reach the sandbox.
- **Ecosystem to copy from**: smolagents — a ~1000-line code-agent that runs generated code in a sandbox by default. Adopt the *posture* (sandbox is the default execution path), not just the library.

→ Prompt-injection screening *before* execution is the safety-guard shape in `references/agent-patterns.md`; sandboxing is the containment *after* it.

## 5. Portability — author once, transform out

A single agent source can target many harnesses — Cursor, Codex, Gemini, Copilot — via per-harness transforms. The four reliability properties (precise `description`, tight tool allowlist, explicit output contract, least privilege) are invariant; only the frontmatter keys differ per harness (see `references/agent-patterns.md`). **Author the agent once, transform to each target — don't hand-maintain N copies that drift.**

---

These four — eval, durability, MCP tooling, sandboxing — apply *on top of* a well-defined agent. They never replace the definition or the orchestration pattern; a fast, durable, well-tooled agent with a vague `description` and no output contract is still a bad agent. Define it first (SKILL.md), then make it measurable and survivable. Deterministic no-code wiring of any of this → `fabius-machina`.
