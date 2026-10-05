"""
test_plan_conformance_skill_boundaries.py — Validação determinística da governança
da skill plan-conformance-patterns (R-055 Q3 / Anti-Silo Fix).

Garante que:
1. A skill plan-conformance-patterns existe e possui frontmatter canônico válido
   (name, version, tier 2, category process, triggers em PT-BR).
2. .github/skills/.index.json registra formalmente a skill plan-conformance-patterns.
3. .github/skills/README.md referencia a skill plan-conformance-patterns em sua listagem.
4. @code-review e @pr-gatekeeper declaram o vínculo lazy com a skill em source_docs_lazy.
5. @adr-sentinel NÃO possui nenhum vínculo com a skill (blindagem contra Smell 2.12 —
   escopo de @adr-sentinel permanece estritamente restrito a docs/adr/*.md).
6. A skill segue a estrutura canônica de .github/skills/templates/skill-template.md
   (seções 0 a 4 presentes).
"""

from pathlib import Path
import json
import re

from tests.governance_audit._helpers import remediation

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent

SKILL_PATH = WORKSPACE_ROOT / ".github" / "skills" / "plan-conformance-patterns" / "SKILL.md"
INDEX_PATH = WORKSPACE_ROOT / ".github" / "skills" / ".index.json"
README_PATH = WORKSPACE_ROOT / ".github" / "skills" / "README.md"
CODE_REVIEW_PATH = WORKSPACE_ROOT / ".github" / "agents" / "code-review.agent.md"
PR_GATEKEEPER_PATH = WORKSPACE_ROOT / ".github" / "agents" / "pr-gatekeeper.agent.md"
ADR_SENTINEL_PATH = WORKSPACE_ROOT / ".github" / "agents" / "adr-sentinel.agent.md"


def test_skill_file_exists():
    """Garante que o arquivo SKILL.md da nova skill foi materializado."""
    assert SKILL_PATH.exists(), remediation(
        f"Arquivo {SKILL_PATH} não encontrado.",
        fix_hint="Criar a skill canônica em .github/skills/plan-conformance-patterns/SKILL.md."
    )


def test_skill_frontmatter_canonical():
    """Garante que o frontmatter da skill é canônico (name, version, tier 2, category process, triggers)."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert fm_match, remediation(
        "Frontmatter YAML não encontrado no início de SKILL.md.",
        fix_hint="Adicionar bloco '---' delimitando o frontmatter YAML no topo do arquivo."
    )
    fm = fm_match.group(1)
    assert "name: plan-conformance-patterns" in fm, remediation(
        "Campo 'name' ausente ou incorreto no frontmatter.",
        fix_hint="Definir 'name: plan-conformance-patterns' no frontmatter da skill."
    )
    assert re.search(r'version:\s*"?1\.0\.0"?', fm), remediation(
        "Campo 'version' ausente ou diferente de 1.0.0 no frontmatter.",
        fix_hint='Definir \'version: "1.0.0"\' no frontmatter da skill.'
    )
    assert "tier: 2" in fm, remediation(
        "Campo 'tier' inválido ou ausente no frontmatter.",
        fix_hint="Definir 'tier: 2' no frontmatter da skill."
    )
    assert "category: process" in fm, remediation(
        "Campo 'category' inválido ou ausente no frontmatter.",
        fix_hint="Definir 'category: process' no frontmatter da skill."
    )
    assert "triggers:" in fm, remediation(
        "Lista 'triggers' ausente no frontmatter.",
        fix_hint="Adicionar lista declarativa de triggers em PT-BR no frontmatter da skill."
    )


def test_skill_structural_conformance_with_template():
    """Garante que a skill segue a estrutura canônica de skill-template.md (seções 0 a 4)."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    required_sections = [
        "## 0) Problema Resolvido",
        "## 1) Quando Usar vs Quando NÃO Usar",
        "## 2) Diretrizes Operacionais",
        "## 3) Padrões Canônicos",
        "## 4) Checklist",
    ]
    for section in required_sections:
        assert section in content, remediation(
            f"Seção obrigatória '{section}' ausente em plan-conformance-patterns/SKILL.md.",
            fix_hint=f"Adicionar a seção '{section}' conforme .github/skills/templates/skill-template.md."
        )
    assert "✅" in content and "❌" in content, remediation(
        "Blocos contrastantes ✅/❌ ausentes na seção 'Quando Usar vs Quando NÃO Usar'.",
        fix_hint="Adicionar blocos '### ✅ Quando Usar' e '### ❌ Quando NÃO Usar' com exemplos contrastantes."
    )


