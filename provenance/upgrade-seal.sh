#!/usr/bin/env bash
# Upgrade the OpenTimestamps proof from "pending" (calendar attestation) to a
# confirmed Bitcoin-block attestation, and commit the upgraded proof.
# Safe to run repeatedly: a no-op until the anchoring Bitcoin block is mined.
#
#   bash provenance/upgrade-seal.sh
#
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"
PROOF=provenance/sealed-commit.txt.ots

OTS=$(command -v ots || ls "$HOME"/Library/Python/*/bin/ots 2>/dev/null | head -1)
if [ -z "${OTS:-}" ]; then
  echo "ots client not found — install: pip3 install --user opentimestamps-client"; exit 1
fi
[ -f "$PROOF" ] || { echo "no proof at $PROOF — nothing to upgrade"; exit 1; }

before=$(shasum -a 256 "$PROOF" | cut -d' ' -f1)
"$OTS" upgrade "$PROOF" 2>&1 || true
after=$(shasum -a 256 "$PROOF" | cut -d' ' -f1)

if [ "$before" != "$after" ]; then
  echo "proof upgraded — committing the confirmed Bitcoin attestation"
  git add "$PROOF"
  # sign if a signing key is configured locally; fall back to unsigned
  git commit -S -q -m "Provenance: upgrade OTS proof to confirmed Bitcoin attestation" 2>/dev/null \
    || git commit -q -m "Provenance: upgrade OTS proof to confirmed Bitcoin attestation"
  git push origin HEAD 2>&1 | tail -2
  echo "done."
else
  echo "no change yet — the anchoring Bitcoin block is not mined. Re-run later."
fi
"$OTS" verify "$PROOF" 2>&1 | tail -3
