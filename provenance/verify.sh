#!/usr/bin/env bash
# Verify the fabius provenance package from a clean clone.
# Read-only: trusts no single party and mutates nothing — the timestamp
# reports a digest-bound OTS proof as pending or Bitcoin-confirmed, and verifies
# the signature against a key in the repo.
#
#   bash provenance/verify.sh
#
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"
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
if [ -n "${OTS:-}" ] && [ -f provenance/sealed-commit.txt.ots ]; then
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
    ots_bound=1
    pass "OpenTimestamps detached digest matches provenance/sealed-commit.txt ($record_hash)"
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
else
  note "ots client or .ots proof absent — install opentimestamps-client, or release not sealed yet"
fi

# 4) Signed tag (authorship) ----------------------------------------------
if [ -f provenance/allowed_signers ]; then
  tag=$(git tag --list 'v*-sealed*' --sort=-creatordate | head -1)
  if [ -n "$tag" ] && git -c gpg.ssh.allowedSignersFile=provenance/allowed_signers verify-tag "$tag" 2>&1 | grep -qi "Good .*signature"; then
    pass "release tag '$tag' carries a valid signature from the committed key"
  else
    note "no verified *-sealed tag found locally (fetch tags: git fetch --tags), or release not sealed yet"
  fi
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
