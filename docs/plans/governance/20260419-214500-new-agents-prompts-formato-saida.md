---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-04-19"
review_verdict: PASS_WITH_NITS
review_rounds: 1
reviewer: "@plan-critic"
review_tier1: PASS
allowed_files:
  - "docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - ".github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md"
  - ".github/agents/governance-factory.agent.md"
  - ".github/skills/agent-contracts/SKILL.md"
  - ".github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md"
  - ".github/agents/templates/agent-template.md"
  - ".github/agents/templates/operational-agent.md"
  - ".github/agents/templates/research-agent.md"
  - ".github/agents/templates/router-agent.md"
  - ".github/prompts/templates/prompt-template.md"
  - "tests/governance_audit/test_router_agents.py"
  - "tests/governance_audit/test_template_sections.py"
lessons_extracted: true
lessons_applied_to: ["@agent-auditor", "plan-conformance-patterns"]
lessons_at: "2026-11-15"
related-planning-doc: "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"
session_id: "sess-20260420-router-header-line-breaks"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-trace-20260420-router-header-line-breaks"
parent_plan_ref: "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 1
  blockers: 0
  majors: 0
  minors: 0
  nits: 4
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
---

# Plano de Manutenção de Governança — Blindagem Preventiva CommonMark-Safe de `Formato de Saída` para Novos Agents e Prompts (Factory, Templates, Contratos e Testes)

## Destino e Papel Read-Only (R-064)

- **Subpasta canônica de destino**: `docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md`.
- O agent planejador/auditor (`@agent-auditor`) permanece **100% Read-Only**: emite o diagnóstico e plano estruturado segundo o template canônico `.github/skills/governance-audit-patterns/references/plan-template-governance.md`; a **materialização física `.md`** em estado `DRAFT` (`approved: false`) é executada exclusivamente nesta Etapa 2 por `@governance-maintainer` sob a exceção canônica R-064 (sem tocar em nenhum arquivo de `.github/`, `tools/` ou `tests/` antes do Gate HITL).
- O plano nasce com `status: DRAFT` e `approved: false`; somente após revisão pré-HITL pelo `@plan-critic` (Gate 1) e aprovação humana explícita via `ask_questions` (Gate 2 / R-064) passa a `APPROVED`/`true` para execução em lote na Etapa 4.

---

## 1. Escopo da Manutenção e Achados (Smells 2.x com Severidade)

No plano pai (`docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md`), os 63 agents existentes e os 4 templates de agents tiveram seus blocos `Formato de Saída` corrigidos para evitar a fusão de linhas consecutivas (*lazy paragraph continuation*) no renderizador CommonMark do VS Code Copilot Chat. Contudo, a auditoria preventiva sobre o pipeline de criação de **novos agents, prompts e stacks** (`@governance-factory` + skills de fábrica/contratos + templates SSOT + testes de auditoria) identificou **4 lacunas estruturais** que permitiriam que novos artefatos voltassem a nascer com colapso de quebra de linha:

- **Smell 2.35 — Ausência de Regra/Checklist Anti-Colapso CommonMark nas Skills e Agente da Fábrica (Severidade: ALTA)**:
  - `.github/skills/governance-factory-patterns/SKILL.md` (§3.1 `type: agent`, §3.2 `type: prompt`, §5 `Formato de Saída`), `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` (§4 `Formato de Saída`), `.github/agents/governance-factory.agent.md` (`## Padrão Estrutural por Tipo` e `## Checklist Antes de Codar`) e `.github/skills/agent-contracts/SKILL.md` (§0 `Regra de Ouro` e §8 `Checklist ao Criar/Revisar Agent`) não instruem explicitamente que todo novo agent ou prompt deve isolar linhas de cabeçalho (`Agente Ativo:`, `[Se aplicável] Handoff:`, `Skills Carregadas:`, `[CURRENT_STATE_LOCK: ...]`) com linha em branco (`\n\n`) e formatar metadados `Campo: valor` consecutivos como lista Markdown (`- `).
