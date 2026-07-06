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

`fabius-cohors` (the schema + the five patterns), `fabius-doctrina` (serve/fine-tune/eval the model an agent calls — doctrina owns the model, cohors owns the agent), `fabius-machina` (deterministic wiring vs generative orchestration — the line), and `fabius-praesidium` (least-privilege tool permissions; sandbox code-as-action agents).
