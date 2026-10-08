# Agent Execution Protocol Sync (R-059 / R-060 / R-051 / R-042 / R-066)

> Ferramenta determinística para sincronização atômica do bloco `<execution_protocol>` com cabeçalho H2 CommonMark (`## ⚙️ Protocolo de Execução Obrigatório`) em todos os agentes executores e prompts elegíveis do ecossistema a partir de uma fonte canônica única, utilizando **Composição Dinâmica por Capabilities**.

---

## 1) 🎯 Objetivo e Arquitetura de Composição Dinâmica

O protocolo **Plan-Then-Batch (R-059)** combinado com o **Teto Rígido de Tool Turns / Warm Start (R-060)** estabelece as diretrizes normativas para prevenir desperdício de tokens, loops investigativos $O(N^2)$ e corrupção de arquivos estruturados (R-051).

Com a **Composição Dinâmica por Capabilities**, o protocolo elimina ruído, repetições ("Smell 2.x") e instruções mortas:
- **Núcleo Comum Imperativo (CORE):** Redação enxuta e obrigatória cobrindo:
  1. `ENUMERAR`: Mapeamento interno prévio de arquivos e comandos.
  2. `CONSOLIDAR (Limiar >= 2)`: Uso compulsório de `ctx_batch_execute` ou script iterativo no sandbox.
  3. `Comandos curtos não suspendem a regra`: Respeito estrito ao limiar mesmo em comandos breves.
  4. `Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)`: Orçamento estrito com parada no 4º turno.
  5. `Warm Start Compulsório & Batch Querying (R-060)`: Inicialização silenciosa de índices locais e batch query.
- **Cláusulas Condicionais por Capabilities:** Inspecionadas no frontmatter YAML:
  * **Validação Agrupada com `get_errors` (R-051):** Injetada apenas se o artefato declarar ferramentas de mutação/edição (`replace_string_in_file`, `create_file`, `insert_edit_into_file`, `get_errors`) ou for executor com sandbox de execução (`ctx_execute`, `ctx_execute_file`).
  * **Telemetria de Handoff (R-042):** Injetada apenas se `run_subagent` estiver na lista de `tools:`.
  * **Progressive Disclosure (R-066):** Injetada apenas se `source_docs_lazy:` estiver declarado.

---

## 2) 🔍 Elegibilidade Primária por Tools (`is_ctx_eligible`)

A injeção do bloco `<execution_protocol>` segue o princípio de **eliminação de instrução morta**: o protocolo descreve o uso de ferramentas MCP (`ctx_execute`, `ctx_batch_execute`, `ctx_search`, etc.), portanto sua presença só faz sentido em artefatos que efetivamente possuem essas ferramentas declaradas.

- **Helper `is_ctx_eligible(tools: list[str]) -> bool`**: Retorna `True` se qualquer item da lista `tools` começar com `"context-mode/ctx_"`.
- **Regra Primária Mandatória**: Só agents e prompts com ferramentas `context-mode/ctx_*` em `tools:` recebem o bloco `<execution_protocol>`. Arquivos SEM `ctx_*` em `tools:` **NUNCA** recebem o bloco, independentemente de papéis ou configurações.
- **Relação com `protocol_roles.json` (Overrides Especiais)**:
  - Para prompts: a elegibilidade por `tools:` é suficiente (não há papéis). Prompts elegíveis recebem o bloco composto por capabilities; não-elegíveis têm qualquer bloco residual removido (ex.: `del-project-context.prompt.md` e `health.prompt.md`).
  - Para agents: a função `is_ctx_eligible()` atua como filtro primário. Um agente só recebe o bloco se for elegível por `tools:` **E** não estiver com override de exclusão em `protocol_roles.json` (ex.: routers como `agent-router`, `database-router` continuam excluídos mesmo declarando `ctx_search`, pois seu papel é puramente de roteamento e triagem).

---

## 3) 🛠️ Modos de Operação (CLI)

O script adota o contrato de guard-rails de governança:

| Comando | Comportamento | Efeito Colateral | Uso Típico |
| :--- | :--- | :--- | :--- |
| `python tools/agent_protocol_sync/sync_execution_protocol.py --check` | **Fail-Safe CI**: exit code 1 se houver drift | Nenhum (read-only) | Pull Requests & CI Gates |
| `python tools/agent_protocol_sync/sync_execution_protocol.py` | **Dry-Run**: exibe agentes e prompts com drift | Nenhum (read-only) | Inspeção local prévia |
| `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` | **Mutating**: aplica correções e remove blocos de não-elegíveis | Grava arquivos `.agent.md` e `*.prompt.md` | Manutenção transversal / batch updates |

---

## 4) 🧩 Mapeamento de Papéis (Roles)

Em `protocol_roles.json`:
- `STANDARD`: Agentes executores que recebem o bloco canônico composto dinamicamente de acordo com suas capabilities (desde que elegíveis por `tools:`).
- `CUSTOM`: Agentes com particularidades essenciais de execução (ex.: `codegraph-engine`). Nesses, o script apenas valida a presença da marca normativa `R-060` sem sobrescrever o conteúdo customizado.

---

## 5) 🔒 Segurança e Idempotência (Invariantes)

- **Idempotência Estrita:** Execuções sucessivas de `--apply` produzem 0 atualizações na segunda rodada.
- **Diff Cirúrgico:** Substitui estritamente o bloco com cabeçalho `## ⚙️ Protocolo de Execução Obrigatório` e `<execution_protocol>...</execution_protocol>` ou a remove de arquivos não-elegíveis sem alterar frontmatter, personas ou seções adjacentes.
- **Suíte de Testes:** `tests/governance_audit/test_sync_execution_protocol_invariants.py`.
