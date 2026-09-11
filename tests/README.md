# Arquitetura e Estrutura de Testes — Multi-Agent System (MAS)

> **Documentação de Governança de Qualidade**  
> Referência normativa: [`CLAUDE.md`](../CLAUDE.md) (regras normativas globais), [`agent-evals-lab/SKILL.md`](../.github/skills/agent-evals-lab/SKILL.md) e [`governance-audit-patterns/SKILL.md`](../.github/skills/governance-audit-patterns/SKILL.md).

Este documento descreve a arquitetura, a taxonomia e a cobertura de todos os arquivos de teste do ecossistema `deep-agents-copilot`. Seguindo as melhores práticas da engenharia de software para **Sistemas Multi-Agentes (MAS)** de 2025/2026, a qualidade é tratada como um **Quality Gate Contínuo em Camadas**, garantindo determinismo, segurança, menor privilégio de ferramentas e prevenção de regressões em rotas e workflows.

---

## 1. Pirâmide de Testes para Sistemas Multi-Agentes

Diferente de aplicações monolíticas tradicionais, um sistema multi-agente opera sobre máquinas de estados finitos (FSM), grafos de decisão direcionados e interfaces conversacionais com LLM. Para evitar custos proibitivos de inferência e *flakiness* (não-determinismo) em CI/CD, adotamos uma **Pirâmide de Testes em 3 Camadas**:

```text
                        ▲
                       / \     Camada 3: Avaliação de Trajetória / User Simulation
                      / L3\    Prompt /eval-workflows com Gemini 3.8 Flash (caso a caso)
                     /-----\
                    /  L2   \  Camada 2: Trajetórias E2E & Invariantes de Handoff
                   /         \ Transições de workflows, schema v1.3 e isolamento de tools
                  /-----------\
                 /     L1      \ Camada 1: Quality Gate Estático & Topologia de Grafos
                /               \ [Pytest determinístico: 0 tokens, execução em < 10s no CI]
               ─────────────────
```

- **Camada 1 (Tier 1 — Estático / 0 Tokens)**: Valida topologia de grafos, esquemas YAML, conformidade de seções contra templates canônicos (1-de-N), isolamento de dados de projetos locais e ausência de *dead-ends*.
- **Camada 2 (Tier 1.5 — Trajetórias & Contratos de Transição)**: Valida sequências completas de estados dos 5 Workflows Canônicos (R-050), detecção de deriva de intenção (R-042), ativação de Circuit Breakers (R-050.2) e propagação do `state_bag`.
- **Camada 3 (Tier 2 — Simulação Orientada a Cenários)**: Avaliação de interações reais via modelo SLM (`Gemini 3.8 Flash`) disparada sob demanda por cenário unitário (anti-decaimento de contexto).

---

## 2. Mapa dos Módulos de Teste

A suíte de testes reside em `tests/` e divide-se em 6 domínios especializados:

```
tests/
├── governance_audit/              # Auditoria estática de smells, templates e isolamento
│   ├── test_governance_smells.py
│   ├── test_local_project_isolation.py
│   ├── test_template_sections.py
│   └── test_router_agents.py
│
├── operational_flow/              # Workflows operacionais (R-050), trajetórias e simulador
│   ├── casos-workflows.yaml       # Catálogo declarativo de cenários E2E
│   ├── test_operational_workflows.py
│   ├── test_workflow_trajectories.py
│   └── workflow_eval_simulator.py  # CLI de avaliação e métricas de cobertura
│
├── routing_gate/                  # Quality gate de roteamento do agent-router
│   └── test_routing_quality_gate.py
│
├── code-summarizer/               # Extração AST, segurança e orquestração do summarizer
│   ├── test_extract_fidelidade.py
│   ├── test_extract_seguranca.py
│   ├── test_orquestracao_contrato.py
│   ├── test_custo_contrato.py
│   └── test_pending_suites.py
│
├── codegraph_visualizer/          # Contratos OpenAPI/AsyncAPI e métricas de grafo
│   ├── test_contract_parser.py
│   ├── test_diff_checker.py
│   ├── test_metrics_calculator.py
│   └── test_template_bundler.py
│
└── context_insight_visualizer/    # Telemetria, invocações e hooks declarativos
    └── test_agent_invocations.py
```

