# Fabius Cohors — agent catalog index

Loaded on demand by `fabius-cohors`. The skill has the decision rules; `agent-patterns.md` has the copy-from schema and the recurring shapes; this file maps the production agent catalog under `references/agents/`. Counts are measured from disk. Page in one slice — never the whole tree.

## fabius-agency — 248 role/persona agents across 17 divisions

Each agent is a self-contained markdown definition (YAML frontmatter + full system prompt) — drop the file into Claude Code, Cursor, or OpenCode to activate the specialist. The per-agent table lives in `agents/fabius-agency/README.md`; the division directories:

| Division | Agents | Scope |
|---|---|---|
| `agents/fabius-agency/academic/` | 5 | scholarly worldbuilding — anthropologist, geographer, historian, narratologist |
| `agents/fabius-agency/design/` | 9 | brand guardianship, image-prompt engineering, inclusive visuals, persona walkthroughs |
| `agents/fabius-agency/engineering/` | 33 | backend / AI / data / infra architects and engineers across the stack |
| `agents/fabius-agency/finance/` | 5 | bookkeeping, FP&A, financial analysis, investment research |
| `agents/fabius-agency/game-development/` | 20 | game and audio design plus `blender/` and `godot/` tool packs |
| `agents/fabius-agency/gis/` | 13 | geospatial analysis, cartography, BIM, 3D scenes |
| `agents/fabius-agency/marketing/` | 36 | SEO/AEO, AI-citation strategy, app-store optimization, content and growth |
| `agents/fabius-agency/paid-media/` | 7 | PPC and paid-social strategy, creative, account audits |
| `agents/fabius-agency/product/` | 5 | product management, feedback synthesis, sprint prioritization |
| `agents/fabius-agency/project-management/` | 7 | experiment tracking, Jira stewardship, meeting notes, project shepherding |
| `agents/fabius-agency/sales/` | 9 | account and deal strategy, coaching, discovery |
| `agents/fabius-agency/security/` | 10 | appsec, cloud security, architecture, blockchain audit |
| `agents/fabius-agency/spatial-computing/` | 6 | visionOS / XR / Metal engineering |
| `agents/fabius-agency/specialized/` | 53 | cross-domain operators — orchestrators, governance, back-office (largest division) |
| `agents/fabius-agency/strategy/` | 16 | strategy briefs plus a `coordination/` sub-pack |
| `agents/fabius-agency/support/` | 6 | support analytics, reporting, finance tracking, infrastructure |
| `agents/fabius-agency/testing/` | 8 | accessibility, API, performance testing, evidence collection |

## Language packs — 85 runnable ADK sample agents

Full agent projects (code, not just prompts), one directory per agent:

| Pack | Projects | Scope |
|---|---|---|
| `agents/python/` | 74 | the main ADK sample set — RAG, customer service, financial advisor, data science/engineering, claim adjudication, brand alignment, security |
| `agents/go/` | 5 | financial advisor, LLM auditor, research and sailing demos |
| `agents/java/` | 2 | software bug assistant, time-series forecasting |
| `agents/kotlin/` | 2 | fun facts, LLM auditor |
| `agents/android/` | 1 | fun facts |
| `agents/typescript/` | 1 | customer service |

## Orchestration extractions — 163 swarm-coordination agents

`agents/orchestration/` — agent definitions extracted from a multi-agent swarm-coordination framework: 108 core agents (`agents/`) + 55 plugin agents across 32 plugins (`plugins/`). Knowledge-only — framework code stripped; see its `README.md` and `LICENSE`.

`agents/opencode/README.md` — how to import any catalog agent as an OpenCode per-project specialist (permissions, model override, system prompt).

## Semantic lookup — fabius-vec.db

When browsing by name or division isn't enough, use dense retrieval: `agents/fabius-vec.db` (a copy also ships inside `agents/fabius-agency/`). Query it through `fabius-archivum`'s RAG tooling — `skills/fabius-archivum/references/knowledge/rag/query.py` — the same `fabius-vec` retrieval contract CORPUS.md defines for every library.
