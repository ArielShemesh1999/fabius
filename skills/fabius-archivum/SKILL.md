---
name: fabius-archivum
description: >
  fabius's persistent-memory layer — lets the agent stop re-deriving: write what it learns into an
  interlinked markdown knowledge base, retrieve from it cheaply, and keep it healthy (index + log +
  when-to-add-vector). Use when work spans sessions, when a fact or decision is worth keeping, when
  the user says "remember this", when a knowledge base is growing, to set up a per-project memory or
  an Obsidian vault so the next session starts ahead, or whenever the agent is about
  to redo research it (or a past session) already did. Directory schema and page conventions live in
  references/memory-schema.md; the knowledge engine itself — a vector engine, the wiki pattern, and a
  RAG pipeline — lives in references/knowledge/. Cross-session auto-recall (capture → compress →
  re-inject without being asked) and source-grounded external-corpus connectors live in
  references/external-recall.md.
when_to_use: >
  "what did we decide last time", "save this for later", "set up project memory", "index the
  vault", or before redoing research a past session covered.
license: UNLICENSED
metadata:
  author: shear559
---
<!-- © 2026 shear559 · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->

# Fabius Archivum — don't re-derive what you already learned

*Archivum* — the record office, where what's settled is kept. An agent that re-researches every session pays full price each time. This layer makes knowledge compound: write it down, link it, retrieve it, keep it true.

## Three layers

- **Raw sources** — the immutable source-of-truth documents. Read them, never edit them.
- **The wiki** — an agent-owned directory of markdown pages (entities, concepts, comparisons, syntheses). This is the externalized long-term memory — the part that compounds.
- **The schema** — a concrete config encoding the directory structure, the conventions, and the workflows. It turns a chat assistant into a disciplined archivist.

Two navigation files keep hundreds of pages tractable:

- **Index** — a catalog: every page with its link, a one-line summary, and metadata. Read this FIRST at query time, before opening any page.
- **Log** — append-only, consistently prefixed, chronological. Greppable and tailable with plain unix tools.

## The three operations

**Write boundary.** Archivum never turns a read-only task into a mutation. Ingest, capture, file-back, scaffold, and lint writes run only when the workspace has opted into Archivum memory **and** its contract authorizes those writes. Otherwise return a proposed record or diff without touching the store.

**Ingest (WRITE).** A new source arrives → read it under `fabius-disciplina` → write a summary page → update the index and touched cross-references → append one log line. Mutate surgically; prove claims.

**Query (READ).** Narrow through the index and symbolic filters → read the matching slice → synthesize a **cited** answer. File it back only under the write boundary above.

**Lint (MAINTAIN).** Periodically self-heal: contradictions, stale claims, orphan pages, missing cross-references, data gaps. Post-mortems and architecture write-ups become new pages.

## Page hygiene

- One page = one entity, concept, or decision. Link liberally with `[[other-page]]` — a link to a not-yet-written page is a valid forward marker, not an error.
- Frontmatter for retrievability: a stable id/name, a one-line description (this is what the index shows), a type, and **absolute** dates (`2026-06-21`, never "last week").
- Don't duplicate — update or supersede the existing page. Preserve decision history: tombstone/archive a wrong record and link its replacement; delete only an unambiguous current-run duplicate when the authorized scope and recovery path make that safe. Don't transcribe the source verbatim; record what was non-obvious.

## When to add vector retrieval

Index + grep handles a few hundred pages fine — that's the lazy default (`fabius-parcus`: *does the vector store need to exist yet?*). Reach for a dense vector index (quantized embeddings, online ingest, in-kernel filtered search) only when:

- the corpus outgrows what symbolic search and an index scan can handle, or
- queries turn semantic ("things like X") rather than keyword.

Then the pattern is **hybrid**: narrow symbolically by id or metadata first (project, date, layer), and dense-rerank only that narrowed slice. Online ingest — no retrain on each add — is what a forever-growing base needs.

## The loop that compounds

```
ingest (write) → index (catalog/embed) → query (read, cite, file back) → lint (maintain) → ↺
```

Inside the write boundary, the agent handles summarizing, cross-referencing, filing, and consistency checks. Schema and line formats → `references/memory-schema.md`. When the corpus outgrows grep, `references/knowledge/` is **design, not dependency**: renamed packages/imports leave its pins unresolved. Take the shape; wire a tested store from `references/retrieval-stack.md`. Meeting capture → `references/meeting-capture.md`.

## Cross-session memory — authorized, per project

The next session should start where the last one ended, but only inside a project that opted into a **per-project memory**.

- **Read on start when recall is enabled.** Read the existing index (`MEMORY.md` / `index.md`) before acting, subject to the fresh-eyes gate below. No memory yet → offer setup once; never create it implicitly.
- **Write on milestone when authorized.** In an opted-in store whose contract authorizes ongoing memory writes, update current state and append one `log.md` line after a durable decision/fix. Preserve prior decisions and reasons; supersede them, never rewrite history.
- **One layout, scaled to size.** Small project: a flat `MEMORY.md` index + `log.md` + a handful of topic pages. Large one: the full `wiki/` (entities / concepts / syntheses). Same conventions either way — schema in `references/memory-schema.md`.

