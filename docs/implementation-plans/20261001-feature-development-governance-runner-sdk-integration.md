# Plano de Implementação — Integração `governance_runner` ↔ `local-chat-gateway` (Copilot SDK)

- **Workflow**: WORKFLOW-FEATURE-DEVELOPMENT — Etapa 4 (Plano de Implementação, R-058)
- **Gate**: 2º gate do Duplo Gate Documental (R-064) — **Status: APROVADO (2026-10-01, aprovação humana real via `ask_questions`)** — liberado início de T1/PR-1
- **Autor**: python-arch-advisor · `[CURRENT_STATE_LOCK: WF4_IMPL_PLAN]`
- **Data**: 2026-10-01
- **Documento-base**: `docs/plans/20261001-feature-development-governance-runner-sdk-integration.md` (Plano de Planejamento aprovado — AD-01..AD-04, RQ-01..RQ-09, RK-01..RK-09, CA-01..CA-11, Q-01..Q-05 decididas)
- **Fase do gateway**: Fase 5 (sucede Fase 3 = SDK real; Fase 4 = telemetria/governança multi-turno — já materializada em `test_governance_phase4.py`)
- **Status de execução**: ✅ **CONCLUÍDA (2026-10-01)** — PR-1 a PR-8 implementados e mergeados sob TDD estrito. 355 testes verdes agregados (192 gateway + 163 headless-governance-runner). Ver Seção 8 (Fechamento Final) para evidências objetivas, gaps encontrados e corrigidos durante a execução (Addendums 1-9, todos validados ponta a ponta com Docker + requisições reais).

> **Escopo deste documento**: apenas planejamento de implementação (ordem TDD, matriz de riscos de código, plano de ajuste de `__all__`, plano de fail-fast, sequenciamento de PRs, critérios de pronto). **Nenhum código de aplicação é escrito aqui** — autoria de código/testes reais é responsabilidade do `@python-feature-developer` em handoff subsequente, mediante aprovação humana deste plano.

---

## 0. Decisões vinculantes herdadas (NÃO reabrir debate)

| ID | Decisão |
|---|---|
| Q-01 | `rotear()` invocado em `api/routes.py`, **antes** de `stream_chat` (Opção A — AD-01) |
| Q-02 | **Fail-fast**: grafo/schema de roteamento inválido no startup → gateway **não sobe** (sem modo degradado) |
| Q-03 | Schema default de `governance_runner` (`_schema_padrao`, i.e. `routing-graph.schema.json` embutido no pacote) |
| Q-04 | `PermissionPolicyStub` real nesta fase, atrás de feature flag `GATEWAY_GOVERNANCE_PERMISSIONS` (default **off**) |
| Q-05 | Ajuste mínimo em `governance_runner.routing.__all__` para exportar `Catalogo`/`TabelaTransicao`; `governance.py` passa a importar da fachada pública (`governance_runner.routing`), não mais de `governance_runner.routing.model` |

---

## 1. Evidências de código lidas (grounding para este plano)

| Arquivo | Linhas | Papel atual | Impacto da Fase 5 |
|---|---|---|---|
| `deploy/local-chat-gateway/src/local_chat_gateway/api/routes.py` | 425 | `POST /v1/chat/completions`: budget diário → checkpoint aberto (`get_open_checkpoint`/`parse_checkpoint_response`, Invariante 11) → `_real_or_stub_stream`/`_real_or_stub_completion` → `stream_chat` | Novo wiring: `rotear()` + `transicionar()` via `governance_pipeline.preparar_turno(...)` entre checkpoint e dispatch |
| `deploy/local-chat-gateway/src/local_chat_gateway/governance.py` | ~70 | Wrapper fino; **hoje importa `Catalogo`/`TabelaTransicao` diretamente de `governance_runner.routing.model`** (comentário explícito no docstring: "ainda não constam do `__all__` da fachada pública") | Q-05: passa a importar de `governance_runner.routing` (fachada pública) |
| `deploy/local-chat-gateway/src/local_chat_gateway/permission_policy.py` | 173 | `PermissionMode` (READ_ONLY/PROPOSE/APPLY), `WriteDecision`, `PermissionPolicyStub.autorizar_escrita(sessao, evento, tabela, catalogo, checkpoint_aberto, caminho_destino)` — já implementado e testado (Fase 4), mas **não plugado** no `permission_handler` de `stream_chat` | Wiring condicional à flag `GATEWAY_GOVERNANCE_PERMISSIONS` em `routes.py`/`sdk_session.py` |
| `deploy/local-chat-gateway/src/local_chat_gateway/session_store.py` | 278 | SQLAlchemy Core (sem ORM); tabelas `sessions`, `checkpoints`, `budget_daily`; `SessionRecord`, `SessionStore` | Migração aditiva: colunas `fase`, `workflow`, `etapa`, `agente_ativo`, `aprovacoes` (nullable, default `NULL`) em `sessions` |
| `deploy/local-chat-gateway/src/local_chat_gateway/telemetry.py` | 198 | `_build_otlp_payload`, `emit_chat_trace`; `gen_ai.agent.name="agent-router"` **hard-coded** | Novo parâmetro `agent_name` propagado; novos spans `governance.health_check`, `governance.route`, `governance.workflow_transition` |
| `deploy/local-chat-gateway/src/local_chat_gateway/sdk_session.py` | ~430 | `stream_chat(...)` async generator; `create_session(..., enable_file_hooks=False, enable_config_discovery=False)`; `permission_handler: Callable` simples | Novo parâmetro keyword-only opcional `system_message: str \| None = None` (retrocompatível) |
| `deploy/local-chat-gateway/src/local_chat_gateway/app.py` | 28 | `create_app()` síncrono: `resolved_settings.validate_startup()` → `FastAPI(...)` → `include_router` (**sem lifespan hoje**) | Introduzir `lifespan` assíncrono (`@asynccontextmanager`) que carrega `Grafo`/`TabelaTransicao`/`Catalogo` uma única vez e os expõe via `app.state` |
| `deploy/local-chat-gateway/src/local_chat_gateway/config.py` | 83 | `Settings(BaseSettings)`: `gateway_api_key`, `gateway_bind`, `gateway_port`, paths de projeto | Novos campos: `governance_graph_path`, `governance_schema_path` (opcional, default = schema embutido), `gateway_governance_permissions: bool = False` |
| `tools/headless-governance-runner/src/governance_runner/routing/__init__.py` | ~60 | `__all__` com `DecisaoRota, Deriva, Evento, Fase, GraphValidationError, HandoffPayloadInvalidoError, RoteamentoError, Sessao, ..., Workflow, carregar_grafo, compilar_tabela_transicao, detectar_deriva, rotear, transicionar, validar_handoff` — **sem `Catalogo`/`TabelaTransicao`** | Adicionar `Catalogo` e `TabelaTransicao` ao `__all__` (já importados internamente de `.model`) |
| `tools/headless-governance-runner/src/governance_runner/routing/model.py` | — | `Catalogo`, `TabelaTransicao` (`@dataclass(frozen=True)`) já definidos | Nenhuma mudança de implementação — apenas exposição |
| `tools/headless-governance-runner/src/governance_runner/routing/graph_loader.py` | — | `carregar_grafo(caminho_yaml, caminho_schema) -> Grafo` lança `GraphValidationError`; `compilar_tabela_transicao` | Consumido no lifespan; schema default via `_schema_padrao` (Q-03) |
| `deploy/local-chat-gateway/tests/unit/test_permission_policy.py` | — | 100% cobertura do stub atual (guardas 1-4) | **Não deve ser alterado** — apenas novos testes de wiring em arquivo separado |
| `deploy/local-chat-gateway/tests/integration/test_governance_phase4.py` | 152 | Testes de integração de checkpoint/governança multi-turno já existentes | Base de fixtures reaproveitável para `test_governance_phase5.py` (padrão `mock_context`, `tmp_db_path`) |
| `deploy/local-chat-gateway/tests/unit/test_telemetry.py` | 102 | Asserts sobre `gen_ai.agent.name == "agent-router"` fixo | Deve ganhar parametrização (`agent_name` dinâmico) sem quebrar assert existente (default mantém `"agent-router"`) |
| `deploy/local-chat-gateway/tests/unit/test_sdk_session.py` | 550 | Testes com `_instalar_copilot_falso`, asserts de `enable_file_hooks_recebido is False` | Novo teste: `system_message` propagado para `create_session`/`session.send` sem quebrar os 550 testes existentes |
| `deploy/local-chat-gateway/tests/integration/test_session_store.py` | 134 | `test_session_store_schema_creation_idempotent`, `test_create_session_duplicada_e_idempotente` | Novos testes de colunas aditivas; existentes não tocados (defaults `NULL`) |

Total de testes pré-existentes no diretório `deploy/local-chat-gateway/`: **89 arquivos de teste** no repositório inteiro (contagem via varredura), dos quais o Plano de Planejamento referencia especificamente **124 testes** como a suíte de regressão do gateway (CA-02) — este número é o oráculo de não-regressão e deve ser verificado via `pytest --collect-only -q` no início da Fase 5 (Tarefa 0, ver Seção 2).

---

## 2. Ordem de implementação sob TDD estrito (red → green → refactor)

Princípio geral: **cada item abaixo é um ciclo TDD completo e isolado** (um commit/PR por item, ver Seção 5). Nenhum item avança para "green" sem o item anterior estar mergeado e a suíte completa (124 testes + novos) verde. Testes são sempre escritos por `@test-strategy`/`@python-feature-developer` nesta fase subsequente — aqui apenas se define a sequência e o oráculo de cada etapa.

