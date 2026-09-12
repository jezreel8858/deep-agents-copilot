---
titulo: "Plano de Otimização do Catálogo de Agents — Remoção e Extração de Skills"
status: implementado
data: 2026-08-30
data_implementacao: 2026-08-31
autor: analise-tecnica-catalogo
escopo: ".github/agents/*.agent.md (24 agents)"
---

# Plano de Otimização do Catálogo de Agents

> Análise dos 24 agents em `.github/agents/` com foco em: **(1)** candidatos à remoção por redundância/sobreposição; **(2)** conteúdo/padrões candidatos à extração para skills reutilizáveis, com mapeamento de consumidores.
>
> Este documento é uma **proposta** — nenhuma remoção ou criação de skill foi executada. Requer aprovação explícita antes de implementação (R-033, R-031).

---

## 1) Metodologia

- Leitura integral dos 24 arquivos `.agent.md` (frontmatter, Decision Tree, Catálogo/Conhecimento Base, seções de escopo).
- Cruzamento de: **(a)** sobreposição funcional entre agents; **(b)** duplicação de conteúdo/estrutura entre agents (candidato a skill); **(c)** verificação se já existe skill equivalente antes de propor nova.
- Critério de remoção: agent cuja função é **subconjunto estrito** de outro agent já existente, ou cuja indireção (hop extra de roteamento) não agrega valor de decisão.
- Critério de extração para skill: **padrão estrutural repetido em 3+ agents** (bloco de ask_questions, Decision Tree, formato de saída) sem skill equivalente já registrada em `.github/skills/.index.json`.

---

## 2) Parte A — Agents Candidatos à Remoção

### A.1 — `research-router` → substituir por novo agent `deep-search` (Retriever especializado)

> **Revisão desta seção (2026-08-31):** a proposta original (fundir `research-router` em `agent-router`+`analysis-architect`) foi **corrigida** após revisão. Em vez de empilhar responsabilidade de pesquisa em cima de um agent Critic/Analyst, cria-se um agent dedicado ao papel **Retriever/Researcher** (categoria já mapeada em `categorizacao-agents-mercado.md` §2.4), consolidando pesquisa interna e externa em 1 único especialista.

| Critério | Evidência |
|---|---|
| Função real hoje (`research-router`) | Decide entre **(a)** responder direto/pesquisa atômica via Tavily, ou **(b)** delegar para `@analysis-architect`. Único destino downstream real do catálogo é `analysis-architect`. |
| Problema da fusão original em `analysis-architect` | `analysis-architect` é um agent **Critic/Analyst** (avalia impacto, classifica risco, tiers B1/B2/B3). Empurrar para ele a responsabilidade de **decidir e executar pesquisa** (interna via terminal/ctx + externa via Tavily) mistura 2 papéis distintos no mesmo agent — anti-padrão citado na pesquisa de mercado: *"quando a lista de tools de um agent cresce além do foco (12 tools, 3 domínios), divida: specialists possuem subconjuntos coerentes de tools"* (`categorizacao-agents-mercado.md` §4, DataAspirant 2026). |
| Redundância real não resolvida pela fusão | Hoje, `research-router`, `analysis-architect`, `angular`, `spring-boot`, `spring-reactive` e `bug-triage` **cada um** replica individualmente a mesma hierarquia de decisão "esgotar evidência local (`context-mode`) antes de usar `tavily`" (regra já documentada na skill `tavily/SKILL.md`). Fundir só em `analysis-architect` não elimina essa duplicação nos demais agents — apenas a concentra em mais um lugar. |
| Solução proposta | Criar `deep-search` como **especialista único de pesquisa** — interna (terminal, scripts, `context-mode`) e externa (`tavily`) — que qualquer agent pode consultar via `run_subagent`, em vez de cada agent reimplementar a mesma lógica de decisão local→externo. |
| Padrão de mercado aplicado | "Agents as tools": um Retriever com toolset coerente (terminal + ctx + tavily) chamado por outros agents como se fosse uma ferramenta — consolida decisão de pesquisa em 1 lugar, mantém `analysis-architect` focado em crítica/análise. Continua respeitando o alerta de "excesso de indireção" porque `agent-router → deep-search` permanece **1 salto único** (não reintroduz o duplo salto do desenho anterior). |