def test_index_json_contains_plan_conformance_skill():
    """Garante que a skill plan-conformance-patterns está registrada em .index.json."""
    assert INDEX_PATH.exists(), remediation(
        f"Arquivo {INDEX_PATH} não encontrado.",
        fix_hint="Restaurar o arquivo .github/skills/.index.json."
    )
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    matches = [s for s in data.get("skills", []) if s.get("name") == "plan-conformance-patterns"]
    assert matches, remediation(
        "Entrada 'plan-conformance-patterns' não encontrada em .github/skills/.index.json.",
        fix_hint="Adicionar a entrada da skill em .index.json com name, tier, category, path e related_agents."
    )
    entry = matches[0]
    assert entry.get("tier") == 2, remediation(
        "Tier de 'plan-conformance-patterns' em .index.json deve ser 2.",
        fix_hint="Configurar 'tier: 2' no registro da skill em .index.json."
    )
    assert entry.get("category") == "process", remediation(
        "Categoria de 'plan-conformance-patterns' em .index.json deve ser 'process'.",
        fix_hint="Configurar 'category: \"process\"' no registro da skill em .index.json."
    )
    related = entry.get("related_agents", [])
    assert "@code-review" in related and "@pr-gatekeeper" in related, remediation(
        "related_agents de 'plan-conformance-patterns' deve incluir @code-review e @pr-gatekeeper.",
        fix_hint="Adicionar '@code-review' e '@pr-gatekeeper' na lista related_agents do registro em .index.json."
    )


def test_skills_readme_references_plan_conformance():
    """Garante que o catálogo em .github/skills/README.md referencia a nova skill."""
    assert README_PATH.exists(), remediation(
        f"Arquivo {README_PATH} não encontrado.",
        fix_hint="Restaurar o arquivo .github/skills/README.md."
    )
    content = README_PATH.read_text(encoding="utf-8")
    assert "`plan-conformance-patterns`" in content, remediation(
        "Skill 'plan-conformance-patterns' não referenciada em .github/skills/README.md.",
        fix_hint="Adicionar linha na tabela de catálogo de skills referenciando 'plan-conformance-patterns'."
    )


def test_code_review_agent_has_lazy_link():
    """Garante que @code-review declara vínculo lazy com a skill plan-conformance-patterns."""
    assert CODE_REVIEW_PATH.exists(), remediation(
        f"Arquivo {CODE_REVIEW_PATH} não encontrado.",
        fix_hint="Restaurar .github/agents/code-review.agent.md."
    )
    content = CODE_REVIEW_PATH.read_text(encoding="utf-8")
    assert ".github/skills/plan-conformance-patterns/SKILL.md" in content, remediation(
        "@code-review não declara vínculo com a skill plan-conformance-patterns.",
        fix_hint="Adicionar '.github/skills/plan-conformance-patterns/SKILL.md' em source_docs_lazy de code-review.agent.md."
    )


def test_pr_gatekeeper_agent_has_lazy_link():
    """Garante que @pr-gatekeeper declara vínculo lazy com a skill plan-conformance-patterns."""
    assert PR_GATEKEEPER_PATH.exists(), remediation(
        f"Arquivo {PR_GATEKEEPER_PATH} não encontrado.",
        fix_hint="Restaurar .github/agents/pr-gatekeeper.agent.md."
    )
    content = PR_GATEKEEPER_PATH.read_text(encoding="utf-8")
    assert ".github/skills/plan-conformance-patterns/SKILL.md" in content, remediation(
        "@pr-gatekeeper não declara vínculo com a skill plan-conformance-patterns.",
        fix_hint="Adicionar '.github/skills/plan-conformance-patterns/SKILL.md' em source_docs_lazy de pr-gatekeeper.agent.md."
    )


def test_adr_sentinel_has_no_plan_conformance_link():
    """Blindagem contra Smell 2.12: @adr-sentinel deve permanecer estritamente restrito a docs/adr/*.md."""
    assert ADR_SENTINEL_PATH.exists(), remediation(
        f"Arquivo {ADR_SENTINEL_PATH} não encontrado.",
        fix_hint="Restaurar .github/agents/adr-sentinel.agent.md."
    )
    content = ADR_SENTINEL_PATH.read_text(encoding="utf-8")
    assert "plan-conformance-patterns" not in content, remediation(
        "@adr-sentinel não deve referenciar a skill plan-conformance-patterns (escopo deve permanecer restrito a docs/adr/*.md).",
        fix_hint="Remover qualquer referência a 'plan-conformance-patterns' de .github/agents/adr-sentinel.agent.md."
    )
