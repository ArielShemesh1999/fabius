<div align="center">

<img src="assets/fabius-pixel.svg" alt="fabius" width="440" />

#### scout wide · strike narrow

*One skill that equips Claude end to end — code, prose, agents, design, debug, memory.*

<br/>

<img src="assets/hero.webp" alt="fabius — twelve coordinated skills fused into one super-skill" width="100%" />

<br/>
<br/>

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=for-the-badge&logo=anthropic&logoColor=white)](https://docs.anthropic.com/en/docs/claude-code)
[![Twelve skills](https://img.shields.io/badge/architecture-12_skills,_one_install-1f6feb?style=for-the-badge)](#architecture)
[![Benchmark](https://img.shields.io/badge/benchmark-blind,_reproducible-2ea44f?style=for-the-badge)](#what-it-does)
[![Research-grounded](https://img.shields.io/badge/research--grounded-routing_policy-8957e5?style=for-the-badge)](RESEARCH.md)
[![Whitepaper](https://img.shields.io/badge/whitepaper-40pp_·_proofs_+_coherence-D97757?style=for-the-badge)](paper/fabius-as-a-system.pdf)
[![License](https://img.shields.io/badge/license-MIT-555?style=for-the-badge)](#license)

</div>

---

## What it is

fabius is one super-skill you hand the agent. It sets *how* the agent works across the whole job — write code, write prose, build and orchestrate agents, design UI, visualize data, debug, market the value, harden security, build games, develop on-chain and cryptographically seal artifacts, wire automations, research the sciences, and remember — and routes to a specialist only when a task needs depth. One stance, applied everywhere: talk lean, build lean, run a disciplined process, design at ship quality, build other agents, and stop re-deriving.

It is named for the Fabian doctrine: **scout the whole field, fight only the battle that matters.** One system of twelve coordinated, non-overlapping skills — a router, an always-on lean core, and ten engineering specialists — installed as a single plugin.

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

**Measured, blind, reproducible.** A three-arm evaluation — `baseline`, a generic *"be concise"* control, and the full fabius stance — scored by a judge model that is never told which arm produced which answer. Beating the *"be concise"* control, not the baseline, is the real test. fabius beats it on every tier while cutting output length:

| Model | baseline | "be concise" | **fabius** | vs. control | output cut |
|---|:---:|:---:|:---:|:---:|:---:|
| Opus 4.8 | 12.5 | 13.0 | **13.88** | **+0.88** | **−43%** |
| Sonnet 4.6 | 8.75 | 11.75 | **12.5** | **+0.75** | **−52%** |
| Haiku 4.5 | 8.88 | 9.13 | **10.38** | **+1.25** | **−32%** |

Across four model families — Grok, Mistral, GPT, Claude — the pattern holds: the advantage is largest at trust, ordering, and genuine-build boundaries, and near zero on pure over-engineering traps. Shorter answers that the blind judge scores *higher*.

> The claim the data supports: **structure beats brevity, and the advantage grows as the model's default discipline drops.** Not "smarter," not "10× on everything" — a scope-control system that knows when to compress and when to expand. Method, mechanism, and caveats: **[BENCHMARKS.md](BENCHMARKS.md)**.

---

## Architecture

One router over an always-on lean core and ten specialists, on a thin spine. The router dispatches by layer + machinery + model-tier; process decides *how*, domain decides *what*, and the lean core runs beneath everything.

<div align="center">

<img src="assets/architecture.svg?v=3" alt="How fabius works: your prompt goes to the fabius router, which dispatches by layer, machinery, and model-tier to ten specialists — disciplina (process), decor (design + data-viz), cohors (agents), archivum (memory), mercatus (marketing), praesidium (defensive security), ludus (games), catena (on-chain + sealing), machina (automation), scientia (science) — all running on the always-on fabius-parcus lean core, producing the smallest correct result." width="100%" />

</div>

Each rule has exactly one owning layer; every other layer links to it instead of restating it. That single-owner contract is what keeps twelve skills from contradicting one another. Full layer model, coordination table, and capability matrix: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## The twelve skills

| Skill | Role | What it delivers |
|---|---|---|
| `fabius` | router | reads the job, sets the stance, dispatches by layer + machinery + model-tier |
| `fabius-parcus` | lean core, always on | terse output · the YAGNI ladder · surgical changes · no speculative scope |
| `fabius-disciplina` | engineering process | brainstorm → plan → test-first → prove · grill ambiguity · root-cause debugging |
| `fabius-decor` | design + data-viz | one-accent laws · token vocabulary · mobile-first · live-verify · data-ink charts (figura) |
| `fabius-cohors` | agent engineering | definition schema · least privilege · five orchestration patterns including the swarm |
| `fabius-archivum` | persistent memory | autonomous per-project memory · the LLM-wiki · index + log retrieval · cross-session recall |
| `fabius-mercatus` | go-to-market | positioning · message-to-awareness match · proof over adjectives · a one-action funnel · converting copy |
| `fabius-praesidium` | defensive security | STRIDE per boundary · the OWASP pass · secrets + least-privilege · severity→fix→proof findings |
| `fabius-ludus` | game craft | the core loop first · deliberate juice · state as a machine · the pixel lane · jam-sized scope |
| `fabius-catena` | on-chain + sealing | account-validation-first contracts (EVM + Solana) · money-safe transactions · verifiable provenance sealing |
| `fabius-machina` | automation | deterministic workflow glue · discover-from-live-schema → build → validate AND verify → activate |
| `fabius-scientia` | science | competing falsifiable hypotheses · source-grounded database lookups · reproducible field-standard pipelines |

Each skill is a thin operating contract. The depth — a 69-brand design teardown library, a 200-plus-agent production catalog with a vector-indexed memory, a knowledge engine (vector, wiki, RAG), the full craft-and-discipline process library, and the marketing / defensive-security / game-craft playbooks — lives under each skill's `references/` (indexed by [CORPUS.md](CORPUS.md)) and loads only on demand, so the skill itself stays lean.

> *Latin, for the curious:* **parcus**, frugal · **disciplina**, training · **decor**, what is fitting · **cohors**, the cohort · **archivum**, the record office · **mercatus**, the marketplace · **praesidium**, the garrison · **ludus**, the game (and the school where you drill it) · **catena**, the chain · **machina**, the working mechanism · **scientia**, knowledge won by method.

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

Under the policy sits a **mathematical-foundations layer**: every rule reduced to its formal statement (decision theory, information theory, optimization, scheduling) — adversarially verified, then *proven* to compose as **one consistent, gap-free, model-applicable decision system** (all 18 rules are the same expected-loss / value-of-information threshold wrapped in a measurable task-partition). The decision policy, the math behind all seven figures, the foundations table, the coherence proof, and the direct-vs-analogy honesty ledger live in **[RESEARCH.md](RESEARCH.md)**. The figures are conceptual shapes of documented principles, not fabius measurements — reproduce them with `python3 assets/charts/render_figures.py`.

The full treatment — the twelve-skill architecture, the proven core of eighteen rules with **a complete proof of the mathematics under each one** (every proof adversarially verified, ten corrected before publication), the coherence theorem, the four operational extensions held honestly at the edge, the blind benchmark, and the honesty ledger — is collected as a 40-page **whitepaper**: **[paper/fabius-as-a-system.pdf](paper/fabius-as-a-system.pdf)** (reproduce with `bash paper/build.sh`).

---

## Install

A standard Claude Code plugin — zero build, zero config.

```bash
/plugin marketplace add ArielShemesh1999/fabius
/plugin install fabius
```

Or drop any single `skills/<name>/` folder straight into a project's `.claude/skills/`. Start any task with the `fabius` skill — it loads the stance and routes to the rest. The specialists also self-surface by their description:

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
```

---

## Any agent, any tool

fabius is plain-markdown skills — model- and tool-agnostic. The portable bridge is [`AGENTS.md`](AGENTS.md): copy it into your repo or paste it into your tool's rules, and the agent operates under fabius end to end.

| Tool | How to install |
|---|---|
| Claude Code | `/plugin install fabius` — all twelve skills with progressive disclosure |
| Codex / OpenAI | drop [`AGENTS.md`](AGENTS.md) at the repo root (read automatically) |
| OpenCode | `AGENTS.md` at the repo root, or copy `skills/` into `.opencode/` |
| Cursor | copy `AGENTS.md` into `.cursor/rules/fabius.mdc` |
| Windsurf | `.windsurf/rules/fabius.md` |
| Cline | `.clinerules/fabius.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` at the repo root |
| Any LLM / raw prompt | paste `AGENTS.md` (or a single `SKILL.md`) into the system prompt |

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
│   ├── fabius-machina/     automation           · references: automation build-and-verify playbook
│   └── fabius-scientia/    science              · references: scientific method · database-lookup
├── evals/                  blind benchmark — eval.mjs · portable_eval.py · harness.workflow.js
├── provenance/             content-bound seal — verify.sh · seal manifest · OTS Bitcoin proof · signed tag
├── PROVENANCE.md           how authorship is proven, not asserted (with the limits up front)
├── AGENTS.md               tool-agnostic bridge (Codex / Cursor / Gemini / …)
├── ARCHITECTURE.md         layer model · single-owner table · capability matrix
├── BENCHMARKS.md           method · mechanism · how to reproduce
├── RESEARCH.md             the decision policy, the math, the honesty ledger
├── CORPUS.md               the fabius corpus index — every capability library, one index
├── paper/                  the 40-page whitepaper (PDF) — proofs + coherence theorem
├── assets/charts/          numpy → SVG figure renderer (reproducible)
├── credits/                inspiration and attribution
└── LICENSE                 MIT
```

---

## Boundaries

Lean is a discipline, not a corner-cutter — it never trims input validation, security, accessibility, or data-loss handling. The full never-trim list is owned by [fabius-parcus → *When NOT to be lean*](skills/fabius-parcus/SKILL.md#when-not-to-be-lean).

fabius governs *how* the agent works, never *what* you want. Your instruction always wins, and `stop fabius` reverts the stance.

---

## License

MIT. The bundled `references/` adapt open work — see [credits/](credits/) for inspiration and attribution.

<div align="center">
<br/>
<sub>Built by <a href="https://github.com/ArielShemesh1999">Ariel Shemesh</a> · one folder, the whole stack · scout wide, strike narrow.</sub>
</div>
