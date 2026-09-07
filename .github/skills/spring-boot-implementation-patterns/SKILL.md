---
name: spring-boot-implementation-patterns
description: >-
  Padrões de mercado consolidados (2026) para IMPLEMENTAR features novas e
  correções de bug em Spring Boot — virtual threads vs reativo, N+1/OSIV,
  DTOs de borda, workflow testing-first. Contraparte de execução da
  `spring-boot-backend-patterns` (que é só análise/recomendação).
tier: 2
category: quality
triggers:
  - "implementar service spring boot"
  - "corrigir bug spring boot"
  - "feature spring boot nova"
  - "codar endpoint spring"
  - "virtual threads implementation"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/backend/spring-boot/spring-boot-router.agent.md
  - .github/skills/spring-boot-backend-patterns/SKILL.md
  - .github/instructions/spring-boot-backend.instructions.md
tools: []
---

# Spring Boot Implementation Patterns

## Quando Usar

- Ao implementar feature nova (Entity/Service/Controller) em Spring Boot.
- Ao corrigir bug com causa raiz já localizada no código.
- Ao decidir concorrência **durante a escrita do código**: virtual threads (Java 21+, blocking simples) vs `@spring-reactive-engineer` (I/O-bound extremo) — ver matriz de decisão abaixo.

## Matriz de Decisão — Concorrência (mercado 2026)

| Cenário | Escolha | Racional |
|---|---|---|
| CRUD típico, <1000 req concorrentes, JDBC/JPA | Virtual threads (`spring.threads.virtual.enabled=true`) | Código blocking simples escala sem reescrever para reativo |
| Alta concorrência I/O-bound extrema, drivers reativos disponíveis | WebFlux/Reactor (`@spring-reactive-engineer`) | Ganho real só com stack 100% não-bloqueante ponta a ponta |
| CPU-bound | Nenhum dos dois resolve sozinho | Escalar horizontalmente ou otimizar algoritmo |

## Workflow — Feature Nova

1. Confirmar escopo/critério de aceite (handoff de `@requirements-analyst`/`@tech-solution-architect` se houver).
2. Escrever teste (unitário e, se aplicável, `@DataJpaTest`/slice) antes da implementação (testing-first).
3. Implementar seguindo o adapter do projeto (`spring-boot-backend.instructions.md`): `@Entity`/`@Builder`, `XxxService`+`XxxServiceImpl`, `@RequiredArgsConstructor` com `private final`, controller com `@ResponseStatus` explícito.
4. Nunca retornar `Entity` diretamente do controller — sempre DTO de borda.
5. Rodar testes locais (`mvnw test -Dtest=...` em lote) antes de reportar sucesso.
6. `get_errors` no(s) arquivo(s) editado(s).

## Workflow — Correção de Bug

1. Exigir causa raiz com evidência (`arquivo:linha`) — se ausente, delegar para `@bug-triage` primeiro.
2. Reproduzir a falha em teste antes de corrigir.
3. Diff mínimo — nunca refatorar módulo inteiro para 1 bug.
4. Validar teste de regressão + suíte do módulo intacta.

## Padrões de Código (mercado 2026)

| Prática | Diretriz | Evidência de conformidade |
|---|---|---|
| Injeção de dependência | Constructor injection (`@RequiredArgsConstructor`), nunca field injection | Sem `@Autowired` em campo |
| Configuração | `@ConfigurationProperties` tipado, nunca `@Value` espalhado | Classe de config dedicada por domínio |
| Persistência | Evitar N+1: `JOIN FETCH`/`@EntityGraph`; cuidado com paginação + fetch join | Query plan revisado; sem lazy-loading acidental em loop |
| OSIV | Avaliar `spring.jpa.open-in-view=false` explicitamente (não deixar default implícito) | Decisão documentada no adapter do projeto |
| Concorrência | Virtual threads para blocking simples (Spring Boot 3.2+, Java 21) | `spring.threads.virtual.enabled=true` + pool HikariCP dimensionado (não usar default de 10 sob alta concorrência) |
| Exceções | `BusinessException`/`IntegrationException` + `@RestControllerAdvice` central | Nunca engolir exceção sem log |

## Testing-First (obrigatório)

- Base: JUnit 5 + Mockito (ver `test-implementation-spring-boot` para padrões detalhados de mock/AAA).
- Nenhuma implementação é considerada concluída sem teste executado e resultado reportado.
- Diff coverage do trecho alterado — não da suíte inteira.

## Checklist de PR (implementação)

- [ ] Teste novo/atualizado cobre o comportamento implementado ou corrigido.
- [ ] Controller retorna DTO, nunca Entity.
- [ ] Sem N+1 introduzido (verificado via query log ou `@EntityGraph`).
- [ ] Convenções do adapter do projeto respeitadas (schema, transaction manager).
- [ ] `get_errors` limpo no(s) arquivo(s) tocado(s).
- [ ] Diff mínimo — sem refactor oportunista fora do escopo pedido.

## Anti-padrões

- ❌ Implementar sem teste (viola testing-first).
- ❌ Field injection (`@Autowired` em campo) em vez de constructor injection.
- ❌ Retornar Entity JPA diretamente do controller.
- ❌ Migrar para WebFlux "porque é mais rápido" sem stack 100% não-bloqueante e sem medir ganho real vs virtual threads.
- ❌ Aumentar pool de conexão sem entender o motivo (virtual threads mudam a matemática do pool).
- ❌ Reportar "concluído" sem rodar a suíte de teste local.

## Referências

- Spring Boot Virtual Threads (Project Loom) 2026: https://www.nordync.com/blog/spring-boot-virtual-threads-project-loom-2026
- Spring Data JPA — N+1, OSIV, paginação: https://blog.devgenius.io/spring-boot-jpa-virtual-threads-java-21-avoid-n-1-osiv-pagination-pitfalls-0bde190da6bc
- Spring Boot Reference: https://docs.spring.io/spring-boot/reference/
- `test-implementation-spring-boot` (skill) — padrões detalhados JUnit 5 + Mockito

