---
name: spring-boot-performance-patterns
description: >-
  Diretrizes enterprise de engenharia de performance para Spring Boot (Java 21–25+):
  Virtual Threads (Project Loom) e mitigação de carrier pinning, dimensionamento
  de pool HikariCP, eliminação sistemática de N+1 (Record DTOs e EntityGraph),
  cache multi-nível (Caffeine L1 + Redis L2), Generational ZGC, AppCDS e Spring AOT.
tier: 2
category: quality
triggers:
  - "performance spring boot"
  - "virtual threads spring boot"
  - "thread pinning loom"
  - "hikaricp tuning"
  - "n+1 hibernate jpa"
  - "caffeine redis cache"
  - "generational zgc"
  - "spring boot aot cds"
  - "jvm gc tuning"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-boot/spring-boot-router.agent.md
tools: []
---

# Spring Boot Performance Patterns

> Base de conhecimento especializada em **engenharia de performance backend** para aplicações Spring Boot modernas (Java 21 a Java 25+). Utilizada pelo `@spring-boot-engineer` em modo Advisory (auditoria, dimensionamento, gargalos) e Implementação (aplicação direta de código otimizado).

## Quando Usar

- Ao habilitar ou calibrar Virtual Threads (Project Loom) em APIs I/O-bound.
- Ao dimensionar e diagnosticar saturação de pool de conexões (HikariCP).
- Ao eliminar queries N+1, overhead de Persistence Context ou serialização de entidades.
- Ao arquitetar estratégias de cache multi-nível com proteção contra cache stampede.
- Ao parametrizar flags de JVM (Generational ZGC) e otimizar tempo de inicialização (AppCDS/AOT).

---

## Pilares Técnicos de Performance

### 1) Virtual Threads (Project Loom) e Mitigação de Pinning

- **Ativação**: `spring.threads.virtual.enabled=true` (Spring Boot 3.2+).
- **Adequação de Carga**:
  - *Ideal*: Workloads I/O-bound síncronos (HTTP downstream, mensageria sequencial, queries JDBC).
  - *Inadequado*: Cargas CPU-intensive (compressão, criptografia pesada) ou agrupamento em pool manual (threads virtuais devem ser instanciadas e descartadas sob demanda).
- **Carrier Pinning**:
  - *Java 21–23*: Blocos `synchronized` envolvendo I/O bloqueante amarram a carrier thread do SO. Mitigar migrando para `java.util.concurrent.locks.ReentrantLock`.
  - *Java 24/25 (JEP 491)*: Monitor locks desacoplam threads virtuais nativamente; atentar apenas para chamadas JNI nativas.
  - *Diagnóstico*: `-Djdk.tracePinnedThreads=full`.

```yaml
# application.yml — Virtual threads ativadas
spring:
  threads:
    virtual:
      enabled: true
```

### 2) Dimensionamento Rigoroso de Pool HikariCP

- **Anti-pattern**: Inflar pool de conexões para acompanhar milhares de threads virtuais (gera saturação de CPU/disco no SGBD e contenção de locks).
- **Fórmula de Dimensionamento**:
  $$\text{Pool Size} = (\text{Cores do DB} \times 2) + \text{Canais/Discos}$$
  Geralmente entre 15 e 40 conexões por instância do serviço.
- **Fail-Fast**:
  Manter `connection-timeout: 2500` (ms) para falhar rápido sob sobrecarga, protegendo a estabilidade global.

```yaml
# application.yml — HikariCP tuning
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
      connection-timeout: 2500
      max-lifetime: 1800000
```

### 3) Eliminação Sistemática de N+1 no Hibernate / JPA

- **Record DTO Projections**:
  Utilizar projeções com construtor `SELECT new com.app.dto.ItemResumoDTO(...)` para leituras. Isola o *Persistence Context*, dispensa tracking de dirty checking e reduz alocação de heap.
- **`@EntityGraph` Dinâmico**:
  Substituir relacionamentos fixos `EAGER` por grafos declarativos em métodos de repositório específicos.
