"""
test_ctx_execute_capability_profile.py — Validação determinística do perfil de ferramentas context-mode (R-055 / Smell 2.32).

Verifica que agentes classificados como "Gather-only" não possuem ferramentas
de execução pesada ('context-mode/ctx_execute' e 'context-mode/ctx_execute_file')
em seu frontmatter 'tools:', mantendo compulsoriamente 'context-mode/ctx_batch_execute'.

Referência: docs/implementation-plans/20261003-governance-maintenance-ctx-execute-profile-classification.md
"""

from pathlib import Path
import re
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = BASE_DIR / ".github" / "agents"

# Lista canônica dos 26 agentes classificados formalmente como "Gather-only"
# aprovada no WORKFLOW-GOVERNANCE-MAINTENANCE (Etapa 4 / R-064)
GATHER_ONLY_AGENTS = [
    "agent-auditor",
    "adr-sentinel",
    "bug-triage",
    "code-review",
    "code-style-enforcer",
    "compliance-guardrails",
    "database-specialist",
    "debugger",
    "deep-search",
    "devops-engineer",
    "docs-engineer",
    "feature-planner",
    "pr-gatekeeper",
    "repo-hygiene-auditor",
    "requirements-analyst",
    "runtime-verifier",
    "security-reviewer",
    "tech-solution-architect",
    "test-strategy",
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
]


def _extract_tools(content: str) -> list[str]:
    match = re.search(r"^tools:\s*(\[.*?\])", content, re.MULTILINE)
    if not match:
        return []
    raw = match.group(1)
    return re.findall(r"""['"]([^'"]+)['"]""", raw)


@pytest.fixture(scope="session")
def all_agent_files():
    files = list(AGENTS_DIR.rglob("*.agent.md"))
    assert len(files) > 0, "Nenhum arquivo .agent.md encontrado!"
    return {f.stem.replace(".agent", ""): f for f in files}


def test_gather_only_agents_do_not_have_ctx_execute(all_agent_files):
    """Garante que nenhum dos 26 agentes Gather-only declare ctx_execute ou ctx_execute_file."""
    violations = []
    missing_batch = []

    for name in GATHER_ONLY_AGENTS:
        file_path = all_agent_files.get(name)
        assert file_path is not None, f"Agente '{name}' não foi encontrado em .github/agents/"

        content = file_path.read_text(encoding="utf-8")
        tools = _extract_tools(content)

        if "context-mode/ctx_execute" in tools:
            violations.append(f"{name} ({file_path.name}) possui 'context-mode/ctx_execute'")
        if "context-mode/ctx_execute_file" in tools:
            violations.append(f"{name} ({file_path.name}) possui 'context-mode/ctx_execute_file'")
        if "context-mode/ctx_batch_execute" not in tools:
            missing_batch.append(f"{name} ({file_path.name}) NÃO possui 'context-mode/ctx_batch_execute'")

    assert not violations, (
        f"Violação de perfil Gather-only detectada em {len(violations)} caso(s):\n"
        + "\n".join(violations)
    )
    assert not missing_batch, (
        f"Agentes Gather-only sem 'context-mode/ctx_batch_execute':\n"
        + "\n".join(missing_batch)
    )


def test_gather_process_agents_inventory(all_agent_files):
    """Garante inventário dos agentes Gather+Process sem quebrar o build."""
    gather_process_agents = [
        name for name in all_agent_files.keys() if name not in GATHER_ONLY_AGENTS
    ]
    # Espera-se que agentes mutadores/fábrica existam no ecossistema
    assert len(gather_process_agents) > 0
    assert "governance-maintainer" in gather_process_agents
    assert "governance-factory" in gather_process_agents
