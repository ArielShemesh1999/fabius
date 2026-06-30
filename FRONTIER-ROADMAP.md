# fabius → frontier agent — roadmap

*Research-backed plan to take fabius from "disciplined advisor" to a frontier-class autonomous operator in the league of Manus, OpenAI (Operator/CUA + Agents SDK), and Nous Hermes. Synthesized from a 7-agent research sweep (2026-06-26) and an adversarial feasibility review. Honest by design — fabius's own ethos is "structure beats brevity, measured."*

## Status

- **Phase 0–1 SHIPPED (2026-06-26)** — fabius is now an *operator*, not just an advisor. Built into the synapse worker: acting tools (`fetch` · `web_search` · `code`/CodeAct) on a **least-privilege capability model** (`read` always · `web` only when a search key exists · `exec` only on an explicit `act` opt-in), an **execution-grounded verify oracle** (run the code; a non-zero exit hard-overrides the LLM judge — free via Wandbox, python/js/ts), and a per-run cost/step governor. The console exposes an **Operator-mode toggle** and renders the new tool + code-exec phases. 72/72 worker tests green. Commits: runtime `9575b97`, console `d7d4813`. Found en route: the memory gate was *already* honest (score 60 < the 70 gate → unverified output never compounds), so the real leap was the acting tools + oracle, not a "fail-closed flip." *Paid backends (E2B isolated sandbox · Tavily search · Browserbase) remain opt-in and OFF.* To run live: `wrangler deploy` + one provider key, then POST `/api/fabius/run {"act":true}`.
- **Next:** Phase 2 (early eval gate) → Phase 3 (unify the two stacks + MCP) → Phase 4 (long-horizon driver) → Phase 5 (computer-use, last/narrow).

## The north star (revised after the adversarial pass)

> **fabius is the most *auditable, owner-controlled, verify-gated* autonomous operator — at capability parity with the frontier, and ahead of it on trust.**

Not "the most advanced on raw capability." On raw long-horizon computer-use, every frontier agent rides the **same shared tech** (frontier models + E2B/Browserbase sandboxes + MCP). fabius's defensible lead is the **harness, the discipline, and provenance** — proven by measured evals, not asserted.

## What the frontier actually is (2026)

| Agent | What makes it frontier | Where it's weak (fabius's opening) |
|---|---|---|
| **Manus** | Production harness for long-horizon autonomy: persistent hours-long cloud microVMs (E2B/Firecracker) + context engineering (KV-cache, logit-masking, file-as-memory, recitation); CodeAct; parallel sub-agent "Wide Research"; model-orthogonal ("less structure, more intelligence") | Reliability collapses on long/branching tasks; confident hallucination; prototype-grade code; opaque/unpredictable cost; wraps third-party models (no moat at the brain) |
| **OpenAI** (ChatGPT-agent / CUA + Agents SDK + Responses API + Codex) | Vertical integration — agentic-first base model with the loop baked in; widest hosted platform (handoffs, guardrails, tracing, server-side tools); CUA computer-use at scale (OSWorld ~38%) | Long-flow reliability gaps (Operator retired); latency (screenshot→reason→act); quota/cost-gated; closed/single-vendor |
| **Hermes** (Nous) | Leading **open-weights** agentic line — schema-faithful tool-calling, toggleable reasoning, **operator owns the policy layer**, self-hostable; 2026 Hermes Agent runtime (ReAct + MCP + sandbox + portable skills) | The model is **not a product** — no runtime/sandbox/computer-use; you build the harness; neutral alignment pushes all safety onto you |
| **The technique frontier** | Action space → **CodeAct** (executable code in a real sandbox); long-horizon reliability is the headline metric (~16h@50% mid-2026); capability lives in the **harness** (context engineering, sub-agents, verifiers) | **Benchmark integrity collapse** (Apr-2026 RDI: all 8 major agent benchmarks reward-hacked); reliability tax over long horizons; brittle "memory" that's really retrieval; fragile/slow computer-use grounding |

## What fabius already has (the brain — the hard part most agents lack)

