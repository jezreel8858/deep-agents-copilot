# Plano de Implementação Técnica — Consolidação da Stack Spring Boot (Fase 1 Piloto)

- **Workflow**: WORKFLOW-GOVERNANCE-MAINTENANCE — Etapa 4 (Plano de Implementação Técnica, R-064)
- **Gate**: 2º gate do Duplo Gate Documental (R-064.2) — **Status: 📝 PROPOSTO PARA APROVAÇÃO**
- **Autor**: docs-engineer (com validação técnica referencial de `spring-boot-arch-advisor`)
- **Data**: 2026-10-06
- **Documento-base**: `docs/plans/20261006-governance-maintenance-consolidacao-agents-stacks.md` (Plano Macro Aprovado — Opção C adotada)
- **Tier de Reversibilidade**: **Tier 2 (T2)** — Reversão via Git branch/tag isolada com backup preventivo (R-031)

---

## 1. Resumo Executivo e Escopo da Consolidação

### 1.1 Contexto e Justificativa
A análise da arquitetura de governança (`docs/plans/20261006-governance-maintenance-consolidacao-agents-stacks.md`) identificou sobrecarga cognitiva e latência operacional na stack `spring-boot` decorrentes da divisão em 7 especialistas verticais isolados mais 1 supervisor (`spring-boot-router`). Esse modelo hiper-fragmentado gerava proliferação de handoffs desnecessários (`[HANDOFF]` sob R-042), degradação de contexto em tarefas correlatas e custos elevados de manutenção.

Este Plano de Implementação Técnica detalha a execução da **Fase 1 (Piloto Central)** para a stack `spring-boot`, consolidando os 7 especialistas no **Padrão Triádico Canônico (3 especialistas + 1 router)**:
1. `spring-boot-arch-advisor` (Read-Only)
2. `spring-boot-developer` (Executor Mutativo de Produção)
3. `spring-boot-test-engineer` (Garantia de Qualidade e Testes)

O supervisor hierárquico `spring-boot-router` é preservado integralmente com suas 7 ferramentas canônicas sob o Baseline R-054, simplificando sua Árvore de Decisão para 3 ramos mutuamente exclusivos.

### 1.2 Topologia Canônica Alvo (Padrão Triádico de Stack)

```text
                        [ @agent-router ]
                                │
                                ▼
                    [ @spring-boot-router ]
                    (Supervisor Hierárquico)
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
[@spring-boot-arch]   [@spring-boot-dev]     [@spring-boot-test]
    (Read-Only)        (Executor Core)         (QA & Testes)
```

- **`spring-boot-arch-advisor`** (*Preservado / Read-Only*):
  - Responsável por análise arquitetural (Clean Architecture, Hexagonal), upgrades Java LTS (JDK 21/25), observabilidade (Micrometer, OpenTelemetry), Virtual Threads e autoria exclusiva de Planos Técnicos e Blueprints R-064.2.
- **`spring-boot-developer`** (*Novo Agente Consolidado / Mutativo*):
  - Absorve `spring-boot-feature-developer`, `spring-boot-bug-fixer` e `spring-boot-perf-tuner`.
  - Atua nos modos `feature`, `bugfix` e `perf`, desenvolvendo endpoints REST, services transacionais, DTOs Records, queries JPA e correções com diff cirúrgico.
- **`spring-boot-test-engineer`** (*Novo Agente Consolidado / Mutativo*):
  - Absorve `spring-boot-unit-test-writer`, `spring-boot-integration-test-writer` e `spring-boot-test-fixer`.
  - Atua nos modos `unit`, `integration` (Testcontainers, MockMvc, DataJpaTest) e `fix` (autocorreção com limite estrito de 3 iterações sob R-053).

---

## 2. Inventário Completo de Arquivos e Impacto no File System

Todas as mutações no repositório seguem atomicidade estrita (`all-or-nothing` sob R-051):

