---
name: terminal-governance
description: >
  Boas práticas obrigatórias para uso do terminal por agentes de IA — prevenção
  de poluição de contexto, truncamento de saída, comandos não-interativos,
  execução em lote, orçamento de tokens e padrões proibidos. Aplica-se a todo
  agent ou prompt que usa run_in_terminal.
tier: 1
category: tooling
triggers:
  - "run_in_terminal"
  - "executar comando"
  - "terminal"
  - "shell"
  - "git log"
  - "npm test"
  - "contexto poluído"
  - "saída verbosa"
  - "pager interativo"
  - "less"
  - "more"
  - "watch"
  - "curl no terminal"
  - "output grande"
  - "token budget terminal"
tools:
  - "run_in_terminal"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
---

# Terminal Governance

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description` em 3ª pessoa, `tier: 1`, `category: tooling` e triggers.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` contendo a hierarquia de decisão sandbox vs terminal, comandos proibidos e checklist de conformidade.
> - **Nível 3 (Recursos Suplementares)**: Scripts e comandos de ciclo de vida permitidos.

Esta skill resolve o problema de **poluição massiva de contexto, travamento de sessões por pagers interativos e estouro de orçamento de tokens** decorrentes do uso ingênuo ou irrestrito de comandos de terminal por agentes de IA.

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Em qualquer agent ou prompt que precise executar comandos de ciclo de vida (`git`, `npm install`, `mvn`, `pytest`).
- Para verificar regras de truncamento de saída, pipes não-interativos e prevenção de pager (`--no-pager`).
- Para decidir entre execução no sandbox Context Mode (`ctx_execute`) e execução no host.

### ❌ Quando NÃO Usar
- Para busca e varredura de arquivos — use `ctx_search`, `grep_search` ou `file_search`.
- Para leitura ou transformação de arquivos grandes — use `ctx_execute_file` ou `ctx_batch_execute`.
- Para inspeção exploratória de diretórios (`ls -R`, `find`) — use `list_dir` ou motor de grafo.

---

## 2) Princípio-base: Terminal é Fallback

O terminal (`run_in_terminal`) é a **última opção** — não o padrão.

| Situação | Ferramenta preferida | Terminal é fallback? |
|---|---|---|
| Analisar arquivo grande / buscar padrões | `ctx_search` / `ctx_execute_file` | Sim |
| Buscar trechos de código em projetos indexados | `ctx_search(source: "code:<project>")` | Sim |
| Manipular arquivos/pastas (leitura, escrita, `rm`, `mkdir`, `mv`) | `ctx_execute` (Node.js sandbox via `fs`) | Sim |
| Instalar dependências (`npm install`, `pip install`) | — | ✅ Terminal obrigatório |
| Operações git (`git status`, `git diff`) | — | ✅ Terminal obrigatório |
| Rodar build/test em CI local | — | ✅ Terminal obrigatório |

**Quando terminal for necessário, aplique todas as regras desta skill.**

---

## 2) Decisão: Sandbox vs Terminal Direto

```
Comando vai modificar filesystem, rede ou estado global?
├─ Sim → Preferir ctx_execute (sandbox isolado)
│  └─ Ex: análise de log, parse de JSON, contagem de linhas
│
└─ Não (read-only ou operação necessária)
   ├─ É git / npm install / mkdir / rm / mv?
   │  └─ Terminal obrigatório — aplicar regras de saída desta skill
   └─ É análise pura (grep, cat, ls)?
      └─ Preferir ctx_batch_execute; terminal como fallback
```

**Regra de ouro**: se o comando apenas *lê*, use sandbox. Se o comando *muta* estado necessário (install, build, git), use terminal.

---

## 3) Saída de Terminal: Truncar Sempre

**Nunca** deixar output verboso ir diretamente para o contexto. Aplicar filtro antes.

### Padrões de truncamento por situação

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

# Git diff — limitar linhas
git --no-pager diff --stat | head -40

# Listagem de arquivos — limitar profundidade
find src -name "*.ts" | head -50