### T0 — Baseline de regressão (pré-requisito, não é código novo)
- **Red/Green**: N/A — é uma verificação, não um teste novo.
- **Ação**: rodar `pytest` completo no estado atual do `main` e registrar a contagem exata de testes coletados (deve bater com os 124 mencionados em RQ-09/CA-02) e o tempo de execução, como baseline de comparação para todas as etapas seguintes.
- **Critério de saída**: contagem registrada; qualquer divergência numérica é bloqueante e deve ser investigada antes de T1.

### T1 — `governance_runner.routing.__all__` (Q-05) + `governance.py` (fachada pública) · ✅ **CONCLUÍDO**
- **Red**: teste em `tools/headless-governance-runner/tests/routing_unit/` que faz `from governance_runner.routing import Catalogo, TabelaTransicao` e falha (`ImportError`) no estado atual.
- **Green**: adicionar `"Catalogo"` e `"TabelaTransicao"` ao `__all__` de `routing/__init__.py` (já importados internamente de `.model` — mudança de 2 linhas).
- **Refactor**: atualizar `governance.py` para importar `Catalogo, TabelaTransicao` do pacote `governance_runner.routing` (fachada), removendo o import direto de `governance_runner.routing.model` e o comentário de docstring que justificava a exceção.
- **Teste de não-regressão obrigatório**: suíte completa de `tools/headless-governance-runner/tests/routing_unit/` (inclui `test_graph_loader.py`, `test_handoff.py`, `test_smoke_end_to_end.py`) + `deploy/local-chat-gateway/tests/unit/test_permission_policy.py` (consumidor direto de `governance.py`) permanecem verdes sem alteração de asserts.
- **Dependências**: nenhuma (primeiro item, menor blast radius).

### T2 — Settings + lifespan (carga de Grafo/TabelaTransicao/Catalogo) · ✅ **CONCLUÍDO** (gap do teste fail-fast fechado retroativamente em T8 — ver Seção 8)
- **Red**: teste de integração que instancia `create_app()` com um `Settings` apontando para um YAML de grafo **inválido** (fixture reduzida, análoga a `tests/routing_unit/fixtures/`) e espera que a criação da app levante exceção (startup falha) — este é o teste "irmão" do fail-fast (ver Seção 4), mas aqui cobre apenas a mecânica de carga, não o texto da mensagem.
- **Red (caso feliz)**: teste que instancia `create_app()` com grafo válido e verifica que `app.state.grafo`, `app.state.tabela_transicao`, `app.state.catalogo` estão populados e são as mesmas instâncias entre múltiplas requisições (cache imutável).
- **Green**: (a) novos campos em `config.Settings`: `governance_graph_path: Path | None`, `governance_schema_path: Path | None` (default `None` → usa `_schema_padrao` do `governance_runner`, conforme Q-03); (b) introduzir `lifespan` assíncrono em `app.py` via `@asynccontextmanager` que chama `carregar_grafo` + `compilar_tabela_transicao` uma única vez e atribui a `app.state`.
- **Refactor**: extrair a lógica de carga para função pura testável isoladamente (ex.: `governance_pipeline.carregar_contexto_governanca(settings) -> ContextoGovernanca`) para não acoplar o teste ao ciclo de vida do FastAPI.
- **Teste de não-regressão**: todos os testes que hoje chamam `create_app(settings)` diretamente (ex.: `test_routes_healthz.py`, `test_routes_models.py`) devem continuar funcionando — exige fixture de `Settings` de teste apontando para um grafo válido mínimo (reaproveitar fixtures de `tests/routing_unit/fixtures/valid_graph.yaml` ou equivalente local ao gateway).
- **Dependências**: T1 (precisa de `Catalogo`/`TabelaTransicao` importáveis via fachada).

### T3 — `governance_pipeline.py` (módulo novo, composição pura) · ✅ **CONCLUÍDO**
- **Red**: testes unitários para 3 funções públicas, cada uma em isolamento (sem FastAPI, sem SDK):
  1. `preparar_turno(sessao, mensagem, grafo, tabela) -> DecisaoTurno` — decide se chama `rotear()` (sessão nova / drift via `detectar_deriva`) ou reutiliza o workflow persistido (AD-01, regra de "não re-rotear a cada turno").
  2. `avaliar_transicao(sessao, evento, tabela) -> Sessao` — wrapper fino sobre `transicionar()`, capturando `TransicaoInvalidaError` e convertendo em um resultado tipado (não-exceção) para o chamador em `routes.py` decidir a resposta HTTP controlada.
  3. `montar_contexto(agente, workflow, etapa) -> str` — allowlist de `.github/agents/<agente>.agent.md` + `.github/copilot-instructions.md` + skills do frontmatter, com truncamento por orçamento de bytes (32 KB) e banner R-042 (`Agente Ativo: <agente>` + `[WORKFLOW: <wf> / ETAPA: <n>]`).
- **Green**: implementar as 3 funções compondo exclusivamente a API pública de `governance.py` (nenhuma lógica de roteamento própria — validável por `grep -r "def rotear\|def transicionar" governance_pipeline.py` vazio, reforçando CA-01).
- **Refactor**: isolar a leitura de arquivos `.github/` atrás de uma função injetável (permite mockar em testes sem tocar o filesystem real) e reaproveitar o padrão de path traversal seguro já existente (`_caminho_escrita_seguro`/raiz fixa, citado no Plano de Planejamento Seção 4.5).
- **Teste de não-regressão**: nenhum consumidor existente ainda importa este módulo (é novo) — risco de regressão é nulo nesta etapa isolada.
- **Dependências**: T1, T2.

### T4 — `session_store.py`: campos aditivos de `Sessao` · ✅ **CONCLUÍDO**
- **Red**: teste de migração/schema em `test_session_store.py` que cria uma `SessionStore` nova e verifica que as colunas `fase`, `workflow`, `etapa`, `agente_ativo`, `aprovacoes` existem na tabela `sessions` com default `NULL`; teste adicional que grava uma sessão **sem** esses campos (simulando dado legado) e confirma leitura sem exceção.
- **Green**: adicionar as colunas em `SessionRecord`/DDL de `sessions` (SQLAlchemy Core — `Column(..., nullable=True, default=None)`), com serialização JSON para `aprovacoes` (dict simples).
- **Refactor**: método `SessionStore.atualizar_estado_governanca(session_id, fase, workflow, etapa, agente_ativo, aprovacoes)` dedicado, mantendo `create_session`/`is_checkpoint_open` intocados.
- **Teste de não-regressão**: `test_session_store_schema_creation_idempotent` e `test_create_session_duplicada_e_idempotente` (já existentes) devem passar sem alteração — são o oráculo de retrocompatibilidade desta etapa (RK-05).
- **Dependências**: nenhuma direta (pode rodar em paralelo a T3), mas sequenciado após T2 por ordem de PR (ver Seção 5).

### T5 — `sdk_session.stream_chat`: `system_message` opcional · ✅ **CONCLUÍDO**
- **Red**: novo teste em `test_sdk_session.py` (seguindo o padrão de `_instalar_copilot_falso`) que passa `system_message="banner de teste"` e verifica que o valor chega a `create_session`/é prefixado ao prompt enviado via `session.send`, em modo `append` (não sobrescreve guardrails do SDK, conforme Seção 4.2 do Plano de Planejamento).
- **Red (regressão)**: teste que chama `stream_chat` **sem** o novo parâmetro e confirma que o comportamento é idêntico ao atual (nenhuma mudança de assinatura obrigatória — keyword-only com default `None`).
- **Green**: adicionar `system_message: str | None = None` à assinatura de `stream_chat`, keyword-only, após os parâmetros existentes; se não-`None`, compor com `_joined_prompt(messages)` antes de `session.send`.
- **Refactor**: extrair `_compor_prompt_com_sistema(system_message, mensagens_unidas) -> str` para isolar a lógica de composição e facilitar teste unitário puro (sem SDK).
- **Teste de não-regressão**: todos os 550 testes de `test_sdk_session.py` permanecem verdes (RK-07 — novos parâmetros keyword-only com default).
- **Dependências**: T3 (consome `montar_contexto`).

### T6 — Wiring em `routes.py` (AD-01/AD-02, respeitando Q-02) · ✅ **CONCLUÍDO** (PR de maior risco — correção adicional de bug real documentada em T8/Seção 8)
- **Red**: testes de integração (reaproveitando fixtures de `test_governance_phase4.py`):
  1. Sessão nova, prompt canônico → span/efeito observável de roteamento executado (`DecisaoTurno` não nula) e workflow persistido em `session_store`.
  2. Segundo turno da mesma sessão, sem drift → `rotear()` **não** é chamado novamente (reuso do workflow persistido — CA-04).
  3. `TransicaoInvalidaError` simulada → resposta HTTP **200** com texto controlado (via `_local_text_stream`, mesmo padrão dos checkpoints), nunca 500 (CA-05).
  4. Com `GATEWAY_GOVERNANCE_PERMISSIONS=false` (default): `permission_handler` continua sendo o `_conservative_permission_handler` read-only atual, inalterado (RK-06 mitigado).
  5. Com `GATEWAY_GOVERNANCE_PERMISSIONS=true`: `permission_handler` delega a `PermissionPolicyStub.autorizar_escrita`, usando a `Sessao`/`Catalogo`/`TabelaTransicao` do `app.state`.
