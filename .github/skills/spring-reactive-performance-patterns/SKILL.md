---
name: spring-reactive-performance-patterns
description: >-
  Diretrizes enterprise de engenharia de performance para Spring WebFlux e Project Reactor:
  proteção do event-loop do Netty com BlockHound, controle de concorrência e prefetch
  em flatMap, estratégias de backpressure (limitRate, buffer overflow, drop seguro),
  tuning de memória Netty (PooledByteBufAllocator) e dimensionamento de r2dbc-pool.
tier: 2
category: quality
triggers:
  - "performance webflux"
  - "performance reactor"
  - "bloqueio event loop"
  - "blockhound webflux"
  - "flatmap concurrency prefetch"
  - "backpressure webflux"
  - "netty pooledbytebuf"
  - "r2dbc pool sizing"
  - "direct memory leak netty"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-reactive/spring-reactive-router.agent.md
tools: []
---

# Spring Reactive Performance Patterns

> Base de conhecimento especializada em **engenharia de performance reativa e não-bloqueante** para aplicações Spring WebFlux e Project Reactor. Utilizada pelo `@spring-reactive-engineer` em modo Advisory (auditoria de capacidade, backpressure, diagnóstico de saturação) e Implementação (aplicação direta de fluxos otimizados sem bloqueio).

## Quando Usar

- Ao auditar fluxos reativos contra bloqueio acidental do event-loop do Netty.
- Ao calibrar parâmetros de concorrência e prefetch de operadores como `flatMap`.
- Ao desenhar estratégias de backpressure sob fluxos de alta vazão ou clientes lentos.
- Ao dimensionar e investigar vazamentos de memória Direct (off-heap) no Netty.
- Ao configurar `r2dbc-pool` ou avaliar migração entre WebFlux e Virtual Threads.

---

## Pilares Técnicos de Performance

### 1) Proteção Estrita do Event-Loop (Zero Bloqueio)

- **BlockHound no CI**:
  Incluir `io.projectreactor.tools:blockhound-junit-platform` como gate de CI para abortar testes unitários que executem I/O síncrono ou bloqueios em threads do Reactor.
- **Isolamento de I/O Legado**:
  Encapsular chamadas bloqueantes inevitáveis com `subscribeOn(Schedulers.boundedElastic())`.
- **`subscribeOn` vs `publishOn`**:
  - `subscribeOn`: Altera a thread de geração da fonte inicial (upstream).
  - `publishOn`: Alterna a thread de processamento dos operadores subsequentes (downstream), útil para desviar cálculos pesados de CPU para `Schedulers.parallel()`.

```java
// Isolamento canônico de I/O bloqueante fora do event-loop
Mono<Dado> isolar(ServicoLegado servicoLegado) {
    return Mono.fromCallable(servicoLegado::obterDados)
        .subscribeOn(Schedulers.boundedElastic());
}
```

### 2) Concorrência e Prefetch no `flatMap`

- **Sobrecarga do Default**:
  O `flatMap(mapper)` sem parâmetros utiliza `concurrency=256` e `prefetch=32`. Sobrajamento de requisições satura servidores downstream e estoura filas em memória.
- **Assinatura Explicita**:
  Declarar sempre `flatMap(mapper, maxConcurrency, prefetch)` condizente à capacidade do downstream (ex.: concorrência 16, prefetch 8).
- **Semântica de Operadores Alternativos**:
  - `flatMapSequential`: Executa concorrente mas preserva ordem. Cuidado: atraso no 1º item retém os seguintes na memória (Head-of-Line Blocking).
  - `concatMap`: Execução estritamente sequencial (`concurrency=1`). Preserva ordem com menor consumo de memória e vazão moderada.

```java
// flatMap com controle rigoroso de concorrência e fila
Flux<Item> limitar(Flux<Item> fluxoOrigem) {
    return fluxoOrigem.flatMap(this::chamarApiExterna, 16, 8);
}
```

### 3) Estratégias de Backpressure

- **Fatiamento de Demanda (`limitRate`)**:
  Controla a quantidade de elementos requisitados upstream: `fluxo.limitRate(100, 75)` solicita 100 itens inicialmente e renova lotes de 75 a cada avanço.
- **Buffer com Estratégia de Transbordo**:
  Declarar limite e ação explícita para evitar OOM sob acúmulo:
  - `BufferOverflowStrategy.DROP_OLDEST`: Descarta elementos antigos (telemetria/métricas).
  - `BufferOverflowStrategy.DROP_LATEST`: Preserva fila existente e descarta novas entradas.
  - `BufferOverflowStrategy.ERROR`: Dispara `Exceptions.failWithOverflow()` fail-fast.
