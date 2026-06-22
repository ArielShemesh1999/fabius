---
name: fabius-archivum
description: >
  fabius's persistent-memory layer — lets the agent stop re-deriving: write what it learns into an
  interlinked markdown knowledge base, retrieve from it cheaply, and keep it healthy (index + log +
  when-to-add-vector). Use when work spans sessions, when a fact or decision is worth keeping, when
  the user says "remember this", when a knowledge base is growing, or whenever the agent is about
  to redo research it (or a past session) already did. Directory schema and page conventions live in
  references/memory-schema.md; the knowledge engine itself — a vector engine, the wiki pattern, and a
  working RAG pipeline — lives in references/knowledge/.
---

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

**Ingest (WRITE).** A new source arrives → read it under `fabius-disciplina` discipline → write a summary page → update the index → revise the handful of cross-referenced pages it touches → append one line to the log. Keep the mutations surgical (`fabius-parcus`); keep the claims proven (`fabius-disciplina`). One source richer.

**Query (READ).** A question arrives → narrow through the index and symbolic filters to the right slice (project, layer, date range) → read only that slice → synthesize a **cited** answer → file the good answer back as a new page. Each query starts from more knowledge than the last.

**Lint (MAINTAIN).** Periodically self-heal: contradictions, stale claims, orphan pages, missing cross-references, data gaps. Post-mortems and architecture write-ups become new pages.

## Page hygiene

- One page = one entity, concept, or decision. Link liberally with `[[other-page]]` — a link to a not-yet-written page is a valid forward marker, not an error.
- Frontmatter for retrievability: a stable id/name, a one-line description (this is what the index shows), a type, and **absolute** dates (`2026-06-21`, never "last week").
- Don't duplicate — update the existing page. A wrong page → delete it. Don't transcribe what the source already records verbatim; record what was non-obvious.

## When to add vector retrieval

Index + grep handles a few hundred pages fine — that's the lazy default (`fabius-parcus`: *does the vector store need to exist yet?*). Reach for a dense vector index (quantized embeddings, online ingest, in-kernel filtered search) only when:

- the corpus outgrows what symbolic search and an index scan can handle, or
- queries turn semantic ("things like X") rather than keyword.

Then the pattern is **hybrid**: narrow symbolically by id or metadata first (project, date, layer), and dense-rerank only that narrowed slice. Online ingest — no retrain on each add — is what a forever-growing base needs.

## The loop that compounds

```
ingest (write) → index (catalog/embed) → query (read, cite, file back) → lint (maintain) → ↺
```

The agent does all the bookkeeping — summarize, cross-reference, file, consistency-check. The human only curates sources and asks questions. Concrete directory schema, page frontmatter, and the index/log line formats live in `references/memory-schema.md`. When the corpus outgrows grep, the working engine — vector store, the wiki-pattern layout, and a runnable RAG indexer/query pipeline — is in `references/knowledge/`.

Pairs with: `fabius-disciplina` (resolved facts and post-mortems get filed here), `fabius-cohors` (grounding and cross-session memory for agents), `fabius-parcus` (don't build the heavy retrieval engine before the corpus demands it).
