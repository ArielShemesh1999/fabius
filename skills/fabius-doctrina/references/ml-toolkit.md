# Fabius Doctrina — the ML/LLM engineering toolkit

Loaded on demand by `fabius-doctrina`. The current **best-in-class stack** (2026) for the model lifecycle — **serve · fine-tune · evaluate · track · cut cost** — license-verified, with the recently-*declined* tools flagged honestly so fabius doesn't build on a dead dependency. One law across the model half: **the HF *library* is Apache, but the *weights* carry their own license** — many checkpoints (diffusion, Llama-derived, gated) are non-commercial; check the model card, and prefer Apache-weight models (the Qwen3.5 / Qwen3.6 line) for a shippable product.

## Serve / infer

| Engine | License | Reach for it when |
|---|---|---|
| **vLLM** *(default)* | Apache-2.0 | Production GPU serving — PagedAttention, continuous batching, tensor/pipeline parallel, broadest model coverage, OpenAI-compatible. |
| **SGLang** | Apache-2.0 | Prefix-heavy / multi-turn / RAG / structured-output where **RadixAttention** KV-prefix reuse dominates throughput. Pin versions (fast churn). |
| **TensorRT-LLM** | Apache-2.0 | NVIDIA-locked, need the perf ceiling — accept per-model engine compilation. **LMDeploy** (Apache-2.0) is a lighter alternative (TurboMind + 4-bit). |
| **llama.cpp** | MIT | Local/edge/on-device over GGUF — CPU, Apple Silicon, consumer GPU, no Python/CUDA; the substrate under Ollama/LM Studio. More than a CLI: **`llama-server`** is an **OpenAI-compatible endpoint** (drop-in for the serve tier on a laptop/CPU box), and it also does **embeddings + reranking** (feeds `fabius-archivum`'s RAG), **multimodal/vision** (`mtmd`), and **GBNF grammar-constrained** JSON/schema output. Repo `ggml-org/llama.cpp`; continuous-build tags (no semver) — **pin a build**; low-bit GGUF quant trades quality — validate output. |
| **Ollama** | MIT | Fastest local dev endpoint (wraps llama.cpp, OpenAI-compatible). A dev convenience — throughput lags vLLM ~9× under concurrency; graduate to vLLM under load. |

> **Flagged:** **TGI** (HF text-generation-inference) was **archived read-only Mar 2026** — its maintainers redirect to vLLM/SGLang. Don't build new systems on it.

## Quantize — a checkpoint, not an adjective

"Quantize it" stays a verb until something emits weights. **llm-compressor** (`vllm-project/llm-compressor`, **Apache-2.0**) is the vLLM-native producer: **W8A8** (INT8 and FP8), **W4A16 / W8A16**, **W4AFP8**, the microscale float formats **NVFP4 / MXFP4 / MXFP8**, and FP8/NVFP4 **KV-cache** quantization — via simple PTQ, GPTQ, AWQ, SmoothQuant, AutoRound or rotation methods (SpinQuant, QuIP). It writes `compressed-tensors` checkpoints that load straight into vLLM, so the quantizer and the server share one format instead of one converting for the other.

**The format follows the silicon, not the fashion** — the NVIDIA compute-capability floor *is* the decision:

| Format | Runs from | Reach for it when |
|---|---|---|
| **W4A16 / W8A16**, **W8A8-INT8** | **7.5** (Turing) | The oldest card in the fleet has to serve it; memory-bound, weight-only. |
| **W8A8-FP8** | **8.9** (Ada Lovelace) | The honest default on Ada and up — float semantics, native tensor cores, small accuracy cost. |
| **W4AFP8** | **9.0** (Hopper) | Hopper, and the weights are the memory wall. |
| **NVFP4 / MXFP4 / MXFP8** | **10.0** (Blackwell) | Blackwell, where the FP4 math is native. NVFP4 holds accuracy via two-level micro-block scaling with high-precision scales; MXFP4 is the alternative when you have **no calibration data**, at possibly lower round-to-nearest accuracy. |
| **NVFP4A16 / MXFP4A16 / MXFP8A16** | *unstated upstream* | Weight-only microscale variants — a memory win with activations left at 16-bit. The vendor documents the compute floor for the **full** NVFP4/MXFP4/MXFP8 schemes as Blackwell (SM100)+ and does not publish one for the A16 forms, so measure on your own silicon before planning capacity around them. |

Below the floor, a low-bit format is a memory win and **not** a compute win — quoting FP4 throughput on hardware with no FP4 tensor core is how a capacity plan goes wrong. Pick the lowest format the accelerator natively executes, then stop. **Quantization is a model change:** re-run the held-out eval on the *quantized* weights, never on the BF16 parent — low-bit formats lose accuracy unevenly across tasks, so an aggregate score hides where it went.

> **Flagged:** **sparse compression (including 2:4 sparsity) is no longer supported** in llm-compressor — dropped for lack of hardware support and user interest. Don't plan a serving stack around it.

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
| **lighteval** (HF) | MIT | Lightweight evals across backends (accelerate/vLLM/SGLang/LiteLLM/HF endpoints) — the modern HF post-leaderboard tool. Its `lighteval eval` entrypoint now names **inspect-ai** the *preferred* backend, so the two compose rather than compete. |
| **Inspect AI** (`UKGovernmentBEIS/inspect_ai`) | MIT | The **agentic / sandboxed** eval framework — UK AI Security Institute + Meridian Labs. Solvers, scorers, model-graded rubrics, a built-in ReAct agent and multi-agent primitives, human baselining, task sandboxes (Docker / Kubernetes / Modal / Proxmox / Vagrant), 200+ prebuilt evals. Reach for it when the unit under test is a **trajectory** — tools called, code executed, multi-turn state — rather than a prompt/completion pair; it is what makes the `expected_tools` doctrine below executable, because the sandbox gives the agent something real to act on and the scorer sees the path, not just the prose. |
| **promptfoo** | MIT | Prompt regression tests + model comparison + red-teaming, in CI. The *eval-my-prompts* tool. |
| **DeepEval** | Apache-2.0 | Pytest-style LLM evals, 40+ metrics (G-Eval, hallucination, RAG, safety) — regression gates that fail CI. (Confident AI dashboard is separate SaaS.) |
| **Ragas** | Apache-2.0 | RAG-specific metrics (faithfulness, context precision/recall). Org is now **`vibrantlabsai`** (old URL redirects); LLM-judge metrics need a capable judge. |
| **Langfuse** | MIT (core) | Open **LLM observability / tracing** + prompt management, self-hostable — the per-call agent-trace layer MLflow/W&B don't natively cover. |

**Assert on the tool trajectory, not the answer text.** For an agent, the first thing that regresses is the **tool path**, and text scoring is blind to it: an agent that quietly stops calling `recall` and starts answering from parametric memory still emits a fluent, plausible, largely-correct paragraph — the score barely moves while the grounding is gone. So make the tool sequence an assertion of its own: declare `expected_tools` per case with **all-of** (every named tool must appear in the trajectory) and **any-of** (at least one of a set must) semantics, and fail the case on the path independent of the prose. That is the eval that catches confabulation the day it starts, rather than the week the complaints arrive. The path is checkable; "is this answer grounded" is a judgment call you'd otherwise pay a judge model to get wrong.

**Run it against the REAL entrypoint, inside a transaction that rolls back.** An eval that calls a reimplementation of the production path tests the reimplementation. Call the **shipped** entrypoint — the same function the app calls — and buy the cleanup from the database instead of from fixture code: open an **outer transaction**, `begin_nested()` for the savepoint, attach a listener that **restarts the savepoint** whenever the code under test commits (its `COMMIT` lands on the savepoint; the outer transaction never sees it, so production code that manages its own transactions runs unmodified), and **roll back unconditionally** in teardown. The agent writes real rows and takes real state transitions; nothing survives the test. Production fidelity at zero cleanup cost — and no `if TESTING:` branch in the product, which is the fixture pattern's real bill.

**Ship a real control arm** — the same task set with the skill/tool/prompt under test removed — or the number means nothing: "94% pass" describes the task set's difficulty until a baseline says what the treatment bought. **The caveat that voids the arm:** the treatment must exercise the **production** path. A cautionary case from the wild — GitNexus's eval enriches the grep **results**, while its shipped hook enriches the **pattern** *pre-call*. The arm billed as "mirroring production" tests a different mechanism than the one that ships, so its delta measures the harness, not the product, and the A/B is clean, well-run, and about nothing. Before trusting a control arm, verify the treatment arm calls what the *user* calls.

## Track (MLOps)

- **MLflow** (Apache-2.0) — self-hostable experiment tracking + model registry + (v3) GenAI eval/tracing. The OSS default.
- **ClearML** (Apache-2.0) — self-host-everything: tracking + orchestration + data/pipeline management.
- **Weights & Biases** — premium hosted tracking; the **`wandb` client is MIT** but the *platform* is proprietary SaaS (self-host needs a commercial license). MLflow/ClearML are the fully-OSS alternatives.

## Route & rank

- **LiteLLM** (MIT) — unified OpenAI-compatible gateway across 100+ providers (routing, cost tracking, virtual keys, guardrails) — fronts vLLM/SGLang/hosted models behind one endpoint.
- **Arena** (formerly LMArena / LMSYS Chatbot Arena, now **arena.ai**) — live human-preference Elo. Top-tier CIs overlap → treat the top ~10 as tied and decide on fit/TCO. *(HF's Open LLM Leaderboard was retired 2025.)* Function-calling → BFCL (see `fabius-cohors`).
- **Model to run end-to-end permissively:** **`Qwen/Qwen3.5-9B`** (Apache-2.0) — a genuinely commercial-safe open-weights model through the serve→fine-tune→eval stack, unlike Llama's community license. At the ~9B tier it carries a 262,144-token native context (RoPE-extensible toward ~1M) and a vision encoder. Two Apache-2.0 generations have landed since the Qwen3 line — **Qwen3.5** (2026, nine sizes from 0.8B to 397B-A17B) and **Qwen3.6** (Apr 2026, 27B dense and 35B-A3B, tuned for agentic coding and repo-level reasoning; no small tier yet) — so **pick the tier first, then take the newest generation that has one**. The license law is the durable part; a model id is a snapshot — re-read the card before you build on it.

## Operate — the dashboard over a served model

- **Open WebUI** (`open-webui/open-webui`) · ⚠️ **Open WebUI License** (BSD-3 + branding-protection clause) · ~145k★ · v0.10.2 — the **self-hosted chat front-end + operator dashboard** over any OpenAI-compatible or Ollama endpoint: multi-model chat, built-in RAG (9 vector DBs), web search, granular **RBAC**, and a Filters/Actions/Pipes/**Tools** plugin system for tool-calling. The human-facing UI to put in front of a doctrina-served model; fully self-hosted, so chat + documents stay on your infra. **License caveat (not OSI since v0.6.6):** you may **not** alter/remove/replace the "Open WebUI" **branding** — doing so is a "material breach" — **unless** the deployment is **≤50 users / 30 days**, you hold an enterprise license, or you have written permission. Fine to run as-is; **you cannot white-label it into a >50-user product** without paying. (Lighter alternatives with no branding lock: **LibreChat** — MIT; **Lobe Chat** — MIT/Apache.)

## Local speech — the ASR / TTS model tier

doctrina owns the speech *models* two other skills consume: `fabius-archivum`'s meeting capture (Meetily) and `fabius-cohors`'s agent voice (Voicebox). doctrina owns the *model*; those skills own the *use*.

- **ASR (speech→text):** **whisper.cpp** (`ggml-org/whisper.cpp`, **MIT**) — the GGUF/ggml sibling of llama.cpp: on-device Whisper for CPU/Apple-Silicon (what Meetily runs); **faster-whisper** (MIT, CTranslate2) for GPU throughput; NVIDIA **Parakeet** (via NeMo) for the fastest live tier — check the NeMo model card's terms before shipping.
- **ASR, the hosted-edge rung:** **`@cf/openai/whisper-large-v3-turbo`** on **Workers AI** — base64 audio in, transcript out, one binding, no GPU, no install, no weight download. Two properties earn it the rung between on-device whisper.cpp and a hosted ASR SaaS: it **auto-detects the language** (no hint to pass — the whole game for mixed Hebrew/English speech, where the hint is exactly what the caller can't know), and it prices at **$0.00051 per audio-minute** *(listed price — re-check before quoting it in a plan)*. Keep the two licenses apart: the **model is MIT** (OpenAI's Whisper weights), the **delivery is Cloudflare's metered platform**. Permissive weights don't make the endpoint free — that's the same weights-vs-service split as this file's opening law, one layer out.

**The decision rule, plainly:**

| | **Web Speech** (`SpeechRecognition`) | **Whisper** (hosted or local) |
|---|---|---|
| Cost | **free** | **metered** ($0.00051/min on Workers AI) |
| Latency | **instant, live-interim** — partial text while the user is still talking | needs the finished clip |
| Text quality | **unpunctuated**, lowercase run-on | **punctuated**, cased |
| Language | must be declared up front | **auto-detected** |
| Reach | **Chrome in practice** (Firefox doesn't ship it; Safari's is partial) | **everywhere** — it's an HTTP call |

Live-feel dictation in Chrome → **Web Speech + a polish pass** (`fabius-cohors` owns that wiring and the never-lose-words fallback; doctrina owns the fast-tier model behind the pass). Must work on Safari/Firefox, or must handle a language the caller can't predict → **Whisper**, and pay for it.

- **TTS (text→speech):** permissive-weight open engines — **Kokoro** (Apache-2.0, tiny/fast), **Piper** (MIT, the local default OpenMontage uses), **Chatterbox** (MIT, Resemble AI) — but **verify each weight's license** (many voice models are non-commercial or research-only), and treat voice-cloning as a **consent/impersonation risk** to gate (`fabius-praesidium`), sealable for provenance (`fabius-catena`).

## Cut input-token cost

- **pxpipe** (`teamchong/pxpipe`, npm **`pxpipe-proxy`**) · **MIT** · ⭐4k+ · v0.7.1 (Jul 2026) *(TypeScript; verified 2026-07-06)* — a local proxy that **renders bulky, stable context — system prompt, tool docs, older history — as PNG images**, so those blocks are billed on the vision channel's pixel pricing instead of per-text-token. Point a client at it with `ANTHROPIC_BASE_URL=http://127.0.0.1:47821` (`npx pxpipe-proxy`); recent turns stay text, and a built-in **profitability gate** only images a block where the token math actually wins. **Honest caveats — this is a sharp *situational* optimization, not a free lunch:** the saving is **pricing-dependent** (it arbitrages a vision-vs-text token economics the provider can change) and **fidelity-bounded** (the model must read the rendered image as accurately as the text — verify on *your* prompts before trusting it in production, `fabius-disciplina`'s prove rule). Best on token-heavy, mostly-static context; **measure the events log (`~/.pxpipe/events.jsonl`), don't assume.** Aligned with `fabius-parcus`'s fewer-tokens ethos — the lean move applied at the API boundary.

## Pairs with

`fabius-doctrina` (the lifecycle playbook), `fabius-cohors` (doctrina owns the *model*; cohors owns the *agent* that calls it — including the TTS/STT tier behind an agent's voice), `fabius-archivum` (the RAG tier a model serves — Ragas evaluates it; the local ASR tier behind meeting capture), `fabius-parcus` (token-cost reduction is the lean stance at the API boundary — pxpipe above), `fabius-praesidium` (a non-commercial or gated weight — or a branding-locked UI — shipping in a paid product is a licensing risk to flag; voice-clone consent), and `fabius-catena` (seal/watermark generated audio for provenance).
