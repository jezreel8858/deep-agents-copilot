"""
test_feature_developer_test_authoring_boundary.py — Validação determinística da barreira
de responsabilidade de autoria de testes para feature-developers de backend e frontend.

Quality Gate que garante:
1. Os <stack>-feature-developer.agent.md contêm cláusula restritiva explícita (❌)
   proibindo a autoria de classes/arquivos de teste unitário ou de integração/componente.
2. Os <stack>-feature-developer.agent.md contêm diretriz obrigatória de handoff para
   unit-test-writer, integration-test-writer ou component-test-writer da respectiva stack.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"
AGENTS_FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"

ALL_FEATURE_DEV_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts", "angular"]


def resolve_feature_developer_file(stack: str) -> Path:
    """Resolve o arquivo feature-developer da stack (backend ou frontend)."""
    if stack == "angular":
        return AGENTS_FRONTEND_DIR / "angular" / "angular-feature-developer.agent.md"
    return AGENTS_BACKEND_DIR / stack / f"{stack}-feature-developer.agent.md"


@pytest.mark.parametrize("stack", ALL_FEATURE_DEV_STACKS)
def test_feature_developer_has_test_authoring_prohibition_and_handoff(stack: str):
    """
    Valida que o <stack>-feature-developer.agent.md:
    (a) proíbe autoria/geração de testes unitários, integração ou componente (marcador ❌);
    (b) formaliza handoff para unit-test-writer, integration-test-writer ou component-test-writer.
    """
    feat_dev_path = resolve_feature_developer_file(stack)
    assert feat_dev_path.exists(), f"Arquivo não encontrado: {feat_dev_path}"

    content = feat_dev_path.read_text(encoding="utf-8")

    # (a) Cláusula proibindo autoria de testes
    has_prohibition = bool(
        re.search(
            r"❌\s*NÃO\s+(?:escrever|gerar|autora).*(?:teste\s+unit[aá]rio|teste\s+de\s+integra[çc][aã]o|teste\s+de\s+componente|classes?\s+de\s+teste|arquivos?\s+\.spec\.ts)",
            content,
            re.IGNORECASE,
        )
    )
    assert has_prohibition, (
        f"{feat_dev_path.name} DEVE conter cláusula com '❌ NÃO' proibindo autoria "
        f"de testes unitários, de integração ou de componentes."
    )

    # (b) Handoff para unit-test-writer, integration-test-writer ou component-test-writer
    has_test_writer_handoff = bool(
        re.search(r"unit-test-writer|integration-test-writer|component-test-writer", content, re.IGNORECASE)
    )
    assert has_test_writer_handoff, (
        f"{feat_dev_path.name} DEVE citar explicitamente handoff ou delegação para "
        f"unit-test-writer, integration-test-writer ou component-test-writer da respectiva stack."
    )
