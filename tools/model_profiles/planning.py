"""Contexto e modelos de dados de planejamento (apply/doctor)."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.model_profiles import allowlist, config, hierarchy, resolver, targets
from tools.model_profiles.errors import RefusalError
from tools.model_profiles.findings import Finding

PROFILES_FILE = "model-profiles.yaml"
LOCAL_PROFILES_FILE = "model-profiles.local.yaml"
LOCAL_PROFILES_EXAMPLE = "model-profiles.local.yaml.example"
ALLOWLIST_FILE = "model-allowlist.yaml"
ROUTING_GRAPH = ".github/agents/routing-graph.yaml"


@dataclass(frozen=True)
class Context:
    repo: Path
    cfg: dict[str, Any]
    allow: allowlist.Allowlist
    targets: list[targets.Target]
    edges: list[tuple[str, str]]
    key_to_tier: dict[str, str]
    local_names: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Change:
    target: targets.Target
    new_model: str
    new_data: bytes


@dataclass
class ProfilePlan:
    name: str
    resolved: dict[str, Any]
    models: dict[str, str]
    changes: list[Change] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


def _load_edges(repo: Path) -> list[tuple[str, str]]:
    graph = repo / ROUTING_GRAPH
    return hierarchy.load_edges(graph) if graph.exists() else []


def resolve_tier_for_key(key: str, tier_map: dict[str, Any]) -> str | None:
    """Resolve o tier de um agent/prompt suportando correspondência exata, wildcards (glob) e regex."""
    if not isinstance(tier_map, dict):
        return None

    # 1. Busca por correspondência exata (maior prioridade)
    for tier, keys in tier_map.items():
        if keys and key in keys:
            return str(tier)

    # 2. Busca por Padrões Wildcard (ex: "*-arch-advisor") ou Regex
    for tier, keys in tier_map.items():
        for pattern in keys or []:
            pattern_str = str(pattern)

            # Match via Wildcard/Glob (ex: *-arch-advisor)
            if fnmatch.fnmatch(key, pattern_str):
                return str(tier)

            # Match via Regex (ex: ^.*-arch-advisor$)
            try:
                if re.search(pattern_str, key):
                    return str(tier)
            except re.error:
                continue

    return None


def build_key_to_tier_map(known_keys: set[str], tier_map: dict[str, Any]) -> dict[str, str]:
    """Resolve dinamicamente o tier para cada chave conhecida no repositório."""
    resolved_map = {}
    for key in known_keys:
        tier = resolve_tier_for_key(key, tier_map)
        if tier:
            resolved_map[key] = tier
    return resolved_map


def _reject_local_tier_map(builtin: Any, local_tm: Any) -> None:
    """Perfil local nao pode introduzir nem mover chaves do tier_map canonico."""
    if local_tm is None:
        return
    if not isinstance(local_tm, dict) or not isinstance(builtin, dict):
        raise RefusalError("tier_map local deve ser um mapeamento", "TIER_MAP")
    targets.validate_keys(local_tm)

    for tier, keys in local_tm.items():
        if str(tier) not in builtin:
            raise RefusalError(f"tier_map local nao pode definir tier novo '{tier}'", "TIER_MAP")
        for key in keys or []:
            key_s = str(key)
            resolved_builtin_tier = resolve_tier_for_key(key_s, builtin)
            if resolved_builtin_tier is None:
                raise RefusalError(
                    f"tier_map local nao pode definir chave nova '{key_s}'", "TIER_MAP")
            if resolved_builtin_tier != str(tier):
                raise RefusalError(
                    f"tier_map local nao pode mover a chave '{key_s}'", "TIER_MAP")


def _validate_profile_shapes(profiles: dict[str, Any], key_to_tier: dict[str, str]) -> None:
    """Mesmas regras dos built-in: forma prompt:<nome>, chaves do tier_map e path traversal."""
    agent_keys = {k for k in key_to_tier if not k.startswith("prompt:")}
    prompt_keys = {k for k in key_to_tier if k.startswith("prompt:")}
    for name, spec in profiles.items():
        if not isinstance(spec, dict):
            raise RefusalError(f"perfil '{name}' deve ser um mapeamento", "PROFILE")
        agents = spec.get("agents") or {}
        prompts = spec.get("prompts") or {}
        if not isinstance(agents, dict) or not isinstance(prompts, dict):
            raise RefusalError(
                f"perfil '{name}': agents e prompts devem ser mapeamentos", "PROFILE")
        keys = [str(k) for k in agents] + [str(k) for k in prompts]
        if keys:
            targets.validate_keys({"_": keys})
        try:
            resolver.validate_profile_keys(str(name), spec, agent_keys, prompt_keys)
        except (KeyError, TypeError, ValueError) as exc:
            raise RefusalError(str(exc), "PROFILE") from exc


def load_merged(repo: Path) -> tuple[dict[str, Any], frozenset[str]]:
    """Carrega built-in e, se existir, mescla `profiles` do arquivo local.

    Arquivo ausente e gracioso. Nome igual a built-in ou chave nova em tier_map recusa.
    """
    cfg = config.load_yaml(repo / PROFILES_FILE)
    tier_map = cfg.get("tier_map") or {}
    targets.validate_keys(tier_map)

    discovered_keys = targets.discover_all_keys(repo)
    key_to_tier = build_key_to_tier_map(discovered_keys, tier_map if isinstance(tier_map, dict) else {})

    builtin = cfg.get("profiles") or {}
    if not isinstance(builtin, dict):
        raise RefusalError("profiles built-in deve ser um mapeamento", "CONFIG")
    local_names: set[str] = set()
    local_path = repo / LOCAL_PROFILES_FILE
    if local_path.exists():
        local = config.load_yaml(local_path)
        _reject_local_tier_map(tier_map, local.get("tier_map"))
        local_profiles = local.get("profiles") or {}
        if not isinstance(local_profiles, dict):
            raise RefusalError("profiles local deve ser um mapeamento", "CONFIG")
        for name in local_profiles:
            if name in builtin:
                raise RefusalError(
                    f"perfil local '{name}' colide com perfil built-in", "PROFILE_COLLISION")
        cfg = dict(cfg)
        cfg["profiles"] = {**builtin, **local_profiles}
        local_names = set(local_profiles)
    _validate_profile_shapes(cfg.get("profiles") or {}, key_to_tier)
    return cfg, frozenset(local_names)


def load_context(repo: Path) -> Context:
    cfg, local_names = load_merged(repo)
    tier_map = cfg.get("tier_map") or {}

    discovered_keys = targets.discover_all_keys(repo)
    key_to_tier = build_key_to_tier_map(discovered_keys, tier_map)

    return Context(
        repo=repo,
        cfg=cfg,
        allow=allowlist.load(repo / ALLOWLIST_FILE),
        targets=targets.discover(repo, key_to_tier),
        edges=_load_edges(repo),
        key_to_tier=key_to_tier,
        local_names=local_names,
    )
