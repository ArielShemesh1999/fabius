#!/usr/bin/env python3
"""Index the Obsidian vault into a TurboVec IdMapIndex.

Walk markdown -> markdown-heading-aware chunks -> local fastembed (bge-small-en, 384d)
-> turbovec IdMapIndex (bit_width=4) persisted to .index/vault.tvim, with a meta.json
sidecar mapping each chunk id -> {file, heading, text}. The .index/ is local-only
(gitignored) because it embeds personal vault content.
"""
import os, sys, json, re, glob
import numpy as np

VAULT = os.path.expanduser(os.environ.get("VAULT", "~/Documents/ObsidianVault"))
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(HERE, ".index")
MODEL = "BAAI/bge-small-en-v1.5"
DIM = 384
MAX_CHARS = 1500          # ~400 tokens per chunk
OVERLAP = 200
SKIP = ("/.obsidian/", "/.trash/", "/.smart-env/", "/.git/")

def iter_md(vault):
    for p in glob.glob(os.path.join(vault, "**", "*.md"), recursive=True):
        if any(s in p for s in SKIP):
            continue
        yield p

def split_sections(text):
    """Split on markdown headings; each section = (heading, body)."""
    sections, head, buf = [], "", []
    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((head, body))
    for ln in text.splitlines():
        if re.match(r'^#{1,6}\s', ln):
            flush()
            head = ln.lstrip('#').strip()
            buf = []
        else:
            buf.append(ln)
    flush()
    return sections or [("", text.strip())]

def chunk_body(body):
    if len(body) <= MAX_CHARS:
        return [body]
    out, start = [], 0
    while start < len(body):
        out.append(body[start:start + MAX_CHARS])
        start += MAX_CHARS - OVERLAP
    return out

def build_chunks(vault):
    chunks = []
    for p in iter_md(vault):
        rel = os.path.relpath(p, vault)
        title = os.path.splitext(os.path.basename(p))[0]
        try:
            text = open(p, encoding="utf-8").read()
        except Exception:
            continue
        for head, body in split_sections(text):
            crumb = title if not head else (title + " > " + head)
            for piece in chunk_body(body):
                if piece.strip():
                    chunks.append({"file": rel, "heading": crumb,
                                   "text": piece, "emb": crumb + "\n" + piece})
    return chunks

def main():
    from fastembed import TextEmbedding
    from turbovec import IdMapIndex
    os.makedirs(INDEX_DIR, exist_ok=True)
    chunks = build_chunks(VAULT)
    if not chunks:
        print("no chunks found in", VAULT); sys.exit(1)
    print("vault:", VAULT, "| chunks:", len(chunks))
    model = TextEmbedding(MODEL)
    vecs = np.array(list(model.embed([c["emb"] for c in chunks])), dtype="float32")
    ids = np.arange(len(chunks), dtype="uint64")
    idx = IdMapIndex(dim=DIM, bit_width=4)
    idx.add_with_ids(vecs, ids)
    idx.write(os.path.join(INDEX_DIR, "vault.tvim"))
    meta = [{"file": c["file"], "heading": c["heading"], "text": c["text"]} for c in chunks]
    json.dump(meta, open(os.path.join(INDEX_DIR, "meta.json"), "w"), ensure_ascii=False)
    print("indexed", len(chunks), "chunks ->", os.path.join(INDEX_DIR, "vault.tvim"))

if __name__ == "__main__":
    main()
