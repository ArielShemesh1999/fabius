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
- **`fabius-cohors`** — the agent-engineering layer: the definition schema, least-privilege permissions, the four orchestration patterns.
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
         ├─ any output / any code         → fabius-parcus      (always, underneath)
         ├─ build / fix / refactor / plan  → fabius-disciplina
         ├─ UI / design / brand            → fabius-decor      → references/design-tokens.md
         ├─ build / orchestrate agents     → fabius-cohors     → references/agent-patterns.md
         └─ remember / knowledge base      → fabius-archivum   → references/memory-schema.md
```

Skills self-surface by their `description`; the router composes them. "Build a landing page" resolves to `fabius-disciplina` (brainstorm the spec) → `fabius-decor` (execute at quality), all under `fabius-parcus`.

## The spine

- **`references/`** — on-demand deep-dives bundled per layer (the token contract, the agent-shape catalog, the wiki schema, the process playbook). Loaded only when a layer needs depth, so the skills themselves stay lean.
- **`evals/`** — a runnable, vendor-agnostic benchmark harness that scores a model with and without the fabius stance. See [BENCHMARKS.md](BENCHMARKS.md).
- **`AGENTS.md`** — the cross-tool bridge. The stance, compiled to plain markdown, so Codex / Cursor / Windsurf / Cline / Copilot / OpenCode / Gemini all run fabius.

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
