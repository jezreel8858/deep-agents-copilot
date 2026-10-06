"""Quality Gate de Orçamento de Linhas e Integridade dos Arquivos-Raiz de Instrução.

Garante que:
1. CLAUDE.md respeita o teto orçamentário de linhas (alvo <= 250, teto máximo < 500) e integridade normativa R-001..R-067.
2. .github/copilot-instructions.md respeita o teto orçamentário de linhas (alvo <= 250, teto máximo < 500).
3. Remissões canônicas a catalog.yaml, routing-graph.yaml e .index.json substituem listagens estáticas manuais.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
COPILOT_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
CATALOG_PATH = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
ROUTING_GRAPH_PATH = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"
INDEX_JSON_PATH = REPO_ROOT / ".github" / "skills" / ".index.json"

TARGET_LINE_BUDGET = 250
MAX_LINE_BUDGET = 500


def test_claude_md_line_budget():
    """Valida que CLAUDE.md cumpre o orçamento de linhas (alvo <= 250 e máximo < 500)."""
    assert CLAUDE_PATH.exists(), "CLAUDE.md deve existir na raiz"
    lines = CLAUDE_PATH.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)
    assert total_lines < MAX_LINE_BUDGET, f"CLAUDE.md excedeu teto máximo de 500 linhas: {total_lines}"
    assert total_lines <= TARGET_LINE_BUDGET, f"CLAUDE.md excedeu o orçamento alvo de 250 linhas: {total_lines}"


def test_copilot_instructions_line_budget():
    """Valida que .github/copilot-instructions.md cumpre o orçamento de linhas (alvo <= 250 e máximo < 500)."""
    assert COPILOT_PATH.exists(), "copilot-instructions.md deve existir em .github/"
    lines = COPILOT_PATH.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)
    assert total_lines < MAX_LINE_BUDGET, f"copilot-instructions.md excedeu teto máximo de 500 linhas: {total_lines}"
    assert total_lines <= TARGET_LINE_BUDGET, f"copilot-instructions.md excedeu o orçamento alvo de 250 linhas: {total_lines}"


def test_claude_md_normative_rules_continuity():
    """Valida que CLAUDE.md mantém todas as 67 regras normativas catalogadas (R-001..R-067)."""
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    rule_numbers = [int(n) for n in re.findall(r"\*\*R-(\d{3})", content)]
    assert rule_numbers, "Nenhuma regra R-xxx encontrada em CLAUDE.md"
    assert max(rule_numbers) == 67, f"Maior regra esperada era 67, encontrou {max(rule_numbers)}"
    for r in range(1, 68):
        rule_tag = f"R-{r:03d}"
        assert rule_tag in content, f"Regra {rule_tag} ausente do índice de CLAUDE.md"


def test_claude_md_canonical_remissions():
    """Valida que CLAUDE.md referencia catalog.yaml e routing-graph.yaml em vez de catálogo estático."""
    content = CLAUDE_PATH.read_text(encoding="utf-8")
    assert "catalog.yaml" in content, "CLAUDE.md deve referenciar catalog.yaml"
    assert "routing-graph.yaml" in content, "CLAUDE.md deve referenciar routing-graph.yaml"
    assert ".index.json" in content, "CLAUDE.md deve referenciar .index.json"
    assert "governance-factory-patterns" in content, "CLAUDE.md deve apontar para governance-factory-patterns"
    assert "harness-engineering-patterns" in content, "CLAUDE.md deve apontar para harness-engineering-patterns"


def test_copilot_instructions_canonical_remissions():
    """Valida que copilot-instructions.md aponta para fontes canônicas e não contém listagem estática manual de agents."""
    content = COPILOT_PATH.read_text(encoding="utf-8")
    assert "catalog.yaml" in content, "copilot-instructions.md deve referenciar catalog.yaml"
    assert ".index.json" in content, "copilot-instructions.md deve referenciar .index.json"
    assert "CLAUDE.md" in content, "copilot-instructions.md deve referenciar CLAUDE.md"
    # Não deve ter o header antigo de listagem estática
    assert "### Agents atuais" not in content, "Listagem estática manual de agents deve ser removida"
    assert "### Skills atuais" not in content, "Listagem estática manual de skills deve ser removida"