**Escopo proposto do novo agent `deep-search`:**

| Dimensão | Conteúdo |
|---|---|
| Papel (taxonomia) | Retriever/Researcher (`categorizacao-agents-mercado.md` §2.4) |
| Pesquisa interna | `grep_search`, `file_search`, `read_file`, `list_dir`, `run_in_terminal` (ex.: `git --no-pager log`, scripts de introspecção do repo), `context-mode/ctx_execute`, `ctx_execute_file`, `ctx_search`, `ctx_batch_execute`, `ctx_index` |
| Pesquisa externa | `tavily/tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research`, `context-mode/ctx_fetch_and_index` (cache de doc externo) |
| Decisão de profundidade | Preserva a lógica já existente em `research-router`: pergunta atômica → responder direto; pesquisa composta (2+ subtemas) → decompor em sub-queries e paralelizar via `run_subagent`, depois sintetizar com citação de fonte |
| Template-base | `templates/research-agent.md` (perfil read-only — nunca escreve código/arquivo de aplicação) |
| Skills de referência | `tavily/SKILL.md` (hierarquia de decisão local→externo), `context-mode/SKILL.md` (coleta indexada), `prompt-engineering-patterns/SKILL.md` (decomposição de query composta) |

**Ação proposta:**
1. Criar `deep-search.agent.md` via `@agent-factory`, herdando a Decision Tree de `research-router` (pergunta atômica vs. composta) e ampliando com pesquisa interna via terminal/`context-mode` como capacidade de primeira classe (hoje só implícita via skill `tavily` § hierarquia local→externo).
2. `agent-router` passa a rotear **toda demanda de pesquisa** (interna aprofundada OU externa) diretamente para `@deep-search` em 1 salto (renomear rota `research_fallback` → apontar para `deep-search`).
3. `analysis-architect` mantém suas próprias `tavily/*`/`context-mode/*` apenas como **fallback de conveniência** para evidência já em mãos, mas passa a delegar para `@deep-search` quando a pesquisa for o objetivo central da tarefa (não um subproduto da análise).
4. Remover `research-router.agent.md`; atualizar `catalog.yaml`, `README.md`, `routing-graph.yaml`, `casos-roteamento.yaml` trocando toda referência de `research-router` por `deep-search`.

**Nota de escopo (não expandir além do pedido nesta correção):** este ajuste **não remove** as tools próprias de `context-mode`/`tavily` já presentes em `analysis-architect`, `angular`, `spring-boot`, `spring-reactive` e `bug-triage`. Uma consolidação total dessas tools em `deep-search` (reduzindo o toolset desses agents) é uma otimização futura possível, fora do escopo desta correção pontual do item A.1 — fica registrada como candidata a um item A.1-bis, se aprovada posteriormente.

**Risco da mudança:** Baixo. `deep-search` herda 100% da capacidade de `research-router` e adiciona pesquisa interna hoje fragmentada — nenhuma capacidade é perdida, e o hop de roteamento permanece único.

---

### A.2 — `impact-architect` → absorver em `analysis-architect` (tier B1)

| Critério | Evidência |
|---|---|
| Função real | Analisar impacto técnico **local** (dependências, contratos, riscos) em 1 projeto — sem cross-sistema. |
| Sobreposição | `analysis-architect.agent.md` já se descreve como cobrindo **"desde análise genérica de impacto até análise profunda de integrações cross-sistema"** (linha 5-8) e já tem uma metodologia B1/B2/B3 onde **B1 = "Diff estrutural... verificação rápida"** — exatamente o escopo declarado de `impact-architect`. |
| Autorreferência | O próprio `impact-architect.agent.md` delega **tudo que é cross-sistema** para `analysis-architect` (linha 105) — ou seja, ele só retém o subconjunto "local" que `analysis-architect` já cobre nativamente via tier B1. |
| Padrão de mercado | Taxonomia 2026 (DataAspirant, GeniOS) recomenda **não fragmentar um mesmo papel de "Analyst/Critic"** em múltiplos agents por escopo de tamanho — a prática consolidada é 1 agent analítico com **tiers de profundidade** (equivalente ao B1/B2/B3 que `analysis-architect` já implementa), não 2 agents divididos por escopo local/global. |

