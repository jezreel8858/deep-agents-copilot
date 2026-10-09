"""
test_planning_doc_template_governance.py — Validação determinística de conformidade
dos templates de documentação de planejamento e implementação (R-064 / R-051 / R-055).

Valida:
1. Os 12 agents listados referenciam 'documentation-writing-patterns' em 'source_docs:'.
2. Os 9 agents de categoria IMPLEMENTAÇÃO mencionam 'related-planning-doc' e '{paralelizavel'/'responsavel}'.
3. Os 3 agents de categoria PLANEJAMENTO mencionam 'Alternativas Rejeitadas' ou 'related-plan'.
4. Nenhum agent de categoria IMPLEMENTAÇÃO ainda referencia notações legadas ('[ ] Nó N' ou '[S]'/'[P]').
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

ALL_TWELVE_AGENTS = [
    "tech-solution-architect",
    "requirements-analyst",
    "business-rules-extractor",
    "refactor-planner",
    "feature-planner",
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]

IMPLEMENTATION_AGENTS = [
    "refactor-planner",
    "feature-planner",
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]

PLANNING_AGENTS = [
    "tech-solution-architect",
    "requirements-analyst",
    "business-rules-extractor",
]


def _find_agent_file(agent_name: str) -> Path:
    matches = list(AGENTS_DIR.glob(f"**/{agent_name}.agent.md"))
    assert len(matches) == 1, f"Agente '{agent_name}' não encontrado unicamente sob .github/agents/: {matches}"
    return matches[0]


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    normalized = content.replace("\r\n", "\n")
    if not normalized.startswith("---"):
        return {}, normalized
    parts = normalized.split("\n---\n", 1)
    if len(parts) < 2:
        parts = re.split(r"\n---\s*\n", normalized, maxsplit=1)
    if len(parts) < 2:
        return {}, normalized
    try:
        data = yaml.safe_load(parts[0].lstrip("-")) or {}
        return data, parts[1]
    except Exception:
        return {}, normalized


@pytest.mark.parametrize("agent_name", ALL_TWELVE_AGENTS)
def test_twelve_agents_reference_documentation_writing_patterns(agent_name: str):
    """1. Os 12 agents listados referenciam 'documentation-writing-patterns' em source_docs:."""
    path = _find_agent_file(agent_name)
    content = path.read_text(encoding="utf-8")
    fm, _ = _parse_frontmatter(content)
    source_docs = fm.get("source_docs", [])
    has_pattern_doc = any("documentation-writing-patterns" in str(doc) for doc in source_docs)
    assert has_pattern_doc, (
        f"Agente '{agent_name}' ({path.relative_to(REPO_ROOT)}) não referencia "
        f"'documentation-writing-patterns' em frontmatter.source_docs: {source_docs}"
    )


@pytest.mark.parametrize("agent_name", IMPLEMENTATION_AGENTS)
def test_nine_implementation_agents_have_frontmatter_and_gfm_checklist(agent_name: str):
    """2. Os 9 agents de IMPLEMENTAÇÃO mencionam front-matter related-planning-doc e {paralelizavel/responsavel}."""
    path = _find_agent_file(agent_name)
    content = path.read_text(encoding="utf-8")
    assert "related-planning-doc" in content, (
        f"Agente de implementação '{agent_name}' não referencia 'related-planning-doc' em seu corpo/template."
    )
    assert "paralelizavel" in content, (
        f"Agente de implementação '{agent_name}' não referencia metadado 'paralelizavel' em seu corpo/template."
    )
    assert "responsavel" in content, (
        f"Agente de implementação '{agent_name}' não referencia metadado 'responsavel' em seu corpo/template."
    )


@pytest.mark.parametrize("agent_name", PLANNING_AGENTS)
def test_three_planning_agents_have_alternativas_rejeitadas_or_related_plan(agent_name: str):
    """3. Os 3 agents de PLANEJAMENTO mencionam a seção 'Alternativas Rejeitadas' ou front-matter related-plan."""
    path = _find_agent_file(agent_name)
    content = path.read_text(encoding="utf-8")
    has_alternativas = "Alternativas Rejeitadas" in content
    has_related_plan = "related-plan" in content
    assert has_alternativas or has_related_plan, (
        f"Agente de planejamento '{agent_name}' não menciona nem 'Alternativas Rejeitadas' nem 'related-plan'."
    )


@pytest.mark.parametrize("agent_name", IMPLEMENTATION_AGENTS)
def test_no_implementation_agent_references_legacy_checklist_notation(agent_name: str):
    """4. Nenhum agent de IMPLEMENTAÇÃO referencia notações antigas ([ ] Nó N ou [S]/[P]) como formato de checklist."""
    path = _find_agent_file(agent_name)
    content = path.read_text(encoding="utf-8")

    # Regex negativo para notação legada do refactor-planner: [ ] Nó N
    assert not re.search(r"\[\s*\]\s+Nó\s+\d", content), (
        f"Agente '{agent_name}' ainda contém referência à notação legada '[ ] Nó N'."
    )

    # Regex negativo para notações legadas do feature-planner: [S] ou [P] no checklist
    assert not re.search(r"\[[SP]\]\s+\d", content), (
        f"Agente '{agent_name}' ainda contém referência à notação legada '[S] N' ou '[P] N'."
    )
    assert not re.search(r"Marcação\s+`?\[[SP]\]`?/`?\[[SP]\]`?", content), (
        f"Agente '{agent_name}' ainda referencia a notação legada '[S]/[P]' no texto explicativo."
    )

ARCH_ADVISOR_AGENTS = [
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]


@pytest.mark.parametrize("agent_name", ARCH_ADVISOR_AGENTS)
def test_arch_advisors_reference_security_review_patterns(agent_name: str):
    """5. Os 7 specialist-arch-advisors referenciam 'security-review-patterns' em source_docs: (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    fm, _ = _parse_frontmatter(agent_content)
    source_docs = fm.get("source_docs", [])
    has_sec_review = any("security-review-patterns" in str(doc) for doc in source_docs)
    assert has_sec_review, (
        f"Arch advisor '{agent_name}' ({path.relative_to(REPO_ROOT)}) não referencia "
        f"'security-review-patterns' em frontmatter.source_docs: {source_docs}"
    )


@pytest.mark.parametrize("agent_name", IMPLEMENTATION_AGENTS)
def test_implementation_agents_have_defensive_checklist(agent_name: str):
    """6. Os 9 agents de IMPLEMENTAÇÃO contêm a seção 'Checklist Defensivo Pré-Code-Review' (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    assert "Checklist Defensivo" in agent_content, (
        f"Agente de implementação '{agent_name}' não contém 'Checklist Defensivo' em seu template/corpo."
    )


@pytest.mark.parametrize("agent_name", PLANNING_AGENTS)
def test_planning_agents_have_threat_modeling_shift_left(agent_name: str):
    """7. Os 3 agents de PLANEJAMENTO contêm a seção 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)' (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças" in agent_content, (
        f"Agente de planejamento '{agent_name}' não contém 'Modelagem de Ameaças' em seu template/corpo."
    )


