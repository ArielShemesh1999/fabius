# Fabius Memoria — the retrieval stack (vector stores · RAG · embedding & reranker models)

Loaded on demand by `fabius-archivum`. The knowledge *engine*, the LLM-wiki pattern, and a working RAG pipeline live in `references/knowledge/`; this is the current **best-in-class stack** (2026) for the moment archivum needs machine retrieval: **where** to store vectors, **how** to retrieve (hybrid + rerank), and **which model** to embed with. Two fabius rules frame it: (1) `fabius-parcus` / *when-to-add-vector* — a small vault doesn't need a vector store at all; grep + the index first. (2) fabius ships **blue-and-white**, so the default embedder must handle **Hebrew** — licenses and multilingual coverage below are honest (`MIT`/`Apache` ship freely, **`NC`/Gemma = flagged**).

## The store ladder — climb only as far as the corpus forces

| Store | License | Reach for it when |
|---|---|---|
| **sqlite-vec** *(default local)* | MIT/Apache | One `.db` file, no server, runs in a CLI / Worker / browser (WASM). The portable memory that travels beside the markdown vault. Brute-force to ~10⁵–10⁶ vectors — verify latency past that. |
| **FAISS** | MIT | The foundational ANN primitive (IVF/HNSW/PQ, GPU, billion-scale) many stacks (incl. txtai) use directly — the reference between a linear scan and a full DB. |
| **LanceDB** | Apache-2.0 | Embedded but scales past sqlite-vec; disk/S3-backed, versioned, multimodal, built-in hybrid (vector+FTS). |
| **pgvector** | PostgreSQL | When memory already lives in Postgres/Supabase — vectors + relational filters + `tsvector` in one ACID store, no second service. Add **pgvectorscale** (StreamingDiskANN) if it grows. |
| **Qdrant** | Apache-2.0 | Graduates to a service: best-in-class payload filters, native dense+sparse hybrid in one call, quantization, multi-vector (ColBERT). |
| **Weaviate** | BSD-3 | Want the DB to own embedding + one-call BM25⊕dense (RRF) hybrid. |
| **Chroma** | Apache-2.0 | Fastest prototype/notebook; small-to-medium, DX over scale. |
| **Milvus** / **Vespa** | Apache-2.0 | Genuinely large (10⁸–10⁹) / GPU indexes (Milvus Lite for a laptop start); **Vespa** for serving-scale native tensor + late-interaction (ColBERT/ColPali) fused with BM25 + filters. |

## RAG frameworks & the runtime

- **sentence-transformers** (Apache-2.0) — the de-facto runtime that *loads and runs* nearly every embedder + cross-encoder reranker below (`SentenceTransformer` / `CrossEncoder`). Almost everything else sits on it.
- **LlamaIndex** (MIT) — the most complete ingest→node-parse→index→query framework; 40+ store integrations, swap embedders/stores behind one API. *(For a tiny vault a hand-rolled sqlite-vec loop is leaner — `fabius-parcus`.)*
- **Haystack** (Apache-2.0) — explicit, typed pipeline graph (retriever→ranker→reader) — fits fabius's *prove-the-wiring* discipline better than magic.
- **txtai** (Apache-2.0) — closest single package to archivum's ethos: an embedded store + vector/keyword/graph recall in one file, no server.

## Hybrid retrieval — dense is not enough

Dense embeddings blur exact terms, code identifiers, and **Hebrew proper names**. Run a lexical leg and fuse:

- **bm25s** (MIT) — ultra-fast pure-Python BM25 (~500× `rank_bm25`); fuse with dense via **Reciprocal Rank Fusion (RRF)**.
- **PyLate + RAGatouille** (MIT / Apache) — train/index/retrieve with **ColBERT late-interaction** (token-level), which generalizes better to niche domains and **low-resource languages like Hebrew** than single-vector recall.
- Pattern: retrieve top-k (dense ⊕ BM25) → **rerank** the top ~50–100 with a cross-encoder → precision@k jumps.
- **Fusion parameterization.** RRF fuses by rank alone; when both legs emit normalized scores, the tunable alternative is a **weighted sum** — `0.7·dense + 0.3·BM25` — with a **min-score floor of ~0.35** (below it, return *nothing* rather than noise) and a **cap of ~6 results** per query: recall that overflows the context budget isn't recall.
- **Temporal decay — raw captures decay, curated knowledge doesn't.** Score decay with a **half-life of ~7 days** applies **only to raw session-log chunks**; curated pages are exempt — promoting a fact to a page is a claim of continued validity, and decaying it punishes exactly the memory worth keeping. Old session hits carry a **staleness annotation proportional to age** ("from a session ~3 weeks ago") so the model weighs them honestly; curated pages never get one.
- **MMR diversity re-rank** — opt-in, **λ ~0.7**. When top-k collapses into near-duplicates of one memory (common once session logs pile up), a maximal-marginal-relevance pass trades a sliver of relevance for coverage. Off by default: on a deduped corpus it only costs precision.

## Embedding models — the default must speak Hebrew

