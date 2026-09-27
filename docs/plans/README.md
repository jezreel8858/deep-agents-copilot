# Planos de Planejamento (R-064)

Diretório canônico para persistência versionada dos **Planos de Planejamento** gerados no início dos Workflows Canônicos (R-050) que envolvem mutação de código ou análises técnicas amplas, conforme a norma **R-064**.

## Convenção de Nomenclatura

```
docs/plans/<AAAAMMDD>-<workflow>-<identificador-curto>.md
```

- `<AAAAMMDD>`: Data da elaboração no formato ISO básico (ex.: `20260401`).
- `<workflow>`: Identificador do workflow canônico em minúsculas sem prefixo `workflow-` (ex.: `feature-development`, `bug-fix`, `refactoring`, `governance-maintenance`, `dependency-vulnerability-remediation`, `framework-migration`).
- `<identificador-curto>`: Slug kebab-case do objetivo ou defeito tratado (ex.: `duplo-gate-r064`, `auth-token-refresh`, `upgrade-spring-boot-3`).

## Propósito e Autoria

- **Quando é gerado**: Ao final da etapa de elicitação de requisitos, RCA, escopo macro ou blueprint de viabilidade (Etapa 1/2 de cada workflow em R-050).
- **Autoria**: O agente especialista dono canônico da etapa inicial de planejamento do workflow (ex.: `@requirements-analyst` / `@tech-solution-architect` em Feature; `@bug-triage` em Bug-Fix; `@refactor-planner` em Refactoring; `@agent-auditor` / `@repo-hygiene-auditor` em Governance; `@tech-solution-architect` em Migration).
- **Materialização e Aprovação**: Como os especialistas analíticos operam em perfil Read-Only, o Orquestrador Raiz materializa o Markdown neste diretório e aciona compulsoriamente `ask_questions` para aprovação humana explícita antes de avançar para a fase técnica subsequente.
- **Conteúdo Mínimo Obrigatório**:
  1. Objetivo e motivação técnica/negócio.
  2. Escopo delimitado e artefatos/arquivos impactados (mapeados via `@code-knowledge-graph` quando aplicável).
  3. Não-escopo explícito.
  4. Riscos técnicos e blast radius inicial.
  5. Critério de aceite e Definition of Done.
