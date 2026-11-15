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
- **Total de Avaliações**: 6
- **Acurácia Global**: 0.500000
- **Cobertura de Arestas (Golden)**: 0.000000
- **Cobertura de Arestas (Total)**: 0.500000

## Métricas por Aresta
| edge_id | para | tipo | sup_manual | sup_graph | tp | fp | fn | precision | recall | f1 | unparseable |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e-aaaa00000001 | bug-triage | keyword_based | 0 | 6 | 3 | 0 | 3 | 1.000000 | 0.500000 | 0.666667 | 0 |
| e-bbbb00000002 | business-rules-extractor | keyword_based | 0 | 0 | 0 | 3 | 0 | 0.000000 | null | null | 0 |

## Rotas Órfãs
- `sem_golden`: ['e-aaaa00000001', 'e-bbbb00000002']
- `sem_avaliacao`: ['e-bbbb00000002']
- `uncoverable`: []

## Colisões Estáticas de Keywords
- Nenhuma colisão detectada.

## Divergências `routing-graph.yaml` × `agent-router.agent.md`
- `nos_nao_citados`: []
- `citados_fora_do_grafo`: []
- `rotas_fantasma`: []

## Sugestões Acionáveis (Consultivas)
| id | codigo | severidade | alvo_arquivo | alvo_ancora | proposta_texto |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SUG-0001 | SUG-KW-ADD | media | .github/agents/routing-graph.yaml | arestas[e-aaaa00000001:bug-triage] | Adicionar keywords candidatas ['prompt'] na aresta 'e-aaaa00000001' (para=bug-triage). |
| SUG-0002 | SUG-DISAMBIG | alta | .github/agents/agent-router.agent.md | disambig:bug-triage->business-rules-extractor | Adicionar regra de desambiguacao explicita entre '@bug-triage' e '@business-rules-extractor' (3 ocorrencias) e calibrar prioridade no routing-graph.yaml. |
| SUG-0003 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-aaaa00000001:bug-triage] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-aaaa00000001' (para=bug-triage). |
| SUG-0004 | SUG-GOLDEN-GAP | baixa | .github/agents/evals/casos-roteamento.yaml | arestas[e-bbbb00000002:business-rules-extractor] | Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa 'e-bbbb00000002' (para=business-rules-extractor). |
