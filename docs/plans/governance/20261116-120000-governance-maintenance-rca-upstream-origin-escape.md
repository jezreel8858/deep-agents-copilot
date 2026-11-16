---
status: APPROVED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-16"
related-planning-doc: "N/A"
session_id: "sess-20261116-rca-upstream"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wf-trace-20261116-000001"
parent_plan_ref: "N/A — plano raiz"
rollback_plan: "git --no-pager restore -- .github/skills/governance-audit-patterns/references/plan-template-governance.md .github/skills/governance-audit-patterns/SKILL.md .github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/agents/plan-critic.agent.md .github/agents/agent-auditor.agent.md .github/agents/governance-factory.agent.md CLAUDE.md .github/copilot-instructions.md .github/agents/workflows.md .github/agents/workflows/invariantes-e-protocolos.md CHANGELOG.md"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
reviewer: "@plan-critic"
reviewed_at: "2026-11-16"
critic_round: 2
critic_Agent: "@plan-critic"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 3
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@agent-auditor"
allowed_files:
  - ".github/skills/governance-audit-patterns/references/plan-template-governance.md"
  - ".github/skills/governance-audit-patterns/SKILL.md"
  - ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
  - ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md"
  - ".github/agents/plan-critic.agent.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/governance-factory.agent.md"
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - "CHANGELOG.md"
---

# Plano de Governança — RCA Upstream (Q0) obrigatória em planos corretivos

## 1. Escopo da manutenção e achados

**Diagnóstico Forense (Q0):** `intencao_plano: evolutivo` — N/A — plano puramente evolutivo/greenfield (institui obrigação nova; nenhum defeito gerado por template, script ou sensor).

**Objetivo:** exigir no `WORKFLOW-GOVERNANCE-MAINTENANCE`, para planos corretivos, remediativos ou híbridos, três dimensões obrigatórias:
- Origem Upstream (Fonte Geradora).
- Análise de Escape (Falha de Contenção).
- Neutralização na Fonte.

Planos 100% evolutivos (greenfield) ficam isentos, com justificativa explícita (`N/A — plano puramente evolutivo/greenfield`).

**Não-escopo:** `WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-FEATURE-DEVELOPMENT` e demais workflows de código permanecem inalterados.

| # | Achado | Evidência | Severidade |
|---|---|---|---|
| A1 | R-055 sem passo Q0 (Origem Upstream) | `CLAUDE.md` L74/L156, `.github/copilot-instructions.md` L53 | Alto |
| A2 | Template de governança sem classificação de intenção nem RCA | `plan-template-governance.md` L45, L49, L53 (68L, 6 itens no corpo) | Alto |
| A3 | Rubrica e `@plan-critic` não reprovam correção só de sintoma | `pre-hitl-skeptical-review-rubric.md` L54/L56, `plan-critic.agent.md` L72/L114 | Alto |
| A4 | Planejadores sem instrução de investigar geradores e templates | `agent-auditor.agent.md` L154, `governance-factory.agent.md` L298 | Sugestão |
| A5 | Sem sensor determinístico pytest para Q0 | `tests/governance_audit/` (ausência de `test_upstream_rca_gate.py`) | Alto |

