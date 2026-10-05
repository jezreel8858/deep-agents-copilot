---
name: harness-eval
description: >-
  Executa o protocolo de avaliação determinística de harness de agentes (Track A: regressão de
  instruções; Track B: calibração de prompts; Track C: auditoria dual-judge) comparando o
  comportamento esperado contra evidências observáveis. Use quando precisar auditar
  deterministicamente a fidelidade de execução de um harness/prompt contra claims e critérios
  de aceitação. Não use para diagnóstico contínuo de harness-vs-modelo (isso é
  `harness-engineering-patterns`) nem para métricas de qualidade de resposta do modelo em si
  (isso é `agent-evals-lab`).
tier: 2
category: quality
license: "CC-BY-4.0"
source_attribution: "Tech Leads Club (agent-skills)"
imported_from: "https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/(development)/harness-eval"
triggers:
  - "quando precisar avaliar deterministamente a eficácia do harness de um agente"
  - "quando for necessário rodar auditoria dual-judge em prompts de agentes"
  - "quando executar testes de regressão de instruções ou calibração de harness"
  - "quando auditar fidelidade de execução contra claims e critérios de aceitação"
source_docs:
  - ".github/skills/harness-eval/references/GLOSSARY.md"
source_docs_lazy:
  - ".github/skills/harness-eval/references/claims.schema.json"
  - ".github/skills/harness-eval/references/PROTOCOL.md"
  - ".github/skills/harness-eval/references/judge-prompts.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
tools: []
---

# Harness Eval

## 0) Problema Resolvido & Atribuição de Origem

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: frontmatter para descoberta e roteamento rápido.
> - **Nível 2 (Corpo Operacional)**: este arquivo com regras essenciais, as 3 trilhas de avaliação e checklist.
> - **Nível 3 (Recursos Suplementares)**: `references/PROTOCOL.md` (protocolo procedural de 11 passos), `references/judge-prompts.md` (prompts de juízes LLM dual-judge), `references/GLOSSARY.md` (glossário técnico) e `references/claims.schema.json` (schema de validação de claims), carregados sob demanda.

Esta skill formaliza um protocolo determinístico de avaliação de harness de agentes — comparando o comportamento **esperado** (declarado em prompts/instruções/claims) contra o comportamento **observado** (evidências reais de execução), evitando conclusões subjetivas sobre "o prompt funciona" sem evidência auditável.

