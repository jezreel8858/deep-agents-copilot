"""
taxonomy — Catalogo de dimensoes de perturbacao e alocacao estratificada (B1-04 / B2-02).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

import yaml

from governance_runner.synth.golden import GoldenSeed
from governance_runner.synth.seeds import SeedLike

__all__ = [
    "DIMENSOES_CANONICAS",
    "DimensaoPerturbacao",
    "Estrato",
    "ItemAlocacao",
    "carregar_taxonomia",
    "alocar_estratos",
]

DIMENSOES_CANONICAS: tuple[str, ...] = (
    "parafrase",
    "ruido_ortografico",
    "code_switching_pt_en",
    "omissao_palavra_chave",
    "distrator_outro_agente",
    "multi_intencao",
    "comprimento_extremo",
    "registro_informal",
)

_TAXONOMY_YAML_PATH = Path(__file__).with_name("taxonomy.yaml")


@dataclass(frozen=True)
class DimensaoPerturbacao:
    """Metadados de uma dimensao de perturbacao da taxonomia."""

    id: str
    descricao: str
    restricoes: Mapping[str, Any]


@dataclass(frozen=True, order=True)
class Estrato:
    """Unidade de amostragem estratificada (agente_alvo, dimensao, seed_source)."""

    agente_alvo: str
    dimensao: str
    seed_source: Literal["manual", "routing_graph"] = "manual"


@dataclass(frozen=True)
class ItemAlocacao:
    """Item individual alocado para geracao sintetica em um estrato."""

    estrato: Estrato
    seed: GoldenSeed | SeedLike
    indice_no_estrato: int
    cobertura_historica: int = 0


def carregar_taxonomia(caminho: str | Path | None = None) -> tuple[DimensaoPerturbacao, ...]:
    """Carrega o catalogo de dimensoes de perturbacao de taxonomy.yaml."""
    alvo = Path(caminho) if caminho is not None else _TAXONOMY_YAML_PATH
    with open(alvo, "r", encoding="utf-8") as fh:
        dados = yaml.safe_load(fh)
    if not isinstance(dados, dict) or not isinstance(dados.get("dimensoes"), list):
        raise ValueError(f"Formato invalido em {alvo}: chave 'dimensoes' ausente.")

    resultado: list[DimensaoPerturbacao] = []
    for item in dados["dimensoes"]:
        if not isinstance(item, dict):
            continue
        dim_id = str(item.get("id", "")).strip()
        if not dim_id:
            continue
        resultado.append(
            DimensaoPerturbacao(
                id=dim_id,
                descricao=str(item.get("descricao", "")).strip(),
                restricoes=dict(item.get("restricoes") or {}),
            )
        )
    return tuple(resultado)


def alocar_estratos(
    seeds: Sequence[GoldenSeed | SeedLike],
    *,
    per_stratum: int = 2,
    targets: Sequence[str] | None = None,
    dimensions: Sequence[str] | None = None,
    cobertura_historica: Mapping[tuple[str, str], int] | None = None,
    rng_seed: int = 42,
) -> tuple[ItemAlocacao, ...]:
    """Aloca sementes por estrato (agente_alvo, dimensao, seed_source) priorizando menor cobertura historica."""
    if per_stratum <= 0 or not seeds:
        return ()

    catalogo = carregar_taxonomia()
    ids_catalogo = tuple(d.id for d in catalogo)
    if dimensions:
        dims_solicitadas = tuple(d.strip() for d in dimensions if d and d.strip())
        for d in dims_solicitadas:
            if d not in ids_catalogo:
                raise ValueError(f"Dimensao de perturbacao desconhecida: '{d}'. Validas: {ids_catalogo}")
        dims_ativas = dims_solicitadas
    else:
        dims_ativas = ids_catalogo

    alvos_filtro: frozenset[str] | None = None
    if targets:
        alvos_filtro = frozenset(t.strip().lstrip("@") for t in targets if t and t.strip())

    seeds_por_chave: dict[tuple[str, Literal["manual", "routing_graph"]], list[GoldenSeed | SeedLike]] = {}
    for s in seeds:
        rota = s.agent_route.lstrip("@")
        if alvos_filtro is not None and rota not in alvos_filtro:
            continue
        src_bruto = getattr(s, "seed_source", "manual")
        src: Literal["manual", "routing_graph"] = (
            "routing_graph" if src_bruto == "routing_graph" else "manual"
        )
        seeds_por_chave.setdefault((rota, src), []).append(s)

    for chave in seeds_por_chave:
        seeds_por_chave[chave].sort(key=lambda item: item.id)

    cobertura = dict(cobertura_historica or {})
    estratos_ordenados: list[tuple[int, Estrato]] = []
    for agente, src in sorted(seeds_por_chave.keys()):
        for dim in dims_ativas:
            est = Estrato(agente_alvo=agente, dimensao=dim, seed_source=src)
            cov = int(cobertura.get((agente, dim), 0))
            estratos_ordenados.append((cov, est))

    estratos_ordenados.sort(key=lambda par: (par[0], par[1].agente_alvo, par[1].dimensao, par[1].seed_source))

    rng = random.Random(rng_seed)
    alocacoes: list[ItemAlocacao] = []

    escolhas_por_estrato: dict[Estrato, list[GoldenSeed | SeedLike]] = {}
    for _, est in estratos_ordenados:
        pool = list(seeds_por_chave[(est.agente_alvo, est.seed_source)])
        rng.shuffle(pool)
        selecionadas: list[GoldenSeed | SeedLike] = []
        for idx in range(per_stratum):
            selecionadas.append(pool[idx % len(pool)])
        escolhas_por_estrato[est] = selecionadas

    for rodada in range(per_stratum):
        for cov, est in estratos_ordenados:
            semente = escolhas_por_estrato[est][rodada]
            alocacoes.append(
                ItemAlocacao(
                    estrato=est,
                    seed=semente,
                    indice_no_estrato=rodada,
                    cobertura_historica=cov,
                )
            )

    return tuple(alocacoes)
