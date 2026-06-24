# Fabius Corpus — the indexed body

One fabius-branded index over **every** capability library. The brain (the `fabius` router) holds this index, never the bulk: on a task it queries the index → pages in the one matching slice → strikes narrow (routing-policy **M9 · R9 · M7**). Every library is fabius-named and reached through the same `fabius-vec` retrieval. The research fabius drew on and the inspiration behind each library are recorded in [credits/](credits/README.md).

---

## The libraries — all under one fabius index

| Library | Owner skill | Holds | Index (read first) | Status |
|---|---|---|---|---|
| **fabius-agents** | `fabius-cohors` | 200+ production agent shapes across 15 domains + language packs | `references/agent-catalog.md` | shipping |
| **fabius-design** | `fabius-decor` | 69-brand design teardowns + animation / UI bundles | `references/design-system.md` | shipping |
| **fabius-knowledge** | `fabius-archivum` | vector engine · the LLM-wiki pattern · the RAG pipeline | `references/memory-schema.md` | shipping |
| **fabius-figura** | `fabius-decor` | chart recipes · the SVG component kit · brand-matched palettes | `references/visualization.md` | entry + `assets/charts/` |
| **fabius-mercatus** | `fabius-mercatus` | channel playbooks · swipe files · launch frames | `references/marketing-playbook.md` | entry (slot) |
| **fabius-praesidium** | `fabius-praesidium` | hardening guides · audit checklists (defensive only) | `references/security-playbook.md` | entry (slot) |
| **fabius-ludus** | `fabius-ludus` | engine recipes · juice patterns · the pixel-art kit | `references/game-playbook.md` | entry (slot) |

**Honest current state.** Three libraries ship full content today (`fabius-agents`, `fabius-design`, `fabius-knowledge`) — and today they ship **bundled** under each owner skill's `references/`, reached through the index. `fabius-figura` ships a reference doc plus the `assets/charts/` SVG path. `fabius-mercatus`, `fabius-praesidium`, and `fabius-ludus` ship a lean entry doc and are populated as the corpus fills. All are addressed identically — one index, one retrieval contract, one fabius brand — so a library can move from bundled to externalized without changing how a skill reaches it.

## Retrieval contract — how the brain reaches the corpus

1. **Classify** the task (routing-policy R1) → the owning skill → its library above.
2. **Read the index first** (R9 · M7) — one-line summaries and metadata, never the bulk.
3. **Page in only the matching slice**; if it still exceeds the budget, **summarize-then-link**, don't inline.
4. The **`fabius-vec`** index plus archivum's `rag/` hooks (`query.py` · `indexer.py` · `hook_retrieve.py`) run the dense lookup when symbolic narrowing isn't enough — and only once corpus size or semantic queries demand a vector store (`fabius-archivum`: *when to add vector retrieval*; `fabius-parcus`: *does it need to exist yet?*).

## Externalization (M9) — the packaging direction

The standing rule (routing-policy **M9**): the brain should hold the **index**, not the library. As a library grows past a lean entry doc, its bulk moves **out** of the installed plugin into the indexed `fabius-corpus`, reached through the same index — so the install stays a lean brain and **adding a capability is adding a row to this index, not a megabyte.** Today the three full libraries are bundled under `references/`; the index is built so they can externalize without any skill changing how it reaches them. The research and inspiration behind every library are kept honestly in [credits/](credits/README.md) — fabius's own record of what it studied.

> One brain, one index, one corpus — every strength reachable as a fabius library, the install kept lean as the library scales.
