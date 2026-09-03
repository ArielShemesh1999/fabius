# Fabius Archivum — wiki schema & conventions

Loaded on demand by `fabius-archivum`. The skill has the loop; this file has the concrete directory schema, the page conventions, and the line formats for the two navigation files.

**Write authorization precedes this schema.** Create or mutate these files only when the workspace opted into Archivum memory and the current request/contract authorizes the write. A read-only query returns a proposed record/diff instead. Preserve history: append log/decision events and supersede stale records; delete only a recoverable, unambiguous duplicate created in the current run.

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
name: stable-kebab-slug          # the id AND the filename: a wikilink resolves by filename, never by this field
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
2026-06-21 LINT    archived 2 duplicate orphans; superseded 3 stale claims
```

One prefix per operation (INGEST / QUERY / LINT), one line per event. Grep the log to reconstruct what happened and when, with no tooling beyond `grep` and `tail`.

## When symbolic search isn't enough → a dense vector layer

Add a quantized vector index (2/3/4-bit embeddings, online ingest with no retrain on add, in-kernel filtered search) only once the corpus outgrows index + grep, or once queries go semantic ("things like X") instead of keyword. Then the retrieval is **hybrid**:

1. Filter symbolically first — by id or metadata (project, date, layer) — to a narrow slice.
2. Dense-rerank only that slice.

Symbolic-first keeps the dense search cheap and the results scoped; pure vector search over the whole base is slower and noisier. Drop-in adapters exist for the common frameworks (LangChain, LlamaIndex, Haystack), so the engine is a swap, not a rewrite.

## Why maintenance stays near zero

Inside an authorized, opted-in store, the agent does the bookkeeping — summarize, cross-reference, file back, and lint. Outside it, offer the record without mutation.

## Per-project opted-in memory (the cross-session contract)

For a project that opted in, memory lives *with the project* and fabius tends it within the authorized contract. This is the in-project shape only — where one store serves many projects, the topology, the read gate and the write-back contract are in [`project-records.md`](project-records.md), and no second store is created beside it:

```
<project>/
  MEMORY.md           # the index: live URLs, stack, current goal, open threads, links to pages. READ FIRST, every session.
  wiki/
    log.md            # append-only: one line per session/decision/fix
    decisions/        # why we chose X over Y (the thing the code never records)
    gotchas/          # the traps that cost an hour; how to avoid them next time
    <topic>.md        # architecture, domain, integrations — one page per thing
```

Small project → collapse `wiki/` into a flat folder beside `MEMORY.md`. Don't build the tree before the pages exist.

### `MEMORY.md` template (scaffold only after opt-in)

```markdown
# <Project> — memory

> Read this first. Update on every milestone. Plain markdown — open in Obsidian if you like.

- **Live:** <url> · **Stack:** <one line> · **Repo:** <url>
- **Goal now:** <the current objective>
- **Open threads:** <what's unfinished, with the next step>

## Index
- [Architecture](wiki/architecture.md) — how it fits together
- [Decisions](wiki/decisions/) — why, not just what
- [Gotchas](wiki/gotchas/) — traps + avoidance
- [Log](wiki/log.md) — chronological
```

### The authorized loop, applied to a project

1. **Session start** — if the index exists and the recall dial permits, read it. If absent, offer setup once; do not scaffold implicitly.
2. **On a milestone** — when ongoing memory writes are authorized, update current state and append one `log.md` line. Supersede old decisions; never erase their reason or event history.
3. **Session end** — under the same authorization, refresh `Goal now` + `Open threads` so the next session opens mid-stride.
4. **Periodic lint** — link orphans, mark contradictions, and supersede stale claims; do not silently rewrite history.

### Three session-memory hygiene rules

- **Dump before compaction.** When a large tool output — a fetched page, an API response, a research result — will be needed later, write it to a memory file *immediately*: compaction/truncation destroys unpersisted tool results mid-session. This is the store-side twin of the pre-compaction lifeboat in [`external-recall.md`](external-recall.md).
- **Bookkeeping files are marked, not hidden.** Prefix them (`_index.md`, `_meta/`) and skip that prefix in the store's read rule — nothing can hide a file from `ls`, so the convention has to be explicit.
- **Cap the auto-maintained index** at a fixed entry count (~50); regenerate it and inject it every turn, so the model always knows *what memories exist* without reading them. Past the cap, consolidate rather than append.

### Obsidian onboarding steps (offer once, never block)

The vault is just the project's memory folder — no migration, no export:

1. Install Obsidian (obsidian.md) — free, local, no account.
2. *Open folder as vault* → pick the project's `wiki/` (or the project root).
3. Enable **Graph view** (see the link structure) and the **Dataview** community plugin (query frontmatter — e.g. list every page by `updated`).
4. Done. fabius writes the markdown from the conversation; the human browses, follows `[[links]]`, reads the graph. If they'd rather not install anything, the same files work with `grep` + any editor.
