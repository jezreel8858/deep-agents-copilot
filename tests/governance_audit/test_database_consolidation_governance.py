"""
test_database_consolidation_governance.py — Validação determinística da consolidação
da stack Database (Padrão Triádico 3+1 — Fase 3 do Plano de Governança).

Quality Gate que garante:
1. Topologia estrita: o diretório .github/agents/backend/database/ contém exatamente
   os 4 agentes (1 supervisor + 3 especialistas) e 1 sub-catálogo.
2. Eliminação completa dos 6 especialistas legados e subpastas oracle/ e informix/.
3. Sub-catálogo database-catalog.yaml consolidado com 3 especialistas (database-arch-advisor,
   oracle-database-specialist, informix-database-specialist).
4. Decision Tree de 3 branches em database-router.agent.md preservando baseline R-054.
5. database-arch-advisor é read-only com perfil Gather-only.
6. oracle-database-specialist e informix-database-specialist são executores com R-046 e Zero-Noise.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_DIR = REPO_ROOT / ".github" / "agents" / "backend" / "database"
CATALOG_FILE = DB_DIR / "database-catalog.yaml"
ROUTER_FILE = DB_DIR / "database-router.agent.md"
ARCH_FILE = DB_DIR / "database-arch-advisor.agent.md"
ORA_FILE = DB_DIR / "oracle-database-specialist.agent.md"
INF_FILE = DB_DIR / "informix-database-specialist.agent.md"

EXPECTED_FILES = {
    "database-router.agent.md",
    "database-arch-advisor.agent.md",
    "oracle-database-specialist.agent.md",
    "informix-database-specialist.agent.md",
    "database-catalog.yaml"
}

LEGACY_AGENT_FILES = [
    "oracle-migration-dev.agent.md",
    "oracle-plsql-expert.agent.md",
    "oracle-query-tuner.agent.md",
    "informix-migration-dev.agent.md",
    "informix-spl-expert.agent.md",
    "informix-query-tuner.agent.md"
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


def test_database_directory_file_count_and_composition():
    """Valida que existem exatamente os 5 arquivos canônicos no diretório database."""
    assert DB_DIR.exists(), f"Diretório Database não encontrado: {DB_DIR}"
    current_files = {p.name for p in DB_DIR.iterdir() if p.is_file()}
    assert current_files == EXPECTED_FILES, remediation(
        f"Composição inesperada no diretório Database: {current_files ^ EXPECTED_FILES}",
        fix_hint="Certifique-se de manter apenas router, arch-advisor, oracle-specialist, informix-specialist e catalog.yaml."
    )
    # Garante que não há subpastas residuais oracle/ ou informix/
    subdirs = [p.name for p in DB_DIR.iterdir() if p.is_dir()]
    assert len(subdirs) == 0, f"Subdiretórios residuais encontrados em {DB_DIR}: {subdirs}"


def test_database_catalog_triadic_structure():
    """Valida que database-catalog.yaml declara os 3 especialistas da tríade e o router."""
    assert CATALOG_FILE.exists()
    data = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or {}
    assert data.get("router", {}).get("id") == "database-router"
    agents = data.get("agents", {})
    assert len(agents) == 3, f"database-catalog.yaml deve conter exatamente 3 especialistas, encontrados {len(agents)}"
    assert "database-arch-advisor" in agents
    assert "oracle-database-specialist" in agents
    assert "informix-database-specialist" in agents


def test_database_router_preserves_r054_tools():
    """Valida que database-router preserva exatamente as 7 tools canônicas sob R-054."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    frontmatter = content.split("---")[1]
    parsed = yaml.safe_load(frontmatter)

    tools = set(parsed.get("tools", []))
    assert tools == R054_CANONICAL_ROUTER_TOOLS, (
        f"database-router DEVE conter as 7 tools canônicas R-054. Encontrado: {tools}"
    )


def test_database_router_three_branches_decision_tree():
    """Valida que database-router.agent.md despacha para os 3 especialistas canônicos."""
    assert ROUTER_FILE.exists()
    content = ROUTER_FILE.read_text(encoding="utf-8")
    assert "@database-arch-advisor" in content
    assert "@oracle-database-specialist" in content
    assert "@informix-database-specialist" in content
    assert "3 especialistas" in content.lower() or "3 Especialistas" in content


def test_database_arch_advisor_is_gather_only():
    """Valida que database-arch-advisor não possui ferramentas mutativas ou de execução pesada."""
    assert ARCH_FILE.exists()
    content = ARCH_FILE.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---")[1])
    tools = set(frontmatter.get("tools", []))
    assert "context-mode/ctx_execute" not in tools
    assert "context-mode/ctx_execute_file" not in tools
    assert "context-mode/ctx_batch_execute" in tools


def test_database_executors_declare_r046_and_zero_noise():
    """Valida R-046 e Zero-Noise Test Policy nos especialistas executores de Oracle e Informix."""
    for file_path in [ORA_FILE, INF_FILE]:
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert "r-046" in content.lower() or "idempotência" in content.lower()
        assert "Zero-Noise Test Policy (terminal-governance/SKILL.md §3.1)" in content