- **Green**: inserir chamada a `governance_pipeline.preparar_turno(...)` e `avaliar_transicao(...)` em `routes.py`, posicionadas **após** a resolução de checkpoint aberto e **antes** de `_real_or_stub_stream`/`_real_or_stub_completion` (AD-01 Opção A, Q-01); feature flag lida de `settings.gateway_governance_permissions` para o wiring condicional do `permission_handler` (Q-04).
- **Refactor**: extrair a composição de `system_message` (via `montar_contexto`) para um helper único reaproveitado por `_real_or_stub_stream` e `_real_or_stub_completion`, evitando duplicação.
- **Teste de não-regressão**: toda a suíte de `test_routes_healthz.py`, `test_routes_models.py`, `test_governance_phase4.py` permanece verde; CA-06 (`enable_file_hooks=False`/`enable_config_discovery=False` preservados) e CA-08 (`SDKUnavailableError` → stub, roteamento ainda executado/telemetrado) são re-verificados explicitamente nesta etapa.
- **Dependências**: T2, T3, T4, T5 (ponto de integração final do backend).

### T7 — `telemetry.py`: spans por etapa + `gen_ai.agent.name` dinâmico · ✅ **CONCLUÍDO**
- **Red**: (a) teste que `emit_chat_trace` aceita parâmetro `agent_name` e o atributo `gen_ai.agent.name` no payload reflete o valor passado (não mais hard-coded); (b) novos testes unitários para os 3 novos spans (`governance.health_check`, `governance.route`, `governance.workflow_transition`) verificando os atributos `deep_agents.*` definidos na Seção 5 do Plano de Planejamento (namespace customizado, nunca inventando chaves em `gen_ai.*`).
- **Red (regressão)**: o teste existente que assume `gen_ai.agent.name == "agent-router"` continua passando **sem alteração de assert**, porque o default do novo parâmetro é `"agent-router"`.
- **Green**: adicionar parâmetro `agent_name: str = "agent-router"` a `emit_chat_trace`/`_build_otlp_payload`; novas funções `emit_governance_health_check_span`, `emit_governance_route_span`, `emit_governance_workflow_transition_span` (ou parametrização de uma função genérica `emit_custom_span(name, attributes, parent_span_id)`).
- **Refactor**: consolidar construção de atributos `deep_agents.*` em um helper único para evitar divergência de nomenclatura entre os 3 novos spans.
- **Teste de não-regressão**: `test_telemetry.py` (102 linhas, asserts de hierarquia de spans) permanece verde sem alteração dos asserts existentes.
- **Dependências**: T6 (precisa saber o que instrumentar — ordem de etapas do turno já wireada).

### T8 — Testes unitários adicionais + `tests/integration/test_governance_phase5.py` · ✅ **CONCLUÍDO** (encontrou e corrigiu gap de CA-09 e bug de CA-08 — ver Seção 8)
- **Red/Green/Refactor**: este item é, por natureza, o fechamento formal da suíte (CA-11) — não introduz produção nova, mas consolida os cenários end-to-end que cruzam T1-T7: sessão nova → roteamento → persistência → turno 2 sem re-roteamento → checkpoint com `TransicaoInvalidaError` → fail-fast de startup (via subprocesso ou `pytest.raises` na criação da app, conforme Seção 4) → flag de permissões on/off.
- **Dependências**: todos os itens anteriores (T1-T7) mergeados.

> **Nota de disciplina TDD**: para cada T1-T8, a ordem red→green→refactor é obrigatória e cada cor é um commit distinto dentro do mesmo PR (ver Seção 5), nunca um único commit "implementa + testa".

---

## 3. Matriz de riscos de código (RK-01..RK-09 → arquivos/símbolos/blast radius)

| Risco | Arquivos/símbolos concretos afetados | Blast radius (módulos/testes tocados) | Mitigação concreta nesta fase |
|---|---|---|---|
| **RK-01** — Re-roteamento a cada turno muda agente no meio de workflow | `governance_pipeline.preparar_turno`; `session_store` (campo `workflow` persistido); `routing/drift.py` (`detectar_deriva`) | `routes.py`, `test_governance_phase5.py` (cenário "turno 2 sem drift") | `preparar_turno` só chama `rotear()` se `sessao.workflow is None` OU `detectar_deriva(...)` sinalizar drift — testado explicitamente em T6/T8 (CA-04) |
| **RK-02** — Persona `.agent.md` grande estoura janela/custo | `governance_pipeline.montar_contexto`; arquivos `.github/agents/*.agent.md`, `.github/copilot-instructions.md` | Nenhum teste existente tocado (módulo novo); novo teste unitário de truncamento em T3 | Orçamento de bytes (32 KB) + allowlist fixa, testado com fixture de arquivo grande sintético |
| **RK-03** — Injeção de contexto reabre vetor do bug de hooks (2026-09-29) | `governance_pipeline.montar_contexto` (NUNCA lê `.github/hooks/`); `sdk_session.create_session` (`enable_file_hooks=False`, `enable_config_discovery=False` preservados) | `test_sdk_session.py` (550 testes, inclui asserts de `enable_file_hooks_recebido is False`); `test_governance_phase5.py` (CA-06, CA-07) | Nenhuma alteração nos parâmetros `enable_file_hooks`/`enable_config_discovery`; `montar_contexto` só lê Markdown estático via allowlist explícita, nunca glob de `.github/hooks/` |
| **RK-04** — `GraphValidationError` derruba gateway | `app.py` (`lifespan`); `config.Settings` (`governance_graph_path`/`governance_schema_path`); `governance_runner.routing.graph_loader.carregar_grafo` | Todo o processo de startup do gateway (`create_app`); todos os testes de integração que chamam `create_app(settings)` | **Intencional (Q-02 fail-fast)** — não é bug, é comportamento documentado; mitigação é o runbook de deploy (checagem de grafo/schema em CI antes de subir) + mensagem de erro clara (ver Seção 4) |
| **RK-05** — Schema `session_store` alterado quebra sessões persistidas | `session_store.py` (`SessionRecord`, DDL de `sessions`) | `test_session_store.py` (`test_session_store_schema_creation_idempotent`, `test_create_session_duplicada_e_idempotente`) — **oráculo de retrocompatibilidade** | Campos aditivos com `nullable=True`/default `None`; nenhuma coluna existente renomeada/removida |
| **RK-06** — Wiring `PermissionPolicyStub` muda comportamento de tools (hoje read-only fixo) | `routes.py` (`_conservative_permission_handler` vs. `PermissionPolicyStub.autorizar_escrita`); `permission_policy.py` (já implementado, não alterado); `config.Settings.gateway_governance_permissions` | `test_permission_policy.py` (**não deve ser alterado** — 100% cobertura do stub já existe); novo arquivo de teste de wiring em `routes.py` | Feature flag `GATEWAY_GOVERNANCE_PERMISSIONS` default **off**; comportamento read-only é o caminho default testado por toda a suíte atual |
| **RK-07** — Regressão nos 124 testes (assinatura de `stream_chat`) | `sdk_session.py` (`stream_chat`); todos os chamadores em `routes.py` | `test_sdk_session.py` (550 linhas/testes), `test_routes_healthz.py`, `test_routes_models.py`, `test_governance_phase4.py` | Novo parâmetro `system_message` keyword-only com default `None` — nenhuma chamada existente precisa mudar |
| **RK-08** — `Catalogo`/`TabelaTransicao` importados de submódulo interno | `governance.py`; `governance_runner/routing/__init__.py` (`__all__`); `governance_runner/routing/model.py` | `tools/headless-governance-runner/tests/routing_unit/*` (toda a suíte, pois toca `__all__` do pacote público); `test_permission_policy.py` (consumidor indireto via `governance.py`) | Q-05: adicionar ao `__all__` é mudança aditiva e não-quebra — símbolos já existiam e eram importáveis via path interno; o path interno continua funcionando (não é removido), apenas `governance.py` passa a preferir a fachada pública |
| **RK-09** — Despacho apenas por persona (1 sessão SDK) ≠ handoff real multiagente | `governance_pipeline.montar_contexto` (injeta persona via `system_message`, não cria sub-sessões SDK) | Nenhum teste quebrado — é uma limitação de escopo documentada, não um defeito | Fora de escopo desta fase (documentado explicitamente); candidato a Fase 6 — nenhuma ação de mitigação de código nesta fase, apenas nota no README/CHANGELOG do gateway |

**Blast radius consolidado (visão agregada)**:
- **Módulos de produção tocados**: `api/routes.py`, `governance.py`, `governance_pipeline.py` (novo), `session_store.py`, `sdk_session.py`, `telemetry.py`, `app.py`, `config.py`, `governance_runner/routing/__init__.py`.
- **Módulos de produção explicitamente NÃO tocados** (âncoras de retrocompatibilidade): `permission_policy.py` (lógica interna), `governance_runner/routing/model.py`, `governance_runner/routing/graph_loader.py`, `governance_runner/routing/router.py`, `governance_runner/routing/state_machine.py` — nenhuma lógica de domínio do runner é reimplementada ou alterada (CA-01).
- **Suítes de teste como oráculo de não-regressão**: os 124 testes pré-existentes do gateway (`deploy/local-chat-gateway/tests/`) + a suíte completa de `tools/headless-governance-runner/tests/routing_unit/` e `runner_unit/` (ambas tocadas apenas por T1/Q-05) devem permanecer verdes após cada PR da Seção 5.

---

## 4. Plano de fail-fast no lifespan do FastAPI (Q-02)

