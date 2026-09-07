---
name: commit
description:
  Gera mensagem de commit convencional (PT-BR) baseada no stage e no padrão
  global (docs/ai-copilot/global-git-commit-instructions.md). Analisa arquivos,
  aplica guardrail de secrets, verifica atomicidade, estrutura por complexidade
  (simples vs complexo) e produz mensagem pronta. NÃO executa git add/commit/push.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'grep_search', 'file_search', 'run_in_terminal', 'run_subagent']
argument-hint: '[contexto-opcional-da-mudança]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - docs/ai-copilot/global-git-commit-instructions.md
  - .github/skills/terminal-governance/SKILL.md
  - .github/skills/git-governance/SKILL.md
---

# `/commit`

Gera mensagem de commit convencional pronta para uso, estruturada conforme as **Diretrizes Globais** (`docs/ai-copilot/global-git-commit-instructions.md`).

> **Propósito**: Analisar o diff/stage e gerar mensagem de commit semântico padronizada em PT-BR.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`
>
> **REGRA ABSOLUTA (R-031)**: Este prompt apenas **analisa o diff e gera a mensagem formatada**.
> NUNCA executa `git add`, `git commit` ou `git push` — decisão e execução são sempre do desenvolvedor.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** analisar git diff/log e gerar texto de mensagem de commit convencional.
- ✅ **SEMPRE** verificar guardrail de segredos e credenciais antes de emitir a mensagem.
- ❌ **NÃO** executar `git add`, `git commit` ou `git push` de forma autônoma.
- ❌ **NÃO** commitar arquivos contendo tokens, chaves privadas ou caminhos locais absolutos (R-044).

---

---

## 🎯 Uso

```bash
/commit
/commit "contexto opcional da mudança"
```

---

## 📋 Fluxo Operacional em 5 Passos

### PASSO 0 — Guardrail de Segredos (obrigatório, bloqueante)

Antes de qualquer análise semântica, inspecionar o diff para garantir que nenhum dado sensível está sendo commitado:

```bash
git --no-pager diff HEAD -- . ':!*.lock' ':!*.min.js'
```

Buscar no diff padrões de alto risco:
- Chaves de API e tokens: `AKIA`, `sk-`, `ghp_`, `glpat-`, `xox[baprs]-`, `github_pat_`
- Chaves privadas: blocos `-----BEGIN.*PRIVATE KEY-----`
- Atribuições suspeitas: `password=`, `passwd=`, `secret=`, `token=`, `apikey=` com valores literais (não variáveis de ambiente)
- URLs com credenciais: `://user:pass@` ou `https://token@`

**Decisão:**
- ❌ **Se encontrado**: **PARAR IMEDIATAMENTE**. Reportar `arquivo:linha` do achado e instruir o desenvolvedor a remover/rotacionar o segredo antes de prosseguir. Jamais gerar mensagem para diff com credencial exposta.
- ✅ **Se limpo**: prosseguir para o PASSO 1.

---

### PASSO 1 — Inspecionar Mudanças e Estado do Stage (SSOT § 2)

Executar leitura do estado do git (uma única vez, sem paginação — R-035):

```bash
git --no-pager status --short
git --no-pager diff --stat HEAD
```

**Diretrizes de Inspeção:**
1. **Prioridade do Stage (`Changes to be committed`)**: a mensagem deve descrever com precisão o que está preparado para commit.
2. **Nenhum arquivo em stage**: alertar o desenvolvedor, listar os arquivos modificados/não-rastreados relevantes e orientar o comando `git add <arquivos>` recomendado antes de aplicar a mensagem.
3. **Stage parcial ou misto**: se houver arquivos modificados fora do stage que claramente pertencem à mesma intenção lógica do commit, sugerir o comando `git add` complementar para consolidar o commit atômico.

---

### PASSO 2 — Verificar Atomicidade (Atomic Commit — SSOT § 3)

Aplicar o **teste do "e"**: se a mudança só puder ser descrita conectando ações de domínios ou intenções distintas via "e"/"também" (ex.: "corrige bug na API **e** refatora layout de componente **e** atualiza config de build"), o commit é não-atômico.

