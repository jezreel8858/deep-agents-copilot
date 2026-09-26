# Estratégia de Testes e Matriz de Evals — Qualidade e Observabilidade Multi-Agent

> **Estado**: WF4_TEST_STRATEGY_GATEWAY · **Autor**: test-strategy · **Status**: PROPOSTO  
> **Normas de Referência**: [BLUEPRINT_AGENT_OBSERVABILITY.md](./BLUEPRINT_AGENT_OBSERVABILITY.md) · [agent-evals-lab](../../.github/skills/agent-evals-lab/SKILL.md) · [agent-observability-otel](../../.github/skills/agent-observability-otel/SKILL.md) · OTel GenAI Semconv v1.41+

---

## 1. Visão Geral e Princípios Operacionais

A avaliação contínua (Evals) no ecossistema GitHub Copilot / Deep-Agents atua como um **Quality Gate determinístico e preventivo**. O objetivo é impedir que alterações de prompts, configurações de modelos ou ferramentas introduzam regressões comportamentais, degradação de roteamento ou vazamentos de telemetria e credenciais.

### Pilares Fundamentais
1. **Risk-First e Blast Radius**: Cenários prioritários (P1) cobrem caminhos de execução críticos, integridade de roteamento e segurança de dados/segredos.
2. **Determinismo na Governança**: Validações estruturais e semânticas prévias (offline/lint/contract) antes de benchmarks estocásticos.
3. **Observabilidade Semconv v1.41+**: Verificação contínua de traces OTel gerados pelo proxy stdio MCP e exporters do Langfuse.
4. **Precedência de Ferramentas (Smell 2.24/2.26)**: Garantia de que operações de I/O priorizem o sandbox `context-mode` sobre ferramentas nativas individuais de editor.

---

## 2. Tipos de Evals Mapeados

### 2.1 Tool Correctness & Tool Selection
- **Objetivo**: Avaliar se o subagente seleciona a ferramenta correta para o contexto e executa chamadas eficientes.
- **Aspectos Avaliados**:
  - **Tool Selection Ratio**: Escolha de `context-mode` (`ctx_execute`, `ctx_batch_execute`, `ctx_search`) em substituição a ferramentas nativas de editor (`read_file`, `create_file`).
  - **Batching & Consolidated Execution (Smell 2.26)**: Verificação de que operações envolvendo 2 ou mais arquivos são consolidadas em turnos únicos de execução, evitando encadeamento redundante de tool turns.
  - **Argument & Schema Correctness**: Validação de parâmetros (caminhos absolutos/relativos, timeouts, payloads válidos).
  - **Turn Budget Compliance**: Cumprimento do limite de turnos (≤ 5 tool turns por ciclo) com acionamento correto do Circuit Breaker na 4ª iteração.

### 2.2 Routing Accuracy & State Flow
- **Objetivo**: Validar a precisão e determinismo da Decision Tree do `agent-router` contra intenções de usuário.
- **Aspectos Avaliados**:
  - **Casos Canônicos**: Intenções com direcionamento explícito (ex.: "criar componente Angular" -> `@angular-router`; "especificar arquitetura" -> `@tech-solution-architect`).
  - **Casos Ambíguos / Edge Cases**: Intenções híbridas (ex.: "adicionar endpoint e tela para relatórios" -> decomposição correta via Workflow 4 Gateway).
  - **Anti-Sticky Session (R-042)**: Capacidade de desengajar e redirecionar quando o usuário altera o escopo da conversa.
  - **State-Locking Parity**: Emissão obrigatória do identificador `[CURRENT_STATE_LOCK: ...]` na primeira linha de execução.

### 2.3 Trace & Telemetry Integrity
- **Objetivo**: Assegurar fidelidade, conformidade e confidencialidade dos spans emitidos pelo pipeline OTel/Langfuse.
- **Aspectos Avaliados**:
  - **Semantics Compliance**: Emissão obrigatória de `gen_ai.provider.name` (substituindo o obsoleto `gen_ai.system`), `gen_ai.operation.name` (`chat`, `invoke_agent`, `execute_tool`).
  - **Proxy stdio MCP Tracing**: Spans `execute_tool` com atributos do protocolo JSON-RPC, nome da tool, duração real e status code/error mapping.
  - **Secret & PII Masking (Zero-Leak Gate)**: Mascaramento obrigatório via regex de tokens JWT, chaves de API, senhas e headers sensíveis nos spans (`traces.json`).

