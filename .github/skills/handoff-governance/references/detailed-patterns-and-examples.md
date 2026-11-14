# Handoff Governance — Schemas Detalhados, Guardrails e Fan-Out/Fan-In

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

### 2.5 & 2.6) Intake Guardrail, Circuit Breaker e Offloading de Artefatos

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

#### 3. Circuit Breaker de Falhas & Retry Budget (Anti-Loop de Correção)
- **Retry Budget por Etapa**: `MAX_RETRIES_PER_STEP = 2`.
- **Transição de Estados (`CLOSED` → `OPEN`)**:
  - `CLOSED` (Normal): O fluxo prossegue normalmente entre os agentes da máquina de estados do workflow.
  - `OPEN` (Disparado): Se um agente executor (ex.: `<stack>-developer`, `<stack>-test-engineer`) falhar por 2 vezes consecutivas na mesma etapa de execução (ex.: testes continuam falhando após 2 tentativas cirúrgicas de fix), o Circuit Breaker é compulsoriamente desarmado (`state: OPEN`).
  - **Ação Imediata**: O agente suspende imediatamente qualquer nova tentativa autônoma de alteração de código e escala o caso para decisão humana via `ask_questions` (R-047/R-027), acompanhado do diagnóstico da falha, evitando queima descontrolada de créditos e poluição do histórico de commits.

#### 4. Protocolo de Rollback Atômico de Workspace em Disparo de Circuit Breaker
Quando o Circuit Breaker desarmar ou a cadeia abortar por erro irrecuperável durante uma etapa mutativa:
- **Com Git Worktree Ativo (Isolamento R-049 / `git-worktree-governance`)**:
  - O agente/orquestrador executa o descarte seguro do worktree temporário:
    ```bash
    git --no-pager worktree remove --force .worktrees/<task-id>
    git --no-pager branch -D worktree/<task-id>
    ```
- **No Workspace Principal**:
  - Se a falha ocorreu no workspace principal, o agente DEVE reportar o diff exato e orientar ou executar o rollback cirúrgico dos arquivos parciais afetados:
    ```bash
    git --no-pager checkout -- <arquivos-alterados-na-etapa>
    ```
  - Nenhuma alteração incompleta, parcial ou quebrada deve permanecer no workspace sem aprovação expressa do usuário.

---

### 2.6) Governança de Context Engineering & Offloading de Artefatos em Handoffs (2026)

O aumento da complexidade de workflows multi-agente exige a transição formal de "Prompt Engineering" para **Context Engineering** (*Write, Select, Compress, Isolate*), garantindo eficiência de custos, preservação de KV-cache e prevenção de *Context Poisoning*.

#### 1. Os 4 Pilares de Context Engineering em Handoffs
- **Write**: Definição rigorosa e declarativa do contrato e dos boundaries de cada tarefa no payload de handoff, sem ambiguidades contextuais.
- **Select**: O agente receptor busca e carrega informações sob demanda (*just-in-time*) via `ctx_search` (FTS5/BM25) ou leitura cirúrgica, em vez de o emissor despejar todo o conhecimento histórico no payload.
- **Compress**: Resumo executivo estruturado (máx. 5 linhas) no campo `contexto`, eliminando transcrições de turnos de chat e saídas intermediárias de ferramentas.
- **Isolate**: Subagentes executores operam com isolamento de contexto (recebem apenas o payload estrito da sua etapa, sem carregar o ruído de conversas anteriores).

#### 2. Regra de Ouro: Limiar de Offloading de Artefatos (2 KB / 50 Linhas)
- **Proibição de Bloat**: Todo artefato técnico que ultrapassar **2 KB** (ou aproximadamente **50 linhas** de código, JSON, YAML, AST de grafo, especificações OpenAPI ou logs de erro) **NÃO PODE ser embutido como texto bruto** no campo `evidencias` ou `contexto` do payload de handoff.
- **Padrão Pointer / Artifact Reference**:
  - O agente emissor deve persistir o artefato no workspace ou indexar no `context-mode` (`ctx_index`), preenchendo o payload de handoff exclusivamente com o ponteiro tipado:
    ```yaml
    evidencias:
      - tipo: "pointer"
        artifact_ref: "docs/architecture/technical-blueprint.md" # ou "ctx:codegraph-engine:ast-dump"
        hash: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        mime_type: "text/markdown"
        tamanho_bytes: 8420
        resumo_executivo: "Technical Blueprint com 5 endpoints REST, contratos OpenAPI v3 e modelo de entidades para o domínio de pagamentos."
    ```
- **Consumo pelo Receptor**: O agente receptor inspeciona o `resumo_executivo` e, se e somente se necessitar dos detalhes brutos do artefato, realiza a consulta cirúrgica do `artifact_ref` via `read_file` pontual ou `ctx_search(source: ...)` com escopo delimitado.

> **Alinhamento com Harness Engineering (2026)**: O padrão *Write, Select, Compress, Isolate* implementado acima materializa na prática a recomendação de mercado de handoffs sucintos e portáteis. Conforme detalhado em `harness-engineering-patterns` (§ 2.2 — Zona Inteligente de Tokens e Sessões Descartáveis), ao aproximar-se do limiar prático de degradação (~100k tokens na janela ativa), o agente deve consolidar o estado essencial em um handoff portátil e disparar um reset de sessão, mantendo a inferência sempre na zona de alta fidelidade cognitiva.

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