**Ação proposta:**
1. Adicionar explicitamente ao Método de Análise de `analysis-architect` (Etapa 4 — Tier B1) o formato de saída hoje exclusivo de `impact-architect` (Dependências/Contratos afetados, Riscos, Mitigação mínima) como **template padrão de saída B1**.
2. `agent-router` passa a rotear "análise de impacto local" diretamente para `@analysis-architect` (indicando tier B1 no motivo).
3. Remover `impact-architect.agent.md` e todas as referências (`catalog.yaml`, `README.md`, `routing-graph.yaml`, `casos-roteamento.yaml`, e as ~15 referências cruzadas em outros agents — ver lista abaixo).

**Agents que hoje referenciam `impact-architect` e precisam de atualização de link (trocar para `analysis-architect` tier B1):**
`bug-triage`, `test-strategy`, `refactor-planner`, `test-implementation`, `angular`, `spring-boot`, `spring-reactive`, `business-rules-extractor`, `requirements-analyst`, `code-review`.

**Risco da remoção:** Médio-baixo. Requer atualizar ~10 agents que hoje apontam para `@impact-architect` como handoff — mudança mecânica (find & replace de referência), sem perda de capacidade.

---

### A.3 — Resumo da Parte A

| Agent | Ação | Agents/Docs a atualizar | Esforço |
|---|---|---|---|
| `research-router` | **Substituir** por novo agent `deep-search` (Retriever interno+externo) | `catalog.yaml`, `agents/README.md`, `routing-graph.yaml`, `casos-roteamento.yaml`, `agent-router.agent.md` | Baixo-Médio (criação de agent novo via `@agent-factory`) |
| `impact-architect` | Remover — absorvido por `analysis-architect` (tier B1) | `catalog.yaml`, `agents/README.md`, `routing-graph.yaml`, `casos-roteamento.yaml`, + 10 agents com handoff cruzado | Médio |

**Catálogo resultante:** 24 → 23 agents (`research-router` sai, `deep-search` entra — neutro em contagem; `impact-architect` sai — líquido -1).

---

## 3) Parte B — Conteúdo Redundante Dentro de um Agent (sem remover o agent inteiro)

### B.1 — `adapter-generator.agent.md` duplica `project-scanner` (skill já existente)

O bloco "🔍 Scanner de Projeto — O Que Procurar" (linhas 50-147 de `adapter-generator.agent.md`, ~100 linhas com tabelas de detecção de linguagem/framework/estrutura/codestyle/testes/integração) é **quase idêntico** ao conteúdo já existente em `.github/skills/project-scanner/SKILL.md` § 2 (Artefatos Essenciais — Checklist de Scan).

**Ação proposta:** Remover as tabelas duplicadas de `adapter-generator.agent.md` e substituir por referência direta: *"Aplicar o checklist de scan definido em `project-scanner-governance` (skill já carregada em Docs Sempre Anexadas)"*. Reduz ~90 linhas de duplicação sem perda de informação (a skill já é pre-fetch obrigatório do agent).

---

## 4) Parte C — Padrões Candidatos à Extração para Skill Nova

> Verificado contra `.github/skills/.index.json` (45 skills) — nenhuma das 3 skills abaixo existe hoje.

### C.1 — Skill nova: `structured-intake-patterns`

**Padrão identificado:** bloco de coleta estruturada via `ask_questions` com **P1..PN**, critério de "mínimo necessário para prosseguir" e template de consolidação ("Pré-Contexto Validado" / equivalente), repetido quase palavra-por-palavra em:

| Agent | Bloco equivalente | Linhas aprox. |
|---|---|---|
| `bug-triage` | Seção "Pré-Checklist de Triagem" (P1-P8, 4 seções) | ~70 linhas |
| `test-fix` | "Protocolo de Detecção de Contexto" (P1-P3) | ~25 linhas |
| `business-rules-extractor` | "Protocolo de Coleta de Contexto" (P1-P4) | ~20 linhas |
| `requirements-analyst` | Aplicação de `ask_questions` para ambiguidade (via skill própria, mas o *padrão de bloco* é o mesmo) | ~10 linhas |

