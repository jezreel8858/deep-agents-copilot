#!/usr/bin/env bash
# Lib compartilhada (apenas `source`; sem efeitos colaterais alem de definir funcoes/variaveis).
# Contrato publico: dac_resolve_maven dac_cache_dir dac_platform dac_download dac_verify_sha256
#                   dac_log dac_die dac_detect_jdk dac_lock_get dac_tilde
# Exit codes: 0 ok | 1 build | 2 uso | 10 sem Maven | 11 rede | 12 JDK | 13 SHA | 14 plataforma/lock | 15 timeout | 16 mvnw bloqueado
# shellcheck shell=bash

if [ -n "${DAC_RESOLVE_LOADED:-}" ]; then return 0; fi
DAC_RESOLVE_LOADED=1

DAC_DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DAC_LOCK_FILE="${DAC_LOCK_FILE:-$DAC_DEV_DIR/tools.lock}"
DAC_MVN_MODE="${DAC_MVN_MODE:-daemon}"            # daemon | wrapper | auto
DAC_ALLOW_TARGET_WRAPPER="${DAC_ALLOW_TARGET_WRAPPER:-0}"  # permite mvnw do alvo como fallback no modo daemon
DAC_MAVEN_CMD=()
DAC_MAVEN_KIND=""
DAC_BOOT_RC=0

dac_log() { printf '[dac] %s\n' "$*" >&2; }

dac_die() {
  local code="$1"; shift
  dac_log "ERRO($code): $*"
  exit "$code"
}

# Substitui o prefixo $HOME por <HOME> para mensagens sem caminho de usuario.
dac_tilde() { printf '%s' "${1/#"$HOME"/<HOME>}"; }

dac_platform() {
  local os arch
  case "$(uname -s)" in
    Linux*) os=linux ;;
    Darwin*) os=darwin ;;
    MINGW*|MSYS*|CYGWIN*) os=windows ;;
    *) os=unknown ;;
  esac
  case "$(uname -m)" in
    x86_64|amd64) arch=amd64 ;;
    arm64|aarch64) arch=aarch64 ;;
    *) arch="$(uname -m)" ;;
  esac
  printf '%s-%s' "$os" "$arch"
}

dac_cache_dir() { printf '%s' "${XDG_CACHE_HOME:-$HOME/.cache}/deep-agents-copilot"; }

# dac_lock_get <secao> <chave> -> valor (vazio se ausente)
dac_lock_get() {
  [ -f "$DAC_LOCK_FILE" ] || return 0
  awk -v s="[$1]" -v k="$2" '
    { sub(/\r$/, "") }
    /^[[:space:]]*#/ { next }
    $0 == s { in_s = 1; next }
    /^\[/ { in_s = 0 }
    in_s { i = index($0, "="); if (i > 0 && substr($0, 1, i - 1) == k) { print substr($0, i + 1); exit } }
  ' "$DAC_LOCK_FILE"
}

# dac_download <url> <destino>  (somente hosts oficiais Apache)
dac_download() {
  local url="$1" dest="$2"
  case "$url" in
    https://downloads.apache.org/*|https://archive.apache.org/dist/*) ;;
    *) dac_die 14 "host fora da allowlist oficial no tools.lock" ;;
  esac
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 2 --connect-timeout 20 -m "${DAC_DOWNLOAD_TIMEOUT:-900}" -o "$dest" "$url" \
      || dac_die 11 "falha de download (rede/offline sem cache)"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -T 60 -O "$dest" "$url" || dac_die 11 "falha de download (rede/offline sem cache)"
  else
    dac_die 10 "curl/wget ausentes"
  fi
}

# dac_verify_sha256 <arquivo> <sha256-esperado>
dac_verify_sha256() {
  local file="$1" exp="${2:-}" act
  case "$exp" in
    ""|*[!0-9a-f]*) dac_die 14 "SHA-256 pendente/invalido no tools.lock (revisao humana necessaria)" ;;
  esac
  [ "${#exp}" -eq 64 ] || dac_die 14 "SHA-256 pendente/invalido no tools.lock (revisao humana necessaria)"
  if command -v sha256sum >/dev/null 2>&1; then act="$(sha256sum "$file" | cut -d' ' -f1)"
  elif command -v shasum >/dev/null 2>&1; then act="$(shasum -a 256 "$file" | cut -d' ' -f1)"
  elif command -v openssl >/dev/null 2>&1; then act="$(openssl dgst -sha256 -r "$file" | cut -d' ' -f1)"
  else dac_die 10 "sha256sum/shasum/openssl ausentes"
  fi
  if [ "$act" != "$exp" ]; then
    rm -f "$file"
    dac_die 13 "SHA-256 divergente; artefato descartado"
  fi
}

