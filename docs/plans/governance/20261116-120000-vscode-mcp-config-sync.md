---
title: "Plano de Governança — Sincronização de MCP Servers no VS Code e Template Genérico vscode_mcp.json"
status: "APPROVED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-16T12:00:00Z"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-vscode-mcp-01"
session_id: "e0fbf32b-34fc-47af-b026-b703d0eb6dd2"
parent_plan_ref: "N/A — plano raiz"
related-planning-doc: "N/A"
allowed_files:
  - ".vscode/mcp.json"
  - ".config/vscode_mcp.json"
  - "tmp/mcp.json.bak"
  - "docs/plans/governance/20261116-120000-vscode-mcp-config-sync.md"
reviewer: "@plan-critic"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
review_tier1: "PASS"
rollback_plan:
  strategy: "Restaurar .vscode/mcp.json a partir do backup pré-execução salvo em tmp/mcp.json.bak (visto que .vscode/ é ignorado pelo Git na linha 3 do .gitignore e git checkout não se aplica a arquivos ignorados) e remover .config/vscode_mcp.json do disco."
  verification: "Validar parsing JSON de .vscode/mcp.json restaurado, confirmar ausência de .config/vscode_mcp.json e executar pytest tests/governance_audit/ -q confirmando exit code 0."
---

# Plano de Governança — Sincronização de MCP Servers no VS Code e Template Genérico `vscode_mcp.json`

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

Sincronizar a configuração de servidores MCP do VS Code (`.vscode/mcp.json`, atualmente com apenas 2 servidores e usando configuração legada v1 no `context-mode`) tomando como base o arquivo `.config/idea_mcp.json` do IntelliJ IDEA (6 servidores homologados: `codegraph`, `tavily`, `context-mode`, `playwright`, `mcp-atlassian`, `figma`), validar o funcionamento de todos os 6 servidores MCP no ambiente local e criar o template genérico `.config/vscode_mcp.json` livre de caminhos absolutos de máquina/usuário e segredos literais (R-010, R-038, R-044).

| Parâmetro de Correlação | Valor |
| :--- | :--- |
| **Workflow ID** | `WORKFLOW-GOVERNANCE-MAINTENANCE` |
| **Workflow Trace ID** | `wt-20261116-vscode-mcp-01` |
| **Session ID** | `e0fbf32b-34fc-47af-b026-b703d0eb6dd2` |
| **Autor Intelectual** | `@agent-auditor` |
| **Materializador Físico (Etapa 2)** | `@docs-engineer` (R-064) |
| **Executor Declarativo (Etapa 5)** | `@governance-maintainer` (pós-Gate HITL) |
| **Status Inicial** | `DRAFT` (`approved: false`) |

| ID | Severidade | Smells / Regras Mapeadas | Artefato(s) Afetado(s) | Diagnóstico Verificado | Solução Prescrita |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F-01** | **HIGH** | `Smell 2.12` (Drift de Configuração) / `R-008` / `R-056` | `.vscode/mcp.json` (L1–26) | Drift de configuração entre IDEs (`Smell 2.12`): `.vscode/mcp.json` utiliza invocação legada v1 do `context-mode` (`npx -y context-mode` sem `server --agent copilot-cli` e com `CONTEXT_MODE_IDLE_TIMEOUT_MS: "0"` em vez de `CONTEXT_MODE_DATA_DIR`), impedindo a subida do servidor v2.1.10 no VS Code, além de omitir 4 dos 6 servidores homologados (`tavily`, `playwright`, `mcp-atlassian`, `figma`). | Atualizar `.vscode/mcp.json` com os 6 servidores de `.config/idea_mcp.json`, migrando `context-mode` para `["/c", "npx", "-y", "context-mode", "server", "--agent", "copilot-cli"]` (flag v2 verificada em `docs/context/setup-context-mode-intellij.md` L49 e `tests/governance_audit/test_context_mode_v2_tool_names.py` L116) com `CONTEXT_MODE_DATA_DIR: "${userHome}/.config/vscode/context-mode"` e `type: "stdio"`. |
| **F-02** | **HIGH** | `R-010` / `R-038` / `R-044` / `OWASP A02` | `.config/vscode_mcp.json` (novo arquivo) | Ausência de template versionado `.config/vscode_mcp.json` para usuários de VS Code; risco de violação R-044 (regex de caminhos absolutos de drive/usuário em `.githooks/pre-commit`) e risco de segurança OWASP A02 caso `NODE_TLS_REJECT_UNAUTHORIZED: "0"` ou caminhos fixos do `.config/idea_mcp.json` sejam propagados ao template genérico. | Criar `.config/vscode_mcp.json` utilizando variáveis portáteis nativas do VS Code (`${workspaceFolder}` e `${userHome}`) e placeholders padronizados em inglês (`your_tavily_api_key`, `https://your-company.atlassian.net`, `your.email@company.com`, `your_api_token`, `your_figma_access_token`, `${userHome}/certs/corporate-ca.pem`), removendo `NODE_TLS_REJECT_UNAUTHORIZED: "0"`, `disabled` e `timeout`. |
| **F-03** | **MEDIUM** | `R-016` / `R-023` | `.vscode/mcp.json` | Necessidade de evidência empírica e reproduzível de que os 6 servidores MCP inicializam e respondem ao protocolo MCP (`initialize` JSON-RPC 2.0 via `stdio`) antes de consolidar `.config/vscode_mcp.json`. | Executar bateria efêmera de smoke test determinístico via protocolo JSON-RPC 2.0 (`initialize`) e verificação de binários (`codegraph`, `npx`, `uvx`) para cada um dos 6 servidores configurados, sem persistir scripts `.py` no repositório. |