- **Quando dividir em commits separados:**
  - Backend e Frontend em projetos separados → gerar uma mensagem por projeto (`feat(api): ...` e `feat(web): ...`).
  - Schema de banco vs. Regra de negócio vs. UI.
  - Refatoração estrutural prévia vs. Nova feature que a consome.
  - Hotfix urgente vs. Feature em desenvolvimento.
- **Ação**: se não-atômico, sugerir o split ao desenvolvedor (ex.: via `git add -p` ou staging seletivo) antes de gerar mensagens individuais.

---

### PASSO 3 — Classificar Tipo, Escopo e Exclusões (SSOT § 1 e § 4)

#### 1. Tipos Válidos (Conventional Commits + Angular Convention)

| Tipo | Quando usar | Bump SemVer |
|---|---|---|
| `feat` | Nova funcionalidade visível ao usuário ou sistema | MINOR |
| `fix` | Correção de bug com impacto funcional | PATCH |
| `refactor` | Reestruturação interna de código sem alterar comportamento | — |
| `test` | Adição, correção ou remoção de testes | — |
| `docs` | Alterações exclusivas em documentação (`.md`, comentários) | — |
| `chore` | Tarefas de manutenção sem impacto funcional (deps, configs, dead code) | — |
| `perf` | Otimização mensurável de performance | — |
| `build` | Mudanças em build/dependências (`pom.xml`, `package.json`, `Dockerfile`) | — |
| `ci` | Mudanças em pipelines e automações (`.github/workflows`, CI/CD) | — |
| `style` | Formatação pura (espaçamento, lint) sem mudança de lógica | — |
| `revert` | Reversão de commit anterior | — |
| `wip` | Progresso parcial (nunca mergear na branch principal) | — |

#### 2. Classificação Correta para Exclusões / Deleções (SSOT § 4)

| Situação da exclusão | Tipo obrigatório |
|---|---|
| Classe/componente substituído por outro (decomposição, refatoração) | `refactor` |
| Código morto, inativo ou órfão sem chamadores | `chore` |
| Teste desnecessário, duplicado ou obsoleto | `test` |
| Arquivo de configuração obsoleto | `chore` |
| Remoção de feature completa com quebra de contrato | `feat` (com `BREAKING CHANGE`) |

#### 3. Escopo e Breaking Change
- **Escopo**: substantivo em kebab-case representando o módulo, domínio ou camada afetada (ex.: `auth`, `escala`, `service`, `governance`, `deps`).
- **Breaking Change**: usar `!` no título (`feat(api)!: ...`) **OU** trailer `BREAKING CHANGE:` no rodapé — **nunca ambos** ao mesmo tempo.

---

### PASSO 4 — Estruturar a Mensagem Conforme Complexidade (SSOT § 5, § 6 e § 7)

> **Regra de Ouro (72 colunas)**: título com no máximo **72 caracteres** em PT-BR no imperativo ("adiciona", "corrige", "remove", "refatora", "atualiza"). Linhas do corpo com wrap em **máximo 72 caracteres**.

Avaliar o volume de arquivos modificados para escolher a estrutura:

#### Formato A: Commit Simples (1 a 5 arquivos) — SSOT § 5.1

```text
<tipo>(<escopo>): <resumo curto no imperativo em PT-BR>

- Descrição narrativa sucinta do que foi feito e da motivação da mudança.

Arquivos adicionados:
- caminho/Arquivo.ts — por que foi criado e sua responsabilidade.

Arquivos modificados:
- caminho/Arquivo.ts — o que foi alterado (resumido).

Arquivos removidos:
- caminho/Arquivo.ts — motivo da exclusão e classe/módulo substituto.

Como validar:
- <comando de teste ou verificação específico>
```
*(Omitir listas que não tiverem arquivos correspondentes).*

#### Formato B: Commit Complexo (6+ arquivos ou múltiplas frentes) — SSOT § 5.2