**Conteúdo proposto da skill (Tier 2, categoria `process`):**
- Estrutura canônica de bloco de intake: `P1..PN` com opções pré-definidas + campo aberto (R-027).
- Critério objetivo de "mínimo necessário para prosseguir" vs. "lacuna aceitável — registrar como não informado".
- Template de consolidação (`## PRÉ-CONTEXTO VALIDADO` ou equivalente por domínio).
- Tabela de "Mapeamento de Respostas → Estratégia" como padrão reutilizável.

**Consumidores mapeados (agents que devem referenciar esta skill em vez de repetir o bloco):**
- `bug-triage` (substituir bloco P1-P8 por referência + especialização de domínio)
- `test-fix` (substituir bloco P1-P3)
- `business-rules-extractor` (substituir bloco P1-P4)
- `requirements-analyst` (referenciar como base do próprio processo de `ask_questions`)

**Impacto:** Redução de ~125 linhas duplicadas nos 4 agents; 1 fonte única de verdade para o padrão "coleta estruturada antes de agir".

---

### C.2 — Skill nova: `governance-factory-patterns`

**Padrão identificado:** os 3 agents "factory" (`agent-factory`, `skill-factory`, `prompt-factory`) compartilham estrutura quase idêntica:
- Decision Tree: `Criar novo? → coletar campos via ask_questions → verificar duplicata → gerar arquivo → atualizar catálogo(s) → reportar`.
- Checklist "Antes de Criar/Revisar" com os mesmos ~8 itens (nome kebab-case, campo obrigatório presente, não duplica existente, catálogo atualizado na mesma entrega — R-015).
- Formato de Saída com bloco de "Validações: ✅/❌" item a item.

| Agent | Bloco equivalente | Linhas aprox. |
|---|---|---|
| `agent-factory` | Decision Tree + Checklist + Formato de Saída | ~50 linhas |
| `skill-factory` | Decision Tree + Checklist + Formato de Saída | ~45 linhas |
| `prompt-factory` | Decision Tree + Checklist + Formato de Saída | ~55 linhas |

**Conteúdo proposto da skill (Tier 1, categoria `governance`):**
- Fluxo canônico "Factory Pattern": criar vs. revisar vs. auditar em lote.
- Checklist genérico de qualidade estrutural (nome, campo obrigatório, duplicata, atualização atômica de catálogo — R-015).
- Template de "Formato de Saída" com bloco de validações ✅/❌ parametrizável por tipo de artefato (`agent`|`skill`|`prompt`).
- Regra de ouro: **atualização atômica** de índice + README na mesma entrega (R-015) é comum aos 3.

**Consumidores mapeados:**
- `agent-factory` (mantém a especificidade de templates `research-agent.md`/`operational-agent.md`, mas referencia a skill para o fluxo genérico).
- `skill-factory` (mantém especificidade de `SKILL.md` template, referencia a skill para o fluxo genérico).
- `prompt-factory` (mantém especificidade de `.prompt.md` template/naming, referencia a skill para o fluxo genérico).

**Impacto:** Redução de ~150 linhas duplicadas nos 3 agents; padroniza qualquer 4º "factory" futuro (ex.: `instructions-factory`, se vier a existir) sem reinventar o fluxo.

---

### C.3 — Skill nova: `specialist-hybrid-advisory-implementation-patterns`

**Padrão identificado:** os 3 specialists híbridos (`angular`, `spring-boot`, `spring-reactive`, todos v2.0.0) compartilham quase 90% da estrutura de agent, variando apenas o domínio técnico:
- Seção "Modos de Operação" (tabela Advisory/Implementação idêntica em forma).
- "Formato de Saída — Advisory" (Resumo/Escopo/Não-Escopo/Entradas/Análise por Pilar/Riscos/Recomendação/Handoff/Confiança) — idêntico nos 3.
- "Formato de Saída — Implementação" (bloco markdown com Resultado/Evidências/Testes executados/Validações/Próximo passo) — **idêntico literal** nos 3 arquivos, só troca o caminho de exemplo.
- Checklist "Antes de Analisar/Implementar" — idêntico em estrutura.
- Critério de desambiguação de modo via `ask_questions` — frase idêntica nos 3.

| Agent | Bloco duplicado (Modos + Formatos de Saída + Checklist) | Linhas aprox. |
|---|---|---|
| `angular` | ~90 linhas | |
| `spring-boot` | ~85 linhas | |
| `spring-reactive` | ~85 linhas | |

