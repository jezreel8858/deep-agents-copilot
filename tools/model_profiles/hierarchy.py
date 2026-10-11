"""Regra D6: custo do pai >= custo do filho (cost_rank), com excecao por model_exception_reason."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Collection, Mapping
from tools.model_profiles import config
COST_HIERARCHY = "cost_hierarchy"
UNVERIFIABLE = "cost_rank_unverifiable"
@dataclass(frozen=True)
class Violation:
    parent: str
    child: str
    kind: str
def load_edges(routing_graph: Path) -> list[tuple[str, str]]:
    data = config.load_yaml(routing_graph)
    return [(e["de"], e["para"]) for e in data.get("arestas") or []]
def _kind(parent_rank: int | None, child_rank: int | None) -> str | None:
    if parent_rank is None or child_rank is None:
        return UNVERIFIABLE
    return COST_HIERARCHY if child_rank > parent_rank else None
def find_violations(
    edges: list[tuple[str, str]],
    model_by_key: Mapping[str, str],
    cost_rank_by_model: Mapping[str, int | None],
    exceptions: Collection[str] = (),
) -> list[Violation]:
    out: list[Violation] = []
    for parent, child in edges:
        if parent not in model_by_key or child not in model_by_key or child in exceptions:
            continue
        kind = _kind(cost_rank_by_model.get(model_by_key[parent]),
                     cost_rank_by_model.get(model_by_key[child]))
        if kind:
            out.append(Violation(parent, child, kind))
    return out
