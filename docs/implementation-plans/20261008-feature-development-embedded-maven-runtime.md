---
status: approved
approved_by: humano (aprovação explícita via ask_questions)
approved_date: 2026-10-08
date: 2026-10-08
autor: spring-boot-arch-advisor
workflow: feature-development
related-planning-doc: docs/implementation-plans/20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md
tier: full
plan_ref: docs/implementation-plans/20261008-feature-development-embedded-maven-runtime.md
reversibility: T2
progress: 0
allowed_files:
  - scripts/dev/lib/resolve.sh
  - scripts/dev/tools.lock
  - scripts/dev/bootstrap-mvnd.sh
  - scripts/dev/mvn-test.sh
  - scripts/dev/mvn-test.cmd
  - .gitattributes
  - .gitignore
  - nul
  - .github/skills/embedded-runtime-governance/SKILL.md
  - .github/skills/.index.json
  - .github/agents/backend/spring-boot/spring-boot-developer.agent.md
  - .github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md
  - .github/agents/backend/spring-reactive/spring-reactive-developer.agent.md
  - .github/agents/backend/spring-reactive/spring-reactive-test-engineer.agent.md
  - .github/agents/backend/ejb/ejb-developer.agent.md
  - .github/agents/backend/ejb/ejb-test-engineer.agent.md
  - .github/agents/backend/struts/struts-developer.agent.md
  - .github/agents/backend/struts/struts-test-engineer.agent.md
  - .github/agents/runtime-verifier.agent.md
  - .github/agents/pr-gatekeeper.agent.md
  - .github/agents/backend/spring-boot/spring-boot-catalog.yaml
  - .github/agents/backend/spring-reactive/spring-reactive-catalog.yaml
  - .github/agents/backend/ejb/ejb-catalog.yaml
  - .github/agents/backend/struts/struts-catalog.yaml
  - .github/agents/catalog.yaml
  - .a2a/agentcards/spring-boot-developer.agentcard.json
  - .a2a/agentcards/spring-boot-test-engineer.agentcard.json
  - .a2a/agentcards/spring-reactive-developer.agentcard.json
  - .a2a/agentcards/spring-reactive-test-engineer.agentcard.json
  - .a2a/agentcards/ejb-developer.agentcard.json
  - .a2a/agentcards/ejb-test-engineer.agentcard.json
  - .a2a/agentcards/struts-developer.agentcard.json
  - .a2a/agentcards/struts-test-engineer.agentcard.json
  - .a2a/agentcards/runtime-verifier.agentcard.json
  - .a2a/agentcards/pr-gatekeeper.agentcard.json
  - tests/governance_audit/test_embedded_maven_runtime_governance.py
---

Progresso: 0/14 tarefas concluídas

# Plano de Implementação Técnica — Runtime Maven Embutido (wrappers + mvnd verificado)

> Escopo: ADVISORY (Gate 2, R-064). Plano sem código. Dono: `spring-boot-arch-advisor` (Maven/Java + infra compartilhada `scripts/dev/lib`). Plano paralelo: `python-arch-advisor` (dono de `pyproject.toml`, `uv.lock`, `.python-version`, `py-test.sh`).
> Higiene (R-038/R-043/R-044): nenhum caminho de máquina, nome de usuário ou nome de projeto local em arquivos versionados. Usar apenas `<workspace>`, `<HOME>`, `[PROJETO-ALVO]`.

## 1. Dependência cruzada

- Mesmo commit/PR da consolidação `20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md` (não editado por este plano; apenas referenciado em `related-planning-doc`).
- Arquivos compartilháveis com aquele plano: `.gitignore`, `.gitattributes`, `.github/skills/.index.json`, `.github/agents/catalog.yaml`, `.a2a/agentcards/*`. Regra: mudanças **aditivas** e por linhas distintas; o executor faz rebase/merge manual e roda a suíte `tests/governance_audit` ao final (ver §7).
- Ordem: este plano executa **após** a consolidação frontend concluir suas edições de catálogo/index (evita conflito), e **depois** da tarefa T1 do plano Python (criação dos arquivos de fronteira, ver §3).

## 2. Fronteira com o plano Python (anti-conflito)

