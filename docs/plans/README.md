# Planos de Workflow e Arquitetura — Taxonomia Unificada `docs/plans/<tipo>/` (R-064)

Diretório canônico central para persistência versionada de **todos os Planos de Planejamento e Implementação** elaborados nos Workflows Canônicos (R-050), conforme a norma **R-064** e o limite de concisão **R-066** (≤ 300 linhas).

---

## 1. Convenção de Nomenclatura e Estrutura de Diretórios

```text
docs/plans/<tipo>/<AAAAMMDD-HHMMSS>-<identificador-curto>.md
```

- `<tipo>`: Uma das **8 subpastas canônicas** correspondentes ao discriminador `plan_type` do frontmatter YAML:
  - `docs/plans/feature/` (`plan_type: "feature"`)
  - `docs/plans/refactor/` (`plan_type: "refactor"`)
  - `docs/plans/architecture/` (`plan_type: "architecture"`)
  - `docs/plans/implementation/` (`plan_type: "implementation"`)
  - `docs/plans/test-strategy/` (`plan_type: "test-strategy"`)
  - `docs/plans/bug-triage/` (`plan_type: "bug-triage"`)
  - `docs/plans/requirements/` (`plan_type: "requirements"`)
  - `docs/plans/governance/` (`plan_type: "governance"`)
