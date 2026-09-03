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
  vault", before work on a project that already has a record, "watch this video", "what does this recording show", "ask my sources", or before
  redoing research a past session covered.
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

**Ingest (WRITE).** A new source arrives → read it under `fabius-disciplina` → write a summary page → update the index and touched cross-references → append one log line. Mutate surgically; prove claims. A video is a source too — captions first, frames only as the question demands, every claim quoted at `t=MM:SS`, never "I watched" → `references/video-ingest.md`.

**Query (READ).** Narrow through the index and symbolic filters → read the matching slice → synthesize a **cited** answer. File it back only under the write boundary above.

**Lint (MAINTAIN).** Periodically self-heal: contradictions, stale claims, orphan pages, missing cross-references, data gaps. Post-mortems and architecture write-ups become new pages.

## Page hygiene

- One page = one entity, concept, or decision. Link liberally with `[[other-page]]` — a link to a not-yet-written page is a valid forward marker, not an error.
- Frontmatter for retrievability: a stable id/name, a one-line description (this is what the index shows), a type, and **absolute** dates (`2026-06-21`, never "last week"). A project page adds status, a repo/workspace pointer, a live URL — read, never guessed — and a last-push date.
- Don't duplicate — update or supersede the existing page. Preserve decision history: tombstone/archive a wrong record and link its replacement; delete only an unambiguous current-run duplicate when the authorized scope and recovery path make that safe. Don't transcribe the source verbatim; record what was non-obvious.

## When to add vector retrieval

Index + grep handles a few hundred pages — the lazy default (`fabius-parcus`: *does the vector store need to exist yet?*). Add a dense index only once the corpus outgrows symbolic search, or queries turn semantic rather than keyword. Then retrieval is **hybrid**: narrow symbolically first, dense-rerank only that slice. Detail → `references/memory-schema.md`.

## The loop that compounds

```
ingest (write) → index (catalog/embed) → query (read, cite, file back) → lint (maintain) → ↺
```

Inside the write boundary, the agent handles summarizing, cross-referencing, filing, and consistency checks. Schema and line formats → `references/memory-schema.md`. When the corpus outgrows grep, `references/knowledge/` is **design, not dependency**: renamed packages/imports leave its pins unresolved. Take the shape; wire a tested store from `references/retrieval-stack.md`. Meeting capture → `references/meeting-capture.md`.

## Cross-session memory — the project record

The next session starts where the last ended, but only inside a workspace that opted into a **record store**. The store is *declared*, not discovered from the repo: it may sit outside every repo and serve many projects, one page per project. Full contract → [`references/project-records.md`](references/project-records.md).

- **Resolve the store before testing for one.** A central hub (one page per project, shared index + log) or an in-project store — never both. Already opted in → the offer is spent: read every time, never re-ask, never scaffold a second store beside a declared one.
- **Project-page gate — a precondition, not a dial.** Work that names a project reads that project's ONE page IN FULL first: brief · stack · decisions · health · open items · live URL. Not the index row, not a grep hit. No page for a named project in a declared store → propose the page; don't start blind.
- **Cross-check the page against reality, not against itself.** An unversioned page's dates are a claim. Diff them against the tree's head and any live URL it names. Reality wins on facts, the page wins on intent; correct the page in the same session.
- **One record, one owner.** Project state lives on the canonical page only; a harness store keeps cross-project behavior, never a copy. A fact in two stores eventually disagrees with itself.
- **Sync is finishing, not follow-up.** Before reporting done, same session: dated decision lines, state fields bumped, open items rewritten to the next step, one appended log line.
- **Assume a second writer.** Append at the END, append-only; read the tail, never rewrite a shared log; sign every entry and decision line. Never re-date or edit another writer's entry.

What goes in: the things the *code doesn't say* — decisions and their why, rejected approaches, gotchas, live URLs, current goals, open threads. One page = one thing, linked with `[[slug]]`.

### Onboarding (offer once)

