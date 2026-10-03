#!/usr/bin/env bash
# ctx-sequence-reset.sh
# Hook SessionStart UNICO (telemetria original do context-mode + reset do circuit breaker
# mesclados em um so comando).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/.state"
mkdir -p "$STATE_DIR" 2>/dev/null || true

{
  printf '[%s] session-reset invoked pid=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$$"
} >> "$STATE_DIR/ctx-sequence-guard.debug.log" 2>/dev/null || true

if command -v context-mode >/dev/null 2>&1; then
  IDEA_INITIAL_DIRECTORY="$(pwd -W 2>/dev/null || pwd)"
  IDEA_INITIAL_DIRECTORY="${IDEA_INITIAL_DIRECTORY^}"
  export IDEA_INITIAL_DIRECTORY
  context-mode hook jetbrains-copilot sessionstart >/dev/null 2>&1 || true
fi

rm -f "$STATE_DIR/ctx-sequence-guard.json" 2>/dev/null || true
exit 0