| Model (HF id) | License | Note |
|---|---|---|
| **BAAI/bge-m3** *(default)* | MIT | One model, three modes (dense + sparse + ColBERT), 100+ langs incl. **Hebrew & Arabic**, 8192-token. Unrestricted commercial. |
| **Qwen/Qwen3-Embedding** (0.6B/4B/8B) | Apache-2.0 | 2025 SOTA multilingual (8B topped MTEB); instruction-aware, Matryoshka dims. 0.6B for on-device, 8B for a server. |
| **intfloat/multilingual-e5-large-instruct** | MIT | Battle-tested 560M, 100 langs incl. Hebrew — the dependable baseline everything assumes. *Must use `query:`/`passage:` prefixes or quality drops silently.* |
| **Snowflake/arctic-embed-l-v2.0** | Apache-2.0 | ~568M, strong multilingual + Matryoshka (shrink dims for a smaller index). Verify Hebrew empirically. |
| **Alibaba-NLP/gte-multilingual-base** | Apache-2.0 | Compact ~305M, 8192-token, CPU-friendly; pairs with `gte-multilingual-reranker-base`. The long-doc budget option. |
| **nomic-ai/nomic-embed-text-v2-moe** | Apache-2.0 | Open *data + code* MoE embedder — the provenance-transparent pick, aligns with fabius's auditable ethos. |
| **jinaai/jina-embeddings-v3** | ⚠️ **CC-BY-NC-4.0** | Strong, but **non-commercial** — benchmark reference only; don't ship on the open weights (same for jina-reranker). |
| **google/embeddinggemma-300m** | ⚠️ **Gemma license** (use-restricted) | Excellent 300M on-device multilingual (100+ langs) — but **not OSI-permissive**; for a commercial-safe local embedder prefer Qwen3-Embedding-0.6B (Apache) or bge-m3 (MIT). |

## Reranker models — the precision stage

| Model (HF id) | License | Note |
|---|---|---|
| **BAAI/bge-reranker-v2-m3** *(default)* | Apache-2.0 | Lightweight multilingual cross-encoder on bge-m3 lineage (Hebrew-capable); the most-adopted open reranker, drops into LlamaIndex/Haystack. |
| **Qwen/Qwen3-Reranker** (0.6B/4B/8B) | Apache-2.0 | SOTA, instruction-aware; use matched with Qwen3-Embedding so both stages align. 0.6B for interactive recall. |
| **mixedbread-ai/mxbai-rerank-large-v2** | Apache-2.0 | Permissive multilingual alternative to non-commercial Jina/Cohere rerankers. |
| **answerdotai/answerai-colbert-small-v1** | Apache-2.0 | ~33M late-interaction, CPU-friendly — punches above its size but **English-focused** (not for Hebrew). |
| **vidore/colpali-v1.3** | ⚠️ **Gemma license** | *Visual* retrieval — embeds PDF/scanned **page images** directly (skips OCR); great for scanned Hebrew documents, but review the Gemma terms + needs a GPU. |

## Shortlisting — MTEB/MMTEB, then verify

The **MTEB / MMTEB leaderboard** (Apache-2.0 benchmark) is the evidence base — filter the multilingual/MMTEB tab (and any Hebrew-bearing tasks) to shortlist. But scores are **self-reported and gameable** — treat as a shortlist, never ground truth, and **always re-validate on your own Hebrew queries** before committing an archivum model.

## Capture in · publish out — the vault's two open ends

Retrieval is the *middle* of archivum's job; a vault is only as good as what flows **into** it and how it's read back **out**. Two open, **local-first** tools bracket the store — both keep the "your notes stay yours" contract archivum is built on.

- **Meetily** (`Zackriya-Solutions/meetily`) · **MIT** · ~21k★ · v0.4.0 (2026, pre-1.0) — a **local meeting-capture** desktop app (Tauri; macOS/Windows prebuilt, Linux from source): mic **+ system audio** → real-time on-device transcription via **whisper.cpp** (or an NVIDIA **Parakeet** tier, ~4× faster) → an LLM **summary** through a pluggable brain — local **Ollama** for full offline, or Claude/Groq/OpenAI-compatible. The fabius fit: a meeting becomes a **compressed, source-grounded memory** — transcript → summary → retrievable note in the LLM-wiki — wired like any capture→compress→re-inject source (see [`external-recall.md`](external-recall.md)) over the engine in [`references/knowledge/`](knowledge/). **Two honest caveats:** (1) **speaker diarization is PRO-only** — the free build gives transcription + summary but no reliable speaker labels; (2) **"local" is a config, not a guarantee** — choose Ollama/whisper to keep audio on the machine; a cloud summary provider ships transcript text off-box (`fabius-praesidium`). The **ASR/model tier** (whisper.cpp vs Parakeet, quantization, local serving) is `fabius-doctrina`'s — doctrina owns the *model*, archivum owns the *note*.
- **Docsify** (`docsifyjs/docsify`) · **MIT** · ~31k★ · v4.13.1 stable / v5 RC — publish the markdown vault as a **browsable, searchable site with zero build**: one `index.html` (CDN script) over a folder of `.md`, client-side full-text search, themes, straight onto GitHub Pages. The lean KB viewer that travels *beside* the vault — no SSG build pipeline to stand up (`fabius-parcus`: don't add a build a folder-of-markdown doesn't need). **Caveats:** it renders **client-side**, so there's no static HTML artifact → weaker SEO / AI-crawler visibility than a pre-rendered SSG unless you add prerender (`fabius-mercatus`); and it renders arbitrary markdown/HTML in the browser → **an XSS surface for untrusted content** (sanitize; `fabius-praesidium`). v4 is maintenance-end; v5 is still an RC.

## Pairs with

`fabius-archivum` (the knowledge engine, LLM-wiki, RAG pipeline in `references/knowledge/`), `fabius-parcus` (*when-to-add-vector* — don't stand up a store a small vault doesn't need), **Fabius Bidi** / **Fabius Yisrael** (why the default embedder must handle Hebrew), `fabius-cohors` (a retrieval tool the agent calls), `fabius-doctrina` (the local ASR/LLM tier behind Meetily's on-device capture), and `fabius-praesidium` (privacy of captured audio; XSS of a client-rendered docs site).
