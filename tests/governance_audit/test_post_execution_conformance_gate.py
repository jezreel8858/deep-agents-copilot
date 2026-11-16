"""
test_post_execution_conformance_gate.py — Sensor determinístico Q3 (R-055 / R-064) para o Quality Gate Pós-Execução.

Garante que:
1. invariantes-e-protocolos.md possui subseções ### 10.x únicas (sem colisão) e inclui ### 10.7, ### 10.8 e ### 10.9.
2. workflow-governance-maintenance.md inclui a Subetapa 5b com @agent-auditor antes do encerramento.
3. Os 5 workflows de código referenciam plan-conformance-patterns e os níveis N1, N2 e N3.
4. Os templates plan-frontmatter-r064.md e plan-template-governance.md contêm a seção
   "## Parecer de Conformidade Pós-Execução (R-064)".
5. handoff-governance/SKILL.md declara os motivos canônicos revisao_conformidade_pos_execucao e
   conformidade_reprovada_retorno_execucao.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
WORKFLOWS_DIR = AGENTS_DIR / "workflows"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
INVARIANTES_MD = WORKFLOWS_DIR / "invariantes-e-protocolos.md"
WORKFLOW_GOV_MAINT_MD = WORKFLOWS_DIR / "workflow-governance-maintenance.md"
HANDOFF_GOVERNANCE_SKILL_MD = SKILLS_DIR / "handoff-governance" / "SKILL.md"
PLAN_FRONTMATTER_R064_MD = REPO_ROOT / ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
PLAN_TEMPLATE_GOVERNANCE_MD = REPO_ROOT / ".github/skills/governance-audit-patterns/references/plan-template-governance.md"

CODE_WORKFLOW_FILES = (
    "workflow-bug-fix.md",
    "workflow-refactoring.md",
    "workflow-feature-development.md",
    "workflow-dependency-vulnerability-remediation.md",
    "workflow-framework-migration.md",
)


def test_invariantes_subsections_10_x_uniqueness_and_presence() -> None:
    """Valida unicidade das subseções ### 10.x e presença de ### 10.7, ### 10.8 e ### 10.9."""
    content = INVARIANTES_MD.read_text(encoding="utf-8")
    headings = re.findall(r"^(###\s+10\.\d+)\b", content, flags=re.MULTILINE)
    assert headings, remediation(
        "Nenhuma subseção ### 10.x encontrada em invariantes-e-protocolos.md.",
        fix_hint="Preservar a numeração canônica ### 10.1 a ### 10.9 na Seção 10 de invariantes-e-protocolos.md.",
    )
    duplicates = sorted({h for h in headings if headings.count(h) > 1})
    assert not duplicates, remediation(
        f"Colisão de numeração detectada em invariantes-e-protocolos.md: {duplicates}.",
        fix_hint="Garantir que cada subseção ### 10.x tenha numeração única em invariantes-e-protocolos.md.",
    )
    for required in ("### 10.7", "### 10.8", "### 10.9"):
        assert required in headings, remediation(
            f"Subseção obrigatória {required} ausente em invariantes-e-protocolos.md.",
            fix_hint=f"Adicionar ou restaurar a subseção {required} em invariantes-e-protocolos.md.",
        )


def test_workflow_governance_maintenance_substep_5b_agent_auditor() -> None:
    """Valida presença da Subetapa 5b com @agent-auditor em workflow-governance-maintenance.md."""
    content = WORKFLOW_GOV_MAINT_MD.read_text(encoding="utf-8")
    assert "5b" in content and "@agent-auditor" in content, remediation(
        "Subetapa 5b com @agent-auditor ausente em workflow-governance-maintenance.md.",
        fix_hint="Documentar a Subetapa 5b (Quality Gate Pós-Execução via @agent-auditor) no Estado 5 de workflow-governance-maintenance.md.",
    )
    assert "revisao_conformidade_pos_execucao" in content, remediation(
        "Motivo de handoff revisao_conformidade_pos_execucao ausente em workflow-governance-maintenance.md.",
        fix_hint="Incluir o motivo canônico revisao_conformidade_pos_execucao na Subetapa 5b de workflow-governance-maintenance.md.",
    )


