---
name: spring-reactive-webflux-patterns
description: >-
  Diretrizes enterprise para análise e recomendação de arquiteturas reativas com
  Spring WebFlux e Project Reactor, com foco em resiliência, capacidade e operação.
tier: 2
category: quality
triggers:
  - "spring webflux"
  - "project reactor"
  - "backend reativo"
  - "reactive streams"
  - "backpressure"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-reactive/spring-reactive-router.agent.md
tools: []
---

# Spring Reactive / WebFlux Patterns

> Esta skill cobre o modo **Advisory** (análise/recomendação, sem código). Para o modo **Implementação** (codificar feature/bugfix), ver [`spring-reactive-implementation-patterns`](../spring-reactive-implementation-patterns/SKILL.md).

## Quando usar

- Quando a solução exigir alta concorrência I/O-bound e latência previsível.
- Quando houver dúvidas sobre escolha entre modelo imperativo e reativo.
- Quando for necessário revisar pipelines Reactor, backpressure e controle de erros.
- Quando for preciso definir observabilidade e capacidade operacional de fluxos reativos.

## Pilares técnicos

| Pilar | Diretriz objetiva | Evidência mínima |
|---|---|---|
| Modelo de execução | Validar aderência do problema ao paradigma reativo antes de recomendar WebFlux | perfil de carga, padrão de I/O, SLA de latência |
| Composição reativa | Garantir cadeia Reactor legível, cancelável e com tratamento de erro explícito | fluxos `Mono`/`Flux`, estratégia de timeout/retry |
| Backpressure | Definir estratégia de controle de demanda e buffers por cenário | política de consumo, limites de fila e fallback |
| Integrações | Evitar bloqueio em event-loop e isolar pontos inevitavelmente bloqueantes | inventário de chamadas externas e drivers usados |
| Observabilidade | Coletar sinais de throughput, latência p95/p99 e taxa de erro por fluxo | métricas por endpoint/stream e tracing distribuído |
| Resiliência | Aplicar timeout, retry com limite e circuit breaker por risco | política de falhas transitórias vs permanentes |

## Checklist verificável

- [ ] Caso de uso justifica arquitetura reativa (I/O concorrente e custo de thread).
- [ ] Riscos de bloqueio em event-loop foram mapeados.
- [ ] Backpressure e limites de buffer foram definidos.
- [ ] Estratégia de erro/timeout/retry foi classificada por tipo de falha.
- [ ] Métricas operacionais mínimas foram especificadas (throughput, p95/p99, erro).

## Anti-padrões

- ❌ Adotar WebFlux por tendência sem requisito técnico objetivo.
- ❌ Misturar chamadas bloqueantes sem isolamento e sem mensuração de impacto.
- ❌ Usar retry infinito sem limite e sem política de idempotência.
- ❌ Publicar recomendação reativa sem critérios de observabilidade e capacidade.

## Referências oficiais

- Spring WebFlux Reference: https://docs.spring.io/spring-framework/reference/web/webflux.html
- Spring Boot Reactive Support: https://docs.spring.io/spring-boot/reference/web/reactive.html
- Project Reactor Reference: https://projectreactor.io/docs/core/release/reference/
- Reactive Streams Specification: https://www.reactive-streams.org/
- Micrometer Docs: https://docs.micrometer.io/
- OpenTelemetry Java: https://opentelemetry.io/docs/languages/java/

