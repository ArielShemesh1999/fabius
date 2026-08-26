#!/usr/bin/env bash
# Verify the fabius provenance package from a clean clone.
# Read-only: trusts no single party and mutates nothing — the timestamp
# reports a digest-bound OTS proof as pending or Bitcoin-confirmed, and verifies
# the signature against a key in the repo.
#
#   bash provenance/verify.sh [--require-confirmed]
#
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"
require_confirmed=0
case "${1:-}" in
  "") ;;
  --require-confirmed) require_confirmed=1 ;;
  *) echo "usage: bash provenance/verify.sh [--require-confirmed]"; exit 2 ;;
esac
ok=0; warn=0; fail=0
say(){ printf '%s\n' "$*"; }
pass(){ say "  PASS  $*"; ok=$((ok+1)); }
note(){ say "  NOTE  $*"; warn=$((warn+1)); }
bad(){  say "  FAIL  $*"; fail=$((fail+1)); }

say "== fabius provenance verification =="

# 1) Embedded provenance fingerprint is present in every skill --------------
marked=$(grep -rl "provenance fab1-" skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
total=$(ls -1 skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$marked" = "$total" ] && [ "$total" -gt 0 ]; then
  pass "provenance fingerprint present in all $total skills"
else
  bad "fingerprint present in only $marked/$total skills (tampered or stripped?)"
fi

# 2) Sealed commit hash is an ancestor of HEAD ----------------------------
if [ -f provenance/sealed-commit.txt ]; then
  sealed=$(grep -Eo '[0-9a-f]{40}' provenance/sealed-commit.txt | head -1)
  if git merge-base --is-ancestor "$sealed" HEAD 2>/dev/null; then
    pass "sealed commit $sealed is in this branch's history"
  elif git cat-file -e "$sealed^{commit}" 2>/dev/null; then
    note "sealed commit $sealed present but not an ancestor of HEAD (detached/other branch?)"
  else
    note "sealed commit $sealed not in local history (shallow clone? fetch full history)"
  fi
else
  note "provenance/sealed-commit.txt missing — release not sealed yet"
fi

# 3) OpenTimestamps detached proof ----------------------------------------
OTS=$(command -v ots || ls "$HOME"/Library/Python/*/bin/ots 2>/dev/null | head -1)
ots_bound=0
ots_confirmed=0
if [ -f provenance/sealed-commit.txt ] && [ -f provenance/sealed-commit.txt.ots ]; then
  # Binding and structural validity are release invariants, not optional
  # conveniences supplied by the external OTS client. The dependency-free
  # parser rejects malformed envelopes, wrong digests and trailing garbage.
  binding_output=$(node scripts/verify-ots-binding.mjs \
    provenance/sealed-commit.txt provenance/sealed-commit.txt.ots 2>&1)
  binding_code=$?
  if [ "$binding_code" -eq 0 ]; then
    ots_bound=1
    record_hash=$(shasum -a 256 provenance/sealed-commit.txt 2>/dev/null | awk '{print $1}')
    pass "OpenTimestamps proof is structurally valid and embeds the exact sealed-record SHA-256 ($record_hash)"
  else
    bad "OpenTimestamps detached proof is malformed or not bound to provenance/sealed-commit.txt — $binding_output"
  fi
elif [ -f provenance/sealed-commit.txt.ots ]; then
  bad "OpenTimestamps proof exists without provenance/sealed-commit.txt"
else
  note "OpenTimestamps detached proof absent — release not sealed yet"
fi

if [ "$ots_bound" -eq 1 ] && [ -n "${OTS:-}" ]; then
  # The Bitcoin attestation is embedded IN the proof file — `ots info` reads it
  # with no Bitcoin node. (`ots verify` additionally cross-checks the block
  # header against a node/explorer; absence of a node is not "unconfirmed".)
  info=$("$OTS" info provenance/sealed-commit.txt.ots 2>&1)
  proof_hash=$(printf '%s\n' "$info" | sed -n 's/^File sha256 hash: \([0-9a-fA-F]\{64\}\)$/\1/p' | head -1 | tr 'A-F' 'a-f')
  record_hash=$(shasum -a 256 provenance/sealed-commit.txt 2>/dev/null | awk '{print $1}')
  if [ -z "$proof_hash" ]; then
    bad "OpenTimestamps proof does not expose a detached file digest — refusing attestation claims"
  elif [ "$proof_hash" != "$record_hash" ]; then
    bad "OpenTimestamps proof digest MISMATCH — proof covers $proof_hash, sealed-commit.txt is $record_hash"
  else
    pass "external OTS parser independently reports the same detached digest"
    info_blocks=$(printf '%s' "$info" | grep -oiE "BitcoinBlockHeaderAttestation\([0-9]+\)" | grep -oE "[0-9]+")
    block=$(printf '%s\n' "$info_blocks" | head -1)
    if [ -n "$block" ]; then
      # `ots info` only parses bytes supplied by the proof. A forged proof can
      # contain a syntactically valid BitcoinBlockHeaderAttestation, so parsing
      # it is never confirmation. Require the OTS verifier to validate the
      # attestation against its trusted Bitcoin source and the exact record.
      verify_code=0
      verify_out=$("$OTS" verify -f provenance/sealed-commit.txt provenance/sealed-commit.txt.ots 2>&1) || verify_code=$?
      if [ "$verify_code" -eq 0 ]; then
        trusted_block=$(printf '%s\n' "$verify_out" | sed -n 's/^Success! Bitcoin block \([0-9][0-9]*\) attests existence.*$/\1/p' | head -1)
        if [ -n "$trusted_block" ] && printf '%s\n' "$info_blocks" | grep -Fxq "$trusted_block"; then
          ots_confirmed=1
          pass "OpenTimestamps proof trusted-verifies against Bitcoin block $trusted_block"
        else
          bad "OpenTimestamps verifier success did not bind a parsed Bitcoin attestation — NOT confirmed"
        fi
      elif printf '%s\n' "$verify_out" | grep -qiE 'Could not connect to (local )?Bitcoin node|No Bitcoin node (is |was )?(available|configured)|Not checking Bitcoin attestation; Bitcoin disabled|Connection refused'; then
        note "proof contains a digest-bound Bitcoin block attestation for block $block, but trusted verification is unavailable — NOT confirmed"
      else
        bad "OpenTimestamps Bitcoin attestation failed trusted verification — NOT confirmed (ots verify exit $verify_code)"
      fi
    elif printf '%s' "$info" | grep -qi "PendingAttestation"; then
      note "digest-bound OTS proof present but still pending Bitcoin confirmation — run: $OTS upgrade provenance/sealed-commit.txt.ots"
    else
      note "digest-bound OTS proof present but no recognizable attestation — inspect: $OTS info provenance/sealed-commit.txt.ots"
    fi
  fi
elif [ "$ots_bound" -eq 1 ]; then
  note "digest-bound OTS proof is structurally valid, but the external ots client is unavailable — attestation status not evaluated"
fi
if [ "$require_confirmed" -eq 1 ] && [ "$ots_confirmed" -ne 1 ]; then
  bad "Bitcoin confirmation is required for a provenance-only proof upgrade"
fi

# 4) Signed tag (key attribution + release-to-release continuity) ---------
if [ -f provenance/allowed_signers ]; then
  bootstrap_tag=v1.0.0-sealed
  bootstrap_object_expected=87b0e8d3458bc21a6e231cfaa63b3f14c128435f
  bootstrap_key_sha_expected=a3e825409eb5abe1030632fd414d95eb481fc93cf1a546ed692e83df3e6278bd # gitleaks:allow — public-key digest, not a credential
  canonical_tags=$(git tag --list 'v*-sealed*' --sort=-version:refname \
    | awk '/^v[0-9]+\.[0-9]+\.[0-9]+-sealed$/')
  tag=$(printf '%s\n' "$canonical_tags" | sed -n '1p')
  trust_file=$(mktemp "${TMPDIR:-/tmp}/fabius-signers.XXXXXX") || trust_file=""
  if [ -z "$tag" ]; then
    note "no canonical *-sealed tag found locally (fetch tags: git fetch --tags), or release not sealed yet"
  elif [ -z "$trust_file" ]; then
    bad "could not create a temporary historical trust file"
  else
    git show "$bootstrap_tag:provenance/allowed_signers" > "$trust_file" 2>/dev/null || :
    bootstrap_object=$(git rev-parse "refs/tags/$bootstrap_tag" 2>/dev/null || :)
    bootstrap_key_sha=$(shasum -a 256 "$trust_file" 2>/dev/null | awk '{print $1}')
    if [ "$bootstrap_object" != "$bootstrap_object_expected" ] \
       || [ "$bootstrap_key_sha" != "$bootstrap_key_sha_expected" ]; then
      bad "historical signing bootstrap object or key digest does not match the pinned trust root"
    elif ! cmp -s "$trust_file" provenance/allowed_signers; then
      bad "current allowed_signers differs from the pinned historical trust root"
    else
      chain_ok=1
      chain_failures=""
      for candidate in $canonical_tags; do
        candidate_type=$(git cat-file -t "refs/tags/$candidate" 2>/dev/null || :)
        if [ "$candidate_type" != tag ]; then
          chain_ok=0; chain_failures="$chain_failures $candidate:not-annotated"
        fi
        if ! git show "$candidate:provenance/allowed_signers" 2>/dev/null | cmp -s - "$trust_file"; then
          chain_ok=0; chain_failures="$chain_failures $candidate:trust-root-drift"
        fi
        if ! git -c "gpg.ssh.allowedSignersFile=$trust_file" verify-tag "$candidate" 2>&1 | grep -qi "Good .*signature"; then
          chain_ok=0; chain_failures="$chain_failures $candidate:bad-signature"
        fi
      done
      if [ "$chain_ok" -eq 1 ]; then
        tag_count=$(printf '%s\n' "$canonical_tags" | grep -c . | tr -d ' ')
        pass "all $tag_count canonical release tags preserve and verify against the pinned historical trust root"
      else
        bad "canonical release signature chain failed:$chain_failures"
      fi
    fi
  fi
  [ -z "$trust_file" ] || rm -f "$trust_file"
else
  bad "provenance/allowed_signers missing"
fi

# 5) Content-bound seal — recompute every sealed file's hash + the merkle root --
if [ -f provenance/seal-manifest.json ]; then
  count=$(grep -o '"count": [0-9]*' provenance/seal-manifest.json | grep -o '[0-9]*' | head -1)
  if command -v python3 >/dev/null 2>&1; then
    if python3 - <<'PY'
import glob, hashlib, json, sys
m = json.load(open("provenance/seal-manifest.json"))
bad = 0
# MEMBERSHIP FIRST. Hashing only the files the manifest lists proves that nothing
# LISTED changed — it cannot notice a contract that was ADDED after sealing, because
# the loop never visits it. An added skill carrying a copied fingerprint would
# otherwise pass every other leg of this script while reaching the model unsealed.
# The sealed set is exactly: every skills/*/SKILL.md plus the three canonical docs.
on_disk = set(glob.glob("skills/*/SKILL.md")) | {"ARCHITECTURE.md", "CORPUS.md", "AGENTS.md"}
listed = set(m["files"])
for p in sorted(on_disk - listed):
    print("    UNSEALED file present:", p); bad += 1
for p in sorted(listed - on_disk):
    print("    sealed file no longer on disk:", p); bad += 1
for p, h in m["files"].items():
    try:
        d = hashlib.sha256(open(p, "rb").read()).hexdigest()
    except FileNotFoundError:
        print("    missing sealed file:", p); bad += 1; continue
    if d != h:
        print("    hash mismatch:", p); bad += 1
leaves = sorted(hashlib.sha256((p + "\x00" + h).encode("utf-8")).digest() for p, h in m["files"].items())
lvl = leaves
while len(lvl) > 1:
    lvl = [hashlib.sha256(lvl[i] + (lvl[i + 1] if i + 1 < len(lvl) else lvl[i])).digest() for i in range(0, len(lvl), 2)]
if (lvl[0].hex() if lvl else "") != m.get("merkle_root"):
    print("    merkle root mismatch"); bad += 1
sys.exit(1 if bad else 0)
PY
    then
      pass "content-bound seal verified — all ${count:-?} sealed files match their sha256 and the merkle root recomputes"
    else
      bad "content-bound seal MISMATCH — a sealed file changed since sealing (see above). If intended, re-run: bash provenance/seal-skills.sh"
    fi
  else
    note "python3 absent — skipped the seal recompute (each file is still checkable by hand: shasum -a 256 <path> vs provenance/seal-manifest.json)"
  fi
else
  note "provenance/seal-manifest.json missing — create the content-bound seal: bash provenance/seal-skills.sh"
fi

# 6) Seal freshness — the release anchor/proof must cover the CURRENT manifest --
if [ -f provenance/seal-manifest.json ] && [ -n "${sealed:-}" ] && git cat-file -e "$sealed^{commit}" 2>/dev/null; then
  if git cat-file -e "$sealed:provenance/seal-manifest.json" 2>/dev/null \
     && git show "$sealed:provenance/seal-manifest.json" 2>/dev/null | cmp -s - provenance/seal-manifest.json; then
    if [ "$ots_confirmed" -eq 1 ]; then
      pass "Bitcoin-confirmed sealed commit contains the current seal manifest — the block date covers every sealed file"
    elif [ "$ots_bound" -eq 1 ]; then
      pass "digest-bound pending OTS record contains the current seal manifest — Bitcoin confirmation is not claimed yet"
    else
      note "sealed commit contains the current manifest, but no digest-bound OTS proof was verified"
    fi
  else
    if [ "$ots_confirmed" -eq 1 ]; then
      note "current seal manifest postdates the Bitcoin-confirmed release anchor (anchor covers commit ${sealed:0:7} only) — re-tag and re-stamp per PROVENANCE.md §6"
    elif [ "$ots_bound" -eq 1 ]; then
      note "current seal manifest postdates the digest-bound pending release anchor (record covers commit ${sealed:0:7} only; no Bitcoin confirmation is claimed) — re-tag and re-stamp per PROVENANCE.md §6"
    else
      note "current seal manifest postdates the release anchor (record covers commit ${sealed:0:7} only; no digest-bound proof was verified) — re-tag and re-stamp per PROVENANCE.md §6"
    fi
  fi
  freshtag=$(git tag --list 'v*-sealed*' --sort=-creatordate | head -1)
  if [ -n "$freshtag" ] && git show "$freshtag^{commit}:provenance/sealed-commit.txt" 2>/dev/null | cmp -s - provenance/sealed-commit.txt; then
    pass "newest sealed tag '$freshtag' matches the current anchor record"
  else
    note "newest sealed tag predates the current anchor record — re-tag per PROVENANCE.md §6"
  fi
fi

say ""
say "== $ok passed · $warn notes · $fail failed =="
[ "$fail" -eq 0 ]
