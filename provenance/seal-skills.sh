#!/usr/bin/env bash
# Build the content-bound seal manifest for fabius.
#
# Computes a SHA-256 over every skill contract (skills/*/SKILL.md) and the core
# system docs, then a binary Merkle root over those leaves, and writes the result
# to provenance/seal-manifest.json. This is the *content-bound* half of the
# provenance apparatus (PROVENANCE.md §3): unlike the embedded fab1- comment, every
# value here is recomputable from the public files — forging one needs a hash
# collision. Re-run after changing any sealed file, then re-tag + re-stamp (§6).
#
#   bash provenance/seal-skills.sh
#
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"

python3 - <<'PY'
import hashlib, json, glob, os

# The sealed set: every skill contract + the core system documents.
files = sorted(glob.glob("skills/*/SKILL.md"))
for core in ("ARCHITECTURE.md", "CORPUS.md", "AGENTS.md"):
    if os.path.exists(core):
        files.append(core)

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

file_hashes = {}
for p in files:
    with open(p, "rb") as f:
        file_hashes[p] = sha256_hex(f.read())

# Binary Merkle root over leaves = sha256( path \0 filehash ), sorted.
leaves = sorted(
    hashlib.sha256((p + "\x00" + h).encode("utf-8")).digest()
    for p, h in file_hashes.items()
)
level = leaves[:]
if not level:
    raise SystemExit("no files to seal")
while len(level) > 1:
    nxt = []
    for i in range(0, len(level), 2):
        a = level[i]
        b = level[i + 1] if i + 1 < len(level) else level[i]  # duplicate last if odd
        nxt.append(hashlib.sha256(a + b).digest())
    level = nxt
merkle_root = level[0].hex()

manifest = {
    "spec": "fabius-seal/v1",
    "algorithm": "sha256",
    "merkle": "binary, leaf = sha256(path \\u0000 filehash), leaves sorted, last duplicated if odd",
    "note": "Content-bound seal of the fabius skill contracts and core docs. Every value is recomputable from the public files: recompute each file's sha256 and the merkle root and compare. See PROVENANCE.md §3 and skills/fabius-catena/references/sealing.md.",
    "count": len(file_hashes),
    "files": dict(sorted(file_hashes.items())),
    "merkle_root": merkle_root,
}

with open("provenance/seal-manifest.json", "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"sealed {len(file_hashes)} files")
print(f"merkle_root sha256: {merkle_root}")
PY
