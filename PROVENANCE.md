<div align="center">

# Provenance & release attribution of fabius

### How the repository records what was sealed, when it existed, and which key signed it — with the limits up front.

</div>

This document is the apparatus that lets anyone inspect **what was sealed**, **which key signed it**, and whether its detached OpenTimestamps proof is merely calendar-attested or trusted-verified against Bitcoin. It records release provenance and attribution; it is not by itself proof of originality, exclusive ownership, first creation, or a legal entitlement. Six mechanisms support the record: three repository facts — the fingerprint (§3), copyright notice (§4), and public git objects (§4); one recomputable content-bound seal (§3·b); and two release artifacts — the digest-bound OpenTimestamps proof (§1) and signed tag (§2). `bash provenance/verify.sh` reports the live state. A pending proof is not called Bitcoin-confirmed.

**The honesty stance, up front.** A public git repository **cannot be made uncloneable.** That is not a missing setting — it is how git works: anyone who can read the repo can `git clone` it in full, history included. Disabling forks does not stop it. No code, license, or watermark changes this. Anyone who promises a "clone-proof" public repo is selling a fiction.

So this package does not attempt prevention. It combines three kinds of evidence:

1. **Priority** — after Bitcoin confirmation, places an independently checkable upper bound on when the exact digest-bound record existed. It does not prove that no earlier copy existed.
2. **Key attribution** — binds a release tag to the holder of the committed signing key; key custody determines the strength of that attribution.
3. **Detection & enforcement support** — makes some public verbatim clones searchable and preserves evidence useful to a fact-specific enforcement process.

The one true way to keep an *idea* from being copied is to not publish it. Once it is public, claims must be supported by **specific provenance evidence and fact-specific enforcement, not by a lock.** This document records that evidence without deciding legal ownership.

---

## 1 · Priority evidence (OpenTimestamps → Bitcoin)

OpenTimestamps can provide independently checkable priority evidence for exact bytes. Anyone can copy the proof, but it remains bound to the original digest and signed release; copying it does not create an earlier timestamp for different bytes.

At seal time, `provenance/sealed-commit.txt` records the full git commit hash and tree hash of the sealed release. A commit hash covers the tracked tree, commit metadata and parent links. The adjacent `.ots` file is a detached proof over the record's SHA-256. `verify.sh` first uses the repository's dependency-free parser to validate the complete detached-proof structure, reject trailing garbage, and compare its embedded digest with a fresh SHA-256 of the record; this binding does not depend on an installed OTS client. Calendar attestations are the pending state. Bytes that merely parse as a `BitcoinBlockHeaderAttestation` are still untrusted input: confirmation requires a successful `ots verify` against a trusted Bitcoin source, for the same record and the same parsed block.

- **What it proves after Bitcoin confirmation.** That the digest-bound sealed record — and therefore the commit/tree it names — existed no later than the attested block. Before confirmation it proves only that calendar servers accepted the digest; it has no Bitcoin block date yet.
- **What it does NOT prove.** Existence-by-a-date is not authorship or ownership. The bounded combined claim is: *this key signed these bytes, and this exact record existed no later than the trusted-verified block*. It does not prove first creation, exclusivity, originality, or legal ownership.
- **Honest caveat.** A fresh proof starts pending and may later upgrade to a Bitcoin attestation. Run `bash provenance/upgrade-seal.sh` when available; it checks detached-digest binding before the upgrade and never commits or pushes. Never infer confirmation from the file's presence or prose. `verify.sh` is the live state check.
- **Immutable record wording.** Each released `sealed-commit.txt` is itself part of the detached proof, so its prose cannot be corrected in place without invalidating that proof. Treat only the digest binding and trusted-verifier result reported by `verify.sh` as status; a parsed attestation alone is never confirmation.

---

## 2 · Release-key attribution — a cryptographically signed release

`provenance/allowed_signers` contains the public half of a dedicated Ed25519 signing key. The sealed release is published as a **git tag signed** with the private half. The gate pins the historical bootstrap tag object and key digest, requires the current trust-root file and every canonical release's copy to remain byte-identical, and verifies every canonical tag with that root. A release therefore cannot authorize a replacement key merely by committing that key, replacing a recent tag, and signing the pair with it. Key rotation is intentionally unsupported until a separately reviewed old-key-authorized transition protocol exists.

