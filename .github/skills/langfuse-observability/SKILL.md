---
name: langfuse-observability
description: >
  Especialização Langfuse para observabilidade de LLMs/Agents: modelo de dados
  trace→observations (span/generation/event), prompt management versionado com
  labels, evaluations/datasets/scores (LLM-as-judge) e integração com coding
  assistants via CLI/SDK/MCP. Complementa `agent-observability-otel`
  (convenções OTel GenAI vendor-neutral) com práticas Langfuse-specific (2025/2026).
tier: 2
category: observability
triggers:
  - "langfuse"
  - "prompt versioning"
  - "prompt management"
  - "llm tracing"
  - "dataset evaluation llm"
  - "llm as judge"
  - "trace langfuse"
  - "score generation"
  - "session tracing agent"
  - "langfuse cli"
source_docs:
  - .github/skills/agent-observability-otel/SKILL.md
  - .github/skills/agent-evals-lab/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Langfuse Observability

## 1) Quando Usar / Escopo

- Instrumentar aplicações LLM/agent com o SDK ou CLI do Langfuse (traces, generations, scores).
- Versionar e promover prompts (labels `production`/`staging`) com rastreabilidade prompt↔trace.
- Criar datasets de avaliação, rodar experiments (benchmarking entre versões de prompt/modelo) e configurar LLM-as-judge.
- Avaliar a própria skill de coding assistant (metodologia "Evaluating AI Agent Skills") antes de publicar.
- **Não usar para**: convenções OTel GenAI vendor-neutral genéricas (→ `agent-observability-otel`) nem para frameworks de eval standalone sem vínculo a Langfuse (→ `agent-evals-lab`). Esta skill é uma **especialização**, não substitui as duas — combine-as.

## 2) Modelo de Dados Langfuse

```
Trace (unidade de execução: 1 request/conversa/job)
 ├─ metadata: environment, user_id, session_id, tags, release
 └─ Observations (passos dentro do trace)
     ├─ Span       → etapa genérica (ex.: retrieval, orquestração)
     ├─ Generation → chamada de LLM (model, input, output, usage.tokens, cost)
     └─ Event      → ponto instantâneo (ex.: erro, decisão de roteamento)
```

- `trace_id` deve ser propagado via OTel context propagation quando integrado a `agent-observability-otel`.
- `generation` carrega prompt versionado (referência à versão usada), não só o texto renderizado.

## 3) Boas Práticas de Tracing

- Nomear traces de forma significativa (operação de negócio, não `"trace-1"`).
- `environment` (`production` | `staging` | `dev`) para segregar dashboards e custo de sampling.
- `user_id` para troubleshooting por usuário; `session_id` apenas quando há continuidade multi-turn real (app single-request não precisa).
- Vincular prompt versionado ao trace (rastreabilidade de qual prompt gerou qual resultado).
- Anexar `scores` (numérico, categórico ou booleano) e feedback humano diretamente ao trace/generation.
- Registrar tokens (`input`/`output`) e custo por generation — nunca deixar custo invisível.

## 4) Prompt Management

- `create_prompt` / `get_prompt` / `compile(variables)` para versionamento com variáveis.
- Labels de promoção controlada (ex.: `production`, `staging`) — nunca promover direto sem label.
- `prompt-migration`: versionar antes de qualquer deploy que altere comportamento do prompt em produção.

## 5) Evaluations, Datasets & Experiments

- Datasets com casos de teste (`input`/`expected`) para benchmarking reprodutível.
- `experiments` para comparar versões de prompt/modelo sobre o mesmo dataset.
- LLM-as-judge com critérios determinísticos calibrados (evitar juízo subjetivo não replicável).
- Scores numérico/categórico/booleano inline em traces e generations.
- Reaproveitar frameworks já normatizados em `agent-evals-lab` (DeepEval, Ragas, Promptfoo, MLflow) para gerar os scores estruturados antes de enviá-los ao Langfuse — não reimplementar métricas.

## 6) Integração com Coding Assistants

- Estrutura oficial do repositório `langfuse/skills`: `SKILL.md` (sempre carregado) + docs de referência sob demanda (`cli.md`, `instrumentation.md`, `prompt-migration.md`) — segue o Agent Skills Open Standard (progressive disclosure).
- `@langfuse/cli` (gerado a partir do OpenAPI spec) para consultar/gerenciar traces, prompts, datasets e scores sem sair do fluxo do assistente.
- Alternativa: MCP server do Langfuse para acesso via tool-calling nativo.
- Compatível com Claude Code, Cursor, Codex, Windsurf e GitHub Copilot (mesmo padrão de Agent Skill).
- Metodologia "Evaluating AI Agent Skills": dataset de prompts reais de usuário → execução do agente sobre o dataset → avaliação via LLM-as-judge com critérios determinísticos → iteração.

## 7) Anti-padrões

- ❌ Logar prompt/completion completo sem redaction/verificação de PII.
- ❌ Tratar Langfuse como observabilidade de infraestrutura full-stack — ele cobre LLM-behavior (prompts/tokens/scores), não substitui OTel Collector/APM (usar em conjunto, ver `agent-observability-otel` §5).
- ❌ Criar spans/generations proprietários sem atributos `gen_ai.*` (vendor lock-in — ver `agent-observability-otel` §7).
- ❌ Habilitar tracing verboso em produção sem `environment` segregando test/prod (custo e ruído de sampling).
- ❌ Ignorar `session_id`/`user_id` em apps multi-turn (degrada troubleshooting).
- ❌ Versionar prompt sem label de promoção controlada (deploy direto em `production`).
- ❌ Duplicar convenções de span já normatizadas em `agent-observability-otel` — usar como base, não reimplementar.
- ❌ Não marcar `gen_ai.tool.type = "mcp"` quando o trace envolve ferramentas MCP (perde granularidade de troubleshooting).

## 8) Checklist

- [ ] Trace nomeado com escopo/operação de negócio.
- [ ] `environment`, `user_id`, `session_id` (quando aplicável) presentes.
- [ ] Prompt versionado e linkado ao trace/generation.
- [ ] Scores/feedback anexados quando houver avaliação.
- [ ] PII redigida antes de logar prompt/completion.
- [ ] Dataset/experiment criado antes de promover mudança de prompt/modelo.
- [ ] Integração com `agent-observability-otel` verificada quando o stack já usa OTel Collector.

## 9) Referências

- Langfuse Docs — "What does a good trace look like?" (langfuse.com/docs/observability/best-practices).
- Langfuse Blog — "AI Agent Observability, Tracing & Evaluation with Langfuse".
- Langfuse Blog — "Evaluating AI Agent Skills" (2026-02-26).
- Langfuse Docs — "Agent Skill" (Agent Skills Open Standard, changelog 2026-05-26).
- GitHub `langfuse/skills` — estrutura oficial (`SKILL.md` + `cli.md`/`instrumentation.md`/`prompt-migration.md`).
- GitHub Discussion `langfuse/langfuse#3764` — boas práticas de tracing e tool usage.
- `.github/skills/agent-observability-otel/SKILL.md` — convenções OTel GenAI (base vendor-neutral).
- `.github/skills/agent-evals-lab/SKILL.md` — frameworks de eval (DeepEval/Ragas/Promptfoo/MLflow).
