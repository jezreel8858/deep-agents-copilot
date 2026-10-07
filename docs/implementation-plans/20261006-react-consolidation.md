# Plano de Implementação Técnica — Consolidação da Stack React (Fase 1 Piloto)

- **Workflow**: WORKFLOW-GOVERNANCE-MAINTENANCE — Etapa 4 (Plano de Implementação Técnica, R-064)
- **Gate**: 2º gate do Duplo Gate Documental (R-064.2) — **Status: 📝 PROPOSTO PARA APROVAÇÃO**
- **Autor**: docs-engineer (com validação técnica referencial de `react-arch-advisor`)
- **Data**: 2026-10-06
- **Documento-base**: `docs/plans/20261006-governance-maintenance-consolidacao-agents-stacks.md` (Plano Macro Aprovado — Opção C adotada)
- **Tier de Reversibilidade**: **Tier 2 (T2)** — Reversão via Git branch/tag isolada com backup preventivo (R-031)

---

## 1. Resumo Executivo e Escopo da Consolidação

### 1.1 Contexto e Justificativa
A auditoria de arquitetura de governança identificou severa dispersão funcional na stack `react`, que contava com 8 agentes especialistas mais 1 supervisor (`react-router`). Funções fortemente integradas na rotina de engenharia de frontend moderno — como criação de componentes, estilização via Tailwind/CSS Modules e resolução de re-renders indesejados — estavam particionadas entre `react-feature-developer`, `react-ui-stylist` e `react-bug-fixer`. Paralelamente, a camada de testes estava fragmentada em 4 agentes separados (`unit-test-writer`, `component-test-writer`, `e2e-writer`, `test-fixer`).

Este Plano de Implementação Técnica detalha a execução da **Fase 1 (Piloto Central)** para a stack `react`, reduzindo o catálogo de 8 especialistas para **3 agentes canônicos** estruturados sob o **Padrão Triádico**:
1. `react-arch-advisor` (Read-Only)
2. `react-developer` (Executor Mutativo de Frontend)
3. `react-test-engineer` (Garantia de Qualidade e Testes de UI)

O supervisor `react-router` é integralmente preservado, retendo suas 7 ferramentas canônicas sob o Baseline R-054 e adotando uma Árvore de Decisão simplificada e determinística.

### 1.2 Topologia Canônica Alvo (Padrão Triádico de Stack)

```text
                        [ @agent-router ]
                                │
                                ▼
                       [ @react-router ]
                    (Supervisor Hierárquico)
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
  [@react-arch]          [@react-dev]           [@react-test]
   (Read-Only)          (Executor Core)         (QA & Testes)
```

- **`react-arch-advisor`** (*Preservado / Read-Only*):
  - Responsável por análise arquitetural (React 19+, Server Components vs Client Components), React Compiler, design de estado global (TanStack Query / Zustand), auditoria de Core Web Vitals (INP, LCP, CLS) e autoria exclusiva de Planos Técnicos R-064.2.
- **`react-developer`** (*Novo Agente Consolidado / Mutativo*):
  - Absorve `react-feature-developer`, `react-bug-fixer` e `react-ui-stylist`.
  - Atua nos modos `feature`, `bugfix` e `styling`, construindo componentes acessíveis, custom hooks, gerenciamento de estado e estilização responsiva sob metodologia Test-Last.
- **`react-test-engineer`** (*Novo Agente Consolidado / Mutativo*):
  - Absorve `react-unit-test-writer`, `react-component-test-writer`, `react-e2e-writer` e `react-test-fixer`.
  - Atua nos modos `unit` (Vitest), `component` (React Testing Library), `e2e` (Playwright) e `fix` (autocorreção de testes flaky com teto R-053).

---

## 2. Inventário Completo de Arquivos e Impacto no File System

Todas as mutações seguem o princípio de atomicidade estrita (`all-or-nothing` sob R-051):

