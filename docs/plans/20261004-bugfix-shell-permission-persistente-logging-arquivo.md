# Plano de Planejamento — Negação persistente de shell (git status/diff) + Logging em arquivo (.tmp)

> Autoria: `bug-triage` (Etapa 1 — Triagem & Causa Raiz, WORKFLOW-BUG-FIX). Este documento NÃO
> implementa código; é o artefato R-064 que antecede a Etapa 2 (Plano de Implementação, de autoria
> do `<stack>-arch-advisor` correspondente).

## 1. Contexto

- Bugfix anterior já presente no código-fonte: `sdk_session.py:158-200` (`_comando_shell_e_seguro`)
  e `permission_policy.py:187-233` (`comando_terminal_e_seguro`) — corrigem o bug real de
  2026-10-02 em que TODO comando de shell (inclusive `git --no-pager status/diff`, 100% read-only)
  era negado com a mensagem `"Negado pela politica local (GATEWAY_PERMISSION_MODE)."`.
- Cobertura de teste existente confirma a correção: `tests/unit/test_sdk_session.py:1507-1571`
  (classe dedicada a `_comando_shell_e_seguro`) e `tests/unit/test_permission_policy.py:545-616`.
- Usuário relata que, mesmo após **2 restarts completos** (gateway + `apps/web`) e repetição do
  teste via `pr-gatekeeper`, a negação **persiste**.

## 2. Causa raiz hipotética (2 hipóteses, não mutuamente exclusivas)

### H1 — Deploy obsoleto (imagem Docker ou processo zumbi) — CONFIANÇA ALTA

**Evidência 1:** `docker-compose.yml` (linhas 15-18, comentário do próprio arquivo):
> "Nota: os serviços 'gateway' e 'web' usam `pull_policy=build`, entao o Compose SEMPRE constroi a
> imagem localmente (nunca tenta pull de registry). **Apos alterar codigo-fonte em src/ ou
> apps/web/, use '--build' (ou 'docker compose build gateway web') para forcar a reconstrucao.**"

**Evidência 2:** `docker-compose.yml` (serviço `gateway`): `pull_policy: build` sem `volumes:` de
bind-mount de `src/` para dentro do container — ou seja, o código do container é **congelado no
momento do build da imagem**. Um `docker compose restart`/`down && up` (sem `--build`) **reutiliza a
imagem já construída anteriormente**, que pode conter a versão do código ANTERIOR à correção de
`sdk_session.py`/`permission_policy.py` caso o(s) arquivo(s) tenham sido alterados depois do último
`--build`.

**Categoria:** `config-env` / deploy (não é um bug de lógica residual).

**Caminho alternativo (se o usuário roda via `dev_watch.py`, não Docker):** `dev_watch.py:416-422`
sobe `uvicorn.run(..., reload=True, reload_dirs=[str(GATEWAY_DIR / "src")])` — hot-reload cobre
`src/`, então um simples salvar do arquivo já deveria bastar SEM restart manual. Se mesmo assim a
negação persiste em modo dev, a hipótese desloca para: (a) processo `uvicorn` anterior não foi
efetivamente encerrado (porta `8080` ainda servida por worker antigo) — comum no Windows quando o
terminal é fechado sem `Ctrl+C` limpo, deixando o processo filho `reload` órfão; ou (b)
`__pycache__`/`.pytest_cache` com bytecode não invalidado (menos provável com reload ativo, mas não
descartado).

**Pergunta objetiva necessária (ver gate de aprovação):** confirmar se a execução é via
`docker compose up` (Dockerfile) ou via `python dev_watch.py` (uvicorn local com `--reload`) — a
remediação concreta (Etapa de implementação) diverge entre os dois caminhos.

### H2 — Gap de unwrapping de shell wrapper (`powershell -Command "..."`) — CONFIANÇA MÉDIA (risco residual, não necessariamente a causa DESTE incidente)

