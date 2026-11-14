---
name: handoff-governance
description: "Define diretrizes e padrões para regras de delegação e handoff entre agents — payload mínimo, critérios de escalonamento, fluxos de delegação e rastreabilidade de contexto entre agents. Use quando atuar em handoff, delegação entre agents, delegar agent. Não use para tarefas fora do escopo de handoff-governance ou implementação direta de código de negócio não relacionado."
tier: 1
category: governance
triggers:
  - "handoff"
  - "delegação entre agents"
  - "delegar agent"
  - "escalar análise"
  - "roteamento downstream"
  - "transferir tarefa"
  - "agent delegation"
source_docs:
  - .github/agents/catalog.yaml
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Handoff Governance

## Quando Usar

- Ativação em cenários de handoff, delegação entre agents, delegar agent.

## Quando NÃO Usar

- Não usar para demandas fora do domínio de `handoff-governance` ou quando outra skill específica cobrir integralmente o escopo.

## 1) Quando Fazer Handoff

```
Agent DEVE delegar quando:
  ✅ Tarefa está fora do seu não-escopo declarado
  ✅ Requer especialização que outro agent tem
  ✅ Resultado do agent atual é pré-requisito para o próximo
  ✅ Complexidade excede capacidade de análise do agent atual

Agent NÃO DEVE delegar quando:
  ❌ A delegação é para evitar trabalho (lazy handoff)
  ❌ Agent downstream não tem o contexto necessário
  ❌ Seria mais eficiente o agent atual completar com esforço incremental
  ❌ Criaria loop (A → B → A)
```


## 2) Payload Mínimo de Handoff

```yaml
# Todo handoff deve incluir:

handoff_payload:
  para: "@nome-do-agent"             # agent receptor
  motivo: "<1 linha clara>"          # por que está delegando
  contexto:
    solicitacao_original: "<texto>"   # o que o usuário pediu
    trabalho_realizado: "<resumo>"    # o que foi feito até aqui
    descobertas_chave:               # achados relevantes
      - "<item 1>"
      - "<item 2>"
    artefatos:                        # arquivos/paths relevantes
      - "<path>"
    restricoes:                       # limitações identificadas
      - "<restrição>"
  proximos_passos_sugeridos:
    - "<passo 1>"
  nao_retornar_para: true            # evitar loop
```

**Exemplo real:**

```yaml
handoff_payload:
  para: "@test-engineer"
  motivo: "Estratégia mapeada — pronto para implementar suítes"
  contexto:
    solicitacao_original: "Testes para OrderService"
    trabalho_realizado: "Mapeamento de risco por método completado"
    descobertas_chave:
      - "OrderService tem 12 métodos públicos"
      - "processarPagamento() é risco crítico (dados financeiros)"
      - "Stack: Spring Boot + JUnit 5 + Mockito"
    artefatos:
      - "src/main/java/com/projeto/service/OrderService.java"
    restricoes:
      - "Não existe test slice configurado para repositório legado"
  proximos_passos_sugeridos:
    - "Implementar testes unitários com JUnit 5 + Mockito"
    - "Priorizar cobertura de processarPagamento() (90%+)"
```


### 2.1) Schema Formal — Campos Obrigatórios e Identidade do Emissor

- Todo handoff DEVE validar schema com `emissor`, `receptor`, `motivo`, `contexto_transferido` e `contrato_esperado`, preservando rastreabilidade imutável.
- Schema JSON/YAML completo em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

### 2.2) Gap de Guardrails em Handoffs

**⚠️ Risco operacional confirmado** (OpenAI Agents SDK, 2025): tool guardrails **não se aplicam a handoffs** — apenas ao primeiro agent da cadeia (input guardrails) e ao agent que produz o output final (output guardrails). Agents intermediários numa cadeia de handoffs ficam sem validação de saída por padrão.

**Estratégias compensatórias obrigatórias:**

| Cenário | Estratégia |
|---|---|
| Handoff com dados sensíveis | Validar campos PII/credenciais no payload **antes** de delegar |
| Handoff cross-domínio (ex.: research → implementation) | Agent receptor confirma recebimento: `Contexto recebido: [resumo]` |
| Cadeia com 3+ agents | Inserir ponto de validação explícita no agent intermediário central |
| Payload com schema crítico | Usar `yaml-governance` para validar `handoff_payload` antes de prosseguir |

