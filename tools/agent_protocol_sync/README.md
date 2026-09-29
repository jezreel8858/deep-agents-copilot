# Agent Execution Protocol Sync (R-059 / R-060 / R-051)

> Ferramenta determinística para sincronização atômica do bloco `<execution_protocol>` em todos os agentes executores do ecossistema a partir de uma fonte canônica única.

---

## 1) 🎯 Objetivo e Motivação

O protocolo **Plan-Then-Batch (R-059)** combinado com o **Teto Rígido de Tool Turns / Warm Start (R-060)** estabelece as diretrizes normativas para prevenir desperdício de tokens, loops investigativos $O(N^2)$ e corrupção de arquivos estruturados (R-051).

Anteriormente, essa seção estava replicada manualmente em 77 arquivos `.agent.md`. Edições manuais ou regex ad-hoc em lote causavam corrupção de caracteres de controle e drift entre agentes. Este script formaliza a arquitetura **Single Canonical Source**:
- **Fonte Canônica Única:** `tools/agent_protocol_sync/_execution-protocol-fragment.md`
- **Mapeamento de Papéis:** `tools/agent_protocol_sync/protocol_roles.json` (`STANDARD` vs `CUSTOM`)
- **Gates Automatizados:** CI fail-hard no GitHub Actions bloqueando drifts antes do merge.

---

## 2) 🛠️ Modos de Operação (CLI)

O script adota o contrato de guard-rails de governança:

| Comando | Comportamento | Efeito Colateral | Uso Típico |
| :--- | :--- | :--- | :--- |
| `python tools/agent_protocol_sync/sync_execution_protocol.py --check` | **Fail-Safe CI**: exit code 1 se houver drift | Nenhum (read-only) | Pull Requests & CI Gates |
| `python tools/agent_protocol_sync/sync_execution_protocol.py` | **Dry-Run**: exibe agentes com drift e instrução | Nenhum (read-only) | Inspeção local prévia |
| `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` | **Mutating**: aplica o bloco canônico nos arquivos | Grava arquivos `.agent.md` | Manutenção transversal / batch updates |

---

## 3) 🧩 Mapeamento de Papéis (Roles)

Em `protocol_roles.json`:
- `STANDARD`: Agentes que recebem integralmente o bloco canônico padrão delimitado por `<!-- BEGIN:STANDARD -->`.
- `CUSTOM`: Agentes com particularidades essenciais de execução (ex.: `code-knowledge-graph`). Nesses, o script apenas valida a presença da marca normativa `R-060` sem sobrescrever o conteúdo customizado.

---

## 4) 🔒 Segurança e Idempotência (Invariantes)

- **Idempotência Estrita:** Execuções sucessivas de `--apply` produzem 0 atualizações na segunda rodada.
- **Diff Cirúrgico:** Substitui estritamente a tag `<execution_protocol>...</execution_protocol>` sem alterar frontmatter, personas ou seções adjacentes.
- **Suíte de Testes:** `tests/governance_audit/test_sync_execution_protocol_invariants.py`.