**Evidência 1:** `permission_policy.py:208-233` (`comando_terminal_e_seguro`) só reconhece o comando
como seguro se o texto normalizado **começar literalmente** com `"git "` (linha 225) ou corresponder
a um item exato da allowlist fixa `_COMANDOS_SEGUROS_NAO_GIT` (linhas 121-140, ex.: `ls`, `cat`,
`echo`). Não há nenhuma lógica de "unwrap" de invólucros de shell (`powershell -Command "..."`,
`cmd /c ...`, `bash -lc "..."`) antes dessa checagem.

**Evidência 2:** `tests/unit/test_sdk_session.py:115,241-248` — TODOS os fixtures de teste da classe
`TestPermissionRequestShell` assumem `shell_full_command_text` como o comando **bare** (ex.:
`"git --no-pager status"`), nunca testando o cenário em que o SDK entrega o texto como invólucro de
shell nativo do SO (`"powershell -Command \"git status\""`). Ou seja, a correção de 2026-10-02 nunca
foi validada contra esse formato — é um ponto cego de cobertura, não uma garantia.

**Evidência de apoio (não conclusiva):** `agent_catalog.py:99-101` (`_TOOLS_SHELL_NATIVAS =
{"run_in_terminal": "bash"}`) mostra que o gateway SEMPRE traduz `run_in_terminal` para a tool nativa
`"bash"` do SDK (nunca `"powershell"` literal) — reduz a probabilidade de H2 ser a causa raiz desta
ocorrência específica (o SDK deveria receber `"bash"` como tool, não `"powershell"`), mas não a
elimina, pois o comportamento de parsing de `full_command_text` depende de introspecção real do SDK
no SO Windows do usuário, não verificada nesta triagem (fora do escopo read-only: exigiria rodar o
SDK real).

**Categoria:** `logic-error` latente / `mini-refactoring` (função compartilhada, ver blast radius).

## 3. Blast Radius & Consumidores (Challenge Gate executado)

`comando_terminal_e_seguro`/`_comando_shell_e_seguro` são **heurísticas centralizadas (R-055)**
reutilizadas por:

| Consumidor | Arquivo:linha | Efeito de qualquer alteração |
|---|---|---|
| `routes._conservative_permission_handler` (handler default) | `api/routes.py:118` | Todo `run_in_terminal` de QUALQUER agent (não só `pr-gatekeeper`) |
| `routes._governance_permission_handler` (quando `GATEWAY_GOVERNANCE_PERMISSIONS=true`) | `api/routes.py:233` | Idem, caminho de governança |
| `sdk_session._identificador_e_seguro_nativo` (2 implementações duplicadas) | `sdk_session.py:377-388` e `sdk_session.py:1227-1238` | Bypass nativo de `PermissionRequestShell` em AMBOS os fluxos de sessão (sync/async) |
| `permission_policy.tool_call_nao_escrita_e_segura` (MCP) | `permission_policy.py:379-452` | `mcp_context-mode_ctx_execute`/`ctx_execute_file`/`ctx_batch_execute` de TODOS os ~100+ agents |
| `permission_policy._comando_batch_item_e_seguro` | `permission_policy.py:330-341` | Itens individuais de `ctx_batch_execute(commands=[...])` |

**Classificação de Blast Radius: 🟡 AMARELO (Mini-Refactoring Pontual)** — qualquer ajuste em
`comando_terminal_e_seguro` (ex.: unwrap de `powershell -Command`/`cmd /c`) atravessa handler
conservador, handler de governança, 2 pontos de bypass nativo duplicados em `sdk_session.py` e o
caminho MCP — não é um fix isolado de 1 arquivo. Exige safety net (testes de caracterização) para
os 5 consumidores acima ANTES de qualquer alteração na função compartilhada.

**Regras de negócio confirmadas via Challenge Gate (ver `ask_questions` desta sessão):** ver seção 6.

## 4. Gap de Observabilidade — Logging em arquivo