_dac_java_major() {  # <java-bin> -> major
  local v
  v="$("$1" -version 2>&1 | awk -F'"' '/version/ {print $2; exit}')"
  case "$v" in
    1.*) v="${v#1.}" ;;
  esac
  v="${v%%[.-]*}"
  printf '%s' "$v"
}

_dac_pom_java() {  # <pom> -> major requerido (vazio se ausente/ambiguo)
  local pom="$1" t v
  for t in maven.compiler.release java.version maven.compiler.source maven.compiler.target; do
    v="$(sed -n "s:.*<$t>[[:space:]]*\([^<[:space:]]*\)[[:space:]]*</$t>.*:\1:p" "$pom" | head -1)"
    if [ -n "$v" ]; then
      case "$v" in *'$'*) return 0 ;; esac
      case "$v" in 1.*) v="${v#1.}" ;; esac
      printf '%s' "${v%%[.-]*}"
      return 0
    fi
  done
}

# dac_detect_jdk [raiz-do-projeto]  -> exporta DAC_JDK_MAJOR / DAC_JDK_REQUIRED (e JAVA_HOME se DAC_JAVA_HOME)
dac_detect_jdk() {
  local root="${1:-}" javabin="" have req=""
  if [ -n "${DAC_JAVA_HOME:-}" ]; then
    [ -e "$DAC_JAVA_HOME/bin/java" ] || [ -e "$DAC_JAVA_HOME/bin/java.exe" ] || dac_die 12 "DAC_JAVA_HOME invalido (sem bin/java)"
    export JAVA_HOME="$DAC_JAVA_HOME"
    javabin="$DAC_JAVA_HOME/bin/java"
  elif [ -n "${JAVA_HOME:-}" ] && { [ -e "$JAVA_HOME/bin/java" ] || [ -e "$JAVA_HOME/bin/java.exe" ]; }; then
    javabin="$JAVA_HOME/bin/java"
  elif command -v java >/dev/null 2>&1; then
    javabin="java"
  else
    dac_die 12 "JDK ausente; defina DAC_JAVA_HOME ou JAVA_HOME"
  fi
  have="$(_dac_java_major "$javabin")"
  case "$have" in ""|*[!0-9]*) dac_die 12 "nao foi possivel determinar a versao do JDK" ;; esac
  DAC_JDK_MAJOR="$have"
  if [ -n "$root" ] && [ -f "$root/pom.xml" ]; then
    req="$(_dac_pom_java "$root/pom.xml")"
    case "$req" in *[!0-9]*) req="" ;; esac
  fi
  DAC_JDK_REQUIRED="$req"
  if [ -z "$req" ]; then
    [ -n "${DAC_JAVA_HOME:-}" ] || dac_die 12 "versao Java ausente/ambigua no pom.xml; defina DAC_JAVA_HOME"
  elif [ "$have" -lt "$req" ]; then
    dac_die 12 "JDK $have incompativel com pom (requer >= $req); defina DAC_JAVA_HOME"
  fi
  export DAC_JDK_MAJOR DAC_JDK_REQUIRED
}

# ---- cascata (Chain of Responsibility): cada _dac_try_* retorna 0 e preenche DAC_MAVEN_CMD/KIND ----
_dac_set() { DAC_MAVEN_CMD=("${@:2}"); DAC_MAVEN_KIND="$1"; }

_dac_mvnd_name() { case "$(dac_platform)" in windows-*) printf 'mvnd.cmd' ;; *) printf 'mvnd' ;; esac; }

_dac_try_env() {
  local b
  if [ -n "${DAC_MAVEN_BIN:-}" ]; then
    [ -e "$DAC_MAVEN_BIN" ] || command -v "$DAC_MAVEN_BIN" >/dev/null 2>&1 || dac_die 10 "DAC_MAVEN_BIN invalido"
    case "$(basename "$DAC_MAVEN_BIN")" in
      mvnd*) _dac_set mvnd "$DAC_MAVEN_BIN" ;;
      mvnw*) _dac_set mvnw "$DAC_MAVEN_BIN" ;;
      *) _dac_set mvn "$DAC_MAVEN_BIN" ;;
    esac
    return 0
  fi
  if [ -n "${MVND_HOME:-}" ]; then
    b="$MVND_HOME/bin/$(_dac_mvnd_name)"
    [ -e "$b" ] || dac_die 10 "MVND_HOME invalido (sem bin/mvnd)"
    _dac_set mvnd "$b"; return 0
  fi
  return 1
}

