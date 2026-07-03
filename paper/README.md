<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->
# The whitepaper

**[fabius-as-a-system.pdf](fabius-as-a-system.pdf)** — *Fabius: the autonomous AI agent that runs on every major model (v1.1.0).* The canonical, full whitepaper: the fifteen-skill architecture (the *praetorium* router that dispatches by layer + machinery + model-tier, four engineering specialists, nine domain verticals, on the always-on lean core), the proven core of eighteen routing rules with a full **proof of the mathematics under every rule**, the coherence theorem (the core composes into one consistent, complete, composable decision system), the four operational extensions (R11–R13, M9) stated honestly *outside* the proof, the fabius benchmark — one reproducible test in three panels (blind-judged quality on the newest Claude models · objective executed tests + factual checklists · blind cross-family demos) — and the direct-vs-analogy honesty ledger. The decision policy and coherence proof are stated over the routing core and hold unchanged as domain verticals are added on the same single-owner contract (`R1` Domain axis, `R13` verticals).

## How it was made — and why you can trust the math

The proofs were not hand-written and waved through. Each of the 22 formal statements was written by one agent and then **adversarially verified by an independent reviewer whose only job was to find an error**. That pass corrected ten of them — including a cap that should round to 4 not 3, a value-of-information attribution, a missing completeness hypothesis, and a linearity-vs-independence slip — before anything reached the page. A final auditor checked the whole set for cross-consistency and drafted the coherence capstone. The verified proof content lives in [`proofs.json`](proofs.json) and [`coherence.html`](coherence.html).

The honesty bar is the same as the rest of the project: **real-math** where the equation genuinely governs the routing decision, **analogy** where a correct theorem from generative-model sampling / transport / IR is borrowed only for its shape (and proves nothing about agents), **qualitative** for the one control-flow invariant. 18 real-math · 3 analogy · 1 qualitative.

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
| `proofs.json` | the 22 adversarially-verified proof blocks |
| `coherence.html` | the coherence capstone theorem |
| `build.sh` | one-command reproduce |

The figures and the benchmark's numbers are the same ones used in [`../RESEARCH.md`](../RESEARCH.md) and [`../BENCHMARKS.md`](../BENCHMARKS.md) — one benchmark, three panels, canonical receipt `../evals/results.benchmark.json`; the paper is their collected, proof-complete form.
