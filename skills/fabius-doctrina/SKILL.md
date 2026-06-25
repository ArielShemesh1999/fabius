---
name: fabius-doctrina
description: >
  fabius's AI/ML-engineering layer — train, serve, evaluate, and operate machine-learning and LLM
  systems as production software. This is the model lifecycle: dataset → train / fine-tune → EVALUATE →
  serve / infer → monitor. It owns model serving and inference (vLLM-class, OpenAI-compatible
  endpoints, batching, quantization), MLOps and experiment tracking (MLflow-class — runs, params,
  metrics, model registry, reproducibility), and rigorous model/LLM evaluation (eval harnesses, blind
  judges, ground-truth sets, regression gates). It is NOT the scientific method over natural-science
  data — that's fabius-scientia; it is NOT agent orchestration — that's fabius-cohors (doctrina owns
  the MODEL an agent calls, not the agent). Use when the task is to train / fine-tune a model, serve or
  deploy a model, evaluate a model or prompt, track ML experiments, set up an inference endpoint, build
  a RAG/LLM-app's model tier, or when the user says "serve this model", "fine-tune", "eval my prompts",
  "track these runs", "MLOps", "why is inference slow", or names vLLM / MLflow / an eval harness. The
  serving recipes, the MLOps + experiment-tracking contract, and the evaluation playbook live in
  references/ml-engineering-playbook.md.
---
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-6bbf82d118bce2cee9d7ac71f034fa26 · authenticity proof: PROVENANCE.md · github.com/ArielShemesh1999/fabius -->

# Fabius Doctrina — train it, serve it, prove it, operate it

*Doctrina* — the body of learning, the act of teaching something to learn. Machine **learning** is its literal subject: a model is taught from data, then it has to earn production. A model that scores well in a notebook and silently rots in production is the failure mode here — so the same Fabian stance holds, made specific to models: **scout the data and the metric, strike the smallest model that clears the bar, and prove it on a held-out reality before it serves a user.**

## 1. Doctrina and its neighbors — one concern, sharp edges

- **doctrina** owns the **model as a built artifact**: train / fine-tune it, evaluate it, serve it, operate it. The risk is a model that looks right offline and fails on live inputs.
- **fabius-scientia** owns the **scientific method over natural-science data** (hypotheses, omics/bio databases, reproducible analysis). A gene-expression study is scientia; serving a trained classifier is doctrina. Both share the reproducibility discipline; they don't share the concern.
- **fabius-cohors** owns the **agent** (LLM tools, orchestration, output contracts). doctrina owns the **model the agent calls** — its serving, its evaluation, its cost. An agent that calls a model: cohors owns the agent loop, doctrina owns whether the model is served well and scored honestly.
- **fabius-disciplina** owns the **engineering process** (plan → test → prove). doctrina's "prove" *is* an `eval`; it names the ML-specific version of that step and never drops below it.
- **AI/model security** (prompt injection, model/data supply chain, exfiltration) → **fabius-praesidium**. doctrina builds and serves; praesidium hardens.

All of it stands on `fabius-parcus`'s never-trim floor and YAGNI ladder: the smallest model, the smallest serving stack, the smallest training run that answers the question.

## 2. The lifecycle is a loop, and evaluation is its hinge

Run it in order, and never skip the hinge: **data → train / fine-tune → EVALUATE → serve → monitor → (back to data).**

- **Reach for the smallest rung first** (the YAGNI ladder for models): a prompt to an existing model → retrieval (RAG) over a prompt → a fine-tune → training from scratch. Most "we need a model" tasks are a prompt or a retrieval step, not a training run. Don't spin a GPU cluster for what a system prompt solves.
- **Fine-tune only when the cheaper rung provably fails** — you have the labeled data, the eval shows the gap, and the gap is *behavioral* (format, domain, style), not *knowledge* (which RAG fixes cheaper).

## 3. Evaluation is the load-bearing step — eval before you ship, eval to compare

A model claim without an eval is a vibe. The discipline is fabius's own benchmark posture (see the repo's `BENCHMARKS.md`), applied to every model decision:

