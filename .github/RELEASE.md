# Release integrity

Repository version: **2.7.0**. The version string alone does not establish release status; the canonical signed tag and GitHub Release do. A release tag does not by itself establish Bitcoin confirmation.

## Three gates

- `bash scripts/verify-all.sh --mode=dev` permits a dirty worktree, but requires every version field to be the exact next patch after the newest signed release and replays every committed aggregate the historical receipts can support.
- `bash scripts/verify-all.sh --mode=release` is verification after sealing. It requires a clean `HEAD` exactly at the newest `vX.Y.Z-sealed` tag, validates the pinned historical tag object and key digest, verifies every canonical release tag against that unchanged root, validates the detached OTS structure and record digest without an external client, and binds a coherent version matrix plus a single-parent anchor commit that modifies exactly `provenance/sealed-commit.txt` and `provenance/sealed-commit.txt.ots`.
- `bash scripts/verify-all.sh --mode=proof-upgrade` is only for a later Bitcoin-confirmed replacement of the detached `.ots` bytes. Before commit it accepts exactly one staged `.ots` modification with no divergent worktree bytes; after commit it accepts one clean, untagged, direct proof-only child. It requires trusted Bitcoin verification and rejects pending, unavailable, forged, mismatched or unrelated changes.

None of these modes tags, timestamps, commits, pushes, publishes, installs, deploys, or creates a GitHub Release.

GitHub-hosted runners do not provide a trusted Bitcoin node. A proof-upgrade workflow therefore fails closed unless the maintainer deliberately provisions a pinned OTS client and a trusted Bitcoin RPC; parsed proof bytes or an arbitrary public API are not substituted for that trust boundary.

## Content-bound seal boundary

The Merkle manifest covers exactly:

- every top-level `skills/*/SKILL.md` contract;
- `AGENTS.md`;
- `ARCHITECTURE.md`;
- `CORPUS.md`.

Changing any of those files requires `bash provenance/seal-skills.sh`, a new release commit, a new anchor record and OpenTimestamps proof, and a new allowed-signature sealed tag. Nested reference material, runtime, evals, packaging, and public docs are outside that exact manifest-derived Merkle set; changing them does not justify reusing an old release tag. Every content release still gets a new version and signed tag because the tag binds the complete git tree.

The current release gate intentionally permits no signing-key rotation: `provenance/allowed_signers` and every canonical tag must remain bound to the pinned historical root. A future rotation requires a separately reviewed old-key-authorized transition protocol; replacing one or more recent tags and letting them authorize each other is never accepted.

## Human-gated release checklist

1. Finish the intended content and run the development aggregate gate.
2. If a sealed file changed, regenerate `provenance/seal-manifest.json` and rerun the development gate.
3. Rebuild `paper/fabius-as-a-system.pdf`; update `paper/artifact.json` with its version, SHA-256 and page count.
4. Commit the release tree. Create a fresh `provenance/sealed-commit.txt` and matching `.ots` proof for that release commit.
5. Create the allowed-signature `vX.Y.Z-sealed` tag at the anchor-record commit, then run the release gate from a clean checkout. The unchanged pinned historical trust root must verify the complete canonical tag chain, including the new tag.
6. With explicit owner approval, push the commit and tag.
7. Create the GitHub Release for that exact tag. Attach `paper/fabius-as-a-system.pdf` as `fabius-as-a-system-vX.Y.Z.pdf`, publish the exact SHA-256 from `paper/artifact.json`, and use the current `shear559/fabius` install commands. Mark it latest only after the asset is present.
8. When the digest-bound OTS proof can be trusted-verified against Bitcoin, run `bash provenance/upgrade-seal.sh`. It upgrades a temporary copy and atomically replaces only the detached proof after rechecking the record binding; it never stages, commits or pushes. Stage exactly `provenance/sealed-commit.txt.ots`, then run `bash scripts/verify-all.sh --mode=proof-upgrade`; the gate rejects an unstaged or staged-plus-divergent proof. If approved, commit exactly that staged file as the single direct child of the sealed tag and rerun the same gate from the clean child before pushing. Pending, unavailable, parsed-only or block-mismatched attestations must never be published as confirmed.
