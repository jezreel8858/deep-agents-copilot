# Prompt Files — Copilot Chat

Prompts operacionais para workflow de execução no chat.

---

## ⚠️ CLARIFICAÇÃO CRÍTICA: `/init-context` vs `/add-project-context`

**Você pode estar confuso — e isso é válido!** Ambos lidam com contexto, mas são **completamente diferentes**:

| Aspecto | `/init-context` | `/add-project-context` |
|---------|---|---|
| **Propósito** | Carregar **governança global** (R-001..R-051) | Descobrir **stack de projeto específico** |
| **Escopo** | TODO Copilot na sessão | APENAS 1 projeto |
| **Quando usar** | **PRIMEIRO — antes de tudo** | **DEPOIS — para cada projeto** |
| **Frequência** | ❌ 1x por sessão (não repetir) | ✅ N vezes (1 por projeto) |
| **Output** | Conformidade + Model validado | catalog.yaml atualizado |
| **Pré-requisito** | ✅ SIM (de tudo) | DEPOIS de /init-context |

### 🔄 Ordem Obrigatória

```
1. /init-context
   └─ Valida CLAUDE.md + copilot-instructions.md
   └─ Carrega R-001..R-051
   └─ Faz 1x por sessão APENAS

2. @agent-router ou qualquer agent
   └─ Usa contexto de governança já carregado

3. /add-project-context <projeto>
   └─ Para CADA projeto novo
   └─ Descobre stack + cria binding
   └─ Reutilizável (repete para cada projeto)

4. /deep-search, /plan, /implement, /validate
   └─ Usa contexto governança + binding já pronto
```

---

## Prompts de Inicialização

| Command | Arquivo | Descrição | Frequência |
|---------|---------|-----------|-----------|
| `/init-context` | `.github/prompts/init-context.prompt.md` | Inicializa contexto de governança obrigatório (carrega CLAUDE.md + copilot-instructions.md) para eliminar alucinação e assegurar conformidade com R-001..R-051 | **1x/sessão** |

---

## Prompts de Projeto

| Command | Arquivo | Descrição | Frequência |
|---------|---------|-----------|-----------|
| `/add-project-context` | `.github/prompts/add-project-context.prompt.md` | Auto-carregar contexto estruturado de um projeto (intent + RRF) com descoberta de stack e criação de artefatos | **N×** (1/projeto) |
| `/del-project-context` | `.github/prompts/del-project-context.prompt.md` | Remover contexto de um projeto do binding e cache (operação destrutiva, com confirmação) | **Conforme necessário** |
| `/connect-integration-graphs` | `.github/prompts/connect-integration-graphs.prompt.md` | ⭐ **(NEW)** Audita e conecta integrações cross-repo entre projetos já registrados — levanta contratos/endpoints (`@tech-solution-architect`), confirma no grafo existente restrito ao fluxo de integração (`@code-knowledge-graph`) e aplica as fronteiras (`manifesto.boundaries`) que faltam em `.codegraphrc.json` até fechar todo gap. | **Conforme necessário** |
| `/visualize-graph` | `.github/prompts/visualize-graph.prompt.md` | ⭐ **(NEW)** Compila e abre o visualizador web interativo do grafo de conhecimento multi-repo (Material 3, 2D/3D, multi-select, filtros de isolados/papéis/camadas e pontes REST). | **Conforme necessário** |

---

## Prompts de Workflow

| Command | Arquivo | Descrição |
|---|---|---|
| `/agent-router` | `.github/prompts/agent-router.prompt.md` | ⭐ **(NEW)** Alias fino do agent `@agent-router` — ponto de entrada obrigatório agent-first (R-037): Health Check (R-034), Prompt Structuring (R-041), classificação de intenção e delegação ao downstream correto. |
| `/deep-search` | `.github/prompts/deep-search.prompt.md` | ⭐ **(v2.0)** Alias fino do agent `@deep-search` — Retriever/Researcher interno (codebase/context-mode) e externo (Tavily, budget de 3 chamadas), com decisão atômica vs composta e síntese com citação de fonte. Renomeado de `/research`. |
| `/plan` | `.github/prompts/plan.prompt.md` | Cria plano de implementação detalhado com processo interativo |
| `/implement` | `.github/prompts/implement.prompt.md` | Executa plano aprovado com checkpoints e pausas para verificação |
| `/validate` | `.github/prompts/validate.prompt.md` | Valida implementação contra plano e identifica desvios |
| `/commit` | `.github/prompts/commit.prompt.md` | ⭐ **(v1.2)** Gera mensagem de commit convencional (PT-BR, Conventional Commits) alinhada às diretrizes globais (`global-git-commit-instructions.md`), com guardrail de secrets, atomicidade e templates por complexidade (simples vs complexo). Nunca executa git. |
| `/review` | `.github/prompts/review.prompt.md` | ⭐ **(v2.0)** Alias fino do agent `@code-review` — revisão de código por qualidade, convenções e impacto. Relatório compacto por severidade. |

