# Deep Agents Gateway (MVP)
Gateway OpenAI-compatible local para o Copilot SDK, com governanca aplicada em
codigo (nao um proxy passivo). Ver `docs/architecture/BLUEPRINT_LOCAL_CHAT_GATEWAY.md`
e `docs/implementation-plans/20260929-feature-development-local-chat-gateway-mvp.md`.
## Rodar localmente fora do Docker (dev watch com bootstrap automatico)
```
python dev_watch.py
```
**Zero comandos extras na 1a execucao** -- `dev_watch.py` faz sozinho:
1. Cria `.venv` neste diretorio se nao existir.
2. Instala `governance-runner` (editable) + `deep-agents-gateway[dev,sdk]`
   (editable) se ainda nao estiverem presentes no venv.
3. Reexecuta a si mesmo com o Python do `.venv` se o `python`/`py` do PATH
   resolver para outro interpretador (evita `did not find executable at
   ...python.exe` em shells com um `python` global quebrado/desatualizado).
4. Gera `.env` a partir de `.env.example` com `GATEWAY_API_KEY`/
   `WEB_ACCESS_CODE` aleatorios seguros, se `.env` nao existir.
5. Resolve os paths de `.env` com default de CONTAINER
   (`GOVERNANCE_GRAPH_PATH`, `GOVERNANCE_GITHUB_DIR`, `PROJECTS_LOCAL_YAML`,
   `GATEWAY_WORKSPACE_DIR`, `GATEWAY_DB_PATH`) para os equivalentes do host.
6. Avisa (sem bloquear) se `secrets/copilot_token` estiver ausente/vazio --
   unica credencial que precisa ser colada manualmente (token pessoal, nao
   pode ser gerado automaticamente).
7. Sobe o uvicorn com `--reload` apontando para `src/`.

Flags uteis:
```
python dev_watch.py --port 8081
python dev_watch.py --no-reload       # debugger attachado, sem watch
python dev_watch.py --reinstall       # forca reinstalacao das deps editaveis
python dev_watch.py --no-bootstrap    # pula criacao de venv/instalacao (mais rapido)
```
> `[sdk]` (pacote `github-copilot-sdk`, import `copilot`) ja e instalado
> automaticamente pelo bootstrap acima. Sem ele, `sdk_session._import_copilot()`
> levantaria `SDKUnavailableError` e `routes.py` cairia sempre no fallback
> deterministico (stub -- resposta fixa `"stub: SDK real do Copilot ainda
> nao integrado..."`). Se mesmo assim o chat responder esse texto, confirme
> que `secrets/copilot_token` tem um token valido (unico passo manual).

### Troubleshooting: "porta ja esta em uso"

Bug real investigado (2026-10-04): reexecucoes rapidas de `dev_watch.py`
(ex.: apos um crash do uvicorn que nao libera a porta a tempo) falhavam com
um traceback cru do `OSError`/`[WinError 10048]`. `dev_watch.py` agora
detecta isso ANTES de subir o uvicorn e falha rapido com uma mensagem
acionavel. Para liberar a porta manualmente (PowerShell):
```
Get-NetTCPConnection -LocalPort 8080 | Select-Object -Property OwningProcess
Stop-Process -Id <PID> -Force
```
Ou use outra porta: `python dev_watch.py --port 8081`.

### Nota: logging em arquivo (`.tmp/gateway.log`)

Alem do stdout do uvicorn, o gateway agora grava logs (aditivamente, nunca
substituindo o stdout) em `.tmp/gateway.log` (rotacionado por tamanho --
`GATEWAY_LOG_MAX_BYTES`/`GATEWAY_LOG_BACKUP_COUNT`), util para inspecionar
uma sessao apos fechar o terminal. Caminho configuravel via
`GATEWAY_LOG_FILE`; `.tmp/` e gitignored.

## Testes
```
pytest deploy/local-chat-gateway/tests -v --tb=short
mypy --strict deploy/local-chat-gateway/src/local_chat_gateway
black --check --line-length 88 deploy/local-chat-gateway/src deploy/local-chat-gateway/tests
isort --check-only deploy/local-chat-gateway/src deploy/local-chat-gateway/tests
flake8 deploy/local-chat-gateway/src deploy/local-chat-gateway/tests
```

## Uso via Docker / docker-compose (MVP)

> Modo padrao: **read-only** e **localhost-only**. O servico `gateway` roda com
> `read_only: true` (filesystem raiz imutavel, exceto `/tmp` via tmpfs e o volume
> `gateway-data`), `cap_drop: [ALL]` e `no-new-privileges:true`. Nenhuma porta e
> publicada fora de `127.0.0.1` por padrao -- exposicao em LAN exige alteracao
> explicita e consciente do `docker-compose.yml` (fora do escopo documentado aqui).

### 1. Configurar variaveis de ambiente
```
cp .env.example .env
# edite .env: GATEWAY_API_KEY, LOBE_ACCESS_CODE (nunca "change-me"), PROJECTS_ROOT_PATH
```

`PROJECTS_ROOT_PATH` deve apontar para o diretorio-pai comum (path absoluto
do host) que contem TODOS os projetos registrados em `projects.local.yaml`
(campo `path_externo`) -- ex.: se `projects.local.yaml` registra
`D:\workspace\meu-projeto-a` e `D:\workspace\meu-projeto-b`, configure
`PROJECTS_ROOT_PATH=D:/workspace`. O gateway (`projects_catalog.py`) traduz
automaticamente cada `path_externo` para o path correspondente dentro do
container (montado uma unica vez em `/workspaces`) a cada request de chat --
**qualquer projeto novo adicionado ao YAML e clonado sob esse mesmo
diretorio-pai fica acessivel ao Copilot sem editar `.env`/`docker-compose.yml`
novamente**. Projetos com `path_externo` fora dessa raiz sao ignorados
(logado como aviso). Se a variavel nao for definida no `.env`, o compose usa
como fallback o diretorio vazio `./.workspace-placeholder` deste pacote --
seguro para uso em `read_only`, mas nenhum projeto fica acessivel.

