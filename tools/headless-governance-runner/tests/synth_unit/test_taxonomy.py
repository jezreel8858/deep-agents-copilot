from __future__ import annotations

from collections import Counter

import pytest

from governance_runner.synth.golden import carregar_seeds_golden
from governance_runner.synth.taxonomy import DIMENSOES_CANONICAS, alocar_estratos, carregar_taxonomia


def test_catalogo_cobre_dimensoes_canonicas() -> None:
    assert {d.id for d in carregar_taxonomia()} == set(DIMENSOES_CANONICAS)
    assert len(DIMENSOES_CANONICAS) == 8


def test_alocacao_deterministica_por_seed() -> None:
    seeds = carregar_seeds_golden()
    a = alocar_estratos(seeds, per_stratum=2, rng_seed=7)
    b = alocar_estratos(seeds, per_stratum=2, rng_seed=7)
    assert [(i.estrato, i.seed.id) for i in a] == [(i.estrato, i.seed.id) for i in b]


@pytest.mark.parametrize("per_stratum", [1, 2, 3])
def test_alocacao_respeita_per_stratum(per_stratum: int) -> None:
    seeds = carregar_seeds_golden()
    aloc = alocar_estratos(seeds, per_stratum=per_stratum, dimensions=["parafrase"])
    assert aloc
    contagem = Counter(i.estrato for i in aloc)
    assert max(contagem.values()) <= per_stratum
    assert {i.estrato.dimensao for i in aloc} == {"parafrase"}


def test_alocacao_filtra_targets() -> None:
    seeds = carregar_seeds_golden()
    alvo = seeds[0].agent_route.lstrip("@").lower()
    aloc = alocar_estratos(seeds, per_stratum=1, targets=[alvo], dimensions=["parafrase"])
    assert {i.estrato.agente_alvo.lstrip("@").lower() for i in aloc} == {alvo}


def test_alocacao_estratifica_todas_as_dimensoes() -> None:
    aloc = alocar_estratos(carregar_seeds_golden(), per_stratum=1)
    assert {i.estrato.dimensao for i in aloc} == set(DIMENSOES_CANONICAS)


def test_alocacao_sem_seeds_e_vazia() -> None:
    assert len(alocar_estratos([], per_stratum=2)) == 0
