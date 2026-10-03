---
status: concluído
date: 2026-10-03
autor: governance-factory
workflow: WORKFLOW-GOVERNANCE-MAINTENANCE
related-planning-doc: docs/plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md
progress: 100
---

# Plano de Implementação — Progressive Disclosure de `source_docs:` (R-066)

- **Workflow**: WORKFLOW-GOVERNANCE-MAINTENANCE — Etapa 4 (Plano de Implementação, R-058)
- **Gate**: 2º gate do Duplo Gate Documental (R-064) — **Status: ✅ APROVADO E EXECUTADO (100% concluído)**
- **Autor**: governance-factory
- **Data**: 2026-10-03
- **Documento-base**: `docs/plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md` (Plano de Planejamento aprovado — Opção B adotada: alterar `sync_required_source_docs.py` + schema; R-066 confirmada livre; R-065 já ocupada)

## 0.0 Status de Execução (100% concluído)

| Frente | Status | Observação |
|---|---|---|
| T0 (INV-01/02/03) | ✅ Concluído | Achados corrigiram materialmente premissas do plano original — ver §0.3 |
| F4 (Regra R-066) | ✅ Concluído | `CLAUDE.md` § 3, `copilot-instructions.md` § 2, `governance-audit-patterns/SKILL.md` **Smell 2.31** |
| F1 (Gerador/schema) | ✅ Concluído (escopo revisado) | Nova ferramenta `tools/agent_source_docs_sync/sync_lazy_source_docs.py` (allowlist fixa: CLAUDE.md, copilot-instructions.md, workflows.md — ver §0.4 sobre tentativa de limiar dinâmico revertida) |
| F2 (Skills/prompts) | ✅ Concluído | 188 artefatos migrados (95 `.agent.md`, 71 `SKILL.md`, 22 `*.prompt.md`), drift=0 |
| F5 (Teste determinístico) | ✅ Concluído | `tests/governance_audit/test_r066_progressive_disclosure_budget.py` — 6 testes |
| F6 (Templates canônicos) | ✅ Concluído | 6 templates (4 agent + skill + prompt) migrados para o contrato de 2 camadas |
| F7 (Sub-catálogos stack) | ✅ Concluído (N/A confirmado) | 8 `*-catalog.yaml` verificados — nenhum replica o padrão de full-load; nenhuma migração necessária |
| F3 (Fatiamento workflows.md) | ✅ Concluído | 10 arquivos criados em `.github/agents/workflows/`; `workflows.md` reduzido a índice (199 linhas); 11 testes de CI + 5 referências de produção atualizados |

**Validação de regressão final**: suíte completa `tests/governance_audit` + `tests/operational_flow` + `tests/routing_unit` + `tests/evals` + `tests/routing_gate`: **508/509 passando**, 1 falha pré-existente e não-relacionada (`test_no_local_projects_referenced_in_git_tracked_files`, vazamento de nomes de projeto em `apps/web`/`deploy/` — fora do escopo deste plano).

## 0.5 F3 — Detalhamento da Execução (Fatiamento de workflows.md)

### Arquivos criados em `.github/agents/workflows/`
`_índice embutido em workflows.md` + `workflow-bug-fix.md` (160 linhas), `workflow-refactoring.md` (110), `workflow-technical-analysis.md` (76), `workflow-feature-development.md` (105), `workflow-governance-maintenance.md` (92), `workflow-dependency-vulnerability-remediation.md` (70), `workflow-framework-migration.md` (204), `workflow-release-readiness.md` (55), `workflow-prompt-synthesis.md` (83), `invariantes-e-protocolos.md` (364, cobrindo §4-§10: Handoff Protocol, Invariantes, Visibilidade, Chaining, Circuit Breaker, Multi-Projeto, R-064 Gates).

### Estratégia de segurança adotada
`workflows.md` manteve as primeiras 153 linhas intactas (§1 Visão Geral incl. §1.5 Quality Review Loop/R-065, §2 Matriz de Roteamento, intro §3) — satisfazendo `test_agnostic_governance_files.py` (exige tabela de papéis genéricos §1.3 nas primeiras 45 linhas) e `test_r065_severity_guard.py` (R-065 em §1.5) sem qualquer alteração. O restante (§3.1-3.9 + §4-§10) foi extraído byte-a-byte via script Python determinístico (sem alteração de texto, apenas reorganização física).

### 11 testes de CI corrigidos (blast radius real, confirmado maior que a estimativa original de 3)
`test_anti_manual_user_delegation_governance.py`, `test_architectural_blueprint_gate_governance.py`, `test_catalog_agents_referenced_in_canonical_workflows.py` (2 funções), `test_local_project_isolation.py` (1 de 2 funções afetadas), `test_migration_engine_governance.py`, `test_prompt_synthesis_output_format_governance.py` (4 funções, reescrita completa com path dedicado `WORKFLOW_PROMPT_SYNTHESIS_FILE`), `test_systemic_reuse_gate.py`, `test_operational_workflows.py` (13 funções, correção mecânica via substituição global). Novo helper compartilhado `tests/governance_audit/_helpers.py::read_workflows_full_content(repo_root)` reconstrói o conteúdo equivalente ao monólito original (índice + todos os arquivos de `workflows/`) para assertions de substring que não dependem de localização física específica.

### 5 referências de produção atualizadas
`codegraph-engine.agent.md` (linha 45, citação textual → `workflows/workflow-framework-migration.md`), `README.md` (linhas 13 e 115, contagem corrigida de 8→9 workflows + link para `workflows/`), `routing-graph.yaml` (linha 554, citação §3.7.1 → caminho do arquivo fatiado), `runtime-verifier.agent.md` (linha 39, citação §3.1/§5 → caminhos fatiados). `agent-router.agent.md` já estava correto (workflows.md em `source_docs_lazy:` desde F1/F2).

## 0.3 Achados de T0 que Corrigem Premissas do Plano Aprovado

Uma iteração intermediária tentou classificar como lazy **qualquer** documento referenciado com >300 linhas (não apenas a allowlist fixa). Isso causou regressão real: moveu `handoff-governance/SKILL.md`, `agent-contracts/SKILL.md` e `terminal-governance/SKILL.md` (>300 linhas) para `source_docs_lazy:`, quebrando 6 testes existentes que exigem essas skills especificamente em `source_docs:` (full) por força de outras regras (R-042, R-049). Revertido cirurgicamente para a allowlist fixa de 3 documentos. **Generalizar o teto de linhas para o universo completo de documentos referenciados é um ciclo de governança separado**, que precisaria primeiro reconciliar com R-042/R-049 antes de qualquer migração.

## 0.3 Achados de T0 que Corrigem Premissas do Plano Aprovado

