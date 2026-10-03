---
name: performance-engineering-patterns
description: >
  Diretrizes consolidadas de performance engineering para revisão especializada —
  Core Web Vitals (LCP/INP/CLS) no frontend, N+1 queries e profiling de latência
  no backend, otimização de índice e queries no banco. Baseado em padrões de
  mercado 2026 (web.dev, DORA, práticas de revisão de performance).
tier: 2
category: quality
triggers:
  - "performance"
  - "otimização"
  - "latência"
  - "n+1"
  - "core web vitals"
  - "lcp"
  - "inp"
  - "cls"
  - "profiling"
  - "query lenta"
  - "throughput"
  - "sla"
  - "gargalo"
  - "bottleneck"
source_docs:
  - .github/skills/code-review-patterns/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Performance Engineering Patterns

> Base de conhecimento para agents que fazem **análise especializada de performance** — complementa a dimensão "Performance" já existente em `code-review-patterns` (genérica) com critérios objetivos por camada (frontend, backend, banco).

## Quando Usar

- Antes de aprovar merge de código em caminho quente (hot path) de alto tráfego.
- Ao investigar degradação de SLA/latência reportada em produção.
- Ao revisar queries novas ou alteradas em ORM.
- Ao avaliar Core Web Vitals de uma feature de frontend nova.

## 1) Frontend — Core Web Vitals (thresholds 2026)

| Métrica | Bom | Precisa melhorar | Ruim |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s–4s | > 4s |
| **INP** (Interaction to Next Paint) — substituiu FID em mar/2024 | ≤ 200ms (competitivo: ≤ 150ms) | 200ms–500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |

### Padrões de Otimização
- **LCP**: lazy-load de imagens abaixo da dobra, `NgOptimizedImage`/`next/image`, preload de recurso crítico, CDN.
- **INP**: mover trabalho pesado para fora da main thread (`scheduler.yield()`, Web Workers), evitar handlers síncronos longos, Server Components para reduzir JS no cliente.
- **CLS**: reservar espaço para imagens/anúncios (`width`/`height` ou `aspect-ratio`), evitar inserção de conteúdo acima do fold sem reserva de espaço.

## 2) Backend — Padrões de Degradação Comuns

| Padrão | Sintoma | Fix |
|---|---|---|
| **N+1 Query** | 1 query lista + N queries por item (loop) | JOIN, `prefetch_related`/`@EntityGraph`/`JOIN FETCH` |
| **Trabalho desnecessário em loop** | Alocação de objeto, regex compilado, connection lookup dentro de loop | Mover para fora do loop |
| **Falta de cache** | Recomputação de valor estável a cada requisição | Cache em memória (Caffeine/Redis) com TTL |
| **Payload excessivo** | Serialização de campos não usados pelo cliente | DTO de borda com apenas campos necessários |
| **Bloqueio de thread em I/O** | Chamada síncrona bloqueante em endpoint de alto tráfego | Virtual threads (Java 21+) ou reativo (WebFlux) |

### Critério de Revisão (não é otimização prematura)
> Performance review não é sobre benchmarking cada mudança — é sobre reconhecer padrões que **historicamente causam incidentes em produção em escala**.

- [ ] Query dentro de loop (N+1) → sempre reportar, independente de escala atual.
- [ ] Falta de índice em coluna de filtro frequente → reportar com evidência do plano de execução se disponível.
- [ ] Micro-otimização sem medição em caminho não-crítico → não reportar (evita review fatigue).

## 3) Banco de Dados — Otimização de Query

| Sinal | Ação Recomendada |
|---|---|
| `SELECT *` em produção | Listar colunas explícitas |
| Filtro sem índice (`WHERE campo_nao_indexado = ?`) | Sugerir `CREATE INDEX` |
| `LIKE '%termo%'` em tabela grande | Considerar full-text search / índice trigram |
| Paginação ausente em lista potencialmente grande | Adicionar `LIMIT`/`OFFSET` ou keyset pagination |
| Transação de escopo amplo | Reduzir escopo (abrir tarde, fechar cedo) |

## 4) Ferramentas de Medição

| Camada | Ferramenta |
|---|---|
| Frontend (lab) | Lighthouse CI, WebPageTest, Squoosh (imagens) |
| Frontend (RUM) | PageSpeed Insights (CrUX), SpeedCurve, Calibre |
| Backend (profiling) | async-profiler (Java), py-spy (Python), Node `--prof` |
| Banco | `EXPLAIN ANALYZE`, slow query log |
| Observabilidade | OpenTelemetry traces + métricas de latência p50/p95/p99 |

## 5) Critérios de Bloqueio de Merge

Bloquear (🔴) **somente** quando:
- N+1 query confirmado em caminho de alto tráfego (não apenas teórico).
- Ausência de paginação em endpoint que pode retornar volume ilimitado.
- Regressão de SLA documentada e mensurável (ex.: p95 de 200ms → 2s).
- Core Web Vitals "Ruim" introduzido em página crítica de conversão.

Demais achados → alertar (🟠/🟡), não bloquear por otimização especulativa sem medição.

## Checklist de Saída

- [ ] Padrão de degradação identificado com evidência (`arquivo:linha` ou query).
- [ ] Métrica alvo declarada (SLA, threshold de CWV) quando aplicável.
- [ ] Fix concreto sugerido, não apenas "otimizar".
- [ ] Distinção clara entre bloqueador (produção-crítico) e sugestão (otimização especulativa).

## Anti-Padrões

- ❌ Bloquear por otimização prematura sem medição em caminho não-crítico.
- ❌ Sugerir cache sem considerar invalidação/consistência.
- ❌ Reportar CWV "ruim" sem confirmar que a página é crítica para conversão/SEO.
- ❌ Ignorar trade-off entre performance e legibilidade/manutenibilidade sem justificativa de escala real.

## Referências

- web.dev Core Web Vitals — https://web.dev/vitals
- INP substituiu FID (mar/2024) — thresholds atualizados 2026.
- DORA metrics — cycle time e review velocity como proxies de saúde de engenharia.
- Padrões observados em ferramentas de mercado (CodeAnt.ai, Greptile, CodeRabbit) — performance como dimensão "quando importa", não bloqueio universal.

