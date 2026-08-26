# Fabius Cohors — agent catalog index

Loaded on demand by `fabius-cohors`. The skill has the decision rules; `agent-patterns.md` has the copy-from schema and recurring shapes; this file maps the catalog under `references/agents/`. Counts are measured from disk. Nested skill bundles are deliberately quarantined as `REFERENCE.md`, so the plugin exposes only its 15 root contracts. To adapt one elsewhere, copy it explicitly into the target project's own `SKILL.md`; do not make it discoverable inside this plugin. Page in one slice — never the whole tree.

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

## Language packs — 85 ADK sample-agent reference projects

Full sample projects (code, not just prompts), one directory per agent. Treat them as adaptation references, not plug-and-play plugin skills; some upstream loaders expect the quarantined file to be named `SKILL.md` in a separate target project.

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

## Lookup — symbolic now, archived vector artifact

Use the tables above and symbolic search first, for example `rg -n "<role-or-capability>" skills/fabius-cohors/references/agents/`. `agents/fabius-vec.db` (also copied under `agents/fabius-agency/`) is an archived index artifact, but this plugin does **not** ship a compatible runnable query adapter: Archivum's vendored RAG is design-only after its package/import naming pass. Do not invoke `query.py` as if it worked; wire a compatible vector adapter explicitly if dense lookup becomes necessary.
