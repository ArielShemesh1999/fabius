<div align="center">

# Provenance & authorship of fabius

### How ownership of fabius is *proven*, not asserted — stated honestly, with the limits up front.

</div>

fabius is original work. This document is the apparatus that lets anyone inspect **what was sealed**, **which key signed it**, and whether its detached OpenTimestamps proof is merely calendar-attested or actually Bitcoin-confirmed. Six mechanisms back that up: three repository facts — the fingerprint (§3), proprietary copyright notice (§4), and GitHub history (§4); one recomputable content-bound seal (§3·b); and two release artifacts — the digest-bound OpenTimestamps proof (§1) and signed tag (§2). `bash provenance/verify.sh` reports the live state. A pending proof is not called Bitcoin-confirmed.

**The honesty stance, up front.** A public git repository **cannot be made uncloneable.** That is not a missing setting — it is how git works: anyone who can read the repo can `git clone` it in full, history included. Disabling forks does not stop it. No code, license, or watermark changes this. Anyone who promises a "clone-proof" public repo is selling a fiction.

So this package does not attempt prevention. It combines three kinds of evidence:

1. **Priority** — after Bitcoin confirmation, places an independently checkable upper bound on when the exact digest-bound record existed. It does not prove that no earlier copy existed.
2. **Key attribution** — binds a release tag to the holder of the committed signing key; key custody determines the strength of that attribution.
3. **Detection & enforcement support** — makes some public verbatim clones searchable and preserves evidence useful to a fact-specific enforcement process.

The one true way to keep an *idea* from being copied is to not publish it. Once it is public, ownership is defended by **provenance and enforcement, not by a lock.** This document is that defense.

---

## 1 · Priority evidence (OpenTimestamps → Bitcoin)

The strongest evidence of ownership is a timestamp no one can backdate. A thief can copy your files; they cannot copy a date that predates their copy.

At seal time, `provenance/sealed-commit.txt` records the full git commit hash and tree hash of the sealed release. A commit hash covers the tracked tree, commit metadata and parent links. The adjacent `.ots` file is a detached proof over the record's SHA-256. `verify.sh` first compares the digest embedded in that proof with a fresh SHA-256 of the record; only a matching proof can be considered. Calendar attestations are the pending state. A `BitcoinBlockHeaderAttestation` is the confirmed state.

- **What it proves after Bitcoin confirmation.** That the digest-bound sealed record — and therefore the commit/tree it names — existed no later than the attested block. Before confirmation it proves only that calendar servers accepted the digest; it has no Bitcoin block date yet.
- **What it does NOT prove.** Existence-by-a-date is not, by itself, authorship — it proves the *data* was there, not that *you* are the only one who had it. Its power is in combination (§2, §4): priority date **+** your signature **+** GitHub's retained push history (public and independently checkable, §4) makes "I had it first, signed, third-party-recorded" provable from three independent directions.
- **Honest caveat.** A fresh proof starts pending and may later upgrade to a Bitcoin attestation. Run `bash provenance/upgrade-seal.sh` when available; it checks detached-digest binding before the upgrade and never commits or pushes. Never infer confirmation from the file's presence or prose. `verify.sh` is the live state check.
- **Legacy record wording.** The current v2.6.2 `sealed-commit.txt` is itself the immutable bytes covered by the detached proof, so changing its legacy sentence would invalidate that proof. The sentence uses “anchored” more broadly than this document does. Treat only the parsed attestation reported by `verify.sh` as status; today the bundled proof is digest-bound and pending, not Bitcoin-confirmed.

---

## 2 · Authorship — a cryptographically signed release

`provenance/allowed_signers` contains the public half of a dedicated Ed25519 signing key. The sealed release is published as a **git tag signed** with the private half. `git verify-tag` confirms the signature against the committed public key.

