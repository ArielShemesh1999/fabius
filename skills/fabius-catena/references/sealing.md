# Fabius Catena — the sealing primitive

The on-demand depth for `fabius-catena`'s provenance concern. The skill is the contract (hash → sign → anchor → verify); this is how you actually run it, and how `fabius` seals its **own** skills. Boring cryptography only. Scout wide, strike narrow.

## The guarantee — provenance, not truth

Sealing does **not** prove an artifact is good, true, or original. It proves something narrower and achievable: that this is **exactly what was registered, by which key, and when** — re-checkable by anyone, indefinitely, with **no trusted third party**. In the generative-AI era, appearance has stopped being evidence ("it looks genuine" proves nothing) and bit-exact hashes are brittle under lawful format migration. The trustworthy question is no longer *does it look real* but *is this exactly what was registered, by which key, when* — and that is a question of provenance you can answer with math.

- **Proves:** existence-at-a-date (un-backdatable), binding to a signing key (possession), and integrity of the exact bytes.
- **Does NOT prove:** authorship of the *ideas* (a seal is an attestation of **possession, not origination** — multi-attestation is allowed by design), nor that the content is honest. It inverts the burden of proof: **unsealed content becomes the suspect class.**

## The primitive — four parts, each a public recomputable fact

```
seal(artifact) = { exactHash, signature, timestampProof, bundle }
```

1. **Hard-bind the bytes** — `exactHash = H(artifact)` with a collision-resistant hash (SHA-256 / keccak-256). Forging a seal for different content requires a **hash collision**, which is a public, detectable event. There is no shielded region where a forgery can hide.
2. **Sign the commitment** — an **EUF-CMA** signature (e.g. Ed25519 / ECDSA / EIP-712 typed data on EVM) over the structured commitment, binding it to the author's key. The private key never leaves the author's machine.
3. **Anchor the time** — terminate the timestamp in **Bitcoin** via OpenTimestamps so it can't be backdated, even by a malicious sequencer of any L2 you also use. The priority date is math against the public chain, attested by no one.
4. **Export a self-contained bundle** — everything a verifier needs (the hash, the signature, the public key, the timestamp proof, and the algorithm identifiers) so verification runs **offline, client-side, after any operator, indexer, or even the ledger is gone.**

Verification is free and runs anywhere: recompute `H(artifact)`, check it equals `exactHash`, verify the signature against the pinned key, and confirm the timestamp proof against the chain.

**What needs an external service.** Hashing, signing, and verification are **local** — no network, no account. Only the timestamp *anchor* reaches an external service (an **OpenTimestamps** calendar → Bitcoin); it is the one optional live-tier dependency, and even an un-anchored seal still binds content and authorship. fabius bundles none of it (see [the catena skill](../SKILL.md) and [ARCHITECTURE.md](../../../ARCHITECTURE.md) → *External connections*).

## The five rules of the trust core

The deepest commitment, drawn from the cryptographic-failure record (BCTV14's undetectable counterfeit, "Frozen Heart", even Bitcoin's own CVE-2018-17144): **the trust core must be boring.**

1. **Boring cryptography only.** Lean on collision-resistant hashing, EUF-CMA signatures, Merkle trees, and ledger persistence — **no trusted setup, no SNARK, no oracle, no token** in the core. Nothing about integrity may depend on the price, issuance, or governance of any asset. **Rely on the cryptographic signature — never on a coin.**
2. **Detectability by construction.** Every claim a seal makes is recomputable from public data; a forgery requires a hash collision (a public event), so a forged seal cannot exist unobserved.
3. **Additivity.** Frontier components (zkVM proofs, on-chain anchoring) may *add* capability — but each can fail to zero, and the seal degrades exactly to the core guarantee and not one inch below.
4. **Diversity.** No single codebase is ever the sole witness to a registry's correctness — independent implementations and recomputation are the antidote to a monoculture bug.
5. **Scheduled mortality.** Every algorithm in use today eventually falls. Make renewal a **calendar event, not an emergency** (next rule).

## Aggregate, renew, and (optionally) conceal