| Caminho do Arquivo | Ação | Justificativa Técnica / Governança |
|---|---|---|
| `.github/agents/backend/spring-boot/spring-boot-developer.agent.md` | **Criar** | Agente consolidador de desenvolvimento backend, correções e tuning. |
| `.github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md` | **Criar** | Agente consolidador de engenharia de testes e autocorreção de suítes. |
| `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` | **Modificar** | Sincronizar handoffs para `spring-boot-developer` e `spring-boot-test-engineer`. |
| `.github/agents/backend/spring-boot/spring-boot-router.agent.md` | **Modificar** | Atualizar Árvore de Decisão de 7 para 3 especialistas sob Baseline R-054. |
| `.github/agents/backend/spring-boot/spring-boot-catalog.yaml` | **Modificar** | Reestruturar sub-catálogo local para exatamente 3 especialistas + 1 router. |
| `.github/agents/catalog.yaml` | **Modificar** | Atualizar nó `spring-boot-router` e remover 6 IDs legados do catálogo central. |
| `.github/agents/routing-graph.yaml` | **Modificar** | Atualizar arestas e descrições do domínio backend Spring Boot. |
| `.github/agents/backend/spring-boot/spring-boot-feature-developer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `spring-boot-developer`). |
| `.github/agents/backend/spring-boot/spring-boot-bug-fixer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `spring-boot-developer`). |
| `.github/agents/backend/spring-boot/spring-boot-perf-tuner.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `spring-boot-developer`). |
| `.github/agents/backend/spring-boot/spring-boot-unit-test-writer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `spring-boot-test-engineer`). |
| `.github/agents/backend/spring-boot/spring-boot-integration-test-writer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `spring-boot-test-engineer`). |
| `.github/agents/backend/spring-boot/spring-boot-test-fixer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `spring-boot-test-engineer`). |
| `tests/governance_audit/test_feature_developer_test_authoring_boundary.py` | **Modificar** | Adequar validação da barreira de testes para o novo identificador `spring-boot-developer`. |
| `tests/governance_audit/test_spring_boot_consolidation.py` | **Criar** | Teste automatizado validando a invariante 3+1 e integridade referencial. |

---

## 3. Matriz de Migração de Conteúdo, Prompts e Modos Operacionais

A consolidação preserva 100% das heurísticas acumuladas no projeto, desacoplando-as em **modos operacionais** e **skills dinâmicas** sob **Progressive Disclosure (R-066)**:

| Agente Anterior | Destino Consolidado | Modo de Operação | Heurísticas e Regras Críticas Absorvidas | Skills Ativas (Estáticas / Dinâmicas) | Conjunto Canônico de Ferramentas (Tools) |
|---|---|---|---|---|---|
| `spring-boot-arch-advisor` | `spring-boot-arch-advisor` | `advisory` (Preservado) | Perfil Read-Only mandatória; sem comandos de mutação de código; elaboração de Planos Técnicos R-064.2 e ADRs; conformidade Java 21+ e Virtual Threads. | `spring-boot-backend-patterns`, `specialist-hybrid-advisory-implementation-patterns`, `agent-contracts`, `context-mode` | file_search, grep_search, list_dir, ask_questions, run_subagent, context-mode/ctx_search, context-mode/ctx_batch_execute, context-mode/ctx_index |
| `spring-boot-feature-developer` | `spring-boot-developer` | `feature` | TDD estrito (testing-first); DTOs Java Records; injeção por construtor via Lombok `@RequiredArgsConstructor` com `private final`; endpoints REST versionados `/v1/`; barreira de autoria de testes. | `spring-boot-implementation-patterns`, `efficient-batch-code-modification`, `terminal-governance`, `context-mode` | file_search, grep_search, list_dir, ask_questions, run_subagent, get_errors, run_in_terminal, context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch_execute, context-mode/ctx_index, context-mode/ctx_execute_file |
| `spring-boot-bug-fixer` | `spring-boot-developer` | `bugfix` | Root Cause Analysis (RCA); diagnóstico cirúrgico de `BusinessException`, `LazyInitializationException` e rollback indevido de transações; diff mínimo estrito. | `spring-boot-implementation-patterns`, `code-tracing`, `clean-architecture-patterns` (via R-066) | Mesmas ferramentas mutativas de `spring-boot-developer` |
| `spring-boot-perf-tuner` | `spring-boot-developer` | `perf` | Eliminação de N+1 via JPA EntityGraph e JOIN FETCH; tuning de pool HikariCP; otimização de Virtual Threads (não bloquear carrier thread); paginação de queries. | `spring-boot-performance-patterns`, `database-query-tuning-patterns` (via R-066) | Mesmas ferramentas mutativas de `spring-boot-developer` |
| `spring-boot-unit-test-writer` | `spring-boot-test-engineer` | `unit` | JUnit 5 + Mockito BDD (`given/when/then`); cobertura de fluxos alternativos e exceptions de domínio; isolamento hermético de dependências externas. | `test-implementation-spring-boot`, `test-coverage-governance`, `context-mode` | file_search, grep_search, list_dir, ask_questions, run_subagent, get_errors, run_in_terminal, context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch_execute, context-mode/ctx_index, context-mode/ctx_execute_file |
| `spring-boot-integration-test-writer` | `spring-boot-test-engineer` | `integration` | Testcontainers (PostgreSQL, Oracle, Kafka, LocalStack); `@DataJpaTest` e MockMvc com asserções estritas de JSONPath e HTTP status codes. | `test-implementation-spring-boot`, `testcontainers-patterns` (via R-066) | Mesmas ferramentas mutativas de `spring-boot-test-engineer` |
| `spring-boot-test-fixer` | `spring-boot-test-engineer` | `fix` | Estabilização de testes instáveis (flaky tests); teto rígido de 3 ciclos de autocorreção sob R-053; escalonamento compulsório ao atingir o limite. | `test-implementation-spring-boot`, `code-tracing` (via R-066) | Mesmas ferramentas mutativas de `spring-boot-test-engineer` |

