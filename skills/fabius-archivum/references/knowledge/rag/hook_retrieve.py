#!/usr/bin/env python3
"""Score-gated vault retrieval for the UserPromptSubmit hook.
Prints a compact context block, or nothing if no chunk clears MIN_SCORE."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(HERE, ".index")
MODEL = "BAAI/bge-small-en-v1.5"
MIN = float(os.environ.get("MIN_SCORE", "0.55"))
K = int(os.environ.get("K", "4"))

def main():
    q = " ".join(sys.argv[1:]).strip()
    if len(q) < 12:
        return
    if not os.path.exists(os.path.join(INDEX_DIR, "vault.tvim")):
        return
    from fastembed import TextEmbedding
    from turbovec import IdMapIndex
    idx = IdMapIndex.load(os.path.join(INDEX_DIR, "vault.tvim"))
    meta = json.load(open(os.path.join(INDEX_DIR, "meta.json")))
    model = TextEmbedding(MODEL)
    try:
        qv = np.array(list(model.query_embed([q])), dtype="float32")
    except Exception:
        qv = np.array(list(model.embed([q])), dtype="float32")
    scores, ids = idx.search(qv, k=K)
    hits = [(float(s), meta[int(i)]) for s, i in zip(scores[0], ids[0]) if float(s) >= MIN]
    if not hits:
        return
    out = ["[Vault RAG - relevant context from the Obsidian knowledge base (source of truth). Use if helpful; ignore if off-topic.]"]
    for s, m in hits:
        snip = " ".join(m["text"][:260].split())
        out.append("- (%s, %s) %s" % (m["heading"], m["file"], snip))
    print("\n".join(out))

if __name__ == "__main__":
    main()