- `<AAAAMMDD-HHMMSS>`: Timestamp de elaboração no formato ISO compacto `AAAAMMDD-HHMMSS` (ex.: `20261113-120000`), exigido em todas as 8 subpastas (regex `^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md# Planos de Workflow e Arquitetura — Taxonomia Unificada `docs/plans/<tipo>/` (R-064)

Diretório canônico central para persistência versionada de **todos os Planos de Planejamento e Implementação** elaborados nos Workflows Canônicos (R-050), conforme a norma **R-064** e o limite de concisão **R-066** (≤ 300 linhas).

---

## 1. Convenção de Nomenclatura e Estrutura de Diretórios

```text
docs/plans/<tipo>/<AAAAMMDD-HHMMSS>-<identificador-curto>.md
```

- `<tipo>`: Uma das **8 subpastas canônicas** correspondentes ao discriminador `plan_type` do frontmatter YAML:
  - `docs/plans/feature/` (`plan_type: "feature"`)
  - `docs/plans/refactor/` (`plan_type: "refactor"`)
  - `docs/plans/architecture/` (`plan_type: "architecture"`)
  - `docs/plans/implementation/` (`plan_type: "implementation"`)
  - `docs/plans/test-strategy/` (`plan_type: "test-strategy"`)
  - `docs/plans/bug-triage/` (`plan_type: "bug-triage"`)
  - `docs/plans/requirements/` (`plan_type: "requirements"`)
  - `docs/plans/governance/` (`plan_type: "governance"`)
; proibidos prefixos `PLAN-`, `REQ-` ou nomes sem timestamp; em `docs/plans/implementation/` segue `<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md`).
- `<workflow>`: Identificador do workflow canônico em minúsculas sem prefixo `workflow-` (ex.: `feature-development`, `bug-fix`, `code-refactoring`, `governance-maintenance`, `dependency-vulnerability-remediation`, `framework-migration`).
- `<identificador-curto>`: Slug kebab-case do objetivo ou defeito tratado.

---

## 2. Taxonomia das 8 Subpastas Canônicas (`docs/plans/<tipo>/`)

| Subpasta (`docs/plans/<tipo>/`) | `plan_type` | Propósito Canônico | Workflows Principais (R-050) |
| :--- | :--- | :--- | :--- |
| `docs/plans/feature/` | `feature` | Planos funcionais de feature, fatiamento vertical de épicos/histórias e escopo de entrega. | `WORKFLOW-FEATURE-DEVELOPMENT` |
| `docs/plans/refactor/` | `refactor` | Planos de refatoração estrutural em ondas atômicas, extração de módulos e blast radius. | `WORKFLOW-CODE-REFACTORING` |
| `docs/plans/architecture/` | `architecture` | Blueprints de solução multi-stack, migração de frameworks e topologia arquitetural. | `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-TECHNICAL-ANALYSIS` |
| `docs/plans/implementation/` | `implementation` | Planos técnicos de implementação por stack (Gate 2 R-064) com allowlist de arquivos e passos TDD. | Todos os workflows com mutação de código |
| `docs/plans/test-strategy/` | `test-strategy` | Planos de estratégia de testes, pirâmide de cobertura, contratos de integração e E2E. | `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-BUG-FIX` |
| `docs/plans/bug-triage/` | `bug-triage` | Planos de RCA (Root Cause Analysis), reprodução determinística, blast radius e hipótese de fix. | `WORKFLOW-BUG-FIX`, `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` |
| `docs/plans/requirements/` | `requirements` | Documentos de elicitação de requisitos, critérios Given/When/Then e matriz de rastreabilidade. | `WORKFLOW-FEATURE-DEVELOPMENT` (Etapa 1) |
| `docs/plans/governance/` | `governance` | Planos de manutenção de governança, auditoria de catálogo e evolução de skills/agents/prompts. | `WORKFLOW-GOVERNANCE-MAINTENANCE` |

---

## 3. Matriz Agente Autor (100% Read-Only) → Skill → Template → Subpasta → Agente Escritor Físico

Os agentes planejadores, consultores arquiteturais (`*-arch-advisor`), analistas de requisitos e agentes de triagem operam sob perfil estritamente **100% Read-Only** (R-025). Eles estruturam o plano conforme o template da skill correspondente e delegam a persistência física em disco ao `@docs-engineer` (ou `@governance-maintainer` em fluxos de governança) antes do checkpoint de aprovação humana via `ask_questions` (R-064).

| Agente Autor (100% Read-Only) | Skill Dono do Template | `plan_type` / Template | Subpasta Canônica | Agente Escritor Físico |
| :--- | :--- | :--- | :--- | :--- |
| `@requirements-analyst` | `.github/skills/requirements-engineering/SKILL.md` | `requirements` (Template de Engenharia de Requisitos) | `docs/plans/requirements/` | `@docs-engineer` |
| `@feature-planner` | `.github/skills/agile-Work-Item-Planning/SKILL.md` | `feature` (Template de Plano Funcional de Feature) | `docs/plans/feature/` | `@docs-engineer` |
| `@refactor-planner` | `.github/skills/refactoring-patterns/SKILL.md` | `refactor` (Template de Plano de Refatoração em Ondas) | `docs/plans/refactor/` | `@docs-engineer` |
| `@tech-solution-architect` | `.github/skills/architecture-patterns/SKILL.md` | `architecture` (Template de Blueprint Arquitetural) | `docs/plans/architecture/` | `@docs-engineer` |
| `@bug-triage` | `.github/skills/debugging-strategies/SKILL.md` | `bug-triage` (Template de Triagem e RCA) | `docs/plans/bug-triage/` | `@docs-engineer` |
| `@agent-auditor` / `@repo-hygiene-auditor` | `.github/skills/agent-governance-standards/SKILL.md` | `governance` (Template de Manutenção de Governança) | `docs/plans/governance/` | `@docs-engineer` / `@governance-maintainer` |
| `@<stack>-arch-advisor` (Python, Spring Boot, WebFlux, EJB, Struts, React, Angular, Database) | `.github/skills/documentation-writing-patterns/SKILL.md` | `implementation` (Template de Plano de Implementação Técnica) | `docs/plans/implementation/` | `@docs-engineer` |
| `@<stack>-arch-advisor` / `@tech-solution-architect` | `.github/skills/test-strategy-and-piramide/SKILL.md` | `test-strategy` (Template de Estratégia e Pirâmide de Testes) | `docs/plans/test-strategy/` | `@docs-engineer` |

---

## 4. Frontmatter YAML Comum Obrigatório (R-064)

Todo arquivo persistido sob `docs/plans/<tipo>/*.md` (exceto `README.md`) DEVE iniciar com o frontmatter YAML canônico abaixo:

```yaml
---
status: DRAFT | APPROVED | IN_PROGRESS | COMPLETED | REJECTED
approved: false | true
author: "@<agent-autor-canonico>"
plan_type: "feature" | "refactor" | "architecture" | "implementation" | "test-strategy" | "bug-triage" | "requirements" | "governance"
created_at: "AAAA-MM-DD"
date: "AAAA-MM-DD"
workflow: "<WORKFLOW-CANONICO-R050>"
related-planning-doc: "docs/plans/<tipo>/<arquivo>.md | N/A — plano raiz (<WORKFLOW>)"
allowed_files:
  - "<glob-ou-caminho-explicito>"
---
```

---

## 5. Template Base de Plano de Planejamento (R-064 / R-066)

### 1. Contexto e Objetivo
- Problema diagnosticado, motivação técnica/negócio e formulação clara do objetivo.

### 2. Opções Consideradas e Decisão Técnica Adotada
- Comparativo objetivo das abordagens avaliadas e justificativa da decisão escolhida.

### 3. Alternativas Rejeitadas
- Seção obrigatória documentando os descartes e trade-offs técnicos.

### 4. Escopo Delimitado, Arquivos Impactados e Não-Escopo
- Artefatos/arquivos mapeados (via `@codegraph-engine` quando aplicável) e fronteiras explícitas de Não-Escopo.

### 5. Riscos Técnicos, Blast Radius e Estratégia de Rollback
- Matriz de riscos, raio de impacto inicial e procedimento determinístico de reversão.

### 6. Critérios de Aceitação e Definition of Done (DoD)
- Critérios verificáveis (CA-01..CA-NN) exigidos para encerramento do workflow.

## 7. Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)

Todo documento de planejamento DEVE incluir formalmente a análise de segurança prévia (Shift-Left Security):
- **Vetores de Risco & Superfície de Ataque (STRIDE)**: Mapeamento preventivo contra vulnerabilidades comuns (STRIDE — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege; OWASP Top 10 e CWEs relevantes à superfície de ataque).
- **Autenticação e Autorização**: Controles mandatórios de identidade, sessão, RBAC/ABAC e prevenção de privilégio excessivo.
- **Dados Sensíveis e LGPD/GDPR**: Classificação de dados, mascaramento de PII em logs/traces, criptografia em trânsito e em repouso.
- **Dependências e Validações de Borda**: Auditoria de pacotes/dependências (SCA/Reachability), validação estrita de schemas, sanitização de inputs e mitigação de injeções.
