"""
test_bug_fixer_blast_radius.py — Validação determinística do blast-radius check prévio
em especialistas bug-fixer de todas as stacks.

Quality Gate que garante:
1. Todos os 6 <stack>-bug-fixer.agent.md formalizam cláusula/etapa de verificação de
   "blast-radius" ou análise de "chamadores/dependentes".
2. A cláusula estipula explicitamente que essa verificação deve ocorrer ANTES de qualquer
   menção a "diff mínimo" ou aplicação cirúrgica de correção (ordem textual relativa).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"
AGENTS_FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"

ALL_BUG_FIXER_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts", "angular"]


def resolve_bug_fixer_file(stack: str) -> Path:
    """Resolve o arquivo bug-fixer da stack (backend ou frontend)."""
    if stack == "angular":
        return AGENTS_FRONTEND_DIR / "angular" / "angular-bug-fixer.agent.md"
    return AGENTS_BACKEND_DIR / stack / f"{stack}-bug-fixer.agent.md"


@pytest.mark.parametrize("stack", ALL_BUG_FIXER_STACKS)
def test_bug_fixer_blast_radius_precedes_diff_application(stack: str):
    """
    Valida que o <stack>-bug-fixer.agent.md:
    (a) Contém diretriz mencionando blast-radius ou chamadores/dependentes;
    (b) A menção de blast-radius/chamadores ocorre ANTES da aplicação de diff mínimo
        na cláusula (ordem textual relativa e precedência explícita via 'ANTES de').
    """
    bf_path = resolve_bug_fixer_file(stack)
    assert bf_path.exists(), remediation(
        f"Arquivo do bug-fixer não encontrado: {bf_path}",
        fix_hint=f"Verifique a existência do agente {stack}-bug-fixer.agent.md."
    )

    content = bf_path.read_text(encoding="utf-8")

    # Localiza a linha ou diretriz que declara blast-radius ou chamadores/dependentes
    blast_clause_match = re.search(
        r"-\s*✅\s*[^\n]*(?:blast-radius|chamadores/dependentes)[^\n]*",
        content,
        re.IGNORECASE,
    )
    assert blast_clause_match is not None, remediation(
        f"[{bf_path.name}] Cláusula de blast-radius check não encontrada no agente.",
        fix_hint=(
            "Adicione uma cláusula '✅ Executar Blast-Radius Check ANTES de aplicar o diff mínimo: "
            "buscar (...) todos os chamadores/dependentes diretos...' sob a seção de escopo cirúrgico."
        ),
    )

    clause_text = blast_clause_match.group(0)

    # Valida presença de 'blast-radius' ou 'chamadores/dependentes'
    blast_term_match = re.search(r"blast-radius|chamadores/dependentes", clause_text, re.IGNORECASE)
    assert blast_term_match is not None, remediation(
        f"[{bf_path.name}] Termo 'blast-radius' ou 'chamadores/dependentes' ausente na cláusula.",
        fix_hint="Mencione 'blast-radius' ou 'chamadores/dependentes' na cláusula de impacto."
    )

    # Valida menção a 'diff mínimo' ou aplicação de correção na cláusula
    diff_term_match = re.search(
        r"diff\s+m[íi]nimo|aplicar\s+(?:o\s+)?diff|aplica[çc][ãa]o\s+de\s+corre[çc][ãa]o",
        clause_text,
        re.IGNORECASE,
    )
    assert diff_term_match is not None, remediation(
        f"[{bf_path.name}] Menção a 'diff mínimo' ou aplicação de correção ausente na cláusula.",
        fix_hint="A cláusula deve contrastar o check de blast-radius com a aplicação do 'diff mínimo'."
    )

    # Valida ordem textual relativa: blast-radius DEVE vir ANTES do diff mínimo na declaração
    assert blast_term_match.start() < diff_term_match.start(), remediation(
        f"[{bf_path.name}] Ordem textual incorreta: 'blast-radius' deve preceder 'diff mínimo' na cláusula.",
        fix_hint="Reestruture a frase para 'Executar Blast-Radius Check ANTES de aplicar o diff mínimo'."
    )

    # Valida precedência temporal explícita ('ANTES de')
    assert re.search(r"antes\s+de", clause_text, re.IGNORECASE), remediation(
        f"[{bf_path.name}] Precedência temporal ('ANTES de') ausente na cláusula de blast-radius.",
        fix_hint="Inclua 'ANTES de aplicar o diff mínimo' para estabelecer o gate temporal determinístico."
    )
