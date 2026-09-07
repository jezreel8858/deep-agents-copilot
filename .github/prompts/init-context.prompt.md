---
name: init-context
description:
  ⚠️ PRÉ-REQUISITO OBRIGATÓRIO — Inicializa contexto de governança global para TODA sessão.
  Carrega CLAUDE.md + copilot-instructions.md, valida conformidade R-001..R-040.
  Execute UMA ÚNICA VEZ no início da sessão ANTES de /add-project-context ou qualquer agent.
  NÃO REPITA na mesma sessão — faz 1x apenas.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'list_dir', 'run_subagent', 'run_in_terminal', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search', 'context-mode/ctx_stats']
argument-hint: ''
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - docs/ai-context/catalog.yaml
  - docs/ai-context/catalog.local.yaml.example
  - .github/skills/terminal-governance/SKILL.md
---

# `/init-context`

**PRIMEIRO COMMAND DA SESSÃO — Obrigatório antes de tudo!**

Inicializa contexto obrigatório de governança. Execute 1x por sessão APENAS.

> **Propósito**: PRÉ-REQUISITO para toda execução downstream. Carregar regras R-001..R-046, validar model, eliminar alucinação.
> **Workspace**: `${workspaceFolder}`
>
> **FREQUÊNCIA**: ❌ 1x POR SESSÃO (nunca repita na mesma sessão)
>
> **ORDEM**: SEMPRE PRIMEIRO — antes de `/add-project-context` ou `@agent-router`
>
> **PRÓXIMO PASSO**: Após `/init-context` completar, execute `/add-project-context <projeto>` para cada projeto novo.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** carregar regras globais, checar binding context e auditar telemetria/ambiente de sessão.
- ✅ **SEMPRE** verificar a existência de `catalog.yaml` e `binding.md` (R-034).
- ❌ **NÃO** implementar código ou executar refatorações de aplicação.
- ❌ **NÃO** repetir este comando múltiplas vezes na mesma sessão.

---

---

## 📌 Source Docs (Pre-Fetch Obrigatório)

Este prompt carrega **automaticamente** (conforme frontmatter `source_docs`):

- ✅ **`CLAUDE.md`** — Governança global, regras normativas R-001..R-039
- ✅ **`.github/copilot-instructions.md`** — Roteamento rápido, agents, skills, binding

**Validação**: Se algum arquivo não foi anexado, Copilot **DEVE** alertar e carregá-lo manualmente.

```
⚠️ ALERTA: Arquivo não anexado automaticamente!
   → Carregando manualmente...
```

---

## 🎯 Uso

### Invocação Explícita (Manual)

```bash
/init-context
```

### Invocação Automática (Copilot — Obrigatório)

Copilot **EXATAMENTE**:
1. Ao iniciar sessão ou trabalho em novo repositório
2. Após reset explícito do usuário ou perda de contexto relevante
3. ANTES de invocar `@agent-router` na primeira execução da sessão

---

## 📋 Execução em 8 Passos

### **PASSO 1: Validar Carregamento de Diretrizes Base**

Copilot VERIFICA que ambos os `source_docs` foram carregados:

```
[Health Check] Source Docs
├─ CLAUDE.md → ✅ Anexado (regras R-001..R-039)
├─ .github/copilot-instructions.md → ✅ Anexado (agents + skills + binding)
└─ Status: ✅ Pronto
```

**Se FALTA algum:**

```
⚠️ PRÉ-REQUISITO NÃO ATENDIDO!

Arquivo faltando: <arquivo>

→ Tentando carregar manualmente...
```

**Depois, prosseguir para PASSO 2.**

---

### **PASSO 2: Detectar Ambiente de Execução (Environment Fingerprint)**

Detecta terminal(is) disponível(is), versão de Python, versão de Node.js, versão de Java/JDK e CLI do Codegraph (`@optave/codegraph`) nesta máquina — registra em `catalog.local.yaml` (gitignored, R-043) para reuso por agents downstream (`code-knowledge-graph`, `test-engineer`, `devops-engineer`, `spring-boot-engineer`, `spring-reactive-engineer`, etc.) sem repetir a detecção a cada sessão.

> Preferir `context-mode/ctx_execute` (sandbox, Think in Code — R-008); `run_in_terminal` é fallback apenas se o MCP estiver indisponível. Nunca bloqueia a sessão — item ausente é registrado como `available: false`.