| Caminho do Arquivo | Ação | Justificativa Técnica / Governança |
|---|---|---|
| `.github/agents/frontend/react/react-developer.agent.md` | **Criar** | Agente consolidador de desenvolvimento de tela, estilização e bugs de UI. |
| `.github/agents/frontend/react/react-test-engineer.agent.md` | **Criar** | Agente consolidador de testes frontend (Vitest, RTL, Playwright) e fix. |
| `.github/agents/frontend/react/react-arch-advisor.agent.md` | **Modificar** | Sincronizar handoffs para `react-developer` e `react-test-engineer`. |
| `.github/agents/frontend/react/react-router.agent.md` | **Modificar** | Reestruturar a Árvore de Decisão para 3 ramos exclusivos sob Baseline R-054. |
| `.github/agents/frontend/react/react-catalog.yaml` | **Modificar** | Reestruturar sub-catálogo local para exatamente 3 especialistas + 1 router. |
| `.github/agents/catalog.yaml` | **Modificar** | Atualizar nó `react-router` e remover 7 IDs legados do catálogo global. |
| `.github/agents/routing-graph.yaml` | **Modificar** | Atualizar nós, arestas e keywords do ecossistema React. |
| `.github/agents/frontend/react/react-feature-developer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-developer`). |
| `.github/agents/frontend/react/react-bug-fixer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-developer`). |
| `.github/agents/frontend/react/react-ui-stylist.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-developer`). |
| `.github/agents/frontend/react/react-unit-test-writer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-test-engineer`). |
| `.github/agents/frontend/react/react-component-test-writer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-test-engineer`). |
| `.github/agents/frontend/react/react-e2e-writer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-test-engineer`). |
| `.github/agents/frontend/react/react-test-fixer.agent.md` | **Remover** | Especialista legado descontinuado (absorvido por `react-test-engineer`). |
| `tests/governance_audit/test_frontend_test_last_governance.py` | **Modificar** | Atualizar asserções de Test-Last e isenção de testes para `react-developer`. |
| `tests/governance_audit/test_react_consolidation.py` | **Criar** | Teste automatizado validando a topologia 3+1 e integridade referencial. |

---

## 3. Matriz de Migração de Conteúdo, Prompts e Modos Operacionais

A consolidação absorve integralmente as atribuições dos 8 especialistas originais em **modos operacionais** orientados por tarefa e **skills dinâmicas** acionadas sob **Progressive Disclosure (R-066)**:

| Agente Anterior | Destino Consolidado | Modo de Operação | Heurísticas e Regras Críticas Absorvidas | Skills Ativas (Estáticas / Dinâmicas) | Conjunto Canônico de Ferramentas (Tools) |
|---|---|---|---|---|---|
| `react-arch-advisor` | `react-arch-advisor` | `advisory` (Preservado) | Perfil Read-Only mandatória; sem ferramentas de escrita de código; análise de CWV (INP/LCP/CLS); Server vs Client Components; TanStack Query e Zustand; autoria de Planos R-064.2. | `react-frontend-patterns`, `react-performance-patterns`, `specialist-hybrid-advisory-implementation-patterns`, `context-mode` | file_search, grep_search, list_dir, ask_questions, run_subagent, context-mode/ctx_search, context-mode/ctx_batch_execute, context-mode/ctx_index |
| `react-feature-developer` | `react-developer` | `feature` | Tipagem TypeScript estrita; metodologia Test-Last em UI; separação de server-state (TanStack Query) e client-state (Zustand); custom hooks focados em responsabilidade única. | `react-implementation-patterns`, `efficient-batch-code-modification`, `terminal-governance`, `context-mode`, `frontend-visual-feedback-loop` | file_search, grep_search, list_dir, ask_questions, run_subagent, get_errors, run_in_terminal, context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch_execute, context-mode/ctx_index, context-mode/ctx_execute_file, Playwright (inspeção) |
| `react-bug-fixer` | `react-developer` | `bugfix` | Diagnóstico de re-render storms; correção de memory leaks em subscriptions de hooks; validação do array de dependências de `useEffect`; diff cirúrgico com zero refatoração colateral. | `react-implementation-patterns`, `code-tracing` (via R-066) | Mesmas ferramentas mutativas de `react-developer` |
| `react-ui-stylist` | `react-developer` | `styling` | Design tokens semânticos; mobile-first responsivo; Tailwind CSS / CSS Modules; acessibilidade WCAG 2.1 AA (contraste, foco visível, rótulos ARIA); loops visuais via snapshots. | `react-responsive-ui-patterns`, `frontend-visual-feedback-loop` (via R-066) | Mesmas ferramentas mutativas de `react-developer` + Playwright para screenshots e inspeção de layout |
| `react-unit-test-writer` | `react-test-engineer` | `unit` | Vitest para testes isolados de hooks (`renderHook`), reducers puros e funções de transformação de dados; sem dependência do DOM real. | `test-implementation-react-vitest`, `test-coverage-governance`, `context-mode` | file_search, grep_search, list_dir, ask_questions, run_subagent, get_errors, run_in_terminal, context-mode/ctx_execute, context-mode/ctx_search, context-mode/ctx_batch_execute, context-mode/ctx_index, context-mode/ctx_execute_file |
| `react-component-test-writer` | `react-test-engineer` | `component` | React Testing Library (RTL); queries orientadas a acessibilidade (`getByRole`, `findByLabelText`); mock de providers (QueryClientProvider, ThemeProvider); user-event para disparos reais. | `test-implementation-react-vitest`, `frontend-visual-feedback-loop` | Mesmas ferramentas mutativas de `react-test-engineer` + Playwright |
| `react-e2e-writer` | `react-test-engineer` | `e2e` | Playwright com Page Object Model (POM); testes de jornada do usuário; gravação de trace e vídeo sob falha; asserções determinísticas de navegação e rede. | `playwright-mcp`, `test-implementation-frontend` | Mesmas ferramentas mutativas de `react-test-engineer` + suite Playwright completa |
| `react-test-fixer` | `react-test-engineer` | `fix` | Estabilização de testes flaky de frontend; tratamento de concorrência e timers assíncronos (`waitFor`, `act`); teto de 3 iterações sob R-053 com escalonamento formal. | `test-implementation-react-vitest`, `code-tracing` (via R-066) | Mesmas ferramentas mutativas de `react-test-engineer` |

