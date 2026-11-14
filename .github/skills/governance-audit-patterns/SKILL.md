---
name: governance-audit-patterns
description: "Define o catálogo canônico de Smells de Governança (2.1 a 2.33), matriz Perfil ↔ Tools ↔ Skills e arquitetura Two-Tier Hybrid (Quality Gate Estático + LLM Audit) para auditoria do ecossistema. Use quando auditar agents, skills, prompts, catálogos e contratos normativos. Não use para aplicar refatorações mutativas em lote (delegar a @governance-maintainer) ou criar artefatos do zero (delegar a @governance-factory)."
tier: core
category: governance
triggers:
  - "auditar governança"
  - "governance smells"
  - "auditar agentes"
  - "verificar conformidade de skills"
  - "validar catálogo"
source_docs:
  - .github/agents/agent-auditor.agent.md
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Governance Audit Patterns

## Quando Usar

- Ativação em cenários de auditar governança, governance smells, auditar agentes.

## 0) Propósito e Problema Resolvido

Padroniza a auditoria estática e semântica do ecossistema de governança (`.github/agents/`, `.github/skills/`, `.github/prompts/`, `catalog.yaml`, `routing-graph.yaml`, `.index.json`), combinando sensores determinísticos em `tests/governance_audit/` com inspeção semântica read-only por `@agent-auditor`.

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Auditar conformidade de agents, skills, prompts e catálogos contra os templates SSOT e regras normativas (`CLAUDE.md`).
- Detectar smells estruturais (`2.1` a `2.33`), deriva contratual, violação de Progressive Disclosure (`R-066`) ou vazamento de evidências (`R-044`).

### ❌ Quando NÃO Usar
- Executar modificações em lote nos arquivos auditados — delegar a `@governance-maintainer` (`R-057`).
- Criar novos agents, skills, prompts ou stacks do zero — delegar a `@governance-factory`.

## 2) Diretrizes e Padrões Canônicos — Arquitetura Two-Tier Hybrid e Catálogo de Smells

### 2.0) Arquitetura Two-Tier Hybrid (Quality Gate Estático + LLM Audit)
- **Tier 1 (Determinístico / `pytest tests/governance_audit/`)**: Valida invariantes sintáticas, frontmatter, seções de templates SSOT (`test_template_sections.py`), orçamento de Progressive Disclosure (`R-066` / `≤ 300 linhas`) e paridade de catálogos (`R-015` / `R-040`).
- **Tier 2 (Semântico / `@agent-auditor`)**: Avalia coerência de escopo, sobreposição semântica (`R-003`), qualidade de exemplos contrastantes (`✅ BOM` vs `❌ RUIM`) e aderência de perfis.

> **Progressive Disclosure (`R-066`)**: As tabelas completas de detecção, exemplos detalhados e matrizes estendidas dos Smells `2.1` a `2.34` residem em `references/smells-catalog-detailed.md`. Abaixo está o índice normativo canônico obrigatório:

### 2.1 — Anti-padrão Estrutural (Duplicação sem Skill Equivalente)
Instruções técnicas repetidas em múltiplos agents sem extração para `SKILL.md` compartilhada (`R-003`).

### 2.2 — Gap de Perfil (Agent Incompleto)
Ausência de seções obrigatórias do template SSOT (`ESCOPO E NÃO-ESCOPO`, `Quando Delegar`, `Formato de Saída`, `Checklist`, `Retorno ao Router`, `Combina Com`, `<execution_protocol>`).

### 2.3 — Gap de Diretriz (Regra Não Referenciada ou Sem Enforcement)
Regra normativa declarada em `CLAUDE.md` sem enforcement correspondente em template, skill ou teste em `tests/governance_audit/`.

### 2.4 — Diretriz Redundante (Duplicação entre Camadas de Governança)
Cópia literal extensa de regras entre `CLAUDE.md`, `copilot-instructions.md`, agents e skills em vez de referência à SSOT (`source_docs` / `source_docs_lazy`).

### 2.5 — Gap de Cobertura de Categoria (Taxonomia)
Artefato órfão ou ausente em `catalog.yaml`, `routing-graph.yaml`, `.index.json` ou `agent-router.agent.md` (`R-015` / `R-040`).

