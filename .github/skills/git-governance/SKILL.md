---
name: git-governance
description: Convenções de git workflow, branch naming, commit standards e PR guidelines para projetos enterprise.
tier: 2
category: governance
triggers:
  - "como nomear branch"
  - "padrão de commit"
  - "convention de PR"
  - "git workflow"
  - "mensagem de commit"
  - "branch naming"
tools: []
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
---

# Git Governance

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description` em 3ª pessoa, `tier: 2`, `category: governance` e triggers.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` definindo branch naming, commits semânticos, PR guidelines e guardrails de atomicidade.
> - **Nível 3 (Recursos Suplementares)**: Templates e regras globais em `docs/ai-copilot/`.

Esta skill padroniza o fluxo de versionamento Git em projetos enterprise, garantindo histórico semântico rastreável, atomicidade de entregas e prevenção contra vazamento de segredos ou commits autônomos por agentes de IA.

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao nomear novas branches (`feature/`, `fix/`, `refactor/`, `chore/`).
- Ao redigir mensagens de commit semântico conforme Conventional Commits e diretrizes globais.
- Ao estruturar templates e descrições de Pull Request com matriz de risco.
- No prompt `/commit` e no agent `@pr-gatekeeper`.

### ❌ Quando NÃO Usar
- Para execução autônoma de `git commit` ou `git push` (expressamente proibido por R-031).
- Para resolver conflitos de merge às cegas sem inspeção humana.
- Como substituto de revisão técnica de código (escopo de `@code-review`).

---

## 2) Branch Naming Convention

**Formato padrão:**

```
<tipo>/<jira-id>-<descricao-kebab>
```

| Tipo | Uso |
|------|-----|
| `feat/` | Nova funcionalidade |
| `fix/` | Correção de bug |
| `refactor/` | Refatoração sem mudança de comportamento |
| `test/` | Apenas testes |
| `docs/` | Apenas documentação |
| `chore/` | Build, deps, configuração |
| `hotfix/` | Correção crítica em produção |

**Exemplos:**

```
docs/governance-simplificar-binding-initializer
```

**Regras:**
- Sempre kebab-case
- ID Jira quando existir (`<PROJETO>-<numero>`)
- Descrição em PT-BR ou EN (consistente no projeto)
- Máximo 60 caracteres no total

---

## 2) Commit Convention (Conventional Commits)

Use `/commit` para gerar a mensagem automaticamente. Referência rápida:

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[trailers opcionais]
```

**Tipos:**

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova feature |
| `fix` | Bug fix |
| `refactor` | Refactor |
| `test` | Testes |
| `docs` | Documentação |
| `chore` | Build/deps/config |
| `perf` | Performance |

**Regras da mensagem:**
- Imperativo, PT-BR: "adiciona", "corrige", "remove", "extrai"
- Sem ponto final na primeira linha
- ≤ 72 caracteres na primeira linha
- Corpo separado por linha em branco

---

## 3) Pull Request Guidelines

**Título do PR** deve seguir Conventional Commits:

```
feat(auth): adiciona autenticação por token JWT
fix(entity): corrige NPE em PecaEntity ao buscar por ID nulo
```

**Template mínimo de PR:**

> **Diretriz de Renderização Anti-Corrupção**: Na seção "Como testar", prefira comandos formatados como código inline (`pytest tests/modulo -v` ou `mvn test`) para evitar conflito de cercas aninhadas quando a descrição for encapsulada em blocos markdown de documentação ou PRs.

```markdown
## O que foi feito
- <item 1>
- <item 2>

## Tipo de mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Refactor
- [ ] Docs

## Como testar
1. Executar testes: `pytest tests/modulo -v`
2. Validar comportamento funcional: <passo 2>

## Checklist
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Sem secrets expostos
- [ ] CLAUDE.md consultado para convenções
```

---

## 4) Merge Strategy

| Estratégia | Quando usar |
|-----------|------------|
| **Squash merge** | Features pequenas (1-3 commits) — mantém histórico limpo |
| **Merge commit** | Features grandes ou releases — preserva contexto |
| **Rebase** | ❌ Evitar em branches compartilhadas |

---

## 5) Checklist Pré-PR

- [ ] Branch nomeada conforme convenção?
- [ ] Commits seguem Conventional Commits (use `/commit`)?
- [ ] Testes passando?
- [ ] Sem `console.log` / `System.out.println` de debug?
- [ ] Sem credenciais expostas (R-010)?
- [ ] Nenhuma execução autônoma de `git commit`/`git push` por agentes de IA (R-031)?
- [ ] PR title segue o formato?
- [ ] Descrição clara do que e por quê?

---

## 6) Referências

- Conventional Commits: https://www.conventionalcommits.org/
- `/commit` prompt: `.github/prompts/commit.prompt.md`
- Regras de segurança: `CLAUDE.md` R-010

