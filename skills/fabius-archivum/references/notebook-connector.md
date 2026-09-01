<!-- © 2026 shear559 · fabius · reference depth for skills/fabius-archivum/SKILL.md -->

# Fabius Notarius — the source-grounded notebook that answers only from what was filed

Loaded on demand by `fabius-archivum`. [`external-recall.md`](external-recall.md) Part B gives the connector pattern — a source registry plus an ask-until-complete loop; this file works it through its strongest current instance, the unofficial `notebooklm-py` client over a Gemini Notebook. fabius supplies the rules; the harness's shell runs `notebooklm …` and the model reads the JSON. fabius hosts, schedules and calls nothing. The one law that outranks the rest: **the notebook is a reader over filed sources, never a second source of truth** — the markdown wiki stays canonical, and every notebook answer is a cited candidate to verify, not a fact to file.

## What it is, honestly

- **The service.** Google renamed NotebookLM to Gemini Notebook in July 2026 — same product, old links redirect. The client keeps its `notebooklm-py` name; since 0.8.1 its default host is `https://notebook.google.com`, and `NOTEBOOKLM_BASE_URL` accepts only that, the pre-rename personal host, or the enterprise host.
- **The client.** `notebooklm-py` (Teng Lin, MIT) is UNOFFICIAL: undocumented endpoints, no affiliation with Google, liable to break on any backend change. Terms of service and rate limits are the user's responsibility. Studied at version 0.8.1 plus unreleased commits, HEAD `453e8ca` (2026-08-31).
- **Three stability layers.** The Python public API (`__all__`, SemVer 0.x); the MCP tool surface (preview, outside semver — 33 tools at the studied HEAD); the REST `/v1` surface (experimental). The pattern outlives the product — a worked instance, not a dependency.

## Why archivum reaches for it

| Need | Lever | Caveat |
|---|---|---|
| Register a corpus | One notebook = one registry entry `{name, description, topics}`; let the notebook summarize itself for the description | Never tag it generically |
| A cited answer | `ask "…" --json` → `answer`, `conversation_id`, `turn_number`, `references[{source_id, citation_number, cited_text}]` | `cited_text` is the fragment verbatim since 0.8.1 (older builds truncated it) — still verify against `source fulltext <id>`. `--prompt-file` carries a long question: a prompt, never a source |
| Hard scoping | `-s <source_id>` (repeatable) on the CLI; `source_ids` on MCP `chat_ask` | "Use only the authoritative sources" in a prompt is advice, not a retrieval filter |
| Offload the heavy reading | The notebook's model reads the corpus; the agent spends tokens on orchestration and synthesis | A routing rule (R9 · R11), not a saving claim — carry no multiplier |
| Completeness | fabius's forced-follow-up loop: ask → diff against the original request → re-query the gaps → synthesize | fabius's own loop (Part B); upstream's nearest analogue, `AskResult.next_steps` / MCP `suggest_followups`, is model-suggested, not a diff against the request |

## Surfaces

| Surface | Install | Layer | Notes |
|---|---|---|---|
| CLI `notebooklm` | `uv tool install "notebooklm-py[browser]"` (`pipx` works too) | CLI + Python API | `[browser]` is what makes `login` work. PyPI or a release tag, never `main`; skip `[cookies]` on Python 3.13+ (fails to build) |
| Python | `uv add notebooklm-py` — no Playwright, no Chromium | SemVer 0.x | `async with NotebookLMClient.from_storage() as client:` |
| MCP `notebooklm-mcp` | `pip install "notebooklm-py[mcp]"`; wire with `notebooklm mcp install claude-code\|claude-desktop\|cursor\|windsurf` | Preview, not semver | stdio default, loopback HTTP on request. The user's client config starts it — fabius starts nothing |
| REST `notebooklm-server` | `server` extra | Experimental | Token-required, loopback-only by default |

## Sources

