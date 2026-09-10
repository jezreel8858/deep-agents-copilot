# 🚀 Quick Start — Prompts Operacionais

Guia rápido para usar os prompts do Copilot Chat.

---

## ⚠️ FIRST STEP — OBRIGATÓRIO

```bash
/init-context
```

**Razão**: Carregar governança global (R-001..R-051). Faça isto **UMA ÚNICA VEZ** no início da sessão.

---

## 1️⃣ Início de Tarefa — Novo Projeto

```bash
/add-project-context <caminho-do-projeto>
```

**Resultado**: Contexto estruturado com Intent, RRF top 5, convenções e instruções carregadas.

**Nota**: Repita este comando para cada projeto novo (use `/del-project-context` para remover).

---

## 2️⃣ Pesquisa Contextualizada

```bash
/pesquisar "padrão que você quer entender"
```

**Quando usar**: Entender um padrão, dependência ou regra de negócio.

---

## 3️⃣ Criar Plano de Implementação

```bash
/plano "descreva a mudança aqui"
```

**Resultado**: Plano com fases, riscos e validações.

---

## 4️⃣ Executar Plano com Checkpoints

```bash
/implement "fase-1: criar entity" "fase-2: controller" "fase-3: testes"
```

**Nota**: A cada fase completa, use `/ctx-checkpoint` para salvar estado.

---

## 5️⃣ Validar Implementação

```bash
/validar
```

**Verifica**: Cobertura de testes, qualidade de código, aderência ao plano.

---

## 🔄 Workflow Completo (Exemplo Genérico)

```bash
# PASSO 1: Preparar Copilot (faz 1x APENAS)
/init-context

# PASSO 2: Carregar projeto
/add-project-context <caminho-do-projeto>

# PASSO 3: Pesquisar contexto
/pesquisar "padrão ou conceito a investigar"

# PASSO 4: Health check
/ctx-doctor

# PASSO 5: Planejar
/plan "descreva a tarefa aqui"

# PASSO 6: Implementar com checkpoints
/implement "fase-1: preparar" "fase-2: converter" "fase-3: testar"
/ctx-checkpoint  # ← após cada fase

# PASSO 7: Validar
/validate

# PASSO 8: Se houver interrupção, retomar:
/ctx-resume

# PASSO 9: Limpeza (quando terminar ou mudar de projeto)
/del-project-context <nome-do-projeto>
```

---

## 🔄 Gerenciamento de Múltiplos Projetos (mesma sessão)

```bash
# Uma única vez no início:
/init-context

# Projeto 1:
/add-project-context <caminho-projeto-a>
# ... trabalhar com projeto-a ...
/del-project-context <nome-projeto-a>

# Projeto 2:
/add-project-context <caminho-projeto-b>
# ... trabalhar com projeto-b ...
/del-project-context <nome-projeto-b>
```

**Nota**: `/init-context` fica ativo TODA a sessão. Mude de projeto com `/add-project-context` + `/del-project-context`.

---

## 📊 Context Mode — Quando Usar

| Comando | Situação |
|---------|----------|
| `/ctx-doctor` | Antes de tarefa crítica (valida MCP) |
| `/ctx-status` | Monitorar consumo de sessão |
| `/ctx-checkpoint` | Antes de pausar/trocar tarefa |
| `/ctx-resume` | Recuperar de checkpoint anterior |
| `/ctx-insight` | Análise profunda de padrões |

---

## 🧠 Regras Rápidas de Economia (ctx-first)

- Faça retomada por `ctx_search(..., sort: "timeline")` antes de nova coleta.
- Use `ctx_batch_execute(commands, queries)` como coleta principal.
- Agrupe perguntas relacionadas no mesmo `queries: [...]`.
- Use `source` quando consultar múltiplas fontes indexadas.
- Para conteúdo grande, use `ctx_execute_file` ou `ctx_index(path)`, nunca dump bruto.

---

## ✅ Checklist Rápido: Você Está Certo?

- [ ] Executou `/init-context` no início da sessão (1x APENAS)?
- [ ] Executou `/add-project-context <projeto>` para o projeto atual?
- [ ] Conhece a ordem: `/init-context` → `/add-project-context` → agents?
- [ ] Nunca repete `/init-context` na mesma sessão?
- [ ] Usa `/add-project-context` uma vez POR PROJETO?

Se **TODOS SIM**: ✅ Você está usando correto!
