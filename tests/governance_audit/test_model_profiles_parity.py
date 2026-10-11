"""
test_model_profiles_parity.py — Validação de paridade dos perfis e tier_map (T-B1.7).

Quality Gate determinístico que garante:
1. O perfil built-in 'default' resolvido bate 100% com o model: atual de cada um dos arquivos
   (contagem dinâmica em .github/agents/** e .github/prompts/**).
2. O tier_map cobre 100% dos arquivos do repositório que possuem frontmatter model:, sem duplicidade.
3. Precedência de resolução D2 por tabela de casos: agents/prompts > tiers > extends > default.
4. Detecção determinística de ciclos em extends com lista ordenada de caminho.
5. Perfil 'economico' rebaixa orchestration e standard para Claude Haiku 5.5 (IA-4).
6. get_canonical_key usa relative_to sem split nem resolve().
7. Todo perfil resolvido cobre todos os tiers do tier_map.
8. agents: e prompts: dos perfis built-in e do model-profiles.local.yaml.example são válidos.
9. Forma canônica prompt:<nome> é exigida e formas alternativas são rejeitadas.
10. Bordas de resolve_profile e loader YAML que falha em chaves duplicadas.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import (
    collect_repo_frontmatter_files,
    load_allowlist,
    load_profiles,
    safe_load_yaml_unique,
)
from tools.model_profiles.resolver import (
    get_canonical_key,
    get_tier_for_key,
    normalize_model_name,
    resolve_profile,
    resolve_target_model,
    validate_profile_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = REPO_ROOT / "model-profiles.yaml"
LOCAL_EXAMPLE_PATH = REPO_ROOT / "model-profiles.local.yaml.example"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"


def test_tier_map_covers_100_percent_without_duplicates():
    """Valida que tier_map cobre exatamente 100% dos arquivos com model: sem nenhuma duplicidade."""
    data = load_profiles(REPO_ROOT)
    assert "tier_map" in data, "tier_map deve existir em model-profiles.yaml"
    tier_map = data["tier_map"]

    repo_files = collect_repo_frontmatter_files(REPO_ROOT)
    repo_keys = set(repo_files.keys())

    # Verifica duplicidade no tier_map
    seen_keys: dict[str, str] = {}
    for tier_name, items in tier_map.items():
        assert isinstance(items, list), f"Tier '{tier_name}' deve ser uma lista de chaves"
        for item in items:
            assert item not in seen_keys, f"Chave '{item}' duplicada: presente em '{seen_keys[item]}' e '{tier_name}'"
            seen_keys[item] = tier_name

    tier_map_keys = set(seen_keys.keys())

    # Diferença nos dois sentidos
    missing_in_tier_map = repo_keys - tier_map_keys
    unknown_in_tier_map = tier_map_keys - repo_keys

    msg = []
    if missing_in_tier_map:
        msg.append(f"Arquivos com model: ausentes do tier_map ({len(missing_in_tier_map)}): {sorted(missing_in_tier_map)}")
    if unknown_in_tier_map:
        msg.append(f"Chaves no tier_map sem arquivo correspondente ({len(unknown_in_tier_map)}): {sorted(unknown_in_tier_map)}")

    assert not msg, "\n".join(msg)


def test_default_profile_parity_with_frontmatters():
    """Valida que o perfil 'default' resolvido bate 100% com o model: de cada arquivo no repositório."""
    data = load_profiles(REPO_ROOT)
    tier_map = data["tier_map"]
    profiles = data["profiles"]

    key_to_tier = {}
    for tier_name, items in tier_map.items():
        for item in items:
            key_to_tier[item] = tier_name

    resolved_default = resolve_profile("default", profiles)
    repo_files = collect_repo_frontmatter_files(REPO_ROOT)

    mismatches = []
    for key, (file_path, actual_model) in repo_files.items():
        tier = get_tier_for_key(key, key_to_tier)
        resolved_model = resolve_target_model(key, tier, resolved_default)
        if resolved_model != actual_model:
            rel_path = file_path.relative_to(REPO_ROOT).as_posix()
            mismatches.append(
                f"{rel_path} ({key}): frontmatter='{actual_model}', default_resolvido='{resolved_model}' (tier={tier})"
            )

    assert not mismatches, (
        f"Foram encontradas {len(mismatches)} divergências entre perfil default e frontmatters canônicos:\n"
        + "\n".join(mismatches)
    )


def test_economico_profile_downgrades_orchestration_and_standard_to_haiku():
    """Valida que o perfil 'economico' rebaixa orchestration e standard para Claude Haiku 5.5 conforme IA-4 e D6."""
    data = load_profiles(REPO_ROOT)
    profiles = data["profiles"]
    resolved_economico = resolve_profile("economico", profiles)

    assert resolved_economico["tiers"]["orchestration"] == "Claude Haiku 5.5", (
        f"orchestration em economico deve ser 'Claude Haiku 5.5', obteve: {resolved_economico['tiers']['orchestration']}"
    )
    assert resolved_economico["tiers"]["standard"] == "Claude Haiku 5.5", (
        f"standard em economico deve ser 'Claude Haiku 5.5', obteve: {resolved_economico['tiers']['standard']}"
    )
    # Herança do balanceado (premium) e default (light)
    assert resolved_economico["tiers"]["premium"] == "Claude Sonnet 5.5"
    assert resolved_economico["tiers"]["light"] == "Gemini 3.8 Flash"


def test_all_resolved_profiles_cover_all_tier_map_tiers():
    """Garante que todo perfil built-in resolvido cobre 100% dos tiers declarados no tier_map (Achado 7)."""
    data = load_profiles(REPO_ROOT)
    tier_map_tiers = set(data["tier_map"].keys())
    profiles = data["profiles"]

    for profile_name in profiles.keys():
        resolved = resolve_profile(profile_name, profiles)
        resolved_tiers = set(resolved["tiers"].keys())
        missing_tiers = tier_map_tiers - resolved_tiers
        assert not missing_tiers, (
            f"Perfil '{profile_name}' resolvido não cobre todos os tiers do tier_map: ausentes {missing_tiers}"
        )


def test_builtin_and_local_example_agents_prompts_validation():
    """Valida agents: e prompts: dos perfis built-in e do model-profiles.local.yaml.example (Achado 8)."""
    data = load_profiles(REPO_ROOT)
    allowlist = load_allowlist(REPO_ROOT)
    pinnable_names = {m["name"] for m in allowlist["models"] if m.get("pinnable")}

    tier_map = data["tier_map"]
    all_agent_keys = {item for t, items in tier_map.items() for item in items if not item.startswith("prompt:")}
    all_prompt_keys = {item for t, items in tier_map.items() for item in items if item.startswith("prompt:")}

    # Valida perfis built-in
    for profile_name, pdata in data["profiles"].items():
        validate_profile_keys(profile_name, pdata, all_agent_keys, all_prompt_keys)
        resolved = resolve_profile(profile_name, data["profiles"])
        for m in resolved["tiers"].values():
            assert m in pinnable_names, f"Modelo '{m}' no perfil built-in '{profile_name}' não é pinnable na allowlist"

    # Valida model-profiles.local.yaml.example
    assert LOCAL_EXAMPLE_PATH.exists(), "model-profiles.local.yaml.example deve existir"
    local_data = safe_load_yaml_unique(LOCAL_EXAMPLE_PATH.read_text(encoding="utf-8"))
    assert "profiles" in local_data, "model-profiles.local.yaml.example deve conter 'profiles'"

    combined_profiles = dict(data["profiles"])
    combined_profiles.update(local_data["profiles"])

    for local_name, local_pdata in local_data["profiles"].items():
        validate_profile_keys(local_name, local_pdata, all_agent_keys, all_prompt_keys)
        resolved = resolve_profile(local_name, combined_profiles)
        for t, m in resolved["tiers"].items():
            assert m in pinnable_names, f"Tier '{t}' no perfil local '{local_name}' usa modelo inválido '{m}'"
        for a, m in resolved["agents"].items():
            assert m in pinnable_names, f"Agent '{a}' no perfil local '{local_name}' usa modelo inválido '{m}'"
            assert a in all_agent_keys, f"Agent '{a}' no perfil local '{local_name}' não consta no tier_map"
        for p, m in resolved["prompts"].items():
            assert m in pinnable_names, f"Prompt '{p}' no perfil local '{local_name}' usa modelo inválido '{m}'"
            assert p in all_prompt_keys, f"Prompt '{p}' no perfil local '{local_name}' não consta no tier_map"


def test_canonical_prompt_key_and_error_on_non_canonical():
    """Garante a forma canônica prompt:<nome> e testa que formas alternativas falham como erro (Achado 9)."""
    # 1. get_canonical_key para prompts gera com prefixo prompt:
    p_path = PROMPTS_DIR / "commit.prompt.md"
    assert get_canonical_key(p_path, agents_dir=AGENTS_DIR, prompts_dir=PROMPTS_DIR) == "prompt:commit"

    # 2. validate_profile_keys rejeita chaves em prompts: sem o prefixo prompt:
    invalid_profile = {
        "prompts": {
            "commit": "Gemini 3.8 Flash"  # forma não-canônica (sem 'prompt:')
        }
    }
    with pytest.raises(ValueError, match="deve usar a forma canônica 'prompt:<nome>'"):
        validate_profile_keys("teste-invalido", invalid_profile)

    # 3. resolve_profile rejeita prompt sem prefixo canônico
    with pytest.raises(ValueError, match="deve usar a forma canônica 'prompt:<nome>'"):
        resolve_profile("teste-invalido", {"teste-invalido": invalid_profile})


def test_get_canonical_key_uses_relative_to_without_resolve_or_split():
    """Testa get_canonical_key contra agents e prompts comuns e templates (Achado 5)."""
    agent_file = AGENTS_DIR / "debugger.agent.md"
    assert get_canonical_key(agent_file, agents_dir=AGENTS_DIR, prompts_dir=PROMPTS_DIR) == "debugger"

    agent_template = AGENTS_DIR / "templates" / "router-agent.md"
    assert get_canonical_key(agent_template, agents_dir=AGENTS_DIR, prompts_dir=PROMPTS_DIR) == "templates/router-agent"

    prompt_file = PROMPTS_DIR / "deep-search.prompt.md"
    assert get_canonical_key(prompt_file, agents_dir=AGENTS_DIR, prompts_dir=PROMPTS_DIR) == "prompt:deep-search"

    prompt_template = PROMPTS_DIR / "templates" / "prompt-template.md"
    assert get_canonical_key(prompt_template, agents_dir=AGENTS_DIR, prompts_dir=PROMPTS_DIR) == "prompt:templates/prompt-template"


def test_key_to_tier_error_message():
    """Garante mensagem amigável e clara em vez de KeyError cru ao buscar chave inexistente (Achado 6)."""
    key_to_tier = {"debugger": "premium"}
    with pytest.raises(KeyError) as exc_info:
        get_tier_for_key("agente-fantasma", key_to_tier)
    assert "agente-fantasma" in str(exc_info.value)
    assert "não encontrada no tier_map" in str(exc_info.value)


def test_precedence_d2_table_cases():
    """Testa por tabela a regra de precedência D2: agents/prompts > tiers > extends > default."""
    synthetic_profiles = {
        "default": {
            "tiers": {
                "premium": "Claude Opus 5.5",
                "orchestration": "Claude Sonnet 5.5",
                "standard": "Claude Sonnet 5.5",
                "light": "Gemini 3.8 Flash",
            }
        },
        "base_custom": {
            "extends": "default",
            "tiers": {"standard": "Grok 4.7"},
        },
        "child_custom": {
            "extends": "base_custom",
            "agents": {"special-agent": "Claude Opus 5.5"},
            "prompts": {"prompt:special-prompt": "Claude Haiku 5.5"},
        },
    }

    resolved = resolve_profile("child_custom", synthetic_profiles)

    # 1. Herança do default (não modificado em base nem child)
    assert resolve_target_model("tech-solution-architect", "premium", resolved) == "Claude Opus 5.5"
    assert resolve_target_model("agent-router", "orchestration", resolved) == "Claude Sonnet 5.5"
    assert resolve_target_model("prompt:review", "light", resolved) == "Gemini 3.8 Flash"

    # 2. Sobrescrita de tier via base_custom (extends)
    assert resolve_target_model("python-developer", "standard", resolved) == "Grok 4.7"

    # 3. Sobrescrita pontual de agent ganha do tier
    assert resolve_target_model("special-agent", "standard", resolved) == "Claude Opus 5.5"

    # 4. Sobrescrita pontual de prompt ganha do tier
    assert resolve_target_model("prompt:special-prompt", "light", resolved) == "Claude Haiku 5.5"


def test_cycle_detection_in_extends_deterministic_order():
    """Garante que ciclos em extends geram ValueError com caminho ordenado e determinístico (Achado 6)."""
    cyclic_profiles = {
        "p1": {"extends": "p2"},
        "p2": {"extends": "p3"},
        "p3": {"extends": "p1"},
    }

    with pytest.raises(ValueError) as exc_info:
        resolve_profile("p1", cyclic_profiles)

    assert "Ciclo detectado em extends: p1 -> p2 -> p3 -> p1" in str(exc_info.value)

    # Autoextensão direta
    self_extending = {"self": {"extends": "self"}}
    with pytest.raises(ValueError) as exc_self:
        resolve_profile("self", self_extending)
    assert "Ciclo detectado em extends: self -> self" in str(exc_self.value)


def test_resolve_profile_edge_cases():
    """Valida bordas: extends inexistente, tiers null, herança de description e quality_warning, nomes não-string."""
    # 1. Extends inexistente
    with pytest.raises(KeyError, match="Perfil base 'inexistente' referenciado por 'p' não existe"):
        resolve_profile("p", {"p": {"extends": "inexistente"}})

    # 2. Perfil inexistente
    with pytest.raises(KeyError, match="Perfil 'fantasma' não encontrado"):
        resolve_profile("fantasma", {})

    # 3. Tiers null e herança de metadata
    profiles = {
        "base": {
            "description": "Base desc",
            "quality_warning": "Warning base",
            "tiers": {"light": "Gemini 3.8 Flash"},
        },
        "child": {
            "extends": "base",
            "tiers": None,  # tiers null
            "agents": None,
            "prompts": None,
        },
        "child_override": {
            "extends": "base",
            "description": "Child desc",
            "quality_warning": None,  # herda base se None
            "tiers": {"standard": "Grok 4.7"},
        },
    }

    res_child = resolve_profile("child", profiles)
    assert res_child["tiers"]["light"] == "Gemini 3.8 Flash"
    assert res_child["description"] == "Base desc"
    assert res_child["quality_warning"] == "Warning base"

    res_override = resolve_profile("child_override", profiles)
    assert res_override["description"] == "Child desc"
    assert res_override["quality_warning"] == "Warning base"
    assert res_override["tiers"]["standard"] == "Grok 4.7"

    # 4. Rejeição de modelo não-string
    invalid_model_profile = {
        "bad": {
            "tiers": {"light": 12345}  # int em vez de str
        }
    }
    with pytest.raises(TypeError, match="Nome do modelo deve ser string"):
        resolve_profile("bad", invalid_model_profile)


def test_yaml_loader_fails_on_duplicate_keys():
    """Garante que o carregador YAML falha determinísticamente em chave duplicada (Achado 10)."""
    dup_yaml = """
    key1: value1
    key1: value2
    """
    with pytest.raises(yaml.constructor.ConstructorError) as exc_info:
        safe_load_yaml_unique(dup_yaml)
    assert "Chave duplicada encontrada no YAML: 'key1'" in str(exc_info.value)
