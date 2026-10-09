#!/usr/bin/env bash
# Instala mvnd (versao do tools.lock) no cache do usuario com SHA-256 verificado.
# Idempotente. Stdout: caminho do binario mvnd (para uso por scripts). Logs: stderr.
# Exit: 0 ok | 2 uso | 10 ferramenta ausente | 11 rede | 13 SHA divergente | 14 plataforma/lock/SHA pendente
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/resolve.sh
. "$SCRIPT_DIR/lib/resolve.sh"

usage() {
  cat <<'EOF'
Uso: bootstrap-mvnd.sh [--dry-run] [--help]
  --dry-run  mostra plataforma, URL, estado do cache e SHA (sem rede, sem instalar)
Env: XDG_CACHE_HOME, DAC_LOCK_WAIT (s, default 120), DAC_DOWNLOAD_TIMEOUT (s, default 900)
EOF
}

dry=0
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --dry-run) dry=1 ;;
    *) usage >&2; dac_die 2 "argumento invalido: $1" ;;
  esac
  shift
done

ver="$(dac_lock_get mvnd version)"
[ -n "$ver" ] || dac_die 14 "secao [mvnd] ausente no tools.lock"
plat="$(dac_platform)"
url="$(dac_lock_get mvnd "url.$plat")"
sha="$(dac_lock_get mvnd "sha256.$plat")"
[ -n "$url" ] || dac_die 14 "plataforma $plat sem entrada no tools.lock"

cache="$(dac_cache_dir)"
dest="$cache/mvnd/$ver/$plat"
bin="$dest/bin/$(_dac_mvnd_name)"

sha_state="ok"
case "$sha" in ""|*[!0-9a-f]*) sha_state="pendente" ;; *) [ "${#sha}" -eq 64 ] || sha_state="pendente" ;; esac

if [ "$dry" -eq 1 ]; then
  hit="miss"; [ -e "$bin" ] && hit="hit"
  dac_log "mvnd $ver plataforma=$plat cache=$hit sha256=$sha_state"
  dac_log "url=$url"
  dac_log "destino=$(dac_tilde "$dest")"
  [ "$sha_state" = "ok" ] || [ "$hit" = "hit" ] || dac_die 14 "SHA-256 pendente no tools.lock; bootstrap bloqueado"
  exit 0
fi

healthy() { [ -e "$bin" ] && timeout 60 "$bin" --version >/dev/null 2>&1; }

if healthy; then printf '%s\n' "$bin"; exit 0; fi

[ "$sha_state" = "ok" ] || dac_die 14 "SHA-256 pendente no tools.lock para $plat (revisao humana necessaria)"

mkdir -p "$cache/mvnd"
lock="$cache/mvnd/.lock-$ver-$plat"
tmp=""
have_lock=0
cleanup() {
  [ -n "$tmp" ] && rm -rf "$tmp"
  [ "$have_lock" -eq 1 ] && rmdir "$lock" 2>/dev/null || true
}
trap cleanup EXIT

waited=0
until mkdir "$lock" 2>/dev/null; do
  if healthy; then printf '%s\n' "$bin"; exit 0; fi
  [ "$waited" -lt "${DAC_LOCK_WAIT:-120}" ] || dac_die 11 "timeout aguardando outro bootstrap em andamento"
  sleep 2; waited=$((waited + 2))
done
have_lock=1

if healthy; then printf '%s\n' "$bin"; exit 0; fi

tmp="$(mktemp -d "$cache/mvnd/.tmp.XXXXXX")"
archive="$tmp/artifact"
dac_log "baixando mvnd $ver ($plat)"
dac_download "$url" "$archive"
dac_verify_sha256 "$archive" "$sha"
dac_log "SHA-256 verificado"

mkdir "$tmp/x"
case "$url" in
  *.zip) command -v unzip >/dev/null 2>&1 || dac_die 10 "unzip ausente"; unzip -q "$archive" -d "$tmp/x" ;;
  *.tar.gz) command -v tar >/dev/null 2>&1 || dac_die 10 "tar ausente"; tar -xzf "$archive" -C "$tmp/x" ;;
  *) dac_die 14 "formato de artefato nao suportado" ;;
esac

top=""
for d in "$tmp/x"/*/; do top="${d%/}"; break; done
[ -n "$top" ] && [ -e "$top/bin/$(_dac_mvnd_name)" ] || dac_die 14 "layout inesperado do artefato"

rm -rf "$dest"
mkdir -p "$(dirname "$dest")"
mv "$top" "$dest"
healthy || dac_die 10 "mvnd instalado nao executa (--version falhou; verifique JDK)"
dac_log "instalado em $(dac_tilde "$dest")"
printf '%s\n' "$bin"
