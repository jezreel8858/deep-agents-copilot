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
- **Conteúdo Mínimo Obrigatório** (conforme `.github/skills/documentation-writing-patterns/SKILL.md` § 2.1 — Categoria PLANEJAMENTO):
  1. Front-matter YAML de planejamento canônico (`status: draft`, `date`, `autor`, `workflow`, `related-plan: <path | N/A>`).
  2. Contexto/Problema, formulação do objetivo e motivação técnica/negócio.
  3. Opções consideradas e Decisão técnica adotada.
  4. Alternativas Rejeitadas (seção obrigatória justificando descartes e trade-offs).
  5. Escopo delimitado, artefatos/arquivos impactados (mapeados via `@codegraph-engine` quando aplicável) e Não-escopo explícito.
  6. Riscos técnicos, consequências e blast radius inicial.
  7. Critério de aceite e Definition of Done (único a nível de documento, sem checklist obrigatório de execução).

## 🛡️ Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

Todo documento de planejamento DEVE incluir formalmente a análise de segurança prévia (Shift-Left Security):
- **Vetores de Risco & Superfície de Ataque**: Mapeamento preventivo contra vulnerabilidades comuns (STRIDE, OWASP Top 10, CWEs relevantes ao domínio).
- **Requisitos de Segurança Mandatórios**: Autenticação, autorização (RBAC/ABAC), criptografia em repouso e trânsito, proteção de dados sensíveis (LGPD/GDPR).
- **Validações de Borda**: Contratos de entrada estritos, validação de schemas, sanitização de inputs e mitigação de injeções.
- **Trilha de Auditoria e Observabilidade**: Logging seguro de eventos de segurança sem vazamento de PII ou credenciais.

## 🛡️ Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

Todo documento de planejamento DEVE incluir formalmente a análise de segurança prévia (Shift-Left Security):
- **Vetores de Risco & Superfície de Ataque**: Mapeamento preventivo contra vulnerabilidades comuns (STRIDE, OWASP Top 10, CWEs relevantes ao domínio).
- **Requisitos de Segurança Mandatórios**: Autenticação, autorização (RBAC/ABAC), criptografia em repouso e trânsito, proteção de dados sensíveis (LGPD/GDPR).
- **Validações de Borda**: Contratos de entrada estritos, validação de schemas, sanitização de inputs e mitigação de injeções.
- **Trilha de Auditoria e Observabilidade**: Logging seguro de eventos de segurança sem vazamento de PII ou credenciais.
