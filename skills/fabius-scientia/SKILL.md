---
name: fabius-scientia
description: >
  fabius's scientific-research layer — the empirical method made executable, for biology and the
  data-heavy sciences. It runs a real hypothesis loop (clarify → literature → competing, falsifiable
  hypotheses → experiment design → predictions → report), grounds every factual claim in an
  authoritative database with cross-identifier mapping instead of guessing, sequences bioinformatics /
  cheminformatics / omics pipelines as routers over field-standard tools, and enforces the
  reproducibility gotchas an LLM otherwise gets confidently wrong. Use for biology, genomics / RNA-seq,
  proteins, chemistry / molecules, clinical and multi-omics data, scientific-database lookups
  (gene / compound / variant / disease), "generate a hypothesis", "design an experiment", "analyze
  this dataset scientifically", or a literature-grounded research question. The method loop, the
  unified database-lookup contract, the pipeline-as-router pattern, and the reproducibility checklist
  live in references/science-playbook.md.
when_to_use: >
  "search PubMed", "differential expression", "protein structure", "map this identifier", "is
  this finding supported by the literature".
license: UNLICENSED
metadata:
  author: Ariel Shemesh
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Scientia — hypothesis, evidence, reproducible result

*Scientia* — knowledge won by method, not by assertion. A confident-sounding answer is the failure mode here: in science, an unsourced claim or a silently-wrong pipeline is worse than "I don't know." This layer makes the agent an empiricist — it hypothesizes in the open, grounds in sources, and leaves a reproducible trail.

## 1. Method first — competing hypotheses, never one

Run the loop explicitly: **clarify the phenomenon → search the literature → synthesize → generate 3–5 *competing* mechanistic hypotheses → score each on testability / falsifiability / parsimony / explanatory power / novelty → design experiments with controls and a stated statistical test → state quantitative, falsifiable predictions → report concisely.** The load-bearing step is *competing* hypotheses: a single hypothesis is advocacy, not science. Force the alternatives and let the scoring, not the first idea, decide.

## 2. Ground every claim — ask the database, don't approximate

A scientific fact has a source; produce it. Use a **unified lookup contract** instead of a plausible guess:

1. Define the retrieval contract — entity + constraints + fields + exhaustive-vs-targeted.
2. Pick a **primary** source and a **validation** source; avoid fanning out across many APIs.
3. **Count first, then paginate** deterministically; reconcile the counts.
4. Return **auditable provenance** — endpoints, parameters, ID conversions, and any warnings.

Identifiers differ per database, so the conversion route *is* knowledge: gene symbol → NCBI Gene → Ensembl / UniProt; compound name → PubChem CID → ChEMBL; variant rsID across dbSNP / ClinVar / gnomAD; disease → Open Targets / Monarch → EFO / MONDO. Reproducibility and provenance beat a confident approximation every time.

## 3. Pipelines are routers, not reimplementations

A heavyweight analysis (RNA-seq, docking, MD, single-cell) is a **sequence of specialist steps**, not one monolithic script. Name the stages, hand off between them, and document the **convergence artifact** (e.g. a gene-level counts matrix) that joins them. Default to the **audited field-standard pipeline** (e.g. `nf-core`) before any manual recipe; reserve the manual path for learning or a constrained environment.

## 4. Be resource-aware before you choose a tool

Compute-heavy science branches on hardware. Probe CPU / GPU / RAM / disk *first*, then choose: pandas vs Dask at the memory tier; PyTorch on MPS / CUDA / ROCm / CPU by the GPU tier; the worker count for parallelism. Picking the tool before knowing the machine is how a job OOMs at hour three.

## 5. The reproducibility gotchas — the bugs an LLM makes confidently

Bake the domain failure-points into every pipeline as a checklist, because these are the mistakes made *fluently*: RNA-seq wants **raw counts, not TPM/FPKM** into DESeq2, **≥3 replicates**, correct **strandedness**, no **batch/condition confounding**, and **consistent gene IDs** across differential-expression and enrichment; species is **case-sensitive** (`PAX7` ≠ `Pax7`). **Pin tool versions** (database schemas drift upstream), keep API keys in **env, never in scripts or shell history**, and isolate dependencies. Provenance over plausibility.

## Boundaries

One concern per skill — keep scientia to the genuinely scientific core and route the rest: general literature synthesis and the build/debug process to `fabius-disciplina`; storing and re-querying findings to `fabius-archivum`; and the **supply-chain risk of third-party science skills** (they execute code — scan and review before adopting) to `fabius-praesidium`. Don't mirror an entire discipline's tool catalog — encode the transferable *patterns* and a curated set of high-value workflows; the rest is `references/`.

## References

- The hypothesis-generation loop with scoring criteria, the unified database-lookup contract and the cross-identifier maps, the pipeline-as-router pattern, the resource-detection prerequisite, and the per-domain reproducibility checklist → `references/science-playbook.md`.
- Structural-biology prediction (AlphaFold / -Multimer with honest pLDDT/PAE confidence), resource-gated GPU/MD/FEM simulation and protocol-as-code wet-lab automation (PyLabRobot), and auditable literature grounding (Zotero, Jupyter-AI) as additional pipeline-as-router stages → `references/structural-bio-and-simulation.md`.
- The verified tool + HuggingFace-model stack — bio/chem/omics toolkits and protein/genomics/chemistry models, with the non-commercial trap flagged (AlphaFold3, ESM3/ESM-C, Nucleotide Transformer) vs the commercial-clean picks (ESM-2, Boltz-2, Chai-1, Evo 2) → `references/science-toolkit.md`.

**Live tier (optional).** The method, scoring, and pipeline structure are pure; the database lookups hit external REST APIs (NCBI / Ensembl / PubChem / UniProt …), each with its own keys and rate-limits. fabius bundles none — the full map is in [ARCHITECTURE.md](../../ARCHITECTURE.md) (*External connections*).

Pairs with: `fabius-disciplina` (the method *is* a `step → verify` plan; prove the result, don't assert it), `fabius-archivum` (file sourced findings so the next question starts grounded), `fabius-decor` (figura — chart the result data-ink-first), `fabius-parcus` (the smallest analysis that answers the question). `stop fabius` drops the stance (kill-switch owned by `fabius`).
