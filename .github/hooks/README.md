# Hooks - Harness Controls (governança genérica)

Este diretório concentra hooks operacionais para manter execução previsível no IDE.

## ⚠️ Causa raiz real confirmada (JetBrains): host faz *templating* de `$variável` na string de comando do hook

**Diagnóstico de campo (2026-10-03), confirmado via `idea.log` com `#com.github.copilot:trace`**:
um bug anterior (resolução de `cwd`, ver histórico abaixo) foi corrigido com um bootstrap inline em
PowerShell usando variáveis `$in`, `$root`, `$j`, `$p`. **Esse fix nunca funcionou de fato** — o
`stderr` capturado no `idea.log` mostrava erro de parser do PowerShell com todo token `$algumacoisa`
silenciosamente **apagado** da string antes da execução:

```
+ =[Console]::In.ReadToEnd(); =; try { =|ConvertFrom-Json; if(.cwd){=.c ...
```

(deveria ser `$in=[Console]::In.ReadToEnd(); $root=$null; try { $j=$in|ConvertFrom-Json; if($j.cwd){$root=$j.c...`)

**Causa raiz real**: o host JetBrains Copilot aplica algum tipo de *template expansion* na string do
campo `"powershell"`/`"bash"` do hook antes de repassá-la ao processo — qualquer `$token` que ele não
reconhece como variável de template própria é removido, e não escapado. Isso explica por que **nenhum
hook com `$variável` cru no JSON jamais chegou a executar com sucesso** (nem telemetria, nem o guard).

**Fix definitivo**: eliminar completamente o uso de `$variável` literal nos campos `"powershell"` do
hook. Os comandos `powershell` em `context-mode.json` agora usam
`-EncodedCommand <Base64 UTF-16LE>` — a string resultante não contém nenhum caractere `$` literal,
portanto é imune a esse templating. O script PowerShell real (equivalente ao bootstrap anterior,
agora apenas codificado) permanece o mesmo: lê o payload do stdin, extrai `cwd`, resolve o caminho do
script alvo (`ctx-sequence-guard.ps1` / `ctx-sequence-reset.ps1`) e invoca passando o stdin como
parâmetro posicional. Para regenerar o Base64 após qualquer alteração na lógica do bootstrap, use
Node (`Buffer.from(script, 'utf16le').toString('base64')`) — evite gerar via `powershell -Command`
com here-string em terminais Git Bash/MINGW, que tende a corromper o heredoc.

**Validado end-to-end**: `echo '<payload>' | powershell -EncodedCommand <base64>` reproduzido
manualmente no terminal com payload real (`cwd` apontando para a raiz do projeto) — sequência
`allow → deny` confirmada, e `.github/hooks/.state/ctx-sequence-guard.debug.log` populado
corretamente, provando execução real (não apenas ausência de erro).

### Histórico: bug anterior (cwd do processo ≠ cwd declarado no hook)

Antes do bug acima ser descoberto, já havia sido identificado e corrigido um problema distinto: o
host gera o processo do hook a partir do diretório de instalação do plugin
(`C:\Program Files\JetBrains\IntelliJ IDEA 2026.2.1\...`), ignorando o campo `"cwd": "."` declarado
em `context-mode.json`. A correção (ler o `cwd` do próprio payload JSON do hook, em vez de confiar no
`cwd` do processo) continua válida e está embutida no script agora codificado em Base64 — apenas a
*forma de transporte* da lógica mudou (de `$var` cru para `-EncodedCommand`), não a lógica em si.

## ⚠️ Hipótese forte (não definitivamente confirmada para JetBrains, mas com precedente documentado): `preToolUse` não é aplicado a chamadas de tool feitas por **subagents** (`run_subagent`)

**Evidência (2026-10-03)**: mesmo após o fix de `-EncodedCommand` (confirmado funcional via teste manual
isolado no terminal — ver seção acima), um teste real em IntelliJ Copilot Chat onde `agent-router`
delegou a um subagent (`docs-engineer`) que executou 3 chamadas sequenciais de `ctx_execute` **não
disparou o hook nenhuma vez** — nem `ctx-sequence-guard.debug.log` nem `ctx-sequence-guard.json` foram
criados. Isso descarta definitivamente bug de templating/cwd como causa *neste* cenário específico,
pois ambos já estavam corrigidos e validados isoladamente.

