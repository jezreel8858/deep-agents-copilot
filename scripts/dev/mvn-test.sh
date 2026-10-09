#!/usr/bin/env bash
# Executa Maven (default: `test`) em um projeto-alvo via runtime embutido. Saida enxuta + log completo fora do repo.
# Uso: mvn-test.sh [--dry-run] <raiz-do-projeto> [args-maven...] | --stop | --help
# Exit: 0 ok | 1 build/teste | 2 uso | 10 sem Maven | 11 rede | 12 JDK | 13 SHA | 14 plataforma | 15 timeout | 16 mvnw bloqueado
# Env: DAC_MVN_MODE=daemon(default)|wrapper|auto  DAC_MVN_TIMEOUT (s, default 900 = 15 min; REVISAO HUMANA)
#      DAC_MVND_OPTS (args extras so para mvnd, ex.: -Dmvnd.maxHeapSize=1g)  DAC_MVN_STOP_ON_EXIT=1
#      DAC_JAVA_HOME  DAC_MAVEN_BIN  MVND_HOME  DAC_ALLOW_TARGET_WRAPPER=1  DAC_LOG_DIR (default: cache do usuario)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/resolve.sh
. "$SCRIPT_DIR/lib/resolve.sh"

DAC_MVN_TIMEOUT="${DAC_MVN_TIMEOUT:-900}"

usage() { sed -n '2,7p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

dry=0
[ $# -gt 0 ] || { usage >&2; dac_die 2 "informe a raiz do projeto"; }

stop_mvnd() {
  if dac_find_mvnd; then
    timeout 60 "${DAC_MAVEN_CMD[@]}" --stop >/dev/null 2>&1 || true
    dac_log "mvnd --stop executado"
  else
    dac_log "nenhum mvnd localizado; nada a parar"
  fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --stop) stop_mvnd; exit 0 ;;
    --dry-run) dry=1; shift ;;
    *) break ;;
  esac
done
[ $# -gt 0 ] || dac_die 2 "informe a raiz do projeto"

root="$1"; shift
[ -d "$root" ] && [ -f "$root/pom.xml" ] || dac_die 2 "raiz invalida (pom.xml ausente)"
case "$DAC_MVN_TIMEOUT" in ""|*[!0-9]*) dac_die 2 "DAC_MVN_TIMEOUT deve ser numerico (segundos)" ;; esac
root="$(cd "$root" && pwd)"

args=("$@")
[ ${#args[@]} -gt 0 ] || args=(test)

if [ "$dry" -eq 1 ]; then export DAC_NO_BOOTSTRAP=1; fi
dac_detect_jdk "$root"
dac_resolve_maven "$root"

cmd=("${DAC_MAVEN_CMD[@]}" -B -ntp)
if [ "$DAC_MAVEN_KIND" = mvnd ] && [ -n "${DAC_MVND_OPTS:-}" ]; then
  # shellcheck disable=SC2206
  cmd+=(${DAC_MVND_OPTS})
fi
cmd+=("${args[@]}")

logdir="${DAC_LOG_DIR:-$(dac_cache_dir)/logs}"
log="$logdir/mvn-test-$(date +%Y%m%d-%H%M%S)-$$.log"

dac_log "modo=$DAC_MVN_MODE maven=$DAC_MAVEN_KIND jdk=$DAC_JDK_MAJOR timeout=${DAC_MVN_TIMEOUT}s"
if [ "$dry" -eq 1 ]; then
  dac_log "dry-run: ${args[*]}"
  dac_log "log: $(dac_tilde "$log")"
  exit 0
fi

mkdir -p "$logdir"
if [ "${DAC_MVN_STOP_ON_EXIT:-0}" = "1" ] && [ "$DAC_MAVEN_KIND" = mvnd ]; then
  trap 'timeout 60 "${DAC_MAVEN_CMD[@]}" --stop >/dev/null 2>&1 || true' EXIT
fi

start=$SECONDS
rc=0
( cd "$root" && timeout "$DAC_MVN_TIMEOUT" "${cmd[@]}" ) >"$log" 2>&1 || rc=$?
elapsed=$((SECONDS - start))

if [ "$rc" -eq 124 ]; then
  dac_log "timeout excedido (${DAC_MVN_TIMEOUT}s); log: $(dac_tilde "$log")"
  [ "$DAC_MAVEN_KIND" = mvnd ] && { timeout 60 "${DAC_MAVEN_CMD[@]}" --stop >/dev/null 2>&1 || true; }
  exit 15
fi

tests="$(grep -E '^\[[A-Z]+\] Tests run:' "$log" | grep -v ' in ' | tail -1 || true)"
mods="$(grep -cE '^\[INFO\] .* (SUCCESS|FAILURE) \[' "$log" || true)"
build="$(grep -E 'BUILD (SUCCESS|FAILURE)' "$log" | tail -1 | sed 's/^\[[A-Z]*\] //' || true)"
printf 'resultado: %s | tempo: %ss | modulos: %s\n' "${build:-sem BUILD}" "$elapsed" "${mods:-0}"
[ -z "$tests" ] || printf '%s\n' "${tests#*] }"
if [ "$rc" -ne 0 ]; then
  grep -E '^\[ERROR\]' "$log" | head -15 || true
  [ "$DAC_MAVEN_KIND" = mvnd ] && { timeout 60 "${DAC_MAVEN_CMD[@]}" --stop >/dev/null 2>&1 || true; }
fi
printf 'log: %s\n' "$(dac_tilde "$log")"
[ "$rc" -eq 0 ] || exit 1