- **What it proves.** That the holder of the private key produced this tag — binding the release to *your* key, not merely to a date.
- **What it does NOT prove.** Key attribution is exactly as strong as custody of the private key and the pinned historical public trust root. The private key lives only on the maintainer's machine (`~/.ssh/fabius_signing`), never in the repo. GitHub currently reports the release tag's SSH signature as **Verified**; the independent gate verifies the complete canonical chain with the pinned root, so the claim does not depend on GitHub's badge or a key introduced by the release being checked.

---

## 3 · Detection — an embedded, discoverable fingerprint

Every skill file carries a provenance marker:

```
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-… · release evidence: PROVENANCE.md -->
```

- **What it does.** It is a **tripwire** — but not a passive alarm: detection is not automatic. You (or a saved GitHub code-search alert) must periodically search for the token. It is high-entropy and unique to fabius, so a search surfaces any verbatim clone that is public, indexed, and still carries the comment — including the automated, "copy the whole repo and re-upload" theft that is by far the most common.
- **What it does NOT do.** It is *not* a barrier. A determined adversary can `grep -v` it out in seconds. It defeats lazy and automated copying, nothing stronger — and it says so.
- **What removal does and does not cost the thief.** Stripping the marker defeats the web-search tripwire, so the fingerprint protects only against **verbatim** copies that keep the comment. It is **not** re-derivable from stolen files — nothing in this repo reconstructs the token from content, and a content-bound value could not survive the rewording a determined thief would do anyway. The fingerprint is a convenience for *discovery* of lazy/verbatim clones; the durable *proof* lives in the timestamp and signature (§1, §2), not the comment.

### 3·b — A content-bound seal: a value anyone can recompute

The fingerprint above is a *discovery* aid; it is not derived from the content. `provenance/seal-manifest.json` adds the **content-bound** half: a SHA-256 over every skill contract (`skills/*/SKILL.md`) and the core system docs (`ARCHITECTURE.md`, `CORPUS.md`, `AGENTS.md`), plus a **binary Merkle root** over those leaves and the algorithm identifier. `bash provenance/seal-skills.sh` builds it; `verify.sh` recomputes it.

- **What it does.** Every value is recomputable from the files. The Merkle root commits the exact sealed file list at once. A digest-bound, Bitcoin-confirmed release record containing that manifest extends the block date to those exact bytes. A pending proof does not. Between an edit and the next re-seal + re-tag + re-stamp, new bytes are development state only.
- **What it does NOT do.** It binds the **exact expression**: rewording a skill changes its hash, by design. So it strengthens detection of **verbatim or substantial** copies and gives integrity (tamper-evidence) for this repo's own files — it does not reach an idea-level reimplementation, the same honest limit as everything here. This is **boring cryptography only** (a hash and a Merkle tree — no trusted setup, no token), drawn from fabius's own SEAL research; the primitive and its rules are documented in [`skills/fabius-catena/references/sealing.md`](skills/fabius-catena/references/sealing.md).

---

## 4 · Two repository records

- **No broad license granted (legal hook).** fabius is **publicly readable and proprietary** (`LICENSE`; `NOTICE` restates it for visibility). Public visibility is not a grant to copy or redistribute. Apply the actual LICENSE terms; proprietary status is not a standalone infringement finding.
- **Public git objects and signature status.** GitHub distributes the repository's commit and tag objects and reports signature-verification state. Git author/committer dates can be rewritten by rebase or amend, and activity feeds are not permanent timestamp archives, so neither replaces the independently verified OTS priority evidence in §1.

---

## 5 · The threat model, made explicit

