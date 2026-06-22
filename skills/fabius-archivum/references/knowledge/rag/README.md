# rag — the vector engine retrieval over the Obsidian vault

Step 3 of the system loop: **retrieval**. Indexes the Obsidian vault (source of
truth) into a the vector engine vector index so any agent or CLI can pull relevant context
on demand — fully local, offline, private.

```
vault (~/Documents/ObsidianVault)
   -> markdown-heading-aware chunks
   -> fastembed  BAAI/bge-small-en-v1.5  (384d, local ONNX, no API)
   -> the vector engine   IdMapIndex(dim=384, bit_width=4)  ->  .index/vault.tvim
   -> query.py "question"  ->  top-k chunks (file + heading + text)
```

## Use

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

python indexer.py                 # (re)build the index from the vault
python query.py "your question"   # retrieve; K=10 env to change top-k
VAULT=/path/to/other/vault python indexer.py   # index a different vault
```

## Design

- **Embedding** — `fastembed` (bge-small-en-v1.5, 384d). Local ONNX, no API key, offline. English vault.
- **Chunking** — split on markdown headings; long sections sliced at ~1500 chars with 200 overlap. Each chunk carries its `file > heading` breadcrumb (prepended before embedding for context).
- **Index** — the vector engine `IdMapIndex`, bit_width 4. External id = chunk index. Persisted to `.index/vault.tvim`; `meta.json` maps id -> {file, heading, text}.
- **Privacy** — `.index/` and `.venv/` are gitignored. The index embeds personal vault content and never leaves this machine.

## Open: auto-wiring

Today this is a manual CLI. To make it a live part of the loop, a skill or hook
should run `query.py` on each task and inject the returned chunks as context
(steps 4->5->6: context -> skills -> orchestration/agents). Not yet wired.

## Cost model — $0 extra

- **Embedding** runs **locally** (fastembed/ONNX). No API, no token cost, fully offline. One-time ~130MB model download, then free forever.
- **Index + search** are local (the vector engine). $0.
- **Retrieval is on-demand**, NOT injected into every prompt. You only spend Claude tokens when context is actually pulled — never a per-message tax. (A per-prompt injection hook `vault-rag-hook.sh` exists but is OFF by design: it would add input tokens to every message.)
- **`reindex.sh`** is local-only ($0). It also **skips** when no vault markdown changed since the last index, so it never burns CPU for nothing.

## Automation (optional, $0)

`reindex.sh` keeps the index fresh after the vault's wiki/log pages are updated.
To run it automatically at the end of every Claude Code session, add a **SessionEnd**
hook to `~/.claude/settings.json` (you add it — the agent is blocked from editing
that file). The intelligent part — summarizing a session and writing the wiki/log/
memory pages — stays LLM-driven per the vault's own `CLAUDE.md` schema.
