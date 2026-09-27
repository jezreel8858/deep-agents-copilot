# Plano de Implementação Técnica — Redesenho do WORKFLOW-PROMPT-SYNTHESIS & Migração Global XML → Markdown

> **Workflow**: WORKFLOW-GOVERNANCE-MAINTENANCE
> **Gate**: 2 (Plano de Implementação Técnica, R-064)
> **Executor Responsável**: `@governance-maintainer`
> **Data**: 2026-09-27
> **Status**: ✅ Executado em 2026-09-27
> **Protocolo Operacional**: `efficient-batch-code-modification` (Single-Turn MCP Batching, R-046, R-051, R-055)
> **Base de Diagnóstico**: `docs/plans/20260927-workflow-governance-maintenance-prompt-synthesis-redesign.md` (Gate 1 Aprovado)

---

## 1. Mapeamento de Diffs Planejados por Arquivo (Antes vs. Depois)

| # | Arquivo | Seção / Linhas | Antes (Resumo) | Depois Planejado (Resumo) |
|---|---|---|---|---|
| 1 | `.github/agents/workflows.md` | § 3.9 (Objetivo, Mermaid, Estados 1, 4, 5, Typed State Bag) | Cita XML canônico, 1 a 3 perguntas, State Bag inconsistente, sem red-teaming | Template Markdown legível; 5–10 rodadas; Quality Gate de corte; consumo exclusivo de agents/workflows; State Bag com 3 campos novos |
| 2 | `.github/agents/workflows.md` | § 5 (Invariantes 17 e 19) | 17(c) genérico; 19 prescreve "1 a 3 perguntas" | 17(c) desdobrado com checklist determinístico; 19 reescrito para 5–10 rodadas + teto |
| 3 | `.github/prompts/craft-prompt.prompt.md` | Passos 1, 4, 5, Formato de Saída, Regras | Esqueleto XML; proíbe fugir do XML | Esqueleto Markdown aprovado; checklist de red-teaming; 5–10 rodadas |
| 4 | `.github/agents/prompt-structuring.agent.md` | Frontmatter, Decision Tree, Formato de Saída | `<task>/<context>/<constraints>/<output_format>` | Seções Markdown genéricas (`## Tarefa`, `## Contexto`, `## Restrições`, `## Formato de Saída Esperado`) |
| 5 | `.github/agents/requirements-analyst.agent.md` | Escopo / Processo | Perguntas pontuais genéricas | Cláusula específica: 5–10 rodadas no Estado 1 do WORKFLOW-PROMPT-SYNTHESIS |
| 6 | `.github/skills/prompt-engineering-patterns/SKILL.md` | Quando Usar, Técnicas, Checklist | Cita XML como formato canônico | Migra para Markdown estruturado |
| 7 | `.github/skills/harness-engineering-patterns/SKILL.md` | Linha 61 | Cita XML | Atualiza para Markdown |
| 8 | `.github/skills/README.md` | Linha 29 | Cita XML | Atualiza descrição |
| 9 | `CLAUDE.md` | § R-041 | Cita XML | Sincroniza para Markdown |
| 10 | `.github/agents/catalog.yaml` | `prompt-structuring` (descrição) | Cita XML | Atualiza descrição |
| 11 | `.github/agents/routing-graph.yaml` | Nós/transições | Cita XML | Sincroniza descrições |
| 12 | `.a2a/agentcards/prompt-structuring.agentcard.json` | `description` | Cita XML | Atualiza descrição (paridade A2A) |
| 13 | `.github/agents/evals/casos-roteamento.yaml` | Casos de regressão | Cita XML | Atualiza texto de contexto simulado |
| 14 | `templates/prompt-synthesis-output.md` | Novo arquivo | Inexistente | Template canônico reutilizável (Q2/R-055) |
| 15 | `tests/governance_audit/test_prompt_synthesis_output_format_governance.py` | Novo arquivo | Inexistente | Teste determinístico (Q3/R-055) |
| 16 | `CHANGELOG.md` | `[Unreleased]` | Sem registro | Registro da manutenção |

## 2. Invariante 17(c) Desdobrado (Red-Teaming contra Solution Space)

Checklist de corte com 4 critérios excludentes (classes/métodos internos; bibliotecas/frameworks/algoritmos não pedidos; arquitetura/design patterns prescritos; tecnologias não mencionadas) + cláusula de bloqueio e finalidade explícita de consumo exclusivo por agents/workflows.

## 3. Invariante 19 Reescrito

Elicitação de 5 a 10 rodadas via `ask_questions`, sem checklist fixo, com cláusula de teto na 10ª rodada (declarar lacunas residuais em `## Restrições e Não-Escopo` e prosseguir).

## 4. Typed State Bag — Novos Campos
`rodadas_elicitacao_realizadas`, `lacunas_residuais_declaradas`, `red_teaming_solution_space` (aprovado/violações), `formato_saida: "markdown_code_block"`, `consumo_exclusivo_agents: true`.

## 5. Novo Template `craft-prompt.prompt.md`
Passo 4 (síntese em Markdown), Passo 5 (Quality Gate ativo com checklist), bloco de saída final com o esqueleto Markdown aprovado.

## 6. Migração Global — Padrão Genérico para `@prompt-structuring`/skill
```markdown
# Prompt Estruturado — [Objetivo Conciso]

## Tarefa
## Contexto
## Restrições e Não-Escopo
## Formato de Saída Esperado
```

## 7. Novo Teste Determinístico
`tests/governance_audit/test_prompt_synthesis_output_format_governance.py` com 5 casos: ausência de XML residual, migração de prompt-structuring/skill, presença do checklist de red-teaming, limites de rodadas 5-10, paridade dos campos do State Bag.

## 8. Ordem de Execução em Lote (R-046/R-051)
```
LOTE 1: templates/prompt-synthesis-output.md + craft-prompt.prompt.md
LOTE 2: workflows.md (§3.9, Invariantes, State Bag) + requirements-analyst.agent.md
LOTE 3: prompt-structuring.agent.md + prompt-engineering-patterns + harness-engineering-patterns + skills/README.md
LOTE 4: CLAUDE.md + catalog.yaml + routing-graph.yaml + agentcard.json + casos-roteamento.yaml + CHANGELOG.md
LOTE 5: novo teste pytest
VALIDAÇÃO: get_errors em lote + pytest completo
```

Execução via `ctx_execute` em processo único (Node.js), sem ferramentas nativas de edição fragmentada, All-or-Nothing.

