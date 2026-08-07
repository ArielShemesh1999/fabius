# Fabius Machina — the automation & durable-execution toolkit

Loaded on demand by `fabius-machina`. Best-in-class (2026) platforms for deterministic service-to-service wiring, license-verified — because automation licensing is a minefield: **n8n is fair-code** (source-available, no reselling as a service), **Windmill AGPL**, **Inngest server SSPL**, **Make/Zapier proprietary SaaS**; the genuinely permissive options are marked. Honest note: **HuggingFace is not the tool here** — the one reliable route to correct workflow JSON is a **schema-grounded MCP server**, not a fine-tuned model.

## Visual / no-code platforms

> **Seam before you pick a canvas — the artifact decides.** A visual/no-code canvas whose **deliverable is a deterministic workflow** (fixed steps wiring SaaS/APIs, even if one step calls an LLM) is machina's — below. A visual/no-code canvas whose **deliverable is *the agent itself*** (a generative LLM agent) is **`fabius-cohors` → Flowise** (`references/agent-frameworks.md`), not here. n8n's "AI-agent nodes" embed a generative step *inside* a deterministic flow; they don't make n8n the place to *build an agent*. If the user says "build an agent" → cohors, every time.

| Platform | License | Note |
|---|---|---|
| **n8n** | ⚠️ **fair-code** (Sustainable Use) | The reference visual canvas — 1500+ integrations, AI-agent nodes, workflows as **plain JSON** (sealable/diffable/dry-runnable). *Self-host free, but can't resell as a hosted service.* **The deliverable is a deterministic workflow; if it's the agent itself → `fabius-cohors`/Flowise.** |
| **Node-RED** | Apache-2.0 | The truly-open (Apache) counterpart — flows as JSON, run locally; strongest in IoT/edge/protocol glue. When license purity matters. |
| **Activepieces** | MIT (core) | MIT self-hostable Zapier-alt where ~280+ "pieces" are also **MCP servers** — design the flow *and* drive the connectors. *(Enterprise pieces separately licensed.)* |
| **Make** · **Zapier** | proprietary SaaS | Breadth (3k / 9k+ connectors) + hosted MCP endpoints, but **nothing sealable/ownable** — flag the lock-in vs n8n. Zapier MCP keeps credentials with Zapier, not the model. |
| **Huginn** | MIT | Most self-sovereign watch-and-notify (self-host, no vendor). *Mature-but-quiet — commits land but last tagged release 2022.* |

## Code-first durable execution — the silent-failure killer

The core machina rule is *no step silently half-completes.* Durable-execution frameworks give exactly-once-ish semantics at the framework level instead of hand-rolled retries.

| Framework | License | Note |
|---|---|---|
| **Temporal** | **MIT** | Write workflows as ordinary code (Go/Java/TS/Py/.NET); survives crashes via event-sourced replay. The code-first heavyweight — infra you operate. |
| **Trigger.dev** | Apache-2.0 | TS durable background tasks/AI workflows — retries, queues, idempotency keys, observability dashboard (the *prove-it-ran* surface). Ensure v4 docs. |
| **Hatchet** | MIT | Postgres-backed durable task queue / orchestration — fully permissive, uses the Postgres you likely already run. A cleaner sealable answer than SSPL Inngest. |
| **DBOS Transact** | MIT | A *library* (not a server) that checkpoints workflow state into your Postgres so a program resumes from the last completed step after a crash — durable execution as an ownable, code-first artifact. |
| **Inngest** | ⚠️ **SSPL** (server) | Event→step→retry with step memoization, minimal infra — but the **server is SSPL** (SDKs Apache). |
| **Windmill** | ⚠️ **AGPL-3.0** | Scripts (TS/Py/Go/Bash/SQL) → APIs/jobs/flows + auto-UIs, git-syncable — but **network-copyleft**. |

## Data / scheduled orchestrators (all Apache-2.0)

- **Airflow** — the institutional scheduled-DAG default (ETL-shaped); 3.x task isolation cuts partial-run failures. **Prefect** — Airflow-class in lightweight dynamic Python. **Dagster** — asset-oriented with types + lineage + local materialization (the most *test-first*, dry-run-before-live). **Kestra** — declarative **git-native YAML** workflows — a plain diffable text artifact, ideal for machina's seal/review discipline.

## Webhook & queue infrastructure

- **Svix** (MIT) — reliable **outbound** webhooks: HMAC signatures, backoff retries, delivery logs — turns "fire a POST and hope" into provable delivery. **Hookdeck** (proprietary, free tier) — the **inbound** counterpart (ingest, durable queue, dedup, replay) — closes the dropped/duplicated-inbound-event gap Svix doesn't. **BullMQ** (MIT) — Redis-backed durable queue between steps (backpressure, delayed jobs, retries) you fully own.

**Emit the Standard Webhooks shape whether or not you use a vendor** (spec Apache-2.0; it is the convention receivers now expect — OpenAI, Anthropic, Google, Twilio, Kong, PagerDuty, Supabase, Clerk, ngrok and Resend among the implementers). Three fixed headers — `webhook-id`, `webhook-timestamp`, `webhook-signature` — over a signed `id.timestamp.payload`: HMAC-SHA256 under a `v1` prefix, or ed25519 under `v1a` when the receiver must verify without holding the shared secret, and multiple space-delimited signatures so a key can be rotated without dropping deliveries. Two receiver-side rules fall straight out of it and make machina's abstract Day-2 advice concrete: **reject any delivery whose `webhook-timestamp` is outside your tolerance window** — that is the replay defence — and **use `webhook-id` as the idempotency key**, held for a few minutes, which is exactly the stable dedupe key the re-fire rule asks for. Nothing rival is pending: the IETF `Idempotency-Key` header draft expired without ever becoming an RFC, so this convention is the contract.

## The agent's build path — schema, not a model

**n8n-mcp** (`czlonkowski/n8n-mcp`, MIT) is the headline: an MCP server giving the agent structured access to 2,400+ n8n nodes + schemas (core *and* community), so it **looks up the real node config and validates before emitting JSON** instead of hallucinating params — the skill's *prove-the-wiring-before-live* gate. It also carries the gates the discipline asks for: autofix-with-preview, a test run, workflow versions to roll back an edit. n8n now ships a **first-party instance-level MCP server in every edition** too (Cloud, Enterprise, free self-hosted) covering the same five gates with nothing extra to run — but over core nodes only, and it needs a live instance. Take the first-party server on a current instance; take `n8n-mcp` for community-node coverage or discovery with no instance at all. Either beats the negligible-adoption n8n-workflow-generator fine-tunes on HF; don't reach for a model where a schema will do.

## Pairs with

`fabius-machina` (the build-and-verify discipline + silent-failure catalog), `fabius-cohors` (the line: machina wires *deterministic* steps; cohors orchestrates *generative* agents), `fabius-praesidium` (webhook signing, least-privilege credentials), and `fabius-parcus` (a fair-code/AGPL/SSPL dependency in a sealed product is a real constraint — pick the permissive option the task allows).