| Kind | Command | Note |
|---|---|---|
| URL · YouTube | `source add <url>` | Loopback, private and link-local hosts refused unless `--allow-internal`; non-HTTP schemes always refused |
| File — PDF, Word, EPUB, Markdown, plain text, images, audio, video | `source add ./path` | Symlinks refused by default (`--follow-symlinks`). A path that does not exist is ingested as pasted TEXT with only a stderr warning — pass `--type file` so a typo fails loudly |
| Pasted text | `source add "…" --type text` | |
| Google Drive | `source add-drive <id> <title> --mime-type <google-doc\|google-slides\|google-sheets\|pdf>` by reference; `source add-drive-file <id>` for upload-only kinds | The title on a by-reference add is overwritten from Drive metadata — rename after. MCP `drive` needs an explicit `mime_type` |
| Web research | `source add-research "query" --mode fast\|deep --from web\|drive` | Deep is web-only. `--timeout` defaults to 1800 s per phase, worst case twice. Upstream-reported: fast = a handful of sources in seconds, deep = 20+ sources in 15–30+ min. Run deep with `--no-wait`; a subagent runs `research wait -n <id> --import-all --timeout 1800` (`--cited-only` trims it; `--max-sources N` lives on `research import` only) |

After every ingest read the titles in `source list --json`: paywalls, X.com and bot walls ingest as READY with an error page as the body — pre-fetch such pages to a local `.md` instead. MCP `source_wait` warnings (thin, soft-404, challenge page) are advisory only.

## Artifacts

| Artifact | Download | The archivum use |
|---|---|---|
| Report (custom · briefing-doc · study-guide · blog-post) | `.md` | The filed record — a synthesis to verify, then write into the wiki under the write boundary |
| Quiz · Flashcards | `.json` / `.md` / `.html` | An eval set for a skill, drawn from the sources, not written by its author |
| Mind map (`--kind interactive`, default) | `.json` | Structure for a wiki page — the node tree drafts headings and `[[links]]`. Note-backed maps can collapse a multi-source request into one source's outline (upstream-documented) |
| Data table | `.csv` (UTF-8 with BOM) | Raw rows for a comparison page |
| Slide deck · Infographic | `.pdf` / `.pptx` · `.png` | Handed to `fabius-decor`; not memory |
| Audio · Video overview | `.m4a` (audio/mp4, not MP3) · `.mp4` | Media, not memory. Cinematic (Veo 3) gating is unsettled upstream — its skill says AI Ultra only, its quota snapshot lists 2/day on Pro; treat as unknown, let the account refuse. ~30–40 min upstream-reported |

Generation is asynchronous by default except `mind-map`. Capture `task_id` from `--json`; `artifact poll <task_id>` is the one-shot check right after `generate`, `artifact wait <artifact_id>` blocks with backoff once listed. Poll every 15–30 s (upstream advice). MCP-brokered download links expire after 30 min (upstream-documented); Google's own media-URL lifetime is undocumented — list right before downloading.

## Auth — tiers, the gate, and hygiene

| Method | Reach for it when | Caveat |
|---|---|---|
| `notebooklm login` (browser) | A person is present | Does not survive expiry unattended |
| `login --browser-cookies <browser>` · `auth import-cookies JSON` | A signed-in browser exists | Firefox is the easier source on Windows |
| `login --master-token --account EMAIL` (`[headless]` extra) | Servers, CI, unattended runs | Full-account, never rotates; upstream's own docs disagree on whether a password change kills it (install notes: no; troubleshooting: yes) — treat as unknown; on exposure revoke at Google Security → Your devices; single-consumer — concurrent re-mints invalidate each other; dedicated or throwaway account only |
| `NOTEBOOKLM_AUTH_JSON` inline | One short-lived job | Cannot be refreshed; `login` and `auth refresh` refuse it |
| `NOTEBOOKLM_REFRESH_CMD` | A secret store re-issues cookies | Inherits the FULL parent environment minus a scrub list — keep unrelated secrets out of the launching shell |

