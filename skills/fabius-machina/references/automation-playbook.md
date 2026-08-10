# Fabius Machina — automation build-and-verify playbook

The on-demand depth for `fabius-machina`'s build-and-verify discipline. The skill is the contract; this is how you run each step — templates, decision tables, commands, gotchas. Scout wide, strike narrow.

n8n + `n8n-mcp` is the **worked example** throughout. The shape is platform-agnostic; the gotchas are n8n's. Carry the shape to Zapier/Make/Pipedream; rebuild the gotcha list per platform.

> **Optional live tier.** The `n8n-mcp` MCP server and `N8N_API_URL`/`N8N_API_KEY` are **not bundled** — the user configures them. Discovery, validation, and design run without an instance; only *writing to a live instance* needs the API. fabius bundles no runtime (see [ARCHITECTURE.md](../../../ARCHITECTURE.md) → *External connections*).

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

### Discovery reads the present; the changelog reads the near future

A platform publishes what it is about to take away, and reading that list is the other half of discovery — ship onto a doomed node and you have inherited someone else's migration. n8n's v3.0 cut (targeted October 2026) removes the legacy **Function**, **Function Item** and **Item Lists** nodes — migrate to the Code node, and to Split Out / Aggregate / Sort / Limit / Remove Duplicates / Summarize respectively — and drops the `$getPairedItem` expression helper in favour of standard item linking. Self-hosted installs become **Docker-only**: `npm` / `npx n8n` stops being supported, so a runbook that installs n8n from npm has an expiry date. Workflow-import-from-URL leaves the editor (file and CLI import stay). If a template you are about to deploy still carries a doomed node, replace it at build time.

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
| templates | `search_templates` / `get_template` / `n8n_deploy_template` | no |
| docs | `get_node` docs | no |
| **build** | `n8n_create_workflow` | **yes** |
| **edit** | `n8n_update_partial_workflow` | **yes** |
| **repair before verify** | `n8n_autofix_workflow` (preview first) | **yes** |
| **test gate** | `n8n_test_workflow` | **yes** |
| **eval gate (AI nodes)** | `n8n_evaluations` (read 2.30+, run/cancel 2.32+) | **yes** |
| **undo a bad edit** | `n8n_workflow_versions` | **yes** |
| state / dedupe store | `n8n_manage_datatable` | **yes** |
| credentials / audit | `n8n_manage_credentials` / `n8n_audit_instance` | **yes** |

Split by configuration: **search / validate / template / docs need no API.** CRUD / credential / audit ops need `N8N_API_URL` + `N8N_API_KEY` set. Discover and validate fully without an instance; you only need the live instance to write.

Run autofix in **preview** (`applyFixes: false`) *before* the verify pass, never after: it rewrites expression formats, typeVersions, error outputs, webhook paths and node types, and you want to read that diff rather than inherit it. `n8n_test_workflow` makes gate four mechanical — it auto-detects the trigger kind (webhook / form / chat) — so a first real run in production is no longer an excuse, and `n8n_workflow_versions` is the rollback that makes a bad surgical edit cheap.

**The first-party bridge covers the same gates under different names.** n8n's built-in instance-level MCP server maps: discovery → `search_nodes` / `get_node_types` / `explore_node_resources`; checking → `validate_node_config` / `validate_workflow`; build → `create_workflow_from_code`; edit → `update_workflow`; test → `test_workflow` + `prepare_test_pin_data`; activate → `publish_workflow` / `unpublish_workflow`; forensics → `get_execution` / `search_executions`; state → the data-table tools. It ships in every edition and authenticates by OAuth or a personal MCP access token rather than the public API key; each workflow must be opted into MCP individually, and self-hosted can shut the whole surface off with `N8N_DISABLED_MODULES=mcp`. Take it when the instance is current; take `n8n-mcp` when you need community-node coverage, autofix, or discovery with no instance at all.

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
| **Python Code node** | the runtime split is the trap, not the library list: Pyodide is gone in v2, and what native Python may import depends on the **deployment** — on Cloud it imports *nothing*, stdlib included; self-hosted imports only what the `n8nio/runners` image ships **and** allowlists | settle the deployment before you write the `import`; on Cloud, do it in JS. A Pyodide script is not a native script — native exposes only `_items` / `_item` and bracket access (`item["json"]["x"]`, never `item.json.x`), so a port is a rewrite |
| **Two prefix formats** | short for search/validate, full for CRUD (see §1) | match prefix to operation |

Prefer **smart parameters** over fragile index math: `branch: "true"` for an IF node, `case: 0` for a Switch — not raw output-index arithmetic that breaks when ports reorder.

**The general rule:** every automation platform has its own silent-failure set. Keep a living per-platform list and check it before activating. The list above is n8n's; the *practice* transfers.

## Day-2 — make it survive re-firing

