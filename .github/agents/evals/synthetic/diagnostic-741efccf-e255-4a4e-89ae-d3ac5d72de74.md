# Diagnóstico de Assertividade de Roteamento — `741efccf-e255-4a4e-89ae-d3ac5d72de74`

> **Aviso**: Artefato consultivo (HITL). Nenhum arquivo-alvo é modificado automaticamente.

## Metadados e Hashes
- `diagnostic_version`: `1`
- `diagnostic_id`: `diag-3ed889fdf886`
- `eval_run_id`: `741efccf-e255-4a4e-89ae-d3ac5d72de74`
- `finished_at`: `2026-11-15T08:29:36.115809+00:00`
- `routing_graph_sha256`: `1af92528ac31ef5a29a3b1b1fb995754bae227562a2d8ceaf2a4457c4c3d2647`
- `router_agent_sha256`: `285d4b1e79d4e78d8685331de88db6daaf0b7a425da68ba49dfa89f49804c0c0`
- `golden_set_sha256`: `196b5dd437f09f16a7cb8cce5aa1302195dafe25f3760eee2968179e34d56efe`

## Resumo Executivo
- **Total de Avaliações**: 9
- **Acurácia Global**: 0.666667
- **Cobertura de Arestas (Golden)**: 1.000000
- **Cobertura de Arestas (Total)**: 0.184211

## Métricas por Aresta
| edge_id | para | tipo | sup_manual | sup_graph | tp | fp | fn | precision | recall | f1 | unparseable |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e-02c6d7d1c7cd | database-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-0deda784e717 | tech-solution-architect | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-17992619cd8f | security-reviewer | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-1e69283f7e01 | debugger | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-231043400f42 | governance-factory | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-29a82d8c7294 | python-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-2dd75835ee0c | docs-engineer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-31086a8727f5 | feature-planner | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-316e674417a6 | governance-maintainer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-31998f180c47 | ejb-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-36527ca3e648 | tech-solution-architect | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-3978fb343b11 | struts-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-3ab33c52be64 | compliance-guardrails | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-40d7be967241 | code-style-enforcer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-49640048de99 | refactor-planner | keyword_based | 0 | 0 | 0 | 1 | 0 | 0.000000 | null | null | 0 |
| e-4b90caff6f5c | pr-gatekeeper | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-562a6ca3b730 | plan-critic | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-56a9fbad60e1 | tech-solution-architect | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-597778e57b18 | database-specialist | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-59e71f5faf3f | angular-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-5d82f5863407 | spring-boot-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-6385e3e1a09c | bug-triage | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-6a286d516252 | adr-sentinel | keyword_based | 0 | 1 | 0 | 0 | 1 | null | 0.000000 | null | 1 |
| e-6b64286b4210 | agent-auditor | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-70da634ba973 | code-review | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-7af9cfeea3a5 | performance-agent | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-87f9c0b67c3b | ddd-bounded-context-mapper | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-9cd79bd055bc | devops-engineer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-af3821cb2649 | business-rules-extractor | keyword_based | 0 | 1 | 0 | 0 | 1 | null | 0.000000 | null | 0 |
| e-bbe493a29f10 | tech-solution-architect | security_gate | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-c48903e85052 | react-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-c865048e7f45 | requirements-analyst | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-c8da7cb5f0d9 | runtime-verifier | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-cc45b4ef8230 | test-strategy | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-da3863230a7a | repo-hygiene-auditor | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-e6f649fa9331 | deep-search | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-e8913204b387 | spring-reactive-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-f355f737c33c | codegraph-engine | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |

## Rotas Órfãs
- `sem_golden`: []
- `sem_avaliacao`: ['e-02c6d7d1c7cd', 'e-0deda784e717', 'e-1e69283f7e01', 'e-231043400f42', 'e-29a82d8c7294', 'e-2dd75835ee0c', 'e-31086a8727f5', 'e-316e674417a6', 'e-31998f180c47', 'e-3978fb343b11', 'e-3ab33c52be64', 'e-40d7be967241', 'e-49640048de99', 'e-4b90caff6f5c', 'e-562a6ca3b730', 'e-597778e57b18', 'e-59e71f5faf3f', 'e-5d82f5863407', 'e-70da634ba973', 'e-7af9cfeea3a5', 'e-87f9c0b67c3b', 'e-9cd79bd055bc', 'e-bbe493a29f10', 'e-c48903e85052', 'e-c865048e7f45', 'e-c8da7cb5f0d9', 'e-cc45b4ef8230', 'e-da3863230a7a', 'e-e6f649fa9331', 'e-e8913204b387', 'e-f355f737c33c']
- `uncoverable`: []

