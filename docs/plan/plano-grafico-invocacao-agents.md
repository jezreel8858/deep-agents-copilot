---
status: planejado
data_criacao: 2026-08-30
autor: docs-engineer
tipo: plano-de-implementacao
---

# Plano de Implementação — Gráfico de Invocação de Agentes (Estilo When You Code) no Context Insight Visualizer

## 1. Contexto & Requisito

- **Demanda**: Adicionar ao `tools/context-insight-visualizer` um gráfico de barras mostrando a quantidade de vezes que cada agente do ecossistema foi invocado, contabilizando tanto invocações diretas quanto invocações delegadas via `sub_agent` (`run_subagent`), seguindo a mesma identidade visual e componentes de layout do card "When You Code".
- **Visual "When You Code"**:
  - **Mini-stats no topo do card**: indicadores resumidos em destaque (ex.: Agente Mais Invocado, Total de Invocações, Via Subagente).
  - **Barras verticais proporcionais (`flex-end`)**: altura calculada relativa ao valor máximo (`maxCount`), cantos arredondados, preenchimento com cor temática (primária / cyan) e opacidade dinâmica baseada na intensidade de uso.
  - **Suporte a tooltip contextual no hover**: exibição de detalhamento completo ao passar o cursor (total, diretas, via subagente).
  - **Rótulos limpos e monospace**: tipografia padronizada no rodapé de cada coluna para identificação imediata dos agentes.

---

## 2. Mapeamento de Arquivos Afetados

| # | Arquivo | Responsabilidade no Escopo |
|---|---|---|
| 1 | `tools/context-insight-visualizer/generator/extractor.py` | Extrator de telemetria SQLite/JSON: parser de agentes em `session_events` e `tool_calls`. |
| 2 | `tools/context-insight-visualizer/schemas/insight-data.schema.json` | Validação do contrato do payload JSON (`agentInvocations`). |
| 3 | `tools/context-insight-visualizer/generator/insights_engine.py` | Agregação e propagação para o bundle de dados. |
| 4 | `tools/context-insight-visualizer/template/index.html` | Card HTML na visualização do Dashboard. |
| 5 | `tools/context-insight-visualizer/template/styles/charts.css` | Estilos específicos das barras verticais e mini-stats de agentes. |
| 6 | `tools/context-insight-visualizer/template/scripts/state.js` | Getter reativo `getAgentInvocations()`. |
| 7 | `tools/context-insight-visualizer/template/scripts/charts.js` | Função de renderização `renderAgentInvocations()`. |
| 8 | `tools/context-insight-visualizer/template/scripts/app.js` | Chamada no ciclo de inicialização e troca de abas. |
| 9 | `tools/context-insight-visualizer/generator/template_bundler.py` e `generate.py` | Regeneração do bundle autônomo `dist/context-insight.html`. |

---

## 3. Decomposição de Subtasks [S]/[P]

### Fase 1: Backend de Extração & Contrato de Dados

- **[S] 1.1 Contrato Schema JSON**: Atualizar `schemas/insight-data.schema.json` adicionando o nó `agentInvocations` (array de objetos `{ agent: string, total: number, direct: number, subagent: number }`).
- **[S] 1.2 Extrator de Telemetria (`extractor.py`)**: Implementar detecção de agentes em `session_events` (via regex de menção `@nome`, tags `Agente Ativo:`, `Handoff:`, `role`, `intent`) e chamadas de ferramenta `run_subagent` / `subagent` (extraindo `agentName` no payload JSON/string).
- **[P] 1.3 Insights Engine (`insights_engine.py`)**: Incorporar `agentInvocations` no payload consolidado `build_insights_payload()` e calcular métricas agregadas (top agent, total de invocações e subagent ratio).

### Fase 2: Estrutura HTML & Estilização CSS

- **[P] 2.1 Card HTML (`template/index.html`)**: Adicionar o card de gráfico "Invocação de Agentes" na grid de gráficos do Dashboard com 3 mini-stats (`statTopAgent`, `statTotalAgentInvocations`, `statSubagentInvocations`), container `#agentInvocationsBars` e legenda de cores.
- **[P] 2.2 Estilização CSS (`template/styles/charts.css`)**: Declarar classes `.agent-bars-container`, `.agent-bar-col`, `.agent-bar-fill`, `.agent-bar-direct`, `.agent-bar-subagent`, `.agent-bar-label` e mini-stats alinhados aos design tokens do Material 3 e ao estilo `.heatmap-*`.

### Fase 3: Estado & Renderização JS

- **[S] 3.1 Estado Reativo (`template/scripts/state.js`)**: Adicionar método `getAgentInvocations()` retornando a lista do payload injetado.
- **[S] 3.2 Renderizador de Barras (`template/scripts/charts.js`)**: Implementar `renderAgentInvocations()` calculando `maxCount`, gerando colunas verticais com altura proporcional, preenchimento bicolor/empilhado (Direta vs Subagente), tooltips informativos e atualização dos mini-stats.
- **[S] 3.3 Integração de Ciclo de Vida (`template/scripts/app.js`)**: Invocar `renderAgentInvocations()` em `initApp()` e em `switchView('dashboard')`.

### Fase 4: Bundling, Testes & Validação

- **[S] 4.1 Bundling & Regeneração (`generate.py`)**: Executar regeneração de `dist/context-insight.html` via `generate.py` e validar ausência de regressões no schema e no carregamento offline.
- **[S] 4.2 Testes Automatizados**: Adicionar/atualizar testes unitários em Python para garantir extração resiliente de agentes mesmo com dados corrompidos ou ausentes.

---

## 4. Critérios de Pronto (Definition of Done)

- [ ] Schema `insight-data.schema.json` validado com o novo campo `agentInvocations`.
- [ ] `extractor.py` computa corretamente invocações diretas e via subagentes (`run_subagent`).
- [ ] Card exibido no Dashboard com layout e proporções idênticos ao padrão do "When You Code".
- [ ] Hover nas barras apresenta tooltip com detalhamento claro de invocações.
- [ ] Bundle standalone `dist/context-insight.html` gerado e executável offline sem dependências de CDN externas.
- [ ] Testes unitários do pipeline Python com 100% de aprovação.

