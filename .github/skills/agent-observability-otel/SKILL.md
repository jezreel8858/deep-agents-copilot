---
name: agent-observability-otel
description: >
  Convenções de observabilidade para agents de IA com OpenTelemetry GenAI Semantic
  Conventions v1.41+ (2026). Cobre spans (invoke_agent, execute_tool, chat), métricas
  de tokens/latência/custo, logs estruturados e integração com backends (Langfuse Cloud, Datadog).
tier: 2
category: observability
triggers:
  - "observability agent"
  - "opentelemetry llm"
  - "otel genai"
  - "tracing agent"
  - "spans llm"
  - "token usage metrics"
  - "latência llm"
  - "gen_ai semconv"
  - "langfuse"
  - "rastreabilidade agent"
  - "mcp tool tracing"
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Agent Observability — OpenTelemetry GenAI

> **Baseado em**: OTel GenAI Semantic Conventions v1.41+ (status: Development) · 2026
> **Nota**: atributos `gen_ai.*` podem mudar sem major version bump — validar contra spec antes de usar em produção. A partir de v1.36+, `gen_ai.system` foi **deprecado** em favor de `gen_ai.provider.name`; manter leitura de fallback apenas para instrumentações legadas ainda não migradas.

## 1) Por que Observabilidade em Agents?

Agents falham de formas que parecem sucesso: outputs bem formados mas incorretos, tool calls redundantes, ações semanticamente inválidas. Métricas tradicionais (HTTP 200, latência p99) não capturam isso.

**O que precisa ser rastreado em agents:**
- Decisões do LLM (quais tools foram chamadas e com quais argumentos)
- Latência por etapa (LLM call, tool execution, retrying)
- Uso e custo de tokens por sessão e por usuário
- Falhas de ferramenta e seus motivos
- Handoffs entre agents (quem delegou para quem)

---

## 2) OTel GenAI — Tipos de Span

A OTel GenAI Semantic Conventions definem os principais tipos de span via `gen_ai.operation.name`: `chat`, `invoke_agent`, `execute_tool`, `create_agent` e `embeddings`.

### 2.1) gen_ai.client.chat — Chamada ao LLM

```
Span Kind: CLIENT
Operação:  gen_ai.operation.name = "chat"

Atributos obrigatórios:
  gen_ai.provider.name     = "openai" | "anthropic" | "azure.ai.openai" | "gcp.gemini"
                             ← substitui gen_ai.system (deprecado v1.36+)
  gen_ai.request.model     = "gpt-4o" | "claude-sonnet-4" | etc.
  gen_ai.response.model    = modelo real usado (pode diferir do solicitado)

Atributos de uso:
  gen_ai.usage.input_tokens   = N    ← tokens enviados (prompt)
  gen_ai.usage.output_tokens  = N    ← tokens gerados (completion)
                                        (gen_ai.usage.total_tokens NÃO é atributo
                                         oficial da spec — computar client-side
                                         como input_tokens + output_tokens)

Atributos de performance:
  gen_ai.request.temperature  = 0.7
  gen_ai.request.max_tokens   = 4096
  gen_ai.response.finish_reason = "stop" | "length" | "tool_calls"
```

### 2.2) invoke_agent — Invocação de Agent

```
Span Kind: SERVER (se entrada do usuário) ou CLIENT (se delegação de outro agent)
Operação:  gen_ai.operation.name = "invoke_agent"

Atributos:
  gen_ai.agent.name           = "test-implementation"   ← nome do agent
  gen_ai.agent.description    = "Implementa suítes de teste"
  gen_ai.provider.name        = "openai" | "anthropic" | etc. (provider do modelo do agent)
  gen_ai.request.id           = "<uuid-da-sessão>"      ← correlation ID
  agent.conversation.id       = "<conversa>"
```

### 2.3) execute_tool — Execução de Tool/MCP