| Artefato | Dono | Regra |
|---|---|---|
| `scripts/dev/lib/resolve.sh` | **Este plano (Maven/infra)** | Lib compartilhada; Python apenas faz `source` e usa funções `dac_log`, `dac_die`, `dac_cache_dir`, `dac_verify_sha256`, `dac_download`. Sem edições do plano Python. |
| `scripts/dev/tools.lock` | **Este plano** | Seção `[mvnd]` minha; plano Python pode **anexar** seção `[uv]` em bloco separado, após meu merge. Formato chave=valor estável (contrato). |
| `scripts/dev/bootstrap-mvnd.sh`, `mvn-test.sh`, `mvn-test.cmd` | Este plano | — |
| `scripts/dev/py-test.sh`, `pyproject.toml`, `uv.lock`, `.python-version` | Plano Python | Não tocados aqui. |
| `.gitignore`, `.gitattributes` | Este plano (cria regras Maven/EOL/logs) | Plano Python só adiciona `.venv/` etc. em commit posterior ou linha própria. |
| Skill `embedded-runtime-governance` | Este plano | Contrato de exit codes comum; plano Python referencia por ponteiro (seção própria para uv fica sob autoria Python após merge). |
| `tests/governance_audit/test_embedded_maven_runtime_governance.py` | Este plano | Teste Python equivalente em arquivo separado do plano Python. |

Ordem sugerida: (1) este plano entrega `resolve.sh` + `tools.lock` + `.gitattributes` + `.gitignore` primeiro (T1–T3) → (2) plano Python consome a lib → (3) demais tarefas deste plano (skill, agents, testes) seguem em paralelo.

## 3. Mini-ADRs

### ADR-1 — mvnd com daemon (decisão humana) vs. wrapper/`--no-daemon`
- Contexto: recomendação técnica era `auto` com `--no-daemon` em agents (previsível, sem processo residual).
- Decisão (humana): **sempre mvnd com daemon** como padrão em `mvn-test.sh`.
- Alternativas: wrapper `mvnw` (reprodutível, sem binário extra, mais lento a frio); `mvnd --no-daemon` (sem residual, perde ganho de latência).
- Consequências: builds repetidos mais rápidos; **risco aceito** (ver §5): daemon órfão, RAM residual, travamento de arquivos no Windows (`target/`, jars em uso). Mitigações obrigatórias descritas em §5.
- Override: `DAC_MVN_MODE=wrapper|auto|daemon` (default `daemon`).

### ADR-2 — wrappers versionados + download verificado SHA-256 + `uv` vs. `mise`
- Decisão: scripts versionados em `scripts/dev/` + `tools.lock` com SHA-256 + `uv` para Python.
- Alternativa **rejeitada**: `mise` (nova ferramenta obrigatória, shims em PATH, superfície de configuração extra, política corporativa incerta).
- Consequências: zero dependência prévia além de `bash`, `curl`/`wget`, `sha256sum`/`shasum`, `tar`/`unzip`; manutenção manual de versões/hashes no `tools.lock`.

### ADR-3 — `assets/maven-mvnd-*` fora do versionamento
- Decisão: ignorar `/assets/maven-mvnd-*/`; bootstrap baixa para cache do usuário (`${XDG_CACHE_HOME:-$HOME/.cache}/deep-agents-copilot/mvnd/<versão>/<plataforma>`). **Sem Git LFS.**
- Consequências: repositório leve (−43 MB de risco de commit acidental); exige rede no 1º uso (ver pendência offline §9). O diretório local existente permanece como cache oportunista opcional (fonte local), nunca rastreado.

## 4. Especificação técnica (sem código)

### 4.1 `scripts/dev/lib/resolve.sh` (somente `source`, sem efeitos colaterais)
Cascata de resolução do binário Maven (primeira que satisfizer vence; `DAC_MVN_MODE` filtra a elegibilidade):
1. Env explícito: `DAC_MAVEN_BIN` (binário) ou `MVND_HOME` (`$MVND_HOME/bin/mvnd`).
2. `./mvnw` do **projeto-alvo** `[PROJETO-ALVO]`: usado se existir **quando `DAC_MVN_MODE=wrapper|auto`** (decisão humana 2026-10-08; execução de wrapper do alvo é execução de código arbitrário — risco aceito e documentado na skill). No modo padrão (`daemon`) a prioridade permanece mvnd (ADR-1).
3. `mvnd` no `PATH`.
4. `mvn` no `PATH`.
5. Bootstrap (`bootstrap-mvnd.sh`) para cache do usuário → resolve de lá.
6. Erro explícito (exit codes abaixo).

