<!-- © 2026 shear559 · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · release evidence: PROVENANCE.md · github.com/shear559/fabius -->
# Fabius Corpus — the indexed body

One fabius-branded index over the capability libraries owned by the fifteen public skills. The router holds this small map, resolves one owner, reads that owner's entry page, and pages in only the matching slice (routing-policy **M9 · R9 · M7**). Retrieval is symbolic by default (`rg`, catalog links, and exact paths); an owner may opt into a tested vector index when corpus size and semantic queries justify it. There is no universal runnable `fabius-vec` dependency. Research inputs and inspirations are recorded in [credits/](credits/README.md).

---

## The libraries — all under one fabius index

| Library | Owner skill | Holds | Index (read first) | Status |
|---|---|---|---|---|
| **fabius-agents** | `fabius-cohors` | production agent shapes across domains and languages | [`skills/fabius-cohors/references/agent-catalog.md`](skills/fabius-cohors/references/agent-catalog.md) | bundled reference corpus |
| **fabius-design** | `fabius-decor` | design teardowns, animation/UI references, icon/motion/material maps, RTL/BiDi discipline, review vocabulary + generated-UI anti-pattern catalogue | [`skills/fabius-decor/references/design-system.md`](skills/fabius-decor/references/design-system.md) | bundled reference corpus |
| **fabius-knowledge** | `fabius-archivum` | LLM-wiki pattern, memory schema, the multi-project record contract (read-first gate · staleness cross-check · sync-back · two-writer rules), cross-session auto-recall, meeting capture, video ingest, source-grounded notebook connector, and optional RAG prototype | [`skills/fabius-archivum/references/memory-schema.md`](skills/fabius-archivum/references/memory-schema.md) | design reference; run only after its documented dependency smoke test |
| **fabius-figura** | `fabius-decor` | chart-selection, data-ink, palette, SVG, and diagram guidance | [`skills/fabius-decor/references/visualization.md`](skills/fabius-decor/references/visualization.md) | entry guidance; no promised full component library |
| **fabius-disciplina** | `fabius-disciplina` | impact-mapped testing, systematic debugging, planning, and verification | [`skills/fabius-disciplina/references/process-playbook.md`](skills/fabius-disciplina/references/process-playbook.md) | bundled reference corpus |
| **fabius-mercatus** | `fabius-mercatus` | channel playbooks, swipe references, and launch frames | [`skills/fabius-mercatus/references/marketing-playbook.md`](skills/fabius-mercatus/references/marketing-playbook.md) | bundled reference corpus |
| **fabius-praesidium** | `fabius-praesidium` | defensive hardening guides and audit checklists | [`skills/fabius-praesidium/references/security-playbook.md`](skills/fabius-praesidium/references/security-playbook.md) | bundled reference corpus |
| **fabius-ludus** | `fabius-ludus` | engine recipes, feel patterns, and pixel-art references | [`skills/fabius-ludus/references/game-playbook.md`](skills/fabius-ludus/references/game-playbook.md) | bundled reference corpus |
| **fabius-catena** | `fabius-catena` | EVM/Solana development and provenance sealing | [`onchain-playbook.md`](skills/fabius-catena/references/onchain-playbook.md) · [`sealing.md`](skills/fabius-catena/references/sealing.md) | bundled reference corpus |
| **fabius-machina** | `fabius-machina` | automation build/verify discipline and silent-failure catalog | [`skills/fabius-machina/references/automation-playbook.md`](skills/fabius-machina/references/automation-playbook.md) | bundled reference corpus |
| **fabius-scientia** | `fabius-scientia` | scientific-method loop, database lookup, and reproducibility | [`skills/fabius-scientia/references/science-playbook.md`](skills/fabius-scientia/references/science-playbook.md) | bundled reference corpus |
| **fabius-doctrina** | `fabius-doctrina` | serving, MLOps/experiment tracking, and model evaluation | [`skills/fabius-doctrina/references/ml-engineering-playbook.md`](skills/fabius-doctrina/references/ml-engineering-playbook.md) | bundled reference corpus |
| **fabius-fortuna** | `fabius-fortuna` | market/economic analysis, valuation, backtesting, and risk | [`skills/fabius-fortuna/references/markets-and-quant-playbook.md`](skills/fabius-fortuna/references/markets-and-quant-playbook.md) | bundled reference corpus |
| **fabius-concilium** | `fabius-concilium` | strongest-seat baseline, council protocol, and runnable reference | [`council-protocol.md`](skills/fabius-concilium/references/council-protocol.md) · [`council.mjs`](skills/fabius-concilium/references/council.mjs) | bundled reference corpus |
| **fabius-lean** | `fabius-parcus` | overcomplication tells, surgical-change discipline, assumptions | [`skills/fabius-parcus/references/lean/guidelines/`](skills/fabius-parcus/references/lean/guidelines/) | bundled reference corpus |

**Honest current state.** Bulk source material still ships inside owner `references/` directories. Those descendants are source material, not independently triggerable skills: former nested skill entrypoints are named `REFERENCE.md`, while other source documents retain descriptive filenames. The packaged discovery gate requires the public skill set to equal the fifteen manifest entries exactly. Figura is an entry/guidance layer today, not a hidden full chart-component library. Archivum's RAG folder is optional reference code, not a guaranteed executable feature of every install.

**Resource toolkits.** Owners also index external tools and datasets with licence/risk notes. These catalogs are recommendations to inspect at task time, not bundled dependencies and not proof that every upstream entry remains available or suitable. The router's [`skill-frontmatter.md`](skills/fabius/references/skill-frontmatter.md) contract applies to the fifteen public `SKILL.md` files; nested `REFERENCE.md` source documents are deliberately non-discoverable.

## Retrieval contract — how the brain reaches the corpus

1. **Classify** the task (routing-policy R1) → the owning skill → its library above.
2. **Read the index first** (R9 · M7) — one-line summaries and metadata, never the bulk.
3. **Page in only the matching slice**; if it still exceeds the budget, **summarize-then-link**, don't inline.
4. Use symbolic search first. Add an owner's vector index only when measured recall or corpus size justifies it, and only after that exact implementation passes its dependency and query smoke tests. Archivum's `rag/` folder is one optional prototype, not a universal retrieval command.

## Externalization (M9) — the packaging direction

The standing rule (routing-policy **M9**) is direction, not a description of today's package: the brain should hold the index, while bulk moves to a separately versioned, content-addressed corpus only after retrieval quality and offline availability are preserved. Today the bulk remains bundled under `references/`, so the install is not yet the lean externalized form. The `REFERENCE.md` boundary prevents that bulk from expanding the public trigger surface while migration remains unfinished. Research inputs stay attributed in [credits/](credits/README.md).

> One brain, one index, one reviewed public skill surface; bundled references today, measured externalization tomorrow.
