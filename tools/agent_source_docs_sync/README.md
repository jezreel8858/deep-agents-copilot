# Agent Required Source Docs Sync (R-042 / R-046 / R-051)

> Sincronização determinística e atômica de referências contratuais obrigatórias no frontmatter (`source_docs:`) de agentes (.agent.md) com base em regras canônicas declarativas.

---

## 1) 🎯 Objetivo e Motivação

Agentes executores e especialistas que declaram capacidade de sub-delegação (`tools: ['run_subagent', ...]`) possuem a obrigação normativa de referenciar formalmente as diretrizes de governança em seu frontmatter (`source_docs:`):
- **`.github/skills/handoff-governance/SKILL.md`**: Protocolo de emissão obrigatória de telemetria de handoff (`[HANDOFF]`, `session_id`, `sequence_index`, `call_stack_depth`, R-042).
- **`.github/skills/agent-contracts/SKILL.md`**: Contratos de orquestração, regras de delegação plana (*Flat Delegation*) e ciclo de vida do agente (§ 0.3).

Anteriormente, tais adições eram realizadas via edições de LLM ad-hoc ou verificadas por checagens frágeis de regex de texto livre em testes. Esta ferramenta substitui esse modelo por uma **Single Canonical Source declarativa** com verificação semântica YAML e atualização cirúrgica idempotente.

---

## 2) 🛠️ Modos de Operação (CLI)

O script adota o contrato padronizado de governança via `tools/governance_sync/core.py`:

| Modo | Comando | Comportamento | Exit Code |
| :--- | :--- | :--- | :---: |
| **Check (Default / CI)** | `python tools/agent_source_docs_sync/sync_required_source_docs.py --check` | Varre todos os agentes e reporta drift sem modificar nenhum arquivo. | `1` se houver drift/erro, `0` se limpo |
| **Dry-Run** | `python tools/agent_source_docs_sync/sync_required_source_docs.py --dry-run` | Simula a inserção cirúrgica e exibe o diff unificado no terminal. | `0` se sem erros |
| **Apply** | `python tools/agent_source_docs_sync/sync_required_source_docs.py --apply` | Insere cirurgicamente os itens faltantes nos arquivos em disco com validação R-051. | `0` se gravado com sucesso |

---

## 3) 📋 Regras Declarativas e Schema (`required_source_docs_rules.json`)

As regras são declaradas no arquivo `tools/agent_source_docs_sync/required_source_docs_rules.json`, permitindo estender facilmente novos predicados sem alterar o código do script:

```json
{
  "rules": [
    {
      "id": "run_subagent_requires_handoff_and_contracts",
      "description": "Agents com run_subagent devem referenciar handoff-governance e agent-contracts",
      "condition": {
        "tools_contains": "run_subagent"
      },
      "exclude_files": [
        "agent-router.agent.md"
      ],
      "required_source_docs": [
        ".github/skills/handoff-governance/SKILL.md",
        ".github/skills/agent-contracts/SKILL.md"
      ]
    }
  ]
}
```

---

## 4) 🛡️ Segurança, Idempotência e R-051

- **YAML-Aware & Cirúrgico**: Utiliza `yaml.safe_load` para compreensão estrutural das listas `tools:` e `source_docs:`, mas realiza a inserção textual cirúrgica diretamente no bloco `source_docs:`, preservando intactos todos os comentários, formatação de aspas, blocos multiline e ordem existente.
- **Append Estrito**: Nunca remove nem reordena documentos já declarados no agente; apenas anexa os itens faltantes ao final da lista existente.
- **R-051 (Double-Check Pós-Escrita)**: Em modo `--apply`, cada arquivo alterado é imediatamente relido do disco e submetido a uma nova rodada de parsing YAML e asserção de paridade de campos antes de ser computado como sucesso.
- **Idempotência**: Executar `--apply` sucessivas vezes garante 0 modificações e 0 drift a partir da segunda execução.

---

## 5) 🔗 Integração CI & Testes

- **CI Gate**: Integrado compulsoriamente em `.github/workflows/routing-quality-gate.yml` como gate mecânico antes da suíte pytest.
- **Suíte de Testes**:
  - `tests/governance_audit/test_sync_required_source_docs_invariants.py`: Valida drift zero e idempotência estrita de `--apply`.
  - `tests/governance_audit/test_telemetry_emission_governance.py`: Valida contratualmente que 100% dos agentes atendem à conformidade de telemetria sem falso-positivos de regex.