**Conteúdo proposto da skill (Tier 1, categoria `governance`):**
- Template canônico do "perfil híbrido" (Advisory + Implementação): quando declarar cada modo, critério de desambiguação, formato de saída de cada modo (parametrizado por stack).
- Regra "testing-first inegociável" no modo Implementação (comum aos 3, cada um com sua ferramenta de teste — Vitest/Jasmine, JUnit5, StepVerifier/WebTestClient).
- Checklist unificado "Antes de Analisar/Implementar" com placeholder por pilar técnico do domínio.

**Consumidores mapeados:**
- `angular`, `spring-boot`, `spring-reactive` (os 3 atuais).
- **Futuro:** qualquer novo specialist híbrido (ex.: `python-django`, `nodejs-nestjs`, `react`) herda o padrão sem reescrever ~90 linhas por agent.

**Impacto:** Redução de ~260 linhas duplicadas nos 3 agents atuais; acelera criação de futuros specialists híbridos via `agent-factory` (que passaria a referenciar esta skill como template adicional).

---

### C.4 — Resumo da Parte C

| Skill nova | Tier | Consumidores mapeados | Linhas duplicadas removidas (estimado) |
|---|---|---|---|
| `structured-intake-patterns` | 2 (process) | `bug-triage`, `test-fix`, `business-rules-extractor`, `requirements-analyst` | ~125 |
| `governance-factory-patterns` | 1 (governance) | `agent-factory`, `skill-factory`, `prompt-factory` | ~150 |
| `specialist-hybrid-advisory-implementation-patterns` | 1 (governance) | `angular`, `spring-boot`, `spring-reactive` | ~260 |

**Total estimado de redução de duplicação:** ~535 linhas + 90 linhas do item B.1 = **~625 linhas**, sem perda de capacidade funcional.

---

## 5) Parte D — Proposta Adicional: Agent de Auditoria Contínua de Governança

> Adicionado por solicitação explícita (2026-08-31). Formaliza como **capacidade permanente do catálogo** o tipo de análise manual feita neste próprio documento (Partes A/B/C) — hoje essa auditoria só acontece quando alguém pede manualmente.

### D.1 — Por Que Isso é Boa Prática (evidência de mercado)

Pesquisa (Tavily 2026) confirma que **governança de multi-agent systems deve ser processo contínuo, não checagem pontual**:

| Achado de mercado | Fonte |
|---|---|
| Governança "não deve ser tratada como exercício único — políticas devem ser revisadas regularmente conforme capacidades evoluem, novas tools são introduzidas, objetivos mudam" | Lumenova AI, "Governance Frameworks for Multi-Agent Systems" (2026) |
| Catálogo de **"LLM code smells"** (5 padrões problemáticos recorrentes, ferramenta `SpecDetect4LLM`, detectados estaticamente, 60,5% dos sistemas analisados tinham ao menos 1) — precedente direto para um catálogo de "agent/prompt smells" aplicado a `.agent.md`/`SKILL.md` | arXiv:2512.18020, "Specification and Detection of LLM Code Smells" (2026) |
| **Prompt Pattern Catalog**: catálogos formais de padrões reutilizáveis de prompt (intenção, contexto, problema, template, trade-offs) — base para comparar um agent contra "o que bom se parece" | EmergentMind, "Prompt Pattern Catalog" |
| **TrustAgent taxonomy**: separa componentes intrínsecos (brain/memory/tool) de extrínsecos (user/other agents/environment) para mapear riscos e gaps — framework aplicável para classificar gaps de perfil | KDD 2025, "A Survey on Trustworthy LLM Agents" |
| **OWASP Top 10 for Agentic Applications (2026)** — já referenciado pela skill `agent-safety-guardrails` deste projeto — cobre "excessive agency", "goal hijacking", riscos que um auditor de catálogo deve verificar estruturalmente (ex.: agent com tools além do necessário para seu escopo declarado) | OWASP GenAI Security Project, 2026 |
| Métricas de governança recomendadas vão além de "existe/não existe": **taxa de violação de política, completude de auditoria, frequência de intervenção humana** — não apenas contagem de arquivos | Lumenova AI (2026) |

