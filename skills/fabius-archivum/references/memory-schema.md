# Fabius Archivum — wiki schema & conventions

Loaded on demand by `fabius-archivum`. The skill has the loop; this file has the concrete directory schema, the page conventions, and the line formats for the two navigation files.

## Directory schema

```
knowledge/
  index.md          # catalog: every page, its link, a 1-line summary, metadata. READ FIRST.
  log.md            # append-only, prefixed, chronological. grep/tail with unix tools.
  entities/         # one page per concrete thing (a project, a person, a system)
  concepts/         # one page per idea or pattern
  comparisons/      # X-vs-Y pages
  syntheses/        # answers worth keeping, filed back from queries
  raw/              # immutable source-of-truth docs — read, never edit
```

Scale this *down* for a small base: a flat folder of pages plus `index.md` and `log.md` is enough. Don't build the subdirectory tree before the page count demands it (`fabius-parcus`: the structure shouldn't exist until the pages do).

## Page frontmatter

```yaml
---
name: stable-kebab-slug          # the id; links use [[stable-kebab-slug]]
description: one line — this is what index.md shows for retrieval
type: entity | concept | comparison | synthesis
updated: 2026-06-21              # absolute dates only, never "last week"
---
```

Body: the fact or synthesis. Link related pages liberally with `[[slug]]` — a link to a page that doesn't exist yet is a valid forward marker, not an error.

## index.md line format

```
- [Title](entities/thing.md) — one-line hook (type, updated)
```

Read the index before reading any page. Index-based retrieval scales to hundreds of pages without loading them — the index is small, the pages are not.

## log.md line format

```
2026-06-21 INGEST  added entities/vector-index.md; revised concepts/retrieval.md
2026-06-21 QUERY   "how does X scale" → filed syntheses/x-scaling.md
2026-06-21 LINT    removed 2 orphans; fixed 3 stale claims
```

One prefix per operation (INGEST / QUERY / LINT), one line per event. Grep the log to reconstruct what happened and when, with no tooling beyond `grep` and `tail`.

## When symbolic search isn't enough → a dense vector layer

Add a quantized vector index (2/3/4-bit embeddings, online ingest with no retrain on add, in-kernel filtered search) only once the corpus outgrows index + grep, or once queries go semantic ("things like X") instead of keyword. Then the retrieval is **hybrid**:

1. Filter symbolically first — by id or metadata (project, date, layer) — to a narrow slice.
2. Dense-rerank only that slice.

Symbolic-first keeps the dense search cheap and the results scoped; pure vector search over the whole base is slower and noisier. Drop-in adapters exist for the common frameworks (LangChain, LlamaIndex, Haystack), so the engine is a swap, not a rewrite.

## Why maintenance stays near zero

The agent does the bookkeeping — summarize the source, cross-reference the touched pages, file the answer back, lint for contradictions. The human only curates which sources come in and asks the questions. That division is the whole point: the knowledge base is the agent's job, not the human's chore.
