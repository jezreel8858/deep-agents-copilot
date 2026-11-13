---
name: plan
description: Cria plano de implementação detalhado com análise de dependências, paralelismo e checklist de autonomia.
agent: 'agent'
router_bypass: slash_workflow
model: "Claude Sonnet 5.5"
tools: ['read_file', 'grep_search', 'file_search', 'list_dir', 'ask_questions', 'run_subagent', 'context-mode/ctx_search', 'context-mode/ctx_batch_execute', 'context-mode/ctx_execute', 'context-mode/ctx_execute_file']
argument-hint: '[descrição-da-feature | caminho-do-arquivo]'
source_docs:
  - 'docs/plans/README.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/plan`

> **Propósito**: Criar planos de implementação detalhados com análise de dependências, DAG de etapas, paralelismo e checklist de autonomia.
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/plan` (argumento: `[descrição-da-feature | caminho-do-arquivo]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** elaborar plano detalhado com fases atômicas, rastreabilidade e estimativas.
- ✅ **SEMPRE** mapear dependências e responsabilidades no formato `{paralelizavel: bool, responsavel: "<agent>"}` e contingências inline `[fallback: X]`.
- ✅ **SEMPRE** incorporar análise de segurança Shift-Left e Checklist Defensivo Pré-Code-Review nos planos gerados.
- ❌ **NÃO** implementar código ou criar arquivos da aplicação (foco exclusivo em planejamento).
- ❌ **NÃO** tomar decisões arquiteturais irreversíveis sem explicitar trade-offs e alternativas.

---

Você é responsável por criar planos de implementação detalhados com processo interativo. Seja cético, exaustivo e colaborativo para produzir specs técnicas de alta qualidade.

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/plan`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## Resposta Inicial

Se nenhum parâmetro foi fornecido:

```
Vou ajudar a criar um plano de implementação detalhado. Para começar:

1. Descrição da task/ticket (ou referência a arquivo)
2. Contexto, restrições ou requisitos específicos

Dica: `/plan <descrição ou caminho do arquivo>` para começar direto.
```

## Processo

### Passo 1: Contexto Inicial

1. **Faça retomada de sessão** com `ctx_search(..., sort: "timeline")` antes de qualquer nova coleta.
2. **Levante contexto do codebase** via `ctx_batch_execute(commands, queries)` como coleta primária.
3. **Use `ctx_search(queries:[...])`** para follow-up sobre o que já foi indexado.
4. **Leia arquivo integralmente apenas em exceção** (quando faltar literal essencial para o plano).
5. **Analise e verifique entendimento**:
   - Cross-reference requisitos com código real
   - Note discrepâncias e suposições
   - Determine escopo real
6. **Apresente entendimento + perguntas focadas**:

```
Baseado no pedido e research, entendo que precisamos [resumo preciso].

Encontrei que:
- [detalhe com `arquivo:linha` quando aplicável]
- [padrão/constraint relevante]
- [complexidade/edge case]

Perguntas que research não respondeu:
- [pergunta técnica que requer julgamento humano]
```

**Apenas pergunte o que não pode ser respondido por investigação do codebase.**

### Passo 2: Análise Antecipada de Bloqueadores

**Antes de qualquer pergunta**, varra os cenários que podem pausar `/implement`:

| Categoria | Verificar | Ação se incerto |
|---|---|---|
| **Paths de arquivo** | Todos os arquivos-alvo existem? | `list_dir` / `file_search` |
| **Decisões de negócio** | Regra tem caminho determinístico? | Escalar ao usuário |
| **Dependências de fase** | Fase B realmente depende de Fase A completa? | Documentar ou paralelizar |
| **Edge cases críticos** | Null / empty / conflict / permission cobertos? | Definir explicitamente |
| **Critérios mensuráveis** | "Sucesso" é verificável? | Transformar em verificação concreta |
| **Conflito com código existente** | Há código que já resolve parcialmente? | Reaproveitar ou documentar substituição |

**Resultado obrigatório desta etapa:**
- Lista dos itens resolvidos pelo research (sem perguntar ao usuário)
- Lista enxuta: **máximo 5 perguntas raiz** para o usuário

### Passo 3: Outline do Plano

Apresente a estrutura com marcação de paralelismo explícita (R-018):

```
Estrutura proposta:

## Visão Geral
[1-2 frases]

## Dependências entre Fases
| Fase | Depende de | Pode rodar em paralelo com |
|---|---|---|
| Fase 1 | — | Fase 2 |
| Fase 2 | — | Fase 1 |
| Fase 3 | Fases 1 e 2 | — |

