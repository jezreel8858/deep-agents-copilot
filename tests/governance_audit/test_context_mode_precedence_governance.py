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
        assert "100% OBRIGATÓRIO" in c or "100% obrigatório" in c, f"[{pf.name}] DEVE declarar context-mode 100% obrigatório"
        assert "fallback exclusivo" in c, f"[{pf.name}] DEVE citar fallback exclusivo de editor"


EXECUTOR_AGENT_NAMES = {
    "adapter-generator.agent.md",
    "angular-bug-fixer.agent.md",
    "angular-component-test-writer.agent.md",
    "angular-e2e-writer.agent.md",
    "angular-feature-developer.agent.md",
    "angular-test-fixer.agent.md",
    "angular-ui-stylist.agent.md",
    "angular-unit-test-writer.agent.md",
    "binding-initializer.agent.md",
    "business-rules-extractor.agent.md",
    "database-specialist.agent.md",
    "docs-engineer.agent.md",
    "ejb-bug-fixer.agent.md",
    "ejb-feature-developer.agent.md",
    "ejb-integration-test-writer.agent.md",
    "ejb-perf-tuner.agent.md",
    "ejb-test-fixer.agent.md",
    "ejb-unit-test-writer.agent.md",
    "governance-factory.agent.md",
    "governance-maintainer.agent.md",
    "informix-migration-dev.agent.md",
    "informix-spl-expert.agent.md",
    "oracle-migration-dev.agent.md",
    "oracle-plsql-expert.agent.md",
    "pr-gatekeeper.agent.md",
    "python-bug-fixer.agent.md",
    "python-feature-developer.agent.md",
    "python-integration-test-writer.agent.md",
    "python-perf-tuner.agent.md",
    "python-test-fixer.agent.md",
    "python-unit-test-writer.agent.md",
    "requirements-analyst.agent.md",
    "spring-boot-bug-fixer.agent.md",
    "spring-boot-feature-developer.agent.md",
    "spring-boot-integration-test-writer.agent.md",
    "spring-boot-perf-tuner.agent.md",
    "spring-boot-test-fixer.agent.md",
    "spring-boot-unit-test-writer.agent.md",
    "spring-reactive-bug-fixer.agent.md",
    "spring-reactive-feature-developer.agent.md",
    "spring-reactive-integration-test-writer.agent.md",
    "spring-reactive-resilience-tuner.agent.md",
    "spring-reactive-test-fixer.agent.md",
    "spring-reactive-unit-test-writer.agent.md",
    "struts-bug-fixer.agent.md",
    "struts-feature-developer.agent.md",
    "struts-integration-test-writer.agent.md",
    "struts-perf-tuner.agent.md",
    "struts-test-fixer.agent.md",
    "struts-unit-test-writer.agent.md",
}


def test_all_mutating_agents_declare_r056_and_explicit_prohibition():
    """
    Varredura dinâmica e assertiva (R-056 / Smell 2.24):
    Todo .agent.md no repositório com perfil executor mutativo
    DEVE conter a regra R-056 e a proibição explícita no seu texto.
    """
    agent_files = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    assert len(agent_files) >= 40, "Deve haver ao menos 40 agents no catálogo"

    mutating_agents = [
        af for af in agent_files
        if af.name in EXECUTOR_AGENT_NAMES
    ]

    assert len(mutating_agents) == len(EXECUTOR_AGENT_NAMES), (
        f"Esperados {len(EXECUTOR_AGENT_NAMES)} agentes executores, encontrados {len(mutating_agents)}"
    )

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


