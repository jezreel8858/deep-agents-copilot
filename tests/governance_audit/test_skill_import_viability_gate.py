"""
test_skill_import_viability_gate.py — Validação determinística do Protocolo de Avaliação de
Pertinência de Importação de Skills (R-067 / Skill Import Viability & Solution Alternative Gate).

Garante que:
1. CLAUDE.md formaliza a regra normativa R-067 com os conceitos de impacto negativo e solução alternativa.
2. copilot-instructions.md referencia R-067.
3. governance-factory-patterns/SKILL.md documenta o gate (§3.4) na Decision Tree, Checklist e Formato de Saída.
4. governance-factory.agent.md incorpora o gate em seu contrato operacional (CRÍTICO, type: skill e checklist).
5. governance-audit-patterns/SKILL.md cataloga o Smell 2.33 vinculado a R-067.
6. routing-graph.yaml registra keywords de roteamento para pedidos de importação de skill externa.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_r067_declared_in_claude_md():
    """Valida se CLAUDE.md declara a regra normativa R-067 com seus conceitos essenciais."""
    claude_file = REPO_ROOT / "CLAUDE.md"
    assert claude_file.exists()
    content = claude_file.read_text(encoding="utf-8")

    assert "R-067" in content, "CLAUDE.md DEVE declarar a regra normativa R-067"
    assert "Importação de Skills" in content or "Importação de Skill" in content, (
        "CLAUDE.md DEVE mencionar o Protocolo de Avaliação de Pertinência de Importação de Skills"
    )
    assert "impacto negativo" in content, (
        "CLAUDE.md DEVE explicitar a obrigação de reportar impacto negativo quando não pertinente"
    )
    assert "solução alternativa" in content, (
        "CLAUDE.md DEVE explicitar a obrigação de propor solução alternativa quando aplicável"
    )


def test_r067_declared_in_copilot_instructions():
    """Valida se copilot-instructions.md referencia a regra R-067."""
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"
    assert ci_file.exists()
    content = ci_file.read_text(encoding="utf-8")

    assert "R-067" in content, "copilot-instructions.md DEVE referenciar a regra R-067"
    assert "Importação de Skills" in content or "Importação de Skill" in content, (
        "copilot-instructions.md DEVE mencionar o Protocolo de Avaliação de Pertinência de Importação de Skills"
    )


def test_governance_factory_patterns_skill_declares_import_viability_gate():
    """Valida se governance-factory-patterns/SKILL.md documenta o gate de viabilidade de importação (§3.4)."""
    skill_file = SKILLS_DIR / "governance-factory-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "R-067" in content, "governance-factory-patterns/SKILL.md DEVE referenciar R-067"
    assert "3.4)" in content, "governance-factory-patterns/SKILL.md DEVE conter a subseção §3.4 do gate"
    assert "Skill Import Viability" in content or "Avaliação de Pertinência de Importação" in content, (
        "governance-factory-patterns/SKILL.md DEVE nomear o Skill Import Viability & Solution Alternative Gate"
    )
    assert "solução alternativa" in content, (
        "governance-factory-patterns/SKILL.md DEVE detalhar a obrigação de propor solução alternativa"
    )
    assert "IMPORTAÇÃO EXTERNA" in content, (
        "governance-factory-patterns/SKILL.md DEVE ramificar a Decision Tree para origem = IMPORTAÇÃO EXTERNA"
    )


def test_governance_factory_agent_declares_import_viability_gate():
    """Valida se governance-factory.agent.md incorpora o gate em seu contrato operacional."""
    agent_file = AGENTS_DIR / "governance-factory.agent.md"
    assert agent_file.exists()
    content = agent_file.read_text(encoding="utf-8")

    assert "R-067" in content, "governance-factory.agent.md DEVE referenciar R-067"
    assert "Protocolo de Avaliação de Pertinência" in content, (
        "governance-factory.agent.md DEVE declarar o Protocolo de Avaliação de Pertinência de Importação"
    )
    assert "solução alternativa" in content, (
        "governance-factory.agent.md DEVE declarar a obrigação de propor solução alternativa"
    )


def test_smell_2_33_cataloged_in_governance_audit_patterns():
    """Valida se governance-audit-patterns/SKILL.md cataloga o Smell 2.33 vinculado a R-067."""
    skill_file = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "2.33" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.33"
    assert "R-067" in content, "governance-audit-patterns/SKILL.md DEVE vincular o Smell 2.33 à regra R-067"
    assert "Skill Import Viability Gate" in content, (
        "governance-audit-patterns/SKILL.md DEVE nomear o Skill Import Viability Gate no Smell 2.33"
    )


def test_routing_graph_declares_skill_import_keywords():
    """Valida se routing-graph.yaml registra keywords de roteamento para importação de skill externa
    na aresta agent-router -> governance-factory."""
    rg_file = AGENTS_DIR / "routing-graph.yaml"
    assert rg_file.exists()
    content = rg_file.read_text(encoding="utf-8")

    assert "importar skill" in content, (
        "routing-graph.yaml DEVE registrar a keyword 'importar skill' na aresta de governance-factory"
    )
    assert "R-067" in content, (
        "routing-graph.yaml DEVE referenciar R-067 na descrição do nó governance-factory"
    )
