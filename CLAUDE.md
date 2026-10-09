# CLAUDE.md — governanca-ai-reutilizavel

## 1) Objetivo
Prover ecossistema de governança de IA reutilizável, modular e auditável via Copilot e Claude, aplicando arquitetura de agentes especializados, skills operacionais desacopladas e orquestração determinística.

## 2) Hierarquia de Instruções
1. **Instruções de Sistema** (runtime/plataforma)
2. **`CLAUDE.md`** (regras normativas globais inegociáveis — single source of truth)
3. **`.github/copilot-instructions.md`** (diretrizes operacionais e de runtime do Copilot)
4. **`.github/agents/*.agent.md`** (contratos operacionais de agentes)
5. **`.github/skills/*/SKILL.md`** (procedimentos e playbooks executáveis)
6. **`.github/instructions/*.instructions.md`** (adapters de ecossistema/linguagem)
7. **`.github/instructions/local/*.instructions.md`** (overlay local de projeto — gitignored)

## 3) Regras Normativas (R-001..R-067)
Índice normativo condensado. O detalhamento operacional, checklists e anti-padrões residem nas skills canônicas vinculadas:

- **R-001**: Escopo restrito exclusivamente ao solicitado pelo usuário ou plano aprovado. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-002**: Mudança mínima, atômica, reversível e rastreável. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-003**: Sem duplicação — regras globais residem em `CLAUDE.md`; `.github/*` apenas referencia. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-004**: Rastreabilidade com caminhos exatos e símbolos tocados. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-005**: Não inventar catálogo — referencie apenas agents e skills existentes em `catalog.yaml` e `.index.json`. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-006**: Pré-condições do Roteador — vide [`agent-router.agent.md`](.github/agents/agent-router.agent.md) e [`handoff-governance`](.github/skills/handoff-governance/SKILL.md).
- **R-007**: Decisões explícitas registradas em bullets curtos. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-008**: Execução obrigatória via context-mode — Think in Code & Zero-Noise Test Policy: O uso de `context-mode` MCP (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_search`, `ctx_index`) é 100% OBRIGATÓRIO para leitura, modificação e criação de arquivos; ferramentas nativas de editor são estritamente proibidas quando o context-mode estiver disponível (rebaixadas a fallback exclusivo de indisponibilidade). ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-009**: Sem arquivos autônomos sem solicitação explícita ou padrão governado. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-010**: Segurança estrita — nunca expor credenciais, tokens ou dados sensíveis. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-011**: Sem overengineering — implementar o estritamente necessário para a fase atual. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-012**: Clarificação progressiva com o usuário diante de incertezas de escopo. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-013**: PT-BR operacional na documentação de governança e respostas. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-014**: Um objetivo por arquivo, com responsabilidade única e coesa. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-015**: Atualização atômica de catálogo e dependências ao alterar artefatos de governança. ([governance-factory-patterns](.github/skills/governance-factory-patterns/SKILL.md))
- **R-016**: Evidência objetiva e reproduzível com comandos e arquivos tocados. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-017**: PT-BR com ortografia e acentuação culta em arquivos `.md`. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-018**: Planejamento paralelo para etapas independentes e seguras. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-019**: Busca web proativa com ctx-cache em incertezas técnicas externas. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-020**: Falha compacta em 3 linhas: Causa / Local / Ação corretiva. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-021**: Model Routing Signal — emissão obrigatória de sinal visual de modelo recomendado no topo. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-021.1**: Sinal Adicional de Fan-Out — Model Routing por Volume de Alvos (≥ 10 alvos/arquivos/operações homogêneas). ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-022**: Auto-recuperação do Context Mode com 1 retry antes de erro ou fallback. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-023**: MCP Trust Allowlist restrita a servidores homologados. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-024**: MCP Least-Tools — manter ativas apenas as ferramentas necessárias à tarefa. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-025**: MCP Prompt Budget — redução de tools ativas em caso de pressão de tokens. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-026**: Sem código inline executável de aplicação em agents/skills/prompts. ([governance-factory-patterns](.github/skills/governance-factory-patterns/SKILL.md))
- **R-027**: Clarificação Obrigatória via ask_questions frente a qualquer ambiguidade de requisitos. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-028**: Estrutura de Resposta Code Assist Standard com resumo padronizado em 5 seções. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-029**: Postura Senior Engineer: concisão, bullets, tabelas e código limpo. ([agent-contracts](.github/skills/agent-contracts/SKILL.md))
- **R-030**: Checkpoint obrigatório por fase com parada para validação humana. ([plan-conformance-patterns](.github/skills/plan-conformance-patterns/SKILL.md))
- **R-031**: Plano Auto-Implementável — Zero-Interrupção em planos aprovados. ([plan-conformance-patterns](.github/skills/plan-conformance-patterns/SKILL.md))
- **R-032**: Nomeação de documentação em `kebab-case.md`. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-033**: Sincronização Automática de Documentação Viva & Proibição de Documentação Especulativa. ([documentation-writing-patterns](.github/skills/documentation-writing-patterns/SKILL.md))
- **R-034**: Health Check de Binding Context obrigatório no primeiro turno. ([handoff-governance](.github/skills/handoff-governance/SKILL.md) / [.github/instructions/README.md](.github/instructions/README.md))
- **R-035**: Terminal sem paginação interativa — Zero Pager Bloqueante (`--no-pager`). ([terminal-governance](.github/skills/terminal-governance/SKILL.md))
- **R-036**: Identificador Normativo Reservado / Rastreabilidade Histórica. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-037**: Ponto de Entrada Obrigatório — Agent Router First: toda solicitação inicia em `@agent-router`. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-038**: Genericidade Obrigatória em Governança — desacoplamento de projetos e stacks ([governance-factory-patterns § 3.5](.github/skills/governance-factory-patterns/SKILL.md)).
- **R-039**: Diagramas em Markdown exclusivamente via blocos Mermaid válidos. ([mermaid-diagrams](.github/skills/mermaid-diagrams/SKILL.md))
- **R-040**: Grafo de Roteamento como Fonte de Verdade estrutural em `routing-graph.yaml`. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-041**: Exceção de Loop Controlado no refinamento de prompt (`prompt-structuring`, máx. 5 voltas). ([prompt-engineering-patterns](.github/skills/prompt-engineering-patterns/SKILL.md))
- **R-042**: Re-triagem Obrigatória por Turno — Anti Sticky-Session: todo turno reavalia o agent ativo e redireciona ao router se houver deriva de intenção; mesmo quando não há agent ativo residente (ou ausência de agent ativo), aplica-se R-063. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-043**: Local Overlay Pattern — isolamento total de adapters locais em `.github/instructions/local/` (gitignored). ([.github/instructions/README.md](.github/instructions/README.md))
- **R-044**: Anonimização Obrigatória de Evidência de Análise Real — proibido persistir dados reais em arquivos commitáveis ([governance-factory-patterns § 3.6](.github/skills/governance-factory-patterns/SKILL.md)).
- **R-045**: Exclusividade do Motor de Grafo — `@codegraph-engine` (RNF-004) para CLI optave/codegraph e artefatos de grafo. ([codegraph-engine](.github/agents/codegraph-engine.agent.md) / [codegraph-optave-usage](.github/skills/codegraph-optave-usage/SKILL.md))
- **R-046**: Single-Turn Batching Obrigatório — Economia de Tokens e Créditos: alterações multi-arquivo consolidadas no mesmo turno (Single-Turn MCP Batching com `ctx_batch_execute` ou script iterativo em `ctx_execute`). ([efficient-batch-code-modification](.github/skills/efficient-batch-code-modification/SKILL.md))
- **R-047**: Fluxo Contínuo Sem Becos Sem Saída — respostas propositivas; prevê a exceção de Delegação Plana para routers. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-048**: Proibição de Leitura Integral de Arquivos Grandes — Leitura Cirúrgica Obrigatória via `ctx_execute`/`grep_search`. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-049**: Vinculação Compulsória de Governança de Terminal em Tooling & Zero-Noise Test Execution. ([terminal-governance](.github/skills/terminal-governance/SKILL.md))
- **R-050**: Workflows Operacionais Determinísticos — Pipelines de Estado Finito descritos em `workflows.md`, com suporte a Fast-Path determinístico (ex.: `WORKFLOW-BUG-FIX`, `WORKFLOW-FEATURE`) e controle de transições. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-050.4**: Loop de Revisão de Qualidade (Quality Review Loop) — ciclo avaliador-otimizador com teto rígido de 3 iterações antes de promover mudanças em workflows aplicáveis. ([workflows.md § 1.5](.github/agents/workflows.md#15-loop-de-revisão-de-qualidade) / [handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-051**: Proteção Anti-Corrupção em Edição de Arquivo Único Grande/Estruturado e Markdown com Âncoras Repetidas: verificação obrigatória pré e pós-edição (all-or-nothing). ([efficient-batch-code-modification](.github/skills/efficient-batch-code-modification/SKILL.md))
- **R-052**: Reset Mandatório pós-Conclusão de Workflow / Post-Task Router Handback — Anti Sticky-Agent: ao atingir o estado final do workflow (conclusao_de_workflow_anterior), devolver controle ao `@agent-router`. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-053**: Execution Gate Independente de Modelo — Banner-Antes-de-Mutação mandatório antes de modificar código em workflows. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-054**: Governança Estrita de Routers — Tooling Least Privilege, Zero Discovery e Delegação Plana Obrigatória. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-055**: Portão de Reúso e Generalização Sistêmica em Governança — Anti-Silo Fix: responder compulsoriamente a Q1 (peers), Q2 (templates canônicos) e Q3 (testes no pytest). ([governance-factory-patterns § 3.2](.github/skills/governance-factory-patterns/SKILL.md))
- **R-056**: Precedência Mandatória e 100% Obrigatória de Context Mode em Leitura e Modificação de Arquivos — Anti-Editor Tool Sprawl: ferramentas de editor rebaixadas a fallback exclusivo de indisponibilidade. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-057**: Proibição Estrita de Terceirização de Edição Manual ao Usuário por Agentes Analíticos / Read-Only — Anti-Manual User Delegation & Automated Workflow Continuity: é vedado transferir edição manual ao usuário. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-058**: Blueprint Técnico e Decomposição Obrigatórios em Features Complexas — Anti-Premature Implementation Bypass & Anti-Gap Dumping: geração obrigatória de Blueprint Técnico antes de codificar. ([task-decomposition-patterns](.github/skills/task-decomposition-patterns/SKILL.md))
- **R-059**: Regra do Limiar >= 2 e Protocolo Plan-Then-Batch Global — Anti-MCP Tool Chaining (Smell 2.26) & Anti-Miopia Reativa (Smell 2.13): ao atingir o Limiar >= 2 alvos ou comandos, é vedado o chaining sequencial no chat; use o Protocolo Plan-Then-Batch (etapas: ENUMERAR todos os arquivos/comandos, CONSOLIDAR em `ctx_batch_execute` ou script iterativo `ctx_execute`, DESPACHAR & VALIDAR com `get_errors` ao final). Comandos curtos do usuário ("prosseguir", "continue") mantêm o rigor do protocolo. Circuit Breaker de Tool-Chaining Sequencial interrompe chamadas redundantes. ([context-mode](.github/skills/context-mode/SKILL.md) / [efficient-batch-code-modification](.github/skills/efficient-batch-code-modification/SKILL.md))
- **R-060**: Teto Rígido de Tool Turns (≤ 5), Warm Start Compulsório e Consolidação de Queries em Lote — Anti-Token Debt & Anti-Turn Chaining: orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução; inicialização silenciosa de bases pré-computadas (Warm Start) no primeiro comando e agrupamento de buscas em batch query com truncamento na borda. ([context-mode](.github/skills/context-mode/SKILL.md))
- **R-061**: Diagnóstico de Harness-vs-Modelo e Poda Anti-Bloat de Instrução — Harness Engineering: heurísticas de diagnóstico harness-antes-de-modelo, zona inteligente (~100k tokens), minimalismo de instrução-raiz e poda cirúrgica ("delete e observe"). ([harness-engineering-patterns](.github/skills/harness-engineering-patterns/SKILL.md))
- **R-062**: Zero Impersonation pelo Orquestrador Raiz — Anti Root-Agent-Impersonation: É terminantemente proibido ao modelo do turno raiz se autodenominar ou assinar como qualquer especialista antes de delegar via `run_subagent`; cabe ao Orquestrador Raiz exclusivamente invocar o router. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-063**: Zero Execução Direta pelo Orquestrador Raiz sem Router — Anti Silent Bypass: É terminantemente proibido ao modelo do turno raiz executar diretamente tarefas técnicas sem antes invocar o router via `run_subagent`; o Orquestrador Raiz deve sempre invocar o router para triagem. ([handoff-governance](.github/skills/handoff-governance/SKILL.md))
- **R-064**: Duplo Gate Documental de Planejamento e Implementação Universal — Persistência Versionada + Aprovação Humana Prévia por Fase; nenhum codificador altera código sem `plan_ref` aprovado (Tiers Full/Light via `<stack>-arch-advisor`, vide [invariantes-e-protocolos.md § 10](.github/agents/workflows/invariantes-e-protocolos.md#10-r-064--duplo-gate-documental-de-planejamento-e-implementação-universal)). ([plan-conformance-patterns](.github/skills/plan-conformance-patterns/SKILL.md))
- **R-065**: Guard de Severidade Arquitetural no Loop de Qualidade — achados bloqueantes impedem promoção de fase em workflows de implementação. ([workflows.md § 1.5](.github/agents/workflows.md#15-loop-de-revisão-de-qualidade) / [agent-safety-guardrails](.github/skills/agent-safety-guardrails/SKILL.md))
- **R-066**: Progressive Disclosure Compulsória de `source_docs:` — Anti Context Bloat Inicial / Full-Load vs. Lazy-Load: arquivos de governança volumosos (> 300 linhas) devem ser declarados exclusivamente sob `source_docs_lazy:`, proibida a leitura integral via `read_file`. ([governance-audit-patterns](.github/skills/governance-audit-patterns/SKILL.md))
- **R-067**: Protocolo de Avaliação de Pertinência de Importação de Skills — Skill Import Viability & Solution Alternative Gate: em caso de não pertinência na importação de skills externas, deve reportar impacto negativo e propor solução alternativa viável. ([governance-factory-patterns § 3.4](.github/skills/governance-factory-patterns/SKILL.md))

### 3.1) Regra de Autoria de Agents
Ao criar novos agents, respeitar o teto estrito de prompt tokens, o padrão canônico de frontmatter e os templates governados em `.github/agents/templates/` (R-015, R-038).

## 4) Fluxo Operacional Base
1. **Entrada Obrigatória**: Inicia em `@agent-router` (R-037), que realiza Health Check de binding (R-034) e avalia o grafo de roteamento.
2. **Refinamento**: Se ambíguo ou aberto, encaminha ao `prompt-structuring` (R-041) para clarificação antes do despacho.
3. **Despacho Direto**: O router despacha o especialista downstream apropriado em nível plano (Flat Delegation, R-047/R-054).
4. **Execução em Workflow**: Execuções técnicas seguem os Workflows Canônicos formalizados em `workflows.md` (R-050) com verificação em duplo gate (R-064).
5. **Quality Review Loop**: Toda mutação passa por gates estritos de testes, higiene e arquitetura (R-065).
6. **Handoff ou Conclusão**: Ao concluir o workflow, reset obrigatório devolvendo controle ao `@agent-router` (R-052). Derivas de intenção acionam re-triagem imediata (R-042).

## 5) Estrutura de Governança
- `.github/agents/` — Contratos de agentes especializados e sub-roteadores de domínio.
- `.github/skills/` — Procedimentos operacionais padronizados, regras de tooling e playbooks executáveis.
- `.github/prompts/` — Prompts reutilizáveis e comandos customizados (/implement, /refactor, /test-plan).
- `.github/instructions/` — Adapters de ecossistema e stack (compartilhados) e overlay local em `local/` (gitignored, R-043).
- `tools/` — Automação determinística e scripts de validação de conformidade estrutural.

## 6) Catálogo Canônico e Grafo de Roteamento
O catálogo de agentes e a topologia de roteamento são geridos como dados estruturados versionados, eliminando duplicações manuais:
- **Catálogo Estruturado de Agents**: Vide [`.github/agents/catalog.yaml`](.github/agents/catalog.yaml) (fonte única de verdade para metadados, modelos, ferramentas e descrições dos agents).
- **Grafo Estruturado de Roteamento**: Vide [`.github/agents/routing-graph.yaml`](.github/agents/routing-graph.yaml) (nós, arestas, condições e políticas de transição).
- **Índice Estruturado de Skills**: Vide [`.github/skills/.index.json`](.github/skills/.index.json).
- **Casos de Teste de Roteamento**: Vide [`.github/agents/evals/casos-roteamento.yaml`](.github/agents/evals/casos-roteamento.yaml).
- **Ferramentas de Automação Determinística**:
  - `tools/agent_protocol_sync/sync_execution_protocol.py` — Sincronização determinística do protocolo `<execution_protocol>` em lote (R-059/R-060).
  - `tools/agentcard_exporter/export_agentcards.py` — Validador e exportador de conformidade A2A AgentCard v1.0.0 (R-051).

## 7) Política de Mudança
1. **Alteração em Governança**: Atualize atomicamente catálogos, grafos e dependências cruzadas (R-015).
2. **Adição de Regra Normativa**: Regras globais entram exclusivamente neste arquivo sob o formato `- **R-xxx**: ...`, atualizando simultaneamente `.github/copilot-instructions.md`.
3. **Preservação de Genericidade**: Nenhuma regra ou documentação global pode referenciar projetos locais ou tecnologias exclusivas (R-038).

## 8) Definition of Done (Governança)
Toda entrega de governança é considerada concluída quando satisfaz:
- [ ] Diffs cirúrgicos aplicados via script no sandbox do `context-mode` (R-008 / R-046 / R-056).
- [ ] Checklist de Genericidade (R-038) cumprido: vide [governance-factory-patterns/SKILL.md § 3.5](.github/skills/governance-factory-patterns/SKILL.md).
- [ ] Checklist de Anonimização de Evidência Real (R-044) cumprido: vide [governance-factory-patterns/SKILL.md § 3.6](.github/skills/governance-factory-patterns/SKILL.md).
- [ ] Portão de Reúso Sistêmico (R-055 / Q1-Q2-Q3) avaliado e propagado para templates canônicos e artefatos análogos.
- [ ] Sincronização atômica (R-015) realizada em `catalog.yaml`, `routing-graph.yaml` e documentações conexas.
- [ ] Suíte de testes `pytest tests/governance_audit` executada com 100% de aprovação.
