<div align="center">

# Provenance & authorship of fabius

### How ownership of fabius is *proven*, not asserted — stated honestly, with the limits up front.

</div>

fabius is original work. This document is the apparatus that lets anyone — a court, a maintainer, a stranger — confirm **when it existed**, anchored to Bitcoin with no trusted party, and **who made it**, as strongly as the custody of one signing key allows. Six mechanisms back that up: three are plain repository facts — the fingerprint (§3), the MIT notice (§4), and GitHub's public push history (§4); one is a **content-bound seal** recomputable from the files themselves (§3·b); and two are cryptographic artifacts generated when the release is **sealed**: the Bitcoin timestamp (§1) and the signed release tag (§2). `bash provenance/verify.sh` reports the live state of each. Every mechanism is paired with exactly what it does *and does not* prove, in the same measured-not-claimed spirit as [RESEARCH.md](RESEARCH.md).

**The honesty stance, up front.** A public git repository **cannot be made uncloneable.** That is not a missing setting — it is how git works: anyone who can read the repo can `git clone` it in full, history included. Disabling forks does not stop it. No code, license, or watermark changes this. Anyone who promises a "clone-proof" public repo is selling a fiction.

So this package does not attempt prevention. It does three things that are real:

1. **Priority** — proves this exact work existed, in your hands, *before any copy could*. An un-forgeable date.
2. **Authorship** — binds the work to your cryptographic key.
3. **Detection & enforcement** — makes a lazy or automated clone *findable*, and gives you a clean, evidence-backed path to a takedown.

The one true way to keep an *idea* from being copied is to not publish it. Once it is public, ownership is defended by **provenance and enforcement, not by a lock.** This document is that defense.

---

## 1 · Priority — an un-forgeable date (OpenTimestamps → Bitcoin)

The strongest evidence of ownership is a timestamp no one can backdate. A thief can copy your files; they cannot copy a date that predates their copy.