```
[Health Check] Environment Fingerprint
├─ Cache existente em catalog.local.yaml → environment.detected_at com menos de 7 dias?
│   ├─ Sim → reutilizar cache, pular detecção (exibir "✅ cache reaproveitado")
│   └─ Não → executar detecção completa (abaixo), em lote (1 execução, não 1 comando por item)
```

**Detecção completa (comandos não-interativos, sem paginação — R-035):**

| Item | Como detectar | Observação |
|---|---|---|
| Shells instalados | `where powershell` / `where cmd` / `where bash` / `where wsl` (Windows) ou `which -a bash zsh fish` (Unix) | Apenas existência no PATH — nunca executar/abrir o shell |
| Shell ativo nesta sessão | `$SHELL`, `$OSTYPE`, `$ComSpec`, nome do processo pai (heurística, best-effort) | Informativo — não crítico se impreciso |
| Python | tentar `python --version`, depois `python3 --version`, depois `py --version` (Windows launcher) — usar o **primeiro que executa com sucesso** | ⚠️ Aliases de app-store (ex.: `WindowsApps\python.exe`) podem existir no PATH mas apontar para instalação quebrada/ausente — sempre validar rodando `--version`, nunca confiar só na existência do caminho |
| Node.js | `node --version` | Capturar também `npm --version` se disponível |
| Java/JDK | `java -version` (saída vai para **stderr**, capturar com `2>&1`) + `echo $JAVA_HOME` (Unix) / `echo %JAVA_HOME%` (Windows) | Relevante para `spring-boot-engineer`, `spring-reactive-engineer` e a skill `java-jdk-backend-governance` (LTS: 17, 21) — registrar mesmo se não for LTS, apenas informativo |
| Codegraph CLI | `codegraph --version` | Relevante para `@code-knowledge-graph` e FASE 4 de `/add-project-context` (`@optave/codegraph`) — registrar versão se disponível |

Se algum item não for encontrado ou falhar, registrar `available: false` — **nunca falhar/bloquear a sessão** por isso.

**Persistir em `catalog.local.yaml`** (nova chave de topo, irmã de `projetos:`):

```yaml
environment:
  detected_at: "<ISO-8601>"
  os: "<windows|linux|macos>"
  shells_available:
    - name: "powershell"
      path: "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
    - name: "cmd"
      path: "C:\\Windows\\System32\\cmd.exe"
    - name: "git-bash"
      path: "C:\\Program Files\\Git\\usr\\bin\\bash.exe"
    - name: "wsl"
      path: "C:\\Windows\\System32\\wsl.exe"
  shell_ativo_na_sessao: "<ex.: MINGW64 (Git Bash)>"
  python:
    available: true
    version: "<major.minor.patch>"
    path: "<caminho-que-de-fato-executou>"
  nodejs:
    available: true
    version: "<major.minor.patch>"
    path: "<caminho>"
  java:
    available: true
    version: "<major.minor.patch>"
    java_home: "<caminho-ou-null-se-nao-definido>"
  codegraph:
    available: true
    version: "<major.minor.patch>"
```

**Exibir:**

```
[Environment Fingerprint]
├─ SO: <windows|linux|macos>
├─ Shells disponíveis: <lista>
├─ Shell ativo nesta sessão: <shell>
├─ Python: ✅/❌ <versão> (<path>)
├─ Node.js: ✅/❌ <versão> (<path>)
├─ Java/JDK: ✅/❌ <versão> (JAVA_HOME: <path-ou-"não definido">)
├─ Codegraph CLI: ✅/❌ <versão ou "não instalado"> (@optave/codegraph)
└─ Registrado em: docs/ai-context/catalog.local.yaml (gitignored — nunca commitado, R-043)
```

**Depois, prosseguir para PASSO 3.**

---

### **PASSO 3: Informar Modelo Ativo (R-021)**

Exibir modelo em uso — apenas **informativo**, não bloqueante:

```
[Model Info]
├─ Recomendado: Claude Haiku (inicialização, Q&A)
│               Claude Sonnet+ (implementação/refactor)
│               Claude Opus  (arquitetura complexa)
└─ Atual (sessão): <model-atual>
```

> `/init-context` carrega contexto de governança — não bloqueia por modelo.

---

### **PASSO 4: Exibir Regras Críticas**

O nível de detalhe é **condicional** — verificar se binding context existe (PASSO 5 antecipa resultado):

