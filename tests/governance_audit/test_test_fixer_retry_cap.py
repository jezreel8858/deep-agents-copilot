"""
test_test_fixer_retry_cap.py — Validação determinística da heurística de classificação
e teto numérico de tentativas (retry cap) em especialistas test-fixer.

Quality Gate que garante:
1. Todos os 6 <stack>-test-fixer.agent.md contêm a heurística de classificação binária:
   "bug real na aplicação" (com handoff para <stack>-bug-fixer) vs.
   "drift de implementação/flakiness" (corrigir o teste).
2. Todos os 6 <stack>-test-fixer.agent.md contêm cláusula restritiva explícita (❌)
   com cap numérico explícito (máximo 2 tentativas) antes de escalar para @bug-triage.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"
AGENTS_FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"

ALL_TEST_FIXER_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts", "angular"]


def resolve_test_fixer_file(stack: str) -> Path:
    if stack == "angular":
        return AGENTS_FRONTEND_DIR / "angular" / "angular-test-engineer.agent.md"
    if stack in ("spring-boot", "spring-reactive", "ejb", "struts", "python"):
        return AGENTS_BACKEND_DIR / stack / f"{stack}-test-engineer.agent.md"
    return AGENTS_BACKEND_DIR / stack / f"{stack}-test-fixer.agent.md"


@pytest.mark.parametrize("stack", ALL_TEST_FIXER_STACKS)
def test_test_fixer_classification_heuristic_and_bug_fixer_handoff(stack: str):
    """
    Valida que o <stack>-test-fixer.agent.md possui a heurística de classificação binária
    (bug real vs drift/flakiness) e formaliza handoff para o bug-fixer da stack.
    """
    tf_path = resolve_test_fixer_file(stack)
    assert tf_path.exists(), remediation(
        f"Arquivo do test-fixer não encontrado: {tf_path}",
        fix_hint=f"Verifique a existência do agente {stack}-test-fixer.agent.md."
    )

    content = tf_path.read_text(encoding="utf-8")

    # (a) Classificação binária: bug real vs drift/flakiness
    has_classification = bool(
        re.search(
            r"classificar.*?(?:bug\s+real).*?(?:drift|flakiness)",
            content,
            re.IGNORECASE | re.DOTALL,
        )
    )
    assert has_classification, remediation(
        f"[{tf_path.name}] Heurística de classificação binária (bug real vs drift/flakiness) ausente.",
        fix_hint=(
            "Adicione a diretriz: '✅ Antes de corrigir, classificar a falha como \"teste quebrado "
            "por bug real na aplicação\" (...) vs. \"teste quebrado por drift de implementação/flakiness\"...'"
        ),
    )

    # Handoff formal para o bug-fixer da respectiva stack
    expected_bug_fixer = f"{stack}-developer" if stack in ("spring-boot", "spring-reactive", "angular", "ejb", "struts", "python") else f"{stack}-bug-fixer"
    has_handoff = bool(
        re.search(
            rf"handoff\s+para\s+[`@]*{re.escape(expected_bug_fixer)}",
            content,
            re.IGNORECASE,
        )
    )
    assert has_handoff, remediation(
        f"[{tf_path.name}] Handoff para @{expected_bug_fixer} não formalizado na classificação.",
        fix_hint=f"Formalize o handoff explicitamente: 'handoff para `@{expected_bug_fixer}`, NÃO corrigir o teste'."
    )


@pytest.mark.parametrize("stack", ALL_TEST_FIXER_STACKS)
def test_test_fixer_retry_cap_and_escalation(stack: str):
    """
    Valida que o <stack>-test-fixer.agent.md possui cap numérico explícito (2 tentativas)
    e regra de escalada (handoff para @bug-triage com ask_questions).
    """
    tf_path = resolve_test_fixer_file(stack)
    assert tf_path.exists(), remediation(
        f"Arquivo do test-fixer não encontrado: {tf_path}",
        fix_hint=f"Verifique a existência do agente {stack}-test-fixer.agent.md."
    )

    content = tf_path.read_text(encoding="utf-8")

    # (b) Cap numérico explícito (2 tentativas / CAP RÍGIDO)
    has_cap = bool(
        re.search(
            r"-\s*❌\s*[^\n]*(?:CAP\s+R[ÍI]GIDO|[Cc][Aa][Pp])[^\n]*2\s+tentativas",
            content,
        )
    )
    assert has_cap, remediation(
        f"[{tf_path.name}] Cláusula proibitiva com CAP numérico explícito (2 tentativas) ausente.",
        fix_hint=(
            "Adicione a cláusula: '❌ NÃO tentar auto-correção indefinidamente — CAP RÍGIDO "
            "de no máximo 2 tentativas de correção do mesmo teste; se falhar novamente, escalar...'"
        ),
    )

    # Escalação para bug-triage
    has_escalation = bool(
        re.search(
            r"escalar\s+para\s+[`@]*bug-triage",
            content,
            re.IGNORECASE,
        )
    )
    assert has_escalation, remediation(
        f"[{tf_path.name}] Escalação para @bug-triage após exaustão do cap ausente.",
        fix_hint="Adicione a instrução de escalação para '@bug-triage' com ask_questions."
    )
