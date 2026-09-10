---
name: init-context
description:
  ⚠️ PRÉ-REQUISITO OBRIGATÓRIO — Inicializa contexto de governança global para TODA sessão.
  Carrega CLAUDE.md + copilot-instructions.md, valida conformidade R-001..R-051.
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
  - .github/skills/context-mode/SKILL.md
---

# `/init-context`

**PRIMEIRO COMMAND DA SESSÃO — Obrigatório antes de tudo!**

Inicializa contexto obrigatório de governança. Execute 1x por sessão APENAS.

> **Propósito**: PRÉ-REQUISITO para toda execução downstream. Carregar regras R-001..R-051, validar model, eliminar alucinação.
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

- ✅ **`CLAUDE.md`** — Governança global, regras normativas R-001..R-051
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

> **Regra de Emissão de Progresso**: Durante os Passos 1 a 8, emita apenas **1 linha compacta de status** por passo concluído. Todos os dados detalhados coletados devem ser mantidos em memória e consolidados no checklist final.

### **PASSO 1: Validar Carregamento de Diretrizes Base**

Copilot VERIFICA que ambos os `source_docs` foram carregados, mantendo status em memória e emitindo 1 linha de progresso:

```
[1/8] Diretrizes: ✅ CLAUDE.md + copilot-instructions.md carregados
```

**Se FALTA algum:**

```
[1/8] Diretrizes: ⚠️ <arquivo> ausente → tentando carregar manualmente via read_file...
```

Depois, prosseguir para PASSO 2.

---

### **PASSO 2: Detectar Ambiente de Execução (Environment Fingerprint)**

Detecta terminal(is) disponível(is), versão de Python, versão de Node.js, versão de Java/JDK e CLI do Codegraph (`@optave/codegraph`) nesta máquina — registra em `catalog.local.yaml` (gitignored, R-043) para reuso por agents downstream (`code-knowledge-graph`, `test-engineer`, `devops-engineer`, `spring-boot-engineer`, `spring-reactive-engineer`, etc.) sem repetir a detecção a cada sessão.

> Preferir `context-mode/ctx_execute` (sandbox, Think in Code — R-008); `run_in_terminal` é fallback apenas se o MCP estiver indisponível. Nunca bloqueia a sessão — item ausente é registrado como `available: false`.

**Lógica de Cache (TTL 7 dias):**
- Se `catalog.local.yaml` já possui `environment.detected_at` com menos de 7 dias: reutilizar cache, pular detecção ativa.
- Se ausente ou expirado: executar detecção completa em lote (1 execução, não 1 comando por item).

**Detecção completa (comandos não-interativos, sem paginação — R-035):**

| Item | Como detectar | Observação |
|---|---|---|
| Shells instalados | `where powershell` / `where cmd` / `where bash` / `where wsl` (Windows) ou `which -a bash zsh fish` (Unix) | Apenas existência no PATH — nunca executar/abrir o shell |
| Shell ativo nesta sessão | `$SHELL`, `$OSTYPE`, `$ComSpec`, nome do processo pai (heurística, best-effort) | Informativo — não crítico se impreciso |
| Python | tentar `python --version`, depois `python3 --version`, depois `py --version` (Windows launcher) — usar o **primeiro que executa com sucesso** | ⚠️ Aliases de app-store (ex.: `WindowsApps\python.exe`) podem existir no PATH mas apontar para instalação quebrada/ausente — sempre validar rodando `--version`, nunca confiar só na existência do caminho |
| Node.js | `node --version` | Capturar também `npm --version` se disponível |
| Java/JDK | `java -version` (saída vai para **stderr**, capturar com `2>&1`) + `echo $JAVA_HOME` (Unix) / `echo %JAVA_HOME%` (Windows) | Relevante para `spring-boot-engineer`, `spring-reactive-engineer` e a skill `java-jdk-backend-governance` (LTS: 17, 21) — registrar mesmo se não for LTS, apenas informativo |
| Codegraph CLI | `codegraph --version` | Relevante para `@code-knowledge-graph` e FASE 4 de `/add-project-context` (`@optave/codegraph`) — registrar versão se disponível |
| Git Pager (R-035) | `git config core.pager cat` | Desativa pager interativo (`less`) no Git local do workspace para prevenir travamento do terminal em `git diff`/`log` |

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

