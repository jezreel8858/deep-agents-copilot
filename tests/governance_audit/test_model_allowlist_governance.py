"""
test_model_allowlist_governance.py — Validação determinística da allowlist de modelos (T-B1.6).

Quality Gate determinístico que garante:
1. Paridade catalog.yaml model: <-> frontmatter <-> default <-> allowlist (Achado 1).
2. model-allowlist.yaml possui schema válido, names únicos, campos obrigatórios e ranges numéricos válidos.
3. Hoist de source e verified_at no nível global com override por item e URL oficial documentada.
4. Provider vs nome do modelo consistente.
5. Todo model: configurado em .github/agents/** e .github/prompts/** pertence à allowlist e é pinnable=True.
6. Todo modelo referenciado nos perfis built-in de model-profiles.yaml pertence à allowlist e é pinnable=True.
7. Frescor global via função pura com injeção de data e rejeição de datas futuras.
8. Custos e cost_rank são únicos e contíguos com desempate alfabético verificado.
9. deprecated/retired exige retirement_date e retired não pode ser pinnable.
"""
from __future__ import annotations

import datetime
import difflib
from pathlib import Path
import warnings
import pytest
import yaml

from tests.governance_audit._helpers import (
    check_allowlist_freshness,
    collect_repo_frontmatter_files,
    load_allowlist,
    load_profiles,
    safe_load_yaml_unique,
)
from tools.model_profiles.resolver import resolve_profile

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = REPO_ROOT / "model-allowlist.yaml"
PROFILES_PATH = REPO_ROOT / "model-profiles.yaml"
CATALOG_PATH = REPO_ROOT / ".github" / "agents" / "catalog.yaml"

VALID_PROVIDERS = {"anthropic", "google", "openai", "xai", "github"}
VALID_STATUSES = {"ga", "preview", "deprecated", "retired", "special"}
VALID_COST_LABELS = {"low", "medium", "high", "variable", None}

PROVIDER_PREFIX_RULES = {
    "Claude": "anthropic",
    "Gemini": "google",
    "GPT": "openai",
    "Grok": "xai",
    "Auto": "github",
}