---

## 2. Artefatos Afetados e allowed_files

| # | Arquivo Declarativo (`allowed_files`) | Linhas Atuais em Disco | Operação | Papel no Plano |
| :- | :--- | :--- | :--- | :--- |
| 1 | `.vscode/mcp.json` | **26 linhas** (local, ignorado por `.gitignore` na linha 3 `.vscode/`) | Atualização | Configuração local de runtime dos 6 servidores MCP no VS Code |
| 2 | `.config/vscode_mcp.json` | **0 linhas** (novo arquivo em `.config/`) | Criação | Template genérico e portátil para usuários do VS Code (par de `.config/idea_mcp.json` de 79 linhas) |
| 3 | `docs/plans/governance/20261116-120000-vscode-mcp-config-sync.md` | **Novo arquivo** | Criação | Registro formal de planejamento R-064 |

- **Conformidade C10 / R-043 / R-044**: Nenhum arquivo de `allowed_files` contém o infixo reservado de isolamento local (R-043) e nenhum caminho absoluto de máquina/usuário será gravado em `.config/vscode_mcp.json` ou neste plano (R-044).

---

## 3. Plano de Correção em Lote (Plan-Then-Batch)

0. **Passo 0 — Snapshot de Backup Local Pré-Mutação (`.vscode/mcp.json` → `tmp/mcp.json.bak`)**:
   - Como `.vscode/` está no `.gitignore` (linha 3) e não possui histórico rastreado pelo Git, copiar as 26 linhas atuais de `.vscode/mcp.json` para `tmp/mcp.json.bak` (diretório `tmp/` ignorado na linha 9 do `.gitignore`), garantindo restauração determinística caso o rollback seja acionado.
