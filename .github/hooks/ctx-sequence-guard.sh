#!/usr/bin/env bash
# ctx-sequence-guard.sh
#
# Circuit Breaker MECANICO (R-046 / R-059 / R-060 / Smell 2.26 - Anti MCP Tool Chaining Sequencial).
# Hook PreToolUse UNICO (telemetria original do context-mode + guard mesclados em um so comando,
# para evitar depender de suporte a multiplas entradas de hook por evento no host).
#
# Fail-open por design: qualquer falha (jq ausente, JSON invalido, erro de I/O) sempre permite
# a chamada - este script nunca deve ser a causa de um bloqueio indevido do agente.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/.state"
STATE_FILE="$STATE_DIR/ctx-sequence-guard.json"
DEBUG_LOG="$STATE_DIR/ctx-sequence-guard.debug.log"

mkdir -p "$STATE_DIR" 2>/dev/null || true

INPUT="$(cat 2>/dev/null || true)"

# Trace incondicional: prova que o hook foi invocado pelo host, independente da decisao final.
{
  printf '[%s] invoked pid=%s stdin_len=%s preview=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$$" "${#INPUT}" \
    "$(printf '%s' "$INPUT" | tr -d '\n' | head -c 200)"
} >> "$DEBUG_LOG" 2>/dev/null || true

# Telemetria original do context-mode (best-effort, nunca bloqueia, reencaminha o mesmo stdin).
if command -v context-mode >/dev/null 2>&1; then
  IDEA_INITIAL_DIRECTORY="$(pwd -W 2>/dev/null || pwd)"
  IDEA_INITIAL_DIRECTORY="${IDEA_INITIAL_DIRECTORY^}"
  export IDEA_INITIAL_DIRECTORY
  printf '%s' "$INPUT" | context-mode hook jetbrains-copilot pretooluse >/dev/null 2>&1 || true
fi

allow() {
  echo '{"permissionDecision":"allow"}'
  exit 0
}

command -v jq >/dev/null 2>&1 || allow
[[ -z "$INPUT" ]] && allow

TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.toolName // .tool_name // empty' 2>/dev/null || true)"
[[ -z "$TOOL_NAME" ]] && allow

if [[ ! "$TOOL_NAME" =~ ^ctx_execute(_file)?$ ]]; then
  # Qualquer outra ferramenta (incl. ctx_batch_execute) reseta a sequencia.
  rm -f "$STATE_FILE" 2>/dev/null || true
  allow
fi

COUNTER=0
if [[ -f "$STATE_FILE" ]]; then
  COUNTER="$(jq -r '.counter // 0' "$STATE_FILE" 2>/dev/null || echo 0)"
  [[ "$COUNTER" =~ ^[0-9]+$ ]] || COUNTER=0
fi

COUNTER=$((COUNTER + 1))
jq -n --argjson c "$COUNTER" '{counter: $c}' > "$STATE_FILE" 2>/dev/null || true

if [[ "$COUNTER" -ge 2 ]]; then
  REASON='Circuit Breaker R-046/R-059/R-060 (context-mode SKILL.md secao 4.1): 2+ chamadas consecutivas de ctx_execute/ctx_execute_file SEM ctx_batch_execute interposto. Isto e feedback automatizado corrigivel (equivalente a erro de lint) - NAO pare, NAO peca permissao ao usuario e NAO repita a mesma chamada isolada. Reconsolide TODOS os alvos pendentes desta tarefa em UMA unica chamada ctx_batch_execute(commands:[...], queries:[...]) e prossiga imediatamente.'
  jq -n --arg r "$REASON" '{permissionDecision:"deny", permissionDecisionReason:$r}' 2>/dev/null || \
    echo "{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$REASON\"}"
  exit 0
fi

allow

