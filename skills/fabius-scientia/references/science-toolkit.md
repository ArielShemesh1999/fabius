# Fabius Scientia — the science toolkit (bio · chem · omics)

Loaded on demand by `fabius-scientia`. The field-standard **tools** and the strongest HF **science models** (2026), license-verified — because the single biggest trap here is a **non-commercial model wearing a research paper's prestige.** "ESM = MIT" holds only for Meta's ESM-2; AlphaFold**2** is Apache but AlphaFold**3** is non-commercial + gated; Nucleotide Transformer and ESM-C/ESM3 are non-commercial. Ground every factual claim in an authoritative database (Biopython/Entrez), and sequence pipelines as **routers over field-standard tools** — don't reinvent normalization or dispersion models.

## Toolkits

| Tool | License | Note |
|---|---|---|
| **RDKit** | BSD-3 | The cheminformatics workhorse — SMILES/SDF parsing, descriptors, fingerprints, conformers. Canonicalize before feeding any chem model. |
| **Biopython** | BSD-style | Sequences/alignments/PDB + programmatic NCBI-Entrez/UniProt access — backs the *ground-every-claim-in-a-database* contract. |
| **Biotite** | BSD-3 | Fast NumPy-array structural bioinformatics — vectorized structure analysis (RMSD, contact maps) to validate ESMFold/Boltz output. |
| **scanpy** (scverse) | BSD-3 | The single-cell RNA-seq backbone over AnnData — the substrate Geneformer/scGPT consume. Pair with **scvi-tools** (BSD-3 — scVI/scANVI/totalVI probabilistic models). |
| **Nextflow** (nf-core) | Apache-2.0 | Containerized, portable, reproducible pipelines (`nf-core/rnaseq`, `/sarek`) — the *pipelines-as-routers* pattern realized. |
| **Snakemake** | MIT | Rule/DAG reproducible pipelines (Pythonic, Make-like) — the other orchestration choice. |
| **OpenMM** | MIT (+LGPL) | GPU molecular dynamics — refine/stress-test predicted complexes beyond a static structure. |
| **Bioconductor** | Artistic-2.0 | The R omics ecosystem (DESeq2/edgeR/limma) — route bulk RNA-seq differential expression here. *(Per-package licenses vary.)* |
| **DeepChem** | MIT | Deep-learning-for-chemistry framework + the **MoleculeNet** benchmark — the eval harness for QSAR-style tasks. |

## Protein — structure & design

| Model | License | Note |
|---|---|---|
| **ESM-2 / ESMFold** (facebook) | **MIT** | *Default commercial protein-LM* — embeddings, zero-shot variant effects, single-sequence folding (no MSA). 650M is the sweet spot; supersedes ProtT5/ProtBERT. |
| **Boltz-2** (jwohlwend/boltz) | **MIT** | Open AlphaFold3-class **structure + binding affinity** with commercially-usable weights — the default for complex/ligand work. |
| **Chai-1** (chai-lab) | **Apache-2.0** | Second commercially-clean AF3 alternative (protein/DNA/RNA/ligand), explicitly permitted for drug discovery. |
| **ESM3 / ESM-C** (EvolutionaryScale) | ⚠️ **non-commercial** | Frontier embeddings (ESM-C) / generative design (ESM3) — but Cambrian **Non-Commercial** (only ESM-C **300M** is open). Don't assume ESM = MIT here. |
| **AlphaFold** (DeepMind) | AF2 code Apache / **weights CC-BY-4.0** · AF3 ⚠️ **non-commercial + gated** | AF2 (via ColabFold) = commercial-OK reference baseline; **AF3 forbids commercial use** — route commercial complex+ligand to Boltz/Chai. |
| **ProteinMPNN** (dauparas) | **MIT** | The field-standard inverse-folding / **sequence-design** model (the design half the structure predictors don't cover; partners with RFdiffusion). |

## Genomics & single-cell

| Model | License | Note |
|---|---|---|
| **Geneformer** (ctheodoris) | Apache-2.0 | Single-cell foundation model — cell-type annotation, in-silico perturbation to nominate targets. Consumes scanpy/AnnData. |
| **scGPT** (bowang-lab) | MIT | Generative single-cell multi-omics (annotation/integration/perturbation). *Checkpoints via repo links — pin the one you use.* |
| **Evo 2** (arcinstitute/evo2_7b) | **Apache-2.0** | The largest fully-open biological FM (DNA+RNA+protein, up to 1Mb context) — the commercial-clean genomics LM the NC Nucleotide Transformer isn't. |
| **Enformer** (EleutherAI port) | CC-BY-4.0 | Expression/epigenetics from ~200kb DNA — commercial-OK variant-effect-on-expression (unlike Nucleotide Transformer). |
| **Nucleotide Transformer** (InstaDeepAI) | ⚠️ **CC-BY-NC-SA-4.0** | Leading DNA-LM but **non-commercial + share-alike** — for commercial DNA work prefer Evo 2 / Enformer. |

## Chemistry

- **MoLFormer-XL** (ibm, Apache-2.0) — molecular LM over SMILES for embeddings/property prediction; pairs with RDKit-canonicalized SMILES. **ChemBERTa** (DeepChem, MIT) — lightweight SMILES baseline inside DeepChem/MoleculeNet.

## Evaluate

**ProteinGym** (OATML-Markslab/**ProteinGym_v1**, MIT) — the standardized variant-effect benchmark + leaderboard (~2.7M substitutions, 217 DMS assays). The *predictions → report* step grounded in a real benchmark, not self-reported accuracy. *(Use `_v1` — `_v0.1` is stale/broken.)*

## Pairs with

`fabius-scientia` (the hypothesis loop + database-lookup contract), `fabius-doctrina` (serve/fine-tune a science model), `fabius-praesidium` (a non-commercial or gated weight in a paid/clinical deliverable is a real licensing risk), and `fabius-archivum` (literature/database grounding for the method loop).
