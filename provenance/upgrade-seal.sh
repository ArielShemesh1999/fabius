#!/usr/bin/env bash
# Upgrade the OpenTimestamps proof from a pending calendar attestation when a
# stronger attestation is available. This script never stages, commits or pushes.
# Safe to run repeatedly: a no-op until an upgrade is available.
#
#   bash provenance/upgrade-seal.sh
#
set -uo pipefail
if [ -n "${FABIUS_VERIFY_ROOT:-}" ]; then
  cd "$FABIUS_VERIFY_ROOT"
else
  cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"
fi
PROOF=provenance/sealed-commit.txt.ots
RECORD=provenance/sealed-commit.txt

[ "$#" -eq 0 ] || { echo "usage: bash provenance/upgrade-seal.sh (never commits or pushes)"; exit 2; }

OTS=$(command -v ots || ls "$HOME"/Library/Python/*/bin/ots 2>/dev/null | head -1)
if [ -z "${OTS:-}" ]; then
  echo "ots client not found — install: pip3 install --user opentimestamps-client"; exit 1
fi
[ -f "$PROOF" ] || { echo "no proof at $PROOF — nothing to upgrade"; exit 1; }
[ -f "$RECORD" ] || { echo "no sealed record at $RECORD — refusing detached proof upgrade"; exit 1; }

tmp=$(mktemp -d "provenance/.fabius-ots-upgrade.XXXXXX") || exit 1
case "$tmp" in
  provenance/.fabius-ots-upgrade.*) ;;
  *) echo "unexpected temporary path — refusing proof upgrade"; exit 1 ;;
esac
trap 'rm -rf "$tmp"' EXIT
work_proof="$tmp/sealed-commit.txt.ots"
cp "$PROOF" "$work_proof"

# Bind the detached proof to the exact record before trusting or upgrading it.
info=$("$OTS" info "$PROOF" 2>&1)
proof_hash=$(printf '%s\n' "$info" | sed -n 's/^File sha256 hash: \([0-9a-fA-F]\{64\}\)$/\1/p' | head -1 | tr 'A-F' 'a-f')
record_hash=$(shasum -a 256 "$RECORD" | awk '{print $1}')
[ -n "$proof_hash" ] || { echo "proof does not expose a detached sha256 digest — refusing upgrade"; exit 1; }
[ "$proof_hash" = "$record_hash" ] || {
  echo "proof digest mismatch — refusing upgrade"; exit 1;
}

before=$(shasum -a 256 "$PROOF" | cut -d' ' -f1)
upgrade_code=0
"$OTS" upgrade "$work_proof" 2>&1 || upgrade_code=$?
after=$(shasum -a 256 "$work_proof" | cut -d' ' -f1)

after_info=$("$OTS" info "$work_proof" 2>&1)
after_hash=$(printf '%s\n' "$after_info" | sed -n 's/^File sha256 hash: \([0-9a-fA-F]\{64\}\)$/\1/p' | head -1 | tr 'A-F' 'a-f')
[ "$after_hash" = "$record_hash" ] || { echo "upgraded proof lost record binding — FAIL"; exit 1; }
block=$(printf '%s\n' "$after_info" | grep -oiE 'BitcoinBlockHeaderAttestation\([0-9]+\)' | grep -oE '[0-9]+' | head -1)

if [ "$before" != "$after" ] && [ -n "$block" ]; then
  mv "$work_proof" "$PROOF"
  echo "proof upgraded locally and remains digest-bound; parsed Bitcoin block $block is present"
  echo "working tree only — require: bash scripts/verify-all.sh --mode=proof-upgrade"
elif [ "$before" != "$after" ]; then
  mv "$work_proof" "$PROOF"
  echo "proof changed locally and remains digest-bound, but no Bitcoin block attestation is present"
  echo "working tree only — do not describe it as Bitcoin-confirmed"
else
  echo "no proof change available; current detached digest remains bound"
fi
[ "$upgrade_code" -eq 0 ] || echo "ots upgrade exited $upgrade_code; proof status above is authoritative"