#### Se binding context **JÁ EXISTE** (sessão recorrente):

Exibir apenas top 5 — sem ruído para quem já conhece as regras:

```
📋 TOP 5 REGRAS CRÍTICAS ATIVAS  (ver todas: CLAUDE.md)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[R-009] Sem arquivos autônomos: solicite aprovação ANTES
[R-010] Segurança: nunca expor credenciais
[R-027] Clarificação: use ask_questions (nunca deduza)
[R-037] Agent Router First: toda solicitação → @agent-router
[R-038] Genericidade: .github/* sem projetos específicos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✅ R-001..R-040 ativas — Agents respeitarão
```

#### Se binding context **NÃO EXISTE** (primeira execução):

Exibir resumo completo para garantir alinhamento:

```
📋 REGRAS CRÍTICAS ATIVAS (primeira execução — leia com atenção)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[R-001] Escopo: altere APENAS o solicitado
[R-002] Mudança mínima: prefira pequenas alterações
[R-003] Sem duplicação: regra global → CLAUDE.md
[R-008] Execução: prefira ctx_* (terminal é fallback)
[R-009] Sem arquivos autônomos: solicite aprovação ANTES
[R-010] Segurança: nunca expor credenciais
[R-027] Clarificação: use ask_questions (nunca deduza)
[R-031] Plano Auto-Implementável: zero-interrupção + contingências
[R-034] Health Check Binding: verificar catalog.yaml + binding.md
[R-035] Terminal: sem paginação interativa (--no-pager, GIT_PAGER=cat)
[R-037] Agent Router First: TODA solicitação começa com @agent-router
[R-038] Genericidade: .github/* deve ser genérica (sem projetos específicos)
[R-039] Diagramas: usar Mermaid em .md (nada de PNG/SVG)
[R-040] Grafo de Roteamento: routing-graph.yaml é fonte de verdade estrutural

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✅ R-001..R-040 ativas — Agents respeitarão
```

---

### **PASSO 5: Validar Binding Context (R-034) + Overlay Local (R-043)**

Verificar se estrutura de binding existe **NESTE repositório de governança**:

```
[Health Check] Binding Context (R-034) — verificando NESTE repositório
├─ ./docs/ai-context/catalog.yaml → ?          (compartilhado/commitado — sem projetos)
├─ ./docs/ai-context/binding.md → ?            (compartilhado/commitado)
├─ ./docs/ai-context/catalog.local.yaml → ?    (gitignored — overlay de projetos, R-043)
└─ Status: ?
```

> ⚠️  O binding context (catalog.yaml + binding.md) é **EXCLUSIVO DESTE repositório**.
> Projetos externos (project-example-app, etc.) NÃO possuem
> e NÃO devem possuir catalog.yaml ou binding.md.
> **Projetos são dados LOCAIS (R-043)**: vivem em `catalog.local.yaml` (gitignored) —
> nunca em `catalog.yaml`. Se `catalog.local.yaml` não existir, criar a partir de
> `catalog.local.yaml.example` (template tracked, sem dados reais) antes de prosseguir.

**Se `catalog.yaml` e `binding.md` existem:**

Ler `catalog.yaml` (adapters/global) **e** `catalog.local.yaml` (se existir — projetos) e
exibir estado real **mesclado em memória** (nunca escrever de volta em `catalog.yaml`):

```
✅ Binding context DETECTADO (neste repositório de governança)

   Projetos registrados (fonte: catalog.local.yaml, gitignored):
   ├─ <nome-projeto-1>  → adapter: .github/instructions/local/<nome-projeto-1>.instructions.md ✅
   ├─ <nome-projeto-2>  → adapter: .github/instructions/local/<nome-projeto-2>.instructions.md ✅
   └─ ... (total: <n> projetos)

   Adapters compartilhados em .github/instructions/ (raiz, commitados):
   └─ <lista-de-arquivos-.instructions.md>

   Adapters locais em .github/instructions/local/ (gitignored, por projeto):
   └─ <lista-de-arquivos-.instructions.md>

   → Pronto para /add-project-context, /pesquisar, /plano, @agent-router
```

**Se `catalog.yaml`/`binding.md` FALTAM:**

