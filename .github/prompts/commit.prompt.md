---
name: commit
description: >-
  Gera mensagem de commit convencional (PT-BR), título/descrição de PR com matriz
  de risco e plano de rollback, e entrada de CHANGELOG, consumindo a skill
  git-governance. Aplica guardrail de segredos e atomicidade. NÃO executa
  git add/commit/push.
agent: 'agent'
router_bypass: utility
model: "Gemini 4 Hydrogen"
tools: ['context-mode/ctx_batch', 'context-mode/ctx_execute', 'context-mode/ctx_search']
argument-hint: '[contexto-opcional-da-mudança]'
source_docs:
  - '.github/skills/git-governance/SKILL.md'
  - '.github/skills/efficient-batch-code-modification/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/commit`

Analisa o diff/stage e gera mensagem de commit, título/descrição de PR e entrada de CHANGELOG. Regras normativas vivem na skill [`git-governance`](../skills/git-governance/SKILL.md) (SSOT); consultar `references/` sob demanda.

```bash
/commit
/commit "contexto opcional da mudança"
```

> **Arquivo Ativo**: `${file}` · **Workspace**: `${workspaceFolder}`

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/commit` (argumento: `[contexto-opcional-da-mudança]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` nem delegar via `run_subagent` — este prompt utilitário possui `router_bypass: utility` (exceção canônica a R-037/R-063) e DEVE ser executado diretamente pelo Orquestrador Raiz.
- ✅ APENAS analisar diff/log e gerar texto (commit, PR, CHANGELOG).
- ✅ SEMPRE executar o guardrail de segredos antes de emitir qualquer mensagem.
- ❌ NUNCA executar `git add`, `git commit` ou `git push` (R-031) nem alterar o índice do git.
- ❌ NUNCA gerar mensagem para diff com credencial/caminho local absoluto exposto (R-010 / R-044).
- ✅ O uso de context-mode é 100% OBRIGATÓRIO para leituras e inspeções quando disponível (R-008 / R-046 / R-056 / Smell 2.24 / Smell 2.26): toda coleta via `ctx_batch` ou script consolidado em lote único. Proibido terminal de leitura e ferramentas nativas de editor; sem chamadas unitárias encadeadas.

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/commit`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## 📋 Fluxo em 5 Passos

### Passo 1 — Guardrail de Segredos (bloqueante)

Coletar em **uma** chamada batch: `git --no-pager diff HEAD -- . ':!*.lock' ':!*.min.js'`, `git --no-pager status --short`, `git --no-pager diff --stat HEAD`. Varrer o diff com o catálogo de `references/secrets-guardrail.md` (camada 3).

- Achado → **PARAR**, reportar `arquivo:linha` (sem ecoar o valor), exigir remoção + rotação.
- Limpo → prosseguir.

### Passo 2 — Inspeção do Stage

Priorizar `Changes to be committed`. Sem stage: listar modificados relevantes e sugerir `git add <arquivos>`. Stage misto: sugerir `git add` complementar para a mesma intenção.

### Passo 3 — Atomicidade

Aplicar o teste do "e" (`references/commit-formats.md` § 3). Não-atômico → sugerir split (`git add -p`) e gerar uma mensagem por commit.

### Passo 4 — Classificação e Estrutura

Definir tipo, escopo e breaking change (`references/commit-formats.md` § 1-2). Escolher o formato por volume: **A** (1-5 arquivos) ou **B** (6+ ou múltiplas frentes) — § 4-5. Incluir "Como validar" (§ 6), motivo/substituto para removidos (§ 7) e trailers reais (§ 8).

### Passo 5 — Apresentação

> **Anti-Corrupção de Markdown**: NUNCA encapsular a resposta inteira em bloco global; cada artefato copiável deve ser um bloco isolado e autocontido (Blocos 1 a 5).

Apresentar a saída estruturada nas seguintes seções claras:

