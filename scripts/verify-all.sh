#!/usr/bin/env bash
# One read-only entry point for the repository's deterministic gates.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"

mode=dev
case "${1:-}" in
  --mode=dev|--mode=release|--mode=proof-upgrade) mode=${1#--mode=} ;;
  "") ;;
  *) echo "usage: bash scripts/verify-all.sh [--mode=dev|--mode=release|--mode=proof-upgrade]"; exit 2 ;;
esac

passed=0
failed=0
run_gate() {
  label=$1
  shift
  printf '\n===== %s =====\n' "$label"
  if "$@"; then passed=$((passed+1)); else failed=$((failed+1)); fi
}

run_gate "structural install + seal invariants" node evals/structural.mjs
run_gate "nested reference quarantine" node scripts/verify-reference-quarantine.mjs
run_gate "FBS suite schema" node evals/suite/validate.mjs
run_gate "committed benchmark receipt replay" node evals/verify-receipts.mjs
run_gate "base eval harness selftest" node evals/eval.mjs --selftest
run_gate "portable eval harness selftest" python3 evals/portable_eval.py --selftest
run_gate "runtime unit/integration tests" node --test runtime/test/*.test.mjs
run_gate "Concilium deterministic protocol selftest" node skills/fabius-concilium/references/council.mjs --selftest
run_gate "repo-local package truth" node scripts/verify-package.mjs
run_gate "upstream registry coherence" node scripts/verify-upstream.mjs
run_gate "upstream registry adversarial regression" node scripts/test-verify-upstream.mjs
run_gate "paper artifact oracle" node scripts/verify-paper-artifact.mjs
run_gate "paper artifact adversarial regression" node scripts/test-verify-paper-artifact.mjs
run_gate "OpenTimestamps detached-proof binding" node scripts/test-verify-ots-binding.mjs
if [ "$mode" = proof-upgrade ]; then
  run_gate "provenance bundle (Bitcoin confirmation required)" bash provenance/verify.sh --require-confirmed
else
  run_gate "provenance bundle" bash provenance/verify.sh
fi
run_gate "provenance adversarial regression" bash provenance/test-verify.sh
run_gate "release-state adversarial regression" node scripts/test-verify-release.mjs
run_gate "$mode release integrity" node scripts/verify-release.mjs "--mode=$mode"

printf '\n===== aggregate =====\n'
printf '%s gate groups passed · %s failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
