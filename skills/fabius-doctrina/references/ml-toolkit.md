# Fabius Doctrina — the ML/LLM engineering toolkit

Loaded on demand by `fabius-doctrina`. The current **best-in-class stack** (2026) for the model lifecycle — **serve · fine-tune · evaluate · track · cut cost** — license-verified, with the recently-*declined* tools flagged honestly so fabius doesn't build on a dead dependency. One law across the model half: **the HF *library* is Apache, but the *weights* carry their own license** — many checkpoints (diffusion, Llama-derived, gated) are non-commercial; check the model card, and prefer Apache-weight models (Qwen3) for a shippable product.

## Serve / infer

| Engine | License | Reach for it when |
|---|---|---|
| **vLLM** *(default)* | Apache-2.0 | Production GPU serving — PagedAttention, continuous batching, tensor/pipeline parallel, broadest model coverage, OpenAI-compatible. |
| **SGLang** | Apache-2.0 | Prefix-heavy / multi-turn / RAG / structured-output where **RadixAttention** KV-prefix reuse dominates throughput. Pin versions (fast churn). |
| **TensorRT-LLM** | Apache-2.0 | NVIDIA-locked, need the perf ceiling — accept per-model engine compilation. **LMDeploy** (Apache-2.0) is a lighter alternative (TurboMind + 4-bit). |
| **llama.cpp** | MIT | Local/edge/on-device over GGUF — CPU, Apple Silicon, consumer GPU, no Python/CUDA; the substrate under Ollama/LM Studio. More than a CLI: **`llama-server`** is an **OpenAI-compatible endpoint** (drop-in for the serve tier on a laptop/CPU box), and it also does **embeddings + reranking** (feeds `fabius-archivum`'s RAG), **multimodal/vision** (`mtmd`), and **GBNF grammar-constrained** JSON/schema output. Repo `ggml-org/llama.cpp`; continuous-build tags (no semver) — **pin a build**; low-bit GGUF quant trades quality — validate output. |
| **Ollama** | MIT | Fastest local dev endpoint (wraps llama.cpp, OpenAI-compatible). A dev convenience — throughput lags vLLM ~9× under concurrency; graduate to vLLM under load. |

> **Flagged:** **TGI** (HF text-generation-inference) was **archived read-only Mar 2026** — its maintainers redirect to vLLM/SGLang. Don't build new systems on it.

## Fine-tune

The HF training stack — **transformers** + **accelerate** (distributed/mixed-precision) + **datasets** (streaming) — is the foundation; **DeepSpeed** (Apache-2.0) is the distinct ZeRO scale-out engine under most large fine-tunes.

| Tool | License | Note |
|---|---|---|
| **TRL** | Apache-2.0 | HF post-training — SFT, DPO, GRPO/PPO, reward modeling. The fine-tune backbone. |
| **PEFT** | Apache-2.0 | LoRA / QLoRA / adapters — fine-tune big models on modest hardware, ship swappable adapters. |
| **Unsloth** | Apache-2.0 (core) | ~2× faster, lower-VRAM LoRA/QLoRA (Triton kernels), drop-in for TRL/PEFT. *Studio UI / CLI are AGPL-3.0; multi-GPU historically Pro-gated.* |
| **Axolotl** | Apache-2.0 | Fine-tune-as-**YAML** — reproducible SFT/DPO/GRPO across model families. |

> **Flagged:** **torchtune** (Meta) **halted active development Jul 2025** — prefer TRL/Axolotl/Unsloth.

## Evaluate

| Tool | License | Note |
|---|---|---|
| **lm-evaluation-harness** (EleutherAI) | MIT | De-facto capability benchmarks (MMLU/GSM8K/GPQA/IFEval). **Pin the version + few-shot config** — scores are format-sensitive. (**HELM** is the heavier holistic alt.) |
| **lighteval** (HF) | MIT | Lightweight evals across backends (accelerate/vLLM/HF endpoints) — the modern HF post-leaderboard tool. |
| **promptfoo** | MIT | Prompt regression tests + model comparison + red-teaming, in CI. The *eval-my-prompts* tool. |
| **DeepEval** | Apache-2.0 | Pytest-style LLM evals, 40+ metrics (G-Eval, hallucination, RAG, safety) — regression gates that fail CI. (Confident AI dashboard is separate SaaS.) |
| **Ragas** | Apache-2.0 | RAG-specific metrics (faithfulness, context precision/recall). Org is now **`vibrantlabsai`** (old URL redirects); LLM-judge metrics need a capable judge. |
| **Langfuse** | MIT (core) | Open **LLM observability / tracing** + prompt management, self-hostable — the per-call agent-trace layer MLflow/W&B don't natively cover. |

## Track (MLOps)

- **MLflow** (Apache-2.0) — self-hostable experiment tracking + model registry + (v3) GenAI eval/tracing. The OSS default.
- **ClearML** (Apache-2.0) — self-host-everything: tracking + orchestration + data/pipeline management.
- **Weights & Biases** — premium hosted tracking; the **`wandb` client is MIT** but the *platform* is proprietary SaaS (self-host needs a commercial license). MLflow/ClearML are the fully-OSS alternatives.

## Route & rank

- **LiteLLM** (MIT) — unified OpenAI-compatible gateway across 100+ providers (routing, cost tracking, virtual keys, guardrails) — fronts vLLM/SGLang/hosted models behind one endpoint.
- **Arena** (formerly LMArena / LMSYS Chatbot Arena, now **arena.ai**) — live human-preference Elo. Top-tier CIs overlap → treat the top ~10 as tied and decide on fit/TCO. *(HF's Open LLM Leaderboard was retired 2025.)* Function-calling → BFCL (see `fabius-cohors`).
- **Model to run end-to-end permissively:** **Qwen/Qwen3-8B** (Apache-2.0) — a genuinely commercial-safe open-weights model through the serve→fine-tune→eval stack, unlike Llama's community license.

## Operate — the dashboard over a served model

- **Open WebUI** (`open-webui/open-webui`) · ⚠️ **Open WebUI License** (BSD-3 + branding-protection clause) · ~145k★ · v0.10.2 — the **self-hosted chat front-end + operator dashboard** over any OpenAI-compatible or Ollama endpoint: multi-model chat, built-in RAG (9 vector DBs), web search, granular **RBAC**, and a Filters/Actions/Pipes/**Tools** plugin system for tool-calling. The human-facing UI to put in front of a doctrina-served model; fully self-hosted, so chat + documents stay on your infra. **License caveat (not OSI since v0.6.6):** you may **not** alter/remove/replace the "Open WebUI" **branding** — doing so is a "material breach" — **unless** the deployment is **≤50 users / 30 days**, you hold an enterprise license, or you have written permission. Fine to run as-is; **you cannot white-label it into a >50-user product** without paying. (Lighter alternatives with no branding lock: **LibreChat** — MIT; **Lobe Chat** — MIT/Apache.)

## Local speech — the ASR / TTS model tier

doctrina owns the speech *models* two other skills consume: `fabius-archivum`'s meeting capture (Meetily) and `fabius-cohors`'s agent voice (Voicebox). doctrina owns the *model*; those skills own the *use*.

- **ASR (speech→text):** **whisper.cpp** (`ggml-org/whisper.cpp`, **MIT**) — the GGUF/ggml sibling of llama.cpp: on-device Whisper for CPU/Apple-Silicon (what Meetily runs); **faster-whisper** (MIT, CTranslate2) for GPU throughput; NVIDIA **Parakeet** (via NeMo) for the fastest live tier — check the NeMo model card's terms before shipping.
- **TTS (text→speech):** permissive-weight open engines — **Kokoro** (Apache-2.0, tiny/fast), **Piper** (MIT, the local default OpenMontage uses), **Chatterbox** (MIT, Resemble AI) — but **verify each weight's license** (many voice models are non-commercial or research-only), and treat voice-cloning as a **consent/impersonation risk** to gate (`fabius-praesidium`), sealable for provenance (`fabius-catena`).

## Cut input-token cost

- **pxpipe** (`teamchong/pxpipe`, npm **`pxpipe-proxy`**) · **MIT** · ⭐4k+ · v0.7.1 (Jul 2026) *(TypeScript; verified 2026-07-06)* — a local proxy that **renders bulky, stable context — system prompt, tool docs, older history — as PNG images**, so those blocks are billed on the vision channel's pixel pricing instead of per-text-token. Point a client at it with `ANTHROPIC_BASE_URL=http://127.0.0.1:47821` (`npx pxpipe-proxy`); recent turns stay text, and a built-in **profitability gate** only images a block where the token math actually wins. **Honest caveats — this is a sharp *situational* optimization, not a free lunch:** the saving is **pricing-dependent** (it arbitrages a vision-vs-text token economics the provider can change) and **fidelity-bounded** (the model must read the rendered image as accurately as the text — verify on *your* prompts before trusting it in production, `fabius-disciplina`'s prove rule). Best on token-heavy, mostly-static context; **measure the events log (`~/.pxpipe/events.jsonl`), don't assume.** Aligned with `fabius-parcus`'s fewer-tokens ethos — the lean move applied at the API boundary.

## Pairs with

`fabius-doctrina` (the lifecycle playbook), `fabius-cohors` (doctrina owns the *model*; cohors owns the *agent* that calls it — including the TTS/STT tier behind an agent's voice), `fabius-archivum` (the RAG tier a model serves — Ragas evaluates it; the local ASR tier behind meeting capture), `fabius-parcus` (token-cost reduction is the lean stance at the API boundary — pxpipe above), `fabius-praesidium` (a non-commercial or gated weight — or a branding-locked UI — shipping in a paid product is a licensing risk to flag; voice-clone consent), and `fabius-catena` (seal/watermark generated audio for provenance).