### 3.1 Preservação da Barreira Test-Last e Isenção de Testes no Frontend
A fusão do papel de estilização visual no `react-developer` exige conformidade com as diretrizes consolidadas de frontend:
- O `react-developer` opera no modelo **Test-Last / Implementation-First**: sua responsabilidade principal é a renderização visual, ergonomia de componentes e estilização responsiva. Ele é **expressamente proibido de ser o autor de suítes de testes unitários ou de integração**.
- O `react-test-engineer` assume de forma independente a autoria de testes pós-implementação, eliminando o viés do desenvolvedor e garantindo cobertura idônea.

---

## 4. Configuração de Modelos de IA e Política Biparadigma (R-021 / R-021.2)

A governança de modelos garante alta precisão sem desperdício de recursos computacionais:

| Agente | Perfil Operacional | Modelo Canônico Formal | Exceção Econômica Autorizada (R-021) | Critério de Escalonamento Automático (R-021.2) |
|---|---|---|---|---|
| **`react-router`** | Supervisor Hierárquico de Domínio | **Claude Sonnet 5.5** | Nenhuma (100% mandatória) | N/A |
| **`react-arch-advisor`** | Análise Arquitetural, CWV, RSC e Planos R-064.2 | **Claude Sonnet 5.5** | Nenhuma (100% mandatória) | N/A |
| **`react-developer`** | Desenvolvimento de Telas, Hooks, Styling e Bugs | **Claude Sonnet 5.5** | Nenhuma (100% mandatória) | N/A |
| **`react-test-engineer`** | Planejamento de Casos RTL, E2E Playwright e Flakiness | **Claude Sonnet 5.5** | **Claude Haiku / Gemini Flash** (permitido exclusivamente em geração repetitiva de mocks de dados, fixtures de componente e asserts triviais de render) | **Escalonamento Mandatório**: Caso a execução do Vitest ou Playwright falhe em 2 ciclos consecutivos, o sub-agente comuta imediatamente para **Claude Sonnet 5.5**. |

*Nota de Catálogo*: O campo `model:` declarado no frontmatter de catálogo (`react-catalog.yaml`) permanece formalizado como **Claude Sonnet 5.5** para todos os especialistas.

---

## 5. Tier de Reversibilidade (T2) e Estratégia de Rollback

### 5.1 Enquadramento do Tier de Reversibilidade (R-031)
A consolidação da stack React é classificada como **Tier 2 (T2 — Risco Estrutural Controlado)**:
- Impacta o roteamento de frontend, remove 7 arquivos de agentes legados, cria 2 novos agentes e atualiza o grafo central.
- A reversibilidade determinística é garantida via Git branch e checkpoint tag.

### 5.2 Procedimento de Checkpoint e Rollback Determinístico

```bash
# 1. Criação do checkpoint preventivo antes de iniciar a migração
git checkout -b chore/react-consolidation-phase1
git tag checkpoint-pre-consolidation-react

# 2. Em caso de falha nos Quality Gates ou testes de governança:
git reset --hard checkpoint-pre-consolidation-react
git clean -fd .github/agents/frontend/react/
```

O rollback atômico restaura o repositório em menos de 15 segundos sem deixar nós corrompidos.

---

## 6. Checklist de Execução Passo a Passo (GFM)

