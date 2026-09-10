---
name: handoff-governance
description: >
  Regras de delegação e handoff entre agents — payload mínimo, critérios de
  escalonamento, fluxos de delegação e rastreabilidade de contexto entre agents.
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
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/catalog.yaml
tools: []
---

# Handoff Governance

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

---

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

---

### 2.1) Schema Formal — Campos Obrigatórios e Identidade do Emissor

Todo handoff deve usar este schema tipado (versão 1.3), validável via `yaml-governance`:

```yaml
handoff_payload:
  versao: "1.3"                           # string — versão do schema de handoff (v1.3: projeto_alvo e chaining)
  para: "<nome-exato-do-agent>"           # string — enum do catálogo de agents
  motivo: "<1 linha clara>"               # string — razão objetiva da delegação
  emissor:                                # identidade do agent delegante (P10)
    nome: "<nome-do-agent-atual>"
    versao: "<versao-semantica>"          # ex.: "1.1.0"
    modelo_llm: "<modelo-usado>"          # ex.: "Gemini 3.8 Flash"
    timestamp: "<ISO-8601>"              # ex.: "2026-08-28T14:23:00Z"
  roteamento_grafo:                       # extensão aditiva (v1.1) — topologia e transição de estado, opcional
    current_node: "<nome-do-agent-atual>" # string — alias explícito do nó emissor
    next_node: "<nome-exato-do-agent>"    # string — alias explícito do nó receptor (idêntico a 'para')
    shared_memory_keys:                   # opcional: chaves semânticas para indexação/recuperação via context-mode
      - "<source-ou-tag-no-context-mode>"
  origem_contexto:                        # metadados de sub-rotina e retorno lateral (R-042 Call Stack)
    parent_agent: "<nome-do-agent-pai>"   # opcional: agent que originou a chamada em sub-rotina
    task_id: "<id-da-tarefa>"             # opcional: identificador único da sub-tarefa
    call_type: "subroutine"               # opcional: enum [subroutine | permanent_transfer]
    return_to_parent: true                # opcional: boolean — se true, agent receptor DEVE retornar ao parent_agent
  workflow_tracking:                      # extensão aditiva (v1.2/v1.3) — rastreamento de pipeline determinístico (R-050)
    workflow_id: "<id-do-workflow>"       # opcional: enum [WORKFLOW-BUG-FIX | WORKFLOW-REFACTORING | WORKFLOW-TECHNICAL-ANALYSIS | WORKFLOW-FEATURE-DEVELOPMENT | WORKFLOW-GOVERNANCE-MAINTENANCE]
    etapa_atual: 1                        # opcional: integer — 1-based da etapa corrente
    total_etapas: 5                       # opcional: integer — total de estados do workflow
    nome_etapa: "<nome-da-etapa>"         # opcional: string — identificador da etapa em workflows.md
    proximos_agentes_permitidos:          # opcional: lista de agents autorizados na transição seguinte
      - "<nome-do-proximo-agent>"
    politica_desvio: "strict"             # opcional: enum [strict | adaptive] — strict veda pular estados sem deriva R-042
    projeto_alvo:                         # extensão v1.3 — isolamento e contexto de workspace multi-projeto (R-050.3)
      id: "<id-do-projeto>"               # ex.: "[PROJETO-ALVO]" ou "governance-core"
      root_path: "<caminho-absoluto>"     # ex.: "<workspace>/<project>"
      adapter_ref: "<caminho-adapter>"    # ex.: ".github/instructions/local/[PROJETO-ALVO].instructions.md"
    chaining:                             # extensão v1.3 — encadeamento de workflows e herança de diagnóstico (R-050.1)
      origem_workflow_id: "<id-origem>"   # ex.: "WORKFLOW-TECHNICAL-ANALYSIS" se veio de análise prévia
      proposta_referenciada: "<id-prop>"  # ex.: "PROPOSTA-1" ou "PROPOSTA-2"
      carry_over_state:                   # metadados e arquivos herdados do workflow anterior
        arquivos_afetados:
          - "<caminho-do-arquivo>"
        diagnostico_previo: "<resumo do diagnóstico anterior para não re-analisar>"
  contexto:
    solicitacao_original: "<texto>"
    trabalho_realizado: "<resumo>"
    descobertas_chave:
      - "<item>"
    artefatos:
      - "<path>"
    restricoes:
      - "<restrição>"
  proximos_passos_sugeridos:
    - "<passo>"
  nao_retornar_para: true
```

> **Retrocompatibilidade**: consumidores v1.0 continuam lendo `para`/`emissor`/`contexto` sem quebra. `roteamento_grafo` é OPCIONAL e destinado a handoffs que exigem persistência de rastro além da janela de contexto atual (via `ctx_index`, camada auxiliar — nunca substitui o banner de visibilidade em chat).

> **Correlação OTel**: os campos `emissor.nome`, `emissor.modelo_llm` e `timestamp` mapeiam diretamente para atributos `gen_ai.agent.name`, `gen_ai.request.model` e `timestamp` do span `invoke_agent` — use `agent-observability-otel` para rastrear handoffs em pipelines instrumentados.
>
> **Protocolo de Retorno Lateral / Call Stack (`call_type: "subroutine"`)**: quando um agent invoca outro como sub-rotina com `call_type: "subroutine"` e `return_to_parent: true`, o agent receptor (ex.: `@deep-search`) opera em escopo delimitado e DEVE, ao concluir sua análise ou síntese, invocar `run_subagent(agentName: parent_agent, ...)` devolvendo os dados diretamente ao agent solicitante, em vez de finalizar no chat ou devolver ao `@agent-router` por falsa deriva de intenção.

