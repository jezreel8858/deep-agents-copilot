"""
test_spring_boot_consolidation.py — Validação determinística da consolidação
da stack Spring Boot no Padrão Triádico Canônico (3 especialistas + 1 router).

Quality Gates:
1. QG-01: Exatamente 3 especialistas e 1 router presentes no diretório backend/spring-boot/.
2. QG-02: spring-boot-router possui exatamente as 7 tools canônicas do Baseline R-054.
3. QG-03: Zero referências residuais aos especialistas legados em catalog.yaml e routing-graph.yaml.
4. QG-04: Sub-catálogo local spring-boot-catalog.yaml registra exatamente os 3 novos especialistas e 1 router.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SB_DIR = AGENTS_DIR / "backend" / "spring-boot"
CATALOG_PATH = AGENTS_DIR / "catalog.yaml"
ROUTING_GRAPH_PATH = AGENTS_DIR / "routing-graph.yaml"
SB_CATALOG_PATH = SB_DIR / "spring-boot-catalog.yaml"

EXPECTED_FILES = {
    "spring-boot-arch-advisor.agent.md",
    "spring-boot-developer.agent.md",
    "spring-boot-test-engineer.agent.md",
    "spring-boot-router.agent.md",
    "spring-boot-catalog.yaml",
}

LEGACY_AGENT_IDS = [
    "spring-boot-feature-developer",
    "spring-boot-bug-fixer",
    "spring-boot-perf-tuner",
    "spring-boot-unit-test-writer",
    "spring-boot-integration-test-writer",
    "spring-boot-test-fixer",
]

R054_CANONICAL_ROUTER_TOOLS = {
    "read_file",
    "file_search",
    "grep_search",
    "list_dir",
    "ask_questions",
    "run_subagent",
    "context-mode/ctx_search",
}


def test_qg01_spring_boot_directory_has_exact_triad_files():
    """Valida presença exata de 3 especialistas, 1 router e 1 catalog na stack spring-boot."""
    actual_files = {p.name for p in SB_DIR.iterdir() if p.is_file()}
    assert actual_files == EXPECTED_FILES, (
        f"Divergência de arquivos em {SB_DIR}. Esperados: {EXPECTED_FILES}, Encontrados: {actual_files}"
    )


def test_qg02_spring_boot_router_preserves_r054_tools():
    """Valida que spring-boot-router preserva exatamente as 7 tools canônicas sob R-054."""
    router_file = SB_DIR / "spring-boot-router.agent.md"
    content = router_file.read_text(encoding="utf-8")
    frontmatter = content.split("---")[1]
    parsed = yaml.safe_load(frontmatter)

    tools = set(parsed.get("tools", []))
    assert tools == R054_CANONICAL_ROUTER_TOOLS, (
        f"spring-boot-router DEVE conter as 7 tools canônicas R-054. Encontrado: {tools}"
    )


def test_qg03_zero_legacy_references_in_catalogs_and_graph():
    """Garante expurgo total dos 6 especialistas legados em catalog.yaml e routing-graph.yaml."""
    cat_text = CATALOG_PATH.read_text(encoding="utf-8")
    graph_text = ROUTING_GRAPH_PATH.read_text(encoding="utf-8")

    for legacy_id in LEGACY_AGENT_IDS:
        assert legacy_id not in cat_text, (
            f"Referência residual ao agente legado '{legacy_id}' encontrada em {CATALOG_PATH.name}"
        )
        assert legacy_id not in graph_text, (
            f"Referência residual ao agente legado '{legacy_id}' encontrada em {ROUTING_GRAPH_PATH.name}"
        )


def test_qg04_spring_boot_subcatalog_has_exact_triad_agents():
    """Valida que spring-boot-catalog.yaml registra exatamente os 3 novos especialistas e 1 router."""
    parsed = yaml.safe_load(SB_CATALOG_PATH.read_text(encoding="utf-8"))
    assert parsed.get("router", {}).get("id") == "spring-boot-router"

    registered_agents = set(parsed.get("agents", {}).keys())
    expected_agents = {
        "spring-boot-arch-advisor",
        "spring-boot-developer",
        "spring-boot-test-engineer",
    }
    assert registered_agents == expected_agents, (
        f"spring-boot-catalog.yaml deve registrar exatamente {expected_agents}. Encontrado: {registered_agents}"
    )
