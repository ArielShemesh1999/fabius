#!/usr/bin/env bash
# Select the aggregate verification mode from repository state, not event name.
# A main-branch run at an already sealed HEAD must verify as a release too.
set -uo pipefail
if [ -n "${FABIUS_VERIFY_ROOT:-}" ]; then
  cd "$FABIUS_VERIFY_ROOT"
else
  cd "$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"
fi

canonical_tags=$(git tag --points-at HEAD --list 'v*-sealed' 2>/dev/null \
  | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+-sealed$' || true)
tag_count=$(printf '%s\n' "$canonical_tags" | sed '/^$/d' | wc -l | tr -d ' ')

if [ "$tag_count" -gt 1 ]; then
  echo "multiple canonical sealed tags point at HEAD" >&2
  exit 1
fi

if [ "$tag_count" -eq 1 ]; then
  if [ "$(git cat-file -t "refs/tags/${canonical_tags}" 2>/dev/null || true)" != tag ]; then
    echo "canonical sealed tag at HEAD is not annotated: $canonical_tags" >&2
    exit 1
  fi
  mode=release
else
  mode=dev
  newest_tag=$(git tag --list 'v*-sealed' --sort=-version:refname 2>/dev/null \
    | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+-sealed$' | head -1 || true)
  if [ -n "$newest_tag" ] \
     && [ "$(git cat-file -t "refs/tags/${newest_tag}" 2>/dev/null || true)" = tag ]; then
    tag_commit=$(git rev-parse "${newest_tag}^{}")
    parents=$(git show -s --format=%P HEAD)
    proof_delta=$(git diff-tree --no-commit-id -r --no-renames --name-status HEAD)
    if [ "$parents" = "$tag_commit" ] \
       && [ "$proof_delta" = $'M\tprovenance/sealed-commit.txt.ots' ]; then
      mode=proof-upgrade
    fi
  fi
fi

case "${GITHUB_REF:-}" in
  refs/tags/*)
    expected=${GITHUB_REF#refs/tags/}
    if ! printf '%s\n' "$expected" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+-sealed$'; then
      echo "tag event is not a canonical sealed release: $expected" >&2
      exit 1
    fi
    if [ "$mode" != release ] || [ "$canonical_tags" != "$expected" ]; then
      echo "tag event does not preserve its canonical sealed tag at HEAD: $expected" >&2
      exit 1
    fi
    ;;
esac

printf '%s\n' "$mode"
