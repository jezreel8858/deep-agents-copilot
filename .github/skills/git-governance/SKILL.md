---
name: git-governance
description: Índice canônico (SSOT) de git workflow — branch naming, commits semânticos, PRs com matriz de risco e rollback, guardrail de segredos e changelog.
tier: 2
category: governance
triggers:
  - "como nomear branch"
  - "padrão de commit"
  - "convention de PR"
  - "git workflow"
  - "mensagem de commit"
  - "branch naming"
  - "matriz de risco"
  - "changelog"
tools: []
source_docs:
  - docs/ai-copilot/global-git-commit-instructions.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# Git Governance

> **Progressive Disclosure**: Nível 1 = frontmatter; Nível 2 = este índice (regras curtas); Nível 3 = `references/` (carregar apenas o necessário via `ctx_execute_file`/`ctx_search`).

Padroniza versionamento Git: histórico semântico, commits atômicos, PRs auditáveis e zero segredos. **SSOT única** consumida por `/commit` e `@pr-gatekeeper`.

## 1) Quando Usar

- ✅ Nomear branches, redigir commits, PR (título/descrição/risco/rollback) e entradas de CHANGELOG.
- ❌ Executar `git add/commit/push` de forma autônoma (R-031), resolver conflitos às cegas, substituir `@code-review`.

## 2) Mapa de Referências (Nível 3)

| Necessidade | Arquivo |
|---|---|
| Formato A/B, tipos, atomicidade, trailers | [`references/commit-formats.md`](references/commit-formats.md) |
| Template de PR + Plano de Rollback | [`references/pr-template.md`](references/pr-template.md) |
| Critérios de risco e blast radius | [`references/risk-matrix.md`](references/risk-matrix.md) |
| Defesa em camadas de segredos, regex | [`references/secrets-guardrail.md`](references/secrets-guardrail.md) |
| Keep a Changelog + mapeamento semântico | [`references/changelog.md`](references/changelog.md) |

## 3) Branch Naming

Formato: `<tipo>/<jira-id>-<descricao-kebab>` (ex.: `docs/governance-simplificar-binding-initializer`).

| Tipo | Uso |
|---|---|
| `feat/` `fix/` `refactor/` | Feature, bug, refatoração |
| `test/` `docs/` `chore/` | Testes, documentação, build/deps |
| `hotfix/` | Correção crítica em produção |

Regras: kebab-case; ID Jira quando existir; ≤ 60 caracteres.

## 4) Regras Essenciais de Commit

- `<tipo>(<escopo>): <resumo>` — imperativo PT-BR, sem ponto final, ≤ 72 colunas.
- Um commit = uma intenção (teste do "e"). Detalhes: `references/commit-formats.md`.

## 5) Pull Request

- Título em Conventional Commits; descrição conforme `references/pr-template.md`.
- **Matriz de Risco** (`references/risk-matrix.md`) e **Plano de Rollback** obrigatórios.
- Comandos de validação em inline code (anti-corrupção de cercas).

## 6) Segredos (R-010 / R-044)

Camada 3 (agente) bloqueante antes de qualquer mensagem/PR; achado → parar, reportar `arquivo:linha`, exigir rotação. Catálogo e camadas 1-2: `references/secrets-guardrail.md`.

## 7) Merge Strategy

| Estratégia | Quando |
|---|---|
| Squash merge | Features pequenas (1-3 commits) |
| Merge commit | Features grandes/releases |
| Rebase | ❌ Evitar em branches compartilhadas |

## 8) Conflitos de Merge/Rebase

Nunca `--abort` como fuga (só base errada ou pedido humano); diagnosticar hunk a hunk, preservar intenção de ambos os lados, sem refatorações acessórias, rodar checks antes de `--continue`; sem `git push --force` por agentes (R-031). Procedimento completo: `.github/skills/git-conflict-resolution-patterns/SKILL.md`.

## 9) Checklist Pré-PR

- [ ] Branch conforme convenção; commits atômicos e semânticos
- [ ] Testes passando; sem debug (`console.log`, `System.out.println`)
- [ ] Guardrail de segredos limpo (R-010)
- [ ] Matriz de Risco + Plano de Rollback preenchidos
- [ ] CHANGELOG atualizado (`references/changelog.md`)
- [ ] Nenhuma execução autônoma de `git commit`/`git push` (R-031)

## 10) Referências

- Conventional Commits: https://www.conventionalcommits.org/
- Keep a Changelog 1.1: https://keepachangelog.com/en/1.1.0/
- Regra 50/72: https://cbea.ms/git-commit/
- Consumidores: `.github/prompts/commit.prompt.md`, `.github/agents/pr-gatekeeper.agent.md`