---

## 3. Detalhamento Arquivo por Arquivo

Abaixo detalha-se o escopo de cobertura e a importância crítica de cada arquivo de teste para a estabilidade do sistema.

### 3.1. Governança e Auditoria Estática (`tests/governance_audit/`)

#### `test_governance_smells.py`
- **O que cobre**: Implementação estática determinística dos 17 smells de governança catalogados em `governance-audit-patterns/SKILL.md`:
  - **Smell 2.2**: Integridade de frontmatter obrigatório (`name`, `description`, `tools`, `run_subagent` por R-042).
  - **Smell 2.6 / 2.14**: Ausência de paths absolutos locais em arquivos commitados (R-044).
  - **Smell 2.7 / 2.7.1**: Matriz de ferramentas por papel (agents read-only proibidos de possuir ferramentas mutativas de escrita; uso de terminal exigindo `terminal-governance` por R-049; context-mode exigindo skill por R-008).
  - **Smell 2.8**: Protocolo de batching R-046 em agents mutativos.
  - **Smell 2.11**: Teto de 8 linhas para código inline executável em skills (R-026).
  - **Smell 2.15 / 2.16 / 2.17 / 2.20**: Prevenção de acoplamento rígido de range normativo (herança aberta de CLAUDE.md), desativação de pager no Git (`--no-pager` por R-035) e regra de delegação plana no router (R-047).
- **Importância para a qualidade**: Atua como o **escudo primário de governança**. Impede que agentes degradem seus contratos operacionais ou acumulem ferramentas perigosas (como permissão de escrita em agentes de auditoria), eliminando regressões antes da revisão humana.

#### `test_local_project_isolation.py`
- **O que cobre**: Isolamento estrito de projetos locais e políticas de privacidade corporativa (R-038 e R-043/R-044):
  - Garante que arquivos rastreados no Git nunca mencionem caminhos reais de máquina ou nomes de projetos do usuário (exige placeholders genéricos como `[PROJETO-ALVO]`).
  - Garante que `catalog.local.yaml` permaneça no `.gitignore` e que `docs/ai-context/catalog.yaml` contenha zero entradas na chave `projetos:`.
- **Importância para a qualidade**: **Segurança da Informação e Portabilidade**. Garante que o repositório de governança possa ser compartilhado publicamente ou entre equipes corporativas sem vazar identificadores, caminhos locais ou estruturas de código proprietárias do desenvolvedor.

#### `test_template_sections.py`
- **O que cobre**: Validação de conformidade estrutural contra os templates canônicos (Smells 2.9, 2.10 e 2.11):
  - **Disjunção 1-de-N**: Valida se cada artefato cumpre as seções estruturais de **ao menos um template** de seu contexto (ex.: agents atendendo a `operational-agent.md`, `research-agent.md` ou `agent-template.md`).
  - Extração dinâmica de templates em `.github/agents/templates/`, `.github/skills/templates/` e `.github/prompts/templates/`.
  - Normalização semântica de cabeçalhos H2 para validar conceitos essenciais (`escopo`, `workflow`, `contrato_saida`, `retorno_router`, `seguranca`, `checklist`, `combina_com`).
- **Importância para a qualidade**: **Padronização Instrucional**. Garante que novos agentes, prompts e skills criados pela equipe ou por automações (`governance-factory`) sigam rigorosamente a arquitetura de *Progressive Disclosure* da literatura 2026, evitando prompts caóticos ou agentes sem limites negativos de atuação.

