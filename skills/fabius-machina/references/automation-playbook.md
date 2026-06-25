# Fabius Machina — automation build-and-verify playbook

The on-demand depth for `fabius-machina`'s build-and-verify discipline. The skill is the contract; this is how you run each step — templates, decision tables, commands, gotchas. Scout wide, strike narrow.

n8n + `n8n-mcp` is the **worked example** throughout. The shape is platform-agnostic; the gotchas are n8n's. Carry the shape to Zapier/Make/Pipedream; rebuild the gotcha list per platform.

## The transferable shape

```
discover (live schema) → build (surgical edits) → validate AND verify → test (sample data) → activate
```

Five gates, in order. Skipping any is where silent failures enter. The shape is fixed; the tools below are how you run it on n8n.

## 1. Discover from the live schema — never from model memory

The node/API surface drifts between releases: param renamed, default flipped, a port added. Model memory is a stale snapshot. Read the *current* schema for **every** node you place.

```
search_nodes({ query: "slack" })          # find the node
get_node({ nodeType, includeExamples: true })  # current params + worked examples
```

`includeExamples: true` is not optional — the examples encode the shapes (return form, port semantics) you'd otherwise guess wrong.

Two prefix formats coexist — **wrong prefix = node-not-found**:

| Context | Prefix | Example |
|---|---|---|
| search / validate | short | `nodes-base.slack` |
| create / CRUD | full | `n8n-nodes-base.slack` |

## 2. Build incrementally — patch, don't regenerate

A surgical partial update beats regenerating the whole workflow: smaller blast radius, far higher success rate (the project's testing log reports ~99% success on partial updates vs frequent failure on full regenerates — *reported by the project*, not fabius-measured).

```
n8n_create_workflow(...)              # NEW workflow only
n8n_update_partial_workflow({         # every edit after — surgical
  intent: "add error branch to HTTP node",   # ALWAYS pass intent
  operations: [ ... ]
})
```

**Always attach an explicit `intent`.** Without it the tool can't tell you *why* an edit was rejected; with it you get an actionable error instead of a silent no-op. Rule: create once, then only ever partial-update.

Templates skip the blank page when one fits:

```
search_templates({ query: "..." }) → n8n_deploy_template({ id })
```

## 3. Validate AND verify — two different gates

- **Validate** = the JSON is well-formed and params type-check. Says nothing about correctness.
- **Verify** = the **connections** match the intended data flow. The trigger reaches the transform reaches the write; the error port goes somewhere; no orphan node.

```
validate_node({ nodeType, ... })       # per-node, before wiring
validate_workflow({ workflow, profile: "runtime" })   # whole graph
```

> "Validation passing" ≠ "workflow correct." A perfectly-valid workflow can be wired backwards.

**Always pass an explicit profile** — the default under-checks:

| Profile | Use |
|---|---|
| `minimal` | fast structural pass while drafting |
| `runtime` | **default for real builds** — checks as if executing |
| `ai-friendly` | tolerant shapes for agent-driven assembly |
| `strict` | pre-production, every gate on |

## 4. Test on sample data, then activate

Tests **execute**: writes write, messages send, emails leave. Run on safe sample input first, confirm the *real* effect (row appeared, message landed), then flip live. Never let the first real execution be the activation.

## Tool-per-intent map (n8n-mcp)

| Intent | Tool | Needs instance API? |
|---|---|---|
| discovery | `search_nodes` / `get_node(includeExamples:true)` | no |
| node check | `validate_node` | no |
| workflow check | `validate_workflow` | no |
| templates | `search_templates` / `n8n_deploy_template` | no |
| docs | `get_node` docs | no |
| **build** | `n8n_create_workflow` | **yes** |
| **edit** | `n8n_update_partial_workflow` | **yes** |
| credentials / audit | credential + audit ops | **yes** |

Split by configuration: **search / validate / template / docs need no API.** CRUD / credential / audit ops need `N8N_API_URL` + `N8N_API_KEY` set. Discover and validate fully without an instance; you only need the live instance to write.

## The silent-failure catalog (n8n) — fail with NO error, just wrong data

These are learned by getting burned. Check against them before activating.

| Gotcha | Trap | Do this |
|---|---|---|
| **Webhook nesting** | payload is under `$json.body`, not `$json` | reference `$json.body.field` |
| **Code return shape** | Code node returns `[{json:{...}}]`; the agent-callable **Code Tool** returns a plain **string** (constantly confused) | match the form to the node kind |
| **Placeholder credential** | a `REPLACE_ME` id **permanently disables** the UI credential selector | omit `credentials` entirely if unknown |
| **Node IDs** | non-UUIDv4 ids cause subtle UI binding failures | generate real UUIDv4 ids |
| **SplitInBatches ports** | `main[1]` = loop body (per batch), `main[0]` = done — easy to swap | wire deliberately; add a Limit-1 after `main[0]` |
| **responseCode** | defaults to `200` even on error paths | set the code explicitly on error branches |
| **Python Code node** | stdlib only — **no external libraries** | use JS, or stay in stdlib |
| **Two prefix formats** | short for search/validate, full for CRUD (see §1) | match prefix to operation |

Prefer **smart parameters** over fragile index math: `branch: "true"` for an IF node, `case: 0` for a Switch — not raw output-index arithmetic that breaks when ports reorder.

**The general rule:** every automation platform has its own silent-failure set. Keep a living per-platform list and check it before activating. The list above is n8n's; the *practice* transfers.

## Day-2 — make it survive re-firing

- **Idempotency** — a re-fired trigger must not double-act. Dedupe on a stable key; upsert, don't blind-insert.
- **Explicit error responses** — set real status codes on error paths (don't let `200` lie); make the caller able to tell it failed.
- **Retries with backoff** — for transient upstream failures; bounded, not infinite.
- **Secrets in env / a manager** — never in the workflow JSON (`fabius-praesidium`, `fabius-parcus`). A workflow you can't safely re-run is a liability.

## Boundary — where machina stops

Machina wires the **deterministic** steps. The moment a node *is* an LLM agent (generative output, tool loop), that node is `fabius-cohors`' concern — own it there. Don't re-document fabius's own router/specialist structure here; the value of this doc is the automation-domain know-how. See `../SKILL.md` for the machina/cohors line, and `../../../CORPUS.md` for where this library sits in the index.

*Numeric claims here (partial-update success rate, node frequencies, timings) are the upstream project's testing-log figures — point-in-time, early 2026, reported by the project, not fabius-measured.*

Adapted from czlonkowski/n8n-skills by Romuald Członkowski (MIT; hooks layer Apache-2.0) — re-expressed in fabius's own voice.