What goes in: the things the *code doesn't say* — decisions and their why, rejected approaches, gotchas, live URLs, current goals, open threads. Not a transcript; the non-obvious and retrievable. One page = one thing, linked with `[[slug]]`.

### Obsidian onboarding (offer once)

The wiki is plain markdown — works in any editor, best browsed in Obsidian (backlinks, graph, Dataview). On a project with no memory yet, offer the choice once:

1. **Obsidian** (richer) — install from obsidian.md → *Open folder as vault* on `wiki/` → enable Graph + Dataview. After opt-in, fabius writes; they browse links live.
2. **Plain md** (zero install) — just the `wiki/` dir of markdown. Same retrieval (`index.md` + grep), no app.

Either way the human curates sources and asks; fabius maintains only after opt-in. Never block work for setup or scaffold without authorization.

## Auto-recall — surface memory without being asked

Auto-recall is a dial, not a universal prepend. **Off** for trivial work; **off or dampened** for security, incident, debugging, and error-recovery fresh-eyes routes; index-only for ordinary continuation; deeper only when the task truly matches. On fresh-eyes routes, inspect current evidence first and compare memory afterward. Every retrieved record is a suspect candidate: verify that its situation matches and its outcome was proven before using it; prefer the newest verified value when records conflict.

When recall is enabled, keep its three stages separate:

- **Capture** — in an authorized opted-in store, record a durable decision/fix/result without blocking the work.
- **Compress** — turn the raw capture into a small, *typed and titled* record (a title + a type + a compact body), not a transcript dump. Typed-and-titled is what makes later filtering and progressive disclosure cheap.
- **Re-inject** — when the recall dial permits, surface a compact index of matching recent records; do not dump it blindly into every task.

Retrieve under **progressive disclosure**: when recall is on, inject titles/ids first and pull a full record only on demand. Check the harness before wiring anything; adopt its native per-repo index/topic pattern instead of a parallel store. Hand-wire only where the harness ships nothing (`references/external-recall.md`).

## Ground in an external corpus — ask, don't guess

When an answer must be **source-true** (a domain spec, a contract, a curated body of documents), route the question to an authoritative external knowledge base that answers **only** from its sources and signals uncertainty — instead of pattern-matching from the model's weights. Two rules make this reliable:

- **Keep a source registry.** Store each external corpus as `{ name, description, topics }` and select by topic at query time — the connector remembers *which* corpus answers *which* question. To register an unknown corpus, ask it to summarize *itself* first, then use that as its metadata; never tag it generically.
- **Loop until complete, then synthesize.** After each retrieved answer, diff it against the *original* request, identify the gaps, and re-query — only synthesize once nothing is missing. A single lookup is rarely the whole answer.

Stay provider-agnostic (the connector pattern outlives any one product) and keep credentials and the registry **out of the repo**. Connector recipe + the when-to-reach-external decision table → `references/external-recall.md`.

## Memory discipline — page, don't stuff

The memory rules from the routing policy (MemGPT, Voyager, the memory surveys; full set in [routing-policy.md](../fabius/references/routing-policy.md)):

- **Retrieve on demand (R9).** Read the index, then the matched page fully when exact evidence requires it; never load an unrelated whole page or directory "just in case." If the matched set exceeds budget, summarize-then-link. *(MemGPT)*
- **Write only decision-changing facts (M7).** Authorized `write = EVICT` (durable fact → page + log); `read = RECALL` (index→page on a miss, logged as QUERY). Everything addressable by `[[slug]]`.
- **Promote verified solutions to skills (M6).** When skill writes are authorized, file a solved-and-verified sub-problem as a named reusable page; supersede, don't duplicate, and retain failed approaches as anti-pattern history. *(Voyager)*
- **Tie-break by recency + load-bearingness (M8).** When index entries tie on relevance, surface the freshest decision-bearing pages first; fold a grown batch of log lines up into a synthesis page. *(Generative Agents, analogy)*

**Live tier (optional).** The markdown index + log + grep needs nothing; auto-recall rides the harness's own memory where it has one and lifecycle hooks where it doesn't; where memory must be a *tool*, the Messages API ships a GA one (`memory_20250818`) whose handler you own — and must path-validate. An external-corpus connector is provider-agnostic (NotebookLM / `notebooklm-mcp` / a vector store) — you configure it. fabius bundles the *pattern*, not the service — the full map is in [ARCHITECTURE.md](../../ARCHITECTURE.md) (*External connections*).

Pairs with: `fabius-disciplina` (resolved facts and post-mortems get filed here), `fabius-cohors` (grounding and cross-session memory for agents), `fabius-parcus` (don't build the heavy retrieval engine before the corpus demands it).