| Adversary | What they do | What stops / catches them |
|---|---|---|
| **Automated scraper / re-uploader** | clone, re-publish verbatim | embedded fingerprint (§3) → web-search hit; an unlicensed copy may support a fact-specific infringement claim (§4) |
| **Lazy human** | fork, swap the README, claim it | fingerprint + signed tag + your earlier OTS date (§1–3) |
| **Determined plagiarist** | strip markers, reword, re-commit | the signed tag attributes exact bytes to a key and OTS can bound when their record existed; either may support a later comparison, but neither proves the other work is derivative, and the fingerprint cannot help once removed |
| **"I can just copy it"** | redistribute, drop your name | fabius grants **no broad license**; copying may infringe absent permission or an applicable exception, while idea-level reimplementations remain out of reach (§4) |
| **Anyone** | obtain & re-clone the repo | nothing prevents it — the repo is **public** and clonable by a stranger with no credentials (the honesty stance, up front); the seal (§1–4) plus the absence of any license grant (§4) is the *whole* defense, not a backstop |

What this package **cannot** stop: a determined actor who rewrites fabius from scratch using only the *ideas*. This apparatus binds exact expression, release-key attribution and priority evidence; it neither protects ideas nor decides ownership or infringement. That gap is real and is the price of publishing.

---

## 6 · Verify everything (from a clean clone)

```bash
bash provenance/verify.sh
```

It checks, in order: fingerprint coverage; anchor commit ancestry; **dependency-free detached OTS structure and digest binding before reading any attestation**; trusted Bitcoin verification of the same parsed block when the external verifier is available; pending vs Bitcoin-confirmed state; pinned historical signing-key continuity across every canonical tag; every sealed file hash and Merkle root; and whether the anchor record/tag contain the current manifest. A proof swap from another release is a failure even if that proof has a valid Bitcoin attestation. A pending proof remains a NOTE, never a Bitcoin PASS.

```bash
shasum -a 256 skills/*/SKILL.md ARCHITECTURE.md CORPUS.md AGENTS.md                # content-bound seal — compare to provenance/seal-manifest.json
node scripts/verify-ots-binding.mjs                                               # dependency-free detached structure + exact record digest
ots info provenance/sealed-commit.txt.ots                                         # compare File sha256 hash to: shasum -a 256 provenance/sealed-commit.txt
ots verify provenance/sealed-commit.txt.ots                                       # then verify the matching proof's attestation
git -c gpg.ssh.allowedSignersFile=provenance/allowed_signers \
    verify-tag "$(git tag --list 'v*-sealed*' --sort=-creatordate | head -1)"  # release-key attribution
grep -rl "provenance fab1-" skills/*/SKILL.md                                     # fingerprint coverage
```

After editing any top-level skill contract or core doc, rebuild the seal: `bash provenance/seal-skills.sh`. A new content release also needs a new version, release commit, anchor record/proof and signed tag. The human-gated sequence is in [`.github/RELEASE.md`](.github/RELEASE.md).

---

## 7 · If someone steals it — the enforcement playbook

1. **Capture evidence.** Archive the offending repo/page (URL + screenshot + `git clone` of the copy). Note the date.
2. **Assemble priority evidence.** First confirm the detached digest matches, then run `ots verify` and export the relevant Git history. If the proof has a Bitcoin attestation, its block date is one item of evidence; it is not by itself a complete authorship or infringement case.
3. **Evaluate the claim before filing.** Check the actual licence, permission, fair-use or other applicable exceptions, and substantial similarity; preserve the specific URLs and paths at issue. GitHub's current [submission guide](https://docs.github.com/en/site-policy/content-removal-policies/guide-to-submitting-a-dmca-takedown-notice) and [DMCA policy](https://docs.github.com/en/site-policy/content-removal-policies/dmca-takedown-policy) are authoritative. A notice contains legal statements made under penalty of perjury; obtain legal advice when the facts are uncertain.
4. **Use the host's current process.** For GitHub, use its current copyright channel and identify each allegedly infringing location. For another host or search engine, follow that provider's published process rather than assuming GitHub's form or timeline applies.
5. **Keep the evidence safe.** Back up the signing key, signed tag, sealed record, detached proof and captured comparison off-machine.

---

<div align="center">

**The bar, restated.** Not "unclonable" and not self-proving ownership — *inspectable evidence*. Exact bytes you can seal, priority you can anchor to Bitcoin, a release key you can verify, and verbatim copying you can sometimes detect. Honest about the one thing none of it does: stop a public repo from being cloned, decide a legal dispute, or prevent an idea from being re-implemented.

</div>
