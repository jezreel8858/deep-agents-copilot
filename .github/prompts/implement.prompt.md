---
name: implement
description: Executa plano aprovado fase a fase, marcando `- [x]` ao concluir e registrando checkpoints obrigatórios.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'insert_edit_into_file', 'create_file', 'grep_search', 'file_search', 'get_errors', 'run_in_terminal', 'run_subagent', 'context-mode/ctx_search', 'context-mode/ctx_batch_execute', 'context-mode/ctx_execute', 'context-mode/ctx_execute_file']
argument-hint: '[caminho-do-plano | descrição-da-fase]'
source_docs:
  - .github/skills/efficient-batch-code-modification/SKILL.md
  - .github/skills/terminal-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/implement`

> **Propósito**: Executar plano técnico aprovado fase a fase sob R-031 (zero-interrupção), marcando `- [x]` ao concluir.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** executar as tarefas estritamente especificadas no plano aprovado.
- ✅ **SEMPRE** aplicar Single-Turn Batching e limiar de 5 arquivos da skill `efficient-batch-code-modification` (R-046).
- ✅ **SEMPRE** validar `get_errors` ao final de cada fase executada.
- ❌ **NÃO** parar para pedir confirmações intermediárias (R-031) exceto por bloqueio absoluto (credencial exposta ou estado irrecuperável).
- ❌ **NÃO** fazer commits autônomos ou alterar arquivos fora do plano aprovado.

---

Você foi encarregado de implementar um plano técnico aprovado. Planos contêm fases com mudanças específicas e critérios de sucesso.

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
