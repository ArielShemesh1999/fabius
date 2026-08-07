# Fabius Doctrina — the ML-engineering playbook

The on-demand depth for `fabius-doctrina`: the rung ladder (do you even need to train?), the evaluation playbook, the serving recipes, and the MLOps contract. The SKILL.md is the stance; this is how you run the model lifecycle well. These are capabilities fabius **applies** by reaching for named ecosystem tools — fabius bundles no runtime; the optional live tier (GPU, tracking server, registry, inference API) routes to ARCHITECTURE.md external connections. Tool names and versions are a point-in-time snapshot (early 2026); re-verify before you depend on one.

Scout the data and the metric, strike the smallest model that clears the bar, prove it on held-out reality.

## 1. The rung ladder — most "we need a model" tasks aren't a training run

Climb from cheapest to most expensive and **stop at the first rung the eval clears**:

1. **Prompt an existing model.** Capability you can get from a system prompt + a good model is not a training problem. Try this first, always.
2. **Retrieval (RAG) over a prompt.** The gap is *knowledge* the model lacks (your docs, current facts)? Add retrieval, not weights. Cheaper, updatable, auditable — and it's the right fix for "the model doesn't know about X." (The agent/RAG wiring is `fabius-cohors`; doctrina owns the *retrieval-and-model* quality and its eval.)
3. **Fine-tune.** Only when the gap is *behavioral* (format adherence, domain tone, a narrow task the base model fumbles) and §2's eval proves the cheaper rungs fail. **Name the asset before you name the method:** labeled outputs → supervised fine-tuning; no labels but a programmatic checker (a unit test, a parser, an exact-match grader, a policy rule) → reinforcement learning; neither → you're still on rung 1 or 2. Both branches run LoRA before a full fine-tune — but LoRA is only cheap *and* equal if you configure it that way, and the library defaults don't.
    - **SFT.** Four conditions turn "most of the gain" into parity with a full fine-tune at roughly two-thirds the compute: apply the adapter to **all linear layers** (`target_modules="all-linear"`), never attention-only — attention-only underperforms even at a higher rank chosen to match the parameter count; give it **enough rank for the dataset** (~256 at post-training scale), because LoRA only falls behind once the data exceeds adapter capacity; set the **learning rate ~10× the full-fine-tune rate** (LoRA's 1/r scaling makes the optimum roughly rank-independent); and hold the **effective batch size under ~32**, which more rank does not fix. Run it the default way and it quietly loses — and you conclude the wrong thing about LoRA instead of about your config.
    - **RL from a verifiable reward.** When you can't write the right *answer* but can write the *checker*, policy-gradient training (GRPO-class, in TRL) optimizes against that checker directly and needs no labeled outputs at all. It also needs far less adapter capacity than SFT — **rank 1–32** against SFT's 256 — because an episode carries on the order of one bit of information regardless of model size. Reserve it for machine-checkable success: the moment a human has to read the output to score it, you're back to SFT plus an eval.
4. **Train from scratch.** Almost never the answer for an application. Reserve it for a genuinely novel architecture or a domain no pretrained model covers.

**Decision rule:** name the gap (knowledge vs behavior vs neither) before reaching for a GPU, then name the asset. A knowledge gap → RAG; a behavior gap with labeled data → SFT; a behavior gap with a checker instead of labels → RL; neither → it's a prompt. The most expensive mistake in ML engineering is training when a prompt would have done; the second is concluding you can't train because nobody labeled anything.

## 2. Evaluation — the load-bearing step, in detail

A model claim without an eval is a vibe. This is fabius's own benchmark discipline (`BENCHMARKS.md`) applied to every model decision.

**Build the eval set first.**
- **Held-out and representative** — sampled from the real input distribution, never seen in training. *Leakage* (any train/eval overlap) manufactures a number that dies in production; check for it explicitly (dedup by content hash, split by entity/time not at random when rows are correlated).
- **Sized to the decision** — a few dozen sharp cases beat thousands of easy ones. Include the hard, the adversarial, and the failure modes you've actually seen.

**Pick the metric that matches the job.**
- **Classification / retrieval** — precision, recall, F1 **at the operating threshold**; accuracy lies under class imbalance. For retrieval: recall@k, MRR, nDCG.
- **Generation / LLM** — a task rubric scored by a **blind judge** model (never told which arm produced the answer), plus an **objective signal** that can't be flattered: exact-match where applicable, length, latency, cost. The objective signal is the hard floor; the judge score is directional (it carries model-family priors — read the outputs yourself).
- **Calibration matters when a probability is consumed** — a model that says 0.9 should be right ~90% of the time; check reliability, not just rank.

**A judge score is a measurement with an unknown error rate — measure the error rate or don't quote the number.** Hold back a small **human-labeled calibration slice**, score it with both the humans and the judge, and correct the headline number with the resulting sensitivity/specificity instead of publishing the raw pass rate. This is not pedantry: the correction carries **1/J** in the judge's Youden index, so a merely-moderate judge doesn't blur a comparison, it can *flip* it — a published MMLU-Pro case landed on a **−0.330** gap with a tight interval where the true gap was **+0.048**. Two rules keep it honest. Calibrate **per comparison** — one calibration set shared across the models being compared is exactly where those sign reversals came from. And prefer a **PPI++**-style estimator (judge labels on everything, human labels on the slice) over a plain Rogan–Gladen correction, because it degrades gracefully as judge quality drops, which is where the naive correction blows up. Human labels are part of the judge pipeline; budget them.

**Compare against a control, not nothing.** The cheaper model, last week's prompt, the previous checkpoint. Beating "no model" is trivial; beating *the thing this replaces* is the test. Report the delta — **and its interval, because a delta without one is not a comparison.** Four cheap rules make it a real one. Quote the **standard error of the mean across questions** with every score. Use **clustered** standard errors when questions arrive in related groups (several items per document, per scenario, per seed), or you'll understate the noise several-fold. Run the comparison on **question-level paired differences**, never on two population means — the pairing cancels item difficulty, which is the variance that otherwise swamps the gap. Cut what's left by **resampling answers per question** rather than by buying more questions. Then do the **power** arithmetic *before* the run: an eval too small to resolve the effect you care about can't return a pass or a fail, only a coin flip with a decimal point.

**Gate on it.** The eval runs in CI; a prompt or weight change that drops the score fails the change. An eval you run once is a measurement; an eval that gates is a guarantee against silent regression. Gate on the *interval*, not the point estimate — a check that fires on unmeasured noise gets muted within a month, and then nothing is gated at all. (This is the model-tier sibling of `fabius-disciplina`'s prove step.)

## 3. Serving — the smallest stack that meets the SLA

Inference is where cost and latency live. Match the engine to the load:

- **Low volume / prototyping** → the model's hosted API, or a single-process load (`transformers` pipeline). Don't stand up a cluster to serve ten requests.
- **Real throughput** → a purpose-built inference server (**vLLM**-class): **PagedAttention** removes the KV-cache fragmentation that caps batch size; **continuous batching** keeps the GPU saturated across requests of different lengths; an **OpenAI-compatible** endpoint is a drop-in so clients don't change. (ecosystem: vLLM — NVIDIA/AMD/TPU/Apple-silicon backends.)
- **Right-size before scaling out** — quantization (FP8/INT8/4-bit) and the **smallest model that passes §2** beat renting a bigger GPU. A 7B that clears the bar serves cheaper and faster than a 70B that clears it by more than the bar needs. "4-bit" is not a specification: name the format, check it against the accelerator's compute capability (§5), and re-run §2 on the *quantized* weights — quantization is a model change. The producing toolchain and the per-format hardware floor are in `ml-toolkit.md` (*Quantize*).
- **Measure the tail, not the mean** — tokens/sec, and **p95/p99 latency** under realistic concurrency. The average hides the request that times out.

**Decision rule:** serving engine follows the hardware (§5) and the SLA, never the hype. Throughput need + a GPU → vLLM-class; a handful of calls → the API. Don't build the throughput stack until the throughput exists.

**Serving via someone else's API — the tier you don't host.** Most LLM apps never stand up a GPU: their whole serving story is a call to a hosted model from behind a platform function. That tier is its own engineering problem, not a non-decision: cost and latency are shaped by the request you send rather than by a GPU you can resize, and none of its failure modes show up in an offline eval.

- **A reasoning model bills its thoughts against your output ceiling.** Rolling aliases (`*-latest` and friends) usually resolve to thinking models, and their thought tokens count toward the same cap as the answer (`max_tokens` / `maxOutputTokens` / `max_completion_tokens`). A "safe" 800-token cap then returns replies cut mid-word, or a candidate with no text at all — **non-deterministically**, because an open-ended greeting thinks longer than a retrieval question. Set the ceiling several times the expected answer and let the system prompt shape length: the cap bounds abuse, it does not control length. A thinking-budget parameter is not universally accepted — some aliases reject the request outright, so verify it against the exact model id before shipping it.
- **Read the stop reason every turn.** A truncation or filter stop (`finish_reason` / `stop_reason` / `finishReason` = length · max_tokens · safety · recitation) is an amputated answer posing as a complete one. A client that reads only the text ships the truncation to the user and logs it as a success.
- **Time-to-first-token can outlive the platform's deadline.** Reasoning pushes first-token latency past the gateway timeout on a perfectly healthy turn, and awaiting upstream *before* constructing the response makes the function time out instead of stream. Return the streaming response **immediately** and start the upstream fetch inside the stream body; map upstream HTTP failures to in-body error lines (the status is already sent); heartbeat a keep-alive line every ~10s (an empty object on an NDJSON stream, a comment frame on SSE) so a client watchdog doesn't kill a thinking turn. Add one silent retry on a wholly-empty turn, and a client-side stall watchdog with a resend affordance.

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