## Colisões Estáticas de Keywords
- `auditoria` (substring): ['e-3ab33c52be64', 'e-59e71f5faf3f', 'e-6a286d516252', 'e-c48903e85052']
- `catalogo` (substring): ['e-2dd75835ee0c', 'e-316e674417a6', 'e-6b64286b4210']
- `cobertura` (substring): ['e-59e71f5faf3f', 'e-cc45b4ef8230']
- `core web vitals` (substring): ['e-59e71f5faf3f', 'e-7af9cfeea3a5', 'e-c48903e85052']
- `dependencias` (substring): ['e-36527ca3e648', 'e-c8da7cb5f0d9', 'e-f355f737c33c']
- `fluxo de dados` (substring): ['e-0deda784e717', 'e-f355f737c33c']
- `flyway` (substring): ['e-02c6d7d1c7cd', 'e-597778e57b18']
- `layout autenticado` (exata): ['e-59e71f5faf3f', 'e-c48903e85052']
- `login playwright` (exata): ['e-59e71f5faf3f', 'e-c48903e85052']
- `nao funciona` (substring): ['e-6385e3e1a09c', 'e-c865048e7f45']
- `pull request` (substring): ['e-4b90caff6f5c', 'e-70da634ba973']
- `react` (substring): ['e-c48903e85052', 'e-e8913204b387']
- `readme` (substring): ['e-2dd75835ee0c', 'e-da3863230a7a']
- `refatorar` (substring): ['e-316e674417a6', 'e-49640048de99']
- `revisar pr` (substring): ['e-231043400f42', 'e-70da634ba973']
- `risco` (substring): ['e-36527ca3e648', 'e-4b90caff6f5c', 'e-cc45b4ef8230']
- `stack trace` (exata): ['e-1e69283f7e01', 'e-6385e3e1a09c']
- `validacao visual layout` (exata): ['e-59e71f5faf3f', 'e-c48903e85052']

## Workflows
- **Macro-F1**: 0.777778
- **Acurácia**: 0.777778
- **Consistência workflow×rota**: 0.857143
- **Banner coverage**: 0.777778

| workflow_id | suporte | tp | fp | fn | precision | recall | f1 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| WORKFLOW-BUG-FIX | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-FEATURE-DEVELOPMENT | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-FRAMEWORK-MIGRATION | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-GOVERNANCE-MAINTENANCE | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-PROMPT-SYNTHESIS | 1 | 0 | 0 | 1 | null | 0.000000 | null |
| WORKFLOW-REFACTORING | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-RELEASE-READINESS | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| WORKFLOW-TECHNICAL-ANALYSIS | 1 | 0 | 0 | 1 | null | 0.000000 | null |

### Colisões de Gatilhos de Workflows
- `analisar` (gatilho_aresta): ['WORKFLOW-TECHNICAL-ANALYSIS'] ['e-70da634ba973']
- `atualizar dependencias` (gatilho_aresta): ['WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION'] ['e-36527ca3e648']
- `eliminar god class` (gatilho_aresta): ['WORKFLOW-REFACTORING'] ['e-87f9c0b67c3b']
- `manutencao de catalogo` (gatilho_aresta): ['WORKFLOW-GOVERNANCE-MAINTENANCE'] ['e-2dd75835ee0c']
- `migracao angular` (gatilho_aresta): ['WORKFLOW-FRAMEWORK-MIGRATION'] ['e-59e71f5faf3f']
- `migrar para signals` (gatilho_aresta): ['WORKFLOW-FRAMEWORK-MIGRATION'] ['e-59e71f5faf3f']
- `migrar para standalone` (gatilho_aresta): ['WORKFLOW-FRAMEWORK-MIGRATION'] ['e-59e71f5faf3f']
- `migrar spring boot` (gatilho_aresta): ['WORKFLOW-FRAMEWORK-MIGRATION'] ['e-5d82f5863407']
- `migrar struts` (gatilho_aresta): ['WORKFLOW-FRAMEWORK-MIGRATION'] ['e-3978fb343b11']
- `nao funciona` (gatilho_aresta): ['WORKFLOW-BUG-FIX'] ['e-c865048e7f45']
- `preparar prompt novo chat` (gatilho_aresta): ['WORKFLOW-PROMPT-SYNTHESIS'] ['e-4b90caff6f5c']
- `refatorar` (gatilho_aresta): ['WORKFLOW-REFACTORING'] ['e-316e674417a6', 'e-49640048de99']

