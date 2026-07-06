# Fabius Catena — the on-chain & sealing toolkit (defensive)

Loaded on demand by `fabius-catena`. Best-in-class (2026) for the skill's two jobs — **(1) build & review on-chain code**, **(2) seal provenance** — **defensive only** (audit/harden/verify, never exploit tooling). The analyzers are mostly **copyleft** (`AGPL`/`GPL`) — fine to run as a CLI, but a source-disclosure trigger if you *bundle* them into a distributed service; flagged below. Honest note: **HuggingFace has no strong, maintained production on-chain models** — the one defensible artifact is a labeled vuln dataset; the real strength here is deterministic tools.

## Job 1 — EVM

| Tool | License | Note |
|---|---|---|
| **Foundry** | Apache/MIT | *Default EVM backbone* — `forge test` with **fuzz + invariant** tests is the money-safe gate; `anvil --fork-url` = throwaway mainnet fork for on-chain reads/writes without gas. |
| **OpenZeppelin Contracts** | MIT | **The "don't-roll-your-own" library** — audited ReentrancyGuard, AccessControl/Ownable, SafeERC20, ERC-20/721/1155. The literal embodiment of *money-safe by default*. |
| **Hardhat 3** | MIT | TS-first environment (v3 rewrite, Rust-backed) + Ignition reproducible deploys — for JS/TS stacks. |
| **viem** | MIT | Default modern TS client (reads/writes/typed contracts); its native **`signTypedData` (EIP-712)** is the exact primitive for the signed, content-bound attestations in Job 2. |
| **ethers.js** (MIT) · **wagmi** (MIT) | MIT | ethers for legacy/SDK interop; wagmi (React hooks) only for a dApp UI. |
| **web3.py** | MIT | Python client — repo moved to **`ApeWorX/web3.py`** (pin the canonical URL); use `eth-account` for typed-data signing. |

## Job 1 — Solana

| Tool | License | Note |
|---|---|---|
| **Anchor** | Apache-2.0 | Default program framework — `#[account(...)]` constraints **enforce the account-validation-first rule** + emit the TS IDL client. (Repo now under `solana-foundation`.) |
| **Solana Kit** (@solana/kit) | MIT | Modern tree-shakeable TS client (the renamed web3.js 2.x); full break from 1.x. |
| **LiteSVM** | Apache-2.0 | Fast in-process test VM — the Solana test gate (assert behavior, incl. clock/compute-budget, before mainnet). |
| **Pinocchio** | Apache-2.0 | Zero-dep low-CU programs — but **NOT feature-complete and UNAUDITED** per Solana's docs; hand-rolls account validation → raises the review bar. Anchor stays the safe default. |

## Job 1 — defensive analysis

Run all three layers: **static → fuzz → symbolic.** Copyleft as noted.

| Tool | License | Layer |
|---|---|---|
| **Slither** | ⚠️ AGPL-3.0 | Static — 90+ detectors, the default first-pass CI gate. |
| **Aderyn** (Cyfrin) | ⚠️ GPL-3.0 | Static — fast Rust, Markdown reports double as an audit deliverable. Fewer detectors — pair with Slither. |
| **Wake** (Ackee) | **ISC** | Static **+** fuzz in one Python tool — the most redistribution-friendly if catena ever bundles an analyzer. |
| **Echidna** | ⚠️ AGPL-3.0 | Fuzz — property/invariant testing (declare invariants, let it try to break them). |
| **Medusa** (Trail of Bits) | ⚠️ AGPL-3.0 | Fuzz — parallel, coverage-guided; reach for it over Echidna on large state spaces. |
| **Halmos** (a16z) | ⚠️ AGPL-3.0 | Symbolic — bounded formal verification of existing Foundry tests (no new spec language). |

> **Flagged:** **Mythril** is maintenance-stale (last release Mar 2024) — an optional extra, not a primary gate.

## Job 2 — provenance sealing (boring cryptography only)

- **noble-curves** (MIT) + **@noble/hashes** (MIT) — audited, zero-dep signatures (secp256k1/ed25519, same curves as EVM+Solana keys) and keccak/sha for the content-bound hash. The "boring cryptography" the skill mandates.
- **OpenTimestamps** (LGPL-3.0) — the Bitcoin-anchored, offline-verifiable timestamp. **Use the maintained Python `opentimestamps-client`** as the primitive — the `javascript-opentimestamps` lib is effectively unmaintained (last release 2019). The proof needs an "upgrade" step after Bitcoin confirms.
- **Sigstore Cosign** (Apache-2.0) + **in-toto** (Apache-2.0) — keyless `sign-blob` + a signed **supply-chain attestation** of *how* an artifact was produced (public Rekor log; a privacy trade-off vs. offline sealing). Rounds out "hash + signature + timestamp + attested chain".

## HuggingFace — honestly minimal

No strong maintained production on-chain models exist. The one defensible resource: **`mwritescode/slither-audited-smart-contracts`** (MIT dataset) — ~113k contracts multilabeled with Slither vuln classes, *only* for training/benchmarking a vuln classifier (labels are Slither output, not human ground truth — inherits its false positives). The real strength is the deterministic tools above.

## Pairs with

`fabius-catena` (the account-validation-first + sealing playbooks), `fabius-praesidium` (defensive posture, supply-chain — both hard-defensive, no offense), and `fabius-parcus` (OpenZeppelin over a hand-rolled primitive; the least code that's money-safe).