### 2.6 — Vazamento de Evidência Real (R-044)
Presença de paths locais de máquina, nomes de sistemas internos, credenciais ou IDs de demandas reais em artefatos versionados (`R-038` / `R-044`).

### 2.7 — Desalinhamento Contratual (Perfil ↔ Tools ↔ Skills ↔ Catálogo)
Divergência entre o perfil do agent (`Router`, `Analítico/Read-Only/Advisor`, `Executor/Developer/Test-Engineer`), suas `tools:`, `source_docs:`/`source_docs_lazy:` e `catalog.yaml`.

### 2.7.1 — Matriz Canônica de Conformidade (Perfil ↔ Tools ↔ Skills)
- `Router`: sem tools de escrita; requer `run_subagent` e `handoff-governance`.
- `Analítico/Read-Only/Advisor`: sem tools de edição (`insert_edit_into_file`, `create_file`, `replace_string_in_file`); requer `run_subagent` e `context-mode/ctx_search`.
- `Executor/Developer/Test-Engineer`: possui tools de mutação/execução (`ctx_execute`, `ctx_batch`, `get_errors`) e skills `safe-file-editing` / `efficient-batch-code-modification`.
- **Invariante Sintática de `tools:`**: Em `.agent.md`, `.prompt.md` e `SKILL.md`, o campo `tools:` no frontmatter deve ser declarado estritamente em sintaxe inline `tools: ['...']` (ou `tools: []`), sendo proibido o formato de lista YAML multilinha (`tools:\n  - ...`).

### 2.8 — Violação de Batching e Limiar de Modificação (R-046)
Edições sequenciais arquivo a arquivo no chat em vez de consolidação em lote via `ctx_batch` / `ctx_execute` (`R-046` / `R-059`).

### 2.9 — Não Conformidade com Template Canônico de Agent e Matriz de Modelo
Desvio das seções de `.github/agents/templates/{agent-template,operational-agent,research-agent,router-agent}.md` ou fixação indevida de modelo tier máximo (`Claude Opus`) sem `model_exception_reason:` (`R-021`).

### 2.10 — Desvio de Sintaxe e Variáveis em Prompts (`.prompt.md`)
Ausência de variáveis nativas (`${file}`, `${selection}`, `${workspaceFolder}`), seções obrigatórias de `.github/prompts/templates/prompt-template.md` ou `<execution_protocol>` (`R-059`/`R-060`).

### 2.11 — Não Conformidade com a Spec de Skills (Progressive Disclosure)
`SKILL.md` sem frontmatter em 3ª pessoa (`Fornece/Define... Use quando... Não use para...`), sem seções canônicas de `.github/skills/templates/skill-template.md` ou excedendo `≤ 300 linhas` sem extrair detalhes para `references/` (`R-066`).

### 2.12 — Conflito de Responsabilidade Cross-Artefato (Agents vs Prompts vs Skills)
SSOT invertido: listar `.prompt.md` em `source_docs:`/`source_docs_lazy:` ou embutir regras de domínio exclusivas dentro de prompts em vez de `SKILL.md`.

### 2.13 — Hipertrofia Instrucional e Redundância de Saída em Runtime (Output Bloat / Multi-Layer Redundancy)
Listas de pré-carregamento manual de skills no corpo markdown do agent duplicando `source_docs:`/`source_docs_lazy:` do frontmatter.

### 2.14 — Evidência Real Não-Anonimizada em Evals Minerados (Violação R-044 na Telemetria)
Prompts ou casos em `evals/` contendo nomes próprios, rotas privadas ou dados reais sem sanitização (`R-044`).

### 2.15 — Acoplamento Rígido de Range Normativo (Hardcoded Normative Range Coupling)
Referências estáticas frágeis a intervalos de regras (ex.: `R-001 a R-050`) que ficam obsoletas quando novas regras `R-0xx` são adicionadas.

### 2.16 — Agent Mutativo Sem Skill de Edição Segura Referenciada (R-051)
Agente com permissão de mutação de código sem referenciar `safe-file-editing` em `source_docs:` e validação com `get_errors` (`R-051`).