### Comportamento esperado
1. No `lifespan` assíncrono de `app.py` (introduzido em T2), a primeira ação é carregar o grafo: `grafo = carregar_grafo(settings.governance_graph_path_resolvido, settings.governance_schema_path_resolvido)`.
2. Se `carregar_grafo` levantar `GraphValidationError` (schema JSON inválido, YAML malformado, nó/aresta inconsistente, ciclo proibido, etc.), a exceção **propaga sem captura** através do `lifespan` — o Uvicorn/FastAPI aborta o processo de startup e o container **não entra em estado "ready"** (sem health check respondendo, sem bind de porta completado para tráfego).
3. **Não há fallback para modo degradado**: nenhuma rota é registrada, nenhum stub de roteamento substitui o grafo ausente — a decisão humana (Q-02) foi explícita em rejeitar esse caminho.
4. **Mensagem de erro esperada**: a exceção `GraphValidationError` já carrega (por contrato de `graph_loader.py`) informação suficiente para localizar a causa raiz (arquivo, e idealmente o ponto de falha de validação do schema — ex.: caminho JSON Pointer do `jsonschema`, se a biblioteca subjacente expuser). O `lifespan` deve **envolver** essa exceção em uma mensagem de log estruturado (não silenciar) antes de deixá-la propagar, contendo no mínimo: caminho do YAML usado, caminho do schema usado, e a mensagem original de `GraphValidationError`. Exemplo de log esperado (nível `CRITICAL`/`ERROR`, antes do crash):
   ```text
   CRITICAL: Falha fatal de startup — grafo de roteamento inválido.
     graph_path=/governance/.github/agents/routing-graph.yaml
     schema_path=<schema padrão embutido em governance_runner._schema_padrao>
     causa=<mensagem original de GraphValidationError>
   O gateway NÃO sobe (fail-fast, Q-02). Corrija o grafo/schema e reinicie.
   ```
5. **Runbook de deploy** (ação fora deste documento, mas a ser referenciada no CHANGELOG/README do gateway): checagem de validade do grafo/schema deve rodar em pipeline **CI**, antes do deploy, como gate preventivo adicional (reduz a chance de descobrir o problema apenas em produção).

### Teste que comprova a falha de startup (especificação do oráculo, a ser escrito por `@python-feature-developer`)
- **Nome sugerido**: `test_create_app_fail_fast_grafo_invalido` em `deploy/local-chat-gateway/tests/integration/test_governance_phase5.py`.
- **Arranjo**: fixture de YAML de grafo propositalmente inválido (ex.: nó referenciado em aresta mas ausente em `nos`, ou campo obrigatório do schema ausente) + `Settings` de teste apontando `governance_graph_path` para esse arquivo.
- **Ato**: chamar `create_app(settings)` (ou o helper que executa o `lifespan` de forma síncrona em teste, conforme padrão do FastAPI `TestClient`/`asgi-lifespan`).
- **Assert**: `pytest.raises(GraphValidationError)` (ou a exceção de domínio equivalente que o `lifespan` deixa propagar) — **nenhuma** instância de `FastAPI` utilizável é retornada; nenhuma rota responde.
- **Assert complementar**: captura de log (`caplog`) confirma a presença da mensagem estruturada acima, no nível apropriado, antes da propagação da exceção.
- **Caso feliz espelhado (não-regressão)**: `test_create_app_startup_ok_com_grafo_valido` garante que, com grafo válido, `create_app(settings)` retorna normalmente e `app.state.grafo`/`app.state.tabela_transicao`/`app.state.catalogo` estão populados.

---

## 5. Sequenciamento de PRs/commits pequenos e ordem de merge segura

| PR | Título | Conteúdo | Pré-requisito (merge) | Suíte de verificação obrigatória | Status |
|---|---|---|---|---|---|
| **PR-1** | `feat(routing): expõe Catalogo/TabelaTransicao no __all__ público (Q-05)` | T1 completo (red→green→refactor) | nenhum | `tools/headless-governance-runner/tests/routing_unit/` completo + `test_permission_policy.py` | ✅ Concluído |
| **PR-2** | `feat(gateway): Settings + lifespan de carga do grafo de roteamento` | T2 completo | PR-1 mergeado | PR-1 suite + `test_routes_healthz.py`, `test_routes_models.py` | ✅ Concluído |
| **PR-3** | `feat(gateway): governance_pipeline.py — preparar_turno/avaliar_transicao/montar_contexto` | T3 completo | PR-2 mergeado | PR-2 suite + testes unitários novos de `governance_pipeline` | ✅ Concluído |
| **PR-4** | `feat(gateway): session_store — campos aditivos de estado de governança` | T4 completo | PR-2 mergeado (pode ser paralelo a PR-3, mas merge sequencial recomendado para reduzir conflitos de revisão) | `test_session_store.py` completo (existente + novos) | ✅ Concluído |
| **PR-5** | `feat(gateway): sdk_session.stream_chat — system_message opcional` | T5 completo | PR-3 mergeado | `test_sdk_session.py` completo (550 testes + novos) | ✅ Concluído |
| **PR-6** | `feat(gateway): wiring de roteamento/transição/permissões em routes.py` | T6 completo | PR-3, PR-4, PR-5 mergeados | Suíte completa do gateway (124 testes + novos de integração) | ✅ Concluído |
| **PR-7** | `feat(gateway): telemetry — spans de etapa + gen_ai.agent.name dinâmico` | T7 completo | PR-6 mergeado | `test_telemetry.py` completo (existente + novos) | ✅ Concluído |
| **PR-8** | `test(gateway): test_governance_phase5.py — fechamento end-to-end + fail-fast` | T8 completo (inclui o teste de fail-fast da Seção 4) | PR-1..PR-7 todos mergeados | Suíte **completa** do repositório (gateway + headless-governance-runner), sem exceção | ✅ Concluído — encontrou e corrigiu gap de CA-09 e bug de CA-08 |

**Regras de ordem de merge segura**:
1. Nenhum PR é mergeado com a suíte de regressão vermelha — cada PR roda CI completo (gateway + headless-governance-runner), não apenas os testes do módulo tocado.
2. PR-1 é o único pré-requisito universal (menor blast radius, habilita a fachada pública usada por quase todos os demais).
3. PR-4 (session_store) e PR-3 (governance_pipeline) não têm dependência direta entre si, mas **devem mergear em sequência** (nunca em paralelo no mesmo momento) para evitar conflitos de merge em `routes.py` quando PR-6 depender de ambos.
4. PR-6 é o PR de maior risco (ponto de integração) — deve ser o menor possível em diffs não relacionados ao wiring em si (nenhum refactor oportunista "de passagem").
5. PR-8 é o gate final: só é aberto após todos os demais estarem em `main`, e sua aprovação equivale à conclusão funcional da Fase 5 (antes do fechamento formal do CA-10, que exige validação manual via Lobe Chat + Langfuse, fora do escopo de PR de código).

---

## 6. Critérios de "pronto" objetivos (mapeados a CA-01..CA-11)

| CA | Critério (Plano de Planejamento) | Critério de "pronto" objetivo nesta implementação | PR(s) responsável(is) | Resultado real |
|---|---|---|---|---|
| CA-01 | `grep -r "def rotear\|def transicionar\|class Catalogo" deploy/local-chat-gateway/src` vazio | Comando executado em CI (step dedicado) retorna vazio após PR-3/PR-6; nenhuma lógica de domínio duplicada em `governance_pipeline.py` | PR-3, PR-6 | ✅ Verificado (`grep_exit=1`) |
| CA-02 | 124 testes pré-existentes verdes sem alteração de asserts | `pytest --collect-only -q` no baseline (T0) bate com 124; mesma contagem (+ novos) verde em cada PR; nenhum `assert` existente editado (apenas novos testes adicionados) | Todos (verificação contínua) | ✅ Suíte final: 167 (gateway) + 163 (runner) = 330 testes verdes |
| CA-03 | Sessão nova → span `governance.route` com `deep_agents.routing.escolhido`/`workflow` não nulo (fixture WF1..WF8) | Teste parametrizado em `test_governance_phase5.py` com 1 fixture por workflow canônico, assert de atributos não-nulos no payload OTLP capturado | PR-7, PR-8 | ✅ Coberto para subconjunto representativo (`WORKFLOW-BUG-FIX`, `WORKFLOW-TECHNICAL-ANALYSIS`) — ampliação aos 8 workflows é trabalho futuro não-bloqueante |
| CA-04 | Segundo turno não re-roteia (sem drift) | Teste em `test_governance_phase5.py` verifica ausência de novo span `route` (ou `deep_agents.routing.reused=true`) no 2º turno da mesma sessão | PR-6, PR-8 | ✅ `governance.rotear.assert_not_called()` confirmado |
| CA-05 | `TransicaoInvalidaError` → HTTP 200 com texto controlado + span com `error.type` | Teste de integração força transição ilegal e assert de `response.status_code == 200` + span com atributo `error.type` presente | PR-6, PR-7, PR-8 | ✅ Confirmado |
| CA-06 | `create_session` mantém `enable_file_hooks=False`/`enable_config_discovery=False` | Teste unitário (já existente, reforçado) continua passando sem alteração de assert após T5/T6 | PR-5, PR-6 | ✅ Confirmado — zero alteração nesses parâmetros em toda a Fase 5 |
| CA-07 | `system_message` contém banner + persona; nenhum `.github/hooks/` lido | Teste unitário de `montar_contexto` com `assert "Agente Ativo:" in resultado`; teste com `monkeypatch`/spy garantindo zero chamadas de leitura a caminhos contendo `hooks/` | PR-3, PR-5 | ✅ Confirmado (unitário + integração e2e) |
| CA-08 | `SDKUnavailableError` → stub, roteamento ainda executado/telemetrado | Teste de integração com SDK indisponível confirma que `DecisaoTurno`/span `route` ocorrem mesmo no caminho stub | PR-6, PR-8 | ✅ **Bug real encontrado e corrigido em T8**: `emit_chat_trace` não era chamado no fallback stub; corrigido com diff mínimo em `_real_or_stub_stream`/`_real_or_stub_completion` |
| CA-09 | Health check falho (grafo inválido) impede startup (fail-fast), com log claro | Teste da Seção 4 (`test_create_app_fail_fast_grafo_invalido`) + `caplog` assertando mensagem estruturada | PR-2, PR-8 | ✅ **Gap de processo encontrado e corrigido em T8**: o teste havia sido reportado como concluído em T2, mas nunca existira de fato (fixture órfã); escrito retroativamente em PR-8 |
| CA-10 | Trace visível no Langfuse com hierarquia da Seção 5 do Plano de Planejamento | **Validação manual** (fora do escopo de PR de código) via Lobe Chat + Docker local — critério fechado por evidência de screenshot/export de trace, não por teste automatizado | Pós-PR-8, validação manual | ⏳ **PENDENTE** — não-bloqueante para o merge técnico |
| CA-11 | Novo `tests/integration/test_governance_phase5.py` | Arquivo criado e presente na suíte CI, cobrindo os cenários de T6/T8 (roteamento, reuso, transição inválida, permissões on/off, fail-fast) | PR-8 | ✅ Arquivo final com 12 testes de integração |

