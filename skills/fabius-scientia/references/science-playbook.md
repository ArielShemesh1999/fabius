# Fabius Scientia — scientific-method & database-lookup playbook

The on-demand depth for `fabius-scientia`'s empirical-method concern. The skill is the contract; this is how you run it. Scout wide, strike narrow.

The skill (`../SKILL.md`) names the five moves: method-first, ground-every-claim, pipelines-as-routers, resource-aware, reproducibility-gotchas. This file is the operating manual behind each — templates, decision tables, per-API data, failure checklists. Versions and limits below are an **early-2026 snapshot** — re-verify before relying on them.

## 1. The hypothesis loop — run it as explicit steps

Never advocate one mechanism. The load-bearing rule: **force 3–5 competing hypotheses and let the scoring decide.** A lone hypothesis is advocacy.

1. **Clarify the phenomenon.** State the observation, the system, the units. Strip ambiguity before searching.
2. **Search the literature.** Biomed → PubMed (E-utilities). General → fabius-disciplina. Capture PMIDs + the claim each supports.
3. **Synthesize.** What is established, what is contested, what is unknown. The gap is where hypotheses live.
4. **Generate 3–5 competing mechanistic hypotheses.** Distinct mechanisms, not rewordings. Include at least one null/boring alternative.
5. **Score each** on the rubric below; rank by total.
6. **Design experiments** — positive + negative controls, the manipulated variable, the readout, and a **named statistical test** stated up front (e.g. two-way ANOVA, DESeq2 Wald, log-rank).
7. **State quantitative, falsifiable predictions** — "H2 predicts ≥2-fold knockdown effect, p<0.05; if effect <1.2-fold, H2 is rejected."
8. **Report concisely** — phenomenon → ranked hypotheses with scores → the discriminating experiment → predictions.

### Scoring rubric (score each hypothesis 1–5)

| Criterion | Asks | Low (1) | High (5) |
|---|---|---|---|
| Testability | Can a feasible experiment probe it? | needs unavailable tech | bench-ready today |
| Falsifiability | What result kills it? | unfalsifiable / vague | one clean disconfirming outcome |
| Parsimony | How many assumptions? | many ad-hoc steps | one mechanism |
| Explanatory power | Covers the observations? | explains a fragment | explains all + edge cases |
| Novelty | New vs. restated dogma | textbook restatement | genuinely new prediction |

The winning experiment is the one that **discriminates between the top two** — design for the contrast, not for confirming the leader.

## 2. The unified database-lookup contract

Turn many heterogeneous APIs into one deterministic retrieval. A scientific fact has a source — produce it; reproducibility and provenance beat a plausible approximation.

1. **Define the contract** — entity + constraints + fields + exhaustive-vs-targeted. ("All ClinVar pathogenic variants in BRCA1, fields: rsID/clin-sig/condition. Exhaustive.")
2. **Pick a PRIMARY source + a VALIDATION source.** Avoid fan-out across many APIs — two well-understood sources beat six half-trusted ones.
3. **COUNT first, then paginate deterministically.** Get the total, then walk fixed-size pages (sorted key) so the run is repeatable.
4. **Reconcile the counts.** Records returned == count promised? If not, stop and report the gap — don't silently truncate.
5. **Return auditable provenance** — endpoints hit, params, ID conversions performed, and any warnings (rate-limit retries, partial pages, deprecated fields).

## 3. Cross-identifier mapping — the conversion route IS knowledge

IDs differ per database; the route between them is the knowledge, not a detail. Standard routes:

| From | Through | To |
|---|---|---|
| Gene symbol | NCBI Gene | Ensembl ID / UniProt accession |
| Compound name | PubChem CID | ChEMBL ID (via UniChem) |
| Variant rsID | dbSNP | ClinVar / gnomAD records |
| Disease name | Open Targets / Monarch | EFO / MONDO ontology ID |

Resolve to a stable accession early, carry it through the pipeline, and log every hop in the provenance trail.

## 4. Per-API operational facts (data — re-verify, point-in-time)

Capture these as DATA, not lore; APIs drift.

