---
name: agent-evals-lab
description: "Estrutura de avaliação contínua para agents de IA — baseada no ecossistema 2026 (DeepEval, Ragas, MLflow). Cobre métricas de qualidade, casos canônicos e ambíguos, regressão de roteamento e integração com CI/CD via pytest. Use quando atuar em evals agent, avaliação llm, deepeval. Não use para tarefas fora do escopo de agent-evals-lab ou implementação direta de código de negócio não relacionado."
tier: 2
category: quality
triggers:
  - "evals agent"
  - "avaliação llm"
  - "deepeval"
  - "ragas"
  - "hallucination detection"
  - "agent quality"
  - "test llm agent"
  - "regressão roteamento"
  - "benchmark agent"
  - "ci evals"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Agent Evals Lab

> **Baseado em**: DeepEval v3.0 · Ragas 0.2 · MLflow Tracing · ecossistema de evals 2026

## Quando Usar

- Ativação em cenários de evals agent, avaliação llm, deepeval.

## Quando NÃO Usar

- Não usar para demandas fora do domínio de `agent-evals-lab` ou quando outra skill específica cobrir integralmente o escopo.

## 1) Filosofia — Evals Como Quality Gate

Avaliação de agents não é QA de fim de processo — é **portão de implantação contínua**. A cada mudança de prompt, modelo ou tool, uma suíte de evals deve rodar automaticamente e bloquear regressões.

```
Mudança de prompt / modelo / tool
           ↓
  [Suíte de Evals Automáticos]
           ↓
  ┌────────────────────────────┐
  │  Métricas de qualidade     │
  │  Casos canônicos: ≥ 90%    │
  │  Casos ambíguos: ≥ 70%     │
  │  Regressão routing: 100%   │
  └────────────────────────────┘
           ↓
  PASS → deploy | FAIL → bloquear
```


## 2) Tipos de Métricas — O que Medir

### 2.1) Métricas de Resposta

| Métrica | O que mede | Framework | Quando usar |
|---|---|---|---|
| **Faithfulness** | Resposta se apoia em contexto fornecido | DeepEval, Ragas | RAG, análise de código |
| **Answer Relevancy** | Resposta responde à pergunta feita | DeepEval, Ragas | Q&A, busca |
| **Hallucination** | Afirmações não suportadas por contexto | DeepEval | Crítico — sempre |
| **Correctness** | Resposta é factualmente correta | DeepEval | Com ground truth |
| **Contextual Precision** | Chunks relevantes foram priorizados | Ragas | RAG |

### 2.2) Métricas de Agent

| Métrica | O que mede | Framework |
|---|---|---|
| **Tool Correctness** | Tool certa foi chamada | DeepEval |
| **Argument Correctness** | Argumentos corretos passados à tool | DeepEval |
| **Step Efficiency** | Mínimo de steps necessários foram usados | DeepEval |
| **Plan Adherence** | Agent seguiu o plano gerado | DeepEval |
| **Task Completion** | Tarefa foi completada com sucesso | Custom |

### 2.3) Métricas de Segurança

| Métrica | O que mede |
|---|---|
| **Prompt Injection** | Detecta tentativas de hijacking |
| **PII Leak** | Dados sensíveis vazaram no output |
| **Toxicity** | Conteúdo prejudicial no output |
| **Excessive Agency** | Agent realizou ações não solicitadas |

### 2.4) Métricas de Qualidade do Harness vs. Métricas do Modelo

Na engenharia de agentes contemporânea (2026), é imperativo desacoplar falhas do *modelo* (inferência pura) de falhas do *harness* (infraestrutura, ferramentas, system prompt e injeção de contexto), conforme preconizado em `harness-engineering-patterns`:

| Dimensão | O que avalia | Métricas típicas | Skill canônica de referência |
|---|---|---|---|
| **Qualidade do Modelo** | Capacidade de raciocínio, alucinação, consistência semântica e fidelidade das respostas | Faithfulness, Answer Relevancy, Hallucination, Correctness | `agent-evals-lab` (§ 2.1) |
| **Qualidade do Harness** | Precisão de tool definitions, schema de retorno, tamanho de janela útil, taxa de overhead de tokens e clareza de system prompt | Tool Calling Accuracy, Schema Adherence, Context Window Saturation, Tool Latency/Failures | `harness-engineering-patterns` |

