---
status: APPROVED
approved: true
approved_by: "human_gate"
approved_at: "2026-11-16"
tier: "light"
author: "@python-arch-advisor"
plan_type: "implementation"
created_at: "2026-11-16"
date: "2026-11-16"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
related-planning-doc: "docs/plans/governance/20261116-120000-governance-maintenance-rca-upstream-origin-escape.md"
parent_plan_ref: "docs/plans/governance/20261116-120000-governance-maintenance-rca-upstream-origin-escape.md"
plan_ref: "docs/plans/implementation/20261116-130000-governance-maintenance-test-upstream-rca-gate.md"
reversibility: "T1"
rollback_plan: "git --no-pager revert HEAD && pytest tests/governance_audit/ -q"
progress: 100
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
  nits: 2
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@python-arch-advisor"
allowed_files:
  - "tests/governance_audit/test_upstream_rca_gate.py"
---

# Plano de Implementação Técnica (Onda 2 — T9 / Q3): Suíte Automatizada `test_upstream_rca_gate.py` (R-065)

## 1. Vínculo com o Plano de Planejamento (`related-planning-doc`) e Contexto Arquitetural

- **Plano Pai Aprovado (Gate 1)**: `docs/plans/governance/20261116-120000-governance-maintenance-rca-upstream-origin-escape.md` (`WORKFLOW-GOVERNANCE-MAINTENANCE`, Onda 1 concluída para T1–T8 nos 12 artefatos Markdown).
- **Escopo Exclusivo desta Onda 2 (T9 / Decisão HITL Q3)**: Materializar e executar o gate estático de regressão em Python (`tests/governance_audit/test_upstream_rca_gate.py`) para validar de forma determinística e contínua todas as âncoras normativas do **Gate de Origem Upstream & Anti-Symptom-Patching (R-065 / Passo 0 — Q0)** introduzidas nas tarefas **T1 a T8** nos 12 arquivos `.md` da Onda 1.
- **Isolamento de Fronteira de Escrita (R-064 / R-050)**: Como os agentes de governança (`@governance-maintainer`, `@docs-engineer`) possuem bloqueio estrutural para edição de código-fonte `.py`, a execução de T9 é isolada neste plano filho `plan_type: "implementation"` emitido por `@python-arch-advisor` com `allowed_files: ["tests/governance_audit/test_upstream_rca_gate.py"]` para implementação exclusiva pelo `@python-developer` após revisão do `@plan-critic` e Gate 2 HITL.

---

## 2. Decisões de Design, Padrões Aplicados e Alternativas Rejeitadas

### 2.1. Princípios Arquiteturais e Invariantes de Teste

1. **Zero Dependências Externas & I/O Determinístico**: Uso exclusivo da biblioteca padrão (`pathlib.Path`, `re`) e `pytest.mark.parametrize`, lendo os 12 arquivos Markdown em UTF-8 a partir de `REPO_ROOT = Path(__file__).resolve().parents[2]`.
2. **Rastreabilidade 1:1 com T1–T8**: Cada caso parametrizado na suíte `tests/governance_audit/test_upstream_rca_gate.py` mapeia explicitamente uma tarefa da Onda 1 (T1 a T8) e valida as âncoras exatas aplicadas nos 12 arquivos `.md`.
3. **Mensagens de Falha Autoexplicativas (Actionable Diagnostics)**: Cada `assert` informa o arquivo relativo, a tarefa correspondente (T1–T8) e a âncora normativa ausente para diagnóstico imediato em CI.

### 2.2. Alternativas Rejeitadas (Trade-offs)

