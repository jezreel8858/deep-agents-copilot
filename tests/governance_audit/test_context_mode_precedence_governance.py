"""
test_context_mode_precedence_governance.py — Validação determinística da precedência mandatória do context-mode (R-056 / Smell 2.24).

Garante que:
1. CLAUDE.md e copilot-instructions.md formalizam as regras normativas R-008 e R-056 com 100% de obrigatoriedade
   para leitura, modificação e criação de arquivos quando context-mode disponível.
2. Ferramentas nativas de editor (read_file, replace_string_in_file, insert_edit_into_file, create_file) e terminal
   são estritamente proibidas quando context-mode disponível, rebaixadas a fallback exclusivo de indisponibilidade.
3. governance-audit-patterns/SKILL.md cataloga o Smell 2.24 (Editor Tool Sprawl / R-056).
4. efficient-batch-code-modification/SKILL.md define a precedência Nível 1 (Context-Mode 100% Compulsório)
   e Nível 2 (Fallback Exclusivo quando Context-Mode Indisponível).
5. Templates operacionais (operational-agent.md e agent-template.md) incluem a cláusula de uso 100% obrigatório
   e proibição de editor tools / fallback exclusivo.
6. governance-factory.agent.md valida a regra R-056 e Smell 2.24 em seu checklist para novos agentes.
7. governance-maintainer.agent.md e agentes pares aplicam a precedência mandatória de context-mode.
"""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"


def test_r008_and_r056_declared_in_claude_md():
    """Valida se CLAUDE.md declara R-008 e R-056 com uso 100% obrigatório e proibição de editor tools."""
    claude_file = REPO_ROOT / "CLAUDE.md"
    assert claude_file.exists()
    content = claude_file.read_text(encoding="utf-8")

    assert "R-008" in content, "CLAUDE.md DEVE declarar a regra normativa R-008"
    assert "R-056" in content, "CLAUDE.md DEVE declarar a regra normativa R-056"
    assert "100% OBRIGATÓRIO" in content, (
        "CLAUDE.md DEVE explicitar a obrigatoriedade de 100% do context-mode"
    )
    assert "estritamente proibidas quando o context-mode estiver disponível" in content, (
        "CLAUDE.md DEVE declarar ferramentas nativas de editor como estritamente proibidas"
    )
    assert "fallback exclusivo" in content, (
        "CLAUDE.md DEVE rebaixar ferramentas de editor a fallback exclusivo"
    )
    assert "ctx_execute" in content, "CLAUDE.md DEVE citar ctx_execute como primário"


def test_r056_and_r008_declared_in_copilot_instructions():
    """Valida se copilot-instructions.md declara o uso 100% obrigatório e fallback exclusivo."""
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"
    assert ci_file.exists()
    content = ci_file.read_text(encoding="utf-8")

    assert "R-008" in content, "copilot-instructions.md DEVE referenciar a regra R-008"
    assert "R-056" in content, "copilot-instructions.md DEVE referenciar a regra R-056"
    assert "100% OBRIGATÓRIO" in content, (
        "copilot-instructions.md DEVE declarar context-mode 100% obrigatório"
    )
    assert "fallback exclusivo" in content, (
        "copilot-instructions.md DEVE definir ferramentas de editor como fallback exclusivo"
    )
    assert "estritamente proibidas" in content or "estritamente proibidos" in content, (
        "copilot-instructions.md DEVE proibir ferramentas manuais de editor quando context-mode disponível"
    )


def test_smell_2_24_documented_in_governance_audit_patterns():
    """Valida se o Smell 2.24 está catalogado na skill de auditoria com a regra endurecida."""
    skill_file = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "2.24" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.24"
    assert "Editor Tool Sprawl" in content, (
        "Smell 2.24 DEVE identificar o anti-padrão de Editor Tool Sprawl"
    )
    assert "100% obrigatório" in content, (
        "Smell 2.24 DEVE citar o uso 100% obrigatório de context-mode"
    )
    assert "fallback exclusivo" in content, (
        "Smell 2.24 DEVE citar o rebaixamento de editor tools a fallback exclusivo"
    )