**Distinção crítica em relação ao `/health` já existente:** `/health` (`.github/prompts/health.prompt.md`) faz **checagem estrutural/sincronização** (arquivo existe? contagem bate? YAML válido? R-038 aplicado?). O agent proposto aqui faz **análise semântica/qualitativa** do conteúdo (duplicação de lógica entre agents, regra normativa nunca referenciada, grupo taxonômico sem cobertura, anti-padrão de design) — exatamente o tipo de achado que gerou as Partes A/B/C deste próprio documento. Não há sobreposição — são complementares (`/health` = sintaxe/existência; novo agent = semântica/qualidade).

### D.2 — Escopo Proposto do Novo Agent

| Dimensão | Conteúdo |
|---|---|
| Papel (taxonomia) | Critic/Analyst aplicado à própria governança (meta-nível) — nunca aplica a correção, apenas analisa e recomenda, delegando a execução a `agent-factory`/`skill-factory`/`prompt-factory`/`docs-curator` |
| Escopo de leitura | `.github/agents/*.agent.md`, `.github/skills/*/SKILL.md`, `.github/prompts/*.prompt.md`, `docs/ai-context/routing-graph.yaml`, `docs/ai-context/evals/casos-roteamento.yaml`, `CLAUDE.md`, `.github/copilot-instructions.md` |
| Detecta — Anti-padrões estruturais | Blocos de conteúdo quase idênticos repetidos em 3+ arquivos sem skill equivalente (mesmo critério aplicado nas Partes B/C deste plano) |
| Detecta — Gaps de perfil | Agent sem `run_subagent` (R-042), sem seção "Retorno ao Router", sem banner "Agente Ativo", sem "Docs Sempre Anexadas", sem `version` quando aplicável — aplicando retroativamente o checklist que hoje `agent-factory` só valida em **criação nova** |
| Detecta — Gaps de diretrizes | Regra normativa (`R-001..R-042`) nunca referenciada por nenhum agent/skill; ou regra referenciada mas sem enforcement real (nenhum checklist a cobra) |
| Detecta — Diretrizes redundantes | Mesma regra/conteúdo duplicado em `CLAUDE.md` + `copilot-instructions.md` + skill (viola R-003 — "sem duplicação") |
| Detecta — Gaps de cobertura de categoria | Grupo taxonômico de `categorizacao-agents-mercado.md` §2 sem agent correspondente, ou com sobreposição de 2+ agents no mesmo papel (o próprio achado que gerou A.1/A.2 deste plano) |
| Saída | Relatório por severidade (Bloqueador/Alto/Sugestão — reaproveitando taxonomia já existente em `code-review-patterns`), com recomendação objetiva e handoff sugerido |
| Frequência de uso | Sob demanda (auditoria periódica do catálogo), não gatilho automático — análogo em cadência a `/health`, mas de profundidade semântica |

### D.3 — Skill Nova Associada: consolidação de "agent smells" de mercado

Para evitar que o novo agent invente critérios próprios, propõe-se criar a skill `governance-audit-patterns` (Tier 1, categoria `governance`) **consolidando pesquisa de mercado** antes da criação do agent (conforme solicitado):

| Fonte consolidada | O que aporta à skill |
|---|---|
| Catálogo de "LLM code smells" (`SpecDetect4LLM`, arXiv:2512.18020) | Padrão de catalogar "cheiros" com: nome, sintoma, efeito na qualidade, remediação — adaptado de código para artefatos `.agent.md`/`SKILL.md` |
| Prompt Pattern Catalog (EmergentMind) | Baseline de "como um prompt/agent bem estruturado se parece" para comparação |
| TrustAgent taxonomy (KDD 2025) | Framework intrínseco (brain/memory/tool) vs. extrínseco (user/other agents/environment) para classificar a origem do gap |
| OWASP Top 10 Agentic Applications (2026) | Cross-check de segurança (excessive agency, tool sprawl) já parcialmente coberto por `agent-safety-guardrails` — a skill nova referencia, não duplica |
| `code-review-patterns` (já existente neste projeto) | Taxonomia de severidade (bloqueador/alta/sugestão) — reaproveitada, não recriada |
| `agent-contracts/SKILL.md` § 8-9 (já existente) | Baseline de "formato de saída por perfil" e "tooling mínimo por perfil" — critério objetivo para detectar gap de perfil |

