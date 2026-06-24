# Fabius — system architecture

Fabius is **one system**, not a bundle of plugins. A single super-skill routes eight coordinated capability layers over a thin supporting spine — nine skills in all, counting the router itself — so any agent gains end-to-end engineering capability from one install. The router dispatches on three axes together: **which layer(s)**, **how much machinery**, and **which model tier**. This document is the system's own architecture and its capability matrix.

The organizing idea is the Fabian one: **scout wide, strike narrow.** Investigate broadly (process and memory make you wide); deliver the single smallest correct thing (lean makes you narrow). The layers below split exactly along that line.

---

## Layer model

```
                    ┌───────────────────────────────────────────────┐
   ROUTER     ───►  │  fabius — the praetorium: reads the job, sets  │
                    │  the stance, picks layer + machinery + tier    │
                    └───────────────────────────────────────────────┘
                                        │
   CORE       ───►  fabius-parcus — always-on lean core (runs under every layer)
                                        │
      ┌──────────┬──────────┬──────────┼──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼          ▼          ▼          ▼
  disciplina   decor      cohors    archivum   mercatus  praesidium   ludus
  eng.       design +    agent      persistent go-to-     defensive   game
  process    data-viz    eng.       memory     market     security    craft
      └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
                                        │
                    ┌───────────────────────────────────────────────┐
   SPINE      ───►  │  references/ · CORPUS.md · evals/ · AGENTS.md  │
                    │  (deep-dives) (the index) (benchmark)(any tool)│
                    └───────────────────────────────────────────────┘
                                        │
                                        ▼
   end to end: code · prose · UI + data-viz · agents · debug · memory
               · marketing · defensive-security · games
```

- **`fabius`** — the router / super-skill (the *praetorium*). Reads the task, sets the working stance, and dispatches on three axes: which layer(s), how much machinery (the capability ladder), and which model tier. Owns the system-level kill-switch and the *scout-wide / strike-narrow* maxim.
- **`fabius-parcus`** — the always-on lean core. Runs *underneath* every other layer (never instead of one): terse prose, the YAGNI ladder, surgical changes, assumption-checking.
- **`fabius-disciplina`** — the engineering-process layer: brainstorm → plan → test-first → prove, grilling ambiguity, root-cause debugging. Owns planning, test discipline, and the clarifying-question procedure.
- **`fabius-decor`** — the design layer: token vocabulary, the one-accent laws, mobile-first, the live-verify checklist — **and the data-visualization concern** (the *figura* library: data-ink charts, reproducible tokenized SVG, diagrams-as-code).
- **`fabius-cohors`** — the agent-engineering layer: the definition schema, least-privilege permissions, the five orchestration patterns (sequential / parallel / hierarchical / human-in-the-loop / swarm).
- **`fabius-archivum`** — the persistent-memory layer: interlinked notes, index + log, when to add vector retrieval.
- **`fabius-mercatus`** — the go-to-market layer: positioning, message-to-awareness match, proof over adjectives, a one-action funnel, converting copy, the smallest-campaign launch loop.
- **`fabius-praesidium`** — the defensive-security layer: STRIDE threat-modeling per trust boundary, the OWASP pass, secrets + least-privilege hygiene, and a severity→fix→proof finding contract. Hardens, never weaponizes.
- **`fabius-ludus`** — the game-craft layer: the core loop first, deliberate game feel (juice), state as an explicit machine, the pixel-art lane, balance one knob at a time, jam-sized scope.

## Coordination contract — single owner, zero overlap

Each rule has exactly one owning layer; every other layer references it instead of restating it. This is what keeps nine skills from contradicting each other:

| Rule | Owner |
|---|---|
| Planning (`step → verify`), test discipline, the clarifying-question / grill procedure | `fabius-disciplina` |
| Lean prose, the YAGNI ladder, the never-trim list, auto-clarity carve-outs | `fabius-parcus` |
| System kill-switch, routing + dispatch (layer · machinery · model tier), the shared maxim | `fabius` |
| Token contract, the one-accent laws, the data-visualization (figura) rules | `fabius-decor` |
| Message + positioning + the funnel path + converting copy | `fabius-mercatus` |
| Threat model, the audit, the finding contract (active security work) | `fabius-praesidium` |
| The game loop, game feel, balance, the studio pipeline | `fabius-ludus` |
| Agent-shape catalog, wiki schema (the deep references) | `fabius-cohors` / `fabius-archivum` `references/` |

