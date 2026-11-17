"""
test_ctx_execute_capability_profile.py — Validação determinística do perfil de ferramentas context-mode (R-055 / Smell 2.32).

Verifica:
1. Os 24 agentes classificados como "Gather-only" NÃO possuem 'context-mode/ctx_execute'
   em seu frontmatter 'tools:', mantêm compulsoriamente 'context-mode/ctx_batch',
   usam CLAUSE_BATCH_ONLY e NÃO contêm instrução contraditória de 'ctx_execute (com file)'
   na seção '## CRÍTICO: ESCOPO E NÃO-ESCOPO' nem na cláusula CONSOLIDAR.
2. Os 7 agentes classificados como COMPUTE_READONLY_AGENTS possuem 'context-mode/ctx_execute'
   em seu frontmatter 'tools:' e contêm o guardrail anti-mutação (CLAUSE_BATCH_OR_EXEC_READONLY /
   vedação de fs.writeFileSync).
3. O agente 'database-specialist' possui 'context-mode/ctx_execute' no frontmatter
   (integrando EXPECTED_CTX_EXECUTE_AGENTS) e usa CLAUSE_BATCH_OR_EXEC.
4. Os prompts '.github/prompts/validate.prompt.md' e '.github/prompts/strategic-review.prompt.md'
   possuem 'context-mode/ctx_execute' no frontmatter e a cláusula Read-Only (CLAUSE_BATCH_OR_EXEC_READONLY).

Referência:
- docs/plans/governance/20261003-090000-governance-maintenance-ctx-execute-profile-classification.md
- docs/plans/governance/20261117-120000-governance-maintenance-ctx-execute-profile-revisao.md
"""

from pathlib import Path
import re
import pytest

