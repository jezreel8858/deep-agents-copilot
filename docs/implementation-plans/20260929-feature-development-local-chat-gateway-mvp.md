# Plano de Implementação — Pacote `local_chat_gateway` (MVP Completo)

> **Workflow Canônico**: `WORKFLOW-FEATURE-DEVELOPMENT` (Fases 1, 2, 3 e 4 Concluídas e Validadas)
> **Blueprint de origem**: [`docs/architecture/BLUEPRINT_LOCAL_CHAT_GATEWAY.md`](../architecture/BLUEPRINT_LOCAL_CHAT_GATEWAY.md)
> **Data de Atualização**: 2026-09-29
> **Autoria**: `@python-arch-advisor`
> **Decisões consolidadas**: D1=`read_only`, D2=SQLite, D3=FastAPI+uvicorn, D4=Lobe Chat (MVP ativo)
> **Status de Execução**: **Fases 1 a 4 CONCLUÍDAS** — 119/119 testes verdes, integração real, governança e SQLite 100% operacionais.

---

## 1) Estrutura de Diretórios Atual (Consolidada)

```
deploy/local-chat-gateway/
├── pyproject.toml              # FastAPI, uvicorn, pydantic, sqlalchemy, PyYAML, extra [sdk]
├── .env.example                # Template com PROJECTS_ROOT_PATH, secrets e chaves
├── .env                        # Configuração local ativa do operador (gitignored)
├── Dockerfile                  # Multi-stage build (builder + runtime não-root UID 10001)
├── Dockerfile.dockerignore     # Contexto de build enxuto
├── docker-compose.yml          # Services gateway + lobe-chat (+ otel profile)
├── secrets/
│   └── copilot_token           # Secret do Copilot SDK (montado via Docker secret)
├── src/local_chat_gateway/
│   ├── __init__.py
│   ├── py.typed
│   ├── app.py                  # FastAPI app factory (telemetry auto_configure=False)
│   ├── config.py               # Settings com PROJECTS_ROOT_PATH e PROJECTS_LOCAL_YAML
│   ├── auth.py                 # Bearer local, GATEWAY_API_KEY, recusa "change-me"
│   ├── governance.py           # wrapper fino sobre governance_runner.routing/runner
│   ├── checkpoint_engine.py    # gramática Seção 5 do blueprint + Invariante 11
│   ├── permission_policy.py    # stub read_only/propose/apply + 4 guardas
│   ├── event_mapper.py         # stub SDK→SSE, Literal de eventos confirmados
│   ├── sdk_session.py          # Integração real Copilot SDK (lazy, tipada, streaming SSE)
│   ├── projects_catalog.py     # Descoberta automática multi-projeto (projects.local.yaml)
│   ├── session_store.py        # SQLite: sessions, checkpoints, budget_daily
│   └── api/
│       ├── __init__.py
│       ├── routes.py           # /v1/models, /v1/chat/completions (stream/non-stream), /healthz
│       └── schemas.py          # ChatMessage, ChatCompletionRequest/Response/Chunk, Error
└── tests/
    ├── conftest.py              # fixtures: tmp_db, client (TestClient), fake_settings, session_store
    ├── unit/
    │   ├── test_checkpoint_engine.py
    │   ├── test_permission_policy.py
    │   ├── test_event_mapper.py
    │   ├── test_auth.py
    │   ├── test_sdk_session.py        # Mocks de eventos, permissões tipadas e guardas
    │   └── test_projects_catalog.py   # Resolução de paths host->container (Win/POSIX)
    └── integration/
        ├── test_routes_models.py      # Contratos /v1/models e streaming SSE
        ├── test_routes_healthz.py     # /healthz sem autenticação
        ├── test_session_store.py      # SQLite migrações e persistência
        └── test_governance_phase4.py  # Multi-turno, teto diário 429 e Invariante 11
```

---

## 2) Registro de Fases Executadas

### ✅ Fase 1 — Skeleton do Pacote & Governança em Código (Concluída)
- Módulos fundamentais implementados: `auth.py`, `checkpoint_engine.py`, `permission_policy.py`, `session_store.py`, `api/schemas.py`, `api/routes.py`, `config.py`, `governance.py`.
- Regra Invariante 11 implementada e coberta por testes parametrizados (custo zero e sem mutação para respostas evasivas).
- Dependência local de `governance-runner` mantida via instalação editável com zero duplicação de código.

