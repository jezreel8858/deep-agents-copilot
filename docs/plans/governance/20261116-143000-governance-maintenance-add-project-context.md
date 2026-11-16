---
title: "Plano de Manutenção de Governança — Remediação Estrutural de add-project-context e Artefatos Correlatos"
status: "APPROVED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-16"
related-planning-doc: "N/A"
review_verdict: "PASS"
review_rounds: 2
reviewer: "@plan-critic"
review_tier1: "PASS"
session_id: "sess-20261116-01"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-gov-audit-01"
parent_plan_ref: "N/A — plano raiz"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS"
  author_ref: "@agent-auditor"
allowed_files:
  - ".github/prompts/add-project-context.prompt.md"
  - ".github/agents/binding-initializer.agent.md"
  - ".github/agents/adapter-generator.agent.md"
  - ".github/agents/codegraph-engine.agent.md"
  - ".github/skills/project-context-builder/SKILL.md"
  - ".github/skills/project-scanner/SKILL.md"
---

# Plano de Manutenção de Governança — `add-project-context` e Artefatos Correlatos

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

Materializar o plano de remediação estrutural de governança originado pela auditoria do `@agent-auditor` sobre o fluxo `/add-project-context` (`.github/prompts/add-project-context.prompt.md`) e seus agentes e skills correlatos, eliminando efeitos colaterais pré-HITL, contradições de confinamento territorial (R-043/R-044), corrupções semânticas por substituição textual, lacunas de proteção contra Indirect Prompt Injection (OWASP ASI01/ASI06), referências legadas a `catalog.yaml`/`binding.md` e hipertrofia instrucional (R-060 / arXiv:2602.11988v1).

| Parâmetro de Correlação | Valor |
| :--- | :--- |
| **Workflow ID** | `WORKFLOW-GOVERNANCE-MAINTENANCE` |
| **Workflow Trace ID** | `wt-20261116-gov-audit-01` |
| **Session ID** | `sess-20261116-01` |
| **Autor Intelectual** | `@agent-auditor` |
| **Materializador Físico (Etapa 2)** | `@docs-engineer` (R-064) |
| **Executor Declarativo (Etapa 5)** | `@governance-maintainer` (pós-Gate HITL) |
| **Status Inicial** | `DRAFT` (`approved: false`) |