```
Span Kind: INTERNAL
Operação:  gen_ai.operation.name = "execute_tool"

Atributos:
  gen_ai.tool.name            = "read_file" | "grep_search" | "run_in_terminal"
  gen_ai.tool.call.id         = "<id-da-chamada>"
  gen_ai.tool.description     = "Lê conteúdo de arquivo"
  gen_ai.tool.type            = "function" | "mcp"        ← "mcp" para tools MCP
  tool.execution.status       = "success" | "error" | "timeout"
  tool.execution.duration_ms  = 123

Exemplo — tool nativa MCP (context-mode):
  gen_ai.operation.name = "execute_tool"
  gen_ai.tool.name      = "context-mode/ctx_search"
  gen_ai.tool.type      = "mcp"
  gen_ai.tool.call.id   = "call_8f2a"
  tool.execution.status = "success"
```

### 2.4) Hierarquia de Spans (Multi-step Agent)

```
[invoke_agent: test-implementation]          ← raiz da sessão
  ├── [gen_ai.client.chat]                   ← 1ª chamada ao LLM
  │     └── gen_ai.provider.name=anthropic · tokens: 850 in / 320 out
  ├── [execute_tool: read_file]              ← tool call 1 (type=function)
  │     └── duration: 12ms, status: success
  ├── [execute_tool: context-mode/ctx_search] ← tool call 2 (type=mcp)
  │     └── duration: 45ms, status: success
  ├── [gen_ai.client.chat]                   ← 2ª chamada ao LLM (com tool results)
  │     └── gen_ai.provider.name=anthropic · tokens: 1200 in / 580 out
  └── [execute_tool: insert_edit_into_file]  ← tool call 3 (type=function)
        └── duration: 8ms, status: success
```

---

## 3) Métricas Obrigatórias (gen_ai.*)

```yaml
# Métricas definidas na OTel GenAI spec

gen_ai.client.token.usage:
  tipo: Histogram
  unit: tokens
  labels: [gen_ai.provider.name, gen_ai.request.model, gen_ai.token.type]
  quando: cada chamada LLM
  alerta: p95 > 3000 tokens/req → revisar prompt

gen_ai.client.operation.duration:
  tipo: Histogram
  unit: segundos
  labels: [gen_ai.provider.name, gen_ai.request.model, gen_ai.operation.name]
  quando: cada operação LLM
  alerta: p99 > 30s → degradação do provider

gen_ai.tool.execution.duration:
  tipo: Histogram
  unit: milissegundos
  labels: [gen_ai.tool.name, gen_ai.tool.type, tool.execution.status]
  quando: cada tool call (inclui tools nativas e MCP)
  alerta: qualquer tool > 5s → timeout implícito

gen_ai.session.cost:
  tipo: Counter
  unit: USD
  labels: [gen_ai.agent.name, gen_ai.provider.name, gen_ai.request.model]
  quando: cada sessão completa
  alerta: > $0.50/sessão → revisar eficiência
```

---

## 4) Logs Estruturados (JSON)

```json
{
  "timestamp": "2026-07-30T14:23:05.123Z",
  "level": "INFO",
  "service": "copilot-agent",
  "agent_name": "test-implementation",
  "operation": "execute_tool",
  "tool_name": "context-mode/ctx_search",
  "tool_type": "mcp",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "duration_ms": 12,
  "status": "success",
  "message": "Tool executada com sucesso"
}
```

**Campos obrigatórios em todos os logs de agent:**
- `timestamp` — ISO 8601 com milliseconds
- `trace_id` + `span_id` — correlação com traces OTel
- `agent_name` — qual agent gerou o log
- `operation` — qual ação foi executada (`chat` | `invoke_agent` | `execute_tool`)
- `status` — `success` | `error` | `timeout`

---

## 5) Backends de Observabilidade

