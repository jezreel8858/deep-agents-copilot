"""
test_r065_severity_guard.py — Validação determinística do Guard de Severidade Arquitetural (R-065).

Garante que:
1. workflows.md § 1.5 (Loop de Revisão de Qualidade) formaliza a regra normativa R-065.
2. O texto de R-065 cobre expressamente as 3 categorias arquiteturais bloqueantes que NUNCA entram no loop:
   - Contract Testing / API pública (WORKFLOW-REFACTORING)
   - blueprint / Sprint Contract do tech-solution-architect ou <stack>-arch-advisor (WORKFLOW-FEATURE-DEVELOPMENT)
   - Matriz De-Para / Symbol Exhaustion Gate (WORKFLOW-FRAMEWORK-MIGRATION)
3. Os 3 avaliadores céticos canônicos (code-review.agent.md, adr-sentinel.agent.md, security-reviewer.agent.md)
   mantêm isolamento estrito contra especialistas de implementação nominal (@<stack>-bug-fixer, @<stack>-feature-developer),
   preservando o padrão-ouro de roteamento via domain-router / tech-solution-architect.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
WORKFLOWS_FILE = AGENTS_DIR / "workflows.md"


def test_workflows_section_1_5_contains_r065_guard():
    """Valida se a seção 1.5 de workflows.md declara a regra normativa R-065."""
    assert WORKFLOWS_FILE.exists(), remediation(
        f"Arquivo {WORKFLOWS_FILE} não existe",
        fix_hint="Restaurar o arquivo .github/agents/workflows.md"
    )
    content = WORKFLOWS_FILE.read_text(encoding="utf-8")

    match_1_5 = re.search(
        r"###\s+1\.5\s+Loop de Revisão de Qualidade[\s\S]*?(?:###\s+1\.6|\n##\s+|\Z)",
        content
    )
    assert match_1_5, remediation(
        "Seção '### 1.5 Loop de Revisão de Qualidade' não encontrada em workflows.md",
        fix_hint="Verifique se o cabeçalho '### 1.5 Loop de Revisão de Qualidade' está íntegro em workflows.md."
    )
    section_text = match_1_5.group(0)
    assert "R-065" in section_text, remediation(
        "Regra normativa R-065 não encontrada dentro da seção § 1.5 de workflows.md",
        fix_hint="Adicionar o bloco normativo R-065 (Guard de Severidade Arquitetural) na seção 1.5 de workflows.md."
    )


def test_r065_covers_three_architectural_categories():
    """Valida se R-065 cobre Contract Testing, blueprint/Sprint Contract e Matriz De-Para."""
    assert WORKFLOWS_FILE.exists()
    content = WORKFLOWS_FILE.read_text(encoding="utf-8")

    match_r065 = re.search(r"\*\*R-065[^*]*\*\*:[\s\S]*?(?=\n\d+\.\s+|\n###|\Z)", content)
    assert match_r065, remediation(
        "Parágrafo de definição da regra **R-065** não encontrado em workflows.md",
        fix_hint="Formalizar a regra **R-065 (Guard de Severidade Arquitetural no Loop de Qualidade)** no item 1 das Regras Normativas do § 1.5."
    )
    r065_text = match_r065.group(0)

    assert re.search(r"Contract Testing|API pública", r065_text), remediation(
        "Categoria arquitetural 'Contract Testing / API pública' ausente no texto de R-065",
        fix_hint="Incluir 'violação de Contract Testing/API pública (WORKFLOW-REFACTORING)' no escopo bloqueante de R-065."
    )
    assert re.search(r"blueprint|Sprint Contract", r065_text), remediation(
        "Categoria arquitetural 'blueprint / Sprint Contract' ausente no texto de R-065",
        fix_hint="Incluir 'violação de blueprint/Sprint Contract do tech-solution-architect ou <stack>-arch-advisor' no escopo de R-065."
    )
    assert re.search(r"Matriz De-Para|Symbol Exhaustion Gate", r065_text), remediation(
        "Categoria arquitetural 'Matriz De-Para / Symbol Exhaustion Gate' ausente no texto de R-065",
        fix_hint="Incluir 'quebra de Matriz De-Para/Symbol Exhaustion Gate (WORKFLOW-FRAMEWORK-MIGRATION)' no escopo de R-065."
    )


@pytest.mark.parametrize("evaluator_file", [
    "code-review.agent.md",
    "adr-sentinel.agent.md",
    "security-reviewer.agent.md",
])
def test_skeptical_evaluators_isolate_from_stack_specialists(evaluator_file: str):
    """Garante que avaliadores céticos não contêm delegação direta nominal a especialistas de implementação por stack."""
    agent_path = AGENTS_DIR / evaluator_file
    assert agent_path.exists(), remediation(
        f"Arquivo {agent_path} não encontrado",
        fix_hint=f"Verifique a existência de .github/agents/{evaluator_file}"
    )
    content = agent_path.read_text(encoding="utf-8")

    match = re.search(r"##\s+Quando Delegar\s*\n([\s\S]*?)(?:\n<execution_protocol>|\n##|\Z)", content)
    assert match, remediation(
        f"Seção 'Quando Delegar' não encontrada em {evaluator_file}",
        fix_hint=f"Adicionar seção '## Quando Delegar' no arquivo {evaluator_file}."
    )
    delegation_text = match.group(1)

    nominal_stack_pattern = re.compile(
        r"@(?:[a-z0-9-]+)-(?:bug-fixer|feature-developer|code-generator)\b",
        re.IGNORECASE
    )
    matches = nominal_stack_pattern.findall(delegation_text)
    assert not matches, remediation(
        f"Avaliador cético {evaluator_file} contém delegação direta nominal a especialista de stack: {matches}",
        fix_hint=(
            f"Remova o handoff nominal direto para {matches} em {evaluator_file}. "
            "Avaliadores céticos devem delegar para routers (@agent-router / domain-router) ou arquitetos "
            "(@tech-solution-architect), preservando a neutralidade e o padrão-ouro de roteamento."
        )
    )
