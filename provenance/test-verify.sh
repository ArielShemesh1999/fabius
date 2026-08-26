#!/usr/bin/env bash
# Deterministic adversarial checks for provenance/verify.sh. No proof is changed.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"

tmp=$(mktemp -d "${TMPDIR:-/tmp}/fabius-provenance-test.XXXXXX") || exit 1
trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/ots" <<'SH'
#!/usr/bin/env bash
case "${1:-}" in
  info)
    digest=$(shasum -a 256 provenance/sealed-commit.txt | awk '{print $1}')
    printf 'File sha256 hash: %s\nTimestamp:\nverify BitcoinBlockHeaderAttestation(999999)\n' "$digest"
    ;;
  verify)
    case "${FAKE_OTS_VERIFY_MODE:-invalid}" in
      success) echo "Success! Bitcoin block 999999 attests existence as of 2026-01-01 UTC"; exit 0 ;;
      wrongblock) echo "Success! Bitcoin block 888888 attests existence as of 2025-01-01 UTC"; exit 0 ;;
      unavailable) echo "Could not connect to Bitcoin node: deterministic test outage" >&2; exit 1 ;;
      invalid) echo "Verification failed: forged Bitcoin attestation" >&2; exit 1 ;;
      *) echo "unknown fake mode" >&2; exit 2 ;;
    esac
    ;;
  *) echo "unexpected fake ots command" >&2; exit 2 ;;
esac
SH
chmod +x "$tmp/ots"

passed=0
failed=0
check_case() {
  label=$1
  mode=$2
  expected_code=$3
  expected_text=$4
  forbidden_text=$5
  output=$(PATH="$tmp:$PATH" FAKE_OTS_VERIFY_MODE="$mode" bash provenance/verify.sh 2>&1)
  code=$?
  if [ "$code" -eq "$expected_code" ] \
     && printf '%s\n' "$output" | grep -Fq "$expected_text" \
     && ! printf '%s\n' "$output" | grep -Fq "$forbidden_text"; then
    printf '  PASS  %s\n' "$label"
    passed=$((passed+1))
  else
    printf '  FAIL  %s (exit %s; expected %s)\n%s\n' "$label" "$code" "$expected_code" "$output"
    failed=$((failed+1))
  fi
}

echo "== fabius provenance adversarial tests =="
check_case \
  "forged parsed attestation fails when trusted verification rejects it" \
  invalid 1 \
  "FAIL  OpenTimestamps Bitcoin attestation failed trusted verification" \
  "PASS  OpenTimestamps proof trusted-verifies"
check_case \
  "unavailable trusted verifier never upgrades parsed bytes to confirmation" \
  unavailable 0 \
  "NOTE  proof contains a digest-bound Bitcoin block attestation for block 999999, but trusted verification is unavailable — NOT confirmed" \
  "PASS  OpenTimestamps proof trusted-verifies"
check_case \
  "trusted verifier success is required for Bitcoin confirmation" \
  success 0 \
  "PASS  OpenTimestamps proof trusted-verifies against Bitcoin block 999999" \
  "FAIL  OpenTimestamps Bitcoin attestation"
check_case \
  "verifier success for a different block cannot bless the parsed attestation" \
  wrongblock 1 \
  "FAIL  OpenTimestamps verifier success did not bind a parsed Bitcoin attestation" \
  "PASS  OpenTimestamps proof trusted-verifies"

printf '\n== %s passed · %s failed ==\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
