<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/shear559/fabius -->
# The whitepaper

**[fabius-as-a-system.pdf](fabius-as-a-system.pdf)** — *Fabius — one set of operating rules above every model (v2.6.1).* The canonical, full whitepaper: the fifteen-skill architecture (the *praetorium* router that dispatches by layer + machinery + model-tier, four engineering specialists, nine domain verticals, on the always-on lean core), the proven core of **twenty-two** routing rules with a full **proof of the mathematics under every rule** — eighteen forming the mathematical core and four (R11–R13, M9) governing what the router itself adds — the coherence theorem (the core composes into one consistent, complete, composable decision system, with its exceptions printed in full), the fabius benchmark — one reproducible test in four panels (blind-judged quality on the four Claude models current at the 2026-07-01 run · objective executed tests + factual checklists · blind cross-family demos · the FBS run — the versioned 100-task suite executing the IDENTITY.md contract BASE → FAB → FAB_MEMORY) — and the honesty ledger (measured, not claimed). The decision policy and coherence proof are stated over the routing core and hold unchanged as domain verticals are added on the same single-owner contract (`R1` Domain axis, `R13` verticals).

## How it was made — and why you can trust the math

The proofs were not hand-written and waved through. Each of the 26 formal statements was written by one agent and then **adversarially verified by an independent reviewer whose only job was to find an error**. That pass corrected ten of them — including a cap that should round to 4 not 3, a value-of-information attribution, a missing completeness hypothesis, and a linearity-vs-independence slip — before anything reached the page. A final auditor checked the whole set for cross-consistency and drafted the coherence capstone. The verified proof content lives in [`proofs.json`](proofs.json) and [`coherence.html`](coherence.html).

The honesty bar is the same as the rest of the project: measured, not claimed. Each proof block is classed **real-math** where the equation genuinely governs the routing decision, or **qualitative** where the statement is a control-flow invariant rather than a theorem — **22 real-math · 4 qualitative**, the class recorded per block in `proofs.json`. Every rule is fabius's own — derived and adversarially verified; the few operational heuristics are labelled as such, carry no proof claim, and never govern a route the way the mathematical gates do.

## Reproduce the PDF

```bash
bash paper/build.sh
```

This self-hosts MathJax, recomputes the figures (`numpy` → SVG), assembles the HTML, and renders the PDF with headless Chrome.

## Files

| File | Role |
|---|---|
| `fabius-as-a-system.pdf` | the rendered paper (the deliverable) |
| `template.html` | the prose, tables, and layout (print CSS + MathJax) |
| `build.py` | assembler — inlines figures, math-safes + injects the proofs |
| `proofs.json` | the 26 adversarially-verified proof blocks (22 real-math · 4 qualitative) |
| `coherence.html` | the coherence capstone theorem |
| `build.sh` | one-command reproduce |

The figures and the benchmark's numbers are the same ones used in [`../RESEARCH.md`](../RESEARCH.md) and [`../BENCHMARKS.md`](../BENCHMARKS.md) — one benchmark, four panels, canonical receipt `../evals/results.benchmark.json`; the paper is their collected, proof-complete form.
