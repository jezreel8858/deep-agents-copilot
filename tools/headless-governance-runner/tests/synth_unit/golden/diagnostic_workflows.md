# Diagnóstico de Assertividade de Roteamento — `run-wf`

> **Aviso**: Artefato consultivo (HITL). Nenhum arquivo-alvo é modificado automaticamente.

## Metadados e Hashes
- `diagnostic_version`: `1`
- `diagnostic_id`: `diag-99b99b5d86f8`
- `eval_run_id`: `run-wf`
- `finished_at`: `2026-11-15T15:00:00+00:00`
- `routing_graph_sha256`: `1111111111111111111111111111111111111111111111111111111111111111`
- `router_agent_sha256`: `2222222222222222222222222222222222222222222222222222222222222222`
- `golden_set_sha256`: `3333333333333333333333333333333333333333333333333333333333333333`

## Resumo Executivo
- **Total de Avaliações**: 8
- **Acurácia Global**: 0.500000
- **Cobertura de Arestas (Golden)**: 0.000000
- **Cobertura de Arestas (Total)**: 1.000000

## Métricas por Aresta
| edge_id | para | tipo | sup_manual | sup_graph | tp | fp | fn | precision | recall | f1 | unparseable |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e-aaaa00000001 | bug-triage | keyword_based | 0 | 6 | 2 | 0 | 4 | 1.000000 | 0.333333 | 0.500000 | 0 |
| e-bbbb00000002 | business-rules-extractor | keyword_based | 0 | 2 | 2 | 2 | 0 | 0.500000 | 1.000000 | 0.666667 | 0 |

## Rotas Órfãs
- `sem_golden`: ['e-aaaa00000001', 'e-bbbb00000002']
- `sem_avaliacao`: []
- `uncoverable`: []

## Colisões Estáticas de Keywords
- Nenhuma colisão detectada.

## Workflows
- **Macro-F1**: 0.485714
- **Acurácia**: 0.428571
- **Consistência workflow×rota**: 0.600000
- **Banner coverage**: 0.714286

| workflow_id | suporte | tp | fp | fn | precision | recall | f1 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| WORKFLOW-BUG-FIX | 5 | 2 | 0 | 3 | 1.000000 | 0.400000 | 0.571429 |
| WORKFLOW-FEATURE-DEVELOPMENT | 0 | 0 | 0 | 0 | null | null | null |
| WORKFLOW-NOGATILHO | 0 | 0 | 0 | 0 | null | null | null |
| WORKFLOW-REFACTORING | 2 | 1 | 2 | 1 | 0.333333 | 0.500000 | 0.400000 |

### Colisões de Gatilhos de Workflows
- `erro` (exata): ['WORKFLOW-BUG-FIX', 'WORKFLOW-REFACTORING'] []
- `erro` (gatilho_aresta): ['WORKFLOW-REFACTORING'] ['e-aaaa00000001']

## Divergências `routing-graph.yaml` × `agent-router.agent.md`
- `nos_nao_citados`: []
- `citados_fora_do_grafo`: []
- `rotas_fantasma`: ['feature-planner']

## Sugestões Acionáveis (Consultivas)
| id | codigo | severidade | alvo_arquivo | alvo_ancora | proposta_texto |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SUG-0001 | SUG-KW-ADD | media | .github/agents/routing-graph.yaml | arestas[e-aaaa00000001:bug-triage] | Adicionar keywords candidatas ['prompt'] na aresta 'e-aaaa00000001' (para=bug-triage). |
| SUG-0002 | SUG-DISAMBIG | alta | .github/agents/agent-router.agent.md | disambig:bug-triage->business-rules-extractor | Adicionar regra de desambiguacao explicita entre '@bug-triage' e '@business-rules-extractor' (2 ocorrencias) e calibrar prioridade no routing-graph.yaml. |
| SUG-0003 | SUG-DISAMBIG | alta | .github/agents/agent-router.agent.md | disambig:bug-triage->feature-planner | Adicionar regra de desambiguacao explicita entre '@bug-triage' e '@feature-planner' (2 ocorrencias) e calibrar prioridade no routing-graph.yaml. |
| SUG-0004 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-aaaa00000001:bug-triage] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-aaaa00000001' (para=bug-triage). |
| SUG-0005 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-bbbb00000002:business-rules-extractor] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-bbbb00000002' (para=business-rules-extractor). |
| SUG-0006 | SUG-GRAPH-PHANTOM | alta | .github/agents/agent-router.agent.md | phantom:feature-planner | Rota fantasma observada 'feature-planner' nao pertence a routing-graph.yaml::nos; restringir delegacao no prompt. |
| SUG-0007 | SUG-WF-COLLISION | media | .github/agents/routing-graph.yaml | gatilho:erro | Resolver colisao exata do gatilho 'erro' entre workflows ['WORKFLOW-BUG-FIX', 'WORKFLOW-REFACTORING']. |
| SUG-0008 | SUG-WF-COLLISION | baixa | .github/agents/routing-graph.yaml | gatilho:erro | Resolver colisao gatilho_aresta do gatilho 'erro' entre workflows ['WORKFLOW-REFACTORING'] e arestas ['e-aaaa00000001']. |
| SUG-0009 | SUG-WF-LOW-RECALL | media | .github/agents/routing-graph.yaml | workflows[WORKFLOW-BUG-FIX].gatilhos | Recall 0.400000 do workflow 'WORKFLOW-BUG-FIX' abaixo de 0.7; revisar gatilhos. |
| SUG-0010 | SUG-WF-LOW-RECALL | media | .github/agents/routing-graph.yaml | workflows[WORKFLOW-REFACTORING].gatilhos | Recall 0.500000 do workflow 'WORKFLOW-REFACTORING' abaixo de 0.7; revisar gatilhos. |
| SUG-0011 | SUG-WF-LOW-PRECISION | media | .github/agents/routing-graph.yaml | workflows[WORKFLOW-REFACTORING].gatilhos | Precisao 0.333333 do workflow 'WORKFLOW-REFACTORING' abaixo de 0.7; restringir gatilhos. |
| SUG-0012 | SUG-WF-INCONSISTENT-ROUTE | media | .github/agents/agent-router.agent.md | wf-route:WORKFLOW-BUG-FIX->feature-planner | Rota observada incoerente com a etapa 1 do workflow (WORKFLOW-BUG-FIX->feature-planner); alinhar delegacao com etapa 1. |
| SUG-0013 | SUG-WF-MISSING-BANNER | baixa | .github/agents/agent-router.agent.md | banner:workflow | Respostas sem linha 'Workflow:' valida; reforcar o banner obrigatorio no agent-router. |
| SUG-0014 | SUG-WF-UNKNOWN-ID | media | .github/agents/agent-router.agent.md | banner:workflow-id | Workflow com ID fora do snapshot do grafo; alinhar IDs do banner aos workflows de routing-graph.yaml. |
| SUG-0015 | SUG-WF-UNCOVERABLE | baixa | .github/agents/routing-graph.yaml | workflows[WORKFLOW-NOGATILHO] | Workflow 'WORKFLOW-NOGATILHO' sem gatilhos validos ou sem padroes de etapa 1; nao eh possivel gerar seeds. |
