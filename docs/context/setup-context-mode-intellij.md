# Guia de Configuração: Context Mode no IntelliJ IDEA

Este documento consolida todas as etapas necessárias para configurar e estabilizar o **Context Mode** no ambiente JetBrains (IntelliJ IDEA), garantindo que o MCP, o Knowledge Base e o Insight Dashboard funcionem corretamente de forma genérica.

## 📊 Status Atual (v2.1.10)

✅ **100% OPERACIONAL** — Verificado em 2026-06-17.
A configuração genérica agora captura sessões e telemetria nativamente no IntelliJ IDEA, sem necessidade de triggers manuais após a primeira validação.

| Componente | Status | Local |
|---|---|---|
| **Knowledge Base** | ✅ OK | `C:\Users\{username}\.config\JetBrains\context-mode\content` |
| **Sessions & Telemetry** | ✅ OK | `C:\Users\{username}\.config\JetBrains\context-mode\sessions` |
| **Hooks (Dual-Case)** | ✅ OK | `.github/hooks/context-mode.json` |
| **Dashboard** | ✅ OK | `http://localhost:4747` |

---

## 1. Variáveis de Ambiente (SO)

Defina as seguintes variáveis de sistema no Windows para garantir a persistência e visualização correta (já validadas):

| Variável              | Valor Recomendado                                   | Finalidade                                        |
|-----------------------|-----------------------------------------------------|---------------------------------------------------|
| `CONTEXT_MODE_DATA_DIR`    | `C:\Users\{username}\.config\JetBrains\context-mode` | Raiz de armazenamento dos bancos de dados         |
| `CONTEXT_MODE_DATA_DIR` | `%CONTEXT_MODE_DATA_DIR%\sessions`                       | Localização do banco de sessões e telemetria      |
| `CONTEXT_MODE_DATA_DIR` | `%CONTEXT_MODE_DATA_DIR%\content`                        | Localização do banco de conteúdo (Knowledge Base) |

## 2. Configuração do MCP Server (mcp.json)

O arquivo de configuração do Copilot deve ser ajustado para operar de forma **genérica**. Embora o uso de wrappers (`cmd.exe /c cd`) funcione, a recomendação atual é manter o comando simples e realizar a injeção de ambiente diretamente no arquivo de hooks (ver Seção 3).

**Localização do arquivo:** `C:\Users\{username}\AppData\Local\github-copilot\intellij\mcp.json`

### Configuração Validada (mcp.json):
```json
{
  "servers": {
    "context-mode": {
      "type": "stdio",
      "command": "cmd.exe",
      "args": [
        "/c",
        "npx",
        "-y",
        "context-mode",
        "server",
        "--agent",
        "copilot-cli"
      ],
      "env": {
        "IDEA_INITIAL_DIRECTORY": "<workspace>/[PROJETO-EXEMPLO]",
        "CONTEXT_MODE_DATA_DIR": "C:\\Users\\{username}\\.config\\JetBrains\\context-mode\\sessions"
      }
    }
  }
}
```

## 3. Hooks (Padrão de Resiliência - Injeção e Dual-Case + Fallback Claude-Code)

Para garantir visibilidade total no IntelliJ, os hooks em `.github/hooks/context-mode.json` devem suportar tanto `camelCase` quanto `PascalCase` e forçar a detecção da plataforma via variável de ambiente.

**NOTA IMPORTANTE (2026-06-17):** O adapter nativo de JetBrains não suporta `userpromptsubmit` e `erroroccurred` nativamente. Para contornar essa limitação e garantir que o Dashboard capture **Prompts** e **Error Rate**, redirecionamos esses eventos para o dispatcher do `claude-code`, que implementa a lógica de extração completa.

### Estrutura Corrigida (Unificação de Hash + Fallback):
```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot sessionstart",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot sessionstart",
        "cwd": "."
      }
    ],
    "SessionStart": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot sessionstart",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot sessionstart",
        "cwd": "."
      }
    ],
    "userPromptSubmitted": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook claude-code userpromptsubmit",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook claude-code userpromptsubmit",
        "cwd": "."
      }
    ],
    "UserPromptSubmitted": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook claude-code userpromptsubmit",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook claude-code userpromptsubmit",
        "cwd": "."
      }
    ],
    "preToolUse": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot pretooluse",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot pretooluse",
        "cwd": "."
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot pretooluse",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot pretooluse",
        "cwd": "."
      }
    ],
    "postToolUse": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot posttooluse",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot posttooluse",
        "cwd": "."
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot posttooluse",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot posttooluse",
        "cwd": "."
      }
    ],
    "preCompact": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot precompact",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot precompact",
        "cwd": "."
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook jetbrains-copilot precompact",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook jetbrains-copilot precompact",
        "cwd": "."
      }
    ],
    "errorOccurred": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook claude-code posttooluse",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook claude-code posttooluse",
        "cwd": "."
      }
    ],
    "ErrorOccurred": [
      {
        "type": "command",
        "bash": "IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}; context-mode hook claude-code posttooluse",
        "powershell": "$env:IDEA_INITIAL_DIRECTORY=$PWD.Path; context-mode hook claude-code posttooluse",
        "cwd": "."
      }
    ]
  }
}
```