Grounded in `synapse/worker/src/index.js` (the executable runtime) + the 15 skills:

- **Multi-model gateway**, 5 providers, one normalized shape, keyed fallback (`PROVIDERS`/`callLLM` ~2174-2291) — incl. open-weights (Hermes/Llama via Groq).
- **Inspectable 3-axis router** + 6-rung capability ladder + tier selection, callable **token-free** at `/api/fabius/route` (`route()` ~2340).
- **Real ReAct loop** (LLM emits one action/turn, runtime executes, observation fed back; `runFabius` ~2461).
- **Independent verifier (Prove)** with prompt-injection hardening (`fabiusVerify` ~2549).
- **Verify-gated compounding memory** — only verified (pass + score≥70) output grounds future runs; semantic RAG over Vectorize, quality×recency ranked (`decideMemoryWrite` ~2579, `recallMemory` ~1404).
- **Multi-agent orchestration that executes** + a **resumable Flow DAG** (handoffs, human gates, atomic step-claim, retry, dep-cascade; `runFlowWave` ~1780).
- **Key-vault security** (per-request `X-LLM-Key`, never persisted), rate-limit denial-of-wallet guard, token/step caps.
- **Live org-graph console** (Synapse) on a real CF Worker + D1 + Vectorize backend.
- **The wedge** — the Fabian stance compiled to a **proven 18-rule routing policy** (sourced to ReAct/ToT/Reflexion/MemGPT/DSPy/Voyager), **content-bound provenance seal**, 15 single-owner skills.

## The gap (the hands + autonomy)

1. **No acting tools.** The ReAct loop has only 2 **read-only** tools (`recall`, `route`) — it advises, it can't *do* (`AGENT_TOOLS` ~2407).
2. **No code execution / CodeAct sandbox** — the frontier's primary action space.
3. **No computer/GUI use.**
4. **Long-horizon capped short** — 5-step loop, 4-step waves, externally driven (no self-driver).
5. **Verifier is a soft LLM opinion** that *defaults to pass* on reviewer failure — the one place the discipline leaks.
6. **Two stacks not unified** — the Flow/orchestrate path is Anthropic-only, tool-less, single-message.
7. **`callLLM` is text-only** — no multimodal/native tool-calling (prerequisite for CUA + reliable tool use).
8. **Execution gated on a key** — no key → everything simulates.

## The build ladder (corrected by the feasibility review)

**Infra reality:** a Cloudflare Worker **cannot** run a VM or browser. CodeAct/CUA/long-horizon all need an **external sandbox** (E2B or Modal) + a browser farm (Browserbase) — real accounts, billing, egress, latency. The long-horizon driver must live in a **Durable Object / Cron**, never the request path. State this plainly; it's not a one-line edit.

**Phase 0 — the unglamorous prerequisite (do first).**
- Native **tool-calling + structured output** in `callLLM` for Anthropic + OpenAI (the loop currently hand-rolls JSON-action parsing; `callLLM` is text-in/text-only-out). This unblocks reliable tool use *and* is the foundation CUA needs.

**Phase 1 — make the central claim TRUE (highest credibility-leap per effort).**
- **Execution-grounded verify (SHIPPED):** when the deliverable is code, *run it/its tests* in a sandbox as a **hard oracle** that overrides the LLM judge (`fabiusVerify`). The no-reviewer default stays `{pass:true,score:60}` — deliberately **not** flipped to fail-closed, because the memory gate is already honest (score 60 < the 70 write gate → unverified output never compounds). This converts verify-gated memory from soft opinion to real signal — fabius's whole differentiator, made true.
- **CodeAct tool:** one `AGENT_TOOLS` entry that POSTs model-emitted code to **one** external sandbox (E2B/Modal) and feeds stdout/stderr back (the executor at ~2527 already runs any registered tool). Same sandbox serves the oracle.
- **Web tool pack:** `web_search` + `fetch` + `file` as registry entries (untrusted-content hardening reused).
- **Per-run cost/time/sandbox-minute budget governor** (extend the `ratelimit` table) — autonomy without it is a cost bomb.