### 2.17 — Comando Git Sem Desativação de Pager (Violação R-035)
Invocação de `git log`, `git diff`, `git show` ou `git branch` sem `--no-pager` ou `GIT_PAGER=cat` (`R-035`).

### 2.18 — Gap de Definição de Pronto (Feature Não-Alcançável / Rota Órfã de Navegação)
Componente/página criada sem registro em rotas, menu ou ponto de entrada alcançável pelo usuário (`R-050`).

### 2.19 — Ausência de Verificação de Reuso de Design System / Componentes Compartilhados
Criação de componente visual duplicado sem inspecionar biblioteca compartilhada do projeto (`R-050`).

### 2.20 — Duplicação por Aninhamento de Router (Nested Subagent Sprawl)
Encadeamento desnecessário `router -> sub-router -> specialist` quando o roteamento direto já está resolvido.

### 2.21 — Cegueira Visual e Suposição de Contratos de UI (Visual Blindness & Unverified UI Contracts)
Agentes de frontend (`*-developer`, `*-test-engineer`) sem integração `playwright-mcp` (`playwright/browser_*` + `.github/skills/playwright-mcp/SKILL.md` em `source_docs`).

### 2.22 — Sticky Agent e Falha de Reset de Workflow (R-042 / R-052)
Retenção indevida de controle por agente especialista após conclusão de workflow ou diante de deriva de intenção, sem retornar a `@agent-router` (`conclusao_de_workflow_anterior` / `deriva_de_intencao`).

### 2.23 — Router Over-Empowerment e Pre-Routing Discovery Bloat (R-054)
Orquestrador/router violando a diretriz de **Zero Discovery** (`ZERO TOOL CALLS DE DISCOVERY`) ao executar exploração profunda antes de delegar ao especialista (`R-054`).

### 2.24 — Omissão de Precedência de Context-Mode em Agentes Mutadores e Leitores (Editor Tool Sprawl / R-056)
Uso de ferramentas nativas de editor/terminal quando o `context-mode` é **100% obrigatório**, devendo as tools nativas atuar apenas como **fallback exclusivo** de indisponibilidade (`R-008` / `R-056`).

### 2.25 — Terceirização Indevida de Edição ao Usuário por Agentes Analíticos / Read-Only (Anti-Manual User Delegation & Dead-End Analysis / R-057)
Agente analítico/read-only que instrui o usuário a editar arquivos manualmente ("adicione a linha X", "edite o arquivo Y") em vez de delegar ao agente operacional ou retornar ao `@agent-router` (`R-057`).

### 2.26 — MCP Tool Chaining Sequencial no Chat / Omissão de ctx_batch e Script Consolidado (R-008 / R-046 / R-056)
Múltiplas chamadas unitárias sequenciais no chat em vez de **Single-Turn MCP Batching** via chamada única de `ctx_batch` ou script iterativo consolidado (`R-008` / `R-046` / `R-056` / `R-059`).

### 2.27 — Desvio Prematuro para Implementação e Despejo de Lacunas Arquiteturais (Premature Implementation Bypass & Gap Dumping / R-058)
Pular o gate de Blueprint Técnico de `@tech-solution-architect` em tarefas arquiteturais/cross-stack ou despejar perguntas técnicas abertas ao usuário sem recomendação fundamentada (`R-058`).

### 2.28 — Mensagem de Sensor Sem Remediação Acionável (Non-Actionable Assertion Message / Anti Positive Prompt Injection)
Testes em `tests/governance_audit/` cujo `assert` falha sem mensagem explicando `AÇÃO CORRETIVA:` / como remediar deterministicamente o erro.

### 2.29 — Root Orchestrator Agent Impersonation (R-062)
O orquestrador raiz (`agent-router`) finge ser um especialista (emitindo `Agente Ativo: <especialista>`) sem invocar `run_subagent` real (`R-062`).

### 2.30 — Silent Root Tool Execution / Zero-Agent Router Bypass (R-063)
O orquestrador raiz executa tools de inspeção/edição diretamente para responder ao usuário sem delegar via `run_subagent` e sem emitir banner (`R-063`).

