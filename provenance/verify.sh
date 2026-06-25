#!/usr/bin/env bash
# Verify the fabius provenance package from a clean clone.
# Read-only: trusts no single party and mutates nothing — the timestamp
# anchors to Bitcoin and the signature verifies against a key in the repo.
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

# 3) OpenTimestamps proof (Bitcoin priority date) -------------------------
OTS=$(command -v ots || ls "$HOME"/Library/Python/*/bin/ots 2>/dev/null | head -1)
if [ -n "${OTS:-}" ] && [ -f provenance/sealed-commit.txt.ots ]; then
  # The Bitcoin attestation is embedded IN the proof file — `ots info` reads it
  # with no Bitcoin node. (`ots verify` additionally cross-checks the block
  # header against a node/explorer; absence of a node is not "unconfirmed".)
  info=$("$OTS" info provenance/sealed-commit.txt.ots 2>&1)
  block=$(printf '%s' "$info" | grep -oiE "BitcoinBlockHeaderAttestation\([0-9]+\)" | grep -oE "[0-9]+" | head -1)
  if [ -n "$block" ]; then
    pass "OpenTimestamps proof anchored to Bitcoin block $block (cross-check its merkle root on any explorer, or 'ots verify' with a node)"
  elif printf '%s' "$info" | grep -qi "PendingAttestation"; then
    note "OTS proof present but still pending Bitcoin confirmation — run: $OTS upgrade provenance/sealed-commit.txt.ots"
  else
    note "OTS proof present but no recognizable attestation — inspect: $OTS info provenance/sealed-commit.txt.ots"
  fi
else
  note "ots client or .ots proof absent — install opentimestamps-client, or release not sealed yet"
fi

# 4) Signed tag (authorship) ----------------------------------------------
if [ -f provenance/allowed_signers ]; then
  tag=$(git tag --list 'v*-sealed' --sort=-version:refname | head -1)
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
import hashlib, json, sys
m = json.load(open("provenance/seal-manifest.json"))
bad = 0
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

say ""
say "== $ok passed · $warn notes · $fail failed =="
[ "$fail" -eq 0 ]