**Adaptações-Chave:**
- **userPromptSubmitted / UserPromptSubmitted**: Redirecionadas para `claude-code userpromptsubmit` (fallback) em vez de `jetbrains-copilot userpromptsubmit`, garantindo que eventos de prompt sejam capturados e a métrica **Prompts** seja preenchida no Dashboard.
- **errorOccurred / ErrorOccurred**: Redirecionadas para `claude-code posttooluse` (fallback) em vez de um evento específico inexistente, garantindo que falhas de ferramentas sejam classificadas e a métrica **Error Rate** seja atualizada.
- **Injeção de Ambiente Melhorada**: Adicionado `IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}` em Bash para garantir conversão para uppercase (Windows-safe path), assegurando compatibilidade total com o hash de projeto no Insight.

*A injeção de `IDEA_INITIAL_DIRECTORY=$(pwd -W); IDEA_INITIAL_DIRECTORY=${IDEA_INITIAL_DIRECTORY^}` (Bash) ou `$PWD.Path` (PowerShell) garante que o caminho do projeto seja sempre normalizado no estilo Windows, unificando os hashes de Conteúdo e Sessão no Insight Dashboard.*

### Shim do `codex` (Opcional)

Se desejado, crie symlink para compatibilidade:
```bash
ln -s /d/Dev/Programas/node-v22.20.0-win-x64/context-mode /d/Dev/Programas/node-v22.20.0-win-x64/codex
```
Nota: Hooks funcionam mesmo sem o shim (configuração global no Codex está separada).

## 4. Comandos Utilitários de Diagnóstico

Sempre que houver instabilidade ou ausência de dados no dashboard, utilize os atalhos de prompt:

- `/ctx-doctor`: Valida instalação, hooks e conectividade.
- `/ctx-status`: Exibe snapshot de consumo e economia de contexto.
- `/ctx-insight`: Abre o dashboard em `http://localhost:4747`.
- `/ctx-checkpoint`: Persiste o estado da sessão atual para retomada cross-session.

## 5. Troubleshooting Comum

### 5.1. Sessions vazio, mas Knowledge Base tem dados

**Sintoma:** Knowledge Base exibe 4+ fontes e 10+ chunks "just now", mas Sessions mostra apenas eventos antigos ("11m ago").

**Causa:** Hooks estão **configurados globalmente** e funcionando, mas MCP precisa recarregá-los na inicialização do IDE.

**Solução (3 passos):**

1. **RESTART COMPLETO do IntelliJ:**
   ```bash
   # File → Exit (ou Ctrl+Q)
   # Aguarde 3-5 segundos
   # Reabra IntelliJ
   # Abra o projeto
   ```

2. **Validar Hooks após restart:**
   ```
   /ctx-doctor
   # Todos os 6 hooks devem estar [OK]
   ```

3. **Testar captura de eventos:**
   ```
   /ctx-status
   # Sessions deve exibir eventos com timestamp "just now" ou "<1m ago"
   ```

**Por quê?** Hooks são registrados pelo MCP apenas na inicialização do IDE, não em runtime. Sem restart, o dispatcher não carrega os handlers.

---

### 5.3. Erro [FAIL] Hook configuration no /ctx-doctor

**Sintoma:** O comando `/ctx-doctor` falha com `[FAIL] Hook configuration — não conseguiu ler .github/hooks/context-mode.json`.

**Causa:** O IntelliJ às vezes falha ao propagar o diretório de trabalho ou o path correto para os hooks.

**Solução:** 
1. Adote o padrão de **Dual-Case** e **Injeção de Ambiente** descrito na Seção 3.
2. Certifique-se de que o binário do `context-mode` esteja no PATH do sistema.
3. Se o erro persistir, use o fallback do `mcp.json` com `cd /d` (Seção 2).

---

