"""
test_hybrid_model_routing_and_zero_noise_governance.py — Quality Gate Determinístico de Modelo Híbrido e Política Zero-Noise.

Valida as seguintes garantias de governança:
(a) Qualquer agent com papel feature-developer, bug-fixer ou test-fixer DEVE utilizar o modelo "Claude Sonnet 5";
(b) Qualquer agent com papel test-writer (unit/integration/component) DEVE utilizar o modelo "Gemini 3.8 Flash";
(c) Todos os 30 agents executores DEVEM declarar '.github/skills/terminal-governance/SKILL.md' em source_docs;
(d) Todos os 30 agents executores DEVEM citar expressamente 'Zero-Noise Test Policy (terminal-governance/SKILL.md §3.1)';
(e) .github/copilot-instructions.md DEVE formalizar a regra R-021.2 (Retry-Rate Model Escalation).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml
from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"

PROMOTED_ROLES = ("feature-developer", "bug-fixer", "test-fixer")
TEST_WRITER_ROLES = ("unit-test-writer", "integration-test-writer", "component-test-writer")

PROMOTED_AGENTS = [
    "angular-feature-developer", "angular-bug-fixer", "angular-test-fixer",
    "spring-boot-feature-developer", "spring-boot-bug-fixer", "spring-boot-test-fixer",
    "spring-reactive-feature-developer", "spring-reactive-bug-fixer", "spring-reactive-test-fixer",
    "ejb-feature-developer", "ejb-bug-fixer", "ejb-test-fixer",
    "python-feature-developer", "python-bug-fixer", "python-test-fixer",
    "struts-feature-developer", "struts-bug-fixer", "struts-test-fixer",
]

TEST_WRITER_AGENTS = [
    "angular-component-test-writer", "angular-unit-test-writer",
    "spring-boot-integration-test-writer", "spring-boot-unit-test-writer",
    "spring-reactive-integration-test-writer", "spring-reactive-unit-test-writer",
    "ejb-integration-test-writer", "ejb-unit-test-writer",
    "python-integration-test-writer", "python-unit-test-writer",
    "struts-integration-test-writer", "struts-unit-test-writer",
]

ALL_30_EXECUTORS = PROMOTED_AGENTS + TEST_WRITER_AGENTS


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def get_executor_agent_files() -> list[Path]:
    files = []
    for p in AGENTS_DIR.glob("**/*.agent.md"):
        if "templates" in p.parts:
            continue
        stem = p.name.replace(".agent.md", "")
        if stem in ALL_30_EXECUTORS:
            files.append(p)
    return files


def test_promoted_executor_agents_use_claude_sonnet_5():
    """Valida (a): feature-developer, bug-fixer e test-fixer devem usar Claude Sonnet 5."""
    agent_files = get_executor_agent_files()
    assert len(agent_files) == 30, f"Esperados 30 agents executores, encontrados {len(agent_files)}"

    for agent_file in agent_files:
        stem = agent_file.name.replace(".agent.md", "")
        if stem in PROMOTED_AGENTS:
            content = agent_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            model = fm.get("model")
            assert model == "Claude Sonnet 5", remediation(
                f"Agent '{stem}' possui model '{model}' no frontmatter, esperado 'Claude Sonnet 5'",
                fix_hint=f"Edite {agent_file.relative_to(REPO_ROOT)} definindo model: \"Claude Sonnet 5\""
            )


def test_test_writers_use_gemini_38_flash():
    """Valida (b): test-writers (unit/integration/component) devem usar Gemini 3.8 Flash."""
    agent_files = get_executor_agent_files()
    for agent_file in agent_files:
        stem = agent_file.name.replace(".agent.md", "")
        if stem in TEST_WRITER_AGENTS:
            content = agent_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            model = fm.get("model")
            assert model == "Gemini 3.8 Flash", remediation(
                f"Agent '{stem}' possui model '{model}' no frontmatter, esperado 'Gemini 3.8 Flash'",
                fix_hint=f"Edite {agent_file.relative_to(REPO_ROOT)} definindo model: \"Gemini 3.8 Flash\""
            )


def test_all_30_executors_declare_terminal_governance_in_source_docs():
    """Valida (c): Todos os 30 agents executores devem referenciar terminal-governance/SKILL.md em source_docs."""
    agent_files = get_executor_agent_files()
    for agent_file in agent_files:
        stem = agent_file.name.replace(".agent.md", "")
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        source_docs = fm.get("source_docs") or []
        has_tg = any("terminal-governance/SKILL.md" in doc for doc in source_docs)
        assert has_tg, remediation(
            f"Agent '{stem}' não referencia .github/skills/terminal-governance/SKILL.md em source_docs",
            fix_hint=f"Adicione '.github/skills/terminal-governance/SKILL.md' em source_docs de {agent_file.relative_to(REPO_ROOT)}"
        )


def test_all_30_executors_cite_zero_noise_test_policy_literal():
    """Valida conformidade textual da menção explícita à Zero-Noise Test Policy."""
    agent_files = get_executor_agent_files()
    expected_phrase = "Zero-Noise Test Policy (terminal-governance/SKILL.md §3.1)"
    for agent_file in agent_files:
        stem = agent_file.name.replace(".agent.md", "")
        content = agent_file.read_text(encoding="utf-8")
        assert expected_phrase in content, remediation(
            f"Agent '{stem}' não cita literalmente '{expected_phrase}'",
            fix_hint=f"Padronize o bullet de testes em {agent_file.relative_to(REPO_ROOT)} com '{expected_phrase}'"
        )


def test_stack_catalogs_model_parity_for_promoted_agents():
    """Valida paridade de catálogo: *-catalog.yaml deve refletir 'Claude Sonnet 5' para os 18 promovidos."""
    catalog_files = list(AGENTS_DIR.glob("**/*-catalog.yaml"))
    for cat in catalog_files:
        content = cat.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
        agents_dict = data.get("agents") or {}
        for agent_id, agent_info in agents_dict.items():
            if agent_id in PROMOTED_AGENTS:
                model = agent_info.get("model")
                assert model == "Claude Sonnet 5", remediation(
                    f"Catálogo {cat.relative_to(REPO_ROOT)} declara model '{model}' para '{agent_id}', esperado 'Claude Sonnet 5'",
                    fix_hint=f"Atualize a entrada de '{agent_id}' no catálogo {cat.relative_to(REPO_ROOT)} para model: 'Claude Sonnet 5'"
                )


def test_copilot_instructions_has_retry_rate_escalation_rule():
    """Valida formalização da regra R-021.2 no arquivo normativo principal."""
    content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
    assert "R-021.2" in content, remediation(
        "Regra R-021.2 não encontrada em .github/copilot-instructions.md",
        fix_hint="Adicione a seção da Nota R-021.2 logo após R-021.1 em .github/copilot-instructions.md"
    )
    assert "Retry-Rate Escalation" in content, remediation(
        "Menção textual 'Retry-Rate Escalation' não encontrada em .github/copilot-instructions.md",
        fix_hint="Certifique-se de nomear a nota como 'Nota (R-021.2 — Retry-Rate Escalation)'"
    )