def test_efficient_batch_code_modification_skill_declares_context_mode_precedence():
    """Valida se efficient-batch-code-modification/SKILL.md define a precedência e fallback exclusivo."""
    skill_file = SKILLS_DIR / "efficient-batch-code-modification" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "R-056" in content, "efficient-batch-code-modification/SKILL.md DEVE referenciar R-056"
    assert "R-008" in content, "efficient-batch-code-modification/SKILL.md DEVE referenciar R-008"
    assert "100% OBRIGATÓRIO" in content or "100% Compulsório" in content, (
        "A skill DEVE definir o Nível 1 como 100% obrigatório/compulsório para context-mode"
    )
    assert "Fallback Exclusivo" in content or "fallback exclusivo" in content, (
        "A skill DEVE definir Nível 2 como fallback exclusivo quando context-mode indisponível"
    )
    assert "estritamente proibidas quando o context-mode estiver disponível" in content, (
        "A skill DEVE proibir expressamente ferramentas de editor quando context-mode disponível"
    )


def test_operational_and_general_templates_declare_context_mode_precedence():
    """Valida se os templates operacionais incluem a cláusula de precedência R-056 e fallback exclusivo."""
    templates = [
        AGENTS_DIR / "templates" / "operational-agent.md",
        AGENTS_DIR / "templates" / "agent-template.md",
    ]

    for tpl in templates:
        assert tpl.exists(), f"Template {tpl.name} deve existir"
        content = tpl.read_text(encoding="utf-8")

        assert "100% OBRIGATÓRIO" in content, (
            f"[{tpl.name}] DEVE declarar o uso 100% OBRIGATÓRIO de context-mode"
        )
        assert "fallback exclusivo" in content, (
            f"[{tpl.name}] DEVE declarar o rebaixamento a fallback exclusivo de ferramentas de editor"
        )


def test_governance_factory_enforces_context_mode_precedence_for_mutating_agents():
    """Valida se governance-factory.agent.md valida a regra R-056 e fallback exclusivo em seu checklist."""
    gf_file = AGENTS_DIR / "governance-factory.agent.md"
    assert gf_file.exists()
    content = gf_file.read_text(encoding="utf-8")

    assert "R-056" in content, "governance-factory.agent.md DEVE referenciar R-056 em seu checklist"
    assert "Smell 2.24" in content, "governance-factory.agent.md DEVE mencionar a prevenção do Smell 2.24"
    assert "100% obrigatório" in content, (
        "governance-factory.agent.md DEVE exigir o uso 100% obrigatório de context-mode"
    )
    assert "fallback exclusivo" in content, (
        "governance-factory.agent.md DEVE mencionar o fallback exclusivo de ferramentas de editor"
    )


def test_governance_maintainer_and_peer_agents_align_with_context_mode_precedence():
    """Valida se governance-maintainer e agentes pares declaram 100% obrigatório e fallback exclusivo."""
    gm_file = AGENTS_DIR / "governance-maintainer.agent.md"
    assert gm_file.exists()
    gm_content = gm_file.read_text(encoding="utf-8")

    assert "100% OBRIGATÓRIO" in gm_content, (
        "governance-maintainer.agent.md DEVE declarar context-mode 100% OBRIGATÓRIO"
    )
    assert "fallback exclusivo" in gm_content.lower(), (
        "governance-maintainer.agent.md DEVE citar fallback exclusivo"
    )

    peer_files = [
        AGENTS_DIR / "backend" / "ejb" / "ejb-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "python" / "python-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "spring-boot" / "spring-boot-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "spring-reactive" / "spring-reactive-test-fixer.agent.md",
        AGENTS_DIR / "backend" / "struts" / "struts-test-fixer.agent.md",
        AGENTS_DIR / "database-specialist.agent.md",
        AGENTS_DIR / "frontend" / "angular" / "angular-test-fixer.agent.md",
    ]

    for pf in peer_files:
        assert pf.exists(), f"Peer agent {pf.name} deve existir"
        c = pf.read_text(encoding="utf-8")
        assert "100% obrigatório" in c, f"[{pf.name}] DEVE declarar context-mode 100% obrigatório"
        assert "fallback exclusivo" in c, f"[{pf.name}] DEVE citar fallback exclusivo de editor"


