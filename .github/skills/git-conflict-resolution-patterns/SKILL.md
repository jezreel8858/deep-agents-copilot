---
name: git-conflict-resolution-patterns
description: >-
  Fornece protocolo determinístico para diagnosticar, investigar e resolver conflitos de merge, rebase ou cherry-pick em Git preservando a intenção semântica original de ambas as branches. Use quando um conflito precisar ser resolvido hunk a hunk com rastreabilidade de autoria e validação por testes. Não use para desfazer histórico (`git revert`) ou para resolução puramente automática sem revisão semântica.
tier: 2
category: process
triggers:
  - "conflito de merge"
  - "conflito de rebase"
  - "resolver conflito git"
  - "merge conflict"
  - "cherry-pick conflitante"
  - "hunk conflitante"
  - "divergência de branch"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/git-governance/SKILL.md
  - .github/skills/terminal-governance/SKILL.md
tools: []
---

# Git Conflict Resolution Patterns

## 0) Problema Resolvido & Princípios Fundamentais

Formaliza um protocolo determinístico de resolução de conflitos de merge/rebase/cherry-pick, evitando tanto a aceitação cega de um dos lados (`--ours`/`--theirs` em bloco) quanto a resolução puramente sintática que descarta a intenção original de uma das branches.

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao resolver marcadores de conflito (`<<<<<<<`, `=======`, `>>>>>>>`) resultantes de merge, rebase ou cherry-pick.
- Quando ambas as pontas do conflito possuem alterações legítimas que precisam ser fundidas semanticamente.
- Antes de qualquer commit de resolução de conflito, como gate de validação.

### ❌ Quando NÃO Usar
- Para reverter histórico completo (`git revert`) — fora de escopo desta skill.
- Para resolução automática de conflito sem revisão humana ou de agent (risco de perda silenciosa de intenção).
- Quando não há acesso seguro a terminal não-interativo — delegar para `terminal-governance`.

---

## 2) Protocolo de 4 Passos

### Passo 1 — Diagnóstico de Estado
1. `git --no-pager status` para localizar arquivos em conflito.
2. `git --no-pager diff` para inspecionar os hunks conflitantes e seus marcadores.

### Passo 2 — Busca de Fontes Primárias (Histórico)
1. `git --no-pager log --oneline -n 20 -- <arquivo>` para localizar commits/SHAs e PRs relacionados a cada ponta do conflito.
2. Ler a mensagem de commit de cada SHA para entender a intenção original antes de decidir qual trecho preservar.

### Passo 3 — Resolução Semântica Hunk-a-Hunk
1. Avaliar cada hunk individualmente — nunca aceitar `--ours`/`--theirs` em bloco para o arquivo inteiro.
2. Fundir as duas intenções quando não forem mutuamente exclusivas; escolher a intenção correta quando forem.
3. Remover os marcadores de conflito apenas após decisão fundamentada em evidência do Passo 2.

### Passo 4 — Validação por Testes/Linter Antes do Commit
1. Executar a suíte de testes e o linter do stack afetado sobre o arquivo resolvido.
2. Bloquear o commit se restar qualquer marcador de conflito residual ou falha de teste/lint.

---

## 3) Regra de Comandos Git Não-Interativos (R-035)

TODO comando git usado neste protocolo DEVE evitar pager bloqueante: sempre `git --no-pager diff`, `git --no-pager log`, `git --no-pager show`. Comandos git puros sem `--no-pager` são terminantemente proibidos por travarem a sessão aguardando `q`.

---

## 4) Checklist de Auto-Verificação

- [ ] Estado diagnosticado via `git --no-pager status`/`diff` antes de qualquer edição.
- [ ] Histórico de ambas as pontas investigado via `git --no-pager log` com SHAs/commits identificados.
- [ ] Cada hunk resolvido preservando a intenção original de ambos os lados (não apenas a sintaxe).
- [ ] Nenhum marcador de conflito residual (`<<<<<<<`/`=======`/`>>>>>>>`) no arquivo final.
- [ ] Testes e linter executados e verdes antes do commit de resolução.

---

## 5) Anti-padrões

| Anti-padrão | Risco / Sintoma | Correção Recomendada |
|---|---|---|
| Aceitar `--ours`/`--theirs` em bloco sem revisão | Perda silenciosa da intenção de uma das branches | Resolução hunk a hunk com leitura do histórico (Passo 2/3) |
| Commitar com marcador de conflito residual | Build quebrado / código corrompido em produção | Validar ausência de `<<<<<<<` antes do commit (Passo 4) |
| Resolver sem rodar testes/linter | Regressão silenciosa introduzida pela fusão | Passo 4 obrigatório antes de finalizar |
| Comando git com pager interativo travando sessão | Sessão travada aguardando `q` em "Processing..." | `--no-pager` obrigatório em todo comando (R-035) |

---

## 6) Consumidores Mapeados e Integrações

| Consumidor | Papel na Relação | Momento de Uso |
|---|---|---|
| `@pr-gatekeeper` | Preparação de PR/commit | Antes de finalizar submissão com histórico divergente |
| `@governance-maintainer` | Sincronização em lote de artefatos | Ao reconciliar branches de manutenção de governança |
| `@refactor-planner` | Planejamento de refatoração | Ao coordenar branches de longa duração (Branch by Abstraction) |

---

## 7) Referências e Documentação Conexa

- `CLAUDE.md` — R-035 (Terminal sem paginação interativa — Zero Pager Bloqueante).
- `.github/skills/git-governance/SKILL.md` — convenções de branch, commit e PR.
- `.github/skills/terminal-governance/SKILL.md` — boas práticas de uso de `run_in_terminal`.
