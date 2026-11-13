---
name: implement
description: Executa plano aprovado fase a fase, marcando `- [x]` ao concluir e registrando checkpoints obrigatórios.
agent: 'agent'
router_bypass: slash_workflow
model: "Claude Sonnet 5.5"
tools: ['read_file', 'insert_edit_into_file', 'create_file', 'grep_search', 'file_search', 'get_errors', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_search', 'context-mode/ctx_batch_execute', 'context-mode/ctx_execute', 'context-mode/ctx_execute_file']
argument-hint: '[caminho-do-plano | descrição-da-fase]'
source_docs:
  - '.github/skills/efficient-batch-code-modification/SKILL.md'
  - '.github/skills/terminal-governance/SKILL.md'
  - 'docs/plans/implementation/README.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/implement`

> **Propósito**: Executar plano técnico aprovado fase a fase sob R-031 (zero-interrupção), marcando `- [x]` ao concluir.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/implement` (argumento: `[caminho-do-plano | descrição-da-fase]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** executar as tarefas estritamente especificadas no plano aprovado.
- ✅ **SEMPRE** aplicar Single-Turn Batching e limiar de 5 arquivos da skill `efficient-batch-code-modification` (R-046).
- ✅ **SEMPRE** validar `get_errors` ao final de cada fase executada.
- ❌ **NÃO** parar para pedir confirmações intermediárias (R-031) exceto por bloqueio absoluto (credencial exposta ou estado irrecuperável).
- ❌ **NÃO** fazer commits autônomos ou alterar arquivos fora do plano aprovado.

---

Você foi encarregado de implementar um plano técnico aprovado. Planos contêm fases com mudanças específicas e critérios de sucesso.

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/implement`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## Início

Dado o plano ou descrição:
- Leia o plano **completamente** (sem `offset/limit`)
- Cheque checkmarks existentes (`- [x]`)
- Retome contexto por `ctx_search(..., sort: "timeline")` e só depois colete o necessário
- Evite leitura integral dos arquivos por padrão; use `ctx_batch_execute`/`ctx_search` para mapear impacto
- Leia trecho literal com `read_file` apenas quando necessário para edição precisa
- Pense como as peças se encaixam antes de agir
- Comece a implementar fase por fase

Sem plano definido: peça o arquivo ou a descrição.

## Filosofia de Implementação

Planos são cuidadosamente desenhados, mas a realidade pode divergir. Seu trabalho é:
- Seguir a intenção do plano **adaptando** ao que encontra
- Implementar cada fase **completamente** antes da próxima
- Verificar que o trabalho faz sentido no contexto mais amplo
- **Atualizar checkboxes** no plano conforme conclui itens

Se algo não bate com o plano exatamente, comunique claramente:

```
Problema na Fase [N]:
Esperado: [o que o plano diz]
Encontrado: [situação atual]
Por que importa: [explicação]

Como proceder?
```

## Verificação por Fase

Após cada fase:
- Execute verificações previstas no plano (automáticas e manuais)
- Corrija problemas antes de seguir
- **Marque `- [x]`** no plano com a ferramenta de edição disponível, em uma única alteração agrupada no arquivo
- **Registre checkpoint obrigatório** com `/ctx-checkpoint` imediatamente após marcar `[x]`
- **Pause para verificação humana** quando houver passos manuais:

```
Fase [N] Completa — Pronto para Verificação Manual

Verificação automatizada passou:
- [lista do que passou]

Checkpoint registrado via /ctx-checkpoint:
- checkpoint::<task-slug>::<YYYY-MM-DD-HHmm>

Por favor execute os passos manuais:
- [lista dos manuais]

Me avise quando concluir para prosseguir à Fase [N+1].
```

Se instruído a executar múltiplas fases consecutivamente, pule a pausa até a última.

**Não marque itens de verificação manual sem confirmação do usuário.**

## Regras Críticas (não negociáveis)

- **Checkpoint obrigatório por fase** — ao concluir cada fase (marcar `[x]`), executar `/ctx-checkpoint`
- **Checkpoint obrigatório de fechamento** — ao concluir a última fase/plano, executar `/ctx-checkpoint` final
- **Checkpoint obrigatório** — após cada `[x]` marcado, declare `lastStep` e `nextStep` para captura pelo Context Mode
- **Sem loops de correção** — se algo falhar, PARE e explique (formato 3 linhas: Causa/Local/Ação)
- **Sem commits/push autônomos** — gere apenas mensagem via `/commit`
- **Um comando por vez** via `ctx_execute`
- **`get_errors` UMA vez** por arquivo editado
- **Edições agrupadas** — todas as mudanças de um arquivo em uma chamada
- **Token budget obrigatório** — agrupar perguntas em `queries: [...]`, usar `source` quando aplicável, evitar saída bruta
- **Payload grande** — persistir em arquivo e processar por `ctx_execute_file` ou `ctx_index(path)`

## Se Travar

Se algo não funciona:
- Releia o código relevante via `ctx_search`
- Considere se o codebase evoluiu desde a escrita do plano
- Apresente o mismatch claramente e aguarde aprovação

## Retomando Trabalho

Se o plano tem checkmarks:
- Confie que o trabalho concluído está feito
- Continue do primeiro item não-marcado
- Verifique trabalho anterior apenas se algo parece errado

## Combina Com

- `/plan` → cria o plano que este executa
- `/ctx-checkpoint` → obrigatório ao concluir fase e ao concluir plano
- `/validate` → após concluir, valida a implementação
- `/commit` → gera mensagem (usuário commita)

## 📄 Verificação de Gate R-064 em `docs/plans/<tipo>/` (`docs/plans/implementation/`)

- Antes de iniciar qualquer mutação de código, valide que o plano técnico em `docs/plans/implementation/` (Gate 2) e o respectivo plano de Gate 1 em `docs/plans/<tipo>/` (`feature/`, `refactor/`, `architecture/`, `test-strategy/`, `bug-triage/`, `requirements/`, `governance/`) possuem frontmatter R-064 com `status: APPROVED`, `approved: true`, `plan_type` válido e `allowed_files` cobrindo todos os arquivos-alvo.
- Caso o plano em `docs/plans/implementation/` (ou `docs/plans/<tipo>/`) esteja ausente, em `DRAFT` ou com `approved: false`, interrompa a execução imediatamente e solicite o cumprimento do Gate R-064.

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/implement` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/implement`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch_execute`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).

</execution_protocol>