**Linha de progresso emitida:**

```
[2/8] Ambiente: ✅ <SO> · <Shell ativo> · Python <ver|❌> · Node <ver|❌> · Java <ver|❌> · Codegraph <ver|❌>
```
*(Se cache reutilizado: `[2/8] Ambiente: ✅ Cache reaproveitado (< 7 dias) — <SO> · <Shell ativo> · Python <ver> · Node <ver> · Java <ver> · Codegraph <ver>`)*

Dados detalhados são preservados em memória para o checklist final. Depois, prosseguir para PASSO 3.

---

### **PASSO 3: Informar Modelo Ativo (R-021)**

Validar modelo em uso — informativo, não bloqueante:
- Recomendações de referência: Claude Haiku (inicialização, Q&A) | Claude Sonnet+ (implementação/refactor) | Claude Opus (arquitetura complexa).

**Linha de progresso emitida:**

```
[3/8] Modelo: ✅ <model-atual> (sessão ativa)
```

Depois, prosseguir para PASSO 4.

---

### **PASSO 4: Exibir Regras Críticas**

O nível de detalhe é verificado em memória conforme a existência de binding context (PASSO 5 antecipa resultado):

- **Sessão recorrente (binding já existe)**: top 5 regras críticas ativas mantidas em memória:
  - `[R-009]` Sem arquivos autônomos: solicite aprovação ANTES
  - `[R-010]` Segurança: nunca expor credenciais
  - `[R-027]` Clarificação: use ask_questions (nunca deduza)
  - `[R-037]` Agent Router First: toda solicitação → @agent-router
  - `[R-038]` Genericidade: .github/* sem projetos específicos
- **Primeira execução (binding ausente ou novo clone)**: catálogo completo mantido em memória:
  - `[R-001]` Escopo · `[R-002]` Mudança mínima · `[R-003]` Sem duplicação · `[R-008]` Execução ctx_* first · `[R-009]` Sem arquivos autônomos · `[R-010]` Segurança · `[R-027]` Clarificação · `[R-031]` Plano Auto-Implementável · `[R-034]` Health Check Binding · `[R-035]` Terminal sem paginação · `[R-037]` Agent Router First · `[R-038]` Genericidade · `[R-039]` Diagramas Mermaid · `[R-040]` Grafo de Roteamento fonte de verdade.

**Linha de progresso emitida:**

```
[4/8] Regras: ✅ R-001..R-051 ativas (<recorrente: top 5 em memória | 1ª vez: catálogo completo>)
```

Depois, prosseguir para PASSO 5.

---

### **PASSO 5: Validar Binding Context (R-034) + Overlay Local (R-043)**

Verificar se estrutura de binding existe **NESTE repositório de governança**:
- `./docs/ai-context/catalog.yaml` (compartilhado/commitado — sem projetos)
- `./docs/ai-context/binding.md` (compartilhado/commitado)
- `./docs/ai-context/catalog.local.yaml` (gitignored — overlay de projetos, R-043)

> ⚠️ O binding context (`catalog.yaml` + `binding.md`) é **EXCLUSIVO DESTE repositório**. Projetos externos NÃO possuem e NÃO devem possuir `catalog.yaml` ou `binding.md`.
> **Projetos são dados LOCAIS (R-043)**: vivem em `catalog.local.yaml` (gitignored) — nunca em `catalog.yaml`. Se `catalog.local.yaml` não existir, criar a partir de `catalog.local.yaml.example` (template tracked, sem dados reais) antes de prosseguir.

**Ações:**
1. Se `catalog.yaml` e `binding.md` existem: ler `catalog.yaml` (adapters/global) e `catalog.local.yaml` (se existir — projetos), mesclando em memória para o checklist final.
2. Se `catalog.yaml`/`binding.md` faltam: disparar agent `binding-initializer` para criação neste repositório.
3. Se apenas `catalog.local.yaml` faltar: copiar template (`cp docs/ai-context/catalog.local.yaml.example docs/ai-context/catalog.local.yaml`) e prosseguir com 0 projetos.

**Linha de progresso emitida:**

```
[5/8] Binding: ✅ catalog.yaml + binding.md presentes (<n> projetos no overlay local)
```
*(Se incompleto: `[5/8] Binding: ⚠️ Incompleto (faltando <arquivo>) → disparando binding-initializer`)*

Depois, prosseguir para PASSO 6.

---

### **PASSO 6: Verificar Herança de Instruções Genéricas**

Para cada projeto registrado em `catalog.local.yaml` (gitignored, R-043), verificar se o campo `extends:` está configurado, conectando o projeto aos adapters genéricos disponíveis em `catalog.yaml` (compartilhado).

**Se algum projeto registrado está sem `extends:`**, perguntar via `ask_questions` (por projeto):
- **(A)** Herdar 1 adapter existente (selecionar da lista)
- **(B)** Herdar múltiplos adapters existentes
- **(C)** Não herdar agora — projeto possui ou terá adapter próprio em `.github/instructions/local/`

Se usuário escolhe A ou B:
1. Exibir preview do YAML a ser adicionado ao projeto em `catalog.local.yaml` (gitignored):
   ```yaml
   extends:
     - "<adapter-id>"
   ```
2. Aguardar confirmação do usuário
3. Atualizar `catalog.local.yaml` com o campo `extends:` no projeto correspondente — **nunca `catalog.yaml`** (R-043)

**Linha de progresso emitida:**

```
[6/8] Herança: ✅ <n-com-extends> configurados (<n-sem-extends> sem extends)
```

Depois, prosseguir para PASSO 7.

---

### **PASSO 7: Validar Atividade do Context Mode (Dashboard Health)**

Verificar se a sessão atual do Context Mode está sendo rastreada para evitar "Dashboard vazia" no JetBrains:
1. Execute `ctx_stats()`.
2. Se `Total calls` retornar 0 ou falhar, invoque `/ctx-start` para inicializar a telemetria e o banco de dados da sessão.

**Linha de progresso emitida:**

```
[7/8] Context Mode: ✅ Ativo (<n> chamadas registradas)
```
*(Se inativo: `[7/8] Context Mode: ⚠️ Inativo (0 chamadas) → disparando /ctx-start...`)*

Depois, prosseguir para PASSO 8.

---

### **PASSO 8: Verificar Cache de Grafo de Conhecimento, Código e Sumarização (por Projeto)**

Para cada projeto registrado em `catalog.local.yaml` (gitignored, R-043 — nunca em `catalog.yaml`), verificar se já existe cache de **grafo de conhecimento** (`@code-knowledge-graph`), de **código-fonte indexado** (`code:<project-id>`) e de **sumarização** (`@code-summarizer`) no Context Mode:

- Projetos registrados = 0 → pular verificação.
- Projetos registrados > 0 → executar queries em lote via `ctx_batch_execute` (queries de todos os projetos no mesmo array — nunca 1 chamada por projeto, R-008):
  - `ctx_search(queries: ["code-graph:<project-id>:*"])`
  - `ctx_search(queries: ["*"], source: "code:<project-id>")`
  - `ctx_search(queries: ["code-summary:<project-id>:*"])`

> Cache ausente é puramente informativo — nunca bloqueia a sessão nem dispara construção automática autônoma (R-009). Os detalhes por projeto são mantidos em memória para o checklist final.

**Linha de progresso emitida:**

```
[8/8] Cache Projetos: ✅ <n-com-grafo>/<n-total> grafo · <n-com-codigo>/<n-total> código · <n-com-sumario>/<n-total> sumário
```
*(Se 0 projetos: `[8/8] Cache Projetos: ℹ️ Nenhum projeto registrado no overlay`)*

---

## ✅ Validação Final — Checklist de Inicialização

Ao concluir `/init-context`, Copilot exibe o bloco consolidado com todos os dados coletados nos Passos 1 a 8:

| Verificação | Status / Detalhes |
|---|---|
| **Diretrizes Base (PASSO 1)** | ✅ `CLAUDE.md` + `.github/copilot-instructions.md` carregados (regras R-001..R-051) |
| **Ambiente (Fingerprint, PASSO 2)** | ✅ `<SO>` · Shell: `<shell>` · Python: `<versão|ausente>` · Node: `<versão|ausente>` · Java: `<versão|ausente>` · Codegraph: `<versão|ausente>` (registrado em `catalog.local.yaml`) |
| **Modelo Ativo (PASSO 3)** | ✅ `<model-atual>` (sessão ativa, R-021) |
| **Regras Críticas (PASSO 4)** | ✅ R-001..R-051 ativas (exibição contextual: `<recorrente \| 1ª vez>`) |
| **Binding Context (PASSO 5)** | ✅ `./docs/ai-context/` DESTE repo · `<n>` projetos no overlay local · `<n>` adapters disponíveis |
| **Herança de Instruções (PASSO 6)** | ✅ `<n-com-extends>` configurados · `<n-sem-extends>` sem `extends:` |
| **Context Mode Session (PASSO 7)** | ✅ Ativo · `<Total calls>` chamadas registradas (dashboard rastreável) |
| **Cache por Projeto (PASSO 8)** | ℹ️ Grafo: `<n-com-grafo>/<n-total>` · Código: `<n-com-codigo>/<n-total>` · Sumários: `<n-com-sumario>/<n-total>` |

🎯 **Próximos passos recomendados:**
- `/add-project-context <caminho-externo>` para plugar um projeto externo
- `/del-project-context <nome-projeto>` para desplugar um projeto
- `@agent-router` para classificar intenção e rotear a solicitação
- `/health` para auditar a saúde da governança
- *Nenhum arquivo será criado fora DESTE repositório de governança ✅*

### 💡 Recomendações para Esta Sessão

Sintetiza em bullets objetivos apenas as pendências reais detectadas nos Passos 1-8 — nunca genéricas, sempre condicionadas ao estado real:

- **[Environment]** *(se python/node ausente)*: Instale `<ferramenta>` antes de invocar agents dependentes (ex.: `test-engineer`, `devops-engineer`).
- **[Environment]** *(se codegraph ausente)*: Instale o codegraph (`npm install -g @optave/codegraph`) para habilitar grafo de conhecimento em `/add-project-context` e `@code-knowledge-graph`.
- **[Model]** *(se recomendável)*: Ajuste o modelo da sessão conforme a complexidade da tarefa (R-021).
- **[Binding]** *(se incompleto)*: Execute `binding-initializer` — `catalog.yaml`/`binding.md` ausentes (R-034).
- **[Extends]** *(se houver projeto sem extends)*: Configure herança em `<n>` projeto(s) pendente(s) — PASSO 6.
- **[Cache]** *(se houver projeto sem grafo/sumário)*: Considere `@code-knowledge-graph` / `@code-summarizer` para `<projeto(s)>` antes de análises profundas.
- **[Sessão]** *(se Context Mode inativo)*: Rode `/ctx-start` — Total calls = 0, dashboard não vai rastrear.
- **[Fluxo]**: Toda solicitação a partir daqui deve começar por `@agent-router` (R-037).

> **Se nenhuma pendência for detectada:**
> ```
> ✅ Nenhuma pendência detectada — ambiente 100% conforme.
> → Prossiga diretamente para @agent-router.
> ```
> Recomendações são sempre informativas — nunca bloqueiam a sessão nem disparam ação autônoma (R-009). Ordem fixa: Environment → Model → Binding → Extends → Cache → Sessão → Fluxo.

---

## 🔄 Combina Com (Encadeamento)

- **`@agent-router`**: Próximo passo obrigatório para toda solicitação downstream (R-037 — Agent Router First).
- **`/add-project-context <caminho>`**: Para vincular projetos externos no overlay local (`catalog.local.yaml`, R-043).
- **`/health`**: Para auditar a saúde da governança e validar conformidade.

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

> Histórico de versões: ver CHANGELOG.md