### INV-01 — RESOLVIDO (resultado diferente do hipotetizado)
`tools/agent_protocol_sync/` **não gera `prerequisite_docs`/`source_docs` em `catalog.yaml`** (esse módulo só sincroniza o bloco `<execution_protocol>`). Busca exaustiva (`grep -r "catalog.yaml" tools/**/*.py`) confirma que **nenhum script no repositório gera ou protege `catalog.yaml`** — é um arquivo **manualmente mantido**, sem gate `--check`/`--apply`. Isso **invalida a premissa central de F1** ("nunca editar `catalog.yaml` manualmente, sempre via `--apply`") — não existe tal mecanismo para este arquivo. `tools/agent_source_docs_sync/sync_required_source_docs.py` protege **apenas** o frontmatter de `.agent.md` individuais (e só a presença de 2 docs específicos quando `run_subagent` está em `tools:` — não a lista completa nem `CLAUDE.md`/`copilot-instructions.md`).

**Impacto**: F1 pode editar `catalog.yaml` diretamente (sem risco de reversão por CI), mas a resolução de `prerequisite_docs` vs `source_docs` deixa de ser "migrar lógica de gerador" e passa a ser edição direta coordenada. O componente que *é* protegido (`sync_required_source_docs.py` + `required_source_docs_rules.json`) precisa mesmo assim ser estendido para suportar a classificação full/lazy nos 35 `.agent.md`.

### INV-02 — RESOLVIDO
`.github/agents/runtime-verifier.agent.md` **referencia `workflows.md` literalmente** na linha 38 (citação textual, não `source_docs:`). Confirmado via grep direto.

### INV-03 — RESOLVIDO (blast radius ~4x maior que o estimado)
Grep exaustivo por `workflows\.md` no repositório encontrou **31 arquivos**, não os 8 inicialmente mapeados. Dos quais **11 são testes em `tests/governance_audit/`** que fazem `Path(...).read_text()` + `assert <string> in content` com **acoplamento estrutural fino** (números de seção `§3.9`, `§3.7`, `§1.5`, `§3.1`; limites de linha absolutos como `line_num <= 45` em `test_agnostic_governance_files.py`; extração de substring por índice de seção em `test_prompt_synthesis_output_format_governance.py`):

`test_agnostic_governance_files.py`, `test_anti_manual_user_delegation_governance.py`, `test_architectural_blueprint_gate_governance.py`, `test_governance_smells.py`, `test_local_project_isolation.py`, `test_migration_engine_governance.py`, `test_prompt_synthesis_output_format_governance.py`, `test_r065_severity_guard.py`, `test_catalog_agents_referenced_in_canonical_workflows.py`, `test_systemic_reuse_gate.py`, `test_operational_workflows.py` (em `tests/operational_flow/`).

**Impacto crítico em F3**: fatiar `workflows.md` em 11 arquivos **quebraria simultaneamente os 11 testes acima**, pois várias asserções dependem de **números de linha absolutos** ou de que todas as seções estejam no **mesmo arquivo contíguo** (ex.: `test_agnostic_governance_files.py:87` usa `line_num <= 45` relativo ao arquivo monolítico inteiro). Reescrever essas 11 asserções para apontar a arquivos fatiados é um esforço de implementação **não-trivial e de alto risco de regressão silenciosa** — maior que o resto do plano combinado (F1+F2+F4+F6+F7).

**Recomendação**: **F3 deve ser destacado deste plano e tratado como um sub-plano dedicado** (`docs/plans/<nova-data>-governance-maintenance-workflows-md-slicing.md`), com seu próprio Duplo Gate Documental (R-064), escopo e matriz de risco centrados exclusivamente nos 11 testes de CI. F1, F2, F4, F6, F7 **não dependem de F3** e podem prosseguir de forma independente e seguro.

---

## 0.1 Ressalva Crítica de Enforcement — Natureza Textual/CI-Estática, NÃO Mecânico-Runtime

> **Achado de pesquisa de mercado (Tavily, confirmado em 3 fontes autoritativas antes da aprovação deste plano)**: os campos `source_docs:` e `source_docs_lazy:` **NÃO são reconhecidos nativamente** por nenhuma especificação oficial de plataforma:
> - **GitHub Copilot `.agent.md`** (docs.github.com, Visual Studio/VS Code Learn, `awesome-copilot/AGENTS.md`): campos oficiais são `name`, `description`, `tools`, `model`, `disable-model-invocation`, `user-invocable`, `mcp-servers`, `argument-hint`.
> - **Anthropic Agent Skills `SKILL.md`** (`agentskills.io/specification`): campos oficiais são `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
> - **GitHub Copilot `.instructions.md`**: `description`, `applyTo`.
>
> `source_docs`/`source_docs_lazy` são **campos 100% proprietários desta governança**, sem suporte nativo de plataforma. Não existe mecanismo de "pre-fetch automático" disparado pela plataforma — a cláusula "Pre-fetch automático pelo agent" (`copilot-instructions.md` § 2) **depende inteiramente de o próprio modelo ler essa instrução textual e decidir voluntariamente chamar `read_file`/`ctx_search`** nos arquivos listados.

### Implicações diretas para este plano

1. **A solução (contrato de 2 camadas `source_docs`/`source_docs_lazy`) permanece tecnicamente válida** — não há "quebra de spec" a temer, pois não existe spec oficial a violar. O sistema inteiro já era uma convenção auto-imposta antes desta mudança; a mudança apenas refina essa convenção.
2. **Nenhuma camada desta solução impede mecanicamente que um agente ignore `source_docs_lazy` e chame `read_file` integral de qualquer forma.** O enforcement real possível é exclusivamente:
   - **Estático/CI-time**: `tests/governance_audit/test_r066_progressive_disclosure_budget.py` (F5) valida que o *frontmatter declarado* está correto (documento certo na camada certa), não que o *comportamento em runtime* respeitou a declaração.
   - **Textual/instrucional**: a regra R-066 (F4) e o Smell 2.27 em `governance-audit-patterns/SKILL.md` normatizam a expectativa de comportamento, mas sua observância depende de disciplina do modelo em cada sessão — o mesmo gap já documentado no plano irmão `docs/plans/20260929-governance-maintenance-harness-bloat-audit.md` (Achado #4: "Enforcement mecânico do hook não verificável... dependente de disciplina do modelo, não de bloqueio determinístico").
3. **R-066 (c) deve deixar essa limitação explícita** no próprio texto normativo (ver §5.1 abaixo, já ajustado) para não criar falsa sensação de bloqueio mecânico onde só existe convenção auditável.
4. **Critério de sucesso realista**: esta mudança reduz o **custo esperado médio** de context bloat (porque a maioria dos agentes/sessões seguirá a convenção textual quando bem redigida e reforçada por exemplo nos templates — R-029/R-061), e torna o desvio **auditável e detectável post-hoc** via F5 — mas não oferece garantia **hard** de zero full-load em toda sessão. Qualquer expectativa de bloqueio 100% determinístico em runtime exigiria um mecanismo de hook/permission handler real (fora de escopo deste plano — ver plano irmão, Frente C, ADR de viabilidade de enforcement mecânico).

---

## 0.2 Investigações Pendentes de Confirmação em T1 (não bloqueiam a aprovação do plano, bloqueiam o início de T1)

| # | Item | Motivo | Ação em T1 |
|---|---|---|---|
| INV-01 | Confirmar qual ferramenta gera o campo `prerequisite_docs:` em `.github/agents/catalog.yaml` (suspeita: `tools/agent_protocol_sync`, não lido nesta etapa) | A pesquisa desta etapa confirmou que `source_docs:` (frontmatter de cada `.agent.md`) e `prerequisite_docs:` (agregado em `catalog.yaml`) têm payload idêntico, mas são escritos por mecanismos distintos | Ler o script gerador de `catalog.yaml` antes de tocar no schema (T1.0) |
| INV-02 | Confirmar se `.github/agents/runtime-verifier.agent.md` referencia `workflows.md` por string literal ou apenas por citação de seção sem o literal `.md` | Grep atual não encontrou o literal `workflows.md` no conteúdo corrente do arquivo, embora histórico de commit indique relação | Novo grep dedicado no início de T3, antes de qualquer edição |
| INV-03 | Levantar **todos** os testes que fazem parsing direto do conteúdo de `workflows.md` (não apenas os 3 agents citados) | Encontrados nesta pesquisa: `tests/operational_flow/test_operational_workflows.py`, `tests/governance_audit/test_catalog_agents_referenced_in_canonical_workflows.py`, `tests/governance_audit/test_systemic_reuse_gate.py` — todos leem `WORKFLOWS_PATH`/`WORKFLOWS_MD_PATH` e fazem `assert "<string>" in content` | Mapear 100% das ocorrências via grep consolidado em T3.1 antes de fatiar o arquivo |

> Ver também **§0.1** (Ressalva Crítica de Enforcement) — nenhuma das frentes abaixo introduz bloqueio mecânico de runtime; o enforcement é estático (CI/F5) e textual (R-066/F4).

---

## 1. Ordem de Execução das 7 Frentes e Grafo de Dependências

```
F1 (schema/gerador) ──► F2 (skills/prompts) ──► F5 (teste determinístico)
     │                                               ▲
     ├──► F7 (sub-catálogos stack-specific)──────────┘
     │
     └──► F6 (templates canônicos, nascem já conformes)

