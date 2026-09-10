# Guia de Configuração: Context Mode no IntelliJ IDEA

Este documento consolida todas as etapas necessárias para configurar e estabilizar o **Context Mode** no ambiente JetBrains (IntelliJ IDEA), garantindo que o MCP, o Knowledge Base e o Insight Dashboard funcionem corretamente de forma genérica.

## 📊 Status Atual (v1.0.162)

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
| `CONTEXT_MODE_DIR`    | `C:\Users\{username}\.config\JetBrains\context-mode` | Raiz de armazenamento dos bancos de dados         |
| `INSIGHT_SESSION_DIR` | `%CONTEXT_MODE_DIR%\sessions`                       | Localização do banco de sessões e telemetria      |
| `INSIGHT_CONTENT_DIR` | `%CONTEXT_MODE_DIR%\content`                        | Localização do banco de conteúdo (Knowledge Base) |

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
        "cd /d D:\\workspace\\eco-sistema-app && D:\\Dev\\Programas\\node-v26.3.0-win-x64\\context-mode.cmd"
      ],
      "env": {
        "SOURCE": "jetbrains-copilot",
        "IDEA_INITIAL_DIRECTORY": "<workspace>/[PROJETO-EXEMPLO]",
        "CONTEXT_MODE_PROJECT_DIR": "<workspace>/[PROJETO-EXEMPLO]",
        "CONTEXT_MODE_DIR": "C:\\Users\\{username}\\.config\\JetBrains\\context-mode",
        "INSIGHT_SESSION_DIR": "C:\\Users\\{username}\\.config\\JetBrains\\context-mode\\sessions",
        "INSIGHT_CONTENT_DIR": "C:\\Users\\{username}\\.config\\JetBrains\\context-mode\\content",
        "CONTEXT_MODE_IDLE_TIMEOUT_MS": "0"
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

### Resumo anterior (legado — para referência)

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
**Ambiente:** Windows + JetBrains + GitHub Copilot MCP + Context Mode v1.0.162  
**Modo:** ✅ Genérico (funciona com qualquer projeto no IntelliJ)  
**Hooks:** ✅ Globalmente configurados em `C:\Users\{username}\.codex\hooks.json`
