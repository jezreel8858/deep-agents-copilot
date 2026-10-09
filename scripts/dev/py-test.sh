#!/usr/bin/env bash
# py-test.sh - roda pytest de forma reprodutivel (uv --locked) com saida enxuta e log fora do repo.
# Uso: scripts/dev/py-test.sh [--project <raiz-alvo>] [--dry-run] [--verbose] [--help] [args pytest...]
# Plano: docs/implementation-plans/20261008-feature-development-embedded-python-runtime.md
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAC_HOME="$(cd "$SCRIPT_DIR/../.." && pwd)"
export DAC_HOME
[ -f "$SCRIPT_DIR/lib/resolve.sh" ] || { printf '[dac] ERRO(2): lib/resolve.sh ausente (plano Maven)\n' >&2; exit 2; }
# shellcheck source=lib/resolve.sh
. "$SCRIPT_DIR/lib/resolve.sh"
usage() {
  cat <<'USAGE'
py-test.sh [--project <raiz-alvo>] [--dry-run] [--verbose] [--help] [args pytest...]
Cascata: DAC_UV_BIN | DAC_PYTHON_BIN -> uv no PATH/cache -> bootstrap (DAC_BOOTSTRAP_UV=1)
         -> python>=3.11 + tests/requirements.txt -> erro.
Env: DAC_UV_BIN DAC_PYTHON_BIN DAC_BOOTSTRAP_UV DAC_VERBOSE DAC_TEST_TIMEOUT(900s) DAC_HOME(derivado)
--project <alvo>  roda no [PROJETO-ALVO] usando o ambiente do DAC_HOME (args pytest relativos ao alvo).
Exit: 0 ok | 1 falha de teste | 2 uso | 10 sem runner | 11 rede | 12 python | 13 SHA | 14 plataforma
      15 timeout | 17 uv.lock desatualizado
USAGE
}
TARGET=""; DRY=0; VERBOSE="${DAC_VERBOSE:-0}"; PYARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --dry-run) DRY=1 ;;
    --verbose) VERBOSE=1 ;;
    --project) [ $# -ge 2 ] || dac_die 2 "--project requer um caminho"; TARGET="$2"; shift ;;
    --project=*) TARGET="${1#--project=}" ;;
    --) shift; PYARGS+=("$@"); break ;;
    *) PYARGS+=("$1") ;;
  esac
  shift
done
if [ -n "$TARGET" ]; then
  [ -d "$TARGET" ] || dac_die 2 "raiz do alvo inexistente"
  TARGET="$(cd "$TARGET" && pwd)"
else
  TARGET="$DAC_HOME"
fi
if [ ! -f "$TARGET/pytest.ini" ] && [ ! -f "$TARGET/pyproject.toml" ] && [ ! -d "$TARGET/tests" ]; then
  dac_die 2 "alvo sem pytest.ini/pyproject.toml/tests"
