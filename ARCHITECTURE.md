# Fabius — system architecture

Fabius is **one system**, not a bundle of plugins. A single super-skill routes five coordinated capability layers over a thin supporting spine — six skills in all, counting the router itself — so any agent gains end-to-end engineering capability from one install. This document is the system's own architecture and its capability matrix.

The organizing idea is the Fabian one: **scout wide, strike narrow.** Investigate broadly (process and memory make you wide); deliver the single smallest correct thing (lean makes you narrow). The layers below split exactly along that line.

---

## Layer model

```
                       ┌────────────────────────────────────────┐
   ROUTER        ───►  │  fabius   — reads the job, sets the     │
                       │           stance, routes to a layer     │
                       └────────────────────────────────────────┘
                                         │
       ┌──────────────┬─────────────────┼──────────────────┬────────────────┐
       ▼              ▼                 ▼                  ▼                ▼
  fabius-parcus  fabius-disciplina  fabius-decor     fabius-cohors   fabius-archivum
  lean core      eng. process       design system    agent eng.      persistent memory
  (runs under
   every layer)
       └──────────────┴─────────────────┴──────────────────┴────────────────┘
                                         │
                       ┌────────────────────────────────────────┐
   SPINE         ───►  │  references/  ·  evals/  ·  AGENTS.md   │
                       │  (deep-dives)  (benchmark)  (any tool)  │
                       └────────────────────────────────────────┘
                                         │
                                         ▼
       end-to-end engineering: code · prose · UI · agents · debug · memory
```

- **`fabius`** — the router / super-skill. Reads the task, sets the working stance, pulls the right layer. Owns the system-level kill-switch and the *scout-wide / strike-narrow* maxim.
- **`fabius-parcus`** — the always-on lean core. Runs *underneath* every other layer (never instead of one): terse prose, the YAGNI ladder, surgical changes, assumption-checking.
- **`fabius-disciplina`** — the engineering-process layer: brainstorm → plan → test-first → prove, grilling ambiguity, root-cause debugging. Owns planning, test discipline, and the clarifying-question procedure.
- **`fabius-decor`** — the design layer: token vocabulary, the one-accent laws, mobile-first, the live-verify checklist.
- **`fabius-cohors`** — the agent-engineering layer: the definition schema, least-privilege permissions, the five orchestration patterns (sequential / parallel / hierarchical / human-in-the-loop / swarm).
- **`fabius-archivum`** — the persistent-memory layer: interlinked notes, index + log, when to add vector retrieval.

## Coordination contract — single owner, zero overlap

Each rule has exactly one owning layer; every other layer references it instead of restating it. This is what keeps six skills from contradicting each other:

| Rule | Owner |
|---|---|
| Planning (`step → verify`), test discipline, the clarifying-question / grill procedure | `fabius-disciplina` |
| Lean prose, the YAGNI ladder, the never-trim list, auto-clarity carve-outs | `fabius-parcus` |
| System kill-switch, routing, the shared maxim | `fabius` |
| Token contract, agent-shape catalog, wiki schema (the deep references) | `fabius-decor` / `fabius-cohors` / `fabius-archivum` `references/` |

`fabius-parcus` is the only always-on layer. It composes with whatever task layer the router selects, and it never competes for a task verb — there is no "build" or "design" it wants to own, so it can run underneath the layer that does.

## Skill-resolution flow

```
prompt → fabius (router)
         ├─ any output / any code         → fabius-parcus      → references/lean/guidelines/
         ├─ build / fix / refactor / plan  → fabius-disciplina  → references/process-playbook.md · references/process/
         ├─ UI / design / brand            → fabius-decor      → references/design-tokens.md · references/design/ (69 brands)
         ├─ build / orchestrate agents     → fabius-cohors     → references/agent-patterns.md · references/agents/ (catalog + fabius-vec.db)
         └─ remember / knowledge base      → fabius-archivum   → references/memory-schema.md · references/knowledge/ (vector · wiki · rag)
```

Skills self-surface by their `description`; the router composes them. "Build a landing page" resolves to `fabius-disciplina` (brainstorm the spec) → `fabius-decor` (execute at quality), all under `fabius-parcus`.

## The spine

- **`references/`** — on-demand depth bundled per layer, loaded only when a layer needs it so the skills stay lean. Each specialist ships a lean entry doc **plus a full library**: `fabius-decor` → a 69-brand design teardown library (`references/design/`); `fabius-cohors` → a 200+-agent production catalog with a `fabius-vec.db` memory index (`references/agents/`); `fabius-archivum` → a knowledge engine, wiki pattern, and RAG pipeline (`references/knowledge/`); `fabius-disciplina` → the craft + discipline process library (`references/process/`); `fabius-parcus` → the lean guidelines (`references/lean/`).
- **`evals/`** — a runnable, vendor-agnostic benchmark harness that scores a model with and without the fabius stance: `eval.mjs` (Anthropic/OpenAI), `portable_eval.py` (cross-vendor), a `harness.workflow.js` multi-agent variant, and a committed `results.json` from a measured run. See [BENCHMARKS.md](BENCHMARKS.md).
- **`AGENTS.md`** — the cross-tool bridge. The stance, compiled to plain markdown, so Codex / Cursor / Windsurf / Cline / Copilot / OpenCode / Gemini all run fabius.
- **Decision policy** — the `fabius` router carries `references/routing-policy.md` (10 routing rules + 8 orchestration/memory rules, each sourced honestly to the agent-research canon — ReAct, Toolformer, Tree of Thoughts, Reflexion, MemGPT, DSPy, Voyager…), `references/agent-research.md` (the knowledge base), and `references/failures.md` (a Reflexion-style lesson log that grows from real incidents). The reasoning, the math, and the direct-vs-analogy honesty ledger are in [RESEARCH.md](RESEARCH.md).

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
| Build / orchestrate agents | cohors | precise description + least-privilege tools + output contract |
| Persist + retrieve knowledge | archivum | interlinked notes, index + log, cheap retrieval |
| Talk lean | parcus | shorter output, full substance |
| Never cut what matters | parcus (guardrail) | validation, security, a11y, data-loss handling preserved |

## Extension points

- **Add a capability layer** — a new `skills/fabius-<name>/SKILL.md` plus its path in `plugin.json` `skills[]`. Give it a precise `description` and a single owned concern; link to siblings, don't duplicate them.
- **Deepen a layer** — add a `references/<file>.md` and point the skill at it (progressive disclosure).
- **Add a benchmark model or task** — edit `evals/eval.mjs`.
- **Target a new tool** — copy `AGENTS.md` into that tool's rules path.

## Design principles

1. **One system, one stance** — install once, work end-to-end.
2. **Single owner, zero overlap** — one rule, one home; everyone else links.
3. **Lean by default, never flimsy** — minimal artifact, guardrails non-negotiable.
4. **Scout wide, strike narrow** — fan out to understand; deliver the smallest correct thing.
5. **Model- and tool-agnostic** — prompt-level scaffolding, portable to any agent that reads standing instructions.