_dac_try_wrapper() {  # <raiz>
  local root="${1:-}"
  [ -n "$root" ] && [ -f "$root/mvnw" ] || return 1
  if [ -x "$root/mvnw" ]; then _dac_set mvnw "$root/mvnw"; else _dac_set mvnw bash "$root/mvnw"; fi
}

_dac_try_mvnd_path() { local b; b="$(command -v mvnd 2>/dev/null)" && _dac_set mvnd "$b"; }
_dac_try_mvn() { local b; b="$(command -v mvn 2>/dev/null)" && _dac_set mvn "$b"; }

_dac_try_cache() {
  local ver plat b
  ver="$(dac_lock_get mvnd version)"; plat="$(dac_platform)"
  [ -n "$ver" ] || return 1
  b="$(dac_cache_dir)/mvnd/$ver/$plat/bin/$(_dac_mvnd_name)"
  [ -e "$b" ] && _dac_set mvnd "$b"
}

_dac_try_bootstrap() {
  local out rc=0
  if [ "${DAC_NO_BOOTSTRAP:-0}" = "1" ]; then DAC_BOOT_RC=10; return 1; fi
  out="$("$DAC_DEV_DIR/bootstrap-mvnd.sh")" || rc=$?
  if [ "$rc" -eq 0 ] && [ -n "$out" ]; then _dac_set mvnd "$out"; return 0; fi
  [ "$rc" -eq 13 ] && exit 13   # SHA divergente nunca cai em fallback
  DAC_BOOT_RC="$rc"
  return 1
}

# dac_find_mvnd: mvnd ja disponivel (env/PATH/cache), sem bootstrap. Usado por --stop.
dac_find_mvnd() { _dac_try_env && [ "$DAC_MAVEN_KIND" = mvnd ] && return 0; _dac_try_mvnd_path || _dac_try_cache; }

# dac_resolve_maven <raiz-do-projeto-alvo>
dac_resolve_maven() {
  local root="${1:-}" wrapper_present=0
  case "$DAC_MVN_MODE" in daemon|wrapper|auto) ;; *) dac_die 2 "DAC_MVN_MODE invalido (daemon|wrapper|auto)" ;; esac
  [ -n "$root" ] && [ -f "$root/mvnw" ] && wrapper_present=1
  _dac_try_env && return 0
  case "$DAC_MVN_MODE" in
    wrapper)
      _dac_try_wrapper "$root" && return 0
      dac_log "[FALLBACK] mvnw do alvo ausente; tentando mvnd/mvn"
      _dac_try_mvnd_path && return 0
      _dac_try_mvn && return 0
      _dac_try_cache && return 0
      ;;
    auto)
      _dac_try_wrapper "$root" && return 0
      _dac_try_mvnd_path && return 0
      _dac_try_mvn && return 0
      _dac_try_cache && return 0
      ;;
    daemon)
      _dac_try_mvnd_path && return 0
      _dac_try_cache && return 0
      if _dac_try_bootstrap; then return 0; fi
      dac_log "[FALLBACK] mvnd indisponivel (bootstrap rc=$DAC_BOOT_RC); tentando mvnw/mvn"
      if [ "$DAC_ALLOW_TARGET_WRAPPER" = "1" ]; then _dac_try_wrapper "$root" && return 0; fi
      _dac_try_mvn && return 0
      [ "$wrapper_present" -eq 1 ] && [ "$DAC_ALLOW_TARGET_WRAPPER" != "1" ] \
        && dac_die 16 "mvnw do alvo bloqueado (defina DAC_ALLOW_TARGET_WRAPPER=1 ou DAC_MVN_MODE=wrapper)"
      [ "$DAC_BOOT_RC" -ne 0 ] && [ "$DAC_BOOT_RC" -ne 10 ] && dac_die "$DAC_BOOT_RC" "bootstrap do mvnd falhou e nao ha alternativa"
      dac_die 10 "nenhum Maven resolvido"
      ;;
  esac
  if [ "$DAC_MVN_MODE" != daemon ]; then _dac_try_bootstrap && return 0; fi
  [ "$DAC_BOOT_RC" -ne 0 ] && [ "$DAC_BOOT_RC" -ne 10 ] && dac_die "$DAC_BOOT_RC" "bootstrap do mvnd falhou e nao ha alternativa"
  dac_die 10 "nenhum Maven resolvido"
}
