"""
test_agent_guardrails_regression.py — Suíte Regressiva Determinística de Guardrails por Agency Score (0–3) e OWASP ASI01..ASI10:2026.

Valida que 100% dos agents em .github/agents/**/*.agent.md (63 agents):
1. São classificados de forma determinística, exaustiva e sem sobreposição em exatamente 1 Agency Score (0, 1, 2 ou 3);
2. Cumprem os invariantes de ferramentas (tools:) e seções de guardrails obrigatórios do seu Agency Score;
3. Mantêm integridade referencial com .github/skills/agent-safety-guardrails/references/agency-score-matrix.md e teto R-066 (<= 300 linhas).
"""

from pathlib import Path
import re
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = BASE_DIR / ".github" / "agents"
SKILLS_DIR = BASE_DIR / ".github" / "skills"
MATRIX_PATH = SKILLS_DIR / "agent-safety-guardrails" / "references" / "agency-score-matrix.md"

SCORE_0_AGENTS = [
    "adr-sentinel",
    "agent-auditor",
    "angular-arch-advisor",
    "compliance-guardrails",
    "database-arch-advisor",
    "devops-engineer",
    "ejb-arch-advisor",
    "feature-planner",
    "plan-critic",
    "prompt-structuring",
    "python-arch-advisor",
    "react-arch-advisor",
    "repo-hygiene-auditor",
    "requirements-analyst",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "test-strategy"
]

SCORE_1_AGENTS = [
    "agent-router",
    "database-router",
    "ejb-router",
    "python-router",
    "spring-boot-router",
    "spring-reactive-router",
    "struts-router",
    "angular-router",
    "react-router"
]

SCORE_2_AGENTS = [
    "deep-search"
]

SCORE_3_AGENTS = [
    "adapter-generator",
    "angular-developer",
    "angular-test-engineer",
    "binding-initializer",
    "bug-triage",
    "business-rules-extractor",
    "code-review",
    "code-style-enforcer",
    "codegraph-engine",
    "database-specialist",
    "ddd-bounded-context-mapper",
    "debugger",
    "docs-engineer",
    "ejb-developer",
    "ejb-test-engineer",
    "governance-factory",
    "governance-maintainer",
    "informix-database-specialist",
    "oracle-database-specialist",
    "performance-agent",
    "pr-gatekeeper",
    "python-developer",
    "python-test-engineer",
    "react-developer",
    "react-test-engineer",
    "refactor-planner",
    "runtime-verifier",
    "security-reviewer",
    "spring-boot-developer",
    "spring-boot-test-engineer",
    "spring-reactive-developer",
    "spring-reactive-test-engineer",
    "struts-developer",
    "struts-test-engineer",
    "tech-solution-architect"
]

DIRECT_EDIT_TOOLS = {
    "replace_string_in_file",
    "insert_edit_into_file",
    "create_file",
    "edit",
}


def _extract_tools(content: str) -> list[str]:
    match = re.search(r"^tools:\s*(\[.*?\])", content, re.MULTILINE)
    if not match:
        return []
    return re.findall(r"""['"]([^'"]+)['"]""", match.group(1))


@pytest.fixture(scope="session")
def all_agents() -> dict[str, Path]:
    files = sorted(AGENTS_DIR.rglob("*.agent.md"))
    assert len(files) >= 63, f"Esperados pelo menos 63 agents, encontrados {len(files)}"
    return {f.stem.replace(".agent", ""): f for f in files}


def test_exhaustive_and_mutually_exclusive_agency_score_classification(all_agents):
    """Garante cobertura de 100% do catálogo em exatamente um Agency Score (0, 1, 2 ou 3) sem órfãos."""
    s0, s1, s2, s3 = set(SCORE_0_AGENTS), set(SCORE_1_AGENTS), set(SCORE_2_AGENTS), set(SCORE_3_AGENTS)
    assert len(s0) == 18, f"Score 0 deve conter 18 agents, tem {len(s0)}"
    assert len(s1) == 9, f"Score 1 deve conter 9 routers, tem {len(s1)}"
    assert len(s2) == 1, f"Score 2 deve conter 1 retriever (deep-search), tem {len(s2)}"
    assert len(s3) == 35, f"Score 3 deve conter 35 executores, tem {len(s3)}"

    # Disjunção mútua
    assert s0.isdisjoint(s1) and s0.isdisjoint(s2) and s0.isdisjoint(s3)
    assert s1.isdisjoint(s2) and s1.isdisjoint(s3)
    assert s2.isdisjoint(s3)

    classified = s0 | s1 | s2 | s3
    catalog = set(all_agents.keys())
    orphans = catalog - classified
    missing = classified - catalog
    assert not orphans, f"Agents órfãos sem Agency Score: {sorted(orphans)}"
    assert not missing, f"Agents listados no Score mas ausentes do disco: {sorted(missing)}"


def test_score_0_read_only_guardrails(all_agents):
    """Score 0 (Read-Only): zero tools de edição direta e presença de Escopo/Não-Escopo e restrições ❌."""
    violations = []
    for name in SCORE_0_AGENTS:
        content = all_agents[name].read_text(encoding="utf-8")
        tools = set(_extract_tools(content))
        forbidden = tools & DIRECT_EDIT_TOOLS
        if forbidden:
            violations.append(f"{name}: possui tools de edição proibidas em Score 0: {sorted(forbidden)}")
        if "ESCOPO" not in content.upper():
            violations.append(f"{name}: ausente seção de ESCOPO / NÃO-ESCOPO")
        if "❌" not in content:
            violations.append(f"{name}: ausente restrição negativa explícita (❌)")
    assert not violations, "Violações em Score 0:\n" + "\n".join(violations)


