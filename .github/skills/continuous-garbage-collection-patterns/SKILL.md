---
name: continuous-garbage-collection-patterns
description: >-
  Diretrizes para varreduras periódicas de baixo custo ("Janitor Tasks") que
  detectam drift documental, código morto, duplicação de regras entre camadas
  de governança e desalinhamento entre catálogo/agents/skills em execução —
  complementando a auditoria sob demanda do agent-auditor/repo-hygiene-auditor
  com um modo de saneamento contínuo inspirado no conceito de "garbage
  collection" de código-fonte aplicado a artefatos de governança e documentação
  viva. Base de conhecimento para o modo autônomo de repo-hygiene-auditor e
  governance-maintainer.
tier: 2
category: process
triggers:
  - "garbage collection de governança"
  - "drift de documentação"
  - "saneamento contínuo"
  - "janitor task"
  - "higiene contínua do repositório"
  - "documentação defasada"
  - "código morto em governança"
  - "auditoria periódica"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/governance-audit-patterns/SKILL.md
  - .github/skills/repository-hygiene-patterns/SKILL.md
  - .github/skills/documentation-writing-patterns/SKILL.md
  - .github/skills/efficient-batch-code-modification/SKILL.md
tools: []
---

# Continuous Garbage Collection Patterns

## 0) Propósito

Enquanto `governance-audit-patterns` cataloga smells **estruturais** (frontmatter, tools, batching) e `repository-hygiene-patterns` avalia a **maturidade estática** do repositório (README, licença, CI), esta skill define o **modo contínuo/periódico** de saneamento: varreduras de baixo custo (idealmente Tier 1, sem LLM) que detectam **entropia acumulada** ao longo do tempo — documentação que ficou defasada em relação ao código real, agents/skills descomissionados ainda citados, duplicação de regras que deveriam ter sido consolidadas e drift entre o catálogo declarado e o estado real do repositório.

**Fundamentação de mercado**: OpenAI (*Harness engineering: leveraging Codex in an agent-first world*, Fev/2026) reporta que times que dependiam de limpeza manual periódica ("sextas-feiras de limpeza de AI slop") não escalavam — a solução foi codificar "princípios de ouro" mecânicos e um processo recorrente de *background tasks* que varrem o repositório, atualizam métricas de qualidade e abrem PRs cirúrgicos de correção. Martin Fowler/Thoughtworks (*Harness engineering for coding agent users*, Abr/2026) classifica esse tipo de sensor como **"Sensor Contínuo de Drift"**, distinto dos sensores acionados apenas no ciclo de mudança (pre-commit/CI).

## 1) Diferença entre os 3 Modos de Auditoria de Governança

| Modo | Quando roda | Escopo | Skill/Agent |
|---|---|---|---|
| **Sob Demanda (Reativo)** | Usuário pede explicitamente "audite X" | Artefato ou diff específico | `@agent-auditor`, `@repo-hygiene-auditor` |
| **Gate de Mudança (CI)** | A cada PR/commit | Diff atual | `tests/governance_audit/` (pytest) |
| **Contínuo/Periódico (Janitor)** | Executado sob demanda em intervalo recorrente (ex.: início de sessão, semanalmente) | Repositório inteiro, sem relação com um diff específico | Esta skill — consumida por `@repo-hygiene-auditor` (modo estendido) e `@governance-maintainer` (execução) |

## 2) Categorias de Drift Detectáveis

### 2.1 — Drift Documental (Documentação Defasada)
- **Sintoma**: `docs/*.md` descreve comportamento, contagem de agents/skills ou convenções que não correspondem mais ao estado real do `.github/agents/` ou `.github/skills/`.
- **Detecção determinística**: comparar contagens declaradas em prosa (ex.: "17 smells de governança", "60 skills") contra a contagem real via glob (`**/*.agent.md`, `**/SKILL.md`) e cabeçalhos `### 2.N` no `governance-audit-patterns/SKILL.md`.
- **Remediação**: `@docs-engineer` (modo curate) atualiza o número/lista para refletir o estado real.

### 2.2 — Referência Órfã (Agent/Skill Descomissionado Ainda Citado)
- **Sintoma**: `README.md`, `docs/` ou outro agent cita um nome de agent/skill que não existe mais no catálogo.
- **Detecção determinística**: extrair todos os nomes declarados em `catalog.yaml` e `.index.json`; buscar por menções a nomes **fora** dessa lista que sigam o padrão de nomenclatura de agent/skill (`@<kebab-case>`).
- **Remediação**: `@docs-engineer` remove/atualiza a referência; já coberto parcialmente por Smell 2.1 (`governance-audit-patterns`).

### 2.3 — Duplicação de Regra Não Consolidada
- **Sintoma**: A mesma regra normativa (R-0XX) é reexplicada com texto divergente em 2+ arquivos que deveriam apenas referenciar `CLAUDE.md`.
- **Detecção determinística**: já coberto por Smell 2.4 (`governance-audit-patterns`) — esta skill adiciona a dimensão de **frequência de execução periódica**, não apenas gate de PR.