| ID | Severidade | Smells / Regras Mapeadas | Artefato(s) Afetado(s) | Diagnóstico Verificado | Solução Prescrita |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F-01** | **BLOCKER** | `Smell 2.13` / `R-027` / `R-064` | `.github/prompts/add-project-context.prompt.md` (L234–256) | Efeito colateral antes do HITL: `adapter-generator (modo=generate-one)` grava `.github/instructions/local/[PROJETO-ALVO].instructions.md` na Fase 2.4 antes da confirmação humana na Fase 2.5. | Consolidar em um único Gate HITL (`ask_questions` R-027) na Fase 2 que valida metadados e preview antes de qualquer gravação em disco na Fase 3. |
| **F-02** | **BLOCKER** | `Smell 2.12` / `R-043` / `R-044` | `.github/prompts/add-project-context.prompt.md` (L27, L49, L89 vs L318, L398–399) | Contradição normativa de confinamento: o prompt afirma nunca criar arquivos no projeto externo, mas a Fase 4 (`codegraph build`) cria `.codegraph/graph.db` e a Fase 4.1 cria `.codegraphrc.json` em `[CAMINHO-EXTERNO]`. | Explicitar no Guardrail que o **código-fonte e configurações de negócio** em `[CAMINHO-EXTERNO]` jamais são modificados, documentando de forma transparente e restrita o cache local de indexação `.codegraph/` (e `.codegraphrc.json` apenas quando multi-projeto for confirmado no Gate HITL). |
| **F-03** | **BLOCKER** | `Smell 2.12` / `R-043` | `.github/prompts/add-project-context.prompt.md` (L86, L109–115, L278–280, L291–294, L485–488, L564, L586–587) | Corrupção semântica por search-and-replace: duplicação de `✓ Existe: ./.github/instructions/README.md?` no Health Check, contradição entre `[UPDATE] .github/instructions/README.md` (L278) vs `❌ Nenhuma operação em .github/instructions/README.md` (L280), e comando incorreto `git checkout .github/instructions/README.md` na L564. | Limpar todas as 16 ocorrências corrompidas — `.github/instructions/README.md` e `.github/agents/catalog.yaml` são compartilhados e somente-leitura durante `/add-project-context`; a escrita local em tempo de uso ocorre em artefatos locais de binding e `.github/instructions/local/[PROJETO-ALVO].instructions.md`. |
| **F-04** | **BLOCKER** | `OWASP ASI01/ASI06` | `.github/prompts/add-project-context.prompt.md`, `.github/agents/adapter-generator.agent.md`, `.github/skills/project-scanner/SKILL.md` | Ausência de guardrail OWASP ASI01/ASI06 (Indirect Prompt Injection e Persistent Context Poisoning) ao ingerir arquivos de `[CAMINHO-EXTERNO]`. | Adicionar cláusula obrigatória de sanitização tratando conteúdo lido de `[CAMINHO-EXTERNO]` (`README.md`, `package.json`, comentários) como dado não-confiável inerte, vedando copiar instruções imperativas ou prompts embutidos de arquivos externos para dentro de `.github/instructions/local/[PROJETO-ALVO].instructions.md`. |
| **F-05** | **HIGH** | `Smell 2.12` / `R-043` | `.github/agents/binding-initializer.agent.md` (L5–8, L53, L69, L83–131, L218, L251, L262, L283, L287, L298) | Contém 18 referências legadas a `catalog.yaml` e `binding.md` e tenta validar `README.md` com `yaml.safe_load` (L251). | Alinhar integralmente `binding-initializer.agent.md` à arquitetura R-043 de registro local e verificação somente-leitura de `.github/instructions/README.md`, aplicando `yaml.safe_load` exclusivamente sobre arquivos YAML. |
| **F-06** | **HIGH** | `Smell 2.26` / `R-056` | `.github/prompts/add-project-context.prompt.md` (L11), `.github/skills/project-context-builder/SKILL.md` (L50) | Frontmatter `tools:` do prompt omite `context-mode/ctx_index`, `context-mode/ctx_execute` e `context-mode/ctx_batch` exigidos pelo corpo do prompt (L47, L264, L349) e pela regra R-056; skill prioriza tools nativas legadas. | Sincronizar o frontmatter `tools:` e diretrizes operacionais de ambos com `context-mode` (R-056 e prevenção do Smell 2.26). |
| **F-07** | **HIGH** | `Smell 2.13` / `R-060` | `.github/prompts/add-project-context.prompt.md` | Excesso de paradas HITL (5 interações distribuídas nas Fases 2.3, 2.5, 3, 4.1 e 4.5 na mesma execução, violando o teto R-060 de até 5 turnos) e hipertrofia do prompt (648 linhas). | Reduzir `add-project-context.prompt.md` para um fluxo enxuto (abaixo de 250 linhas) com **1 único checkpoint HITL via `ask_questions` (R-027)** na Fase 2 seguido de execução atômica consolidada nas Fases 3 e 4 (tornando a sumarização final apenas nota informativa sob demanda, sem abrir novo modal `ask_questions`). |
| **F-08** | **HIGH** | `Smell 2.13` / `R-060` | `.github/agents/adapter-generator.agent.md`, `.github/skills/project-context-builder/SKILL.md` | Hipertrofia instrucional em adapters gerados (acima de 600 linhas de boilerplate redundante, contrariando arXiv:2602.11988v1). | Instituir em `adapter-generator.agent.md` e `project-context-builder/SKILL.md` a diretriz **"Delta-Only / Non-Inferable Instructions"** (teto recomendado de até 150 linhas para novos adapters gerados em `local/`, focando em comandos verificados zero-noise, invariantes arquiteturais não-óbvios, design system local e proibições de CI, sem repetir convenções já cobertas pelo adapter pai em `extends`). |
| **F-09** | **MEDIUM** | `Smell 2.12` | `.github/prompts/add-project-context.prompt.md` | Numeração e ordenação inconsistente de fases ao longo do prompt. | Renumerar e ordenar sequencialmente as fases: `FASE 1` Scan Read-Only → `FASE 2` Gate HITL Único → `FASE 3` Binding Atômico e Geração do Adapter → `FASE 4.1` Codegraph Build/Registry → `FASE 4.2` Indexação FTS5 `ctx_index` → `FASE 4.3` Fronteiras `.codegraphrc.json` quando houver múltiplos projetos. |
| **F-10** | **MEDIUM** | `Smell 2.12` | `.github/prompts/add-project-context.prompt.md` | Rótulo ambíguo de obrigatoriedade na Fase 4 (mistura de execução obrigatória com semântica de opt-out). | Corrigir o rótulo da Fase 4 para `(execução obrigatória sem opt-out; falha reportada em modo degradado sem reverter a Fase 3)`. |
| **F-11** | **MEDIUM** | `Smell 2.12` / `R-043` | `.github/agents/codegraph-engine.agent.md` (L196), `.github/skills/project-scanner/SKILL.md` (L165) | Referências residuais legadas a `catalog.yaml` nos artefatos de grafo e scanner de projetos externos. | Substituir `catalog.yaml` na L196 de `codegraph-engine.agent.md` (2 ocorrências) e na L165 de `project-scanner/SKILL.md` (1 ocorrência) pela referência à arquitetura de isolamento local R-043. |