1. **Files.** Everything lives under `~/.notebooklm/profiles/<name>/` (`storage_state.json`, `context.json`, `master_token.json` at 0600), relocatable with `NOTEBOOKLM_HOME`. Add `.notebooklm/` to `.gitignore`; never print or log a cookie or token; `unset` an env credential when done. Compromise → revoke at Google, delete the directory (`fabius-praesidium`).
2. **The gate.** Two fields, both required: `auth check --test --json` must report `status` = `ok` and `checks.token_fetch` = `true`. Without `--test` the command merely parses the file, so a stale one still passes; `notebooklm status` says nothing about auth.
3. **Keepalive.** For a file-backed profile the user's scheduler runs `notebooklm --profile <p> auth refresh --quiet` every 15–20 min (the client throttles to 60 s anyway). Exit 0 means "no error", not "rotation happened".
4. **Cookie snapshots are not a CI credential.** Upstream observed (2026-08) a copied `__Secure-1PSIDTS` dying within ~30 min once another client rotated the session, whatever its `expires`. Ship the master token to CI instead. Never subset cookies: `SID` and `__Secure-1PSIDTS` are required, and partial extractions are upstream's leading suspect for "auth expires immediately".
5. **MCP over HTTP.** The bearer is env-only (`NOTEBOOKLM_MCP_TOKEN`, no flag — nothing in a process list); a non-loopback bind needs that token plus `NOTEBOOKLM_MCP_ALLOW_EXTERNAL_BIND=1` or the server fails closed.

## Autonomy laws

1. **Run without asking:** listings and reads (`list`, `source list`, `artifact list`, `history`, `research status`, `suggest-prompts`, `auth check`), `create`, `source add`, `ask` without `--save-as-note`, profile list/create/switch, and any `*wait` executed inside a subagent.
2. **Ask first, then pass `-y`:** every deletion — of a notebook, a source (by id, by title, or `source clean`), a note, an artifact, a label, a profile — plus `share remove`, `clear` and `auth logout`; `ask --new`, which permanently deletes the notebook's server-side conversation before asking; `generate *` (long, quota-consuming); `download *` (writes to disk); `research cancel` (fire-and-forget; confirms nothing); `--save-as-note` and `history --save`; any `*wait` in the main conversation.
3. **`language set` is ask-first in fabius** although upstream lists it as free: a GLOBAL account setting that changes every notebook's output, stored per `NOTEBOOKLM_HOME`, so `-p work` does not switch it. Per-command `--language` on `generate` is the surgical alternative.
4. **`--json` is not a consent flag.** Under `--json` most destructive commands refuse to prompt and return `CONFIRM_REQUIRED` or `VALIDATION_ERROR` until `-y` is passed. The two that proceed anyway are `ask --new --json` and `share remove --json` — treat them as loaded.
5. **MCP mirrors the CLI.** Deletion tools (`notebook_delete`, `source_delete`, `studio_delete`, `share_remove_user`) need `confirm=true`; otherwise they return a `needs_confirmation` preview and change nothing. `share_set_user` and public-widening `share_set_access` are gated the same way. Errors arrive typed with a `retriable` flag — branch on the code.

## Parallel agents and long work

- **Never `notebooklm use <id>` from parallel agents.** The selection lives in one `context.json` per profile, concurrent writers overwrite each other, and it does not survive a sandbox reset. Pass `-n <id>` on every call or set `NOTEBOOKLM_NOTEBOOK` (flag > env > `use` context).
- **Isolate agents** with `NOTEBOOKLM_PROFILE=agent-<id>` or a private `NOTEBOOKLM_HOME`; one Google account per concurrent master-token consumer. Full UUIDs in automation — 6+ character prefixes turn ambiguous as a notebook grows; MCP callers set `NOTEBOOKLM_MCP_STRICT_IDS=1` and chain on the echoed canonical `notebook_id`.
- **Wait in a subagent, not in the main turn.** Source processing 30 s–10 min, deep research 15–30+ min (upstream-reported): start with `--no-wait`, hand the `task_id` or `run_id` to a subagent (`fabius-cohors`). R5 applies — never act on the assumed completion of a task nobody polled.
- **MCP hosts cache the tool list.** When an upgrade folds or renames a tool, hosts go on calling the old name; remove and re-add the connector — a reconnect is often not enough.

## Quota discipline

