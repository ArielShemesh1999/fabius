# Fabius Scientia — structural biology, simulation & literature-grounding pipeline stages

More executable verticals under scientia's existing rules — structure prediction, compute-heavy simulation, and an auditable reference library — each folded as a pipeline stage, not a new doctrine.

The skill (`../SKILL.md`) already sets the laws this file obeys: **pipelines are routers** (§3), **resource-aware before tool choice** (§4), **ask the database, don't approximate** (§2), and the **reproducibility gotchas** (§5). Nothing here overrides them — these are additional stages that snap onto the same rails. The named tools are ARGAZ-catalogued ecosystem capabilities fabius can *apply*, not runtime fabius bundles; their DB/web calls are the optional live tier (→ ARCHITECTURE.md). Versions below are an **early-2026 snapshot** — re-verify the number before relying on it.

## 1. Structural biology — prediction is a heavyweight stage with a convergence artifact

Protein 3D structure and complex prediction is a router stage, not a monolith. Treat **AlphaFold** (single-chain 3D) and **AlphaFold-Multimer** (complexes / multimers) as one specialist step in a longer pipeline — sequence in, structure out — exactly like STAR in the RNA-seq router.

- **Convergence artifact = the predicted structure + its confidence.** Downstream (docking, MD, interface analysis) consumes the structure; everything upstream produces it. Name it; hand off to it.
- **Report confidence honestly, never silently.** The structure ships *with* pLDDT (per-residue) and PAE / ipTM (interface, for multimers). Low-pLDDT regions are disorder or low-confidence guesses — flag them; don't draw mechanistic conclusions on a pLDDT<50 loop.
- **Ground the structural claim like any other** (§2): a known structure has a source — produce the **PDB ID** or the **AlphaFold DB** accession (UniProt-keyed) before predicting from scratch. Predict only when no deposited structure exists; record which path you took in the provenance trail.
- AlphaFold is **GPU-heavy and disk-heavy** (genetic-database search dwarfs the inference). It is governed by §2 below — probe before you launch.

```
sequence  →  template/MSA search  →  AlphaFold / -Multimer  →  predicted structure + pLDDT/PAE  →  docking / MD / interface
                                                                (convergence artifact, with confidence)
```

## 2. Simulation — resource-detection is not optional here, it is the first stage

GPU physics / FEM / MD and contact / cloth simulation are the most compute-heavy work scientia touches. Apply §4 (resource-aware) **as a hard gate**: probe CPU / GPU / RAM / disk and write the small resources file *before* choosing the engine. Picking the simulator before knowing the machine is the canonical OOM-at-hour-three.

| Probe | Branches the simulation choice |
|---|---|
| GPU (`nvidia-smi` / `rocminfo` / MPS) | GPU-accelerated MD/FEM vs CPU fallback; precision (fp32/fp64) |
| RAM | system size / mesh resolution that fits in core vs streamed |
| Disk | trajectory-write strategy (frame stride, compression) |
| CPU (`nproc`) | domain-decomposition / worker count |

- MD wants the same reproducibility floor as any pipeline (§5): **pinned engine + forcefield version**, fixed random seed where the question needs determinism, and a stated equilibration protocol — an unreported seed or unpinned forcefield makes the run unrepeatable.
- Long simulations are a `step → verify` plan, not one launch — checkpoint, and verify convergence (energy plateau, RMSD) before trusting downstream analysis. That discipline is `fabius-disciplina`'s; route there, don't re-derive it.

**Wet-lab automation — the protocol becomes code.** When the "simulation" is a physical experiment, **PyLabRobot** (vendor-agnostic, async, Jupyter-native) turns a bench protocol into reproducible Python that drives liquid handlers / plate readers across vendors. The win is the §5 win: a protocol-as-code is version-pinnable, diffable, and re-runnable — a PDF SOP is none of those. Same gotchas apply: pin the library version, keep instrument credentials in **env, never in the notebook** (→ keys-in-env is §5; supply-chain vetting of the SDK and any plug-ins is `fabius-praesidium`).

## 3. Literature grounding — the source must be producible, with the route

This reinforces §2 of the skill ("ask the database, don't approximate"), it does not replace it. A scientific claim has a source — **produce it, with the endpoint / identifier / conversion route.** Two tools make that source auditable:

- **Zotero** — a personal reference library with semantic search. Use **local no-key mode** for offline / private work and the **cloud API** when sync is wanted. Ingest by **DOI or URL**, dedup, and tag, so every cited claim resolves to a stored item, not a half-remembered title. This is the human-readable end of the §3 cross-identifier discipline: paper claim → DOI → stored, taggable record.
- **Jupyter-AI** — notebook-driven analysis where the prompt, the code, the data pull, and the figure live in one re-runnable document. The notebook *is* the provenance: re-execute top to bottom and the result reproduces, or it doesn't and you've found the gap.

The rule stands unchanged: don't paraphrase a finding you can't point at. The endpoint, the identifier (DOI / PMID / accession), and the conversion route (§3 of the playbook) are the deliverable, not a footnote. Zotero's cloud sync and Jupyter-AI's model/web calls are **optional live-tier** dependencies — fabius bundles neither; the map is in ARCHITECTURE.md.

## 4. Reproducibility floor — unchanged, restated for these stages

The §5 gotchas are not RNA-seq-only; they bind every stage above. Per-stage, the non-negotiables:

- [ ] **Pin every version** — AlphaFold + its genetic databases, the MD engine + forcefield, PyLabRobot, the Zotero schema. Schemas and weights drift upstream; an unpinned stack is unrepeatable.
- [ ] **Report confidence, don't bury it** — pLDDT/PAE for structures, convergence metrics for MD. A number without its uncertainty is a guess wearing a lab coat.
- [ ] **≥3 replicates** where the claim is statistical (replicate simulations / wet-lab wells), and **FDR correction** on any multiple-testing readout — the same fluent LLM mistakes recur outside transcriptomics.
- [ ] **Species / identifier case-sensitivity** carries through: `PAX7` ≠ `Pax7` at the UniProt lookup that seeds AlphaFold, the same as at the gene table.
- [ ] **Credentials in env, never in scripts, notebooks, or shell history** — labware SDKs and Zotero API keys included.

YAGNI ladder (`fabius-parcus`): don't fold a structure-prediction or MD stage in because it's impressive — fold it only when the question demands it. The smallest pipeline that answers the question wins; a deposited PDB structure beats a fresh AlphaFold run, a closed-form estimate beats an MD campaign.

## Boundaries / routing

| Need | Route to |
|---|---|
| Long-run as a `step → verify` plan; debugging a stuck simulation | `fabius-disciplina` |
| Storing & re-querying predicted structures / sourced findings | `fabius-archivum` |
| Charting trajectories / confidence data-ink-first | `fabius-decor` |
| Vetting AlphaFold wrappers, lab-SDK plug-ins, third-party science skills that run code | `fabius-praesidium` |
| Smallest pipeline that answers the question | `fabius-parcus` |

---

Tools named (AlphaFold / AlphaFold-Multimer, PyLabRobot, Zotero, Jupyter-AI) are ARGAZ-catalogued ecosystem capabilities applied under scientia's rules — re-expressed in fabius's own voice, not bundled runtime.