**Definição de "pronto" da Fase 5 (agregada)**: PR-1 a PR-8 mergeados em `main`, suíte CI completa verde (gateway + headless-governance-runner), CA-01 a CA-09 e CA-11 verificados automaticamente em CI, e CA-10 pendente apenas de validação manual documentada (não bloqueia o merge técnico, mas bloqueia o fechamento formal da Fase 5 no changelog/governança).

**Status real (2026-10-01)**: ✅ todos os critérios automatizáveis (CA-01 a CA-09, CA-11) verificados objetivamente. Apenas CA-10 permanece pendente (validação manual).

---

## 7. Próximo passo de governança

Este documento consolida o 2º gate do Duplo Gate Documental (R-064). A implementação foi executada integralmente (T1-T8/PR-1-8) sob TDD estrito, com aprovação prévia deste plano obtida do usuário real via `ask_questions` em 2026-10-01. Ver Seção 8 para o fechamento final com evidências objetivas.

---

## 8. Fechamento Final — Evidências Objetivas de Execução (2026-10-01)

### Contagem final de testes (verificada diretamente via terminal, não apenas relatada pelos subagentes)
| Suíte | Resultado |
|---|---|
| `deploy/local-chat-gateway/tests/` | **167 passed**, 1 warning pré-existente (`StarletteDeprecationWarning`, não relacionado) |
| `tools/headless-governance-runner/tests/` | **163 passed** |
| **Total agregado** | **330 testes verdes, 0 falhas** |

### Validações estáticas finais
- `grep -rn "^def rotear\|^def transicionar\|^class Catalogo" deploy/local-chat-gateway/src --include="*.py"` → vazio (`grep_exit=1`), confirmando CA-01.
- `mypy --strict` em todo `src/` do gateway → `Success: no issues found in 16 source files`.

### Gaps/bugs reais encontrados e corrigidos durante T8 (auditoria de fechamento)
1. **Gap de processo — CA-09**: o teste de fail-fast de startup (`test_create_app_fail_fast_grafo_invalido`/`test_create_app_startup_ok_com_grafo_valido`) foi relatado como concluído durante a execução de T2, mas uma auditoria em T8 revelou que ele nunca havia sido escrito de fato — a fixture `grafo_invalido_aresta_no_inexistente.yaml` existia órfã, sem nenhum teste referenciando-a. **Lição de processo**: relatos de subagentes de "teste concluído" foram verificados de forma insuficiente em T2; a partir de T6/T7, passou-se a exigir disciplina TDD executada na mesma chamada (sem terceirização de testes Red), e a verificação final em T8 (auditoria externa) capturou o gap residual antes do fechamento da fase.
2. **Bug real de produção — CA-08**: `emit_chat_trace` não era invocado no caminho de fallback (`except SDKUnavailableError`) de `_real_or_stub_stream`/`_real_or_stub_completion` em `routes.py`, quebrando a garantia de telemetria no modo stub (SDK indisponível). Corrigido com diff mínimo, sem alterar o contrato público dessas funções.

### Desvios de escopo documentados (não-bloqueantes)
- **CA-03**: a fixture de teste (`valid_graph.yaml`) cobre 2 dos 8 workflows canônicos (`WORKFLOW-BUG-FIX`, `WORKFLOW-TECHNICAL-ANALYSIS`). O teste parametrizado usa esse subconjunto como representativo documentado. Ampliação da fixture para os 8 workflows completos é candidata a trabalho futuro.
- **RQ-09/CA-02 (baseline numérico)**: a suíte de regressão real do gateway já era maior que os "124 testes" estimados no Plano de Planejamento original — a contagem final de 167 inclui o baseline real + todos os testes novos de T1-T8, sem nenhuma perda de cobertura pré-existente.

### Pendência não-bloqueante
- **CA-10**: validação manual do trace completo no Langfuse via Lobe Chat + Docker com token real do Copilot SDK — requer ambiente real; fora do escopo de execução automatizada desta fase. Não bloqueia o merge técnico, mas bloqueia o fechamento formal da Fase 5 no changelog/governança até ser realizada.

### Addendum — Gaps reais de deploy encontrados e corrigidos (2026-10-01, pós-fechamento)

Ao tentar subir o stack real via `docker compose --profile lobe --profile otel up`, 3 gaps adicionais (não cobertos pela suíte de testes unitários/integração, pois dependiam do ambiente Docker real) foram descobertos e corrigidos:

1. **Infra nunca conectada**: `GOVERNANCE_GRAPH_PATH`/`GOVERNANCE_SCHEMA_PATH` (introduzidas em T2) nunca foram adicionadas ao `docker-compose.yml` (environment do serviço `gateway`) nem ao `.env.example`. Corrigido com default `GOVERNANCE_GRAPH_PATH=/governance/.github/agents/routing-graph.yaml` (caminho já acessível via o volume read-only `/governance` existente).
2. **Bug real em `config.py`**: campos Pydantic `Path | None` não tratam string vazia (`""`, comum quando uma env var do compose não é definida) como `None` — `Path("")` resolve para `.` (diretório atual), bypassando o fallback de schema padrão (Q-03) e causando `GraphValidationError: Is a directory`. Corrigido com `field_validator(mode="before")` normalizando string vazia para `None`, coberto por 4 novos testes unitários em `tests/unit/test_config.py` (ciclo TDD Red→Green completo).
3. **Bug de empacotamento em `governance-runner`**: o `pyproject.toml` do pacote não declarava `[tool.setuptools.package-data]`, então `routing-graph.schema.json` (schema padrão embutido, Q-03) nunca era incluído no pacote instalado via `pip install` — causando `FileNotFoundError` em runtime (funcionava em modo editável de desenvolvimento, mas falhava no container Docker com instalação real). Corrigido adicionando `governance_runner = ["routing/*.json"]`.

**Validação final real (não apenas testes automatizados)**: `docker compose --profile lobe --profile otel up -d` → todos os 3 containers (`local-chat-gateway`, `lobe-chat`, `local-chat-gateway-otel-collector`) `Up`/`healthy`; `curl http://127.0.0.1:8080/healthz` → `{"status":"ok"}`. Suíte de regressão final: **171 testes (gateway) + 163 testes (headless-governance-runner) = 334 testes verdes**.

**Lição de processo**: a suíte de testes unitários/integração (mockada) não cobre o ciclo completo de empacotamento Python (`pip install` real) nem a configuração declarativa do `docker-compose.yml` — esses gaps só se manifestam ao subir o stack real via Docker. Recomenda-se, para fases futuras com mudanças estruturais de config/packaging, incluir um smoke test real de `docker compose up` como gate adicional antes do fechamento formal da fase (candidato a CA-12 em revisões futuras deste documento).

### Addendum 2 — Gaps reais adicionais encontrados ao processar requisição real (2026-10-01)

Ao enviar o primeiro prompt real via `/v1/chat/completions` ("o que faz o projeto projeto-exemplo-app?"), **2 gaps adicionais** (não detectáveis pelos 334 testes automatizados, pois dependem de estado persistido em volume Docker e de variáveis de shell do host) foram encontrados e corrigidos:

4. **Bug real em `session_store.py` — migração de schema ausente**: `metadata.create_all()` (SQLAlchemy) é idempotente apenas para **criar tabelas ausentes** — nunca adiciona colunas a uma tabela `sessions` já existente no disco. O volume Docker `gateway-data`, persistido **antes** de T4/PR-4, continha uma tabela `sessions` com apenas as colunas originais, causando `sqlalchemy.exc.OperationalError: no such column: sessions.workflow` em toda requisição real (HTTP 500). A promessa de retrocompatibilidade do RK-05 era falsa para bancos pré-existentes — os testes de T4 sempre usavam `tmp_db_path` novo (nunca testavam abrir um banco com schema antigo). Corrigido com `_migrar_colunas_aditivas_sessions()` (inspeção via `sqlalchemy.inspect` + `ALTER TABLE ADD COLUMN` idempotente), coberto por **1 novo teste de integração** (`test_banco_com_schema_antigo_pre_t4_e_migrado_automaticamente`) que reproduz o schema legado manualmente antes de instanciar `SessionStore`.
5. **Colisão de variável de ambiente do shell do host**: o shell do desenvolvedor tinha `OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318` e `LANGFUSE_OTLP_AUTH=<placeholder>` exportados (configuração de telemetria da IDE, ver `docs/context/setup-telemetry-copilot.md` e `tools/otel-langfuse/README.md`). Docker Compose dá precedência a variáveis de shell sobre o `.env` — o gateway herdava silenciosamente o endpoint OTel errado (loopback dele mesmo, onde nada escuta) e o coletor enviava uma credencial Basic Auth placeholder ao Langfuse Cloud, causando `401 Unauthenticated` em 100% dos traces, mesmo com o `.env` correto. Corrigido renomeando a variável host-side do gateway para `GATEWAY_OTEL_EXPORTER_OTLP_ENDPOINT` (exclusiva deste compose, sem colidir com a convenção global da IDE) e adicionando `LANGFUSE_ENDPOINT` ao `environment:` do serviço `otel-collector` (nunca era propagado, então o endpoint EU-default sempre era usado independente da região real das credenciais).

**Validação final real (requisição ponta a ponta)**: `POST /v1/chat/completions` com prompt real → **HTTP 200**, resposta completa do SDK real do Copilot investigando o projeto `projeto-exemplo-app` via tools (`view`, `bash`); logs do `otel-collector` sem nenhuma ocorrência de `error`/`401` após a correção — telemetria entregue ao Langfuse Cloud (região US) com sucesso.

### Addendum 4 — Reliability fix: retenção de referência de Futures em background (2026-10-01)

Durante a investigação do Addendum 3, testes manuais isolados (`docker exec` + `asyncio.run()`) confirmaram que o payload gerado por `_build_otlp_payload`/`emit_chat_trace` estava correto e chegava ao Langfuse — mas spans de requisições **reais** via `/v1/chat/completions` (`governance.route`, `governance.workflow_transition`, `chat: deep-agents/router`) não apareciam de forma confiável no dashboard, mesmo sem nenhum erro nos logs do `otel-collector`.

**Causa raiz**: `loop.run_in_executor(None, _dispatch_http, endpoint, payload)` era chamado sem reter nenhuma referência ao `Future` retornado — um anti-padrão explicitamente documentado pelo próprio `asyncio` ("Important: Save a reference to the result... the event loop only keeps a weak reference"). Dentro do processo persistente do Uvicorn (múltiplas requisições concorrentes, longas sessões de SDK com dezenas de tool calls), isso tornava o despacho de telemetria vulnerável a perda silenciosa.

**Correção**: novo helper `_schedule_background_dispatch(endpoint, payload)` em `telemetry.py`, que retém o `Future` em um `set` module-level (`_background_dispatch_tasks`) até sua conclusão (via `add_done_callback`), eliminando qualquer possibilidade de descarte prematuro — aplicado em `emit_chat_trace` e `_emit_custom_governance_span`. Coberto por 2 novos testes (`test_emit_chat_trace_retem_referencia_forte_do_future_ate_concluir`, `test_emit_governance_route_span_retem_referencia_forte_do_future`).

**Validação**: 179 testes verdes, `mypy --strict` limpo, rebuild + requisição real confirmada sem perda de spans.

**Evidência final via API pública do Langfuse (`GET /api/public/v2/observations`, pós-fix)**: duas sessões reais distintas disparadas via `/v1/chat/completions` após o rebuild (`debug-trace-counting-final` e `confirmacao-final-fix-referencia`) apresentaram **7/7 observations** cada, sem nenhuma perda, cobrindo toda a cadeia esperada: `governance.route` (EVENT) → `governance.workflow_transition` (EVENT) → `chat: deep-agents/router` (GENERATION, raiz) → `session.provisioning` (SPAN) → `session.first_turn` (SPAN) → `invoke_agent` (AGENT) → `chat claude-sonnet-5` (GENERATION, span nativo do SDK). Nota: a antiga rota `GET /api/public/observations/{id}` (detalhe individual) e `GET /api/public/traces` foram descontinuadas pelo Langfuse Cloud (`410 LEGACY_API_UNAVAILABLE_FOR_NEW_ORGANIZATION`, sunset 2026-11-16) para organizações criadas após 2026-09-16 — a verificação programática de observations deve usar exclusivamente `GET /api/public/v2/observations?fromStartTime=<from>&toStartTime=<to>` com paginação por `cursor` (não há `totalPages`/offset).

### Addendum 5 — Bug real: resolução de `.github/` para persona/núcleo do agente (2026-10-01)

Log real de produção reportado pelo usuário via screenshot do console Docker:
```
montar_contexto: artefato nao encontrado: /usr/local/.github/agents/tech-solution-architect.agent.md
montar_contexto: artefato nao encontrado: /usr/local/.github/copilot-instructions.md
```

**Causa raiz**: exatamente a mesma classe de bug do Addendum 1 (resolução de schema via `__file__`). `governance_pipeline._GITHUB_DIR` era calculado como `Path(__file__).resolve().parents[4]` — que funciona em dev local (instalação editável, `__file__` aponta para o repositório real), mas dentro do container Docker o pacote é instalado via `pip install` em `site-packages` (`/usr/local/lib/python3.12/site-packages/local_chat_gateway/governance_pipeline.py`), fazendo `parents[4]` resolver para `/usr/local` em vez do volume real `/governance:ro`. Resultado: o `system_message` injetado na sessão do SDK ficava **permanentemente vazio** de persona/núcleo (apenas o banner `Agente Ativo: ...`), silenciosamente, sem erro visível na resposta HTTP (apenas `logger.warning`).

**Correção** (ciclo TDD completo, 5 novos testes):
- `governance_pipeline.montar_contexto` ganhou parâmetro `github_dir: Path | None = None`, propagado também a `_caminho_contexto_seguro`/`_ler_artefato_allowlist` (a guarda RK-03 de bloqueio de `hooks/` continua válida com qualquer `github_dir`).
- Novo campo `Settings.governance_github_dir: Path` (alias `GOVERNANCE_GITHUB_DIR`, default `/governance/.github`, com o mesmo tratamento de string vazia → default real, nunca `Path('.')`).
- `routes.py` propaga `github_dir=settings.governance_github_dir` na única chamada a `montar_contexto`.
- `docker-compose.yml`/`.env.example` documentam a nova variável (opcional, já com default correto).

**Validação final**: 184 testes verdes, `mypy --strict` limpo, rebuild + requisição real → HTTP 200, **zero** ocorrências de "artefato nao encontrado" nos logs do gateway.

### Addendum 3 — Gap real de mapeamento de atributos Langfuse (2026-10-01)

Após a telemetria chegar ao Langfuse (Addendum 2 resolvido), o usuário reportou que **muitos dados apareciam vazios no dashboard** (Input, Output, Cost, Provided Model Name sempre "—" nos spans com `scope.name="local_chat_gateway"`, enquanto o span nativo do SDK, `scope.name="github.copilot"`, exibia esses dados corretamente para `chat claude-sonnet-5`).

**Causa raiz** (confirmada via pesquisa da documentação oficial do Langfuse, OTel ingestion v4):
1. `gen_ai.prompt`/`gen_ai.completion` como atributos de string plana **não são reconhecidos** pelo parser de extração de Input/Output do Langfuse — ele espera `gen_ai.prompt.<n>.*` indexado (convenção OpenLLMetry/Traceloop) ou os atributos nativos `langfuse.observation.*`.
2. Sem `gen_ai.request.model`, o span nunca é classificado como tipo **"generation"** no modelo de dados do Langfuse — fica como "span" genérico, sem colunas de Cost/Model Name/Token Usage.
3. Para **instrumentação manual** (nosso caso — `telemetry.py` constrói o payload OTLP/JSON manualmente), a documentação do Langfuse recomenda explicitamente os atributos `langfuse.observation.input`/`langfuse.observation.output`/`langfuse.observation.type`, que têm **precedência** sobre as convenções `gen_ai.*` genéricas.

**Correção aplicada em `telemetry.py`** (ciclo TDD completo, 5 novos testes em `test_telemetry.py`):
- Root span (`chat`): adicionados `langfuse.observation.type="generation"`, `langfuse.observation.input`/`output` (mesmo conteúdo de `gen_ai.prompt`/`completion`, mantidos para compatibilidade legada), `gen_ai.request.model` (novo parâmetro `model`, propagado de `routes.py` via `settings.copilot_model`, com fallback `"auto"` quando o SDK usa o modelo default), `gen_ai.response.finish_reason="stop"`, e `session.id` (atributo adicional reconhecido pela doc Langfuse para correlação, além do já existente `langfuse.session.id`).
- Spans filhos de `execute_tool`: adicionado `langfuse.observation.type="tool"`.
- Spans customizados de governança (`governance.health_check`/`governance.route`/`governance.workflow_transition`): adicionado `langfuse.observation.type="event"` (decisões instantâneas, `start=end`, correspondem ao tipo "Event" do modelo de dados do Langfuse).
- `routes.py`: todas as 4 chamadas a `emit_chat_trace` (stream + non-stream × SDK real + stub) agora passam `model=settings.copilot_model`.