### 6.1 Pré-Requisitos e Baseline
- [ ] Criar branch `chore/react-consolidation-phase1`.
- [ ] Criar tag Git de segurança `checkpoint-pre-consolidation-react`.
- [ ] Executar baseline de governança: `pytest tests/governance_audit/test_frontend_test_last_governance.py tests/governance_audit/test_router_agents.py`.
- [ ] Verificar ausência de diffs pendentes em `.github/agents/frontend/react/`.

### 6.2 Criação dos Agentes Consolidados
- [ ] Criar `.github/agents/frontend/react/react-developer.agent.md` com suporte aos modos `feature`, `bugfix` e `styling`, absorvendo as tools de Playwright para feedback visual.
- [ ] Criar `.github/agents/frontend/react/react-test-engineer.agent.md` com suporte aos modos `unit`, `component`, `e2e` e `fix` (teto R-053).
- [ ] Validar frontmatters N1 e seções obrigatórias de cada novo agente contra os templates canônicos (`specialist-agent.md`).

### 6.3 Atualização dos Agentes Preservados
- [ ] Modificar `.github/agents/frontend/react/react-arch-advisor.agent.md` atualizando a seção 'Quando Delegar' e regras de handoff.
- [ ] Modificar `.github/agents/frontend/react/react-router.agent.md` reduzindo a Árvore de Decisão para os 3 ramos canônicos (`arch-advisor`, `developer`, `test-engineer`) sob o Baseline R-054.

### 6.4 Sincronização de Catálogos e Grafo Global
- [ ] Modificar `.github/agents/frontend/react/react-catalog.yaml` registrando exatamente os 3 especialistas e 1 router.
- [ ] Modificar `.github/agents/catalog.yaml` atualizando o nó `react-router` e expurgando as referências aos 7 especialistas antigos.
- [ ] Modificar `.github/agents/routing-graph.yaml` atualizando as arestas e keywords do domínio `react-router`.

### 6.5 Remoção Atômica dos Agentes Legados
- [ ] Remover `.github/agents/frontend/react/react-feature-developer.agent.md`.
- [ ] Remover `.github/agents/frontend/react/react-bug-fixer.agent.md`.
- [ ] Remover `.github/agents/frontend/react/react-ui-stylist.agent.md`.
- [ ] Remover `.github/agents/frontend/react/react-unit-test-writer.agent.md`.
- [ ] Remover `.github/agents/frontend/react/react-component-test-writer.agent.md`.
- [ ] Remover `.github/agents/frontend/react/react-e2e-writer.agent.md`.
- [ ] Remover `.github/agents/frontend/react/react-test-fixer.agent.md`.

### 6.6 Testes e Quality Gates
- [ ] Atualizar `tests/governance_audit/test_frontend_test_last_governance.py` para validar `react-developer`.
- [ ] Criar `tests/governance_audit/test_react_consolidation.py` com asserções para:
  - Exatamente 3 especialistas e 1 router no diretório e catálogo local.
  - Zero referências remanescentes aos agentes removidos no catálogo central e no grafo.
  - Paridade de tools do Baseline R-054 no `react-router`.
- [ ] Executar suíte completa de governança: `pytest tests/governance_audit/`.
- [ ] Obter relatório 100% verde (sem falhas novas).

---

## 7. Quality Gates e Critérios de Aceitação Determinísticos

| ID | Quality Gate | Mecanismo de Verificação | Critério de Aceitação Objetivo |
|---|---|---|---|
| **QG-01** | **Contagem Triádica Estrita** | `test_react_consolidation.py` | Exatamente 3 agentes especialistas e 1 router presentes no diretório `frontend/react/`. |
| **QG-02** | **Conformidade R-054 do Router** | `test_router_agents.py` | `react-router` contém as 7 tools canônicas de supervisor hierárquico. |
| **QG-03** | **Barreira Test-Last Frontend** | `test_frontend_test_last_governance.py` | `react-developer` declara formalmente proibição de autoria de specs de teste. |
| **QG-04** | **Integridade de Roteamento** | `test_governance_sync_core.py` | Grafo `routing-graph.yaml` sem nós órfãos ou arestas inválidas. |
| **QG-05** | **Teto de Autocorreção (R-053)** | `test_test_fixer_retry_cap.py` | `react-test-engineer` possui teto máximo de 3 iterações de fix antes de escalonar. |
| **QG-06** | **Progressive Disclosure (R-066)** | `test_r066_progressive_disclosure_budget.py` | Metadados `source_docs_lazy:` respeitam o limite orçamentário de tokens sem context bloat. |