### ✅ Fase 2 — Infraestrutura Docker & Streaming SSE (Concluída)
- `Dockerfile` multi-stage com usuário não-root `gateway` (UID 10001).
- `docker-compose.yml` com profiles (`lobe`, `otel`), hardening `read_only: true`, `cap_drop: [ALL]`.
- Implementação de streaming SSE real em `/v1/chat/completions` (necessário para o Lobe Chat, que opera exclusivamente via stream).
- Correção de falhas reais de build: `pull_policy: build`, unificação de comando `pip install` para resolução de dependência local e desligamento do auto-OTel do FastAPI 0.142.

### ✅ Fase 3 — Integração Real com GitHub Copilot SDK & Multi-Projeto (Concluída)
- **Módulo `sdk_session.py`**:
  - Extra opcional `[sdk]` (`github-copilot-sdk>=1.0.15`) com import tardio resiliente.
  - Mapeamento correto de eventos reais pós-análise de sessão viva: `AssistantMessageData` (`.content`), `AssistantIdleData` (fim de turno), `ToolExecutionStartData`, `ToolExecutionCompleteData`.
  - Fix de permissões tipadas: retorno de `PermissionDecisionApproveOnce` e `PermissionDecisionReject` (eliminando o erro `AttributeError: dict object has no attribute to_dict`).
  - Cache de correlação `tool_call_id -> tool_name` para visualização amigável de execução de ferramentas no chat.
  - Blindagem de isolamento: `enable_file_hooks=False` e `enable_config_discovery=False` para evitar que hooks de outros projetos sob a raiz montada quebrem as ferramentas da sessão do gateway.
- **Volume do Usuário & Filesystem**:
  - Volume nomeado `gateway-home:/home/gateway` cobrindo o `$HOME` inteiro do usuário do container, eliminando falhas de `EROFS: Read-only file system` na inicialização do runtime nativo e criação de logs/sessões.
- **Descoberta Automática Multi-Projeto (`projects_catalog.py`)**:
  - Montagem de `${PROJECTS_ROOT_PATH}:/workspaces` contendo todos os projetos.
  - Leitura dinâmica de `projects.local.yaml` traduzindo paths externos (Windows ou POSIX) para dentro do container.
  - Injeção de `additional_directories` e `working_directory="/workspaces"` na sessão do SDK.
  - Qualquer novo projeto clonado no host dentro de `PROJECTS_ROOT_PATH` torna-se acessível imediatamente sem reiniciar ou reconfigurar o gateway.

### ✅ Fase 4 — Fiação de Governança em Tempo de Execução, Multi-Turno & Checkpoints (Concluída)
- **Sessões Multi-Turno Persistidas**:
  - `session_id` extraído do cabeçalho `x-session-id` / `x-conversation-id` ou gerado via hash estável da primeira mensagem.
  - Reuso e touch de sessão em `SessionStore` (SQLite), repassando `session_id` nativamente ao `client.create_session(...)` do SDK.
- **Enforcement de Teto Diário (`GATEWAY_MAX_PREMIUM_PER_DAY`)**:
  - Bloqueio automático com HTTP 429 (`rate_limit_error`) se o consumo do dia ultrapassar o limite configurado.
  - Registro atômico de consumo no SQLite por dia (`budget_daily`).
- **Enforcement da Invariante 11 nos Endpoints**:
  - Se houver checkpoint pendente na sessão, respostas vagas ("ok", "prossiga", "sim") ou fora da gramática reemitem a pergunta localmente via streaming SSE ou JSON com custo zero (zero chamadas de rede ou LLM).
  - Respostas válidas resolvem o checkpoint no SQLite e liberam o fluxo normal.
- **Bridge de Permissões com as 4 Guardas**:
  - `PermissionRequestWrite` integrado: negado em `read_only` e `propose`; em `apply`, bloqueado se houver checkpoint pendente ou se o arquivo for sensível (`.git`, `secrets`, `.env`, `.pem` — Guarda 4).

---

## 3) Status de Qualidade & Testes Atuais

```
119 passed, 1 warning (103 unitários + 16 integração)
mypy --strict src: Success (0 issues em 14 arquivos fonte)
black / isort / flake8: 100% em conformidade
```

---

## 4) Checklist de Conclusão do Pacote MVP

- [x] Fase 1 entregue (Skeleton de governança em código).
- [x] Fase 2 entregue (Docker compose, profiles lobe/otel, streaming SSE).
- [x] Fase 3 entregue (Integração SDK real + multi-projeto automático via `projects.local.yaml`).
- [x] Fase 4 entregue (Governança runtime, SQLite session store, teto diário 429, Invariante 11 e guardas de escrita).
- [x] Imagem Docker `local-chat-gateway:local` reconstruída e validada.
- [x] 119 testes automatizados verdes e linters sem violações.
