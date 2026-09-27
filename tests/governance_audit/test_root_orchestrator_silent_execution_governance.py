"""
test_root_orchestrator_silent_execution_governance.py — Validação determinística da proibição de
execução direta pelo Orquestrador Raiz sem router (R-063 / Anti Silent Bypass).

Quality Gate que garante:
1. CLAUDE.md declara a regra normativa R-063 (Zero Execução Direta pelo Orquestrador Raiz sem Router).
2. CLAUDE.md complementa R-042 com referência explícita a R-063 e persistência da re-triagem.
3. copilot-instructions.md propaga a cláusula no diagrama §1.1 (ramo Não -> triagem normal).
4. copilot-instructions.md propaga a regra em §2 (Sempre — bullet R-063).
5. Template canônico router-agent.md, skill governance-audit-patterns e os 7 domain routers propagam R-063 incondicionalmente.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
AGENT_ROUTER_PATH = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
ROUTER_TEMPLATE_PATH = REPO_ROOT / ".github" / "agents" / "templates" / "router-agent.md"
GOVERNANCE_SKILL_PATH = REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"


def test_r063_declared_in_claude_md():
    """Valida se R-063 (Zero Execução Direta pelo Orquestrador Raiz) está formalizada em CLAUDE.md."""
    assert CLAUDE_PATH.exists(), "CLAUDE.md não encontrado"
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    assert "R-063" in content, "CLAUDE.md DEVE declarar a regra normativa R-063"
    assert "Zero Execução Direta" in content, (
        "CLAUDE.md DEVE nomear explicitamente a regra como 'Zero Execução Direta pelo Orquestrador Raiz sem Router'"
    )
    assert "Orquestrador Raiz" in content
    assert "sem antes invocar" in content
    assert "run_subagent" in content


def test_r042_complemented_with_r063_reference():
    """Valida se R-042 em CLAUDE.md referencia R-063 e reforça a obrigação mesmo sem agent ativo."""
    assert CLAUDE_PATH.exists(), "CLAUDE.md não encontrado"
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    assert "R-042" in content, "CLAUDE.md DEVE declarar R-042"
    r042_block = content.split("- **R-042")[1].split("- **R-043")[0]
    assert "R-063" in r042_block, "R-042 DEVE referenciar explicitamente R-063"
    assert "não há agent ativo residente" in r042_block.lower() or "ausência de agent ativo" in r042_block.lower(), (
        "R-042 DEVE explicitar que a ausência de agent ativo não suspende a obrigação de triagem"
    )


def test_copilot_instructions_diagram_propagates_r063():
    """Valida se o diagrama de fluxo §1.1 em copilot-instructions.md propaga R-063 no ramo Não."""
    assert COPILOT_INSTRUCTIONS_PATH.exists(), "copilot-instructions.md não encontrado"
    content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
    assert "R-063" in content, "copilot-instructions.md DEVE referenciar R-063"
    assert "triagem normal" in content
    assert "run_subagent antes de qualquer tool" in content or "OBRIGATÓRIO invocar @agent-router" in content


def test_copilot_instructions_sempre_bullet_propagates_r063():
    """Valida se §2 'Sempre' em copilot-instructions.md possui bullet formal para R-063."""
    assert COPILOT_INSTRUCTIONS_PATH.exists(), "copilot-instructions.md não encontrado"
    content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
    assert "Zero Execução Direta pelo Orquestrador Raiz sem Router (R-063" in content or (
        "R-063" in content and "Anti Silent Bypass" in content
    ), "copilot-instructions.md DEVE conter o bullet formal de R-063 em §2"


def test_r063_propagation_in_template_and_domain_routers():
    """Valida se R-063 e a subseção de proibição estão propagadas no template canônico e nos 7 domain routers.
    
    Quality Gate incondicional garantindo que:
    1. templates/router-agent.md contém a subseção 'Zero Execução Direta pelo Orquestrador Raiz (R-063)'.
    2. governance-audit-patterns/SKILL.md cataloga Smell 2.30 com referência a R-063.
    3. Todos os 7 domain routers (stack routers) possuem a subseção 'Zero Execução Direta pelo Orquestrador Raiz (R-063)'.
    """
    assert ROUTER_TEMPLATE_PATH.exists(), "templates/router-agent.md não encontrado"
    assert GOVERNANCE_SKILL_PATH.exists(), "governance-audit-patterns/SKILL.md não encontrado"
    
    template_content = ROUTER_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "R-063" in template_content, "templates/router-agent.md DEVE conter referência explícita a R-063"
    assert "Zero Execução Direta pelo Orquestrador Raiz" in template_content or "Anti Silent Bypass" in template_content, (
        "templates/router-agent.md DEVE conter a subseção ou cláusula de R-063"
    )

    skill_content = GOVERNANCE_SKILL_PATH.read_text(encoding="utf-8")
    assert "R-063" in skill_content, "governance-audit-patterns/SKILL.md DEVE referenciar R-063"
    assert "2.30" in skill_content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.30"

    domain_routers = [
        p for p in AGENTS_DIR.glob("**/*router*.agent.md")
        if "templates" not in p.parts and p.name != "agent-router.agent.md"
    ]
    assert len(domain_routers) >= 7, f"Esperado ao menos 7 domain routers, encontrados: {len(domain_routers)}"

    for router_path in domain_routers:
        content = router_path.read_text(encoding="utf-8")
        assert "R-063" in content, f"{router_path.name} DEVE conter referência explícita a R-063"
        assert "Zero Execução Direta pelo Orquestrador Raiz" in content or "Anti Silent Bypass" in content, (
            f"{router_path.name} DEVE conter a subseção de R-063"
        )