def test_canonical_documentation_templates_contain_security_sections():
    """8. Templates canônicos em SKILL.md e READMEs de planos contêm as seções mandatórias de segurança (R-046 / R-064)."""
    skill_path = REPO_ROOT / ".github" / "skills" / "documentation-writing-patterns" / "SKILL.md"
    assert skill_path.exists(), "documentation-writing-patterns/SKILL.md deve existir"
    skill_content = skill_path.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in skill_content, (
        "documentation-writing-patterns/SKILL.md deve conter 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )
    assert "Checklist Defensivo Pré-Code-Review" in skill_content, (
        "documentation-writing-patterns/SKILL.md deve conter 'Checklist Defensivo Pré-Code-Review'"
    )

    plans_readme = REPO_ROOT / "docs" / "plans" / "README.md"
    assert plans_readme.exists(), "docs/plans/README.md deve existir"
    plans_content = plans_readme.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in plans_content, (
        "docs/plans/README.md deve conter a seção 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )

    impl_readme = REPO_ROOT / "docs" / "implementation-plans" / "README.md"
    assert impl_readme.exists(), "docs/implementation-plans/README.md deve existir"
    impl_content = impl_readme.read_text(encoding="utf-8")
    assert "Checklist Defensivo Pré-Code-Review" in impl_content, (
        "docs/implementation-plans/README.md deve conter a seção 'Checklist Defensivo Pré-Code-Review'"
    )


def test_plan_prompt_contains_defensive_sections_and_normalized_tags():
    """9. Prompt /plan contém referências a segurança Shift-Left, Checklist Defensivo e tags normalizadas (R-046 / R-051)."""
    prompt_path = REPO_ROOT / ".github" / "prompts" / "plan.prompt.md"
    assert prompt_path.exists(), ".github/prompts/plan.prompt.md deve existir"
    prompt_content = prompt_path.read_text(encoding="utf-8")

    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in prompt_content, (
        "plan.prompt.md deve mencionar 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )
    assert "Checklist Defensivo Pré-Code-Review" in prompt_content, (
        "plan.prompt.md deve mencionar 'Checklist Defensivo Pré-Code-Review'"
    )
    assert '{paralelizavel: bool, responsavel: "<agent>"}' in prompt_content, (
        "plan.prompt.md deve especificar notação de tag '{paralelizavel: bool, responsavel: "<agent>"}'"
    )

ARCH_ADVISOR_AGENTS = [
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]


@pytest.mark.parametrize("agent_name", ARCH_ADVISOR_AGENTS)
def test_arch_advisors_reference_security_review_patterns(agent_name: str):
    """5. Os 7 specialist-arch-advisors referenciam 'security-review-patterns' em source_docs: (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    fm, _ = _parse_frontmatter(agent_content)
    source_docs = fm.get("source_docs", [])
    has_sec_review = any("security-review-patterns" in str(doc) for doc in source_docs)
    assert has_sec_review, (
        f"Arch advisor '{agent_name}' ({path.relative_to(REPO_ROOT)}) não referencia "
        f"'security-review-patterns' em frontmatter.source_docs: {source_docs}"
    )


@pytest.mark.parametrize("agent_name", IMPLEMENTATION_AGENTS)
def test_implementation_agents_have_defensive_checklist(agent_name: str):
    """6. Os 9 agents de IMPLEMENTAÇÃO contêm a seção 'Checklist Defensivo Pré-Code-Review' (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    assert "Checklist Defensivo" in agent_content, (
        f"Agente de implementação '{agent_name}' não contém 'Checklist Defensivo' em seu template/corpo."
    )


@pytest.mark.parametrize("agent_name", PLANNING_AGENTS)
def test_planning_agents_have_threat_modeling_shift_left(agent_name: str):
    """7. Os 3 agents de PLANEJAMENTO contêm a seção 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)' (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças" in agent_content, (
        f"Agente de planejamento '{agent_name}' não contém 'Modelagem de Ameaças' em seu template/corpo."
    )


def test_canonical_documentation_templates_contain_security_sections():
    """8. Templates canônicos em SKILL.md e READMEs de planos contêm as seções mandatórias de segurança (R-046 / R-064)."""
    skill_path = REPO_ROOT / ".github" / "skills" / "documentation-writing-patterns" / "SKILL.md"
    assert skill_path.exists(), "documentation-writing-patterns/SKILL.md deve existir"
    skill_content = skill_path.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in skill_content, (
        "documentation-writing-patterns/SKILL.md deve conter 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )
    assert "Checklist Defensivo Pré-Code-Review" in skill_content, (
        "documentation-writing-patterns/SKILL.md deve conter 'Checklist Defensivo Pré-Code-Review'"
    )

    plans_readme = REPO_ROOT / "docs" / "plans" / "README.md"
    assert plans_readme.exists(), "docs/plans/README.md deve existir"
    plans_content = plans_readme.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in plans_content, (
        "docs/plans/README.md deve conter a seção 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )

    impl_readme = REPO_ROOT / "docs" / "implementation-plans" / "README.md"
    assert impl_readme.exists(), "docs/implementation-plans/README.md deve existir"
    impl_content = impl_readme.read_text(encoding="utf-8")
    assert "Checklist Defensivo Pré-Code-Review" in impl_content, (
        "docs/implementation-plans/README.md deve conter a seção 'Checklist Defensivo Pré-Code-Review'"
    )


def test_plan_prompt_contains_defensive_sections_and_normalized_tags():
    """9. Prompt /plan contém referências a segurança Shift-Left, Checklist Defensivo e tags normalizadas (R-046 / R-051)."""
    prompt_path = REPO_ROOT / ".github" / "prompts" / "plan.prompt.md"
    assert prompt_path.exists(), ".github/prompts/plan.prompt.md deve existir"
    prompt_content = prompt_path.read_text(encoding="utf-8")

    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in prompt_content, (
        "plan.prompt.md deve mencionar 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )
    assert "Checklist Defensivo Pré-Code-Review" in prompt_content, (
        "plan.prompt.md deve mencionar 'Checklist Defensivo Pré-Code-Review'"
    )
    assert '{paralelizavel: bool, responsavel: "<agent>"}' in prompt_content, (
        "plan.prompt.md deve especificar notação de tag '{paralelizavel: bool, responsavel: "<agent>"}'"
    )

ARCH_ADVISOR_AGENTS = [
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]


@pytest.mark.parametrize("agent_name", ARCH_ADVISOR_AGENTS)
def test_arch_advisors_reference_security_review_patterns(agent_name: str):
    """5. Os 7 specialist-arch-advisors referenciam 'security-review-patterns' em source_docs: (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    fm, _ = _parse_frontmatter(agent_content)
    source_docs = fm.get("source_docs", [])
    has_sec_review = any("security-review-patterns" in str(doc) for doc in source_docs)
    assert has_sec_review, (
        f"Arch advisor '{agent_name}' ({path.relative_to(REPO_ROOT)}) não referencia "
        f"'security-review-patterns' em frontmatter.source_docs: {source_docs}"
    )


@pytest.mark.parametrize("agent_name", IMPLEMENTATION_AGENTS)
def test_implementation_agents_have_defensive_checklist(agent_name: str):
    """6. Os 9 agents de IMPLEMENTAÇÃO contêm a seção 'Checklist Defensivo Pré-Code-Review' (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    assert "Checklist Defensivo" in agent_content, (
        f"Agente de implementação '{agent_name}' não contém 'Checklist Defensivo' em seu template/corpo."
    )


@pytest.mark.parametrize("agent_name", PLANNING_AGENTS)
def test_planning_agents_have_threat_modeling_shift_left(agent_name: str):
    """7. Os 3 agents de PLANEJAMENTO contêm a seção 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)' (R-046 / R-051)."""
    path = _find_agent_file(agent_name)
    agent_content = path.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças" in agent_content, (
        f"Agente de planejamento '{agent_name}' não contém 'Modelagem de Ameaças' em seu template/corpo."
    )


def test_canonical_documentation_templates_contain_security_sections():
    """8. Templates canônicos em SKILL.md e READMEs de planos contêm as seções mandatórias de segurança (R-046 / R-064)."""
    skill_path = REPO_ROOT / ".github" / "skills" / "documentation-writing-patterns" / "SKILL.md"
    assert skill_path.exists(), "documentation-writing-patterns/SKILL.md deve existir"
    skill_content = skill_path.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in skill_content, (
        "documentation-writing-patterns/SKILL.md deve conter 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )
    assert "Checklist Defensivo Pré-Code-Review" in skill_content, (
        "documentation-writing-patterns/SKILL.md deve conter 'Checklist Defensivo Pré-Code-Review'"
    )

    plans_readme = REPO_ROOT / "docs" / "plans" / "README.md"
    assert plans_readme.exists(), "docs/plans/README.md deve existir"
    plans_content = plans_readme.read_text(encoding="utf-8")
    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in plans_content, (
        "docs/plans/README.md deve conter a seção 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )

    impl_readme = REPO_ROOT / "docs" / "implementation-plans" / "README.md"
    assert impl_readme.exists(), "docs/implementation-plans/README.md deve existir"
    impl_content = impl_readme.read_text(encoding="utf-8")
    assert "Checklist Defensivo Pré-Code-Review" in impl_content, (
        "docs/implementation-plans/README.md deve conter a seção 'Checklist Defensivo Pré-Code-Review'"
    )


def test_plan_prompt_contains_defensive_sections_and_normalized_tags():
    """9. Prompt /plan contém referências a segurança Shift-Left, Checklist Defensivo e tags normalizadas (R-046 / R-051)."""
    prompt_path = REPO_ROOT / ".github" / "prompts" / "plan.prompt.md"
    assert prompt_path.exists(), ".github/prompts/plan.prompt.md deve existir"
    prompt_content = prompt_path.read_text(encoding="utf-8")

    assert "Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)" in prompt_content, (
        "plan.prompt.md deve mencionar 'Modelagem de Ameaças & Requisitos de Segurança (Shift-Left)'"
    )
    assert "Checklist Defensivo Pré-Code-Review" in prompt_content, (
        "plan.prompt.md deve mencionar 'Checklist Defensivo Pré-Code-Review'"
    )
    assert '{paralelizavel: bool, responsavel: "<agent>"}' in prompt_content, (
        "plan.prompt.md deve especificar notação de tag '{paralelizavel: bool, responsavel: "<agent>"}'"
    )


# ─────────────────────────────────────────────────────────────
# Emenda D (D5) — nomenclatura de planos em docs/implementation-plans/
# ─────────────────────────────────────────────────────────────

PLANS_DIR = REPO_ROOT / "docs" / "implementation-plans"
WORKFLOWS_DIR = AGENTS_DIR / "workflows"
PLAN_NAME_PATTERN = re.compile(r"^\d{8}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
# Convenção de prefixo de workflow vigente a partir desta data (planos anteriores são legado e só seguem o regex).
PLAN_WORKFLOW_PREFIX_SINCE = "20261008"


def _plan_files() -> list[Path]:
    return sorted(p for p in PLANS_DIR.glob("*.md") if p.name != "README.md")


def _workflow_slugs() -> set[str]:
    """Deriva slugs de workflow dos arquivos `workflow-<slug>.md` (sem hardcode)."""
    return {p.stem.removeprefix("workflow-") for p in WORKFLOWS_DIR.glob("workflow-*.md")}


def test_deve_seguir_padrao_de_nome_quando_plano_em_implementation_plans():
    """D5: todo plano (exceto README.md) segue ^\\d{8}-[a-z0-9]+(-[a-z0-9]+)*\\.md$."""
    plans = _plan_files()
    assert plans, "docs/implementation-plans/ deve conter planos"
    invalid = [p.name for p in plans if not PLAN_NAME_PATTERN.match(p.name)]
    assert not invalid, f"Planos fora do padrão AAAAMMDD-slug.md: {invalid}"


def test_deve_ter_prefixo_de_workflow_quando_plano_recente():
    """D5: planos a partir de PLAN_WORKFLOW_PREFIX_SINCE iniciam o slug com um workflow existente (derivado de workflows/)."""
    slugs = _workflow_slugs()
    assert slugs, "slugs de workflow devem ser derivados de .github/agents/workflows/"
    invalid = [
        p.name
        for p in _plan_files()
        if p.name[:8] >= PLAN_WORKFLOW_PREFIX_SINCE
        and not any(p.name[9:].startswith(slug + "-") for slug in slugs)
    ]
    assert not invalid, f"Planos recentes sem prefixo de workflow ({sorted(slugs)}): {invalid}"


def test_deve_rejeitar_nome_quando_fora_do_padrao():
    """D5: sanidade do regex — positivos e negativos (boundary de 8 dígitos, maiúsculas, hífen duplo)."""
    ok = ["20261008-feature-development-x.md", "20261008-a.md"]
    ruim = ["2026108-a.md", "202610080-a.md", "20261008-A.md", "20261008--a.md", "20261008-a-.md", "20261008-a_b.md", "20261008.md", "20261008-a.MD"]
    assert all(PLAN_NAME_PATTERN.match(n) for n in ok)
    assert not any(PLAN_NAME_PATTERN.match(n) for n in ruim)


def test_nao_deve_conter_identificador_proibido_quando_nome_de_plano():
    """D5: nenhum nome de plano contém identificador de projeto local (mensagem mascarada ID-LOCAL)."""
    from tests.governance_audit.test_local_project_isolation import get_forbidden_project_identifiers

    patterns = [
        re.compile(rf"(?<![a-zA-Z0-9]){re.escape(t)}(?![a-zA-Z0-9])", re.IGNORECASE)
        for t in get_forbidden_project_identifiers()
    ]
    leaks = [p.name for p in _plan_files() if any(pt.search(p.name) for pt in patterns)]
    assert not leaks, f"{len(leaks)} nome(s) de plano contêm projeto local proibido (ID-LOCAL, R-038/R-044)"
