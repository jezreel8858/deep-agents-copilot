"""
test_r064_author_resolution.py — Validação determinística da autoria do Plano de Implementação (R-064) no WORKFLOW-BUG-FIX.

Garante que:
1. O agente bug-triage (.github/agents/bug-triage.agent.md) delega a autoria técnica do Plano de Implementação
   (docs/implementation-plans/, R-064) dinamicamente para <stack>-arch-advisor (via domain-router da stack).
2. Veda terminantemente @tech-solution-architect para essa finalidade no WORKFLOW-BUG-FIX,
   restringindo sua atuação ao estado WF1_SECURITY_CHECKPOINT (parecer de segurança read-only).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
BUG_TRIAGE_FILE = REPO_ROOT / ".github" / "agents" / "bug-triage.agent.md"


def _extract_delegation_table(content: str) -> str:
    """Extrai a tabela ou bloco da seção 'Quando Delegar'."""
    match = re.search(r"##\s+Quando Delegar\s*\n([\s\S]*?)(?:\n<execution_protocol>|\n##|\Z)", content)
    assert match, remediation(
        "Seção '## Quando Delegar' não encontrada em bug-triage.agent.md",
        fix_hint="Certifique-se de que a seção '## Quando Delegar' existe no arquivo bug-triage.agent.md."
    )
    return match.group(1)


def test_bug_triage_delegates_implementation_plan_to_generic_stack_arch_advisor():
    """Valida que bug-triage associa o Plano de Implementação / R-064 a <stack>-arch-advisor dinâmico."""
    assert BUG_TRIAGE_FILE.exists(), remediation(
        f"Arquivo {BUG_TRIAGE_FILE} não existe",
        fix_hint="Restaurar o arquivo .github/agents/bug-triage.agent.md"
    )
    content = BUG_TRIAGE_FILE.read_text(encoding="utf-8")
    delegation_text = _extract_delegation_table(content)

    plan_lines = [
        line for line in delegation_text.splitlines()
        if "Plano de Implementação" in line or "implementation-plans" in line
    ]
    assert plan_lines, remediation(
        "Nenhuma linha sobre 'Plano de Implementação' encontrada na tabela 'Quando Delegar' de bug-triage.agent.md",
        fix_hint="Adicionar linha na tabela 'Quando Delegar' cobrindo autoria do Plano de Implementação (R-064)."
    )

    matched_line = plan_lines[0]
    assert "<stack>-arch-advisor" in matched_line, remediation(
        "A delegação do Plano de Implementação não referencia '<stack>-arch-advisor' dinâmico",
        fix_hint="Atualizar a linha na tabela 'Quando Delegar' para apontar para '<stack>-arch-advisor'."
    )
    assert "R-064" in matched_line, remediation(
        "A linha de delegação do Plano de Implementação deve referenciar formalmente a regra R-064",
        fix_hint="Incluir a sigla '(R-064)' na descrição da delegação em bug-triage.agent.md."
    )
    assert "docs/implementation-plans/" in matched_line, remediation(
        "A linha de delegação deve citar o diretório canônico 'docs/implementation-plans/'",
        fix_hint="Incluir 'docs/implementation-plans/' na coluna de situação da tabela 'Quando Delegar'."
    )


def test_bug_triage_forbids_tech_solution_architect_for_implementation_plan():
    """Valida proibição expressa de @tech-solution-architect para materialização de Plano de Implementação no bug-triage."""
    assert BUG_TRIAGE_FILE.exists()
    content = BUG_TRIAGE_FILE.read_text(encoding="utf-8")
    delegation_text = _extract_delegation_table(content)

    plan_lines = [
        line for line in delegation_text.splitlines()
        if "Plano de Implementação" in line or "implementation-plans" in line
    ]
    assert plan_lines, "Linha de Plano de Implementação deve existir na tabela de delegação"
    matched_line = plan_lines[0]

    assert re.search(r"\bNUNCA\b.*@tech-solution-architect", matched_line), remediation(
        "Vedação explícita 'NUNCA @tech-solution-architect' não encontrada na delegação do Plano de Implementação",
        fix_hint="Declarar explicitamente '**NUNCA** `@tech-solution-architect` para esta finalidade' na linha de R-064."
    )
    assert "WF1_SECURITY_CHECKPOINT" in matched_line, remediation(
        "Referência a WF1_SECURITY_CHECKPOINT ausente na linha do Plano de Implementação",
        fix_hint="Esclarecer que tech-solution-architect só atua no WORKFLOW-BUG-FIX via estado WF1_SECURITY_CHECKPOINT."
    )
