"""
routing_graph — Anti-Corruption Layer read-only sobre routing/graph_loader.py (B1-01).

Invariantes:
- Reutiliza routing/graph_loader.py::carregar_grafo como fonte unica de verdade.
- O caminho do JSON Schema eh SEMPRE o schema empacotado em routing/routing-graph.schema.json
  (nunca fornecido pelo usuario — R-054 Zero Discovery).
- Rejeita caminhos de routing-graph fora do repo_root ou que escapem via symlink/traversal.
- Calcula edge_id deterministico via SHA-256 canonico invariante a reordenacao do YAML,
  falhando explicitamente com ValueError em caso de colisao.
- Matching de keywords estritamente literal sobre texto normalizado (anti-ReDoS).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from governance_runner import routing
from governance_runner.routing.graph_loader import GraphValidationError, carregar_grafo
from governance_runner.routing.model import Grafo
from governance_runner.synth.normalize import normalizar

__all__ = [
    "DEFAULT_ROUTING_GRAPH_REL_PATH",
    "TIPOS_ARESTA_EXCLUIDOS",
    "EXIT_ROUTING_GRAPH_INVALIDO",
    "EXIT_PATH_PROIBIDO",
    "ResolutionKind",
    "RoutingGraphPathError",
    "RotaGrafo",
    "GrafoSnapshot",
    "calcular_edge_id",
    "resolver_caminho_routing_graph",
    "carregar_snapshot_grafo",
    "rotas_validas",
    "resolver_aresta",
]

DEFAULT_ROUTING_GRAPH_REL_PATH = Path(".github") / "agents" / "routing-graph.yaml"
TIPOS_ARESTA_EXCLUIDOS: frozenset[str] = frozenset({"health_check", "mandatory_pre_step"})
EXIT_ROUTING_GRAPH_INVALIDO = 4
EXIT_PATH_PROIBIDO = 5

ResolutionKind = Literal["keyword", "unique_target", "priority", "orphan"]

_SCHEMA_FIXO_PACOTE: Path = Path(routing.__file__).resolve().parent / "routing-graph.schema.json"
_REPO_ROOT_PADRAO: Path = Path(__file__).resolve().parents[5]


class RoutingGraphPathError(ValueError):
    """Caminho de routing-graph fora do repositorio ou traversal/symlink invalido (exit code 5)."""

    exit_code = EXIT_PATH_PROIBIDO


@dataclass(frozen=True)
class RotaGrafo:
    """Representacao imutavel de uma aresta do routing-graph para o dominio synth."""

    edge_id: str
    de: str
    para: str
    tipo: str
    regra: str | None
    prioridade: float
    threshold_score: float
    nivel_routing: str
    keywords: tuple[str, ...] = ()
    sinal_r006: str | None = None
    gatilho: str | None = None
    sinal: str | None = None
    descricao_no: str = ""
    valida: bool = True

    @property
    def keywords_norm(self) -> tuple[str, ...]:
        """Keywords normalizadas e deduplicadas preservando ordem."""
        vistas: list[str] = []
        for kw in self.keywords:
            n = normalizar(kw)
            if n and n not in vistas:
                vistas.append(n)
        return tuple(vistas)


@dataclass(frozen=True)
class GrafoSnapshot:
    """Snapshot imutavel e validado do routing-graph.yaml."""

    sha256: str
    rotas: tuple[RotaGrafo, ...]
    nos: frozenset[str]
    nos_descricoes: dict[str, str] = field(default_factory=dict)
    todas_rotas: tuple[RotaGrafo, ...] = ()


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def calcular_edge_id(
    *,
    de: str,
    para: str,
    prioridade: float,
    tipo: str | None,
    regra: str | None = None,
    keywords: tuple[str, ...] | list[str] = (),
) -> str:
    """Calcula o edge_id deterministico e independente da ordem do YAML.

    Formula: "e-" + sha256(canonical_json([de, para, prioridade, tipo, discriminador]))[:12]
    onde discriminador = regra se presente, senao sha256("\n".join(sorted(keywords_norm))).
    """
    tipo_norm = (tipo or "keyword_based").strip() or "keyword_based"
    prio_norm = float(prioridade)
    if regra is not None and str(regra).strip():
        discriminador = str(regra).strip()
    else:
        kws_norm = sorted({normalizar(str(k)) for k in keywords if normalizar(str(k))})
        discriminador = hashlib.sha256("\n".join(kws_norm).encode("utf-8")).hexdigest()

    raw = _canonical_json([str(de).strip(), str(para).strip(), prio_norm, tipo_norm, discriminador])
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"e-{digest}"


def resolver_caminho_routing_graph(
    path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> Path:
    """Resolve e valida o caminho do routing-graph.yaml garantindo permanencia sob repo_root."""
    raiz = (repo_root if repo_root is not None else _REPO_ROOT_PADRAO).resolve(strict=False)
    if path is None:
        candidato = raiz / DEFAULT_ROUTING_GRAPH_REL_PATH
    else:
        bruto = Path(path)
        if ".." in bruto.parts:
            raise RoutingGraphPathError("Caminho invalido para --routing-graph: path traversal rejeitado.")
        candidato = bruto if bruto.is_absolute() else (raiz / bruto)

    resolvido = candidato.resolve(strict=False)
    if not resolvido.is_relative_to(raiz):
        raise RoutingGraphPathError("Caminho invalido para --routing-graph: fora da raiz do repositorio.")
    if candidato.exists() and candidato.is_symlink():
        alvo_real = candidato.resolve(strict=True)
        if not alvo_real.is_relative_to(raiz):
            raise RoutingGraphPathError("Caminho invalido para --routing-graph: symlink escapa do repositorio.")
    return resolvido


def _eh_rota_valida(
    de: str,
    para: str,
    tipo: str,
    nos: frozenset[str],
    *,
    incluir_tipos: frozenset[str] | None = None,
    excluir_tipos: frozenset[str] = TIPOS_ARESTA_EXCLUIDOS,
) -> bool:
    if de != "agent-router":
        return False
    if para not in nos or para == "agent-router":
        return False
    if incluir_tipos is not None:
        return tipo in incluir_tipos
    return tipo not in excluir_tipos


def _converter_grafo_para_snapshot(grafo: Grafo, sha256: str) -> GrafoSnapshot:
    nos_desc: dict[str, str] = {n.id: n.descricao for n in grafo.nos_por_id}
    todas: list[RotaGrafo] = []
    vistas_por_id: dict[str, RotaGrafo] = {}

    for aresta in grafo.arestas:
        cond = aresta.condicoes
        tipo = (cond.tipo or "keyword_based").strip() or "keyword_based"
        regra = cond.regra.strip() if cond.regra and str(cond.regra).strip() else None
        keywords = tuple(str(k).strip() for k in (cond.keywords or ()) if str(k).strip())
        eid = calcular_edge_id(
            de=aresta.de,
            para=aresta.para,
            prioridade=aresta.prioridade,
            tipo=tipo,
            regra=regra,
            keywords=keywords,
        )
        valida = _eh_rota_valida(aresta.de, aresta.para, tipo, grafo.nos)
        rota = RotaGrafo(
            edge_id=eid,
            de=aresta.de,
            para=aresta.para,
            tipo=tipo,
            regra=regra,
            prioridade=float(aresta.prioridade),
            threshold_score=float(aresta.threshold_score),
            nivel_routing=str(aresta.nivel_routing),
            keywords=keywords,
            sinal_r006=cond.sinal_r006,
            gatilho=cond.gatilho,
            sinal=cond.sinal,
            descricao_no=nos_desc.get(aresta.para, ""),
            valida=valida,
        )
        if eid in vistas_por_id:
            anterior = vistas_por_id[eid]
            raise ValueError(
                f"Colisao de edge_id '{eid}' entre arestas "
                f"({anterior.de}->{anterior.para}, prio={anterior.prioridade}, tipo={anterior.tipo}) e "
                f"({rota.de}->{rota.para}, prio={rota.prioridade}, tipo={rota.tipo})."
            )
        vistas_por_id[eid] = rota
        todas.append(rota)

    todas_ordenadas = tuple(sorted(todas, key=lambda r: r.edge_id))
    validas_ordenadas = tuple(r for r in todas_ordenadas if r.valida)
    return GrafoSnapshot(
        sha256=sha256,
        rotas=validas_ordenadas,
        nos=grafo.nos,
        nos_descricoes=nos_desc,
        todas_rotas=todas_ordenadas,
    )


def carregar_snapshot_grafo(
    path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> GrafoSnapshot:
    """Carrega e valida routing-graph.yaml via graph_loader.carregar_grafo com schema fixo."""
    caminho_yaml = resolver_caminho_routing_graph(path, repo_root=repo_root)
    if not caminho_yaml.exists() or not caminho_yaml.is_file():
        raise GraphValidationError(f"Arquivo de grafo inexistente: {caminho_yaml.name}")
    conteudo_bytes = caminho_yaml.read_bytes()
    sha256 = hashlib.sha256(conteudo_bytes).hexdigest()
    grafo = carregar_grafo(caminho_yaml, _SCHEMA_FIXO_PACOTE)
    return _converter_grafo_para_snapshot(grafo, sha256)


def rotas_validas(
    snapshot: GrafoSnapshot,
    *,
    incluir_tipos: frozenset[str] | set[str] | tuple[str, ...] | None = None,
) -> tuple[RotaGrafo, ...]:
    """Filtra as rotas validas do snapshot (excluindo health_check e mandatory_pre_step)."""
    inc = frozenset(incluir_tipos) if incluir_tipos is not None else None
    origem = snapshot.todas_rotas if snapshot.todas_rotas else snapshot.rotas
    filtradas = [
        r
        for r in origem
        if _eh_rota_valida(r.de, r.para, r.tipo, snapshot.nos, incluir_tipos=inc)
    ]
    return tuple(sorted(filtradas, key=lambda r: r.edge_id))


def resolver_aresta(
    expected_route: str,
    prompt_norm: str,
    snapshot: GrafoSnapshot,
) -> tuple[str | None, ResolutionKind]:
    """Resolve uma rota esperada + prompt normalizado para (edge_id, resolution_kind)."""
    alvo = expected_route.strip().lstrip("@").lower()
    texto_norm = normalizar(prompt_norm)
    candidatas = [r for r in rotas_validas(snapshot) if r.para.lower() == alvo]
    if not candidatas:
        return None, "orphan"

    def _contar_hits(rota: RotaGrafo) -> int:
        if not texto_norm:
            return 0
        hits = 0
        for kw_n in rota.keywords_norm:
            if kw_n and kw_n in texto_norm:
                hits += 1
        return hits

    if len(candidatas) == 1:
        unica = candidatas[0]
        if _contar_hits(unica) > 0:
            return unica.edge_id, "keyword"
        return unica.edge_id, "unique_target"

    pontuadas = [(_contar_hits(r), r) for r in candidatas]
    max_hits = max(h for h, _ in pontuadas)
    if max_hits > 0:
        melhores = [r for h, r in pontuadas if h == max_hits]
        melhores.sort(key=lambda r: (r.prioridade, r.edge_id))
        return melhores[0].edge_id, "keyword"

    candidatas_ordenadas = sorted(candidatas, key=lambda r: (r.prioridade, r.edge_id))
    return candidatas_ordenadas[0].edge_id, "priority"
