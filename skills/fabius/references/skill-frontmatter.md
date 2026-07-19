# Fabius — SKILL frontmatter contract

The cross-harness contract for every `SKILL.md` frontmatter block in this plugin. One key set, written once, that discovers and routes correctly in every harness that reads Agent Skills. Loaded on demand — consult it before touching any skill's frontmatter, and when a new harness enters the support matrix.

> **Honesty.** This is a reference file: external sources are cited inline. Harness behavior below is a **2026-07 snapshot**, verified against each harness's own documentation (and, where the docs are silent, its parser source) — re-verify on any harness release before relying on a limit.

---

## The canonical key set

Five keys, each earning its bytes:

| Key | Why it exists |
|---|---|
| `name` | Identity. Must equal the skill's directory name — single-owner routing depends on the match. Lowercase + hyphens keeps it valid in every harness (grok-build's strictest rule is the binding one; see matrix). |
| `description` | The discovery surface — the only text every harness feeds its router. **≤ 1024 chars flattened**: the fabius structural-gate budget, chosen because it is the tightest cap any supported harness applies before truncating. |
| `when_to_use` | Trigger phrasing only — situations, user phrases, task shapes. **Complementary to `description`, never a restatement**: harnesses that read both concatenate them, so a duplicated sentence pays its cost twice and buys nothing. Combined `description` + `when_to_use` **≤ 1536 chars flattened** — the Claude Code listing budget; past it the listing truncates and the tail is invisible to the router. Written snake_case (see matrix for why that survives everywhere). |
| `license` | Provenance in-band. The skill file travels alone when a harness copies it out of the repo; the license must travel with it. |
| `metadata.author` | Attribution in-band, same reason. `metadata` is the spec-sanctioned bag for non-standard keys, and grok-build promotes `metadata.author` (and `metadata.short-description`) to its display layer — so authorship renders instead of rotting. |

Everything else the body can say, the body says — frontmatter is the part every harness parses on *every* discovery scan, so it stays byte-minimal.

## Per-harness field matrix — 2026-07 snapshot

| Harness | Behavior |
|---|---|
| **Claude Code** | Full documented key list includes `name`, `description`, `when_to_use`, `license`, `metadata` (plus keys fabius skips, below). Unknown keys are tolerated, not fatal. Listing truncation at 1536 chars of combined description text is the binding budget. *Source: Claude Code skills reference, code.claude.com/docs/en/skills.* |
| **grok-build** | Kebab-case is the documented primary for multi-word keys — `when-to-use` — and the parser reads `when-to-use` first with a `when_to_use` fallback (both keys are also on the malformed-YAML recovery list), so fabius's snake_case form loads intact. `metadata.author` / `metadata.short-description` are promoted for display. `name`: lowercase letters, digits, hyphens, ≤ 64 chars; spaces and underscores are normalized to hyphens; omitted `name` falls back to the directory name. Discovery does **not** honor `.gitignore` under known skill roots (`.grok/`, `.agents/`, `.claude/`, `.cursor/`) — an ignored skill file on disk still loads; hiding takes `[skills] ignore` in config. Plugins are **disabled by default** until explicitly enabled — and enabling ≠ trusting: install requires `--trust`, and an untrusted plugin's hooks and MCP servers stay blocked even when its skills list. *Sources: xai-org/grok-build `docs/user-guide/08-skills.md`, `09-plugins.md`; parser: `crates/codegen/xai-grok-tools/src/implementations/skills/discovery.rs`.* |
| **Cursor** | Reads `.claude/skills/` alongside its own `.cursor/skills/`. Follows the Agent Skills spec key set; anything non-standard belongs under `metadata` — the spec's escape hatch — which is exactly where fabius already keeps `author`. *Source: Cursor docs, Agent Skills.* |
| **Codex** | Ingests the plugin through its git plugin marketplace — the full repo arrives as-is, so the frontmatter contract above is what Codex sees; no per-key translation layer exists to fix a violation after the fact. *Source: OpenAI Codex plugin/marketplace docs.* |

The intersection rule falls out of the matrix: **write the strictest harness's form, and it degrades to a tolerated unknown everywhere else.** snake_case `when_to_use` is Claude Code's documented key and grok-build's verified fallback; kebab `when-to-use` would invert that bet with nothing gained.

## Keys fabius deliberately does not use

`allowed-tools`, `model`, `effort`, `disable-model-invocation`, `argument-hint`. Two reasons, both structural:

- **Byte-minimal frontmatter.** Every key is parsed on every discovery scan across fifteen contracts; a key that doesn't change a routing decision is pure cost.
- **Single-owner routing lives in the router, not in per-file grants.** Which layer runs, with what latitude, is `fabius`'s decision (see [routing-policy.md](routing-policy.md)) — scattering tool grants, model pins, or invocation locks across fifteen files would fork that authority into sixteen places and let two of them disagree.

## Enforcement

The structural gate (`evals/structural.mjs`) enforces this contract mechanically — name↔directory match, required keys, and the flattened description budget fail the build, not a review.