Observação: com `DAC_MVN_MODE=daemon` (default) a ordem efetiva prefere mvnd (itens 1/3/5) e cai em `mvnw`/`mvn` somente com **fallback sinalizado** (log `[FALLBACK]`) quando mvnd for indisponível. `wrapper` prioriza item 2→4; `auto` segue a cascata acima.

Funções públicas (contrato): `dac_resolve_maven`, `dac_cache_dir`, `dac_platform` (os-arch normalizado: linux-amd64, darwin-amd64, darwin-aarch64, windows-amd64), `dac_download`, `dac_verify_sha256`, `dac_log`, `dac_die <code> <msg>`, `dac_detect_jdk`.

JDK: parâmetro, nunca hardcode. Ordem: `DAC_JAVA_HOME` → `JAVA_HOME` → `java` no PATH. Versão exigida por stack é lida **em runtime** do `pom.xml` do `[PROJETO-ALVO]` (`maven.compiler.release|source|target`, `java.version`, `maven-toolchains`); se ausente/ambíguo, `exit 12` com instrução de definir `DAC_JAVA_HOME` (lacuna §9). Stacks legados (EJB/Struts) podem exigir JDK 8/11 → nunca assumir 21.

Contrato de exit codes (compartilhado, documentado na skill):

| Code | Significado |
|---|---|
| 0 | Sucesso |
| 1 | Falha de build/teste Maven (propagado do alvo) |
| 2 | Uso inválido (args, raiz do projeto sem `pom.xml`) |
| 10 | Nenhum Maven resolvido (cascata esgotada, bootstrap indisponível) |
| 11 | Falha de download/rede/offline sem cache |
| 12 | JDK ausente ou incompatível com o pom do alvo |
| 13 | SHA-256 divergente (artefato descartado, nunca instalado) |
| 14 | Plataforma sem entrada no `tools.lock` |
| 15 | Timeout excedido (daemon ou build; ver §5) |
| 16 | Política bloqueou `mvnw` do alvo e não há alternativa |

### 4.2 `scripts/dev/tools.lock`
- Formato chave=valor por seção, ex.: `[mvnd]` com `version=1.0.6`, e por plataforma `url.<plataforma>=` e `sha256.<plataforma>=`.
- URLs: **somente oficiais** (host de releases do projeto Apache Maven Daemon / `downloads.apache.org` ou `archive.apache.org`) — allowlist de host verificada em teste.
- SHA-256: **nunca inventado**. Executor obtém os valores da página/arquivos `.sha256` oficiais do release 1.0.6, grava e **revalida** baixando o artefato e calculando localmente; divergência bloqueia o merge. Plataformas faltantes ficam ausentes (→ exit 14), jamais com placeholder.
- Comentário de proveniência por entrada (URL de origem da checksum), sem dados de máquina.

### 4.3 `scripts/dev/bootstrap-mvnd.sh`
- Idempotente: se `<cache>/<versão>/<plataforma>/bin/mvnd` existe e executa `--version`, retorna 0 sem rede.
- Fluxo: ler `tools.lock` → baixar para arquivo temporário (`mktemp` no mesmo filesystem do cache) → validar SHA-256 → extrair em diretório temporário → `mv` atômico para destino final → limpar temporários via `trap`.
- Lock simples (diretório `mkdir`) para evitar bootstrap concorrente; timeout de espera.
- Cache: `${XDG_CACHE_HOME:-$HOME/.cache}/deep-agents-copilot/`; no Windows (Git Bash) `$HOME` resolve para `<HOME>`.
- Saída enxuta; exit codes do §4.1; nunca imprime caminhos absolutos em artefatos versionados (logs vão para diretório ignorado).

### 4.4 `scripts/dev/mvn-test.sh <raiz-do-projeto> [args]`
- Valida raiz (`pom.xml`), resolve Maven e JDK, executa `test` (default) com `-q -B -ntp` + args repassados.
- mvnd por padrão (`DAC_MVN_MODE=daemon`); timeout (`DAC_MVN_TIMEOUT`, default definido pelo executor, ex.: 20 min) → exit 15 e `mvnd --stop`.
- Saída enxuta: stdout/stderr integrais para arquivo de log em diretório ignorado (`logs/dev/` ou `target/`‑externo), e no terminal apenas **resumo** (módulos/testes executados, falhas, tempo) + caminho **relativo** do log.
- Não faz `clean` implícito (evita travar `target/` no Windows); `clean` só via arg explícito.
- Subcomando/flag `--stop` → `mvnd --stop` (cleanup); trap de EXIT opcional `DAC_MVN_STOP_ON_EXIT=1`.