**Consumidor mapeado:** o novo agent proposto (único consumidor inicial).

### D.4 — Nome Definido

> **Decisão do mantenedor (2026-08-31):** nome escolhido — **`agent-auditor`**.

| Candidato avaliado | Racional |
|---|---|
| ✅ **`agent-auditor`** (escolhido) | Nome direto — comunica claramente "audita agents" (e por extensão, o catálogo de governança como um todo). |
| `governance-auditor` | Alternativa mais ampla — descartada em favor do nome escolhido. |
| `catalog-inspector` | Alternativa considerada — descartada. |
| `agent-doctor` | Alternativa considerada — descartada (risco de confusão com `/ctx-doctor`/`/health`). |
| `redundancy-auditor` | Alternativa considerada — descartada (escopo mais estreito que o real). |
| `governance-linter` | Alternativa considerada — descartada. |

**Escopo da skill `governance-audit-patterns` (D.3) confirmado pelo mantenedor** — prosseguir conforme descrito, sem ajustes adicionais.

---

## 6) Roadmap de Implementação

> Notação R-018: `[P]` paralelo, `[S]` sequencial.

### Fase 0 — Aprovação (bloqueante)
- `[S]` Apresentar este plano ao mantenedor e obter aprovação explícita por item (A.1, A.2, B.1, C.1, C.2, C.3, D) — nenhuma remoção/criação sem confirmação (R-033).
- `[S]` **Item D**: nome `agent-auditor` confirmado (§D.4) — pendente apenas aprovação final de execução.

### Fase 1 — Extração de Skills + Criação do `deep-search` (não quebra nada, é aditivo)
- `[P]` Criar `structured-intake-patterns` via `@skill-factory` `[fallback: revisar manualmente se skill-factory indisponível]`.
- `[P]` Criar `governance-factory-patterns` via `@skill-factory`.
- `[P]` Criar `specialist-hybrid-advisory-implementation-patterns` via `@skill-factory`.
- `[P]` Criar `deep-search.agent.md` via `@agent-factory` (item A.1 — Retriever interno+externo, template `research-agent.md`).
- `[P]` Criar skill `governance-audit-patterns` via `@skill-factory` (item D.3 — consolidação de padrões de mercado já pesquisados nesta análise).
- `[S]` Criar `agent-auditor.agent.md` via `@agent-factory` (nome confirmado em D.4), referenciando `governance-audit-patterns`.
- `[S]` Atualizar `.github/skills/.index.json` e `.github/skills/README.md` atomicamente (R-015).

### Fase 2 — Deduplicação de Agents Existentes (referenciam as skills novas)
- `[P]` Atualizar `bug-triage`, `test-fix`, `business-rules-extractor`, `requirements-analyst` para referenciar `structured-intake-patterns`.
- `[P]` Atualizar `agent-factory`, `skill-factory`, `prompt-factory` para referenciar `governance-factory-patterns`.
- `[P]` Atualizar `angular`, `spring-boot`, `spring-reactive` para referenciar `specialist-hybrid-advisory-implementation-patterns`.
- `[S]` Atualizar `adapter-generator` removendo tabelas de scanner duplicadas (item B.1).
- `[S]` `get_errors`/revisão de consistência em cada arquivo tocado.

### Fase 3 — Remoção/Substituição de Agents Redundantes
- `[S]` Validar `deep-search.agent.md` (criado na Fase 1) cobre 100% da Decision Tree antiga de `research-router` + pesquisa interna via terminal/`context-mode`.
- `[S]` Mover formato de saída B1 de `impact-architect` para `analysis-architect` (Etapa 4 do Método de Análise).
- `[S]` Atualizar `agent-router.agent.md` (Decision Tree + rotas) para apontar pesquisa diretamente a `@deep-search` e impacto local a `@analysis-architect` (tier B1).
- `[P]` Atualizar os ~10 agents que referenciam `@impact-architect` para apontar a `@analysis-architect` (tier B1).
- `[S]` Remover `research-router.agent.md` e `impact-architect.agent.md`.
- `[S]` Atualizar `catalog.yaml`, `agents/README.md`, `docs/ai-context/routing-graph.yaml`, `docs/ai-context/evals/casos-roteamento.yaml` (R-015/R-040) — inclui trocar nó `research-router` por `deep-search` no grafo.