### 5.4. Hook registrado mas nunca produz efeito (debug.log/state.json nunca aparecem)

**Sintoma:** mesmo com `Enable Hooks` ativado no plugin e `Editor preview features` habilitado no GitHub.com, um hook customizado (ex.: `.github/hooks/ctx-sequence-guard.ps1`) nunca cria evidência de execução (nenhum log de diagnóstico, nenhum state file).

**Causa raiz confirmada (2026-10-03, via `idea.log` com trace `#com.github.copilot:trace` habilitado em `Help → Diagnostic Tools → Debug Log Settings`)**: o host JetBrains Copilot aplica algum tipo de *template expansion* na string do campo `"powershell"`/`"bash"` do hook antes de repassá-la ao processo, e **apaga silenciosamente qualquer token `$variável`** que não reconheça como variável de template própria. O `stderr` capturado em `hookExecutions` mostra o sintoma de forma inequívoca — toda ocorrência de `$nome` vira vazio:

```
+ =[Console]::In.ReadToEnd(); =; try { =|ConvertFrom-Json; if(.cwd){=.c ...
```

(deveria ser `$in=[Console]::In.ReadToEnd(); $root=$null; try { $j=$in|ConvertFrom-Json; ...`)

**Diagnóstico**: localizar `idea.log` (`Help → Show Log in Explorer`, caminho típico `%LOCALAPPDATA%\JetBrains\<Produto><Versão>\log\idea.log`) e buscar por `hookExecutions` — se `status: "failure"` com `stderr` mostrando erro de parser com tokens `$` faltando, é este bug.

**Solução**: eliminar `$variável` literal do campo `"powershell"` do hook. Use `-EncodedCommand <Base64 UTF-16LE>` — a string resultante não contém `$` literal, portanto é imune ao templating do host. Detalhes completos (incluindo como regerar o Base64) em `.github/hooks/README.md`.

**Lição geral de troubleshooting**: nunca aceitar "feature desligada" ou "versão desatualizada" como causa raiz de um hook que não produz efeito sem antes consultar `hookExecutions` no `idea.log` com trace habilitado — é o único diagnóstico que revela o `stderr` real do processo spawnado.

---



1. **Dashboard vazio (No sessions):**

## 6. Checklist de Validação Pós-Restart

✅ **ESTADO VALIDADO (2026-06-17):**
- [x] IntelliJ reiniciado completamente
- [x] `/ctx-doctor` → Todos os hooks [OK] (Dual-Case funcional)
- [x] `/ctx-status` → Sessão ativa com telemetria detectada
- [x] Insight Dashboard → Exibindo sessões e chunks em tempo real

✅ **Conclusão:** O ambiente está 100% funcional e configurado para escala, garantindo que toda atividade no Copilot JetBrains seja indexada e rastreável pelo Context Mode.

---

**Data da última atualização:** 2026-06-16  
**Ambiente:** Windows + JetBrains + GitHub Copilot MCP + Context Mode v2.1.10  
**Modo:** ✅ Genérico (funciona com qualquer projeto no IntelliJ)  
**Hooks:** ✅ Globalmente configurados em `C:\Users\{username}\.codex\hooks.json`


<!-- Configuração v2.1.10: server.mjs --agent copilot-cli | CONTEXT_MODE_DATA_DIR -->

---

## 7. Troubleshooting: Diagnóstico e Correção do `context-mode doctor` / `ctx_doctor` (v2.1.10+)

Esta seção documenta as duas falhas diagnosticadas no código-fonte do **Context Mode (v2.1.10+)** ao executar o diagnóstico de integridade via CLI (`context-mode doctor`) ou via tool MCP (`ctx_doctor`) no IntelliJ IDEA, com suas respectivas causas raiz e soluções definitivas.

### 7.1. Falha 1 — `FAIL copilot-cli` / `FAIL codex`: `old context-mode entry, run: context-mode setup` (`D4 old entries` / `runDoctor`)

#### Sintoma

- **Na CLI (`context-mode doctor`)**: Os agentes `copilot-cli` e/ou `codex` falham com:
  ```text
  FAIL copilot-cli: old context-mode entry, run: context-mode setup
  FAIL codex: old context-mode entry, run: context-mode setup
  ```
- **Na tool MCP (`ctx_doctor`)**: O check `D4 (old entries)` reporta a presença de diretórios legados da v1:
  ```text
  D4 | old entries | WARN | old context-mode data dir <agent home>/context-mode/ | run ctx_upgrade
  ```

