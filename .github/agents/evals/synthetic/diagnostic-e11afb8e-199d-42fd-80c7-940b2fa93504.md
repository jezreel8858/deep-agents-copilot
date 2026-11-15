# Diagnóstico de Assertividade de Roteamento — `e11afb8e-199d-42fd-80c7-940b2fa93504`

> **Aviso**: Artefato consultivo (HITL). Nenhum arquivo-alvo é modificado automaticamente.

## Metadados e Hashes
- `diagnostic_version`: `1`
- `diagnostic_id`: `diag-fca52925eb24`
- `eval_run_id`: `e11afb8e-199d-42fd-80c7-940b2fa93504`
- `finished_at`: `2026-11-15T05:13:00.000000+00:00`
- `routing_graph_sha256`: `1af92528ac31ef5a29a3b1b1fb995754bae227562a2d8ceaf2a4457c4c3d2647`
- `router_agent_sha256`: `b656b9ad8b1524db6326730cb0eb87c3380a53411a8412c6369643fd12edd642`
- `golden_set_sha256`: `a8177837ec7eca49e5e6e6f95561d0d29a1d92194471cff21cd593565ec14edf`

## Resumo Executivo
- **Total de Avaliações**: 4
- **Acurácia Global**: 0.750000
- **Cobertura de Arestas (Golden)**: 0.763158
- **Cobertura de Arestas (Total)**: 0.105263

## Métricas por Aresta
| edge_id | para | tipo | sup_manual | sup_graph | tp | fp | fn | precision | recall | f1 | unparseable |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e-02c6d7d1c7cd | database-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-0deda784e717 | tech-solution-architect | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-17992619cd8f | security-reviewer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-1e69283f7e01 | debugger | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-231043400f42 | governance-factory | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-29a82d8c7294 | python-router | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-2dd75835ee0c | docs-engineer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-31086a8727f5 | feature-planner | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-316e674417a6 | governance-maintainer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-31998f180c47 | ejb-router | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-36527ca3e648 | tech-solution-architect | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-3978fb343b11 | struts-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-3ab33c52be64 | compliance-guardrails | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-40d7be967241 | code-style-enforcer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-49640048de99 | refactor-planner | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-4b90caff6f5c | pr-gatekeeper | keyword_based | 0 | 1 | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0 |
| e-562a6ca3b730 | plan-critic | keyword_based | 0 | 1 | 0 | 0 | 1 | null | 0.000000 | null | 1 |
| e-56a9fbad60e1 | tech-solution-architect | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-597778e57b18 | database-specialist | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-59e71f5faf3f | angular-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-5d82f5863407 | spring-boot-router | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-6385e3e1a09c | bug-triage | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-6a286d516252 | adr-sentinel | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-6b64286b4210 | agent-auditor | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-70da634ba973 | code-review | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-7af9cfeea3a5 | performance-agent | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-87f9c0b67c3b | ddd-bounded-context-mapper | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-9cd79bd055bc | devops-engineer | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
| e-af3821cb2649 | business-rules-extractor | keyword_based | 0 | 0 | 0 | 0 | 0 | null | null | null | 0 |
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
- `sem_golden`: ['e-0deda784e717', 'e-29a82d8c7294', 'e-31998f180c47', 'e-4b90caff6f5c', 'e-562a6ca3b730', 'e-56a9fbad60e1', 'e-597778e57b18', 'e-c8da7cb5f0d9', 'e-e6f649fa9331']
- `sem_avaliacao`: ['e-02c6d7d1c7cd', 'e-0deda784e717', 'e-17992619cd8f', 'e-1e69283f7e01', 'e-231043400f42', 'e-2dd75835ee0c', 'e-31086a8727f5', 'e-316e674417a6', 'e-36527ca3e648', 'e-3978fb343b11', 'e-3ab33c52be64', 'e-40d7be967241', 'e-49640048de99', 'e-56a9fbad60e1', 'e-597778e57b18', 'e-59e71f5faf3f', 'e-5d82f5863407', 'e-6385e3e1a09c', 'e-6a286d516252', 'e-6b64286b4210', 'e-70da634ba973', 'e-7af9cfeea3a5', 'e-87f9c0b67c3b', 'e-9cd79bd055bc', 'e-af3821cb2649', 'e-bbe493a29f10', 'e-c48903e85052', 'e-c865048e7f45', 'e-c8da7cb5f0d9', 'e-cc45b4ef8230', 'e-da3863230a7a', 'e-e6f649fa9331', 'e-e8913204b387', 'e-f355f737c33c']
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

## Divergências `routing-graph.yaml` × `agent-router.agent.md`
- `nos_nao_citados`: ['plan-critic']
- `citados_fora_do_grafo`: ['agente-1', 'agente-2', 'agente-3', 'agente-4', 'agente-5']
- `rotas_fantasma`: []

