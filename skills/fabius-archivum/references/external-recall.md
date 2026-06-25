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

### Wiring to Claude Code lifecycle hooks

| Hook | Stage | Rule |
|---|---|---|
| `SessionStart` | Re-inject | Build + prepend the recall block before the agent acts |
| `PostToolUse` | Capture | **Fire-and-forget** to a background worker — never compress inline |
| `Stop` / `SessionEnd` | Finalize | Flush pending captures; fold the session into a summary record |

The one trap: **never compress inside the `PostToolUse` hook.** Summarizing inline stalls the agent on *every* tool call. Capture writes the raw fact and returns immediately; a background worker compresses.

> The wiring is illustrative. The **pattern** is what ships. Do not stand up a daemon, a worker queue, or a vector DB before the corpus demands one (`fabius-parcus`: *does it need to exist yet?*). A flat `MEMORY.md` + `log.md` re-read on start covers a small project.

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
