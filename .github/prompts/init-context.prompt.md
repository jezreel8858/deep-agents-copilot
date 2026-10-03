---
name: init-context
description:
  ⚠️ PRÉ-REQUISITO OBRIGATÓRIO — Inicializa contexto de governança global para TODA sessão.
  Carrega CLAUDE.md + copilot-instructions.md, valida conformidade com as regras normativas globais.
  Execute UMA ÚNICA VEZ no início da sessão ANTES de /add-project-context ou qualquer agent.
  NÃO REPITA na mesma sessão — faz 1x apenas.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'list_dir', 'run_subagent', 'run_in_terminal', 'ask_questions', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search', 'context-mode/ctx_stats']
argument-hint: ''
source_docs:
  - .github/instructions/README.md
  - .config/idea_mcp.json
  - .github/hooks/context-mode.json
  - docs/context/setup-context-mode-intellij.md
  - .github/projects.local.yaml.example
  - .github/skills/context-mode/SKILL.md
  - docs/agent-context/codegraph-guia-uso.md
  - .github/skills/terminal-governance/SKILL.md
  - .github/skills/project-scanner/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/init-context`

**PRIMEIRO COMMAND DA SESSÃO — Obrigatório antes de tudo!**

Inicializa contexto obrigatório de governança. Execute 1x por sessão APENAS.

> **Propósito**: PRÉ-REQUISITO para toda execução downstream. Carregar regras normativas globais, validar model, eliminar alucinação.
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
- ✅ **SEMPRE** verificar a existência de `.github/instructions/README.md` e `.github/projects.local.yaml.example` (R-034).
- ❌ **NÃO** implementar código ou executar refatorações de aplicação.
- ❌ **NÃO** repetir este comando múltiplas vezes na mesma sessão.

---

## 🎯 Uso

### Invocação Explícita (Manual)

```bash
/init-context
```

### Invocação Automática (Copilot — Obrigatório)

Copilot **EXATAMENTE**:
1. Ação iniciar sessão ou trabalho em novo repositório
2. Após reset explícito do usuário ou perda de contexto relevante
3. ANTES de invocar `@agent-router` na primeira execução da sessão

---

## 📋 Execução em 9 Passos

> **Regra de Emissão de Progresso**: Durante os Passos 1 a 9, emita apenas **1 linha compacta de status** por passo concluído. Todos os dados detalhados coletados devem ser mantidos em memória e consolidados no checklist final.

> **Modo Zero-Touch**: quando houver permissão de escrita, o `/init-context` deve aplicar automaticamente configurações e criar arquivos faltantes sem interação adicional. Quando faltar permissão, registrar como `pending_manual_action` e continuar.

### **PASSO 1: Validar Carregamento de Diretrizes Base**

Copilot VERIFICA que ambos os `source_docs` foram carregados, mantendo status em memória e emitindo 1 linha de progresso:

```
[1/9] Diretrizes: ✅ CLAUDE.md + copilot-instructions.md carregados
```

**Se FALTA algum:**

```
[1/9] Diretrizes: ⚠️ <arquivo> ausente → tentando carregar manualmente via read_file...
```

Depois, prosseguir para PASSO 2.

---

### **PASSO 2: Detectar Ambiente de Execução (Environment Fingerprint)**

Detectar de forma determinística: **SO (Windows/Linux/macOS), shell ativo e shells disponíveis, IDE ativa (VS Code/JetBrains), runtimes e ferramentas de bootstrap**.

> Preferir `context-mode/ctx_execute` em lote. Sessão nunca falha por ausência de runtime opcional; registrar `available: false`.

**Lógica de cache (TTL 7 dias):**
- Se `environment.detected_at` em `.github/projects.local.yaml` < 7 dias: reaproveitar snapshot.
- Se ausente/expirado: executar detecção completa.

**Matriz mínima de detecção:**
- SO: `windows`, `linux`, `macos`.
- Shell ativo: `powershell`, `cmd`, `bash`, `zsh`, `git-bash`.
- Shells disponíveis: PowerShell Desktop/Core, CMD, Bash, Zsh, Git Bash (quando aplicável).
- IDE ativa: heurística por processo/caminho (`code`, `idea`, `intellij`, `jetbrains`).
- Runtimes: Node.js >= 20, Bun, Python >= 3.11.
- Tooling: `codegraph`, `npx`, `git`.

**Comandos de detecção por SO (não interativos):**
- Windows: `where`, `Get-Command`, `cmd /c ver`, `$PSVersionTable`.
- Linux/macOS: `uname -s`, `command -v`, `which -a`.

**Linha de progresso emitida:**

```
[2/9] Ambiente: ✅ <so> · shell=<ativo> · ide=<ativa> · runtimes detectados
```

Depois, prosseguir para PASSO 3.

---

### **PASSO 3: Sanitizar Terminal e Encoding (R-035 / R-049)**

Aplicar automaticamente baseline de terminal seguro:
- `git config core.pager cat` (local do workspace).
- Windows CMD: `chcp 65001`.
- Windows PowerShell: `$OutputEncoding = [System.Text.Encoding]::UTF8`.
- Bash/Zsh/Git Bash: `export LANG=en_US.UTF-8` e `export LC_ALL=en_US.UTF-8` (best effort).

Também validar que `.github/` está visível para busca indexada:
- Em `.ignore` e `.rgignore`, garantir presença de `!.github/` e `!.github/**`.

**Linha de progresso emitida:**

```
[3/9] Terminal: ✅ pager=cat · UTF-8 aplicado · .github visivel para indexacao
```

Depois, prosseguir para PASSO 4.

---

### **PASSO 4: Validar Runtimes (Node/Bun/Python) com Degradação Elegante**

Validar versões mínimas e registrar resultado sem bloquear sessão:
- Node.js: `>= 20.0.0`.
- Bun: presente/opcional.
- Python: `>= 3.11.0`.

Se não atingir versão mínima ou estiver ausente:
- registrar `available: false` e `reason`;
- adicionar recomendação final de instalação;
- **não interromper** `/init-context`.

**Linha de progresso emitida:**

```
[4/9] Runtimes: ✅ node=<ok|pendente> · bun=<ok|pendente> · python=<ok|pendente>
```

Depois, prosseguir para PASSO 5.

---

### **PASSO 5: Provisionar CLI do Codegraph (`@optave/codegraph`)**

Fluxo automático:
1. Verificar `codegraph --version`.
2. Se ausente e Node disponível: tentar `npm install -g @optave/codegraph`.
3. Revalidar versão.
4. Se continuar indisponível: registrar `available: false` e orientação final.

**Linha de progresso emitida:**

```
[5/9] Codegraph: ✅ <versao|pendente> (motor de grafo deterministico)
```

Depois, prosseguir para PASSO 6.

---

### **PASSO 6: Provisionar MCP na IDE Ativa (VS Code ou IntelliJ)**

Registrar servidores MCP obrigatórios: `context-mode`, `codegraph`, `tavily`.

- VS Code: `.vscode/mcp.json`.
- IntelliJ (repo): `.config/idea_mcp.json`.
- IntelliJ (host): `%LOCALAPPDATA%\\github-copilot\\intellij\\mcp.json` (Windows) ou `~/.config/github-copilot/intellij/mcp.json` (Linux/macOS).

**Regras:**
- Não sobrescrever valores sensíveis existentes (ex.: `TAVILY_API_KEY`).
- Criar entradas ausentes com merge incremental.
- Marcar `disabled: false` quando aplicável.

**Linha de progresso emitida:**

```
[6/9] MCP: ✅ context-mode + codegraph + tavily registrados para <ide>
```

Depois, prosseguir para PASSO 7.

---

### **PASSO 7: Configurar Hooks e Telemetria do Context Mode**

Validar configuração dual-case em `.github/hooks/context-mode.json`:
- `sessionStart`/`SessionStart`;
- `preToolUse`/`PreToolUse`;
- `postToolUse`/`PostToolUse`;
- `preCompact`/`PreCompact`;
- `userPromptSubmitted`/`UserPromptSubmitted`;
- `errorOccurred`/`ErrorOccurred`.

Executar health check de telemetria:
- `ctx_stats` para verificar atividade.
- dashboard local: `http://localhost:4747`.

**Linha de progresso emitida:**

```
[7/9] Telemetria: ✅ hooks dual-case validos · dashboard 4747 verificado
```

Depois, prosseguir para PASSO 8.

---

### **PASSO 8: Garantir Overlay Local e Persistir `environment` (R-043)**

Garantir isolamento local:
1. Se `.github/projects.local.yaml` não existe, criar a partir de `.github/projects.local.yaml.example`.
2. Persistir/atualizar o bloco `environment:` sem remover `projetos:`.
3. Incluir snapshot completo do ambiente detectado (SO, shell, IDE, runtimes, codegraph, MCP e telemetria).

**Estrutura alvo mínima:**

```yaml
environment:
  detected_at: "<ISO-8601>"
  os: "<windows|linux|macos>"
  ide:
    active: "<vscode|intellij|unknown>"
    available:
      vscode: true
      intellij: true
  shells_available:
    - name: "<powershell|pwsh|cmd|bash|zsh|git-bash>"
      path: "<path>"
  shell_ativo_na_sessao: "<shell>"
  python:
    available: true
    version: "<major.minor.patch|n/a>"
    path: "<path|n/a>"
  nodejs:
    available: true
    version: "<major.minor.patch|n/a>"
    path: "<path|n/a>"
  bun:
    available: true
    version: "<major.minor.patch|n/a>"
    path: "<path|n/a>"
  codegraph:
    available: true
    version: "<major.minor.patch|n/a>"
  mcp:
    vscode: "<ok|pending_manual_action|na>"
    intellij: "<ok|pending_manual_action|na>"
  terminal:
    pager_configured: true
    utf8_configured: true
  telemetry:
    hooks_context_mode: "<ok|warning>"
    dashboard_url: "http://localhost:4747"
```

**Linha de progresso emitida:**

```
[8/9] Overlay: ✅ projects.local.yaml pronto · environment persistido
```

Depois, prosseguir para PASSO 9.

---

### **PASSO 9: Verificação Final de Conformidade e Resumo de Boot**

Antes de encerrar, validar:
- os 9 passos foram executados com 1 linha de progresso por etapa;
- nenhum comando interativo foi usado;
- nenhuma credencial foi exibida em texto claro;
- ausência de runtime opcional foi tratada como não-bloqueante.

Incluir status do modelo ativo (R-021) no resumo final.

**Linha de progresso emitida:**

```
[9/9] Boot: ✅ inicializacao zero-touch concluida
```

---

## ✅ Validação Final — Checklist Consolidado (9 itens)

| Etapa | Verificação | Status / Detalhes |
|---|---|---|
| **1/9** | Diretrizes Base | ✅ `CLAUDE.md` + `.github/copilot-instructions.md` carregados |
| **2/9** | Detecção de Ambiente | ✅ `so`, `shell`, `ide` e fingerprint coletados |
| **3/9** | Sanitização de Terminal | ✅ `core.pager=cat` + UTF-8 aplicado + `.github` visível no índice |
| **4/9** | Runtimes | ✅ Node>=20 / Bun / Python>=3.11 avaliados (sem bloqueio por ausência) |
| **5/9** | Codegraph CLI | ✅ `@optave/codegraph` validado/provisionado |
| **6/9** | MCP por IDE | ✅ `context-mode`, `codegraph`, `tavily` provisionados em VS Code/IntelliJ |
| **7/9** | Hooks e Telemetria | ✅ hooks dual-case + dashboard `http://localhost:4747` |
| **8/9** | Overlay Local (R-043) | ✅ `.github/projects.local.yaml` criado/atualizado com `environment:` |
| **9/9** | Conformidade de Execução | ✅ 1 linha de progresso por etapa + sem comandos interativos |

---

## 🧩 Sintaxe de Boot por Shell (referência rápida)

Use a sintaxe conforme shell detectado no PASSO 2:

| Shell | Exemplo de comando de bootstrap |
|---|---|
| **PowerShell** | `powershell -ExecutionPolicy Bypass -NoProfile -Command "git config core.pager cat; $OutputEncoding=[System.Text.Encoding]::UTF8"` |
| **CMD** | `cmd /c "git config core.pager cat && chcp 65001"` |
| **Bash/Zsh/Git Bash** | `bash -lc 'git config core.pager cat; export LANG=en_US.UTF-8; export LC_ALL=en_US.UTF-8'` |

---

## ✅ Validação Final — Checklist de Inicialização

Ação concluir `/init-context`, Copilot exibe o bloco consolidado com todos os dados coletados nos Passos 1 a 9:

| Verificação | Status / Detalhes |
|---|---|
| **Diretrizes Base (PASSO 1)** | ✅ `CLAUDE.md` + `.github/copilot-instructions.md` carregados (regras normativas globais) |
| **Ambiente (PASSO 2)** | ✅ `<SO>` · Shell ativo `<shell>` · IDE `<ide>` |
| **Terminal/Encoding (PASSO 3)** | ✅ `core.pager=cat` · UTF-8 aplicado · `.github` indexável |
| **Runtimes (PASSO 4)** | ✅ Node `<versão|ausente>` · Bun `<versão|ausente>` · Python `<versão|ausente>` |
| **Codegraph (PASSO 5)** | ✅ `<versão|ausente>` |
| **MCP na IDE (PASSO 6)** | ✅ VS Code `<ok|na>` · IntelliJ `<ok|na>` |
| **Hooks/Telemetria (PASSO 7)** | ✅ Context Mode ativo · dashboard rastreável |
| **Overlay Local (PASSO 8)** | ✅ `projects.local.yaml` presente e `environment:` persistido |
| **Conformidade (PASSO 9)** | ✅ Fluxo sem bloqueios interativos e sem exposição de segredos |

🎯 **Próximos passos recomendados:**
- `/add-project-context <caminho-externo>` para plugar um projeto externo
- `/del-project-context <nome-projeto>` para desplugar um projeto
- `@agent-router` para classificar intenção e rotear a solicitação
- `/health` para auditar a saúde da governança
- *Nenhum arquivo será criado fora DESTE repositório de governança ✅*

### 💡 Recomendações para Esta Sessão

Sintetiza em bullets objetivos apenas as pendências reais detectadas nos Passos 1-9 — nunca genéricas, sempre condicionadas ao estado real:

- **[Environment]** *(se node/python ausente ou abaixo da versão mínima)*: instalar runtime e repetir `/init-context`.
- **[Codegraph]** *(se ausente)*: executar `npm install -g @optave/codegraph`.
- **[MCP]** *(se integração da IDE exigir ação manual)*: concluir merge dos blocos em `.vscode/mcp.json` ou `.config/idea_mcp.json`.
- **[Tavily]** *(se sem chave)*: configurar `TAVILY_API_KEY` localmente (nunca versionar).
- **[Sessão]** *(se telemetria inativa)*: executar `/ctx-start` e revalidar `ctx_stats`.
- **[Fluxo]**: toda solicitação subsequente deve começar por `@agent-router` (R-037).

> **Se nenhuma pendência for detectada:**
> ```
> ✅ Nenhuma pendência detectada — ambiente 100% conforme.
> → Prossiga diretamente para @agent-router.
> ```
> Recomendações são informativas e não bloqueiam a sessão.

---

## 🔄 Combina Com (Encadeamento)

- **`@agent-router`**: Próximo passo obrigatório para toda solicitação downstream (R-037 — Agent Router First).
- **`/add-project-context <caminho>`**: Para vincular projetos externos no overlay local (`projects.local.yaml`, R-043).
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
| "MCP não aparece na IDE" | Arquivo de configuração local não sincronizado | aplicar merge em `.vscode/mcp.json` ou `%LOCALAPPDATA%\\github-copilot\\intellij\\mcp.json` |
| "Acentuação quebrada no Windows" | codepage/encoding não aplicados | repetir PASSO 3 (`chcp 65001` ou `$OutputEncoding`) |
| "Python/Node não encontrado" | Runtime ausente no host | registrar `available: false` e instalar depois (não bloqueia sessão) |
| "Codegraph CLI não encontrado" | `@optave/codegraph` não instalado globalmente | `npm install -g @optave/codegraph` |
| "Dashboard sem eventos" | hooks não carregados | validar `.github/hooks/context-mode.json` e executar `/ctx-start` |

---

> Histórico de versões: ver CHANGELOG.md

<execution_protocol>
**Protocolo Plan-Then-Batch (Smell 2.26 / Smell 2.13 / R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **DESPACHAR & VALIDAR**: Aplique todas as mutações ou leituras em processo único no sandbox (all-or-nothing verificado, R-051) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
4. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
5. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
6. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).
8. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".
</execution_protocol>