At seal time, `provenance/sealed-commit.txt` records the full git commit hash and tree hash of the sealed release. A commit hash is the SHA over the root of a Merkle (hash) tree covering every tracked file, *plus* the commit metadata and parent links — so that one 40-character hash commits every file **and** the full ancestor history; change a single byte anywhere and the hash changes. (Git's object hash is SHA-1 by default: collision-weakened but still second-preimage-secure, and the OpenTimestamps anchor over the file uses SHA-256 — so backdating requires breaking the timestamp, not just git.) `provenance/sealed-commit.txt.ots` is the **OpenTimestamps** proof that anchors the SHA-256 of that file into the **Bitcoin blockchain**.

- **What it proves.** That the sealed commit — and therefore every file it contains — existed no later than the timestamp's Bitcoin block. This is checkable by anyone, forever, with no trusted third party: the proof is math against the public chain.
- **What it does NOT prove.** Existence-by-a-date is not, by itself, authorship — it proves the *data* was there, not that *you* are the only one who had it. Its power is in combination (§2, §4): priority date **+** your signature **+** GitHub's public push history makes "I had it first, signed, in public" provable from three independent directions.
- **Honest caveat.** A fresh OpenTimestamps proof is initially attested by calendar servers and *upgrades* to full Bitcoin confirmation within a few hours to a day. Run `ots upgrade provenance/sealed-commit.txt.ots` to pull the Bitcoin attestation once it is mined; `verify.sh` reports which state it is in.

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

- **What it does.** Unlike the comment, every value here is **recomputable from the public files** — a verifier hashes the bytes and compares. Forging a seal for altered content requires a **hash collision**, which is a public, detectable event (the *detectability-by-construction* property). The Merkle root commits all fifteen files at once, so the OpenTimestamps anchor over the sealed commit (§1) — which contains this manifest — extends an **un-backdatable date to the exact bytes of every skill**, not just to a comment.
- **What it does NOT do.** It binds the **exact expression**: rewording a skill changes its hash, by design. So it strengthens detection of **verbatim or substantial** copies and gives integrity (tamper-evidence) for this repo's own files — it does not reach an idea-level reimplementation, the same honest limit as everything here. This is **boring cryptography only** (a hash and a Merkle tree — no trusted setup, no token), drawn from fabius's own SEAL research; the primitive and its rules are documented in [`skills/fabius-catena/references/sealing.md`](skills/fabius-catena/references/sealing.md).

---

## 4 · Two records you already hold for free

- **MIT's attribution clause (legal hook).** fabius is MIT-licensed — permissive on use, but it makes one thing *binding*: the **copyright line and permission notice in `LICENSE`** "shall be included in all copies or substantial portions." (`NOTICE` restates that for visibility; MIT itself does not require a separate NOTICE file.) For a verbatim or substantial copy, stripping the notice means the copier never met the license condition, so the work is used outside the license — ordinary copyright infringement. You still must show they copied substantial protected expression; the notice point removes their license defense, it is not a standalone win.
- **GitHub's public history (third-party record).** Every commit and push to a public GitHub repo is timestamped and retained by a neutral third party. Your commit timeline is itself corroborating evidence of priority, independent of §1.

---

## 5 · The threat model, made explicit

| Adversary | What they do | What stops / catches them |
|---|---|---|
| **Automated scraper / re-uploader** | clone, re-publish verbatim | embedded fingerprint (§3) → web-search hit; MIT-notice violation (§4) |
| **Lazy human** | fork, swap the README, claim it | fingerprint + signed tag + your earlier OTS date (§1–3) |
| **Determined plagiarist** | strip markers, reword, re-commit | OTS priority date + GitHub history (§1, §4) give priority + authorship evidence that *supports* a substantial-similarity claim — but priority alone does not prove their copy is a derivative; that needs a similarity analysis a court performs, and the fingerprint cannot help once they reword |
| **"It's MIT, I can"** | redistribute, drop your name | MIT *requires* the notice in a verbatim/substantial copy — stripping it forfeits the license (→ infringement); idea-level reimplementations are out of reach (§4) |
| **Anyone** | "make it private so no one clones it" | the only thing that *prevents* cloning — out of scope here by your choice; see the honesty stance |

What this package **cannot** stop: a determined actor who rewrites fabius from scratch using only the *ideas*. Ideas are not protected by any of this — only the expression, the date, and the authorship are. That gap is real and is the price of publishing.

---

## 6 · Verify everything (from a clean clone)

```bash
bash provenance/verify.sh
```

It checks, in order: the fingerprint is intact in every skill; the sealed commit is in this branch's history; the OpenTimestamps proof (and whether it is Bitcoin-confirmed yet); the signed tag; and the **content-bound seal** — recomputing every sealed file's SHA-256 and the Merkle root against `provenance/seal-manifest.json`. The fingerprint and seal-manifest checks run today; the timestamp and signed-tag checks become meaningful **after the release is sealed** and report NOTE until then. Manual equivalents:

```bash
shasum -a 256 skills/*/SKILL.md ARCHITECTURE.md CORPUS.md AGENTS.md                # content-bound seal — compare to provenance/seal-manifest.json
ots verify provenance/sealed-commit.txt.ots                                       # priority date (Bitcoin)
git -c gpg.ssh.allowedSignersFile=provenance/allowed_signers \
    verify-tag "$(git tag --list 'v*-sealed' --sort=-version:refname | head -1)"  # authorship
grep -rl "provenance fab1-" skills/*/SKILL.md                                     # fingerprint coverage
```

After editing any skill or core doc, rebuild the seal so it stays valid: `bash provenance/seal-skills.sh` (then re-tag and re-stamp to refresh §1–§2).

---

## 7 · If someone steals it — the enforcement playbook

1. **Capture evidence.** Archive the offending repo/page (URL + screenshot + `git clone` of the copy). Note the date.
2. **Establish your priority.** Run `ots verify` on your proof and export your GitHub commit history. Your date predates theirs — that is the whole case.
3. **File a DMCA takedown.** Use GitHub's copyright form at `https://github.com/contact/dmca` (fastest), email `copyright@github.com`, or postal mail. A valid notice must include: your original work (`github.com/ArielShemesh1999/fabius`) **and the specific infringing URLs/paths in the clone**; your name, email, and physical address; a good-faith-belief statement; a statement, **under penalty of perjury**, that the information is accurate and that you are the owner or authorized to act for them; and your signature; cite the retained-notice violation and your timestamp proof. GitHub reviews the notice for these required elements and, if complete, notifies the user and generally gives them about a day to act before disabling the content; the user may file a counter-notice that can restore it. GitHub recommends contacting the user first. A DMCA notice is sworn under penalty of perjury — a baseless or overbroad one can expose **you** to liability under 17 U.S.C. §512(f), so file only for an actual verbatim or substantial copy.
4. **For non-GitHub hosts**, send the same notice to the host's abuse/DMCA contact and, if indexed, to the search engine.
5. **Keep the key safe.** Your signing key and your `.ots` proof are the spine of every claim — back them up off-machine.

---

<div align="center">

**The bar, restated.** Not "unclonable" — *provable*. Priority you can anchor to Bitcoin, authorship you can sign, copying you can detect, and a license violation you can act on. Honest about the one thing none of it does: stop a public repo from being cloned, or an idea from being re-implemented.

</div>