---

## Prompts de Context Mode

| Command | Arquivo | Descrição |
|---|---|---|
| `/ctx-start` | `.github/prompts/ctx-start.prompt.md` | ⭐ **(NEW)** Inicializa e valida a sessão do Context Mode para garantir rastreabilidade |
| `/ctx-checkpoint` | `.github/prompts/ctx-checkpoint.prompt.md` | Grava snapshot de sessão no FTS5 para retomada cross-session |
| `/ctx-resume` | `.github/prompts/ctx-resume.prompt.md` | Retoma contexto de checkpoint específico ou lista disponíveis |
| `/ctx-doctor` | `.github/prompts/ctx-doctor.prompt.md` | Diagnostica conectividade e saúde do Context Mode (MCP) |
| `/ctx-insight` | `.github/prompts/ctx-insight.prompt.md` | Abre dashboard de analytics do Context Mode |
| `/ctx-status` | `.github/prompts/ctx-status.prompt.md` | Exibe estatísticas de consumo da sessão atual |
| `/health` | `.github/prompts/health.prompt.md` | ⭐ **(NEW)** Health check completo da governança: binding, agents, skills, prompts, R-038 e conformidade `ctx-first`. |

---

## ✅ Checklist: Você Está Usando Correto?

- [ ] **Primeira coisa:** Executou `/init-context` na sessão?
- [ ] **Para cada projeto:** Executou `/add-project-context <projeto>`?
- [ ] **catalog.yaml sincronizado:** Verificou se projeto está em `docs/ai-context/catalog.yaml`?
- [ ] **Pronto para agentes:** Pode agora usar `@agent-router` com contexto completo?

Se **TODOS SIM**: ✅ Você está usando corretamente!

---

## ✅ Checklist de Auditoria ctx-first (economia de créditos)

Use esta lista para revisar qualquer prompt `.prompt.md` antes de publicar:

- [ ] O prompt inicia com retomada por `ctx_search(..., sort: "timeline")` quando aplicável?
- [ ] A coleta principal usa `ctx_batch_execute(commands, queries)` em vez de chamadas fragmentadas?
- [ ] As perguntas de follow-up estão agrupadas em um único `queries: [...]`?
- [ ] O prompt orienta uso de `source` quando houver múltiplas fontes indexadas?
- [ ] Há regra explícita contra saída bruta extensa no chat?
- [ ] Para arquivos grandes, o prompt manda usar `ctx_execute_file` em vez de leitura integral?
- [ ] Há bloqueio explícito para `ctx_index(content: ...)` com payload grande?
- [ ] O fallback para terminal está restrito e justificado?
- [ ] O prompt evita releitura redundante de dados já coletados/indexados?
- [ ] A saída esperada pede síntese objetiva com evidência (`arquivo:linha`), sem dump?

---

## ✅ Checklist de Conformidade de Frontmatter (padrão Copilot 2026)

Use `@governance-factory` para auditar e corrigir automaticamente:

| Campo | Status | Significado |
|---|---|---|
| `description` | **OBRIGATÓRIO** | Habilita discoverability no Quick Pick do Copilot |
| `model` | Recomendado | "Gemini 3.8 Flash" / "Gemini 3.8 Flash" / "Claude Opus 5" (string única — arrays não são suportados) |
| `tools` | Quando usa ferramentas | Princípio de menor privilégio — listar apenas o necessário |
| `source_docs` | Quando precisa de contexto | Pre-fetch de governança ou projeto |
| `name` | Opcional | Override do filename como slash command |

**Template de referência**: `.github/prompts/templates/prompt-template.md`

**Para criar ou auditar prompts**: use `@governance-factory`