- **What it proves.** That the holder of the private key produced this tag — binding the release to *your* key, not merely to a date.
- **What it does NOT prove.** Authorship is exactly as strong as your custody of the private key. The key lives only on your machine (`~/.ssh/fabius_signing`), never in the repo. It is not yet a GitHub green **"Verified"** badge — that requires uploading the public key to your account (`gh auth refresh -h github.com -s admin:ssh_signing_key` then `gh ssh-key add ~/.ssh/fabius_signing.pub --type signing`). The local signature is independently verifiable today regardless.

---

## 3 · Detection — an embedded, discoverable fingerprint

Every skill file carries a provenance marker:

```
<!-- © 2026 Ariel Shemesh · fabius · provenance fab1-… · authenticity proof: PROVENANCE.md -->
```

- **What it does.** It is a **tripwire** — but not a passive alarm: detection is not automatic. You (or a saved GitHub code-search alert) must periodically search for the token. It is high-entropy and unique to fabius, so a search surfaces any verbatim clone that is public, indexed, and still carries the comment — including the automated, "copy the whole repo and re-upload" theft that is by far the most common.
- **What it does NOT do.** It is *not* a barrier. A determined adversary can `grep -v` it out in seconds. It defeats lazy and automated copying, nothing stronger — and it says so.
- **What removal does and does not cost the thief.** Stripping the marker defeats the web-search tripwire, so the fingerprint protects only against **verbatim** copies that keep the comment. It is **not** re-derivable from stolen files — nothing in this repo reconstructs the token from content, and a content-bound value could not survive the rewording a determined thief would do anyway. The fingerprint is a convenience for *discovery* of lazy/verbatim clones; the durable *proof* lives in the timestamp and signature (§1, §2), not the comment.

### 3·b — A content-bound seal: a value anyone can recompute

The fingerprint above is a *discovery* aid; it is not derived from the content. `provenance/seal-manifest.json` adds the **content-bound** half: a SHA-256 over every skill contract (`skills/*/SKILL.md`) and the core system docs (`ARCHITECTURE.md`, `CORPUS.md`, `AGENTS.md`), plus a **binary Merkle root** over those leaves and the algorithm identifier. `bash provenance/seal-skills.sh` builds it; `verify.sh` recomputes it.

- **What it does.** Every value is recomputable from the files. The Merkle root commits the exact sealed file list at once. A digest-bound, Bitcoin-confirmed release record containing that manifest extends the block date to those exact bytes. A pending proof does not. Between an edit and the next re-seal + re-tag + re-stamp, new bytes are development state only.
- **What it does NOT do.** It binds the **exact expression**: rewording a skill changes its hash, by design. So it strengthens detection of **verbatim or substantial** copies and gives integrity (tamper-evidence) for this repo's own files — it does not reach an idea-level reimplementation, the same honest limit as everything here. This is **boring cryptography only** (a hash and a Merkle tree — no trusted setup, no token), drawn from fabius's own SEAL research; the primitive and its rules are documented in [`skills/fabius-catena/references/sealing.md`](skills/fabius-catena/references/sealing.md).

---

## 4 · Two records you already hold for free

- **No broad license granted (legal hook).** fabius is **publicly readable and proprietary** (`LICENSE`; `NOTICE` restates it for visibility). Public visibility is not a grant to copy or redistribute. Apply the actual LICENSE terms; proprietary status is not a standalone infringement finding.
- **GitHub's retained history (third-party record).** Every commit and push to this GitHub repo is timestamped and retained by a neutral third party (the repo is public, so this record is already openly visible and independently checkable by anyone, not merely producible on request). Your commit timeline is corroborating evidence of priority, independent of §1.

---

## 5 · The threat model, made explicit