| Backend | Tipo | OTel GenAI Nativo | Melhor Para |
|---|---|---|---|
| **Langfuse Cloud** | SaaS (gratuito até 50k traces/mês) | ✅ | **Padrão recomendado**: zero overhead de CPU/RAM local, traces LLM, prompt versioning, custo |
| **Langfuse (Self-hosted)** | ✅ Open Source | ✅ | Traces LLM, prompt versioning, custo (requer infraestrutura local/dedicada) |
| **MLflow Tracing** | ✅ | ✅ | CI/CD integration, model registry |
| **Arize Phoenix** | ✅ (Elastic 2.0) | ✅ | RAG + agent traces combinados |
| **Datadog LLM Obs.** | ❌ | ✅ v1.37+ | Infraestrutura + LLM em um só lugar |
| **Grafana + Tempo** | ✅ | Parcial | Self-hosted, budget constrained |

### 5.1 Destino OTLP Padrão: Langfuse Cloud (SaaS)

Para evitar consumo massivo de CPU/RAM em máquinas de desenvolvimento locais decorrente de contêineres analíticos pesados (ClickHouse, PostgreSQL, MinIO, Redis), o padrão arquitetural do repositório é o **Langfuse Cloud** (`https://cloud.langfuse.com` ou `https://us.cloud.langfuse.com`):
- **Zero footprint local**: Sem instâncias locais de banco de dados analítico ou storage de objetos.
- **Endpoint OTLP**: `https://cloud.langfuse.com/api/public/otel`
- **Autenticação**: Header HTTP `Authorization: Basic <base64(public_key:secret_key)>`
- **Proxy OTel Local Leve**: O OpenTelemetry Collector local atua exclusivamente como pipeline de mascaramento prévio (redaction) e normalização Semconv v1.41+ antes do envio seguro para a nuvem.

---

## 6) Boas Práticas

- **Correlacionar com `trace_id`**: toda log line, erro e métrica de uma sessão deve compartilhar o mesmo `trace_id` para correlação no backend
- **Não logar conteúdo de prompt/completion por padrão**: pode conter PII — usar feature flag controlada
- **Instrumentar tool calls individuais**: latência por tool é mais útil que latência total da sessão; marcar `gen_ai.tool.type` (`function` vs `mcp`) para diferenciar tools nativas de MCP
- **Token budget awareness**: emitir alerta quando sessão ultrapassa 80% do token budget configurado, usando `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens`
- **Gravar finish_reason**: `tool_calls` vs `stop` vs `length` indica qualidade da conversa
- **Migrar `gen_ai.system` → `gen_ai.provider.name`**: instrumentações legadas devem ser atualizadas; dashboards e alertas que ainda referenciam `gen_ai.system` devem manter leitura dual temporária até a migração completa

---

## 7) Anti-padrões

- ❌ Logar prompt completo ou completion sem verificar PII
- ❌ Usar apenas métricas de HTTP (status 200) para monitorar saúde de agents
- ❌ Não correlacionar logs com trace_id (impossível debugar multi-step agents)
- ❌ Medir só latência end-to-end sem breakdown por etapa (LLM vs tool)
- ❌ Não registrar token usage (custo invisível)
- ❌ Criar spans proprietários sem usar atributos gen_ai.* (lock-in de vendor)
- ❌ Continuar emitindo apenas `gen_ai.system` sem migrar para `gen_ai.provider.name` (atributo deprecado desde v1.36+)
- ❌ Tratar tools MCP como tools de função comuns sem marcar `gen_ai.tool.type = "mcp"` (perde granularidade de troubleshooting)

---

## 8) Referências

- OTel GenAI Semconv v1.41+: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Zylos Research — OTel for AI Agents: https://zylos.ai/research/2026-02-28-opentelemetry-ai-agent-observability
- Digital Applied — Observability 2026: https://www.digitalapplied.com/blog/ai-agent-observability-2026-tracing-monitoring-stack-guide
- OpenLLMetry (instrumentação automática): https://github.com/traceloop/openllmetry
- Langfuse Cloud (backend gerenciado SaaS): https://cloud.langfuse.com/
- Langfuse Docs (OpenTelemetry Ingestion): https://langfuse.com/docs/analytics/overview