### 3.1 Preservação da Barreira de Responsabilidade de Testes
Para evitar que o agente executor contamine a integridade das suítes de validação:
- O novo `spring-boot-developer` **NÃO PODE** ser o autor de novas classes de teste unitário ou de integração de regressão. Ele apenas roda testes pré-existentes para satisfazer o ciclo red-green-refactor e solicita formalmente a criação/ampliação de suítes ao `@spring-boot-test-engineer`.
- O `spring-boot-test-engineer` **NÃO PODE** alterar código de produção (services, controllers, repositories), limitando-se estritamente à autoria de testes e mocks.

---

## 4. Configuração de Modelos de IA e Política Biparadigma (R-021 / R-021.2)

A distribuição de capacidade de inferência segue a política de custo-benefício e determinismo do projeto:

| Agente | Perfil Operacional | Modelo Canônico Formal | Exceção Econômica Autorizada (R-021) | Critério de Escalonamento Automático (R-021.2) |
|---|---|---|---|---|
| **`spring-boot-router`** | Supervisor Hierárquico de Domínio | **Claude Sonnet 5.5** | Nenhuma (100% mandatória) | N/A |
| **`spring-boot-arch-advisor`** | Análise Arquitetural, Planos R-064.2 e ADRs | **Claude Sonnet 5.5** | Nenhuma (100% mandatória) | N/A |
| **`spring-boot-developer`** | Desenvolvimento de Produção, Bugfix e Concorrência | **Claude Sonnet 5.5** | Nenhuma (100% mandatória) | N/A |
| **`spring-boot-test-engineer`** | Planejamento de Cenários, Testcontainers e Flakiness | **Claude Sonnet 5.5** | **Claude Haiku / Gemini Flash** (permitido exclusivamente em geração repetitiva de DTOs de Mock, Fixtures e asserts triviais) | **Escalonamento Mandatório**: Caso a suíte acuse erro de compilação ou falha em 2 execuções consecutivas do mesmo ciclo, o sub-agente comuta imediatamente para **Claude Sonnet 5.5**. |

*Nota de Catálogo*: O campo `model:` declarado no frontmatter de catálogo (`spring-boot-catalog.yaml`) permanece fixado como **Claude Sonnet 5.5** para todos os especialistas.

---

## 5. Tier de Reversibilidade (T2) e Estratégia de Rollback

### 5.1 Enquadramento do Tier de Reversibilidade (R-031)
A consolidação da stack é classificada como **Tier 2 (T2 — Risco Estrutural Controlado)**:
- Impacta o roteamento hierárquico, a sincronização de 2 catálogos (`spring-boot-catalog.yaml` e `catalog.yaml`), o grafo global (`routing-graph.yaml`) e remove 6 arquivos de agente.
- A reversibilidade é 100% assegurada através de branch dedicada e tag Git pré-execução.

### 5.2 Procedimento de Checkpoint e Rollback Determinístico

```bash
# 1. Criação do checkpoint preventivo antes de iniciar a migração
git checkout -b chore/spring-boot-consolidation-phase1
git tag checkpoint-pre-consolidation-spring-boot

# 2. Em caso de falha nos Quality Gates ou testes de governança:
git reset --hard checkpoint-pre-consolidation-spring-boot
git clean -fd .github/agents/backend/spring-boot/
```

O tempo médio estimado de rollback é inferior a 15 segundos, restaurando integralmente os 7 especialistas originais sem efeitos colaterais.

---

## 6. Checklist de Execução Passo a Passo (GFM)