from tools.agent_protocol_sync.sync_execution_protocol import (
    CLAUSE_BATCH_ONLY,
    CLAUSE_BATCH_OR_EXEC,
    CLAUSE_BATCH_OR_EXEC_READONLY,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = BASE_DIR / ".github" / "agents"
PROMPTS_DIR = BASE_DIR / ".github" / "prompts"

# Lista canônica dos 24 agentes classificados formalmente como "Gather-only"
# aprovada no WORKFLOW-GOVERNANCE-MAINTENANCE (R-064)
GATHER_ONLY_AGENTS = [
    "adr-sentinel",
    "bug-triage",
    "code-review",
    "code-style-enforcer",
    "compliance-guardrails",
    "debugger",
    "deep-search",
    "devops-engineer",
    "feature-planner",
    "plan-critic",
    "pr-gatekeeper",
    "repo-hygiene-auditor",
    "requirements-analyst",
    "runtime-verifier",
    "security-reviewer",
    "test-strategy",
    "database-arch-advisor",
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]

GATHER_ONLY_AGENT_FILES = {f"{name}.agent.md" for name in GATHER_ONLY_AGENTS}

# Lista canônica dos 7 agentes Read-Only computacionais (Score 0 com ctx_execute Read-Only)
COMPUTE_READONLY_AGENTS = [
    "agent-auditor",
    "tech-solution-architect",
    "performance-agent",
    "refactor-planner",
    "business-rules-extractor",
    "codegraph-engine",
    "ddd-bounded-context-mapper",
]

# Agentes que obrigatoriamente possuem context-mode/ctx_execute (inclui database-specialist e os 7 COMPUTE_READONLY_AGENTS)
EXPECTED_CTX_EXECUTE_AGENTS = [
    "database-specialist",
    "informix-database-specialist",
    "oracle-database-specialist",
    "governance-maintainer",
    "governance-factory",
    "docs-engineer",
    *COMPUTE_READONLY_AGENTS,
]


def _extract_tools(content: str) -> list[str]:
    match = re.search(r"^tools:\s*(\[.*?\])", content, re.MULTILINE)
    if not match:
        return []
    raw = match.group(1)
    return re.findall(r"""['"]([^'"]+)['"]""", raw)


def _extract_critico_section(content: str) -> str:
    match = re.search(
        r"^##\s+CRÍTICO:.*?(?=^##\s+|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(0) if match else ""


@pytest.fixture(scope="session")
def all_agent_files():
    files = [
        f for f in AGENTS_DIR.rglob("*.agent.md")
        if "templates" not in f.parts
    ]
    assert len(files) > 0, "Nenhum arquivo .agent.md encontrado!"
    return {f.stem.replace(".agent", ""): f for f in files}


def test_gather_only_agents_do_not_have_ctx_execute(all_agent_files):
    """
    Garante que os 24 agentes Gather-only:
    - NÃO possuem 'context-mode/ctx_execute' no frontmatter;
    - possuem 'context-mode/ctx_batch' no frontmatter;
    - NÃO contêm instrução contraditória de 'ctx_execute (com file)' na seção
      '## CRÍTICO: ESCOPO E NÃO-ESCOPO' nem na cláusula CONSOLIDAR;
    - usam CLAUSE_BATCH_ONLY no bloco <execution_protocol>.
    """
    assert len(GATHER_ONLY_AGENTS) == 24, (
        f"Esperados 24 agentes em GATHER_ONLY_AGENTS, encontrados {len(GATHER_ONLY_AGENTS)}"
    )
    assert "database-specialist" not in GATHER_ONLY_AGENTS, (
        "'database-specialist' é executor DDL/DML e NÃO deve pertencer a GATHER_ONLY_AGENTS"
    )

    violations = []
    missing_batch = []
    contradiction_violations = []
    clause_violations = []

    for name in GATHER_ONLY_AGENTS:
        file_path = all_agent_files.get(name)
        assert file_path is not None, f"Agente '{name}' não foi encontrado em .github/agents/"

        content = file_path.read_text(encoding="utf-8")
        tools = _extract_tools(content)

        if "context-mode/ctx_execute" in tools:
            violations.append(f"{name} ({file_path.name}) possui 'context-mode/ctx_execute'")
        if "context-mode/ctx_batch" not in tools:
            missing_batch.append(f"{name} ({file_path.name}) NÃO possui 'context-mode/ctx_batch'")

        critico_section = _extract_critico_section(content)
        if "ctx_execute (com file)" in critico_section or "ctx_execute` (com `file`)" in critico_section:
            contradiction_violations.append(
                f"{name} ({file_path.name}) contém instrução contraditória 'ctx_execute (com file)' na seção CRÍTICO"
            )

        if CLAUSE_BATCH_ONLY not in content:
            clause_violations.append(
                f"{name} ({file_path.name}) NÃO contém CLAUSE_BATCH_ONLY em <execution_protocol>"
            )
        if re.search(r"2\.\s+\*\*CONSOLIDAR[^\n]*ctx_execute", content):
            contradiction_violations.append(
                f"{name} ({file_path.name}) menciona 'ctx_execute' na cláusula CONSOLIDAR"
            )

    assert not violations, (
        f"Violação de perfil Gather-only detectada em {len(violations)} caso(s):\n"
        + "\n".join(violations)
    )
    assert not missing_batch, (
        f"Agentes Gather-only sem 'context-mode/ctx_batch':\n"
        + "\n".join(missing_batch)
    )
    assert not contradiction_violations, (
        f"Contradição Textual-Tooling (Smell 2.32) em agentes Gather-only:\n"
        + "\n".join(contradiction_violations)
    )
    assert not clause_violations, (
        f"Agentes Gather-only sem CLAUSE_BATCH_ONLY:\n"
        + "\n".join(clause_violations)
    )


def test_compute_readonly_agents_have_ctx_execute_and_readonly_guardrail(all_agent_files):
    """
    Garante que os 7 COMPUTE_READONLY_AGENTS possuem 'context-mode/ctx_execute' no frontmatter
    e contêm o guardrail anti-mutação (CLAUSE_BATCH_OR_EXEC_READONLY / vedação de fs.writeFileSync).
    """
    assert len(COMPUTE_READONLY_AGENTS) == 7, (
        f"Esperados 7 agentes em COMPUTE_READONLY_AGENTS, encontrados {len(COMPUTE_READONLY_AGENTS)}"
    )

    missing_tool = []
    missing_guardrail = []

    for name in COMPUTE_READONLY_AGENTS:
        file_path = all_agent_files.get(name)
        assert file_path is not None, f"Agente '{name}' não foi encontrado em .github/agents/"

        content = file_path.read_text(encoding="utf-8")
        tools = _extract_tools(content)

        if "context-mode/ctx_execute" not in tools:
            missing_tool.append(f"{name} ({file_path.name}) NÃO possui 'context-mode/ctx_execute'")

        has_readonly_clause = CLAUSE_BATCH_OR_EXEC_READONLY in content
        has_write_prohibition = "fs.writeFileSync" in content and (
            "Read-Only" in content or "PROIBIDO" in content
        )
        if not (has_readonly_clause or has_write_prohibition):
            missing_guardrail.append(
                f"{name} ({file_path.name}) NÃO contém guardrail anti-mutação (CLAUSE_BATCH_OR_EXEC_READONLY / vedação de fs.writeFileSync)"
            )

    assert not missing_tool, (
        f"COMPUTE_READONLY_AGENTS sem 'context-mode/ctx_execute':\n"
        + "\n".join(missing_tool)
    )
    assert not missing_guardrail, (
        f"COMPUTE_READONLY_AGENTS sem guardrail anti-mutação Read-Only:\n"
        + "\n".join(missing_guardrail)
    )


def test_database_specialist_has_ctx_execute_and_batch_or_exec_clause(all_agent_files):
    """
    Garante que 'database-specialist' pertence a EXPECTED_CTX_EXECUTE_AGENTS,
    possui 'context-mode/ctx_execute' no frontmatter e usa CLAUSE_BATCH_OR_EXEC.
    """
    assert "database-specialist" in EXPECTED_CTX_EXECUTE_AGENTS
    db_file = all_agent_files.get("database-specialist")
    assert db_file is not None, "database-specialist.agent.md deve existir"

    content = db_file.read_text(encoding="utf-8")
    tools = _extract_tools(content)

    assert "context-mode/ctx_execute" in tools, (
        "database-specialist.agent.md DEVE declarar 'context-mode/ctx_execute' em tools:"
    )
    assert "context-mode/ctx_batch" in tools, (
        "database-specialist.agent.md DEVE declarar 'context-mode/ctx_batch' em tools:"
    )
    assert CLAUSE_BATCH_OR_EXEC in content, (
        "database-specialist.agent.md DEVE usar CLAUSE_BATCH_OR_EXEC no <execution_protocol>"
    )


def test_validate_and_strategic_review_prompts_have_ctx_execute_and_readonly_clause():
    """
    Garante que '.github/prompts/validate.prompt.md' e '.github/prompts/strategic-review.prompt.md'
    possuem 'context-mode/ctx_execute' no frontmatter e a cláusula Read-Only (CLAUSE_BATCH_OR_EXEC_READONLY).
    """
    target_prompts = ["validate.prompt.md", "strategic-review.prompt.md"]

    for prompt_name in target_prompts:
        prompt_path = PROMPTS_DIR / prompt_name
        assert prompt_path.exists(), f"Prompt '{prompt_name}' não encontrado em .github/prompts/"

        content = prompt_path.read_text(encoding="utf-8")
        tools = _extract_tools(content)

        assert "context-mode/ctx_execute" in tools, (
            f"{prompt_name} DEVE declarar 'context-mode/ctx_execute' no frontmatter tools:"
        )
        assert CLAUSE_BATCH_OR_EXEC_READONLY in content, (
            f"{prompt_name} DEVE conter CLAUSE_BATCH_OR_EXEC_READONLY em <execution_protocol>"
        )
        assert "fs.writeFileSync" in content, (
            f"{prompt_name} DEVE explicitar a vedação de fs.writeFileSync (modo Read-Only)"
        )


def test_gather_process_agents_inventory(all_agent_files):
    """Garante inventário dos agentes Gather+Process (EXPECTED_CTX_EXECUTE_AGENTS) sem quebrar o build."""
    gather_process_agents = [
        name for name in all_agent_files.keys() if name not in GATHER_ONLY_AGENTS
    ]
    assert len(gather_process_agents) > 0
    for expected in EXPECTED_CTX_EXECUTE_AGENTS:
        assert expected in gather_process_agents, (
            f"Agente '{expected}' deveria estar no inventário Gather+Process (fora de GATHER_ONLY_AGENTS)"
        )
        tools = _extract_tools(all_agent_files[expected].read_text(encoding="utf-8"))
        assert "context-mode/ctx_execute" in tools, (
            f"Agente '{expected}' em EXPECTED_CTX_EXECUTE_AGENTS DEVE declarar 'context-mode/ctx_execute'"
        )