```
⚠️ Binding context INCOMPLETO (neste repositório)!

Faltando:
  - <arquivo>

→ Disparando agent `binding-initializer` para criação...
→ Todos os arquivos serão criados NESTE repositório.
→ Nenhum arquivo será criado nos projetos externos.
```

**Se apenas `catalog.local.yaml` FALTAR** (primeira vez nesta máquina/clone):

```
ℹ️ Overlay local não encontrado — criando a partir do template.
→ cp docs/ai-context/catalog.local.yaml.example docs/ai-context/catalog.local.yaml
→ Prosseguindo normalmente (0 projetos registrados nesta máquina ainda)
```

---

### **PASSO 6: Verificar Herança de Instruções Genéricas**

Para cada projeto registrado em `catalog.local.yaml` (gitignored, R-043), verificar se o campo `extends:` está configurado, conectando o projeto aos adapters genéricos disponíveis em `catalog.yaml` (compartilhado).

```
[Health Check] Herança de Instruções Genéricas
├─ Adapters genéricos disponíveis:
│   ├─ Listar automaticamente de `.github/instructions/*.instructions.md`
│   └─ Sugerir herança por similaridade de stack
├─ Projetos sem `extends:` configurado: ?
└─ Status: ?
```

**Se `projetos:` está vazio ou todos já têm `extends:`:**

```
✅ Herança de instruções OK
   → Nenhum projeto sem extends: pendente
   → Pronto para /add-project-context, /pesquisar, /plano
```

**Se algum projeto registrado está sem `extends:`**, perguntar via `ask_questions` (por projeto):

```
Projeto "[nome-do-projeto]" não possui `extends:` configurado.
Deseja configurar herança de instruções genéricas agora?
```

Opções:
- **(A)** Herdar 1 adapter existente (selecionar da lista)
- **(B)** Herdar múltiplos adapters existentes
- **(C)** Não herdar agora — projeto possui ou terá adapter próprio

**Se usuário escolhe A ou B:**
1. Exibir preview do YAML a ser adicionado ao projeto em `catalog.local.yaml` (gitignored):
   ```yaml
   extends:
     - "<adapter-id>"
   ```
2. Aguardar confirmação do usuário
3. Atualizar `catalog.local.yaml` com o campo `extends:` no projeto correspondente — **nunca `catalog.yaml`** (R-043)

**Se usuário escolhe C:**
```
⚠️ Projeto sem herança de instruções genéricas registrada.
   Certifique-se de que possui adapter próprio em .github/instructions/local/
```

---

### **PASSO 7: Validar Atividade do Context Mode (Dashboard Health)**

Verificar se a sessão atual do Context Mode está sendo rastreada para evitar "Dashboard vazia" no JetBrains:
1. Execute `ctx_stats()`.
2. Se `Total calls` retornar 0 ou falhar, invoque `/ctx-start` para inicializar a telemetria e o banco de dados da sessão.

---

### **PASSO 8: Verificar Cache de Grafo de Conhecimento, Código e Sumarização (por Projeto)**

Para cada projeto registrado em `catalog.local.yaml` (gitignored, R-043 — nunca em `catalog.yaml`), verificar se já existe cache de **grafo de conhecimento** (`@code-knowledge-graph`), de **código-fonte indexado** (`code:<project-id>`) e de **sumarização** (`@code-summarizer`) no Context Mode — evita reconstrução/reprocessamento desnecessário e informa ao usuário o que já está disponível para consulta imediata via `ctx_search`.

```
[Health Check] Cache de Grafo/Código/Sumarização por Projeto
├─ Projetos registrados em catalog.local.yaml: <n>
├─ Se <n> = 0 → pular este passo (nenhum projeto para checar)
└─ Para cada <project-id>:
    ├─ ctx_search(queries: ["code-graph:<project-id>:*"])   → grafo cacheado?
    ├─ ctx_search(queries: ["*"], source: "code:<project-id>") → código-fonte indexado no FTS5?
    └─ ctx_search(queries: ["code-summary:<project-id>:*"]) → sumários cacheados?
```

> Executar em **lote** via `ctx_batch_execute` (queries de todos os projetos no mesmo array — nunca 1 chamada por projeto, R-008/economia de contexto/token budget).

**Exibir tabela consolidada:**

```
📊 STATUS DE CACHE — Grafo, Código-Fonte e Sumarização
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Projeto           | Grafo (code-graph:*) | Código (code:*) | Sumarização (code-summary:*)
------------------|----------------------|-----------------|-----------------------------
<project-id-1>    | ✅ cacheado          | ✅ indexado     | ✅ cacheado
<project-id-2>    | ❌ ausente           | ❌ ausente      | ⚠️ parcial (<n> arquivos)
<project-id-3>    | ❌ ausente           | ❌ ausente      | ❌ ausente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: <n-com-grafo>/<n-total> com grafo | <n-com-codigo>/<n-total> com código indexado | <n-com-sumario>/<n-total> com sumarização
```

**Se algum projeto estiver sem cache (grafo, código e/ou sumarização):**

```
ℹ️ Cache ausente não bloqueia a sessão — apenas informativo.
   → Para construir grafo: invocar @code-knowledge-graph (RF-002, sob demanda)
   → Para indexar código-fonte: executar ctx_index(path: "<projeto>/src", source: "code:<project-id>")
   → Para sumarizar: invocar @code-summarizer (RF-002, sob demanda)
   → Nenhuma construção automática é feita por este prompt (R-009 — sem ação autônoma sem confirmação)
```

**Se `projetos:` estiver vazio em `catalog.local.yaml`:**

```
ℹ️ Nenhum projeto registrado ainda — pulando verificação de cache de grafo/sumarização.
   → Use /add-project-context <caminho> para registrar o primeiro projeto.
```

---

## ✅ Validação Final — Checklist de Inicialização

Ao concluir `/init-context`, Copilot **EXIBE**:

```
╔═══════════════════════════════════════════════════════════╗
║         ✅ CONTEXTO DE GOVERNANÇA INICIALIZADO            ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║ [✅] Diretrizes base carregadas                          ║
║      CLAUDE.md + copilot-instructions.md                 ║
║                                                           ║
║ [✅] Environment Fingerprint (PASSO 2)                   ║
║      Shell ativo: <shell> | Python: <versão ou ausente>  ║
║      Node.js: <versão ou ausente> | Java: <versão ou ausente> ║
║      Codegraph CLI: <versão ou ausente>                  ║
║      Registrado em: catalog.local.yaml (gitignored)      ║
║                                                           ║
║ [✅] Regras críticas (R-001..R-040) ativas              ║
║      Exibidas conforme contexto (recorrente/1ª vez)      ║
║                                                           ║
║ [✅] Binding context verificado (R-034)                  ║
║      Localização: ./docs/ai-context/ DESTE repo          ║
║      Projetos registrados: <n-projetos>                  ║
║      Adapters em .github/instructions/: <n-adapters>     ║
║                                                           ║
║ [✅] Herança de instruções verificada (PASSO 6)          ║
║      Projetos com extends: <n-projetos-com-extends>      ║
║      Projetos sem extends: <n-projetos-sem-extends>      ║
║                                                           ║
║ [✅] Context Mode Session (PASSO 7)                      ║
║      Estatísticas: <Total calls> chamadas               ║
║      Status: ✅ Ativo (rastreável no Dashboard)         ║
║                                                           ║
║ [✅] Cache de Grafo/Sumarização por Projeto (PASSO 8)    ║
║      Grafo (code-graph:*): <n-com-grafo>/<n-total>       ║
║      Sumarização (code-summary:*): <n-com-sumario>/<n-total> ║
║                                                           ║
║ [✅] PRONTO PARA PRÓXIMO PASSO                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🎯 Próximos passos recomendados:
    → /add-project-context <caminho-externo>  para plugar um projeto externo
    → /del-project-context <nome-projeto>     para desplugar um projeto
    → @agent-router                           para classificar intenção
    → /health                                 para checar saúde da governança
    → /deep-search, /plan, /implement, /validate para fluxo de desenvolvimento
    → Nenhum arquivo será criado fora DESTE repositório de governança ✅

ℹ️  Validação de contexto: ✅ SUCESSO
   Estado armazenado para sessão | Disponível para agents downstream
```

---

### 💡 Recomendações ao Usuário

Ao final do checklist, Copilot **SEMPRE** sintetiza em bullets objetivos as recomendações derivadas do que foi observado nos Passos 1-8 — nunca genéricas, sempre condicionadas ao estado real detectado nesta execução:

```
💡 RECOMENDAÇÕES PARA ESTA SESSÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Environment] <se python/node ausente: "Instale <ferramenta> antes de invocar agents que dependem dele (ex.: test-implementation, devops-engineer)">
[Environment] <se codegraph ausente: "Instale o codegraph (npm install -g @optave/codegraph) para habilitar grafo de conhecimento em /add-project-context e @code-knowledge-graph">
[Model]       <se recomendável: "Ajuste o modelo da sessão conforme a complexidade da tarefa (R-021)">
[Binding]     <se incompleto: "Execute binding-initializer — catalog.yaml/binding.md ausentes (R-034)">
[Extends]     <se houver projeto sem extends: "Configure herança em <n> projeto(s) pendente(s) — PASSO 6">
[Cache]       <se houver projeto sem grafo/sumário: "Considere @code-knowledge-graph/@code-summarizer para <projeto(s)> antes de análises profundas">
[Sessão]      <se Context Mode inativo: "Rode /ctx-start — Total calls = 0, dashboard não vai rastrear">
[Fluxo]       "Toda solicitação a partir daqui deve começar por @agent-router (R-037)"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Regras de geração:**
- Cada linha só aparece se a condição correspondente foi de fato detectada nos Passos 1-8 desta execução — nunca listar recomendação para item já ✅/conforme.
- Se **nenhuma** condição de alerta foi detectada (tudo ✅), exibir apenas:
  ```
  💡 RECOMENDAÇÕES PARA ESTA SESSÃO
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Nenhuma pendência detectada — ambiente 100% conforme.
  → Prossiga diretamente para @agent-router.
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- Recomendações são **sempre informativas** — nunca bloqueiam a sessão nem disparam ação autônoma (R-009); apenas apontam o próximo comando/agent que o usuário pode invocar.
- Ordem fixa: Environment → Model → Binding → Extends → Cache → Sessão → Fluxo (reflete a ordem dos Passos 2/3/5/6/8/7/router).

---

## 🚀 Integração com Agent Router

Após `/init-context` executar com sucesso, **Copilot automaticamente prossegue**:

```
[CONTEXTO INICIALIZADO] ✅

Você está pronto para:

1. @agent-router
   └─ Copilot classifica intenção
   └─ Copilot roteia para agent correto

2. Agent Downstream (bug-triage | test-strategy | etc)
   └─ Recebe contexto já carregado + diretrizes ativas
   └─ Nenhuma violação de R-001..R-039 esperada
```

**Regra (R-037)**: Toda solicitação após `/init-context` deve começar com `@agent-router`.

---

## 🔄 Quando Invocar Manualmente

Invoque `/init-context` **manualmente** em caso de:

| Cenário | Ação |
|---------|------|
| Novo repositório / primeira vez | `/init-context` ANTES de qualquer agent |
| Mudança de contexto entre projetos (mesma sessão) | usar `/add-project-context` para o projeto alvo (sem repetir `/init-context`) |
| Ambiguidade em regras | `/init-context` para validar conformidade |
| Agent comportamento estranho | `/init-context` + `/ctx-doctor` (diagnóstico) |
| Início de nova sessão (cross-session) | `/init-context` para recarregar estado |

---

## 🚨 Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| "Arquivo não anexado" | Pre-fetch falhou | Copilot carrega manualmente via `read_file` |
| "Binding context ausente" | `catalog.yaml` ou `binding.md` faltando | Disparar `binding-initializer` automaticamente |
| "Copilot não respeita regras após" | Regras não foram relevantes no downstream | Reexecutar `/init-context` ou ativar diagnostics com `/ctx-doctor` |
| "Python/Node não encontrado" | Ferramenta não instalada ou fora do PATH | Normal — registrado como `available: false`, não bloqueia a sessão; instalar se necessário para o agent alvo |
| "Path de Python existe mas `--version` falha" | Alias quebrado (ex.: stub da Microsoft Store apontando para instalação removida) | Detecção deve tentar o próximo candidato (`python3`, `py`) — nunca considerar `available: true` só pela existência do path |
| "Java não encontrado / JAVA_HOME vazio" | JDK não instalado ou não configurado no PATH | Normal — registrado como `available: false`; relevante apenas antes de invocar `spring-boot-engineer`/`spring-reactive-engineer` |
| "Codegraph CLI não encontrado" | `@optave/codegraph` não instalado globalmente | Normal — registrado como `available: false`; executar `npm install -g @optave/codegraph` antes de `/add-project-context` |

---

## ✅ Resultado Final Esperado

Ao completar `/init-context`, você verá:

```
CONTEXTO INICIALIZADO COM SUCESSO

[PASSO 1] Diretrizes base — OK
[PASSO 2] Environment fingerprint — DETECTADO (shell/python/node/java/codegraph registrados em catalog.local.yaml)
[PASSO 3] Modelo ativo — INFORMADO
[PASSO 4] Regras criticas — ATIVAS (R-001..R-040)
[PASSO 5] Binding context — VALIDO (<n> projetos registrados)
[PASSO 6] Herança de instruções — OK (<n-com-extends> c/ extends | <n-sem-extends> sem extends)
[PASSO 7] Context Mode Session — ATIVA (<n> chamadas)
[PASSO 8] Cache grafo/sumarização — <n-com-grafo>/<n-total> com grafo | <n-com-sumario>/<n-total> com sumarização

Proximo: /add-project-context <path> | /pesquisar | @agent-router
```

---

*v1.2 Init Context Prompt — 2026-06-12*
PASSO 5 adicionado: verificação de herança de instruções genéricas via campo `extends:` em `catalog.yaml`.

*v1.3 — 2026-09-01*
PASSO 7 adicionado: verificação de cache de grafo de conhecimento (`code-graph:<project-id>:*`, `@code-knowledge-graph`) e de sumarização (`code-summary:<project-id>:*`, `@code-summarizer`) por projeto registrado em `catalog.yaml`, via `ctx_batch_execute`/`ctx_search` em lote — puramente informativo, nunca aciona construção/sumarização automática (R-009).

*v1.4 — 2026-09-01*
Seção "💡 Recomendações ao Usuário" adicionada ao final do checklist de validação — sintetiza em bullets condicionais (Model/Binding/Extends/Cache/Sessão/Fluxo) apenas as pendências reais detectadas nos Passos 1-7, sempre informativa e nunca bloqueante/autônoma (R-009).

*v1.5 — 2026-09-01*
PASSO 4/5/7 atualizados para o Local Overlay Pattern (R-043): projetos deixam de viver em `catalog.yaml` (compartilhado/commitado) e passam a viver em `catalog.local.yaml` (gitignored). Toda leitura de projeto agora faz merge em memória dos dois arquivos; nenhuma escrita de projeto/adapter toca o arquivo compartilhado.

*v1.6 — 2026-09-01*
Novo PASSO 2 (Environment Fingerprint): detecta shells disponíveis (PowerShell/CMD/Git Bash/WSL/bash/zsh), shell ativo na sessão, versão de Python e versão de Node.js — registra em `catalog.local.yaml` (chave `environment:`, gitignored, R-043) para reuso por agents downstream sem repetir detecção a cada sessão. PASSOs 2-7 renumerados para 3-8. Adicionado `run_in_terminal` e as tools `context-mode/ctx_execute`, `ctx_batch_execute`, `ctx_search`, `ctx_stats` ao frontmatter (corrige gap pré-existente onde PASSO 6/7 antigos já as citavam no corpo sem declará-las). Cache de detecção válido por 7 dias (evita reexecução redundante). Tratamento explícito de aliases quebrados de Python (ex.: stub da Microsoft Store) — nunca considerar `available: true` apenas pela existência do path, sempre validar `--version`. Complementado por `.githooks/pre-commit` (defesa em profundidade — bloqueia commit acidental de `catalog.local.yaml` mesmo com `git add -f`).

*v1.7 — 2026-09-01*
PASSO 2 estendido com detecção de Java/JDK (`java -version` + `JAVA_HOME`) — relevante para os agents `spring-boot-engineer`/`spring-reactive-engineer` e a skill `java-jdk-backend-governance` (LTS 17/21). Nova chave `environment.java` no schema persistido em `catalog.local.yaml`. `/health` ganhou CAT-7 (Environment Fingerprint) — auditoria read-only de presença/idade do fingerprint (TTL 7 dias), sem redetectar nem escrever no overlay local (isso permanece exclusivo do `/init-context`).

*v1.8 — 2026-09-03*
PASSO 2 estendido com detecção do CLI `@optave/codegraph` (`codegraph --version`) — relevante para o agent `@code-knowledge-graph` e a FASE 4 de `/add-project-context`. Nova chave `environment.codegraph` no schema persistido em `catalog.local.yaml`. Recomendações e troubleshooting atualizados com instruções de instalação via `npm install -g @optave/codegraph`.

