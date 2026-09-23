"""
test_architectural_blueprint_gate_governance.py — Validação determinística do gate de Blueprint Técnico
e proibição de desvio prematuro para implementação / gap dumping (R-058 / Smell 2.27).

Quality Gate que garante:
1. CLAUDE.md declara a regra normativa R-058.
2. copilot-instructions.md declara a diretriz R-058.
3. governance-audit-patterns/SKILL.md cataloga o Smell 2.27 (Premature Implementation Bypass & Gap Dumping).
4. agent-router.agent.md declara a proibição de bypass prematuro e a vedação de gap dumping no handoff.
5. router-agent.md (template) incorpora a regra R-058 para routers de domínio.
6. workflows.md formaliza o Invariante 20 no WORKFLOW-FEATURE-DEVELOPMENT.
7. routing-graph.yaml formaliza o Estado 3 do WORKFLOW-FEATURE-DEVELOPMENT com a exigência R-058.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
GOVERNANCE_SKILL_PATH = REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md"
ROUTER_AGENT_PATH = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
ROUTER_TEMPLATE_PATH = REPO_ROOT / ".github" / "agents" / "templates" / "router-agent.md"
WORKFLOWS_PATH = REPO_ROOT / ".github" / "agents" / "workflows.md"
ROUTING_GRAPH_PATH = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"


def test_r058_declared_in_claude_md():
    """Valida se R-058 está formalizada em CLAUDE.md."""
    assert CLAUDE_PATH.exists(), "CLAUDE.md não encontrado"
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    assert "R-058" in content, "CLAUDE.md DEVE declarar a regra normativa R-058"
    assert "Anti-Premature Implementation Bypass" in content or "Blueprint Técnico" in content, (
        "CLAUDE.md DEVE explicitar o gate de Blueprint Técnico obrigatório (R-058)"
    )


def test_r058_declared_in_copilot_instructions():
    """Valida se R-058 está formalizada em copilot-instructions.md."""
    assert COPILOT_INSTRUCTIONS_PATH.exists(), "copilot-instructions.md não encontrado"
    content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
    assert "R-058" in content, "copilot-instructions.md DEVE declarar a regra R-058"
    assert "Blueprint Técnico" in content or "Anti-Premature Implementation Bypass" in content, (
        "copilot-instructions.md DEVE referenciar a regra R-058"
    )


def test_smell_2_27_documented_in_governance_audit_patterns():
    """Valida se o Smell 2.27 está catalogado na skill de auditoria de governança."""
    assert GOVERNANCE_SKILL_PATH.exists(), "governance-audit-patterns/SKILL.md não encontrado"
    content = GOVERNANCE_SKILL_PATH.read_text(encoding="utf-8")
    assert "2.27" in content, "governance-audit-patterns/SKILL.md DEVE catalogar a seção do Smell 2.27"
    assert "R-058" in content, "governance-audit-patterns/SKILL.md DEVE vincular o Smell 2.27 à regra R-058"
    assert "Despejo de Lacunas Arquiteturais" in content or "Gap Dumping" in content, (
        "governance-audit-patterns/SKILL.md DEVE explicitar o conceito de Gap Dumping"
    )


def test_agent_router_declares_r058_and_gap_dumping_prohibition():
    """Valida se agent-router.agent.md declara R-058 e proíbe gap dumping para executores de código."""
    assert ROUTER_AGENT_PATH.exists(), "agent-router.agent.md não encontrado"
    content = ROUTER_AGENT_PATH.read_text(encoding="utf-8")
    assert "R-058" in content, "agent-router.agent.md DEVE referenciar R-058"
    assert "Smell 2.27" in content or "Lacunas para handoff" in content, (
        "agent-router.agent.md DEVE proibir despejo de lacunas de arquitetura no handoff para implementadores"
    )
    assert "tech-solution-architect" in content, (
        "agent-router.agent.md DEVE orientar despacho para tech-solution-architect em features complexas"
    )


def test_router_template_declares_r058_and_blueprint_gate():
    """Valida se o template de router (router-agent.md) herda as proibições de R-058."""
    assert ROUTER_TEMPLATE_PATH.exists(), "templates/router-agent.md não encontrado"
    content = ROUTER_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "R-058" in content, "templates/router-agent.md DEVE referenciar a regra R-058"
    assert "Smell 2.27" in content or "tech-solution-architect" in content, (
        "templates/router-agent.md DEVE incorporar a restrição de blueprint prévio"
    )


def test_workflows_feature_development_declares_invariant_20():
    """Valida se workflows.md formaliza o Invariante 20 no WORKFLOW-FEATURE-DEVELOPMENT."""
    assert WORKFLOWS_PATH.exists(), "workflows.md não encontrado"
    content = WORKFLOWS_PATH.read_text(encoding="utf-8")
    assert "Invariante de Blueprint Técnico e Decomposição Obrigatórios" in content or "Invariante 20" in content, (
        "workflows.md DEVE declarar o Invariante 20"
    )
    assert "R-058" in content, "workflows.md DEVE vincular o Invariante 20 à regra R-058"
    assert "Smell 2.27" in content, "workflows.md DEVE vincular o Invariante 20 ao Smell 2.27"
    assert "feature-planner" in content, "workflows.md DEVE mencionar o papel de @feature-planner para subtasks"


def test_routing_graph_enforces_r058_on_feature_development():
    """Valida se routing-graph.yaml formaliza R-058 em WORKFLOW-FEATURE-DEVELOPMENT e na aresta correspondente."""
    assert ROUTING_GRAPH_PATH.exists(), "routing-graph.yaml não encontrado"
    content = ROUTING_GRAPH_PATH.read_text(encoding="utf-8")
    assert "R-058" in content, "routing-graph.yaml DEVE referenciar a regra R-058"

    data = yaml.safe_load(content) or {}
    wf4 = next((wf for wf in data.get("workflows", []) if wf["id"] == "WORKFLOW-FEATURE-DEVELOPMENT"), None)
    assert wf4 is not None, "WORKFLOW-FEATURE-DEVELOPMENT deve existir no grafo"

    etapa3 = next((e for e in wf4.get("estados", []) if e.get("etapa") == 3), None)
    assert etapa3 is not None, "Estado 3 deve existir no WORKFLOW-FEATURE-DEVELOPMENT"
    assert "tech-solution-architect" in etapa3.get("agent", ""), (
        "Estado 3 de WORKFLOW-FEATURE-DEVELOPMENT deve pertencer a tech-solution-architect"
    )
    assert etapa3.get("proibir_bypass_direto_para_implementador") is True, (
        "Estado 3 deve declarar proibir_bypass_direto_para_implementador: true"
    )