> **Atribuição de Origem (Conformidade de Licença)**: esta skill é adaptada da skill `harness-eval` do catálogo open-source [Tech Leads Club — agent-skills](https://github.com/tech-leads-club/agent-skills), licenciado sob **CC-BY-4.0**. A adaptação preserva o protocolo procedural original, ajustando-o ao padrão N1/N2/N3 (Anthropic Agent Skills Open Standard) e à governança PT-BR deste repositório. Ver `imported_from:` no frontmatter para a fonte canônica.

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao validar formalmente se um prompt/harness de agente cumpre os claims declarados (Track C — auditoria dual-judge).
- Ao executar testes de regressão de instruções após alteração de prompt/system message (Track A).
- Ao calibrar um prompt experimental contra um baseline aprovado antes de promovê-lo (Track B).
- Ao precisar de um veredito reprodutível e auditável (dual-judge) sobre fidelidade de execução, não apenas uma impressão subjetiva.

### ❌ Quando NÃO Usar
- Para diagnóstico contínuo/heurístico de comportamento anômalo de agent (tools/system-prompt/permissões/contexto) — isso é `harness-engineering-patterns` (§ 2.1 Diagnóstico Harness-vs-Modelo).
- Para métricas gerais de qualidade de resposta do modelo (faithfulness, hallucination, tool correctness) fora do escopo de claims de harness — isso é `agent-evals-lab`.
- Para estruturar o prompt de uma tarefa específica no formato canônico de task prompt — isso é `prompt-engineering-patterns`.

---

## 2) Diretrizes Operacionais e Processo Canônico (Tracks A, B e C)

O protocolo completo de 11 passos está detalhado em `references/PROTOCOL.md` (carregado sob demanda). Resumo operacional das 3 trilhas:

| Trilha | Objetivo | Quando Acionar |
|---|---|---|
| **Track A — Regressão de Instruções** | Garantir que uma alteração de prompt/harness não quebrou comportamento previamente validado | Após qualquer edição em prompt/system message já homologado |
| **Track B — Calibração de Prompts** | Comparar variante experimental contra baseline aprovado em casos canônicos e de borda | Antes de promover um prompt experimental a produção |
| **Track C — Auditoria Dual-Judge** | Validar claims declarados (o que o prompt afirma fazer) contra evidência observável de execução | Auditoria formal de conformidade/qualidade de um harness já em produção |

**Fluxo canônico resumido** (detalhamento completo em `references/PROTOCOL.md`):
1. Extrair claims testáveis do prompt/harness-alvo (schema em `references/claims.schema.json`).
2. Definir casos de teste canônicos e de borda cobrindo cada claim.
3. Executar o harness-alvo e capturar evidências brutas de execução (transcript, tool calls, outputs).
4. Submeter evidência + claim a **dois juízes LLM independentes** (prompts em `references/judge-prompts.md`) em modo dual-judge (reduz viés de avaliador único).
5. Calcular score de conformidade por claim e consolidar veredito (aprovado/reprovado/divergente — desempate humano em caso de divergência entre juízes).
6. Registrar o resultado com evidência auditável (nunca aprovar apenas por impressão subjetiva — R-044 Vazamento de Evidência Real).

---

## 3) Padrões Canônicos com Exemplos Contrastantes

### Padrão: Veredito Baseado em Evidência vs. Impressão Subjetiva

#### ❌ Anti-padrão (Incorreto)
Concluir "o prompt está calibrado" ou "o harness está conforme" apenas por leitura do prompt ou por uma única execução observada manualmente, sem captura estruturada de evidência nem segundo juiz independente.

#### ✅ Padrão Canônico (Correto)
Extrair claims testáveis explícitos, executar casos canônicos/de borda, capturar evidência bruta e submeter a dual-judge (dois juízes LLM independentes) antes de emitir veredito de conformidade — qualquer divergência entre os dois juízes é sinalizada para desempate humano, nunca resolvida silenciosamente por um único lado.

---

## 4) Checklist de Auto-Verificação

- [ ] Claims testáveis extraídos e validados contra `references/claims.schema.json`.
- [ ] Casos de teste canônicos e de borda cobrem todos os claims declarados.
- [ ] Evidência de execução capturada de forma estruturada (não apenas impressão subjetiva).
- [ ] Avaliação de conformidade executada em modo **dual-judge** (dois juízes LLM independentes, `references/judge-prompts.md`).
- [ ] Divergências entre juízes escaladas para desempate humano (nunca resolvidas silenciosamente).
- [ ] Trilha correta selecionada (A: regressão / B: calibração / C: auditoria dual-judge) conforme o objetivo da avaliação.
- [ ] Atribuição de origem (CC-BY-4.0, Tech Leads Club) preservada e não omitida em usos derivados.

---

## 5) Consumidores Mapeados e Integrações

| Consumidor | Papel na Relação | Momento de Uso |
|---|---|---|
| `@agent-auditor` | Executor da auditoria dual-judge (Track C) sobre agents/skills/prompts já em produção | `WORKFLOW-GOVERNANCE-MAINTENANCE` |
| `@governance-maintainer` | Calibração de prompts/harness (Track B) antes de promover variante experimental | Revisão de prompt/system message candidato |
| `harness-engineering-patterns` (skill) | Fronteira: diagnóstico heurístico contínuo vs. auditoria formal sob demanda | Desenho de suíte de governança de harness |
| `agent-evals-lab` (skill) | Fronteira: avaliação de qualidade do harness (claims) vs. qualidade do modelo (faithfulness/hallucination) | Desenho de suíte de evals |

---

## 6) Referências e Documentação Conexa

- `references/PROTOCOL.md` — protocolo procedural detalhado de 11 passos e critérios de scoring.
- `references/judge-prompts.md` — prompts canônicos para os juízes LLM dual-judge.
- `references/GLOSSARY.md` — glossário técnico de termos de harness evaluation.
- `references/claims.schema.json` — schema JSON de validação estrutural de claims.
- `.github/skills/harness-engineering-patterns/SKILL.md` — diagnóstico heurístico contínuo de harness-vs-modelo (fronteira distinta).
- `.github/skills/agent-evals-lab/SKILL.md` — avaliação contínua de qualidade de resposta do modelo (fronteira distinta).
- Fonte original: Tech Leads Club, `agent-skills` (CC-BY-4.0) — https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/(development)/harness-eval
