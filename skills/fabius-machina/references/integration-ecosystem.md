# Fabius Machina — integration-platform decision map

Which wiring platform to reach for once the task outgrows the n8n worked example. The skill is the contract; this is how you pick the seam without re-implementing what a maintained catalog already hardens.

n8n + `n8n-mcp` is machina's worked example (→ `automation-playbook.md`). It is not the only shape. The intent decides the platform; the five gates — discover → build → validate AND verify → test → activate — and every Day-2 rule (idempotency, explicit errors, retries-with-backoff) hold on **all** of them. None of these is fabius-bundled runtime; they are the optional live tier (→ [ARCHITECTURE.md](../../../ARCHITECTURE.md) → *External connections*). Versions below are an early-2026 snapshot — encode the decision, re-verify the version number.

## 1. Pick by the binding intent — not by familiarity

| If the task is… | Reach for… | Why |
|---|---|---|
| "connect to 50 SaaS APIs, each with its own OAuth" | a **managed-OAuth tool catalog** (Composio) | the auth dance is already hardened — don't hand-roll it |
| "the data can't leave our network" | a **self-hostable engine** (Activepieces) | network isolation; the wiring stays on-prem |
| "let an agent *drive* the workflow" | an **MCP-bridged platform** (n8n-MCP and peers) | the agent calls the seam; wiring stays deterministic |
| "wire fixed steps across known SaaS/APIs" | n8n / Zapier / Make (the worked example) | the default; tool-per-intent map already written |

The platform is a means. The five gates and Day-2 rules are the same regardless of which you pick.

## 2. Managed-OAuth tool catalogs — don't re-implement the auth dance

When the intent is breadth ("connect to dozens of SaaS APIs"), a managed-integration layer removes hand-rolling each auth flow.

**Composio** (early 2026: 1000+ tools, managed OAuth, MCP server + multi-framework bindings) is the catalog of record here. The decision rule:

- **Don't re-implement an OAuth flow a maintained catalog already hardens.** Token refresh, scope handshakes, revocation — these are where hand-rolled glue rots silently.
- **Still least-privilege the scope.** A managed catalog makes the broad grant *easy*; that is the trap. Request only the scopes the workflow uses (→ `fabius-praesidium`).
- **Secrets stay in env / a manager — never in the workflow JSON**, catalog or not (→ `fabius-parcus`).
- The five gates do not relax: the catalog hands you a working connection, not a correct workflow. **Validate AND verify** the data flow before activating.

## 3. Open / self-hostable engines — keep the wiring on-prem

When data can't cross the network boundary, a self-hostable engine with network isolation keeps the whole machine inside it.

**Activepieces** (early 2026: 280+ pieces, pieces exposable as MCP servers, hot-reload, type-safe connectors) is the worked example. Self-hosting changes *where* it runs, not *how* you build:

- **Discover from the live schema** — the running instance's piece versions, not memory. Self-hosted ≠ frozen; pieces still drift.
- **Validate AND verify** — type-safe connectors catch shape errors at the seam, but type-checking is validation, not verification. A type-correct workflow can still be wired backwards.
- **Test on sample data before activating.** On-prem writes are still real writes.
- **Network isolation is a security property to keep, not just a deployment fact** — egress rules and secret handling are `fabius-praesidium`'s concern; route there, don't re-spec here.

## 4. The MCP bridge — let an agent drive, keep the seam machina

An automation platform exposed over MCP lets an agent operate the workflow tooling — discover nodes, build, validate, trigger.