### 4.5 `scripts/dev/mvn-test.cmd` (opcional)
- Shim que localiza `bash` (Git for Windows) e delega a `mvn-test.sh`, propagando exit code. Sem lógica duplicada. Se `bash` ausente → exit 10 com mensagem.

### 4.6 `.gitattributes` / `.gitignore` / artefato `nul`
- `.gitattributes`: `*.sh text eol=lf`; `*.cmd text eol=crlf`; `scripts/dev/tools.lock text eol=lf`.
- `.gitignore`: adicionar `/assets/maven-mvnd-*/` e diretório de logs (`logs/dev/`). A entrada `nul` já existe no `.gitignore`.
- Arquivo `nul` na raiz: arquivo regular de 179 bytes, ignorado (artefato típico de redirecionamento `> nul` em shell Unix no Windows). **Confirmar** conteúdo via `ctx_execute_file` (não é conteúdo sensível?) antes de remover; remoção só do arquivo de trabalho local (não rastreado) e manter a regra do `.gitignore`. Atenção: `nul` é nome reservado no Windows — remover com prefixo de namespace/via Git Bash.

### 4.7 Skill `embedded-runtime-governance` (nova)
- `.github/skills/embedded-runtime-governance/SKILL.md`: contrato de exit codes, cascata de resolução, política de `DAC_MVN_MODE`, `DAC_ALLOW_TARGET_WRAPPER`, parâmetro JDK, mitigação do daemon, fallback, regra de higiene (sem caminhos/nomes). Progressive disclosure (R-066): agents referenciam por **ponteiro** (`source_docs_lazy`/seção “Runtime Maven embutido”), sem copiar conteúdo.
- Registrar em `.github/skills/.index.json` (+ sincronizar `catalog.yaml` global).
- Skill é multi-stack: seção Python reservada ao plano Python (apenas âncora/ponteiro).

### 4.8 Agents a atualizar (ponteiro à skill, sem duplicar)
spring-boot, spring-reactive, ejb, struts × (developer, test-engineer) + `runtime-verifier` + `pr-gatekeeper`. Alteração mínima por agent: 1 linha de regra “executar Maven apenas via `scripts/dev/mvn-test.sh <raiz>`; contrato em skill `embedded-runtime-governance`” e inclusão da skill em `source_docs_lazy`/skills. Respeitar R-054/baseline de contagem por stack (nenhum agent novo). Sincronizar sub-catálogos `*-catalog.yaml`, `catalog.yaml`, agentcards `.a2a/agentcards/*` e `.index.json`.

## 5. Riscos

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| **[ACEITO — decisão humana]** Daemon órfão/RAM residual/travamento de arquivos no Windows (modo sempre-daemon) | Média | Médio–Alto | `mvnd --stop` exposto (`mvn-test.sh --stop`) e invocado em falha/timeout; `DAC_MVN_STOP_ON_EXIT`; timeout (exit 15); sem `clean` implícito; limite de memória do daemon documentado (`-Xmx` via `DAC_MVND_OPTS`); override `DAC_MVN_MODE=wrapper|auto` e fallback `mvnw`/`mvn` quando mvnd indisponível, com log `[FALLBACK]`; orientação de cleanup na skill |
| Supply chain (artefato adulterado) | Baixa | Alto | SHA-256 obrigatório, URLs oficiais (host allowlist), extração temporária + `mv` atômico, descarte em divergência (exit 13) |
| Hash inventado/errado | Média | Alto | Executor valida na fonte oficial **e** localmente; teste de formato (64 hex) + revisão humana |
| Execução de `./mvnw` do alvo não confiável | Média | Alto | `DAC_ALLOW_TARGET_WRAPPER` + política; wrapper do alvo é ordem 2 só quando permitido |
| JDK incompatível por stack (EJB/Struts legados) | Alta | Médio | Lê pom em runtime; exit 12; parâmetro `DAC_JAVA_HOME`; pendência humana |
| CRLF quebrando `.sh` no Windows | Média | Médio | `.gitattributes` + teste de ausência de `\r` |
| Vazamento de caminho/usuário em scripts/logs | Média | Médio | Teste de varredura; logs ignorados; mensagens com caminhos relativos/`<HOME>` |
| Conflito de merge com consolidação e plano Python | Média | Baixo | Ordem do §2 e edições aditivas |
| Bit executável perdido no Windows | Média | Médio | `git update-index --chmod=+x` na checagem do executor (ver validação); teste verifica modo no índice |

