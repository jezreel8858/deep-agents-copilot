# Plano de Implementação — Persistência de Estado de Sessão e Recuperação de Crash (Terminal Hang)

> Workflow: WORKFLOW-GOVERNANCE-MAINTENANCE — Etapa 3
> Data: 2026-09-27
> Baseado em: `docs/plans/20260927-governance-maintenance-session-checkpoint-recovery.md` (aprovado, 1 ajuste: NÃO criar skill nova)
> Executor: `@governance-factory`
> Tipo: revisão (múltiplos artefatos existentes)

## 1) Escopo Técnico Confirmado

| # | Artefato | Ação |
|---|---|---|
| 1 | `.github/skills/terminal-governance/SKILL.md` | Reescrever § 5 (antipadrão de espera bloqueante) + nova subseção 5.2 (watchdog obrigatório) + reforço na tabela de padrões proibidos |
| 2 | `.github/skills/agent-memory-policy/SKILL.md` | EXPANDIR (não criar skill nova) — nova subseção 3.2 "Checkpoint Automático Pré-Risco" + `source_docs` ampliado |
| 3 | `.github/hooks/context-mode.json` | Ler e confirmar limitação de schema (sem matcher por conteúdo de tool) — documentar a limitação em `agent-memory-policy/SKILL.md` § 3.2 em vez de alterar o JSON (evita corromper config funcional) |
| 4 | `.github/prompts/ctx-resume.prompt.md` | Nova seção "Retomada Após Crash/Trava SEM Checkpoint Prévio" (fallback best-effort via git status/diff) |
| 5 | `.github/skills/README.md` + `CHANGELOG.md` | Atualização de descrição das 2 linhas de catálogo + nova entrada [2.44.0] |

## 2) Decisão Técnica — Item 3 (context-mode.json)

Após leitura do schema real do hook (`sessionStart`, `PreToolUse`, `PostToolUse`, `preCompact`, etc.), confirmado que o formato é um mapa fixo de eventos de ciclo de vida → comando único (`bash`/`powershell`), **sem suporte a matcher condicional por nome de tool ou conteúdo do comando invocado**. Como JSON não suporta comentários, alterar o arquivo para "documentar" a limitação o corromperia como config válida. Decisão: **não modificar o JSON**; a limitação e a responsabilidade consequente (disparo do checkpoint pré-risco pelo agent, não pelo hook automático) são documentadas em `agent-memory-policy/SKILL.md` § 3.2.

## 3) Ordem de Execução (R-046 batching via context-mode)

1. Localização do root do workspace correto entre as 3 pastas declaradas (`D:/workspace/deep-agents-copilot` confirmado via `ctx_execute`).
2. Leitura em lote dos 7 arquivos-alvo via `ctx_execute`.
3. Edição consolidada de `terminal-governance/SKILL.md` (§5 + tabela de proibidos) com verificação de unicidade de âncora (R-051).
4. Edição consolidada de `agent-memory-policy/SKILL.md` (frontmatter `source_docs` + nova §3.2).
5. Edição de `ctx-resume.prompt.md` (frontmatter `source_docs` + nova seção de fallback).
6. Atualização de `.github/skills/README.md` (2 linhas de catálogo).
7. Atualização de `CHANGELOG.md` (nova entrada [2.44.0]).
8. Validação estrutural final (grep de termos normativos + contagem de agents afetados por R-055).

## 4) Incidente de Execução e Correção (Registro de Transparência)

Durante a Etapa 5, uma primeira tentativa de edição de `agent-memory-policy/SKILL.md` usou uma função de substituição com semântica incorreta (`anchorEnd = null` interpretado como "até o fim do arquivo"), o que truncou o arquivo para apenas ~1KB. O erro foi detectado imediatamente pela validação pós-edição (comprimento de arquivo inconsistente) e corrigido via `git checkout -- <arquivo>` (restauração do estado original) antes de reaplicar a edição com uma função de substituição de substring pura (`safeStrReplace`, sem semântica de fim de arquivo). Nenhuma mudança corrompida foi persistida além do sandbox local antes da correção.

## 5) Reúso Sistêmico (R-055)

- `terminal-governance/SKILL.md` é **referenciada**, não duplicada, por 61 agents que declaram `run_in_terminal` — a correção do antipadrão de espera bloqueante e a nova regra de watchdog propagam-se automaticamente sem necessidade de editar cada agent individualmente.
- Q2 (template): não há template de agent/skill a atualizar — a mudança é de conteúdo normativo dentro de uma skill já existente.
- Q3 (teste determinístico): necessário — sinalizado como pendente para `@governance-maintainer` (Etapa 4), validando presença de `timeout -k` / `isBackground` em `terminal-governance/SKILL.md`.

## 6) Critério de Pronto

- [x] `terminal-governance/SKILL.md` com § 5.2 (watchdog) e § 5 corrigida (antipadrão removido).
- [x] `agent-memory-policy/SKILL.md` com § 3.2 (checkpoint automático pré-risco) e `source_docs` ampliado.
- [x] Limitação do `context-mode.json` documentada (não modificado — decisão técnica registrada).
- [x] `ctx-resume.prompt.md` com fallback de crash sem checkpoint.
- [x] `.github/skills/README.md` e `CHANGELOG.md` atualizados.
- [x] Teste determinístico em `tests/governance_audit/` (`test_session_checkpoint_recovery_governance.py`).