- **Estado atual:** `logging.getLogger(__name__)` é usado em 10 módulos (`agent_catalog.py`,
  `auth.py`, `governance_pipeline.py`, `permission_policy.py`, `projects_catalog.py`,
  `prompts_catalog.py`, `sdk_session.py`, `telemetry.py`, `turn_recorder.py`, `api/routes.py`), mas
  **nenhuma chamada a `logging.basicConfig`/`FileHandler`/`dictConfig` foi encontrada em todo
  `src/local_chat_gateway/`** — os logs dependem inteiramente do handler default do `uvicorn`
  (stdout/console), sem persistência em arquivo.
- **Pasta `.tmp/` candidata:** `deploy/local-chat-gateway/.tmp/` **NÃO EXISTE** hoje (verificado).
  O workspace tem um `tmp/` na RAIZ (ignorado via `/tmp/` em `.gitignore` raiz), mas vazio e sem
  relação com o gateway. O `.gitignore` do próprio `deploy/local-chat-gateway/` está **vazio** — ou
  seja, criar `.tmp/` ali exige também adicionar a entrada de ignore nesse `.gitignore` local
  (e possivelmente no `Dockerfile.dockerignore`, para não vazar logs locais para a imagem).
- **Pergunta objetiva necessária:** confirmar se o caminho correto é
  `deploy/local-chat-gateway/.tmp/gateway.log` (escopo local ao serviço, recomendado) ou um caminho
  na raiz do workspace (`./tmp/local-chat-gateway/gateway.log`) — ver gate de aprovação.

## 5. Critérios de Aceitação Objetivos

1. `docker compose build gateway && docker compose up -d` (ou `python dev_watch.py`, conforme
   resposta à pergunta da seção 2) seguido de `git --no-pager status` via `pr-gatekeeper` retorna
   sucesso (sem `"Negado pela politica local"`), reproduzindo exatamente os passos do incidente.
2. Teste de caracterização novo cobrindo `shell_full_command_text` no formato de invólucro de SO
   (`"powershell -Command \"git status\""` / `"cmd /c git status"`) — define explicitamente se H2
   é ou não um problema real (Red test antes, Green depois, se a decisão do gate for corrigir).
3. Suíte completa `tests/unit/test_sdk_session.py::TestPermissionRequestShell` e
   `tests/unit/test_permission_policy.py` (linhas 545-616) permanece 100% verde (safety net).
4. Logs do gateway passam a ser gravados em arquivo dentro de `.tmp/` (caminho exato definido no
   gate), rotacionado (`RotatingFileHandler`, limite de tamanho) e em paralelo ao stdout existente
   (não substituir, apenas adicionar handler).
5. Nenhuma tool MCP (`ctx_execute`/`ctx_batch_execute`) ou agent existente tem seu comportamento de
   permissão alterado além do escopo descrito (validado pelos testes de caracterização dos 5
   consumidores da seção 3).

## 6. Gate de Aprovação (Challenge Gate + perguntas objetivas)

Ver `ask_questions` desta mesma mensagem — bloqueia o avanço para a Etapa 2 (Plano de
Implementação) até resposta do usuário.

## 7. Rollback Plan

- H1 (deploy): nenhuma alteração de código envolvida — rollback é apenas re-apontar para a imagem/
  processo anterior (`docker compose down` sem remover a imagem antiga, se preservada por tag; ou
  matar o processo `uvicorn` novo e religar o antigo). Risco de rollback: BAIXO.
- H2 (unwrap de shell wrapper), se aprovado para correção: alteração isolada em
  `comando_terminal_e_seguro` (novo passo de normalização ANTES da checagem `git `/utilitários),
  reversível via `git revert` do commit único; testes de caracterização dos 5 consumidores
  (seção 3) são o safety net que detecta regressão antes do merge. Risco de rollback: BAIXO (função
  pura, sem estado persistente, sem migração).