1. **Bloco 1 (Mensagem de Commit)**: bloco ```text isolado pronto para revisão (Formato A ou Formato B conforme `references/commit-formats.md`).
2. **Bloco 2 (Comando para Execução Manual)**: bloco ```bash isolado utilizando `git commit -F - << 'EOF' ... EOF` (precedido de `git add` se sugerido) para preservar formatação e evitar cercas aninhadas.
3. **Bloco 3 (Título do PR)**: bloco ```text isolado no formato Conventional Commits (≤72 cols, imperativo, PT-BR).
4. **Bloco 4 (Descrição do PR)**: bloco ````markdown isolado (delimitado por 4 backticks) com seções "O que mudou", "Matriz de Risco", "Plano de Rollback", "Como validar" e "Checklist" (alinhado a `references/pr-template.md`). Em "Como validar", usar inline code para evitar conflito de cercas.
5. **Bloco 5 (CHANGELOG.md - Entrada Sugerida)**: bloco ```diff isolado sugerido no formato Keep a Changelog / SemVer (alinhado a `references/changelog.md` §4: `<= 200 chars` por bullet, `<= 8 bullets` por versão e zero listagem exaustiva de arquivos/RCA).

A matriz de risco segue `references/risk-matrix.md`. Em "Como validar", usar inline code.

## ✅ Checklist Antes de Exibir

- [ ] Guardrail de segredos executado e diff limpo
- [ ] Mensagem reflete o stage; atomicidade respeitada
- [ ] Título imperativo, PT-BR, sem ponto final, ≤ 72 cols; corpo ≤ 72 cols
- [ ] Removidos com motivo e substituto; "Como validar" presente
- [ ] PR com Matriz de Risco e Plano de Rollback; CHANGELOG compatível com SemVer e `references/changelog.md` §4 (`<= 200 chars/bullet`, `<= 8 bullets/versão`, sem listas exaustivas/RCA)
- [ ] Blocos isolados (sem cerca global ou aninhada)
- [ ] Nenhum comando git de escrita executado

## 🔄 Referências

- Skill SSOT: [`.github/skills/git-governance/SKILL.md`](../skills/git-governance/SKILL.md)
- Consumidor correlato: [`@pr-gatekeeper`](../agents/pr-gatekeeper.agent.md)

---

*v2.0 — commit prompt — modularizado sobre git-governance (SSOT única)*

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/commit` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/commit`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
**Enumerar & Consolidar (`>= 2` alvos):** Liste todos os arquivos/comandos antes de agir (mesmo em prompts curtos). Para `>= 2` alvos, use `ctx_batch` ou script único em `ctx_execute` (`language: "javascript"` com `fs`/`path` nativos para I/O; proibido `python`/`python -c` para I/O por bloqueio AMSI/Defender e varreduras irrestritas). Em timeout (`ETIMEDOUT`/`taskkill`), máx. **1 retry** trocando de estratégia; no 2º, aborte e reporte via Compact Error Reporting (`R-020`).
**Orçamento de Turnos & Warm Start (R-060):** Teto de **5 tool turns** por ciclo (1: Batch Gather / Warm Start silencioso; 2: Execução em lote; 3: Validação). Ao atingir o Turno 4 sem conclusão, acione o Circuit Breaker, salve evidências no `ctx_index` e finalize ou use `ask_questions` (`R-027`: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais, `description` com `[Consequência prática + Trade-off]` e 1ª opção `(Recomendado)`).
**Recibo Estruturado de Etapa (R-068):** Encerre entregas de pipeline com bloco YAML `receipt` + `step_delta` conforme `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml` (`mode: readonly_analysis` para Score 0; máx. 10 itens inline; excedente em `ctx_index` `wf:<trace>:delta:step-<n>`).
**Pós-Mutação & Conformidade de Plano (R-051 / R-064):** Execute mutações em lote atômico, rode `get_errors` agrupado uma única vez ao final e preencha `step_delta.plan_conformance` (`within_allowed_files`, `out_of_scope_files`) contra `allowed_files` do `plan_ref` ativo.

</execution_protocol>