## Divergências `routing-graph.yaml` × `agent-router.agent.md`
- `nos_nao_citados`: []
- `citados_fora_do_grafo`: ['agente-1', 'agente-2', 'agente-3', 'agente-4', 'agente-5']
- `rotas_fantasma`: []

## Sugestões Acionáveis (Consultivas)
| id | codigo | severidade | alvo_arquivo | alvo_ancora | proposta_texto |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SUG-0001 | SUG-KW-ADD | media | .github/agents/routing-graph.yaml | arestas[e-6a286d516252:adr-sentinel] | Adicionar keywords candidatas ['ambito', 'ambito tecnica', 'analisar'] na aresta 'e-6a286d516252' (para=adr-sentinel). |
| SUG-0002 | SUG-KW-ADD | media | .github/agents/routing-graph.yaml | arestas[e-af3821cb2649:business-rules-extractor] | Adicionar keywords candidatas ['abordar', 'abordar refatoracao', 'acoplamento'] na aresta 'e-af3821cb2649' (para=business-rules-extractor). |
| SUG-0003 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:auditoria | Resolver colisao substring da keyword 'auditoria' compartilhada entre arestas ['e-3ab33c52be64', 'e-59e71f5faf3f', 'e-6a286d516252', 'e-c48903e85052']. |
| SUG-0004 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:catalogo | Resolver colisao substring da keyword 'catalogo' compartilhada entre arestas ['e-2dd75835ee0c', 'e-316e674417a6', 'e-6b64286b4210']. |
| SUG-0005 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:cobertura | Resolver colisao substring da keyword 'cobertura' compartilhada entre arestas ['e-59e71f5faf3f', 'e-cc45b4ef8230']. |
| SUG-0006 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:core web vitals | Resolver colisao substring da keyword 'core web vitals' compartilhada entre arestas ['e-59e71f5faf3f', 'e-7af9cfeea3a5', 'e-c48903e85052']. |
| SUG-0007 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:dependencias | Resolver colisao substring da keyword 'dependencias' compartilhada entre arestas ['e-36527ca3e648', 'e-c8da7cb5f0d9', 'e-f355f737c33c']. |
| SUG-0008 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:fluxo de dados | Resolver colisao substring da keyword 'fluxo de dados' compartilhada entre arestas ['e-0deda784e717', 'e-f355f737c33c']. |
| SUG-0009 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:flyway | Resolver colisao substring da keyword 'flyway' compartilhada entre arestas ['e-02c6d7d1c7cd', 'e-597778e57b18']. |
| SUG-0010 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:layout autenticado | Resolver colisao exata da keyword 'layout autenticado' compartilhada entre arestas ['e-59e71f5faf3f', 'e-c48903e85052']. |
| SUG-0011 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:login playwright | Resolver colisao exata da keyword 'login playwright' compartilhada entre arestas ['e-59e71f5faf3f', 'e-c48903e85052']. |
| SUG-0012 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:nao funciona | Resolver colisao substring da keyword 'nao funciona' compartilhada entre arestas ['e-6385e3e1a09c', 'e-c865048e7f45']. |
| SUG-0013 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:pull request | Resolver colisao substring da keyword 'pull request' compartilhada entre arestas ['e-4b90caff6f5c', 'e-70da634ba973']. |
| SUG-0014 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:react | Resolver colisao substring da keyword 'react' compartilhada entre arestas ['e-c48903e85052', 'e-e8913204b387']. |
| SUG-0015 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:readme | Resolver colisao substring da keyword 'readme' compartilhada entre arestas ['e-2dd75835ee0c', 'e-da3863230a7a']. |
| SUG-0016 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:refatorar | Resolver colisao substring da keyword 'refatorar' compartilhada entre arestas ['e-316e674417a6', 'e-49640048de99']. |
| SUG-0017 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:revisar pr | Resolver colisao substring da keyword 'revisar pr' compartilhada entre arestas ['e-231043400f42', 'e-70da634ba973']. |
| SUG-0018 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:risco | Resolver colisao substring da keyword 'risco' compartilhada entre arestas ['e-36527ca3e648', 'e-4b90caff6f5c', 'e-cc45b4ef8230']. |
| SUG-0019 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:stack trace | Resolver colisao exata da keyword 'stack trace' compartilhada entre arestas ['e-1e69283f7e01', 'e-6385e3e1a09c']. |
| SUG-0020 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:validacao visual layout | Resolver colisao exata da keyword 'validacao visual layout' compartilhada entre arestas ['e-59e71f5faf3f', 'e-c48903e85052']. |
| SUG-0021 | SUG-DISAMBIG | alta | .github/agents/agent-router.agent.md | disambig:business-rules-extractor->refactor-planner | Adicionar regra de desambiguacao explicita entre '@business-rules-extractor' e '@refactor-planner' (1 ocorrencias) e calibrar prioridade no routing-graph.yaml. |
| SUG-0022 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-1 | Alinhar agente '@agente-1' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0023 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-2 | Alinhar agente '@agente-2' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0024 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-3 | Alinhar agente '@agente-3' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0025 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-4 | Alinhar agente '@agente-4' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0026 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-5 | Alinhar agente '@agente-5' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0027 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:analisar | Resolver colisao gatilho_aresta do gatilho 'analisar' entre workflows ['WORKFLOW-TECHNICAL-ANALYSIS'] e arestas ['e-70da634ba973']. |
| SUG-0028 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:atualizar dependencias | Resolver colisao gatilho_aresta do gatilho 'atualizar dependencias' entre workflows ['WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION'] e arestas ['e-36527ca3e648']. |
| SUG-0029 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:eliminar god class | Resolver colisao gatilho_aresta do gatilho 'eliminar god class' entre workflows ['WORKFLOW-REFACTORING'] e arestas ['e-87f9c0b67c3b']. |
| SUG-0030 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:manutencao de catalogo | Resolver colisao gatilho_aresta do gatilho 'manutencao de catalogo' entre workflows ['WORKFLOW-GOVERNANCE-MAINTENANCE'] e arestas ['e-2dd75835ee0c']. |
| SUG-0031 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:migracao angular | Resolver colisao gatilho_aresta do gatilho 'migracao angular' entre workflows ['WORKFLOW-FRAMEWORK-MIGRATION'] e arestas ['e-59e71f5faf3f']. |
| SUG-0032 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:migrar para signals | Resolver colisao gatilho_aresta do gatilho 'migrar para signals' entre workflows ['WORKFLOW-FRAMEWORK-MIGRATION'] e arestas ['e-59e71f5faf3f']. |
| SUG-0033 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:migrar para standalone | Resolver colisao gatilho_aresta do gatilho 'migrar para standalone' entre workflows ['WORKFLOW-FRAMEWORK-MIGRATION'] e arestas ['e-59e71f5faf3f']. |
| SUG-0034 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:migrar spring boot | Resolver colisao gatilho_aresta do gatilho 'migrar spring boot' entre workflows ['WORKFLOW-FRAMEWORK-MIGRATION'] e arestas ['e-5d82f5863407']. |
| SUG-0035 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:migrar struts | Resolver colisao gatilho_aresta do gatilho 'migrar struts' entre workflows ['WORKFLOW-FRAMEWORK-MIGRATION'] e arestas ['e-3978fb343b11']. |
| SUG-0036 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:nao funciona | Resolver colisao gatilho_aresta do gatilho 'nao funciona' entre workflows ['WORKFLOW-BUG-FIX'] e arestas ['e-c865048e7f45']. |
| SUG-0037 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:preparar prompt novo chat | Resolver colisao gatilho_aresta do gatilho 'preparar prompt novo chat' entre workflows ['WORKFLOW-PROMPT-SYNTHESIS'] e arestas ['e-4b90caff6f5c']. |
| SUG-0038 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:refatorar | Resolver colisao gatilho_aresta do gatilho 'refatorar' entre workflows ['WORKFLOW-REFACTORING'] e arestas ['e-316e674417a6', 'e-49640048de99']. |
| SUG-0039 | SUG-WF-LOW-RECALL | media | .github/agents/routing-graph.yaml | workflows[WORKFLOW-PROMPT-SYNTHESIS].gatilhos | Recall 0.000000 do workflow 'WORKFLOW-PROMPT-SYNTHESIS' abaixo de 0.7; revisar gatilhos. |
| SUG-0040 | SUG-WF-LOW-RECALL | media | .github/agents/routing-graph.yaml | workflows[WORKFLOW-TECHNICAL-ANALYSIS].gatilhos | Recall 0.000000 do workflow 'WORKFLOW-TECHNICAL-ANALYSIS' abaixo de 0.7; revisar gatilhos. |
| SUG-0041 | SUG-WF-INCONSISTENT-ROUTE | media | .github/agents/agent-router.agent.md | wf-route:WORKFLOW-REFACTORING->refactor-planner | Rota observada incoerente com a etapa 1 do workflow (WORKFLOW-REFACTORING->refactor-planner); alinhar delegacao com etapa 1. |
| SUG-0042 | SUG-WF-MISSING-BANNER | baixa | .github/agents/agent-router.agent.md | banner:workflow | Respostas sem linha 'Workflow:' valida; reforcar o banner obrigatorio no agent-router. |