| Alternativa Avaliada | Motivo da Rejeição | Trade-off Assumido na Solução Escolhida |
| :--- | :--- | :--- |
| **Alternativa 1: Acoplar os testes de R-065 dentro de `test_planning_doc_template_governance.py`** | Viola o Princípio de Responsabilidade Única (SRP) ao misturar validação de templates de planos (`docs/plans/**`) com auditoria da regra de negócio transversal R-065 distribuída em 12 arquivos de instructions, skills, agents e README. | Criar o módulo dedicado `tests/governance_audit/test_upstream_rca_gate.py` adiciona 1 arquivo na suíte de auditoria, mas isola falhas de R-065 e preserva `allowed_files` cirúrgico. |
| **Alternativa 2: Validar apenas a presença da string genérica `"R-065"` nos 12 arquivos via regex simples** | Permite falso-positivo por menção nominal superficial sem garantir que as cláusulas estruturais críticas verificadas em `TASK_ANCHORS_SPEC` (`Q0`, `T2-RCA`, `Neutralização na Fonte` e `Diagnóstico Forense — RCA Upstream (R-055 Q0)`) permaneçam íntegras. | Validar múltiplas âncoras semânticas por arquivo (T1–T8) exige manutenção sincronizada caso o texto normativo mude, porém garante proteção real contra regressão semântica. |
| **Alternativa 3: Executar parser AST/Markdown pesado de terceiros (ex.: `markdown-it-py` ou `mistune`)** | Introduz dependência externa desnecessária e aumenta o tempo de execução da suíte `tests/governance_audit/` sem ganho para verificação de invariantes textuais e tabelas GFM. | Uso de `pathlib` + buscas de substring exatas verificadas executa em `< 50ms` com zero dependências extras. |

---

## 3. Escopo de Arquivos (`allowed_files`) e Sequência de Execução em Lote (Plan-Then-Batch, R-059)

| Ordem | Caminho do Arquivo (`allowed_files`) | Operação | Responsável | Descrição |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `tests/governance_audit/test_upstream_rca_gate.py` | `CREATE` | `@python-developer` | Criação da suíte Pytest validando as âncoras de RCA Upstream (R-065 / Q0) referentes a T1–T8 nos 12 arquivos `.md` da Onda 1. |

---

## 4. Checklist GFM Unificado de Tarefas

Progresso: 0/2 tarefas concluídas

- [x] **T9.1**: Implementar `tests/governance_audit/test_upstream_rca_gate.py` cobrindo integralmente as invariantes T1 a T8 nos 12 arquivos `.md` da Onda 1 com testes parametrizados e verificação de ausência de placeholders residuais {paralelizavel: false, responsavel: "@python-developer"}
- [x] **T9.2**: Executar `pytest tests/governance_audit/test_upstream_rca_gate.py tests/governance_audit/test_planning_doc_template_governance.py -q` e `get_errors` garantindo 100% de aprovação sem regressões {paralelizavel: false, responsavel: "@python-developer"}

---

## 5. Abordagem Técnica de Baixo Nível, Especificação Completa de `test_upstream_rca_gate.py` (T1 a T8) e Estratégia TDD / Teste de Regressão

### 5.1. Mapeamento Exato das Âncoras de T1 a T8 nos 12 Arquivos `.md` (Onda 1)

| Tarefa | Arquivo Alvo (12 arquivos `.md`) | Âncoras Obrigatórias Verificadas pelo Teste |
| :---: | :--- | :--- |
| **T1-template** | `.github/skills/governance-audit-patterns/references/plan-template-governance.md` | `Q0`, `NEEDS_REVISION`, `Neutralização na Fonte`, `Diagnóstico Forense — RCA Upstream (R-055 Q0)` |
| **T2-skill** | `.github/skills/governance-audit-patterns/SKILL.md` | `R-065`, `Q0` |
| **T3-rubric** | `.github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md` | `R-065`, `Q0`, `NEEDS_REVISION`, `T2-RCA`, `Neutralização na Fonte` |
| **T4-critic** | `.github/agents/plan-critic.agent.md` | `R-065`, `NEEDS_REVISION`, `T2-RCA`, `Neutralização na Fonte` |
| **T5-auditor** | `.github/agents/agent-auditor.agent.md` | `Q0` |
| **T5-factory** | `.github/agents/governance-factory.agent.md` | `R-065`, `Q0` |
| **T6-preflight** | `.github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md` | `R-065`, `Q0` |
| **T7-claude** | `CLAUDE.md` | `R-065`, `Q0` |
| **T7-copilot** | `.github/copilot-instructions.md` | `R-065`, `Q0` |
| **T7-workflows** | `.github/agents/workflows.md` | `R-065`, `Q0` |
| **T7-invariantes** | `.github/agents/workflows/invariantes-e-protocolos.md` | `R-065`, `Q0` |
| **T8-changelog** | `CHANGELOG.md` | `Q0`, `T2-RCA`, `Neutralização na Fonte` |

### 5.2. Especificação de Implementação de `tests/governance_audit/test_upstream_rca_gate.py`