#### `test_router_agents.py`
- **O que cobre**: Validação especializada para os 6 agents com perfil de Router / Supervisor (`agent-router`, `angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `database-router`):
  - Presença das 6 seções obrigatórias (`CRÍTICO: ESCOPO DE ROTEAMENTO`, `Regras Herdadas`, `Skills Associadas`, `Decision Tree`, `Formato de Saída`, `Retorno ao Router`).
  - Árvore de decisão em formato estruturado com bifurcações (`├─`, `└─`, `->`).
  - Menor privilégio: presença compulsória de `run_subagent` e proibição absoluta de ferramentas mutativas (`create_file`, `insert_edit_into_file`, `replace_string_in_file`).
  - Conformidade direta dos supervisores de domínio com `router-agent.md`.
- **Importância para a qualidade**: **Confiabilidade de Roteamento**. Routers são a espinha dorsal de orquestração; um bug em um router trava ou desvia o fluxo de desenvolvimento de todo o domínio. Este teste assegura que nenhum router usurpe o papel de executor ou omita rotas de especialistas.

---

### 3.2. Fluxo Operacional e Trajetórias (`tests/operational_flow/`)

#### `test_operational_workflows.py`
- **O que cobre**: Consistência sistêmica e integridade conceitual dos workflows canônicos (R-050):
  - Validação da sintaxe e renderização dos diagramas Mermaid no `README.md`.
  - Validação dos Golden Paths operacionais (ex.: `prompt-structuring` após router, `code-knowledge-graph` obrigatório em refatorações, `deep-search` obrigatório na criação de artefatos).
  - Presença dos 5 workflows em `workflows.md` e `routing-graph.yaml`.
  - Schema v1.3 de handoff (`workflow_tracking`, `projeto_alvo`, `chaining`).
- **Importância para a qualidade**: **Prevenção de Becos Sem Saída (Anti-Dead-End)**. Garante que os fluxos declarados na documentação e no grafo de roteamento possuam correspondência real no código e que nenhum agente aponte para um sucessor inexistente.

#### `test_workflow_trajectories.py`
- **O que cobre**: Validação ponta a ponta (E2E) das trajetórias sequenciais declaradas em `casos-workflows.yaml`:
  - Execução dos 5 workflows canônicos (`BUG-FIX`, `REFACTORING`, `TECHNICAL-ANALYSIS`, `FEATURE-DEVELOPMENT`, `GOVERNANCE-MAINTENANCE`).
  - Invariantes de cada etapa: isolamento de ferramentas (etapas de triagem e review sem mutação direta) e verificação do banner universal de fluxo.
  - Cenários de borda:
    - **Deriva de Intenção (R-042)**: detecção de mudança de stack multi-turno e retorno ao router raiz.
    - **Circuit Breaker (R-050.2)**: interrupção forçada após 3 falhas consecutivas de regressão.
    - **Fast-Chaining (R-050.1)**: transferência direta de contexto entre workflows sem triagem redundante.
  - Quality gates numéricos de cobertura mínima de workflows e estados.
- **Importância para a qualidade**: **Garantia de Comportamento Sistêmico**. Simula a experiência real de ponta a ponta que o desenvolvedor vivencia no chat, verificando se os agentes colaboram em cadeia sem perder o contexto ou quebrar as regras de segurança.

#### `workflow_eval_simulator.py`
- **O que cobre**: Motor executivo em Python (CLI) que implementa:
  - Validação estática de trajetórias em lote com emissão de relatórios formatados em console ou JSON.
  - Cálculo analítico das 5 dimensões de cobertura de workflows contra o grafo.
  - Ponto de integração para execução de simulações com o modelo `Gemini 3.8 Flash`.
- **Importância para a qualidade**: **Observabilidade e Diagnóstico Rápido**. Permite aos engenheiros e ao CI/CD inspecionar a saúde dos fluxos em milissegundos sem depender de sessões manuais de chat.

---

### 3.3. Roteamento Central (`tests/routing_gate/`)

#### `test_routing_quality_gate.py`
- **O que cobre**: O portão de qualidade do `@agent-router`:
  - Validação de esquema do grafo `routing-graph.yaml` (nós, arestas, fallbacks).
  - Execução da suíte de regressão de roteamento contra `casos-roteamento.yaml` (casos canônicos, ambíguos e de borda).
  - Verificação de thresholds de confiança mínima por rota.
  - Prevenção de loops e verificação de circuit breakers de roteamento.
- **Importância para a qualidade**: **Assertividade de Ponto de Entrada**. O router é o portão de entrada de 100% das mensagens do usuário (R-037). Este teste garante que mudanças em prompts ou regras não causem desvios de rota (*routing drift*) ou loops infinitos.

---

### 3.4. Especialistas e Ferramentas Auxiliares

#### `tests/code-summarizer/`
- **Arquivos**: `test_extract_fidelidade.py`, `test_extract_seguranca.py`, `test_orquestracao_contrato.py`, `test_custo_contrato.py`, `test_pending_suites.py`.
- **O que cobrem**: O motor determinístico de sumarização de código (RF-001/RF-002):
  - Fidelidade de parsing AST em Java, TypeScript, Python e SQL.
  - Prevenção absoluta de vazamento de segredos/tokens no resumo (tolerância zero — RNF-005).
  - Máquina de estados de custo (cache FTS5 → determinístico AST → fallback LLM).
- **Importância para a qualidade**: **Economia de Contexto e Segurança**. Assegura que o resumidor de código entregue resumos estruturados de altíssima fidelidade sem gastar tokens caros de LLM e sem vazar credenciais no contexto do chat.

#### `tests/codegraph_visualizer/`
- **Arquivos**: `test_contract_parser.py`, `test_diff_checker.py`, `test_metrics_calculator.py`, `test_template_bundler.py`.
- **O que cobrem**: O motor de visualização e análise de grafos de código:
  - Parsing de contratos OpenAPI e AsyncAPI.
  - Detecção de quebra de fronteiras arquiteturais entre módulos.
  - Cálculo de métricas de acoplamento e detecção de ciclos de dependência.
  - Geração de relatórios HTML autocontidos.
- **Importância para a qualidade**: **Integridade Arquitetural**. Garante que o visualizador de grafos forneça evidências matemáticas confiáveis sobre acoplamento e contratos de API para o `@code-knowledge-graph`.

#### `tests/context_insight_visualizer/`
- **Arquivos**: `test_agent_invocations.py`.
- **O que cobre**: Observabilidade e telemetria dos agents:
  - Rastreamento de chamadas de subagents via hooks declarativos.
  - Extração de métricas de uso de ferramentas e latência.
- **Importância para a qualidade**: **Rastreabilidade Operacional**. Garante que o painel de insights receba dados fidedignos sobre quais agentes foram disparados e como as sessões estão evoluindo.

---

## 4. As 5 Dimensões de Cobertura de Workflows (MAS)

Em sistemas multi-agentes, a cobertura é monitorada através de cinco dimensões complementares:

| Dimensão | O que mede | Status Atual | Meta Mínima (Gate) |
|---|---|:---:|:---:|
| **1. Workflow-Level Coverage** | Workflows canônicos com ao menos 1 cenário E2E | **5/5 (100%)** | 100% |
| **2. State & Stage Coverage** | Etapas finitas visitadas nas trajetórias | **22/23 (95.7%)** | ≥ 85% |
| **3. Transition / Edge Coverage** | Pares de delegação únicos $(Agente_A \to Agente_B)$ validados | **17 transições** | ≥ 10 transições |
| **4. Agent Participation** | Agentes do catálogo exercitados ativamente | **18 agentes** | ≥ 15 agentes |
| **5. Safety & Edge Case Coverage** | Modos de falha, drift (R-042) e circuit breakers testados | **4/4 (100%)** | 100% |

### Como inspecionar a cobertura via CLI:
```bash
# Exibir o painel de cobertura formatado
python tests/operational_flow/workflow_eval_simulator.py --coverage

# Exportar métricas estruturadas em JSON (para pipelines de CI/CD)
python tests/operational_flow/workflow_eval_simulator.py --coverage --json
```

---

## 5. Guia de Execução

### Pré-requisitos
```bash
python -m pip install -r tests/requirements.txt
```

### Comandos de Execução Recomendados

```bash
# 1. Executar a suíte completa (108 testes, execução em ~7s)
python -m pytest tests/ -v

# 2. Executar apenas os testes de governança e templates
python -m pytest tests/governance_audit/ -v

# 3. Executar apenas a validação de trajetórias de workflows
python -m pytest tests/operational_flow/ -v

# 4. Executar apenas o quality gate de roteamento do agent-router
python -m pytest tests/routing_gate/ -v
```

### Integração Contínua (CI/CD)

Toda a suíte de testes de governança e workflows é executada automaticamente pelo GitHub Actions em:
`.github/workflows/routing-quality-gate.yml`

Qualquer falha estrutural, regressão de rotas, quebra de seções de template ou violação de isolamento de projetos locais **bloqueia imediatamente o merge do Pull Request**.