> **Diagnóstico Cruzado**: Antes de culpar a capacidade de raciocínio do modelo por uma falha de agente, audite o harness: schemas de ferramentas ambíguos, instruções contraditórias em arquivos de prompt e saturação da janela útil (> 100k tokens) degradam drasticamente o desempenho mesmo dos modelos mais avançados.

---

## 3) Estrutura de Caso de Teste

```python
# Formato padrão — agnóstico de framework
{
  "id": "test-impl-001",
  "categoria": "canonico",         # canonico | ambiguo | regressao | seguranca
  "input": {
    "solicitacao": "Implementar testes para UserService",
    "contexto": "Spring Boot, JUnit 5",
    "stack": "backend"
  },
  "expected": {
    "agent_route": "test-implementation",  # agent esperado
    "tool_calls": ["read_file", "grep_search", "insert_edit_into_file"],
    "output_contains": ["@Test", "@ExtendWith", "verify("],
    "output_not_contains": ["git push", "npm install"]
  },
  "metricas": ["faithfulness", "tool_correctness", "task_completion"],
  "threshold": 0.85,               # score mínimo para PASS
  "critico": True                  # bloquear CI se falhar
}
```

---

## 4) Suítes de Avaliação

- **4.1 Suite Canônica (≥ 90% threshold)**: prompt claro → 1 agent esperado.
- **4.2 Suite Ambígua (≥ 70% threshold)**: prompt ambíguo → Clarify Gate ou múltiplos agents.
- **4.3 Suite de Regressão de Roteamento (100%)**: bugs históricos de roteamento.
- **4.4 Suite de Segurança (100% block rate)**: bloqueio de prompt injection e exfiltração.
- Exemplos YAML completos em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

## 5) Integração com CI/CD

- Executar suítes via `pytest` + `DeepEval` em pipeline GitHub Actions/GitLab a cada alteração em `.github/agents/**` ou `.github/skills/**`.
- Implementação de referência (`test_agent_routing.py` e workflow YAML) em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

## 6) Frameworks Recomendados (2026)

| Framework | Licença | Melhor Para |
|---|---|---|
| **DeepEval** | Apache 2.0 | Agent evals, pytest-native, 50+ métricas |
| **Ragas** | Apache 2.0 | RAG pipelines, contextual precision |
| **MLflow Evals** | Apache 2.0 | CI/CD integration, model registry |
| **Promptfoo** | MIT | Red teaming, segurança, comparação de prompts |
| **Arize Phoenix** | Elastic 2.0 | Observabilidade + evals integrados |

> **Recomendação**: DeepEval para CI/CD + Ragas para RAG quality + Promptfoo para security evals.

---

## 7) Anti-padrões

- ❌ Avaliar só com LLM-as-judge sem ground truth (viés do avaliador)
- ❌ Threshold único para todos os casos (canônico ≠ ambíguo)
- ❌ Evals apenas em desenvolvimento, não em CI/CD (regressões silenciosas)
- ❌ Casos de teste com intenção artificial (não representam uso real)
- ❌ Ignorar falhas de segurança em favor de métricas de qualidade
- ❌ Dataset estático sem atualização após mudanças de comportamento do model

---

## 8) Referências

- DeepEval: https://deepeval.com/
- Ragas: https://docs.ragas.io/
- MLflow Agent Evaluation: https://mlflow.org/top-5-agent-evaluation-frameworks
- Promptfoo (security): https://www.promptfoo.dev/
- LLM Eval 2026 Landscape: https://futureagi.substack.com/p/llm-evaluation-frameworks-metrics

---

## 9) Suíte de Casos Real — Fonte de Verdade

Os casos de teste desta skill estão materializados em:

**[`.github/agents/evals/casos-roteamento.yaml`](../../agents/evals/casos-roteamento.yaml)**

Estrutura do arquivo:
- `canonicos` — 10 casos com threshold 0.90 e `critico: true`
- `ambiguos` — 4 casos com threshold 0.70 e `comportamento: ask_questions`
- `regressao` — 5 casos com threshold 1.00 (bugs históricos de roteamento nunca devem regredir)
- `seguranca` — 4 casos de guardrail (prompt injection, commit autônomo, instalação, system prompt)

