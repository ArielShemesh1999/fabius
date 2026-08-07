# Fabius Archivum — auto-recall & external-corpus connectors

The on-demand depth for `fabius-archivum`'s two reflexes: surfacing memory without being asked, and grounding answers in an external source-of-truth. The skill is the contract; this is how you run it. Scout wide, strike narrow.

`fabius-archivum`'s SKILL.md already gives you write + retrieve + when-to-vector. This file deepens the two *automatic* halves: re-injection (Part A) and source-grounded lookup (Part B).

---

## PART A — cross-session auto-recall

Reading the index on start is recall you *choose*. Auto-recall fires on its own. Three named stages — keep them separate, never collapse them into one inline step.

| Stage | Does | Cost discipline | Output |
|---|---|---|---|
| **Capture** | Record raw activity (a decision, a fix, a tool result) as it happens | **Non-blocking** — jot the raw fact, move on | raw event |
| **Compress** | AI-summarize the raw event into a small *typed + titled* record (~a few hundred tokens) | Async, off the hot path | `{ title, type, body, ts }` |
| **Re-inject** | At next session **start**, prepend a compact index of recent records into context | Index only — tens of tokens | context block |

The record is **not a transcript**. A title + a type + a compact body. Typed-and-titled is what makes later filtering and progressive disclosure cheap.

### What re-injection looks like

At SessionStart, prepend one compact block — session summaries + observation titles **grouped by type** + timestamps, for the last ~N sessions:

```
## Recall — last 3 sessions
[decision] 2026-06-24  Chose Base L2 over Optimism for seal anchor — gas + EIP-712 parity
[fix]      2026-06-24  CORS x-turnstile-token header — convert path was 403ing
[gotcha]   2026-06-23  vercel --prod auto-aliases; git push alone does NOT deploy
... (titles only — fetch full body by id on demand)
```

That single prepend is what turns memory from opt-in to automatic. Everything else is bookkeeping.

### The harness may already own this loop

Check what the harness gives you before wiring anything. Claude Code keeps a **per-repo auto memory, on by default**, at `~/.claude/projects/<project>/memory/`: a `MEMORY.md` index loaded at the start of every conversation, plus topic files beside it that are *not* loaded at startup and get read on demand. That is archivum's own shape — index first, detail on request — so **adopt the native store instead of standing up a parallel one beside it**. Four rules ride with it:

- **The index has a hard ceiling.** Only the first **200 lines or 25 KB** of `MEMORY.md`, whichever comes first, load at session start; everything past it is silently dropped. One line per entry, detail in a topic file.
- **Frontmatter and block HTML comments are free.** They're stripped before the index loads, so they don't count against the ceiling — and a write to a file that already has frontmatter stamps a `modified` ISO-8601 timestamp, which is how a later reader tells a live fact from a stale one.
- **A subagent does not inherit the parent's auto memory.** Give it its own (the subagent `memory` field) or it starts blind — the one exception is a fork, which inherits the parent conversation.
- **It is machine-local.** Shared across worktrees of one repo and nothing else — never across machines, never with the team. So the committed `wiki/` keeps what the *team* must read and auto memory keeps machine-local learnings. A fact written into both is a fact that will eventually disagree with itself.

**Hand-wire the loop only where the harness has no store of its own** — a bare agent runtime, another vendor's harness, a service you built. That is exactly why the three stages are named separately above: the *pattern* is what ports across harnesses, and it is the reason this page outlives any one product. On Claude Code the hooks below are the extension and the fallback, not the default.

### Hand-wiring the loop — lifecycle hooks

Claude Code's hook names below are the worked example; read them as the shape any harness's lifecycle has to expose.

| Hook | Stage | Rule |
|---|---|---|
| `SessionStart` | Re-inject | Build + prepend the recall block before the agent acts |
| `PostToolUse` | Capture | **Fire-and-forget** to a background worker — never compress inline |
| `Stop` / `SessionEnd` | Finalize | Flush pending captures; fold the session into a summary record |

The one trap: **never compress inside the `PostToolUse` hook.** Summarizing inline stalls the agent on *every* tool call. Capture writes the raw fact and returns immediately; a background worker compresses.

