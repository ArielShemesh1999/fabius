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
  working RAG pipeline — lives in references/knowledge/. Cross-session auto-recall (capture → compress →
  re-inject without being asked) and source-grounded external-corpus connectors live in
  references/external-recall.md.
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

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

## Cross-session memory — autonomous, per project

The point of a record office: the next session starts where the last one ended. Keep a **per-project memory** and tend it without being asked.

- **Read on start.** Beginning work on a project, read its memory index (`MEMORY.md` / `index.md`) *before* acting — the cheapest way to not re-derive last session's decisions. No memory yet → that's the signal to set one up.
- **Write on milestone.** After a decision, a fix, an architecture choice, a "why we did it this way", or at session end — update the page it touches and append one `log.md` line. Surgical (`fabius-parcus`), proven (`fabius-disciplina`). You don't wait to be told; the bookkeeping is your job.
- **One layout, scaled to size.** Small project: a flat `MEMORY.md` index + `log.md` + a handful of topic pages. Large one: the full `wiki/` (entities / concepts / syntheses). Same conventions either way — schema in `references/memory-schema.md`.

What goes in: the things the *code doesn't say* — decisions and their why, rejected approaches, gotchas, live URLs, current goals, open threads. Not a transcript; the non-obvious and retrievable. One page = one thing, linked with `[[slug]]`.

### Obsidian onboarding (offer once)

The wiki is plain markdown — works in any editor, best browsed in Obsidian (backlinks, graph, Dataview). On a project with no memory yet, offer the choice once:

1. **Obsidian** (richer) — guide them: install from obsidian.md → *Open folder as vault* on the project's `wiki/` dir → enable Graph + Dataview. fabius writes the pages; they browse and follow links live. *(Obsidian is the IDE, the LLM is the programmer, the wiki is the codebase.)*
2. **Plain md** (zero install) — just the `wiki/` dir of markdown. Same retrieval (`index.md` + grep), no app.

Either way the human curates sources and asks; fabius writes and maintains. Never block work to set this up — scaffold the minimal `MEMORY.md` + `log.md` and keep going.

## Auto-recall — surface memory without being asked

Reading the index on start (above) is recall you *choose*. The stronger habit is recall that fires **automatically**, so the agent never re-derives what a past session already settled. The loop has three named stages — keep them separate:

- **Capture** — record what happened (a decision, a fix, a result) as it happens. Capture must be **non-blocking**: never stop the work to summarize; jot the raw fact and move on.
- **Compress** — turn the raw capture into a small, *typed and titled* record (a title + a type + a compact body), not a transcript dump. Typed-and-titled is what makes later filtering and progressive disclosure cheap.
- **Re-inject** — at the **start** of the next session, surface a compact index of the recent records (titles grouped by type, last-N sessions) into context *before* acting. That single step is what turns memory from opt-in to automatic.

Retrieve under **progressive disclosure**: inject the small index (titles/ids) by default; pull a record's full body only on demand. This is `fabius-parcus`'s progressive-disclosure rule applied to memory — the same reason a SKILL.md is lean and its `references/` page in on demand. (In Claude Code this maps onto lifecycle hooks — capture on tool-use, re-inject on session-start — but the *pattern* is what matters; don't build a daemon before the corpus demands one. Wiring in `references/external-recall.md`.)

## Ground in an external corpus — ask, don't guess

When an answer must be **source-true** (a domain spec, a contract, a curated body of documents), route the question to an authoritative external knowledge base that answers **only** from its sources and signals uncertainty — instead of pattern-matching from the model's weights. Two rules make this reliable:

- **Keep a source registry.** Store each external corpus as `{ name, description, topics }` and select by topic at query time — the connector remembers *which* corpus answers *which* question. To register an unknown corpus, ask it to summarize *itself* first, then use that as its metadata; never tag it generically.
- **Loop until complete, then synthesize.** After each retrieved answer, diff it against the *original* request, identify the gaps, and re-query — only synthesize once nothing is missing. A single lookup is rarely the whole answer.

Stay provider-agnostic (the connector pattern outlives any one product) and keep credentials and the registry **out of the repo**. Connector recipe and the decision table for *when to reach for an external corpus vs read local files* → `references/external-recall.md`.

## Memory discipline — page, don't stuff

The memory rules from the routing policy (MemGPT, Voyager, the memory surveys; full set in [routing-policy.md](../fabius/references/routing-policy.md)):

- **Retrieve on demand (R9).** Read the index, page in only the matching slice; if it still exceeds the budget, summarize-then-link — never cat a whole page or directory "just in case." *(MemGPT)*
- **Write only decision-changing facts (M7).** `write = EVICT` (flush durable facts to a page + log line under window pressure / at session end); `read = RECALL` (index→page on a miss, logged as QUERY). Everything addressable by `[[slug]]`.
- **Promote verified solutions to skills (M6).** After a self-contained sub-problem is solved *and verified*, file it as a named reusable skill page; query archivum and compose existing skills before planning from scratch; supersede, don't duplicate. Failures leave an anti-pattern note. *(Voyager)*
- **Tie-break by recency + load-bearingness (M8).** When index entries tie on relevance, surface the freshest decision-bearing pages first; fold a grown batch of log lines up into a synthesis page. *(Generative Agents, analogy)*

Pairs with: `fabius-disciplina` (resolved facts and post-mortems get filed here), `fabius-cohors` (grounding and cross-session memory for agents), `fabius-parcus` (don't build the heavy retrieval engine before the corpus demands it).