**Regra de manutenção** (análoga ao R-015): qualquer PR que altere `agent-router.agent.md` ou `.github/agents/routing-graph.yaml` **deve** atualizar o arquivo de casos na mesma entrega.

**Integração com CI** (conforme seção `execucao` do arquivo):
```yaml
# Gatilho sugerido para pipeline
on_change:
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/routing-graph.yaml"
run: pytest tests/evals/ --tb=short  # usando casos-roteamento.yaml como dataset
```

---

## 10) Mineração Contínua de Regressões (Data-Driven Evals)

Ciclo de retroalimentação contínua (*evals flywheel*): transforma falhas de roteamento e desvios operacionais reais capturados na telemetria FTS5 do Context Mode em novos casos de teste formais em `casos-roteamento.yaml`.

### 10.1) Consulta de Telemetria

A mineração é executada sob demanda (ex.: auditoria periódica pelo `agent-auditor` ou rotina de curadoria de qualidade) utilizando as tags padronizadas e os campos aditivos de telemetria (`session_id`, `sequence_index`, `call_stack_depth`, `outcome_summary`):

```json
// (a) Reconstruir timeline completa de uma sessão determinística via session_id + sequence_index
{
  "queries": ["session_id:<id_da_sessao>", "sequence_index"],
  "source": "handoff-telemetry:*",
  "sort": "timeline"
}
```
> **Finalidade (a)**: Permite auditar e validar se a trajetória do ecossistema e das delegações comportou-se de forma correta e sem desvios do início ao fim do chat.

```json
// (b) Detectar desvio de intenção/escopo via tag [INTENT_DRIFT] + outcome_summary
{
  "queries": ["[INTENT_DRIFT]", "outcome_summary"],
  "source": "handoff-telemetry:*"
}
```
> **Finalidade (b)**: Identifica transições onde agentes downstream reportaram deriva de escopo ou retorno ao router, permitindo isolar prompts ambíguos ou gaps de escopo no catálogo.

```json
// (c) Detectar complexidade excessiva via call_stack_depth elevado ou [LOOP_LIMIT] recorrente
{
  "queries": ["call_stack_depth", "[LOOP_LIMIT]"],
  "source": "handoff-telemetry:*"
}
```
> **Finalidade (c)**: Localiza aninhamentos excessivos de subagentes ou esgotamento de loops operacionais, elegendo automaticamente os fluxos anômalos como candidatos primários à simplificação arquitetural e refatoração de roteamento (handoff imediato para `@refactor-planner`).

### 10.2) Protocolo de Extração e Estruturação

1. **Isolamento de Contexto**: A partir dos registros recuperados, identificar:
   - Prompt ou solicitação original que causou a falha/deriva;
   - Agente emissor e rota que falhou;
   - Agente receptor correto identificado após resolução humana ou re-roteamento;
   - Lição aprendida e motivo da deriva.

2. **Formatação do Caso de Regressão**:
   - Adicionar novo caso sob a seção `regressao` de `.github/agents/evals/casos-roteamento.yaml`:
     ```yaml
     - id: "regr-XXX"
       solicitacao: "<texto do prompt minerado devidamente anonimizado>"
       rota_esperada: "<rota_correta>"
       agente_esperado: "<@agente_correto>"
       threshold: 1.00
       critico: true
       contexto: "<motivo da falha original minerada do log e lição aprendida>"
     ```

### 10.3) Portão de Sanitização Obrigatório (R-044)

**⚠️ REGRA BLOQUEANTE**: Nenhum caso minerado de telemetria pode ser gravado em `casos-roteamento.yaml` sem passar pelo filtro rigoroso de anonimização da norma **R-044**:
- Nomes de projetos/repositórios reais → genericizar para `[PROJETO-X]`.
- Nomes de classes, métodos e variáveis do domínio do usuário → genericizar para `ServicoExemploX`, `operacaoExemploX`.
- Caminhos absolutos do filesystem local (`<drive>:\<caminho>`, `/<pasta>/...`) → `<workspace>/[PROJETO-X]/...` ou suprimir.
- Credenciais, tokens ou dados pessoais (PII/R-010) eventualmente presentes no trace → remoção obrigatória.

## Checklist de Conformidade

- [ ] Diretrizes, contratos e restrições de escopo de `agent-evals-lab` verificados e atendidos.
