#!/usr/bin/env bash
# UserPromptSubmit hook: retrieve relevant Obsidian-vault context and inject it.
# Disable anytime:  touch ~/.claude/.vault-rag-off
[ -f "$HOME/.claude/.vault-rag-off" ] && exit 0
RAG="/Users/arielshemesh/Desktop/Workspace/03-Personal/architecture-skills/rag"
[ -x "$RAG/.venv/bin/python" ] || exit 0
PROMPT="$(python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("prompt",""))
except Exception: pass' 2>/dev/null)"
[ ${#PROMPT} -lt 12 ] && exit 0
OUT="$("$RAG/.venv/bin/python" "$RAG/hook_retrieve.py" "$PROMPT" 2>/dev/null)"
[ -n "$OUT" ] && printf '%s\n' "$OUT"
exit 0
