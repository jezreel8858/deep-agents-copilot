---
name: governance-factory-patterns
description: "Define o fluxo canônico 'Factory Pattern' para criar, revisar e manter artefatos de governança (agent, skill, prompt e stack), incluindo Decision Tree, templates SSOT e checklists de qualidade. Use quando criar ou auditar agents, skills, prompts ou stacks. Não use para implementar código de aplicação de negócio ou executar auditoria read-only isolada."
tier: core
category: governance
triggers:
  - "criar agente"
  - "criar skill"
  - "criar prompt"
  - "nova stack"
  - "ecossistema de agentes"
  - "factory pattern"
  - "atualizar catálogo"
  - "checklist de criação"
source_docs:
  - .github/agents/governance-factory.agent.md
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Governance Factory Patterns

## Quando Usar

- Ativação em cenários de criar agente, criar skill, criar prompt.

## 0) Problema Resolvido

Formaliza o fluxo canônico compartilhado pelos 4 tipos de artefatos e subsistemas de governança criados/revisados por `@governance-factory` e mantidos por `@governance-maintainer` (**agent**, **skill**, **prompt** e **stack** — ecossistema de domínio completo), garantindo paridade com os templates SSOT em `.github/agents/templates/`, `.github/prompts/templates/` e `.github/skills/templates/`.

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Criar ou revisar `.agent.md`, `SKILL.md`, `.prompt.md` ou uma nova `stack` de domínio.
- Sincronizar contratos estruturais de artefatos com os templates SSOT e regras `R-015`, `R-040`, `R-055`, `R-066` e `R-067`.
- Avaliar pertinência de importação de skills externas antes da materialização (`R-067`).

### ❌ Quando NÃO Usar
- Implementar regras de negócio ou código de aplicação (`backend`, `frontend`, `mobile`) — delegar ao developer da stack.
- Executar auditoria estática/read-only de smells sem criação ou refatoração — usar `governance-audit-patterns` com `@agent-auditor`.

## 2) Diretrizes Operacionais e Decision Tree Canônica (Factory Pattern)

```text
Solicitação (create / update / review de agent | skill | prompt | stack)
  ├─ 1. Gate de Pertinência / Anti-Duplicidade (R-003 / origem = IMPORTAÇÃO EXTERNA -> Gate R-067 §3.4)
  ├─ 2. Classificação de Tipo e Perfil (Router | Analítico/Read-Only/Advisor | Executor/Developer/Test-Engineer)
  ├─ 3. Seleção de Template SSOT (.github/{agents,prompts,skills}/templates/)
  ├─ 4. Aplicação de Progressive Disclosure (R-066: SKILL.md <= 300 linhas; docs > 300 linhas em source_docs_lazy)
  ├─ 5. Gate de Autocrítica Semântica (1 round grounded) + Portão de Reúso Sistêmico (R-055 Q1/Q2/Q3)
  └─ 6. Atualização Atômica de Catálogos (R-015 / R-040) + Validação pytest / get_errors
```

## 3) Padrões Canônicos e Campos Obrigatórios por Tipo de Artefato

> Detalhamento completo e exemplos estendidos em `references/artifact-specs-and-stack-topology.md`.

### 3.1) `type: agent` (`.github/agents/templates/{agent-template,operational-agent,research-agent,router-agent}.md`)
- **Parametrização por Perfil**:
  - `Router`: triagem, Decision Tree, delegação via `run_subagent` com banner `R-042`, zero edição direta (`R-062`/`R-063`).
  - `Analítico/Read-Only/Advisor`: diagnóstico e blueprint acionável sem mutar arquivos e sem terceirizar edição manual ao usuário (`R-057`/`R-058`).
  - `Executor/Developer/Test-Engineer`: mutação em lote (`Plan-Then-Batch` / `R-059`), validação `get_errors` (`R-051`) e teto `≤ 5` turnos (`R-060`).
- **Frontmatter YAML obrigatório**: `name`, `description` (3ª pessoa, `≤ 400` chars), `model` (conforme matriz §9 e `R-021`), `tools` (menor privilégio + `run_subagent`, estritamente em sintaxe inline `tools: ['...']` — proibido formato de lista YAML multilinha `tools:\n  - ...`), `skills`, `source_docs` (docs `≤ 300` linhas) e `source_docs_lazy` (docs `> 300` linhas, `R-066`).
- **Seções canônicas obrigatórias**: `Perfil`, `ESCOPO E NÃO-ESCOPO`, `Diretrizes`, `Quando Delegar`, `Checklist`, `Formato de Saída`, `Anti-padrões`, `Combina Com`, `Retorno ao Router (R-042)` e `<execution_protocol>` (`R-059`/`R-060`).