## Sugestões Acionáveis (Consultivas)
| id | codigo | severidade | alvo_arquivo | alvo_ancora | proposta_texto |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SUG-0001 | SUG-KW-ADD | media | .github/agents/routing-graph.yaml | arestas[e-562a6ca3b730:plan-critic] | Adicionar keywords candidatas ['cetica', 'cetica independente', 'dados'] na aresta 'e-562a6ca3b730' (para=plan-critic). |
| SUG-0002 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:auditoria | Resolver colisao substring da keyword 'auditoria' compartilhada entre arestas ['e-3ab33c52be64', 'e-59e71f5faf3f', 'e-6a286d516252', 'e-c48903e85052']. |
| SUG-0003 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:catalogo | Resolver colisao substring da keyword 'catalogo' compartilhada entre arestas ['e-2dd75835ee0c', 'e-316e674417a6', 'e-6b64286b4210']. |
| SUG-0004 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:cobertura | Resolver colisao substring da keyword 'cobertura' compartilhada entre arestas ['e-59e71f5faf3f', 'e-cc45b4ef8230']. |
| SUG-0005 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:core web vitals | Resolver colisao substring da keyword 'core web vitals' compartilhada entre arestas ['e-59e71f5faf3f', 'e-7af9cfeea3a5', 'e-c48903e85052']. |
| SUG-0006 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:dependencias | Resolver colisao substring da keyword 'dependencias' compartilhada entre arestas ['e-36527ca3e648', 'e-c8da7cb5f0d9', 'e-f355f737c33c']. |
| SUG-0007 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:fluxo de dados | Resolver colisao substring da keyword 'fluxo de dados' compartilhada entre arestas ['e-0deda784e717', 'e-f355f737c33c']. |
| SUG-0008 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:flyway | Resolver colisao substring da keyword 'flyway' compartilhada entre arestas ['e-02c6d7d1c7cd', 'e-597778e57b18']. |
| SUG-0009 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:layout autenticado | Resolver colisao exata da keyword 'layout autenticado' compartilhada entre arestas ['e-59e71f5faf3f', 'e-c48903e85052']. |
| SUG-0010 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:login playwright | Resolver colisao exata da keyword 'login playwright' compartilhada entre arestas ['e-59e71f5faf3f', 'e-c48903e85052']. |
| SUG-0011 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:nao funciona | Resolver colisao substring da keyword 'nao funciona' compartilhada entre arestas ['e-6385e3e1a09c', 'e-c865048e7f45']. |
| SUG-0012 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:pull request | Resolver colisao substring da keyword 'pull request' compartilhada entre arestas ['e-4b90caff6f5c', 'e-70da634ba973']. |
| SUG-0013 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:react | Resolver colisao substring da keyword 'react' compartilhada entre arestas ['e-c48903e85052', 'e-e8913204b387']. |
| SUG-0014 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:readme | Resolver colisao substring da keyword 'readme' compartilhada entre arestas ['e-2dd75835ee0c', 'e-da3863230a7a']. |
| SUG-0015 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:refatorar | Resolver colisao substring da keyword 'refatorar' compartilhada entre arestas ['e-316e674417a6', 'e-49640048de99']. |
| SUG-0016 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:revisar pr | Resolver colisao substring da keyword 'revisar pr' compartilhada entre arestas ['e-231043400f42', 'e-70da634ba973']. |
| SUG-0017 | SUG-KW-COLLISION | baixa | .github/agents/routing-graph.yaml | keyword:risco | Resolver colisao substring da keyword 'risco' compartilhada entre arestas ['e-36527ca3e648', 'e-4b90caff6f5c', 'e-cc45b4ef8230']. |
| SUG-0018 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:stack trace | Resolver colisao exata da keyword 'stack trace' compartilhada entre arestas ['e-1e69283f7e01', 'e-6385e3e1a09c']. |
| SUG-0019 | SUG-KW-COLLISION | media | .github/agents/routing-graph.yaml | keyword:validacao visual layout | Resolver colisao exata da keyword 'validacao visual layout' compartilhada entre arestas ['e-59e71f5faf3f', 'e-c48903e85052']. |
| SUG-0020 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-0deda784e717:tech-solution-architect] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-0deda784e717' (para=tech-solution-architect). |
| SUG-0021 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-29a82d8c7294:python-router] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-29a82d8c7294' (para=python-router). |
| SUG-0022 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-31998f180c47:ejb-router] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-31998f180c47' (para=ejb-router). |
| SUG-0023 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-4b90caff6f5c:pr-gatekeeper] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-4b90caff6f5c' (para=pr-gatekeeper). |
| SUG-0024 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-562a6ca3b730:plan-critic] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-562a6ca3b730' (para=plan-critic). |
| SUG-0025 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-56a9fbad60e1:tech-solution-architect] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-56a9fbad60e1' (para=tech-solution-architect). |
| SUG-0026 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-597778e57b18:database-specialist] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-597778e57b18' (para=database-specialist). |
| SUG-0027 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-c8da7cb5f0d9:runtime-verifier] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-c8da7cb5f0d9' (para=runtime-verifier). |
| SUG-0028 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-e6f649fa9331:deep-search] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-e6f649fa9331' (para=deep-search). |
| SUG-0029 | SUG-ROUTER-DOC | media | .github/agents/agent-router.agent.md | node:plan-critic | Documentar o agente '@plan-critic' nas instrucoes do agent-router.agent.md. |
| SUG-0030 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-1 | Alinhar agente '@agente-1' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0031 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-2 | Alinhar agente '@agente-2' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0032 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-3 | Alinhar agente '@agente-3' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0033 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-4 | Alinhar agente '@agente-4' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
| SUG-0034 | SUG-ROUTER-DOC | media | .github/agents/routing-graph.yaml | nos:agente-5 | Alinhar agente '@agente-5' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos. |
