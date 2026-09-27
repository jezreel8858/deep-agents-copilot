# Plano de Planejamento — Redesenho do WORKFLOW-PROMPT-SYNTHESIS

> **Workflow**: WORKFLOW-GOVERNANCE-MAINTENANCE
> **Gate**: 1 (Plano de Planejamento, R-064)
> **Autor**: `@agent-auditor`
> **Data**: 2026-09-27
> **Status**: ✅ Executado em 2026-09-27
> **Decisão de Escopo (Q1/R-055)**: Migração GLOBAL do formato XML→Markdown — `@prompt-structuring.agent.md` e `prompt-engineering-patterns/SKILL.md` também migram para o padrão Markdown legível, unificando todo prompt estruturado do catálogo (blast radius expandido conforme tabela de riscos acima).

## Objetivo
Redesenhar o `WORKFLOW-PROMPT-SYNTHESIS` (§ 3.9 de `.github/agents/workflows.md`) para:
1. Substituir o formato de saída XML por template Markdown legível no Estado 4/5.
2. Introduzir um Quality Gate ativo de red-teaming contra Solution Space como checklist verificável explícito no Estado 5.
3. Ampliar a elicitação do Estado 1 para mínimo 5 / máximo 10 rodadas de `ask_questions`.
4. Explicitar textualmente que o prompt gerado é consumo exclusivo de outros agents/workflows, nunca resposta final ao usuário.

Preservando 100% dos invariantes de governança hoje vigentes (R-027, R-045, Anti-Blackbox, Anti-Alucinação de Caminhos) que não dependem da sintaxe XML em si.

## Escopo (Arquivos Afetados)

| Arquivo | Trecho/Seção | Tipo de Mudança |
|---|---|---|
| `.github/agents/workflows.md` | § 3.9 Estado 1 (texto + diagrama Mermaid `S1_Req`) | Alterar exigência de "1 a 3 perguntas" para "mínimo 5 / máximo 10 rodadas" |
| `.github/agents/workflows.md` | § 3.9 Estado 4 (texto + Typed State Bag `formato_saida`) | Substituir referência a "XML canônico" por template Markdown; corrigir inconsistência pré-existente |
| `.github/agents/workflows.md` | § 3.9 Estado 5 (texto + diagrama `S5`) | Adicionar checklist ativo de red-teaming Solution Space antes da emissão |
| `.github/agents/workflows.md` | § 5, Invariante 17(c) | Expandir/desdobrar em invariante dedicado com checklist verificável |
| `.github/agents/workflows.md` | § 5, Invariante 19 (R-027) | Atualizar para "mínimo 5 / máximo 10 rodadas" + cláusula de teto com lacunas residuais |
| `.github/agents/workflows.md` | Typed State Bag `WORKFLOW-PROMPT-SYNTHESIS` | Novos campos: `rodadas_elicitacao_realizadas`, `lacunas_residuais_declaradas`, `red_teaming_solution_space` |
| `.github/prompts/craft-prompt.prompt.md` | Passo 4, Formato de Saída, Regras de Autonomia | **Achado crítico**: contém o template XML operacional e proibição explícita de fugir dele — precisa reescrita completa |
| `.github/agents/prompt-structuring.agent.md` | Linhas 6, 59, 79, 80, 93–96, 105–109, 122 | Referências ao formato `<task>/<context>/<constraints>/<output_format>` — **decisão pendente de escopo** |
| `.github/agents/requirements-analyst.agent.md` | Contrato de rodadas de `ask_questions` | Alinhar "1 a 3" com a nova regra 5–10 quando atuando neste workflow específico |
| `.github/skills/prompt-engineering-patterns/SKILL.md` | Linhas 29, 54, 72, 74, 75 | Skill de origem do padrão XML — **decisão pendente de escopo (R-055)** |
| `.github/skills/harness-engineering-patterns/SKILL.md` | Linha 61 | Menção cruzada cosmética |
| `.github/skills/README.md` | Linha 29 | Atualização de texto se o formato mudar globalmente |

## Diagnóstico de Gaps

1. **Gap de escopo do pedido vs. blast radius real**: `craft-prompt.prompt.md` é o artefato que efetivamente instrui a emissão literal do bloco XML — sem atualizá-lo, a mudança em `workflows.md` fica sem efeito prático.
2. **Gap de consistência interna pré-existente**: Typed State Bag do Estado 4 já grava `formato_saida: "markdown_code_block"` enquanto o texto diz "XML" — drift documental anterior a sanar.
3. **Gap de fronteira de responsabilidade (Smell 2.12)**: `prompt-structuring.agent.md` e `prompt-engineering-patterns/SKILL.md` declaram o formato XML como padrão **genérico** do agent, não exclusivo deste workflow. Decisão explícita necessária: restrito ao WORKFLOW-PROMPT-SYNTHESIS ou migração global.
4. **Tensão textual em elicitação livre**: `craft-prompt.prompt.md` hoje proíbe "perguntas abertas ou excessivas" — precisa reconciliar com "rodadas livres 5–10" sem virar pergunta aberta sem critério.
5. **Ausência de teste determinístico** que proteja o formato de saída específico do Estado 4/5 — nenhuma blindagem contra regressão silenciosa hoje.

## Riscos e Blast Radius

| Item | Blast Radius | Justificativa |
|---|---|---|
| Reescrita § 3.9 Estados 1/4/5 + diagramas + State Bag | Médio | Confinado a uma seção, mas exige coerência texto/diagrama/YAML |
| Reescrita Invariantes 17/19 § 5 | Médio | Cross-references citadas literalmente em `craft-prompt.prompt.md` |
| Reescrita `craft-prompt.prompt.md` | **Alto** | Artefato de execução real; resíduo de XML gera comportamento inconsistente |
| Decisão de escopo `prompt-structuring.agent.md`/skill | **Alto (pendente)** | Se migração global, blast radius se expande a todo prompt estruturado do catálogo |
| Cobertura de testes | Baixo (ausência, não quebra) | Nenhum teste falha, mas nenhum valida a nova regra sem criação dedicada |

## Critério de Pronto (Definition of Done)
- [ ] § 3.9 Estados 1, 4, 5 refletem literalmente as 3 decisões aprovadas.
- [ ] Diagramas Mermaid atualizados, sem menção residual a XML no fluxo de emissão.
- [ ] Invariante 19 e 17(c)/dedicado reescritos com cross-references sincronizadas em `craft-prompt.prompt.md`.
- [ ] Typed State Bag com os 3 campos novos e `formato_saida` corrigido.
- [ ] `craft-prompt.prompt.md` migrado para o esqueleto Markdown aprovado, com finalidade de consumo exclusivo por agents/workflows explícita.
- [ ] Decisão do usuário registrada sobre escopo de `prompt-structuring.agent.md`/skill.
- [ ] Teste determinístico novo em `tests/governance_audit/` validando ausência de XML residual e presença do checklist de red-teaming.
- [ ] Suíte de testes pré-existente 100% verde.

## Reúso Sistêmico (R-055)
- **Q1 (Peers)**: Aplica-se a `prompt-structuring.agent.md`/`prompt-engineering-patterns` apenas se migração global for aprovada.
- **Q2 (Templates)**: Avaliar criação de `templates/prompt-synthesis-output.md` como template canônico reutilizável.
- **Q3 (Teste)**: Criar `test_prompt_synthesis_output_format_governance.py` em `tests/governance_audit/`.