### 3.2) `type: prompt` (`.github/prompts/templates/prompt-template.md`)
- **Frontmatter YAML obrigatório**: `name`, `description`, `agent`, `model`, `tools` (estritamente inline `tools: ['...']`, proibido `tools:\n  - ...`), `argument-hint`, `source_docs`, `source_docs_lazy`.
- **Seções obrigatórias**: `## 🎯 Invocação e Variáveis Nativas` (`${file}`, `${selection}`, `${workspaceFolder}`), `## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO`, `## 📋 Fluxo de Execução Passo a Passo`, `## ✅ Checklist Antes de Apresentar`, `## 📊 Formato de Saída` e `## ⚙️ Protocolo de Execução Obrigatório` (`<execution_protocol>` com `R-059`/`R-060`).

### 3.3) `type: skill` (`.github/skills/templates/skill-template.md`)
- **Frontmatter YAML obrigatório**: `name` e `description` em 3ª pessoa com gatilhos explícitos (`Fornece/Define... Use quando... Não use para...`, `≤ 400` chars), `tools` (estritamente em sintaxe inline `tools: ['...']` ou `tools: []` — proibido formato multilinha `tools:\n  - ...`), além de metadados de proveniência quando adaptada (`R-067`).
- **Seções obrigatórias**: `## Quando Usar`, `## Quando NÃO Usar`, `## Diretrizes` / `## Padrões` (com exemplos contrastantes `✅ BOM` vs `❌ RUIM`), `## Checklist` e `## Referências`.
- **Progressive Disclosure (`R-066`)**: teto estrito de `≤ 300 linhas` no `SKILL.md` principal, extraindo tabelas/catálogos/exemplos extensos para `references/`.

### 3.6) Enforcement de Agents de Planejamento (R-064 / CA-04 — mandatório)

Todo agent criado ou revisado que atue em planejamento, arquitetura (`*-arch-advisor`, `tech-solution-architect`), estratégia de testes (`test-strategy`), triagem (`bug-triage`) ou requisitos (`requirements-analyst`) DEVE: (a) manter perfil **100% Read-Only**; (b) vincular-se ao template de plano da sua skill com frontmatter R-064; (c) apontar para `docs/plans/<tipo>/`; (d) declarar handoff de materialização física `.md` para `@docs-engineer` (ou `@governance-maintainer`). Detalhes em `references/artifact-specs-and-stack-topology.md` §2.1.

## 4) Checklist de Qualidade Estrutural e Gates Obrigatórios

### 3.1) Gate de Autocrítica Semântica (grounded, 1 round — obrigatório)
Revisar o artefato gerado contra escopo negativo, ausência de escopo fantasma e paridade com o template SSOT antes de persistir.

### 3.2) Portão de Reúso e Generalização Sistêmica (R-055 / Anti-Silo Fix — obrigatório em revisões)
Responder obrigatoriamente antes de concluir:
- **Q1 (Artefatos Irmãos / Peers)**: outros agents/skills do mesmo perfil possuem a mesma lacuna?
- **Q2 (Template Canônico / Herança)**: deve ser propagado para `.github/{agents,prompts,skills}/templates/` ou `required_source_docs_rules.json`?
- **Q3 (Enforcement Determinístico)**: requer teste automatizado em `tests/governance_audit/`?

### 3.3) Retrofit e Descoberta de Consumidores Pós-Criação de Skill (obrigatório)
Mapear agents consumidores em `.github/agents/` e registrar a skill em `source_docs:` (se `≤ 300` linhas) ou `source_docs_lazy:` (se `> 300` linhas, `R-066`) e em `.github/skills/.index.json`.