---

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

---

### 2.3) Indexação Semântica de Telemetria (FTS5 / BM25)

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
```

> **Consulta e Pruning**: consulte via `ctx_search(queries: ["[INTENT_DRIFT]"], source: "handoff-telemetry:<projeto>")`. O ciclo de vida desta telemetria segue a política de retenção episódica (TTL 7 dias, conforme `agent-memory-policy`).

---

### 2.4) Intake Guardrail & Circuit Breaker em Runtime

Para mitigar riscos de *Excessive Agency* (OWASP Agentic AI) e loops de execução não intencionais entre agentes (A → B → A), todo fluxo de handoff deve operar sob dois mecanismos de contenção em runtime:

#### 1. Intake Guardrail (Passo 0 no Agent Receptor)
Todo agent acionado como subagente via `run_subagent` DEVE executar uma verificação declarativa de entrada antes de qualquer processamento de domínio:
- **Campos Obrigatórios**: validar presença de `emissor.nome`, `motivo` e `contexto.solicitacao_original` no payload.
- **Tratamento de Payload Inválido**: se o payload omitir os campos obrigatórios, o agent receptor NÃO tenta deduzir a intenção; rejeita imediatamente e devolve erro estruturado ao `@agent-router`:
  ```yaml
  handoff_rejeitado:
    motivo: "payload_invalido_campos_ausentes"
    campos_faltantes: ["emissor", "contexto"]
  ```

#### 2. Circuit Breaker Stateful (Prevenção de Loops e Profundidade de Pilha)
- **Call Stack Depth**: subagentes encadeados em sub-rotinas (`call_type: "subroutine"`) devem monitorar a profundidade acumulada em `origem_contexto.call_stack_depth`.
- **Teto Rígido**: `MAX_DEPTH = 3`. Se `call_stack_depth >= 3`, o Circuit Breaker é desarmado: o agent interrompe qualquer delegação subsequente e força o retorno imediato ao `parent_agent` ou `@agent-router` com `motivo: "circuit_breaker_max_depth_exceeded"`.
- **Detecção de Ciclos Imediatos (Anti-Ping-Pong)**: se o nó de destino proposto for idêntico ao `parent_agent` imediato sem que nenhum artefato ou descoberta nova tenha sido gerada, o handoff é bloqueado com `motivo: "circuit_breaker_cycle_detected"`.

---

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

---

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

---

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

**Visibilidade obrigatória (banner de identidade)**: para que a re-triagem seja auditável a cada turno (não só quando o `@agent-router` responde), TODO agent abre sua resposta com `Agente Ativo: <name>`; se a resposta é resultado de handoff/re-triagem recebido, uma segunda linha declara `Handoff: <origem> → <destino> (motivo: ...)`. Padrão de mercado: OpenAI Agents SDK (`HandoffOutputItem` — "Handed off from X to Y") e LangGraph (`active_agent` streamado ao usuário). Detalhes e checklist em `agent-contracts/SKILL.md` § 0.

---

### 5.1) Modo Fan-out/Fan-in (Orchestrator-Workers)

Use quando a solicitação for explicitamente marcada `[P]` pelo R-018 — múltiplos agents sem dependência entre si podem trabalhar em paralelo.

**Quando usar fan-out vs. delegação única:**

| Situação | Padrão | Custo LLM |
|---|---|---|
| 1 domínio, 1 agent especializado | Delegação única (padrão) | 1 call/domínio |
| N domínios simultâneos sem dependência | Fan-out (Orchestrator-Workers) | 2 calls/domínio |
| N domínios com dependência sequencial | Pipeline sequencial | 1 call/domínio/passo |

**Estrutura obrigatória para fan-out:**

```yaml
fan_out:
  trigger: "R-018 [P] marcado explicitamente"
  workers:
    - agent: "<agent-1>"
      escopo: "<escopo delimitado e sem sobreposição>"
    - agent: "<agent-2>"
      escopo: "<escopo delimitado e sem sobreposição>"
  fan_in:
    criterio_conclusao: "todos os workers reportaram resultado"
    formato_agregacao: "tabela comparativa | lista unificada | decisão por votação"
  guardrail_saida: true   # obrigatório — validar output de cada worker antes de agregar
```

**Anti-padrão**: fan-out sem ponto explícito de fan-in resulta em resultados fragmentados sem síntese. Prefira sempre delegação única quando o ganho de paralelismo não for evidente.

---

## 6) Anti-padrões

- ❌ Handoff sem payload de contexto (downstream começa do zero)
- ❌ Delegar para evitar trabalho ("lazy handoff")
- ❌ Loop de delegação (A → B → A) — detectar e interromper
- ❌ Handoff sem motivo explícito (não rastreável)
- ❌ Múltiplos handoffs em sequência quando um agent pode fazer o trabalho todo
- ❌ Não registrar que houve handoff no output (invisível para o usuário)