## Fases:
1. [P] [Nome da fase] — [o que entrega] | sem dependências
2. [P] [Nome da fase] — [o que entrega] | sem dependências
3. [S] [Nome da fase] — [o que entrega] | depende de: Fase 1 + Fase 2

Legenda: [P] = paralela, [S] = sequencial
```

**Regra:** toda fase sem dependência real DEVE ser marcada `[P]`.

### Passo 4: Escrita do Plano

Após aprovação do outline, escreva o plano com:
- Visão Geral
- Estado Atual vs Desejado
- O Que NÃO Faremos (escopo explícito)
- 🛡️ Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)
- Fases com: passos, critério de verificação automatizada, critério manual (formato `{paralelizavel: bool, responsavel: "<agent>"}`)
- 🔒 Checklist Defensivo Pré-Code-Review
- Decisões Tomadas durante o planejamento

### ✅ Checklist de Autonomia — Gate Obrigatório

**Antes de finalizar o plano**, confirme cada item:

- [ ] Todos os paths de arquivo são verificados
- [ ] Zero itens "TBD", "a definir" ou "dependendo de X"
- [ ] Toda fase com critério de sucesso verificável
- [ ] Fases independentes marcadas `[P]`
- [ ] Dependências entre fases documentadas na tabela
- [ ] Edge cases de negócio resolvidos ou explicitamente fora do escopo
- [ ] Decisões tomadas durante planejamento registradas
- [ ] Modelagem de ameaças & requisitos de segurança Shift-Left documentados
- [ ] Checklist Defensivo Pré-Code-Review integrado com validações de segurança
- [ ] Tags de paralelismo e responsabilidade normalizadas no formato `{paralelizavel: bool, responsavel: "<agent>"}`
- [ ] Nenhuma pergunta ao usuário ficará em aberto durante `/implement`

### Aviso ao usuário (inclua no plano gerado):

> Este plano será executado por `/implement`, que **obrigatoriamente**:
> 1. Marca `- [x]` antes de passar para a próxima fase
> 2. Executa `/ctx-checkpoint` após cada fase concluída (`[x]`) e no fechamento do plano
> 3. Declara `lastStep` e `nextStep` após cada `[x]` para captura pelo Context Mode
> 4. PARA se qualquer fase falhar (sem loops de correção)

## Diretrizes Importantes

1. **Seja cético** — questione requisitos vagos; verifique com código
2. **Seja interativo** — valide etapa por etapa, não escreva tudo de uma vez
3. **Seja exaustivo** — use `ctx_search` e `ctx_batch_execute` para levantar contexto real
4. **Token budget** — agrupe perguntas no mesmo `queries`, use `source` e evite múltiplas chamadas unitárias
5. **Sem TBD** — qualquer item "a definir" no plano final é inválido
6. **Decisões explícitas** — toda decisão de design deve ser registrada na seção "Decisões Tomadas"
7. **Autonomia total** — o plano deve ser executável por `/implement` sem nenhuma pergunta ao usuário

## Combina Com

- `/deep-search` → pesquisa é input deste plano
- `/implement` → executa o plano criado aqui
- `/validate` → valida a implementação contra este plano
- `/commit` → gera mensagem (usuário commita)

## 📄 Materialização Universal em `docs/plans/<tipo>/` e Gate R-064

- Todo plano gerado deve ser estruturado conforme a árvore canônica `docs/plans/<tipo>/` (`feature/`, `refactor/`, `architecture/`, `implementation/`, `test-strategy/`, `bug-triage/`, `requirements/`, `governance/`) documentada em `docs/plans/README.md`.
- O plano deve incluir o frontmatter YAML comum R-064 (`.github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md`) com `status`, `approved`, `author`, `plan_type`, `created_at`, `allowed_files` e `related-planning-doc`.
- Agentes planejadores, `*-arch-advisor`, analistas de requisitos e agentes de triagem operam em perfil **100% Read-Only (R-025)**: a persistência física do arquivo `.md` em `docs/plans/<tipo>/` ocorre via handoff para `@docs-engineer` (ou `@governance-maintainer` em governança) antes do Gate de Aprovação Humana R-064 (`ask_questions`).

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/plan` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/plan`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

> **Contrato de UX `ask_questions` (R-027 / CA-03..CA-05)**: 1–4 perguntas/chamada, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais e mutuamente exclusivas (Anti-Strawman), `description` obrigatório (`[Consequência prática / O que faz] + [Trade-off principal ou quando escolher]`) e 1ª opção `(Recomendado)` quando houver melhor prática técnica (exceção: decisão puramente de negócio/produto).

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