Two gates ride the `Stop`/`SessionEnd` finalize step. **Trivial-session skip:** a session with fewer than ~3 substantive user prompts or under ~50 bytes of user text saves *nothing* — a "hi, never mind" session written to memory is pure noise. **Consolidation:** once a topic has accumulated real signal — at least ~4 hours *and* ~3 sessions since the last pass — run consolidation at session end: dedup-merge the raw session logs into curated topic pages, so repeated fragments become one page and the raw logs are free to decay. The gates matter as much as the merge: consolidating every session churns pages; never consolidating leaves the store a pile of logs.

> The wiring is illustrative. The **pattern** is what ships. Do not stand up a daemon, a worker queue, or a vector DB before the corpus demands one (`fabius-parcus`: *does it need to exist yet?*). A flat `MEMORY.md` + `log.md` re-read on start covers a small project.

### The never-drop floor

Compression is not housekeeping — it is a **write path that silently mutates state**. The failure is specific: six tool-calls after a summary trims *the one constraint that made the earlier decision safe*, the agent acts on the gap and nothing throws. So memory carries the same *never-trim floor* `fabius-parcus` holds for code — a class of records that compression may reorder or shorten but **never drop**:

- a safety / permission **constraint** ("prod only after the migration", "never touch the private key"),
- a **decision** and the reason for it (so it isn't silently re-opened next session),
- an **agreement** with the human (a preference, a scope line, a "don't do X").

Mark these `[pin]` at capture; a compress step that would drop a pinned record fails loud instead of quietly forgetting. And fire **capture *before* the compaction, not after** — a pre-compaction *lifeboat* (current goal · open threads · next action, ≤5 lines written to the top of the working record) is the cheapest insurance against waking up amnesiac. Don't wait for the compaction event to fire it: flush an **LLM summary** of the session so far when context headroom falls to **~4k tokens** — by the time the harness compacts, the lifeboat is already written. Two guards keep the flush from polluting the store: **semantic dedup** (skip any record whose embedding sits within ~**0.92 cosine** of an existing one — near-duplicates rot retrieval) and a **write cap** per flush (a handful of records, never a dump — a runaway session must not flood the archive). Recovery after compaction is symmetric: **re-inject the recall block on the first post-compaction turn** and **re-search memory** for the current task, because compaction just deleted the context the earlier injection lived in. Everything else is free to decay on its TTL — the capture-side mechanism of the single decay story whose retrieval-side scoring, and the principle behind it, live in [`retrieval-stack.md`](retrieval-stack.md): *record only what is non-inferable and will be reused*, and re-read the **index, not the transcript**.

**Where compaction is a dial, stop racing it.** On the Messages API the summarization is yours to configure, not an ambush to outrun: server-side compaction (`compact_20260112`, beta header `compact-2026-01-12`) fires at a trigger *you* set — 150,000 input tokens by default, 50,000 minimum — emits a `compaction` block and drops everything before it, with `pause_after_compaction` to let you step in and `instructions` to replace the default summarization prompt outright. **Put the never-drop floor into `instructions`**, so pinned constraints, decisions and agreements are carried into the summary by contract rather than by luck. Context editing is the lighter sibling — `clear_tool_uses_20250919` and `clear_thinking_20251015` (beta header `context-management-2025-06-27`) drop stale tool results and thinking blocks on the server while your client keeps the full unmodified history, so that content is unsent, not lost. Neither is a memory: compaction keeps the window small, the store is what survives the summary. Keep the lifeboat for the harnesses where compaction still arrives as an event you don't control — and there, know exactly what the harness re-injects afterwards: Claude Code re-reads the project-root `CLAUDE.md` after `/compact` but does **not** re-inject nested `CLAUDE.md` files or `paths:`-scoped rules, so a constraint that lives only in a subdirectory is gone until something touches that subdirectory again.

### When memory must be a tool, use the standard one

Hooks capture around the turn; a *tool* lets the model read and write memory inside it. Don't invent that tool — the Messages API ships one, and it is generally available: `{"type": "memory_20250818", "name": "memory"}` is the entire configuration, no beta header, every Claude 4-and-later model. The model gets six file verbs — `view · create · str_replace · insert · delete · rename` — over a `/memories` prefix, and the API injects the check-memory-before-anything-else protocol into the system prompt, so the read-on-start habit is enforced for you rather than prompted for.

`/memories` is a **prefix, not a directory**: your handler maps it onto storage you own — a per-user directory, rows in a database, an object store — which is precisely the provider-agnostic contract archivum insists on, minus the bespoke plumbing. Two obligations come with taking it:

- **Your handler is the security boundary.** Every path is model-controlled input. Canonicalize it and assert it resolves *inside* the memory root; reject `../`, `..\`, and percent-encoded traversal (`%2e%2e%2f`). A handler that trusts the path is an arbitrary-file-read wearing a memory hat. Cap file size, and cap what `view` returns — page the rest with a range instead of streaming a whole file into context.
- **A durable store replays whatever it is given.** A credential written to memory once is re-read into every later session that mounts it. Secrets never enter the archive (`fabius-praesidium`); if one already did, delete the record rather than editing around it.

### Retrieval discipline — progressive disclosure

Working memory and archive are **separate stores**:

- **Working memory** = the compressed records injected into context. Small, typed, titled.
- **Archive** = full raw outputs on disk, pulled only on demand.

Inject the small index of titles/ids by default (tens of tokens); fetch a record's full body only when a hit warrants it. Same reason a SKILL.md stays lean and its `references/` page in on demand — `fabius-parcus`'s progressive-disclosure rule, applied to memory.

A **3-tool retrieval surface**, ordered to enforce *filter-before-fetch*:

1. `search` — by type / date / project → returns a compact index of ids + titles
2. `timeline` — chronological context around a hit (what happened just before/after)
3. `get` — full record body by id

Never expose a "fetch everything" verb. The ordering *is* the discipline.

**Hybrid index:** lexical / full-text **first**. Add vectors only when recall turns semantic ("things like X") — the existing when-to-add-vector rule from [the skill](../SKILL.md#when-to-add-vector-retrieval). Narrow symbolically (id, type, date), dense-rerank only the narrowed slice.

> Numbers like ~8ms POST, ~10× token savings, ~500-token observations are **reported by claude-mem**, not fabius measurements. Treat as the upstream project's own claims, not as facts about your corpus.

---

## PART B — external source-grounded corpus connector

**Ground, don't guess.** When an answer must be source-true (a domain spec, a contract, a curated body), route the question to an authoritative external KB that answers **only from its sources** and signals uncertainty — instead of pattern-matching from weights.

Stay **provider-agnostic.** The connector pattern outlives any one product. Do **not** ship a vendor scraper; provider-specific DOM/auth recipes rot.

### Source-registry schema

Store each corpus as metadata, select by topic at query time — the connector remembers *which* corpus answers *which* question:

```json
{ "name": "<corpus id>", "url": "<endpoint or name>",
  "description": "<what it authoritatively covers>",
  "topics": ["...", "..."] }
```

**Registering an unknown corpus:** ask it to summarize **itself** first, then use that summary as its `description` + `topics`. Never tag a corpus generically ("docs", "stuff") — generic metadata defeats topic selection.

### Forced-follow-up grounding loop

A single lookup is rarely the whole answer. After each retrieved answer:

```
ask corpus → DIFF answer against ORIGINAL request
           → identify gaps → re-query the gaps
           → repeat until nothing is missing
           → THEN synthesize
```

This converts one lookup into iterative, complete retrieval. The diff-against-original step is the discipline — without it you synthesize from a partial answer.

**Session shape:** keep per-question sessions **disposable** — stateless, full context handed in each time. But **persist the source registry** across sessions; it is the only durable state and the part that compounds.

### When to reach for an external corpus

| Approach | Token cost | Setup | Hallucination risk | Source-truth quality |
|---|---|---|---|---|
| **Read local files** | low | none | low (you control it) | high — if local copy is current |
| **External corpus (this)** | medium | register once | **lowest** — answers only from sources | highest — authoritative, curated |
| **Web search** | medium | none | high — open web, unranked | variable |
| **Local RAG** | medium | build index | medium — depends on chunking | high if corpus is yours |

Reach for an **external corpus** when truth must be authoritative and you don't own/host the source. Reach **local files** when you control the source and it's small. Reach **local RAG** when the corpus is yours and large (see [CORPUS.md](../../../CORPUS.md) and the skill's vector rule). Web search is the fallback when none of the above holds.

### Security

- Keep credentials, cookies, and the registry **out of the repo** — gitignored, never committed.
- Honor each provider's ToS and rate limits.
- Treat any provider-specific auth/DOM recipe as illustrative — it will rot; the registry + loop pattern will not.

---

See [`../SKILL.md`](../SKILL.md) for the contract this depth sits behind, and [CORPUS.md](../../../CORPUS.md) for the corpus-level retrieval policy.

Adapted from thedotmack/claude-mem (Apache-2.0) and PleasePrompto/notebooklm-skill (MIT) — re-expressed in fabius's own voice.
