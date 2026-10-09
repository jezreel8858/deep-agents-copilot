# Maven — Cascata de Resolução, JDK e Daemon

Origem: `scripts/dev/lib/resolve.sh` (`dac_resolve_maven`, `dac_detect_jdk`) e `scripts/dev/mvn-test.sh`.

## Cascata por modo

| Passo | `daemon` (default) | `wrapper` | `auto` |
| :---: | :--- | :--- | :--- |
| 0 | `DAC_MAVEN_BIN` → `MVND_HOME` (inválido = exit 10) | idem | idem |
| 1 | mvnd no PATH | `./mvnw` do alvo (se ausente: `[FALLBACK]`) | `./mvnw` do alvo |
| 2 | mvnd no cache do usuário | mvnd no PATH | mvnd no PATH |
| 3 | bootstrap do mvnd (SHA-256) | `mvn` no PATH | `mvn` no PATH |
| 4 | `[FALLBACK]`: `./mvnw` do alvo (só com `DAC_ALLOW_TARGET_WRAPPER=1`) | mvnd no cache | mvnd no cache |
| 5 | `mvn` no PATH | bootstrap do mvnd | bootstrap do mvnd |
| fim | `mvnw` presente e não permitido → exit 16; falha de bootstrap → seu exit (11/14…); senão exit 10 | exit 10 / rc do bootstrap | idem |

- SHA divergente no bootstrap → exit 13 imediato (sem fallback).
- `--dry-run` define `DAC_NO_BOOTSTRAP=1`: nunca baixa nem instala.

## JDK

1. `DAC_JAVA_HOME` (deve ter `bin/java`; exportado como `JAVA_HOME`) → 2. `JAVA_HOME` → 3. `java` no PATH; nenhum → exit 12.
2. Versão exigida lida do `pom.xml` (`maven.compiler.release`, `java.version`, `maven.compiler.source`, `maven.compiler.target`); JDK menor que a exigida → exit 12.
3. Versão ausente/ambígua (ex.: propriedade com `$`) sem `DAC_JAVA_HOME` → exit 12 com instrução de definir `DAC_JAVA_HOME`.

## Bootstrap do mvnd

- Versão/URL/SHA-256 por plataforma em `tools.lock` (`[mvnd]`); hosts permitidos: `downloads.apache.org`, `archive.apache.org`.
- Idempotente: lock por diretório (`DAC_LOCK_WAIT`), extração em tmp + `mv` atômico, healthcheck `--version`.
- SHA pendente/vazio ou plataforma ausente → exit 14. Nunca usar placeholder.
- Online obrigatório no 1º bootstrap; depois, cache do usuário. Air-gapped/espelho interno fora de escopo.

## Daemon — operação e mitigação

- Parada: `scripts/dev/mvn-test.sh --stop` (localiza mvnd via env/PATH/cache; `timeout 60`; sempre exit 0).
- Parada automática: falha de build (exit 1), timeout (exit 15) e, opcional, saída (`DAC_MVN_STOP_ON_EXIT=1`).
- Heap/opções só do mvnd: `DAC_MVND_OPTS` (ex.: `-Dmvnd.maxHeapSize=1g`).
- Windows: travamento de `target/` e jars em uso → rodar `--stop` antes de limpar o alvo.
- Execução usa `-B -ntp`, args default `test`, sem `clean` implícito; log em `<HOME>/.cache/deep-agents-copilot/logs/mvn-test-<data>-<pid>.log`.