| Fact | Databases | Consequence |
|---|---|---|
| POST-only (need `curl`, not a simple GET fetch) | Open Targets, gnomAD, GDC, SEC EDGAR | a plain GET fetch silently fails / 405s |
| Rate limits | NCBI 3/sec (10 with key), Ensembl 15/sec | exceed → 429; throttle + back off |
| Free API key required | NCBI E-utilities (recommended) | raises your rate ceiling |
| Paid / restricted (with free fallback) | DrugBank (paid → use ChEMBL/PubChem), COSMIC (academic → use cBioPortal/gnomAD) | don't block on access you lack |

### Database categories

| Domain | Sources |
|---|---|
| Chemistry | PubChem · ChEMBL · DrugBank · KEGG |
| Biology | UniProt · Ensembl · NCBI · STRING · GEO · GTEx · PDB · AlphaFold · dbSNP · gnomAD |
| Clinical | Open Targets · ClinVar · cBioPortal · OMIM · HPO · Monarch |

## 5. Pipeline-as-router — sequence specialists, name the convergence artifact

A heavyweight analysis is a **sequence of specialist steps**, not a monolith. Name the stages, hand off, document the artifact that joins them. **Always offer the audited field-standard path before the manual recipe.**

Worked example — bulk RNA-seq:

```
FastQC + trim  →  STAR / Salmon  →  counts matrix  →  pydeseq2  →  pathway enrichment  →  figures
                                    (convergence artifact)
```

The gene-level **counts matrix** is the convergence artifact: everything upstream produces it, everything downstream consumes it. Field-standard first:

```bash
# Preferred: one audited command (reproducible, peer-reviewed)
nextflow run nf-core/rnaseq --input samplesheet.csv --genome GRCh38 -profile docker
```

Reserve the manual STAR-by-hand recipe for learning or a constrained environment.

## 6. Resource-awareness — probe the machine FIRST

Picking the tool before knowing the machine is how a job OOMs at hour three. Probe CPU / GPU / RAM / disk and write a small resources file, then branch:

| Dimension | Probe | Branch |
|---|---|---|
| RAM | `free -g` / `vm_stat` | pandas (fits in RAM) vs Dask (out-of-core) |
| GPU | `nvidia-smi` / `rocminfo` / MPS check | PyTorch device: CUDA / ROCm / MPS / CPU |
| CPU | `nproc` | worker count for parallel stages |
| Disk | `df -h` | intermediate-file strategy / streaming |

## 7. Reproducibility gotchas — the bugs an LLM makes confidently

Bake these per-pipeline as a failure-points checklist; they are the mistakes made *fluently*.

RNA-seq / DESeq2:
- [ ] **RAW counts** into DESeq2 — never TPM / FPKM (they break the negative-binomial model)
- [ ] **≥3 replicates** per condition — fewer kills dispersion estimation
- [ ] Correct **strandedness** (unstranded / forward / reverse) at quantification
- [ ] No **batch ↔ condition confounding** — if batch tracks condition, the effect is unattributable
- [ ] **Consistent gene IDs** across differential-expression and enrichment (one namespace, e.g. Ensembl)
- [ ] **Species is case-sensitive** — `PAX7` (human) ≠ `Pax7` (mouse)

Every pipeline:
- [ ] **Pin tool + database versions** — schemas and annotations drift upstream
- [ ] **API keys in env, never in scripts or shell history**
- [ ] **Isolate dependencies** (conda env / container) per analysis

## 8. Structuring science skills

Build science as **many single-concern skills**, not one giant biology skill. But `fabius-scientia` must **not** mirror an entire 147-skill catalog — encode the transferable **patterns** (this playbook) plus a curated set of high-value workflows; the rest stays in `references/`. See the externalization rule in `../../../CORPUS.md` (M9: hold the index, not the bulk).

**Supply-chain caution:** third-party science skills *execute code*. Scan and review before adopting — route that risk to `fabius-praesidium`.

## Boundaries / routing

| Need | Route to |
|---|---|
| General literature synthesis, build/debug process | `fabius-disciplina` |
| Storing & re-querying sourced findings | `fabius-archivum` |
| Charting results data-ink-first (figura) | `fabius-decor` |
| Vetting third-party skills that run code | `fabius-praesidium` |

---

Adapted from K-Dense-AI/scientific-agent-skills (MIT; per-skill licenses vary) — re-expressed in fabius's own voice.
