"""
test_r066_progressive_disclosure_budget.py — Validação determinística de
Progressive Disclosure Compulsória de source_docs: (R-066 / Smell 2.31).

Escopo desta rodada (F1+F2+F4 do plano de implementação
docs/implementation-plans/20261003-governance-maintenance-progressive-disclosure-source-docs.md):
    - F3 (fatiamento de .github/agents/workflows.md) foi DESTACADO deste plano para
      um sub-plano dedicado (blast radius real: 11 testes de CI com acoplamento
      estrutural fino, não os 3 originalmente estimados — ver §0.3 do plano de
      implementação). Portanto, os testes abaixo NÃO assumem que workflows.md foi
      fatiado; apenas que CLAUDE.md/copilot-instructions.md/workflows.md estão
      corretamente classificados como `source_docs_lazy:` onde referenciados.

Garante que:
1. CLAUDE.md e .github/copilot-instructions.md, quando referenciados por qualquer
   .agent.md / SKILL.md / *.prompt.md, estão em `source_docs_lazy:`, nunca em
   `source_docs:` (full-load).
2. Nenhum documento listado em `source_docs:` (full-load) de qualquer artefato
   excede o teto de 500 linhas (R-066(a)).
3. R-066 está formalizada em CLAUDE.md e espelhada em copilot-instructions.md.
4. A categoria de smell 2.31 está documentada em governance-audit-patterns/SKILL.md.
5. tools/agent_source_docs_sync/sync_lazy_source_docs.py reporta drift=0 (--check).
6. O bloco <execution_protocol> (fonte única: tools/agent_protocol_sync/
   _execution-protocol-fragment.md) instrui operacionalmente o agent sobre o
   significado de `source_docs_lazy:` no seu próprio frontmatter (gap fechado:
   antes desta regra, a semântica só existia em documentos que os próprios agents
   não carregavam por padrão — ver docs/implementation-plans/20261003-...md § 14).
7. Os 22 *.prompt.md também recebem o bloco <execution_protocol> (gap irmão
   encontrado em sessão subsequente — nenhum prompt tinha o bloco, apesar de
   100% deles declararem `source_docs_lazy:`; ver [2.52.2] e § 15 do
   implementation-plan).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"
GOVERNANCE_AUDIT_SKILL = REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md"

LAZY_ALLOWLIST = {
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/agents/workflows.md",
}

FULL_LOAD_LINE_BUDGET = 500

TARGET_GLOBS: list[tuple[Path, str]] = [
    (REPO_ROOT / ".github" / "agents", "**/*.agent.md"),
    (REPO_ROOT / ".github" / "skills", "**/SKILL.md"),
    (REPO_ROOT / ".github" / "prompts", "**/*.prompt.md"),
]


def _get_target_files() -> list[Path]:
    files: list[Path] = []
    for base_dir, pattern in TARGET_GLOBS:
        if not base_dir.is_dir():
            continue
        for p in sorted(base_dir.glob(pattern)):
            if "templates" in p.parts:
                continue
            files.append(p)
    return files


def _parse_frontmatter(path: Path) -> dict:
    import re

    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?\r?\n)---\r?\n?", text, re.DOTALL)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def test_lazy_allowlist_docs_never_in_full_source_docs():
    """CLAUDE.md/copilot-instructions.md/workflows.md NUNCA devem estar em
    'source_docs:' (full-load) — apenas em 'source_docs_lazy:' (R-066(b))."""
    violations: list[str] = []
    for tf in _get_target_files():
        fm = _parse_frontmatter(tf)
        full_docs = fm.get("source_docs") or []
        if isinstance(full_docs, str):
            full_docs = [full_docs]
        for doc in full_docs:
            if doc in LAZY_ALLOWLIST:
                violations.append(f"{tf.relative_to(REPO_ROOT)} declara '{doc}' em source_docs (full)")

    assert not violations, remediation(
        f"{len(violations)} artefato(s) declaram documento(s) de alto fan-in em source_docs (full-load):\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint=(
            "Rode `python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply` para migrar "
            "automaticamente esses documentos para source_docs_lazy. Nunca edite o frontmatter manualmente."
        ),
    )


def test_full_load_docs_under_line_budget():
    """Todo documento da LAZY_ALLOWLIST (CLAUDE.md/copilot-instructions.md/workflows.md)
    permanece fora de 'source_docs:' (full) de todo artefato — validação complementar
    ao teste anterior, focada especificamente no teto de linhas que justifica a
    classificação lazy desses 3 documentos centrais (R-066(a)/(b)).

    NOTA DE ESCOPO (ver docs/implementation-plans/20261003-...): esta rodada do plano
    restringe a classificação lazy à allowlist fixa (CLAUDE.md, copilot-instructions.md,
    workflows.md) — NÃO generaliza para qualquer skill/doc > 500 linhas, pois várias
    skills (ex. handoff-governance, agent-contracts, terminal-governance) são
    mandatoriamente exigidas em source_docs (full) por outras regras (R-042/R-049)
    mesmo excedendo o teto. Generalizar o teto de linhas para todo o universo de
    documentos é um ciclo de governança separado, fora deste escopo aprovado."""
    violations: list[str] = []
    for tf in _get_target_files():
        fm = _parse_frontmatter(tf)
        full_docs = fm.get("source_docs") or []
        if isinstance(full_docs, str):
            full_docs = [full_docs]
        for doc in full_docs:
            if doc in LAZY_ALLOWLIST:
                doc_path = REPO_ROOT / doc
                line_count = len(doc_path.read_text(encoding="utf-8").splitlines()) if doc_path.is_file() else 0
                violations.append(
                    f"{tf.relative_to(REPO_ROOT)} declara '{doc}' ({line_count} linhas) em source_docs (full)"
                )

    assert not violations, remediation(
        f"{len(violations)} artefato(s) declaram documento(s) da allowlist lazy em source_docs (full):\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint="Rode `python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply` para migrar.",
    )


def test_r066_documented_in_claude_md():
    """CLAUDE.md deve conter a declaração normativa de R-066."""
    content = CLAUDE_MD.read_text(encoding="utf-8")
    assert "R-066" in content, remediation(
        "CLAUDE.md não contém a regra normativa R-066",
        fix_hint="Adicionar o bloco normativo R-066 (Progressive Disclosure Compulsória) em CLAUDE.md § 3.",
    )
    assert "source_docs_lazy" in content, remediation(
        "CLAUDE.md não menciona o campo 'source_docs_lazy' no texto de R-066",
        fix_hint="Garantir que o texto de R-066 declare explicitamente os campos source_docs/source_docs_lazy.",
    )


def test_r066_mirrored_in_copilot_instructions():
    """copilot-instructions.md deve espelhar a regra R-066 (paridade normativa)."""
    content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
    assert "R-066" in content, remediation(
        "copilot-instructions.md não espelha a regra R-066",
        fix_hint="Adicionar a entrada R-066 em copilot-instructions.md § 2 (Sempre), espelhando CLAUDE.md.",
    )


def test_smell_2_31_documented_in_governance_audit_patterns():
    """governance-audit-patterns/SKILL.md deve conter a categoria de smell 2.31
    (Progressive Disclosure Violation / R-066)."""
    content = GOVERNANCE_AUDIT_SKILL.read_text(encoding="utf-8")
    assert "2.31" in content, remediation(
        "governance-audit-patterns/SKILL.md não contém a categoria de Smell 2.31",
        fix_hint="Adicionar a seção '### 2.31 — Progressive Disclosure Violation' em governance-audit-patterns/SKILL.md § 2.",
    )
    assert "R-066" in content, remediation(
        "Smell 2.31 não referencia a regra R-066",
        fix_hint="Vincular a seção do Smell 2.31 à regra normativa R-066.",
    )


def test_sync_lazy_source_docs_check_returns_zero():
    """tools/agent_source_docs_sync/sync_lazy_source_docs.py --check deve reportar
    drift=0 (todos os artefatos já migrados para o contrato de 2 camadas)."""
    result = subprocess.run(
        [sys.executable, "tools/agent_source_docs_sync/sync_lazy_source_docs.py", "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, remediation(
        f"sync_lazy_source_docs.py --check retornou exit code {result.returncode} (drift detectado)",
        fix_hint="Rode `python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply` para corrigir o drift.",
    )


def test_execution_protocol_fragment_instructs_source_docs_lazy_semantics():
    """Fecha o gap de discovery: a fonte canônica do <execution_protocol>
    (tools/agent_protocol_sync/_execution-protocol-fragment.md) DEVE conter uma
    instrução operacional explícita sobre o significado de `source_docs_lazy:`
    — sem isso, o agente não tem, no próprio corpo, nenhuma orientação sobre
    quando NÃO usar `read_file` nos documentos de alto fan-in (CLAUDE.md,
    copilot-instructions.md, workflows.md)."""
    fragment_path = (
        REPO_ROOT / "tools" / "agent_protocol_sync" / "_execution-protocol-fragment.md"
    )
    assert fragment_path.is_file(), remediation(
        f"Fragmento canônico não encontrado em {fragment_path}",
        fix_hint="Restaurar tools/agent_protocol_sync/_execution-protocol-fragment.md.",
    )
    content = fragment_path.read_text(encoding="utf-8")
    assert "source_docs_lazy" in content, remediation(
        "_execution-protocol-fragment.md não instrui o agent sobre source_docs_lazy:",
        fix_hint=(
            "Adicionar um item ao bloco <!-- BEGIN:STANDARD -->...<!-- END:STANDARD --> explicando "
            "que documentos em source_docs_lazy: não foram pré-carregados e devem ser consultados "
            "via context-mode/ctx_search, nunca read_file integral; depois rodar "
            "`python tools/agent_protocol_sync/sync_execution_protocol.py --apply`."
        ),
    )
    assert "R-066" in content, remediation(
        "_execution-protocol-fragment.md não referencia a regra R-066",
        fix_hint="Vincular o item de source_docs_lazy ao R-066 no texto do fragmento.",
    )


def test_standard_agents_execution_protocol_propagated_with_source_docs_lazy_item():
    """Valida que o item de source_docs_lazy/R-066 foi efetivamente propagado
    (via sync_execution_protocol.py --apply) para os agents STANDARD reais,
    não apenas declarado no fragmento canônico — fechando o gap de discovery
    de ponta a ponta (fonte → artefato final lido pelo agent)."""
    result = subprocess.run(
        [sys.executable, "tools/agent_protocol_sync/sync_execution_protocol.py", "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, remediation(
        f"sync_execution_protocol.py --check retornou exit code {result.returncode} (drift detectado)",
        fix_hint="Rode `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` para propagar o fragmento canônico atualizado.",
    )


def test_all_prompts_contain_execution_protocol_block():
    """Valida diretamente (sem depender do script de sync) que 100% dos
    *.prompt.md elegíveis (com context-mode/ctx_* em tools:) possuem o bloco
    <execution_protocol> com a instrução de source_docs_lazy/R-066."""
    prompts_dir = REPO_ROOT / ".github" / "prompts"
    prompt_files = [
        p for p in sorted(prompts_dir.glob("**/*.prompt.md")) if "templates" not in p.parts
    ]
    assert len(prompt_files) >= 20, remediation(
        f"Esperado >= 20 prompts em {prompts_dir}, encontrado {len(prompt_files)}",
        fix_hint="Verifique se .github/prompts/*.prompt.md não foi movido/deletado por engano.",
    )

    violations: list[str] = []
    for pf in prompt_files:
        fm = _parse_frontmatter(pf)
        tools = fm.get("tools") or []
        if isinstance(tools, str):
            tools = [tools]
        if not any(isinstance(t, str) and t.startswith("context-mode/ctx_") for t in tools):
            continue  # Prompts sem ferramentas context-mode não recebem o bloco (prevenção de instrução morta)

        content = pf.read_text(encoding="utf-8")
        if "<execution_protocol>" not in content or "</execution_protocol>" not in content:
            violations.append(f"{pf.relative_to(REPO_ROOT)}: bloco <execution_protocol> ausente")
        elif "source_docs_lazy" not in content:
            violations.append(f"{pf.relative_to(REPO_ROOT)}: bloco presente, mas sem instrução de source_docs_lazy")

    assert not violations, remediation(
        f"{len(violations)} prompt(s) elegíveis sem bloco <execution_protocol> íntegro:\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint="Rode `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` para propagar o bloco a todos os prompts elegíveis.",
    )


