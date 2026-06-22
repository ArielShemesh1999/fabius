#!/usr/bin/env bash
# Refresh the Fabius-Vec vault index — local, $0 (no API). Safe for SessionEnd or manual.
# Skips entirely if no vault markdown changed since the last index (no wasted work).
RAG="/Users/arielshemesh/Desktop/Workspace/03-Personal/architecture-skills/rag"
VAULT="$HOME/Documents/ObsidianVault"
IDX="$RAG/.index/vault.tvim"
[ -x "$RAG/.venv/bin/python" ] || exit 0
if [ -f "$IDX" ]; then
  changed="$(find "$VAULT" -name '*.md' -not -path '*/.obsidian/*' -not -path '*/.trash/*' -newer "$IDX" -print -quit 2>/dev/null)"
  [ -z "$changed" ] && exit 0   # nothing changed -> skip the 2-min rebuild
fi
"$RAG/.venv/bin/python" "$RAG/indexer.py" >>"$RAG/.index/reindex.log" 2>&1
