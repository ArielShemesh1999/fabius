# Credits & inspiration

The fabius **system** — the six skills, `AGENTS.md`, the architecture, and the evals — is original work, written from scratch under one stance (*scout wide, strike narrow*).

The on-demand depth under each skill's `references/` was **informed by and adapted from** the open work below. We learned from these projects and built our own version; credit where it's due. Bundled reference files keep their original `LICENSE` files where present (e.g. `skills/fabius-cohors/references/agents/orchestration/LICENSE`).

| fabius layer | Inspired / adapted from |
|---|---|
| `fabius-archivum` (memory, LLM-wiki) | Andrej Karpathy's "the wiki pattern" — incrementally-built personal knowledge bases ([gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)) |
| `fabius-archivum` (vector engine) | the `fabius-vec` knowledge engine, after open vector-search work (turbovec / ruvector) |
| `fabius-cohors` (swarm orchestration) | claude-flow / ruflo by ruvnet — coordinator + specialized-worker swarms, anti-drift, worktree isolation ([repo](https://github.com/ruvnet/ruflo)) |
| `fabius-cohors` (agent catalog) | open production-agent corpora (Google ADK samples and similar) |
| `fabius-decor` (design library) | open design teardowns + skill bundles (open-design, GSAP animation, UI/UX, HyperFrames) |
| `fabius-parcus` (lean guidelines) | the caveman (prose-trim) and ponytail (code-trim) disciplines |

Names inside the bundled references were aligned to fabius for consistency; the ideas are theirs, the system is ours. If you own one of these and want a change to the attribution, open an issue.
