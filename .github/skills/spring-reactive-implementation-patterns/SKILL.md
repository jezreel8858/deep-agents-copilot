---
name: spring-reactive-implementation-patterns
description: >-
  Padrões de mercado consolidados (2026) para IMPLEMENTAR features novas e
  correções de bug em Spring WebFlux/Reactor — composição não-bloqueante,
  tratamento de erro por operador, testing com StepVerifier/WebTestClient.
  Contraparte de execução da `spring-reactive-webflux-patterns` (só análise).
tier: 2
category: quality
triggers:
  - "implementar endpoint reativo"
  - "corrigir bug webflux"
  - "feature reativa nova"
  - "codar pipeline reactor"
  - "stepverifier implementation"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-reactive/spring-reactive-router.agent.md
  - .github/skills/spring-reactive-webflux-patterns/SKILL.md
tools: []
---

# Spring Reactive Implementation Patterns

## Quando Usar

- Ao implementar feature nova em WebFlux/Reactor com justificativa técnica já validada (I/O-bound real, não modismo).
- Ao corrigir bug com causa raiz localizada (bloqueio de event-loop, erro não tratado, leak de subscription).
- Ao decidir operador de erro/composição **durante a escrita do código**.

## Regra de Ouro — Nunca Bloquear

| Prática proibida | Alternativa correta |
|---|---|
| `Thread.sleep(...)` dentro da cadeia reativa | `.delayElement(Duration...)` |
| `.block()` em código de produção | Retornar `Mono`/`Flux` e deixar o Spring subscrever |
| `.subscribe(...)` manual dentro de `@Controller` | `return` do `Mono`/`Flux` diretamente do handler |
| Driver JDBC clássico dentro do pipeline reativo | Driver reativo (R2DBC) ou isolar em `Schedulers.boundedElastic()` com justificativa |

## Workflow — Feature Nova

1. Confirmar que o caso de uso justifica reativo (perfil de carga, SLA — handoff de `@spring-reactive-engineer` advisory ou análise prévia).
2. Escrever teste com `StepVerifier` (unidade) e/ou `WebTestClient` (endpoint) antes da implementação.
3. Implementar cadeia `Mono`/`Flux` legível: 1 operador por linha lógica, nomes de variável descritivos.
4. Adicionar tratamento de erro explícito (nunca cadeia sem `onError*`).
5. Rodar suíte local antes de reportar sucesso.
6. `get_errors` no(s) arquivo(s) editado(s).

## Workflow — Correção de Bug

1. Exigir causa raiz com evidência (`arquivo:linha`) — se ausente, delegar para `@bug-triage` primeiro.
2. Classificar o tipo: bloqueio de event-loop | erro não tratado | backpressure/overflow | leak de subscription.
3. Reproduzir com `StepVerifier` antes de corrigir.
4. Diff mínimo — isolar a correção ao operador/trecho afetado.

## Padrões de Código (mercado 2026)

| Operador de erro | Uso |
|---|---|
| `onErrorReturn` | Valor de fallback fixo quando o erro ocorre |
| `onErrorResume` | Substituir por outro `Publisher` (ex.: cache, serviço alternativo) |
| `onErrorMap` | Traduzir exceção de infra para exceção de domínio |
| `onErrorContinue` | Logar e continuar o stream sem propagar (usar com cautela — nunca default) |
| `retryWhen` | Retry com backoff e limite — nunca retry infinito |

| Prática | Diretriz |
|---|---|
| Service layer | Retornar `Mono<T>`/`Flux<T>` diretamente, sem lógica bloqueante misturada |
| `WebClient` | Substituto reativo de `RestTemplate` para chamadas externas |
| Cache de publisher | `Mono.cache()`/`Flux.cache()` quando múltiplos subscribers no mesmo publisher |
| Cancelamento | Garantir que operações longas respeitem cancelamento do subscriber |

## Testing-First (obrigatório)

- `StepVerifier` para lógica de composição Reactor (unidade).
- `WebTestClient` para contrato HTTP do endpoint reativo.
- Nenhuma implementação é considerada concluída sem teste executado e resultado reportado.

## Checklist de PR (implementação)

- [ ] Nenhuma chamada bloqueante dentro da cadeia reativa (`Thread.sleep`, `.block()`, JDBC clássico sem isolamento).
- [ ] Tratamento de erro explícito em toda cadeia pública (`onError*`).
- [ ] Teste com `StepVerifier`/`WebTestClient` cobre o comportamento implementado/corrigido.
- [ ] Sem `.subscribe()` manual em controller/handler.
- [ ] `get_errors` limpo no(s) arquivo(s) tocado(s).
- [ ] Diff mínimo — sem refactor oportunista fora do escopo pedido.

## Anti-padrões

- ❌ Implementar sem teste (viola testing-first).
- ❌ Bloquear o event-loop com `Thread.sleep`, `.block()` ou driver JDBC clássico sem isolamento.
- ❌ Cadeia reativa sem tratamento de erro explícito.
- ❌ `retry` sem limite e sem política de idempotência.
- ❌ Adotar WebFlux para caso de uso que virtual threads (Spring Boot MVC) resolveriam de forma mais simples — reavaliar com `@spring-boot` antes de implementar.
- ❌ Reportar "concluído" sem rodar a suíte de teste local.

## Referências

- Spring WebFlux Reference: https://docs.spring.io/spring-framework/reference/web/webflux.html
- Project Reactor Reference: https://projectreactor.io/docs/core/release/reference/
- Common Mistakes in WebFlux (bloqueio, erro, subscribe manual): https://dev.to/adamthedeveloper/spring-webflux-when-to-use-it-and-how-to-build-with-it-5a6e
- Reactor error handling operators: https://rabobank.jobs/en/techblog/the-5-basic-topics-you-should-know-about-project-reactor
- Spring Reactor 2026 — quando ainda vale a pena: https://lucaberton.com/blog/spring-reactor-reactive-java-2026