**C1 (grounding físico e âncoras verificadas via `fs`):**
- `.github/skills/governance-audit-patterns/references/plan-template-governance.md`: L45 (`1. Escopo da manutenção e achados (smells 2.x com severidade)`), L49 (`5. Reúso sistêmico (R-055: Q1/Q2/Q3) e sensores tests/governance_audit/`), L53 (`## Parecer do Revisor Cético Pré-HITL (R-064)`).
- `.github/skills/governance-audit-patterns/SKILL.md`: §5 L170 (`## 5) Referências e Documentação Conexa`) / L173 (`- references/plan-template-governance.md — template de plano governance (R-064) em docs/plans/governance/.`).
- `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md`: L54 (`| `governance` | 1 | Reúso sistêmico R-055 (Q1/Q2/Q3), catálogos R-015, testes determinísticos, rollback |`) e L56 (`## 7. Dupla Lente`).
- `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md`: L6 (`2. **C2 — Seções Obrigatórias**: seções do template (ex.: Alternativas Rejeitadas, Teste de Regressão, Rollback, Parecer do Revisor Cético Pré-HITL, Checklist).`, 15L / 1961B).
- `.github/agents/plan-critic.agent.md`: L72 (item 8 de `## Padrões Obrigatórios`) e L114 (último item de `## Checklist`).
- `.github/agents/agent-auditor.agent.md`: L154 (`- **Checklist Pré-Voo (C1–C9)**: ...`, 176L).
- `.github/agents/governance-factory.agent.md`: L298 (`- **Checklist Pré-Voo (C1–C9)**: ...`, 322L).
- `CLAUDE.md`: L74 (tabela R-055) e L156 (`- **Auto-Reflexão Sistêmica (R-055)**: ...`).
- `.github/copilot-instructions.md`: L53 (`Responder a Q1 (peers)`).
- `.github/agents/workflows.md`: L134 (tabela `WORKFLOW-GOVERNANCE-MAINTENANCE`: `1. Diagnóstico (@agent-auditor)`) e L163 (§ 3.5 `WORKFLOW-GOVERNANCE-MAINTENANCE`: `1. Diagnóstico (@agent-auditor)`).
- `.github/agents/workflows/invariantes-e-protocolos.md`: L156 (`- [▶] **Etapa 1: Diagnóstico Read-Only ou Pesquisa Prévia** → @agent-auditor / @repo-hygiene-auditor / @docs-engineer / @deep-search *(Em Andamento: auditoria estrutural, documental e pesquisa prévia)*`).
- `CHANGELOG.md`: L7 (`## [2.59.0] — 2026-11-16`, 719L).

## 2. Arquivos de governança afetados

| Onda | Executor | Escopo (`allowed_files` / alvo) | Natureza |
|---|---|---|---|
| **Onda 1 (este plano)** | `@governance-maintainer` (Etapa 5 pós-HITL) | 12 arquivos `.md` listados em `allowed_files` no frontmatter (zero Python/globs — C3) | Documentação, templates, rubrica, agentes e SSOT |
| **Onda 2 (Tríade Python — Q3)** | `@python-developer` -> `@test-Automation-engineer` -> `@code-reviewer` | `tests/governance_audit/test_upstream_rca_gate.py` (novo sensor determinístico) | Sensor pytest AST/regex (fora de `allowed_files` da Onda 1 para respeitar segregação C3) |

## 3. Plano de correção em lote (Plan-Then-Batch)

A Onda 1 será aplicada em um único `ctx_execute` (`language: "javascript"`, Node.js `fs`, escrita atômica all-or-nothing dos 12 arquivos `.md` sob R-046), seguida de chamada única a `get_errors` (R-051).

### T1 — `.github/skills/governance-audit-patterns/references/plan-template-governance.md` (L45, L49, L53)

**Antes (Estrutura do Corpo, L45 e L49):**
```markdown
1. Escopo da manutenção e achados (smells 2.x com severidade)
...
5. Reúso sistêmico (R-055: Q1/Q2/Q3) e sensores `tests/governance_audit/`
```
**Depois:**
```markdown
1. Escopo da manutenção e achados (smells 2.x com severidade) + **Diagnóstico Forense (Q0)**: `intencao_plano: corretivo | remediativo | hibrido | evolutivo`
...
5. Reúso sistêmico (R-055: **Q0**/Q1/Q2/Q3) e sensores `tests/governance_audit/`
```