fi
PLAT="$(dac_platform)"
IS_WIN=0; case "$PLAT" in windows-*) IS_WIN=1 ;; esac
native() { if [ "$IS_WIN" = 1 ] && command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }
# ---- bootstrap opt-in do uv (download verificado por SHA-256; host oficial astral-sh/uv) ----
uv_download() {  # <url> <dest>
  case "$1" in
    https://github.com/astral-sh/uv/releases/download/*) ;;
    *) dac_die 14 "host fora da allowlist oficial do uv no tools.lock" ;;
  esac
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 2 --connect-timeout 20 -m "${DAC_DOWNLOAD_TIMEOUT:-900}" -o "$2" "$1" \
      || dac_die 11 "falha de download do uv (rede/offline sem cache)"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -T 60 -O "$2" "$1" || dac_die 11 "falha de download do uv (rede/offline sem cache)"
  else
    dac_die 10 "curl/wget ausentes"
  fi
}
uv_extract() {  # <arquivo> <dir>
  mkdir -p "$2"
  case "$1" in
    *.zip)
      if command -v unzip >/dev/null 2>&1; then unzip -q -o "$1" -d "$2"
      else tar -xf "$(native "$1")" -C "$(native "$2")"; fi ;;
    *) tar -xzf "$1" -C "$2" ;;
  esac
}
uv_bin_name() { if [ "$IS_WIN" = 1 ]; then printf 'uv.exe'; else printf 'uv'; fi; }
uv_bootstrap() {
  local ver url sha dest tmp arc found
  ver="$(dac_lock_get uv version)"
  url="$(dac_lock_get uv "url.$PLAT")"; sha="$(dac_lock_get uv "sha256.$PLAT")"
  [ -n "$ver" ] && [ -n "$url" ] || dac_die 14 "plataforma $PLAT sem entrada [uv] no tools.lock"
  dest="$(dac_cache_dir)/uv/$ver/$PLAT"
  tmp="$(mktemp -d)"; arc="$tmp/${url##*/}"
  dac_log "bootstrap do uv $ver ($PLAT) em cache do usuario"
  uv_download "$url" "$arc"
  dac_verify_sha256 "$arc" "$sha"
  uv_extract "$arc" "$tmp/x"
  found="$(find "$tmp/x" -type f -name "$(uv_bin_name)" | head -1)"
  [ -n "$found" ] || dac_die 10 "binario do uv ausente no artefato"
  mkdir -p "$dest"; cp "$found" "$dest/$(uv_bin_name)"; chmod +x "$dest/$(uv_bin_name)" 2>/dev/null || true
  rm -rf "$tmp"
  printf '%s' "$dest/$(uv_bin_name)"
}
# ---- cascata de resolucao: RUNNER=uv|python ----
RUNNER=""; UV_BIN=""; PY_BIN=""
resolve_runner() {
  local ver c
  if [ -n "${DAC_UV_BIN:-}" ]; then
    if [ -x "$DAC_UV_BIN" ] || command -v "$DAC_UV_BIN" >/dev/null 2>&1; then RUNNER=uv; UV_BIN="$DAC_UV_BIN"; return 0; fi
    dac_log "[FALLBACK] DAC_UV_BIN invalido; seguindo a cascata"
  elif [ -n "${DAC_PYTHON_BIN:-}" ]; then
    if [ -x "$DAC_PYTHON_BIN" ] || command -v "$DAC_PYTHON_BIN" >/dev/null 2>&1; then RUNNER=python; PY_BIN="$DAC_PYTHON_BIN"; return 0; fi
    dac_log "[FALLBACK] DAC_PYTHON_BIN invalido; seguindo a cascata"
  fi
  if c="$(command -v uv 2>/dev/null)"; then RUNNER=uv; UV_BIN="$c"; return 0; fi
  ver="$(dac_lock_get uv version)"
  if [ -n "$ver" ] && [ -x "$(dac_cache_dir)/uv/$ver/$PLAT/$(uv_bin_name)" ]; then
    RUNNER=uv; UV_BIN="$(dac_cache_dir)/uv/$ver/$PLAT/$(uv_bin_name)"; return 0
  fi
  if [ "${DAC_BOOTSTRAP_UV:-${DAC_UV_BOOTSTRAP:-0}}" = "1" ]; then
    if [ "$DRY" = 1 ]; then RUNNER=uv; UV_BIN="<bootstrap uv $ver>"; return 0; fi
    UV_BIN="$(uv_bootstrap)"; RUNNER=uv; return 0
  fi
  for c in python python3; do
    if command -v "$c" >/dev/null 2>&1; then RUNNER=python; PY_BIN="$c"; return 0; fi
  done
  dac_die 10 "nenhum runner (sem uv e sem python>=3.11); use DAC_BOOTSTRAP_UV=1 ou instale python"
}
resolve_runner
CMD=()
if [ "$RUNNER" = uv ]; then
  CMD=("$UV_BIN" run --locked --project "$(native "$DAC_HOME")" --directory "$(native "$TARGET")" pytest -q --tb=short)
else
  "$PY_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null \
    || dac_die 12 "python ausente ou < 3.11"
  "$PY_BIN" -c 'import pytest, yaml, jsonschema' 2>/dev/null \
    || dac_die 12 "dependencias ausentes; execute: python -m pip install -r tests/requirements.txt"
  dac_log "[FALLBACK] sem uv; usando python -m pytest (sem lock)"
  CMD=("$PY_BIN" -m pytest -q --tb=short)
fi
CMD+=("${PYARGS[@]+"${PYARGS[@]}"}")
if [ "$DRY" = 1 ]; then
  printf 'runner=%s\ntarget=%s\ncmd=%s\n' "$RUNNER" "$([ "$TARGET" = "$DAC_HOME" ] && echo DAC_HOME || echo '<alvo>')" "${CMD[*]}"
  exit 0
fi
export MSYS_NO_PATHCONV=1  # caminhos ja nativos via cygpath; apos o bootstrap (curl/tar usam caminhos MSYS)
if [ -z "${PYTEST_DEBUG_TEMPROOT:-}" ]; then  # evita symlink pytest-current em TEMP restrito
  mkdir -p "$(dac_cache_dir)/pytest-tmp"; PYTEST_DEBUG_TEMPROOT="$(native "$(dac_cache_dir)/pytest-tmp")"
fi
export PYTEST_DEBUG_TEMPROOT
LOGDIR="$(dac_cache_dir)/logs"; mkdir -p "$LOGDIR"
LOG="$LOGDIR/py-test-$(date +%Y%m%d-%H%M%S)-$$.log"
TMO="${DAC_TEST_TIMEOUT:-900}"
rc=0
cd "$TARGET"
if command -v timeout >/dev/null 2>&1; then
  timeout "$TMO" "${CMD[@]}" >"$LOG" 2>&1 || rc=$?
else
  "${CMD[@]}" >"$LOG" 2>&1 || rc=$?
fi
if [ "$VERBOSE" = 1 ]; then cat "$LOG"
else
  if [ "$rc" -ne 0 ]; then tail -n 20 "$LOG"
  else grep -E '^(=+ )?[0-9]+ .*(passed|failed|error|skipped|deselected).* in [0-9.]+s|no tests ran' "$LOG" | tail -n 1 || true; fi
fi
printf 'log: %s\n' "$(dac_tilde "$LOG")"
[ "$rc" -eq 0 ] && exit 0
[ "$rc" -eq 124 ] && dac_die 15 "timeout (${TMO}s)"
if [ "$RUNNER" = uv ] && grep -qiE 'lockfile at .*needs to be updated|[Uu]nable to find lockfile' "$LOG"; then
  dac_die 17 "uv.lock desatualizado/ausente; execute: uv lock"
fi
dac_log "pytest rc=$rc"
exit 1