- **Batch Fetching de Segurança**:
  Configurar `hibernate.default_batch_fetch_size: 32` para agregar eventuais relacionamentos lazy pendentes em cláusulas `IN (?, ?, ...)`.

```java
// Repositório com EntityGraph para evitar N+1 em relacionamentos LAZY
@EntityGraph(attributePaths = {"itens", "itens.produto"})
List<Pedido> findTop100ByStatusOrderByDataDesc(StatusPedido status);
```

### 4) Cache Multi-Nível (L1 Caffeine + L2 Redis) e Stampede

- **Topologia Híbrida**:
  - *L1*: In-heap ultrarrápido com Caffeine (latência ~0.01 ms).
  - *L2*: Distribuído compartilhado com Redis (latência ~1–2 ms).
- **Invalidação Transversal**:
  Em mutações, persistir no DB e Redis, emitindo sinal via Redis Pub/Sub com o `instanceId`. Instâncias receptoras executam `caffeine.invalidate(key)`, ignorando mensagens originadas por si mesmas.
- **Single-Flight (Stampede Mitigation)**:
  Usar `caffeine.get(key, k -> carregarDoL2OuBanco(k))` para garantir apenas uma chamada concorrente por chave na mesma JVM.

### 5) JVM Generational ZGC, AppCDS e Spring AOT

- **Generational ZGC (JEP 439)**:
  Configurar `-XX:+UseZGC -XX:+ZGenerational` no Java 21 (padrão em Java 25). Pausas previsíveis sub-milissegundo (< 250 µs) em P99.9 mesmo sob alta taxa de alocação de DTOs.
- **AppCDS (Class Data Sharing)**:
  Gera dump de classes compartilhadas no build (`java -Djarmode=tools -jar app.jar extract`). Acelera boot em 50–70% com consumo de RSS reduzido via `mmap`.
- **Spring AOT Processing**:
  Executa inspeção antecipada de beans e configurações em tempo de build, otimizando caminhos de reflexão no runtime.

---

## Checklist Verificável

- [ ] `spring.threads.virtual.enabled=true` verificado sem blocos `synchronized` bloqueantes no caminho crítico.
- [ ] HikariCP configurado com teto condizente à capacidade real de hardware do SGBD.
- [ ] Mapeamentos de entidade utilizam `FetchType.LAZY` como padrão absoluto.
- [ ] Consultas de leitura utilizam Projeções (Records) ou `@EntityGraph` (zero queries N+1 no log).
- [ ] `hibernate.default_batch_fetch_size` definido para 32 ou 64 como guardrail.
- [ ] Caches L1/L2 possuem políticas de TTL e single-flight contra cache stampede.
- [ ] JVM de produção utiliza Generational ZGC para contenção de pausas de GC.

---

## Anti-padrões

| Anti-padrão | Impacto | Correção Recomendada |
|---|---|---|
| `FetchType.EAGER` em entidades | Queries gigantescas em cascata e N+1 crônico | Mudar para `LAZY` + Record Projections ou EntityGraph |
| Subir HikariCP para 500+ conexões | Colapso do Postgres/Oracle por context switch | Dimensionar pool com fórmula clássica (15–40) |
| Bloqueio síncrono em `synchronized` (Java 21) | Carrier thread pinning, degradação de throughput | Substituir por `ReentrantLock` |
| Ler entidade completa para leitura parcial | Overhead de heap e parsing do Persistence Context | Usar projeções DTO / Records |
| Cache sem TTL ou sem tamanho máximo | Vazamento de memória in-heap (OOM na JVM) | Configurar `maximumSize` e `expireAfterWrite` |

---

## Referências Oficiais

- OpenJDK: *JEP 491: Synchronize Virtual Threads without Pinning* (https://openjdk.org/jeps/491)
- OpenJDK: *JEP 439: Generational ZGC* (https://inside.java/2023/11/28/gen-zgc-explainer)
- Brett Wooldridge: *HikariCP Pool Sizing* (https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)
- Spring Boot Docs: *Class Data Sharing and AOT* (https://docs.spring.io/spring-boot/docs/current/reference/html/deployment.html)