---

## 2. Artefatos Afetados e allowed_files

### 2.1. Grupo A — Artefatos Declarativos de Governança (`Executor: @governance-maintainer`)

A allowlist deste plano compreende exatamente os 6 arquivos declarativos abaixo:

1. `.github/prompts/add-project-context.prompt.md`
2. `.github/agents/binding-initializer.agent.md`
3. `.github/agents/adapter-generator.agent.md`
4. `.github/agents/codegraph-engine.agent.md`
5. `.github/skills/project-context-builder/SKILL.md`
6. `.github/skills/project-scanner/SKILL.md`

- **Justificativa de Exclusão Estrita (Conformidade C10 / R-043)**: O arquivo de template de exemplo de binding local (que contém o infixo reservado de isolamento local no nome) foi **excluído de `allowed_files` e do escopo de mutação deste plano** para respeitar de forma absoluta e inegociável a regra determinística C10/R-043 do Tier 1 e do `@plan-critic`, que proíbe qualquer caminho contendo o padrão de sufixo/infixo local na chave `allowed_files` de planos de governança do repositório `deep-agents-copilot`.

### 2.2. Grupo B — Suíte de Testes Automatizados (`Executor: @python-router → @python-arch-advisor → @python-test-engineer`)

- **Escopo condicional (Q3 do R-055)**: Caso seja necessário adicionar asserções específicas em Python para o fluxo `add-project-context` dentro de `tests/governance_audit/`, a mutação de arquivos `.py` é estritamente vedada ao `@governance-maintainer` (R-065) e deverá ser delegada via handoff formal ao `@python-router` após a Etapa 5. A suíte existente (`pytest -q --tb=short tests/governance_audit/`) já valida integridade de frontmatter, contratos de agentes/skills e fronteira territorial R-043/R-044.

---

## 3. Plano de Correção em Lote (Plan-Then-Batch)

A execução na Etapa 5 pelo `@governance-maintainer` ocorrerá de forma consolidada em lote único via `ctx_execute` (`language: "javascript"`, R-059 / Smell 2.26) sobre os 6 arquivos de `allowed_files`:

1. **Passo 1 — Refatoração Enxuta e Segura de `.github/prompts/add-project-context.prompt.md` (F-01, F-02, F-03, F-04, F-06, F-07, F-09, F-10)**:
   - Sincronizar frontmatter `tools:` adicionando `context-mode/ctx_index`, `context-mode/ctx_execute` e `context-mode/ctx_batch` (R-056).
   - Estruturar o fluxo em menos de 250 linhas com numeração estrita e zero placeholders angulares:
     - `FASE 1`: Health Check de pré-requisitos e Scan Read-Only de `[CAMINHO-EXTERNO]` com cláusula OWASP ASI01/ASI06 (dados externos tratados como texto inerte não-confiável).
     - `FASE 2`: Gate HITL Único via `ask_questions` (R-027) validando metadados inferidos de `[PROJETO-ALVO]`, preview do adapter e, quando houver mais de 1 projeto, topologia de integrações — **nenhum arquivo é gravado antes deste Gate**.
     - `FASE 3`: Binding Atômico no registro local de projetos e Geração do Adapter em `.github/instructions/local/[PROJETO-ALVO].instructions.md` (mantendo `.github/instructions/README.md` e `.github/agents/catalog.yaml` estritamente somente-leitura).
     - `FASE 4`: Indexação e Grafo `(execução obrigatória sem opt-out; falha reportada em modo degradado sem reverter a Fase 3)` subdividida em `FASE 4.1` (Codegraph Build/Registry com transparência sobre `.codegraph/graph.db` em `[CAMINHO-EXTERNO]`), `FASE 4.2` (Indexação FTS5 `ctx_index`) e `FASE 4.3` (Fronteiras `.codegraphrc.json` quando mais de 1 projeto for confirmado no Gate HITL). Sumarização final emitida como nota informativa sob demanda, sem novo modal `ask_questions`.