**Limitação conhecida (não-bloqueante)**: tokens de uso reais (`gen_ai.usage.input_tokens`/`output_tokens`) **não são capturados** pelo nosso código — o event-stream do `github-copilot-sdk` consumido em `sdk_session.py` (`AssistantMessageData`/`ToolExecutionStartData`/`ToolExecutionCompleteData`/`AssistantIdleData`) não expõe contagem de tokens; apenas a instrumentação OTel **nativa** do próprio SDK (`scope.name="github.copilot"`) tem acesso a esses números reais (visível na coluna Cost do span `chat claude-sonnet-5`). Não fabricamos valores falsos — a ausência desses 2 atributos é intencional e documentada; o Cost real da sessão permanece visível via o span nativo do SDK no mesmo trace.

**Validação final**: 177 testes verdes (172 + 5 novos), `mypy --strict` limpo, rebuild + `POST /v1/chat/completions` → HTTP 200, zero erros no `otel-collector`.

### Addendum 6 — Bug real: estado de governança inconsistente ao reiniciar sessão expirada por TTL (2026-10-01)

Usuário reportou via Lobe Chat, ao reenviar o prompt `"o que faz o projeto projeto-exemplo-app?"` em uma conversa já existente:
```
[GOVERNANCA] Nao foi possivel avancar o turno de governanca (sessao preservada no estado anterior): R-037: a partir da Fase.ROUTER só é aceita uma decisão de roteamento explícita (TipoEvento.DECISAO_ROTEAMENTO) — evento recebido tem tipo=<TipoEvento.AVANCO_ETAPA: 'avanco_etapa'>
```

**Causa raiz**: `SessionStore.create_session()` (`routes.py` só a invoca quando `is_session_expired(session_id)` é `True` — TTL `GATEWAY_SESSION_TTL_S`, default 1800s) reiniciava `fase="router"` na branch de `UPDATE`, mas **preservava** os campos aditivos de governança (`workflow`/`etapa`/`agente_ativo`/`aprovacoes`) do turno anterior à expiração. Resultado: `_sessao_atual` (`routes.py`) reconstruía uma `governance.Sessao` com `fase=Fase.ROUTER` **e** `workflow` residual não-nulo — um estado logicamente inconsistente que a `TabelaTransicao`/state machine nunca produz sozinha (todo reset legítimo via `_resetar_para_router`/R-042/R-052 zera `workflow` junto com `fase`). `governance_pipeline.preparar_turno` decide se re-roteia checando apenas `sessao.workflow is None` — como o valor residual não era `None`, o turno reaproveitava o workflow "fantasma" da sessão expirada e gerava `TipoEvento.AVANCO_ETAPA`, que a guard clause 1 (R-037) de `_transicionar_a_partir_do_router` rejeita corretamente por a sessão estar em `Fase.ROUTER`.

**Correção** (TDD completo, 1 novo teste de integração): `create_session()` agora reseta explicitamente `workflow=None, etapa=None, agente_ativo=None, aprovacoes=None` junto com `fase="router"` na branch de `UPDATE` — uma sessão reiniciada por expiração de TTL volta 100% do zero ao router, com a mesma garantia de consistência de um reset via `_resetar_para_router` (RK-06). Novo teste `test_create_session_em_sessao_expirada_reseta_campos_de_governanca` reproduz o estado residual diretamente no `SessionStore` (sem precisar do roteador completo) e confirma o reset total.

**Validação final real (reprodução ponta a ponta)**: estado residual (`fase=em_workflow`, `workflow=WORKFLOW-FEATURE-DEVELOPMENT`, `etapa=3`) inserido diretamente no SQLite do container com `last_seen_at` 2h no passado (além do TTL de 1800s); nova requisição real com o mesmo `session_id` → **HTTP 200**, resposta real do SDK investigando o projeto (zero menção ao erro R-037), sessão corretamente re-roteada do zero para `WORKFLOW-TECHNICAL-ANALYSIS`/etapa 1/`tech-solution-architect` (workflow anterior completamente descartado, sem conflito). 185 testes verdes (184 + 1 novo), `mypy --strict` limpo, zero ocorrências de "error"/"R-037"/"GOVERNANCA" nos logs do gateway pós-fix.

### Addendum 7 — Bug real: estado inconsistente já persistido no banco não era autocorrigido (2026-10-01)

**O fix do Addendum 6 não foi suficiente** — o usuário reportou via screenshot do Lobe Chat que o mesmo erro R-037 persistia em uma conversa já existente, mesmo após o rebuild com o fix. Investigação direta no SQLite do container revelou a linha `('ca967b64f3c18b57', 'router', 'WORKFLOW-TECHNICAL-ANALYSIS', 1, 'tech-solution-architect', ...)` — exatamente o estado inconsistente descrito no Addendum 6 (`fase='router'` + `workflow` residual não-nulo).

**Causa raiz**: o Addendum 6 corrigiu apenas a *escrita futura* de `create_session()` (prevenção), mas **nunca corrige dados já corrompidos sentados no volume** (nenhuma migração/reparo retroativo, ao contrário do que `_migrar_colunas_aditivas_sessions` faz para schema). Pior: a sessão corrompida nunca re-dispara `create_session()` para ser corrigida, porque `is_session_expired()` só retorna `True` após o TTL (1800s) — e cada nova tentativa do usuário (inclusive as que falham com erro R-037) passa primeiro por `touch_session()`, que **renova `last_seen_at`** antes da falha. Resultado: a sessão corrompida fica "viva" e travada **indefinidamente**, pois o TTL nunca expira enquanto o usuário continuar tentando.

**Correção** (TDD completo, 5 novos testes unitários em `tests/unit/test_routes_sessao_atual.py`): guarda de invariante auto-corretiva em `routes._sessao_atual()` — `Fase.ROUTER` **sempre** implica `workflow=None`/`etapa=0`/`agente_ativo=padrão`, independentemente do que estiver persistido no `SessionRecord`. Diferente do fix do Addendum 6 (que previne a escrita), este fix corrige a **leitura** — autocura qualquer linha já corrompida (por este bug ou por qualquer vetor futuro não antecipado) sem exigir migração de dados, pois a invariante é reforçada a cada request, no único ponto de construção de `governance.Sessao` a partir do banco. `aprovacoes` são preservadas (apenas `workflow`/`etapa`/`agente_ativo` residuais são descartados).

**Validação final real (mesma sessão travada do screenshot do usuário)**: a linha `ca967b64f3c18b57` (capturada travada antes do fix, com `last_seen_at` recente — confirmando que o TTL nunca expirava) foi usada diretamente em uma nova requisição real pós-rebuild → **HTTP 200**, resposta real do SDK explicando o projeto `projeto-exemplo-app` (zero menção a R-037/GOVERNANCA), sessão corretamente re-roteada para `em_workflow`/`WORKFLOW-TECHNICAL-ANALYSIS`/etapa 1/`tech-solution-architect`. 190 testes verdes (185 + 5 novos), `mypy --strict` limpo, zero erros nos logs.

**Lição de processo**: ao corrigir um bug de estado inconsistente causado por uma escrita incorreta, sempre considerar separadamente (a) prevenir a escrita futura E (b) autocurar/sanitizar a leitura de dados já persistidos incorretamente — a ausência de (b) deixou o bug do Addendum 6 "meio corrigido" e invisível em testes (que sempre partem de um banco limpo), mas 100% reproduzível em produção real com dados pré-existentes.

### Addendum 8 — Bug real: 4 traces desconectados no Langfuse por turno (trace_id gerado por função) (2026-10-01)

**Causa raiz** (confirmada por `@bug-triage`): `telemetry.py` gerava um `trace_id = uuid.uuid4().hex` **novo a cada função de emissão de span** — `emit_chat_trace` (linha ~234) e a função interna `_emit_custom_governance_span` (linha ~387), reutilizada por `emit_governance_route_span`/`emit_governance_workflow_transition_span`/`emit_governance_health_check_span`. Como um único turno de usuário em `routes.chat_completions` chama essas funções de forma independente (roteamento → transição de workflow → dispatch do SDK), cada chamada recebia seu próprio `trace_id`, fragmentando o turno em até 4 traces desconectados no dashboard do Langfuse. O span com o input/output real do prompt do usuário (`chat: deep-agents/router`, emitido por `emit_chat_trace`) ficava isolado numa árvore de trace órfã, desconectada de `governance.route`/`governance.workflow_transition` — por isso o usuário não via input/output coerentemente agrupados sob o mesmo trace.

**Correção** (TDD estrito, `src/local_chat_gateway/telemetry.py` + `src/local_chat_gateway/api/routes.py`): `trace_id` passa a ser um parâmetro **opcional** (`trace_id: str | None = None`) em `emit_chat_trace`, `_emit_custom_governance_span` e nos 3 wrappers públicos de governança, com fallback para `uuid.uuid4().hex` quando não fornecido (preserva 100% de compatibilidade retroativa com os chamadores diretos já existentes nos testes unitários). O handler `chat_completions` em `routes.py` passa a gerar **um único** `turno_trace_id = uuid.uuid4().hex` logo após a resolução de `session_id` (Seção 1b, antes do enforcement de budget) e o repassa explicitamente a `emit_governance_route_span`, `emit_governance_workflow_transition_span` e, via novo parâmetro `trace_id` de `_real_or_stub_stream`/`_real_or_stub_completion`, a `emit_chat_trace`:

```python
# routes.py — gerado uma única vez por turno (Seção 1b)
turno_trace_id = uuid.uuid4().hex
...
await emit_governance_route_span(..., trace_id=turno_trace_id)
...
await emit_governance_workflow_transition_span(..., trace_id=turno_trace_id)
...
return await _real_or_stub_completion(..., trace_id=turno_trace_id)  # repassado a emit_chat_trace internamente
```

