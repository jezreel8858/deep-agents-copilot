# Agent Execution Protocol Sync (R-059 / R-060 / R-051)

> Ferramenta determinística para sincronização atômica do bloco `<execution_protocol>` em todos os agentes executores e prompts elegíveis do ecossistema a partir de uma fonte canônica única.

---

## 1) 🎯 Objetivo e Motivação

O protocolo **Plan-Then-Batch (R-059)** combinado com o **Teto Rígido de Tool Turns / Warm Start (R-060)** estabelece as diretrizes normativas para prevenir desperdício de tokens, loops investigativos $O(N^2)$ e corrupção de arquivos estruturados (R-051).

Anteriormente, essa seção estava replicada manualmente em 77 arquivos `.agent.md` e nos prompts `.github/prompts/*.prompt.md`. Edições manuais ou regex ad-hoc em lote causavam corrupção de caracteres de controle e drift entre agentes. Este script formaliza a arquitetura **Single Canonical Source**:
- **Fonte Canônica Única:** `tools/agent_protocol_sync/_execution-protocol-fragment.md`
- **Mapeamento de Papéis:** `tools/agent_protocol_sync/protocol_roles.json` (`STANDARD` vs `CUSTOM`)
- **Gates Automatizados:** CI fail-hard no GitHub Actions bloqueando drifts antes do merge.

---

## 2) 🔍 Elegibilidade Primária por Tools (`is_ctx_eligible`)

A injeção do bloco `<execution_protocol>` segue o princípio de **eliminação de instrução morta**: o protocolo descreve o uso de ferramentas MCP (`ctx_execute`, `ctx_batch_execute`, `ctx_search`, etc.), portanto sua presença só faz sentido em artefatos que efetivamente possuem essas ferramentas declaradas.

- **Helper `is_ctx_eligible(tools: list[str]) -> bool`**: Retorna `True` se qualquer item da lista `tools` começar com `"context-mode/ctx_"`.
- **Regra Primária Mandatória**: Só agents e prompts com ferramentas `context-mode/ctx_*` em `tools:` recebem o bloco `<execution_protocol>`. Arquivos SEM `ctx_*` em `tools:` **NUNCA** recebem o bloco, independentemente de papéis ou configurações.
- **Relação com `protocol_roles.json` (Overrides Especiais)**:
  - Para prompts: a elegibilidade por `tools:` é suficiente (não há papéis). Prompts elegíveis recebem o bloco STANDARD; não-elegíveis têm qualquer bloco residual removido (ex.: `del-project-context.prompt.md` e `health.prompt.md`).
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
- `STANDARD`: Agentes executores que recebem integralmente o bloco canônico padrão delimitado por `<!-- BEGIN:STANDARD -->` (desde que elegíveis por `tools:`).
- `CUSTOM`: Agentes com particularidades essenciais de execução (ex.: `codegraph-engine`). Nesses, o script apenas valida a presença da marca normativa `R-060` sem sobrescrever o conteúdo customizado.

---

## 5) 🔒 Segurança e Idempotência (Invariantes)

- **Idempotência Estrita:** Execuções sucessivas de `--apply` produzem 0 atualizações na segunda rodada.
- **Diff Cirúrgico:** Substitui estritamente a tag `<execution_protocol>...</execution_protocol>` ou a remove de arquivos não-elegíveis sem alterar frontmatter, personas ou seções adjacentes.
- **Suíte de Testes:** `tests/governance_audit/test_sync_execution_protocol_invariants.py`.
