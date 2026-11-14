"""
test_perf_tuner_safety_gate.py — Validação determinística do gate de segurança e baseline
em especialistas perf-tuner de todas as stacks de backend.

Quality Gate que garante:
1. Todos os 5 <stack>-perf-tuner.agent.md formalizam a obrigatoriedade de medir baseline
   antes e comparar com o resultado após a mudança (delta mensurável).
2. Todos os 5 <stack>-perf-tuner.agent.md contêm cláusula restritiva explícita (❌)
   proibindo aplicação irrevogável em produção sem validação em canary/staging e
   aprovação humana explícita.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"

PERF_TUNER_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts"]


def resolve_perf_tuner_file(stack: str) -> Path:
    if stack in ("spring-boot", "spring-reactive", "ejb", "struts", "python"):
        return AGENTS_BACKEND_DIR / stack / f"{stack}-developer.agent.md"
    return AGENTS_BACKEND_DIR / stack / f"{stack}-perf-tuner.agent.md"


@pytest.mark.parametrize("stack", PERF_TUNER_STACKS)
def test_perf_tuner_baseline_measured_before_and_after(stack: str):
    """
    Valida que o <stack>-perf-tuner.agent.md formaliza a exigência de medir
    baseline mensurado ANTES da mudança e comparar APÓS com relatório de delta.
    """
    pt_path = resolve_perf_tuner_file(stack)
    assert pt_path.exists(), remediation(
        f"Arquivo do perf-tuner não encontrado: {pt_path}",
        fix_hint=f"Verifique a existência do agente {stack}-perf-tuner.agent.md."
    )

    content = pt_path.read_text(encoding="utf-8")

    # (a) Baseline mensurado antes/depois
    has_baseline_clause = bool(
        re.search(
            r"-\s*✅\s*[^\n]*(?:medir\s+)?baseline\s+mensurado\s+ANTES.*?AP[ÓO]S",
            content,
            re.IGNORECASE | re.DOTALL,
        )
    )
    assert has_baseline_clause, remediation(
        f"[{pt_path.name}] Cláusula de medição de baseline antes/depois ausente.",
        fix_hint=(
            "Adicione a diretriz: '✅ Medir baseline mensurado ANTES da mudança "
            "(profiling/benchmark/métrica objetiva) e comparar com o resultado APÓS a mudança, "
            "documentando o delta.'"
        ),
    )


@pytest.mark.parametrize("stack", PERF_TUNER_STACKS)
def test_perf_tuner_prohibition_production_without_canary_staging_gate(stack: str):
    """
    Valida que o <stack>-perf-tuner.agent.md contém cláusula restritiva explícita (❌)
    proibindo aplicação de mudança de performance irrevogável direto em produção
    sem canary/staging e aprovação humana explícita.
    """
    pt_path = resolve_perf_tuner_file(stack)
    assert pt_path.exists(), remediation(
        f"Arquivo do perf-tuner não encontrado: {pt_path}",
        fix_hint=f"Verifique a existência do agente {stack}-perf-tuner.agent.md."
    )

    content = pt_path.read_text(encoding="utf-8")

    # (b) Cláusula ❌ proibindo produção sem canary/staging/aprovação humana
    has_prohibition_clause = bool(
        re.search(
            r"-\s*❌\s*[^\n]*(?:produ[çc][ãa]o|irrevog[áa]vel)[^\n]*(?:canary|staging|aprova[çc][ãa]o\s+humana)",
            content,
            re.IGNORECASE,
        )
    )
    assert has_prohibition_clause, remediation(
        f"[{pt_path.name}] Cláusula proibitiva (❌) de produção sem canary/staging/aprovação humana ausente.",
        fix_hint=(
            "Adicione a proibição: '❌ NÃO aplicar mudança de performance irrevogável direto em produção "
            "sem validação em canary/staging e aprovação humana explícita (ask_questions)...'"
        ),
    )
