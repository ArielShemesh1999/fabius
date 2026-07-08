# Fabius Cohors — the agent-framework & tool-caller map

Loaded on demand by `fabius-cohors`. The skill owns the *definition schema* and the five orchestration patterns; this is the current **best-in-class stack** (2026) to build them on — the frameworks that define/orchestrate agents, the eval that picks the tool-caller, and the open **models** to put behind the action layer. One license law dominates the model half: **a strong open tool-caller's HF tag often lies.** Most (Hermes, Functionary, watt-tool, xLAM-70B) are **Llama fine-tunes** — the *Llama Community License* (attribution "Built with Llama", 700M-MAU clause, no training-other-models) governs the weights regardless of an "Apache/MIT" tag on the repo. For a sellable product, prefer genuinely permissive backbones.

## Frameworks — pick by orchestration pattern

| Framework | License | Maps to cohors pattern · reach for it when |
|---|---|---|
| **LangGraph** | MIT | Graph/state-machine with durable checkpoints + HITL — explicit state, branching, resumable multi-step. (LangSmith obs is separate paid SaaS.) |
| **OpenAI Agents SDK** | MIT | **Swarm / handoff** — minimal provider-agnostic loop (100+ LLMs), handoffs + agent-as-tool + guardrails + tracing. TS port exists. Successor to "Swarm". |
| **Claude Agent SDK** | MIT | The **definition schema + permission model** directly — custom tools via in-process MCP, hooks, allow/deny tool control. Needs the Claude Code runtime present. |
| **CrewAI** | MIT | **Sequential / hierarchical** role-assignment — "Crews" of role-playing specialists + "Flows". (AMP/Enterprise is paid.) |
| **MS Agent Framework** | MIT | **Multi-agent conversation** (group-chat/handoff) — the supported AutoGen+Semantic-Kernel successor. *Classic `microsoft/autogen` is maintenance-mode;* **AG2** (Apache-2.0) is the community fork keeping the old conversable-agent API. |
| **Pydantic-AI** | MIT | The **typed tool contract** — Pydantic models validate every tool arg + structured output, cutting agent failure modes. |
| **Google ADK** | Apache-2.0 | **Hierarchical** (manager delegates to sub-agents) with first-class **eval** + A2A delegation. |
| **Mastra** | Apache-2.0 (core) | The **TypeScript-native** option — agents+tools+memory+workflows in Node/edge (Vercel/Workers). *`ee/` is a proprietary Enterprise license.* |
| **smolagents** (HF) | Apache-2.0 | The **lean single-agent** shape — "code agents" write actions as executable Python (fewer steps than JSON calls). *Code-as-action = arbitrary execution → MUST sandbox (E2B/Modal/Docker).* |
| **Flowise** | ⚠️ Apache-2.0 **open-core** | The **visual / no-code canvas for building the *agent itself*** — this is where a "drag-and-drop / no-code AI-agent builder" request belongs (cohors, **not** machina's n8n: the deliverable here is a *generative agent*, not a fixed workflow — the artifact decides). A node canvas wires LLMs, tools, RAG, and control flow into a flow, then exposes it as a **REST endpoint + exportable JSON + embeddable widget**. Prototype the *shape* of the five patterns visually, then hand-code the production agent in the cohors schema. *Community core is genuinely Apache-2.0; the enterprise partition (SSO/RBAC/workspaces, `packages/server/src/enterprise`) is a proprietary Commercial License — don't activate or redistribute it. Heavyweight self-hosted service (Node+React+DB), not an embeddable library.* |

## The deep-research harness — a worked multi-agent shape

When the job is long-horizon research (decompose → gather in parallel → synthesize), don't invent the orchestration cold — there's a canonical worked shape to route against.

- **DeerFlow** (`bytedance/deer-flow`) · **MIT** · ~76k★ · v2.0.0 rewrite (Feb 2026) — ByteDance's **lead-agent → parallel isolated sub-agents → synthesis** runtime on LangGraph+LangChain, batteries-included: a filesystem abstraction, cross-session memory, a progressively-loaded skill system, sandboxed execution (local/Docker/K8s), MCP tools, and context compaction. The reason to keep it: its v1 **coordinator → planner → researcher → reporter** pipeline is the **reference shape** for cohors's *hierarchical + parallel* patterns, and v2's isolated-sub-agent model mirrors the swarm contract (scoped tools + termination per worker). **Adopt as a pattern reference, not a dependency** — it's a full runtime (a large LangChain tree + a Next web UI + IM gateways), the opposite of a lean fabius install. **Version trap:** v1 was a narrow deep-research pipeline; v2.0.0 rebranded to a general "SuperAgent" harness — most online tutorials describe the *old* architecture, so pin a version before citing.

## Giving an agent a voice (I/O)

An agent's *voice* is a **modality, not a model**: cohors owns the wiring, `fabius-doctrina` owns the speech model behind it.

- **Voicebox** (`jamiepine/voicebox`) · **MIT** *(app code)* · ~38k★ · v0.5.0 (pre-1.0) — a local-first voice studio (7 TTS engines — Qwen3-TTS, Chatterbox, Kokoro… — plus Whisper dictation and zero-shot cloning) that exposes a **local FastMCP-over-HTTP server**, so any MCP-aware agent (Claude Code, Cursor) gets a chosen **spoken voice** with **no audio leaving the machine**. The clean way to add speech-out to an orchestrated agent — the agent calls a local MCP tool, doctrina's model speaks. **Three caveats fabius prints:** (1) the MIT license covers **Voicebox's code only** — the 7 wrapped model **weights** each carry their own license (several restrict commercial use); verify per-model before shipping. (2) It clones a voice from **seconds of audio with no consent lock** — a biometric-impersonation / deepfake vector: gate it behind consent + provenance (`fabius-praesidium`), and consider sealing/watermarking generated audio (`fabius-catena`). (3) Heavy local install (GPU / Apple-Silicon), young. The **TTS/STT model tier** lives in `fabius-doctrina`.

## Evaluating the tool-caller

- **BFCL / Gorilla** (Apache-2.0) — the standard function-calling eval (AST + executable, single/parallel/multi-turn; V4 adds agentic + web-search). Pick the model behind an agent on *evidence*, not vibes; the harness (`bfcl-eval`) reproduces it locally. **Live-updated — re-check the current table; cited scores go stale fast.**
- **τ²-Bench (tau2-bench, Sierra)** (MIT) — the realistic multi-turn *user↔agent* benchmark where **both** call tools (airline/retail/telecom/banking). The companion to BFCL that xLAM/watt-tool cards themselves cite.

## Open tool-caller models — permissive first

| Model (HF id) | License | Note |
|---|---|---|
| **Qwen3** (Qwen3-235B-A22B-Instruct-2507; dense 4–32B) | **Apache-2.0** | *Default open backbone* — truly permissive (no MAU clause), native tool-calling (~BFCL-v3 70.9), 256K+ ctx. Use Qwen-Agent / vLLM tool parsers. |
| **Kimi K2 Instruct** (moonshotai) | **~MIT** (modified) | 1T-MoE (32B active) built for tool-use + autonomous agentic tasks; license far cleaner than Llama (display "Kimi K2" only above 100M MAU / $20M rev). A better permissive default than Llama 3.3. |
| **GLM-4.6** (zai-org) | **MIT** | 357B, 200K ctx, agentic + tool-use + coding; genuinely MIT weights + code — a permissive heavyweight (GLM-4.5 prior). |
| **Llama 3.3 70B Instruct** | ⚠️ **Llama Community** | Ubiquitous baseline + the base for many fine-tunes — but attribution + 700M-MAU + no-train-other-models; gated. Not Apache/MIT. |
| **Hermes 4 70B** (Nous) · **Functionary v3.1** (MeetKai) · **watt-tool-70B** | ⚠️ **Llama Community** (governs) | Strong specialized tool-callers (reason-then-call / OpenAI-style parallel / DMPO multi-turn) — but all **Llama derivatives**; the repo's MIT/Apache tag does **not** override the Llama license on the weights. |
| **Salesforce xLAM-2-70b-fc-r** | ⚠️ **CC-BY-NC-4.0** | Top BFCL/τ-bench evidence of what dedicated function-call training buys — **research/eval only, do not ship.** (1B/3B/32B are Qwen-based.) |
| *dataset* **Salesforce/xlam-function-calling-60k** | CC-BY-4.0 | 60k verified function-calling samples (APIGen) — the reference *data* to train/eval a tool-caller (note: CC-BY, *not* the model's NC terms). |

## Pairs with

`fabius-cohors` (the schema + the five patterns), `fabius-doctrina` (serve/fine-tune/eval the model an agent calls — doctrina owns the model, cohors owns the agent; also the TTS/STT tier behind an agent's voice), `fabius-machina` (deterministic wiring vs generative orchestration — the line; a visual Flowise flow vs a code n8n flow), `fabius-praesidium` (least-privilege tool permissions; sandbox code-as-action agents; the voice-clone consent gate), and `fabius-catena` (seal/watermark an agent's generated audio for provenance).
