"""
test_pre_hitl_skeptical_plan_gate.py — Validação determinística do Quality Gate Universal de
Revisão Cética Pré-HITL (R-064 / ADR-0014 / R-067).

Valida: agent @plan-critic (read-only, Two-Tier, R-065, ESCALATED_HITL, guardrails R-067),
registro em catalog.yaml e routing-graph.yaml, rubrica modular (§ 1 a § 14), ADR-0014,
metadados em plan-frontmatter-r064.md, seção de parecer nos templates especializados e o
validador determinístico Tier 1 sobre os planos de governança.
"""
from __future__ import annotations

import glob
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT = REPO_ROOT / ".github/agents/plan-critic.agent.md"
CATALOG = REPO_ROOT / ".github/agents/catalog.yaml"
ROUTING = REPO_ROOT / ".github/agents/routing-graph.yaml"
RUBRIC = REPO_ROOT / ".github/skills/plan-conformance-patterns/references/pre-hitl-skeptical-review-rubric.md"
FRONTMATTER_REF = REPO_ROOT / ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md"
ADR = REPO_ROOT / "docs/adr/0014-quality-gate-revisor-cetico-universal-pre-hitl-r064.md"
SOURCE_PLAN = REPO_ROOT / "docs/plans/governance/20261114-120000-revisor-cetico-universal-pre-hitl-r064.md"
R067_PLAN = REPO_ROOT / "docs/plans/governance/20261114-143000-evolucao-skills-guardrails-plan-critic-r067.md"

PARECER_HEADING = "Parecer do Revisor Cético Pré-HITL (R-064)"
CATEGORIES = ["feature", "refactor", "architecture", "implementation",
              "test-strategy", "bug-triage", "requirements", "governance"]
R067_SKILLS = [
    "agent-safety-guardrails",
    "security-review-patterns",
    "code-review-patterns",
    "confidence-fallback-policy",
    "governance-audit-patterns",
]
R067_GUARDRAIL_TOKENS = [
    "Anti-Verbosity",
    "Anti-Formatting",
    "Anti-Anchoring",
    "Anti-Rubber-Stamping",
    "Exhaustive Round-1 Scan",
    "Pre-Mortem",
    "Chain-of-Verification",
    "ASI01",
    "ASI02",
    "ASI08",
    "ASI09",
]
# A categoria 'architecture' reutiliza o template plan-template-feature.md (7 arquivos distintos).
TEMPLATES = [
    ".github/skills/task-decomposition-patterns/references/plan-template-feature.md",
    ".github/skills/refactoring-planning-patterns/references/plan-template-refactor.md",
    ".github/skills/requirements-engineering-patterns/references/plan-template-requirements.md",
    ".github/skills/test-coverage-governance/references/plan-template-test-strategy.md",
    ".github/skills/specialist-hybrid-advisory-implementation-patterns/references/plan-template-implementation.md",
    ".github/skills/code-tracing/references/plan-template-bug-triage.md",
    ".github/skills/governance-audit-patterns/references/plan-template-governance.md",
]
FORBIDDEN_TOOLS = {"create_file", "replace_string_in_file", "insert_edit_into_file",
                   "run_in_terminal", "context-mode/ctx_execute"}