1. **Passo 1 — Atualização de `.vscode/mcp.json` com os 6 Servidores MCP**:
   - Configurar a chave raiz `"servers"` com `"type": "stdio"` para todos os 6 servidores baseados em `.config/idea_mcp.json`, usando placeholders padronizados:
     - `codegraph`: `type: "stdio"`, `command: "cmd.exe"`, `args: ["/c", "codegraph", "mcp", "--multi-repo", "--db", "${workspaceFolder}/.codegraph/graph.db"]`.
     - `tavily`: `type: "stdio"`, `command: "cmd.exe"`, `args: ["/c", "npx", "-y", "tavily-mcp@latest"]`, `env: { "TAVILY_API_KEY": "your_tavily_api_key" }` (sem `NODE_TLS_REJECT_UNAUTHORIZED: "0"` por conformidade R-010 / OWASP A02).
     - `context-mode`: `type: "stdio"`, `command: "cmd.exe"`, `args: ["/c", "npx", "-y", "context-mode", "server", "--agent", "copilot-cli"]`, `env: { "CONTEXT_MODE_DATA_DIR": "${userHome}/.config/vscode/context-mode" }`.
     - `playwright`: `type: "stdio"`, `command: "cmd.exe"`, `args: ["/c", "npx", "-y", "@playwright/mcp@0.0.83", "--isolated", "--storage-state=playwright/.auth/user.json", "--output-dir=.playwright-mcp"]`, `env: {}`.
     - `mcp-atlassian`: `type: "stdio"`, `command: "uvx"`, `args: ["-q", "mcp-atlassian"]`, `env: { "JIRA_URL": "https://your-company.atlassian.net", "JIRA_USERNAME": "your.email@company.com", "JIRA_API_TOKEN": "your_api_token", "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki", "CONFLUENCE_USERNAME": "your.email@company.com", "CONFLUENCE_API_TOKEN": "your_api_token" }`.
     - `figma`: `type: "stdio"`, `command: "uvx"`, `args: ["-q", "--offline", "--with", "mcp==1.30.0", "mcp-figma==0.0.2"]`, `env: { "FIGMA_ACCESS_TOKEN": "your_figma_access_token", "SSL_CERT_FILE": "${userHome}/certs/corporate-ca.pem" }`.
2. **Passo 2 — Validação Funcional Real dos 6 Servidores MCP (Critério Objetivo de Aprovação e Tratamento de Falha)**:
   - Executar verificação efêmera em memória (sem criar nem persistir arquivos `.py` no repositório, respeitando R-055/R-057) que testa cada um dos 6 servidores configurados em `.vscode/mcp.json`:
     - **Pré-aquecimento do cache `uvx` para `figma`**: Como `figma` utiliza `--offline`, caso o pacote `mcp-figma==0.0.2` com `mcp==1.30.0` ainda não esteja no cache local do `uv`, executar previamente `uv tool run --with mcp==1.30.0 mcp-figma==0.0.2 --help` (sem `--offline`) para popular o cache local do `uv`, validando em seguida a invocação exata com `--offline`.
     - **Critério de Aprovação por Servidor (Handshake JSON-RPC 2.0 `initialize`)**: Enviar pela `stdin` de cada processo a requisição `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"vscode-mcp-validator","version":"1.0.0"}}}` (injetando valores sintáticos de placeholder não-vazios nas variáveis de ambiente de autenticação e omitindo `SSL_CERT_FILE` inexistente durante o smoke test de processo). O servidor é considerado **100% APROVADO** quando inicia o processo stdio e responde na `stdout` com envelope JSON-RPC 2.0 contendo `"id": 1` e `"result"` (`protocolVersion`, `capabilities`, `serverInfo`).
     - **Fluxo de Contingência em Caso de Falha**: Se qualquer servidor falhar no handshake `initialize` após 1 retry com ajuste de argumentos/cache (Circuit Breaker R-022), a criação de `.config/vscode_mcp.json` no Passo 3 é bloqueada, a falha é reportada em formato Compact Error Reporting (R-020) e o rollback do Passo 0 é disponibilizado.
3. **Passo 3 — Criação do Template Genérico `.config/vscode_mcp.json` e Auditoria de Conformidade**:
   - Confirmado o handshake JSON-RPC 2.0 de 100% dos 6 servidores no Passo 2, gravar `.config/vscode_mcp.json` com a estrutura validada e variáveis portáteis (`${workspaceFolder}`, `${userHome}`), zero segredos reais (R-010), zero `NODE_TLS_REJECT_UNAUTHORIZED: "0"` (OWASP A02) e zero caminhos absolutos de drive/usuário (R-044).
   - Executar `pytest tests/governance_audit/ -q`, `python -m tools.governance_sync --check` (R-015/R-033) e verificação da regex R-044 do `.githooks/pre-commit`.

---

## 4. Alternativas Rejeitadas

