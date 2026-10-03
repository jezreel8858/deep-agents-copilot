---
status: concluído
date: 2026-10-03
autor: "@agent-auditor (diagnóstico) + governance-maintainer (execução)"
workflow: WORKFLOW-GOVERNANCE-MAINTENANCE
related-plan: docs/plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md
---

# Plano de Planejamento — Classificação de Perfil de Capacidade de Ferramentas de Context-Mode (Gather-only vs Gather+Process)

> **Workflow Canônico**: `WORKFLOW-GOVERNANCE-MAINTENANCE` (R-050)  
> **Cadeia de autoria**: `@agent-auditor` (diagnóstico e proposição de corte, Etapa 1) → Aprovação Humana via `ask_questions` → `@governance-maintainer` (execução transversal consolidada, Etapa 4)  
> **Status**: ✅ Concluído (executado e validado deterministicamente)

---

## 1) Contexto e Motivação

Durante auditorias operacionais e investigações de harness (.github/hooks/README.md), identificou-se que o host do IDE (GitHub Copilot no JetBrains / VS Code) apresenta uma lacuna de cobertura mecânica estrutural: **o hook `preToolUse` não intercepta chamadas de ferramentas disparadas por subagents** gerados através de `run_subagent`.

Enquanto a regra R-056 / R-059 e a skill `context-mode` (§4.1.1) estabelecem que `ctx_batch_execute` é a ferramenta DEFAULT e prioritária para consultas em lote, modelos atuando como subagents frequentemente recorriam a `context-mode/ctx_execute` ou `context-mode/ctx_execute_file` de forma sequencial ou desnecessária. Como o hook `preToolUse` não intercepta o subagent em runtime, a proteção contra Tool Chaining sequencial (Smell 2.26) nesses agentes não podia depender exclusivamente de bloqueios dinâmicos de hook.

A solução canônica e definitiva de governança consiste na **Poda Estrutural de Capacidade (Capability Profile Pruning)** no próprio contrato frontmatter (`tools:`) dos agentes. Agentes cujo escopo operacional é restrito à análise estática, revisão, planejamento e consultoria ("Gather-only") não necessitam de capacidade computacional de execução de código no sandbox (`ctx_execute` / `ctx_execute_file`). O escopo de gathering e execução de comandos estruturados é plenamente coberto por `context-mode/ctx_batch_execute`, `context-mode/ctx_search` e `context-mode/ctx_index`.

---

## 2) Critério de Corte Canônico ("Gather-only vs Gather+Process")

O corte aprovado formalmente segue três condições objetivas:

> **Regra de Retenção de Ferramentas de Execução (`ctx_execute` / `ctx_execute_file`)**:  
> Um agente MANTÉM `context-mode/ctx_execute` e `context-mode/ctx_execute_file` em seu frontmatter `tools:` se, e somente se, **pelo menos UMA** das seguintes condições for verdadeira para sua missão operacional:
> 1. **(a) Agregação computacional entre múltiplos arquivos**: cálculo numérico, percentis, deltas, ratios ou transformações matemáticas complexas que exijam script dedicado em runtime.
> 2. **(b) Estrutura derivada de N variável descoberto em runtime**: construção de grafos de conhecimento, parsing estruturado de catálogo transversal completo, bounded context maps dinâmicos ou árvores de dependência.
> 3. **(c) Geração ou transformação condicional de código-fonte (codegen/mutação)**: agentes de desenvolvimento, correção de bugs, autoria de testes, refatoração e manutenção estrutural em lote.

Se **NENHUMA** dessas três condições se aplicar, o agente é formalmente classificado como **"Gather-only"**:
- **Ação**: Remoção obrigatória de `context-mode/ctx_execute` e `context-mode/ctx_execute_file` do array `tools:`.
- **Invariante**: Retenção compulsória de `context-mode/ctx_batch_execute` (além de `ctx_search` e `ctx_index`), garantindo capacidade total de consulta em lote com economia de tokens.

---

## 3) Tabela Completa dos 26 Agents Gather-Only

Abaixo, a relação completa e aprovada dos 26 agentes classificados como "Gather-only" com a respectiva justificativa de enquadramento:

| # | Agente | Arquivo | Justificativa de Perfil Gather-Only (Não atende a/b/c) |
|---|---|---|---|
| 1 | `agent-auditor` | `.github/agents/agent-auditor.agent.md` | Audita conformidade estática de governança via inspeção declarativa e regras sem agregação computacional ou codegen. |
| 2 | `adr-sentinel` | `.github/agents/adr-sentinel.agent.md` | Guardião e catalogador documental de ADRs e conformidade arquitetural via leitura estática sem transformação de código. |
| 3 | `bug-triage` | `.github/agents/bug-triage.agent.md` | Triagem, categorização e coleta observacional de evidências de incidentes/bugs sem agregação numérica nem codegen. |
| 4 | `code-review` | `.github/agents/code-review.agent.md` | Inspeção e revisão estática de PRs e diffs de código via análise semântica sem mutação ou transformação. |
| 5 | `code-style-enforcer` | `.github/agents/code-style-enforcer.agent.md` | Verificação de estilo, formatação e conformidade de linters via inspeção de regras sem codegen. |
| 6 | `compliance-guardrails` | `.github/agents/compliance-guardrails.agent.md` | Auditoria de aderência a normas, licenças e guardrails legais/segurança via varredura documental. |
| 7 | `database-specialist` | `.github/agents/database-specialist.agent.md` | Análise consultiva de esquemas relacionais, índices e planos de execução sem geração direta de código. |
| 8 | `debugger` | `.github/agents/debugger.agent.md` | Investigação e diagnóstico de causas-raiz de falhas via inspeção de logs e código sem codegen. |
| 9 | `deep-search` | `.github/agents/deep-search.agent.md` | Varredura exaustiva de contexto, documentação e base de código via ferramentas de busca/batch sem runtime compute. |
| 10 | `devops-engineer` | `.github/agents/devops-engineer.agent.md` | Inspeção e diagnóstico de pipelines CI/CD, containers e IaC sem compilação condicional em runtime. |
| 11 | `docs-engineer` | `.github/agents/docs-engineer.agent.md` | Inspeção e estruturação documental técnica e diagramas estáticos sem execução de scripts no sandbox. |
| 12 | `feature-planner` | `.github/agents/feature-planner.agent.md` | Decomposição de requisitos e planejamento de histórias de usuário sem síntese de código. |
| 13 | `pr-gatekeeper` | `.github/agents/pr-gatekeeper.agent.md` | Verificação e validação de critérios de aceitação e gates de qualidade para PRs via inspeção estática. |
| 14 | `repo-hygiene-auditor` | `.github/agents/repo-hygiene-auditor.agent.md` | Inspeção de arquivos obsoletos, artefatos temporários e estrutura de repositório sem agregação computacional. |
| 15 | `requirements-analyst` | `.github/agents/requirements-analyst.agent.md` | Análise, eliciação e detalhamento funcional de requisitos de negócio sem codegen. |
| 16 | `runtime-verifier` | `.github/agents/runtime-verifier.agent.md` | Verificação observacional de integridade de runtime e logs via batch gathering sem processamento derivado. |
| 17 | `security-reviewer` | `.github/agents/security-reviewer.agent.md` | Análise estática de vulnerabilidades e brechas de segurança sem síntese nem mutação de código. |
| 18 | `tech-solution-architect` | `.github/agents/tech-solution-architect.agent.md` | Desenho de solução, padrões arquiteturais e análise de trade-offs conceituais sem codegen. |
| 19 | `test-strategy` | `.github/agents/test-strategy.agent.md` | Definição de pirâmide de testes e critérios de cobertura sem execução direta de scripts de transformação. |
| 20 | `ejb-arch-advisor` | `.github/agents/backend/ejb/ejb-arch-advisor.agent.md` | Consultoria arquitetural e padrões enterprise Java/EJB estritamente orientativa sem codegen. |
| 21 | `python-arch-advisor` | `.github/agents/backend/python/python-arch-advisor.agent.md` | Consultoria arquitetural e boas práticas no ecossistema Python sem geração de código em sandbox. |
| 22 | `spring-boot-arch-advisor` | `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` | Consultoria arquitetural e convenções no ecossistema Spring Boot sem mutação ou transformação. |
| 23 | `spring-reactive-arch-advisor` | `.github/agents/backend/spring-reactive/spring-reactive-arch-advisor.agent.md` | Consultoria arquitetural reativa (WebFlux/Reactor) orientativa sem execução de código. |
| 24 | `struts-arch-advisor` | `.github/agents/backend/struts/struts-arch-advisor.agent.md` | Consultoria arquitetural para sistemas legados Apache Struts sem geração de código. |
| 25 | `angular-arch-advisor` | `.github/agents/frontend/angular/angular-arch-advisor.agent.md` | Consultoria arquitetural frontend para ecossistema Angular sem codegen. |
| 26 | `react-arch-advisor` | `.github/agents/frontend/react/react-arch-advisor.agent.md` | Consultoria arquitetural frontend para ecossistema React sem codegen. |

---

## 4) Agentes "Gather+Process" Preservados

Todos os demais agentes do catálogo de governança retêm suas capacidades completas de `ctx_execute` e `ctx_execute_file`, enquadrando-se categoricamente nos critérios (a), (b) ou (c):
- **Executores de Governança e Fábrica**: `governance-maintainer` (codegen e manutenção em lote multi-arquivo), `governance-factory` (síntese de artefatos).
- **Mapeadores de Domínio e Grafo**: `codegraph-engine` (construção de grafos de nós e arestas), `ddd-bounded-context-mapper` (descoberta de agregados e limites de contexto), `business-rules-extractor` (extração algorítmica).
- **Desenvolvedores e Reparadores de Código (Mutadores)**: todos os especialistas `*-feature-developer`, `*-bug-fixer`, `*-test-writer`, `*-test-fixer`, `*-perf-tuner`, `*-ui-stylist`, `*-e2e-writer`, `*-migration-dev`, `adapter-generator`, `binding-initializer`.

---

## 5) Governança Sistêmica e Portão de Reúso (R-055 / Anti-Silo Fix)

- **Q1 (Impacto em artefatos irmãos/peers)**: Escopo expandido e consolidado para cobrir a totalidade dos 26 agentes Gather-only identificados no ecossistema transversal (raiz e stacks backend/frontend).
- **Q2 (Atualização de templates canônicos)**:
  - `governance-factory-patterns/SKILL.md`: inclusão do critério de corte (a)/(b)/(c) no Checklist de Qualidade Estrutural (§3) para criação de novos agentes.
  - `governance-audit-patterns/SKILL.md`: registro formal do **Smell 2.32** (*Capability Overreach de ctx_execute / ctx_execute_file em Agent Gather-only*).
- **Q3 (Teste determinístico no pytest)**:
  - Criação de `tests/governance_audit/test_ctx_execute_capability_profile.py` com validação estática de não-regressão.
