# Plano de Planejamento — Persistência de Estado de Sessão e Recuperação de Crash (Terminal Hang)

> Workflow: WORKFLOW-GOVERNANCE-MAINTENANCE
> Data: 2026-09-27
> Gatilho: Incidente relatado pelo usuário — script Python travou a sessão do Copilot Chat (JetBrains) durante fase de implementação de migração complexa, sem checkpoint prévio de estado, causando perda de continuidade.

## 1) Contexto do Incidente

- Ambiente: GitHub Copilot Chat, plugin JetBrains.
- Gatilho: agent codificador executou script Python via `run_in_terminal` sem timeout/watchdog.
- Efeito: comando ficou bloqueado aguardando output (hang indefinido do `run_in_terminal`), sessão travada, sem possibilidade de continuar ou recuperar estado em nova sessão.
- Causa raiz confirmada por pesquisa de mercado (não é bug isolado nosso): **issues públicas abertas contra o próprio plugin JetBrains do Copilot** relatam o mesmo comportamento (GitHub Community Discussion #161238; `microsoft/copilot-intellij-feedback#788`; `microsoft/vscode#271999`; YouTrack `RIDER-128167`).

## 2) Pesquisa de Mercado — Resumo Executivo

| Achado | Fonte | Aplicabilidade |
|---|---|---|
| GitHub Copilot SDK/CLI (oficial) já tem "session persistence" nativa (`checkpoints/*.json` + `plan.md`, `resumeSession(sessionId)`) — **mas não está disponível no plugin JetBrains** (nosso client) | docs.github.com/copilot-sdk/features/session-persistence | Confirma que é lacuna de mercado no client atual, não só nossa — não há solução nativa a esperar do fornecedor no curto prazo |
| Claude Code (padrão comunitário replicável): hooks `SessionStart`/`PreCompact` lêem/escrevem `.mind/STATE.md`, `.mind/PROGRESS.md`, `.mind/DECISIONS.md`, checkpoint automático pré-compactação | GitHub `anthropics/claude-code#25999` | Padrão diretamente replicável via hooks já existentes em `context-mode.json` |
| LangGraph Checkpointer: snapshot automático a cada unidade atômica de trabalho, não só ao final | docs.langchain.com/langgraph/checkpointers | Justifica checkpoint **pré-comando-de-risco**, não apenas periódico |
| Watchdog universal de terminal: wrapper `timeout -k <graça> <limite> <cmd>` (GNU coreutils) | linuxize.com/timeout-command-in-linux; padrão adotado por Aider/Codex CLI/hermes-agent | Mitigação direta e de baixo custo para o gatilho do incidente |
| Causa raiz do hang no JetBrains + workaround comunitário: nunca aguardar output bloqueante direto; usar `isBackground:true` + redirect a arquivo + leitura posterior | GitHub Community Discussion `#161238` | Mitigação direta e de baixo custo, sem depender de fix do fornecedor |
| Formato de checkpoint recomendado pelo mercado: híbrido JSON (máquina) + Markdown (humano); frequência: antes de operação de risco | Copilot SDK oficial + padrão Claude Code + `mcp-memory` | Já compatível com o formato existente de `/ctx-checkpoint` neste repo |

Fonte completa da pesquisa: registrada nesta sessão via `@deep-search` (não persistida em arquivo separado — citações acima consolidam o essencial).

## 3) Gaps Confirmados (Auditoria `@agent-auditor`, read-only)

| # | Gap | Artefato afetado | Severidade |
|---|---|---|---|
| 1 | Sem wrapper `timeout -k` obrigatório para comandos potencialmente bloqueantes (scripts Python, processos interativos) | `.github/skills/terminal-governance/SKILL.md` | Alto |
| 2 | Sem padrão `isBackground:true` + redirect a arquivo + leitura posterior para o client JetBrains — pior, § 5 atual prescreve "aguardar output completo", o antipadrão que causou o hang | `.github/skills/terminal-governance/SKILL.md` § 5 | **Crítico** |
| 3 | Sem checkpoint automático de estado de sessão (plano ativo, arquivos em edição, último passo concluído) ANTES de operação de risco | `.github/skills/agent-memory-policy/SKILL.md`, `.github/prompts/ctx-checkpoint.prompt.md`, `.github/hooks/context-mode.json` | **Crítico** |
| 4 | Hook `PreToolUse` sem matcher/granularidade por tool ou classificação de risco do comando | `.github/hooks/context-mode.json` | Alto |
| 5 | Sem protocolo de retomada pós-crash quando NÃO houve checkpoint prévio salvo (distinto do `/ctx-resume` sob demanda) | `.github/prompts/ctx-resume.prompt.md` | Alto |
| 6 | 15 agents declaram `run_in_terminal` em `catalog.yaml` sem visibilidade de conformidade com a nova regra | `.github/agents/catalog.yaml` | Sugestão |

## 4) Escopo da Remediação Proposta (Etapa 3+ do Workflow)

1. **Atualizar `terminal-governance/SKILL.md`**: adicionar seção normativa obrigatória de "Watchdog de Comando Bloqueante" — exigir `timeout -k <graça> <limite> <cmd>` (Linux/WSL/Git Bash) e equivalente `Start-Job`/`Wait-Job -Timeout` (PowerShell) para qualquer script/processo sem timeout nativo; reescrever § 5 para diferenciar "serialização de comandos independentes" de "comando potencialmente bloqueante", exigindo `isBackground:true` + redirect a arquivo (`| tee`/`> arquivo.log`) + leitura via `read_file`/`ctx_execute_file` como padrão obrigatório no client JetBrains.
2. **Expandir `agent-memory-policy/SKILL.md` (decisão do usuário — NÃO criar skill nova)**: formalizar checkpoint automático (formato híbrido Markdown + JSON, reaproveitando `/ctx-checkpoint`) disparado **antes de qualquer operação classificada como risco** (execução de script, comando de longa duração, comando sem timeout nativo) — acoplado ao hook `PreToolUse` já existente em `context-mode.json`. Granularidade/frequência exata delegada ao `@governance-factory` na fase técnica (Plano de Implementação).
3. **Atualizar `.github/hooks/context-mode.json`**: documentar/especificar matcher condicional para `run_in_terminal` com comando de risco, disparando o checkpoint automático do item 2.
4. **Atualizar `ctx-resume.prompt.md`**: adicionar fluxo de fallback para "sessão travou sem checkpoint prévio" — reconstrução best-effort via `git status`/`git diff` + inspeção de handoff.
5. **Propagação e quality gate** (`@governance-maintainer`): confirmar que a nova regra é referenciada pelos 15 agents que declaram `run_in_terminal`; criar teste determinístico em `tests/governance_audit/` que falhe se `terminal-governance/SKILL.md` não contiver os termos normativos `timeout -k` / `isBackground`.

## 5) Não-Escopo

- Não implementar nenhum fix no plugin JetBrains do Copilot em si (fora do nosso controle).
- Não criar mecanismo de "kill automático de processo zumbi" além do wrapper `timeout -k` (nenhuma ferramenta de mercado pesquisada faz isso nativamente).
- Não modificar `context-mode` MCP server (dependência externa) — apenas a camada de governança/skills/hooks deste repositório que orienta o agent a usá-lo corretamente.

## 6) Critério de Pronto

- `terminal-governance/SKILL.md` contém seção de watchdog obrigatório + padrão `isBackground` corrigido.
- Nova skill (ou extensão) de checkpoint automático pré-risco documentada e registrada em `.github/skills/README.md` (ou catálogo equivalente).
- `context-mode.json` com matcher documentado para `run_in_terminal` de risco.
- `ctx-resume.prompt.md` com fallback de crash sem checkpoint.
- Teste determinístico criado em `tests/governance_audit/`.

## 7) Decisão do Usuário (Aprovação)

- Escopo aprovado com 1 ajuste: **NÃO criar skill nova** — expandir `agent-memory-policy/SKILL.md` (item 2 da Seção 4 já atualizado).
- Granularidade/frequência do checkpoint automático: delegada ao `@governance-factory` na fase técnica.

## 8) Próximo Passo

Prosseguir à Etapa 3 (`@governance-factory` — Plano de Implementação técnico + execução dos itens 1, 2 (expansão de `agent-memory-policy`), 3, 4 e 5 da Seção 4).