| Adversary | What they do | What stops / catches them |
|---|---|---|
| **Automated scraper / re-uploader** | clone, re-publish verbatim | embedded fingerprint (§3) → web-search hit; unlicensed copy = infringement (§4) |
| **Lazy human** | fork, swap the README, claim it | fingerprint + signed tag + your earlier OTS date (§1–3) |
| **Determined plagiarist** | strip markers, reword, re-commit | OTS priority date + GitHub history (§1, §4) give priority + authorship evidence that *supports* a substantial-similarity claim — but priority alone does not prove their copy is a derivative; that needs a similarity analysis a court performs, and the fingerprint cannot help once they reword |
| **"I can just copy it"** | redistribute, drop your name | fabius grants **no** license — any verbatim/substantial copy is infringement from the first byte (§4); idea-level reimplementations are out of reach |
| **Anyone** | obtain & re-clone the repo | nothing prevents it — the repo is **public** and clonable by a stranger with no credentials (the honesty stance, up front); the seal (§1–4) plus the absence of any license grant (§4) is the *whole* defense, not a backstop |

What this package **cannot** stop: a determined actor who rewrites fabius from scratch using only the *ideas*. Ideas are not protected by any of this — only the expression, the date, and the authorship are. That gap is real and is the price of publishing.

---

## 6 · Verify everything (from a clean clone)

```bash
bash provenance/verify.sh
```

It checks, in order: fingerprint coverage; anchor commit ancestry; **detached OTS digest binding before reading any attestation**; pending vs Bitcoin-confirmed state; allowed-signature tag; every sealed file hash and Merkle root; and whether the anchor record/tag contain the current manifest. A proof swap from another release is a failure even if that proof has a valid Bitcoin attestation. A pending proof remains a NOTE, never a Bitcoin PASS.

```bash
shasum -a 256 skills/*/SKILL.md ARCHITECTURE.md CORPUS.md AGENTS.md                # content-bound seal — compare to provenance/seal-manifest.json
ots info provenance/sealed-commit.txt.ots                                         # compare File sha256 hash to: shasum -a 256 provenance/sealed-commit.txt
ots verify provenance/sealed-commit.txt.ots                                       # then verify the matching proof's attestation
git -c gpg.ssh.allowedSignersFile=provenance/allowed_signers \
    verify-tag "$(git tag --list 'v*-sealed*' --sort=-creatordate | head -1)"  # authorship
grep -rl "provenance fab1-" skills/*/SKILL.md                                     # fingerprint coverage
```

After editing any top-level skill contract or core doc, rebuild the seal: `bash provenance/seal-skills.sh`. A new content release also needs a new version, release commit, anchor record/proof and signed tag. The human-gated sequence is in [`.github/RELEASE.md`](.github/RELEASE.md).

---

## 7 · If someone steals it — the enforcement playbook

1. **Capture evidence.** Archive the offending repo/page (URL + screenshot + `git clone` of the copy). Note the date.
2. **Assemble priority evidence.** First confirm the detached digest matches, then run `ots verify` and export the relevant Git history. If the proof has a Bitcoin attestation, its block date is one item of evidence; it is not by itself a complete authorship or infringement case.
3. **File a DMCA takedown.** Use GitHub's copyright form at `https://github.com/contact/dmca` (fastest), email `copyright@github.com`, or postal mail. A valid notice must include: your original work (`github.com/shear559/fabius`) **and the specific infringing URLs/paths in the clone**; your name, email, and physical address; a good-faith-belief statement; a statement, **under penalty of perjury**, that the information is accurate and that you are the owner or authorized to act for them; and your signature; cite the retained-notice violation and your timestamp proof. GitHub reviews the notice for these required elements and, if complete, notifies the user and generally gives them about a day to act before disabling the content; the user may file a counter-notice that can restore it. GitHub recommends contacting the user first. A DMCA notice is sworn under penalty of perjury — a baseless or overbroad one can expose **you** to liability under 17 U.S.C. §512(f), so file only for an actual verbatim or substantial copy.
4. **For non-GitHub hosts**, send the same notice to the host's abuse/DMCA contact and, if indexed, to the search engine.
5. **Keep the key safe.** Your signing key and your `.ots` proof are the spine of every claim — back them up off-machine.

---

<div align="center">

**The bar, restated.** Not "unclonable" — *provable*. Priority you can anchor to Bitcoin, authorship you can sign, copying you can detect, and a license violation you can act on. Honest about the one thing none of it does: stop a public repo from being cloned, or an idea from being re-implemented.

</div>
