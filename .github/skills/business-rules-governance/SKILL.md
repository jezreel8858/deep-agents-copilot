---
name: business-rules-governance
description: >
  Taxonomia, templates e padrões para extração, documentação e validação de
  regras de negócio a partir de código-fonte em qualquer linguagem. Define
  o formato markdown canônico para que regras sejam consumíveis por AI Copilot
  como ground truth na validação de refatorações.
tier: 1
category: documentation
triggers:
  - "extrair regras de negócio"
  - "documentar regra"
  - "business rule"
  - "regra de negócio"
  - "validar refatoração"
  - "documentar lógica"
  - "catalogar regras"
  - "rule violation"
  - "breaking change"
  - "regra quebrada"
  - "documentação de código"
tools:
  - "read_file"
  - "grep_search"
  - "file_search"
  - "create_file"
  - "insert_edit_into_file"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
---

# Business Rules Governance

Padrões para extração, documentação e validação de regras de negócio a partir de qualquer código-fonte. O objetivo central é transformar lógica implícita no código em regras explícitas e rastreáveis — servindo como **ground truth** para validar refatorações e evitar regressões silenciosas.

> **Aplica-se a**: `@business-rules-extractor`, `@refactor-planner`, `@tech-solution-architect`, `@docs-engineer` e qualquer agent que precise rastrear ou validar comportamento de negócio.

---

## 1) Taxonomia de Regras de Negócio

| Categoria | Código | O que inclui | Exemplos |
|---|---|---|---|
| **Validação** | `VAL` | Checagem de entrada, integridade de dados, constraints | CPF válido, campo obrigatório, formato de email |
| **Cálculo** | `CALC` | Operações matemáticas de negócio, fórmulas, derivações | Desconto por volume, juros compostos, score de crédito |
| **Autorização** | `AUTH` | Controle de acesso, papéis, permissões, políticas | Admin pode excluir, usuário só vê seus dados |
| **Fluxo/Estado** | `FLOW` | Máquinas de estado, transições, ordens de operação | Pedido: rascunho → aprovado → enviado → entregue |
| **Restrição** | `CSTR` | Limites, thresholds, regras de negócio absolutas | Máximo 3 tentativas de login, prazo de 30 dias |
| **Integração** | `INTG` | Contratos com sistemas externos, protocolos, formatos | Enviar CEP para API de frete, receber em ISO 8601 |
| **Domínio** | `DOM` | Lógica central do domínio, invariantes, conceitos | Produto sem estoque não pode ser vendido |
| **Auditoria** | `AUD` | O que deve ser logado, rastreado ou historizado | Alterar preço gera registro de auditoria |

---

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

## 3) ID de Regra — Convenção

```
BR-<NNN>
│    └── Número sequencial por módulo (001, 002, ...)
└── Business Rule (prefixo fixo)
```

- IDs são **imutáveis** — não reutilizar IDs de regras deletadas.
- Regras deprecadas: marcar `status: deprecated` e adicionar nota de substituição.
- Ao deletar uma regra: manter o ID com `status: removed` + data + motivo.

---

## 4) Extração por Tipo de Código

### Indicadores de Regra de Negócio no Código

| Padrão no código | Categoria provável | O que capturar |
|---|---|---|
| `if/else`, `switch` com condições de negócio | VAL, FLOW, CSTR | Todas as branches e seus significados |
| Cálculos aritméticos com variáveis de negócio | CALC | Fórmula, operandos, resultado |
| Anotações `@Valid`, `@NotNull`, `@Size`, `@Pattern` | VAL | Constraint e campo alvo |
| Listas de `enum` com estados | FLOW | Todos os estados e transições possíveis |
| Verificações de `role`, `permission`, `hasAccess` | AUTH | Quem pode e quem não pode |
| Constantes de limite (`MAX_`, `MIN_`, `LIMIT_`) | CSTR | Valor e contexto de aplicação |
| Chamadas a APIs externas com payloads específicos | INTG | Contrato de entrada e saída |
| `@Transactional`, saveHistory, auditLog | AUD | O que é auditado e quando |
| Throws de exceções de negócio | VAL, DOM | Condição e mensagem |

### Padrões por Linguagem

**Java/Spring Boot:**
```bash
grep_search "@Valid\|@NotNull\|@Size\|@Pattern"       # VAL
grep_search "throw new BusinessException"               # VAL/DOM
grep_search "if.*status.*==\|switch.*status"            # FLOW
grep_search "hasRole\|hasPermission\|@PreAuthorize"    # AUTH
grep_search "MAX_\|MIN_\|LIMIT_\|static final"         # CSTR
```

