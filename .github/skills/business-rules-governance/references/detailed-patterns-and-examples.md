# Business Rules Governance — Templates e Relatórios Detalhados

## 2) Template Canônico de Documento de Regras

Cada arquivo de regras de negócio segue a estrutura abaixo. Nome: `business-rules-<modulo>.md` em `docs/business-rules/`.

```markdown
---
module: <nome-do-modulo>
version: 1.0.0
last_updated: YYYY-MM-DD
status: active | draft | deprecated
source_files:
  - src/path/to/file.ext
---

# Regras de Negócio — <Nome do Módulo>

> Documento gerado por `@business-rules-extractor`. Atualizar sempre que a lógica de negócio mudar.
> Ground truth para validação de refatorações via `@business-rules-extractor` em modo validate.

## Sumário de Regras

| ID | Categoria | Nome | Status |
|---|---|---|---|
| BR-001 | VAL | [Nome da Regra] | active |
| BR-002 | CALC | [Nome da Regra] | active |

---

## BR-001 — [Nome da Regra]

**Categoria:** VAL — Validação  
**Status:** active  
**Arquivo:** `src/modulo/Arquivo.ext:42`  
**Símbolo:** `NomeDaClasseOuMetodo`

### Descrição
[Descrição em linguagem de negócio — o que a regra garante e por quê existe]

### Lógica Implementada
[Descrição precisa do que o código faz — condições, valores, casos]

### Condições e Edge Cases
- **Condição principal:** [quando a regra se aplica]
- **Edge case 1:** [comportamento em caso especial 1]
- **Edge case 2:** [comportamento em caso especial 2]
- **Valor padrão:** [o que acontece quando nenhuma condição é atendida]

### Dependências
- Depende de: [outra regra ou serviço]
- Impacta: [o que é afetado por esta regra]

### Exemplos
| Entrada | Resultado esperado |
|---|---|
| [caso 1] | [resultado 1] |
| [caso 2] | [resultado 2] |

### Histórico
- `YYYY-MM-DD`: [o que mudou]
```

---
