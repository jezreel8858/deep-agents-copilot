"""
test_agent_headings_standardization.py — Suíte determinística de validação de padronização do H1 em agents e templates.

Garante que 100% dos arquivos de agents (*.agent.md) e templates canônicos (.github/agents/templates/*.md)
possuam exatamente '# Perfil Operacional' como seu único cabeçalho H1, assegurando que o nome/identificador
do agente resida exclusivamente no frontmatter YAML (`name: '...'`) como Single Source of Truth (SSOT).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
TEMPLATES_DIR = AGENTS_DIR / "templates"


def get_all_agent_files() -> list[Path]:
    """Retorna todos os 86 arquivos .agent.md sob .github/agents/ (excluindo templates)."""
    return sorted([p for p in AGENTS_DIR.glob("**/*.agent.md") if "templates" not in p.parts])


def get_all_template_files() -> list[Path]:
    """Retorna todos os 4 templates canônicos sob .github/agents/templates/."""
    return sorted(list(TEMPLATES_DIR.glob("*.md")))


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extrai o frontmatter YAML e o corpo markdown após o fechamento '---'."""
    normalized = content.replace("\r\n", "\n")
    if not normalized.startswith("---"):
        return {}, normalized
    parts = normalized.split("\n---\n", 1)
    if len(parts) < 2:
        parts = re.split(r"\n---\s*\n", normalized, maxsplit=1)
    if len(parts) < 2:
        return {}, normalized
    try:
        fm_data = yaml.safe_load(parts[0].replace("---", "")) or {}
    except yaml.YAMLError:
        fm_data = {}
    return fm_data, parts[1]


def extract_headings_outside_code(body: str) -> list[tuple[int, str, int]]:
    """Extrai cabeçalhos Markdown (# .. ######) fora de blocos de código."""
    headings = []
    in_code = False
    for idx, line in enumerate(body.splitlines()):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip(), idx + 1))
    return headings


# ─────────────────────────────────────────────────────────────
# 1. Validação de Padronização de H1 para Agents
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("agent_path", get_all_agent_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_agent_has_exact_standardized_h1(agent_path: Path):
    """
    Valida se todo agent possui:
    1. Frontmatter YAML válido com campo 'name'.
    2. Exatamente 1 cabeçalho H1 fora de blocos de código.
    3. O cabeçalho H1 é exatamente '# Perfil Operacional'.
    4. O H1 é o primeiro cabeçalho do corpo do arquivo.
    """
    content = agent_path.read_text(encoding="utf-8")
    rel_path = agent_path.relative_to(REPO_ROOT).as_posix()
    
    fm, body = parse_frontmatter(content)
    assert fm, f"[{rel_path}] Frontmatter YAML ausente ou inválido"
    assert "name" in fm, f"[{rel_path}] Campo 'name' ausente no frontmatter"
    
    headings = extract_headings_outside_code(body)
    assert len(headings) >= 1, f"[{rel_path}] Nenhum cabeçalho encontrado no corpo markdown"
    
    # Primeiro cabeçalho DEVE ser H1
    first_level, first_title, first_line = headings[0]
    assert first_level == 1, (
        f"[{rel_path}] O primeiro cabeçalho deve ser H1 (#), mas é H{first_level}: '{first_title}' (linha {first_line})"
    )
    assert first_title == "Perfil Operacional", (
        f"[{rel_path}] O H1 deve ser exatamente '# Perfil Operacional', mas foi encontrado '# {first_title}'"
    )
    
    # Não deve existir nenhum outro H1 fora de código
    all_h1s = [h for h in headings if h[0] == 1]
    assert len(all_h1s) == 1, (
        f"[{rel_path}] Esperado exatamente 1 cabeçalho H1 no arquivo, mas foram encontrados {len(all_h1s)}: {all_h1s}"
    )


# ─────────────────────────────────────────────────────────────
# 2. Validação de Padronização de H1 para Templates Canônicos
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("template_path", get_all_template_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_template_has_exact_standardized_h1(template_path: Path):
    """
    Valida se todo template canônico em .github/agents/templates/ possui:
    1. Exatamente 1 cabeçalho H1 fora de blocos de código.
    2. O cabeçalho H1 é exatamente '# Perfil Operacional'.
    3. O H1 é o primeiro cabeçalho do documento.
    """
    content = template_path.read_text(encoding="utf-8")
    rel_path = template_path.relative_to(REPO_ROOT).as_posix()
    
    fm, body = parse_frontmatter(content)
    assert fm, f"[{rel_path}] Frontmatter YAML ausente ou inválido no template"
    
    headings = extract_headings_outside_code(body)
    assert len(headings) >= 1, f"[{rel_path}] Nenhum cabeçalho encontrado no template"
    
    first_level, first_title, first_line = headings[0]
    assert first_level == 1, (
        f"[{rel_path}] O primeiro cabeçalho do template deve ser H1 (#), mas é H{first_level}: '{first_title}'"
    )
    assert first_title == "Perfil Operacional", (
        f"[{rel_path}] O H1 do template deve ser exatamente '# Perfil Operacional', mas foi encontrado '# {first_title}'"
    )
    
    all_h1s = [h for h in headings if h[0] == 1]
    assert len(all_h1s) == 1, (
        f"[{rel_path}] Esperado exatamente 1 cabeçalho H1 no template, encontrados {len(all_h1s)}: {all_h1s}"
    )


# ─────────────────────────────────────────────────────────────
# 3. Contagem Total de Arquivos Auditados
# ─────────────────────────────────────────────────────────────

def test_coverage_exhaustion_count():
    """Garante que a suíte auditou exatamente os 86 agents e 4 templates do repositório."""
    agents = get_all_agent_files()
    templates = get_all_template_files()
    
    assert len(agents) == 86, f"Esperados 86 agents, encontrados {len(agents)}"
    assert len(templates) == 4, f"Esperados 4 templates, encontrados {len(templates)}"