2. **Passo 2 — Alinhamento R-043 em `.github/agents/binding-initializer.agent.md` (F-05)**:
   - Substituir as 18 referências legadas a `catalog.yaml` e `binding.md` pela arquitetura de registro local R-043 e verificação somente-leitura de `.github/instructions/README.md`.
   - Restringir validação `yaml.safe_load` exclusivamente a arquivos YAML, removendo qualquer tentativa de parse YAML sobre `README.md`.
3. **Passo 3 — Guardrail OWASP ASI01/ASI06 e Diretriz Delta-Only em `.github/agents/adapter-generator.agent.md` e `.github/skills/project-context-builder/SKILL.md` (F-04, F-06, F-08)**:
   - Injetar cláusula de sanitização OWASP ASI01/ASI06 vedando cópia de instruções imperativas ou prompts embutidos de `[CAMINHO-EXTERNO]`.
   - Instituir a diretriz **"Delta-Only / Non-Inferable Instructions"** (teto recomendado de até 150 linhas para adapters de `[PROJETO-ALVO]`, cobrindo apenas comandos verificados zero-noise, invariantes arquiteturais não-óbvios, design system local e proibições de CI, delegando convenções base ao adapter pai via `extends`).
   - Atualizar ferramentas de `project-context-builder/SKILL.md` para priorizar `context-mode` (R-056 / Smell 2.26).
4. **Passo 4 — Limpeza de Referências Legadas e Sanitização em `.github/skills/project-scanner/SKILL.md` e `.github/agents/codegraph-engine.agent.md` (F-04, F-11)**:
   - `.github/skills/project-scanner/SKILL.md`: adicionar cláusula OWASP ASI01/ASI06 na leitura de arquivos de `[CAMINHO-EXTERNO]` e atualizar a referência na L165 (1 ocorrência de `catalog.yaml`) para o registro local de projetos R-043.
   - `.github/agents/codegraph-engine.agent.md`: atualizar a L196 (2 ocorrências de `catalog.yaml`) para referenciar o registro local de projetos e adapters locais R-043.

---

## 4. Alternativas Rejeitadas

| # | Alternativa Considerada | Motivo Técnico da Rejeição |
| :--- | :--- | :--- |
| **1** | **Criar um Workflow Canônico separado (`WORKFLOW-PROJECT-SCANNER`) dedicado exclusivamente à Fase 1 de Scan** | Rejeitada por causar inflação desnecessária de catálogo e complexidade de roteamento no `@agent-router`, visto que o subagente `adapter-generator (modo=scan)` apoiado pela skill `project-scanner` já atende integralmente scans isolados Read-Only dentro do workflow existente. |
| **2** | **Manter as 5 paradas HITL distribuídas entre as Fases 2.3, 2.5, 3, 4.1 e 4.5** | Rejeitada por violar diretamente o orçamento rígido de até 5 tool turns por ciclo de execução (R-060 / Smell 2.13), além de induzir fadiga de aprovação humana e permitir efeito colateral em disco (Fase 2.4) antes do consentimento do usuário na Fase 2.5. |
| **3** | **Incluir o arquivo de template de exemplo de binding local em `allowed_files` deste plano** | Rejeitada após apontamento na Rodada 1 do `@plan-critic` (BLOCKER 1 — C10/R-043), pois qualquer caminho contendo o padrão de infixo local colide com o bloqueio determinístico da rubrica C10/R-043 para planos de governança do repositório `deep-agents-copilot`. |

