"""
test_router_model_tier_fanout.py — Validação determinística do modelo/tier dos routers de domínio backend e frontend.

Quality Gate que garante:
1. Os <stack>-router.agent.md utilizam modelo tier >= 1x (ex.: Sonnet, Opus, GPT-5)
   e NÃO estão em allowlist de tier baixo (Flash, Haiku, Mini).
2. O campo model no frontmatter do .agent.md é consistente com a declaração correspondente
   no arquivo .github/agents/catalog.yaml.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
AGENTS_BACKEND_DIR = REPO_ROOT / ".github" / "agents" / "backend"
AGENTS_FRONTEND_DIR = REPO_ROOT / ".github" / "agents" / "frontend"

ALL_ROUTER_STACKS = ["ejb", "spring-boot", "spring-reactive", "python", "struts", "angular"]

LOW_TIER_SUBSTRINGS = ["flash", "haiku", "mini", "small", "nano"]


def resolve_router_file(stack: str) -> Path:
    """Resolve o arquivo do router correspondente à stack (backend ou frontend)."""
    if stack == "angular":
        return AGENTS_FRONTEND_DIR / "angular" / "angular-router.agent.md"
    return AGENTS_BACKEND_DIR / stack / f"{stack}-router.agent.md"


def extract_frontmatter(file_path: Path) -> dict:
    """Extrai e parseia o frontmatter YAML de um arquivo .agent.md."""
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            return yaml.safe_load(parts[1]) or {}
        except Exception:
            return {}
    return {}


@pytest.fixture(scope="session")
def catalog_data() -> dict:
    """Carrega o conteúdo do catalog.yaml."""
    assert CATALOG_PATH.exists(), f"catalog.yaml não encontrado em {CATALOG_PATH}"
    content = CATALOG_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(content) or {}


@pytest.mark.parametrize("stack", ALL_ROUTER_STACKS)
def test_router_model_tier_is_high_tier(stack: str):
    """
    Garante que o <stack>-router.agent.md usa modelo de tier alto (>=1x)
    e não modelos baixos como Flash ou Haiku.
    """
    router_file = resolve_router_file(stack)
    assert router_file.exists(), f"Arquivo não encontrado: {router_file}"

    frontmatter = extract_frontmatter(router_file)
    model = str(frontmatter.get("model", "")).strip()

    assert model, f"{router_file.name} DEVE definir o campo 'model' no frontmatter"

    model_lower = model.lower()
    for low_tier in LOW_TIER_SUBSTRINGS:
        assert low_tier not in model_lower, (
            f"{router_file.name} não deve usar modelo low-tier ({model}), "
            f"pois routers exigem capacidade de raciocínio >= 1x."
        )


@pytest.mark.parametrize("stack", ALL_ROUTER_STACKS)
def test_router_model_consistent_with_catalog(catalog_data: dict, stack: str):
    """
    Garante paridade entre o frontmatter do <stack>-router.agent.md
    e a entrada <stack>-router no catalog.yaml (R-015 / R-040).
    """
    router_file = resolve_router_file(stack)
    frontmatter = extract_frontmatter(router_file)
    model_frontmatter = str(frontmatter.get("model", "")).strip()

    router_key = f"{stack}-router"
    agents_dict = catalog_data.get("agents", {})
    catalog_entry = agents_dict.get(router_key) or catalog_data.get(router_key)

    assert catalog_entry is not None, f"{router_key} não encontrado em catalog.yaml (seção agents)"
    model_catalog = str(catalog_entry.get("model", "")).strip()

    assert model_frontmatter == model_catalog, (
        f"Inconsistência de modelo para {router_key}: "
        f"frontmatter='{model_frontmatter}' vs catalog='{model_catalog}'"
    )