**Phase 2 — the eval gate (moved early, as a safety net).**
- `/api/fabius/eval` running a **GAIA / SWE-bench-lite** subset through the real loop, **anti-reward-hack sandboxed** (no `file://` gold leakage — heed the RDI Apr-2026 finding), numbers published to `BENCHMARKS.md`. This must precede the stack unification so it can't silently break the one working multi-agent path.

**Phase 3 — unify + scale the brain.**
- Replace `callAnthropic` in `executeAgentRun` with the `runFabius` core → every Flow/orchestrate sub-agent gets 5-provider + tools + verify. Real sub-agent spawning from the loop. **MCP client tool** (remote HTTP/SSE servers) for the external ecosystem.

**Phase 4 — long-horizon autonomy.**
- Durable-Object/Cron **driver** that runs `runFlowWave` to completion; implement the documented **R12 dual-exit + stuck-loop escalation** in code; **pause/resume-for-credentials** via the existing gate; **in-run context compaction** (file-as-memory / recitation — the missing piece for 50-step runs); **Voyager learned-skill + Reflexion lesson** memory. Horizon is bounded by the **external sandbox session lifetime**, not CF.

**Phase 5 — computer use (deferred/descoped).**
- `/api/fabius/cua` observe→reason→act over headless Chromium (Anthropic computer-use tool + Set-of-Marks fallback), **per-action human gate**, scoped to high-value flows only. XL, parity-at-best, inherits the anti-bot/2FA/CAPTCHA reliability ceiling — lowest leap-per-effort; do it last and narrow.

## Where fabius genuinely leads (honest)

Not raw capability — **trust**:
1. **Auditability** — the dispatch decision is inspectable and callable **token-free** before spend. No competitor exposes this.
2. **Multi-model freedom** — one gateway over 5 providers incl. open-weights for owner-controlled, neutral-aligned, self-hostable runs. Manus/OpenAI are locked to their own brain; Hermes has no product.
3. **Verification honesty** — once Phase 1 lands, memory gates on whether code actually *ran*, vs the frontier's documented "confident hallucination."
4. **Provenance** — content-bound SSH + Bitcoin-anchored seal on skills (and, later, run transcripts): authenticated, owner-attributed agent work. Unique.
5. **Disciplined cost** — cheapest-tier-that-holds + caps, vs Manus's prefill-heavy ~100:1 unpredictable-credit loop.

Where it only reaches **parity** (no hand-waving): CodeAct, web tools, MCP, sub-agents, computer-use — all ride the same external tech as everyone. Raw model IQ is **not** a fabius lever. The edge is entirely harness + discipline + control, and it isn't real until the Phase 2 eval numbers publish.

## Top risks

- **Security blast radius** — a real sandbox + network turns prompt injection into RCE/exfiltration. Per-request capability flags, `cohors` least-privilege scopes, microVM isolation, human gate on irreversible actions.
- **Denial-of-wallet** — long self-driving loops + sandbox compute. Hard per-run cost/time governor (Phase 1, not later).
- **CF Worker limits** — CPU/subrequest caps; the driver MUST be a Durable Object/Cron, the live shell/browser lives in the external sandbox.
- **Benchmark integrity** — if the eval isn't sandboxed against gold leakage, "measured" credibility (fabius's whole positioning) dies.
- **Scope vs the lean ethos** — every tool must clear `fabius-parcus` YAGNI or fabius becomes the bloated harness it positions against.
- **Provider/model drift** — the `PROVIDERS` tier ids move fast; needs a maintenance cadence.

---
*Sources: first-party Manus context-engineering writeup + E2B Firecracker notes; OpenAI Operator/CUA/Agents-SDK/Responses docs; Nous Hermes 3/4 + Hermes Agent runtime; the agent-research canon (ReAct, Toolformer, ToT, Reflexion, MemGPT, DSPy, Voyager, CodeAct) + 2025-26 surveys; the UC-Berkeley/RDI Apr-2026 benchmark-integrity finding. Grounded in `synapse/worker/src/index.js` line refs. Private strategy doc — not in the public-facing set.*