F3 (fatiamento workflows.md) ─── independente de F1/F2, mas DEVE anteceder F5
                                   (o teste F5 também valida drift=0 pós-fatiamento)

F4 (regra normativa R-066 + smell 2.27) ─── precede F1 textualmente
                                              (a regra deve existir ANTES do schema
                                              que a implementa, para rastreabilidade
                                              de commit único coerente),
                                              mas pode ser escrita em paralelo a F1
                                              (sem dependência de código)
```

| Ordem | Frente | Justificativa de precedência | Pode paralelizar com |
|---|---|---|---|
| 1º | **F4** — Regra R-066 (texto normativo) | Define o contrato semântico (`source_docs` vs `source_docs_lazy`) que F1 implementa mecanicamente. Redigir a regra antes do código evita retrabalho de nomenclatura. | F3 |
| 2º | **F1** — Gerador e schema | F2/F5/F7 dependem do novo schema existir e ser estável (`--check` verde) antes de qualquer migração em lote. | — |
| 3º | **F3** — Fatiamento de `workflows.md` | Independente de F1 em termos de schema, mas deve concluir antes de F5 (o teste determinístico também varre `workflows/`). | F4 (texto), F1 (código) |
| 4º | **F2** — Skills e prompts (94 artefatos) | Só migra em lote depois que F1 estabiliza o contrato de 2 camadas (evita migrar 2x). | F7 |
| 5º | **F7** — Sub-catálogos stack-specific | Mesma razão de F2; roda em paralelo a F2 pois são arquivos disjuntos. | F2 |
| 6º | **F6** — Templates canônicos | Templates só fazem sentido já no formato final; aplicados por último para não haver drift entre template e schema real. | — |
| 7º | **F5** — Teste determinístico `test_r066_progressive_disclosure_budget.py` | Só pode afirmar "drift=0" depois que F1, F2, F3 e F7 estiverem aplicados e regenerados. É o gate final de todo o plano. | — |

**Regra de ouro de sequenciamento**: nenhuma PR de F2/F3/F7 é aberta antes do merge de F1 (schema). F5 é sempre o último merge.

---

## 2. F1 — Gerador e Schema

### 2.1 Estado atual (confirmado por leitura via `context-mode`)

- `tools/agent_source_docs_sync/sync_required_source_docs.py`:
  - `RULES_PATH` → `tools/agent_source_docs_sync/required_source_docs_rules.json` (hoje **1 única regra**: `run_subagent_requires_handoff_and_contracts`, condição `tools_contains: run_subagent`, exige `.github/skills/handoff-governance/SKILL.md` + `.github/skills/agent-contracts/SKILL.md` em `source_docs:`).
  - Funções-chave: `load_rules()`, `evaluate_condition(condition, frontmatter_data)` (hoje só suporta predicado `tools_contains`), `get_agent_files()`, `split_frontmatter_and_body()`, `insert_source_docs(fm_text, missing_docs)` (inserção cirúrgica textual, preserva ordem/indentação), `sync_agent_source_docs(mode="check"|"apply")` (função programática usada também por `tests/governance_audit/test_root_agent_impersonation_governance.py` e pelo próprio CLI via `cmd_check`/`cmd_apply`).
  - CLI emite `"Drift detectado: N"` e, em `--apply`, `"Artefatos atualizados em disco"`.
  - Testado por `tests/governance_audit/test_sync_required_source_docs_invariants.py` (2 testes: `--check` retorna drift=0; `--apply` é idempotente).
- `.github/agents/catalog.yaml`: usa a chave **`prerequisite_docs:`** (não `source_docs:`) por agent, com payload hoje idêntico ao que seria esperado de `source_docs:` do `.agent.md` correspondente (ex.: `agent-router` → `prerequisite_docs: [CLAUDE.md, .github/copilot-instructions.md, .github/agents/README.md, .github/agents/catalog.yaml]`).
  - **INV-01** (ver §0): confirmar o gerador de `catalog.yaml` antes de tocar nele. Hipótese de trabalho: `tools/agent_protocol_sync` agrega `source_docs:` do `.agent.md` e projeta sob o nome `prerequisite_docs:` no catálogo — renomeação sem motivo semântico, violando R-003 (anti-duplicação).

### 2.2 Decisão de schema (Opção B da planning doc, detalhada)

Adotar **diferenciação semântica por 2 campos no frontmatter do `.agent.md`** (fonte de verdade):

```yaml
# Novo contrato de 2 camadas (frontmatter de .agent.md, SKILL.md, .prompt.md)
source_docs:
  - .github/skills/handoff-governance/SKILL.md      # full-load seguro (<500 linhas)
  - .github/skills/agent-contracts/SKILL.md
source_docs_lazy:
  - CLAUDE.md                                        # lazy: NUNCA read_file integral,
  - .github/copilot-instructions.md                  # consumo exclusivo via ctx_search
  - .github/agents/workflows/workflow-bug-fix.md     # qualquer doc fatiado >300 linhas