#### Causa Raiz no Código-Fonte (`src/setup/engine.ts` + `src/core/ops/detect-v1.ts` + `src/core/contracts/constants.ts`)

1. **Detecção de diretórios legados da v1 (`src/core/ops/detect-v1.ts`)**: A função `detectV1` verifica a existência de diretórios de dados legados da v1 em `<agentHome>/context-mode` (`~/.copilot/context-mode` e `~/.codex/context-mode`), emitindo `V1_REASON.dataDir` (`"old context-mode data dir <agent home>/context-mode/"`).
2. **Classificação em `constants.ts` (`src/core/contracts/constants.ts`)**: `V1_REASON.dataDir` pertence a `UPGRADE_KEEP_ASIDE_REASONS`, mas **não** faz parte de `UPGRADE_REPORT_ONLY_REASONS`.
3. **Promoção para `FAIL` em `runDoctor` (`src/setup/engine.ts`)**: Como `V1_REASON.dataDir` não consta em `UPGRADE_REPORT_ONLY_REASONS`, `runDoctor` força `status = "FAIL"` com `V1_FORM_REASON` (`"old context-mode entry, run: context-mode setup"`).

#### Solução Definitiva (Move-Aside Seguro com Backup)

Na v2, os dados ficam centralizados em `~/.context-mode` ou em `CONTEXT_MODE_DATA_DIR` (ex.: `~/.config/JetBrains/context-mode`). Mova (move-aside com backup) ou remova os diretórios legados `~/.copilot/context-mode` e `~/.codex/context-mode` para `backups/v1-aside-<timestamp>/`:

**Opção A — Script Node.js (Multiplataforma / Recomendado):**

```bash
node -e "
const fs = require('fs'), os = require('os'), path = require('path');
const home = os.homedir();
const ts = new Date().toISOString().replace(/[:.]/g, '-');
const backupRoot = path.join(home, '.context-mode', 'backups', 'v1-aside-' + ts);
for (const agentDir of ['.copilot', '.codex']) {
  const legacyDir = path.join(home, agentDir, 'context-mode');
  if (fs.existsSync(legacyDir)) {
    const dest = path.join(backupRoot, agentDir.slice(1) + '-context-mode');
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.renameSync(legacyDir, dest);
    console.log('Move-aside concluído:', legacyDir, '->', dest);
  }
}
"
```

**Opção B — PowerShell / Bash:**

```powershell
# PowerShell (Windows)
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $env:USERPROFILE ".context-mode\backups\v1-aside-$ts"
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
foreach ($agent in @(".copilot", ".codex")) {
    $legacy = Join-Path $env:USERPROFILE "$agent\context-mode"
    if (Test-Path $legacy) { Move-Item -Path $legacy -Destination (Join-Path $backupRoot ($agent.TrimStart(".") + "-context-mode")) -Force }
}
```

```bash
# Bash (Git Bash / Linux / macOS)
TS=$(date +%Y%m%d-%H%M%S) && BACKUP_DIR="$HOME/.context-mode/backups/v1-aside-$TS" && mkdir -p "$BACKUP_DIR"
for d in ~/.copilot/context-mode ~/.codex/context-mode; do [ -d "$d" ] && mv "$d" "$BACKUP_DIR/$(basename $(dirname "$d"))-context-mode"; done
```

---

### 7.2. Falha 2 — `D3 host config | FAIL | wrong: MCP entry` (`Plugin root for copilot-cli not found`) no IntelliJ

#### Sintoma

Ao executar `ctx_doctor` no IntelliJ IDEA com `CONTEXT_MODE_DATA_DIR` customizado (ex.: `C:\Users\{username}\.config\JetBrains\context-mode`), o check `D3 host config` falha com:

```text
D3 | host config | FAIL | wrong: MCP entry — Plugin root for copilot-cli not found at ~/.config/JetBrains/context-mode/plugins/copilot-cli/current. Fix: run ctx_upgrade. (absent) | run ctx_upgrade
```

#### Causa Raiz no Código-Fonte (`src/adapters/table.ts` + `src/core/ops/doctor-config.ts` + `src/core/ops/plugin-root.ts`)

1. **Definição do adapter (`src/adapters/table.ts`)**: O adapter `copilot-cli` utiliza `installMode: "plugin"` e não consta em `OWN_MCP_ENTRY`.
2. **Validação em `doctor-config.ts` (`src/core/ops/doctor-config.ts`)**: Em `mcpWrong`, quando `mcpFile` é `null`, ele valida `resolvePluginRoot(row, env, worktree)`.
3. **Resolução em `plugin-root.ts` (`src/core/ops/plugin-root.ts`)**: `resolvePluginRoot` exige que exista o symlink/junction `<CONTEXT_MODE_DATA_DIR>/plugins/copilot-cli/current` apontando para o diretório real do pacote `context-mode` (onde reside `server.mjs`). Quando `CONTEXT_MODE_DATA_DIR` é customizado para `~/.config/JetBrains/context-mode`, essa junction não existe por padrão se o setup foi rodado apenas no diretório global `~/.context-mode`.

