"""Contexto e modelos de dados de planejamento (apply/doctor)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.model_profiles import allowlist, config, hierarchy, targets
from tools.model_profiles.findings import Finding

PROFILES_FILE = "model-profiles.yaml"
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


def load_context(repo: Path) -> Context:
    cfg = config.load_yaml(repo / PROFILES_FILE)
    tier_map = cfg.get("tier_map") or {}
    targets.validate_keys(tier_map)
    key_to_tier = {str(k): tier for tier, keys in tier_map.items() for k in keys or []}
    return Context(repo, cfg, allowlist.load(repo / ALLOWLIST_FILE),
                   targets.discover(repo, key_to_tier), _load_edges(repo), key_to_tier)
