# Fabius Scientia — the science toolkit (bio · chem · omics)

Loaded on demand by `fabius-scientia`. The field-standard **tools** and the strongest HF **science models** (2026), license-verified — because the single biggest trap here is a **non-commercial model wearing a research paper's prestige.** AlphaFold**2** is Apache but AlphaFold**3** is non-commercial + gated; Nucleotide Transformer is non-commercial; **AlphaGenome's code is Apache-2.0 while its weights and its free API are not.** A license flag is a *dated* fact and it moves in both directions — the whole ESM line (ESMC · ESMFold2 · ESM3) went **MIT** under Chan Zuckerberg Biohub on 2026-05-27, so "ESM = non-commercial" is now exactly as wrong as "ESM = MIT" once was. Re-read the LICENSE file *and* the model card before a flag decides a commercial deliverable, and read the license in parts: code, weights and the hosted API can carry three different terms. Ground every factual claim in an authoritative database (Biopython/Entrez), and sequence pipelines as **routers over field-standard tools** — don't reinvent normalization or dispersion models.

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
| **ESM-2 / ESMFold** (facebook) | **MIT** | The cheap, stable baseline protein-LM — embeddings, zero-shot variant effects, single-sequence folding (no MSA). 650M is the sweet spot; supersedes ProtT5/ProtBERT. Still MIT, but no longer the *only* MIT option in the ESM lineage — the frontier moved to the two rows below. |
| **ESMC 300M / 600M / 6B** (biohub) | **MIT** | *Default commercial protein-LM* — frontier embeddings and variant-effect scoring, plus sparse-autoencoder checkpoints when you need the representation to be interpretable. Code **and weights** are MIT and ungated on the `biohub/*` org; the Cambrian **Non-Commercial** license that used to gate ESM-C/ESM3 is retired, and `biohub/esm3-sm-open-v1` (generative design) is MIT too — that grant lives in the repo's Licenses section, since the ESM3 model card itself carries no license tag. |
| **ESMFold2 / -Fast** (biohub) | **MIT** | All-atom structure prediction across the whole biomolecule set — protein, DNA, RNA, small molecules, modified residues — on a frozen ESMC-6B, single-sequence *or* MSA-conditioned, emitting pLDDT / pAE / pTM / ipTM. Reported on FoldBench to meet or exceed AlphaFold3 on antibody-antigen and protein-protein complexes, and invertible for de-novo binder design. `-Fast` is the single-sequence throughput variant; MSA-conditioning is for hard targets. Data cutoff **Sept 2021** — the `-Experimental-*` checkpoints (including `-Cutoff2025`) exist to reproduce the paper, not to run work on. Query the **ESM Atlas** (6.8B sequences, >1B predicted structures) before folding anything from scratch. |
| **Boltz-2** (jwohlwend/boltz) | **MIT** | Open AlphaFold3-class **structure + binding affinity** with commercially-usable weights — the default for complex/ligand work. |
| **Chai-1** (chai-lab) | **Apache-2.0** | Second commercially-clean AF3 alternative (protein/DNA/RNA/ligand), explicitly permitted for drug discovery. |
| **OpenFold3-preview** (aqlaboratory) | **Apache-2.0** | A bitwise AlphaFold3 reproduction from the AlQuraishi Lab / OpenFold consortium — standard and non-canonical protein / RNA / DNA chains plus small molecules, structure templates, ColabFold or JackHMMER/hhblits MSA pipelines, multi-GPU distributed inference, low-memory mode; `pip install openfold3`. Route here when the deliverable must be auditable end to end: the **training data is published** — including the 13M-sequence MGnify distillation set — so the weights are *reproducible*, not merely downloadable, which no other co-folding stage offers. Weights sit behind an auto-approve HuggingFace form; that is a download gate, not a license restriction. Boltz-2 / Chai-1 stay the fast commercial defaults. |
| **AlphaFold** (DeepMind) | AF2 code Apache / **weights CC-BY-4.0** · AF3 ⚠️ **non-commercial + gated** | AF2 (via ColabFold) = commercial-OK reference baseline; **AF3 forbids commercial use** — route commercial complex+ligand to Boltz-2 / Chai-1 / OpenFold3. |
| **ProteinMPNN** (dauparas) | **MIT** | The field-standard inverse-folding / **sequence-design** model (the design half the structure predictors don't cover; partners with RFdiffusion). |

## Genomics & single-cell

| Model | License | Note |
|---|---|---|
| **Geneformer** (ctheodoris) | Apache-2.0 | Single-cell foundation model — cell-type annotation, in-silico perturbation to nominate targets. Consumes scanpy/AnnData. |
| **scGPT** (bowang-lab) | MIT | Generative single-cell multi-omics (annotation/integration/perturbation). *Checkpoints via repo links — pin the one you use.* |
| **Evo 2** (arcinstitute/evo2_7b) | **Apache-2.0** | The largest fully-open biological FM (DNA+RNA+protein, up to 1Mb context) — the commercial-clean genomics LM the NC Nucleotide Transformer isn't. |
| **AlphaGenome** (google-deepmind) | code Apache-2.0 · ⚠️ **weights + free API non-commercial** | The current regulatory-variant reference — up to **1 Mb** of DNA at **single-base-pair** resolution across gene expression, splicing patterns, chromatin features and contact maps; Enformer's ~200 kb binned regime is the previous generation. Read this license in three parts: `alphagenome` (API client) and `alphagenome_research` (model code) are Apache-2.0, but the Kaggle / HuggingFace **weights require accepting non-commercial model terms**, the free API is non-commercial-only (a commercial offering is in early testing), and all other materials are CC-BY-NC-4.0. The Apache-2.0 badge on the repo does **not** clear a commercial deliverable. Local inference wants an **H100-class GPU**, so in practice you use the API — which reimposes the same non-commercial term. |
| **Enformer** (EleutherAI port) | CC-BY-4.0 | Expression/epigenetics from ~200kb DNA — commercial-OK variant-effect-on-expression (unlike Nucleotide Transformer), and the clean fallback when AlphaGenome's model terms block a paid deliverable. |
| **Nucleotide Transformer** (InstaDeepAI) | ⚠️ **CC-BY-NC-SA-4.0** | Leading DNA-LM but **non-commercial + share-alike** — for commercial DNA work prefer Evo 2 / Enformer. |

## Chemistry

- **MoLFormer-XL** (ibm, Apache-2.0) — molecular LM over SMILES for embeddings/property prediction; pairs with RDKit-canonicalized SMILES. **ChemBERTa** (DeepChem, MIT) — lightweight SMILES baseline inside DeepChem/MoleculeNet.

## Evaluate

**ProteinGym** (OATML-Markslab/**ProteinGym_v1**, MIT) — the standardized variant-effect benchmark + leaderboard (~2.7M substitutions, 217 DMS assays). The *predictions → report* step grounded in a real benchmark, not self-reported accuracy. *(Use `_v1` — `_v0.1` is stale/broken.)*

## Pairs with

`fabius-scientia` (the hypothesis loop + database-lookup contract), `fabius-doctrina` (serve/fine-tune a science model), `fabius-praesidium` (a non-commercial or gated weight in a paid/clinical deliverable is a real licensing risk), and `fabius-archivum` (literature/database grounding for the method loop).