- **Descarte Seguro e Liberação Nativa**:
  Em `onBackpressureDrop()`, se os itens contiverem buffers nativos ou recursos gerenciados, liberar com `ReferenceCountUtil.safeRelease(msg)`.

```java
// Buffer com capacidade máxima e descarte seguro dos mais antigos
Flux<Evento> proteger(Flux<Evento> fluxoEventos) {
    return fluxoEventos.onBackpressureBuffer(1000, BufferOverflowStrategy.DROP_OLDEST);
}
```

### 4) Netty Memory e Connection Tuning

- **`PooledByteBufAllocator`**:
  Utiliza Direct Memory off-heap para permitir Zero-Copy I/O na placa de rede.
- **Virtual Threads Trap**:
  Manter `-Dio.netty.allocator.useCacheForAllThreads=false` (default seguro). Se ativado com Virtual Threads, gera vazamento incontrolável de buffers em `FastThreadLocal`.
- **Pool de Conexões HTTP (`ConnectionProvider`)**:
  Definir sempre limites para `maxConnections`, `pendingAcquireMaxCount` (evita fila ilimitada), `pendingAcquireTimeout` (fail-fast) e `maxIdleTime`.

```java
// ConnectionProvider bounded para WebClient
ConnectionProvider criarProvider() {
    return ConnectionProvider.builder("custom-pool")
        .maxConnections(50)
        .pendingAcquireMaxCount(200)
        .pendingAcquireTimeout(Duration.ofSeconds(3))
        .maxIdleTime(Duration.ofSeconds(20))
        .build();
}
```

### 5) R2DBC Connection Pooling e Trade-offs

- **Necessidade de `r2dbc-pool`**:
  O driver básico SPI não possui pool. A dependência `r2dbc-pool` é mandatória para controlar conexões físicas concorrentes com o banco (`max-size: 20–30`).
- **Matriz de Decisão Arquitetural (2025/2026)**:
  - *WebFlux + R2DBC*: Recomendado para streaming contínuo (SSE, WebSockets) ou clientes 100% não-bloqueantes.
  - *Spring MVC + Virtual Threads (Loom)*: Modelo preferencial para CRUDs corporativos e microsserviços típicos (mesmo throughput, código imperativo simples, ecossistema JPA maduro).

---

## Checklist Verificável

- [ ] Suíte de testes executa com BlockHound ativo e zero violações de thread bloqueante.
- [ ] Nenhum `flatMap` sem concorrência explícita (`maxConcurrency`, `prefetch`) em caminho quente.
- [ ] I/O bloqueante externo ou chamadas JDBC isoladas em `Schedulers.boundedElastic()`.
- [ ] Streams de alta vazão possuem `limitRate` ou `onBackpressureBuffer` parametrizado.
- [ ] `r2dbc-pool` configurado com teto máximo de conexões e timeout de espera explícitos.
- [ ] WebClient utiliza `ConnectionProvider` com fila pendente limitada e timeouts de vida útil.
- [ ] Buffers Netty descartados possuem liberação via `ReferenceCountUtil.safeRelease()`.

---

## Anti-padrões

| Anti-padrão | Impacto | Correção Recomendada |
|---|---|---|
| Chamar `.block()` em código de produção | Congelamento de thread no event-loop | Permanecer na composição reativa com operadores |
| `flatMap` sem limite de concorrência | Tempestade de requisições downstream e estouro de heap | Parametrizar `flatMap(fn, 16, 8)` |
| `flatMapSequential` sob fluxos desiguais | Head-of-line blocking e acúmulo de memória | Usar `flatMap` ou `concatMap` |
| Driver R2DBC sem dependência de pool | Abertura contínua de sockets e recusa do SGBD | Adicionar e configurar `r2dbc-pool` |
| Bloqueio síncrono dentro de `map()` | Degradação catastrófica de latência no Netty | Encapsular em `boundedElastic` |

---

## Referências Oficiais

- Project Reactor Core Docs: *Backpressure and Queues* (https://projectreactor.io/docs/core/release/reference/)
- Reactor Netty Docs: *ConnectionProvider and Memory Tuning* (https://projectreactor.io/docs/netty/snapshot/reference/)
- BlockHound Project: *Java Agent for Detecting Blocking Calls* (https://github.com/reactor/BlockHound)
- R2DBC Pool Specification: (https://github.com/r2dbc/r2dbc-pool)