def test_score_1_router_guardrails(all_agents):
    """Score 1 (Routers): zero tools de edição, presença de CLAUSE_OTEL_PASSTHROUGH e delegação plana."""
    violations = []
    for name in SCORE_1_AGENTS:
        content = all_agents[name].read_text(encoding="utf-8")
        tools = set(_extract_tools(content))
        forbidden = tools & DIRECT_EDIT_TOOLS
        if forbidden:
            violations.append(f"{name}: router possui tools de edição: {sorted(forbidden)}")
        if "CLAUSE_OTEL_PASSTHROUGH" not in content:
            violations.append(f"{name}: ausente CLAUSE_OTEL_PASSTHROUGH")
        if "❌" not in content:
            violations.append(f"{name}: ausente restrições negativas (❌) de não-execução direta")
        if name == "agent-router" and "context-mode/ctx_execute" in tools:
            violations.append("agent-router: não deve possuir context-mode/ctx_execute no frontmatter (R-054)")
    assert not violations, "Violações em Score 1:\n" + "\n".join(violations)


def test_score_2_retriever_web_guardrails(all_agents):
    """Score 2 (deep-search): Gather-only (ctx_batch sem ctx_execute) e guardrails OWASP ASI01/ASI06 (dado inerte + read-only)."""
    content = all_agents["deep-search"].read_text(encoding="utf-8")
    tools = set(_extract_tools(content))
    assert "context-mode/ctx_batch" in tools, "deep-search deve possuir context-mode/ctx_batch"
    assert "context-mode/ctx_execute" not in tools, "deep-search NÃO deve possuir context-mode/ctx_execute"
    assert not (tools & DIRECT_EDIT_TOOLS), f"deep-search não deve ter tools de edição: {tools & DIRECT_EDIT_TOOLS}"
    assert "ASI01" in content and "ASI06" in content, "deep-search deve referenciar OWASP ASI01 e ASI06"
    assert "dado inerte" in content.lower(), "deep-search deve exigir tratamento de conteúdo externo como dado inerte"
    assert "read-only" in content.lower(), "deep-search deve explicitar restrição read-only"


def test_score_3_executor_guardrails(all_agents):
    """Score 3 (Executores): presença de <execution_protocol> (R-059/R-060) e seção de Escopo/Não-Escopo com ❌."""
    violations = []
    for name in SCORE_3_AGENTS:
        content = all_agents[name].read_text(encoding="utf-8")
        if "<execution_protocol>" not in content or "</execution_protocol>" not in content:
            violations.append(f"{name}: ausente bloco <execution_protocol>")
        if "R-059" not in content or "R-060" not in content:
            violations.append(f"{name}: ausente referência a R-059/R-060 no protocolo de execução")
        if "ESCOPO" not in content.upper() or "❌" not in content:
            violations.append(f"{name}: ausente seção de ESCOPO/NÃO-ESCOPO com restrições ❌")
    assert not violations, "Violações em Score 3:\n" + "\n".join(violations)


def test_agency_score_matrix_and_cross_references_and_r066_budget():
    """Valida a matriz canônica agency-score-matrix.md, referências cruzadas e teto R-066 (<= 300 linhas)."""
    assert MATRIX_PATH.exists(), f"Matriz não encontrada: {MATRIX_PATH}"
    matrix_txt = MATRIX_PATH.read_text(encoding="utf-8")
    for score_label in ("Score 0", "Score 1", "Score 2", "Score 3"):
        assert score_label in matrix_txt, f"{score_label} ausente em agency-score-matrix.md"
    for asi in ("ASI01", "ASI02", "ASI03", "ASI04", "ASI05", "ASI06", "ASI07", "ASI08", "ASI09", "ASI10"):
        assert asi in matrix_txt, f"{asi} ausente em agency-score-matrix.md"

    # R-066 budget (<= 300 linhas) + referência à matriz nas skills normativas
    for skill_rel in ("agent-safety-guardrails/SKILL.md", "governance-audit-patterns/SKILL.md"):
        skill_path = SKILLS_DIR / skill_rel
        skill_txt = skill_path.read_text(encoding="utf-8")
        line_count = len(skill_txt.splitlines())
        assert line_count <= 300, f"{skill_rel} excedeu o teto R-066 de 300 linhas: {line_count}"
        assert "agency-score-matrix.md" in skill_txt, f"{skill_rel} deve referenciar agency-score-matrix.md"

    # Referências nos agents de governança e templates
    must_reference = [
        AGENTS_DIR / "agent-auditor.agent.md",
        AGENTS_DIR / "governance-factory.agent.md",
        AGENTS_DIR / "deep-search.agent.md",
        AGENTS_DIR / "templates" / "agent-template.md",
        AGENTS_DIR / "templates" / "research-agent.md",
    ]
    for path_item in must_reference:
        txt = path_item.read_text(encoding="utf-8")
        assert "agency-score-matrix.md" in txt, f"{path_item.name} deve referenciar agency-score-matrix.md"
