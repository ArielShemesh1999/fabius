<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# Fabius Corpus — the indexed body

One fabius-branded index over **every** capability library in the fifteen-skill system. The brain (the `fabius` router) holds this index, never the bulk: on a task it queries the index → pages in the one matching slice → strikes narrow (routing-policy **M9 · R9 · M7**). Every library is fabius-named and reached through the same `fabius-vec` retrieval. The research fabius drew on and the inspiration behind each library are recorded in [credits/](credits/README.md).

---

## The libraries — all under one fabius index

| Library | Owner skill | Holds | Index (read first) | Status |
|---|---|---|---|---|
| **fabius-agents** | `fabius-cohors` | 200+ production agent shapes across 17 domains + language packs | `references/agent-catalog.md` | shipping |
| **fabius-design** | `fabius-decor` | 69-brand design teardowns + animation / UI bundles · the icon-system map (**Iconarium**), motion-library map (**Motus**), design-materials library (**Materia** — illustration/3D/texture/font/color/HuggingFace) + RTL/BiDi discipline (**Bidi**) | `references/design-system.md` | shipping |
| **fabius-knowledge** | `fabius-archivum` | vector engine · the LLM-wiki pattern · the RAG pipeline | `references/memory-schema.md` | shipping |
| **fabius-figura** | `fabius-decor` | chart recipes · the SVG component kit · brand-matched palettes | `references/visualization.md` | entry + `assets/charts/` |
| **fabius-disciplina** | `fabius-disciplina` | the craft + discipline process library — brainstorming · TDD · systematic debugging · writing-plans · verification | `references/process-playbook.md` · `references/process/` | shipping (bundled) |
| **fabius-mercatus** | `fabius-mercatus` | channel playbooks · swipe files · launch frames | `references/marketing-playbook.md` | shipping (bundled) |
| **fabius-praesidium** | `fabius-praesidium` | hardening guides · audit checklists (defensive only) | `references/security-playbook.md` | shipping (bundled) |
| **fabius-ludus** | `fabius-ludus` | engine recipes · juice patterns · the pixel-art kit | `references/game-playbook.md` | shipping (bundled) |
| **fabius-catena** | `fabius-catena` | on-chain dev (EVM + Solana) · the provenance-sealing primitive | `references/onchain-playbook.md` · `references/sealing.md` | shipping (bundled) |
| **fabius-machina** | `fabius-machina` | the automation build-and-verify discipline · the silent-failure catalog | `references/automation-playbook.md` | shipping (bundled) |
| **fabius-scientia** | `fabius-scientia` | the scientific-method loop · the unified database-lookup contract · reproducibility | `references/science-playbook.md` | shipping (bundled) |
| **fabius-doctrina** | `fabius-doctrina` | the model lifecycle — serving (vLLM-class) · MLOps/experiment-tracking · model/LLM evaluation | `references/ml-engineering-playbook.md` | shipping (bundled) |
| **fabius-fortuna** | `fabius-fortuna` | market & economic analysis · valuation · honest backtesting · risk + position sizing | `references/markets-and-quant-playbook.md` | shipping (bundled) |
| **fabius-concilium** | `fabius-concilium` | the cross-model council protocol (3 stages · stage prompts · anonymization · Borda) + a zero-dependency runnable reference | `references/council-protocol.md` · `references/council.mjs` | shipping (bundled) |

**Honest current state.** Thirteen libraries ship full content today (`fabius-agents`, `fabius-design`, `fabius-knowledge`, `fabius-disciplina`, `fabius-mercatus`, `fabius-praesidium`, `fabius-ludus`, `fabius-catena`, `fabius-machina`, `fabius-scientia`, `fabius-doctrina`, `fabius-fortuna`, `fabius-concilium`) — and today they ship **bundled** under each owner skill's `references/`, reached through the index. `fabius-mercatus` bundles its playbook plus the channel-and-swipe library (`references/marketing-playbook.md` + `references/channel-swipe-library.md`); `fabius-praesidium` its playbook plus the hardening & audit library and the security tool arsenal (`references/security-playbook.md` + `references/hardening-guides.md` + `references/security-toolkit.md`); `fabius-ludus` its playbook plus the engine & feel library (`references/game-playbook.md` + `references/engine-recipes.md`). `fabius-figura` ships a reference doc plus the `assets/charts/` SVG path. All are addressed identically — one index, one retrieval contract, one fabius brand — so a library can move from bundled to externalized without changing how a skill reaches it.

**Resource toolkits (per skill).** Beyond the playbooks, each capability skill ships a verified **external-resource library** under its `references/` — best-in-class tools **plus** noise-filtered HuggingFace models/datasets, every entry license-checked (permissive vs non-commercial / copyleft / fair-code flagged honestly): `fabius-archivum` retrieval-stack, `fabius-cohors` agent-frameworks, `fabius-doctrina` ml-toolkit, `fabius-fortuna` markets-toolkit, `fabius-scientia` science-toolkit, `fabius-catena` onchain-toolkit, `fabius-machina` automation-toolkit, `fabius-mercatus` marketing-toolkit, `fabius-ludus` game-toolkit, `fabius-disciplina` testing-toolkit, `fabius-praesidium` security-toolkit; and `fabius-decor` adds the Iconarium / Motus / Materia icon-motion-material layers, the Bidi RTL discipline, and the **Yisrael** Israeli-localization layer.

## Retrieval contract — how the brain reaches the corpus

1. **Classify** the task (routing-policy R1) → the owning skill → its library above.
2. **Read the index first** (R9 · M7) — one-line summaries and metadata, never the bulk.
3. **Page in only the matching slice**; if it still exceeds the budget, **summarize-then-link**, don't inline.
4. The **`fabius-vec`** index plus archivum's `rag/` hooks (`query.py` · `indexer.py` · `hook_retrieve.py`) run the dense lookup when symbolic narrowing isn't enough — and only once corpus size or semantic queries demand a vector store (`fabius-archivum`: *when to add vector retrieval*; `fabius-parcus`: *does it need to exist yet?*).

## Externalization (M9) — the packaging direction

The standing rule (routing-policy **M9**): the brain should hold the **index**, not the library. As a library grows past a lean entry doc, its bulk moves **out** of the installed plugin into the indexed `fabius-corpus`, reached through the same index — so the install stays a lean brain and **adding a capability is adding a row to this index, not a megabyte.** Today the thirteen full libraries are bundled under `references/`; the index is built so they can externalize without any skill changing how it reaches them. The research and inspiration behind every library are kept honestly in [credits/](credits/README.md) — fabius's own record of what it studied.

> One brain, one index, one corpus — every strength reachable as a fabius library, the install kept lean as the library scales.