### 2. Gerar o secret do token do Copilot SDK
```
mkdir -p secrets
echo "<seu-PAT-ou-token-do-Copilot-SDK>" > secrets/copilot_token
```
O arquivo `secrets/copilot_token` e ignorado pelo git (`.gitignore` deste
diretorio) e montado como **Docker secret** em `/run/secrets/copilot_sdk_token`
dentro do container `gateway` -- nunca via variavel de ambiente em texto plano.

### 2.1 Modo de permissao de escrita (`GATEWAY_PERMISSION_MODE`)

| Modo | Comportamento |
|---|---|
| `read_only` (default do `.env.example`) | Nenhuma escrita de arquivo e permitida -- apenas leitura/analise, equivalente a um Code Review automatizado. |
| `propose` | Escrita e sempre negada; o agent e instruido a propor diffs em texto (nao implementado, fora de escopo desta fase). |
| `apply` | Escrita real e permitida nas tools NATIVAS do SDK (`create`/`edit`, mapeadas para `PermissionRequestWrite`), sujeita a 4 guardas (ver `sdk_session._bridge_permissao`/`permission_policy.PermissionPolicyStub`): sem checkpoint humano pendente, caminho fora de `.git/`, `secrets/`, `*.env*`, `*.pem`. **Necessario para usar a UI web como substituto do plugin da IDE (implementar features, nao so consultar).** Comandos de SHELL genericos (`bash`) continuam bloqueados pela politica conservadora de MCP/custom-tool -- apenas as tools estruturadas de criacao/edicao de arquivo sao liberadas em `apply`.

Confirmado por teste real (2026-10-01): em `apply`, uma solicitacao de
criacao de arquivo via a UI web grava de fato no filesystem do HOST (o
bind mount `PROJECTS_ROOT_PATH:/workspaces` e leitura-E-escrita, sem `:ro`).

### 2.2 Custom Agents / `run_subagent` (RT-04)

O catalogo de agents (`.github/agents/**/*.agent.md`) e descoberto
automaticamente no startup (`app.py` lifespan, `agent_catalog.
descobrir_custom_agents`) e repassado ao SDK real via
`create_session(custom_agents=[...])`. **Isto e OBRIGATORIO** para que a
tool `run_subagent` funcione de fato -- o GitHub Copilot SDK NAO descobre
`.github/agents/*.agent.md` automaticamente mesmo com
`enable_config_discovery=True` (issue oficial do mantenedor,
[github/copilot-sdk#1080](https://github.com/github/copilot-sdk/issues/1080),
em aberto). Sem este wiring, o banner `Agente Ativo: <nome>` injetado via
`system_message` e tratado pelo modelo como "role-play" sem lastro, e ele
recusa a persona (confirmado por teste real: *"I don't have access to
tools like ... run_subagent ... I'm GitHub Copilot"*). Com o catalogo
registrado, o modelo adota a persona corretamente e realiza investigacao
real (grep/view/bash) seguindo as instrucoes do `.agent.md`.

**Hooks de arquivo (`.github/hooks/*.json`) permanecem deliberadamente
desabilitados** (`enable_file_hooks=False`). Diferente de `custom_agents`,
file hooks executam comandos de SHELL em pontos do ciclo de vida da sessao
e **nao sao protegidos por `on_permission_request`** (docs oficiais do
SDK). O caso de uso real (orquestracao multi-agent, paridade com o plugin
da IDE) e resolvido inteiramente por `custom_agents` sem reintroduzir esse
vetor de risco.

### 3. Subir os servicos
```
# D4-rev: gateway + frontend web (Next.js + CopilotKit), sem profile
# (pull_policy=build no gateway e no web -> Compose sempre constroi
# localmente, nunca tenta "pull" de um registry)
docker compose up

# Apos alterar codigo em src/ ou apps/web/, force a reconstrucao da imagem:
docker compose up --build

# Com telemetria OTLP opcional (reusa tools/otel-langfuse/otel-collector-config.yaml)
docker compose --profile otel up

```
A UI web fica disponivel em `http://127.0.0.1:3000` (exige `WEB_ACCESS_CODE`
configurado); o gateway expoe `http://127.0.0.1:8080` (`GET /healthz` sem auth,
demais rotas exigem `Authorization: Bearer ${GATEWAY_API_KEY}`).

### 4. Validar a sintaxe do compose (sem subir containers)
```
docker compose config
```
### Nota sobre .dockerignore
O build context deste servico e a RAIZ DO REPOSITORIO (ver Dockerfile). Por
isso, o BuildKit aplica exclusivamente `deploy/local-chat-gateway/Dockerfile.dockerignore`
(convencao `<dockerfile>.dockerignore` do Docker >= 23) -- este e o UNICO
arquivo de ignore ativo para este build. Nao existe mais um `.dockerignore`
simples redundante neste diretorio (removido para eliminar risco de drift
silencioso entre duas copias).
## Nao-escopo desta fase
- Modo `propose` (diff textual) -- apenas negado, sem geracao de diff estruturado.
- Descoberta automatica de hooks de arquivo (`enable_file_hooks`) -- decisao deliberada, ver Secao 2.2.
