# Fabius Decor — explanatory diagrams & concept maps

The on-demand depth for `fabius-decor`'s explanatory-diagram concern — diagrams that *teach* a codebase, a domain, or a flow. The skill is the contract; this is how you run it. Scout wide, strike narrow.

A diagram that explains is a **pedagogy** problem, not a drawing one. The pipeline is fixed and repeatable:

```
extract → typed graph → layer → tour
```

Each stage is deterministic-first, LLM-narrow. Cross-links: owning skill `../SKILL.md`; corpus index `../../../CORPUS.md`; pairs with `references/visualization.md` (figura) for rendering and `fabius-disciplina` for diagram-as-code.

> Snapshot, early 2026. The upstream this re-expresses is a code-analysis tool; its taxonomy sizes and thresholds (below) are *its* tuned defaults, not fabius law. Take the method, fit the numbers to your domain.

## Stage 1 — Two-layer extraction (deterministic first, meaning second)

The single most important rule. Split the work in two passes:

| Pass | Who | Produces | Hard rule |
|---|---|---|---|
| **Structural** | a deterministic parser (AST / tree-sitter / wikilink scan / file walk) | the *facts*: parts and their connections | reproducible byte-for-byte; no model in the loop |
| **Semantic** | the LLM | *judgment only*: one-line summaries, tags, complexity, grouping, layer labels | **forbidden** from re-reading sources to re-derive facts the parser already captured |

Why the forbid clause matters: the moment the model re-derives structure it hallucinates edges that aren't there. Pin the facts in pass 1; let the model annotate, never invent. Cuts tokens hard and kills phantom structure.

Checklist before you let the model touch anything:
- [ ] Parser emitted every node + edge as data (JSON), not prose.
- [ ] Prompt to the model carries the graph and says "annotate these; do not add or remove parts."
- [ ] Model output is *merged onto* parser ids, never a fresh re-listing.

## Stage 2 — The artifact is a typed graph with a fixed vocabulary

A shared schema is the **contract** that lets parallel work compose and merge deterministically. Define it up front:

- **Small node-type set** — enumerate before extracting (e.g. `module`, `topic`, `concept`, `flow`). Small and domain-fit.
- **Small edge-type set** — likewise (`imports`, `related`, `contains`, `precedes`).
- **Stable id convention** — `type:path:name`. Same input → same id, always. This is what makes merge and dedupe possible.
- **Fixed weight per edge type** — a number per type, decided once, so importance is comparable across the graph.

**Caveat — do not copy the upstream taxonomy.** The source ships a 13-node / 26-edge *code-analysis* vocabulary tuned for source trees. Importing it into a general concept map is over-engineering. Lift the **principle** (fixed typed vocabulary + `type:path:name` ids + weighted edges) and define a *smaller* set that fits your domain. A wiki concept map needs maybe 3 node types and 3 edge types.

## Stage 3 — Deterministic merge (the safety net that lets the model be sloppy)

Because pass 2 output is messy, normalize mechanically so the model never has to be precise:

1. **Normalize ids** — strip double prefixes and project-name prefixes; add any that are missing. One canonical form.
2. **Rewrite edge endpoints** to the corrected ids.
3. **Dedupe** — nodes by `id`; edges by the tuple `(source, target, type)`.
4. **Drop dangling edges** — any edge whose source or target is not a known node id is deleted, not patched.

This pass is the reason pass 2 can be loose: garbage ids get healed or dropped, never rendered.

## Stage 4 — Topology-driven narrative (a tour, not a node dump)

The output is a **guided tour** that tells the story the README tells, through the lens of the actual structure. Drive ordering from cheap graph metrics, not vibes:

| Signal | Meaning | Use |
|---|---|---|
| **fan-in** (in-degree) | how many things depend on this | high → teach **early** (it's foundational) |
| **fan-out** (out-degree) | how many things this pulls in | high → good **overview** node (broad scope) |
| **entry point** | scored heuristic: filename patterns (`main`/`index`/`app`/`README`) + shallow path + low fan-in | where the tour starts |

Then:
- **BFS outward** from the entry point.
- **Map BFS depth → tour-step order.** Depth 0 = the overview; depth 1 = direct dependencies; deeper = detail.
- **Collapse tight clusters** (a strongly-coupled group) into **one** step so the tour isn't N near-identical stops.

## Cheap structural signals (derive before asking the model)

Squeeze structure from deterministic signals before spending a token:

- **Directory grouping** — strip the common path prefix, group by remaining top dir.
- **Directory-name → architectural role** lookup:

  | Dir name contains | Role |
  |---|---|
  | `routes`, `api`, `controllers` | api |
  | `services`, `core`, `domain` | service |
  | `models`, `db`, `schema` | data |
  | `utils`, `helpers`, `lib` | utility |

- **Inter-group import frequency** → dependency *direction* between layers (who depends on whom).
- **Intra-group density** > `0.3` → a cohesive layer worth naming as one box.

## Encoding rules that survive serialization

- **Ordinal / sequence info goes in numeric edge weights.** A flow of N steps gets monotonically increasing weights in `[0, 1]`, so step order survives a JSON/graph format that has no inherent ordering.
- **Demand exhaustive 1:1 emission with a self-check.** Never instruct "emit the meaningful edges" — that silently loses data. Require: *emitted edge count == resolved edge count*; make the agent **sum and compare** before writing. Mismatch → it re-emits, doesn't ship.

## Worked case — the Karpathy LLM-wiki pattern

A structured knowledge base: an `index.md` plus many `.md` files using `[[wikilink]]` syntax (the `fabius-archivum` shape). Map it with the same pipeline, scoped down:

- **All deterministic extraction lives in a parse script:**
  - `[[wikilink]]` → a `related` edge.
  - `index.md` sections → `topic` nodes.
- **The LLM adds only the implicit cross-references** the wikilinks don't spell out — nothing it could have parsed.
- **Render with a force-directed layout, not hierarchical** — a knowledge graph has no single root; let topology place it. Obeys fabius-decor's data-ink restraint; render via `references/visualization.md` (figura) or diagram-as-code (`fabius-disciplina`).

**Out of scope — encode the method, not the runtime.** The heavy code-analysis machinery from upstream (tree-sitter grammar packs, Louvain community detection, the live dashboard) is *not* fabius's runtime. We take the four-stage technique; we do not vendor the engine.

---

Adapted from Understand-Anything by Yuxiang Lin / Infinite Universe (Egonex-AI) (MIT) — re-expressed in fabius's own voice.
