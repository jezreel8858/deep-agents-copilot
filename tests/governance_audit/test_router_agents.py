"""
test_router_agents.py — Suíte determinística de validação para agents com perfil de Router / Supervisor.

Cobre especificamente agents com papel de roteamento central e supervisores hierárquicos de domínio:
- agent-router (roteador central / entry-point do ecossistema)
- angular-router (supervisor de domínio frontend Angular)
- spring-boot-router (supervisor de domínio backend Spring Boot)
- spring-reactive-router (supervisor de domínio backend Spring Reactive)
- ejb-router (supervisor de domínio backend Java Legado EJB)
- database-router (supervisor de domínio backend Banco de Dados)
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
ROUTER_TEMPLATE = AGENTS_DIR / "templates" / "router-agent.md"


def parse_frontmatter(content: str) -> dict:
    """Extrai e faz parse do frontmatter YAML delimitado por ---"""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def extract_headings(file_path: Path) -> list[tuple[int, str]]:
    """Extrai cabeçalhos Markdown (# .. ######) ignorando frontmatter YAML e blocos de código."""
    text = file_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if text.startswith("---"):
        idx = text.find("\n---", 3)
        if idx != -1:
            text = text[idx + 4:]
    
    headings = []
    in_code = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
    return headings


def extract_h2_sections(file_path: Path) -> list[str]:
    """Retorna os títulos de nível 2 (##) do documento."""
    return [title for level, title in extract_headings(file_path) if level == 2]


def get_all_router_agents() -> list[Path]:
    """Retorna todos os arquivos .agent.md com perfil de router."""
    return [p for p in AGENTS_DIR.glob("**/*router*.agent.md") if "templates" not in p.parts]


def get_domain_router_agents() -> list[Path]:
    """Retorna os supervisores hierárquicos de domínio (excluindo o agent-router central)."""
    return [p for p in get_all_router_agents() if p.name != "agent-router.agent.md"]


# ─────────────────────────────────────────────────────────────
# 1. Descoberta e Presença de Routers
# ─────────────────────────────────────────────────────────────

def test_all_expected_router_agents_exist():
    """Valida se todos os routers previstos na governança estão presentes."""
    routers = get_all_router_agents()
    router_names = {r.name for r in routers}
    
    expected = {
        "agent-router.agent.md",
        "angular-router.agent.md",
        "spring-boot-router.agent.md",
        "spring-reactive-router.agent.md",
        "ejb-router.agent.md",
        "database-router.agent.md",
        "python-router.agent.md",
        "struts-router.agent.md",
    }
    missing = expected - router_names
    assert not missing, f"Routers ausentes no catálogo: {missing}"


# ─────────────────────────────────────────────────────────────
# 2. Seções Obrigatórias para Perfil de Router
# ─────────────────────────────────────────────────────────────

MANDATORY_DOMAIN_ROUTER_SECTIONS = [
    "CRÍTICO: ESCOPO DE ROTEAMENTO",
    "Decision Tree",
    "Formato de Saída",
    "Retorno ao Router (R-042 — Anti Sticky-Session)",
]

MANDATORY_CENTRAL_ROUTER_SECTIONS = [
    "CRÍTICO: ESCOPO DE ORQUESTRAÇÃO",
    "Model Awareness — Solicitação de Modelo na Delegação",
    "Formato de Saída",
    "Quando Delegar",
]


def test_domain_routers_have_all_mandatory_sections():
    """
    Valida se todo supervisor de domínio (stack router) possui exatamente as 4 seções canônicas:
    1. CRÍTICO: ESCOPO DE ROTEAMENTO
    2. Decision Tree
    3. Formato de Saída
    4. Retorno ao Router (R-042 — Anti Sticky-Session)
    Toda dependência documental e de skills deve residir no frontmatter 'source_docs:' (SSOT).
    """
    domain_routers = get_domain_router_agents()
    assert len(domain_routers) >= 5

    gaps = []
    for router_path in domain_routers:
        h2s = extract_h2_sections(router_path)
        rel_path = router_path.relative_to(REPO_ROOT)
        
        for req in MANDATORY_DOMAIN_ROUTER_SECTIONS:
            found = any(req.lower() in h.lower() for h in h2s)
            if not found:
                gaps.append(f"[{rel_path}] Ausência da seção obrigatória: '## {req}'")

    assert not gaps, f"Violações de seções obrigatórias em routers de domínio:\n" + "\n".join(gaps)


def test_central_router_has_all_mandatory_sections():
    """Valida se o agent-router central possui as seções canônicas de orquestração."""
    central_router = AGENTS_DIR / "agent-router.agent.md"
    assert central_router.exists()

    h2s = extract_h2_sections(central_router)
    gaps = []
    for req in MANDATORY_CENTRAL_ROUTER_SECTIONS:
        found = any(req.lower() in h.lower() for h in h2s)
        if not found:
            gaps.append(f"[agent-router.agent.md] Ausência da seção: '## {req}'")

    assert not gaps, f"Violações de seções no agent-router central:\n" + "\n".join(gaps)


# ─────────────────────────────────────────────────────────────
# 3. Decision Tree Estruturada
# ─────────────────────────────────────────────────────────────

def test_all_routers_contain_structured_decision_tree():
    """Valida se a seção Decision Tree contém branches determinísticos de despacho."""
    routers = get_all_router_agents()

    for router_path in routers:
        content = router_path.read_text(encoding="utf-8")
        rel_path = router_path.relative_to(REPO_ROOT)
        
        # Deve possuir cabeçalho de Decision Tree ou tabela de decisão
        assert "Decision Tree" in content or "Árvore de Decisão" in content, (
            f"[{rel_path}] Ausência de Decision Tree declarada"
        )
        
        # Deve possuir marcadores de bifurcação ou branches de encaminhamento
        has_branches = any(sym in content for sym in ["├─", "└─", "->", "→", "Delegado:"])
        assert has_branches, f"[{rel_path}] Decision Tree não possui branches de encaminhamento"


# ─────────────────────────────────────────────────────────────
# 4. Formato de Saída do Router
# ─────────────────────────────────────────────────────────────

def test_domain_routers_output_format_declares_active_agent_and_delegation():
    """
    Valida se a seção Formato de Saída de supervisores de domínio declara:
    - Agente Ativo: <router-name> (visibilidade de fluxo)
    - Campo de especialista delegado (Delegado: @...)
    - Campo de justificativa técnica (Motivo:)
    - Próximo passo mínimo
    """
    domain_routers = get_domain_router_agents()

    for router_path in domain_routers:
        content = router_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        router_name = fm.get("name", router_path.stem.replace(".agent", ""))
        rel_path = router_path.relative_to(REPO_ROOT)

        assert f"Agente Ativo: {router_name}" in content, (
            f"[{rel_path}] Formato de Saída não declara banner 'Agente Ativo: {router_name}'"
        )
        assert "Delegado:" in content or "Delegando para @" in content, (
            f"[{rel_path}] Formato de Saída não possui campo de delegação ('Delegado:')"
        )
        assert "Motivo:" in content or "motivo:" in content, (
            f"[{rel_path}] Formato de Saída não possui campo de justificativa ('Motivo:')"
        )


def test_central_router_output_format_contract():
    """Valida se o agent-router central declara contrato de delegação com especificação de modelo."""
    central_router = AGENTS_DIR / "agent-router.agent.md"
    content = central_router.read_text(encoding="utf-8")
    assert "Delegando para @" in content or "Delegado:" in content, (
        "agent-router deve declarar padrão de delegação com solicitação de modelo"
    )


# ─────────────────────────────────────────────────────────────
# 5. Tooling Estrito: Menor Privilégio & Sem Ferramentas Mutativas em Domain Routers
# ─────────────────────────────────────────────────────────────

def test_all_routers_and_template_tooling_strict_least_privilege():
    """
    Valida restrições de ferramentas para TODOS os routers (central, domain routers e template) (R-054 / Smell 2.23):
    - OBRIGATÓRIO: run_subagent (R-042 - fundamental para despacho)
    - CONJUNTO PERMITIDO: estritamente o baseline canônico de roteamento
    - PROIBIDO: ferramentas mutativas de código (insert_edit_into_file, create_file, replace_string_in_file, apply_patch)
    - PROIBIDO: ferramentas de execução pesada, terminal ou sandbox (run_in_terminal, ctx_execute, ctx_execute_file, ctx_batch_execute)
    """
    all_routers = get_all_router_agents() + [ROUTER_TEMPLATE]
    prohibited_tools = {
        "insert_edit_into_file", "create_file", "replace_string_in_file", "apply_patch",
        "run_in_terminal", "context-mode/ctx_execute", "context-mode/ctx_execute_file",
        "context-mode/ctx_batch_execute"
    }
    allowed_tools = {
        "read_file", "file_search", "grep_search", "list_dir",
        "ask_questions", "run_subagent", "context-mode/ctx_search"
    }

    for router_path in all_routers:
        fm = parse_frontmatter(router_path.read_text(encoding="utf-8"))
        tools = set(fm.get("tools", []))
        rel_path = router_path.relative_to(REPO_ROOT)

        assert "run_subagent" in tools, (
            f"[{rel_path}] Router não possui 'run_subagent' em tools: (R-042)"
        )

        prohibited = tools.intersection(prohibited_tools)
        assert not prohibited, (
            f"[{rel_path}] Router possui ferramentas proibidas de mutação/execução: {prohibited}"
        )

        unapproved = tools - allowed_tools
        assert not unapproved, (
            f"[{rel_path}] Router possui ferramentas fora do baseline canônico de Least Privilege: {unapproved}"
        )


def test_central_router_has_run_subagent():
    """Valida se o agent-router central possui a ferramenta mandatória run_subagent (R-042)."""
    fm = parse_frontmatter((AGENTS_DIR / "agent-router.agent.md").read_text(encoding="utf-8"))
    tools = set(fm.get("tools", []))
    assert "run_subagent" in tools, "agent-router central deve possuir run_subagent em tools: (R-042)"


# ─────────────────────────────────────────────────────────────
# 6. Skills Mandatórias de Roteamento
# ─────────────────────────────────────────────────────────────

def test_routers_declare_mandatory_routing_skills():
    """Valida se todo router declara agent-contracts e handoff-governance em source_docs."""
    mandatory_skills = ["agent-contracts", "handoff-governance"]

    for router_path in get_all_router_agents():
        fm = parse_frontmatter(router_path.read_text(encoding="utf-8"))
        source_docs = fm.get("source_docs", []) or []
        rel_path = router_path.relative_to(REPO_ROOT)

        for skill in mandatory_skills:
            has_skill = any(skill in str(doc) for doc in source_docs)
            assert has_skill, (
                f"[{rel_path}] Router não referencia a skill obrigatória '{skill}' em source_docs"
            )


# ─────────────────────────────────────────────────────────────
# 7. Conformidade com o Template Canônico router-agent.md
# ─────────────────────────────────────────────────────────────

def test_domain_routers_conform_to_canonical_router_template():
    """Valida se todos os domain routers atendem exatamente à estrutura do template canônico router-agent.md."""
    assert ROUTER_TEMPLATE.exists(), "Template canônico router-agent.md não encontrado"
    tpl_h2s = extract_h2_sections(ROUTER_TEMPLATE)

    for router_path in get_domain_router_agents():
        actual_h2s = extract_h2_sections(router_path)
        rel_path = router_path.relative_to(REPO_ROOT)
        
        # Deve possuir exatamente a mesma quantidade e nomes de seções do template
        assert actual_h2s == tpl_h2s, (
            f"[{rel_path}] Divergência estrutural em relação a router-agent.md:\n"
            f"  Esperado: {tpl_h2s}\n"
            f"  Encontrado: {actual_h2s}"
        )


# ─────────────────────────────────────────────────────────────
# 8. R-054 — Zero Discovery, Flat Delegation e Smell 2.23
# ─────────────────────────────────────────────────────────────

def test_all_routers_declare_zero_discovery_guardrail():
    """Valida se TODOS os routers (central, domain routers e template) declaram formalmente
    a regra mandatória de ZERO TOOL CALLS DE DISCOVERY em suas restrições críticas (R-054 / Smell 2.23)."""
    all_routers = get_all_router_agents() + [ROUTER_TEMPLATE]

    for router_path in all_routers:
        content = router_path.read_text(encoding="utf-8")
        rel_path = router_path.relative_to(REPO_ROOT)

        assert "ZERO TOOL CALLS DE DISCOVERY" in content or "Zero Discovery" in content, (
            f"[{rel_path}] Router não declara o guardrail obrigatório de 'ZERO TOOL CALLS DE DISCOVERY' (R-054)"
        )


def test_all_routers_declare_flat_delegation_rule():
    """Valida se TODOS os routers (central, domain routers e template) declaram formalmente
    o modelo de Delegação Plana (Flat Delegation) (R-047 / R-054 / Smell 2.20)."""
    all_routers = get_all_router_agents() + [ROUTER_TEMPLATE]

    for router_path in all_routers:
        content = router_path.read_text(encoding="utf-8")
        rel_path = router_path.relative_to(REPO_ROOT)

        assert "Flat Delegation" in content or "Delegação Plana" in content, (
            f"[{rel_path}] Router não declara a regra de 'Delegação Plana (Flat Delegation)' (R-054)"
        )


def test_smell_2_23_router_over_empowerment_documented():
    """Valida se o Smell 2.23 (Router Over-Empowerment e Pre-Routing Discovery Bloat)
    está documentado em governance-audit-patterns/SKILL.md."""
    skill_path = REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md"
    assert skill_path.exists()
    content = skill_path.read_text(encoding="utf-8")
    assert "2.23" in content, "Smell 2.23 deve estar documentado em governance-audit-patterns/SKILL.md"
    assert "ZERO TOOL CALLS DE DISCOVERY" in content or "Zero Discovery" in content, (
        "Smell 2.23 deve documentar a regra de Zero Discovery"
    )