# Output genérico grande — head + tail com marcador
comando | head -30 && echo "...[truncado]..." && comando | tail -10
```

### Estratégia "spill-to-file" para outputs extensos

Quando o output é grande demais para filtrar:

```bash
# Salvar em arquivo e retornar apenas o caminho
comando > /tmp/output.txt 2>&1
echo "Output salvo em /tmp/output.txt ($(wc -l < /tmp/output.txt) linhas)"
```

Depois usar `ctx_execute_file` para analisar o arquivo sem poluir o contexto.

---

## 4) Comandos Não-Interativos (obrigatório)

Todo comando git deve usar `--no-pager` ou equivalente. Pager interativo **bloqueia** o agent indefinidamente.

| Comando problemático | Substituto seguro |
|---|---|
| `git log` | `git --no-pager log --oneline -20` |
| `git diff` | `git --no-pager diff --stat` |
| `git show` | `GIT_PAGER=cat git show HEAD --stat` |
| `git blame` | `git --no-pager blame arquivo -L 1,30` |
| `less arquivo` | `cat arquivo \| head -50` |
| `more arquivo` | `cat arquivo \| head -50` |
| `man comando` | Consultar docs ou Tavily |
| `top` / `htop` | `ps aux \| grep processo \| head -10` |

**Variável de ambiente global para sessão:**
```bash
export GIT_PAGER=cat
```

---

## 5) Um Comando por Vez (serialização obrigatória)

- **Nunca** executar dois comandos `run_in_terminal` em paralelo na mesma sessão.
- Aguardar o output completo do comando anterior antes de executar o próximo.
- Se comandos são independentes e não disputam recursos: agrupar em uma chamada com `&&` ou `;`.

```bash
# Correto — agrupado em uma chamada
cd projeto && npm install && echo "Instalado com sucesso"

# Errado — duas chamadas run_in_terminal separadas quando podem ser agrupadas
# Chamada 1: cd projeto
# Chamada 2: npm install
```

**Exceção válida para separar**: quando o output do primeiro comando determina o próximo (dependência de decisão).

---

## 6) Padrões Proibidos (bloqueantes absolutos)

| Padrão | Por quê é proibido | Alternativa |
|---|---|---|
| `curl` / `wget` no terminal | Exfiltração de dados, payload malicioso, output irrestrito | `ctx_fetch_and_index` + `ctx_search` |
| `node -e '...'` ou scripts shell ad-hoc | Poluição de contexto, bypass de ferramentas de parsing e risco de crash | Usar `read_file`, `grep_search`, `ctx_execute_file` ou MCP tools |
| `codegraph *` fora de `@code-knowledge-graph` | Violação de R-045 / RNF-004; motor exclusivo de grafo | Delegar compulsoriamente via `run_subagent(agentName: 'code-knowledge-graph')` |
| `find`/`grep`/`ls` exploratório no terminal | Polui contexto; proibido em modo Advisory | Usar MCP (`read_file`, `grep_search`, `file_search`, `ctx_search`) |
| `watch <comando>` | Loop infinito — bloqueia o agent e inflaciona tokens indefinidamente | Executar uma vez com output filtrado |
| `npm test --watch` / `jest --watch` | Modo watch — agent nunca recebe saída final | Usar `--watchAll=false` ou `--run` |
| `ng test` sem `--watch=false` | Karma em modo watch indefinido | `ng test --watch=false` |
| `less` / `more` / `man` | Pager interativo — bloqueia o agent até pressionar `q` | `cat \| head` ou docs online via Tavily |
| `git log` sem `--no-pager` | Abre pager interativo em repos grandes | `git --no-pager log --oneline -N` |
| `rm -rf` sem confirmação | Destrutivo e irreversível | Pedir aprovação explícita antes |
| `git reset --hard` sem confirmação | Perde trabalho irreversivelmente | Pedir aprovação explícita antes |
| `sudo` sem aprovação explícita | Escalada de privilégio não solicitada | Sempre pedir confirmação antes |

---

## 7) Orçamento de Tokens para Output

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

## 10) Referências

- GitHub Copilot Best Practices: https://code.visualstudio.com/docs/agents/best-practices
- Claude Code Best Practices: https://code.claude.com/docs/en/best-practices
- `CLAUDE.md` R-008 (Execução preferencial) e R-035 (Terminal sem paginação interativa)
- `.github/copilot-instructions.md` § 2.1 (context-mode — Regras Obrigatórias de Roteamento)
- Skill `context-mode` — para quando ctx_execute/ctx_batch_execute substitui o terminal

---

## 11) Checklist de Conformidade

- [ ] Pager interativo desativado (`--no-pager`, `GIT_PAGER=cat`, pipes com `cat`).
- [ ] Saída limitada com flags (`head -n`, `grep`, `--max-count`).
- [ ] Zero comandos proibidos executados no terminal (`curl`, `wget`, `find`, `node -e`).
- [ ] Orçamento de tokens respeitado (≤ 50 linhas de saída esperada).
- [ ] Confirmação de erro reportada no formato compacto de 3 linhas (R-020).