### 3.4) Protocolo de Avaliação de Pertinência de Importação de Skills (Skill Import Viability & Solution Alternative Gate — R-067, obrigatório em toda importação externa)
Antes de importar ou adaptar qualquer skill externa (URL, repositório GitHub, marketplace), executar obrigatoriamente os **4 critérios de avaliação**:
1. **Critério de Pertinência**: A skill resolve problema real das stacks do repositório ou introduz peso morto?
2. **Critério de Duplicidade**: Já existe skill em `.github/skills/` (`.index.json`) com escopo equivalente ou sobreposto (`R-003`)?
3. **Critério de Aderência Estrutural**: O conteúdo pode ser adaptado ao padrão N1/N2/N3 (frontmatter, Progressive Disclosure `≤ 300` linhas, `tier`/`category`/`triggers` em PT-BR)?
4. **Critério de Guardrails**: Compatível com `R-031`, `R-038` e `R-044`?
- **Desfecho**: (a) Aprovada com adaptação + Proveniência (`adapted_from`, `source_url`, `source_license`, `adaptation_notes`); (b) Rejeitada com reporte de impacto negativo e proposta obrigatória de **solução alternativa**; (c) Inconclusiva → consultar usuário via `ask_questions`.

### 3.5) Checklist de Genericidade (R-038) e Anonimização (R-044)
- [ ] Zero caminhos locais de máquina, nomes de projetos reais, endpoints internos ou IDs de demandas (`R-038` / `R-044`).
- [ ] Sincronização atômica (`R-015` / `R-040`): `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md`, `evals/casos-roteamento.yaml`, `.index.json`, `copilot-instructions.md`, `CLAUDE.md`, `README.md` e `CHANGELOG.md`.

## 5) Formato de Saída — Bloco de Validações ✅/❌ (parametrizável)

- ✅ Template SSOT respeitado (`agent-template.md` / `prompt-template.md` / `skill-template.md`).
- ✅ Progressive Disclosure (`R-066`): `SKILL.md ≤ 300 linhas` e `source_docs` vs `source_docs_lazy` sincronizados.
- ✅ Atualização Atômica (`R-015` / `R-040`) e Portão `R-055` (Q1/Q2/Q3) validados.
- ❌ Anti-padrões bloqueados: criar artefato sem consultar `.index.json`/`catalog.yaml`, omitir `Non-Scope`, exceder 300 linhas em `SKILL.md` ou fixar modelo Opus permanentemente sem exceção formal (`R-021`).

## 6) Seleção de Modelo (`model:` — R-021), `description` e Topologia de Stacks (`type: stack`)

- **Classificação de Perfil (`model:` — R-021)**:
  - `"Gemini 3.8 Flash"`: Perfil Procedural / Operacional / SLM de alta velocidade (routers, executores leves).
  - `"Claude Sonnet 5.5"` / `"Gemini 4 Argon"`: Perfil Decompositivo / Deliberativo (arquitetura, `*-developer`, `*-test-engineer`).
  - Proibido fixar tier máximo (`Claude Opus`) permanentemente sem `model_exception_reason:` formalizado (`R-021`). Validar disponibilidade real na IDE (VS Code vs JetBrains).
- **Tamanho e Conteúdo da `description`**:
  - `agent` e `skill`: `≤ 400` caracteres em 3ª pessoa (`Fornece/Define... Use quando... Não use para...`).
  - `prompt`: `≤ 200` caracteres em 3ª pessoa.
- **Topologia para Novas Stacks (`type: stack`)**:
  - Isolamento em `.github/agents/<categoria>/<stack>/`, sub-catálogo local `<stack>-catalog.yaml`, supervisor `<stack>-router.agent.md`, pacote canônico `3+1` (`router`, `arch-advisor`, `developer`, `test-engineer`) e Quádrupla Sincronização Global (`R-015`). Ver detalhes completos em `references/artifact-specs-and-stack-topology.md`.

## 7) Referências e Documentação Conexa

- `references/artifact-specs-and-stack-topology.md` — Tabelas completas de campos, exemplos antes/depois, validação de modelos e topologia detalhada de stacks (`Progressive Disclosure` / `R-066`).
- `.github/agents/templates/agent-template.md`, `operational-agent.md`, `research-agent.md`, `router-agent.md` — Templates SSOT de Agents.
- `.github/prompts/templates/prompt-template.md` — Template SSOT de Prompts.
- `.github/skills/templates/skill-template.md` — Template SSOT de Skills.
- `CLAUDE.md` e `.github/copilot-instructions.md` — Regras normativas da governança.
