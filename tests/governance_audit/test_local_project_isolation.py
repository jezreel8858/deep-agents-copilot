"""
test_local_project_isolation.py — Suíte de testes para garantir 100% de conformidade com
as regras de isolamento e anonimização de projetos locais (R-038, R-043 e R-044).

Garante que:
1. Nenhum arquivo rastreado no repositório faz referência a projetos locais/externos privados.
2. As regras de gitignore para .github/projects.local.yaml e .github/instructions/local/ são rigorosamente respeitadas (R-043).
3. Caminhos absolutos de máquina local ou IDs de usuário reais nunca vazam para arquivos versionados.
4. O catálogo de agents (.github/agents/catalog.yaml) permanece 100% desacoplado de instâncias de projetos locais.
5. docs/ai-context/catalog.yaml foi extinto em favor da arquitetura limpa (Cenário 2).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
THIS_REPO_NAME = REPO_ROOT.name.lower()
THIS_REPO_TOKENS = {THIS_REPO_NAME, "deep-agents-copilot", "deep_agents_copilot", "deep agents copilot"}


def get_git_tracked_files() -> list[Path]:
    """Retorna todos os arquivos rastreados no Git."""
    p = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        pytest.fail(f"Falha ao executar 'git ls-files': {p.stderr}")
    return [REPO_ROOT / f.strip() for f in p.stdout.splitlines() if f.strip()]


def get_forbidden_project_identifiers() -> set[str]:
    """Coleta dinamicamente todos os IDs e nomes de projetos locais externos registrados em projects.local.yaml."""
    forbidden = set()

    # Lê dinamicamente o overlay local da máquina do desenvolvedor (R-043)
    catalog_local = REPO_ROOT / ".github" / "projects.local.yaml"
    if not catalog_local.exists():
        catalog_local = REPO_ROOT / "docs" / "ai-context" / "catalog.local.yaml"

    if catalog_local.exists():
        try:
            data = yaml.safe_load(catalog_local.read_text(encoding="utf-8")) or {}
            for proj in data.get("projetos", []):
                p_id = (proj.get("id") or "").strip().lower()
                p_name = (proj.get("name") or "").strip().lower()
                if p_id and p_id not in THIS_REPO_TOKENS:
                    forbidden.add(p_id)
                if p_name and p_name not in THIS_REPO_TOKENS:
                    forbidden.add(p_name)
        except Exception:
            pass

    return forbidden


# ─────────────────────────────────────────────────────────────
# 1. Vazamento de Identificadores de Projetos Locais
# ─────────────────────────────────────────────────────────────

def test_no_local_projects_referenced_in_git_tracked_files():
    """Valida R-038 e R-044: nenhum arquivo rastreado pelo Git pode referenciar projetos locais externos."""
    forbidden_targets = get_forbidden_project_identifiers()
    tracked_files = get_git_tracked_files()

    media_extensions = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".db", ".sqlite", ".jar"}
    leaks: list[str] = []

    for fpath in tracked_files:
        if not fpath.exists():
            continue
        if fpath.suffix.lower() in media_extensions:
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore").lower()
            rel_path = fpath.relative_to(REPO_ROOT)
            for target in forbidden_targets:
                if target in content:
                    leaks.append(f"[{rel_path}] contém referência ao projeto local proibido: '{target}'")
        except Exception as e:
            leaks.append(f"[{fpath}] Erro ao ler arquivo: {e}")

    assert not leaks, (
        f"Foram detectadas {len(leaks)} referências a projetos locais em arquivos rastreados (violação R-038/R-044):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


# ─────────────────────────────────────────────────────────────
# 2. Guardrails do Gitignore (R-043)
# ─────────────────────────────────────────────────────────────

def test_r043_gitignore_isolation_rules():
    """Valida R-043: .github/projects.local.yaml e .github/instructions/local/ devem estar no .gitignore e não rastreados."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore deve existir na raiz do repositório"

    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    assert ".github/projects.local.yaml" in gitignore_content, (
        ".gitignore deve ignorar '.github/projects.local.yaml' (R-043)"
    )
    assert ".github/instructions/local/" in gitignore_content, (
        ".gitignore deve ignorar '.github/instructions/local/' (R-043)"
    )

    # Valida que nenhum arquivo em local/ ou projects.local.yaml está rastreado no git
    p_catalog = subprocess.run(
        ["git", "ls-files", ".github/projects.local.yaml"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert not p_catalog.stdout.strip(), (
        ".github/projects.local.yaml NUNCA deve ser rastreado pelo git (violação R-043)"
    )

    p_local_instructions = subprocess.run(
        ["git", "ls-files", ".github/instructions/local/"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert not p_local_instructions.stdout.strip(), (
        f"Arquivos sob .github/instructions/local/ NÃO devem ser rastreados: {p_local_instructions.stdout.strip()}"
    )


# ─────────────────────────────────────────────────────────────
# 3. Detecção de Caminhos Absolutos de Máquina Local (R-044)
# ─────────────────────────────────────────────────────────────

def test_no_machine_specific_paths_in_tracked_files():
    """Valida R-044: nenhum arquivo rastreado pode conter caminhos de máquina reais ou IDs de usuário."""
    tracked_files = get_git_tracked_files()

    # Regex para caminhos de máquina específicos não-genéricos
    user_id_pattern = re.compile(r'C:\\Users\\(?!\{username\}|<user>|Public|Default)[a-zA-Z0-9_-]+\\', re.IGNORECASE)

    media_extensions = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".db", ".sqlite", ".jar"}
    leaks: list[str] = []

    for fpath in tracked_files:
        if not fpath.exists():
            continue
        if fpath.suffix.lower() in media_extensions:
            continue

        rel_path = fpath.relative_to(REPO_ROOT)
        lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()

        for idx, line in enumerate(lines, 1):
            line_lower = line.lower()
            if any(term in line_lower for term in ["regex", "padrao", "placeholder", "removidos", "exemplo ilustrativo", "exemplos ilustrativos", "pre-commit"]):
                continue

            if user_id_pattern.search(line):
                leaks.append(f"[{rel_path}:{idx}] Caminho de usuário real de máquina: {line.strip()}")

    assert not leaks, (
        f"Foram detectados {len(leaks)} caminhos absolutos de máquina real (violação R-044):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


# ─────────────────────────────────────────────────────────────
# 4. Desacoplamento SSOT e Catálogo Único (Cenário 2 & R-043)
# ─────────────────────────────────────────────────────────────

def test_unique_catalog_and_zero_projects_in_shared_files():
    """Valida Cenário 2: .github/agents/catalog.yaml é o único catalog.yaml e não contém projetos."""
    # Valida que o antigo catalog.yaml em docs/ai-context foi extinto
    assert not (REPO_ROOT / "docs" / "ai-context" / "catalog.yaml").exists(), (
        "docs/ai-context/catalog.yaml deve ser extinto (Cenário 2 — Coesão em .github/)"
    )

    # Valida que .github/agents/catalog.yaml é o catálogo único de agents
    catalog_shared = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
    assert catalog_shared.exists(), ".github/agents/catalog.yaml deve existir como catálogo único"

    content = catalog_shared.read_text(encoding="utf-8")
    data = yaml.safe_load(content) or {}

    assert "projetos" not in data, (
        ".github/agents/catalog.yaml NÃO pode conter a chave 'projetos:'. "
        "Projetos devem ser declarados exclusivamente em .github/projects.local.yaml (R-043)."
    )

    assert "path_externo" not in content, (
        ".github/agents/catalog.yaml NÃO pode conter 'path_externo:' (R-043)."
    )

    # Valida que o template tracked de projetos existe
    template_tracked = REPO_ROOT / ".github" / "projects.local.yaml.example"
    assert template_tracked.exists(), ".github/projects.local.yaml.example deve existir como template rastreado"


# ─────────────────────────────────────────────────────────────
# 5. Genericidade Padronizada nos Artefatos de Workflow (R-038 & R-050)
# ─────────────────────────────────────────────────────────────

def test_generic_placeholders_in_workflow_and_router():
    """Valida que workflows.md, agent-router e handoff usam placeholders genéricos padronizados."""
    workflows_md = REPO_ROOT / ".github" / "agents" / "workflows.md"
    assert workflows_md.exists()
    content_wf = workflows_md.read_text(encoding="utf-8")
    assert "[PROJETO-ALVO]" in content_wf, "workflows.md deve usar o placeholder genérico [PROJETO-ALVO]"

    router_agent = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
    assert router_agent.exists()
    content_router = router_agent.read_text(encoding="utf-8")
    assert "[PROJETO-ALVO]" in content_router, "agent-router deve usar o placeholder genérico [PROJETO-ALVO]"

    handoff_skill = REPO_ROOT / ".github" / "skills" / "handoff-governance" / "SKILL.md"
    assert handoff_skill.exists()
    content_handoff = handoff_skill.read_text(encoding="utf-8")
    assert "[PROJETO-ALVO]" in content_handoff, "handoff-governance/SKILL.md deve usar o placeholder genérico [PROJETO-ALVO]"
