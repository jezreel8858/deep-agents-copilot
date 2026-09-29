# A2A AgentCard Exporter & Governance Validator (v1.0.0)

> Exportador e validador determinístico do ecossistema de agentes para o padrão aberto **A2A AgentCard** (Linux Foundation v1.0.0 / IETF draft-aevum-agentcard-00).

---

## 1) 🎯 Objetivo e Escopo

O `export_agentcards.py` converte e sincroniza as definições de catálogo (`catalog.yaml`) do repositório para cartões de capacidade e segurança legíveis por máquinas em `.a2a/agentcards/*.agentcard.json` e o índice consolidado `agentcards.index.json`.

### Principais Capacidades:
- **Taxonomia Canônica de Roles (A2A):** Mapeia agentes em `router`, `advisor`, `implementer`, `fixer`, `tester`, `auditor`, `planner`, `researcher`, `gatekeeper`, `specialist`.
- **Perfis de Segurança NSA CSI MCP:** Define dinamicamente zonas de ferramentas (`read-only`, `mutating`, `execution`) e nível de menor privilégio (`strict`, `standard`, `elevated`). Agentes puramente consultivos nunca recebem permissão mutating.
- **Validação Estrita de Schema:** Todo card gerado é compulsoriamente validado contra `docs/schemas/agentcard.schema.json`.

---

## 2) 🛠️ Modos de Operação (CLI)

O utilitário adota o padrão triplo de segurança operacional:

```bash
# 1. Modo Check (default fail-safe / CI)
python tools/agentcard_exporter/export_agentcards.py --check
# ou simplesmente:
python tools/agentcard_exporter/export_agentcards.py

# 2. Modo Dry-Run (visualização de diffs)
python tools/agentcard_exporter/export_agentcards.py --dry-run

# 3. Modo Apply (geração e sincronização física)
python tools/agentcard_exporter/export_agentcards.py --apply
```

### Contrato de Retorno:
- `0`: Sucesso, sem drift (ou gravação bem-sucedida em `--apply`).
- `1`: Drift detectado (cards ausentes ou desatualizados em relação aos catálogos) ou violação de validação contra o schema JSON.

---

## 3) 🛡️ Integração CI & Testes

- **CI Gate:** Integrado no workflow `.github/workflows/routing-quality-gate.yml` como etapa bloqueante antes da suíte pytest.
- **Suíte de Testes:**
  - `tests/governance_audit/test_a2a_agentcards_parity.py`: Garante paridade de 100% entre `.agent.md` e os arquivos `.agentcard.json`.
  - `tests/governance_audit/test_a2a_agentcard_compliance.py`: Valida schema, perfis de menor privilégio e comportamento CLI `--check` / `--dry-run`.