```

**Resolução da duplicação `prerequisite_docs` vs `source_docs`** — decisão adotada: **deprecação com migração, não merge silencioso**.

| Opção avaliada | Decisão |
|---|---|
| Manter `prerequisite_docs:` em `catalog.yaml` como está, ignorando a duplicação | ❌ Rejeitada — perpetua R-003 |
| Fazer `catalog.yaml` projetar **os mesmos 2 campos** (`source_docs` + `source_docs_lazy`) a partir do novo frontmatter, **renomeando** `prerequisite_docs` → `source_docs` (e adicionando `source_docs_lazy`) na próxima regeneração via `--apply` | ✅ **Adotada** — única chave por conceito, nome espelhado 1:1 entre `.agent.md` e `catalog.yaml`, elimina duplicação nominal mantendo o dado |

### 2.3 Diff técnico proposto (nível de função, não código final)

| Arquivo | Mudança |
|---|---|
| `tools/agent_source_docs_sync/required_source_docs_rules.json` | Adicionar campo opcional `lazy: true/false` por entrada em `required_source_docs` (array de objetos `{path, lazy}` em vez de array de strings puro — **breaking change de schema interno**, requer migração da única regra existente) OU manter array de strings e introduzir **classificação automática por tamanho de arquivo** (heurística: `lazy=True` se `len(linhas) > 300` **ou** path ∈ allowlist fixa `["CLAUDE.md", ".github/copilot-instructions.md"]`). **Recomendação**: heurística automática (menor superfície de mudança de schema, zero necessidade de editar JSON manualmente por item). |
| `tools/agent_source_docs_sync/sync_required_source_docs.py` | (a) Nova função `classify_doc_tier(doc_path: str) -> Literal["full", "lazy"]` — aplica a heurística de 300 linhas + allowlist; (b) `insert_source_docs()` passa a receber `missing_full` e `missing_lazy` separadamente e escrever as 2 chaves de frontmatter (`source_docs:`, `source_docs_lazy:`), preservando ordem alfabética dentro de cada bloco; (c) `evaluate_condition()` inalterado (predicados continuam agnósticos à camada); (d) CLI (`cmd_check`/`cmd_apply`) passa a reportar drift separadamente por camada: `"Drift detectado (full): N | Drift detectado (lazy): M"`. |
| `tools/agent_protocol_sync/*` (a confirmar em INV-01) | Gerador de `catalog.yaml` passa a ler `source_docs:` + `source_docs_lazy:` do `.agent.md` e projetar **ambas as chaves com os mesmos nomes** em `catalog.yaml`, removendo `prerequisite_docs:`. |
| `tests/governance_audit/test_sync_required_source_docs_invariants.py` | Adicionar 2 novos testes: (1) `test_sync_classifies_claude_md_as_lazy()` — garante que `CLAUDE.md`/`copilot-instructions.md` sempre caem em `source_docs_lazy`; (2) `test_sync_full_load_docs_under_500_lines()` — garante que nenhum doc em `source_docs:` (full) excede 500 linhas no repositório atual (guarda contra regressão futura de um doc "full" crescer demais). |

### 2.4 Rollback de F1

- Branch dedicada `chore/r066-f1-schema-source-docs-lazy`.
- Tag `pre-r066-f1` no commit anterior ao primeiro `--apply`.
- Rollback = `git revert` do commit único de `--apply` (operação é 100% determinística e idempotente — `sync_required_source_docs.py --apply` duas vezes seguidas não produz diffs adicionais, validado pelo teste de idempotência existente).

---

## 3. F2 — Skills e Prompts (Migração em Lote)

### 3.1 Escopo confirmado

- **72 `SKILL.md`** + **22 `*.prompt.md`** declarando `CLAUDE.md` e/ou `.github/copilot-instructions.md` em `source_docs:` — incluindo a autorreferência de `.github/skills/agent-contracts/SKILL.md` (achado #1 da planning doc).
- Estratégia: **script determinístico**, não edição manual (conforme `.github/skills/efficient-batch-code-modification/SKILL.md` e proibição explícita de editar artefatos fora do gerador).

### 3.2 Abordagem técnica

1. Estender `sync_required_source_docs.py` (ou criar módulo irmão `sync_lazy_source_docs_skills_prompts.py` reaproveitando `split_frontmatter_and_body`/`insert_source_docs` via import, evitando duplicação de lógica) para também varrer `.github/skills/**/SKILL.md` e `.github/prompts/**/*.prompt.md`.
2. Regra declarativa nova em `required_source_docs_rules.json` (ou arquivo irmão `required_source_docs_lazy_migration_rules.json`): para qualquer artefato que já possua `CLAUDE.md` ou `.github/copilot-instructions.md` dentro de `source_docs:`, mover essas 2 entradas para `source_docs_lazy:` (migração estrutural, não adição).
3. Rodar `--apply` em lote único (todos os 94 artefatos no mesmo commit, script único no sandbox — Single-Turn MCP Batching, R-046/R-056).
4. Validar com `--check` (drift=0) antes de abrir PR.

### 3.3 Rollback de F2

- Branch `chore/r066-f2-skills-prompts-lazy-migration`, dependente de F1 já mergeada.
- Tag `pre-r066-f2`.
- Rollback = revert único (mudança é puramente estrutural de frontmatter, sem lógica de negócio).

---

## 4. F3 — Fatiamento de `.github/agents/workflows.md`

### 4.1 Estado atual confirmado

- `workflows.md`: **174.302 caracteres / 1.473 linhas** — monolítico.
- Estrutura real (H2/H3 extraídos): 9 Workflows Canônicos (`WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-TECHNICAL-ANALYSIS`, `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`, `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-RELEASE-READINESS`, `WORKFLOW-PROMPT-SYNTHESIS` — confirmados 9, não 8 como o README ainda lista) + seções transversais (§1 Visão Geral, §2 Matriz de Roteamento, §4 Protocolo de Handoff `workflow_tracking`, §5 Invariantes 1-19, Portão de Reúso Sistêmico R-055).

### 4.2 Lista final dos arquivos-alvo em `.github/agents/workflows/`

| # | Arquivo novo | Conteúdo migrado (seção original) |
|---|---|---|
| 1 | `workflows/_indice.md` | Substitui o corpo de `workflows.md`: Visão Geral (§1), Matriz de Roteamento (§2), referências cruzadas para os 9 arquivos abaixo. **Único arquivo full-load seguro** (<300 linhas). |
| 2 | `workflows/workflow-bug-fix.md` | §3.1 |
| 3 | `workflows/workflow-refactoring.md` | §3.2 |
| 4 | `workflows/workflow-technical-analysis.md` | §3.3 |
| 5 | `workflows/workflow-feature-development.md` | §3.4 |
| 6 | `workflows/workflow-governance-maintenance.md` | §3.5 (inclui Portão de Reúso Sistêmico R-055, Q1/Q2/Q3) |
| 7 | `workflows/workflow-dependency-vulnerability-remediation.md` | §3.6 |
| 8 | `workflows/workflow-framework-migration.md` | §3.7 (inclui Invariante 9 citada por `codegraph-engine.agent.md`) |
| 9 | `workflows/workflow-release-readiness.md` | §3.8 |
| 10 | `workflows/workflow-prompt-synthesis.md` | §3.9 |
| 11 | `workflows/_invariantes-e-handoff.md` | §4 (`workflow_tracking`) + §5 (Invariantes 1-19) — consumido transversalmente por todos os workflows |

`workflows.md` (raiz) **permanece existindo** como arquivo fino de redirecionamento (1 parágrafo + tabela de links), preservando compatibilidade de path para qualquer referência externa não migrada neste ciclo.

### 4.3 Referências diretas a atualizar (confirmado: **5 arquivos de produção + 3 arquivos de teste**, não apenas 3)

| # | Arquivo | Linha(s) | Natureza da referência |
|---|---|---|---|
| 1 | `.github/agents/agent-router.agent.md` | 14, 281 | `source_docs:` (linha 14) + citação textual "conforme workflows.md" (linha 281) |
| 2 | `.github/agents/codegraph-engine.agent.md` | 44 | Citação textual `workflows.md § 3.7, Invariante 9` → migrar para `workflows/workflow-framework-migration.md § Invariante 9` |
| 3 | `.github/agents/README.md` | 13, 115 | Lista de workflows (linha 13, **corrigir para 9 workflows**, hoje cita 8) + link `[workflows.md](workflows.md)` (linha 115) → apontar para `workflows/_indice.md` |
| 4 | `.github/agents/routing-graph.yaml` | 189 | Referência textual em comentário/metadado |
| 5 | **`.github/agents/runtime-verifier.agent.md`** | A confirmar em INV-02 (T3.0) | Histórico de commit indica referência; grep atual no conteúdo corrente não encontrou o literal — **investigar antes de editar** |
| 6 | `tests/operational_flow/test_operational_workflows.py` | 218, 229, 233s., 271, 274s. | `WORKFLOWS_MD_PATH = AGENTS_DIR / "workflows.md"` + múltiplos `assert "<string>" in content` — **DEVE** ser reescrito para ler e concatenar todos os arquivos de `workflows/*.md` (ou apontar `WORKFLOWS_MD_PATH` para `workflows/_indice.md` + agregação) |
| 7 | `tests/governance_audit/test_catalog_agents_referenced_in_canonical_workflows.py` | ~32-56 | `WORKFLOWS_PATH` lido como fonte única de verdade para "agent mencionado em algum workflow" — **DEVE** agregar conteúdo de todos os arquivos fatiados |
| 8 | `tests/governance_audit/test_systemic_reuse_gate.py` | 55-59 | Asserts sobre presença de "Portão de Reúso e Generalização Sistêmica", "R-055" e "Q1/Q2/Q3" em `workflows.md` — **DEVE** apontar para `workflows/workflow-governance-maintenance.md` |

> **Achado adicional desta etapa de implementação** (vs. a lista original de 3 do escopo): os 3 testes acima (#6-#8) são consumidores estruturais de `workflows.md` tão críticos quanto os agents #1-#2. Ignorá-los quebraria o CI imediatamente após o fatiamento. Incluídos compulsoriamente no escopo de F3.

### 4.4 Rollback de F3

- Branch `chore/r066-f3-workflows-slicing`.
- Tag `pre-r066-f3` **antes** de mover qualquer conteúdo (maior blast radius do plano — arquivo consumido por 8 artefatos, incluindo 3 testes de CI).
- Estratégia de rollback em 2 fases: (1) se falha for detectada **antes** do merge, `git checkout` da branch; (2) se falha for detectada **depois** do merge (CI vermelho em produção), revert único do commit de fatiamento restaura `workflows.md` monolítico e os 8 arquivos dependentes ao estado anterior simultaneamente (commit atômico único, não fatiado em múltiplos PRs, para garantir reversibilidade 1:1).

---

## 5. F4 — Regra Normativa R-066

### 5.1 Texto proposto para `CLAUDE.md` (estilo espelhado em R-061)

```markdown
- **R-066 (Progressive Disclosure Compulsória de `source_docs:` — Anti Context Bloat Inicial / Full-Load vs. Lazy-Load)**: Todo artefato de governança (`.agent.md`, `SKILL.md`, `*.prompt.md`) que declara documentação de referência DEVE diferenciar 2 camadas no frontmatter:
  **(a) `source_docs:` (full-load seguro)**: documentos com **menos de 500 linhas**, cujo carregamento integral via `read_file` no boot do agente é aceitável e não satura a janela de contexto inicial.
  **(b) `source_docs_lazy:` (full-load proibido)**: documentos estruturalmente grandes ou centrais de alto fan-in (`CLAUDE.md`, `.github/copilot-instructions.md`, qualquer doc fatiado > 300 linhas, incluindo os arquivos de `.github/agents/workflows/`) — consumo exclusivo via `context-mode/ctx_search` com queries pontuais; `read_file` integral destes documentos é terminantemente proibido fora do bootstrap mínimo necessário.
  **(c) Fonte de Verdade Única e Determinística + Natureza do Enforcement (Textual/CI-Estático, NÃO Mecânico-Runtime)**: a classificação full vs. lazy NUNCA é decidida manualmente por agente — é derivada automaticamente por `tools/agent_source_docs_sync/sync_required_source_docs.py` (heurística de linha-count + allowlist fixa) e aplicada exclusivamente via `--apply`. Edição manual de `source_docs:`/`source_docs_lazy:` em qualquer `catalog.yaml`, `.agent.md`, `SKILL.md` ou `*.prompt.md` é terminantemente proibida (reincidência de R-008/R-056). **Ressalva explícita**: `source_docs`/`source_docs_lazy` são campos proprietários desta governança, sem reconhecimento nativo por nenhuma plataforma (GitHub Copilot, Anthropic Agent Skills); não há bloqueio mecânico de runtime que impeça um agente de ler integralmente um documento classificado como lazy — o enforcement real é **estático** (auditoria CI via `test_r066_progressive_disclosure_budget.py`, que valida a declaração no frontmatter) e **textual/instrucional** (disciplina do modelo em seguir esta regra), análogo ao gap de enforcement já documentado para R-053/R-062/R-063 no plano irmão de Harness Bloat Audit.
  **(d) Remissão Normativa**: Detalhamento em `.github/skills/governance-audit-patterns/SKILL.md` § 2 (Smell 2.27) e validação determinística em `tests/governance_audit/test_r066_progressive_disclosure_budget.py`.
```

### 5.2 Espelhamento em `.github/copilot-instructions.md`

Replicar o texto acima **ipsis litteris** na seção correspondente de regras R-0xx de `copilot-instructions.md`, mantendo paridade 1:1 (padrão observado em R-059/R-060/R-061, que já são espelhadas nos dois arquivos).

### 5.3 Nova categoria de smell em `governance-audit-patterns/SKILL.md` § 2

Próximo número disponível confirmado: **Smell 2.27** (o maior smell catalogado hoje é 2.26 — MCP Tool Chaining Sequencial).

```markdown
### 2.27 — Progressive Disclosure Violation (Full-Load Forçado de Documento Lazy) (R-066)

| Campo | Conteúdo |
|---|---|
| Sintoma | Artefato (`.agent.md`/`SKILL.md`/`*.prompt.md`) declara `CLAUDE.md`, `.github/copilot-instructions.md` ou qualquer doc > 300 linhas dentro de `source_docs:` (camada full-load) em vez de `source_docs_lazy:`; ou agente executa `read_file` integral de documento classificado como lazy |
| Como detectar | (a) `tests/governance_audit/test_r066_progressive_disclosure_budget.py` (drift determinístico do frontmatter **declarado** — camada estática/CI); (b) grep de `read_file.*CLAUDE.md\|copilot-instructions.md` em logs de execução de agente (camada observacional, não bloqueante — sem mecanismo de hook/runtime real) |
| Origem (TrustAgent) | Intrínseco — saturação cega da janela de contexto inicial por hábito de full-load indiscriminado |
| Severidade | **Alto** (não bloqueador imediato de CI, mas gera custo recorrente de tokens em 100% das sessões do agente afetado) |
| Enforcement | **Textual/CI-estático apenas** — `source_docs`/`source_docs_lazy` não são campos reconhecidos nativamente por GitHub Copilot ou Anthropic Agent Skills; não há bloqueio mecânico de runtime (mesma limitação de R-053/R-062/R-063) |
| Remediação | Rodar `tools/agent_source_docs_sync/sync_required_source_docs.py --apply`; nunca editar a chave manualmente (violação adicional de R-008/R-056) |
```

### 5.4 Rollback de F4

- Mudança puramente textual em 3 arquivos (`CLAUDE.md`, `copilot-instructions.md`, `governance-audit-patterns/SKILL.md`), sem geração de código — revert trivial de commit único.

---

## 6. F5 — Teste Determinístico `tests/governance_audit/test_r066_progressive_disclosure_budget.py`

### 6.1 Assertions obrigatórias (especificação, não código final)

| # | Teste | Assertion |
|---|---|---|
| 1 | `test_source_docs_lazy_present_when_claude_md_referenced()` | Para todo `.agent.md`/`SKILL.md`/`*.prompt.md` que referencia `CLAUDE.md` ou `copilot-instructions.md`, essa referência DEVE estar em `source_docs_lazy:`, nunca em `source_docs:` (drift = 0, lista de violações no assert) |
| 2 | `test_full_load_docs_under_line_budget()` | Todo path listado em `source_docs:` (full) de qualquer artefato DEVE corresponder a um arquivo real com `< 500` linhas no repositório atual |
| 3 | `test_workflows_md_sliced_and_indexed()` | `.github/agents/workflows/_indice.md` existe e possui `< 300` linhas; os 9 arquivos de workflow existem; `workflows.md` (raiz) é um arquivo fino de redirecionamento (`< 50` linhas) |
| 4 | `test_sync_required_source_docs_two_tier_check_returns_zero()` | `sync_required_source_docs.py --check` (pós F1/F2/F7) retorna exit code 0 e reporta `"Drift detectado (full): 0"` + `"Drift detectado (lazy): 0"` |
| 5 | `test_catalog_yaml_mirrors_source_docs_naming()` | `catalog.yaml` não contém mais a chave `prerequisite_docs:` — só `source_docs:`/`source_docs_lazy:`, com paridade de conteúdo 1:1 contra o `.agent.md` de origem |
| 6 | `test_stack_catalogs_comply_with_two_tier_schema()` | Idem #5, aplicado a cada `*-catalog.yaml` de domínio confirmado em F7 |

### 6.2 Rollback de F5

- Teste novo e isolado — rollback = remover o arquivo (sem impacto em outros testes, desde que F1-F4/F7 ainda não tenham sido revertidos).

---

## 7. F6 — Templates Canônicos

| Arquivo | Ajuste proposto |
|---|---|
| `.github/agents/templates/agent-template.md` | Frontmatter de exemplo já nasce com `source_docs:` + `source_docs_lazy:` (comentário explicativo inline sobre a regra R-066) |
| `.github/agents/templates/operational-agent.md` | Idem |
| `.github/agents/templates/research-agent.md` | Idem |
| `.github/agents/templates/router-agent.md` | Idem (mantendo baseline de 7 tools R-054 intacto — mudança restrita ao bloco `source_docs`) |
| `.github/skills/templates/skill-template.md` | Idem, com nota de que `CLAUDE.md`/`copilot-instructions.md` vão sempre em `source_docs_lazy:` |
| `.github/prompts/templates/prompt-template.md` | Idem |

### 7.1 Rollback de F6

- Mudança textual em 6 arquivos de template — revert trivial.

---

## 8. F7 — Sub-catálogos Stack-Specific

### 8.1 Confirmação de existência (via leitura direta do repositório)

| Sub-catálogo | Existe? | Path confirmado |
|---|---|---|
| `spring-reactive-catalog.yaml` | ✅ Confirmado | `.github/agents/backend/spring-reactive/spring-reactive-catalog.yaml` |
| `ejb-catalog.yaml` | ✅ Confirmado | `.github/agents/backend/ejb/ejb-catalog.yaml` |
| `database-catalog.yaml` | ✅ Confirmado | `.github/agents/backend/database/database-catalog.yaml` |
| `python-catalog.yaml` | ✅ Confirmado | `.github/agents/backend/python/python-catalog.yaml` |
| `spring-boot-catalog.yaml` | A confirmar em T7.0 (grep dedicado — não localizado nos trechos lidos nesta pesquisa, mas padrão de nomenclatura é consistente com os demais) |
| `angular-catalog.yaml` | A confirmar em T7.0 |
| `struts-catalog.yaml` | A confirmar em T7.0 |

**Ação em T7.0**: antes de aplicar qualquer `--apply`, rodar `file_search`/grep consolidado para os 3 catálogos não confirmados nesta pesquisa (spring-boot, angular, struts) e confirmar se replicam o mesmo padrão de `prerequisite_docs`/`source_docs`. Se confirmados, entram no mesmo lote de F1/F2.

### 8.2 Rollback de F7

- Mesma estratégia de F1/F2: branch dedicada `chore/r066-f7-stack-catalogs`, tag `pre-r066-f7`, revert único (mudança 100% gerada por script).

---

## 9. Matriz de Riscos e Blast Radius Consolidado

| Frente | Blast Radius | Risco Principal | Mitigação |
|---|---|---|---|
| F1 | Alto (35 agents, via ferramenta determinística) | Heurística de classificação (300/500 linhas) classificar incorretamente um doc de fronteira | Teste F5 #2 fixa o teto em 500 linhas como guarda; revisão manual da lista de docs lazy antes do merge |
| F2 | Alto (94 artefatos) | Migração em massa falhar silenciosamente em 1-2 arquivos com frontmatter não-canônico (YAML malformado) | `--check` obrigatório pós-`--apply`; nenhum PR aberto com drift > 0 |
| F3 | Médio-Alto (consumido por 5 arquivos de produção + 3 testes de CI) | Quebra de CI por teste que lê `workflows.md` monolítico diretamente | INV-03 mapeado compulsoriamente em T3.0 antes de mover qualquer linha; commit atômico único |
| F4 | Médio (2 arquivos normativos + 1 skill) | Nenhum — mudança textual pura | — |
| F5 | Pequeno | Teste novo pode já falhar no primeiro `--check` se F1/F2/F3/F7 não estiverem 100% aplicados | F5 só é mergeado por último (ordem de execução §1) |
| F6 | Pequeno | Nenhum — templates não afetam artefatos existentes | — |
| F7 | A confirmar (T7.0) | Sub-catálogo não confirmado existir pode não seguir o mesmo padrão | Grep de confirmação antes de aplicar |

---

## 10. Estratégia de Rollback Global

1. Cada frente (F1-F7) é uma **branch e um commit único e atômico** (squash merge), nunca múltiplos commits parciais na mesma frente.
2. Tag `pre-r066-<frente>` criada imediatamente antes do primeiro `--apply` ou da primeira edição textual de cada frente.
3. Ordem de merge estrita conforme §1 — **nenhuma frente posterior é mergeada antes da anterior estar verde em CI**.
4. Se F5 (gate final) falhar após todas as frentes aplicadas, o rollback é feito **na ordem inversa** (F7→F6→F4→F3→F2→F1), revertendo frente a frente até o teste determinístico voltar a passar, isolando a frente problemática.
5. Nenhuma frente desta lista remove conteúdo normativo existente — todo rollback é reversível por `git revert` simples, sem necessidade de reconstrução manual de estado.

---

## 11. Checklist Unificado (Definition of Done) — 100% Concluído

- [x] T0: INV-01/INV-02/INV-03 confirmados via grep/leitura dedicada
- [x] F4: R-066 redigida em `CLAUDE.md` + espelhada em `copilot-instructions.md` + Smell **2.31** em `governance-audit-patterns/SKILL.md` (não 2.27 — já ocupado por R-058/Gap Dumping)
- [x] F1: `sync_lazy_source_docs.py` implementa classificação full/lazy (allowlist fixa de 3 documentos — CLAUDE.md, copilot-instructions.md, workflows.md; ver §0.4 sobre tentativa de limiar dinâmico revertida)
- [x] F1: gerador de `catalog.yaml` investigado (INV-01) — confirmado **inexistente** (`tools/agent_protocol_sync` cobre apenas `<execution_protocol>`, não `source_docs`/`prerequisite_docs`); resolução da duplicação `prerequisite_docs`/`source_docs` registrada como pendência formal em §13 (fora de escopo desta rodada)
- [x] F1: novo teste `test_sync_lazy_source_docs_check_returns_zero` (em `test_r066_progressive_disclosure_budget.py`) valida drift=0
- [x] F3: INV-02/INV-03 resolvidos; 10 arquivos criados em `.github/agents/workflows/`; `workflows.md` raiz reduzido a índice leve (199 linhas)
- [x] F3: 5 arquivos de produção + **11 testes de CI** (não 3) atualizados — ver §0.5 para detalhamento completo
- [x] F2: 71 `SKILL.md` + 22 `*.prompt.md` migrados via `--apply` em lote único (95 `.agent.md` migrados junto em F1)
- [x] F7: confirmação de existência de `spring-boot-catalog.yaml`/`angular-catalog.yaml`/`struts-catalog.yaml`/demais 5 — nenhum replica o padrão de full-load; nenhuma migração necessária (N/A confirmado)
- [x] F6: 6 templates canônicos (4 agent + skill + prompt) atualizados para nascer em conformidade
- [x] F5: `test_r066_progressive_disclosure_budget.py` criado com 6 testes e verde
- [x] `CHANGELOG.md` recebe entrada única consolidando as 7 frentes ([2.52.0])
- [x] Nenhuma edição manual de `catalog.yaml` ou `*-catalog.yaml` ocorreu em nenhuma fase — confirmado (nenhuma frente desta rodada tocou esses arquivos; resolução de `prerequisite_docs` é pendência formal de ciclo futuro)

---

## 12. Critério de Aceite Final — 100% Atendido

Todos os itens da Planning Doc (§ Critério de Aceite) **mais**:

- [x] Os **11 testes de CI** identificados (não os 3 originalmente estimados) estão verdes pós-fatiamento — validado com 508/509 passando na suíte completa.
- [x] `tools/agent_protocol_sync` investigado (INV-01) — confirmado que **não gera** `catalog.yaml`/`prerequisite_docs`; achado documentado e registrado como pendência formal (§13), não ajuste desta rodada.
- [x] Contagem de workflows no `README.md` corrigida de 8 para 9.
- [x] A ressalva de enforcement textual/CI-estático (§0.1) está refletida literalmente no texto de R-066(c), no Smell 2.31 e em toda a comunicação de conclusão do ciclo — nenhuma entrega deste plano afirma ou sugere bloqueio mecânico de runtime inexistente.

---

## 13. Pendências Formais para Ciclo de Governança Futuro (fora de escopo desta rodada)

1. **Resolução da duplicação `prerequisite_docs:`/`source_docs:` em `.github/agents/catalog.yaml`**: campo confirmado manualmente mantido (INV-01), sem gerador automático. Requer ciclo de planejamento dedicado para decidir entre deprecação de um dos dois campos ou diferenciação semântica formal, incluindo atualização de qualquer consumidor do campo `prerequisite_docs` ainda não identificado.
2. **Generalização do teto de 300/500 linhas** para todo o universo de documentos referenciados em `source_docs:` (além da allowlist fixa de 3 documentos centrais — CLAUDE.md, copilot-instructions.md, workflows.md): tentativa realizada e revertida nesta rodada (§0.4) por conflitar com R-042 (`handoff-governance`/`agent-contracts` mandatoriamente em `source_docs` full) e R-049 (`terminal-governance` idem). Requer reconciliação normativa prévia entre R-066 e essas regras antes de qualquer nova tentativa.
3. **Documento de execução confirmado**: F3 (fatiamento de `workflows.md`) foi executado nesta mesma rodada após investigação de T0 revelar blast radius real (11 testes, não 3) — não foi necessário destacar para sub-plano separado, dado que o risco foi mitigado com sucesso via estratégia de preservação das primeiras 153 linhas + helper de reconstrução de conteúdo (`read_workflows_full_content`).

---

## 14. Adendo Pós-Conclusão — Gap de Discovery de `source_docs_lazy:` (Encontrado e Corrigido na Mesma Sessão)

### 14.1 Diagnóstico do Gap

Após a conclusão de F1-F7 (checklist §11 100% marcado), auditoria adicional do usuário revelou que a migração resolvia apenas **metade** do problema de Progressive Disclosure: moveu as referências para `source_docs_lazy:`, mas nunca instruiu o **próprio agente** sobre o que fazer com essa chave. Mapeamento exaustivo de onde a semântica de `source_docs_lazy` existia em texto (não apenas como chave YAML):

| Local | Explica a semântica no corpo? | Alcance real |
|---|---|---|
| `CLAUDE.md` § R-066 | ✅ Texto completo | ❌ O próprio `CLAUDE.md` está em `source_docs_lazy` — não carregado por padrão (bootstrapping circular) |
| `.github/copilot-instructions.md` | ✅ 1 bullet resumido | ⚠️ Só chega ao modelo por injeção nativa específica do IDE GitHub Copilot — não garantido em outras plataformas/MCP clients |
| `governance-audit-patterns/SKILL.md` Smell 2.31 | ✅ Mas é descrição de auditoria para `@agent-auditor`, não instrução operacional | ❌ Só carregado por 3 agents de governança |
| `agent-contracts/SKILL.md` (banner, full-loaded por dezenas de agents) | ❌ Só a chave no próprio frontmatter, zero explicação no corpo | ❌ Gap confirmado |
| Cada um dos 188 artefatos migrados (ex.: `code-review.agent.md`) | ❌ Só a lista de paths | ❌ Gap confirmado |
| `.github/hooks/context-mode.json` (hook real de runtime) | ❌ Nenhuma referência | Confirma ausência de qualquer mecanismo mecânico |

### 14.2 Solução Adotada

Reaproveitado o mecanismo **já existente e testado** `tools/agent_protocol_sync/sync_execution_protocol.py`, que sincroniza o bloco `<execution_protocol>` (parte do **corpo**, não do frontmatter) a partir de uma fonte canônica única (`_execution-protocol-fragment.md`) para 85 agents mapeados em `protocol_roles.json`.

**Diff aplicado**: adicionado o item 8 ao bloco `<!-- BEGIN:STANDARD -->`:
```
8. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este
   agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`,
   `.github/copilot-instructions.md`, `.github/agents/workflows.md`) NÃO foram pré-carregados — é
   TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente
   via `context-mode/ctx_search` com query pontual apenas quando precisar citá-los.
```

**Propagação**: `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` → 84 de 85 agents mapeados atualizados (1 CUSTOM/`codegraph-engine` inalterado por design — mantém protocolo próprio, script só valida presença de "R-060").

### 14.3 Por que esta solução é superior à alternativa original (editar `agent-contracts/SKILL.md`)

1. **Independe de o agente ter o skill em `source_docs`**: a instrução vai direto no corpo do próprio `.agent.md`, sempre presente.
2. **Reaproveita infraestrutura já testada** (gate `--check` existente, usado em CI) em vez de criar um novo mecanismo.
3. **Rastreabilidade de fonte única**: qualquer ajuste futuro ao texto é feito 1x no fragmento e propagado automaticamente — mesmo padrão disciplinar já usado em F1/F2.

### 14.4 Testes Determinísticos Adicionados

- `test_execution_protocol_fragment_instructs_source_docs_lazy_semantics` — valida que o fragmento canônico contém a instrução + referência a R-066.
- `test_standard_agents_execution_protocol_propagated_with_source_docs_lazy_item` — valida `sync_execution_protocol.py --check` retorna drift=0, confirmando propagação ponta a ponta (fonte → 84 artefatos finais).

### 14.5 Validação Final

539/540 testes passando na suíte completa (`tests/` inteira, exceto a falha pré-existente e não-relacionada `test_no_local_projects_referenced_in_git_tracked_files`). `CHANGELOG.md` [2.52.1] registra a correção.

### 14.6 Lacuna Residual Reconhecida em 14 (Corrigida em § 15)

Routers (`agent-router`, 7 domain routers) e `codegraph-engine` (CUSTOM) não recebem o item 8 — aceitável porque routers operam sob R-054 (Zero Discovery / Least Privilege) e não leem `source_docs_lazy` na prática operacional.

~~Skills (`SKILL.md`) e prompts (`*.prompt.md`) não têm bloco `<execution_protocol>` próprio, mas herdam a instrução do agent executor hospedeiro no momento em que são ativados dentro de uma sessão.~~ → **Premissa corrigida em § 15**: esta suposição estava incompleta para prompts — um `*.prompt.md` pode ser invocado via `/comando` como ponto de entrada direto (ex.: `/commit`, `/plan`), sem nenhum agent executor "hospedeiro" já ativo na sessão. Nesse cenário, o prompt não herda instrução alguma; precisa do próprio bloco.

---

## 15. Adendo Pós-Conclusão #2 — Gap Irmão: Prompts Também Precisavam do `<execution_protocol>`

### 15.1 Diagnóstico

Revisão do usuário sobre `test-strategy.agent.md` levantou a pergunta: "os prompts também deveriam ter `<execution_protocol>`?". Investigação via `context-mode/ctx_execute` (lote único, conforme pedido explícito do usuário para minimizar poluição de contexto/créditos) confirmou:

```
Total prompts: 22
Com <execution_protocol>: 0
Com source_docs_lazy: 22
```

**100% dos prompts já haviam sido migrados para `source_docs_lazy:` em F2/[2.52.0], mas 0% tinham o bloco operacional** — exatamente o mesmo gap de § 14, nunca propagado para prompts porque `sync_execution_protocol.py` só varria `.github/agents/`. A suposição em § 14.6 ("prompts herdam do agent hospedeiro") não se sustentava para prompts invocados como ponto de entrada direto via `/comando`.

### 15.2 Solução Adotada

Estendido `tools/agent_protocol_sync/sync_execution_protocol.py` (mesma fonte canônica, sem duplicar lógica):
- Nova função `get_prompt_files()` — varre `.github/prompts/**/*.prompt.md`, excluindo `templates/`.
- Nova função `sync_prompts(expected_block, apply)` — como prompts não têm distinção STANDARD/CUSTOM nem seção fixa de ancoragem (diferente dos agents, que inserem antes de "## Retorno ao Router"), o bloco é inserido ao **final do arquivo**.
- `main()` agora reporta e sincroniza agents e prompts na mesma execução (`--check` cobre ambos; exit code 1 se qualquer um tiver drift).

Aplicado via `--apply`: **22/22 prompts corrigidos** em uma única operação.

### 15.3 Conflito de Nomenclatura Encontrado e Resolvido

`test_prompt_synthesis_output_format_governance.py::test_no_residual_xml_prompt_synthesis` falhou após a propagação: o teste trata `<execution_protocol>` como uma das 5 tags XML proibidas residuais do **antigo formato de saída** do `WORKFLOW-PROMPT-SYNTHESIS` (conceito histórico não-relacionado ao bloco operacional de Plan-Then-Batch). Corrigido removendo o bloco `<execution_protocol>...</execution_protocol>` do texto de `craft-prompt.prompt.md` **antes** de escanear por XML residual, preservando a proteção original contra regressão do formato antigo nas demais 4 tags (`<role>`, `<project_context>`, `<grounded_files>`, `<acceptance_criteria>`).

### 15.4 Testes Determinísticos Adicionados

- `test_all_prompts_contain_execution_protocol_block` — valida diretamente (sem depender do script) que 100% dos prompts têm o bloco íntegro com a instrução de `source_docs_lazy`.
- `test_standard_agents_execution_protocol_propagated_with_source_docs_lazy_item` (já existente, § 14.4) passa a cobrir prompts transitivamente, pois `sync_execution_protocol.py --check` agora inclui ambos.

### 15.5 Validação Final

540/541 testes passando (toda a suíte, exceto a falha pré-existente e não-relacionada). `CHANGELOG.md` [2.52.2] registra a correção.

### 15.6 Lacuna Residual Final (aceita conscientemente)

Routers e `codegraph-engine` (CUSTOM) permanecem sem o bloco — correto por design (R-054). Templates (`skills/templates/skill-template.md`, `prompts/templates/prompt-template.md`) não recebem o bloco automaticamente (são excluídos do glob por conterem placeholders `<slug-kebab-case>` não-resolvíveis) —se desejado, a inserção manual do bloco nesses 2 templates fica como follow-up de baixo risco para consistência total de "todo novo artefato já nasce em conformidade" (mesmo espírito de F6).


