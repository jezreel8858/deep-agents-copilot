"""
test_playwright_mcp_frontend_governance.py — Governança determinística do MCP Playwright nos agents
frontend (Angular + React). plan_ref: docs/implementation-plans/20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md (T12).

Garante:
1. Paridade das tools `playwright/*` entre Angular e React (developer = 13, test-engineer = 18) e
   sincronia agent.md x sub-catálogo x AgentCard.
2. arch-advisors e routers permanecem sem tools `playwright/*`; arch-advisors referenciam playwright-mcp e VFL
   e o template de plano possui a seção UI/Layout.
3. developers/test-engineers referenciam playwright-mcp e VFL em source_docs (paridade angular/react).
4. Ausência de tag flutuante `@latest` (skills e config do servidor) e versão fixa na skill.
5. Segredos somente por variável de ambiente (sem valores literais) nos artefatos de governança.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
AGENTCARDS_DIR = REPO_ROOT / ".a2a" / "agentcards"
PLAYWRIGHT_SKILL = ".github/skills/playwright-mcp/SKILL.md"
VFL_SKILL = ".github/skills/frontend-visual-feedback-loop/SKILL.md"
STACKS = ("angular", "react")
DEVELOPER_TOOL_COUNT = 13
TEST_ENGINEER_TOOL_COUNT = 18

SECRET_LITERAL = re.compile(
    r"(?i)\b(password|passwd|senha|secret|api[_-]?key)\b\s*[:=]\s*[\"'](?!\$|<|\{|process\.env)[^\"'\s]{4,}[\"']"
)
FLOATING_TAG = re.compile(r"@latest\b")
PINNED_VERSION = re.compile(r"@playwright/mcp@\d+\.\d+\.\d+")


def _agent_path(stack: str, role: str) -> Path:
    return FRONTEND_DIR / stack / f"{stack}-{role}.agent.md"


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    assert match, remediation(
        f"[{path.name}] frontmatter YAML ausente",
        fix_hint="adicionar frontmatter '---' com name/tools/source_docs no topo do arquivo.",
    )
    return yaml.safe_load(match.group(1)) or {}


def _playwright_tools(stack: str, role: str) -> set[str]:
    tools = _frontmatter(_agent_path(stack, role)).get("tools", [])
    return {t for t in tools if t.startswith("playwright/")}


def _catalog_tools(stack: str, role: str) -> set[str]:
    data = yaml.safe_load((FRONTEND_DIR / stack / f"{stack}-catalog.yaml").read_text(encoding="utf-8"))
    tools = data["agents"][f"{stack}-{role}"].get("tools", [])
    return {t for t in tools if t.startswith("playwright/")}


def _card_tools(stack: str, role: str) -> set[str]:
    card = json.loads((AGENTCARDS_DIR / f"{stack}-{role}.agentcard.json").read_text(encoding="utf-8"))
    return {t for t in card.get("tools", []) if t.startswith("playwright/")}


@pytest.mark.parametrize("role,expected", [("developer", DEVELOPER_TOOL_COUNT), ("test-engineer", TEST_ENGINEER_TOOL_COUNT)])
def test_playwright_tools_parity_between_stacks(role: str, expected: int):
    angular = _playwright_tools("angular", role)
    react = _playwright_tools("react", role)
    assert angular == react, remediation(
        f"[{role}] tools playwright/* divergem entre Angular e React: {sorted(angular ^ react)}",
        fix_hint=f"alinhar o frontmatter tools: de angular-{role} e react-{role} (H3 do plano).",
    )
    assert len(angular) == expected, remediation(
        f"[{role}] esperado {expected} tools playwright/*, encontrado {len(angular)}",
        fix_hint="ajustar tools: conforme tabela de paridade 8.1 do plano (developer=13, test-engineer=18).",
    )


def test_developer_tools_are_subset_of_test_engineer_tools():
    for stack in STACKS:
        dev = _playwright_tools(stack, "developer")
        assert dev <= _playwright_tools(stack, "test-engineer"), remediation(
            f"[{stack}] developer possui tools playwright/* ausentes no test-engineer",
            fix_hint="incluir no test-engineer todas as tools playwright/* do developer.",
        )


@pytest.mark.parametrize("stack", STACKS)
@pytest.mark.parametrize("role", ["developer", "test-engineer"])
def test_agent_catalog_and_agentcard_playwright_tools_in_sync(stack: str, role: str):
    agent = _playwright_tools(stack, role)
    assert agent == _catalog_tools(stack, role), remediation(
        f"[{stack}-{role}] tools playwright/* divergem entre agent.md e {stack}-catalog.yaml",
        fix_hint=f"sincronizar {stack}-catalog.yaml com o frontmatter de {stack}-{role}.agent.md.",
    )
    assert agent == _card_tools(stack, role), remediation(
        f"[{stack}-{role}] tools playwright/* divergem entre agent.md e AgentCard",
        fix_hint="executar: python tools/agentcard_exporter/export_agentcards.py --apply",
    )


@pytest.mark.parametrize("stack", STACKS)
@pytest.mark.parametrize("role", ["arch-advisor", "router"])
def test_advisors_and_routers_have_no_playwright_tools(stack: str, role: str):
    tools = _frontmatter(_agent_path(stack, role)).get("tools", [])
    offending = [t for t in tools if t.startswith("playwright/")]
    assert not offending, remediation(
        f"[{stack}-{role}] não deve declarar tools playwright/*: {offending}",
        fix_hint="remover as tools playwright/* (arch-advisor é read-only; router segue baseline R-054).",
    )


@pytest.mark.parametrize("stack", STACKS)
@pytest.mark.parametrize("role", ["arch-advisor", "developer", "test-engineer"])
def test_source_docs_reference_playwright_and_vfl(stack: str, role: str):
    docs = _frontmatter(_agent_path(stack, role)).get("source_docs", [])
    for required in (PLAYWRIGHT_SKILL, VFL_SKILL):
        assert required in docs, remediation(
            f"[{stack}-{role}] source_docs sem {required}",
            fix_hint=f"adicionar '{required}' em source_docs: de {stack}-{role}.agent.md.",
        )


@pytest.mark.parametrize("stack", STACKS)
def test_arch_advisor_plan_template_has_ui_layout_section(stack: str):
    content = _agent_path(stack, "arch-advisor").read_text(encoding="utf-8")
    assert "### UI/Layout" in content, remediation(
        f"[{stack}-arch-advisor] template de plano sem a seção UI/Layout",
        fix_hint="adicionar '### UI/Layout' (auth strategy, ambiente, origens, viewports, projeto-alvo) ao template R-064.",
    )


def test_router_rules_mention_ui_layout_flow():
    for stack in STACKS:
        content = _agent_path(stack, "router").read_text(encoding="utf-8")
        assert "UI/Layout" in content, remediation(
            f"[{stack}-router] sem regra UI/Layout",
            fix_hint="adicionar a regra UI/Layout (arch-advisor -> developer/test-engineer) ao CRÍTICO e à Decision Tree.",
        )


def test_skills_pin_playwright_mcp_version_and_forbid_floating_tag():
    skill = (SKILLS_DIR / "playwright-mcp" / "SKILL.md").read_text(encoding="utf-8")
    assert PINNED_VERSION.search(skill), remediation(
        "playwright-mcp/SKILL.md sem versão fixa de @playwright/mcp",
        fix_hint="documentar '@playwright/mcp@<x.y.z>' validada na doc oficial (T1).",
    )
    targets = [SKILLS_DIR / "playwright-mcp" / "SKILL.md", SKILLS_DIR / "frontend-visual-feedback-loop" / "SKILL.md"]
    targets += sorted((SKILLS_DIR / "frontend-visual-feedback-loop" / "references").glob("**/*.md"))
    for path in targets:
        assert not FLOATING_TAG.search(path.read_text(encoding="utf-8")), remediation(
            f"[{path.name}] contém tag flutuante '@latest'",
            fix_hint="substituir por @playwright/mcp@<versão fixa> (Decisão 3 do plano).",
        )


def test_idea_mcp_playwright_server_is_pinned():
    config_path = REPO_ROOT / ".config" / "idea_mcp.json"
    if not config_path.is_file():
        pytest.skip(".config/idea_mcp.json ausente (arquivo local)")
    args = json.loads(config_path.read_text(encoding="utf-8"))["servers"]["playwright"]["args"]
    assert not any(FLOATING_TAG.search(a) for a in args), remediation(
        f"idea_mcp.json playwright usa tag flutuante: {args}",
        fix_hint="fixar @playwright/mcp@<versão da skill playwright-mcp> e adicionar --isolated/--storage-state.",
    )
    assert any(PINNED_VERSION.search(a) for a in args), remediation(
        "idea_mcp.json playwright sem versão fixa",
        fix_hint="usar a mesma versão documentada em playwright-mcp/SKILL.md.",
    )


def test_governance_artifacts_have_no_literal_secrets():
    files = [
        SKILLS_DIR / "playwright-mcp" / "SKILL.md",
        SKILLS_DIR / "frontend-visual-feedback-loop" / "SKILL.md",
        REPO_ROOT / ".github" / "agents" / "workflows" / "workflow-ui-layout.md",
    ]
    files += sorted((SKILLS_DIR / "frontend-visual-feedback-loop" / "references").glob("**/*.md"))
    for stack in STACKS:
        for role in ("arch-advisor", "developer", "test-engineer", "router"):
            files.append(_agent_path(stack, role))
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            assert not SECRET_LITERAL.search(line), remediation(
                f"[{path.name}:{number}] possível credencial literal",
                fix_hint="usar apenas o NOME de variável de ambiente (process.env.X); nunca valores.",
            )


def test_ui_layout_workflow_is_auxiliary_and_indexed():
    workflow = REPO_ROOT / ".github" / "agents" / "workflows" / "workflow-ui-layout.md"
    index = (REPO_ROOT / ".github" / "agents" / "workflows.md").read_text(encoding="utf-8")
    assert workflow.is_file(), remediation(
        "workflow-ui-layout.md ausente",
        fix_hint="criar .github/agents/workflows/workflow-ui-layout.md (T9).",
    )
    assert "workflows/workflow-ui-layout.md" in index, remediation(
        "workflows.md não indexa workflow-ui-layout",
        fix_hint="adicionar a seção auxiliar 3.A em workflows.md apontando para workflows/workflow-ui-layout.md.",
    )
    assert "9 Workflows Determinísticos" in index, remediation(
        "lista de workflows canônicos 1-9 foi alterada",
        fix_hint="manter o título '9 Workflows Determinísticos' (H6: workflow auxiliar não numerado).",
    )


def test_source_docs_rules_cover_visual_feedback_loop():
    rules_path = REPO_ROOT / "tools" / "agent_source_docs_sync" / "required_source_docs_rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))["rules"]
    covered = any(
        r.get("condition", {}).get("tools_contains") == "playwright/browser_snapshot"
        and VFL_SKILL in r.get("required_source_docs", [])
        for r in rules
    )
    assert covered, remediation(
        "required_source_docs_rules.json sem regra playwright/browser_snapshot -> VFL",
        fix_hint="adicionar regra com condition.tools_contains=playwright/browser_snapshot e required_source_docs=[VFL] (T10).",
    )


def test_playwright_skill_cites_token_storage_matrix_and_reference_exists():
    skill = (SKILLS_DIR / "playwright-mcp" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("Matriz de Decisão por Local do Token", "sessionStorage", "addInitScript", "storageState", "auth-token-storage-patterns.md"):
        assert needle in skill, remediation(
            f"playwright-mcp/SKILL.md sem '{needle}' (matriz por local do token — Emenda B)",
            fix_hint="restaurar a seção § 7.4 (matriz de decisão por local do token) na skill.",
        )
    reference = SKILLS_DIR / "playwright-mcp" / "references" / "auth-token-storage-patterns.md"
    assert reference.is_file(), remediation(
        "references/auth-token-storage-patterns.md ausente",
        fix_hint="criar a referência B2 com templates genéricos (placeholders <PROJETO>_*).",
    )
    content = reference.read_text(encoding="utf-8")
    assert "<PROJETO>_STORAGE_STATE_PATH" in content and not FLOATING_TAG.search(content)


@pytest.mark.parametrize("stack", STACKS)
def test_arch_advisor_ui_layout_requires_token_storage(stack: str):
    content = _agent_path(stack, "arch-advisor").read_text(encoding="utf-8")
    assert "token_storage" in content, remediation(
        f"[{stack}-arch-advisor] seção UI/Layout sem o campo token_storage",
        fix_hint="adicionar 'token_storage: cookie | localStorage | sessionStorage | indexeddb' na seção UI/Layout.",
    )


@pytest.mark.parametrize("stack", STACKS)
def test_test_engineers_point_to_auth_reference(stack: str):
    content = _agent_path(stack, "test-engineer").read_text(encoding="utf-8")
    assert "auth-token-storage-patterns.md" in content, remediation(
        f"[{stack}-test-engineer] sem ponteiro para a referência de auth por local do token",
        fix_hint="adicionar linha apontando para playwright-mcp/references/auth-token-storage-patterns.md.",
    )
