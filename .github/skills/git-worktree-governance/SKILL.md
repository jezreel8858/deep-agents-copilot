---
name: git-worktree-governance
description: Diretrizes de ciclo de vida e isolamento para execução de agentes paralelos e explorações especulativas via Git Worktrees sem colisão de arquivos ou concorrência de build.
tier: 2
category: governance
triggers:
  - "git worktree"
  - "worktree governance"
  - "execução paralela de agentes"
  - "parallel agent isolation"
  - "branch especulativa"
  - "workspace isolation"
tools:
  - "run_in_terminal"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/skills/terminal-governance/SKILL.md"
  - ".github/skills/git-governance/SKILL.md"
---

# Git Worktree Governance

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description` em 3ª pessoa, `tier: 2`, `category: governance` e triggers.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` estabelecendo ciclo de vida de worktrees, isolamento de working directories, comandos seguros não-interativos e prevenção de colisão de lockfiles.
> - **Nível 3 (Recursos Suplementares)**: Governança de terminal em `.github/skills/terminal-governance/SKILL.md`.

Quando múltiplos agentes de IA codificam simultaneamente no mesmo repositório, uma única pasta de trabalho compartilhada causa concorrência destrutiva: colisões em lockfiles (`package.json`, `pom.xml`, `poetry.lock`), reescritas concorrentes de arquivos, locks de índice Git (`index.lock`) e falhas de compilação cruzada.

O padrão **Git Worktree** resolve essa limitação ao permitir que cada agente executor opere em uma working directory e branch isoladas, compartilhando uma única base de objetos Git (`.git`), sem a sobrecarga de clonar o repositório completo.

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Em tarefas paralelas marcadas com `[P]` (R-018) envolvendo escrita ou refatoração concorrente.
- Em refatorações estruturais ou migrações complexas que demandem exploração especulativa (testar abordagens A e B sem sujar o branch principal).
- Quando subagentes executores distintos forem despachados simultaneamente para componentes isolados (ex.: frontend e backend).
- Em sessões longas de auto-remediação ou TDD com múltiplos ciclos de tentativa.

### ❌ Quando NÃO Usar
- Em tarefas de análise estritamente read-only (consultas via AST, `code-knowledge-graph`, `deep-search` ou revisões de código) — dispensam isolamento de working directory.
- Para alterações pontuais sequenciais em um único arquivo (onde `Single-Turn Batching` R-046 é suficiente).
- Em repositórios sem controle Git inicializado.

---

## 2) Ciclo de Vida do Git Worktree para Agentes

O ciclo de vida obrigatório é composto por 5 etapas determinísticas:

```
[1. SETUP]     git worktree add .worktrees/<nome-tarefa> -b <tipo>/<nome-tarefa>
    ↓
[2. ISOLATE]   Agente executor opera estritamente restrito a .worktrees/<nome-tarefa>
    ↓
[3. VERIFY]    Build e testes executados isoladamente no diretório do worktree
    ↓
[4. MERGE]     Merge de volta para a branch de trabalho (após green test verificado)
    ↓
[5. CLEANUP]   git worktree remove .worktrees/<nome-tarefa>
```

---

## 3) Comandos Canônicos e Flags Obrigatórias

Todo comando Git executado no terminal deve desativar o pager interativo via `--no-pager` (R-035).

### 3.1) Criação do Worktree Isolado
Cria um diretório dedicado para o agente com uma nova branch de trabalho:

```bash
git --no-pager worktree add .worktrees/task-refactor -b refactor/task-refactor
```

### 3.2) Listagem e Auditoria de Worktrees Ativos
Inspeciona todos os diretórios de trabalho conectados ao repositório:

```bash
git --no-pager worktree list
```

### 3.3) Remoção e Limpeza Pós-Execução
Remove o diretório de trabalho isolado após a conclusão e merge da tarefa:

```bash
git --no-pager worktree remove .worktrees/task-refactor
```

### 3.4) Pruning de Referências Órfãs
Limpa metadados de worktrees excluídos manualmente do disco:

```bash
git --no-pager worktree prune
```

---

## 4) Diretrizes de Isolamento e Concorrência

1. **Localização Canônica Padronizada**:
   - Todo worktree criado para agentes deve residir compulsoriamente no diretório `.worktrees/` na raiz do repositório.
   - O diretório `.worktrees/` deve constar no `.gitignore` do repositório para evitar versionamento acidental.

2. **Isolamento de Dependências**:
   - Em ecossistemas Node.js ou Python, dependências do worktree devem ser instaladas de forma isolada ou compartilhadas via links simbólicos (`pnpm`, `uv` cache), prevenindo locks no diretório raiz.

3. **Restrição de Escopo do Agente**:
   - Ao despachar um agente executor para um worktree, o caminho relativo da tarefa deve ser ancorado dentro de `.worktrees/<tarefa>/`.
   - É expressamente proibido ao agente no worktree referenciar ou mutar arquivos da raiz principal fora do seu diretório isolado.

---

## 5) Checklist de Limpeza e Merge Seguro

Antes de encerrar o ciclo do worktree:

- [ ] Suíte de testes e linters 100% verde dentro da pasta do worktree?
- [ ] Diffs inspecionados com `git --no-pager diff` confirmando ausência de arquivos acidentais?
- [ ] Commit semântico gerado conforme a convenção de `git-governance`?
- [ ] Merge ou rebase realizado para a branch alvo sem conflitos pendentes?
- [ ] Worktree removido com `git --no-pager worktree remove`?
- [ ] `git --no-pager worktree prune` executado para sanitizar metadados residuais?

---

## 6) Anti-padrões

- ❌ Executar dois agentes mutativos em paralelo na mesma working directory sem isolamento de worktree.
- ❌ Executar comandos `git worktree` sem a flag `--no-pager` (R-035).
- ❌ Criar worktrees fora do padrão `.worktrees/` (ex.: pastas soltas na raiz do projeto).
- ❌ Deixar worktrees órfãos ou não removidos após a conclusão do plano.
- ❌ Fazer merge para a branch principal sem validação prévia de testes no ambiente isolado.

