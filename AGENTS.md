# Deep Agents Copilot — Cross-Tool Interoperability (AGENTS.md)

Este repositório adota o padrão aberto `AGENTS.md` para descoberta e interoperabilidade com ferramentas de IA generativa e agentes de código (Claude Code, OpenAI Codex, Cursor, GitHub Copilot, Gemini CLI).

## Fontes Normativas Canônicas

Para evitar duplicação e divergência de instruções, a fonte canônica e integral de governança reside em:
- **Claude Code / Global**: [`CLAUDE.md`](./CLAUDE.md)
- **GitHub Copilot / IDEs**: [`.github/copilot-instructions.md`](./.github/copilot-instructions.md)

## Diretrizes Fundamentais de Execução

1. **Ponto de Entrada Único & Re-triagem por Turno (R-037 / R-042)**:
   - Todo fluxo de trabalho inicia compulsoriamente no `@agent-router` (`.github/agents/agent-router.agent.md`).
   - A cada turno, a intenção é reavaliada contra a matriz de Não-Escopo para prevenir sticky sessions.

2. **Precedência Mandatória de Context Mode & Think-in-Code (R-008 / R-056)**:
   - Uso 100% obrigatório do MCP `context-mode` (`ctx_execute`, `ctx_batch_execute`, etc.) para leitura, escrita e testes.
   - Ferramentas nativas de editor e shell exploratório são estritamente proibidas quando o context-mode estiver acessível (rebaixadas a fallback exclusivo de indisponibilidade).

3. **Batching Compulsório (R-046 / R-059 / R-060)**:
   - Aplicação do Protocolo Plan-Then-Batch (limiar >= 2 alvos) via execução em processo único no sandbox (zero MCP tool chaining no chat) e teto estrito de ≤ 5 tool turns por ciclo.

## Catálogo de Agentes e Adapters de Stack

- **Catálogo de Agentes**: [`.github/agents/catalog.yaml`](./.github/agents/catalog.yaml)
- **Grafo de Roteamento**: [`.github/agents/routing-graph.yaml`](./.github/agents/routing-graph.yaml)
- **Adapters de Instrução por Stack**: [`.github/instructions/README.md`](./.github/instructions/README.md)