- Logging em arquivo: adição aditiva (`FileHandler` extra), reversível removendo o handler; risco de
  rollback: BAIXO. Atenção a side-effect: arquivo de log pode crescer sem rotação se
  `RotatingFileHandler` não for configurado corretamente (mitigar com limite de tamanho via critério
  de aceitação 4).

## 8. Próximo Agente (após aprovação do gate)

`<stack>-arch-advisor` correspondente à stack do gateway (Python/FastAPI) — provável
`python-arch-advisor` — autora o Plano de Implementação (`docs/implementation-plans/`) cobrindo os
dois fixes (permissão + logging) com o passo-a-passo Red/Green/Safety-Net detalhado.


## 9. Respostas do Gate de Aprovação (registradas via `ask_questions`)

- **Modo de execução confirmado:** `dev_watch.py` local (uvicorn `--reload`), NÃO Docker. Isso
  **descarta H1-Docker** (imagem congelada) e **reforça H1-dev_watch**: a hipótese de causa raiz
  passa a ser processo `uvicorn`/worker de reload **órfão/zumbi** ainda vinculado à porta `8080` no
  Windows (comum quando o terminal anterior é fechado sem `Ctrl+C` limpo, deixando o processo filho
  do `--reload` vivo e servindo o bytecode pré-fix), e não mais a necessidade de `--build`. Ação
  concreta a ser detalhada pelo `python-arch-advisor` na Etapa 2: validar porta `8080` livre
  (`netstat -ano | findstr :8080` / `Get-NetTCPConnection -LocalPort 8080` no PowerShell) ANTES de
  subir `dev_watch.py` novamente, e documentar esse passo de verificação no README do gateway para
  evitar recorrência.
- **Challenge Gate C1 (regra de negócio para H2):** aprovado manter o contrato idêntico de
  `comando_terminal_e_seguro(comando: str) -> bool` — qualquer correção de unwrap de wrapper de
  shell (`powershell -Command "..."`, `cmd /c ...`) deve ser uma normalização ADICIONAL do texto de
  entrada ANTES da checagem `git `/utilitários já existente (linhas 225-233), nunca uma mudança de
  assinatura ou duplicação de lógica — preserva os 5 consumidores mapeados na Seção 3 sem exigir
  alterações neles.
- **Challenge Gate C3 (casos de borda):** usuário não soube confirmar explicitamente — **ação
  obrigatória para a Etapa 2**: o `python-arch-advisor` deve levantar os casos de borda via leitura
  dos testes de caracterização EXISTENTES de `comando_terminal_e_seguro` (`test_permission_policy.py`
  linhas ~545-616) antes de propor a normalização de H2, garantindo que comando vazio, apenas
  espaços, e encadeamento (`&&`/`||`/`;`/`|`) dentro do wrapper continuem cobertos pela recursão já
  implementada (linhas 213-224) — não presumir, validar com teste novo explícito para o caso
  `"powershell -Command \"git status && git diff\""`.
- **Caminho de logging confirmado:** `deploy/local-chat-gateway/.tmp/gateway.log` — a Etapa 2 deve
  incluir: (a) criação do diretório `.tmp/` com `.gitkeep` ou criação lazy via código; (b) entrada
  `.tmp/` no `.gitignore` LOCAL do gateway (hoje vazio); (c) verificação/atualização do
  `Dockerfile.dockerignore` para excluir `.tmp/` do contexto de build da imagem Docker.
- **Gate final:** **APROVADO** — autorizado avanço para Etapa 2 (Plano de Implementação).

## 10. Handoff

Encaminhar para `python-arch-advisor` (stack Python/FastAPI do gateway) com este documento como
insumo completo para autoria do Plano de Implementação em
`docs/implementation-plans/20261004-bugfix-shell-permission-persistente-logging-arquivo.md`
(R-064 — o Orquestrador Raiz materializa o arquivo; `python-arch-advisor` é o autor do conteúdo).