### Fase 4 — Validação Final
- `[S]` Rodar suíte de evals de roteamento (`casos-roteamento.yaml`) para confirmar que nenhum caso canônico quebrou.
- `[S]` Relatório final: 24 → 24 agents (líquido: `deep-search` substitui `research-router`; `impact-architect` removido; `agent-auditor` adicionado), 45 → 49 skills, linhas duplicadas removidas.

---

## 7) Critérios de Rollback

- Se algum caso de eval de roteamento (`casos-roteamento.yaml`) quebrar após Fase 3 → reverter apenas a Fase 3 (skills e o novo `deep-search` da Fase 1/2 permanecem, pois são aditivos e não destrutivos).
- Se `deep-search` não conseguir cobrir a decisão de pesquisa hoje feita por `research-router` → manter `deep-search` para pesquisa interna e reintroduzir apenas a lógica de decisão externa que falhou.
- Se `analysis-architect` não conseguir absorver a carga de decisão de `impact-architect` em produção → reintroduzir apenas o agent específico que falhou, mantendo as skills extraídas e o `deep-search` já criado.

## 8) Não-Escopo Deste Plano

- Não avalia `docs-curator` vs `docs-writer` (distinção já validada por evals dedicados — `regr-008`/`regr-009`).
- Não avalia `test-strategy`/`test-implementation`/`test-fix` (fases distintas do ciclo de teste, sem sobreposição real).
- Não avalia `binding-initializer`/`adapter-generator`/`context-builder` (agents operacionais de bootstrap, escopo estritamente confinado e não sobreposto).

> **Nota de atenção (introduzida por A.1):** a criação de `deep-search` com pesquisa interna via `context-mode`/terminal aproxima seu escopo do de `context-builder` (hoje: coleta/condensa contexto e persiste em `docs/context/*.md`). Diferença preservada nesta versão: `deep-search` **responde/pesquisa sob demanda** (papel Retriever ad-hoc), `context-builder` **persiste artefato reutilizável** em arquivo (papel de preparação de contexto para consumo posterior). Ambos permanecem fora da Fase 0-4 deste plano — mas ficam sinalizados como candidatos a uma futura análise de sobreposição, caso você queira revisar.

## 9) Próximo Passo Mínimo

> **Status final (2026-08-31): plano executado integralmente (Fases 1-4).**

- Fase 1: criadas `structured-intake-patterns`, `governance-factory-patterns`, `specialist-hybrid-advisory-implementation-patterns`, `governance-audit-patterns` (skills), `deep-search` e `agent-auditor` (agents). `.index.json`/`README.md` de skills atualizados atomicamente (45→49 skills).
- Fase 2: deduplicados `bug-triage`, `test-fix`, `business-rules-extractor`, `requirements-analyst` (→ `structured-intake-patterns`); `agent-factory`, `skill-factory`, `prompt-factory` (→ `governance-factory-patterns`); `angular`, `spring-boot`, `spring-reactive` (→ `specialist-hybrid-advisory-implementation-patterns`); `adapter-generator` (item B.1 — tabelas de scanner removidas).
- Fase 3: `research-router.agent.md` e `impact-architect.agent.md` removidos fisicamente; `agent-router` e os ~10 agents com handoff cruzado atualizados para `@deep-search`/`@analysis-architect` (tier B1); `catalog.yaml`, `README.md`, `routing-graph.yaml`, `casos-roteamento.yaml` e `CLAUDE.md` (diagrama de roteamento) atualizados atomicamente.
- Fase 4: contagem final validada — **24 agents** (`ls .github/agents/*.agent.md` = 24), **49 skills**, zero referências residuais a `research-router`/`impact-architect` em todo o repositório (`grep_search` global).
- **Nota de validação:** `get_errors` reporta "Unknown model" em praticamente todo o catálogo de agents (inclusive arquivos não tocados nesta execução) — quirk pré-existente do validador de modelo desta sessão/IDE, não uma regressão introduzida por este plano.
- **Pendente (fora deste plano):** nota de sobreposição `deep-search` vs `context-builder` (§8) permanece registrada para análise futura, se solicitada.