#### Solução Definitiva (Criação da Junction `plugins/copilot-cli/current` ou `ctx_upgrade`)

Crie a junction/symlink `plugins/copilot-cli/current` dentro de `CONTEXT_MODE_DATA_DIR` (ex.: `~/.config/JetBrains/context-mode/plugins/copilot-cli/current`) e em `~/.context-mode/plugins/copilot-cli/current` apontando para o pacote global `context-mode` (ex.: `<node_global>/node_modules/context-mode`), ou execute `ctx_upgrade`:

**Opção A — Script Node.js (`fs.symlinkSync(..., 'junction')`):**

```bash
node -e "
const fs = require('fs'), os = require('os'), path = require('path'), { execSync } = require('child_process');
const home = os.homedir();
const pkgTarget = path.join(execSync('npm root -g', { encoding: 'utf8' }).trim(), 'context-mode');
for (const root of new Set([path.join(home, '.context-mode'), process.env.CONTEXT_MODE_DATA_DIR || path.join(home, '.config', 'JetBrains', 'context-mode')])) {
  const pluginDir = path.join(root, 'plugins', 'copilot-cli'), currentLink = path.join(pluginDir, 'current');
  fs.mkdirSync(pluginDir, { recursive: true });
  if (fs.existsSync(currentLink)) fs.rmSync(currentLink, { recursive: true, force: true });
  fs.symlinkSync(pkgTarget, currentLink, 'junction');
  console.log('Junction criada:', currentLink, '->', fs.realpathSync.native(currentLink));
}
"
```

**Opção B — Prompt de Comando Windows (`mklink /J`):**

```cmd
mkdir "%USERPROFILE%\.config\JetBrains\context-mode\plugins\copilot-cli" 2>nul
mklink /J "%USERPROFILE%\.config\JetBrains\context-mode\plugins\copilot-cli\current" "%APPDATA%\npm\node_modules\context-mode"

mkdir "%USERPROFILE%\.context-mode\plugins\copilot-cli" 2>nul
mklink /J "%USERPROFILE%\.context-mode\plugins\copilot-cli\current" "%APPDATA%\npm\node_modules\context-mode"
```

---

### 7.3. Tabela de Verificação Esperada (`ctx_doctor` 100% PASS — D1 a D11)

Após aplicar ambas as correções, todos os checks de `D1` a `D11` no `ctx_doctor` devem passar (`PASS`):

| Check | Rótulo (`DOCTOR_LABEL`) | Status Esperado | Detalhe Esperado (Ambiente Windows / IntelliJ) | Fix |
|---|---|---|---|---|
| **D1** | `version` | ✅ `PASS` | `2.1.10 (<sha>), latest latest on npm` | — |
| **D2** | `node` | ✅ `PASS` | `v22.x / v24.x (node:sqlite disponível)` | — |
| **D3** | `host config` | ✅ `PASS` | `hook-registered, mcp-registered, plugin root resolvido via junction` | — |
| **D4** | `old entries` | ✅ `PASS` | Sem diretórios legados `~/.copilot/context-mode` ou `~/.codex/context-mode` | — |
| **D5** | `hook round trip` | ✅ `PASS` | Execução `hook.mjs --agent copilot-cli` dentro do orçamento de latência | — |
| **D5b** | `double-fire` | ✅ `PASS` | Sem disparo duplicado de hooks entre escopos | — |
| **D6** | `MCP` | ✅ `PASS` | Servidor MCP respondendo na sessão ativa | — |
| **D7** | `project and worktree` | ✅ `PASS` | Worktree e diretório de projeto resolvidos com sucesso | — |
| **D8** | `context.db` | ✅ `PASS` | `PRAGMA integrity_check: ok` | — |
| **D9** | `index` | ✅ `PASS` | Índices FTS5 e tabelas de conteúdo íntegros | — |
| **D10** | `enforcement mode` | ✅ `PASS` | `enforcement mode: <warn|strict|off>` | — |
| **D11** | `shell` | ✅ `PASS` | `Git Bash: C:\Program Files\Git\bin\bash.exe` | — |
