# Terminal Governance — Exemplos de Comandos, Watchdog e Execução de Testes

### 5.3) Proibição de Delegação Redundante via `run_subagent` (Anti-Cascata Fantasma)

> **Incidente real investigado (2026-10-04)**: um agent com AMBAS `run_in_terminal` e
> `run_subagent` nas próprias `tools:` (ex.: `pr-gatekeeper`), ao ser solicitado a
> "testar se consegue usar `git --no-pager status/diff/log`", delegou a verificação
> via `run_subagent` em vez de simplesmente executar o comando. No SDK headless do
> gateway, `run_subagent` é traduzido para a tool NATIVA genérica `task`/
> `general-purpose` -- que NÃO valida o nome do agent delegado contra nenhum
> catálogo real, aceita um label livre INVENTADO pelo próprio modelo e spawna um
> modelo auxiliar próprio (ex.: `gpt-5.6-luna`), desconectado do agent original.
> Resultado observado em produção: uma cascata recursiva de 8 "subagents fantasmas"
> com nomes como `git-readonly-check`, `git-output`, `exact-git-output`,
> `git-readonly-runner`, `git-inspection` -- nenhum deles um agent real do catálogo
> `.github/agents/**/*.agent.md` -- consumindo ~2 minutos e ~175 mil tokens apenas
> para confirmar 3 comandos git read-only triviais que o agent já tinha permissão
> de rodar diretamente.

**REGRA INVIOLÁVEL**: se o agent já possui `run_in_terminal` (ou `ctx_execute`/
`ctx_batch`) disponível em suas próprias `tools:` e o comando solicitado
está dentro do seu escopo de competência, é **TERMINANTEMENTE PROIBIDO** delegar
essa execução via `run_subagent` apenas para "testar", "confirmar" ou "verificar"
a própria capacidade. Execute o comando diretamente.

`run_subagent` é reservado exclusivamente para:
- Handoff genuíno de escopo para outro agent especializado (ex.: `@code-review`,
  `@agent-router`) quando a tarefa sai da competência do agent atual (R-042).
- Delegação a um agent **nomeado explicitamente e existente** no catálogo
  (`.github/agents/**/*.agent.md`) -- nunca um nome/label inventado ad-hoc para
  descrever uma sub-tarefa genérica de teste/verificação.

| Sintoma de uso incorreto | Correção |
|---|---|
| "Vou delegar para testar o comando X" quando X já está nas próprias `tools:` | Executar X diretamente via `run_in_terminal`/`ctx_execute` |
| Nome de subagent que não corresponde a nenhum `.agent.md` real do catálogo | Não invocar `run_subagent` -- tratar como ação própria |
| Múltiplas invocações sucessivas de `run_subagent` para "confirmar de outro jeito" a mesma verificação | Parar na primeira tentativa bem-sucedida; nunca re-testar a mesma coisa via subagent |

## 7–9) Orçamento de Tokens, Execução de Testes por Stack e Estrutura de Saída

O output de terminal **entra no contexto** e consome tokens. Estimar antes de executar:

| Tipo de output | Estimativa de tokens | Ação recomendada |
|---|---|---|
| `git status` limpo | ~50 tokens | Seguro — executar direto |
| `ls -la` de diretório | ~200 tokens | Seguro com `\| head -20` |
| `git log` 20 commits | ~500 tokens | Usar `--oneline` + `-20` |
| Output de build com erros | ~2.000 tokens | Filtrar com `grep -E "ERROR\|WARN"` |
| Suíte de testes completa | ~10.000+ tokens | Filtrar falhas + `head -60` |
| `npm install` verboso | ~3.000 tokens | Redirecionar, mostrar só resultado final |

**Regra prática**: output > 100 linhas deve ser filtrado **antes** de entrar no contexto.

---

## 8) Execução de Testes via Terminal

Para contexts onde testes precisam ser executados no terminal (sem sandbox), seguir as regras de lote da skill `test-engineer`:

```bash
# Angular Vitest — lote por módulo, output filtrado
npx vitest run src/app/modulo/ 2>&1 | grep -E "FAIL|✗|passed|failed" | head -40

# Angular Karma — lote por glob, sem watch
ng test --watch=false --include="src/app/modulo/**/*.spec.ts" 2>&1 | grep -E "FAILED|SUCCESS|ERROR" | head -40

# Spring Boot — lote por classe, output filtrado
./mvnw test -Dtest="ClasseA,ClasseB" 2>&1 | grep -E "Tests run|FAILED|ERROR|BUILD" | head -40

# pytest — lote com filtro de nome, output filtrado
pytest tests/modulo/ -k "padrao" --tb=short 2>&1 | grep -E "FAILED|passed|error" | head -40
```

---

## 9) Estrutura de Saída Esperada por Comando

Ao reportar resultado de um comando para o usuário, usar formato compacto:

```markdown
Comando: `git --no-pager log --oneline -5`
Saída (5 linhas):
abc1234 feat: adiciona validação de CPF
def5678 fix: corrige null pointer em ServicoX
...

Próximo passo: <ação derivada do output>
```

Nunca colar o output bruto integralmente. Sempre extrair apenas o que é relevante para a decisão.

---

## 4) Tabela Completa de Comandos Não-Interativos

Todo comando git deve usar `--no-pager` ou equivalente. Pager interativo **bloqueia** o agent indefinidamente.

| Comando problemático | Substituto seguro |
|---|---|
| `git diff <arquivo>` (sem `--no-pager`) | `git --no-pager diff <arquivo>` (ou `\| head -60`) |
| `git diff` (resumo) | `git --no-pager diff --stat` |
| `git log` | `git --no-pager log --oneline -20` |
| `git show` | `git --no-pager show HEAD --stat` (ou `GIT_PAGER=cat git show ...`) |
| `git branch` / `git tag` | `git --no-pager branch` / `git --no-pager tag` |
| `git blame` | `git --no-pager blame arquivo -L 1,30` |
| `less arquivo` | `cat arquivo \| head -50` |
| `more arquivo` | `cat arquivo \| head -50` |
| `man comando` | Consultar docs ou Tavily |
| `top` / `htop` | `ps aux \| grep processo \| head -10` |

**Salvaguarda no nível do Git (executar 1x por repositório ou globalmente):**
```bash
git config core.pager cat
```
Isso garante que, mesmo se o comando git for acidentalmente digitado sem `--no-pager`, o Git invocará `cat` em vez de `less`, nunca travando o terminal em modo interativo.

**Variável de ambiente global para sessão:**
```bash
export GIT_PAGER=cat
```

---

## 3) Snippets de Truncamento por Situação

```bash
# Logs — manter apenas erros/falhas
comando 2>&1 | grep -E "ERROR|FAIL|WARN|error|failed" | head -60

# Testes — extrair apenas falhas
npx vitest run 2>&1 | grep -E "FAIL|✗|×|Tests.*failed" | head -60
ng test --watch=false 2>&1 | grep -E "FAILED|Error:" | head -60
pytest 2>&1 | grep -E "FAILED|ERROR" | head -60
./mvnw test 2>&1 | grep -E "FAILED|ERROR|Tests run.*Failures" | head -60

# Git log — limitar quantidade de commits
git --no-pager log --oneline -20

# Git diff — inspecionar arquivo ou limitar linhas (sempre com --no-pager)
git --no-pager diff <arquivo> | head -60
git --no-pager diff --stat | head -40

# Listagem de arquivos — limitar profundidade
find src -name "*.ts" | head -50

# Output genérico grande — head + tail com marcador
comando | head -30 && echo "...[truncado]..." && comando | tail -10
```