- **Plan limits are static, and there is no live remaining-count API** — the settings call carries only the plan's ceilings (upstream-documented). Pace by rule, not by gauge.
- **`tier` is an opaque key, never an ordinal.** 1 = Standard and 2 = Pro are live-confirmed upstream; 4 = Plus, 3 and 6 = the two Ultra tiers, 5 = Workspace "Expanded" are decoded, not confirmed. 4 is a lower plan than 2; never compare with `<` or `>`. Pro, Workspace Higher and Enterprise all report 500/300 — the two numbers cannot identify the surface.
- **Google-published ceilings (upstream snapshot 2026-07-09, subject to change):** 50 sources per notebook on Standard, 100 on Plus, 300 on Pro, 500 and 600 on the two Ultra tiers; Deep Research on Standard is 10 per MONTH; daily quotas roll 24 h from first use. Source caps are per notebook — split a large corpus across notebooks, one registry entry each; the client enforces nothing, the account does.
- **Rate limits** surface as `code: "RATE_LIMITED"`. Upstream advice: `--retry N` on generate, a 2 s pause between bulk adds, 5–10 min before retrying. Audio, video, slide-deck, infographic, quiz and flashcard generation are what upstream lists as unreliable under rate limiting.
- **Ghost rows count.** When a file add fails after its row is registered, the row stays `preparing` (not `error`) and still consumes quota — `source list --status preparing` a minute apart, delete once confirmed stuck. A rejected add — e.g. the 51st source over the cap — can leave a ghost row too; reconcile with `source list` after any errored add or import.

## Write boundary

A "master brain" notebook that accumulates each session's decisions — upstream's own recipe via `note create` and `ask --save-as-note` — is archivum memory and falls under [`../SKILL.md`](../SKILL.md)'s write boundary: writes happen only when the workspace opted in and its contract authorizes them; otherwise return the proposed note as text. The markdown wiki remains the canonical store (schema in [`memory-schema.md`](memory-schema.md)); the notebook is a grounded reader over sources the wiki already points at. `external-recall.md`'s rule holds: a fact in two stores eventually disagrees with itself. Flow one way — wiki record → notebook sources → ask → verify the citation → compound.

## Grounding hygiene

| Trap | Rule |
|---|---|
| `start_char`/`end_char` are UTF-16 offsets into the source DOCUMENT, not into `source read`'s flat `content` (not interchangeable — upstream #2211) | Python: `SourceFulltext.document.slice(start_char, end_char)`; CLI: match `cited_text` against `source fulltext` (several matches possible) |
| MCP `source_read(detail=summary)` is model-generated | Use `detail=full` (bounded and paged, `truncated` flag) when the indexed text itself matters |
| A Drive-backed source stays `status: ready` after the file is deleted | Check `drive_status` / `is_drive_degraded`; an answer leaning on it cites a file that no longer exists |
| Research import is not atomic | Partial commits on timeout; de-dup is by URL only, and skipped if the pre-import snapshot fails |

## Pairs with

[`external-recall.md`](external-recall.md) (Part B), [`retrieval-stack.md`](retrieval-stack.md) (local RAG for a corpus you own), [`meeting-capture.md`](meeting-capture.md) (a filed meeting record is a notebook source), [`memory-schema.md`](memory-schema.md), rules R2 · R5 · R9 · R11 in [`../../fabius/references/routing-policy.md`](../../fabius/references/routing-policy.md), [CORPUS.md](../../../CORPUS.md) and [ARCHITECTURE.md](../../../ARCHITECTURE.md). Layers: `fabius-scientia` (a literature corpus, citations checked against the paper), `fabius-disciplina` (a docs/RFC oracle; R5 before acting on its answer), `fabius-praesidium` (credential hygiene), `fabius-cohors` (the subagent that waits).

Informed by **notebooklm-py** (Teng Lin, MIT) — studied for the source registry, scoped citation-only answers, the CLI / Python / MCP surfaces, destructive-action confirmation rules, credential hygiene and quota honesty, re-expressed in fabius's own voice; no upstream files bundled. See credits/README.md.