**TypeScript/Angular:**
```bash
grep_search "Validators\.\|required\|minLength\|maxLength"   # VAL
grep_search "if.*role\|this\.authService\|canActivate"       # AUTH
grep_search "enum.*Status\|enum.*State\|enum.*Type"          # FLOW
grep_search "throw new Error\|throwError"                     # VAL/DOM
grep_search "const.*=.*\d+.*;"                               # CSTR (constantes)
```

**Python:**
```bash
grep_search "raise.*Error\|raise.*Exception"            # VAL/DOM
grep_search "if.*role\|if.*permission\|@login_required" # AUTH
grep_search "Enum\|IntEnum"                             # FLOW
grep_search "assert\|validate_"                         # VAL
grep_search "MAX_\|MIN_\|LIMIT_"                        # CSTR
```

---

## 5) Protocolo de Validação (Modo Validate)

Quando usado para validar código novo/refatorado contra regras documentadas:

### Checklist de Validação por Regra

Para cada regra no documento `.md`:

```
1. Localizar a regra no código novo (grep pelo símbolo ou lógica)
2. Comparar comportamento:
   ├─ Condição principal ainda existe? → ✅ Preservada
   ├─ Edge cases ainda cobertos? → ✅ Preservada
   ├─ Comportamento mudou? → ⚠️ Alterada (documentar)
   ├─ Regra removida? → 🔴 Violação (reportar)
   └─ Nova condição adicionada? → 📋 Nova regra detectada
```

### Formato de Relatório de Validação

```markdown
## Relatório de Validação — Refatoração de <Módulo>

**Data:** YYYY-MM-DD
**Arquivo de regras:** `docs/business-rules/business-rules-<modulo>.md`
**Código analisado:** `src/path/to/refactored/`

| ID | Nome | Status | Evidência |
|---|---|---|---|
| BR-001 | Nome da Regra | ✅ Preservada | `arquivo.ext:42` |
| BR-002 | Outra Regra | ⚠️ Alterada | Novo threshold: 10 → 15 em `arquivo.ext:87` |
| BR-003 | Terceira Regra | 🔴 Violação | Condição removida — não encontrada no código novo |
| —  | — | 📋 Nova | Nova validação detectada em `arquivo.ext:120` |

### Violações Detectadas (🔴)
[Detalhar cada violação com arquivo:linha, regra esperada e comportamento encontrado]

### Alterações Detectadas (⚠️)
[Detalhar cada alteração — pode ser intencional ou regressão. Requer confirmação humana]

### Novas Regras Detectadas (📋)
[Listar regras novas encontradas — candidatas a documentar]

**Decisão recomendada:**
- [ ] Aceitar alterações como intencionais e atualizar documentação
- [ ] Reverter violações e preservar regras
- [ ] Documentar novas regras identificadas
```

---

## 6) Living Documentation — Manutenção

- Documento de regras vive em `docs/business-rules/` junto ao código.
- **Atualização obrigatória**: sempre que lógica de negócio mudar, o `.md` deve ser atualizado na mesma entrega.
- **Frontmatter `version`**: incrementar a cada atualização (semver: MAJOR ao mudar regra, MINOR ao adicionar, PATCH ao clarificar).
- **CI check recomendado**: validar que arquivos em `docs/business-rules/` têm `last_updated` ≤ 30 dias para módulos ativos.
- **Traceabilidade obrigatória**: todo ID de regra deve ter `source_files` + `arquivo:linha` no campo símbolo.

---

## 7) Documentação Amigável para AI Copilot

Para que a documentação seja consumida eficientemente pelo Copilot:

- **Frontmatter estruturado**: sempre incluir `module`, `version`, `status`, `source_files`.
- **IDs rastreáveis**: usar `BR-NNN` como identificador estável que pode ser referenciado em outros documentos e prompts.
- **Linguagem de negócio** na descrição, **não** técnica — permite que o Copilot valide intenção, não apenas implementação.
- **Exemplos tabulares**: Copilot consome tabelas melhor que parágrafos para casos de entrada/saída.
- **Seção de edge cases**: os casos especiais são onde regressões ocorrem — documentar explicitamente aumenta a confiança da validação.
- **Status explícito**: `active | draft | deprecated | removed` permite que o Copilot filtre regras relevantes.

---

## 8) Referências

- ArgonDigital — Business Rule Extraction: https://argondigital.com/blog/general/using-ai-for-business-rule-extraction-from-legacy-systems
- LLM-Friendly Docs (Fern, 2026): https://buildwithfern.com/post/how-to-write-llm-friendly-documentation
- Markdown as AI Instruction Layer (VS Magazine, 2026): https://visualstudiomagazine.com/articles/2026/02/24/in-agentic-ai-its-all-about-the-markdown.aspx
- Skill `code-tracing` — para localizar regras no código
- Skill `mermaid-diagrams` — para diagramar fluxos de estado

