# Fabius Doctrina — the ML-engineering playbook

The on-demand depth for `fabius-doctrina`: the rung ladder (do you even need to train?), the evaluation playbook, the serving recipes, and the MLOps contract. The SKILL.md is the stance; this is how you run the model lifecycle well. These are capabilities fabius **applies** by reaching for named ecosystem tools — fabius bundles no runtime; the optional live tier (GPU, tracking server, registry, inference API) routes to ARCHITECTURE.md external connections. Tool names and versions are a point-in-time snapshot (early 2026); re-verify before you depend on one.

Scout the data and the metric, strike the smallest model that clears the bar, prove it on held-out reality.

## 1. The rung ladder — most "we need a model" tasks aren't a training run

Climb from cheapest to most expensive and **stop at the first rung the eval clears**:

1. **Prompt an existing model.** Capability you can get from a system prompt + a good model is not a training problem. Try this first, always.
2. **Retrieval (RAG) over a prompt.** The gap is *knowledge* the model lacks (your docs, current facts)? Add retrieval, not weights. Cheaper, updatable, auditable — and it's the right fix for "the model doesn't know about X." (The agent/RAG wiring is `fabius-cohors`; doctrina owns the *retrieval-and-model* quality and its eval.)
3. **Fine-tune.** Only when the gap is *behavioral* (format adherence, domain tone, a narrow task the base model fumbles), you have labeled data, and §2's eval proves the cheaper rungs fail. Prefer parameter-efficient fine-tuning (LoRA/QLoRA) before a full fine-tune — a fraction of the compute for most of the gain.
4. **Train from scratch.** Almost never the answer for an application. Reserve it for a genuinely novel architecture or a domain no pretrained model covers.

**Decision rule:** name the gap (knowledge vs behavior vs neither) before reaching for a GPU. A knowledge gap → RAG; a behavior gap with data → fine-tune; neither → it's a prompt. The most expensive mistake in ML engineering is training when a prompt would have done.

## 2. Evaluation — the load-bearing step, in detail

A model claim without an eval is a vibe. This is fabius's own benchmark discipline (`BENCHMARKS.md`) applied to every model decision.

**Build the eval set first.**
- **Held-out and representative** — sampled from the real input distribution, never seen in training. *Leakage* (any train/eval overlap) manufactures a number that dies in production; check for it explicitly (dedup by content hash, split by entity/time not at random when rows are correlated).
- **Sized to the decision** — a few dozen sharp cases beat thousands of easy ones. Include the hard, the adversarial, and the failure modes you've actually seen.

**Pick the metric that matches the job.**
- **Classification / retrieval** — precision, recall, F1 **at the operating threshold**; accuracy lies under class imbalance. For retrieval: recall@k, MRR, nDCG.
- **Generation / LLM** — a task rubric scored by a **blind judge** model (never told which arm produced the answer), plus an **objective signal** that can't be flattered: exact-match where applicable, length, latency, cost. The objective signal is the hard floor; the judge score is directional (it carries model-family priors — read the outputs yourself).
- **Calibration matters when a probability is consumed** — a model that says 0.9 should be right ~90% of the time; check reliability, not just rank.

**Compare against a control, not nothing.** The cheaper model, last week's prompt, the previous checkpoint. Beating "no model" is trivial; beating *the thing this replaces* is the test. Report the delta.

**Gate on it.** The eval runs in CI; a prompt or weight change that drops the score fails the change. An eval you run once is a measurement; an eval that gates is a guarantee against silent regression. (This is the model-tier sibling of `fabius-disciplina`'s prove step.)

## 3. Serving — the smallest stack that meets the SLA

Inference is where cost and latency live. Match the engine to the load:

- **Low volume / prototyping** → the model's hosted API, or a single-process load (`transformers` pipeline). Don't stand up a cluster to serve ten requests.
- **Real throughput** → a purpose-built inference server (**vLLM**-class): **PagedAttention** removes the KV-cache fragmentation that caps batch size; **continuous batching** keeps the GPU saturated across requests of different lengths; an **OpenAI-compatible** endpoint is a drop-in so clients don't change. (ecosystem: vLLM — NVIDIA/AMD/TPU/Apple-silicon backends.)
- **Right-size before scaling out** — quantization (FP8/INT8/4-bit) and the **smallest model that passes §2** beat renting a bigger GPU. A 7B that clears the bar serves cheaper and faster than a 70B that clears it by more than the bar needs.
- **Measure the tail, not the mean** — tokens/sec, and **p95/p99 latency** under realistic concurrency. The average hides the request that times out.

**Decision rule:** serving engine follows the hardware (§5) and the SLA, never the hype. Throughput need + a GPU → vLLM-class; a handful of calls → the API. Don't build the throughput stack until the throughput exists.

## 4. MLOps — track it or it didn't happen

A model you can't reproduce is a liability, not an asset. The contract (tool-agnostic; MLflow is the worked example — 60M+ monthly installs, autolog for common frameworks, an MCP server in-repo):

- **Log every run** — params, metrics, the **eval score (§2)**, the dataset version, the **code commit**, and the output artifact. A result you can't trace back to its exact inputs is a rumor, not a finding.
- **A model registry** — the gate from `staging` to `production` carries the eval that justified the promotion. Promotion is a decision with attached evidence, not a file copy.
- **Reproducibility is the floor** — pin the stack (framework ↔ CUDA/ROCm ↔ driver), seed where determinism matters, snapshot/version the dataset, isolate dependencies. Secrets in env / a manager, **never** in a notebook, script, or shell history (`fabius-praesidium`, `fabius-parcus`).
- **Monitor after deploy** — production input drifts from your eval set over time; watch input distribution, output distribution, and the live metric. A model decays silently; the monitor is how you notice before the user does. Drift past a threshold → back to §1 with fresh data.

## 5. Resource-awareness before the tool

Compute-heavy work branches on hardware — probe it **first**:

- **GPU / VRAM** sets the model size, the quantization, and the max batch. A 24 GB card and a 7B at FP8 is a different plan than an 80 GB card and a 70B.
- **Accelerator** sets the framework path: CUDA (NVIDIA) / ROCm (AMD) / MPS (Apple) / CPU fallback. The serving engine and the training loop follow the accelerator, not the other way round.
- **CPU / RAM / disk** set the data-loading and preprocessing tier (in-memory vs streaming/sharded).

Picking the model, the trainer, or the serving engine before knowing the machine is how a job OOMs at hour three — the same resource-first rule `fabius-scientia` applies to its pipelines.

## 6. Boundaries — what doctrina hands off

- **Natural-science data** (omics, bio, chemistry, the hypothesis loop) → `fabius-scientia`. Shared discipline (resource-first, reproducibility), different concern.
- **The agent loop** that calls the model (tools, orchestration, output contracts) → `fabius-cohors`. doctrina owns the model's serving + eval + cost; cohors owns the agent.
- **AI/model security** — prompt-injection defense, model/data supply-chain integrity (a poisoned checkpoint or dataset is a real attack), exfiltration via a model → `fabius-praesidium`.
- **Charting the eval/metric results** → `fabius-decor` (figura — data-ink first).
- **The general build/plan/debug loop** around all of it → `fabius-disciplina`.

---

Drawn from ecosystem tools catalogued in the ARGAZ directory of strong AI tooling (vLLM, MLflow, the eval-harness pattern) — re-expressed in fabius's own voice as *how to engineer, serve, and prove a model well*, crediting each tool by name. fabius bundles no runtime; the optional live tier is in [ARCHITECTURE.md](../../../ARCHITECTURE.md) (*External connections*).