| # | Alternativa Considerada | Motivo Técnico da Rejeição |
| :--- | :--- | :--- |
| **1** | **Copiar literalmente os caminhos e `NODE_TLS_REJECT_UNAUTHORIZED: "0"` de `.config/idea_mcp.json` para `.config/vscode_mcp.json`** | Rejeitada porque `.config/idea_mcp.json` contém caminhos com prefixo de drive e pasta de usuário que acionam o bloqueio `[R-044]` do `.githooks/pre-commit`, além de `NODE_TLS_REJECT_UNAUTHORIZED: "0"` desabilitar a verificação TLS (OWASP A02 / R-010). No VS Code, `${workspaceFolder}` e `${userHome}` resolvem caminhos de forma nativa e portátil. |
| **2** | **Manter `npx -y context-mode` sem `server --agent copilot-cli` em `.vscode/mcp.json`** | Rejeitada porque o `context-mode` v2.1.10 exige o subcomando `server --agent copilot-cli` e `CONTEXT_MODE_DATA_DIR` (conforme documentado em `docs/context/setup-context-mode-intellij.md` L49 e exigido por `tests/governance_audit/test_context_mode_v2_tool_names.py` L105–136). |

---

## 5. Reúso Sistêmico (R-055: Q1/Q2/Q3) e Sensores tests/governance_audit/

| Questão R-055 | Resposta Verificada com Evidência Empírica |
| :--- | :--- |
| **Q1 — Quais artefatos irmãos (peers) no repositório possuem o mesmo padrão e foram varridos?** | Foram inspecionados os 2 arquivos irmãos em `.config/`: `.config/idea_mcp.json` (79 linhas, 6 servidores) e `.config/cline_mcp_settings.json` (48 linhas, 3 servidores), além de `.vscode/mcp.json` (26 linhas, 2 servidores). |
| **Q2 — Quais templates, schemas ou contratos canônicos foram atualizados para impedir reincidência?** | `.config/vscode_mcp.json` é introduzido como o template canônico versionado de configuração MCP para o VS Code, paritário aos 6 servidores de `.config/idea_mcp.json`, com placeholders padronizados em inglês, sem `NODE_TLS_REJECT_UNAUTHORIZED: "0"`, e compatível com os contratos de versão fixa (`@playwright/mcp@0.0.83`, `mcp-figma==0.0.2`) e `context-mode` v2 (`--agent copilot-cli`). |
| **Q3 — Qual verificação automatizada garante que a regressão não retorne?** | Inspecionados `tests/governance_audit/test_context_mode_v2_tool_names.py` (L105–136, que varre `.config/idea_mcp.json` e `.config/cline_mcp_settings.json`) e `tests/governance_audit/test_playwright_mcp_frontend_governance.py` (L167–179, que varre `.config/idea_mcp.json`). `.config/vscode_mcp.json` é construído atendendo 100% às mesmas invariantes (`--agent copilot-cli`, `CONTEXT_MODE_DATA_DIR`, ausência de variáveis v1 legadas e `@playwright/mcp@0.0.83` pinado). A eventual inclusão de `.config/vscode_mcp.json` na lista de arquivos de `test_context_mode_v2_tool_names.py` (arquivo `.py` sob governança exclusiva do `@python-router` conforme R-055/R-065) fica registrada como evolução opcional de Grupo B caso desejado pelo usuário, sem bloquear a entrega declarativa em `.config/` e `.vscode/`. |

---

## 6. Rollback e Critério de Pronto

- **Rollback**: Restaurar `.vscode/mcp.json` a partir do snapshot salvo no Passo 0 (`tmp/mcp.json.bak`) e remover `.config/vscode_mcp.json` (mais limpeza de `tmp/mcp.json.bak` após confirmação).
- **Critério de Pronto (DoD)**:
  - [ ] Backup prévio de `.vscode/mcp.json` salvo em `tmp/mcp.json.bak` (Passo 0).
  - [ ] `.vscode/mcp.json` configurado com os 6 servidores MCP (`codegraph`, `tavily`, `context-mode`, `playwright`, `mcp-atlassian`, `figma`) no schema nativo do VS Code (`type: "stdio"`).
  - [ ] Todos os 6 servidores validados com evidência real de resposta JSON-RPC 2.0 `initialize` (`result.serverInfo` / `result.capabilities`).
  - [ ] `.config/vscode_mcp.json` criado em `.config/` de forma 100% genérica (zero caminhos absolutos R-044, zero segredos R-010, zero `NODE_TLS_REJECT_UNAUTHORIZED: "0"`).
  - [ ] `pytest tests/governance_audit/ -q` e `python -m tools.governance_sync --check` aprovados com 100% de sucesso.
