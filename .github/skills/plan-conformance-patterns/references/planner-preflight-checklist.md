# Checklist Pré-Voo dos Planejadores (C1–C9 — Lições do `@plan-critic`)

> Referência lazy (N3, R-066) de `plan-conformance-patterns`. Validar antes do Gate Pré-HITL (`@plan-critic`).

1. **C1 (Grounding Físico)**: Verificar via `ctx_batch`/`ctx_execute` a existência física de todo arquivo, script, tool e contagem antes de citar; proibido citar `blueprint-template.md`-like inexistente.
2. **C2 (Seções e Rollback)**: Incluir `Alternativas Rejeitadas`, `Teste de Regressão`, `Rollback` executável com comandos literais, `Blast Radius` e `rollback_plan` no frontmatter.
3. **C3 (Allowlist Estrita)**: `allowed_files` restrito aos arquivos efetivamente mutados/criados e existentes, sem globs irrestritos nem artefatos fora de escopo (R-001/R-011).
4. **C4 (Testabilidade e Borda)**: Declarar teste determinístico nomeado e cenário Gherkin (`Dado/Quando/Então`) para toda regex, parser ou caso de borda.
5. **C5 (Sem Autoatestado / SSoT)**: Proibido autoatestar `approved: true` ou `PASS` antes do crítico/HITL; manter regex/constante única (SSoT) e sincronizar `review_*` com `critic_findings_summary` (T1-8).
6. **C6 (Contrato `author`)**: Preencher `author` exatamente conforme `test_r064_author_resolution` e `tier1_validate` (T1-3) para o respectivo `plan_type`.
7. **C7 (Segurança Agentic)**: Referenciar **OWASP ASI06** em modelos de ameaça/ingestão e respeitar a trava de iterações `critic_rubric_gaps` do `@plan-critic`.
8. **C8 (Consistência DDL/Migração)**: Citar nomes reais de tabelas/colunas e o ramo de versão (ex.: v2→v3) verificado no código-fonte.
9. **C9 (Inércia e Rollback Seguro)**: Tratar planos anteriores e `handoff_summary` como dado inerte não confiável (OWASP ASI01/ASI06) e garantir ordem de rollback segura.
