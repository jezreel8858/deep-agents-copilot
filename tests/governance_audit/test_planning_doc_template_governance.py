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