**Regra mínima**: todo agent que recebe um handoff deve confirmar explicitamente no início da resposta quais entradas foram recebidas e consideradas válidas.


### 2.3) Delegação Plana (Flat Delegation) vs. Aninhamento de Subagentes (Anti-Duplicação)

Em plataformas com suporte a subagentes via tool-calling (`run_subagent`), como GitHub Copilot no VS Code/JetBrains, existe um risco crítico de **dupla orquestração**:

```
❌ ANINHAMENTO INDEVIDO (Nested Subagent Sprawl — Smell 2.20):
Orquestrador Raiz (Copilot)
   └─► run_subagent(agent-router)
          └─► run_subagent(downstream_agent)  ◄── Downstream executa dentro do router
   Retorno ao Orquestrador Raiz: "Delegado: @downstream_agent"
   Orquestrador Raiz: "O router mandou delegar!"
   └─► run_subagent(downstream_agent)         ◄── Downstream executa PELA SEGUNDA VEZ! (Duplicação e desperdício)

✅ DELEGAÇÃO PLANA (Flat Delegation — Padrão Canônico):
Orquestrador Raiz (Copilot)
   └─► run_subagent(agent-router)
   Retorno: Bloco de Decisão de Roteamento (Agente Ativo, Delegado: @<agent>, Pipeline de Execução)
Orquestrador Raiz despacha o downstream UMA ÚNICA VEZ:
   └─► run_subagent(downstream_agent)
```

**Regras Mandatórias de Delegação Plana:**
1. **Papel Estrito do Router**: `@agent-router` (e supervisores hierárquicos) é um classificador de rota, NÃO um executor. Ele encerra seu turno emitindo o bloco de decisão canônico para o orquestrador raiz, sem invocar subagentes executores downstream via `run_subagent`.
2. **Exceções Permitidas para o Router**: A invocação de `run_subagent` por dentro do `agent-router` é restrita exclusivamente a:
   - `@prompt-structuring` (R-041) para refinamento pré-roteamento de pedidos ambíguos.
   - `@binding-initializer` (R-034) para inicialização obrigatória de contexto ausente.
3. **Salvaguarda no Orquestrador**: Quando o orquestrador raiz recebe o retorno do `agent-router`, ele dispara o agente delegado exatamente uma vez. Se por qualquer anomalia a resposta já contiver o resultado final concluído pelo downstream (`Resultado do @<agent>:`), o orquestrador repassa diretamente ao usuário, sem re-invocar o mesmo agent.


### 2.4) Indexação Semântica de Telemetria (FTS5 / BM25)

Para habilitar rastreabilidade sem poluição de contexto no chat, transições de handoff podem ser indexadas via `context-mode` MCP (`ctx_index`) para auditoria e recuperação semântica:

| Tag | Finalidade | Gatilho / Momento |
|---|---|---|
| `[HANDOFF]` | Registro padrão de transição de responsabilidade | Disparo de `run_subagent` com payload v1.1 |
| `[INTENT_DRIFT]` | Detecção de deriva de intenção do usuário (R-042) | Retorno ao `@agent-router` com `motivo: "deriva_de_intencao"` |
| `[LOOP_LIMIT]` | Esgotamento do teto de iterações de auto-refinamento | Limite atingido em `@prompt-structuring` (R-041, máx. 5 loops) |
| `[SUCCESS]` | Conclusão bem-sucedida de sub-rotina ou entrega | Retorno conclusivo ao agent solicitante (`parent_agent`) ou usuário |

**Formato Canônico de Indexação:**

```yaml
telemetry_entry:
  source: "handoff-telemetry:<projeto>"
  tag: "[HANDOFF] | [INTENT_DRIFT] | [LOOP_LIMIT] | [SUCCESS]"
  timestamp: "<ISO-8601>"
  de: "<agent-emissor>"
  para: "<agent-receptor>"
  motivo: "<motivo-objetivo>"
  task_id: "<id-da-tarefa-ou-sessao>"
  # Extensões aditivas e retrocompatíveis (v1.3+ / telemetria de sessão):
  session_id: "<id-da-sessao>"           # string — correlaciona eventos de um mesmo chat do início ao fim (reaproveita sessionStart do context-mode)
  sequence_index: 0                     # integer — ordenação determinística dos eventos dentro da sessão (0, 1, 2...)
  call_stack_depth: 1                   # integer — profundidade do handoff/subagent na árvore de chamadas (detecta aninhamento excessivo)
  outcome_summary: "sucesso"            # string curta — resultado do nó de handoff (ex.: "sucesso", "desvio_detectado", "loop_excedido")
```