---

## 5. Reúso Sistêmico (R-055: Q1/Q2/Q3) e Sensores tests/governance_audit/

| Questão R-055 | Resposta Verificada com Evidência Empírica |
| :--- | :--- |
| **Q1 — Quais artefatos irmãos (peers) no repositório possuem o mesmo padrão e foram varridos?** | Foram varridos por contagem determinística todos os artefatos que compõem o fluxo de onboarding de projetos externos: (1) `.github/agents/binding-initializer.agent.md` = **18 ocorrências** legadas de `catalog.yaml`/`binding.md`; (2) `.github/prompts/add-project-context.prompt.md` = **16 ocorrências** de `instructions/README.md` com conflito semântico entre UPDATE vs edição proibida; (3) `.github/agents/codegraph-engine.agent.md` = **2 ocorrências** legadas de `catalog.yaml` na L196; (4) `.github/skills/project-scanner/SKILL.md` = **1 ocorrência** legada de `catalog.yaml` na L165; (5) `.github/skills/project-context-builder/SKILL.md` = **0 ocorrências** de `catalog.yaml`, mas requer sincronização de `tools:` com `context-mode` (R-056) e diretriz Delta-Only (F-06/F-08); (6) `.github/agents/adapter-generator.agent.md` = requer guardrail OWASP ASI01/ASI06 e diretriz Delta-Only (F-04/F-08). |
| **Q2 — Quais templates, schemas ou contratos canônicos foram atualizados para impedir reincidência?** | As skills geradoras (`project-context-builder/SKILL.md` e `project-scanner/SKILL.md`), o prompt orquestrador (`add-project-context.prompt.md`) e os contratos dos agentes (`binding-initializer.agent.md`, `adapter-generator.agent.md` e `codegraph-engine.agent.md`) são atualizados conjuntamente com cláusulas de fronteira R-043, teto Delta-Only (até 150 linhas) e sanitização OWASP ASI01/ASI06, prevenindo que novos adapters gerados para `[PROJETO-ALVO]` reintroduzam hipertrofia instrucional ou envenenamento de contexto. |
| **Q3 — Qual verificação automatizada garante que a regressão não retorne?** | A suíte de sensores automatizados em `tests/governance_audit/` executada via `pytest -q --tb=short tests/governance_audit/` valida invariantes de frontmatter, referências cruzadas, isolamento territorial R-043/R-044 e conformidade estrutural dos agentes, skills e prompts em `.github/`. Caso necessário expandir cobertura específica em arquivos `.py`, será acionado handoff ao `@python-router` (Grupo B). |

| Artefato Auditado no Fluxo de Onboarding (Evidência Q1) | Contagem Determinística de Ocorrências Legadas / Conflitos | Escopo de Correção na Allowlist |
| :--- | :--- | :--- |
| `.github/agents/binding-initializer.agent.md` | 18 ocorrências legadas de `catalog.yaml` / `binding.md` | Passo 2 (F-05) |
| `.github/prompts/add-project-context.prompt.md` | 16 ocorrências de `instructions/README.md` com conflito UPDATE vs proibido | Passo 1 (F-01 a F-04, F-06, F-07, F-09, F-10) |
| `.github/agents/codegraph-engine.agent.md` | 2 ocorrências legadas de `catalog.yaml` na L196 | Passo 4 (F-11) |
| `.github/skills/project-scanner/SKILL.md` | 1 ocorrência legada de `catalog.yaml` na L165 | Passo 4 (F-04, F-11) |
| `.github/skills/project-context-builder/SKILL.md` | 0 ocorrências de `catalog.yaml`; requer sincronização `tools:` R-056 e diretriz Delta-Only | Passo 3 (F-06, F-08) |
| `.github/agents/adapter-generator.agent.md` | 0 ocorrências de `catalog.yaml`; requer cláusula OWASP ASI01/ASI06 e diretriz Delta-Only | Passo 3 (F-04, F-08) |

---

## 6. Rollback e Critério de Pronto

### 6.1. Matriz de Riscos Operacionais

