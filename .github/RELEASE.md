# Release integrity

Current development target: **2.6.3 (unreleased)**. A version in the repository is not a GitHub Release, a signed tag, or a Bitcoin-confirmed timestamp.

## Two gates

- `bash scripts/verify-all.sh --mode=dev` permits a dirty worktree, but requires every version field to be the exact next patch after the newest signed release and replays every committed aggregate the historical receipts can support.
- `bash scripts/verify-all.sh --mode=release` is verification after sealing. It requires a clean `HEAD` exactly at the newest allowed-signature `vX.Y.Z-sealed` tag, a coherent version matrix, and an anchor record whose commit/tree are real and contained by the tagged tree.

Neither mode tags, timestamps, commits, pushes, publishes, installs, deploys, or creates a GitHub Release.

## Content-bound seal boundary

The Merkle manifest covers exactly:

- every top-level `skills/*/SKILL.md` contract;
- `AGENTS.md`;
- `ARCHITECTURE.md`;
- `CORPUS.md`.

Changing any of those files requires `bash provenance/seal-skills.sh`, a new release commit, a new anchor record and OpenTimestamps proof, and a new allowed-signature sealed tag. Nested reference material, runtime, evals, packaging, and public docs are outside that exact manifest-derived Merkle set; changing them does not justify reusing an old release tag. Every content release still gets a new version and signed tag because the tag binds the complete git tree.

## Human-gated release checklist

1. Finish the intended content and run the development aggregate gate.
2. If a sealed file changed, regenerate `provenance/seal-manifest.json` and rerun the development gate.
3. Rebuild `paper/fabius-as-a-system.pdf`; update `paper/artifact.json` with its version, SHA-256 and page count.
4. Commit the release tree. Create a fresh `provenance/sealed-commit.txt` and matching `.ots` proof for that release commit.
5. Create the allowed-signature `vX.Y.Z-sealed` tag at the anchor-record commit, then run the release gate from a clean checkout.
6. With explicit owner approval, push the commit and tag.
7. Create the GitHub Release for that exact tag. Attach `paper/fabius-as-a-system.pdf` as `fabius-as-a-system-vX.Y.Z.pdf`, publish the exact SHA-256 from `paper/artifact.json`, and use the current `shear559/fabius` install commands. Mark it latest only after the asset is present.
8. When the digest-bound OTS proof gains a Bitcoin block attestation, run `bash provenance/upgrade-seal.sh`. It updates only the local proof and never stages, commits or pushes. Review it, rerun both provenance and release gates, then publish it as a separate provenance-only change only with explicit owner approval. Pending calendar attestations must never be described as Bitcoin-confirmed.