**Precedente documentado em produto irmão**: `github/copilot-cli` teve o bug
["`preToolUse` hooks are not enforced in subagents" (#2392)](https://github.com/github/copilot-cli/issues/2392)
— hooks configurados funcionavam corretamente para o agente principal, mas eram **completamente
ignorados** para chamadas de tool feitas por subagents via `task`/`run_subagent`. O bug foi corrigido
na CLI (v1.0.49-0), mas **o agente JetBrains usa um bundle próprio e separado**
(`copilot-agent/dist/main.js`, confirmado em
[issue #1819](https://github.com/microsoft/copilot-intellij-feedback/issues/1819)), historicamente
mais atrasado em paridade de recursos de hooks (ex.: ainda não honra `modifiedArgs`/`updatedInput`).
É plausível que o mesmo bug de arquitetura (hooks só interceptam a árvore de execução do agente
principal, não subagents) ainda esteja presente no plugin JetBrains, sem ter sido corrigido em
paridade com a CLI.

**Teste decisivo para confirmar/descartar**: repetir o mesmo prompt de teste, mas instruindo
explicitamente o `agent-router` a **não delegar a nenhum subagent** e executar as chamadas
`ctx_execute` diretamente ele mesmo. Resultado esperado por hipótese:
- Se o hook disparar (debug.log populado, 2ª chamada bloqueada) quando só o agente raiz chama a tool
  → confirma que o bypass é específico de subagents.
- Se o hook continuar sem disparar mesmo com o agente raiz → o problema é mais amplo (schema, versão
  do plugin, ou outro fator ainda não identificado) e a hipótese de subagent-bypass deve ser descartada
  como causa única.

**Se confirmado (subagent-bypass)**: a implicação prática é que **hooks `preToolUse` não são uma
camada de enforcement confiável para tool calls originadas de dentro de um subagent** neste host —
a disciplina via prompt/`SKILL.md` (preferir `ctx_batch_execute`) continua sendo a única linha de
defesa disponível para subagents, até que o plugin JetBrains corrija a paridade com a CLI. Recomenda-se
reportar este achado como issue em `microsoft/copilot-intellij-feedback` referenciando o padrão de
`github/copilot-cli#2392`.



## Hooks disponíveis

### Context Mode

- `.github/hooks/context-mode.json`
  - Registra hooks JetBrains Copilot para `context-mode`.
  - Eventos: `PreToolUse`, `PostToolUse`, `PreCompact`, `SessionStart`.
  - Papel: continuidade de sessão e recuperação de contexto com `ctx_search`.

### Circuit Breaker Mecânico — `ctx-sequence-guard` (Anti MCP Tool Chaining Sequencial)

- `.github/hooks/ctx-sequence-guard.ps1` / `.sh`
  - Hook `PreToolUse` **único** (1 entrada por evento — a telemetria original do `context-mode`
    foi incorporada dentro do próprio script, em vez de uma 2ª entrada no array, após confirmarmos
    empiricamente que o host JetBrains Copilot não garante execução de múltiplas entradas por
    evento no mesmo array).
  - **Fecha o gap documentado em `.github/skills/context-mode/SKILL.md` § 4.1**: o Circuit
    Breaker ali descrito era puramente comportamental (prompt-only), sem enforcement real —
    o que permitia a LLMs fortes (incl. Claude Sonnet) ignorá-lo sob pressão de tarefa.
  - **Mecanismo**: mantém um contador de sessão em `.github/hooks/.state/ctx-sequence-guard.json`
    (gitignored). Toda chamada de `ctx_execute`/`ctx_execute_file` incrementa o contador; toda
    chamada de `ctx_batch_execute` (ou qualquer outra ferramenta) zera o contador. Ao atingir
    `counter >= 2` (2ª chamada consecutiva sem lote interposto), o hook retorna
    `{"permissionDecision":"deny", "permissionDecisionReason": "..."}`.
  - **Log de diagnóstico incondicional**: `.github/hooks/.state/ctx-sequence-guard.debug.log`
    registra toda invocação do hook (timestamp, PID, tamanho do stdin, preview), **independente
    da decisão tomada**. Use este arquivo para provar empiricamente se o host está de fato
    invocando o hook — se o arquivo não existir após uma tarefa com múltiplas chamadas de tool,
    siga o checklist de diagnóstico abaixo antes de suspeitar do script em si.
  - **Reação esperada do agente a um `deny`**: tratar a mensagem como feedback automatizado
    corrigível (equivalente a um erro de lint/CI), nunca como uma negação de permissão do
    usuário — isto é, replanejar imediatamente com `ctx_batch_execute` e prosseguir, sem parar
    nem pedir confirmação ao usuário.
  - `ctx-sequence-reset.ps1` / `.sh` (`SessionStart`, 1 entrada por evento, telemetria embutida)
    limpa o contador no início de cada sessão para não herdar estado `OPEN` de uma anterior.
  - **Fail-open absoluto**: qualquer erro interno do script (JSON inválido, `jq` ausente, falha
    de I/O) sempre resulta em `allow` — o guard nunca pode ser a causa de um bloqueio indevido.

## Checklist de Diagnóstico — Hook Registrado mas Nunca Produz Efeito Observável

Ordem recomendada de investigação quando um hook (qualquer evento) parecer não disparar:

1. **Plugin version** `>= 1.5.57` (mínimo documentado pelo projeto `context-mode` para suporte a
   hooks no JetBrains).
2. **Toggle "Enable Hooks"** em `Settings → Tools → GitHub Copilot → Chat` — confirmar habilitado
   (já é o padrão em contas recentes; raramente é o problema, mas é o check mais barato).
3. **Conta Business/Enterprise**: confirmar que a política de org "Editor preview features" está
   habilitada pelo administrador (irrelevante para Individual/Pro).
4. **IDE reiniciado** após qualquer mudança de toggle (hooks carregam na inicialização do plugin).
5. **`idea.log` com trace habilitado** (`Help → Diagnostic Tools → Debug Log Settings` →
   adicionar `#com.github.copilot:trace`) — localizar `idea.log` via `Help → Show Log in Explorer`
   (caminho típico: `%LOCALAPPDATA%\JetBrains\<Produto><Versão>\log\idea.log`) e buscar por
   `hookExecutions` — cada entrada mostra `source` (qual arquivo `.json` de hook), `status`
   (`planned`/`success`/`failure`) e, em caso de falha, `exitCode`/`stdout`/`stderr` do processo
   spawnado. **Este é o diagnóstico definitivo** — se `hookExecutions` nunca aparecer no log para
   o evento esperado, o host realmente não está carregando aquele hook; se aparecer com
   `status: "failure"`, o `stderr` captado geralmente revela a causa exata (ex.: erro de
   resolução de caminho, módulo Node ausente, etc.) sem necessidade de instrumentação adicional
   no próprio script.
6. **Verificar se o `cwd` do processo spawnado bate com a raiz do projeto** — ver seção acima.
7. **Verificar se o `stderr` do `hookExecutions` mostra tokens `$` ausentes/apagados** (ex.:
   `=algo` em vez de `$var=algo`) — sintoma do bug de templating documentado na seção acima; a
   correção é usar `-EncodedCommand` em vez de `$variável` crua no campo `"powershell"`.

## Variantes de Capitalização dos Eventos

O arquivo `context-mode.json` declara cada evento em **duas variantes de capitalização** propositalmente:

| camelCase | PascalCase | Motivo |
|---|---|---|
| `sessionStart` | `SessionStart` | JetBrains Copilot usa `SessionStart`, Claude Code usa `sessionStart` |
| `userPromptSubmitted` | `UserPromptSubmitted` | Compatibilidade multi-plataforma |
| `preToolUse` | `PreToolUse` | idem |
| `postToolUse` | `PostToolUse` | idem |
| `preCompact` | `PreCompact` | idem |
| `errorOccurred` | `ErrorOccurred` | idem |

**Não remover** as variantes duplicadas — são necessárias para garantir que os hooks disparem em ambas as plataformas.

## Fallback mínimo

Se o hook não estiver disponível:

1. Registrar no resultado que o fallback foi usado.
2. Prosseguir com workflow por prompts (`/plan`, `/implement`, `/validate`, `/research`).
3. Priorizar `ctx_*` quando o MCP estiver acessível novamente.

## Integração

- Manter `.github/hooks/context-mode.json` versionado.
- Alinhar qualquer mudança com `CLAUDE.md` e `.github/copilot-instructions.md`.