def test_all_non_router_agents_prohibit_mcp_tool_chaining():
    """
    Valida que 100% dos agentes não-roteadores contêm a proibição explícita
    contra MCP Tool Chaining sequencial no chat (Smell 2.26).
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
        content = af.read_text(encoding="utf-8")
        if "NÃO encadear chamadas unitárias sequenciais de `ctx_execute`" not in content and "NÃO encadear chamadas unitárias sequenciais de ctx_execute" not in content:
            violations.append(f"[{rel}] ausência de proibição de MCP Tool Chaining sequencial")
        if "Regra de Ouro do Single-Turn MCP" not in content:
            violations.append(f"[{rel}] ausência da Regra de Ouro do Single-Turn MCP")

    assert not violations, (
        f"Violação de Smell 2.26 (MCP Tool Chaining) em {len(violations)} agentes:\n"
        + "\n".join(violations)
    )


def test_threshold_ge_2_and_plan_then_batch_declared_in_normative_docs():
    """
    Valida se CLAUDE.md, copilot-instructions.md, efficient-batch e context-mode
    formalizam deterministicamente a 'Regra do Limiar >= 2' e o 'Protocolo Plan-Then-Batch' (R-059 / Smell 2.26).
    """
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
        assert "Limiar >= 2" in c, f"[{name}] DEVE formalizar a Regra do Limiar >= 2"
        assert "Plan-Then-Batch" in c, f"[{name}] DEVE formalizar o Protocolo Plan-Then-Batch"
        assert "ENUMERAR" in c, f"[{name}] DEVE conter a etapa ENUMERAR do protocolo"
        assert "prosseguir" in c.lower(), f"[{name}] DEVE declarar que comandos curtos ('prosseguir') mantêm o rigor"


def test_all_executor_agents_absence_of_native_editor_tools():
    """
    Valida que 100% dos 50 agentes executores mutativos possuem AUSÊNCIA TOTAL
    de ferramentas nativas de editor (read_file, create_file, insert_edit_into_file, replace_string_in_file)
    no frontmatter YAML tools: (Smell 2.24 / Smell 2.26).
    """
    import re

    forbidden_tools = {"read_file", "create_file", "insert_edit_into_file", "replace_string_in_file"}
    agent_files = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if p.name in EXECUTOR_AGENT_NAMES
    ]
    assert len(agent_files) == len(EXECUTOR_AGENT_NAMES)

    violations = []
    for af in agent_files:
        c = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", c, re.DOTALL)
        if not fm_match:
            violations.append(f"[{af.name}] ausência de frontmatter")
            continue
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_match.group(1))
        if not tools_match:
            violations.append(f"[{af.name}] ausência de tools: no frontmatter")
            continue
        tools_str = tools_match.group(1)
        present_forbidden = [t for t in forbidden_tools if f"'{t}'" in tools_str or f'"{t}"' in tools_str]
        if present_forbidden:
            violations.append(f"[{af.name}] ferramentas nativas de editor proibidas presentes: {present_forbidden}")

    assert not violations, (
        f"Violação de menor privilégio / Smell 2.24 em {len(violations)} agentes executores:\n"
        + "\n".join(violations)
    )


def test_all_executor_agents_declare_all_ctx_tools():
    """
    Valida que 100% dos 50 agentes executores declaram compulsoriamente todas as 5 ferramentas
    context-mode (ctx_execute, ctx_execute_file, ctx_batch_execute, ctx_index, ctx_search) em tools:.
    """
    import re

    required_ctx = [
        "context-mode/ctx_execute",
        "context-mode/ctx_execute_file",
        "context-mode/ctx_batch_execute",
        "context-mode/ctx_index",
        "context-mode/ctx_search",
    ]
    agent_files = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if p.name in EXECUTOR_AGENT_NAMES
    ]
    assert len(agent_files) == len(EXECUTOR_AGENT_NAMES)

    violations = []
    for af in agent_files:
        c = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", c, re.DOTALL)
        if not fm_match:
            continue
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_match.group(1))
        if not tools_match:
            continue
        tools_str = tools_match.group(1)
        missing = [t for t in required_ctx if t not in tools_str]
        if missing:
            violations.append(f"[{af.name}] ferramentas context-mode ausentes: {missing}")

    assert not violations, (
        f"Agentes executores sem o conjunto completo de context-mode ({len(violations)}):\n"
        + "\n".join(violations)
    )


def test_all_executor_agents_contain_execution_protocol_block():
    """
    Valida que 100% dos 50 agentes executores contêm o bloco canônico <execution_protocol>
    referenciando o Protocolo Plan-Then-Batch e a Regra do Limiar >= 2 (Smell 2.26 / Smell 2.13 / R-059).
    """
    agent_files = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if p.name in EXECUTOR_AGENT_NAMES
    ]
    assert len(agent_files) == len(EXECUTOR_AGENT_NAMES)

    violations = []
    for af in agent_files:
        c = af.read_text(encoding="utf-8")
        if "<execution_protocol>" not in c or "</execution_protocol>" not in c:
            violations.append(f"[{af.name}] ausência do bloco <execution_protocol>")
            continue
        if "Plan-Then-Batch" not in c:
            violations.append(f"[{af.name}] <execution_protocol> não referencia 'Plan-Then-Batch'")
        if "Limiar >= 2" not in c:
            violations.append(f"[{af.name}] <execution_protocol> não referencia 'Limiar >= 2'")
        if "ENUMERAR" not in c:
            violations.append(f"[{af.name}] <execution_protocol> não detalha a etapa 'ENUMERAR'")

    assert not violations, (
        f"Agentes executores sem bloco <execution_protocol> válido ({len(violations)}):\n"
        + "\n".join(violations)
    )


def test_all_non_router_agents_absence_of_native_editor_tools():
    """
    Valida que 100% dos 78 agentes nao-roteadores (incluindo prompt-structuring) possuem
    AUSENCIA TOTAL de ferramentas nativas de editor (read_file, create_file, insert_edit_into_file, replace_string_in_file)
    no frontmatter YAML tools: (Smell 2.24 / Smell 2.26 / R-056 / R-059).
    """
    import re

    forbidden_tools = {"read_file", "create_file", "insert_edit_into_file", "replace_string_in_file"}
    all_agents = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    non_routers = [
        p for p in all_agents
        if not p.name.endswith("-router.agent.md") and p.name != "agent-router.agent.md"
    ]
    assert len(non_routers) >= 78, f"Esperado ao menos 78 agentes nao-roteadores, encontrados {len(non_routers)}"

    violations = []
    for af in non_routers:
        c = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", c, re.DOTALL)
        if not fm_match:
            violations.append(f"[{af.name}] ausencia de frontmatter")
            continue
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_match.group(1))
        if not tools_match:
            violations.append(f"[{af.name}] ausencia de tools: no frontmatter")
            continue
        tools_str = tools_match.group(1)
        present_forbidden = [t for t in forbidden_tools if f"'{t}'" in tools_str or f'"{t}"' in tools_str]
        if present_forbidden:
            violations.append(f"[{af.name}] ferramentas nativas de editor proibidas presentes: {present_forbidden}")

    assert not violations, (
        f"Violacao de menor privilegio / Smell 2.24 em {len(violations)} agentes nao-roteadores:\n"
        + "\n".join(violations)
    )


def test_all_non_router_agents_declare_all_ctx_tools():
    """
    Valida que 100% de todos os agentes nao-roteadores (exceto prompt-structuring) declaram
    compulsoriamente todas as 5 ferramentas context-mode (ctx_execute, ctx_execute_file, ctx_batch_execute, ctx_index, ctx_search) em tools:.
    """
    import re

    required_ctx = [
        "context-mode/ctx_execute",
        "context-mode/ctx_execute_file",
        "context-mode/ctx_batch_execute",
        "context-mode/ctx_index",
        "context-mode/ctx_search",
    ]
    all_agents = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    non_routers = [
        p for p in all_agents
        if not p.name.endswith("-router.agent.md") and p.name != "agent-router.agent.md" and p.name != "prompt-structuring.agent.md"
    ]
    assert len(non_routers) >= 77

    violations = []
    for af in non_routers:
        c = af.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", c, re.DOTALL)
        if not fm_match:
            continue
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", fm_match.group(1))
        if not tools_match:
            continue
        tools_str = tools_match.group(1)
        missing = [t for t in required_ctx if t not in tools_str]
        if missing:
            violations.append(f"[{af.name}] ferramentas context-mode ausentes: {missing}")

    assert not violations, (
        f"Agentes nao-roteadores sem o conjunto completo de context-mode ({len(violations)}):\n"
        + "\n".join(violations)
    )


def test_all_non_router_agents_contain_execution_protocol_block():
    """
    Valida que 100% de todos os agentes nao-roteadores (exceto prompt-structuring) contem o bloco canonico <execution_protocol>
    referenciando o Protocolo Plan-Then-Batch e a Regra do Limiar >= 2 (Smell 2.26 / Smell 2.13 / R-059).
    """
    all_agents = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]
    non_routers = [
        p for p in all_agents
        if not p.name.endswith("-router.agent.md") and p.name != "agent-router.agent.md" and p.name != "prompt-structuring.agent.md"
    ]
    assert len(non_routers) >= 77

    violations = []
    for af in non_routers:
        c = af.read_text(encoding="utf-8")
        if "<execution_protocol>" not in c or "</execution_protocol>" not in c:
            violations.append(f"[{af.name}] ausencia do bloco <execution_protocol>")
            continue
        if "Plan-Then-Batch" not in c:
            violations.append(f"[{af.name}] <execution_protocol> nao referencia 'Plan-Then-Batch'")
        if "Limiar >= 2" not in c:
            violations.append(f"[{af.name}] <execution_protocol> nao referencia 'Limiar >= 2'")
        if "ENUMERAR" not in c:
            violations.append(f"[{af.name}] <execution_protocol> nao detalha a etapa 'ENUMERAR'")

    assert not violations, (
        f"Agentes nao-roteadores sem bloco <execution_protocol> valido ({len(violations)}):\n"
        + "\n".join(violations)
    )


def test_code_knowledge_graph_specific_plan_then_batch_safeguard():
    """
    Valida se code-knowledge-graph.agent.md contem salvaguarda especifica exigindo ctx_batch_execute
    ou script de leitura em lote consolidado antes de queries de grafo, proibindo N chamadas de ctx_execute (Smell 2.26 / R-059).
    """
    ckg_file = AGENTS_DIR / "code-knowledge-graph.agent.md"
    assert ckg_file.exists()
    content = ckg_file.read_text(encoding="utf-8")

    assert "ctx_batch_execute" in content, "code-knowledge-graph deve referenciar ctx_batch_execute"
    assert "<execution_protocol>" in content, "code-knowledge-graph deve conter <execution_protocol>"
    assert "N chamadas" in content or "chamadas sequenciais unitárias" in content, (
        "code-knowledge-graph deve proibir explicitamente N chamadas unitarias de ctx_execute"
    )
    assert "inspeção de múltiplos arquivos" in content or "inspeções multi-arquivo" in content, (
        "code-knowledge-graph deve conter regra especifica para inspecao multi-arquivo em lote"
    )


def test_agent_router_safeguard_against_model_discovery_r054():
    """
    Valida se agent-router.agent.md e copilot-instructions.md formalizam a salvaguarda estrita contra
    discovery de catalog.yaml ou *.agent.md em tempo de execucao para descoberta de modelos (R-054 / Zero Discovery).
    """
    router_file = AGENTS_DIR / "agent-router.agent.md"
    ci_file = REPO_ROOT / ".github" / "copilot-instructions.md"

    r_content = router_file.read_text(encoding="utf-8")
    ci_content = ci_file.read_text(encoding="utf-8")

    # In router
    assert "Zero Discovery de Modelos" in r_content or "ZERO DISCOVERY DE MODELOS" in r_content or "RESOLUÇÃO ESTÁTICA / ZERO DISCOVERY EM RUNTIME" in r_content, (
        "agent-router.agent.md deve conter clausula formal de Zero Discovery de Modelos"
    )
    assert "É TERMINANTEMENTE PROIBIDO ao `agent-router` chamar ferramentas de busca ou leitura" in r_content or "É TERMINANTEMENTE PROIBIDO ao `agent-router`" in r_content, (
        "agent-router.agent.md deve proibir ferramentas de busca/leitura para catalog.yaml"
    )

    # In copilot-instructions
    assert "Blindagem contra Discovery de Modelos (R-054)" in ci_content, (
        "copilot-instructions.md deve formalizar a Blindagem contra Discovery de Modelos (R-054)"
    )
    assert "Zero Discovery é absoluto e inegociável" in ci_content, (
        "copilot-instructions.md deve declarar que Zero Discovery e absoluto e inegociavel"
    )


def test_context_mode_sequential_tool_chaining_circuit_breaker_and_explicit_cwd():
    """
    Valida se context-mode/SKILL.md formaliza o Circuit Breaker de Tool-Chaining Sequencial
    (limite de 2 chamadas consecutivas de ctx_execute/ctx_execute_file), a mitigação de cwd explícito
    (anti-PathNotFound / anti-fallback), e se CLAUDE.md referencia o mecanismo sob R-059.
    """
    skill_file = SKILLS_DIR / "context-mode" / "SKILL.md"
    claude_file = REPO_ROOT / "CLAUDE.md"

    assert skill_file.exists(), "context-mode/SKILL.md deve existir"
    assert claude_file.exists(), "CLAUDE.md deve existir"

    s_content = skill_file.read_text(encoding="utf-8")
    c_content = claude_file.read_text(encoding="utf-8")

    # Circuit Breaker de Tool-Chaining Sequencial
    assert "Circuit Breaker de Tool-Chaining Sequencial" in s_content, (
        "context-mode/SKILL.md deve conter secao do Circuit Breaker de Tool-Chaining Sequencial"
    )
    assert "2 (duas) chamadas consecutivas" in s_content or "2 chamadas consecutivas" in s_content, (
        "context-mode/SKILL.md deve definir o limiar de 2 chamadas consecutivas para o Circuit Breaker"
    )
    assert "handoff-governance" in s_content and "2.4" in s_content, (
        "context-mode/SKILL.md deve referenciar o precedente de handoff-governance/SKILL.md 2.4"
    )
    assert "limitação conhecida" in s_content.lower() or "mitigação comportamental" in s_content.lower(), (
        "context-mode/SKILL.md deve explicitar a limitacao comportamental/prompt engineering do circuit breaker"
    )

    # Mitigação de cwd explícito
    assert "cwd" in s_content, "context-mode/SKILL.md deve mencionar parametro cwd"
    assert "PathNotFound" in s_content, "context-mode/SKILL.md deve advertir sobre PathNotFound por omissao de cwd"
    assert "raiz do repositório" in s_content or "raiz do repositório-alvo" in s_content, (
        "context-mode/SKILL.md deve orientar a apontar cwd para a raiz do repositorio"
    )

    # Remissão em CLAUDE.md R-059
    assert "Circuit Breaker de Tool-Chaining Sequencial" in c_content, (
        "CLAUDE.md deve referenciar o Circuit Breaker de Tool-Chaining Sequencial sob R-059"
    )

def test_context_mode_few_shot_batching_and_model_routing_fan_out_signal():
    """
    Valida se context-mode/SKILL.md formaliza o exemplo Few-Shot (4.3) de Anti-Padrão vs Padrão Correto,
    se CLAUDE.md e copilot-instructions.md declaram R-021.1 (Model Routing por Fan-Out),
    e se a skill efficient-batch-code-modification referencia a subseção 4.3.
    """
    ctx_skill_file = SKILLS_DIR / "context-mode" / "SKILL.md"
    eff_skill_file = SKILLS_DIR / "efficient-batch-code-modification" / "SKILL.md"
    claude_file = REPO_ROOT / "CLAUDE.md"
    copilot_file = REPO_ROOT / ".github" / "copilot-instructions.md"

    assert ctx_skill_file.exists(), "context-mode/SKILL.md deve existir"
    assert eff_skill_file.exists(), "efficient-batch-code-modification/SKILL.md deve existir"
    assert claude_file.exists(), "CLAUDE.md deve existir"
    assert copilot_file.exists(), "copilot-instructions.md deve existir"

    ctx_content = ctx_skill_file.read_text(encoding="utf-8")
    eff_content = eff_skill_file.read_text(encoding="utf-8")
    claude_content = claude_file.read_text(encoding="utf-8")
    copilot_content = copilot_file.read_text(encoding="utf-8")

    # Bloco 1: Subseção 4.3 em context-mode/SKILL.md
    assert "4.3" in ctx_content and "Few-Shot: Anti-Padrão vs Padrão Correto de Batching" in ctx_content, (
        "context-mode/SKILL.md deve conter subseção 4.3 com o cabeçalho Few-Shot: Anti-Padrão vs Padrão Correto de Batching"
    )

    # Bloco 2: Remissão em efficient-batch-code-modification/SKILL.md
    assert "context-mode/SKILL.md § 4.3" in eff_content, (
        "efficient-batch-code-modification/SKILL.md deve conter remissão para context-mode/SKILL.md § 4.3"
    )

    # Bloco 3 & 4: R-021.1 em CLAUDE.md e copilot-instructions.md
    assert "R-021.1" in claude_content, "CLAUDE.md deve declarar a regra R-021.1 (Model Routing por Fan-Out)"
    assert "R-021.1" in copilot_content, "copilot-instructions.md deve declarar a regra R-021.1 (Model Routing por Fan-Out)"
    assert "≥ 10 alvos/arquivos/operações homogêneas" in copilot_content, (
        "copilot-instructions.md deve declarar o limiar de fan-out (>= 10 alvos/arquivos/operações)"
    )