- **Smell 2.36 — Esqueletos de `Formato de Saída` Sem Banner `Agente Ativo:` e Sem Diretriz Anti-Colapso em `specialist-hybrid-advisory-implementation-patterns` (Severidade: MÉDIA)**:
  - Em `.github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md` (§2 L44-76 Modo Advisory e §3 L78-97 Modo Implementação), os esqueletos ```markdown não incluem o cabeçalho `Agente Ativo: <stack>-<role>` / `[Se aplicável] Handoff: ...` separado por linha em branco nem o item de verificação CommonMark-safe no `## 5) Checklist Unificado — Antes de Analisar/Implementar` (L126-134).
- **Smell 2.37 — Ausência de Diretriz Explícita In-Place nos 5 Templates Canônicos SSOT (Severidade: MÉDIA)**:
  - `.github/agents/templates/agent-template.md` (L111), `.github/agents/templates/operational-agent.md` (L93), `.github/agents/templates/research-agent.md` (L94), `.github/agents/templates/router-agent.md` (L67 e L79-83, onde `Entradas consideradas:` e `Próximo passo mínimo:` ainda estão colados nos itens de lista sem linha em branco antes do rótulo) e `.github/prompts/templates/prompt-template.md` (L86) não possuem comentário/diretriz normativa explícita junto à seção `Formato de Saída` determinando que qualquer novo campo adicionado ao cabeçalho deve usar lista Markdown (`- `) ou separação por linha em branco (`\n\n`).
- **Smell 2.38 — Cobertura Incompleta do Gate Automatizado Pytest para Prompts, Skills de Fábrica e Teste Negativo com Fixture Sintética (Severidade: ALTA)**:
  - Em `tests/governance_audit/test_router_agents.py` (L380-468), `test_all_agents_and_templates_formato_de_saida_no_adjacent_collapsible_lines()` inspeciona apenas `.github/agents/**/*.agent.md`, `.github/agents/templates/*.md` e `.github/skills/agent-contracts/SKILL.md`, deixando de fora os **22 prompts** (`.github/prompts/**/*.prompt.md`), o template `.github/prompts/templates/prompt-template.md`, `.github/skills/governance-factory-patterns/SKILL.md`, `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` e `.github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md`. Além disso, falta um teste unitário com fixture sintética negativa provando que o validador falha deterministamente caso um novo agent ou prompt seja criado com linhas adjacentes colapsáveis, e falta asserção da diretriz anti-colapso nos templates em `tests/governance_audit/test_template_sections.py`.

---

## 2. Inventário Completo de Arquivos Afetados (`allowed_files`)

Nenhum glob é utilizado em `allowed_files`. Os **13 arquivos** autorizados para este plano são:

1. `docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md` — **Plano R-064** (este artefato).
2. `.github/skills/governance-factory-patterns/SKILL.md` — **Regras e Checklist de Fábrica** (L59-70 e L107-113: adicionar regra obrigatória CommonMark-safe para `Formato de Saída` em `type: agent` e `type: prompt` e item de validação no bloco §5).
3. `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` — **Bloco de Validações §4** (L192-220: adicionar item `- [se agent/prompt] Formato de Saída CommonMark-safe (cabeçalhos isolados por linha em branco e metadados consecutivos em lista '- '): ✅/❌` e isolar `Resumo:` por linha em branco).
4. `.github/agents/governance-factory.agent.md` — **Regras e Checklist do Agente Fábrica** (L122-128 `type: agent`, L147-152 `type: prompt` e L230-252 `## Checklist Antes de Codar`: exigir `Formato de Saída` CommonMark-safe sem linhas adjacentes colapsáveis).
5. `.github/skills/agent-contracts/SKILL.md` — **Contrato Universal e Checklist §0 / §8** (L41-64 e L228-234: explicitar regra CommonMark-safe de separação por `\n\n` entre `Agente Ativo:`, `Handoff:`, `Skills Carregadas:` e `[CURRENT_STATE_LOCK:]`, e uso de lista `- ` para metadados consecutivos no checklist §8).
6. `.github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md` — **Esqueletos Modo Advisory (§2), Modo Implementação (§3) e Checklist (§5)** (L44-76, L78-97 e L126-134: incluir cabeçalho `Agente Ativo: <stack>-<role>` + linha em branco + `[Se aplicável] Handoff: <agent-origem> → <stack>-<role> (motivo: <motivo>)` + linha em branco nos 2 blocos ```markdown, diretriz CommonMark-safe e item no checklist §5).
7. `.github/agents/templates/agent-template.md` — **Template SSOT Geral de Agent** (L111-116 e L201-208: adicionar diretriz explícita em `### Formato de Saída Estruturado` proibindo linhas adjacentes sem `- ` ou `\n\n` e reforçar item no checklist final).
8. `.github/agents/templates/operational-agent.md` — **Template SSOT de Agent Operacional** (L93-100 e L230-239: adicionar diretriz explícita CommonMark-safe antes do bloco ```markdown e no checklist final).
9. `.github/agents/templates/research-agent.md` — **Template SSOT de Agent Analítico/Pesquisa** (L94-101 e L240-248: adicionar diretriz explícita CommonMark-safe antes do bloco ```markdown e no checklist final).
10. `.github/agents/templates/router-agent.md` — **Template SSOT de Domain Router** (L67-85: adicionar diretriz explícita CommonMark-safe antes do bloco ```markdown e inserir linha em branco antes de `Entradas consideradas:` e `Próximo passo mínimo:` para evitar colapso com a lista anterior).
11. `.github/prompts/templates/prompt-template.md` — **Template SSOT de Prompt** (L76-101: adicionar diretriz explícita CommonMark-safe em `## 📊 Formato de Saída` exigindo lista `- ` ou separação por linha em branco para campos de cabeçalho/metadados e item no `## ✅ Checklist Antes de Apresentar`).
12. `tests/governance_audit/test_router_agents.py` — **Ampliação do Validador + Teste Unitário com Fixture Sintética** (L380-469: extrair helper puro `validate_formato_de_saida_commonmark_safe(text: str, rel: str) -> None`, expandir `targets` para incluir todos os `.github/prompts/**/*.prompt.md`, `.github/prompts/templates/prompt-template.md`, `.github/skills/governance-factory-patterns/SKILL.md`, `.github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md` e `.github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md`, e adicionar `test_formato_de_saida_validator_rejects_synthetic_collapsible_agent_and_prompt()` com fixtures sintéticas negativas de agent e prompt).
13. `tests/governance_audit/test_template_sections.py` — **Blindagem de Diretrizes nos Templates e Factory** (adicionar teste `test_templates_and_factory_enforce_commonmark_safe_formato_de_saida()` verificando que os 4 templates de agent, o `prompt-template.md`, `governance-factory.agent.md`, `governance-factory-patterns/SKILL.md`, `agent-contracts/SKILL.md` e `specialist-hybrid-advisory-implementation-patterns/SKILL.md` contêm a diretriz anti-colapso CommonMark em `Formato de Saída`).

---

## 3. Plano de Correção em Lote (Plan-Then-Batch — R-059)

Após o Gate 1 (`@plan-critic`) e aprovação no Gate 2 HITL (`approved: true`), a execução será feita por `@governance-maintainer` em **turno único** via `ctx_execute` (`language: "javascript"`):

1. **Passo 1 (Atualização do Status do Plano)**: Atualizar `docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md` para `status: APPROVED` e `approved: true`.
2. **Passo 2 (Blindagem Normativa nas Skills e no `@governance-factory`)**:
   - Em `.github/skills/governance-factory-patterns/SKILL.md` (§3.1, §3.2 e §5) e `references/artifact-specs-and-stack-topology.md` (§4): adicionar cláusula normativa exigindo que todo bloco `Formato de Saída` isole `Agente Ativo:`, `Handoff:`, `Skills Carregadas:` e `[CURRENT_STATE_LOCK:]` com linha em branco (`\n\n`) e formate metadados `Campo: valor` consecutivos com prefixo de lista Markdown (`- `).
   - Em `.github/agents/governance-factory.agent.md` (`### type: agent`, `### type: prompt` e `## Checklist Antes de Codar`): adicionar verificação obrigatória de conformidade CommonMark-safe do bloco `Formato de Saída` antes de persistir qualquer novo agent, prompt ou stack.
   - Em `.github/skills/agent-contracts/SKILL.md` (§0 e §8): documentar a proibição de linhas adjacentes colapsáveis na Camada 1/Camada 2 e incluir item correspondente no `Checklist ao Criar/Revisar Agent`.
   - Em `.github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md` (§2, §3 e §5): adicionar `Agente Ativo: <stack>-<role>` e `[Se aplicável] Handoff: <agent-origem> → <stack>-<role> (motivo: <motivo>)` separados por `\n\n` no topo dos esqueletos de Modo Advisory e Modo Implementação, além de diretriz CommonMark-safe e item no checklist §5.
3. **Passo 3 (Diretriz In-Place nos 5 Templates Canônicos SSOT)**:
   - Inserir diretriz explícita (`> **Regra Anti-Colapso CommonMark**: ...`) acima do bloco ```markdown de `Formato de Saída` em `agent-template.md`, `operational-agent.md`, `research-agent.md`, `router-agent.md` (incluindo linha em branco antes de `Entradas consideradas:` e `Próximo passo mínimo:`) e `prompt-template.md`, bem como item nos respectivos checklists.
4. **Passo 4 (Ampliação da Blindagem Determinística em `tests/governance_audit/`)**:
   - Em `tests/governance_audit/test_router_agents.py`: estender a varredura para cobrir `prompts/**/*.prompt.md`, `prompts/templates/prompt-template.md` e as skills de fábrica/contratos, além de adicionar teste unitário com fixtures sintéticas negativas (agent e prompt com cabeçalhos/metadados colados) validando `pytest.raises(AssertionError)`.
   - Em `tests/governance_audit/test_template_sections.py`: adicionar asserção de presença da regra anti-colapso nos templates SSOT e no `@governance-factory`.
5. **Passo 5 (Validação Consolidada)**: Executar `pytest tests/governance_audit/` e `get_errors` único com todos os 13 arquivos de `allowed_files`.

---

## 4. Alternativas Rejeitadas

1. **Confiar apenas no teste pós-criação sem atualizar os templates SSOT e as instruções do `@governance-factory`**:
   - *Motivo da rejeição*: Viola o Portão de Reúso Sistêmico (R-055 Q2). Se os templates e a skill `governance-factory-patterns` não instruírem preventivamente o formato CommonMark-safe, o `@governance-factory` continuará gerando artefatos defeituosos na primeira tentativa e falhando apenas tardiamente no pytest.
2. **Validar apenas arquivos reais do repositório sem teste unitário de fixture sintética negativa**:
   - *Motivo da rejeição*: Sem um teste negativo sintético (`pytest.raises(AssertionError)`), uma regressão na regex do validador poderia produzir falso-positivo silencioso (passando sempre sem inspecionar os blocos cercados).
3. **Permitir `<br>` HTML inline nos templates `agent-template.md` e `prompt-template.md`**:
   - *Motivo da rejeição*: Polui o Markdown puro copiado para o chat e é inconsistente com o padrão de listas Markdown (`- `) e parágrafos separados por linha em branco (`\n\n`) adotado nos 63 agents e 22 prompts do repositório.

---

## 5. Reúso Sistêmico (R-055: Q1 / Q2 / Q3) e Compatibilidade de Testes

- **Q1 (Impacto Horizontal / Peers)**: Cobre simultaneamente todos os pontos de entrada de criação de artefatos (`governance-factory.agent.md`, `governance-factory-patterns/SKILL.md`, `agent-contracts/SKILL.md` e `specialist-hybrid-advisory-implementation-patterns/SKILL.md`), bem como os 22 prompts existentes (`.github/prompts/**/*.prompt.md`) que passam a ser auditados continuamente pelo pytest.
- **Q2 (Prevenção Futura / Templates)**: Todos os 4 templates de agents (`agent-template.md`, `operational-agent.md`, `research-agent.md`, `router-agent.md`) e o template de prompt (`prompt-template.md`) passam a conter a diretriz anti-colapso CommonMark explícita in-place e exemplos 100% conformes.
- **Q3 (Blindagem por Teste / Quality Gate)**: `tests/governance_audit/test_router_agents.py` e `tests/governance_audit/test_template_sections.py` passam a validar automaticamente agents, prompts, templates e skills de fábrica, além de testar explicitamente a falha do validador contra fixtures sintéticas defeituosas de agent e prompt.

---

## 6. Rollback e Critério de Pronto

- **Comando de Rollback Exato**:
  ```bash
  git checkout -- .github/skills/governance-factory-patterns/SKILL.md .github/skills/governance-factory-patterns/references/artifact-specs-and-stack-topology.md .github/agents/governance-factory.agent.md .github/skills/agent-contracts/SKILL.md .github/skills/specialist-hybrid-advisory-implementation-patterns/SKILL.md .github/agents/templates/agent-template.md .github/agents/templates/operational-agent.md .github/agents/templates/research-agent.md .github/agents/templates/router-agent.md .github/prompts/templates/prompt-template.md tests/governance_audit/test_router_agents.py tests/governance_audit/test_template_sections.py
  ```
  - **Preservação de Evidência de Auditoria (R-064)**: O artefato de plano `docs/plans/governance/20260419-214500-new-agents-prompts-formato-saida.md` **não** é removido no rollback (`rm -f` vedado), sendo preservado em disco como registro histórico e evidência rastreável de auditoria.
- **Critério de Pronto (DoD)**:
  - [ ] Regras e checklists anti-colapso CommonMark adicionados em `governance-factory-patterns/SKILL.md`, `references/artifact-specs-and-stack-topology.md`, `governance-factory.agent.md`, `agent-contracts/SKILL.md` e `specialist-hybrid-advisory-implementation-patterns/SKILL.md`.
  - [ ] Diretriz explícita CommonMark-safe presente nos 5 templates canônicos (`.github/agents/templates/*.md` e `.github/prompts/templates/prompt-template.md`).
  - [ ] `tests/governance_audit/test_router_agents.py` e `tests/governance_audit/test_template_sections.py` cobrindo prompts, templates e skills de fábrica, incluindo teste unitário negativo com fixture sintética passando com `0 failed`.
  - [ ] `get_errors` sem erros nos 13 arquivos de `allowed_files`.

---

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS` (`review_tier1: PASS`, frontmatter R-064 íntegro, `status: DRAFT`, `approved: false`, `created_at: "2026-04-19"`, `author: "@agent-auditor"`, `reviewer: "@plan-critic"`, 13 entradas explícitas em `allowed_files` sem globs).
- **Tier 2 (`@plan-critic`)**: `PASS_WITH_NITS` (Fast-Pass — Rodada 1: `review_rounds: 1`, `reviewer: "@plan-critic"`, `blockers: 0`, `majors: 0`, `minors: 0`, `nits: 4`).
- **Findings e Resoluções (Rodada 1 — 4 Nits não-bloqueantes registrados)**:
  1. `NIT-01` (Precisão de escopo em `allowed_files` vs varredura read-only): Os 22 prompts existentes (`.github/prompts/**/*.prompt.md`) citados em Q1 (L118) e L81 são inspecionados em modo read-only pelo validador em `tests/governance_audit/test_router_agents.py`, mantendo-se exatamente os 13 arquivos de mutação em `allowed_files`.
  2. `NIT-02` (Alinhamento de linhas aproximadas nos alvos): Os intervalos de linhas indicados no inventário da seção 2 (L71-83) servem como âncora contextual de inspeção; a aplicação em lote no Passo 2–4 utilizará âncoras semânticas de seção com 2–3 linhas de contexto para evitar deslocamento cumulativo.
  3. `NIT-03` (Isolamento das fixtures sintéticas em `test_router_agents.py`): O teste unitário negativo `test_formato_de_saida_validator_rejects_synthetic_collapsible_agent_and_prompt()` operará sobre strings em memória no helper `validate_formato_de_saida_commonmark_safe(text, rel)`, sem criar arquivos temporários em `.github/`.
  4. `NIT-04` (Sincronização de metadados pré-HITL): Persistência de `review_verdict: PASS_WITH_NITS`, `review_rounds: 1` e `critic_findings_summary` (`rounds: 1`, `nits: 4`, `last_verdict: "PASS_WITH_NITS"`) mantendo `status: DRAFT` e `approved: false` até a decisão humana via `ask_questions` (Gate 2 HITL).

## Checklist

- [x] Frontmatter R-064 completo (`plan_type: "governance"`, `status: DRAFT`, `approved: false`, `created_at: "2026-04-19"`, `review_verdict: PASS_WITH_NITS`, `review_rounds: 1`, `related-planning-doc: "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"`, `parent_plan_ref: "docs/plans/governance/20260419-211000-agents-prompts-formato-saida.md"`).
- [x] Persistência exclusiva do plano `DRAFT` por `@governance-maintainer`; zero arquivos alterados em `.github/`, `tools/` ou `tests/` antes do Gate HITL (R-064).
- [x] Seção `## Destino e Papel Read-Only (R-064)`, comando de rollback sem `rm -f` do plano e `allowed_files` explícitos sem globs.
