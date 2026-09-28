"""
test_test_writer_mutation_awareness.py — Validação determinística de sensibilidade
a mutação e valores de fronteira em especialistas test-writer de todas as stacks.

Quality Gate que garante:
1. Todos os especialistas test-writer (unit-test-writer, integration-test-writer,
   component-test-writer) dos 6 stacks contêm menção a "boundary" / "valores de fronteira"
   ou "casos de borda".
2. Todos os test-writers mencionam "mutation score" ou "mutation testing" na diretriz
   de critério de aceite / cobertura qualitativa.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"
AGENTS_FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"

TEST_WRITER_TARGETS = [
    ("ejb", "ejb-unit-test-writer.agent.md", AGENTS_BACKEND_DIR / "ejb"),
    ("ejb", "ejb-integration-test-writer.agent.md", AGENTS_BACKEND_DIR / "ejb"),
    ("spring-boot", "spring-boot-unit-test-writer.agent.md", AGENTS_BACKEND_DIR / "spring-boot"),
    ("spring-boot", "spring-boot-integration-test-writer.agent.md", AGENTS_BACKEND_DIR / "spring-boot"),
    ("spring-reactive", "spring-reactive-unit-test-writer.agent.md", AGENTS_BACKEND_DIR / "spring-reactive"),
    ("spring-reactive", "spring-reactive-integration-test-writer.agent.md", AGENTS_BACKEND_DIR / "spring-reactive"),
    ("python", "python-unit-test-writer.agent.md", AGENTS_BACKEND_DIR / "python"),
    ("python", "python-integration-test-writer.agent.md", AGENTS_BACKEND_DIR / "python"),
    ("struts", "struts-unit-test-writer.agent.md", AGENTS_BACKEND_DIR / "struts"),
    ("struts", "struts-integration-test-writer.agent.md", AGENTS_BACKEND_DIR / "struts"),
    ("angular", "angular-unit-test-writer.agent.md", AGENTS_FRONTEND_DIR / "angular"),
    ("angular", "angular-component-test-writer.agent.md", AGENTS_FRONTEND_DIR / "angular"),
]


@pytest.mark.parametrize("stack,filename,parent_dir", TEST_WRITER_TARGETS)
def test_test_writer_boundary_values_and_mutation_awareness(stack: str, filename: str, parent_dir: Path):
    """
    Valida que cada especialista test-writer dos 6 stacks formaliza:
    (a) Menção a boundary values / valores de fronteira / casos de borda;
    (b) Menção a mutation score / mutation testing na cláusula de qualidade.
    """
    writer_path = parent_dir / filename
    assert writer_path.exists(), remediation(
        f"Arquivo do test-writer não encontrado: {writer_path}",
        fix_hint=f"Verifique a existência do agente {filename} em {parent_dir}."
    )

    content = writer_path.read_text(encoding="utf-8")

    # (a) Menção a boundary / valores de fronteira / casos de borda
    has_boundary = bool(
        re.search(
            r"boundary(?:\s+values)?|valores\s+de\s+fronteira|casos\s+de\s+borda",
            content,
            re.IGNORECASE,
        )
    )
    assert has_boundary, remediation(
        f"[{filename}] Menção a 'boundary values' / 'valores de fronteira' ausente.",
        fix_hint=(
            "Adicione diretriz de cobertura qualitativa exigindo 'valores de fronteira "
            "(boundary values) e casos de borda de regra de negócio'."
        ),
    )

    # (b) Menção a mutation score / mutation testing
    has_mutation = bool(
        re.search(
            r"mutation(?:\s+score|\s+testing)?",
            content,
            re.IGNORECASE,
        )
    )
    assert has_mutation, remediation(
        f"[{filename}] Menção a 'mutation score' / 'mutation testing' ausente.",
        fix_hint=(
            "Adicione diretriz de qualidade exigindo 'considerar mutation score "
            "(quando ferramenta de mutation testing estiver disponível no projeto)'."
        ),
    )