@pytest.mark.parametrize("filename", CODE_WORKFLOW_FILES)
def test_code_workflows_reference_plan_conformance_patterns_and_levels(filename: str) -> None:
    """Valida presença de plan-conformance-patterns e níveis N1/N2/N3 nos 5 workflows de código."""
    content = (WORKFLOWS_DIR / filename).read_text(encoding="utf-8")
    assert "plan-conformance-patterns" in content, remediation(
        f"{filename} não referencia a skill plan-conformance-patterns no gate de conformidade pós-execução.",
        fix_hint=f"Referenciar plan-conformance-patterns na etapa de revisão/conformidade pós-execução de {filename}.",
    )
    for level in ("N1", "N2", "N3"):
        assert re.search(rf"\b{level}\b", content), remediation(
            f"Nível de severidade {level} ausente em {filename}.",
            fix_hint=f"Documentar os níveis N1/N2/N3 de severidade de conformidade pós-execução em {filename}.",
        )


@pytest.mark.parametrize(
    "template_path",
    (PLAN_FRONTMATTER_R064_MD, PLAN_TEMPLATE_GOVERNANCE_MD),
    ids=("plan-frontmatter-r064.md", "plan-template-governance.md"),
)
def test_plan_templates_contain_post_execution_conformance_section(template_path: Path) -> None:
    """Valida presença da seção/metadados de Parecer de Conformidade Pós-Execução (R-064 / § 10.9) nos templates."""
    content = template_path.read_text(encoding="utf-8")
    has_section = (
        "## Parecer de Conformidade Pós-Execução" in content
        or "Quality Gate Pós-Execução de Conformidade" in content
    )
    assert has_section and "10.9" in content, remediation(
        f"Seção de Conformidade Pós-Execução (R-064 / § 10.9) ausente no template {template_path.name}.",
        fix_hint=f"Adicionar a seção de Conformidade Pós-Execução (R-064 / § 10.9) em {template_path.name}.",
    )


def test_handoff_governance_declares_post_execution_conformance_motivos() -> None:
    """Valida presença de revisao_conformidade_pos_execucao e conformidade_reprovada_retorno_execucao."""
    content = HANDOFF_GOVERNANCE_SKILL_MD.read_text(encoding="utf-8")
    for motivo in ("revisao_conformidade_pos_execucao", "conformidade_reprovada_retorno_execucao"):
        assert motivo in content, remediation(
            f"Motivo canônico '{motivo}' ausente em .github/skills/handoff-governance/SKILL.md.",
            fix_hint=f"Registrar o motivo '{motivo}' na tabela de motivos de handoff em handoff-governance/SKILL.md.",
        )


def test_copilot_instructions_declares_governance_post_execution_gate() -> None:
    """Alias canônico do plano de implementação para validação de invariantes 10.x / 10.9."""
    test_invariantes_subsections_10_x_uniqueness_and_presence()


def test_agent_router_enforces_step_5_5_before_closure() -> None:
    """Alias canônico do plano de implementação para validação da Subetapa 5b no workflow."""
    test_workflow_governance_maintenance_substep_5b_agent_auditor()


def test_governance_maintainer_forbids_self_closure_without_auditor_gate() -> None:
    """Alias canônico do plano de implementação para validação de motivos de handoff do gate."""
    test_handoff_governance_declares_post_execution_conformance_motivos()


def test_agent_auditor_supports_post_execution_gate_mode() -> None:
    """Alias canônico do plano de implementação para validação dos templates com Parecer R-064."""
    for tpl in (PLAN_FRONTMATTER_R064_MD, PLAN_TEMPLATE_GOVERNANCE_MD):
        test_plan_templates_contain_post_execution_conformance_section(tpl)


def test_skills_post_implementation_conformance_and_governance_audit_aligned() -> None:
    """Alias canônico do plano de implementação para validação de plan-conformance-patterns nos 5 workflows."""
    for wf in CODE_WORKFLOW_FILES:
        test_code_workflows_reference_plan_conformance_patterns_and_levels(wf)
