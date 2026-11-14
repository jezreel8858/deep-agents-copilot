# Planos de Implementação Técnica (`docs/plans/implementation/` — R-064)

Diretório canônico para persistência versionada dos **Planos de Implementação Técnica Detalhada** (`plan_type: "implementation"`) gerados no Gate 2 (R-064) imediatamente antes de qualquer mutação de código, respeitando o teto de concisão **R-066** (≤ 300 linhas).

---

## 1. Convenção de Nomenclatura

```text
docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<identificador-curto>.md
```

- `<AAAAMMDD-HHMMSS>`: Timestamp de elaboração no formato ISO compacto `AAAAMMDD-HHMMSS` (ex.: `20261113-120000`, regex `^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md# Planos de Implementação Técnica (`docs/plans/implementation/` — R-064)

Diretório canônico para persistência versionada dos **Planos de Implementação Técnica Detalhada** (`plan_type: "implementation"`) gerados no Gate 2 (R-064) imediatamente antes de qualquer mutação de código, respeitando o teto de concisão **R-066** (≤ 300 linhas).

---

## 1. Convenção de Nomenclatura

```text
docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<identificador-curto>.md
```

; proibidos prefixos `PLAN-`, `REQ-` ou nomes sem timestamp).
- `<workflow>`: Identificador do workflow canônico em minúsculas sem prefixo `workflow-` (ex.: `feature-development`, `bug-fix`, `code-refactoring`, `governance-maintenance`, `dependency-vulnerability-remediation`, `framework-migration`).
- `<identificador-curto>`: Slug kebab-case correspondente ao Plano de Planejamento aprovado em `docs/plans/<tipo>/`.

---

## 2. Propósito, Autoria Read-Only e Materialização Física

- **Quando é gerado**: Imediatamente após a aprovação humana do Plano de Planejamento (Gate 1 em `docs/plans/<tipo>/`) e **ANTES de qualquer mutação de código**.
- **Autoria (`author`)**:
  - Quando o workflow possui stack de domínio identificada: o respectivo especialista **`@<stack>-arch-advisor`** (Angular, React, Spring Boot, Spring Reactive, EJB, Struts, Python, Database — perfil 100% Read-Only) estrutura o plano técnico detalhado.
  - Em workflows agnósticos ou transversais: `@tech-solution-architect` ou `@agent-auditor` assume a autoria.
- **Materialização e Aprovação**: O agente autor (100% Read-Only) delega a escrita física deste arquivo em `docs/plans/implementation/` ao **`@docs-engineer`** (ou **`@governance-maintainer`** em fluxos de governança), e o Orquestrador submete o plano ao usuário via `ask_questions` para aprovação prévia obrigatória (Gate 2 R-064).

---

## 3. Frontmatter YAML Obrigatório (`plan_type: "implementation"`)

```yaml
---
status: DRAFT | APPROVED | IN_PROGRESS | COMPLETED | REJECTED
approved: false | true
author: "@<stack>-arch-advisor"
plan_type: "implementation"
created_at: "AAAA-MM-DD"
date: "AAAA-MM-DD"
workflow: "<WORKFLOW-CANONICO-R050>"
related-planning-doc: "docs/plans/<tipo>/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md"
plan_ref: "docs/plans/implementation/<AAAAMMDD-HHMMSS>-<workflow>-<slug>.md"
reversibility: "T1" | "T2" | "T3"
progress: 0
allowed_files:
  - "<caminho-ou-glob-permitido>"
---
```

---

## 4. Template de Plano de Implementação Técnica (Seções Obrigatórias)

1. **Frontmatter YAML de Implementação Canônico**: Incluindo obrigatoriamente `status`, `approved`, `author`, `plan_type: "implementation"`, `created_at`, `workflow`, `related-planning-doc` (apontando para o plano aprovado em `docs/plans/<tipo>/`), `allowed_files`, `reversibility` (`T1|T2|T3`) e `progress`.
2. **Vínculo com o Plano de Planejamento (`related-planning-doc`)**: Referência explícita ao documento aprovado no Gate 1 sob `docs/plans/<tipo>/`.
3. **Decisões de Design & Padrões Aplicados**: Princípios arquiteturais (SOLID, Clean Architecture, DDD, padrões GoF/stack), contratos de interface e invariantes adotadas na solução técnica.
4. **Escopo de Arquivos (`allowed_files`) e Sequência de Execução em Lote (Plan-Then-Batch, R-059)**: Lista exata dos arquivos a serem criados, alterados ou removidos e ordem cronológica de aplicação.
5. **Checklist GFM Unificado de Tarefas**:
   - Formato obrigatório: `- [ ] <descrição> {paralelizavel: bool, responsavel: "<agent>"}` com indicador agregado `Progresso: N/M tarefas concluídas`.
6. **Abordagem Técnica de Baixo Nível e Estratégia TDD**: Contratos de métodos/componentes, diffs conceituais planejados e casos de teste (unitários/integração/E2E) que validarão a implementação.
7. **Riscos de Regressão, Blast Radius e Estratégia de Rollback**: Plano de contingência por etapa (R-031 / R-050.2), coerente com o tier de reversibilidade declarado (`T1`/`T2`/`T3`).

---

## 5. 🔒 Checklist Defensivo Pré-Code-Review

Todo documento de implementação técnica em `docs/plans/implementation/` DEVE incorporar ao final o checklist defensivo com os seguintes itens obrigatórios:
- [ ] **Sanitização & Validação de Borda**: Validação estrita de tipos, tamanhos e formatos em todos os pontos de entrada e parâmetros externos.
- [ ] **Zero Hardcoded Secrets**: Ausência absoluta de credenciais, tokens de API, senhas ou certificados codificados no código ou fixtures.
- [ ] **Logging & Dados Sensíveis**: Mascaramento ou omissão de PII, senhas, tokens e dados sensíveis em logs de depuração e traces.
- [ ] **Controle de Acesso & Autorização**: Validação de escopos, papéis e permissões no nível de serviço/controlador para evitar broken object level authorization (BOLA/IDOR).
- [ ] **Tratamento Seguro de Falhas**: Exceções tratadas sem expor stacktraces ou dados internos ao usuário final, mantendo estado consistente.
- [ ] **Cobertura de Testes Defensivos**: Testes cobrindo fluxos de erro, inputs maliciosos/inválidos e limites de contorno.