## 6. Checklist de Execução Técnica (ordem cronológica, Plan-Then-Batch R-059)

- [ ] T1. Criar `scripts/dev/tools.lock` (seção `[mvnd]`, v1.0.6) com URLs oficiais e SHA-256 obtidos **via web da página oficial de releases** e revalidados por download local `{paralelizavel: false, responsavel: "@spring-boot-developer"}`
- [ ] T2. Criar `.gitattributes` e atualizar `.gitignore` (`/assets/maven-mvnd-*/`, logs) `{paralelizavel: true, responsavel: "@spring-boot-developer"}`
- [ ] T3. Criar `scripts/dev/lib/resolve.sh` (cascata, exit codes, JDK por parâmetro/pom) `{paralelizavel: false, responsavel: "@spring-boot-developer"}`
- [ ] T4. Criar `scripts/dev/bootstrap-mvnd.sh` (idempotente, SHA-256, tmp+mv atômico, cache do usuário) `{paralelizavel: false, responsavel: "@spring-boot-developer"}`
- [ ] T5. Criar `scripts/dev/mvn-test.sh` (+ `--stop`, timeout, log/resumo) e `mvn-test.cmd` opcional; marcar bit executável no índice `{paralelizavel: false, responsavel: "@spring-boot-developer"}`
- [ ] T6. Confirmar e remover artefato `nul` da raiz (arquivo de trabalho local; manter regra do `.gitignore`) `{paralelizavel: true, responsavel: "@spring-boot-developer"}`
- [ ] T7. Criar skill `embedded-runtime-governance/SKILL.md` e registrar em `.github/skills/.index.json` `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [ ] T8. Atualizar os 8 agents backend (spring-boot/spring-reactive/ejb/struts × developer/test-engineer) com ponteiro à skill `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [ ] T9. Atualizar `runtime-verifier` e `pr-gatekeeper` com ponteiro à skill `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [ ] T10. Sincronizar `*-catalog.yaml`, `catalog.yaml`, agentcards e `source_docs` `{paralelizavel: false, responsavel: "@governance-maintainer"}`
- [x] T11. Criar `tests/governance_audit/test_embedded_maven_runtime_governance.py` (ver §7) `{paralelizavel: true, responsavel: "@spring-boot-test-engineer"}`
- [ ] T12. Smoke test do bootstrap em cache temporário isolado e do `mvn-test.sh` contra fixture Maven mínima criada em diretório temporário (fora do repo) `{paralelizavel: false, responsavel: "@spring-boot-test-engineer"}`
- [ ] T13. Integração com plano Python e plano de consolidação (merge de `.gitignore`/index/catálogos; rodar suíte completa) `{paralelizavel: false, responsavel: "@governance-maintainer"}`
- [ ] T14. Revisão final (R-038/R-043/R-044 sweep, `pr-gatekeeper`) e atualização de `progress`/`status: approved` conforme gate `{paralelizavel: false, responsavel: "@pr-gatekeeper"}`

## 7. Validação (silenciosa)

Execução via `ctx_execute`/`ctx_batch_execute` com saída resumida (somente falhas e contagens):
- `pytest tests/governance_audit -q` (suíte completa; sem `-s`), mais o novo teste isolado.
- Teste novo (`test_embedded_maven_runtime_governance.py`) cobre:
  1. Existência e permissão executável (índice Git `100755`) de `resolve.sh`, `bootstrap-mvnd.sh`, `mvn-test.sh`; `tools.lock` presente.
  2. Ausência de caminhos de máquina (letras de unidade, diretórios home de usuário, prefixos de perfil) e nomes de projeto locais em scripts, plano, skill e agents alterados, via regex construída em runtime no teste.
  3. `tools.lock`: cada SHA-256 casa `^[0-9a-f]{64}$`; todas as URLs em allowlist de host oficial; versão `1.0.6`; sem placeholders.
  4. Skill existe, está no `.index.json`; os 10 agents alvo referenciam `embedded-runtime-governance`; catálogos/agentcards sincronizados.
  5. `.gitignore` contém `/assets/maven-mvnd-*/`; `.gitattributes` contém `*.sh text eol=lf`; scripts sem `\r`.
  6. `bash -n` (sintaxe) dos scripts e `shellcheck` se disponível (skip se ausente).
- `git ls-files assets/` não pode listar `maven-mvnd-*`.

## 8. Rollback (T2)

- Reverter o commit; scripts/skill/testes são aditivos. Remover entradas na skill no `.index.json`/catálogos/agentcards via revert do mesmo commit.
- Cache do usuário (`<HOME>/.cache/deep-agents-copilot/`) não é rastreado: limpeza manual opcional; executar `mvnd --stop` antes para liberar arquivos no Windows.
- `DAC_MVN_MODE=wrapper` é o rollback operacional imediato (sem revert) caso o daemon cause problemas.
- Arquivo `nul` e diretório `assets/maven-mvnd-*` locais não são recuperáveis do Git (nunca rastreados): preservar cópia fora do repositório antes da remoção/limpeza, se necessário.

## 9. Decisões humanas registradas (aprovado por humano em 2026-10-08 via ask_questions)

1. **JDK**: lido do `pom.xml` do `[PROJETO-ALVO]` em runtime (sem hardcode); ausente/ambíguo → `exit 12` com instrução de definir `DAC_JAVA_HOME`. Resolvido.
2. **Offline**: online obrigatório no 1º bootstrap; cache do usuário depois. Air-gapped/espelho interno **fora de escopo**. Resolvido.
3. **Política `mvnw`**: usar `./mvnw` do alvo se existir quando `DAC_MVN_MODE=wrapper|auto`; padrão segue mvnd com daemon (decisão humana anterior; risco aceito, ver §5). Resolvido.
4. **CI/`setup-uv`**: fora deste commit. Resolvido.
5. **Commit**: mesmo commit da consolidação. Resolvido.
6. **SHA-256 do mvnd 1.0.6**: o executor valida na página oficial de releases (todas as plataformas necessárias) e revalida por download; **revisão humana dos valores antes do merge** (gate obrigatório). Valor padrão de timeout: definido pelo executor e documentado na skill, sujeito à mesma revisão.
7. **Aprovação do frontmatter** (`draft` → `approved`): concedida em 2026-10-08.

## 10. Critérios de pronto

- Todas as tarefas T1–T14 marcadas; `progress` atualizado; suíte `tests/governance_audit` verde (silenciosa).
- `assets/maven-mvnd-*/` fora do versionamento; nenhum binário rastreado; sem LFS.
- `tools.lock` com hashes validados na origem oficial e localmente.
- `mvn-test.sh` executa teste Maven em fixture com saída enxuta, log e exit codes conforme contrato; `--stop` funcional; fallback validado.
- Skill criada e referenciada por ponteiro nos 10 agents; catálogos/agentcards/`.index.json` sincronizados.
- Sweep de higiene sem ocorrências (caminhos de máquina, usuário, nomes de projeto).
- Integração coerente com o plano Python e com o plano de consolidação (mesmo commit).

### Decisão de Design Pattern (mini-ADR — design-pattern-selection-patterns)
- Contexto: resolução de ferramenta com múltiplas fontes e fallback.
- Decisão: Chain of Responsibility simples (cascata em função shell) — sem framework.
- Alternativas: Strategy por modo (`DAC_MVN_MODE`) — absorvido como filtro da cascata; mise — rejeitado (ADR-2).
- Consequências: baixo acoplamento e testabilidade; custo: disciplina de contrato de exit codes.

### 🔒 Checklist Defensivo Pré-Code-Review
- [ ] Sanitização e validação de inputs (raiz do projeto, args repassados, valores de `tools.lock`)
- [ ] Ausência de segredos/caminhos/usuários em hardcode e logs sem PII
- [ ] Tratamento defensivo de erros (trap/cleanup, SHA-256 divergente descartado, timeout) e política de execução de `mvnw` do alvo
- [ ] Testes defensivos atendendo aos quality gates

## 11. Handoff

Após aprovação humana: `@spring-boot-developer` (T1–T6), `@governance-maintainer` (T7–T10, T13), `@spring-boot-test-engineer` (T11–T12), `@pr-gatekeeper` (T14). Coordenar com `@python-arch-advisor` conforme §2.