### 6.1 Pré-Requisitos e Baseline
- [ ] Criar branch `chore/spring-boot-consolidation-phase1`.
- [ ] Criar tag Git de segurança `checkpoint-pre-consolidation-spring-boot`.
- [ ] Executar baseline de governança: `pytest tests/governance_audit/test_router_agents.py tests/governance_audit/test_feature_developer_test_authoring_boundary.py`.
- [ ] Confirmar que nenhum arquivo em `.github/agents/backend/spring-boot/` possui alterações pendentes não commitadas.

### 6.2 Criação dos Agentes Consolidados
- [ ] Criar `.github/agents/backend/spring-boot/spring-boot-developer.agent.md` com suporte aos modos `feature`, `bugfix` e `perf`.
- [ ] Criar `.github/agents/backend/spring-boot/spring-boot-test-engineer.agent.md` com suporte aos modos `unit`, `integration` e `fix` (teto R-053).
- [ ] Validar frontmatters N1 e seções obrigatórias de cada novo agente contra os templates canônicos (`specialist-agent.md`).

### 6.3 Atualização dos Agentes Preservados
- [ ] Modificar `.github/agents/backend/spring-boot/spring-boot-arch-advisor.agent.md` atualizando a seção 'Quando Delegar' e regras de handoff.
- [ ] Modificar `.github/agents/backend/spring-boot/spring-boot-router.agent.md` reduzindo a Árvore de Decisão para os 3 ramos canônicos (`arch-advisor`, `developer`, `test-engineer`) sob o Baseline R-054.

### 6.4 Sincronização de Catálogos e Grafo Global
- [ ] Modificar `.github/agents/backend/spring-boot/spring-boot-catalog.yaml` mantendo exatamente os 3 novos especialistas e 1 router.
- [ ] Modificar `.github/agents/catalog.yaml` atualizando o nó `spring-boot-router` e expurgando as referências aos 6 especialistas antigos.
- [ ] Modificar `.github/agents/routing-graph.yaml` atualizando as arestas de entrada e saída do nó `spring-boot-router`.

### 6.5 Remoção Atômica dos Agentes Legados
- [ ] Remover `.github/agents/backend/spring-boot/spring-boot-feature-developer.agent.md`.
- [ ] Remover `.github/agents/backend/spring-boot/spring-boot-bug-fixer.agent.md`.
- [ ] Remover `.github/agents/backend/spring-boot/spring-boot-perf-tuner.agent.md`.
- [ ] Remover `.github/agents/backend/spring-boot/spring-boot-unit-test-writer.agent.md`.
- [ ] Remover `.github/agents/backend/spring-boot/spring-boot-integration-test-writer.agent.md`.
- [ ] Remover `.github/agents/backend/spring-boot/spring-boot-test-fixer.agent.md`.

### 6.6 Testes e Quality Gates
- [ ] Adaptar `tests/governance_audit/test_feature_developer_test_authoring_boundary.py` para validar `spring-boot-developer`.
- [ ] Criar `tests/governance_audit/test_spring_boot_consolidation.py` com asserções para:
  - Exatamente 3 especialistas e 1 router no diretório e no catálogo local.
  - Zero referências remanescentes aos agentes removidos no catálogo central e no grafo.
  - Paridade de tools do Baseline R-054 no `spring-boot-router`.
- [ ] Executar suíte completa de governança: `pytest tests/governance_audit/`.
- [ ] Obter relatório 100% verde (sem falhas novas).

---

## 7. Quality Gates e Critérios de Aceitação Determinísticos

| ID | Quality Gate | Mecanismo de Verificação | Critério de Aceitação Objetivo |
|---|---|---|---|
| **QG-01** | **Contagem Triádica Estrita** | `test_spring_boot_consolidation.py` | Exatamente 3 agentes especialistas e 1 router presentes no diretório `backend/spring-boot/`. |
| **QG-02** | **Conformidade R-054 do Router** | `test_router_agents.py` | `spring-boot-router` contém as 7 tools canônicas de supervisor hierárquico. |
| **QG-03** | **Integridade de Roteamento** | `test_governance_sync_core.py` | Grafo `routing-graph.yaml` sem nós órfãos, referências nulas ou ciclos inválidos. |
| **QG-04** | **Barreira de Autoria de Testes** | `test_feature_developer_test_authoring_boundary.py` | `spring-boot-developer` declara formalmente proibição de autoria final de testes. |
| **QG-05** | **Teto de Autocorreção (R-053)** | `test_test_fixer_retry_cap.py` | `spring-boot-test-engineer` possui teto máximo de 3 iterações de fix antes de escalonar. |
| **QG-06** | **Progressive Disclosure (R-066)** | `test_r066_progressive_disclosure_budget.py` | Metadados `source_docs_lazy:` respeitam o limite orçamentário de tokens. |
