#!/usr/bin/env python3
"""Query the vault Fabius-Vec index. Usage: python query.py <question>  (K=5 env to change top-k)."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(HERE, ".index")
MODEL = "BAAI/bge-small-en-v1.5"

def main():
    q = " ".join(sys.argv[1:]).strip()
    if not q:
        print("usage: python query.py <question>"); sys.exit(1)
    k = int(os.environ.get("K", "5"))
    from fastembed import TextEmbedding
    from fabius-vec import IdMapIndex
    idx = IdMapIndex.load(os.path.join(INDEX_DIR, "vault.tvim"))
    meta = json.load(open(os.path.join(INDEX_DIR, "meta.json")))
    model = TextEmbedding(MODEL)
    try:
        qv = np.array(list(model.query_embed([q])), dtype="float32")
    except Exception:
        qv = np.array(list(model.embed([q])), dtype="float32")
    scores, ids = idx.search(qv, k=k)
    for rank, (s, i) in enumerate(zip(scores[0], ids[0]), 1):
        m = meta[int(i)]
        snip = " ".join(m["text"][:300].split())
        print("\n[%d] %.3f  %s  (%s)" % (rank, s, m["heading"], m["file"]))
        print("    " + snip)

if __name__ == "__main__":
    main()