> **Especificação dos Campos Aditivos de Telemetria (Fase 2 / Sessão & Rastreabilidade)**:
> - `session_id` (string): correlaciona todos os eventos de um mesmo chat/sessão do início ao fim. DEVE reaproveitar o identificador de sessão já emitido pelo hook `.github/hooks/context-mode.json` no evento `sessionStart` (variantes `sessionStart` e `SessionStart`, disparado via comando `context-mode hook jetbrains-copilot sessionstart` / `claude-code`). É terminantemente proibido criar qualquer mecanismo de ID de sessão paralelo.
> - `sequence_index` (inteiro): ordenação sequencial determinística dos eventos emitidos dentro da sessão corrente, permitindo a reconstrução exata da timeline.
> - `call_stack_depth` (inteiro): profundidade do handoff ou subagent na árvore hierárquica de chamadas, essencial para contenção de aninhamento excessivo e disparo de Circuit Breaker.
> - `outcome_summary` (string curta): síntese do resultado da transição (ex.: `"sucesso"`, `"desvio_detectado"`, `"loop_excedido"`, `"rejeicao_guardrail"`).
> - **Garantia de Retrocompatibilidade**: todos os 4 novos campos são estritamente aditivos e opcionais. A ausência de qualquer um deles em registros indexados anteriormente não quebra consultas via `ctx_search`, relatórios de auditoria nem parsers de mineração de evals.
>
> **Consulta e Pruning**: consulte via `ctx_search(queries: ["[INTENT_DRIFT]"], source: "handoff-telemetry:<projeto>")`. O ciclo de vida desta telemetria segue a política de retenção episódica com segmentação por tag (conforme `agent-memory-policy`).


### 2.5) Intake Guardrail & Circuit Breaker em Runtime

- **Intake Guardrail**: rejeitar payloads sem escopo claro ou com `call_stack_depth > 3`.
- **Context Offloading (2.6)**: transferir ponteiros de arquivos (`docs/plans/`, `ctx_index`) em vez de blocos brutos extensos.
- Detalhes completos em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

### 2.5) Governança de Retry e Reutilização de Plano (R-053 / R-064)
- **Retry no mesmo escopo**: Tentativas subsequentes dentro do escopo de plano já aprovado reutilizam o mesmo `plan_ref` sem necessitar de novo plano ou novo checkpoint humano.
- **Mudança de escopo ou falha persistente (>2 retries)**: Se a correção ou implementação demandar arquivos fora de `allowed_files` ou persistirem mais de 2 falhas consecutivas de teste/build, interromper compulsoriamente a execução e retornar ao `<stack>-arch-advisor` para reabertura do Gate 2.

## 3) Fluxos de Delegação Comuns

```
@agent-router (triagem)
       │
       ├──→ @bug-triage (bug reportado)
       │         └──→ @tech-solution-architect (bug tem impacto sistêmico)
       │
       ├──→ @test-strategy (planejar testes)
       │         └──→ @test-engineer (executar suítes)
       │
       ├──→ @refactor-planner (planejar refatoração)
       │         └──→ @tech-solution-architect (análise de impacto necessária antes)
       │
       ├──→ @deep-search (pesquisa técnica interna/externa)
       │         └──→ @tech-solution-architect (análise cross-projeto)
       │
       └──→ @docs-engineer (documentar resultado)
```


### 2.3) Schema `workflow_tracking` (v1.3) e Multi-Project Target Tracking

```yaml
workflow_tracking:
  versao: "1.3"
  workflow_id: "WORKFLOW-FEATURE-DELIVERY"
  etapa_atual: 2
  proximos_agentes_permitidos: ["@plan-critic", "@agent-router"]
  projeto_alvo:
    id: "[PROJETO-ALVO]"
    root_path: "<caminho-relativo-ou-worktree>"
  chaining:
    modo: "fast-chaining"
```

### 2.4) Circuit Breaker de Falhas & Retry Budget e Protocolo de Rollback Atômico de Workspace

- **Circuit Breaker de Falhas & Retry Budget**: limite rígido de `MAX_RETRIES_PER_STEP = 2` por etapa; excedido o orçamento, aciona-se o **Protocolo de Rollback Atômico de Workspace** e escalonamento ao `@agent-router`.

