# CHANGELOG — Deep Agents Copilot (Estrutura de Governança Genérica e Reutilizável)

Todas as mudanças significativas nesta base de governança são documentadas aqui.

Formato: [Semantic Versioning](https://semver.org/) | [Conventional Commits](https://www.conventionalcommits.org/)

---

## [2.34.0] — 2026-09-23

### Padronizado & Refatorado
- **Padronização Universal do Cabeçalho H1 (`# Perfil Operacional`) em 100% dos Agentes e Templates**:
  - **Eliminação de Inconsistência Estrutural e Duplicação de Nomes**: Unificação do H1 de todos os 86 arquivos de agents (`.github/agents/**/*.agent.md`) e dos 4 templates canônicos (`.github/agents/templates/*.md`) para a linha exata `# Perfil Operacional`.
  - **Single Source of Truth (SSOT) para Identificadores de Agentes**: O nome e identificador do agente reside agora EXCLUSIVAMENTE no campo `name: '...'` do frontmatter YAML, eliminando a duplicação nominal no corpo textual.
  - **Governança da Fábrica (R-055 Systemic Reuse Gate)**: Atualização de `.github/agents/governance-factory.agent.md` e `.github/skills/governance-factory-patterns/SKILL.md` estipulando `# Perfil Operacional` como regra inegociável na criaç��o e revisão de agentes.
  - **Guardrail Determinístico de Testes**: Implementada a suíte `tests/governance_audit/test_agent_headings_standardization.py` parametrizada sobre os 86 agents e 4 templates, garantindo que o H1 seja único, obrigatório e estritamente padronizado.
  - **Quality Gate**: 248/248 testes aprovados no pytest com 100% de sucesso.

## [2.33.2] — 2026-09-23

### Alterado (Consolidacao de Model Routing por Perfil de Agent)
- **Correcao de Drift de Deteccao (Transparencia)**: Auditoria inicial reportou 21 agents "sem modelo declarado" devido a regex sensivel a quebra de linha CRLF que falhou ao ler o frontmatter de `.agent.md`. Revalidacao confirmou que **100% dos 86 agents ja possuiam `model` declarado no proprio frontmatter** (fonte autoritativa); a tabela real de mudancas necessarias foi reduzida de 24 para **13 upgrades genuinos**.
- **Upgrade Gemini 3.8 Flash -> Claude Sonnet 5 (13 agents)**: Aplicado a agents cujo perfil exige julgamento de alto risco ou raciocinio multi-arquivo profundo, com evidencia de sessao real onde a versao economica nao capturou gaps criticos:
  - `agent-auditor` (auditoria meta-nivel do proprio catalogo de governanca).
  - `governance-factory` (design de novos artefatos de governanca, nao e batch mecanico).
  - `database-specialist` (migracoes/queries genericas de schema - mesmo risco de DDL dos especialistas Oracle/Informix).
  - `security-reviewer`, `compliance-guardrails`, `code-review`, `devops-engineer` (julgamento de severidade/risco).
  - `requirements-analyst` ja estava correto em Sonnet (nao alterado).
  - `debugger`, `business-rules-extractor`, `feature-planner`, `performance-agent` (raciocinio de causa raiz, nuance semantica e planejamento critico).
  - `oracle-migration-dev`, `informix-migration-dev` (correcao de drift: `catalog.yaml` ja indicava Claude Sonnet 5, mas o frontmatter `.agent.md` real estava em Gemini 3.8 Flash).
- **Sincronizacao Multi-Fonte**: Atualizados em lote via `ctx_execute` (all-or-nothing): 13 arquivos `.agent.md`, 3 entradas em `.github/agents/catalog.yaml` (`agent-auditor`, `database-specialist`, `governance-factory`), e 5 `.a2a/agentcards/*.json` correspondentes (`model_preferences.recommended_model`).
- **Estado Final do Ecossistema**: 30 agents em `Claude Sonnet 5` (antes: 17) / 56 agents em `Gemini 3.8 Flash` (antes: 69) - 100% sem drift entre `catalog.yaml` e `.agent.md`.
- **Gap Identificado (fora de escopo desta entrega)**: 21 agents (incluindo os 7 routers de dominio e agents mais recentes como `security-reviewer`, `debugger`, `feature-planner`) nao possuem entrada em `.a2a/agentcards/` nem em `catalog.yaml` - modelo e definido exclusivamente no frontmatter do proprio `.agent.md`. Recomenda-se rodar `agentcard_exporter` para fechar essa lacuna de sincronizacao em entrega futura.
- **Quality Gate**: 256/256 testes deterministicos aprovados (`tests/governance_audit/` + `tests/routing_gate/`).

## [2.33.1] — 2026-09-23

### Corrigido (Auto-Auditoria Pos-Implementacao de R-060)
- **Propagacao Sistemica de R-060 para 100% dos Agentes Executores (Gap Critico Corrigido)**:
  - **Gap Identificado**: A regra R-060 havia sido formalizada apenas em CLAUDE.md, copilot-instructions.md, agent-template.md e no agent code-knowledge-graph.agent.md, mas NAO havia sido propagada para os demais 76 agentes executores nao-roteadores, violando o requisito de solucao geral para todos os agents do projeto.
  - **Correcao Aplicada**: Propagacao em lote unico via ctx_batch_execute do bloco de Teto Rigido de Tool Turns (<= 5) e Warm Start Compulsorio no <execution_protocol> de 100% dos 77 agentes executores nao-roteadores (confirmado via teste determinístico test_all_non_router_agents_declare_r060_turn_budget).
- **Correcao de Corrupcao de Caracteres de Controle (BELL/BACKSPACE/FORMFEED) em Arquivos de Governanca**:
  - **Causa Raiz**: Sequencias de escape Python (\a, \b, \f) presentes em palavras como ask_questions, build-if-missing, batch_query e find_cycles foram interpretadas como caracteres de controle (BEL/BS/FF) pela camada de shell do sandbox durante a escrita em lote, corrompendo 7 arquivos normativos e reincidindo apos a propagacao em lote para os 76 agentes.
  - **Correcao Aplicada**: Substituicao sistematica dos caracteres de controle pelos textos originais em todos os arquivos afetados (CLAUDE.md, copilot-instructions.md, agent-template.md, code-knowledge-graph.agent.md, codegraph-optave-usage/SKILL.md, efficient-batch-code-modification/SKILL.md, CHANGELOG.md e nos 76 agentes executores), incluindo normalizacao de notacao matematica quebrada (O(N^2)) e remocao de blocos LaTeX brutos substituidos por notacao textual simples.
  - **Guardrail de Regressao**: Novo teste test_no_control_character_corruption_in_governance_files em tests/governance_audit/test_turn_budget_and_warm_start_governance.py varre 100% dos arquivos de governanca versionados contra reincidencia de corrupcao.
- **Quality Gate**: 165/165 testes deterministicos aprovados (tests/governance_audit/ + tests/routing_gate/), incluindo os 2 novos testes de guardrail (propagacao R-060 e anti-corrupcao).

## [2.33.0] — 2026-09-24

### Adicionado & Formalizado
- **Teto Rígido de Tool Turns (≤ 5), Warm Start Compulsório e Consolidação de Queries em Lote (R-060 / Anti-Token Debt)**:
  - **Mitigação da Dívida de Tokens Quadrática O(N^2)**: Introduzida a regra normativa **R-060** para eliminar sessões infladas por encadeamento de dezenas de turnos de ferramentas onde todo o histórico é reenviado recursivamente.
  - **Teto de 5 Tool Turns & Circuit Breaker no 4º Turno**: Limite rígido de 5 turnos de ferramentas para qualquer agente executor, com interrupção e condensação mandatória no 4º turno para prevenir loops investigativos redundantes.
  - **Warm Start Compulsório (Build-if-Missing)**: Obrigatoriedade de ferramentas e subsistemas locais baseados em índices (como .codegraph/graph.db) construírem ou validarem suas bases silenciosamente no comando inicial, vedando quebras por cold start que consumiam turnos de depuração do LLM.
  - **Consolidação de Queries & Edge Truncation**: Exigência de que consultas a múltiplos nós/símbolos sejam feitas via chamadas em lote (batch_query, ctx_batch_execute ou script SQLite em sandbox) com destilação semântica e truncamento na borda.
- **Atualização Sistêmica de Artefatos**:
  - CLAUDE.md: Adição de R-060 e atualização do índice normativo para R-001..R-060.
  - .github/copilot-instructions.md: Inclusão de R-059 e R-060 no corpo de regras e detalhamento de turn budgeting e warm start na Seção 2.1.
  - .github/agents/templates/agent-template.md: Incorporação do Teto Rígido de 5 turnos e Warm Start no bloco <execution_protocol>.
  - .github/skills/codegraph-optave-usage/SKILL.md: Formalização de Warm Start (build-if-missing), Batch Querying e Turn Budget ≤ 3 para o @code-knowledge-graph.
  - .github/skills/efficient-batch-code-modification/SKILL.md: Nova Seção 6 detalhando a matemática da dívida de tokens, destilação na borda e Circuit Breaker.
  - .github/agents/code-knowledge-graph.agent.md: Incorporação de salvaguardas de Warm Start e teto de turnos.

## [2.32.0] — 2026-09-24

### Adicionado & Formalizado
- **Universalização do Protocolo Plan-Then-Batch (Smell 2.26 / Smell 2.13 / R-059) em 100% dos Agentes Não-Routers**:
  - **Extensão Holística do Escopo**: Ampliação do protocolo para todos os 27 agentes analíticos, advisory, arquitetos, auditores, reviewers e especialistas restantes (totalizando 78 agentes não-routers no ecossistema).
  - **Saneamento Total de Editor Tools (R-056 / Smell 2.24)**: Remoção integral de `read_file`, `create_file`, `insert_edit_into_file` e `replace_string_in_file` de todos os frontmatters `tools:` e sub-catálogos de domínio.
  - **Conjunto Completo de Context-Mode Mandatório**: Inclusão garantida das 5 ferramentas context-mode (`context-mode/ctx_batch_execute`, `context-mode/ctx_execute`, `context-mode/ctx_execute_file`, `context-mode/ctx_index`, `context-mode/ctx_search`) em todos os agentes não-routers com escopo de arquivos.
  - **Salvaguarda Especializada para `@code-knowledge-graph`**: Exigência expressa de que qualquer inspeção multi-arquivo para extração ou análise comparativa DEVE compulsoriamente utilizar `ctx_batch_execute` ou script iterativo consolidado em sandbox antes de queries de grafo, eliminando chamadas sequenciais unitárias de `ctx_execute`.
- **Blindagem do Router contra Discovery de Modelos em Tempo de Execução (R-054 / Zero Discovery)**:
  - **Eliminação de Runtime Discovery**: Formalizada a proibição inegociável de o `@agent-router` e domain routers chamarem ferramentas de busca/leitura (`read_file`, `grep_search`, `file_search`, `list_dir`) em tempo de execução para inspecionar `catalog.yaml` ou `*.agent.md` em busca de modelos de subagentes delegados.
  - **Resolução Estática / Melhor Esforço**: Mapeamento modelo ↔ agent estabelecido como estático ou convencional (zero tool calls em runtime).
  - **Limpeza do Formato de Saída**: Remoção da menção `(.github/agents/catalog.yaml)` na linha informativa `[Model] Delegando para...` de todos os routers centrais, supervisores de domínio e templates para prevenir alucinações de busca pelo modelo.
- **Sincronização Atômica de Catálogos (R-015 / R-040)**:
  - Atualização com paridade estrita em `.github/agents/catalog.yaml` e nos 7 sub-catálogos hierárquicos de domínio (`backend/database`, `backend/ejb`, `backend/python`, `backend/spring-boot`, `backend/spring-reactive`, `backend/struts`, `frontend/angular`).
- **Quality Gates Determinísticos no Pytest (`tests/governance_audit/`)**:
  - Atualização e expansão de `test_context_mode_precedence_governance.py` com novas asserções cobrindo 100% dos 78 agentes não-routers quanto à ausência de editor tools, presença de todas as ferramentas context-mode, obrigatoriedade do bloco `<execution_protocol>`, salvaguarda específica do `@code-knowledge-graph` e salvaguarda do `@agent-router` contra discovery de modelos em runtime.

---

## [2.31.0] — 2026-09-24

### Adicionado & Formalizado
- **Instituição da Regra R-059, Regra do Limiar >= 2 e Protocolo Plan-Then-Batch (Smell 2.26 / Smell 2.13)**:
  - **Diagnóstico e Causa-Raiz**: Identificado que agents executores mantinham chamadas unitárias sequenciais de `ctx_execute` por alvo no chat (MCP Tool Chaining / Smell 2.26) em tarefas multi-arquivo ou regrediam para ferramentas nativas de editor (`read_file`, `create_file`, `insert_edit_into_file`) em prompts curtos do usuário ("prosseguir", "continue").
  - **Regra do Limiar >= 2 (inegociável)**: Se a tarefa exigir inspecionar, ler, comparar, editar ou executar >= 2 arquivos/comandos/alvos, é terminantemente proibido disparar `ctx_execute` isolado por alvo em turnos sucessivos; exige compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
  - **Protocolo Plan-Then-Batch**: Protocolo em 4 etapas (1. ENUMERAR, 2. CONSOLIDAR, 3. DESPACHAR, 4. Comandos curtos não suspendem a regra) formalizado globalmente em `CLAUDE.md` (R-059), `.github/copilot-instructions.md` § 2.1, `context-mode/SKILL.md` e `efficient-batch-code-modification/SKILL.md`.
  - **Saneamento de Frontmatter dos Agentes Executores (50 Agentes)**: Removidas as affordances de editor (`read_file`, `create_file`, `insert_edit_into_file`, `replace_string_in_file`) de 100% dos 50 agentes executores mutativos, assegurando a presença das 5 ferramentas context-mode (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_index`, `ctx_search`).
  - **Bloco `<execution_protocol>` Canônico**: Inserido bloco estruturado `<execution_protocol>` em 100% dos 50 agentes executores e nos templates operacionais (`operational-agent.md`, `agent-template.md`), tornando o protocolo Plan-Then-Batch contratual em cada especialista.
  - **Sincronização Atômica de Catálogos (R-015/R-040)**: `catalog.yaml` e todos os 7 sub-catálogos de domínio atualizados com paridade estrita nas ferramentas dos agentes executores.
  - **Quality Gate Determinístico Expandido**: `tests/governance_audit/test_context_mode_precedence_governance.py` expandido para validar a presença da Regra do Limiar >= 2, o protocolo Plan-Then-Batch, a ausência de ferramentas nativas de editor nos 50 executores e a presença do bloco `<execution_protocol>`.

---

## [2.30.0] — 2026-09-23

### Adicionado & Formalizado
- **Instituição da Regra R-058 e Invariante 20: Blueprint Técnico e Decomposição Obrigatórios em Features Complexas (Anti-Premature Implementation Bypass & Anti-Gap Dumping / Smell 2.27)**:
  - **Diagnóstico e Causa Raiz**: Identificado que o `@agent-router`, ao despachar novas funcionalidades de stack única (ex.: frontend com BaaS/Firestore) que envolviam novos schemas de persistência, máquinas de estados (3+ transições), concorrência e push notifications, bypassava prematuramente o `@tech-solution-architect` e o `@feature-planner`, despejando lacunas de arquitetura no handoff para o implementador de código resolver no improviso.
  - **Regra Normativa R-058**: Features que tocam novo schema de persistência, máquina de estados (3+ transições), transações/concorrência ou infra/push NUNCA podem ser despachadas diretamente para domain routers ou implementadores de código; exigem passagem compulsória pelo Estado 3 de `WORKFLOW-FEATURE-DEVELOPMENT` (`@tech-solution-architect`) com aprovação no Checkpoint 3b (`ask_questions`).
  - **Decomposição em Subtasks (`@feature-planner`)**: Features com 3 ou mais frentes interdependentes exigem decomposição formal em subtasks sequenciais `[S]` e paralelas `[P]` com Definition of Done granular, evitando improviso na ordem de execução.
  - **Proibição de Gap Dumping e Smell 2.27**: Veda expressamente ao roteador listar lacunas conceituais de schema/permissão em "Lacunas para handoff" para o desenvolvedor improvisar durante a codificação; havendo lacunas de arquitetura, o roteamento mandatório é para `@tech-solution-architect`.
  - **Quality Gate e Testes Determinísticos**: Criada a suíte `tests/governance_audit/test_architectural_blueprint_gate_governance.py` com 7 testes automatizados validando a conformidade em `CLAUDE.md`, `copilot-instructions.md`, `agent-router.agent.md`, `router-agent.md`, `workflows.md`, `routing-graph.yaml` e `governance-audit-patterns/SKILL.md`.
- **Instituição do 9º Workflow Canônico: `WORKFLOW-PROMPT-SYNTHESIS` e Comando Operacional `/craft-prompt` (R-050, R-041)**:
  - **Propósito**: Conduzir o refinamento estrutural de solicitações, mineração determinística de contexto no codebase e síntese de prompts canônicos encapsulados em blocos Markdown (`.md`) prontos para sessões limpas com Prompt Caching otimizado.
  - **Máquina de Estados de 5 Etapas**:
    - *Etapa 1*: Elicitação & Problem Space (`@requirements-analyst` para demandas de negócio / `@prompt-structuring` para tarefas técnicas).
    - *Etapa 2*: Context Grounding & AST Mining (`@code-knowledge-graph` via `run_subagent`).
    - *Etapa 3*: Mapeamento de Restrições e Não-Escopo (`@prompt-structuring` + R-046).
    - *Etapa 4*: Síntese Estruturada & Otimização de Caching (`@prompt-structuring`).
    - *Etapa 5*: Quality Gate & Emissão do Bloco Markdown (`@prompt-structuring`).
  - **Invariante 17 (Visibilidade Progressiva e Anti-Blackbox Execution)**: Veda entregas em caixa-preta; torna compulsória a renderização do Painel de Evidências por Etapa no chat antes do bloco final.
  - **Invariante 18 (Exclusividade do Motor de Grafo & Anti-Tool Chaining / R-045)**: Torna obrigatória a chamada de `@code-knowledge-graph` via `run_subagent` na Etapa 2, proibindo varreduras manuais `fs` no sandbox e MCP Tool Chaining sequencial (Smell 2.26).
  - **Invariante 19 (Interrupção por Ambiguidade & Anti-Alucinação / R-027)**: Proíbe alucinar regras de negócio; impõe parada obrigatória na Etapa 1 via `ask_questions` com opções estruturadas para o usuário definir premissas e regras de domínio.
  - **Prompt Operacional `/craft-prompt`**: Criado `.github/prompts/craft-prompt.prompt.md` e registrado em `.github/prompts/README.md`.
  - **Isolamento de Projetos Locais & Genericidade (R-038/R-043/R-044)**: Typed State Bag 100% genérico e nova asserção determinística `test_no_concrete_local_project_file_paths_in_governance_files` em `test_local_project_isolation.py`.
  - **Quality Gate e Testes Automatizados**: Suíte de testes expandida para **195 testes determinísticos (100% verdes)**, incluindo novos cenários em `casos-roteamento.yaml` (`canon-047`) e `casos-workflows.yaml` (`WF-PROMPT-001`).

---

## [2.29.0] — 2026-09-21

### Adicionado & Endurecido
- **Extensão Universal da Precedência Mandatória de Context-Mode e `ctx_batch_execute` a 100% dos Agentes e Prompts (R-008, R-056 / Smell 2.24, Smell 2.26)**:
  - **Diagnóstico e Eliminação de Gaps**: Identificado que 13 agentes não-roteadores (especialmente os `*-arch-advisor` de todas as stacks, `adr-sentinel`, `compliance-guardrails`, `ddd-bounded-context-mapper`, `devops-engineer`, `feature-planner`, `repo-hygiene-auditor`) e múltiplos prompts (`commit.prompt.md`, `review.prompt.md`, `eval-workflows.prompt.md`, `visualize-graph.prompt.md`) não possuíam `context-mode/ctx_batch_execute` ou as diretrizes mandatórias de precedência, induzindo o uso de dezenas de `read_file` e `grep_search` sequenciais no chat.
  - **Blindagem em 100% dos Agentes Não-Roteadores (78 Agentes)**:
    - Habilitadas compulsoriamente as ferramentas `'context-mode/ctx_execute'`, `'context-mode/ctx_batch_execute'` e `'context-mode/ctx_search'` em 100% dos 78 agentes não-roteadores do catálogo.
    - Inserida em 100% dos agentes a cláusula de Não-Escopo proibindo expressamente o uso de ferramentas nativas de editor (`read_file`, `insert_edit_into_file`, `replace_string_in_file`, `create_file`) e comandos de leitura em terminal quando `context-mode` estiver ativo, rebaixadas a fallback exclusivo de contingência.
    - Inserida a diretriz positiva exigindo inspeções e varreduras no sandbox com Single-Turn MCP Batching para zero desperdício de créditos.
  - **Blindagem de Prompts e Templates**:
    - Atualizados `commit.prompt.md`, `review.prompt.md`, `eval-workflows.prompt.md`, `visualize-graph.prompt.md`, `del-project-context.prompt.md` e os templates `research-agent.md` e `prompt-template.md` com as ferramentas MCP em lote e a regra mandatória de context-mode.
  - **Sincronização Atômica de Catálogos**:
    - Atualizados `catalog.yaml`, os 7 sub-catálogos locais (`angular-catalog.yaml`, `spring-boot-catalog.yaml`, `spring-reactive-catalog.yaml`, `python-catalog.yaml`, `struts-catalog.yaml`, `ejb-catalog.yaml`, `database-catalog.yaml`) e os agentcards A2A.
  - **Quality Gate e Testes Determinísticos (Q3)**:
    - Adicionados testes determinísticos em `tests/governance_audit/test_context_mode_precedence_governance.py` validando que 100% dos agentes não-roteadores possuem `ctx_batch_execute`, `ctx_execute` e declaram a proibição de editor tools. Total da suíte expandido para **192 testes automatizados (100% verdes)**.

---

## [2.28.0] — 2026-09-21

### Adicionado & Endurecido
- **Single-Turn MCP Batching Compulsório e Erradicação de MCP Tool Chaining Sequencial no Chat (R-008, R-046, R-056 / Smell 2.26)**:
  - **Diagnóstico e Causa Raiz**: Identificado que agentes operacionais e de preparação (como `pr-gatekeeper` e outros) incorriam no anti-padrão de disparar 10+ chamadas unitárias sequenciais de `ctx_execute` turno a turno no chat para analisar diffs, arquivos, branches e categorias, reenviando todo o histórico acumulado da conversa a cada turno e drenando créditos de IA desnecessariamente.
  - **Single-Turn MCP Batching Mandatório**: Instituída a regra normativa que exige que qualquer inspeção, levantamento ou mutação envolvendo múltiplos alvos seja consolidada em chamada única:
    - **Via A (`ctx_batch_execute`)**: Para múltiplos comandos shell/git e queries unificadas em uma única rodada de ferramenta.
    - **Via B (script consolidado em `ctx_execute`)**: Para múltiplos arquivos no filesystem processados em loop iterativo interno em processo único no sandbox, retornando um resumo agregado único.
    - **Proibição Absoluta**: Terminantemente vedado o MCP Tool Chaining sequencial no chat.
  - **Systemic Reuse Gate (R-055 / Q1, Q2, Q3)**:
    - **Q1 (Peers e Catálogos)**: Habilitado compulsoriamente `'context-mode/ctx_batch_execute'` em 100% dos agentes do catálogo que possuíam `context-mode/ctx_execute` (`code-knowledge-graph`, `code-review`, `code-style-enforcer`, `database-specialist`, `debugger`, `performance-agent`, `pr-gatekeeper`, `runtime-verifier`, `security-reviewer`), garantindo paridade total; sincronizado `catalog.yaml` para `runtime-verifier` e `pr-gatekeeper`; atualizado `pr-gatekeeper.agent.md` com as diretrizes consolidadas de batching pré-PR.
    - **Q2 (Templates Canônicos e Fábrica)**: Atualizados `agent-template.md`, `operational-agent.md` e `governance-factory.agent.md` com a cláusula de Single-Turn MCP Batching, proibição de encadeamento sequencial e verificação compulsória de `ctx_batch_execute` no checklist de novos agentes.
    - **Q3 (Testes Determinísticos no pytest)**: Adicionados 4 testes determinísticos em `tests/governance_audit/test_context_mode_precedence_governance.py` (`test_smell_2_26_documented_in_governance_audit_patterns`, `test_mcp_batch_execution_and_tool_chaining_prohibition_in_normative_docs`, `test_all_agents_with_ctx_execute_declare_ctx_batch_execute`, `test_catalog_yaml_declares_ctx_batch_execute_for_all_ctx_execute_agents`), atingindo 100% de aprovação (189/189 testes verdes).
  - **Catálogo de Smells de Governança**: Catalogado o **Smell 2.26** ("MCP Tool Chaining Sequencial no Chat / Omissão de ctx_batch_execute e Script Consolidado") em `.github/skills/governance-audit-patterns/SKILL.md` com severidade Bloqueador, critérios de detecção e remediação.
  - **Alinhamento Normativo**: Sincronizados `CLAUDE.md` (R-008, R-046, R-056), `.github/copilot-instructions.md` (Seção 2 e 2.1), `.github/skills/efficient-batch-code-modification/SKILL.md` e `.github/skills/context-mode/SKILL.md`.

---

## [2.27.0] — 2026-09-21

### Modificado & Endurecido
- **Blindagem Completa de Renderização de Blocos de Código e Formatação de PR no `pr-gatekeeper` e Prompts Correlatos (Anti-Fences-Corruption & Isolated Artifacts Blocks)**:
  - **Eliminação da Corrupção por Fences Aninhados**: Identificada e corrigida a causa raiz da quebra de renderização em visualizadores de markdown (fences de mesma contagem de backticks ````text```` / ````bash```` / ````markdown```` dentro de um outer codeblock global ````markdown```` que forçava os LLMs a emitir a resposta inteira encapsulada e causava truncamento prematuro de fences).
  - **Reestruturação Mandatória do Formato de Saída (5 Blocos Autocontidos)**:
    - Removido o outer block markdown que encapsulava o template de saída.
    - Estabelecida a entrega de 5 blocos copiáveis isolados e autocontidos:
      - **Bloco 1 (Mensagem de Commit)**: emitido em bloco ````text```` isolado (Formatos A e B).
      - **Bloco 2 (Comando Bash de Aplicação Manual)**: emitido em bloco ````bash```` isolado e autocontido com heredoc limpo (`git commit -F - << 'EOF' ... EOF`).
      - **Bloco 3 (Título do PR)**: emitido em bloco ````text```` isolado formatado em Conventional Commits (≤72 cols).
      - **Bloco 4 (Descrição Estruturada do PR)**: emitido em bloco delimitado estritamente por 4 backticks (` ``` ` + ` ` ) para cópia direta e sem quebras no GitHub, com instrução explícita para que comandos na seção "Como validar / testar" utilizem inline code (`pytest tests/modulo -v`).
      - **Bloco 5 (CHANGELOG.md)**: emitido em bloco ````diff```` isolado com a entrada semver sugerida.
  - **Guardrail Anti-Corrupção no CRÍTICO**: Adicionadas cláusulas no escopo crítico de `pr-gatekeeper.agent.md` proibindo incondicionalmente o encapsulamento de toda a resposta em markdown global e o aninhamento de fences de mesma quantidade de backticks.
  - **Systemic Reuse Gate (R-055 / Q1, Q2, Q3)**:
    - **Q1 (Peers e Prompts Correlatos)**: Propagadas as regras de isolamento dos 5 blocos e anti-corrupção para `.github/prompts/commit.prompt.md` (PASSO 5, checklist e regras de autonomia) e para `.github/skills/git-governance/SKILL.md` (§ 3 Pull Request Guidelines).
    - **Q2 (Templates Canônicos)**: Atualizados `.github/agents/templates/agent-template.md` e `.github/prompts/templates/prompt-template.md` com diretrizes explícitas de não-encapsulamento global e isolamento de artefatos.
    - **Q3 (Testes Determinísticos)**: Criada a suíte `tests/governance_audit/test_pr_gatekeeper_render_integrity.py` com 6 testes determinísticos validando o balanceamento de fences, ausência de outer fences no formato de saída, presença de guardrails anti-corrupção e paridade no prompt `/commit`.

---

## [2.26.0] — 2026-09-21

### Modificado & Endurecido
- **Blindagem Completa e Sistêmica de Precedência de Context-Mode em Todos os Agentes Mutadores (R-008, R-056 / Smell 2.24)**:
  - **Varredura Universal e Blindagem em Lote**: Aplicada a blindagem em 100% dos 49 agentes executores/mutadores do repositório em todas as stacks (`backend/spring-boot`, `backend/spring-reactive`, `backend/python`, `backend/struts`, `backend/ejb`, `backend/database`, `frontend/angular`, raiz).
  - **Cláusula de Proibição Incondicional (CRÍTICO / NÃO-ESCOPO)**: Inserida a proibição estrita de uso de ferramentas nativas de editor (`read_file`, `insert_edit_into_file`, `replace_string_in_file`, `create_file`) e de comandos de leitura/inspeção em terminal quando `context-mode` estiver disponível no ambiente, estabelecendo que o uso de `context-mode` (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_search`, `ctx_index`) é 100% OBRIGATÓRIO para ler e modificar arquivos (R-008 / R-056 / Smell 2.24).
  - **Diretriz Mandatória Positiva**: Inserida a obrigatoriedade de executar modificações e leituras compulsoriamente via script no sandbox do `context-mode` (`ctx_execute` / `ctx_execute_file`), rebaixando ferramentas manuais de editor a fallback exclusivo de contingência para indisponibilidade comprovada do servidor MCP.
  - **Alinhamento de Ferramentas e Skills**: Adicionado `'context-mode/ctx_execute'` em `binding-initializer` e `docs-engineer`, e declarada a skill `efficient-batch-code-modification` em `adapter-generator` e `binding-initializer`.
  - **Templates Canônicos e Fábrica**: Templates operacionais (`operational-agent.md`, `agent-template.md`) e `governance-factory.agent.md` atualizados com as cláusulas padronizadas e checklist de herança compulsória para novos agentes gerados.
  - **Qualidade e Não-Regressão**: Atualizado `tests/governance_audit/test_context_mode_precedence_governance.py` com o teste dinâmico e assertivo `test_all_mutating_agents_declare_r056_and_explicit_prohibition()` inspecionando todos os agentes mutadores do repositório, alcançando 100% de aprovação (179/179 testes verdes).

---

## [2.25.0] — 2026-09-20

### Modificado & Endurecido
- **Endurecimento da Precedência Mandatória de Context Mode (R-008 e R-056 / Smell 2.24 — 100% Context-Mode Obligation & Editor Tool Prohibition)**:
  - **Uso 100% Obrigatório do Context-Mode**: O uso de `context-mode` (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_index`, `ctx_search`) passa a ser **100% OBRIGATÓRIO** tanto para LEITURAS quanto para MODIFICAÇÃO/CRIAÇÃO de arquivos SEMPRE que a ferramenta context-mode estiver disponível no ambiente, eliminando a fragmentação de dezenas de tool calls no chat, prevenindo truncamentos e erradicando o vazamento de bytes para a janela de contexto.
  - **Proibição Estrita de Ferramentas Nativas de Editor e Terminal**: Ferramentas manuais de editor (`read_file`, `replace_string_in_file`, `insert_edit_into_file`, `create_file`) e comandos de leitura no terminal são **estritamente proibidos quando o context-mode estiver disponível**, sendo rebaixados a **fallback exclusivo** única e estritamente para quando o servidor MCP context-mode estiver comprovadamente indisponível ou desconectado.
  - **Alinhamento Normativo**: Atualizados `CLAUDE.md` (R-008, R-046, R-056) e `.github/copilot-instructions.md` (Seção 2 e Seção 2.1).
  - **Reestruturação de Skills de Governança**:
    - `.github/skills/efficient-batch-code-modification/SKILL.md`: Seção 0 e Seção 5 reestruturadas definindo Nível 1 como 100% Compulsório para context-mode e Nível 2 como Fallback Exclusivo de indisponibilidade de MCP.
    - `.github/skills/governance-audit-patterns/SKILL.md`: Smell 2.24 elevado para Bloqueador ao identificar uso indevido de editor tools ou omissão de precedência mandatória de context-mode.
  - **Systemic Reuse Gate (R-055 / Q1, Q2, Q3)**:
    - **Q1 (Impacto em Peers)**: Propagada a regra endurecida para `.github/agents/governance-maintainer.agent.md` e 7 agentes executores/fixers (`ejb-test-fixer`, `python-test-fixer`, `spring-boot-test-fixer`, `spring-reactive-test-fixer`, `struts-test-fixer`, `database-specialist`, `angular-test-fixer`).
    - **Q2 (Templates Canônicos)**: Atualizados `.github/agents/templates/operational-agent.md`, `.github/agents/templates/agent-template.md` e `.github/agents/governance-factory.agent.md`.
    - **Q3 (Testes Determinísticos)**: Ampliada a suíte `tests/governance_audit/test_context_mode_precedence_governance.py` com 7 novos testes determinísticos verdes cobrindo a proibição e fallback exclusivo.

---

## [2.24.0] — 2026-09-20

### Adicionado
- **Proibição Estrita de Terceirização de Edição Manual ao Usuário por Agentes Analíticos / Read-Only (R-057 / Smell 2.25 — Anti-Manual User Delegation & Automated Workflow Continuity)**:
  - Formalização da regra normativa **R-057** em `CLAUDE.md` e `.github/copilot-instructions.md`, vedando que agentes analíticos, supervisores, auditores e advisors sem ferramentas de mutação instruam o usuário a editar código manualmente sob pretexto de ausência de tools.
  - Catalogação do **Smell 2.25 (Terceirização Indevida de Edição ao Usuário por Agentes Analíticos / Read-Only / Dead-End Analysis)** em `.github/skills/governance-audit-patterns/SKILL.md`, classificado como **Bloqueador** por violar R-047 (Anti Beco Sem Saída).
  - Instituição do **Invariante 16** em `.github/agents/workflows.md` (Regras de Não-Desvio), blindando a transição automática da etapa diagnóstica/analítica para a etapa executora nos workflows operacionais (`WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, etc.).
  - Formalização da sub-seção 6.1 em `.github/skills/agent-contracts/SKILL.md` e anti-padrão na skill `.github/skills/handoff-governance/SKILL.md`.
  - Injeção da cláusula preventiva de não-escopo em templates canônicos (`research-agent.md`, `agent-template.md`, `router-agent.md`) e em 12 agentes analíticos canônicos (`agent-auditor`, `code-review`, `adr-sentinel`, `repo-hygiene-auditor`, `requirements-analyst`, `test-strategy`, `bug-triage`, `refactor-planner`, `runtime-verifier`, `deep-search`, `tech-solution-architect`, `ddd-bounded-context-mapper`).
  - Atualização do checklist de conformidade no `governance-factory.agent.md` para auditar a presença compulsória de R-057 em novos agentes analíticos.
  - Criação da suíte determinística de testes em `tests/governance_audit/test_anti_manual_user_delegation_governance.py` (7 novos testes verdes).

---

## [2.23.0] — 2026-09-19

### Adicionado
- **Consolidação Determinística dos Workflows de Resolução de Bugs e Refatoração Estrutural (`WORKFLOW-BUG-FIX` e `WORKFLOW-REFACTORING`)**:
  - **`WORKFLOW-BUG-FIX`**:
    - Formalização de RCA estruturado via 5 Whys ou Fishbone (Ishikawa), com regra estrita de *evidence before hypothesis* exigindo no mínimo 2 fontes independentes de evidência técnica observável (stack trace, runtime log, payload de rede, APM ou teste isolado).
    - Classificação compulsória e determinística entre falha `flaky` (instabilidade intermitente por concorrência/ambiente/poluição de estado) e `regressao_real` no Estado 1 e no baseline check.
    - Pré-requisito mandatório no Estado 3: declaração antecipada de `blast_radius_estimado` (callers e módulos afetados) e `rollback_plan` no `workflow_state` antes de autorizar qualquer diff cirúrgico.
    - Inclusão do **Mini Mutation-Check Proporcional ao Risco** no Estado 4 para erradicar falsos-verdes nos testes de regressão (injeção de 1 a 3 mutantes sintéticos que devem ser 100% eliminados pelo Red Test).
    - Instituição do **Observação Pós-Fix / Canary Gate** no Estado 5 para defeitos críticos (P0/P1, segurança, autenticação e integridade de dados) com métricas de telemetria e janela de observação definidas.
  - **`WORKFLOW-REFACTORING`**:
    - Formalização explícita de **Contract Testing (Pact-style / consumer-driven contract tests ou OpenAPI / JSON Schema Diff)** no gate de contratos (Sub-rotina 2a / Estado 2) sempre que a refatoração atingir APIs públicas ou interfaces consumidas por múltiplos módulos.
    - Instituição de **Camada de Redundância Proporcional ao Blast Radius** no Estado 5 para blast radius moderado ou alto, composta por: (1) **Auditoria Reversa de Símbolos** (`reverse_symbol_audit` via `@code-knowledge-graph`), (2) **Mini Mutation Gate** (`mini_mutation_gate` para testar a sensibilidade da suíte Golden Master) e (3) **Differential Replay Leve** (`differential_replay_leve` comparando snapshots de entrada e saída pré/pós refatoração).
    - Governança de Rollback fortalecida no Estado 5b com cálculo, registro e reporte quantitativo do **`blast_radius_revertido`** (nós Mikado revertidos, arquivos e callers restaurados) no `workflow_state`.
  - **Blindagem Sistêmica & R-055 (Q1/Q2/Q3)**:
    - Sincronização atômica em `workflows.md` (especificações de fluxo, State Bags tipados, diagramas Mermaid, Invariantes 14 e 15, e templates visuais anti-cegueira).
    - Sincronização estrutural em `routing-graph.yaml` (metadados estruturais de RCA, blast radius, mini mutation, contract testing, redundância e rollback).
    - Expansão da suíte de testes determinísticos em `tests/operational_flow/test_operational_workflows.py`, adicionando validações contratuais e novo teste `test_workflow_bug_fix_and_refactoring_rigor_and_governance_parity`.

---

## [2.22.0] — 2026-09-19

### Removido & Descomissionado
- **Descomissionamento Definitivo e Higienização do `agentic-memory-manager`**:
  - Remoção física do arquivo `.github/agents/agentic-memory-manager.agent.md`.
  - Remoção do nó e arestas correspondentes em `.github/agents/routing-graph.yaml` e das rotas de despacho em `.github/agents/agent-router.agent.md`.
  - Saneamento atômico em cascata sem deixar rastros em `.github/agents/catalog.yaml`, `.github/agents/README.md`, `.github/skills/.index.json`, `.github/skills/agent-memory-policy/SKILL.md`, `CLAUDE.md`, `README.md`, `docs/plan/` e `tools/context-insight-visualizer/`.
  - Justificativa arquitetural: o agente era órfão dos 8 workflows canônicos, conceptualmente arriscado em relação à "memória procedimental" em tempo de execução e 100% redundante com os hooks automáticos de sessão (26 categorias de eventos), FTS5 nativo e comandos (`/ctx-resume`, `/ctx-checkpoint`) do `context-mode` MCP. A skill neutra `agent-memory-policy` foi preservada como referência de governança.
  - Atualização do total de agentes catalogados no ecossistema de 36 para 35 agentes.

---

## [2.21.0] — 2026-09-19

### Adicionado
- **Consolidação de Segurança de Aplicação (AppSec) e Gestão Holística de Vulnerabilidades (SAST, DAST, IAST, SCA, Secrets, ASPM)**:
  - Criação do **Guia Canônico de Segurança de Aplicação e Vulnerabilidades** (`docs/architecture/APPLICATION_SECURITY_GUIDE.md`), detalhando a matriz dos 6 pilares de AppSec: SAST (análise estática e taint tracking), SCA com *Reachability Analysis*, DAST (testes dinâmicos de runtime e APIs), IAST (instrumentação de testes), Secrets Detection (análise de entropia e pre-commit) e ASPM (gestão de postura e orquestração).
  - Alinhamento explícito com as normas e padrões globais consolidados: OWASP Top 10:2025, OWASP ASVS 5.0, OWASP API Security Top 10, CWE Top 25 e OWASP Agentic AI Security (ASI01..ASI10:2026).
  - Formalização da taxonomia de severidade CVSS v3/v4 e definição de SLAs compulsórios de remediação (Crítico ≤ 24h, Alto ≤ 7 dias, Médio ≤ 30 dias, Baixo ≤ 90 dias) integrados aos Quality Gates dos workflows canônicos.
  - Atualização da skill `security-review-patterns` integrando o protocolo de *Reachability Analysis* para redução drástica de falso-positivo em CVEs transitivas.
  - Atualização do Portal de Documentação em `docs/README.md` vinculando as diretrizes de AppSec aos quadrantes de How-To e Conceitos & Arquitetura.

---

## [2.20.0] — 2026-09-19

### Adicionado
- **Consolidação Documental sob Framework Diátaxis & Padrões Globais de Governança de IA (NIST AI RMF, ISO 42001, OWASP Agentic AI)**:
  - Criação do **Portal Central de Documentação** em `docs/README.md`, organizando 100% dos artefatos técnicos do ecossistema nos 4 quadrantes Diátaxis (Tutoriais, Guias Práticos / How-To, Referência Técnica e Conceitos & Arquitetura).
  - Formalização do **Guia Canônico de Boas Práticas de Documentação em Governança de IA** (`docs/architecture/AI_GOVERNANCE_DOCUMENTATION_GUIDE.md`), integrando os pilares de governança responsável (NIST AI RMF 1.0, ISO/IEC 42001 e OWASP Agentic AI 2026).
  - Alinhamento de documentação de agentes ao padrão aberto **Agent Card** (A2A Protocol / Linux Foundation / IETF Draft 2026) com suporte a manifestos estruturados máquina-máquina via `docs/schemas/agentcard.schema.json`.
  - Atualização do `README.md` principal na raiz integrando o Nível 4 de documentação e sincronizando o status de governança global (169 testes determinísticos no pytest).

---

## [2.19.0] — 2026-09-19

### Adicionado
- **Blindagem Determinística do Workflow de Migração e Camada de Redundância Pós-Migração (WORKFLOW-FRAMEWORK-MIGRATION / REQ-008 / REQ-009)**:
  - Elevação do `WORKFLOW-FRAMEWORK-MIGRATION` em `workflows.md` de 5 para **6 etapas canônicas**, adicionando o **Estado 6 (Post-Migration Verification & Redundancy Gate)** como barreira obrigatória antes de qualquer autorização de cutover.
  - Instituição do **Symbol Exhaustion Gate (Inventário Mecânico de Símbolos)** nas Etapas 1 e 2: exige que a Matriz De-Para mapeie compulsoriamente 100% dos símbolos, métodos (públicos e privados), queries e nós da AST inventariados mecanicamente via `@code-knowledge-graph`, erradicando gaps por inferência superficial.
  - Instituição do **Anti-Omission AST Validator** na Etapa 3: verificação no sandbox do código emitido contra a Representação Intermediária (IR) para impedir truncamento e omissão silenciosa de branches de exceção e tabelas secundárias.
  - Instituição da **Tríplice Camada de Redundância Pós-Migração (Estado 6)**:
    - *Sub-rotina 6a (Reverse Orphan Audit)*: Varredura reversa determinística de 100% dos símbolos, métodos, queries e arquivos legados contra a base moderna e a Matriz De-Para para detectar qualquer código legado órfão sem correspondência.
    - *Sub-rotina 6b (Mutation Parity Resilience)*: Injeção de mutantes sintéticos em regras para comprovar que a suíte Golden Master detecta desvios e eliminar testes falsos-verdes ou frágeis.
    - *Sub-rotina 6c (Differential Shadow Replay)*: Comparação semântica paralela de payloads de retorno, integridade de tabelas secundárias de banco de dados e eventos emitidos.
    - Emissão compulsória do *Certificado de Paridade Total & Cutover Autorizado* em `docs/migrations/certificado-paridade-<alvo>.md`.
  - Formalização do **Invariante 13 em `workflows.md` § 5**, e atualização dos Invariantes 8 e 9 para cobrir as 6 etapas canônicas.
  - Especificação dos requisitos funcionais **REQ-008** e **REQ-009** em `docs/requirements/REQ-migration-engine.md` e atualização da Máquina de Estados em `docs/plan/plano-motor-migracao-agnostica.md` (Fase 6 e CORE-05).
  - Alinhamento de governança global em `CLAUDE.md` e `.github/copilot-instructions.md`.
  - Atualização do cenário de validação operacional `WF-MIG-001` em `tests/operational_flow/casos-workflows.yaml` com a Etapa 6.
  - Expansão da suíte de testes em `tests/governance_audit/test_migration_engine_governance.py` validando Symbol Exhaustion Gate, Tríplice Redundância Pós-Migração e declaração das 6 etapas (169 testes verdes no pytest).

---

## [2.18.0] — 2026-09-19

### Adicionado
- **Precedência Mandatória de Context Mode em Modificação de Arquivos (R-056 / Smell 2.24 — Anti-Editor Tool Sprawl)**:
  - Instituição da regra normativa R-056 em `CLAUDE.md` e `copilot-instructions.md`, estabelecendo o `context-mode` (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_index`, `ctx_search`) como canal primário e compulsório de escrita, criação e refatoração de código e governança.
  - Rebaixamento formal de ferramentas manuais de editor (`replace_string_in_file`, `insert_edit_into_file`) a fallbacks restritos de última instância (apenas micro-edições pontuais de 1-2 linhas ou indisponibilidade de sandbox), proibindo terminantemente encadeamento de chamadas de editor em série no chat.
  - Catalogação do **Smell 2.24 (Omissão de Precedência de Context-Mode em Agentes Mutadores / Editor Tool Sprawl)** em `.github/skills/governance-audit-patterns/SKILL.md`.
  - Reestruturação da Seção 0 de `.github/skills/efficient-batch-code-modification/SKILL.md` com a hierarquia de precedência Nível 1 (Context-Mode compulsório para arquivos estruturados e lote) e Nível 2 (Editor fallback).
  - Atualização dos templates canônicos operacionais (`operational-agent.md`, `agent-template.md`) e do `governance-factory.agent.md` com trava de herança compulsória da precedência de `context-mode` para novos agentes mutadores.
  - Criação da suíte determinística em `tests/governance_audit/test_context_mode_precedence_governance.py` (166 testes verdes no pytest).

## [2.17.0] — 2026-09-19

### Adicionado
- **Metodologia Test-Last e Isenção de Testes Unitários para UI na Stack Frontend**:
  - Instituição da abordagem **Test-Last com Verification Gate Obrigatório** (Implementation-First) para agentes especialistas de frontend (`angular-feature-developer`, `angular-bug-fixer`), eliminando os gargalos de ciclos repetitivos de inicialização de test runners e context poisoning por mocks prematuros de DOM.
  - Isenção formal de criação e execução de testes unitários para agentes e tarefas de pura estilização e apresentação visual (`angular-ui-stylist`), consolidando que validações de UI são 100% visuais (Visual Feedback Loop, WCAG 2.2, design tokens e `get_errors` limpo).
  - Atualização do `WORKFLOW-FEATURE-DEVELOPMENT` em `workflows.md` (Estado 5a/5b), formalizando que a escrita de testes unitários/componentes de regressão é delegada aos test-writers ao final da etapa.
  - Sincronização em lote (R-046 / R-055) das skills `angular-implementation-patterns/SKILL.md`, `frontend-visual-feedback-loop/SKILL.md` e `test-implementation-frontend/SKILL.md`.
  - Padronização em `governance-factory.agent.md` e `governance-factory-patterns/SKILL.md` para que futuros ecossistemas de frontend herdem compulsoriamente a isenção de UI e a metodologia Test-Last.
  - Criação da suíte determinística de testes em `tests/governance_audit/test_frontend_test_last_governance.py` (160 testes verdes no pytest).

## [2.16.0] — 2026-09-19

### Adicionado
- **Portão de Reúso e Generalização Sistêmica em Governança (R-055 / Anti-Silo Fix)**:
  - Instituição da regra normativa R-055 em `CLAUDE.md`, `copilot-instructions.md` e `workflows.md` (`WORKFLOW-GOVERNANCE-MAINTENANCE`), tornando compulsória a avaliação prévia de reúso sistêmico antes de qualquer implementação de melhoria ou ajuste em agents, prompts e skills.
  - Eliminação estrutural do anti-padrão de correções em silo (*one-off fixes*): todo agente de governança deve responder obrigatoriamente às 3 perguntas canônicas de generalização:
    - **Q1 (Impacto Horizontal / Peers)**: avaliar e expandir em lote (*Single-Turn Batching*, R-046) para artefatos análogos do mesmo perfil ou camada.
    - **Q2 (Prevenção Futura / Templates)**: atualizar compulsoriamente o template canônico em `templates/` para que futuras criações herdem a diretriz.
    - **Q3 (Blindagem por Teste / Quality Gate)**: criar ou expandir asserções determinísticas no pytest (`tests/governance_audit/`).
  - Criação da suíte determinística de testes em `tests/governance_audit/test_systemic_reuse_gate.py` validando R-055, workflows, skills e os 3 agentes de governança (155 testes verdes).

### Aprimorado
- **Integração do Gate nos Agentes de Governança**:
  - `@agent-auditor`: inclusão de avaliação compulsória de reúso sistêmico (Q1/Q2/Q3) na `Decision Tree`, `Formato de Saída` e `Checklist Antes de Auditar`.
  - `@governance-factory`: adição da trava no bloco `CRÍTICO` e `Checklist Antes de Codar`, vedando revisões em silo.
  - `@governance-maintainer`: adição da etapa de reúso sistêmico na Fase 1 (Dry-Run & Mapeamento em Memória) e no checklist de conclusão.
  - `governance-factory-patterns/SKILL.md`: formalização da subseção §3.2 detalhando o protocolo de decisão para o gate de generalização.

## [2.15.0] — 2026-09-19

### Adicionado
- **Prevenção Compulsória de R-054 no `@governance-factory` (v1.3.0)**:
  - Adição da seção normativa *Baseline R-054 — Governança Estrita de Todo Agent com Perfil de Router*, exigindo esqueleto base de `templates/router-agent.md`, Least Privilege com 7 ferramentas canônicas, Zero Pre-Routing Discovery e Delegação Plana.
  - Detecção automática de perfil router no fluxo `type: agent` (quando `name` termina em `-router` ou `description` indica papel supervisor/despachante).
  - Gate de validação formal em `tests/governance_audit/test_router_agents.py` incorporado aos fluxos de scaffolding de router em `type: stack` e `type: agent`.
  - Inclusão de `.github/skills/governance-audit-patterns/SKILL.md` em `source_docs`.

### Aprimorado
- **Auditoria Dinâmica de Smells e R-054 no `@agent-auditor` (v1.2.0)**:
  - Substituição da contagem estática ("14/13 categorias de smell") por referência dinâmica a `governance-audit-patterns/SKILL.md` § 2 (atualmente até o Smell 2.23).
  - Adição de verificação explícita de conformidade com R-054 e Smell 2.23 na Decision Tree e Checklist ao auditar artefatos com perfil router (`*-router.agent.md` e `templates/router-agent.md`).
- **Saneamento Documental em `@governance-factory`**:
  - Remoção de bloco de texto corrompido/órfão remanescente no final do arquivo.

## [2.14.0] — 2026-09-19

### Adicionado
- **Governança Estrita de Routers (R-054 / Smell 2.23 — Anti-Overthinking Router & Zero Discovery)**:
  - Instituição da regra mandatória de **Zero Pre-Routing Discovery**: proibição absoluta de tool calls de leitura exploratória de código, varredura de diretórios ou scripts de sandbox para investigar o conteúdo de solicitações ou arquivos anexados (`#file:...`) antes de rotear, prevenindo latência e consumo desproporcional de créditos em modelos topo de linha (Claude Sonnet 5).
  - Formalização do **Smell 2.23 (Router Over-Empowerment e Pre-Routing Discovery Bloat)** em `.github/skills/governance-audit-patterns/SKILL.md`, baseado no consenso de mercado de 2025/2026 (*Anthropic, LangChain, Vercel, Atlan/Snowflake via arXiv:2603.17787, Patronus AI e Splunk*).
  - Ampliação da suíte determinística de testes em `tests/governance_audit/test_router_agents.py` com validação estática de Least Privilege universal de ferramentas, presença de Zero Discovery e Delegação Plana em todos os roteadores (150 testes passando no `pytest`).

### Aprimorado
- **Saneamento Universal de Ferramentas em Routers**:
  - Restrição estrita de ferramentas no `agent-router` central, nos 7 supervisores de domínio (`angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `database-router`, `python-router`, `struts-router`) e no template canônico `router-agent.md` ao baseline exclusivo de 7 ferramentas de leitura, busca, clarificação e despacho (`read_file`, `file_search`, `grep_search`, `list_dir`, `ask_questions`, `run_subagent`, `context-mode/ctx_search`).
  - Extirpação completa de ferramentas mutativas (`create_file`, `insert_edit_into_file`, `replace_string_in_file`, `apply_patch`), comandos de terminal (`run_in_terminal`) e sandbox de código (`context-mode/ctx_execute*`) de todos os roteadores.
- **Blindagem Total da Delegação Plana (Flat Delegation / Smell 2.20)**:
  - Proibição expressa de invocar especialistas ou executores downstream via `run_subagent` por dentro de qualquer roteador, garantindo que o despacho seja realizado exclusivamente pelo orquestrador raiz em nível plano.
  - Sincronização atômica de catálogos e governança em `CLAUDE.md` (R-054), `.github/copilot-instructions.md`, `.github/agents/catalog.yaml` e `.a2a/agentcards/agent-router.agentcard.json`.

## [2.13.0] — 2026-09-19

### Aprimorado
- **Padronização Canônica de Formato de Saída (R-042 / R-050 / agent-contracts § 0 e § 8)**:
  - Inserção do banner universal de visibilidade `Agente Ativo: <slug>` e `[Se aplicável] Handoff: <origem> → <destino>` nos blocos de código Markdown de 20 agentes raiz (`bug-triage`, `code-review`, `debugger`, `runtime-verifier`, `code-style-enforcer`, `compliance-guardrails`, `security-reviewer`, `performance-agent`, `devops-engineer`, `pr-gatekeeper`, `database-specialist`, `agentic-memory-manager`, `business-rules-extractor`, `code-knowledge-graph`, `deep-search`, `docs-engineer`, `governance-factory`, `prompt-structuring`, `adapter-generator`, `binding-initializer`).
  - Harmonização dos 7 Stack Routers (`angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `python-router`, `struts-router`, `database-router`) e do template `router-agent.md` com campos de especificação de modelo (`[Model] Delegando para...`), métricas de confiança (`Confiança`, `Confidence Score`) e entradas consideradas.
  - 100% de conformidade com a suíte de testes de governança (147 testes passando no pytest).
- **Evolução de Autonomia Delimitada (3 Tiers) & Gate Pattern no `@prompt-structuring` (R-041)**:
  - Implementação do modelo de 3 Tiers para mitigar anti-padrões de mercado em sistemas multi-agentes (Approval Fatigue, Agency Stripping e Latency Tax): Tier 1 (Fast-Path com bypass para tarefas determinísticas), Tier 2 (Gate Pattern "Prepare, Don't Submit" com preview e confirmação de 1-clique via ask_questions em 1 turno) e Tier 3 (loop interativo multi-turno limitado a 5 iterações para ambiguidade alta).
  - Instituição formal da fronteira Problem Space vs Solution Space: o estruturador delimita exclusivamente o *Quê*, requisitos funcionais e critérios de aceitação, sendo terminantemente vedada a prescrição de implementação técnica interna que pertence aos especialistas de stack.
  - Sincronização do agente `prompt-structuring.agent.md`, diretriz R-041 em `CLAUDE.md` e catálogo `catalog.yaml`.

## [2.12.0] — 2026-09-17

### Adicionado
- **Blindagem Determinística contra "Cleverness Trap" & State-Locking Universal (R-050 / R-054)**:
  - Implementação compulsória do protocolo de **State-Locking** (`[CURRENT_STATE_LOCK: ...]`) e **Halting Conditions** em 28 agentes do ecossistema de governança, prevenindo iniciativas espúrias, antecipação de código e desvios de pipeline em modelos de alta capacidade (Claude Sonnet 5, Opus) e garantindo execução atômica em modelos leves (Gemini Flash).
  - Mapeamento fechado de estados e saídas tipadas em 3 perfis operacionais: (A) Parecer Compacto de Gate/Checkpoint, (B) Technical Blueprint & Context Firewall e (C) Matriz De-Para 5D.

### Aprimorado
- **Endurecimento dos Agentes Planejadores / Deliberativos (Grupo 1)**:
  - `@tech-solution-architect`, `@refactor-planner`, `@feature-planner`, `@requirements-analyst` e `@test-strategy`: saneamento de ferramentas com remoção de `ctx_execute`/`ctx_execute_file`, proibição terminante de gerar código executável e exigência de DAGs/matrizes estruturadas com pontos de parada (*STOP TOTAL*).
- **Endurecimento dos Supervisores Hierárquicos / Domain Routers (Grupo 2)**:
  - `@angular-router`, `@spring-boot-router`, `@spring-reactive-router`, `@ejb-router`, `@database-router`, `@python-router` e `@struts-router`: aplicação de *Delegação Plana (Flat Delegation)*, proibição absoluta de ferramentas mutativas e resolução estrita de papéis genéricos (`specialist-<papel>`) para agentes concretos do catálogo.
- **Endurecimento dos Executores Táticos (Grupo 3)**:
  - 17 agentes executores (`*-feature-developer`, `*-bug-fixer`, `*-ui-stylist`, `*-migration-dev`, `*-spl-expert`, `*-plsql-expert`): trava de execução em TDD estrito (Red Test prévio obrigatório, Single-Turn Batching com diff cirúrgico mínimo ≤ 20 linhas e validação agregada imediata com `get_errors`).
- **Sincronização SSOT & Qualidade**:
  - Atualização de versões no catálogo central `.github/agents/catalog.yaml`.
  - Reexportação de 65 AgentCards A2A em `.a2a/agentcards/`.
  - 100% de conformidade com 147 testes automatizados passando no `pytest`.

## [2.11.0] — 2026-09-16

### Adicionado
- **Matriz De-Para Bidirecional & Prevenção Canônica de Gaps em `WORKFLOW-FRAMEWORK-MIGRATION` (R-050)**:
  - Instituição da **Matriz De-Para de Migração & Rastreabilidade de Gaps** (`docs/migrations/matriz-de-para-<alvo>.md`) como Single Source of Truth obrigatória para qualquer migração tecnológica cross-stack ou elevação de plataforma.
  - Taxonomia rigorosa de status de paridade com 5 estados determinísticos: `[✅ MIGRADO]`, `[⏳ PENDENTE]`, `[⚠️ DIVERGENTE]`, `[ℹ️ DESACOPLADO]` e `[🚫 OBSOLETO]`.
  - Critério de fechamento bloqueante: zero itens `PENDENTE` ou `DIVERGENTE` no módulo ao final do pipeline.
- **Decomposição Estrutural Exaustiva em 5 Dimensões Críticas (Estado 1)**:
  - Eliminação de avaliações superficiais ou limitadas ao "happy path": decomposição sistemática e obrigatória em (1) Borda, Contratos de Entrada & Validações Fail-Fast; (2) Regras de Negócio e Ramificações Condicionais; (3) Pegada de Persistência Relacional & Transações (tabelas pai, filhas, rateios, snapshots, sequências, isolamento); (4) Efeitos Colaterais & Integrações Downstream (SOAP, REST, filas, PDFs/relatórios, e-mails, uploads, webhooks); e (5) Contratos de Saída & DTOs de Resposta.
- **Protocolo Brownfield In-Flight (Reconciliação Delta & Auditoria de Gaps Pré-Existentes — Estado 1b)**:
  - Mecanismo específico e obrigatório para migrações já iniciadas, parciais ou inacabadas no repositório de destino (prevenção do cenário real observado de dezenas de gaps descobertos tardiamente).
  - Comparação cruzada entre a árvore 5D do legado e os artefatos existentes no destino, gerando imediatamente a Matriz De-Para com todos os GAPs catalogados (`GAP-01..GAP-NN`) antes da elaboração do plano de fases.
- **Faseamento Orientado a Risco e Impacto Ancorado na Matriz De-Para (Estado 2)**:
  - Fases autônomas entregáveis (B1..BN) onde cada fase possui uma lista explícita de IDs De-Para sob sua responsabilidade, com critérios de aceite determinísticos.
  - Dashboard Executivo da Matriz De-Para exibido no chat e no Checkpoint Humano 2b para visibilidade e transparência completa a desenvolvedores humanos.
- **Dual-Verification Gate Expandido (Quádruplo Critério de Paridade — Estado 4)**:
  - Aprovação de fase exige simultaneamente: (1) 100% Golden Master verde; (2) 100% de resolução dos IDs De-Para da fase; (3) sign-off do domain-router de origem como oráculo; e (4) atesto estrutural de zero novos ciclos e zero dead-code pelo `@code-knowledge-graph`.
- **Teste de Regressão e Governança**:
  - Novo teste `test_workflow_framework_migration_depara_matrix_and_brownfield_reconciliation` adicionado à suíte operacional (`test_operational_workflows.py`), garantindo 100% de conformidade automatizada.

## [2.10.0] — 2026-09-15

### Adicionado
- **Regra R-052 e Erradicação do Anti-Padrão Sticky Agent**:
  - Nova regra normativa `R-052 (Reset Mandatório pós-Conclusão de Workflow / Post-Task Router Handback — Anti Sticky-Agent)` em `CLAUDE.md` e `.github/copilot-instructions.md`.
  - Proibição absoluta de o último agente ativo reter o controle de novas solicitações do usuário no chat sob pretexto de ser a "mesma stack/tecnologia".
  - Todo encerramento de workflow canônico (R-050) encerra formalmente o ciclo operacional e reverte compulsoriamente o controle ao `@agent-router` (`motivo: "conclusao_de_workflow_anterior"`).
- **Catalogação do Smell 2.22 em `governance-audit-patterns`**:
  - `Smell 2.22 — Sticky Agent e Falha de Reset de Workflow (R-042 / R-052)`: catalogado com severidade Bloqueador.
  - Teste determinístico `test_smell_2_22_workflow_reset_and_anti_sticky_agent_rule` adicionado à suíte `tests/governance_audit/test_governance_smells.py` (100% verde).
- **Fortalecimento da Regra R-051 e Proteção Anti-Corrupção em Markdown Estruturado**:
  - Extensão formal da regra `R-051 (Proteção Anti-Corrupção em Edição de Arquivo Único Grande/Estruturado e Markdown com Âncoras Repetidas)` em `CLAUDE.md`, `.github/copilot-instructions.md`, `efficient-batch-code-modification` e `governance-audit-patterns` (Smell 2.16).
  - Proibição absoluta de invocar `replace_string_in_file` com âncoras ambíguas ou sem verificação prévia de unicidade estrita em memória (`count === 1`), prevenindo o fallback de correspondência aproximada (fuzzy matching) que corrompe/trunca blocos em arquivos com tabelas e seções parecidas (incidente real documentado em `code-knowledge-graph.agent.md`).
  - Atualização do snippet `snippets/safe-single-file-edit-pattern.js` e obrigatoriedade de validação imediata da integridade estrutural pós-escrita (frontmatter `---`, cabeçalhos canônicos e contagem de linhas).
- **Invariantes Dual-Stack e Co-Agência Obrigatória de `@code-knowledge-graph` em `WORKFLOW-FRAMEWORK-MIGRATION` (R-050)**:
  - Formalização das Invariantes 8 e 9 em `workflows.md` § 3.7 e § 5: em migrações cross-stack, o domain router da stack de origem legada (`@ejb-router`, `@struts-router`) e o motor de grafo (`@code-knowledge-graph`, R-045) são co-agentes obrigatórios em todas as etapas (1 a 5), nunca dispensados após o pre-flight.

### Aprimorado
- **Ajuste Fino na Regra R-042**:
  - Esclarecida a cláusula de perfil híbrido dos specialists, restringindo a continuidade sem handoff estritamente a refinamentos imediatos de uma mesma tarefa em andamento.

---

## [2.9.0] — 2026-09-15

### Adicionado
- **Nova Skill Agnóstica `frontend-visual-feedback-loop`**:
  - Padrão canônico de mercado (2025–2026) para execução do Visual Feedback Loop (VFL) desacoplado de framework (Angular, React, Vue, Svelte, Web Components).
  - Suporte a renderização isolada em sandbox (Storybook CSF3 / rota efêmera), captura multi-viewport canônica (`375x667`, `768x1024`, `1440x900`), inspeção da Árvore de Acessibilidade (AOM) e asserções visuais Playwright.
  - Princípio Think-in-Code para persistência de screenshots em disco sem inflar contexto de chat, e circuit breaker com limite rígido de 2 iterações no critic loop.
- **Formalização do Smell 2.21 em `governance-audit-patterns`**:
  - `Smell 2.21 — Cegueira Visual e Suposição de Contratos de UI (Visual Blindness & Unverified UI Contracts)`: cataloga e previne a falsa equivalência entre compilação/testes headless verdes e conformidade visual/contratual real de interface.
  - Teste determinístico `test_smell_2_21_visual_blindness_and_ui_contracts_documented` integrado à suíte Tier 1 de auditoria estática.

### Aprimorado
- **Evolução da Regra R-033 e Erradicação do Drift Documental por Autorreflexão**:
  - Reformulação formal de R-033 no `CLAUDE.md` e `copilot-instructions.md`: distinção entre a proibição estrita de criar arquivos .md especulativos avulsos e a **obrigatoriedade da sincronização automática de documentação viva existente** (`docs/`, README, ADRs, schemas) por autorreflexão contínua em qualquer entrega técnica relevante, eliminando a necessidade de comandos manuais do desenvolvedor.
  - Inclusão do checkpoint de autorreflexão documental no DoD do `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-BUG-FIX` e `WORKFLOW-REFACTORING` (`workflows.md`).
  - Atualização dos checklists e contratos operacionais de `@pr-gatekeeper`, `@angular-feature-developer`, `@angular-ui-stylist`, `@database-specialist` e da dimensão de conformidade documental em `code-review-patterns`.
- **Tratamento Especializado de Bugs de Layout no `WORKFLOW-BUG-FIX` (`workflows.md` e agentes)**:
  - Formalização do Cenário C no Estado 2 com o ciclo VFL (`frontend-visual-feedback-loop`), capturas multi-viewport (375px/768px/1440px) e asserções estritas de AOM.
  - Roteamento compulsório no Estado 3 de defeitos de layout, SCSS, alinhamento de diálogos e ícones para o especialista de UI (`specialist-ui-stylist`), prevenindo que corretores de lógica pura introduzam regressões cosméticas.
  - Exigência de validação dupla no Estado 4 para defeitos de layout: testes de componentes verdes E re-inspeção visual VFL/AOM sem texto literal vazando em ícones.
  - Bifurcação na árvore de decisão de `angular-router` (bugs de runtime -> `angular-bug-fixer`; bugs de layout/CSS -> `angular-ui-stylist`) e atualização do intake de `bug-triage` para acolher evidências visuais.
- **Duplo Quality Gate no `WORKFLOW-FEATURE-DEVELOPMENT` (`workflows.md`)**:
  - Particionamento do Estado 5 para demandas com interface: 5a (Lógica reativa, stores e regras sob TDD com `angular-feature-developer`) e 5b (Handoff mandatório de apresentação visual e tokens com `angular-ui-stylist`).
  - Implantação do Duplo Gate no Estado 6: Gate 1 (Lógica, Contratos & OWASP com `@security-reviewer`) e Gate 2 (Design System, Paridade Visual, zero hex inline e validação de contratos de componentes `shared/` com `@angular-ui-stylist` e `@code-review`).
- **Agentes de Domínio Frontend Angular**:
  - `@angular-feature-developer`: Proibição estrita de suposição de props em inglês, protocolo "Canonical Sibling First" e leitura obrigatória do arquivo `.ts` de componentes `shared/` para validação de `@Input()`.
  - `@angular-ui-stylist`: Auditoria obrigatória de classes de diálogo (`.app-dialog-content`, `.form-grid`), empty-states de largura total, wrappers de ícone e proibição absoluta de cores hexadecimais inline em SCSS de features.
  - `@angular-router`: Atualização da árvore de decisão para sequenciar demandas de UI pelo pipeline em duas fases.
- **Skills e Adapters Compartilhados**:
  - `angular-implementation-patterns` e `frontend-componentization-patterns`: Incorporação do protocolo "Canonical Sibling First" e leitura estrita de interfaces no passo "Reuso-First".
  - `design-system-component-contracts`: Diretrizes de verificação de contratos no lado do consumidor e enforcement de tokens semânticos.
  - `angular-v21-frontend.instructions.md`: Normas canônicas de layout de diálogos, classes utilitárias de scroll e proibição de hexadecimais arbitrários.
  - Atualização atômica de catálogos: `.github/skills/.index.json` (60 skills indexadas), `.github/skills/README.md` e `.github/copilot-instructions.md`.
- **Documentação de Arquitetura e Adapters**:
  - `docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md`: atualização do `WORKFLOW-FEATURE-DEVELOPMENT` com Duplo Quality Gate e inclusão da seção §8.4 sobre o Visual Feedback Loop (VFL) e mitigação do Smell 2.21.
  - `README.md` e `.github/agents/README.md`: alinhamento da contagem para 60 skills especializadas e consolidação dos 8 workflows determinísticos.
  - `.github/instructions/local/<projeto>.instructions.md`: inclusão da Seção 1.3 consolidando paridade visual, protocolo "Canonical Sibling First", leitura estrita de contratos de componentes compartilhados e proibição de hex inline.

---

## [2.8.10] — 2026-09-14

### Refatorado & Saneado
- **Limpeza Profunda de Seções Não-Homologadas e Citações em Frontmatter/Templates**:
  - Extirpação completa das seções legadas e redundantes no corpo Markdown (`## Regras Herdadas`, `## Catálogo / Conhecimento Base`, `## Skills Associadas`) em 9 arquivos de roteadores e templates (`agent-router.agent.md`, `router-agent.md`, `angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `python-router`, `struts-router` e `database-router`).
  - Higienização de comentários e orientações nos frontmatters de todos os templates (`agent-template.md`, `operational-agent.md`, `research-agent.md`, `router-agent.md`, `skill-template.md`, `prompt-template.md`), além de `governance-factory.agent.md`, `binding-initializer.agent.md`, `governance-factory-patterns/SKILL.md` e `agent-memory-policy/SKILL.md`, removendo quaisquer menções instrucionais remanescentes aos nomes das seções legadas.
  - Consolidação formal de dependências documentais e de skills exclusivamente no frontmatter YAML `source_docs:` (SSOT), eliminando duplicação e acoplamento desnecessário no corpo dos agentes.
  - Saneamento de ferramentas do frontmatter de `agent-router.agent.md` removendo referências a ferramentas `angular-cli/*` não-reconhecidas.
- **Fortalecimento do Gate de Homologação de Seções (Smell 2.9)**:
  - `tests/governance_audit/test_template_sections.py`: O teste de homologação foi expandido para cobrir **100% dos agentes** (incluindo todos os routers e templates), garantindo que nenhuma seção não-homologada volte a ser introduzida em qualquer `.agent.md` do repositório.
  - `tests/governance_audit/test_router_agents.py`: Atualizadas as seções obrigatórias dos routers para as 4 seções canônicas de roteamento (`CRÍTICO: ESCOPO`, `Decision Tree`, `Formato de Saída`, `Retorno ao Router`), sem dependência de seções legadas no corpo.
  - Suíte global de testes preservada com **136 testes**, 100% verde (`pytest` em 11.65s).

---

## [2.8.9] — 2026-09-14

### Adicionado & Aprimorado
- **Guia Canônico de Arquitetura e Governança (arc42 / Diátaxis / IEEE 42010)**:
  - Criado o documento canônico `docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md` estruturado conforme as 12 seções padrão do arc42 (v8.2), o padrão internacional IEEE 42010 e o framework Diátaxis (dimensões de *Explanation* e *Architecture Reference*).
  - Consolidação formal do modelo estático e dinâmico da governança multi-agente:
    - *Visão de Contexto e Fronteiras*: diagrama Mermaid delimitando IDE, host, governança central, aplicações de negócio locais e servidores MCP.
    - *Visão de Blocos de Construção (Building Blocks)*: decomposição das 4 camadas (Entrada/Triagem, Supervisores de Domínio, Especialistas de Execução e Agentes Transversais de Qualidade) com mapeamento dos 65 agentes catalogados.
    - *Visão de Execução e Runtime*: especificação determinística dos 8 Workflows Canônicos (R-050), banner universal de handoff (R-042/R-048) e diagrama de estados do Multi-Agent Circuit Breaker (`CLOSED` → `OPEN` → `HALF-OPEN`).
    - *Visão de Implantação*: topologia de runtimes locais, worktrees efêmeros (`.worktrees/`), overlay privado (`projects.local.yaml`) e motor de grafo `@optave/codegraph`.
  - Matriz de Validação de Mercado (Seção 9): mapeamento detalhado e fundamentação de 10 decisões arquiteturais centrais (ADR-01 a ADR-10) confrontadas com publicações e normas de mercado consolidadas em 2026 (Anthropic Agentic Coding Trends Report 2026, NSA CSI MCP Security 2026, Cloud Security Alliance Agentic MCP Security Best Practices v1, Linux Foundation A2A v1.0.0, IETF draft-aevum-agentcard-00, ISO/IEC 25010 e IEEE 42010).

---

## [2.8.8] — 2026-09-14

### Adicionado & Aprimorado
- **Context Engineering & Artifact Offloading em Handoffs (Anthropic 2026 Trends)**:
  - Atualizada a skill `.github/skills/handoff-governance/SKILL.md` com a formalização dos 4 pilares do Context Engineering (*Write, Select, Compress, Isolate*).
  - Estabelecido o limiar normativo de offloading de artefatos (2 KB / 50 linhas): payloads volumosos (ASTs de grafo, diffs extensos, contratos OpenAPI, logs longos) deixam de ser transmitidos como texto bruto no chat e passam a trafegar exclusivamente como ponteiros tipados (`tipo: "pointer"`, `artifact_ref`, `hash`, `resumo_executivo`) associados ao `context-mode` e workspace, prevenindo context bloat e KV-cache thrashing.
- **Multi-Agent Circuit Breakers com Budget de Falhas e Rollback Atômico**:
  - Implementado em `.github/skills/handoff-governance/SKILL.md` o Circuit Breaker de Falhas com Retry Budget estrito (`MAX_RETRIES_PER_STEP = 2`). Falhas repetidas na mesma etapa desarmam o circuito para `state: OPEN`, suspendendo edições autônomas e acionando escalonamento humano obrigatório (`ask_questions` / R-047).
  - Instituído o Protocolo de Rollback Atômico de Workspace: rotina determinística de descarte de worktrees temporários isolados ou saneamento cirúrgico de arquivos parciais via `git checkout -- <arquivos>`, garantindo integridade do workspace em caso de falha de cadeia.
- **Segurança de Ferramentas MCP e Sandboxing (NSA CSI MCP Security 2026 / CSA v1)**:
  - Adicionada a seção 4.9 em `.github/skills/agent-safety-guardrails/SKILL.md` estabelecendo:
    - Zoneamento e Least-Privilege Tool Scoping: Zona 1 (Read-Only) para consultivos/advisors, Zona 2 (Mutating) para implementers e Zona 3 (Execution) sob governança de terminal (R-049).
    - Defesa contra Parameter Tampering e Tool Poisoning (ASI02): validação estrita de schemas de parâmetros JSON contra injeção indireta (CVE-2025-6514).
    - Defesa contra Tool Squatting e Rug Pulls em servidores MCP e proibição de repasse cego de tokens de autorização (*Token Passthrough*) entre limites de confiança inter-agente.
- **Padronização e Exportação A2A AgentCard (Linux Foundation v1.0.0 / IETF draft-aevum-agentcard-00)**:
  - Criado o schema canônico aberto `docs/schemas/agentcard.schema.json` para interoperabilidade e especificação declarativa de agentes.
  - Implementado o utilitário determinístico `tools/agentcard_exporter/export_agentcards.py`, mapeando os catálogos do repositório em 65 arquivos de especificação `AgentCard` em `.a2a/agentcards/*.agentcard.json` e índice consolidado `.a2a/agentcards/agentcards.index.json`.
  - Criadas suítes de testes automatizadas em `tests/governance_audit/test_a2a_agentcard_compliance.py` e `tests/operational_flow/test_circuit_breaker_and_context_offloading.py`.
  - Suíte global de testes expandida para **136 testes**, 100% verde (`pytest` em 12.09s).

---

## [2.8.7] — 2026-09-14

### Adicionado & Aprimorado
- **Alinhamento com OWASP Top 10 for Agentic Applications 2026 (ASI01..ASI10:2026)**:
  - Atualizada a skill `.github/skills/agent-safety-guardrails/SKILL.md` com a taxonomia formal oficial da OWASP para sistemas autônomos de agentes (ASI01:2026 a ASI10:2026), publicada em dezembro de 2025.
  - Implementadas diretrizes operacionais de contenção para:
    - *ASI07: Insecure Inter-Agent Communication*: Validação de schema tipado de handoff (`handoff-governance` v1.1) e não-repúdio via banner de `Agente Ativo:`.
    - *ASI08: Cascading Agent Failures*: Circuit breaker a 3 falhas consecutivas (R-050.2) e isolamento de estado por Typed State Bags.
    - *ASI06: Memory & Context Poisoning*: Controles contra injeção em memória de longo prazo e sanitização de chunks de context-mode.
    - *ASI09: Human-Agent Trust Exploitation*: Neutralidade e transparência em `ask_questions`, vedando perguntas indutivas em operações sensíveis.
- **Nova Skill de Governança: `git-worktree-governance`**:
  - Criada a skill `.github/skills/git-worktree-governance/SKILL.md` (Tier 2, categoria governance) padronizando o ciclo de vida de 5 etapas (`setup → isolate → verify → merge → cleanup`) para agentes executores paralelos e explorações especulativas.
  - Prevenção de colisões em lockfiles (`package.json`, `pom.xml`), locks de git index e concorrência de compilação.
  - Sincronização atômica SSOT (R-015) em `.github/skills/.index.json` (`total_skills: 59`), `.github/skills/README.md`, `.github/copilot-instructions.md` e adição de `.worktrees/` em `.gitignore`.
- **Evals Lab — Validação E2E e Simulação dos 8 Workflows Canônicos (R-050)**:
  - `tests/operational_flow/workflow_eval_simulator.py`: Implementado o método `simulate_state_bag_transitions()` para simulação determinística de propagação do Typed State Bag (`workflow_state`), auditando transições entre etapas sem consumo de tokens de LLM.
  - `tests/operational_flow/test_workflow_trajectories.py`: Adicionados os testes `test_e2e_state_bag_preservation_across_all_8_workflows` e `test_all_8_workflows_have_terminal_quality_gates`, garantindo preservação de artefatos e terminação em Quality Gate formal para todos os 8 workflows.
  - `tests/operational_flow/casos-workflows.yaml`: Corrigido o gate de transição da etapa de implementação do `WF-FEAT-001` para autorizar avanço ao gate de segurança do `security-reviewer`.
  - Suíte de testes expandida para **129 testes**, 100% verde (`pytest` em 13.54s).

---

## [2.8.6] — 2026-09-14

### Refatorado & Consolidado
- **Consolidação Global de SSOT no Frontmatter (`source_docs:`) e Extirpação de Redundâncias**:
  - Unificação de 100% das dependências normativas, contextuais e skills no frontmatter YAML `source_docs:`, eliminando a quádrupla duplicação de links documentais no catálogo de agentes e prompts.
  - Extirpadas **1.350+ linhas de texto redundante** em 79 agentes (`.agent.md`) e 2 prompts (`.prompt.md`), removendo as seções obsoletas do corpo markdown: `## Regras Herdadas`, `## Catálogo / Conhecimento Base`, `## Skills Associadas`, `## Docs Sempre Anexadas (pre-fetch obrigatório)` e `## Source Docs (R-046)`.
  - Preservadas integralmente as seções contratuais de roteamento dos supervisores hierárquicos (8 routers), garantindo a conformidade da máquina de estados de despacho.
- **Refinamento e Blindagem dos Templates Canônicos (`.github/templates/`)**:
  - `agent-template.md`, `operational-agent.md`, `research-agent.md`: Adicionada diretriz normativa de SSOT de documentação, formalizando o bloqueio estrito de seções redundantes de doc-loading no corpo markdown.
  - `router-agent.md`: Documentado o contrato estrutural fechado para supervisores hierárquicos e alinhamento com `test_router_agents.py`.
  - `prompt-template.md`: Consolidada a especificação oficial de Prompt Files com injeção de dependências em `source_docs:` e variáveis nativas do VS Code Copilot.
  - `skill-template.md`: Formalizada a arquitetura de *Progressive Disclosure* em 3 níveis (Nível 1 Metadados, Nível 2 Corpo Operacional de 7 seções canônicas, Nível 3 Recursos Suplementares).
  - Atualizados `governance-factory.agent.md`, `governance-audit-patterns/SKILL.md` (Smell 2.2 saneado) e `adapter-generator.agent.md` para eliminar referências residuais à seção descontinuada `Docs Sempre Anexadas`.
- **Quality Gate de Governança — Gate de Homologação de Seções (Tier 1)**:
  - `tests/governance_audit/test_template_sections.py`: Implementados 4 novos testes determinísticos (`test_homologation_gate_no_unhomologated_sections_in_agents`, `test_homologation_gate_no_unhomologated_sections_in_prompts`, `test_homologation_gate_no_unhomologated_sections_in_skills`, `test_homologation_gate_blocks_unhomologated_injections`) para barrar compulsoriamente a injeção de seções ad-hoc sem template previamente homologado. Suíte expandida para 127 testes passando com 100% verde.

---

## [2.8.5] — 2026-09-14

### Aprimorado
- **Evolução do Agent `bug-triage` (v1.1.0 — Blast Radius Proativo & Challenge Gate de Regras)**:
  - `.github/agents/bug-triage.agent.md`:
    - Adicionado **Challenge Gate de Regras de Negócio & Consumidores (Fase 1.5)** obrigatório via `ask_questions`, impedindo presunção de correção pontual mesmo quando o desenvolvedor já entrega pré-análise e arquivos no prompt.
    - Expandida a Fase C para **Fase C+ (Traçar Call Chain e Blast Radius Proativo)** com classificação em Verde (Cirúrgico), Amarelo (Mini-Refactoring) e Vermelho (Sistêmico) e integração com `@code-knowledge-graph`.
    - Adicionada detecção e tratamento de `mini-refactoring` na classificação de falha e no plano de ação, exigindo **Passo 0: Testes de Caracterização dos Componentes Vizinhos (Safety Net)** antes de qualquer alteração de código compartilhado para evitar quebras colaterais.
    - Vinculadas as skills `refactoring-planning-patterns`, `business-rules-governance` e `efficient-batch-code-modification` em `source_docs` e no catálogo.
  - `.github/agents/catalog.yaml`: Atualizados metadados, `related_agents`, `related_skills` e `source_docs` de `bug-triage` (v1.1.0).

- **Codificação de Diretrizes Anti-Band-Aid e Timing Reativo (`angular-bug-fixer`, `code-tracing`, `angular-implementation-patterns`)**:
  - `code-tracing/SKILL.md`: Adicionados 4 novos anti-padrões essenciais de diagnóstico: máscara visual (desligar spinner sem resolver stream), temporizadores imperativos manuais (`setTimeout`) em código reativo, violação de contratos de consumidores vizinhos, e negligência do timing de renderização no DOM (instanciação tardia sob `@if`).
  - `angular-bug-fixer.agent.md`: Incorporadas restrições explícitas contra flags artificiais de loading, timeouts imperativos, afrouxamento de contratos e violação de ciclo de vida de barramento de eventos.
  - `angular-implementation-patterns/SKILL.md`: Atualizados o workflow de correção de bug e os anti-padrões para exigir rastreamento de fora para dentro e respeito aos invariantes terminais de estado.

---

## [2.8.4] — 2026-09-13

### Corrigido & Sincronizado
- **Saneamento de Referências a Agentes Descomissionados nos READMEs e Catálogo**:
  - `README.md`: Atualizada a seção de especialistas de stack para a topologia vigente de supervisores de domínio (`angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `struts-router`, `python-router` e `database-router`), removendo menções residuais aos agentes monolíticos antigos (`angular-engineer`, `spring-boot-engineer`, `spring-reactive-engineer`).
  - `.github/skills/README.md`: Atualizadas as descrições das skills de performance e implementação para apontar para os especialistas dos ecossistemas de domínio atuais, saneando referências a `angular-engineer`, `spring-boot-engineer`, `spring-reactive-engineer` e `docs-writer`.
  - `.github/agents/catalog.yaml`: Atualizados os campos `related_agents` de `refactor-planner` e `runtime-verifier` para referenciar os routers de domínio e `test-strategy`.
- **Fortalecimento da Suíte de Testes e Governança Estática (Smell 2.1)**:
  - `tests/operational_flow/test_operational_workflows.py`: Atualizado o conjunto `LEGACY_DEPRECATED_AGENTS` para incluir `angular-engineer`, `spring-boot-engineer`, `spring-reactive-engineer` e `test-engineer`.
  - `tests/governance_audit/test_governance_smells.py`: Implementado o teste determinístico `test_smell_2_1_no_deprecated_agents_in_live_readmes` (Smell 2.1 — Referência Órfã) com regex de fronteira de palavras, garantindo que nenhum agente descontinuado volte a ser citado na documentação viva. Suíte totalizando 123 testes (100% verde).

---

## [2.8.3] — 2026-09-12

### Adicionado & Aperfeiçoado
- **Persistência Local e Nuvem de Incidentes de Workflows (`tools/incident_recorder`)**:
  - **Especificação de Requisitos (`docs/requirements/REQ-workflow-incident-persistence.md`)**:
    - Requisitos funcionais (REQ-001 a REQ-009) cobrindo captura contínua de erros, persistência local em SQLite WAL com JSON1, padrão Outbox, fail-safe operacional, aprendizado contínuo com destilação de lições aprendidas (REQ-008) e mecanismo de purge/pruning para liberação de espaço em disco e no Supabase (REQ-009).
    - Requisitos não-funcionais (RNF-001 a RNF-004) para escrita ultrarrápida (<5ms), isolamento ACID local, interoperabilidade documental neutra e sanitização automática de credenciais e tokens (PII/Secret Scrubbing).
  - **Technical Blueprint & Contratos (`docs/plan/plano-persistencia-incidentes-workflows.md`)**:
    - Arquitetura Local-First Outbox Pattern com DDL SQLite local otimizado e DDL Supabase (PostgreSQL 15+ com coluna `document_payload JSONB` e índice GIN).
    - Sub-rotina de ciclo de vida de aprendizado e mecanismo de purge para exclusão de incidentes resolvidos via PostgREST no Supabase e `VACUUM` no SQLite local.
    - Context Firewall dividindo responsabilidades entre `[CORE_PERSISTENCE_TASKS]`, `[LOCAL_STORAGE_TASKS]` e `[CLOUD_SYNC_TASKS]`.
  - **Schema Canônico do Incidente (`docs/schemas/workflow-incident.schema.json`)**:
    - JSON Schema Draft 2020-12 estendido com `rootCause`, `successfulPatch`, `lessonLearned` e `prunedAt` na seção `resolution`.
  - **Módulos de Produção (`tools/incident_recorder/`)**:
    - `secret_scrubber.py`: sanitizador de credenciais, chaves de API (`sk-*`, `ghp_*`, `sbp_*`), Bearer JWTs e senhas.
    - `incident_model.py`: modelo canônico de incidente com validação estrita contra o schema e suporte a lições aprendidas.
    - `sqlite_sink.py`: repositório SQLite com modo WAL, gerenciamento estrito de conexões, métodos `resolve_incident`, busca preventiva `find_lessons` e rotina de purge com `VACUUM` (`purge_learned_incidents`).
    - `supabase_formatter.py`: formatador compatível com PostgREST e gerador de queries de exclusão em lote (`format_supabase_delete_request`).
  - **Suíte de Testes Automatizados (`tests/governance_audit/test_workflow_incident_persistence.py`)**:
    - 13 testes em pytest cobrindo schema, sanitização, banco local SQLite, outbox sync, fail-safe, busca de lições e liberação de espaço (121 testes globais passando, 100% verde).

---

## [2.8.2] — 2026-09-12

### Adicionado & Aperfeiçoado
- **Motor Agnóstico de Migração de Tecnologias Legadas (Agnostic Legacy Migration Engine)**:
  - **Especificação de Requisitos (`docs/requirements/REQ-migration-engine.md`)**:
    - Requisitos funcionais (REQ-001 a REQ-007) com notação EARS e critérios de aceitação Gherkin/BDD, incluindo REQ-007 cobrindo o Bootstrapping Interativo de Novo Projeto com Human-in-the-Loop.
    - Requisitos não-funcionais (RNF-001 a RNF-005) cobrindo desacoplamento estrutural $O(N+M)$, limiar zero de regressão via Dual-Verification, conformidade com ecossistemas de domínio, rastreabilidade e checkpoint humano obrigatório para decisões de build/runtime (RNF-005).
  - **Technical Blueprint & Contratos (`docs/plan/plano-motor-migracao-agnostica.md`)**:
    - Design de pipeline em 3 estágios desacoplados: Source Adapter (extração de legado) → Core Migration Engine (agnóstico) → Target Adapter (geração moderna).
    - Máquina de estados determinística com inclusão formal da sub-rotina Fase 3a (Target Project Bootstrapping via `ask_questions` para escolha de build tool como Maven vs Gradle, versão LTS de runtime e formato de empacotamento).
    - Context Firewall dividindo responsabilidades entre `[CORE_ENGINE_TASKS]`, `[SOURCE_STACK_TASKS]` e `[TARGET_STACK_TASKS]`.
  - **Schema Canônico da Representação Intermediária (`docs/schemas/migration-ir.schema.json`)**:
    - JSON Schema Draft 2020-12 definindo os contratos neutros para `metadata`, `entryPoints`, `domainEntities`, `businessRules` e `characterizationVectors`.
  - **Governança de Workflows (`.github/agents/workflows.md`)**:
    - Formalização do sub-padrão 3.7.1 no `WORKFLOW-FRAMEWORK-MIGRATION` integrando o pipeline agnóstico via IR, o checkpoint interativo da Fase 3a e o gate de Dual-Verification.
  - **Suíte de Testes Automatizados (`tests/governance_audit/test_migration_engine_governance.py`)**:
    - 16 testes unitários e de integração em pytest validando validade do schema, rejeição de payloads incompletos, aprovação de stacks registradas (`struts`, `ejb`, `spring-boot`, `angular`, `python`), rejeição de stacks não cadastradas, contrato de paridade e exigência de confirmação humana para bootstrapping green-field. 100% verde (108 testes da suíte global passando).

---

## [2.8.1] — 2026-09-12

### Adicionado & Aperfeiçoado
- **Geração Integrada de Título e Descrição de Pull Request (`@pr-gatekeeper` e `/commit`)**:
  - **`pr-gatekeeper.agent.md` (v1.1.0 → v1.2.0)**:
    - Atualização do fluxo operacional com passo dedicado para geração de Título de PR no padrão Conventional Commits (≤72 cols, imperativo em PT-BR).
    - Inclusão formal de template estruturado de Descrição de PR contendo: resumo de entregas, tipo de mudança categorizado, matriz de risco avaliada com base no diff, instruções de validação/teste e checklist pré-PR.
    - Sincronização de catálogo em `.github/agents/catalog.yaml` (versão e descrição).
  - **`commit.prompt.md` (v1.3 → v1.4)**:
    - Expansão do PASSO 5 para fornecer, junto à mensagem de commit e comando manual, o Título de PR e a Descrição estruturada de PR pronta para preenchimento na plataforma de Git.
    - Orientações explícitas de entrada para o `CHANGELOG.md` no encerramento da entrega.

---

## [2.8.0] — 2026-09-11

### Adicionado
- **Consolidação de Workflows com Padrões de Mercado (ADLC / Autonomous SDLC 2026 — R-050)**:
  - **Expansão de 5 para 8 Workflows Canônicos e de Ciclo de Vida**: Pesquisa de mercado e benchmarking com padrões corporativos (Anthropic *Building Effective Agents*, Cycode/IBM *Agentic Development Lifecycle - ADLC* e engenharia DevSecOps) identificou e supriu 3 lacunas operacionais críticas de repositórios reais:
    - **`WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION` (WF6)**: remediação determinística de vulnerabilidades SCA e CVEs (`@security-reviewer`), mapeamento de blast radius de dependências (`@code-knowledge-graph`), bump cirúrgico em manifestos/lockfiles (`specialist-developer`), adaptação de breaking changes de bibliotecas (`specialist-bug-fixer`) e quality gate com re-scan de segurança (`runtime-verifier`).
    - **`WORKFLOW-FRAMEWORK-MIGRATION` (WF7)**: condução de elevações estruturais de versão maior de framework ou plataforma (Angular standalone/signals, Spring Boot 2→3, Java 17→21/25, EJB→Spring), com pre-flight assessment (`@tech-solution-architect`), decomposição em fases entregáveis, codemods automatizados no sandbox (`context-mode`), testes de paridade funcional e checkpoints humanos obrigatórios.
    - **`WORKFLOW-RELEASE-READINESS` (WF8)**: pre-flight completo de release e validação pré-deploy, auditando compatibilidade retroativa de contratos OpenAPI (`@tech-solution-architect`), rollout de banco com scripts DDL idempotentes e reversíveis (`@database-specialist`), varredura de segredos e licenças (`@security-reviewer` + `@repo-hygiene-auditor`), packaging semântico com changelog (`@pr-gatekeeper`) e decisão executiva Go/No-Go (`@code-review`).
  - **Sincronização Atômica em Cascata (R-015/R-040/R-050)**:
    - Atualização formal de `workflows.md` (diagrama geral, especificações detalhadas e Typed State Bags para WF6, WF7 e WF8).
    - Inclusão dos 3 pipelines em `routing-graph.yaml` sob o bloco `workflows:`, com expansão das diretrizes de `fast_path_bypass`.
    - Atualização de `CLAUDE.md` (§ R-050 e R-041), `.github/copilot-instructions.md` e `agent-router.agent.md`.
    - Adição de 3 cenários declarativos E2E em `tests/operational_flow/casos-workflows.yaml` (`WF-DEP-001`, `WF-MIG-001`, `WF-REL-001`) e 3 testes específicos em `test_operational_workflows.py`.
    - Validação total da suíte determinística: **92/92 testes passando (100%)** com cobertura de 100% dos workflows (`8/8`).

---

## [2.7.0] — 2026-09-11

### Refatorado & Simplificado
- **Coesão em `.github/` — Simplificação Arquitetural e Desacoplamento Definitivo (Cenário 2)**:
  - **Extinção de `docs/ai-context/catalog.yaml` e `docs/ai-context/binding.md`**: Eliminação de manifestos intermediários redundantes. Os adapters genéricos agora são 100% autodeclaratórios via frontmatter YAML nativo `applyTo` nos próprios arquivos `.instructions.md`, lidos diretamente pelo GitHub Copilot e demais IDEs.
  - **Catálogo Único de Agents (`.github/agents/catalog.yaml`)**: Fim da colisão de nomes. O repositório passa a ter estritamente **um** arquivo `catalog.yaml`, eliminando a necessidade de desambiguações em prompts e no `repo-map.md`.
  - **Migração do Overlay Local de Projetos**: Substituição de `docs/ai-context/catalog.local.yaml` por `.github/projects.local.yaml` (gitignored, R-043) e de seu template rastreado para `.github/projects.local.yaml.example`.
  - **SSOT de Binding Consolidado (`.github/instructions/README.md`)**: O índice de instructions absorveu formalmente todas as definições da hierarquia de 3 camadas (Global $\rightarrow$ Stack $\rightarrow$ Projeto), discovery de IDEs e ciclo de vida de projetos locais.
  - **Extinção do `repo-map.md` e Consolidação Nativa**: O arquivo `repo-map.md` foi integralmente absorvido e extinto. A árvore física oficial do repositório foi incorporada ao `README.md` raiz (para humanos) e os caminhos canônicos consolidados na seção 7 de `CLAUDE.md` e `.github/copilot-instructions.md` (para IAs), eliminando mais um ponto de manutenção e duplicação.
  - **Remoção Completa do Diretório `docs/ai-context/`**: Diretório extinto por completo, concentrando toda a configuração e governança de IA sob `.github/`.
  - **Sincronização em Cascata (R-015/R-043/R-046)**: Atualização atômica de `.gitignore`, `.githooks/pre-commit`, `CLAUDE.md` (R-034 e R-043), `.github/copilot-instructions.md`, todos os agents e prompts operacionais, scripts de tooling e suíte de testes (`test_local_project_isolation.py`, `test_governance_smells.py`, `test_routing_quality_gate.py`), mantendo 100% de conformidade e 89/89 testes aprovados no pytest.

---

## [2.6.2] — 2026-09-11

### Adicionado
- **Prompt `/init-context` — Verificação de Deriva de Stack e Instruções Locais (Drift Detection)**:
  - Adicionado novo PASSO 7 (expandindo a execução para 9 passos) para detectar discrepâncias entre os manifestos reais dos projetos locais externos (`package.json`, `pom.xml`, `build.gradle`, `pyproject.toml`) e os adapters locais em `.github/instructions/local/<projeto>.instructions.md` (R-043).
  - Identifica automaticamente upgrades de versão major de frameworks (ex.: Angular 20 → 21, Spring Boot 2.x → 3.x) e migrações de test runners/bibliotecas (ex.: Karma/Jasmine → Vitest, JUnit 4 → JUnit 5, Jest → Vitest).
  - Adiciona remediação guiada interativa via `ask_questions` (R-009) para sincronização do adapter local, linha dedicada na tabela de checklist consolidada, recomendações e troubleshooting.
  - Inclusão da tool `ask_questions` em `tools:` e de `.github/skills/project-scanner/SKILL.md` em `source_docs:` do prompt.

---

## [2.6.1] — 2026-09-11

### Refatorado
- **Desacoplamento de Cardinalidade Normativa (Herança Aberta de Governança)**:
  - Substituição da referência rígida ao contador fechado (`R-001..R-051`) pela herança aberta desacoplada (`regras normativas globais em CLAUDE.md`) em 45 agents/templates e todos os prompts e catálogos.
  - Eliminação definitiva do problema de *Shotgun Surgery* (manutenção em cascata e gasto desnecessário de créditos Copilot a cada nova regra adicionada ao `CLAUDE.md`).
- **Redefinição do Smell 2.15 (`governance-audit-patterns/SKILL.md` & `test_governance_smells.py`)**:
  - Inversão de sentido do Smell 2.15 de "range desatualizado" para "Acoplamento Rígido de Range Normativo (Hardcoded Range Coupling)".
  - Nova validação automatizada em `test_smell_2_15_no_hardcoded_normative_rule_range`: exige que todo agent herde `CLAUDE.md` e proíbe a reintrodução de ranges numéricos hardcoded em agents.

---

## [2.6.0] — 2026-09-10

### Adicionado
- **Suíte de Testes de Conformidade de Templates (Disjunção 1-de-N)**:
  - `tests/governance_audit/test_template_sections.py`: Implementação estática da regra de conformidade polimórfica (Smells 2.9, 2.10 e 2.11), validando seções de agents, prompts e skills contra os templates canônicos com extração dinâmica e normalização semântica.
  - `tests/governance_audit/test_router_agents.py`: Validação determinística especializada para os 6 agents com perfil de Router / Supervisor (`agent-router`, `angular-router`, `spring-boot-router`, `spring-reactive-router`, `ejb-router`, `database-router`), exigindo as 6 seções obrigatórias e menor privilégio de ferramentas.
  - Template canônico oficial para roteadores em `.github/agents/templates/router-agent.md`.
- **Suíte de Testes de Trajetórias de Workflows Canônicos (R-050) & Simulador MAS**:
  - `tests/operational_flow/casos-workflows.yaml`: Catálogo declarativo com 8 cenários de ponta a ponta (E2E) cobrindo os 5 workflows canônicos, detecção de deriva de intenção (R-042), circuit breaker (R-050.2) e fast-chaining (R-050.1).
  - `tests/operational_flow/test_workflow_trajectories.py`: Validação determinística das transições de estados, isolamento de ferramentas por etapa e thresholds de cobertura (100% workflows, ≥85% etapas, ≥15 agentes).
  - `tests/operational_flow/workflow_eval_simulator.py`: Motor CLI para auditoria estática de trajetórias em lote e cálculo em tempo real das 5 dimensões de cobertura de MAS (`--coverage`).
  - `.github/prompts/eval-workflows.prompt.md`: Prompt operacional parametrizado para avaliação de trajetórias via modelo `Gemini 3.8 Flash`.
- **Documentação Arquitetural de Testes MAS (`tests/README.md`)**:
  - Documentação completa da Pirâmide de Testes de Sistemas Multi-Agentes (MAS), detalhamento arquivo por arquivo, objetivos de qualidade, métricas de cobertura e guia de execução.

### Alterado
- **Configuração do Pytest (`pytest.ini`)**:
  - Inclusão da diretiva `pythonpath = .` garantindo resolução determinística da raiz do projeto independente da forma de invocação do runner.

---

## [2.5.0] — 2026-09-10

### Adicionado
- **Mapa do Repositório Canônico (`docs/ai-context/repo-map.md`)**:
  - Fonte de verdade de navegação determinística de arquivos (princípio Zero Blind Searches), contendo guia de localização direta, tabela rápida de arquivos de governança (Quick File Finder) e árvore física estrutural do projeto.
- **Whitelist de Busca e Indexação para ripgrep (`.ignore` e `.rgignore`)**:
  - Arquivos de configuração na raiz liberando a varredura de `!.github/` e `!.github/**` pelas ferramentas de busca (`file_search` e `grep_search`), sanando falhas de localização com 0 matches de agents e skills em workspaces multi-root.

### Alterado
- **Desambiguação Canônica dos Catálogos (`catalog.yaml`)**:
  - Formalizada a distinção unívoca entre o Catálogo de Agents (`.github/agents/catalog.yaml` — metadados, modelos Gemini/Claude, prioridades) e o Catálogo de Binding (`docs/ai-context/catalog.yaml` — manifest de stacks e adapters).
  - Atualizadas as instruções em `CLAUDE.md`, `.github/copilot-instructions.md` e `.github/agents/agent-router.agent.md` proibindo explicitamente que o router busque modelos em `docs/ai-context/catalog.yaml`.
  - Inclusão do `repo-map.md` como leitura de infraestrutura mandatória no `@agent-router`.

---

## [2.4.0] — 2026-09-10

### Adicionado
- **Novos Smells de Governança (20 Smells Canônicos)** — originados de auditoria real do primeiro ciclo completo de `WORKFLOW-FEATURE-DEVELOPMENT` (feature de Gestão de Usuários/Auditoria Global no projeto de referência):
  - **Smell 2.18 (Gap de Definição de Pronto — Feature Não-Alcançável / Rota Órfã de Navegação)**: nenhum artefato do pipeline (blueprint, implementer, test-strategy, code-review) tratava "alcançabilidade via navegação" como critério de conclusão — feature entregue com testes verdes e build íntegro, porém sem entrada correspondente no menu/sidenav do projeto.
  - **Smell 2.19 (Ausência de Verificação de Reuso de Design System / Componentes Compartilhados)**: agent implementer de UI criou HTML/CSS customizado (`<select>` nativo, cards/badges ad-hoc) ignorando catálogo interno de componentes compartilhados já documentado no projeto (`docs/componentes-shared.md`, `docs/padrao-angular-material.md`).
  - **Smell 2.20 (Duplicação por Aninhamento de Router — Nested Subagent Sprawl)**: identificada e eliminada a duplicação na cadeia de orquestração onde o `@agent-router` invocava executores downstream via `run_subagent` por dentro de si mesmo e, ao retornar ao Orquestrador Raiz com o bloco de decisão, o orquestrador re-disparava o mesmo downstream. Formalizada a regra de Delegação Plana (Flat Delegation) em R-047, R-037, `agent-router.agent.md` e `handoff-governance/SKILL.md` (§ 2.3), acompanhada de teste estático determinístico no Tier 1 (`test_smell_2_20_router_flat_delegation_rule`).
- **Reforço de Definition of Done em Frontend**: `angular-implementation-patterns/SKILL.md` ganha passo 0 (Reuse-First) e passo 7 (Navegabilidade) no Workflow — Feature Nova, com checklist de PR e anti-padrões correspondentes.
- **Princípio Reuse-First**: `frontend-componentization-patterns/SKILL.md` ganha nova seção "Reuso-First: Antes de Criar Componente Novo" com processo objetivo de busca em `shared/`/documentação interna antes de qualquer HTML/CSS customizado.
- **8ª Dimensão de Code Review**: `code-review-patterns/SKILL.md` § 2 ganha dimensão "UX/Design System & Navegabilidade", cobrindo os Smells 2.18/2.19 na revisão de diffs de frontend.
- **Template Canônico Completado em 2 Agents**: `angular-feature-developer.agent.md` e `angular-ui-stylist.agent.md` — únicos 2 agents do catálogo Angular sem `Decision Tree`/`Checklist Antes de Entregar`/`Quando Delegar` — receberam as 3 seções ausentes (Smell 2.9 aplicado retroativamente).
- **Reforço em `tech-solution-architect.agent.md`**: Context Firewall `[FRONTEND_TASKS]` e Checklist Antes de Entregar agora exigem explicitamente tarefa de integração ao shell de navegação e consulta prévia a design system compartilhado quando a feature introduzir rota(s)/UI nova(s).
- **Reforço em `code-review.agent.md`**: novo branch no Decision Tree e item 6 nos Padrões Obrigatórios para validar navegabilidade e reuso de design system antes do veredito em diffs de frontend.
- **Reforço em `test-strategy.agent.md`**: item 5 dos Padrões Obrigatórios exige cenário de Navegabilidade na Matriz de Cenários Frontend quando houver rota nova.
- **Adapter Local Corrigido (`[PROJETO-ALVO].instructions.md`)**: novas seções § 1.1 (Design System Interno — Consulta Obrigatória) e § 1.2 (Navegação — SidenavComponent/Shell como Única Fonte de Verdade), referenciando explicitamente a documentação interna de componentes/design system e o componente de shell de navegação do projeto — o adapter não continha nenhuma dessas referências antes desta correção, apesar de os documentos já existirem no projeto.

### Autocrítica de Processo (Achado de Execução)
- Identificado e documentado que a fidelidade de handoff da Etapa 5 (`tdd_domain_implementation`) de `WORKFLOW-FEATURE-DEVELOPMENT` depende de invocação **real** de `run_subagent` para o specialist correspondente — rotular a resposta com `Agente Ativo: <specialist>` sem a invocação real não carrega o contrato/checklist do agent, tornando as correções de conteúdo insuficientes por si só sem a disciplina de delegação genuína já normatizada em R-042.

---

## [2.3.0] — 2026-09-10

### Adicionado
- **Regra Normativa R-051 (Proteção Anti-Corrupção em Edição de Arquivo Único Grande/Estruturado)**: Formalizada em `CLAUDE.md` e `efficient-batch-code-modification/SKILL.md` (§ 5). Veda o uso de `insert_edit_into_file` em arquivos com mais de 200 linhas, formato YAML/JSON ou consumidos por CI/testes, exigindo o Padrão de Edição Segura Verificada (leitura integral, contagem unívoca de ocorrência da âncora, all-or-nothing write e releitura de confirmação).
- **Snippet Canônico de Edição Segura (`safe-single-file-edit-pattern.js`)**: Materializado em `.github/skills/efficient-batch-code-modification/snippets/safe-single-file-edit-pattern.js` como template reutilizável para context-mode (`ctx_execute`), em estrita conformidade com R-026 (código real fora do corpo da skill).
- **Novos Smells de Governança (17 Smells Canônicos)**:
  - **Smell 2.15 (Citação de Range Normativo Desatualizado — Drift de R-0XX)**: Formalizada em `governance-audit-patterns/SKILL.md` e amparada por teste determinístico no Tier 1 (`test_smell_2_15_no_stale_normative_rule_range`), que lê dinamicamente o maior R-0XX de `CLAUDE.md` e bloqueia desatualizações nos agents.
  - **Smell 2.16 (Agent Mutativo Sem Skill de Edição Segura Referenciada)**: Formalizada em `governance-audit-patterns/SKILL.md` e amparada por teste determinístico no Tier 1 (`test_smell_2_16_mutating_agents_reference_safe_editing_skill`), exigindo que todo agent com tools mutativas referencie `efficient-batch-code-modification`.
- **Transparência de Base de Conhecimento — Terceira Linha do Banner Universal (`Skills Carregadas`)**: Estendido o Banner Universal de Identidade em `CLAUDE.md` (R-042), `agent-contracts/SKILL.md` (§ 0 e § 8), `.github/copilot-instructions.md` e `handoff-governance/SKILL.md` (§ 5.2) para exibir compulsoriamente a linha `Skills Carregadas: <skill-1>, ...` em cada resposta, garantindo visibilidade no chat sobre quais skills foram pre-fetched e consultadas a cada turno.

### Evoluído
- **Auditoria e Refinamento Profundo dos 5 Workflows Canônicos (`workflows.md` e `routing-graph.yaml`)**:
  - **Resolução de Papéis Genéricos (`specialist-<papel>`)**: Formalizada convenção em `workflows.md` § 1.3 mapeando papéis agnósticos de stack (fixer, tester, stylist, implementer, advisory) para os agentes concretos dos sub-catálogos locais (`angular-catalog.yaml`, `spring-boot-catalog.yaml`, `spring-reactive-catalog.yaml`, `ejb-catalog.yaml`).
  - **Princípio Arquitetural de Separação Declarador/Executor em Circuit Breakers**: Formalizado em `workflows.md` § 5 (Invariante #6) e § 8.1. Agentes estritamente read-only (`runtime-verifier`, `refactor-planner`) apenas detectam e declaram vereditos de bloqueio; a execução física de reversão atômica (`git checkout`/`git restore`) é sempre executada pelo especialista de implementação correspondente via `run_subagent`.
  - **WF1 (`WORKFLOW-BUG-FIX`)**: Repro Gate com teto de 2 tentativas e estado terminal Não-Reproduzível; distinção entre testes unitários puros vs testes exigindo contexto de framework/DOM; checkpoint de segurança condicional (R-048.1) para correções que toquem autenticação/identidade.
  - **WF2 (`WORKFLOW-REFACTORING`)**: Safety net com cobertura orientada a risco (`test-coverage-governance/SKILL.md`) em substituição ao threshold plano de 80%; checkpoint de aprovação humana para breaking change, schema ou blast radius grande; limite de escala do DAG Mikado em 15 nós; rollback atômico e incremental decidido pelo planner e executado pelos specialists.
  - **WF3 (`WORKFLOW-TECHNICAL-ANALYSIS`)**: Inclusão de `devops-engineer` e `code-style-enforcer` no dispatch analítico; suporte a Fan-out/Fan-in multidimensional (`[P]`); teto de profundidade em sub-rotinas (`MAX_DEPTH = 3`); escape hatch formal para análises sem achados (`"nenhuma_proposta_necessaria_conformidade_validada"`).
  - **WF4 (`WORKFLOW-FEATURE-DEVELOPMENT`)**: Sequenciamento de requisitos (`@requirements-analyst`) e decomposição (`@feature-planner`); sub-rotina de banco (`@database-specialist`); particionamento com tags de stack; shift-left de testes de segurança em TDD; circuit breaker de 2 tentativas no loop de remediação de segurança.
  - **WF5 (`WORKFLOW-GOVERNANCE-MAINTENANCE`)**: Sincronização atômica estruturada por tipo de artefato, corrigindo a omissão de `evals/casos-roteamento.yaml` para novos agents (R-040); circuit breaker de 3 tentativas no loop de autofix.
- **Sincronização de Ranges Normativos**: Atualizados 100% dos 44 agents com seção de regras herdadas e todos os prompts e catálogos para a numeração consolidada `R-001..R-051`.
- **Expansão de Isolamento Read-Only**: `READONLY_ADVISORY_AGENTS` expandido de 8 para 17 agents em `test_operational_workflows.py`, blindando especialistas consultivos contra tools mutativas.

---

## [2.2.0] — 2026-09-10

### Adicionado
- **Regra Normativa R-050 (Workflows Operacionais Determinísticos — Pipelines de Estado Finito)**: Formalizada em `CLAUDE.md` a obrigatoriedade de vincular e executar toda solicitação técnica através de um dos 5 Workflows Canônicos:
  1. `WORKFLOW-BUG-FIX` (Bugs, Erros 500/NPE, Falhas de Layout e Regressões em 5 etapas).
  2. `WORKFLOW-REFACTORING` (Refatoração Estrutural, Modernização e Desacoplamento em 5 etapas).
  3. `WORKFLOW-TECHNICAL-ANALYSIS` (Análise Técnica, Diagnóstico e Auditoria Especializada em 3 etapas).
  4. `WORKFLOW-FEATURE-DEVELOPMENT` (Nova Feature e Evolução Funcional E2E em 6 etapas).
  5. `WORKFLOW-GOVERNANCE-MAINTENANCE` (Auditoria, Padronização e Manutenção de Governança em 3 etapas).
- **Especificação Canônica dos 5 Workflows (`.github/agents/workflows.md`)**: Novo artefato canônico com diagramas Mermaid em `flowchart TD`, matrizes de entrada/saída, regras de não-desvio e invariantes de execução.
- **Roadmap Visual de Execução no Chat (Anti-Cegueira de Fluxo)**: Padronizada no `@agent-router`, `agent-contracts` (§ 0.1) e `workflows.md` (§ 6) a exibição compulsória do bloco visual `### 🗺️ Pipeline de Execução do Workflow (<total> etapas)` com marcadores `[✅]` (Concluído), `[▶]` (Em Andamento) e `[⏳]` (Pendente) para eliminar a cegueira do usuário durante o fluxo.
- **Extensão de Handoff v1.2 (`workflow_tracking`)**: Adicionado ao schema formal de `handoff-governance` o bloco `workflow_tracking` (`workflow_id`, `etapa_atual`, `total_etapas`, `nome_etapa`, `proximos_agentes_permitidos`, `politica_desvio: "strict"`).
- **Protocolo de Encadeamento de Workflows (Fast-Chaining — R-050.1)**: Reconhecimento de aprovações/ordens de execução de diagnósticos prévios no `@agent-router`, transferindo `carry_over_state` diretamente para a Etapa 1 do workflow de implementação sem desvio para `@prompt-structuring`.
- **Estados de Contingência & Circuit Breaker (R-050.2)**: Inclusão de caminhos formais de rollback (4b em bugfix e 5b em refatoração) nos diagramas e contratos para reversão atômica de diffs sujos e escalação humana via `ask_questions` após esgotar o teto de 3 tentativas de teste ou violar regras de negócio.
- **Rastreamento Multi-Projeto no Handoff (v1.3 — R-050.3)**: Extensão do `workflow_tracking` com `projeto_alvo` (`id`, `root_path`, `adapter_ref`) e `chaining` para garantir isolamento em workspaces multi-repositório.
- **Nova Suíte de Testes de Isolamento de Projetos Locais (`test_local_project_isolation.py`)**: 5 novos testes automatizados determinísticos cobrindo 100% das regras R-038, R-043 e R-044 (varredura de git-tracked files, gitignore guardrails, caminhos de máquina reais e genericidade de placeholders).
- **Verificação #5 no Pre-commit Hook (`.githooks/pre-commit`)**: Bloqueio ativo no commit contra menções a projetos registrados em `catalog.local.yaml`.
- **Testes de Conformidade de Workflows**: 8 testes determinísticos em `tests/operational_flow/test_operational_workflows.py` validando workflows, integridade de `workflows.md`, declaração no grafo, fast-chaining, circuit breaker e rastreamento de projeto-alvo.
- **Novos Casos na Suíte de Evals**: `canon-043` (layout e erro runtime), `canon-044` (refactor com alvo) e `regr-026` (bloqueio de desvio de bugs para `prompt-structuring`) em `.github/agents/evals/casos-roteamento.yaml`.

### Evoluído
- **Regra Normativa R-041 (Fast-Path Determinístico)**: Ajustada em `CLAUDE.md`, `copilot-instructions.md`, `routing-graph.yaml` e `agent-router.agent.md` para permitir que solicitações com intenções operacionais evidentes (bugs, refatoração com alvo, diagnósticos diretos) bypassam o `@prompt-structuring` diretamente para a etapa 1 do workflow, eliminando latência e perguntas redundantes.
- **Agent Router (`@agent-router` v2.0.0)**: Inserido Passo 0.4 (Classificação de Fast-Path) antes do Passo 0.5 e inclusão de `Workflow:` e `Etapa do Workflow:` no Formato de Saída.
- **Grafo Estrutural (`routing-graph.yaml`)**: Adicionado bloco de primeira classe `workflows:` declarando estados finitos e inclusão de `fast_path_bypass` na aresta de `prompt-structuring`.

---

## [2.1.0] — 2026-09-06

### Adicionado
- **Regra Normativa R-046 (Injeção Compulsória de Modificação de Código em Lote)**: Formalizada em `CLAUDE.md` a obrigatoriedade da skill operacional `efficient-batch-code-modification` em toda tarefa que envolva escrita, refatoração ou alteração em massa de código, erradicando loops sequenciais de roundtrip e reenvio recursivo de contexto.
- **Injeção Compulsória em `prompt-structuring` (R-046)**: Adicionado mecanismo no refinamento de prompt para injetar nativamente a constraint de dry-run prévio em memória, single-turn batching e diffs cirúrgicos em `<constraints>` para qualquer tarefa de código sem exigir intervenção manual do usuário.
- **Novo Agente `@governance-maintainer` (v1.0.0)**: Especialista executor em manutenção atômica, refatoração estrutural e sincronização em lote de artefatos de governança (`.github/agents`, `.github/skills`, `.github/prompts`, catálogos e grafo de roteamento). Opera sob o protocolo de single-turn batching e priorização de context-mode sobre terminal.
- **Nova Skill `efficient-batch-code-modification` (Tier 1, Process)**: Protocolo operacional para economia de tokens e créditos Copilot — análise prévia em memória (dry-run), tool calls de escrita emitidas em lote na mesma rodada e diffs cirúrgicos mínimos.

### Evoluído
- **Agents Executores de Código Alinhados a R-046**: Inclusão explícita de `efficient-batch-code-modification` em `source_docs`, `skills:` e diretrizes operacionais de 26 agents (database-specialist e 25 especialistas de domínio em frontend/angular, backend/spring-boot, backend/spring-reactive e backend/ejb).
- **Evolução de `analysis-architect` para `tech-solution-architect` (v2.1.0)**:
  - Adotado o padrão consolidado de mercado *Spec-First / Technical Blueprint* e *Context Firewall* (particionamento isolado `[BACKEND_TASKS]` e `[FRONTEND_TASKS]` para eliminar alucinações e perda de contexto downstream).
  - Escopo: Viabilidade técnica, elaboração de Blueprint, contratos OpenAPI/AsyncAPI, modelo de dados (Flyway) e divisão de tarefas por stack antes do despacho aos Domain Routers.
  - Sincronização atômica de governança (R-015/R-040): atualizados `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md`, `casos-roteamento.yaml` (novo `canon-036`), `requirements-analyst.agent.md`, `feature-planner.agent.md`, `refactor-planner.agent.md`, `code-review.agent.md`, `test-strategy.agent.md`, `bug-triage.agent.md`, `code-knowledge-graph.agent.md`, `copilot-instructions.md`, `CLAUDE.md`, `README.md` e `.index.json`.
  - Substituição do arquivo `analysis-architect.agent.md` por `tech-solution-architect.agent.md`.

### Consolidado
- **Consolidação Biparadigma de Modelos nos Agents e Prompts**:
  - **Paradigma do Prompt Procedural (SLMs / Alta Velocidade — Padrão Base)**: Definido `"Gemini 3.8 Flash"` como escolha padrão em toda a base (54 agents e 16 prompts procedurais/determinísticos: implementadores TDD, fixers, test-writers, geradores de adapters, linters/enforcers, scanners e roteadores de domínio).
  - **Paradigma do Prompt Decompositivo / Raciocínio Guiado (Pensamento Profundo)**: Reservado `"Claude Sonnet 5"` exclusivamente para perfis deliberativos de alta complexidade:
    - **Orquestração e Triagem Central**: `@agent-router` (agent e prompt `/agent-router`).
    - **Arquitetura Técnica & Blueprint**: `@tech-solution-architect`.
    - **Planejamento Decompositivo & Rollback**: `@refactor-planner` e prompt `/plan`.
    - **Elicitação & Decomposição Crítica de Requisitos**: `@requirements-analyst`.
    - **Pesquisa Multi-hop & Síntese Deliberativa**: `@deep-search` (agent e prompt `/deep-search`).
    - **Especialistas de Arquitetura Consultiva (Advisors)**: `@angular-arch-advisor`, `@spring-boot-arch-advisor`, `@spring-reactive-arch-advisor`, `@ejb-arch-advisor`.
  - Sincronização atômica (R-015) em todos os catálogos (`catalog.yaml`, `angular-catalog.yaml`, `spring-boot-catalog.yaml`, `spring-reactive-catalog.yaml`, `ejb-catalog.yaml`) e na skill `governance-factory-patterns/SKILL.md` (§ 9.1).
  - Validação via `get_errors` com 0 erros em todos os arquivos modificados.

## [2.0.0] — 2026-09-06

### Adicionado
- **Arquitetura Hierárquica de Routers de Domínio**: Decomposição de agentes monolíticos em ecossistemas de domínio com sub-catálogos locais e isolamento em pastas:
  - **Frontend Angular (`.github/agents/frontend/angular/`)**: Supervisor `angular-router` + sub-catálogo `angular-catalog.yaml` + 8 especialistas (`angular-arch-advisor`, `angular-feature-developer`, `angular-bug-fixer`, `angular-ui-stylist`, `angular-unit-test-writer`, `angular-component-test-writer`, `angular-test-fixer`, `angular-e2e-writer`).
  - **Backend Spring Boot (`.github/agents/backend/spring-boot/`)**: Supervisor `spring-boot-router` + sub-catálogo `spring-boot-catalog.yaml` + 7 especialistas (`spring-boot-arch-advisor`, `spring-boot-feature-developer`, `spring-boot-bug-fixer`, `spring-boot-perf-tuner`, `spring-boot-unit-test-writer`, `spring-boot-integration-test-writer`, `spring-boot-test-fixer`).
  - **Backend Spring Reactive (`.github/agents/backend/spring-reactive/`)**: Supervisor `spring-reactive-router` + sub-catálogo `spring-reactive-catalog.yaml` + 7 especialistas (`spring-reactive-arch-advisor`, `spring-reactive-feature-developer`, `spring-reactive-bug-fixer`, `spring-reactive-resilience-tuner`, `spring-reactive-unit-test-writer`, `spring-reactive-integration-test-writer`, `spring-reactive-test-fixer`).
  - **Backend Java Legado EJB (`.github/agents/backend/ejb/`)**: Supervisor `ejb-router` + sub-catálogo `ejb-catalog.yaml` + 7 especialistas (`ejb-arch-advisor`, `ejb-feature-developer`, `ejb-bug-fixer`, `ejb-perf-tuner`, `ejb-unit-test-writer`, `ejb-integration-test-writer`, `ejb-test-fixer`).
- **Suporte a `type: stack` no `@governance-factory`**: Nova capacidade de geração de ecossistemas tecnológicos completos estruturados em pastas de domínio com sub-catálogo, router e especialistas canônicos, com pesquisa prévia compulsória via `@deep-search` e sincronização atômica global (R-015).
- **Smell 2.7 (Desalinhamento Contratual: Perfil ↔ Tools ↔ Skills ↔ Catálogo) em `governance-audit-patterns`**: Nova regra de conformidade com Matriz Canônica § 2.7.1 auditando papéis, permissões de escrita, tooling de terminal (`terminal-governance`), MCP `context-mode` e sincronismo atômico com o catálogo. Remediação executada com 100% de conformidade nos 33 agentes de frontend e backend.
- **Dois Fluxos Canônicos de TDD com `@test-strategy`**:
  - *Fluxo 1 (Cross-cutting Gateway)*: `@agent-router` aciona `@test-strategy` para matriz unificada antes de despachar aos routers de frontend/backend.
  - *Fluxo 2 (Consulta Interna de Domínio)*: Routers de domínio consultam `@test-strategy` internamente via `run_subagent` antes de acionar seus test-writers.

### Removido
- Descomissionamento dos agentes monolíticos substituídos pela nova topologia hierárquica: `angular-engineer.agent.md`, `spring-boot-engineer.agent.md`, `spring-reactive-engineer.agent.md` e `test-engineer.agent.md`.

---

## [1.9.0] — 2026-09-04

### Adicionado
- **`tools/context-insight-visualizer/`**: Suíte analítica completa e dashboard standalone (HTML/CSS/JS puro com design tokens do Angular Material 3 Dark Theme e gerador em Python) para métricas locais do Context Mode MCP (`sessions/*.db`, `stats-pid-*.json`, `content/*.db`). Replicando a arquitetura validada de `tools/codegraph-visualizer/` (zero dependências npm em runtime, zero lock-in SaaS, execução offline via `file://`).
  - **Sidebar M3 com 5 Visões Profissionais**:
    - `Dashboard`: Top KPIs (Sessões, R:W Ratio, Compact Rate, Error Rate, PPS), Heatmap 24h ("When You Code"), Volume temporal e cards de Insights determinísticos (`Nice`, `Heads up`, `Fix this`, `FYI`).
    - `Knowledge Base`: Catálogo de 250+ fontes indexadas agrupadas por recência (*Hoje, Ontem, Esta Semana, Anteriores*), proporção de código e modal de inspeção de chunks.
    - `Sessions & Decisions`: Auditoria cronológica de sessões, timeline de eventos com prioridade e **Diário de Decisões Técnicas** com exportação direta para Markdown (`.md`).
    - `Search`: Mecanismo de busca unificado na memória local com destaque em tempo real sobre fontes, decisões técnicas e sessões.
    - `Enterprise`: Painel executivo com matriz de personas de liderança (CTO, EM, DevEx, CISO, QA, Developer) calculando ROI, economia financeira e conformidade.
  - `schemas/insight-data.schema.json`: contrato formal de dados unificado (JSON Schema draft 2020-12) validando todas as estruturas.
  - `generator/`: motor de extração multi-DB com fallback de diretórios, cálculo de KPIs executivos, diário de decisões e empacotador de HTML.

---

## [1.8.0] — 2026-08-30

### Adicionado
- **`agent-contracts/SKILL.md` § 0 — Banner Universal de Identidade (Visibilidade de Fluxo)**: nova regra de ouro — toda resposta de TODO agent (não apenas `agent-router`) abre com `Agente Ativo: <name>`; se resultado de handoff/re-triagem, uma segunda linha declara `Handoff: <origem> → <destino> (motivo: ...)`. Baseado em pesquisa de mercado 2026 (Tavily): LangGraph "Stream the Active Agent" (campo `active_agent` no state, streamado ao usuário) e OpenAI Agents SDK (`HandoffOutputItem` imprimindo "Handed off from X to Y").
- **`agent-router.agent.md`**: novo campo `Transição` no Formato de Saída, explicitando "Nova triagem (1º turno)" | "`<origem>` → `<atual>` (motivo: deriva_de_intencao)" | "Sem mudança".

### Corrigido
- **Gap de visibilidade em R-042**: antes desta correção, apenas o `agent-router` declarava "Agente Ativo" — um agent downstream em `task_mode` por vários turnos consecutivos não reafirmava quem estava respondendo, deixando o usuário sem visibilidade do fluxo. Corrigido nos 23 agents downstream (parágrafo "Banner obrigatório" inserido na seção já existente "Retorno ao Router", via script Node.js determinístico) e nos 2 templates (`research-agent.md`, `operational-agent.md`) usados pelo `agent-factory` para gerar novos agents.

### Alterado
- **`agent-factory.agent.md`**: Padrões Obrigatórios (item 10), Checklist e Formato de Saída passam a validar a presença do banner em todo agent criado/revisado.
- **`CLAUDE.md` (R-042)**, **`copilot-instructions.md`** (fluxo garantido) e **`agents/README.md`** § 8 — formalizam a exigência de visibilidade turno a turno.
- **`handoff-governance/SKILL.md`** § 5.2 — referência cruzada ao banner de identidade.

---

## [1.7.0] — 2026-08-30

### Corrigido
- **Gap estrutural de tooling para R-042**: `run_subagent` era ausente no frontmatter `tools:` de 3 agents (`agent-factory`, `adapter-generator`, `binding-initializer`) — sem essa tool, o handoff de retorno a `@agent-router` descrito em prosa na seção "Retorno ao Router" nunca era executável de fato. Corrigido nos 3 agents.
- **Causa raiz nos templates**: `templates/research-agent.md` (tools com nomenclatura não-canônica `[Read, Grep, Glob]`, sem `run_subagent`, sem seção "Retorno ao Router") e `templates/operational-agent.md` (sem `run_subagent`, seção "Retorno ao Router" totalmente ausente) — todo agent novo criado por `agent-factory` herdava o gap. Ambos corrigidos.

### Adicionado
- **`agent-contracts/SKILL.md` § 9 — Ferramentas Mínimas por Agent (Tooling Baseline)**: tabela de tools mínimas obrigatórias por perfil (Router, Analista, Especialista, Operacional); regra de ouro — `run_subagent` é obrigatório e bloqueante em TODO agent, sem exceção.
- **`agent-factory.agent.md`**: valida a nova regra em Padrões Obrigatórios (itens 8-9), Checklist Antes de Codar e Formato de Saída — nenhum agent é finalizado sem `run_subagent` no frontmatter e sem a seção "Retorno ao Router".

### Alterado
- **`CLAUDE.md` (R-042)**, **`copilot-instructions.md`** e **`agents/README.md`** § 8 — adicionado o pré-requisito estrutural: o handoff de retorno só é efetivo via chamada real de `run_subagent`, não apenas descrito em texto.

---

## [1.6.0] — 2026-08-30

### Alterado
- **Especialistas `angular`, `spring-boot`, `spring-reactive` migrados de perfil "advisory puro" para perfil HÍBRIDO (v2.0.0)**: além de análise/recomendação, agora também implementam feature nova e correção de bug dentro do próprio domínio de stack, seguindo padrões de mercado consolidados via pesquisa Tavily 2026.
- **Testing-first obrigatório** em modo Implementação: nenhum dos 3 agents pode reportar sucesso sem teste escrito/atualizado e suíte executada localmente.
- **`agent-router` / `routing-graph.yaml` / `CLAUDE.md` (R-042)**: condição `intent_drift_detected` ajustada — implementação **dentro** do domínio de stack do specialist não é mais deriva de intenção; deriva só ocorre em pivô **cross-stack** (ex.: `@angular` recebe pedido de código Spring Boot) ou pedido fora do domínio técnico.

### Adicionado
- **3 novas skills de implementação** (Tier 2, pesquisa de mercado 2026 via Tavily):
  - `angular-implementation-patterns` — fronteira Signals/RxJS, testing-first, checklist de PR.
  - `spring-boot-implementation-patterns` — matriz de decisão virtual threads vs reativo, N+1/OSIV, DTOs de borda.
  - `spring-reactive-implementation-patterns` — composição não-bloqueante, operadores de erro (`onErrorResume`/`onErrorMap`/`retryWhen`), `StepVerifier`/`WebTestClient`.
- **`tools:`** dos 3 agents expandidas com `create_file`, `insert_edit_into_file`, `get_errors`, `run_in_terminal`.
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-018` (implementação direta de bugfix), `regr-014` corrigido (implementação no próprio domínio não é deriva), `regr-016` novo (deriva real cross-stack) — suíte passa de 35 para 40 casos.

### Corrigido
- **SYNC (R-015)**: `.github/skills/.index.json` — corrigido gap pré-existente onde as 3 skills de análise (`angular-frontend-patterns`, `spring-boot-backend-patterns`, `spring-reactive-webflux-patterns`) nunca haviam sido registradas; total_skills 39 → 45 (3 análise + 3 implementação novas).
- **SYNC**: `catalog.yaml` (agents), `agents/README.md`, `copilot-instructions.md`, `handoff-governance/SKILL.md` § 5 — todas as referências a "sem implementação"/"advisory puro" para os 3 specialists atualizadas para refletir o perfil híbrido.

---



### Adicionado
- **R-042 (Re-triagem Obrigatória por Turno — Anti Sticky-Session)**: R-037 passa a se aplicar explicitamente a **cada novo turno**, não só ao primeiro. Fecha o gap relatado onde um agent downstream (ex.: `requirements-analyst`) continuava respondendo sozinho mesmo quando o pedido do usuário mudava de fase (requisito→implementação, análise→código, revisão→correção).
- **Seção "Retorno ao Router"** adicionada nos 23 agents downstream/specialist (atualização atômica, R-015): cada agent declara gatilho objetivo de deriva de intenção e retorna a `@agent-router` via handoff (`handoff-governance` § 2.1, `motivo: "deriva_de_intencao"`) em vez de prosseguir fora do próprio escopo.
- **`agent-router.agent.md` v1.5.0**: novo PASSO 0.3 na Decision Tree (checagem de deriva quando há agent ativo de turno anterior); output com campo `Agente Ativo` para auditoria; roteamento direto para `angular`/`spring-boot`/`spring-reactive` (antes órfãos — só alcançáveis por `@menção` manual, nunca roteados pelo próprio router).
- **`docs/ai-context/routing-graph.yaml`**: 3 novos nós `specialist_advisory` (`angular`, `spring-boot`, `spring-reactive`) + arestas de entrada a partir do router; nova aresta reversa universal `de: *downstream → para: agent-router` (condição `intent_drift_detected`, prioridade 0) aplicável a todo nó `downstream`/`specialist_advisory`.
- **`handoff-governance/SKILL.md`**: § 5 nova linha de escalonamento para mudança de fase na mesma conversa; nova § 5.2 "Anti Sticky-Session (R-042)".
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-015/016/017` (specialists agora roteáveis) + `regr-014/015` (regressão de sticky-session, 2 turnos) — suíte passa de 35 para 40 casos.

### Corrigido
- Gap de catálogo: `angular`, `spring-boot` e `spring-reactive` já existiam em `catalog.yaml`/`README.md` mas nunca haviam sido registrados como nós roteáveis em `routing-graph.yaml` nem na Decision Tree do `agent-router` — corrigido.
- **SYNC (R-015)**: `agents/catalog.yaml` (`related_agents: agent-router` adicionado aos 3 specialists), `agents/README.md` (nota R-042 em Diretrizes Transversais), `CLAUDE.md`, `.github/copilot-instructions.md`.

### Pesquisa de mercado (base da decisão)
- OpenAI Agents SDK — padrão `handoff()` + `transfer_back_to_*` (retorno explícito de controle).
- LangGraph `langgraph-supervisor` — `create_handoff_tool` + `add_handoff_back_messages`.
- Padrão de state machine de 2 modos (`orchestrator_mode`/`task_mode`) com detecção conservadora de deriva de tópico (Orchestrator Pattern, 2026).

---

## [1.3.0] — 2026-08-29

### Adicionado
- **Agent `requirements-analyst`**: perfil de elicitação prospectiva para transformar pedido de negócio ambíguo em requisitos funcionais/não-funcionais estruturados e testáveis, com rastreabilidade da fonte; aplica mediação contra *solution-jumping* (Five Whys) antes de qualquer decisão técnica
- **Skill `requirements-engineering-patterns`** (Tier 2): base de conhecimento consolidada via pesquisa de mercado (ISO/IEC/IEEE 29148, EARS, INVEST, Gherkin/BDD, FURPS+, regra de singularidade INCOSE)
- **`docs/ai-context/routing-graph.yaml`**: novo nó + aresta `agent-router → requirements-analyst` (R-040), com `nao_confundir_com` cruzado para evitar colisão com `business-rules-extractor` e `impact-architect`
- **`docs/ai-context/evals/casos-roteamento.yaml`**: `canon-014` (roteamento correto para `requirements-analyst`), `regr-012` e `regr-013` (não-confusão `requirements-analyst` × `business-rules-extractor`) — suíte passa de 32 para 35 casos
- **`agent-router.agent.md`**: nova ramificação na Decision Tree para elicitação de requisito novo; bump `version: 1.3.0 → 1.4.0`

### Corrigido
- **SYNC de catálogos (R-015/R-040)**: atualização atômica de `agents/catalog.yaml` (23 → 24 agents), `skills/.index.json` (38 → 39 skills), `agents/README.md` e `skills/README.md` para refletir o novo perfil de requisitos
- **`README.md`** consolidado para refletir o estado real: 24 agents, 39 skills, 35 casos de roteamento e distinção explícita de escopo entre `requirements-analyst` (pedido → requisito) e `business-rules-extractor` (código → regra)

### Conformidade
- Mantida separação de responsabilidades sem duplicação (R-003): `requirements-analyst` opera em requisito **novo/prospectivo**; `business-rules-extractor` permanece no fluxo **reverso** (código existente)

---

## [1.2.0] — 2026-06-12

### Adicionado
- **Prompt `/commit`**: Gera mensagem Conventional Commits (PT-BR) sem executar git autonomamente
- **Prompt `/review`**: Revisão de código por qualidade, convenções e impacto com relatório por severidade
- **Prompt `/health`**: Health check completo da governança (binding, agents, skills, R-038)
- **Agent `skill-factory`**: Criar/revisar skills com padrão SKILL.md e atualização atômica do `.index.json`
- **Skill `git-governance`**: Convenções de branch naming, commit standards e PR guidelines
- **`docs/ai-context/catalog.yaml`**: Binding instanciado para o ecossistema
- **`docs/ai-context/binding.md`**: Documentação do binding ativo
- Diagrama Mermaid no README.md mostrando fluxo completo de agents

### Corrigido
- **SYNC**: `.index.json` com `total_agents: 10` (corrigido para 15) e 2 skills sem entrada (`project-scanner`, `project-context-builder`)
- **SYNC**: `copilot-instructions.md` § 4.1 ainda mencionava "5 perguntas" após simplificação para 1

### Conformidade R-038
- Todos os arquivos de governança agora seguem o padrão de genericidade obrigatória (R-038)
---

## [1.1.0] — 2026-06-11

### Adicionado
- **Prompt `/init-context` v1.1**: PASSO 2 informativo (não bloqueante), PASSO 3 condicional por sessão, PASSO 4 lista projetos por nome
- **Simplificação `binding-initializer`**: 5 perguntas → 1 pergunta (só nome do ecossistema)
- **Desacoplamento `adapter-generator`**: Removido auto-disparo pelo `binding-initializer` — apenas chamado por `/add-project-context`
- **Guardrail de confinamento**: Todos os arquivos gerados ficam exclusivamente no repositório de governança
- **Naming de adapters**: Padrão `<nome-projeto>.instructions.md` (sem sufixo de stack)
- Source_docs do `/init-context` agora inclui `docs/ai-context/catalog.yaml`
- PASSO 3 do `/init-context` condicional: sessão recorrente mostra top-5; primeira execução mostra todas

### Corrigido
- `add-project-context`: reduzido de 4 para 3 perguntas (Q2 tipo removida — inferida pelo scanner)
- `QUICK-START.md`: exemplos atualizados com caminhos corretos de projeto

---

## [1.0.0] — 2026-06-10

### Adicionado
- Estrutura inicial de governança (`CLAUDE.md`, `copilot-instructions.md`)
- 14 agents: `agent-router`, `bug-triage`, `test-strategy`, `test-implementation`, `refactor-planner`, `impact-architect`, `docs-curator`, `research-router`, `analysis-architect`, `agent-factory`, `context-builder`, `binding-initializer`, `adapter-generator`
- 17 skills: `context-mode`, `context-builder`, `context-compact`, `sonarqube-governance`, `tavily`, `mermaid-diagrams`, `agent-contracts`, `handoff-governance`, `confidence-fallback-policy`, `agent-safety-guardrails`, `agent-observability-otel`, `agent-evals-lab`, `yaml-governance`, `test-implementation-angular`, `test-implementation-backend`, `test-coverage-governance`
- Prompts de workflow: `/research`, `/plan`, `/implement`, `/validate` (renomeados de PT→EN em 2026-08-29)
- Prompts de Context Mode: `/ctx-checkpoint`, `/ctx-resume`, `/ctx-doctor`, `/ctx-insight`, `/ctx-status`
- Prompts de binding: `/init-context`, `/add-project-context`, `/del-project-context`
- Templates base: `catalog-base.yaml`, `binding-base.md`
- Adapters: `spring-boot-backend.instructions.md` (Java/Spring), `angular-v21-frontend.instructions.md` (Angular 21)
- Regras normativas R-001..R-039 em CLAUDE.md