### 2.4 Content Quality / Faithfulness & Grounded Context
- **Objetivo**: Avaliar se a síntese e respostas do agente derivam estritamente do contexto fornecido pelo `context-mode` / base documental.
- **Aspectos Avaliados**:
  - **Faithfulness (Fidelidade)**: Ausência de afirmações que extrapolem o conteúdo inspecionado via sandbox.
  - **Hallucination Detection**: Respostas com referências a classes, métodos ou rotas inexistentes no repositório.
  - **Format Compliance**: Estrutura de saída alinhada com o contrato operacional do agente ativo (banner, seções obrigatórias e próximo passo mínimo).

---

## 3. Matriz de Cenários e Riscos de Teste

| ID | Dimensão | Tipo | Prioridade | Cenário / Comportamento Esperado | Risco Mitigado |
|---|---|---|---|---|---|
| **SCN-TOOL-01** | Tool Selection | Unit / Evals | **P1** | Subagente invoca `ctx_execute`/`ctx_batch_execute` para ler múltiplos arquivos em vez de encadear `read_file`. | Desperdício de contexto O(N), estouro de janela e violação do Smell 2.24/2.26. |
| **SCN-TOOL-02** | Tool Correctness | Evals | **P1** | Parâmetros de execução (linguagem, cwd, timeout) fornecidos em conformidade com schema e sem falha de parsing. | Aborto precoce de subprocessos e falha na extração de evidências. |
| **SCN-TOOL-03** | Turn Budget & Circuit Breaker | Integ | **P2** | Sessão interrompe chamadas após 4 turnos sem progresso, chamando `ask_questions` ou emitindo parecer conclusivo. | Loop investigativo infinito e exaustão de créditos (Smell 2.13). |
| **SCN-ROUT-01** | Routing Accuracy | Evals | **P1** | Prompt canônico de frontend/backend direciona exatamente para o domain-router correspondente. | Roteamento errático, degradação da experiência e retrabalho de handoff. |
| **SCN-ROUT-02** | Routing Edge Cases | Evals | **P2** | Prompt ambíguo com múltiplas tecnologias aciona `WF4_AGENT_ROUTER_GATEWAY` e monta plano decomposto. | Execução monolítica inadequada sem decomposição full-stack. |
| **SCN-ROUT-03** | Anti-Sticky Session | Evals | **P2** | Usuário altera o tópico da conversa e o agente realiza handoff com `motivo: "deriva_de_intencao"`. | Agente preso em contexto anterior respondendo fora do domínio. |
| **SCN-TRAC-01** | Telemetry Semantics | Contract | **P1** | Spans emitidos contêm `gen_ai.provider.name`, `gen_ai.operation.name` e identificadores de modelo corretos. | Telemetria quebrada, incompatibilidade com OTel Semconv v1.41+ e Langfuse. |
| **SCN-TRAC-02** | Tool Spans Proxy MCP | Integ | **P1** | Interceptação stdio gera spans com `execute_tool`, nome da ferramenta e duração real de execução. | Ferramentas invisíveis no tracing e incapacidade de auditar chamadas MCP. |
| **SCN-TRAC-03** | Data Masking / No Leak | Security | **P1** | Spans com tokens, passwords ou strings em padrão `Bearer ...` sofrem redacting automático (`[REDACTED]`). | Vazamento de credenciais e violação de conformidade de segurança. |
| **SCN-QUAL-01** | Faithfulness | Evals | **P1** | Síntese de resposta pontua ≥ 0.90 de concordância estrita com chunks retornados pelo context-mode. | Alucinações arquiteturais e respostas enganosas para o desenvolvedor. |
| **SCN-QUAL-02** | Navigation Shell Check | Contract | **P2** | Se houver nova rota proposta, a estratégia exige obrigatoriamente teste de navegabilidade no shell. | Telas órfãs sem links acessíveis em menus ou rotas do frontend. |

