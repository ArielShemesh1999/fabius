---
name: fabius-machina
description: >
  fabius's automation layer — wire deterministic service-to-service workflows and prove the wiring
  before it runs live. This is no/low-code integration glue (n8n-class): triggers, nodes, webhooks,
  scheduled jobs, API-to-API connections, branching, and error paths. It is NOT agent orchestration —
  that's fabius-cohors. The line: machina wires deterministic steps across SaaS/APIs where each step's
  behavior is fixed; cohors orchestrates LLM agents whose behavior is generative. Use when the user
  says "automate X", "build a workflow", "connect A to B", "when X happens do Y", "set up a webhook /
  a cron / an integration", or names n8n / Zapier / Make. The build discipline, the tool-per-intent
  map, the silent-failure gotcha catalog, and the deployment gate live in references/automation-playbook.md.
when_to_use: >
  "sync these two apps", "nightly job", "when a form is submitted send an email", "glue these
  APIs together", scheduled or event-driven pipelines.
license: UNLICENSED
metadata:
  author: Ariel Shemesh
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Machina — wire the steps, prove the wiring

*Machina* — the contrivance, the working mechanism. An automation is a machine made of other people's APIs: it runs unattended, it moves real data, and a silent miswire double-sends or drops items with no error. So the discipline is the same as everywhere in fabius — **scout the live system, strike the smallest correct wiring, prove it before you trust it.**

## 1. Machina vs cohors — pick the right kind of orchestration

- **machina** — *deterministic* glue. Fixed steps across SaaS/APIs: a webhook fires → transform → call an API → branch → write. The behavior of each node is known in advance. Reliability and idempotency are the whole game.
- **cohors** — *generative* orchestration. LLM agents whose output isn't fixed; the work is least-privilege tools, output contracts, and the agent patterns.

A workflow that *contains* an AI step is still machina at the seams (the wiring) and cohors at that one node (the agent). Own each at its layer; don't collapse them.

## 2. The build discipline — never one-shot a live workflow

1. **Discover from the live schema, never from memory.** A platform's node/API surface drifts between releases; read the *current* schema for every node you place. Memory is where silent failures begin.
2. **Build incrementally with surgical edits.** Prefer a partial/patch update over regenerating the whole workflow — smaller blast radius, far higher success rate. Always attach an explicit *intent* so the platform can give you a useful error.
3. **Validate AND verify.** Validation proves the JSON is well-formed; it does **not** prove the workflow does what you meant. After it validates, inspect the connections against the intended data flow — the two are different checks.
4. **Test on sample data, then activate.** Tests *execute* — writes write and messages send. Run on safe sample input, confirm the real effect, and only then flip it live.

> **"Validation passing" ≠ "workflow correct."** Treat them as two gates, in that order.

## 3. Tool-per-intent and explicit profiles

Map each intent to the right operation rather than reaching for one do-everything call: *discovery* (search/get the node from its live schema) · *checking* (validate node, then validate workflow) · *build vs edit* (create a new workflow vs a surgical partial update). Always pass an **explicit validation profile** (the full, as-if-executing one for real builds) — never rely on the default, which under-checks.

## 4. The silent-failure catalog — what breaks without erroring

Every automation platform has a set of gotchas that *fail silently* — no exception, just wrong data. They are learned by getting burned, so catalog them: payload-nesting surprises (a webhook body arrives nested, not at the root), return-shape mismatches (one node returns a string, another a wrapped object), credential placeholders that lock the UI selector, ID-format requirements, loop-output wiring (which port is the body, which is "done"), default success codes on error paths, and inline-code import limits that belong to the *deployment* rather than the language (the same code node imports different things on a hosted instance than on a self-hosted one). The *specific* gotchas are platform-specific (the playbook captures n8n's); the **practice transfers**: keep a living silent-failure list for whatever platform you wire, and check against it before activating.

## 5. Make it survive Day 2

Idempotency (a re-fired trigger must not double-act), explicit error responses (so the caller knows it failed), retries with backoff, and secrets in env / a manager — never in the workflow JSON (`fabius-praesidium`, `fabius-parcus`). Where the platform ships native dedupe state, use it rather than hand-rolling one.

**The inline-code node is a trust boundary, not a convenience.** On a platform that executes user code *inside its own process*, whoever can edit a workflow can run code as the host — "can edit a workflow" and "can execute on the box" are the same permission. So isolate the executor, or remove it. On n8n that means task runners in external mode (`N8N_RUNNERS_MODE=external`, a shared `N8N_RUNNERS_AUTH_TOKEN`, the runner in its own sidecar): the `internal` default launches the runner as a child process sharing n8n's `uid`/`gid`, and n8n's own docs call it not-for-production. Where you can't isolate it, drop the code node instead (`NODES_EXCLUDE='["n8n-nodes-base.code","n8n-nodes-base.executeCommand","n8n-nodes-base.localFileTrigger"]'` — the var is a JSON array that **replaces** the secure default rather than extending it, so re-list what shipped in it or hardening the Code node silently re-enables Execute Command) and stay on declared nodes. Escapes at this seam are a patch cadence, not a one-off — follow the platform's advisories and stay current. An automation you can't safely re-run — or safely let a colleague edit — is a liability, not a feature.

## References

- The full build discipline, the tool-per-intent decision map, the n8n silent-failure gotcha catalog (as the worked example), the deprecation runway, the code-sandbox isolation setup, and the ordered deployment gate → `references/automation-playbook.md`.
- The integration-platform decision map — managed-OAuth catalogs (Composio), self-hostable engines (Activepieces), the MCP bridge (first-party vs community), and the discipline that survives a platform swap → `references/integration-ecosystem.md`.
- The verified platform + durable-execution stack — visual platforms (n8n/Node-RED/Activepieces), durable execution (Temporal/Trigger.dev/Hatchet/DBOS), data orchestrators, and webhook/queue infra (Svix/Hookdeck/BullMQ) with the Standard Webhooks signing-and-dedupe contract, fair-code/AGPL/SSPL licenses flagged → `references/automation-toolkit.md`.

**Live tier (optional).** Discovery, validation, and design need no runtime; *driving a live instance* needs an MCP bridge — and there are now two, so the choice is real. n8n ships a **first-party instance-level MCP server built into every edition** (Cloud, Enterprise, free self-hosted): nothing extra to run, workflows opt in one at a time, and it authenticates by OAuth or a personal MCP access token rather than the public API key. The community **`n8n-mcp`** is the deeper catalogue (2,400+ nodes, community ones included) with autofix, and its discovery and validation run against *no instance at all*; writes there take `N8N_API_URL` / `N8N_API_KEY`. Default to the first-party server on a current instance; reach for `n8n-mcp` when you need coverage past the core nodes or must design offline. fabius bundles neither — the full map is in [ARCHITECTURE.md](../../ARCHITECTURE.md) (*External connections*).

Pairs with: `fabius-cohors` (when a step needs a real LLM agent — own that node there), `fabius-disciplina` (the `step → verify` plan *is* the workflow; prove it on sample data before live), `fabius-praesidium` + `fabius-parcus` (credentials in env, least privilege, smallest wiring that holds). `stop fabius` drops the stance (kill-switch owned by `fabius`).