def test_catalog_frontmatter_default_allowlist_parity():
    """Valida a paridade quádrupla entre catalog.yaml model: <-> frontmatter <-> default <-> allowlist (Achado 1)."""
    assert CATALOG_PATH.exists(), "catalog.yaml deve existir"
    catalog_data = safe_load_yaml_unique(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog_agents = catalog_data.get("agents", {})

    allowlist = load_allowlist(REPO_ROOT)
    pinnable_names = {m["name"] for m in allowlist["models"] if m.get("pinnable")}

    profiles_data = load_profiles(REPO_ROOT)
    resolved_default = resolve_profile("default", profiles_data["profiles"])

    tier_map = profiles_data["tier_map"]
    key_to_tier = {item: t for t, items in tier_map.items() for item in items}

    repo_files = collect_repo_frontmatter_files(REPO_ROOT)

    mismatches = []
    for agent_name, cinfo in catalog_agents.items():
        cat_model = cinfo.get("model")
        # 1. Deve constar na allowlist e ser pinnable
        if cat_model not in pinnable_names:
            mismatches.append(f"Agent '{agent_name}': model '{cat_model}' em catalog.yaml não é pinnable na allowlist")

        # 2. Deve bater com o frontmatter do arquivo
        if agent_name in repo_files:
            _, fm_model = repo_files[agent_name]
            if cat_model != fm_model:
                mismatches.append(f"Agent '{agent_name}': catalog.yaml='{cat_model}' != frontmatter='{fm_model}'")
        else:
            mismatches.append(f"Agent '{agent_name}' declarado em catalog.yaml não encontrado nos arquivos .agent.md")

        # 3. Deve bater com o perfil default resolvido
        tier = key_to_tier.get(agent_name)
        if not tier:
            mismatches.append(f"Agent '{agent_name}' não possui tier associado em tier_map")
        else:
            def_model = resolved_default["tiers"].get(tier)
            if cat_model != def_model:
                mismatches.append(f"Agent '{agent_name}': catalog.yaml='{cat_model}' != default_resolvido='{def_model}'")

    assert not mismatches, "Divergências na paridade quádrupla catalog <-> frontmatter <-> default <-> allowlist:\n" + "\n".join(mismatches)


def test_allowlist_schema_and_mandatory_fields():
    """Valida schema_version, sources globais e por item, e campos obrigatórios de cada modelo."""
    data = load_allowlist(REPO_ROOT)
    assert data.get("schema_version") == 1, "schema_version deve ser 1"
    assert isinstance(data.get("freshness_days"), int) and data["freshness_days"] >= 1, "freshness_days deve ser int >= 1"

    # Hoist de source e verified_at no nível global com URL oficial
    global_source = data.get("source")
    global_sources = data.get("sources")
    assert global_source or global_sources, "Allowlist deve conter source ou sources no nível global"
    official_url = None
    if isinstance(global_sources, dict):
        official_url = global_sources.get("official")
    if not official_url and isinstance(global_source, str) and "https://" in global_source:
        official_url = global_source
    assert official_url and "https://" in official_url, "Allowlist deve conter URL oficial documentada no source global"

    global_verified_at = data.get("verified_at")
    assert global_verified_at, "verified_at global obrigatório"

    assert "models" in data and isinstance(data["models"], list), "models deve ser uma lista"
    assert len(data["models"]) > 0, "Allowlist não pode estar vazia"

    names_seen = set()
    for entry in data["models"]:
        assert isinstance(entry, dict), "Cada entrada de modelo deve ser um dict"
        name = entry.get("name")
        assert name and isinstance(name, str), f"Modelo sem 'name' válido: {entry}"
        assert name not in names_seen, f"Nome duplicado na allowlist: {name}"
        names_seen.add(name)

        provider = entry.get("provider")
        assert provider in VALID_PROVIDERS, f"Provider inválido para {name}: {provider}"

        # Validação provider vs nome do modelo
        for prefix, expected_provider in PROVIDER_PREFIX_RULES.items():
            if name.startswith(prefix):
                assert provider == expected_provider, (
                    f"Inconsistência de provider para {name}: esperado '{expected_provider}', obteve '{provider}'"
                )

        status = entry.get("status")
        assert status in VALID_STATUSES, f"Status inválido para {name}: {status}"

        pinnable = entry.get("pinnable")
        assert isinstance(pinnable, bool), f"pinnable deve ser booleano para {name}"

        # verified_at e source (efetivos: item ou herdado do global)
        effective_verified_at = entry.get("verified_at", global_verified_at)
        assert effective_verified_at, f"verified_at obrigatório (local ou global) para {name}"

        effective_source = entry.get("source", global_source)
        assert effective_source, f"source obrigatório (local ou global) para {name}"

        # deprecated / retired
        retirement_date = entry.get("retirement_date")
        if status in ("deprecated", "retired"):
            assert retirement_date is not None, f"Modelo '{name}' com status '{status}' exige retirement_date preenchido"
        if status == "retired":
            assert pinnable is False, f"Modelo aposentado (retired) '{name}' não pode ser pinnable"

        # Validação de custos e ranges numéricos
        cost = entry.get("cost")
        if cost is not None:
            assert isinstance(cost, dict), f"cost deve ser dict ou null para {name}"
            assert cost.get("label") in VALID_COST_LABELS, f"label de custo inválido para {name}"
            assert cost.get("unit") == "credits_per_1M_tokens", f"unit deve ser credits_per_1M_tokens para {name}"
            for num_field in ("input", "output", "cache_read", "cache_write"):
                val = cost.get(num_field)
                if val is not None:
                    assert isinstance(val, (int, float)) and val >= 0, (
                        f"Campo de custo '{num_field}' para '{name}' deve ser número >= 0, obteve {val}"
                    )


def test_cost_rank_unique_contiguous_and_tie_breaking():
    """Valida cost_rank único, contíguo de 1 a N, e desempate alfabético verificado."""
    data = load_allowlist(REPO_ROOT)
    models = {m["name"]: m for m in data["models"]}

    # Auto deve ser pinnable: false e cost_rank: null
    assert models["Auto"]["pinnable"] is False, "Auto não pode ser pinnable"
    assert models["Auto"]["cost_rank"] is None, "Auto deve ter cost_rank null"

    # Modelos pinnable
    pinnable_models = [m for m in data["models"] if m.get("pinnable")]
    ranks = [m.get("cost_rank") for m in pinnable_models]

    assert all(isinstance(r, int) and r >= 1 for r in ranks), "Todos os modelos pinnable devem ter cost_rank >= 1"

    # Únicos e contíguos de 1 a len(pinnable_models)
    sorted_ranks = sorted(ranks)
    expected_ranks = list(range(1, len(pinnable_models) + 1))
    assert sorted_ranks == expected_ranks, (
        f"cost_ranks devem ser contíguos de 1 a {len(pinnable_models)}, obteve: {sorted_ranks}"
    )

    # Menor rank é Haiku, maior é Opus
    assert models["Claude Haiku 5.5"]["cost_rank"] == 1
    assert models["Claude Opus 5.5"]["cost_rank"] == len(pinnable_models)

    # Desempate determinístico verificado
    # Claude Sonnet 5.5 e GPT-6.1 Sol têm mesmos custos de input/output (300/1500)
    sonnet = models["Claude Sonnet 5.5"]
    sol = models["GPT-6.1 Sol"]
    assert sonnet["cost"]["input"] == sol["cost"]["input"]
    assert sonnet["cost"]["output"] == sol["cost"]["output"]
    # Desempate alfabético: "Claude Sonnet 5.5" < "GPT-6.1 Sol" => rank(Sonnet) < rank(Sol)
    assert sonnet["name"] < sol["name"]
    assert sonnet["cost_rank"] < sol["cost_rank"], (
        f"Desempate alfabético falhou: {sonnet['name']} ({sonnet['cost_rank']}) vs {sol['name']} ({sol['cost_rank']})"
    )


def test_all_repo_frontmatter_models_in_allowlist():
    """Garante que todo model: em .github/agents/** e .github/prompts/** pertence à allowlist e é pinnable."""
    data = load_allowlist(REPO_ROOT)
    pinnable_models = {m["name"] for m in data["models"] if m.get("pinnable")}
    all_allowed_names = {m["name"] for m in data["models"]}

    repo_files = collect_repo_frontmatter_files(REPO_ROOT)
    assert len(repo_files) > 0, "Nenhum arquivo com model: encontrado no repositório"

    invalid_entries = []
    for key, (file_path, model_name) in repo_files.items():
        if model_name not in pinnable_models:
            rel_path = file_path.relative_to(REPO_ROOT).as_posix()
            suggestions = difflib.get_close_matches(model_name, list(all_allowed_names), n=2, cutoff=0.4)
            sugg_str = f" Sugestões: {suggestions}" if suggestions else ""
            if model_name in all_allowed_names:
                invalid_entries.append(f"{rel_path}: '{model_name}' está na allowlist mas NÃO é pinnable.{sugg_str}")
            else:
                invalid_entries.append(f"{rel_path}: '{model_name}' NÃO está na allowlist.{sugg_str}")

    assert not invalid_entries, (
        f"Foram encontrados {len(invalid_entries)} arquivos com modelos inválidos ou não pinnable:\n"
        + "\n".join(invalid_entries)
    )


def test_built_in_profiles_models_in_allowlist():
    """Garante que todos os modelos referenciados nos perfis de model-profiles.yaml estão na allowlist e são pinnable."""
    data = load_allowlist(REPO_ROOT)
    pinnable_models = {m["name"] for m in data["models"] if m.get("pinnable")}
    all_allowed_names = {m["name"] for m in data["models"]}

    profiles_data = load_profiles(REPO_ROOT)
    for profile_name, pdata in profiles_data["profiles"].items():
        resolved = resolve_profile(profile_name, profiles_data["profiles"])
        for tier_name, model_name in resolved["tiers"].items():
            if model_name not in pinnable_models:
                suggestions = difflib.get_close_matches(model_name, list(all_allowed_names), n=2, cutoff=0.4)
                sugg_str = f" Sugestões: {suggestions}" if suggestions else ""
                pytest.fail(
                    f"Perfil '{profile_name}', tier '{tier_name}': modelo '{model_name}' não é pinnable ou não consta na allowlist.{sugg_str}"
                )


def test_allowlist_freshness_pure_function():
    """Valida frescor com injeção de datas via função pura e rejeição de data futura."""
    ref_date = datetime.date(2026, 10, 10)

    # 1. Data exatamente igual => fresh
    is_fresh, msg = check_allowlist_freshness(ref_date, freshness_days=30, as_of_date=ref_date)
    assert is_fresh is True
    assert msg is None

    # 2. 29 dias depois => fresh
    is_fresh, msg = check_allowlist_freshness(ref_date, freshness_days=30, as_of_date=ref_date + datetime.timedelta(days=29))
    assert is_fresh is True

    # 3. 31 dias depois => warning
    is_fresh, msg = check_allowlist_freshness(ref_date, freshness_days=30, as_of_date=ref_date + datetime.timedelta(days=31))
    assert is_fresh is False
    assert "Allowlist com 31 dias" in msg

    # 4. Data no futuro => lança ValueError
    with pytest.raises(ValueError, match="está no futuro"):
        check_allowlist_freshness(ref_date + datetime.timedelta(days=5), freshness_days=30, as_of_date=ref_date)


def test_allowlist_freshness_warning_live():
    """Alerta via warnings.warn caso a data da allowlist esteja com mais de 30 dias em tempo real."""
    data = load_allowlist(REPO_ROOT)
    verified_str = data.get("verified_at")
    assert verified_str, "model-allowlist.yaml deve conter 'verified_at' global"

    if isinstance(verified_str, datetime.date):
        verified_date = verified_str
    else:
        verified_date = datetime.datetime.strptime(str(verified_str), "%Y-%m-%d").date()

    freshness_days = data.get("freshness_days", 30)
    is_fresh, msg = check_allowlist_freshness(verified_date, freshness_days=freshness_days)
    if not is_fresh:
        warnings.warn(msg, UserWarning, stacklevel=2)