---

## 4. Thresholds de Qualidade & Quality Gate

| Métrica de Avaliação | Target / Threshold Mínimo | Impacto em CI/CD | Justificativa |
|---|---|---|---|
| **Routing Accuracy (Casos Canônicos)** | **100%** | **BLOCKER (P0)** | Nenhuma regressão é tolerada em caminhos primários de roteamento. |
| **Routing Accuracy (Casos Ambíguos / Borda)** | **≥ 80%** | **WARN / REVIEW** | Avalia resiliência e decomposição de intenções complexas. |
| **Tool Precedence Compliance (context-mode)** | **100%** | **BLOCKER (P0)** | Uso de ferramentas nativas manuais é estritamente proibido quando context-mode está ativo. |
| **Single-Turn Batching Compliance (≥ 2 alvos)** | **≥ 95%** | **BLOCKER (P1)** | Vedação de tool-chaining sequencial no chat. |
| **Secret & Credential Masking (Leak Rate)** | **0% (Zero Tolerância)** | **BLOCKER (P0)** | Spans com segredos não mascarados bloqueiam o build imediatamente. |
| **Telemetry Semantics Coverage** | **100%** | **BLOCKER (P1)** | Spans sem `gen_ai.provider.name` ou sem status válido são rejeitados. |
| **Content Faithfulness (DeepEval / Ragas)** | **≥ 0.85** | **BLOCKER (P1)** | Respostas devem ser estritamente fundamentadas no contexto inspecionado. |
| **Hallucination Rate** | **≤ 0.05** | **BLOCKER (P1)** | Taxa máxima tolerada de extrapolação factual. |

---

## 5. Estrutura de Execução no Pytest

A suíte de evals deve ser desacoplada em níveis de execução e integrada ao ecossistema existente sob o diretório `tests/`:

```
tests/
├── evals/
│   ├── conftest.py                   # Fixtures: mock OTel collector, traces loader, evals runner
│   ├── datasets/
│   │   ├── canonical_routing.yaml    # Prompts de teste canônicos para roteamento
│   │   ├── edge_case_routing.yaml    # Prompts ambíguos e de transição de estado
│   │   └── context_ground_truth.json # Pares de contexto inspecionado vs resposta esperada
│   ├── test_tool_selection_evals.py  # Avaliação de seleção e precedência de tools
│   ├── test_routing_accuracy_evals.py# Avaliação de acurácia da árvore de decisão
│   ├── test_telemetry_integrity.py   # Validação de spans OTel Semconv v1.41+ e masking
│   └── test_content_faithfulness.py  # Avaliação de fidelidade e alucinação
├── routing_gate/                     # Quality gate estático já existente (routing-graph.yaml)
├── governance_audit/                 # Governança estrutural de agentes e schemas
└── operational_flow/                 # Simulações de fluxo operacional e circuit breaker
```

### Marcadores do Pytest (`pytest.ini`)
- `@pytest.mark.evals_static`: Testes estáticos rápidos (contratos de spans, datasets, schemas). Roda em todo PR (gate rápido < 30s).
- `@pytest.mark.evals_trace`: Testes de integridade em traces capturados pelo proxy (`traces.json`).
- `@pytest.mark.evals_llm`: Testes estocásticos de inferência (DeepEval / Ragas). Roda em schedule noturno ou trigger manual de release.

---

## 6. Handoff e Próximos Passos Mínimos

1. **Domain Router / Test Writer Handoff**:
   - Acionar `@agent-router` para despacho aos test-writers competentes para implementar as suítes em `tests/evals/`.
   - Implementar os fixtures de trace e datasets YAML conforme a taxonomia definida.
2. **Observability Blueprint Alignment**:
   - O componente `tools/mcp-otel-proxy/` deve produzir saídas em conformidade direta com os contratos de `SCN-TRAC-01` a `SCN-TRAC-03`.