### 2.31 — Progressive Disclosure Violation / Full-Load Forçado de Documento Lazy (R-066)
Manter documento `> 300 linhas` em `source_docs:` (full-load) em vez de `source_docs_lazy:` (consulta via `ctx_search`), ou `SKILL.md > 300 linhas` sem extrair para `references/` (`R-066`).

### 2.32 — Capability Overreach de `ctx_execute` (com `file`) em Agent Gather-only (R-008 / R-046 / R-056 / R-059)
Agente estritamente read-only/gather-only que utiliza `ctx_execute` para mutar estado ou executar ações fora do perfil analítico.

### 2.33 — Importação de Skill Externa sem Avaliação de Pertinência (Skill Import Viability Gate / R-067)
Materializar ou copiar skill externa sem executar os 4 critérios do gate `R-067` (Pertinência, Duplicidade, Aderência Estrutural e Guardrails) ou omitir proveniência (`adapted_from`, `source_url`, `source_license`, `adaptation_notes`).

### 2.34 — Violação da Árvore `docs/plans/<tipo>/` e Escrita Direta por Planejador Read-Only (R-064)
Plano fora de `docs/plans/<tipo>/` (incl. caminhos legados `docs/plans/implementation/`, `docs/plans/requirements/`), frontmatter R-064 comum ausente/incompleto, `plan_type` divergente da subpasta, ou agent planejador/advisor (`*-arch-advisor`, `tech-solution-architect`, `test-strategy`, `bug-triage`, `requirements-analyst`) com tools mutativas/escrita direta do `.md` em vez de handoff a `@docs-engineer`/`@governance-maintainer`.

## 3) Severidade e Formato de Saída Recomendado

- **Severidades**: `CRITICAL` (violação de segurança, `R-044`, `R-062`, `R-063`, quebra de catálogo `R-015`), `HIGH` (smells `2.7`, `2.9`–`2.12`, `2.24`–`2.33`), `MEDIUM` (redundância `2.4`, `2.13`), `LOW` (ajustes cosméticos).
- **Formato de Saída**: Tabela estruturada com `[ID do Smell | Severidade | Arquivo:Linha | Evidência | Remediação Acionável]`.

## 4) Checklist de Conformidade da Auditoria

- [ ] Todos os diretórios (`.github/agents/`, `.github/skills/`, `.github/prompts/`) e catálogos cruzados foram verificados em lote (`ctx_batch`).
- [ ] Sensores estáticos (`pytest tests/governance_audit/ -q --tb=short`) executados e validados.
- [ ] Nenhum arquivo foi modificado diretamente pelo auditor read-only (`R-057`).

## 5) Referências e Documentação Conexa

- `references/smells-catalog-detailed.md` — Tabelas completas, exemplos contrastantes (`✅ BOM` vs `❌ RUIM`), heurísticas de detecção e matrizes detalhadas dos Smells `2.1` a `2.33` (`Progressive Disclosure` / `R-066`).
- `references/plan-template-governance.md` — template de plano `governance` (R-064) em `docs/plans/governance/`.
- `.github/skills/governance-factory-patterns/SKILL.md` — Padrões canônicos de criação e templates SSOT.
- `tests/governance_audit/` — Suíte determinística de sensores e Quality Gates.
- `CLAUDE.md` e `.github/copilot-instructions.md` — Regras normativas do repositório.

| 2.32 | **Degradação de UX no `ask_questions` (R-027 / CA-03..CA-05)**: opções sem `description` estruturado (`[Consequência prática] + [Trade-off]`), omissão de `(Recomendado)` na 1ª opção em decisão técnica, opções espantalho (*strawman*) / dummy `"Outro"` ou violação dos limites ergonômicos (2–4 opções, 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`). | Médio | Exigir `description` com consequência + trade-off, 1ª opção `(Recomendado)` (salvo decisão puramente de negócio), 2–4 opções reais mutuamente exclusivas, 1–4 perguntas, `header` ≤ 25 chars e `allowFreeformInput: true` (`structured-intake-patterns`). |