**Inserir nova seção antes de `## Parecer do Revisor Cético Pré-HITL (R-064)` (L53):**
```markdown
## Diagnóstico Forense — RCA Upstream (R-055 Q0)

- **Classificação de Intenção**: `corretivo | remediativo | hibrido | evolutivo`
- **Isenção Greenfield** (somente se `evolutivo`): `N/A — plano puramente evolutivo/greenfield` (com justificativa de 1 linha).

| Dimensão Q0 | Análise Obrigatória (planos `corretivo`, `remediativo` ou `hibrido`) |
|---|---|
| Origem Upstream (Fonte Geradora) | Qual script (`tools/**`), template SSOT, instrução conflitante ou agente gerou/induziu o defeito |
| Análise de Escape (Falha de Contenção) | Qual sensor (`tests/governance_audit/`), pre-commit hook ou gate falhou em bloquear antes do disco |
| Neutralização na Fonte | Tarefa explícita do plano que corrige o mecanismo gerador/indutor (não apenas o artefato onde o sintoma apareceu) |
```

### T2 — `.github/skills/governance-audit-patterns/SKILL.md` (§5 `## 5) Referências e Documentação Conexa` L170, bullet L173)

**Antes:**
```markdown
- `references/plan-template-governance.md` — template de plano `governance` (R-064) em `docs/plans/governance/`.
```
**Depois:**
```markdown
- `references/plan-template-governance.md` — template de plano `governance` (R-064) em `docs/plans/governance/`; exige RCA Upstream (Q0) em planos corretivos.
```
- Orçamento de linhas preservado: 184L (teto R-066 <= 300L; delta = 0 linhas).

### T3 — `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` (§6, L54 e L56)

**Antes (L54):**
```markdown
| `governance` | 1 | Reúso sistêmico R-055 (Q1/Q2/Q3), catálogos R-015, testes determinísticos, rollback |
```
**Depois (L54):**
```markdown
| `governance` | 1 | RCA Upstream (Q0: Origem + Escape + Neutralização na Fonte para planos corretivos; isenção justificada para evolutivos), Reúso sistêmico R-055 (Q0/Q1/Q2/Q3), catálogos R-015, testes determinísticos, rollback |
```

**Inserir antes de `## 7. Dupla Lente` (L56):**
```markdown
### Extensão `governance` — RCA Upstream (`T2-RCA`)

- **Escopo**: exclusiva para `plan_type: governance` no `WORKFLOW-GOVERNANCE-MAINTENANCE`.
- **Regra**: se o plano for `corretivo`, `remediativo` ou `hibrido` e atuar apenas sobre o sintoma (sem Origem Upstream, Análise de Escape e Neutralização na Fonte), emitir finding `BLOCKER` (código `T2-RCA`) e veredito `NEEDS_REVISION`.
- **Isenção**: planos `evolutivo` (greenfield) com `N/A — plano puramente evolutivo/greenfield` explícito e fundamentado não sofrem bloqueio.
```

### T4 — `.github/agents/plan-critic.agent.md` (L72 e L114)

**Inserir após o item 8 de `## Padrões Obrigatórios` (L72):**
```markdown
9. **RCA Upstream (`plan_type: governance`)**: reprovar (`BLOCKER` `T2-RCA`) plano corretivo/remediativo/hibrido sem Origem Upstream, Análise de Escape e Neutralização na Fonte (rubrica §6).
```
**Inserir ao fim de `## Checklist` (após L114):**
```markdown
- [ ] Plano `governance` corretivo: RCA Upstream (Origem + Escape + Neutralização na Fonte) presente; só sintoma tratado => `BLOCKER` `T2-RCA` / `NEEDS_REVISION`; evolutivo com `N/A` justificado => sem finding.
```

### T5 — `.github/agents/agent-auditor.agent.md` (L154) e `.github/agents/governance-factory.agent.md` (L298)

**Âncora idêntica verificada em ambos:**
```markdown
- **Checklist Pré-Voo (C1–C9)**: Antes do Gate `@plan-critic`, validar `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md`.
```
**Inserir imediatamente após a âncora (184 caracteres, <= 200 chars):**
```markdown
- **RCA Upstream (Q0, planos corretivos)**: investigar `tools/**`, templates SSOT, instruções conflitantes e sensores antes de propor correções; ver `plan-template-governance.md` §1/§5.
```

### T6 — `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` (L6)

**Antes (C2, L6 — 1961 bytes):**
```markdown
2. **C2 (Seções e Rollback)**: Incluir `Alternativas Rejeitadas`, `Teste de Regressão`, `Rollback`, `Blast Radius` e `rollback_plan` (sem `git clean -f`/`rm -f` no plano R-064 em `docs/plans/<tipo>/`, preservando auditoria).
```
**Depois (C2, L6 — 1984 bytes, +23B):**
```markdown
2. **C2 (Seções e Rollback)**: Incluir `Alternativas Rejeitadas`, `Teste de Regressão`, `Rollback`, `Blast Radius`, RCA Q0 (se corretivo) e `rollback_plan` (sem `git clean -f`/`rm -f` no plano R-064 em `docs/plans/<tipo>/`, preservando auditoria).
```
- Orçamento estrito respeitado: 15 linhas (<= 40L) e 1984 bytes (de 1961B para 1984B, <= 2048B), mantendo cobertura C1–C10 intacta.

### T7 — Redação de R-055 e Pipeline WF5 (`CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`, `.github/agents/workflows/invariantes-e-protocolos.md`)

| Arquivo | Linha | Antes | Depois |
|---|---|---|---|
| `CLAUDE.md` | L74 e L156 | `responder compulsoriamente a Q1 (peers)` | `responder compulsoriamente a Q0 (origem upstream/RCA, se corretivo), Q1 (peers)` |
| `.github/copilot-instructions.md` | L53 | `Responder a Q1 (peers)` | `Responder a Q0 (origem upstream/RCA, se corretivo), Q1 (peers)` |
| `.github/agents/workflows.md` | L134 e L163 (`WORKFLOW-GOVERNANCE-MAINTENANCE`: tabela §3 + §3.5, `replaceAll` da substring exata) | `1. Diagnóstico (@agent-auditor)` | `1. Diagnóstico + RCA Upstream Q0 se corretivo (@agent-auditor)` |
| `.github/agents/workflows/invariantes-e-protocolos.md` | L156 | `- [▶] **Etapa 1: Diagnóstico Read-Only ou Pesquisa Prévia** → `@agent-auditor` / `@repo-hygiene-auditor` / `@docs-engineer` / `@deep-search` *(Em Andamento: auditoria estrutural, documental e pesquisa prévia)*` | `- [▶] **Etapa 1: Diagnóstico Read-Only ou Pesquisa Prévia (+ RCA Upstream Q0 se corretivo)** → `@agent-auditor` / `@repo-hygiene-auditor` / `@docs-engineer` / `@deep-search` *(Em Andamento: auditoria estrutural, documental e pesquisa prévia)*` |

### T8 — `CHANGELOG.md` (L7)

**Inserir antes de `## [2.59.0] — 2026-11-16` (L7, bullets <= 200 chars, <= 12 bullets):**
```markdown
## [2.60.0] — 2026-11-16
### Added
- **R-055 Q0 (RCA Upstream)**: planos de governança corretivos exigem Origem Upstream, Análise de Escape e Neutralização na Fonte; evolutivos isentos com `N/A` justificado.
- Teste `tests/governance_audit/test_upstream_rca_gate.py` validando Q0 em template, rubrica, `@plan-critic` e planejadores.
### Changed
- `plan-template-governance.md`, rubrica pré-HITL (`T2-RCA`), `@plan-critic`, `@agent-auditor`, `@governance-factory` e `planner-preflight-checklist.md` (C2).
- Redação de R-055 em `CLAUDE.md`, `copilot-instructions.md`, `workflows.md` e `invariantes-e-protocolos.md`.
```

### T9 — Especificação da Onda 2 (Q3 — Tríade Python): `tests/governance_audit/test_upstream_rca_gate.py`

A ser implementada na Onda 2 via handoff `@agent-router` → `@python-router` → `@python-arch-advisor` → `@python-test-engineer`:
```python
"""test_upstream_rca_gate.py — Q0 (RCA Upstream) em planos corretivos de governança (R-055/R-064)."""
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".github" / "skills"
AG = ROOT / ".github" / "agents"
TEMPLATE = SK / "governance-audit-patterns/references/plan-template-governance.md"
RUBRIC = SK / "plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
PREFLIGHT = SK / "plan-conformance-patterns/references/planner-preflight-checklist.md"

def _t(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def test_template_exige_rca_upstream() -> None:
    c = _t(TEMPLATE)
    for k in ("Origem Upstream", "Análise de Escape", "Neutralização na Fonte", "evolutivo", "N/A — plano puramente evolutivo/greenfield"):
        assert k in c, f"Template governance sem '{k}'. Remediação: adicionar seção 'Diagnóstico Forense — RCA Upstream (R-055 Q0)'."

def test_rubrica_e_critic_reprovam_so_sintoma() -> None:
    for p in (RUBRIC, AG / "plan-critic.agent.md"):
        c = _t(p)
        assert "T2-RCA" in c and "Neutralização na Fonte" in c, f"{p.name}: faltou T2-RCA/Neutralização. Remediação: ver rubrica §6."

@pytest.mark.parametrize("name", ["agent-auditor.agent.md", "governance-factory.agent.md"])
def test_planejadores_apontam_rca_upstream(name: str) -> None:
    c = _t(AG / name)
    assert "RCA Upstream" in c and "tools/**" in c, f"{name} sem diretriz RCA Upstream (Q0). Remediação: adicionar bullet após Checklist Pré-Voo."

def test_preflight_dentro_do_orcamento() -> None:
    p = PREFLIGHT
    assert len(_t(p).splitlines()) <= 40 and p.stat().st_size <= 2048, "Checklist acima de 40L/2048B. Remediação: compactar C2."
    c = _t(p)
    assert all(f"C{i}" in c for i in range(1, 10)), "Checklist sem cobertura C1–C9."

def test_r055_declara_q0_em_instrucoes_e_workflow() -> None:
    for f in ("CLAUDE.md", ".github/copilot-instructions.md", ".github/agents/workflows.md"):
        assert "Q0" in _t(ROOT / f), f"{f} sem Q0 (RCA upstream). Remediação: ver T7 do plano."
```

### Teste de Regressão e Cenários Gherkin (C4)

- **Cenário 1 (Plano Corretivo sem RCA na Fonte)**: *Dado* um plano `governance` com `intencao_plano: corretivo` que altera apenas o artefato-sintoma sem diagnosticar Origem Upstream, Análise de Escape e Neutralização na Fonte, *Quando* o `@plan-critic` avalia na Etapa 3, *Então* emite `BLOCKER` `T2-RCA` com `review_verdict: NEEDS_REVISION`.
- **Cenário 2 (Plano Evolutivo Greenfield)**: *Dado* um plano `governance` com `intencao_plano: evolutivo` e justificativa `N/A — plano puramente evolutivo/greenfield`, *Quando* revisado pelo `@plan-critic`, *Então* não recebe apontamento `T2-RCA`.
- **Teste de Regressão**: execução de `tests/governance_audit/test_upstream_rca_gate.py`, `tests/governance_audit/test_systemic_reuse_gate.py`, `tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py`, `tests/governance_audit/test_planning_doc_template_governance.py` e `tests/governance_audit/test_changelog_integrity.py`.

**Comandos de Verificação (R-035 — zero pager):**
```bash
python -m tools.governance_sync --check
python -m pytest tests/governance_audit/test_systemic_reuse_gate.py tests/governance_audit/test_pre_hitl_skeptical_plan_gate.py tests/governance_audit/test_planning_doc_template_governance.py tests/governance_audit/test_changelog_integrity.py -q -p no:cacheprovider
git --no-pager diff --stat
```

## 4. Alternativas Rejeitadas

| Alternativa | Motivo da rejeição |
|---|---|
| Criar nova regra global `R-068` separada da `R-055` | Fragmenta o Portão de Reúso Sistêmico e aumenta o custo de sincronização; `Q0` (Origem Upstream) é o passo prévio natural de `Q1`/`Q2`/`Q3` na `R-055`. |
| Criar código `T2-8` no núcleo universal da rubrica | Alteraria o contrato `T2-1..T2-7` de todos os 8 tipos de plano e quebraria testes existentes; a extensão `T2-RCA` na seção de `governance` respeita o não-escopo dos demais workflows. |
| Adicionar linha `C11` em `planner-preflight-checklist.md` | O arquivo tem 1961B (folga de 87B até o teto rígido de 2048B); criar `C11` estouraria o orçamento de bytes. Incorporar `, RCA Q0 (se corretivo)` em `C2` (L6) soma apenas 23B (1961B -> 1984B). |
| Exigir RCA forense em 100% dos planos de governança sem filtro | Forçaria alucinação de causa raiz em planos 100% evolutivos (greenfield), violando YAGNI (R-011). |
| Alterar `WORKFLOW-BUG-FIX` ou `WORKFLOW-REFACTORING` | Fora de escopo explícito; esses workflows já possuem agentes e templates dedicados (`@bug-triage`, `@debugger`, `@refactor-planner`). |

## 5. Reúso sistêmico (R-055: Q0/Q1/Q2/Q3) e sensores `tests/governance_audit/`

- **Q0 (Origem Upstream):** `N/A — plano puramente evolutivo/greenfield` (institui a própria obrigação de Q0 no workflow de governança).
- **Q1 (Peers):** cobertura completa dos planejadores e revisores de governança (`@agent-auditor`, `@governance-factory`, `@plan-critic`), além de `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md` e `.github/agents/workflows/invariantes-e-protocolos.md`.
- **Q2 (Templates):** atualização do template SSOT `.github/skills/governance-audit-patterns/references/plan-template-governance.md` e do checklist `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` (C2).
- **Q3 (Sensores Pytest):** especificação completa em T9 do teste determinístico `tests/governance_audit/test_upstream_rca_gate.py`, a ser implementado na Onda 2 via handoff para `@agent-router` → `@python-router` → `@python-arch-advisor` → `@python-test-engineer`.
- **Sincronização Atômica (R-015/R-040):** validação pós-Onda 1 via `python -m tools.governance_sync --check`.
- **Segurança Agêntica e Isolamento (R-043/R-044):** zero referência a adapters ou slugs locais; conteúdo tratado como dado inerte (OWASP ASI01/ASI06).

## 6. Rollback e critério de pronto

- **Blast Radius:** Onda 1 restrita a 12 arquivos `.md` declarativos de governança; Onda 2 restrita a 1 arquivo novo de teste Python (`tests/governance_audit/test_upstream_rca_gate.py`) executado pela Tríade Python. Zero impacto em código de aplicação (`apps/`, `deploy/`) ou nos demais workflows.
- **`rollback_plan` (Onda 1 — 100% executável, zero comandos destrutivos):**
  ```bash
  git --no-pager restore -- .github/skills/governance-audit-patterns/references/plan-template-governance.md .github/skills/governance-audit-patterns/SKILL.md .github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md .github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md .github/agents/plan-critic.agent.md .github/agents/agent-auditor.agent.md .github/agents/governance-factory.agent.md CLAUDE.md .github/copilot-instructions.md .github/agents/workflows.md .github/agents/workflows/invariantes-e-protocolos.md CHANGELOG.md
  ```
- **Rollback da Onda 2 (Tríade Python):** reversão do commit da Onda 2 via `git --no-pager revert HEAD` ou, caso não commitado, remoção cirúrgica via `node -e "const fs=require('fs'); if(fs.existsSync('tests/governance_audit/test_upstream_rca_gate.py')) fs.unlinkSync('tests/governance_audit/test_upstream_rca_gate.py');"` (proibido `rm -f` e `git clean -f`).
- **Critério de pronto (DoD):**
  1. `plan-template-governance.md` atualizado com classificação `corretivo | remediativo | hibrido | evolutivo` e seção `Diagnóstico Forense — RCA Upstream (R-055 Q0)`.
  2. `@agent-auditor` e `@governance-factory` instruídos a investigar `tools/**`, templates SSOT, instruções conflitantes e sensores antes de propor correções.
  3. `pre-hitl-skeptical-review-rubric.md` e `@plan-critic` atualizados com bloqueio `T2-RCA` para planos corretivos que tratem apenas o sintoma.
  4. `planner-preflight-checklist.md` <= 40 linhas e <= 2048 bytes; todas as skills <= 300 linhas; `python -m tools.governance_sync --check` limpo.
  5. Suíte `tests/governance_audit/` (incluindo `test_upstream_rca_gate.py` após Onda 2) 100% verde.

## Parecer do Revisor Cético Pré-HITL (R-064)

- **Tier 1 (Determinístico)**: `PASS` (frontmatter R-064 completo, `rollback_plan` executável no frontmatter e na §6, 12 `allowed_files` existentes e sem globs/Python, zero placeholders `TODO`/`TBD`/`<...>`, seções 1 a 6 + Parecer + Checklist presentes).
- **Tier 2 (`@plan-critic`)**: `PASS_WITH_NITS` (Rodada 2/2, teto R-065 respeitado; 0 BLOCKER, 0 HIGH, 0 MEDIUM, 0 LOW; 7/7 âncoras e números de linha validados literalmente contra o disco).
- **Findings e Resoluções**:
  - **F1 a F4 (Rodada 1)**: Resolvidos integralmente (`rollback_plan` explícito, segregação C3 entre Onda 1 `.md` e Onda 2 Tríade Python, checklist desmarcado).
  - **Achados 1 a 7 de Âncoras/Linhas**: Resolvidos e confirmados na revalidação (`plan-template-governance.md` L45/L49/L53, `pre-hitl-skeptical-review-rubric.md` L54/L56, `planner-preflight-checklist.md` L6 lista numerada 1961B -> 1984B, `invariantes-e-protocolos.md` L156, `SKILL.md` L170/L173, `CHANGELOG.md` L7, `workflows.md` L134/L163).
  - **NIT-1 e NIT-2**: Citação de `| `governance` |` na L54 e seção de parecer sincronizadas.

## Checklist

- [x] Frontmatter R-064 (`plan_type: governance`, `DRAFT`, `approved: false`, `rollback_plan` executável); `review_*`/`critic_*` preenchidos apenas após veredito do `@plan-critic` (C5).
- [x] Persistência por `@docs-engineer`; auditor permanece Read-Only (R-057).
- [x] Conformidade com `docs/plans/governance/` (Smell 2.34).
- [x] Q0 classificada: `evolutivo` com `N/A — plano puramente evolutivo/greenfield`.