### 2.4 — Drift de Sincronização de Catálogo (R-015)
- **Sintoma**: Um agent existe em `.github/agents/**/*.agent.md` mas não está listado em `catalog.yaml`, `routing-graph.yaml` ou `.github/agents/README.md` (ou vice-versa — entrada órfã sem arquivo correspondente).
- **Detecção determinística**: comparação de conjuntos (glob de arquivos físicos vs. chaves declaradas nos YAMLs/README).
- **Remediação**: `@governance-maintainer` sincroniza os 4 artefatos (catálogo, grafo, evals, README) em lote único (R-046).

### 2.5 — Skill Órfã (Sem Consumidor Declarado)
- **Sintoma**: Uma `SKILL.md` existe mas nenhum agent a referencia em `source_docs:`.
- **Detecção determinística**: para cada skill em `.index.json`, verificar se `related_agents` é não-vazio E se pelo menos 1 agent físico realmente cita o caminho da skill em `source_docs:`.
- **Remediação**: `@governance-factory` decide se a skill deve ser vinculada a um agent existente, arquivada ou removida (decisão humana via `ask_questions` antes de deletar).

## 3) Protocolo de Execução (Janitor Run)

1. **Trigger**: Executado sob demanda explícita do usuário (`"rode uma varredura de higiene contínua"`, `"detecte drift de documentação"`) ou como parte do `WORKFLOW-GOVERNANCE-MAINTENANCE` quando o diagnóstico do Estado 1 identificar sinais de entropia acumulada (não é daemon nem cron — este repositório não possui execução em background autônoma).
2. **Coleta (Tier 1, zero tokens quando possível)**: Preferir scripts determinísticos (`ctx_execute` no sandbox) que comparam globs de arquivos físicos contra listas declarativas (catálogo, índice de skills, READMEs) — mesma filosofia de `test_governance_smells.py`.
3. **Relatório Consolidado**: Agrupar achados por categoria (§ 2.1–2.5), citando `arquivo:linha` (R-044) e usando o helper `remediation()` (ver `_helpers.py` de `tests/governance_audit/`) como padrão de mensagem quando aplicável a asserts formais.
4. **Checkpoint Humano**: Nenhuma remoção de arquivo (skill/agent órfã) é executada sem aprovação explícita via `ask_questions` — drift documental (§ 2.1) pode ser corrigido diretamente pelo `@governance-maintainer` em lote (R-046) por ser reversível e de baixo risco.
5. **Fechamento**: Se novos padrões recorrentes de drift forem identificados, o `@governance-maintainer` avalia se vale a pena promover a detecção para um teste determinístico permanente em `tests/governance_audit/` (Q3 do Portão de Reúso R-055), evitando que o mesmo drift precise ser encontrado manualmente de novo no futuro.

## 4) Checklist de Conformidade

- [ ] Achados classificados em uma das 5 categorias de drift (§ 2.1–2.5).
- [ ] Toda detecção determinística preferida a julgamento semântico (LLM) — mesma hierarquia Two-Tier de `governance-audit-patterns` § 1.1.
- [ ] Remoção de artefato (skill/agent órfão) sempre precedida de `ask_questions`.
- [ ] Drift recorrente promovido a teste permanente em `tests/governance_audit/` quando aplicável (R-055 Q3).
- [ ] Relatório final aponta agent executor da remediação (nunca aplica a correção no mesmo turno de diagnóstico sem aprovação, salvo item de baixo risco explicitamente elegível).

## 5) Anti-padrões

- ❌ Tratar esta skill como justificativa para rodar scripts de varredura manual fora do `@code-knowledge-graph` quando a análise for de dependências/chamadas de código de aplicação (fora de escopo — isso é R-045).
- ❌ Deletar uma skill ou agent "órfão" sem checkpoint humano.
- ❌ Duplicar os smells já cobertos por `governance-audit-patterns` — esta skill referencia, não recria.
- ❌ Promover toda variação cosmética a "drift" — o foco é entropia que causa confusão real ao agente consumidor (contagens erradas, referências quebradas, sincronização de catálogo).

## 6) Consumidores Mapeados

- `@repo-hygiene-auditor` (modo estendido de higiene contínua, além da auditoria estática pontual).
- `@governance-maintainer` (execução da remediação em lote após checkpoint humano).
- `@agent-auditor` (pode citar esta skill ao classificar um achado como drift acumulado vs. smell estrutural pontual).

## 7) Referências

- `governance-audit-patterns/SKILL.md` — catálogo de smells estruturais (Tier 1/2).
- `repository-hygiene-patterns/SKILL.md` — matriz de maturidade estática.
- OpenAI, *Harness engineering: leveraging Codex in an agent-first world* (Fev/2026).
- Martin Fowler/Thoughtworks, *Harness engineering for coding agent users* (Abr/2026).