| Risco Identificado | Probabilidade | Impacto | Mitigação |
| :--- | :--- | :--- | :--- |
| Quebra de referências cruzadas entre `add-project-context.prompt.md` e os subagentes `binding-initializer`, `adapter-generator` e `codegraph-engine` | Baixa | Alto | Atualização sincronizada em lote único (Plan-Then-Batch R-059) mantendo os nomes de modos (`generate-one`, `build`, `registry`) e contratos de entrada/saída alinhados às Fases 1 a 4. |
| Violação acidental de sintaxe YAML no frontmatter dos agentes, skills ou prompt | Baixa | Médio | Validação imediata pós-escrita dos frontmatters e execução da suíte `pytest -q --tb=short tests/governance_audit/` somada a `get_errors` agrupado (R-051). |
| Efeito colateral em arquivos fora da allowlist | Muito Baixa | Alto | Modificação restrita exclusivamente aos 6 arquivos declarativos listados em `allowed_files`. |

### 6.2. Procedimento de Rollback Atômico

Em caso de falha na validação pós-execução na Etapa 5, reverter atomicamente todos os 6 artefatos de `allowed_files` com um único comando:

```bash
git checkout -- \
  .github/prompts/add-project-context.prompt.md \
  .github/agents/binding-initializer.agent.md \
  .github/agents/adapter-generator.agent.md \
  .github/agents/codegraph-engine.agent.md \
  .github/skills/project-context-builder/SKILL.md \
  .github/skills/project-scanner/SKILL.md
```

### 6.3. Critério de Pronto (Definition of Done)

1. Todos os 6 arquivos de `allowed_files` atualizados em lote único pelo `@governance-maintainer` após aprovação humana (Gate R-064).
2. Zero ocorrências residuais de `[UPDATE] .github/instructions/README.md` em `add-project-context.prompt.md` e zero chamadas `yaml.safe_load` sobre `README.md` em `binding-initializer.agent.md`.
3. Execução limpa de `get_errors` nos 6 arquivos modificados e aprovação integral da suíte automatizada:

```bash
pytest -q --tb=short tests/governance_audit/
```

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: PASS
- **Tier 2 (@plan-critic)**: PASS (review_rounds: 2, 0 BLOCKER/HIGH pendentes)
- **Findings e Resoluções (Histórico da Rodada 1 → Rodada 2/2)**:
  - **BLOCKER 1 (C10 / R-043 — `allowed_files` continha padrão local proibido)**: Resolvido removendo o arquivo de exemplo local da chave `allowed_files` e do escopo deste plano, mantendo exclusivamente os 6 artefatos canônicos do Grupo A.
  - **BLOCKER 2 (Ausência da seção obrigatória `## 4. Alternativas Rejeitadas` e divergência de títulos das seções do template)**: Resolvido adotando exatamente as 6 seções canônicas de `plan-template-governance.md` e documentando 3 alternativas técnicas rejeitadas na Seção 4.
  - **MINOR / MEDIUM 3 (Campos obrigatórios do frontmatter de `plan-template-governance.md` ausentes e mapeamento explícito de Smells `2.x` na Seção 1)**: Resolvido sincronizando 100% das chaves do frontmatter YAML e adicionando a coluna `Smells / Regras Mapeadas` (`2.12`, `2.13`, `2.26`, `R-043`, `R-056`, `R-060`, `OWASP ASI01/ASI06`) para F-01 a F-11 na Seção 1.
  - **MINOR / MEDIUM 4 (Evidência empírica quantitativa em Q1 do R-055 na Seção 5)**: Resolvido incluindo a contagem determinística verificada por arquivo na resposta de Q1 e na tabela de evidência da Seção 5 (18, 16, 2, 1 e 0 ocorrências).
  - **NIT 5 (Uso de marcadores entre colchetes angulares gerando falso positivo de placeholder no Tier 1)**: Resolvido substituindo 100% dos marcadores angulares por notação entre colchetes retos (`[PROJETO-ALVO]`, `[CAMINHO-EXTERNO]`).

## Checklist

- [x] Frontmatter R-064 completo (`plan_type: governance`).
- [x] Persistência por `@governance-maintainer`/`@docs-engineer`; auditor permanece Read-Only (R-057).
- [x] Conformidade com `docs/plans/[tipo]/` auditada (Smell 2.34).