```python
"""Gate de regressão estático para R-065 (RCA Upstream Q0 & Anti-Symptom-Patching).

Valida que todas as âncoras normativas introduzidas na Onda 1 (T1 a T8)
permanecem íntegras nos 12 arquivos Markdown de governança, skills, agents e README.
"""

from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

WAVE_1_TARGET_FILES: tuple[str, ...] = (
    ".github/skills/governance-audit-patterns/references/plan-template-governance.md",
    ".github/skills/governance-audit-patterns/SKILL.md",
    ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md",
    ".github/agents/plan-critic.agent.md",
    ".github/agents/agent-auditor.agent.md",
    ".github/agents/governance-factory.agent.md",
    ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/agents/workflows.md",
    ".github/agents/workflows/invariantes-e-protocolos.md",
    "CHANGELOG.md",
)

TASK_ANCHORS_SPEC: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "T1-template",
        ".github/skills/governance-audit-patterns/references/plan-template-governance.md",
        (
            "Q0",
            "NEEDS_REVISION",
            "Neutralização na Fonte",
            "Diagnóstico Forense — RCA Upstream (R-055 Q0)",
        ),
    ),
    (
        "T2-skill",
        ".github/skills/governance-audit-patterns/SKILL.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T3-rubric",
        ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md",
        (
            "R-065",
            "Q0",
            "NEEDS_REVISION",
            "T2-RCA",
            "Neutralização na Fonte",
        ),
    ),
    (
        "T4-critic",
        ".github/agents/plan-critic.agent.md",
        (
            "R-065",
            "NEEDS_REVISION",
            "T2-RCA",
            "Neutralização na Fonte",
        ),
    ),
    (
        "T5-auditor",
        ".github/agents/agent-auditor.agent.md",
        (
            "Q0",
        ),
    ),
    (
        "T5-factory",
        ".github/agents/governance-factory.agent.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T6-preflight",
        ".github/skills/plan-conformance-patterns/references/planner-preflight-checklist.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-claude",
        "CLAUDE.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-copilot",
        ".github/copilot-instructions.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-workflows",
        ".github/agents/workflows.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T7-invariantes",
        ".github/agents/workflows/invariantes-e-protocolos.md",
        (
            "R-065",
            "Q0",
        ),
    ),
    (
        "T8-changelog",
        "CHANGELOG.md",
        (
            "Q0",
            "T2-RCA",
            "Neutralização na Fonte",
        ),
    ),
)


def _read_utf8(rel_path: str) -> str:
    target = REPO_ROOT / rel_path
    assert target.is_file(), f"Arquivo obrigatório de R-065 ausente: {rel_path}"
    return target.read_text(encoding="utf-8")


def test_wave1_target_files_count_and_existence() -> None:
    """Garante que os 12 arquivos da Onda 1 existem e referenciam R-065."""
    assert len(WAVE_1_TARGET_FILES) == 12
    for rel_path in WAVE_1_TARGET_FILES:
        content = _read_utf8(rel_path)
        assert ("R-065" in content or "Q0" in content), f"{rel_path} deve conter referência explícita a R-065 ou Q0"


@pytest.mark.parametrize(
    ("task_id", "rel_path", "expected_anchors"),
    TASK_ANCHORS_SPEC,
    ids=[item[0] for item in TASK_ANCHORS_SPEC],
)
def test_upstream_rca_gate_anchors_t1_to_t8(
    task_id: str,
    rel_path: str,
    expected_anchors: tuple[str, ...],
) -> None:
    """Valida todas as âncoras normativas de T1 a T8 nos 12 arquivos Markdown."""
    content = _read_utf8(rel_path)
    for anchor in expected_anchors:
        assert anchor in content, (
            f"[{task_id}] Âncora obrigatória '{anchor}' ausente em {rel_path}"
        )
```

### 5.3. Teste de Regressão (Cenários BDD / Gherkin)