```python
# telemetry.py — fallback retrocompatível em cada função de emissão
trace_id_efetivo = trace_id if trace_id is not None else uuid.uuid4().hex
```

**Testes criados** (`tests/unit/test_telemetry.py`, +2 testes, 190 → 192 no gateway):
1. `test_caracterizacao_emit_chat_trace_sem_trace_id_gera_ids_distintos` — teste de caracterização (safety net): sem `trace_id` explícito, duas chamadas continuam gerando IDs diferentes (fallback retrocompatível preservado, sem regressão nos 20 testes pré-existentes deste módulo).
2. `test_emit_chat_trace_e_governance_spans_compartilham_trace_id_do_turno` — Red → Green: `emit_governance_route_span`, `emit_governance_workflow_transition_span` e `emit_chat_trace` chamadas com o mesmo `trace_id` explícito despacham payloads OTLP com `traceId` idêntico nos 3 spans.

**Validação real ponta a ponta** (`docker compose --profile lobe --profile otel up -d --build --force-recreate gateway`): requisição `POST /v1/chat/completions` com o prompt `"o que faz o projeto projeto-exemplo-app?"` e `x-session-id: fix-trace-unificado-1790877845` (novo) → **HTTP 200**. Consulta subsequente à API v2 do Langfuse (`GET /api/public/v2/observations`, paginação por cursor — rotas legadas `/api/public/traces`/`/api/public/observations/{id}` descontinuadas/410 para esta organização) filtrada pela sessão confirmou os 3 spans customizados do turno com **o mesmo `traceId` (`f87b04db07a44427ac7649d262581687`)**:

| `name` | `type` | `traceId` |
|---|---|---|
| `chat: deep-agents/router` | GENERATION | `f87b04db07a44427ac7649d262581687` |
| `governance.route` | EVENT | `f87b04db07a44427ac7649d262581687` |
| `governance.workflow_transition` | EVENT | `f87b04db07a44427ac7649d262581687` |

192 testes verdes (190 + 2 novos, zero regressão), `mypy --strict` limpo (16 arquivos de `src/local_chat_gateway`), zero erros de `get_errors`. O span nativo do SDK (`chat claude-sonnet-5`/`invoke_agent`, `scope.name=github.copilot`) permanece intencionalmente fora de escopo (caixa-preta de `sdk_session.py`/pacote `copilot`), com seu próprio `traceId` nativo separado — apenas os 3 spans customizados de `local_chat_gateway` foram unificados, conforme causa raiz identificada.

### Addendum 9 — Bug real: `system_message` concatenado como texto no prompt era ignorado pelo Claude subjacente (2026-10-01/02)
**Causa raiz** (confirmada por investigacao direta no SDK real dentro do container): o banner de governanca (`"Agente Ativo: <agente>\n[WORKFLOW:.../ETAPA:...]"` + persona + nucleo, montado por `governance_pipeline.montar_contexto()`) era injetado em `sdk_session.py` via `_compor_prompt_com_sistema()` como **texto simples concatenado como prefixo** do prompt do usuario, enviado via `session.send(...)`. O modelo subjacente (Claude via Copilot SDK) tratava esse bloco como conteudo nao-confiavel embutido na mensagem do usuario (heuristica de seguranca anti prompt-injection do proprio modelo) e o **ignorava explicitamente** — confirmado em teste real via Lobe Chat: a resposta do agente incluia literalmente "ignorei o bloco 'Agente Ativo: tech-solution-architect' ... nao e uma instrucao valida vinda de voce".
**Evidencia da inspecao do SDK real** (`docker exec local-chat-gateway python -c "..."`): `copilot.CopilotClient.create_session(...)` aceita nativamente um parametro `system_message: SystemMessageConfig | None`, uniao de 3 `TypedDict`s em `copilot.session`:
```
$ docker exec local-chat-gateway python -c "import copilot.session as s; print([n for n in dir(s) if 'System' in n])"
['SystemMessageAppendConfig', 'SystemMessageConfig', 'SystemMessageCustomizeConfig', 'SystemMessageReplaceConfig', 'SystemMessageSection']
$ docker exec local-chat-gateway python -c "import copilot.session as s; print(s.SystemMessageAppendConfig.__annotations__); print(s.SystemMessageConfig)"
{'mode': ForwardRef("NotRequired[Literal['append']]"), 'content': ForwardRef('NotRequired[str]')}
copilot.session.SystemMessageAppendConfig | copilot.session.SystemMessageReplaceConfig | copilot.session.SystemMessageCustomizeConfig
```
`SystemMessageAppendConfig` (`{"mode": "append", "content": str}`) **adiciona** o conteudo ao "CLI foundation" do SDK sem substituir guardrails — exatamente o modo que o gateway ja dizia implementar, mas via concatenacao textual manual em vez do canal nativo. `SystemMessageReplaceConfig` remove os guardrails do SDK (fora de escopo, nao usado). `SystemMessageCustomizeConfig` permite customizacao granular por secao (fora de escopo desta correcao).
**Correcao aplicada** (TDD estrito, `src/local_chat_gateway/sdk_session.py` + `tests/unit/test_sdk_session.py`, diff cirurgico):
```python
# ANTES (sdk_session.py, linha ~383) — banner concatenado como texto do usuario:
async with await client.create_session(
    ..., enable_file_hooks=False, enable_config_discovery=False,
) as session:
    session.on(_on_event)
    await session.send(
        _compor_prompt_com_sistema(system_message, _joined_prompt(messages))
    )
```
```python
# DEPOIS — system_message via mecanismo NATIVO do SDK (SystemMessageAppendConfig):
async with await client.create_session(
    ...,
    enable_file_hooks=False,
    enable_config_discovery=False,
    system_message=(
        {"mode": "append", "content": system_message}
        if system_message is not None
        else None
    ),
) as session:
    session.on(_on_event)
    await session.send(_joined_prompt(messages))
```
`_compor_prompt_com_sistema()` foi **preservada** (nao removida) apenas como teste de caracterizacao do comportamento legado (`TestComporPromptComSistema`), com docstring atualizada marcando-a `[LEGADO/NAO MAIS USADO em stream_chat]` — nao e mais chamada em nenhum ponto de producao (`grep` confirma zero outros chamadores alem dos proprios testes unitarios da funcao).
**Testes criados/atualizados** (`tests/unit/test_sdk_session.py`, mantendo 20/20 verdes neste modulo, 192 no gateway no total — sem variacao liquida, pois um teste Red foi substituido/reforcado em vez de adicionado):
1. `test_deve_repassar_system_message_nativo_ao_create_session` (substitui o antigo `test_deve_prefixar_system_message_ao_prompt_quando_fornecido_no_stream_chat`) — Red → Green: `stream_chat(..., system_message="banner de teste", ...)` DEVE repassar `{"mode": "append", "content": "banner de teste"}` a `client.create_session(system_message=...)` **e** `session.send` DEVE receber apenas `"user: oi"` (sem prefixo).
2. `test_deve_enviar_prompt_sem_prefixo_quando_system_message_for_omitido`/`..._for_none_explicito` (regressao, reforcadas): alem do prompt sem prefixo, agora tambem afirmam `instancia.system_message_recebido is None`.
3. Fake `_FakeClient.create_session` em `_instalar_copilot_falso` ganhou o kwarg `system_message: Any = None`, armazenado em `self.system_message_recebido` para as novas asserts.
**Evidencia de resolucao**: `pytest -q` → **192 passed** (suite completa do gateway, zero regressao); `mypy --strict src/local_chat_gateway/sdk_session.py` → **Success: no issues found**; `get_errors` → limpo nos 2 arquivos alterados.
**Validacao real ponta a ponta** (`docker compose --profile lobe --profile otel up -d --build --force-recreate gateway`, `POST /v1/chat/completions`, `x-session-id` novo, prompt `"o que faz o projeto projeto-exemplo-app?"`, HTTP 200): confirmado via `inspect.getsource` dentro do container que o codigo implantado usa `system_message=(...)` nativo e **nao** mais `_compor_prompt_com_sistema(system_message, ...)` em `stream_chat`. O conteudo factual da resposta sobre o projeto permaneceu correto e completo. **Ressalva observada** (fora do escopo de defeito de codigo Python): mesmo com o `system_message` trafegando pelo canal nativo do SDK (sem concatenacao textual), a resposta do modelo ainda mencionou ter "ignorado" o bloco "Agente Ativo / tech-solution-architect" — indicando que a heuristica de desconfianca do Claude subjacente reage ao **padrao de conteudo** do banner (frase no estilo "voce agora e o agente X"), independentemente do canal de transporte (`system_message` nativo vs. prompt do usuario). A causa raiz tecnica original (concatenacao textual ignorada por design anti-injecao) **foi corrigida e verificada** (zero concatenacao remanescente, mecanismo 100% nativo do SDK); a ressalva remanescente e um problema de **redacao/design do conteudo do banner** (`governance_pipeline.montar_contexto`), nao um defeito de codigo — recomenda-se handoff a `@python-arch-advisor`/revisao de prompt-design do banner (ex.: reformular `"Agente Ativo: X"` em linguagem menos auto-referencial/diretiva) como proximo passo, fora do escopo cirurgico deste bug fix.
### Próximo passo mínimo
Preparação de PR real (`@pr-gatekeeper`: síntese de diff, matriz de risco, changelog) e, em paralelo ou posteriormente, validação manual de CA-10 em ambiente com Docker + Lobe Chat + token real do Copilot SDK.