PLAN_NAME_RE = re.compile(r"^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
COMMON_FIELDS = ["status", "approved", "author", "plan_type", "created_at",
                 "related-planning-doc", "allowed_files"]
IMPLEMENTATION_FIELDS = ["tier", "plan_ref", "rollback_plan"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    assert m, "frontmatter YAML ausente"
    return yaml.safe_load(m.group(1)) or {}


# ---------------------------------------------------------------- Tier 1 (determinístico)
def _strip_code(text: str) -> str:
    text = re.sub(r"~~~.*?~~~|`{3}.*?`{3}", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


def tier1_validate(plan_path: Path, repo_root: Path = REPO_ROOT) -> list[str]:
    """Validador determinístico Tier 1 (0 tokens LLM). Retorna lista de violações."""
    violations: list[str] = []
    if not PLAN_NAME_RE.match(plan_path.name):
        violations.append(f"T1-1 nomenclatura inválida: {plan_path.name}")
    text = _read(plan_path)
    try:
        fm = _frontmatter(text)
    except AssertionError:
        return violations + ["T1-2 frontmatter ausente"]
    for field in COMMON_FIELDS:
        if field not in fm:
            violations.append(f"T1-2 campo ausente: {field}")
    pair = (fm.get("status"), fm.get("approved"))
    if pair not in {("DRAFT", False), ("APPROVED", True)}:
        violations.append(f"T1-2 status/approved inconsistentes: {pair}")
    if fm.get("plan_type") != plan_path.parent.name:
        violations.append(f"T1-3 plan_type={fm.get('plan_type')} != pasta {plan_path.parent.name}")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(fm.get("created_at", ""))):
        violations.append("T1-2 created_at fora do formato ISO")
    if fm.get("plan_type") == "implementation":
        violations += [f"T1-4 campo ausente: {f}" for f in IMPLEMENTATION_FIELDS if f not in fm]
    for entry in fm.get("allowed_files") or []:
        if not (glob.glob(str(repo_root / entry), recursive=True) or (repo_root / entry).exists()):
            violations.append(f"T1-5 allowed_files sem grounding físico: {entry}")
    if not re.search(r"^#\s+\S", text, re.MULTILINE):
        violations.append("T1-6 H1 ausente")
    body = _strip_code(text)
    for pat in (r"\bTODO\b", r"\bTBD\b", r"<\.\.\.>"):
        if re.search(pat, body):
            violations.append(f"T1-7 placeholder proibido: {pat}")
    if any(line.strip() == "..." for line in body.splitlines()):
        violations.append("T1-7 placeholder '...' isolado")
    return violations


# ---------------------------------------------------------------- Agent @plan-critic
def test_plan_critic_agent_exists_and_is_read_only():
    assert AGENT.is_file(), "plan-critic.agent.md ausente"
    fm = _frontmatter(_read(AGENT))
    assert fm["name"] == "plan-critic"
    tools = set(fm["tools"])
    assert not (tools & FORBIDDEN_TOOLS), f"tools mutativas/terminal proibidas: {tools & FORBIDDEN_TOOLS}"
    assert {"run_subagent", "context-mode/ctx_batch", "ask_questions"} <= tools
    source_docs = set(fm.get("source_docs") or [])
    for skill in R067_SKILLS:
        expected_doc = f".github/skills/{skill}/SKILL.md"
        assert expected_doc in source_docs, f"skill ausente em source_docs do agent: {expected_doc}"


@pytest.mark.parametrize("token", [
    "# Perfil Operacional", "Agente Ativo: plan-critic", "Read-Only", "R-057", "Two-Tier",
    "Tier 1", "Tier 2", "Context Firewall", "R-043", "R-065", "ESCALATED_HITL",
    "Noise Budget", "Verify Before Criticize", "UNKNOWN", "Fast-Pass", "BLOCKER", "HIGH",
    "Dupla Lente", "Gate 1", "Gate 2", "@agent-router", "@docs-engineer", "@governance-maintainer",
    "pre-hitl-skeptical-review-rubric.md",
] + R067_GUARDRAIL_TOKENS)
def test_plan_critic_body_contract(token: str):
    assert token in _read(AGENT), f"token ausente no agent: {token}"


def test_plan_critic_covers_eight_categories():
    text = _read(AGENT)
    for cat in CATEGORIES:
        assert cat in text, f"categoria ausente no agent: {cat}"


# ---------------------------------------------------------------- Catálogos
def test_plan_critic_registered_in_catalog():
    agents = yaml.safe_load(_read(CATALOG))["agents"]
    assert "plan-critic" in agents
    entry = agents["plan-critic"]
    assert entry["id"] == "plan-critic"
    assert not (set(entry["tools"]) & FORBIDDEN_TOOLS)
    assert "agent-router" in entry["related_agents"]
    related_skills = set(entry.get("related_skills") or [])
    source_docs = set(entry.get("source_docs") or [])
    for skill in R067_SKILLS:
        assert skill in related_skills, f"skill ausente em related_skills do catalog.yaml: {skill}"
        assert f".github/skills/{skill}/SKILL.md" in source_docs, (
            f"skill ausente em source_docs do catalog.yaml: .github/skills/{skill}/SKILL.md"
        )


def test_plan_critic_registered_in_routing_graph():
    graph = yaml.safe_load(_read(ROUTING))
    assert any(n["id"] == "plan-critic" for n in graph["nos"])
    assert any(e["de"] == "agent-router" and e["para"] == "plan-critic" for e in graph["arestas"])


# ---------------------------------------------------------------- Rubrica
@pytest.mark.parametrize("token", CATEGORIES + [
    "R-043", "Tier 1", "Tier 2", "Noise Budget", "R-065", "ESCALATED_HITL", "Fast-Pass",
    "BLOCKER", "HIGH", "Gate 1", "Gate 2", "Context Firewall", "review_verdict",
    "review_rounds", "reviewer", "review_tier1", PARECER_HEADING,
    "projects.local.yaml", ".github/instructions/local/",
] + R067_GUARDRAIL_TOKENS)
def test_rubric_contract(token: str):
    assert RUBRIC.is_file()
    assert token in _read(RUBRIC), f"token ausente na rubrica: {token}"


def test_rubric_noise_budget_and_ceilings():
    text = _read(RUBRIC)
    assert re.search(r"Noise Budget.*?\b5\b", text, re.DOTALL)
    assert "Teto 2x" in text and "3x" in text


# ---------------------------------------------------------------- ADR-0014
def test_adr_0014_contract():
    assert ADR.is_file()
    text = _read(ADR)
    fm = _frontmatter(text)
    assert fm["id"] == "ADR-0014"
    assert fm["status"] == "Aceito"
    assert str(fm["date"]) == "2026-11-14"
    assert fm["type"] == "architectural-decision"
    assert fm["diataxis"] == "explanation"
    for token in ("Opção B", "@plan-critic", "Fast-Pass 1x", "Teto 2x", "3x", "tier: full",
                  "Evaluator-Optimizer", "Demystifying Evals", "CONSENSAGENT",
                  "2604.00478", "LLM-as-a-Judge", "LangChain", "Consequências"):
        assert token in text, f"token ausente no ADR: {token}"


# ---------------------------------------------------------------- Metadados e templates
@pytest.mark.parametrize("meta", ["review_verdict", "review_rounds", "reviewer", "review_tier1"])
def test_frontmatter_reference_declares_review_metadata(meta: str):
    assert meta in _read(FRONTMATTER_REF), f"metadado ausente em plan-frontmatter-r064.md: {meta}"


@pytest.mark.parametrize("template", TEMPLATES)
def test_templates_have_pre_hitl_review_section(template: str):
    path = REPO_ROOT / template
    assert path.is_file(), f"template ausente: {template}"
    assert PARECER_HEADING in _read(path), f"seção de parecer ausente em {template}"


# ---------------------------------------------------------------- Tier 1 sobre os planos de governança
def test_tier1_passes_on_source_governance_plan():
    assert SOURCE_PLAN.is_file()
    assert tier1_validate(SOURCE_PLAN) == []


def test_tier1_passes_on_r067_governance_plan():
    assert R067_PLAN.is_file()
    fm = _frontmatter(_read(R067_PLAN))
    assert fm["status"] == "APPROVED" and fm["approved"] is True
    assert tier1_validate(R067_PLAN) == []


def test_tier1_detects_violations(tmp_path: Path):
    bad_dir = tmp_path / "docs/plans/feature"
    bad_dir.mkdir(parents=True)
    bad = bad_dir / "invalido.md"
    bad.write_text(
        '---\nstatus: DRAFT\napproved: true\nplan_type: "governance"\n'
        'allowed_files:\n  - "nao/existe.py"\n---\n# Plano\nTODO preencher\n',
        encoding="utf-8",
    )
    found = " | ".join(tier1_validate(bad, repo_root=tmp_path))
    for code in ("T1-1", "T1-2", "T1-3", "T1-5", "T1-7"):
        assert code in found, f"violação {code} não detectada: {found}"