- **Idempotency** — a re-fired trigger must not double-act. Dedupe on a stable key; upsert, don't blind-insert. Don't hand-roll it where the platform ships it: on n8n that is a **data table** (instance-native rows, no external DB) driven by the Data table node's **Upsert** / **If Row Exists** / **If Row Does Not Exist** operations, or the **Remove Duplicates** node's *Remove Items Processed in Previous Executions* mode for poll-style triggers. Scope that history to the **workflow** rather than the default **node** when several nodes must share one view, and watermark on a monotonic value (*value is higher than any previous*, *date later than any previous*) instead of an unbounded seen-set when the source is a growing feed — the seen-set holds 10,000 items by default, and past that it forgets. Forgetting is a double-send.
- **Explicit error responses** — set real status codes on error paths (don't let `200` lie); make the caller able to tell it failed.
- **Retries with backoff** — for transient upstream failures; bounded, not infinite.
- **Secrets in env / a manager** — never in the workflow JSON (`fabius-praesidium`, `fabius-parcus`). A workflow you can't safely re-run is a liability.
- **Isolate the code executor** — the Code node runs user-supplied code, and in n8n's default `internal` task-runner mode it runs as a child process of n8n sharing its `uid`/`gid`. That makes *edit a workflow* and *execute on the host* the same permission, which is why n8n's own docs rule internal mode out for production. Production shape: `N8N_RUNNERS_MODE=external` with the `n8nio/runners` sidecar (image version matched to the `n8nio/n8n` image) and a shared `N8N_RUNNERS_AUTH_TOKEN`; in queue mode every worker needs its own sidecar. Harden it — the `-distroless` tag, the unprivileged `nobody` user (uid/gid `65532`), a read-only root filesystem with a small writable `/tmp`, and an AppArmor profile that keeps the runner out of `/proc/*/environ`. If you can't run a sidecar, remove the capability instead — but note the var is typed as a JSON array and **replaces** the default rather than extending it, so re-list what shipped there or you re-enable Execute Command while hardening the Code node: `NODES_EXCLUDE='["n8n-nodes-base.code","n8n-nodes-base.executeCommand","n8n-nodes-base.localFileTrigger"]'`. The import allowlists are part of the boundary, not a convenience — `NODE_FUNCTION_ALLOW_BUILTIN` / `NODE_FUNCTION_ALLOW_EXTERNAL` for JS and `N8N_RUNNERS_STDLIB_ALLOW` / `N8N_RUNNERS_EXTERNAL_ALLOW` for Python, set in the launcher's `n8n-task-runners.json`, which ships locked down on purpose. Widen it one package at a time (→ `fabius-praesidium`).

### Scheduled agents — the LLM-specific guardrails

The moment a scheduled node *is* an agent, the node belongs to `fabius-cohors` — but the **scheduler hardening stays here**, and an agent job adds failure modes a deterministic job does not have:

- **Hard per-job interrupt** — config-defaulted, ~10 minutes — so a runaway agent loop cannot monopolize the scheduler.
- **Missed-fire catchup window** = half the job's period, clamped to roughly 2 minutes–2 hours, plus a short grace for one-shots. A fire time outside the window is rejected as stale — never fired late.
- **File-lock the scheduler tick** so concurrent processes cannot double-tick, and record in-flight job ids *before* writing interrupted status — otherwise a run that completes during the write overwrites "interrupted" with a false "ok".
- **Two boundaries that point into cohors territory** (stated here as boundaries, not doctrine): keep scheduled-run content out of the user model — it pollutes user representations — and out of the target chat session. Deliveries land in their **own session** with a header/footer frame so message-role alternation stays valid.
- **Two schema extras worth copying:** a pre-run script whose stdout injects into the prompt (with a script-only mode that degrades an LLM job to a deterministic one), and chaining one job's last output into the next job's prompt.

## Compile the scrape once — LLM at build time, deterministic at run time

The cost rule for recurring extraction: a **one-off question** gets direct LLM extraction over the page; a **recurring or scheduled scrape** spends LLM calls *once* — compiling a verified deterministic extractor — then runs it for free. The compile pipeline:

```
fetch
→ direct LLM extraction over the page   # this answer becomes the validation oracle
→ map the request onto the output schema, field by field
  (note the schema fields the request does not address)
→ analyze a size-reduced copy of the HTML for selectors and repeated
  structure — analysis only, no code, static-HTML target
→ generate the extractor; verify it through the typed gates
  (→ `fabius-cohors` verified codegen)
→ save the script
```

Keep the LLM answer as the **regression fixture**: when the site's HTML changes and the script's output stops validating, re-invoke the compiler — a fabius-derived operating rule. Sizing the HTML copy for the analysis step is the reduction ladder below.

## Fit the page to the window — the reduction ladder

Grade HTML reduction by task:

- **Level 0** = minify — strip comments, collapse whitespace.
- **Level 1** = level 0 + drop every attribute except `class` / `id` / `href` / `src` / `type`, and blank the styles.
- **Level 2** = level 1 + drop the head and truncate every text node to its first ~20 chars. Level 2 is for **selector discovery**, where content is irrelevant.

**Always mine the script tags** — assignments that parse as JSON: on SPAs the data lives in embedded JSON, not the rendered DOM.

For **content extraction**, convert HTML→Markdown first and chunk token-counted against the model window minus a safety margin. Derive chunk size from a per-model context registry with a fail-soft default — copy the registry *pattern*, never its numbers (they rot). Two halves of one pipeline: this ladder sizes the shards; `fabius-archivum`'s map-reduce extraction contract (`external-recall.md`) governs what each shard must return — cross-link, don't duplicate.

## Boundary — where machina stops

Machina wires the **deterministic** steps. The moment a node *is* an LLM agent (generative output, tool loop), that node is `fabius-cohors`' concern — own it there. Don't re-document fabius's own router/specialist structure here; the value of this doc is the automation-domain know-how. See `../SKILL.md` for the machina/cohors line, and `../../../CORPUS.md` for where this library sits in the index.

*Numeric claims here (partial-update success rate, node frequencies, timings) are the upstream project's testing-log figures — point-in-time, early 2026, reported by the project, not fabius-measured.*

Adapted from czlonkowski/n8n-skills by Romuald Członkowski (MIT; hooks layer Apache-2.0) — re-expressed in fabius's own voice.
