"""
test_r066_progressive_disclosure_budget.py — Validação determinística de
Progressive Disclosure Compulsória de source_docs / source_docs_lazy (R-066 / Smell 2.31).

Garante que:
1. Nenhum documento com <= 300 linhas permanece retido em `source_docs_lazy:` — documentos
   com <= 300 linhas (incluindo CLAUDE.md, .github/copilot-instructions.md e .github/agents/workflows.md
   após enxugamento/fatiamento) devem residir em `source_docs:` (R-066).
2. Qualquer documento da LAZY_ALLOWLIST que exceda 300 linhas (LAZY_LINE_THRESHOLD) deve
   residir exclusivamente em `source_docs_lazy:`, nunca em `source_docs:` (full-load).
3. R-066 está formalizada em CLAUDE.md e espelhada em copilot-instructions.md.
4. A categoria de smell 2.31 está documentada em governance-audit-patterns/SKILL.md.
5. tools/agent_source_docs_sync/sync_lazy_source_docs.py reporta drift=0 (--check).
6. O bloco <execution_protocol> (fonte única: tools/agent_protocol_sync/
   _execution-protocol-fragment.md) mantém a cláusula CLAUSE_LAZY_DOCS para injeção condicional
   quando `source_docs_lazy:` estiver declarado.
7. 100% dos *.prompt.md elegíveis possuem o bloco <execution_protocol> íntegro e sincronizado.
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

LAZY_LINE_THRESHOLD = 300

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

TEMPLATE_GLOBS: list[tuple[Path, str]] = [
    (REPO_ROOT / ".github" / "agents" / "templates", "*.md"),
    (REPO_ROOT / ".github" / "prompts" / "templates", "*.md"),
    (REPO_ROOT / ".github" / "skills" / "templates", "*.md"),
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


def _get_template_files() -> list[Path]:
    files: list[Path] = []
    for base_dir, pattern in TEMPLATE_GLOBS:
        if not base_dir.is_dir():
            continue
        files.extend(sorted(base_dir.glob(pattern)))
    return files


def _parse_frontmatter(path: Path) -> dict:
    import re

    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?\r?\n)---\r?\n?", text, re.DOTALL)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def _doc_line_count(doc: str) -> int:
    doc_path = REPO_ROOT / doc
    return len(doc_path.read_text(encoding="utf-8").splitlines()) if doc_path.is_file() else 0


def test_lazy_allowlist_docs_never_in_full_source_docs():
    """Documentos em source_docs_lazy devem possuir > 300 linhas; documentos <= 300 linhas
    devem ser migrados para source_docs (R-066), incluindo templates canônicos."""
    violations: list[str] = []
    for tf in [*_get_target_files(), *_get_template_files()]:
        fm = _parse_frontmatter(tf)
        lazy_docs = fm.get("source_docs_lazy") or []
        if isinstance(lazy_docs, str):
            lazy_docs = [lazy_docs]
        for doc in lazy_docs:
            lc = _doc_line_count(doc)
            if lc <= LAZY_LINE_THRESHOLD:
                violations.append(
                    f"{tf.relative_to(REPO_ROOT)} declara '{doc}' ({lc} linhas <= {LAZY_LINE_THRESHOLD}) em source_docs_lazy"
                )

    assert not violations, remediation(
        f"{len(violations)} artefato(s) declaram documento(s) com <= {LAZY_LINE_THRESHOLD} linhas em source_docs_lazy:\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint=(
            "Rode `python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply` para migrar "
            "automaticamente documentos <= 300 linhas para source_docs."
        ),
    )


def test_full_load_docs_under_line_budget():
    """Qualquer documento da LAZY_ALLOWLIST que exceda 300 linhas (LAZY_LINE_THRESHOLD)
    não pode permanecer em 'source_docs:' (full-load), devendo ir para 'source_docs_lazy:' (R-066)."""
    violations: list[str] = []
    for tf in _get_target_files():
        fm = _parse_frontmatter(tf)
        full_docs = fm.get("source_docs") or []
        if isinstance(full_docs, str):
            full_docs = [full_docs]
        for doc in full_docs:
            if doc in LAZY_ALLOWLIST:
                line_count = _doc_line_count(doc)
                if line_count > LAZY_LINE_THRESHOLD:
                    violations.append(
                        f"{tf.relative_to(REPO_ROOT)} declara '{doc}' ({line_count} linhas > {LAZY_LINE_THRESHOLD}) em source_docs (full)"
                    )

    assert not violations, remediation(
        f"{len(violations)} artefato(s) declaram documento(s) > {LAZY_LINE_THRESHOLD} linhas da allowlist em source_docs (full):\n"
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
    drift=0 (todos os artefatos sincronizados conforme limiar de 300 linhas)."""
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
    """Garante que a fonte canônica do <execution_protocol>
    (tools/agent_protocol_sync/_execution-protocol-fragment.md) mantém a
    instrução operacional CLAUSE_LAZY_DOCS sobre `source_docs_lazy:` (R-066)."""
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
            "Adicionar a cláusula CLAUSE_LAZY_DOCS explicando que documentos em source_docs_lazy: "
            "devem ser consultados via context-mode/ctx_search, nunca read_file integral."
        ),
    )
    assert "R-066" in content, remediation(
        "_execution-protocol-fragment.md não referencia a regra R-066",
        fix_hint="Vincular o item de source_docs_lazy ao R-066 no texto do fragmento.",
    )