**n8n-MCP** (the worked example's community bridge) and its peers are this layer — and check the platform's own shipped bridge before installing a third-party one; n8n now has a first-party instance-level MCP server in every edition (→ `automation-playbook.md`). The hard rule at this seam:

- **The seam stays machina.** The wiring the agent builds is still deterministic glue — five gates, silent-failure catalog, idempotency. The MCP bridge changes *who calls the tools*, not what the wiring is.
- **The agent node stays cohors.** When a *node inside the workflow* is itself an LLM agent (generative output, tool loop), that node is `fabius-cohors`' concern. Own each at its layer; don't collapse them.
- An agent driving the build does **not** earn a skipped gate. Agent-assembled workflows use the tolerant validation profile (`ai-friendly`) *and then* the runtime verify — the looser profile is for assembly, not for activation.

## 5. What does not change across platforms

The platform is the only variable. These hold on every one:

- **Discover from the live schema, never from model memory** — every platform's surface drifts.
- **Validate AND verify** — two gates, in order; "validation passing" ≠ "workflow correct."
- **Test on sample data, then activate** — tests execute; the first real run must not be the activation.
- **Idempotency** — a re-fired trigger must not double-act. Dedupe on a stable key; upsert, don't blind-insert.
- **Explicit error responses + retries with backoff** — the caller must be able to tell it failed; transient retries are bounded.
- **Least privilege + secrets in env** — managed catalog or self-host, the scope is narrow and the secret is never in the JSON (→ `fabius-praesidium`, `fabius-parcus`).
- **Smallest wiring that holds** — reach for a heavier platform only when the intent (breadth, isolation, agent-driven) actually demands it; otherwise stay on the default (→ `fabius-parcus`, the YAGNI ladder).

## 6. The personal-account / browser-session routine — an observed product shape

Some products expose the trigger→action model at a layer machina never wires: the user's own logged-in browser. **Strawberry** (strawberrybrowser.com — a closed commercial AI browser, free-2000-credits → $250/mo tiers) ships **"Routines"**: event-triggered recurring tasks fired by events in the user's *own* Gmail / Slack / GitHub — *when an email lands, draft a reply; when a PR is ready, approve it.* The same shape machina already owns: an event fires, a fixed action runs. Alongside it — no-bot meeting transcription, structured web-data extraction to spreadsheets, capture from login-protected pages — all riding the user's existing sessions.

**Closed-source, no public API or SDK — nothing here to integrate.** This is the Wispr Flow treatment (→ `fabius-cohors` → *Voice in — the polish law*): the product ships no seam to wire against, so what transfers is the pattern, not a connector. No credits row. An observed product shape, re-derived — not a tool fabius applies.

**What it validates.** The event-triggered Routine over personal accounts is machina's trigger→action seam relocated to the browser-session layer. It confirms the model holds where the actor is the user's authenticated tab rather than a service token — the same five gates, the same idempotency-on-a-re-fired-trigger. Nothing new to build.

**⚠️ The ambient-authority caveat.** An agent acting *inside* your live, already-logged-in sessions wields **broad ambient authority**: it can do anything your logged-in self can, with **no per-action scope** and no OAuth grant to narrow. This inverts machina's normal failure mode — a service-token workflow fails *closed* to its granted scopes; a browser-session actor fails *open* to the whole authenticated identity. A managed catalog at least names its scopes (§2); a live session grants everything at once. That is a standing least-privilege / consent / audit problem, not a feature — route it:

- **least-privilege + consent gate + audit trail → `fabius-praesidium`.** Ambient session authority needs an explicit per-action consent boundary and a logged trail; the browser gives neither for free.
- **the browser-driving actor → `fabius-cohors`.** The moment the actor is a *computer-use / browser-driving agent* — generative, deciding what to click — that's cohors' concern. Machina owns only the **deterministic trigger→action seam**; the generative actor at the other end of it is never machina.

**Personalization / memory** — the "remembers you across sessions" claim — is already held by `fabius-archivum`; nothing to add here.

## Boundary — where this doc stops

This is machina's platform map: which deterministic-wiring engine fits which intent, and the discipline that survives the swap. It does **not** cover agent orchestration — the moment a node *is* an agent, that's `fabius-cohors`. It does **not** re-spec credential handling or network isolation — that's `fabius-praesidium`. The catalogued strengths above (Composio, Activepieces, n8n-MCP) are capabilities fabius can *apply*, credited to their tools — fabius bundles no runtime; the optional live tier is in [ARCHITECTURE.md](../../../ARCHITECTURE.md).

*Tool names and version figures (Composio 1000+ tools, Activepieces 280+ pieces) are an early-2026 ARGAZ-directory snapshot — point-in-time, not fabius-measured. Re-verify before relying on a number.*