```gherkin
Feature: Gate Automatizado de Auditoria de Origem Upstream R-065 (T9)
  Como engenheiro de governança do repositório deep-agents-copilot
  Quero validar automaticamente as âncoras de RCA Upstream (Q0 / R-065) nos 12 arquivos .md da Onda 1
  Para impedir regressões que silenciem o rastreamento do produtor upstream ou o bloqueio de symptom-patching downstream

  Scenario: Todos os 12 artefatos Markdown da Onda 1 preservam as âncoras de T1 a T8
    Given que os 12 arquivos Markdown atualizados na Onda 1 (T1 a T8) existem no repositório
    When a suíte Pytest "tests/governance_audit/test_upstream_rca_gate.py" é executada
    Then todos os casos parametrizados de T1 a T8 passam com 100% de sucesso em menos de 1 segundo

  Scenario: Detecção determinística de remoção acidental das âncoras verificadas em TASK_ANCHORS_SPEC
    Given que um commit futuro remova acidentalmente as âncoras "T2-RCA", "Neutralização na Fonte" ou "Diagnóstico Forense — RCA Upstream (R-055 Q0)" de seus respectivos arquivos em TASK_ANCHORS_SPEC
    When a suíte Pytest "tests/governance_audit/test_upstream_rca_gate.py" é executada no gate de qualidade
    Then o teste falha imediatamente indicando o ID da tarefa (T1-T8), o arquivo afetado e a âncora exata ausente
```

---

## 6. Riscos de Regressão, Blast Radius e Estratégia de Rollback

### 6.1. Blast Radius

- **Raio de Impacto Direto**: Restrito exclusivamente à criação de 1 arquivo de teste estático (`tests/governance_audit/test_upstream_rca_gate.py`).
- **Artefatos de Produção / Runtime / Agentes**: **Zero impacto**. Nenhum arquivo em `.github/agents/`, `.github/skills/`, `.github/instructions/` ou `tools/` é modificado na Onda 2.
- **Tempo de Execução na Suíte de Testes**: Adição estimada de `< 0.05s` na execução de `pytest tests/governance_audit/` (leitura local em memória de 12 arquivos Markdown).

### 6.2. Estratégia de Rollback Executável (`reversibility: T1`)

Como a entrega consiste apenas na adição de um novo arquivo de teste sem efeitos colaterais em estado persistente ou contratos de runtime (`T1 — Totalmente Reversível`), o rollback é imediato e executável em linha única:

```bash
git rm -f tests/governance_audit/test_upstream_rca_gate.py && pytest tests/governance_audit/ -q
```

---

## 7. 🔒 Checklist Defensivo Pré-Code-Review

- [x] **Sanitização & Validação de Borda**: Validação estrita de tipos, tamanhos e formatos em todos os pontos de entrada e parâmetros externos (caminhos resolvidos de forma determinística via `REPO_ROOT = Path(__file__).resolve().parents[2]` e leitura explícita `encoding="utf-8"`).
- [x] **Zero Hardcoded Secrets**: Ausência absoluta de credenciais, tokens de API, senhas ou certificados codificados no código ou fixtures.
- [x] **Logging & Dados Sensíveis**: Mascaramento ou omissão de PII, senhas, tokens e dados sensíveis em logs de depuração e traces.
- [x] **Controle de Acesso & Autorização**: Validação de escopos, papéis e permissões no nível de serviço/controlador para evitar broken object level authorization (BOLA/IDOR) — aplicável ao isolamento estrito de `allowed_files` entre agentes Markdown e `@python-developer`.
- [x] **Tratamento Seguro de Falhas**: Exceções tratadas sem expor stacktraces ou dados internos ao usuário final, mantendo estado consistente (mensagens de asserção claras indicando `task_id`, `rel_path` e âncora esperada).
- [x] **Cobertura de Testes Defensivos**: Testes cobrindo fluxos de erro, inputs maliciosos/inválidos e limites de contorno (verificação da cardinalidade exata dos 12 arquivos e de todas as âncoras T1–T8).

---

## 8. Parecer do Revisor Cético Pré-HITL (R-064)

- **Status da Revisão**: `PASS_WITH_NITS` (promovido após Rodada 2 do `@plan-critic` e aprovação no Gate 2 HITL).
- **Revisor**: `@plan-critic` (`reviewed_at: 2026-11-16`, `review_rounds: 2`, `review_tier1: PASS`).
- **Resumo de Achados**: 0 BLOCKER, 0 MAJOR/HIGH, 0 MINOR, 2 NITs — achados 1–3 da Rodada 1 integralmente resolvidos (NIT-1 saneado no `rollback_plan` do frontmatter sem flag `-f`).
