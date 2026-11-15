"""
seeds — Coverage-Guided Seeding sobre o routing-graph.yaml e Golden Set (B2-01 / CA-01 / CA-02).

Invariantes:
- Em modo 'off' (default), gera zero sementes do grafo.
- Em modo 'gaps', gera sementes apenas para arestas validas com cobertura < min_cobertura.
- Em modo 'all', gera sementes para todas as arestas validas do grafo.
- Keywords e regras do YAML sao tratadas como dados inertes (strip de controles, limite
  de tamanho, sem vazamento de nomes de agentes/diretivas de roteamento) e validadas
  com normalize.sanitizar_prompt.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, replace
from typing import Literal, Protocol, Sequence, runtime_checkable

from governance_runner.synth.golden import GoldenSeed
from governance_runner.synth.normalize import normalizar, sanitizar_prompt
from governance_runner.synth.routing_graph import (
    GrafoSnapshot,
    RotaGrafo,
    resolver_aresta,
    rotas_validas,
)

__all__ = [
    "MODOS_GRAPH_SEEDING",
    "ModoGraphSeeding",
    "SeedLike",
    "SeedRef",
    "calcular_cobertura_golden",
    "enriquecer_seeds_golden",
    "identificar_arestas_uncoverable",
    "gerar_seeds_grafo",
]

ModoGraphSeeding = Literal["off", "gaps", "all"]
MODOS_GRAPH_SEEDING: tuple[ModoGraphSeeding, ...] = ("off", "gaps", "all")

_MAX_LEN_TOKEN = 120
_MAX_LEN_PROMPT = 360
_REGEX_CONTROLES = re.compile(r"[\x00-\x1f\x7f]+")
_REGEX_MENCAO_AGENTE = re.compile(r"@[A-Za-z0-9_\-]+")


@runtime_checkable
class SeedLike(Protocol):
    """Protocolo unificado para GoldenSeed e SeedRef."""

    @property
    def id(self) -> str: ...

    @property
    def prompt(self) -> str: ...

    @property
    def expected_route(self) -> str: ...

    @property
    def agent_route(self) -> str: ...

    @property
    def seed_case_id(self) -> str: ...

    @property
    def seed_source(self) -> Literal["manual", "routing_graph"]: ...

    @property
    def graph_edge_id(self) -> str | None: ...

    @property
    def graph_edge_resolution(self) -> str | None: ...

    @property
    def keywords(self) -> tuple[str, ...]: ...


@dataclass(frozen=True)
class SeedRef:
    """Semente de roteamento (manual ou derivada do routing-graph)."""

    prompt: str
    expected_route: str
    seed_case_id: str
    seed_source: Literal["manual", "routing_graph"] = "routing_graph"
    graph_edge_id: str | None = None
    keywords: tuple[str, ...] = ()
    graph_edge_resolution: str | None = "keyword"

    @property
    def id(self) -> str:
        return self.seed_case_id

    @property
    def solicitacao(self) -> str:
        return self.prompt

    @property
    def agent_route(self) -> str:
        return self.expected_route


def _limpar_fragmento_inerte(texto: str, *, ids_nos: frozenset[str] = frozenset()) -> str:
    """Sanitiza um fragmento do YAML para uso como dado inerte em template neutro."""
    if not texto:
        return ""
    limpo = _REGEX_CONTROLES.sub(" ", str(texto))
    limpo = _REGEX_MENCAO_AGENTE.sub("", limpo)
    # Remove referencias explicitas a ids de agentes para evitar contaminacao no blind-eval
    for no_id in ids_nos:
        if no_id and len(no_id) >= 4:
            limpo = re.sub(re.escape(no_id), "sistema", limpo, flags=re.IGNORECASE)
    for proibido in ("Rota:", "Delegado:", "Agente Ativo:", "expected_agent_route", "run_subagent"):
        limpo = re.sub(re.escape(proibido), "", limpo, flags=re.IGNORECASE)
    limpo = " ".join(limpo.split()).strip(" -:;,.?!")
    return limpo[:_MAX_LEN_TOKEN].strip()


def calcular_cobertura_golden(
    golden_seeds: Sequence[GoldenSeed | SeedLike],
    snapshot: GrafoSnapshot,
) -> dict[str, int]:
    """Calcula a contagem de casos Golden mapeados para cada edge_id valido do snapshot."""
    cobertura: dict[str, int] = {r.edge_id: 0 for r in rotas_validas(snapshot)}
    for seed in golden_seeds:
        edge_id, _ = resolver_aresta(seed.expected_route, normalizar(seed.prompt), snapshot)
        if edge_id is not None and edge_id in cobertura:
            cobertura[edge_id] += 1
    return cobertura


def enriquecer_seeds_golden(
    golden_seeds: Sequence[GoldenSeed],
    snapshot: GrafoSnapshot,
) -> tuple[GoldenSeed, ...]:
    """Atribui graph_edge_id e graph_edge_resolution as sementes Golden para rastreabilidade."""
    enriquecidas: list[GoldenSeed] = []
    for seed in golden_seeds:
        edge_id, res_kind = resolver_aresta(seed.expected_route, normalizar(seed.prompt), snapshot)
        enriquecidas.append(
            replace(
                seed,
                seed_source="manual",
                graph_edge_id=edge_id,
                graph_edge_resolution=res_kind,
            )
        )
    return tuple(enriquecidas)


def _extrair_termos_rota(rota: RotaGrafo, ids_nos: frozenset[str]) -> tuple[list[str], str]:
    """Retorna (lista de keywords limpas, contexto auxiliar limpo) para uma rota."""
    kws_limpas = [
        _limpar_fragmento_inerte(k, ids_nos=ids_nos)
        for k in rota.keywords
        if _limpar_fragmento_inerte(k, ids_nos=ids_nos)
    ]
    contexto_bruto = rota.sinal_r006 or rota.sinal or rota.gatilho or rota.descricao_no or ""
    contexto_limpo = _limpar_fragmento_inerte(contexto_bruto, ids_nos=ids_nos)
    return kws_limpas, contexto_limpo


def identificar_arestas_uncoverable(snapshot: GrafoSnapshot) -> tuple[str, ...]:
    """Retorna os edge_ids validos que nao possuem keywords nem gatilho/sinal/descricao aproveitavel."""
    uncoverable: list[str] = []
    for rota in rotas_validas(snapshot):
        kws, ctx = _extrair_termos_rota(rota, snapshot.nos)
        if not kws and not ctx:
            uncoverable.append(rota.edge_id)
    return tuple(sorted(uncoverable))


_TEMPLATES_NEUTROS: tuple[str, ...] = (
    "Preciso de apoio tecnico na aplicacao sobre {termo_principal}{complemento}.",
    "Como devemos tratar {termo_principal} no projeto{complemento}?",
    "Solicito analise detalhada envolvendo {termo_principal}{complemento}.",
    "Gostaria de revisar o cenario de {termo_principal}{complemento} no repositorio.",
)


def _construir_prompt_neutro(
    rota: RotaGrafo,
    indice: int,
    rng: random.Random,
    ids_nos: frozenset[str],
) -> tuple[str, tuple[str, ...], str] | None:
    kws_limpas, ctx_limpo = _extrair_termos_rota(rota, ids_nos)
    if not kws_limpas and not ctx_limpo:
        return None

    keywords_escolhidas: list[str] = []
    if kws_limpas:
        pool = list(kws_limpas)
        rng.shuffle(pool)
        primaria = pool[indice % len(pool)]
        keywords_escolhidas.append(primaria)
        if len(pool) >= 2:
            secundaria = pool[(indice + 1) % len(pool)]
            if secundaria != primaria:
                keywords_escolhidas.append(secundaria)
        termo_principal = " e ".join(keywords_escolhidas)
        res_kind = "keyword"
    else:
        termo_principal = ctx_limpo
        res_kind = "priority"

    complemento = ""
    if ctx_limpo and ctx_limpo != termo_principal:
        curto = ctx_limpo[:80].strip()
        if curto:
            complemento = f" considerando {curto.lower()}"

    molde = _TEMPLATES_NEUTROS[(indice + rng.randint(0, len(_TEMPLATES_NEUTROS) - 1)) % len(_TEMPLATES_NEUTROS)]
    prompt_bruto = molde.format(termo_principal=termo_principal, complemento=complemento)
    prompt_final = " ".join(prompt_bruto.split())[:_MAX_LEN_PROMPT].strip()

    ok, _ = sanitizar_prompt(prompt_final)
    if not ok:
        prompt_final = f"Preciso de auxilio tecnico com a demanda {indice + 1} do sistema."
        ok2, _ = sanitizar_prompt(prompt_final)
        if not ok2:
            return None

    return prompt_final, tuple(keywords_escolhidas), res_kind


def gerar_seeds_grafo(
    snapshot: GrafoSnapshot,
    cobertura: dict[str, int] | None = None,
    *,
    min_cobertura: int = 3,
    modo: ModoGraphSeeding = "off",
    rng_seed: int = 42,
    targets: Sequence[str] | None = None,
) -> tuple[SeedRef, ...]:
    """Gera sementes guiadas pelo grafo conforme o modo ('off' | 'gaps' | 'all')."""
    if modo not in MODOS_GRAPH_SEEDING:
        raise ValueError(f"Modo --graph-seeding invalido: {modo!r}. Esperado um de {MODOS_GRAPH_SEEDING}.")
    if modo == "off" or min_cobertura <= 0:
        return ()

    alvos_filtro: frozenset[str] | None = None
    if targets:
        alvos_filtro = frozenset(t.strip().lstrip("@").lower() for t in targets if t and t.strip())

    cov_map = dict(cobertura or {})
    rng = random.Random(rng_seed)
    geradas: list[SeedRef] = []

    for rota in rotas_validas(snapshot):
        if alvos_filtro is not None and rota.para.lower() not in alvos_filtro:
            continue
        cov_atual = int(cov_map.get(rota.edge_id, 0))
        if modo == "gaps":
            if cov_atual >= min_cobertura:
                continue
            faltam = min_cobertura - cov_atual
        else:  # modo == "all"
            faltam = max(min_cobertura, min_cobertura - cov_atual)

        for i in range(faltam):
            construido = _construir_prompt_neutro(rota, i, rng, snapshot.nos)
            if construido is None:
                break
            prompt_txt, kws_usadas, res_kind = construido
            geradas.append(
                SeedRef(
                    prompt=prompt_txt,
                    expected_route=rota.para,
                    seed_case_id=f"graph:{rota.edge_id}:{i}",
                    seed_source="routing_graph",
                    graph_edge_id=rota.edge_id,
                    keywords=kws_usadas,
                    graph_edge_resolution=res_kind,
                )
            )

    return tuple(geradas)