### 2.5) Governança de Context Engineering & Offloading de Artefatos em Handoffs

- Payloads que excedam **2 KB / 50 Linhas** DEVEM ser persistidos e referenciados via ponteiro (`tipo: "pointer"`), evitando poluição de janela de contexto.

## 4) Rastreabilidade de Contexto

```
Regra: contexto não se perde entre agents.

Agent emissor registra:
  - O que foi feito
  - Qual agent receptor
  - Motivo da delegação
  - Artefatos passados

Agent receptor confirma:
  - Recebeu o contexto
  - Entendeu os próximos passos
  - Tem os pré-requisitos necessários
```


## 5) Critérios de Escalonamento

| Situação | Escalonamento |
|---|---|
| Bug com impacto sistêmico desconhecido | `@bug-triage` → `@tech-solution-architect` |
| Refatoração sem análise de dependências | `@refactor-planner` → `@tech-solution-architect` |
| Implementação sem estratégia definida | `@test-engineer` → `@test-strategy` primeiro |
| Dúvida técnica que precisa de pesquisa | Qualquer agent → `@deep-search` |
| Documentação a atualizar após mudança | Qualquer agent → `@docs-engineer` |
| **Mudança de fase na mesma conversa** (requisito→implementação, análise→código, revisão→correção) | Downstream atual **DEVE** retornar a `@agent-router` (R-042, re-triagem obrigatória) — **nunca prosseguir sozinho** |
| Especialista híbrido (`@angular-engineer`/`@spring-boot-engineer`/`@spring-reactive-engineer`) recebe pedido de código **fora** do próprio domínio de stack | Specialist → `@agent-router` com handoff (dentro do próprio domínio, o specialist implementa diretamente — não é deriva) |

### 5.2) Anti Sticky-Session (R-042)

Todo agent downstream em `task_mode` reavalia a cada novo turno se a solicitação ainda cabe no seu **Não-Escopo** declarado. Ao detectar deriva (mudança de verbo de ação, stack fora de competência, ou pedido de execução em agent read-only), o agent **interrompe e devolve controle** ao `@agent-router` com `motivo: "deriva_de_intencao"` no payload — nunca conclui a tarefa fora do próprio escopo só porque já estava "no meio da conversa".

**Visibilidade obrigatória (banner de identidade)**: para que a re-triagem seja auditável a cada turno (não só quando o `@agent-router` responde), TODO agent abre sua resposta com `Agente Ativo: <name>`; se a resposta é resultado de handoff/re-triagem recebido, uma segunda linha declara `Handoff: <origem> → <destino> (motivo: ...)`; e uma terceira linha declara `Skills Carregadas: <skill-1>, <skill-2>, ...` com a base de conhecimento efetivamente consultada nesta resposta (ver `agent-contracts/SKILL.md` § 0). Padrão de mercado: OpenAI Agents SDK (`HandoffOutputItem` — "Handed off from X to Y") e LangGraph (`active_agent` streamado ao usuário). Detalhes e checklist em `agent-contracts/SKILL.md` § 0.


### 5.1) Modo Fan-out/Fan-in (Orchestrator-Workers)

- Quando subtasks são independentes (`paralelizavel: true`), o orquestrador despacha workers em paralelo (Fan-Out) e consolida evidências (Fan-In).
- Diagrama e protocolo completo em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

## 6) Anti-padrões

- ❌ **Terceirização Indevida de Execução ao Usuário por Agente Analítico/Read-Only (Smell 2.25 / R-057)**: O agente analítico/read-only constata que não possui ferramentas para editar os arquivos e transfere instruções manuais de edição para o usuário, em vez de realizar o handoff para o executor responsável ou avançar para a próxima etapa do workflow determinístico (R-050).

- ❌ Handoff sem payload de contexto (downstream começa do zero)
- ❌ Delegar para evitar trabalho ("lazy handoff")
- ❌ Loop de delegação (A → B → A) — detectar e interromper
- ❌ Handoff sem motivo explícito (não rastreável)
- ❌ Múltiplos handoffs em sequência quando um agent pode fazer o trabalho todo
- ❌ Não registrar que houve handoff no output (invisível para o usuário)

## Checklist de Conformidade

- [ ] Diretrizes, contratos e restrições de escopo de `handoff-governance` verificados e atendidos.

## Referências

- Detalhamento estendido em `references/` e documentação normativa em `CLAUDE.md`.