`fabius-parcus` keeps the *never-trim* security floor (don't cut validation/security); `fabius-praesidium` owns the *active* security work (model the threat, name the check, prove it closed) and references that floor instead of restating it — single owner on each side of the line.

`fabius-parcus` is the only always-on layer. It composes with whatever task layer the router selects, and it never competes for a task verb — there is no "build" or "design" it wants to own, so it can run underneath the layer that does.

## Skill-resolution flow

```
prompt → fabius (router)   ── dispatch: which layer(s) · how much machinery · which model tier
         ├─ any output / any code         → fabius-parcus      → references/lean/guidelines/
         ├─ build / fix / refactor / plan  → fabius-disciplina  → references/process-playbook.md · references/process/
         ├─ UI / design / brand            → fabius-decor      → references/design-tokens.md · references/design/ (69 brands)
         ├─ chart / graph / diagram        → fabius-decor      → references/visualization.md · assets/charts/ (figura)
         ├─ build / orchestrate agents     → fabius-cohors     → references/agent-patterns.md · references/agents/ (catalog + fabius-vec.db)
         ├─ remember / knowledge base      → fabius-archivum   → references/memory-schema.md · references/knowledge/ (vector · wiki · rag)
         ├─ copy / launch / positioning    → fabius-mercatus   → references/marketing-playbook.md · corpus slot
         ├─ secure / threat-model / audit  → fabius-praesidium → references/security-playbook.md · corpus slot
         └─ game / loop / juice / playable → fabius-ludus      → references/game-playbook.md · corpus slot
```

Skills self-surface by their `description`; the router composes them. "Build a landing page" resolves to `fabius-disciplina` (brainstorm the spec) → `fabius-decor` (execute at quality), all under `fabius-parcus`. A vertical (a game, a launch, a security review) runs a studio: the domain skill leads, process plans, execution follows (routing-policy R13).

## The spine

- **`references/`** — on-demand depth bundled per layer, loaded only when a layer needs it so the skills stay lean. Each specialist ships a lean entry doc **plus a full library**: `fabius-decor` → a 69-brand design teardown library (`references/design/`) + the figura visualization entry (`references/visualization.md`); `fabius-cohors` → a 200+-agent production catalog with a `fabius-vec.db` memory index (`references/agents/`); `fabius-archivum` → a knowledge engine, wiki pattern, and RAG pipeline (`references/knowledge/`); `fabius-disciplina` → the craft + discipline process library (`references/process/`); `fabius-mercatus` → a channel + swipe library (`references/channel-swipe-library.md`); `fabius-praesidium` → a hardening + audit library (`references/hardening-guides.md`); `fabius-ludus` → an engine + feel library (`references/engine-recipes.md`); `fabius-parcus` → the lean guidelines (`references/lean/`).
- **`CORPUS.md`** — the one fabius-branded index over every capability library; the brain holds the index and pages in only the matching slice (routing-policy M9 · R9 · M7).
- **`evals/`** — a runnable, vendor-agnostic benchmark harness that scores a model with and without the fabius stance: `eval.mjs` (Anthropic/OpenAI), `portable_eval.py` (cross-vendor), a `harness.workflow.js` multi-agent variant, and the `results.json` they write on a run (gitignored — the measured numbers are recorded in [BENCHMARKS.md](BENCHMARKS.md)).
- **`AGENTS.md`** — the cross-tool bridge. The stance, compiled to plain markdown, so Codex / Cursor / Windsurf / Cline / Copilot / OpenCode / Gemini all run fabius.
- **Decision policy** — the `fabius` router carries `references/routing-policy.md` (the proven core R1–R10 / M1–M8, plus the operational extensions R11–R13 / M9, each sourced honestly to the agent-research canon — ReAct, Toolformer, Tree of Thoughts, RAP, Reflexion, MemGPT, DSPy, Voyager, the efficiency and memory surveys…), `references/agent-research.md` (the knowledge base + the source-mapped canon table), and `references/failures.md` (a Reflexion-style lesson log that grows from real incidents). The reasoning, the math, and the direct-vs-analogy honesty ledger are in [RESEARCH.md](RESEARCH.md).

## Capability matrix

What an engineer (or an agent) can do end-to-end under fabius:

| Capability | Layer(s) | What it produces |
|---|---|---|
| Write / refactor code lean | parcus (+ disciplina) | minimal, surgical, no speculative scope |
| Plan a multi-step change | disciplina | a `step → verify` plan you can loop on |
| Build test-first | disciplina | failing test → minimum pass → refactor |
| Debug by root cause | disciplina | reproduce → minimize → hypothesize → fix the cause → regression-test |
| Prove before "done" | disciplina | evidence — a run, a passing check — never "should work" |
| Ship-grade UI | decor | tokenized, one-accent, mobile-first, a11y-checked, live-verified |
| Visualize data | decor (figura) | data-ink charts, reproducible tokenized SVG, the right chart for the question |
| Build / orchestrate agents | cohors | precise description + least-privilege tools + output contract |
| Persist + retrieve knowledge | archivum | interlinked notes, index + log, cheap retrieval |
| Market a thing | mercatus | positioning, converting copy, a one-action funnel, a tested launch |
| Harden / audit (defensive) | praesidium | a STRIDE model, the OWASP pass, severity→fix→proof findings |
| Build a small game | ludus | a fun core loop, deliberate juice, an explicit state machine, jam-sized scope |
| Talk lean | parcus | shorter output, full substance |
| Never cut what matters | parcus (guardrail) | validation, security, a11y, data-loss handling preserved |

## Extension points

- **Add a capability layer** — a new `skills/fabius-<name>/SKILL.md` plus its path in `plugin.json` `skills[]`. Give it a precise `description` and a single owned concern; link to siblings, don't duplicate them.
- **Deepen a layer** — add a `references/<file>.md` and point the skill at it (progressive disclosure).
- **Externalize the corpus** — bulk reference material (agent catalogs, design teardowns, swipe files, hardening guides, vector stores) belongs **outside** the installed plugin as the indexed **fabius corpus** ([CORPUS.md](CORPUS.md) — one fabius-branded index over every capability library); the skill ships a lean entry doc + an index and pages in only the matching slice on demand (routing-policy R9 · M7 · M9). Adding a capability = adding a row to the corpus index, not a megabyte. The install stays lean; the library scales without it.
- **Add a benchmark model or task** — edit `evals/eval.mjs`.
- **Target a new tool** — copy `AGENTS.md` into that tool's rules path.

## Design principles

1. **One system, one stance** — install once, work end-to-end.
2. **Single owner, zero overlap** — one rule, one home; everyone else links.
3. **Lean by default, never flimsy** — minimal artifact, guardrails non-negotiable.
4. **Scout wide, strike narrow** — fan out to understand; deliver the smallest correct thing.
5. **Model- and tool-agnostic** — prompt-level scaffolding, portable to any agent that reads standing instructions.