Plain markdown, best browsed in Obsidian (backlinks · graph · Dataview). Offer the choice once — Obsidian, or plain md with `index.md` + grep — then never re-ask. Steps, the store-root trap and the index exclusions → `references/project-records.md`. Never block work for setup; never scaffold without authorization.

## Auto-recall — surface memory without being asked

Auto-recall is a dial, not a universal prepend. **Off** for trivial work; **off or dampened** for security, incident, debugging, and error-recovery fresh-eyes routes; index-only for ordinary continuation; deeper only when the task truly matches. The dial governs prior *conclusions*, never a named project's own page — that read is a precondition, not a dial position. On fresh-eyes routes, inspect current evidence first and compare memory afterward. Every retrieved record is a suspect candidate: verify that its situation matches and its outcome was proven before using it; prefer the newest verified value when records conflict.

When recall is enabled, keep its three stages separate:

- **Capture** — in an authorized opted-in store, record a durable decision/fix/result without blocking the work.
- **Compress** — turn the raw capture into a small, *typed and titled* record (a title + a type + a compact body), not a transcript dump. Typed-and-titled is what makes later filtering and progressive disclosure cheap.
- **Re-inject** — when the recall dial permits, surface a compact index of matching recent records; do not dump it blindly into every task.

Retrieve under **progressive disclosure**: when recall is on, inject titles/ids first and pull a full record only on demand. Check the harness before wiring anything: its native memory is the trigger/pointer tier, not a second record store — records land in the declared store and the harness index keeps the pointer. Hand-wire only where the harness ships nothing (`references/external-recall.md`).

## Ground in an external corpus — ask, don't guess

When an answer must be **source-true** (a spec, a contract, a curated body of documents), route the question to an authoritative external corpus that answers **only** from its sources and signals uncertainty — never pattern-match from weights. Keep a source registry (`{ name, description, topics }`) and select by topic; to register an unknown corpus, ask it to summarize *itself* first. After each answer, diff it against the *original* request and re-query the gaps — synthesize only when nothing is missing. Stay provider-agnostic; keep credentials and the registry **out of the repo**. Connector recipe + the when-to-reach-external table → `references/external-recall.md`; the source-grounded notebook instance → `references/notebook-connector.md`.

## Memory discipline — page, don't stuff

The memory rules from the routing policy (MemGPT, Voyager, the memory surveys; full set in [routing-policy.md](../fabius/references/routing-policy.md)):

- **Retrieve on demand (R9).** Read the index, then the matched page fully when exact evidence requires it; never load an unrelated whole page or directory "just in case" — the page of the project in hand is not a candidate hit, it is the brief, and it is read whole. If the matched set exceeds budget, summarize-then-link. *(MemGPT)*
- **Write only decision-changing facts (M7).** Authorized `write = EVICT` (durable fact → page + log); `read = RECALL` (index→page on a miss, logged as QUERY). Everything addressable by `[[slug]]`.
- **Promote verified solutions to skills (M6).** When skill writes are authorized, file a solved-and-verified sub-problem as a named reusable page; supersede, don't duplicate, and retain failed approaches as anti-pattern history. *(Voyager)*
- **Tie-break by recency + load-bearingness (M8).** When index entries tie on relevance, surface the freshest decision-bearing pages first; fold a grown batch of log lines up into a synthesis page. *(Generative Agents, analogy)*

**Live tier (optional).** Index + log + grep needs nothing; auto-recall rides the harness's own memory as a trigger tier where it has one, lifecycle hooks where it doesn't. Where memory must be a *tool*, the Messages API ships a GA one (`memory_20250818`) whose handler you own — and must path-validate. fabius bundles the *pattern*, not the service — full map in [ARCHITECTURE.md](../../ARCHITECTURE.md) (*External connections*).

Pairs with: `fabius-disciplina` (resolved facts and post-mortems get filed here), `fabius-cohors` (grounding and cross-session memory for agents), `fabius-parcus` (don't build the heavy retrieval engine before the corpus demands it).