- **Merkle-aggregate a release.** Hash many files into a Merkle tree and seal the **root** once — one timestamp commits every file, and any single file proves membership with an inclusion proof. This is exactly how `fabius` seals all its skills at once (below).
- **Crypto-agile renewal.** Carry algorithm identifiers in the bundle and **re-anchor under fresh algorithms on a schedule** (ERS-style epochal renewal) so a seal made under today's cryptography stays provably "anchored before the break" decades from now. An optional post-quantum dual-signature (e.g. ML-DSA) hedges the archival horizon.
- **Confidential sealing (optional).** Seal a **salted commitment** so the on-chain record leaks nothing about the content (defeats dictionary / confirmation oracles), and use chunked Merkle commitments to release and prove a fragment later (selective disclosure). Only reach for this when the content is secret — `fabius-parcus`: does this need to exist yet?

## How fabius seals its own skills (the dogfood)

`fabius` is the worked example. Its provenance apparatus ([PROVENANCE.md](../../../PROVENANCE.md)) is this primitive applied to the repo:

- **Hard-bind:** `provenance/seal-manifest.json` records a content hash of every `skills/*/SKILL.md` (and the load-bearing docs) plus a **Merkle root** over them and the algorithm id — a *content-bound* seal that anyone can recompute from the files. (This is the upgrade SEAL motivates: the per-skill `fab1-…` comment is a discovery tripwire, but it is **not** content-derived; the manifest is.)
- **Sign + anchor:** the sealed release is a **signed git tag** (authorship) plus an **OpenTimestamps → Bitcoin** proof over the sealed commit (un-backdatable priority).
- **Verify offline:** `bash provenance/verify.sh` recomputes the manifest hashes and root, checks the fingerprint coverage, the sealed-commit ancestry, the Bitcoin attestation, and the signed tag — trusting no single party.

Re-seal after changing skills: `bash provenance/seal-skills.sh` (rebuilds the manifest), then re-tag and re-stamp per PROVENANCE.md §6.

### Verify MEMBERSHIP, not only content — the hole every manifest checker starts with

The natural way to write a verifier is to walk the manifest and re-hash each file it lists.
That proves nothing **listed** has changed, and it is blind by construction to a file that
was **added** after sealing, because the loop never visits it. A dropped-in contract
carrying a copied fingerprint comment therefore passes a fingerprint check, passes every
hash in the manifest, and still reaches whatever consumes the sealed set.

So the verifier needs two independent legs, and they answer different questions:

```python
on_disk = set(glob("skills/*/SKILL.md")) | {"ARCHITECTURE.md", "CORPUS.md", "AGENTS.md"}
listed  = set(manifest["files"])
for p in on_disk - listed: fail("UNSEALED file present:", p)   # ← the added-file leg
for p in listed - on_disk: fail("sealed file missing:",   p)   # ← the removed-file leg
for p, h in manifest["files"].items(): check_hash(p, h)        # ← the content leg
```

The general rule, and it outlives this repo: **a seal defines a SET, not just a list of
hashes.** Any verifier that cannot say "these files and no others" is answering a weaker
question than the one people think it answered. State the set membership rule explicitly
somewhere machine-readable, so the verifier derives the expected set rather than trusting
the manifest to describe itself.

The same asymmetry applies wherever a sealed artifact is *consumed*, not just checked: a
loader that reads a sealed set should be able to refuse anything outside it. fabius's local
runtime takes `--sealed-only` for exactly this — the seal becomes a gate instead of a
report (→ `../../fabius-cohors/references/local-agent-runtime.md`).

## The honest limits

A public git repo **cannot be made uncloneable** — that is how git works, and no seal changes it. Sealing defends ownership by **provenance and enforcement, not by a lock**: priority you can anchor to Bitcoin, authorship you can sign, copying you can detect. It does not protect *ideas* — only the expression, the date, and the authorship. Claim exactly that and no more.

---

Drawn from **SEAL** — *A Universal Cryptographic Sealing Primitive for Digital File Provenance in the Age of Generative AI* (v2.0), Ariel Shemesh's own research (`research/SEAL_Whitepaper_v2.0`). The findings are the author's; this doc re-expresses the buildable bit-exact spine in fabius's own voice.
