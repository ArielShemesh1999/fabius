#!/usr/bin/env bash
# Fetch the specification test vectors the crypto suite runs against.
#
# These are other people's files and they stay other people's files: they are downloaded
# on demand, never vendored into the repo, and never edited. If a vector changes upstream
# and our implementation stops matching it, that is exactly the signal we want.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p test/vectors

fetch() {
  printf '  %-14s' "$2"
  if curl -fsSL "$1" -o "test/vectors/$2"; then
    echo "ok ($(wc -c < "test/vectors/$2" | tr -d ' ') bytes)"
  else
    echo "FAILED — $1"; exit 1
  fi
}

echo "fetching specification vectors:"
fetch https://raw.githubusercontent.com/bitcoin/bips/master/bip-0340/test-vectors.csv bip340.csv
fetch https://raw.githubusercontent.com/paulmillr/nip44/main/nip44.vectors.json      nip44.json
echo
echo "now run:  node --test test/nostr.test.mjs"