def test_all_mutating_agents_declare_r056_and_explicit_prohibition():
    """
    Varredura dinâmica e assertiva (R-056 / Smell 2.24):
    Todo .agent.md no repositório que declare insert_edit_into_file ou create_file em tools:
    DEVE conter a regra R-056 e a proibição explícita no seu texto.
    """
    import re

    agent_files = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    assert len(agent_files) >= 40, "Deve haver ao menos 40 agents no catálogo"

    mutating_agents = []
    for af in agent_files:
        content = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        fm_text = fm_match.group(1)
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_text)
        if not tools_match:
            continue
        tools_str = tools_match.group(1)
        if "insert_edit_into_file" in tools_str or "create_file" in tools_str:
            mutating_agents.append(af)

    assert len(mutating_agents) >= 45, f"Esperado ao menos 45 agentes mutadores, encontrados {len(mutating_agents)}"

    violations = []
    for ma in mutating_agents:
        rel = ma.relative_to(REPO_ROOT)
        text = ma.read_text(encoding="utf-8")

        # 1. R-056
        if "R-056" not in text:
            violations.append(f"[{rel}] ausência da citação explícita a 'R-056'")

        # 2. Cláusula de proibição estrita de editor tools
        if "NÃO usar ferramentas nativas de editor" not in text:
            violations.append(f"[{rel}] ausência da cláusula 'NÃO usar ferramentas nativas de editor'")

        # 3. 100% OBRIGATÓRIO
        if "100% OBRIGATÓRIO" not in text and "100% obrigatório" not in text:
            violations.append(f"[{rel}] ausência de '100% OBRIGATÓRIO'")

        # 4. Fallback exclusivo
        if "fallback exclusivo" not in text.lower():
            violations.append(f"[{rel}] ausência de 'fallback exclusivo'")

        # 5. Diretriz positiva de execução no sandbox
        if "sandbox do `context-mode`" not in text and "sandbox do context-mode" not in text:
            violations.append(f"[{rel}] ausência da diretriz positiva de execução no sandbox do context-mode")

    assert not violations, (
        f"Violação de R-056 / Smell 2.24 em {len(violations)} agentes mutadores:\n"
        + "\n".join(violations)
    )


def test_smell_2_26_documented_in_governance_audit_patterns():
    """Valida se o Smell 2.26 está catalogado na skill de auditoria com remediação e detecção."""
    skill_file = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    assert "2.26" in content, "governance-audit-patterns/SKILL.md DEVE catalogar o Smell 2.26"
    assert "MCP Tool Chaining Sequencial no Chat" in content, (
        "Smell 2.26 DEVE identificar o anti-padrão de MCP Tool Chaining Sequencial no Chat"
    )
    assert "ctx_batch_execute" in content, (
        "Smell 2.26 DEVE referenciar ctx_batch_execute"
    )
    assert "Single-Turn MCP Batching" in content, (
        "Smell 2.26 DEVE referenciar a exigência de Single-Turn MCP Batching"
    )


def test_mcp_batch_execution_and_tool_chaining_prohibition_in_normative_docs():
    """Valida se CLAUDE.md, copilot-instructions.md, efficient-batch e context-mode proíbem tool chaining sequencial."""
    claude_file = REPO_ROOT / "CLAUDE.md"
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"
    eff_file = SKILLS_DIR / "efficient-batch-code-modification" / "SKILL.md"
    ctx_file = SKILLS_DIR / "context-mode" / "SKILL.md"

    for path_obj, name in [
        (claude_file, "CLAUDE.md"),
        (ci_file, "copilot-instructions.md"),
        (eff_file, "efficient-batch-code-modification/SKILL.md"),
        (ctx_file, "context-mode/SKILL.md"),
    ]:
        assert path_obj.exists(), f"{name} deve existir"
        c = path_obj.read_text(encoding="utf-8")
        assert "Single-Turn MCP Batching" in c or "Single-Turn Batching" in c, (
            f"[{name}] DEVE referenciar Single-Turn Batching"
        )
        assert "Smell 2.26" in c or "Tool Chaining" in c or "tool chaining" in c, (
            f"[{name}] DEVE referenciar Smell 2.26 ou proibição de tool chaining sequencial"
        )
        assert "ctx_batch_execute" in c, f"[{name}] DEVE citar ctx_batch_execute"


def test_all_agents_with_ctx_execute_declare_ctx_batch_execute():
    """
    Valida que 100% dos agentes que declaram context-mode/ctx_execute
    também declaram compulsoriamente context-mode/ctx_batch_execute em tools: (Smell 2.26).
    """
    import re

    agent_files = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    assert len(agent_files) >= 40

    missing_batch = []
    for af in agent_files:
        c = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---s*\n(.*?)\n---", c, re.DOTALL)
        if not fm_match:
            continue
        fm_text = fm_match.group(1)
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_text)
        if not tools_match:
            continue
        tools_str = tools_match.group(1)
        if "context-mode/ctx_execute" in tools_str and "context-mode/ctx_batch_execute" not in tools_str:
            missing_batch.append(str(af.relative_to(REPO_ROOT)))

    assert not missing_batch, (
        f"Smell 2.26: {len(missing_batch)} agentes possuem ctx_execute mas não possuem ctx_batch_execute:\n"
        + "\n".join(missing_batch)
    )


