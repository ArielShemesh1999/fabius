# rag — archived design for vector retrieval over an Obsidian vault

> **Design reference only — not runnable as vendored.** The package/import naming pass intentionally left this snapshot without resolvable dependencies. The commands below document the original shape; they are not installation or execution instructions for this plugin. Use index + `rg` now, or wire and test a compatible vector adapter explicitly.

This snapshot describes a local retrieval design: markdown-heading chunks → embeddings → quantized index → top-k context.

```
vault (~/Documents/ObsidianVault)
   -> markdown-heading-aware chunks
   -> fastembed  BAAI/bge-small-en-v1.5  (384d, local ONNX, no API)
   -> the vector engine   IdMapIndex(dim=384, bit_width=4)  ->  .index/vault.tvim
   -> query.py "question"  ->  top-k chunks (file + heading + text)
```

## Historical command shape (does not run as shipped)

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

## Open: adapter and auto-wiring

This snapshot has neither a working adapter nor auto-wiring. After replacing the unresolved engine dependency, validate indexing and querying on a disposable corpus before any hook injects returned chunks (steps 4→5→6: context → skills → orchestration/agents).

## Intended local cost shape

- **Embedding** was designed to run locally (fastembed/ONNX), with no inference API charge after the model download; compute, storage, and maintenance still have cost.
- **Index + search** were designed to stay local once a compatible engine is supplied.
- **Retrieval is on-demand**, NOT injected into every prompt. You only spend Claude tokens when context is actually pulled — never a per-message tax. (A per-prompt injection hook `vault-rag-hook.sh` exists but is OFF by design: it would add input tokens to every message.)
- **`reindex.sh`** illustrates freshness skipping, but is not an executable plugin workflow until the adapter is repaired or replaced.

## Automation design (not wired)

`reindex.sh` records the intended freshness workflow, but cannot maintain an index until a compatible adapter is supplied and tested. Only then should a user-authorized **SessionEnd** hook invoke it; memory writes still follow the vault's own contract and authorization boundary.
