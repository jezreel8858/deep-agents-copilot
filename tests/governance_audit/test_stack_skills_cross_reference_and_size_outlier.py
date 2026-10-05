"""
test_stack_skills_cross_reference_and_size_outlier.py — Validação determinística de
governança para skills especializadas por stack e prevenção de outliers de tamanho.

Garante que:
1. Skills de implementação de testes por stack (`test-implementation-<stack>`)
   declaram obrigatoriamente a skill genérica correspondente em `source_docs` e no corpo.
2. Skills de performance por stack (`*-performance-patterns`) declaram obrigatoriamente
   a skill genérica `performance-engineering-patterns` em `source_docs` e no corpo.
3. As skills genéricas mantêm catálogos/tabelas referenciando todas as especializações ativas.
4. Nenhuma skill especializada por stack atua como outlier de tamanho (teto de 500 linhas),
   garantindo que princípios universais sejam extraídos para as camadas genéricas.
"""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".github" / "skills"

# Mapeamento de skills de teste especializadas -> skill genérica esperada
STACK_TEST_SKILLS = {
    "test-implementation-python": "test-implementation-backend",
    "test-implementation-spring-boot": "test-implementation-backend",
    "test-implementation-angular-jasmine": "test-implementation-frontend",
    "test-implementation-angular-vitest": "test-implementation-frontend",
    "test-implementation-react-vitest": "test-implementation-frontend",
}

# Mapeamento de skills de performance especializadas -> skill genérica esperada
STACK_PERF_SKILLS = {
    "angular-performance-patterns": "performance-engineering-patterns",
    "react-performance-patterns": "performance-engineering-patterns",
    "spring-boot-performance-patterns": "performance-engineering-patterns",
    "spring-reactive-performance-patterns": "performance-engineering-patterns",
}

MAX_SPECIALIZED_SKILL_LINES = 500


@pytest.mark.parametrize("stack_skill,generic_skill", STACK_TEST_SKILLS.items())
def test_test_implementation_stack_skills_cross_reference_generic(stack_skill: str, generic_skill: str):
    """Garante que toda skill test-implementation-<stack> referencia sua respectiva skill genérica."""
    skill_file = SKILLS_DIR / stack_skill / "SKILL.md"
    assert skill_file.exists(), f"Arquivo de skill {skill_file} deve existir"

    content = skill_file.read_text(encoding="utf-8")
    
    # 1. Deve declarar no frontmatter source_docs
    expected_doc_ref = f".github/skills/{generic_skill}/SKILL.md"
    assert expected_doc_ref in content, (
        f"A skill {stack_skill} DEVE declarar '{expected_doc_ref}' em source_docs no frontmatter."
    )

    # 2. Deve citar a skill genérica no corpo do markdown
    assert generic_skill in content, (
        f"A skill {stack_skill} DEVE referenciar explicitamente '{generic_skill}' no texto."
    )


@pytest.mark.parametrize("perf_skill,generic_skill", STACK_PERF_SKILLS.items())
def test_performance_stack_skills_cross_reference_generic(perf_skill: str, generic_skill: str):
    """Garante que toda skill *-performance-patterns referencia a skill genérica performance-engineering-patterns."""
    skill_file = SKILLS_DIR / perf_skill / "SKILL.md"
    assert skill_file.exists(), f"Arquivo de skill {skill_file} deve existir"

    content = skill_file.read_text(encoding="utf-8")

    # 1. Deve declarar no frontmatter source_docs
    expected_doc_ref = f".github/skills/{generic_skill}/SKILL.md"
    assert expected_doc_ref in content, (
        f"A skill {perf_skill} DEVE declarar '{expected_doc_ref}' em source_docs no frontmatter."
    )

    # 2. Deve citar a skill genérica no corpo do markdown
    assert generic_skill in content, (
        f"A skill {perf_skill} DEVE referenciar explicitamente '{generic_skill}' no texto."
    )


def test_generic_skills_catalog_their_stack_specializations():
    """Garante que as skills genéricas mantêm tabelas ativas listando todas as suas especializações."""
    # 1. test-implementation-frontend
    fe_file = SKILLS_DIR / "test-implementation-frontend" / "SKILL.md"
    fe_content = fe_file.read_text(encoding="utf-8")
    assert "test-implementation-angular-vitest" in fe_content
    assert "test-implementation-angular-jasmine" in fe_content
    assert "test-implementation-react-vitest" in fe_content

    # 2. test-implementation-backend
    be_file = SKILLS_DIR / "test-implementation-backend" / "SKILL.md"
    be_content = be_file.read_text(encoding="utf-8")
    assert "test-implementation-spring-boot" in be_content
    assert "test-implementation-python" in be_content

    # 3. performance-engineering-patterns
    perf_file = SKILLS_DIR / "performance-engineering-patterns" / "SKILL.md"
    perf_content = perf_file.read_text(encoding="utf-8")
    for ps in STACK_PERF_SKILLS.keys():
        assert ps in perf_content, f"performance-engineering-patterns deve listar a especialização {ps}"


@pytest.mark.parametrize("specialized_skill", list(STACK_TEST_SKILLS.keys()) + list(STACK_PERF_SKILLS.keys()))
def test_specialized_skills_size_outlier_guard(specialized_skill: str):
    """Guarda contra inflação desproporcional: skills especializadas não devem exceder MAX_SPECIALIZED_SKILL_LINES."""
    skill_file = SKILLS_DIR / specialized_skill / "SKILL.md"
    assert skill_file.exists()

    lines = skill_file.read_text(encoding="utf-8").splitlines()
    line_count = len(lines)

    assert line_count <= MAX_SPECIALIZED_SKILL_LINES, (
        f"A skill {specialized_skill} possui {line_count} linhas, excedendo o teto de {MAX_SPECIALIZED_SKILL_LINES}. "
        f"Decomponha conceitos universais/genéricos para a skill base correspondente."
    )