def test_catalog_yaml_declares_ctx_batch_execute_for_all_ctx_execute_agents():
    """
    Valida que toda entrada em catalog.yaml que declara context-mode/ctx_execute
    também declara context-mode/ctx_batch_execute em tools:.
    """
    import yaml

    cat_file = AGENTS_DIR / "catalog.yaml"
    assert cat_file.exists()
    cat_data = yaml.safe_load(cat_file.read_text(encoding="utf-8"))

    agents = cat_data.get("agents", {})
    missing_in_cat = []
    for ag_id, ag_info in agents.items():
        tools = ag_info.get("tools", [])
        if "context-mode/ctx_execute" in tools and "context-mode/ctx_batch_execute" not in tools:
            missing_in_cat.append(ag_id)

    assert not missing_in_cat, (
        f"catalog.yaml possui agentes com ctx_execute sem ctx_batch_execute: {missing_in_cat}"
    )


def test_all_non_router_agents_declare_ctx_batch_execute_and_ctx_execute():
    """
    Valida que 100% dos agentes não-roteadores (exceto prompt-structuring, que não possui tools de arquivo)
    declaram compulsoriamente 'context-mode/ctx_batch_execute' e 'context-mode/ctx_execute' em tools:.
    """
    import re

    all_agents = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    
    non_routers = [
        p for p in all_agents
        if not p.name.endswith("-router.agent.md") and p.name != "agent-router.agent.md" and p.name != "prompt-structuring.agent.md"
    ]
    assert len(non_routers) >= 75, f"Esperado ao menos 75 agentes não-roteadores, encontrados {len(non_routers)}"

    missing_batch = []
    missing_exec = []
    for af in non_routers:
        c = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", c, re.DOTALL)
        if not fm_match:
            continue
        fm_text = fm_match.group(1)
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_text)
        if not tools_match:
            continue
        tools_str = tools_match.group(1)
        rel = str(af.relative_to(REPO_ROOT))
        if "context-mode/ctx_batch_execute" not in tools_str:
            missing_batch.append(rel)
        if "context-mode/ctx_execute" not in tools_str:
            missing_exec.append(rel)

    assert not missing_batch, (
        f"100% dos agentes não-roteadores DEVEM possuir ctx_batch_execute. Faltam ({len(missing_batch)}):\n"
        + "\n".join(missing_batch)
    )
    assert not missing_exec, (
        f"100% dos agentes não-roteadores DEVEM possuir ctx_execute. Faltam ({len(missing_exec)}):\n"
        + "\n".join(missing_exec)
    )


def test_all_non_router_agents_declare_r056_and_prohibition():
    """
    Valida que 100% dos agentes não-roteadores declaram compulsoriamente a proibição
    de ferramentas manuais de editor e o uso 100% obrigatório de context-mode (R-008 / R-056 / Smell 2.24).
    """
    all_agents = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    non_routers = [
        p for p in all_agents
        if not p.name.endswith("-router.agent.md") and p.name != "agent-router.agent.md" and p.name != "prompt-structuring.agent.md"
    ]

    violations = []
    for af in non_routers:
        rel = str(af.relative_to(REPO_ROOT))
        text = af.read_text(encoding="utf-8")
        if "NÃO usar ferramentas nativas de editor" not in text:
            violations.append(f"[{rel}] ausência de proibição de editor tools")
        if "100% OBRIGATÓRIO" not in text and "100% obrigatório" not in text:
            violations.append(f"[{rel}] ausência de '100% OBRIGATÓRIO'")
        if "fallback exclusivo" not in text.lower():
            violations.append(f"[{rel}] ausência de 'fallback exclusivo'")

    assert not violations, (
        f"Violação de R-056 em {len(violations)} agentes não-roteadores:\n"
        + "\n".join(violations)
    )


def test_prompts_declare_context_mode_precedence_and_batching():
    """Valida que prompts de execução declaram context-mode e batching mandatórios."""
    prompts_dir = REPO_ROOT / ".github" / "prompts"
    commit_p = prompts_dir / "commit.prompt.md"
    review_p = prompts_dir / "review.prompt.md"
    tpl_p = prompts_dir / "templates" / "prompt-template.md"

    for p, name in [(commit_p, "commit.prompt.md"), (review_p, "review.prompt.md"), (tpl_p, "prompt-template.md")]:
        assert p.exists()
        c = p.read_text(encoding="utf-8")
        assert "ctx_batch_execute" in c, f"[{name}] DEVE declarar ctx_batch_execute"
        assert "100% OBRIGATÓRIO" in c or "100% obrigatório" in c, f"[{name}] DEVE declarar context-mode 100% obrigatório"
