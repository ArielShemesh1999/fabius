<div align="center">

<img src="assets/fabius-pixel.svg" alt="fabius" width="440" />

#### scout wide · strike narrow

*An autonomous AI agent that runs on every major model — Anthropic · OpenAI · Google · Mistral · Groq — from one console.*

<br/>

<img src="assets/hero.webp" alt="fabius — an autonomous AI agent of fifteen coordinated capability layers, one console, every model" width="100%" />

<br/>
<br/>

[![Autonomous agent](https://img.shields.io/badge/fabius-autonomous_AI_agent-7a3dff?style=for-the-badge)](https://synapse-vert-one.vercel.app)
[![Runs on every model](https://img.shields.io/badge/runs_on-every_model-7a3dff?style=for-the-badge)](#what-it-is)
[![Open the console](https://img.shields.io/badge/console-synapse-6322e8?style=for-the-badge)](https://synapse-vert-one.vercel.app)
[![Benchmark](https://img.shields.io/badge/benchmark-blind,_reproducible-2ea44f?style=for-the-badge)](#what-it-does)
[![Structural tests](https://img.shields.io/badge/structural_tests-23%2F23-2ea44f?style=for-the-badge)](BENCHMARKS.md)
[![Research-grounded](https://img.shields.io/badge/research--grounded-routing_policy-7a3dff?style=for-the-badge)](RESEARCH.md)
[![Whitepaper](https://img.shields.io/badge/whitepaper-proofs_+_coherence-7a3dff?style=for-the-badge)](paper/fabius-as-a-system.pdf)

</div>

---

## What it is

fabius is an autonomous AI agent. It runs on **every major model** — Anthropic · OpenAI · Google · Mistral · Groq — managed from one console, with a **Scout → Plan → Strike → Prove → Record** loop, an independent verifier, verify-gated compounding memory, least-privilege operator tools (`fetch` · `web_search` · `code`-exec), voice, and channels (Telegram [@fabiusagent_bot](https://t.me/fabiusagent_bot), WhatsApp). It sets *how* the work gets done across the whole job — write code, write prose, build and orchestrate other agents, design UI, visualize data, debug, market the value, harden security, build games, develop on-chain and cryptographically seal artifacts, wire automations, research the sciences, engineer and serve ML systems, analyze markets, and remember — drawing on a specialist layer only when a task needs depth. One stance, applied everywhere: talk lean, build lean, run a disciplined process, design at ship quality, build other agents, and stop re-deriving.

It lives across three aligned surfaces:

- **Brain** — this private, provenance-sealed repo.
- **Face** — the landing: **[fabius-landing.vercel.app](https://fabius-landing.vercel.app)**
- **Console** — synapse, the system itself: **[synapse-vert-one.vercel.app](https://synapse-vert-one.vercel.app)**

It is named for the Fabian doctrine: **scout the whole field, fight only the battle that matters.** Internally the agent is composed of fifteen coordinated, non-overlapping capability layers — a router (`fabius`), an always-on lean core (`fabius-parcus`), and thirteen engineering specialists — that decide how each job is done.

What fabius *is* — an **intelligence amplification layer**, not a model — and the contract for how it must be judged (same model, BASE → FAB → FAB_MEMORY, better outcomes on less waste) is fixed in **[IDENTITY.md](IDENTITY.md)**; its executable form is the **Fabius Benchmark Suite** in [`evals/suite/`](evals/suite/).

---

## What it does

Same model, one concentrated set of operating rules. The stance changes the *shape* of the output across every kind of work:

| You ask for | Typical model default | Under fabius |
|---|---|---|
| Code | verbose, over-engineered, may skip validation | minimal and surgical, validation and security kept |
| A bug fix | patches the symptom | reproduce → root cause → regression test |
| UI | inline styles, inconsistent, desktop-first | design tokens, one accent, mobile-first, accessible |
| An agent | broad tools, vague role | least privilege, precise output contract |
| An explanation | padded, hedged | tight, exact, no filler |
| Research / memory | re-derives every session | written down once, retrieved the next time |
| On-chain code | unchecked accounts, unsafe signing | account-validation-first, money-safe, simulate before signing |
| An automation | one-shot, silent miswires | discover-from-live-schema, validate AND verify, then activate |
| A science question | a confident guess | competing hypotheses, source-grounded lookups, reproducible |
| An ML system | a model that rots in prod | held-out leakage-free eval, the smallest serving stack, tracked + reproducible |
| A stock / market | a confident prediction | risk sized first, evidence over narrative, backtests proven out-of-sample (analysis, not advice) |

**One benchmark: fabius improves every model it runs on** — blind-judged on the newest Claude models, objectively verified by executed tests and factual checks, demoed across external families — on **20–35% less output**. One test, four panels, one receipt.

**Panel A — Quality, judged blind.** The four newest Claude models, 15 tasks × 3 arms — `baseline`, a generic *"be concise"* control (the real test), and fabius: the shipped `AGENTS.md` + routed `SKILL.md` injected *verbatim* — scored by **two independent blind judges** (inter-judge gap 0.72/15) never told which arm produced which answer. Blind score /15:

| Model | baseline | **fabius** | vs. baseline | output cut |
|---|:---:|:---:|:---:|:---:|
| Fable 5 | 14.50 | **14.73** | **+0.23** | **−25.3%** |
| Sonnet 5 | 14.07 | **14.50** | **+0.43** | **−33.7%** |
| Opus 4.8 | 14.40 | **14.60** | **+0.20** | −20.0% |
| Haiku 4.5 | 11.73 | 11.40 | −0.33 | **−35.5%** |

Every capable tier beats *both* the bare model and the "be concise" control (which scores 14.60 on Fable, 14.43 on Opus, 14.07 on Sonnet 5) — Sonnet 5's **+0.43** is the largest lift of the four; the output cut is universal, 20–34% on every model. Haiku is the one dip: it gains **+0.71** on its twelve specialist tasks and gives it back (−4.50) on three trivial one-liners under the full contract — the case *for* model-tier routing and the lean gate. The sharpest per-domain color inside the panel is a routed specialist rescuing the small model: on Haiku the security route jumps **9.0 → 14.5** and the on-chain SPL-balance task **10.5 → 14.5** once the specialist contract is injected — a guardrail the bare model doesn't supply on its own.

**Panel B — Objective, no judge.** Generated code **executed against hidden test suites**; domain deliverables graded against **factual checklists** by two strict graders — *looks right* versus *is right*. 9 deliverables × 3 arms × the same four models. Percent of hidden tests + factual checks passed:

| Model | bare model | under fabius | objective gain |
|---|:---:|:---:|:---:|
| Haiku 4.5 | 75.6% | **93.0%** | **+17.4** |
| Opus 4.8 | 84.9% | **90.7%** | +5.8 |
| Sonnet 5 | 84.9% | **90.7%** | +5.8 |
| Fable 5 | 87.2% | **90.7%** | +3.5 |

Executed algorithm code had no headroom — every bare model already ~100%; fabius holds it. The gains are in the deliverables that only *look* right: domain checklists move Haiku 58→88, Sonnet 5 74→84, Opus 74→84, Fable 78→84; per-deliverable, the parameterized SQL route **67.5% → 100%**, the idempotent webhook 40% → 67.5%, Solana account-validation 47.5% → 57.5% — output still cut 12–25% while doing it. **Every one of the four models gains objectively** (+3.5 to +17.4).

**Panel C — External families, demoed blind.** The same stance carried through the portable harness (`evals/portable_eval.py`, 6 tasks, measured 2026-06-22 with live provider keys), blind-scored against the *"be concise"* control on the genuine-build tasks: **Grok +8.5 · GPT +7.0 · Claude +7.0 · Mistral +2.5** (/15). Every family gains; Gemini is wired but carries no number without a key.

**Panel D — The FBS run: BASE → FAB → FAB_MEMORY.** The evaluation contract of [IDENTITY.md](IDENTITY.md), executed on the versioned **Fabius Benchmark Suite** (`evals/suite/`, FBS v1.0 — 100 neutral production-shaped tasks, 3 tiers, categories A–J, objective checks per task) with **two blind judges** on a seven-dimension 0–4 rubric (run 2026-07-05). On **Haiku 4.5** the layers stack monotonically: 25.27 → 26.00 → **26.73**/28 (**+1.46**) on 11–14% less output. On **Sonnet 5** (full 100 tasks) outcome-per-token rises — quality held at **93%** while output fell **10–12%**, the stress tier's objective check-rate up 89.9 → 93.7 — and the first behavioral measurement of memory: recalled snapshots lift design **+4.91** and *cost* security −1.57, the measured case for verify-gated recall. The one catastrophic FAB cell (a stub answer, 1.5/28) is printed in the receipt, not hidden.

Honest miss, printed: Haiku dips on trivial one-liners under the full contract (while gaining on its specialist tasks) — exactly what the router's model-tier dispatch and the lean gate exist to catch; every other model gains on both panels. **Built right, too:** a deterministic suite (`node evals/structural.mjs`) proves the system is well-formed — fifteen single-owner contracts, every reference live, the content-bound seal verifiable — **23/23**. The canonical receipt is **`evals/results.benchmark.json`**; full method, per-task numbers, and the raw receipts: **[BENCHMARKS.md](BENCHMARKS.md)**.

> The claim the data supports: **structure beats brevity, and the advantage grows as the model's default discipline drops.** Not "smarter," not "10× on everything" — a scope-control system that knows when to compress and when to expand. Method, mechanism, and caveats: **[BENCHMARKS.md](BENCHMARKS.md)**.

---

## Architecture

One router over an always-on lean core and thirteen specialists, on a thin spine. The router dispatches by layer + machinery + model-tier; process decides *how*, domain decides *what*, and the lean core runs beneath everything.

<div align="center">

<img src="assets/architecture.svg" alt="How fabius works: your prompt goes to the fabius router, which dispatches by layer, machinery, and model-tier to thirteen specialists — disciplina (process), decor (design + data-viz), cohors (agents), archivum (memory), mercatus (marketing), praesidium (defensive security), ludus (games), catena (on-chain + sealing), machina (automation), scientia (science), doctrina (ML engineering), fortuna (markets & finance), concilium (cross-model council) — all running on the always-on fabius-parcus lean core, producing the smallest correct result." width="100%" />

</div>

Each rule has exactly one owning layer; every other layer links to it instead of restating it. That single-owner contract is what keeps fifteen skills from contradicting one another. Full layer model, coordination table, and capability matrix: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## The fifteen capability layers

| Layer | Role | What it delivers |
|---|---|---|
| `fabius` | router | reads the job, sets the stance, dispatches by layer + machinery + model-tier |
| `fabius-parcus` | lean core, always on | terse output · the YAGNI ladder · surgical changes · no speculative scope |
| `fabius-disciplina` | engineering process | brainstorm → plan → test-first → prove · grill ambiguity · root-cause debugging · code-graph scouting · live-web fact-check · real-browser verify |
| `fabius-decor` | design + data-viz | one-accent laws · token vocabulary · mobile-first · live-verify · data-ink charts (figura) |
| `fabius-cohors` | agent engineering | definition schema · least privilege · five orchestration patterns including the swarm · agent evaluation · long-run durability · MCP tools · sandboxed exec |
| `fabius-archivum` | persistent memory | autonomous per-project memory · the LLM-wiki · index + log retrieval · cross-session recall |
| `fabius-mercatus` | go-to-market | positioning · message-to-awareness match · proof over adjectives · a one-action funnel · converting copy · SEO + AI-answer visibility |
| `fabius-praesidium` | defensive security | STRIDE per boundary · the OWASP pass · secrets + least-privilege · severity→fix→proof findings · third-party skill/MCP supply-chain audit |
| `fabius-ludus` | game craft | the core loop first · deliberate juice · state as a machine · the pixel lane · jam-sized scope |
| `fabius-catena` | on-chain + sealing | account-validation-first contracts (EVM + Solana) · money-safe transactions · verifiable provenance sealing · pre-deploy audit (Slither + fuzzing) · agent wallets |
| `fabius-machina` | automation | deterministic workflow glue · discover-from-live-schema → build → validate AND verify → activate · managed-OAuth + self-hostable integration platforms |
| `fabius-scientia` | science | competing falsifiable hypotheses · source-grounded database lookups · reproducible field-standard pipelines · structure prediction · simulation · literature grounding |
| `fabius-doctrina` | AI/ML engineering | the model lifecycle — train/fine-tune → evaluate → serve → monitor · held-out eval + blind judges · vLLM-class serving · MLOps + experiment tracking |
| `fabius-fortuna` | markets & finance | method over money — risk sized first · fundamental + technical + quantitative analysis · valuation · honest backtesting (out-of-sample, cost-aware) · analysis not advice |
| `fabius-concilium` | cross-model council | convene N models on one question · first opinions → anonymized peer-review → chairman synthesis · ensemble epistemics that beats a single seat · gated hard on cost (N+N+1 calls) |

Each skill is a thin operating contract. The depth — a 69-brand design teardown library, a 200-plus-agent production catalog with a vector-indexed memory, a knowledge engine (vector, wiki, RAG), the full craft-and-discipline process library, and the marketing / defensive-security / game-craft playbooks — lives under each skill's `references/` (indexed by [CORPUS.md](CORPUS.md)) and loads only on demand, so the skill itself stays lean.

> *Latin, for the curious:* **parcus**, frugal · **disciplina**, training · **decor**, what is fitting · **cohors**, the cohort · **archivum**, the record office · **mercatus**, the marketplace · **praesidium**, the garrison · **ludus**, the game (and the school where you drill it) · **catena**, the chain · **machina**, the working mechanism · **scientia**, knowledge won by method · **doctrina**, training · **fortuna**, fortune (and the market's turns) · **concilium**, the summoned council.

---

## The one idea

One axis dissolves the "be thorough versus be minimal" tension:

<div align="center">

### Scout wide in what you investigate.&nbsp;&nbsp;Strike narrow in what you ship.

</div>

Fan out to understand and verify. Ship the smallest correct artifact. Explain it in the fewest words. Process and memory make you wide; lean makes you narrow. They never conflict — they live on different axes.

---

## Grounded in agent research

fabius's decisions aren't hand-waving. Its routing policy is drawn from the agent-research canon — ReAct, Toolformer, Tree of Thoughts, RAP, Reflexion, MemGPT, DSPy, Voyager, and the 2026 efficiency and memory surveys — turned into a documented decision policy (a proven core of ten routing + eight orchestration/memory rules, plus operational extensions for model-tier dispatch, long-horizon loops, verticals, and corpus externalization), stated with an explicit ledger separating what the papers *measured* from what fabius *borrows by analogy*. Two principles, illustrated:

<div align="center">
<img src="assets/fig-capability-ladder.svg" alt="Capability vs machinery: fabius stops at the knee instead of climbing to a swarm" width="49%" />
<img src="assets/fig-reflection-iteration.svg" alt="Reflection quality vs iteration: a hard oracle earns more passes than soft self-critique" width="49%" />
</div>

**Climb one rung, stop at the knee** (left) — capability scales sub-linearly with machinery, so fabius adds the smallest sufficient rung (`inline → tool → retrieval → plan → subagent → swarm`) and never jumps to a swarm. **Refine on a real signal** (right) — a hard oracle (test, compiler) earns ~3 iterations, soft self-critique caps at 1–2, no signal ships once to human review.

Under the policy sits a **mathematical-foundations layer**: every rule reduced to its formal statement (decision theory, information theory, optimization, scheduling) — adversarially verified, then *proven* to compose as **one consistent, gap-free, model-applicable decision system** (all **22** rules are the same expected-loss / value-of-information threshold wrapped in a measurable task-partition, the composition’s exceptions printed; a researched frontier layer R14–R16 · M10–M13 sits at the working edge). The decision policy, the math behind all seven figures, the foundations table, the coherence proof, and the direct-vs-analogy honesty ledger live in **[RESEARCH.md](RESEARCH.md)**. The figures are conceptual shapes of documented principles, not fabius measurements — reproduce them with `python3 assets/charts/render_figures.py`.

The full treatment — the fifteen-skill architecture, the proven core of twenty-two rules with **a complete proof of the mathematics under each one** (every proof adversarially verified, corrections recorded in the receipt), the coherence theorem with its exceptions printed, the researched frontier layer held honestly at the edge, the blind benchmark, and the honesty ledger — is collected as a **whitepaper** (40+ pages): **[paper/fabius-as-a-system.pdf](paper/fabius-as-a-system.pdf)** (reproduce with `bash paper/build.sh`).

---

## Run it

fabius runs from **one console — [synapse-vert-one.vercel.app](https://synapse-vert-one.vercel.app)** — across every major model (Anthropic · OpenAI · Google · Mistral · Groq): pick a model, give it the goal, and watch the Scout → Plan → Strike → Prove → Record loop run with an independent verifier and verify-gated memory. Reach the agent on Telegram [@fabiusagent_bot](https://t.me/fabiusagent_bot) or WhatsApp. Read the paper → **[paper/fabius-as-a-system.pdf](paper/fabius-as-a-system.pdf)**.

<details>
<summary>Owner-only — the brain is also a private Claude Code plugin</summary>

The sealed brain in this repo doubles as the owner's own Claude Code plugin (zero build, zero config):

```bash
/plugin marketplace add ArielShemesh1999/fabius
/plugin install fabius
```

Or drop any single `skills/<name>/` folder into a project's `.claude/skills/`. The router loads the stance and routes to the rest; the specialists also self-surface by description:

```text
write code          → fabius-parcus
build a feature     → fabius-disciplina
build UI / a page   → fabius-decor
chart / visualize   → fabius-decor
build an agent      → fabius-cohors
remember this       → fabius-archivum
market / launch it  → fabius-mercatus
secure / audit it   → fabius-praesidium
make a game         → fabius-ludus
on-chain / seal it  → fabius-catena
automate a workflow → fabius-machina
research (science)  → fabius-scientia
serve / eval a model→ fabius-doctrina
markets / backtest  → fabius-fortuna
ask a council       → fabius-concilium
```

</details>

---

## Portable stance

The agent's operating stance is plain markdown, so it travels. The portable bridge is [`AGENTS.md`](AGENTS.md) — drop it into any other tool (or paste it into a system prompt) and that tool runs under the same fabius stance end to end.

| Tool | Carry the stance in via |
|---|---|
| Claude Code | the private plugin — `/plugin install fabius` (all fifteen layers, progressive disclosure) |
| grok-build (xAI) | native — discovers the Claude Code plugin (`.claude/plugins` + `skills/`) and reads `AGENTS.md` automatically; no file conversion — enable the plugin once (`grok plugin install <path> --trust`, then enable) |
| Codex / OpenAI | the full plugin via Codex's git plugin marketplace (`[marketplaces]` in `~/.codex/config.toml`) — all fifteen skills + [`AGENTS.md`](AGENTS.md) |
| OpenCode | `AGENTS.md` at the repo root, or copy `skills/` into `.opencode/` |
| Cursor | `AGENTS.md` → `.cursor/rules/fabius.mdc` |
| Windsurf | `.windsurf/rules/fabius.md` |
| Cline | `.clinerules/fabius.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` at the repo root |
| Any model / raw prompt | paste `AGENTS.md` (or a single `SKILL.md`) into the system prompt |

Verified 2026-07-19: loaded in Claude Code; installed and enabled in Codex via its plugin marketplace; installed and enabled in grok-build (0.2.103) with all fifteen skills discovered (in-session activation pending auth). The repo is private — remote installs need repo access; a local-path install works without auth.

---

## Repository layout

```text
fabius/
├── .claude-plugin/         plugin + marketplace manifests
├── skills/
│   ├── fabius/             router  · references: routing-policy · agent-research · failures
│   ├── fabius-parcus/      always-on lean core
│   ├── fabius-disciplina/  engineering process  · references: process library
│   ├── fabius-decor/       design + data-viz    · references: 69-brand library · visualization (figura)
│   ├── fabius-cohors/      agent engineering    · references: 200+ agent catalog
│   ├── fabius-archivum/    persistent memory    · references: vector · wiki · RAG
│   ├── fabius-mercatus/    go-to-market         · references: marketing playbook · channel + swipe library
│   ├── fabius-praesidium/  defensive security   · references: STRIDE/OWASP playbook · hardening · AI-review
│   ├── fabius-ludus/       game craft           · references: game playbook · engine recipes
│   ├── fabius-catena/      on-chain + sealing   · references: onchain playbook · sealing primitive
│   ├── fabius-machina/     automation           · references: automation build-and-verify · integration platforms
│   ├── fabius-scientia/    science              · references: scientific method · database-lookup · structure/sim/literature
│   ├── fabius-doctrina/    AI/ML engineering    · references: serving · MLOps · evaluation playbook
│   ├── fabius-fortuna/     markets & finance    · references: analysis · valuation · honest backtesting · risk
│   └── fabius-concilium/   cross-model council  · references: council protocol · council.mjs (runnable)
├── evals/                  the benchmark — three panels + receipts (results.benchmark.json canonical) · structural.mjs (23/23) · portable_eval.py
├── provenance/             content-bound seal — verify.sh · seal manifest · OTS Bitcoin proof · signed tag
├── PROVENANCE.md           how authorship is proven, not asserted (with the limits up front)
├── AGENTS.md               tool-agnostic bridge (Codex / Cursor / Gemini / …)
├── ARCHITECTURE.md         layer model · single-owner table · capability matrix
├── BENCHMARKS.md           method · mechanism · how to reproduce
├── RESEARCH.md             the decision policy, the math, the honesty ledger
├── CORPUS.md               the fabius corpus index — every capability library, one index
├── paper/                  the whitepaper (PDF) — proofs + coherence theorem
├── assets/charts/          numpy → SVG figure renderer (reproducible)
├── credits/                inspiration and attribution
└── LICENSE                 usage terms + attribution
```

---

## Boundaries

Lean is a discipline, not a corner-cutter — it never trims input validation, security, accessibility, or data-loss handling. The full never-trim list is owned by [fabius-parcus → *When NOT to be lean*](skills/fabius-parcus/SKILL.md#when-not-to-be-lean).

fabius governs *how* the agent works, never *what* you want. Your instruction always wins, and `stop fabius` reverts the stance.

---

## Credits

Some bundled `references/` adapt prior work — see [credits/](credits/) for attribution. fabius is private and proprietary — all rights reserved (see [LICENSE](LICENSE)); authorship is proven, not asserted — see [PROVENANCE.md](PROVENANCE.md).

<div align="center">
<br/>
<sub>Built by <a href="https://github.com/ArielShemesh1999">Ariel Shemesh</a> · one folder, the whole stack · scout wide, strike narrow.</sub>
</div>
