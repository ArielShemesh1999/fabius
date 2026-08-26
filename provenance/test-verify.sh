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
    if [ "${FAKE_OTS_VERIFY_MODE:-invalid}" = pending ]; then
      printf 'File sha256 hash: %s\nTimestamp:\nPendingAttestation("https://calendar.example")\n' "$digest"
    else
      printf 'File sha256 hash: %s\nTimestamp:\nverify BitcoinBlockHeaderAttestation(999999)\n' "$digest"
    fi
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
  upgrade)
    proof=${2:-}
    [ -n "$proof" ] || exit 2
    cp "$proof" "$proof.bak"
    printf 'deterministic-upgrade' >> "$proof"
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

check_required_case() {
  label=$1
  mode=$2
  expected_code=$3
  expected_text=$4
  output=$(PATH="$tmp:$PATH" FAKE_OTS_VERIFY_MODE="$mode" bash provenance/verify.sh --require-confirmed 2>&1)
  code=$?
  if [ "$code" -eq "$expected_code" ] && printf '%s\n' "$output" | grep -Fq "$expected_text"; then
    printf '  PASS  %s\n' "$label"
    passed=$((passed+1))
  else
    printf '  FAIL  %s (exit %s; expected %s)\n%s\n' "$label" "$code" "$expected_code" "$output"
    failed=$((failed+1))
  fi
}

check_required_case \
  "confirmed mode accepts trusted verification of the matching block" \
  success 0 \
  "PASS  OpenTimestamps proof trusted-verifies against Bitcoin block 999999"
check_required_case \
  "confirmed mode rejects an unavailable trusted verifier" \
  unavailable 1 \
  "FAIL  Bitcoin confirmation is required for a provenance-only proof upgrade"
check_required_case \
  "confirmed mode rejects a pending calendar attestation" \
  pending 1 \
  "FAIL  Bitcoin confirmation is required for a provenance-only proof upgrade"

upgrade_root="$tmp/upgrade-root"
mkdir -p "$upgrade_root/provenance"
cp provenance/sealed-commit.txt "$upgrade_root/provenance/sealed-commit.txt"
cp provenance/sealed-commit.txt.ots "$upgrade_root/provenance/sealed-commit.txt.ots"
upgrade_before=$(shasum -a 256 "$upgrade_root/provenance/sealed-commit.txt.ots" | awk '{print $1}')
upgrade_output=$(PATH="$tmp:$PATH" FABIUS_VERIFY_ROOT="$upgrade_root" FAKE_OTS_VERIFY_MODE=success \
  bash provenance/upgrade-seal.sh 2>&1)
upgrade_code=$?
upgrade_after=$(shasum -a 256 "$upgrade_root/provenance/sealed-commit.txt.ots" | awk '{print $1}')
upgrade_temp_count=$(find "$upgrade_root/provenance" -maxdepth 1 -name '.fabius-ots-upgrade.*' | wc -l | tr -d ' ')
upgrade_backup_count=$(find "$upgrade_root/provenance" -maxdepth 2 -name '*.bak' | wc -l | tr -d ' ')
if [ "$upgrade_code" -eq 0 ] && [ "$upgrade_before" != "$upgrade_after" ] \
   && [ "$upgrade_temp_count" -eq 0 ] && [ "$upgrade_backup_count" -eq 0 ] \
   && printf '%s\n' "$upgrade_output" | grep -Fq 'parsed Bitcoin block 999999 is present'; then
  printf '  PASS  proof upgrade publishes one bound proof and leaves no temp or backup artifact\n'
  passed=$((passed+1))
else
  printf '  FAIL  proof upgrade publication contract (exit %s; temp %s; backup %s)\n%s\n' \
    "$upgrade_code" "$upgrade_temp_count" "$upgrade_backup_count" "$upgrade_output"
  failed=$((failed+1))
fi

printf '\n== %s passed · %s failed ==\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