- **A held-out, representative eval set** the model never trained on — the only thing that predicts production. Leakage from train into eval is the cardinal sin; it manufactures a number that doesn't survive contact with a user.
- **The metric matches the job**: classification → precision/recall/F1 at the operating threshold (accuracy lies on imbalance); generation/LLM → a task rubric scored by a **blind judge** (never told which system produced the answer) plus an objective signal (length, exact-match, latency) that can't be flattered.
- **Compare against a control, not just a baseline** — a cheaper model, last week's prompt, the previous checkpoint. "Better than nothing" is easy; "better than the thing it replaces" is the real test.
- **Make it a regression gate**: the eval runs in CI; a prompt or model change that drops the score fails the change. An eval you run once is a measurement; an eval that gates is a guarantee.

(LLM-as-judge is directional — its scores carry model-family priors; keep the objective signals as the hard floor and read the outputs. Same honest posture as fabius's own benchmarks.)

## 4. Serve lean — the smallest stack that meets the SLA

Inference is where the cost and the latency live. Match the serving to the load, don't over-build it:

- **A few calls** → the model's hosted API or a one-process load. **Real throughput** → a purpose-built server (vLLM-class): **PagedAttention** kills the memory fragmentation that caps batch size, continuous batching keeps the GPU full, and an **OpenAI-compatible** endpoint is a drop-in (no client rewrite).
- **Right-size before you scale out**: quantization (INT8/FP8/4-bit) and the smallest model that passes §3's eval beat a bigger GPU. Measure tokens/sec and tail latency (p95/p99), not just the average.
- **Match the hardware tier first** (§6) — picking the serving engine before knowing the GPU is how a deploy OOMs under load.

## 5. MLOps — track it or it didn't happen

A model you can't reproduce is a liability. The contract (MLflow-class, tool-agnostic):

- **Log every run**: params, metrics, the eval score, the data/version, the code commit, the artifact. A result you can't trace to its inputs is a rumor.
- **A model registry** for what's promotable: stage → production with the eval that justified it attached. Promotion is a decision with evidence, not a file copy.
- **Reproducibility is the floor**: pin versions (framework ↔ CUDA ↔ driver), seed where it matters, snapshot the dataset. Keys in env, never in a notebook or shell history (`fabius-praesidium`, `fabius-parcus`).

## 6. Resource-awareness before the tool

Compute-heavy work branches on hardware. Probe **GPU / VRAM / CPU / RAM / disk first**, then choose: the GPU tier sets the model size, the quantization, and the batch; the framework follows the accelerator (CUDA / ROCm / MPS / CPU). Picking the model or the trainer before knowing the machine is how a job OOMs at hour three — the same resource-first rule `fabius-scientia` applies to its pipelines.

## Boundaries

One concern per skill. Keep doctrina to the genuinely ML-engineering core and route the rest: natural-science data analysis and the hypothesis loop → `fabius-scientia`; the agent loop and tool wiring around a model → `fabius-cohors`; the general build/plan/debug process → `fabius-disciplina`; model/AI security and the model/data supply chain → `fabius-praesidium`; charting the eval results → `fabius-decor` (figura). Don't mirror a framework's whole API — encode the transferable decisions (which rung, which metric, how to serve, what to track); the depth is `references/`.

## References

- The serving recipes (vLLM-class throughput, quantization, OpenAI-compatible endpoints), the MLOps + experiment-tracking contract (runs, registry, reproducibility), the evaluation playbook (held-out sets, blind judges, regression gates), and the train-vs-fine-tune-vs-RAG decision ladder → `references/ml-engineering-playbook.md`.

**Live tier (optional).** The decision rules, the eval design, and the lifecycle are pure knowledge. *Running* the work needs the user's own compute and services: a **GPU** for serving/training, an MLflow (or equivalent) **tracking server**, a **model registry / hub**, and any hosted **inference API**. fabius bundles none — the full map is in [ARCHITECTURE.md](../../ARCHITECTURE.md) (*External connections*).

Pairs with: `fabius-disciplina` (the eval *is* the prove step — gate on it), `fabius-scientia` (shares the resource-first + reproducibility discipline; hands off when the task is natural-science data), `fabius-cohors` (owns the agent that calls the model doctrina serves), `fabius-praesidium` (hardens the model and its supply chain), `fabius-parcus` (the smallest model / stack / run that clears the bar). `stop fabius` drops the stance.