def test_standard_agents_execution_protocol_propagated_with_source_docs_lazy_item():
    """Valida que o bloco <execution_protocol> está 100% sincronizado com
    sync_execution_protocol.py --check (drift=0)."""
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
    """Valida diretamente que 100% dos *.prompt.md elegíveis (com context-mode/ctx_* em tools:)
    possuem o bloco <execution_protocol> sincronizado (incluindo instrução de source_docs_lazy
    quando o frontmatter declarar source_docs_lazy)."""
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
            continue

        content = pf.read_text(encoding="utf-8")
        if "<execution_protocol>" not in content or "</execution_protocol>" not in content:
            violations.append(f"{pf.relative_to(REPO_ROOT)}: bloco <execution_protocol> ausente")
        elif bool(fm.get("source_docs_lazy")) and "source_docs_lazy" not in content:
            violations.append(f"{pf.relative_to(REPO_ROOT)}: declara source_docs_lazy mas sem instrução correspondente no bloco")

    assert not violations, remediation(
        f"{len(violations)} prompt(s) elegíveis sem bloco <execution_protocol> íntegro:\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint="Rode `python tools/agent_protocol_sync/sync_execution_protocol.py --apply` para propagar o bloco a todos os prompts elegíveis.",
    )


def test_canonical_templates_progressive_disclosure_threshold():
    """Valida que todos os templates canônicos (.github/agents/templates/*.md,
    .github/prompts/templates/*.md, .github/skills/templates/*.md) não mantenham
    documentos com <= 300 linhas em source_docs_lazy: (R-066 / Q2 R-055)."""
    template_files = _get_template_files()
    assert len(template_files) >= 6, remediation(
        f"Esperado >= 6 arquivos de template canônico, encontrado {len(template_files)}",
        fix_hint="Verifique .github/agents/templates/*.md, .github/prompts/templates/*.md e .github/skills/templates/*.md.",
    )
    violations: list[str] = []
    for tpl in template_files:
        fm = _parse_frontmatter(tpl)
        lazy_docs = fm.get("source_docs_lazy") or []
        if isinstance(lazy_docs, str):
            lazy_docs = [lazy_docs]
        for doc in lazy_docs:
            lc = _doc_line_count(doc)
            if lc <= LAZY_LINE_THRESHOLD:
                violations.append(
                    f"{tpl.relative_to(REPO_ROOT)} declara '{doc}' ({lc} linhas <= {LAZY_LINE_THRESHOLD}) em source_docs_lazy"
                )

    assert not violations, remediation(
        f"{len(violations)} template(s) canônico(s) declaram documento(s) com <= {LAZY_LINE_THRESHOLD} linhas em source_docs_lazy:\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint="Mova documentos com <= 300 linhas de source_docs_lazy: para source_docs: nos templates canônicos.",
    )


def test_all_skills_respect_300_lines_ceiling():
    """Valida que 100% dos arquivos .github/skills/*/SKILL.md (81 skills) respeitam
    o teto estrito de <= 300 linhas (R-066 Progressive Disclosure)."""
    skills_dir = REPO_ROOT / ".github" / "skills"
    skill_files = sorted(p for p in skills_dir.glob("*/SKILL.md") if "templates" not in p.parts)
    assert len(skill_files) == 81, f"Esperado 81 skills, encontrado {len(skill_files)}"

    violations: list[str] = []
    for sf in skill_files:
        lc = len(sf.read_text(encoding="utf-8").splitlines())
        if lc > LAZY_LINE_THRESHOLD:
            violations.append(f"{sf.relative_to(REPO_ROOT)}: {lc} linhas (teto={LAZY_LINE_THRESHOLD})")

    assert not violations, remediation(
        f"{len(violations)} skill(s) excedem o teto de {LAZY_LINE_THRESHOLD} linhas (R-066):\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint="Extraia exemplos extensos e tabelas detalhadas para references/*.md.",
    )


def test_clause_lazy_docs_present_iff_source_docs_lazy_non_empty():
    """Valida que nos prompts e templates canônicos com <execution_protocol>, a cláusula
    de source_docs_lazy (CLAUSE_LAZY_DOCS) está presente se e somente se source_docs_lazy
    no frontmatter não for vazio."""
    files_to_check = [
        *sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")),
        *_get_template_files(),
    ]
    violations: list[str] = []
    for f in files_to_check:
        content = f.read_text(encoding="utf-8")
        if "<execution_protocol>" not in content:
            continue
        fm = _parse_frontmatter(f)
        lazy_docs = fm.get("source_docs_lazy") or []
        has_lazy_fm = bool(lazy_docs)
        ep_match = content.split("<execution_protocol>", 1)[1].split("</execution_protocol>", 1)[0]
        has_lazy_clause = "source_docs_lazy" in ep_match
        if has_lazy_fm != has_lazy_clause:
            violations.append(
                f"{f.relative_to(REPO_ROOT)}: source_docs_lazy no frontmatter={has_lazy_fm}, "
                f"mas CLAUSE_LAZY_DOCS no <execution_protocol>={has_lazy_clause}"
            )

    assert not violations, remediation(
        f"{len(violations)} inconsistência(s) entre source_docs_lazy e CLAUSE_LAZY_DOCS:\n"
        + "\n".join(f"  - {v}" for v in violations),
        fix_hint="Sincronize o bloco <execution_protocol> com o estado de source_docs_lazy no frontmatter.",
    )
