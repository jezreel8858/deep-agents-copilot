---
name: 'eval-workflows'
description: 'Avalia a conformidade de trajetórias dos workflows canônicos (R-050) com Gemini 3.8 Flash'
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'get_errors']
argument-hint: '[cenario-id | todos]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/agent-evals-lab/SKILL.md
  - .github/skills/handoff-governance/SKILL.md
---

# `eval-workflows`

> **Propósito**: Executar avaliação controlada de trajetórias e transições de multi-agentes baseada em micro-cenários isolados (1 cenário por turno), prevenindo decaimento de atenção e alucinação.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Este prompt utiliza as variáveis de contexto nativas do VS Code Copilot:
- Arquivo sob análise: `${file}`
- Workspace root: `${workspaceFolder}`
- Argumento opcional: `${input:param}` para especificar o ID do cenário (ex.: `WF-BUG-001`, `WF-REF-001`, `WF-EDGE-INTENT-DRIFT`).

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ NÃO executar avaliação monolítica misturando múltiplos workflows em uma única chamada aberta.
- ❌ NÃO implementar código da aplicação ou modificar arquivos de produção durante o eval.
- ❌ NÃO aprovar trajetórias que violem as regras de menor privilégio de tooling ou omitam o banner obrigatório.
- ✅ Ler a especificação declarativa em `tests/operational_flow/casos-workflows.yaml`.
- ✅ Avaliar um cenário por vez com foco em:
  1. Identificação correta da etapa inicial e do agente roteado;
  2. Preservação do banner universal `Agente Ativo: <name>` e do `Pipeline de Execução`;
  3. Conformidade das transições de handoff (schema v1.3);
  4. Acionamento do Circuit Breaker em caso de falha de regressão repetida.

---

## 📋 Fluxo de Execução Passo a Passo

### Passo 1 — Coleta de Contexto e Linha de Base
- Carregar o catálogo de cenários em `tests/operational_flow/casos-workflows.yaml`.
- Identificar o cenário selecionado pelo parâmetro ou selecionar o primeiro pendente.

### Passo 2 — Processamento e Transformação
- Mapear a sequência de etapas esperada: `etapa`, `agente`, `invariantes` e `proximos_permitidos`.
- Comparar o comportamento observado na sessão contra os critérios declarados do cenário.

### Passo 3 — Validação e Checagem Imediata
- Validar se os agentes da cadeia mantiveram o isolamento de ferramentas (read-only sem mutação).
- Validar se houve detecção de deriva de intenção caso a solicitação tenha migrado de contexto.

### Passo 4 — Saída Estruturada
- Emitir o relatório de avaliação no formato canônico da governança.

---

## ✅ Checklist Antes de Apresentar

- [ ] Cenário identificado por ID único em `casos-workflows.yaml`.
- [ ] Todas as etapas da trajetória foram auditadas individualmente.
- [ ] Nenhuma ferramenta mutativa executada durante a avaliação.
- [ ] Veredito final (`APROVADO` ou `REPROVADO`) com justificativa fundamentada.

---

## 📊 Formato de Saída

### 🧪 Relatório de Avaliação de Trajetória: <cenario_id> — <cenario_nome>

- **Workflow Canônico**: <WORKFLOW-ID>
- **Tipo de Cenário**: <fast_path | standard | intent_drift | circuit_breaker | fast_chaining>
- **Projeto Alvo**: <projeto_alvo>

#### Trajetória Observada vs. Esperada
| Etapa | Agente Esperado | Banner Válido? | Invariantes Respeitadas? | Transição Permitida? |
|---|---|:---:|:---:|:---:|
| 1 | <agente_1> | ✅/❌ | ✅/❌ | ✅/❌ |
| 2 | <agente_2> | ✅/❌ | ✅/❌ | ✅/❌ |

#### Diagnóstico e Veredito
- **Score de Aderência**: <0.0 a 1.0>
- **Resultado**: <APROVADO | REPROVADO>
- **Desvios / Gaps Observados**: <descrição em ≤ 2 linhas, ou 'Nenhum desvio detectado'>
- **Próximo Passo Mínimo**: <ação sugerida>

---

## 🚨 Regras de Autonomia

- Em caso de inconsistência no grafo de roteamento, pare e aponte a aresta divergente.
- Nunca gere mocks de resposta falsos; avalie estritamente com base nos artefatos reais.

---

## 🔄 Combina Com (Encadeamento)

- `/validate` -> executa validação da suíte pytest completa após a avaliação do cenário.
- `/plan` -> aciona novo planejamento caso desvios de governança sejam detectados.