```text
<tipo>(<escopo>): <resumo consolidado no imperativo em PT-BR>

- Descrição narrativa consolidada: o que o conjunto entrega e o porquê.
- Referência a planos ou ADRs se aplicável (ex.: docs/plan/PLANO.md).

─── Novos arquivos ──────────────────────────────────────────────────
  [Grupo Funcional A]
  - caminho/Arquivo.ts — responsabilidade/objetivo

─── Arquivos modificados ────────────────────────────────────────────
  [Grupo Funcional B]
  - caminho/Arquivo.ts — o que foi alterado e por quê

─── Arquivos removidos ──────────────────────────────────────────────
  [Grupo Funcional C — Motivo da Exclusão]
  - caminho/Arquivo.ts — motivo da remoção e componente substituto

─── Breaking changes ────────────────────────────────────────────────
  (omitir se não houver quebra de contrato)
  - Descrever o que quebrou e instruções de migração

Como validar:
- <comando de teste/verificação da suíte ou módulo>
```

#### Seção "Como validar" (Obrigatória para feat, fix, refactor, test e perf — SSOT § 6)
- Java/Maven: `mvn -Dtest=ClasseTest test > logs/test-run.out 2>&1`
- Python/pytest: `pytest tests/modulo -v`
- Angular/Frontend: `npm test` ou `ng test --watch=false`
- Docs/Chore puros: `Como validar: N/A — alteração sem impacto em testes.`

#### Regra Mandatória para Arquivos Removidos
**NUNCA** listar um arquivo removido sem informar:
1. O **motivo** da exclusão (código morto, obsolescência, deprecação).
2. O **substituto** direto que assumiu a responsabilidade (se aplicável).

#### Rodapés e Trailers Padronizados (SSOT § 7)
Incluir apenas com dados reais existentes:
```text
BREAKING CHANGE: <descrição da quebra (quando não usado ! no título)>
Closes #123
Refs #456
Co-authored-by: Nome <email@exemplo.com>
```

---

### PASSO 5 — Apresentar a Mensagem e Instruções de Aplicação

Apresentar a saída em duas partes claras:

1. **Bloco de Mensagem Formatada**: a mensagem pronta para revisão.
2. **Comando para Execução Manual**: bloco bash utilizando `git commit -F - << 'EOF'` para facilitar a cópia e preservar quebras de linha e caracteres especiais.
3. Se houver sugestão de staging prévio, exibir o `git add` correspondente antes do commit.

---

## ✅ Checklist de Validação Antes de Exibir

- [ ] **Secrets**: Guardrail do PASSO 0 executado e diff 100% limpo?
- [ ] **Stage**: Mensagem reflete fielmente o que está staged (ou orienta o `git add` adequado)?
- [ ] **Atomicidade**: Teste do "e" respeitado?
- [ ] **Título**: Verbo no imperativo, PT-BR, sem ponto final, ≤ 72 caracteres?
- [ ] **Corpo**: Wrap em ≤ 72 caracteres por linha, explicando por quê e não apenas o quê?
- [ ] **Remoções**: Todo arquivo removido tem motivo e substituto explicados?
- [ ] **Validação**: Seção `Como validar:` presente com comando executável?
- [ ] **Autonomia**: Nenhum comando `git add`, `git commit` ou `git push` executado automaticamente.

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** executar `git add`, `git commit`, `git push` ou variações.
- ❌ **NUNCA** alterar o índice do git (staging) de forma autônoma.
- ❌ **NUNCA** gerar mensagem para diff contendo credenciais ou segredos expostos.
- ✅ **SEMPRE** exibir a mensagem estruturada e o comando pronto para execução manual pelo dev.

---

## 🔄 Rastreabilidade e Referências

- Guia Global de Commits: [`docs/ai-copilot/global-git-commit-instructions.md`](../../docs/ai-copilot/global-git-commit-instructions.md)
- Skill de Governança Git: [`.github/skills/git-governance/SKILL.md`](../skills/git-governance/SKILL.md)
- Padrão Conventional Commits v1.0.0: https://www.conventionalcommits.org/
- Regra de Formatação 50/72 (Chris Beams): https://cbea.ms/git-commit/

---

*v1.2 — commit prompt — 2026-09-04 (alinhamento integral com global-git-commit-instructions.md)*

