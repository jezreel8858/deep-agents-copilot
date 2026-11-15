"""
diagnostics — Oraculo offline deterministico de assertividade de roteamento (B3-01 / CA-05).

Invariantes:
- Puramente deterministico e 100% offline (zero chamadas LLM / SDK).
- Timestamp unico derivado de synth_runs.finished_at (ou started_at se nulo) — nunca datetime.now().
- Ordenacao lexicografica estavel em todas as colecoes; floats arredondados com round(x, 6).
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Literal, Sequence

from governance_runner.synth.golden import GoldenSeed
from governance_runner.synth.normalize import normalizar
from governance_runner.synth.routing_graph import (
    GrafoSnapshot,
    RotaGrafo,
    resolver_aresta,
    rotas_validas,
)
from governance_runner.synth.seeds import (
    calcular_cobertura_golden,
    identificar_arestas_uncoverable,
)

__all__ = [
    "EXIT_EVAL_RUN_INEXISTENTE",
    "DIAGNOSTIC_VERSION",
    "AVISO_HITL",
    "CODIGOS_SUGESTAO",
    "CATEGORIAS_DIVERGENCIA",
    "SynthEvalRunInvalidoError",
    "HashesDiagnostico",
    "ResumoDiagnostico",
    "SuportePorFonte",
    "MetricaAresta",
    "RotasOrfas",
    "ColisaoKws",
    "DivergenciaRouterMd",
    "SugestaoAcionavel",
    "DiagnosticoAssertividade",
    "diagnosticar_avaliacao",
]

EXIT_EVAL_RUN_INEXISTENTE = 3
DIAGNOSTIC_VERSION = 1
AVISO_HITL = "Artefato consultivo (HITL). Nenhum arquivo-alvo é modificado automaticamente."

CODIGOS_SUGESTAO: tuple[str, ...] = (
    "SUG-KW-ADD",
    "SUG-KW-COLLISION",
    "SUG-DISAMBIG",
    "SUG-GOLDEN-GAP",
    "SUG-ROUTER-DOC",
    "SUG-GRAPH-PHANTOM",
)

CATEGORIAS_DIVERGENCIA: tuple[str, ...] = (
    "KEYWORD_COLLISION",
    "PROMPT_DRIFT",
    "COVERAGE_GAP",
    "CONFIDENCE_CALIBRATION",
)

_STOPWORDS_PT: frozenset[str] = frozenset(
    {
        "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
        "um", "uma", "uns", "umas", "para", "por", "com", "sem", "que",
        "se", "ao", "aos", "as", "os", "ou", "e", "o", "a", "como",
        "sobre", "mais", "menos", "muito", "isso", "isto", "esse", "essa",
        "este", "esta", "preciso", "quero", "gostaria", "ajuda", "ajudar",
        "apoio", "tecnico", "aplicacao", "projeto", "sistema", "pedido",
        "seguinte", "variacao", "fazer", "analise", "detalhada", "envolvendo",
        "cenario", "revisar", "repositorio", "considerando",
    }
)

_REGEX_CITACAO_AGENTE = re.compile(r"@([a-z0-9]+(?:-[a-z0-9]+)+)")


class SynthEvalRunInvalidoError(LookupError):
    """eval_run_id inexistente ou run nao eh do tipo 'eval' (exit code 3)."""

    exit_code = EXIT_EVAL_RUN_INEXISTENTE


@dataclass(frozen=True)
class HashesDiagnostico:
    routing_graph_sha256: str
    router_agent_sha256: str
    golden_set_sha256: str


@dataclass(frozen=True)
class ResumoDiagnostico:
    total_avaliacoes: int
    acuracia_global: float
    cobertura_arestas_golden: float
    cobertura_arestas_total: float


@dataclass(frozen=True)
class SuportePorFonte:
    manual: int
    routing_graph: int


@dataclass(frozen=True)
class MetricaAresta:
    edge_id: str
    para: str
    tipo: str
    suporte: SuportePorFonte
    tp: int
    fp: int
    fn: int
    precision: float | None
    recall: float | None
    f1: float | None
    unparseable: int


@dataclass(frozen=True)
class RotasOrfas:
    sem_golden: tuple[str, ...]
    sem_avaliacao: tuple[str, ...]
    uncoverable: tuple[str, ...]


@dataclass(frozen=True)
class ColisaoKws:
    keyword_norm: str
    edges: tuple[str, ...]
    tipo: Literal["exata", "substring"]


@dataclass(frozen=True)
class DivergenciaRouterMd:
    nos_nao_citados: tuple[str, ...]
    citados_fora_do_grafo: tuple[str, ...]
    rotas_fantasma: tuple[str, ...]


@dataclass(frozen=True)
class SugestaoAcionavel:
    id: str
    codigo: str
    severidade: Literal["alta", "media", "baixa"]
    alvo_arquivo: str
    alvo_ancora: str
    evidencias: tuple[str, ...]
    proposta_texto: str
    categoria_divergencia: str = "COVERAGE_GAP"


@dataclass(frozen=True)
class DiagnosticoAssertividade:
    diagnostic_version: int
    diagnostic_id: str
    eval_run_id: str
    finished_at: str
    hashes: HashesDiagnostico
    resumo: ResumoDiagnostico
    por_aresta: tuple[MetricaAresta, ...]
    matriz_confusao: dict[str, dict[str, int]]
    orfas: RotasOrfas
    colisoes: tuple[ColisaoKws, ...]
    divergencias_router_md: DivergenciaRouterMd
    sugestoes: tuple[SugestaoAcionavel, ...]
    aviso: str = AVISO_HITL


def _r6(valor: float) -> float:
    return round(float(valor), 6)


def _div_segura(num: int | float, den: int | float) -> float | None:
    if den <= 0:
        return None
    return _r6(float(num) / float(den))


def _detectar_colisoes_estaticas(rotas: Sequence[RotaGrafo]) -> tuple[ColisaoKws, ...]:
    """Detecta colisoes exatas e por substring entre keywords de arestas com para distintos."""
    mapa_exato: dict[str, dict[str, set[str]]] = {}
    todas_kws: list[tuple[str, str, str]] = []

    for r in rotas:
        for kw_n in r.keywords_norm:
            if not kw_n:
                continue
            mapa_exato.setdefault(kw_n, {}).setdefault(r.para, set()).add(r.edge_id)
            todas_kws.append((kw_n, r.para, r.edge_id))

    colisoes: list[ColisaoKws] = []
    vistas: set[tuple[str, tuple[str, ...], str]] = set()

    for kw_n in sorted(mapa_exato.keys()):
        por_para = mapa_exato[kw_n]
        if len(por_para) >= 2:
            edges_envolvidas = tuple(sorted({eid for s in por_para.values() for eid in s}))
            chave = (kw_n, edges_envolvidas, "exata")
            if chave not in vistas:
                vistas.add(chave)
                colisoes.append(ColisaoKws(keyword_norm=kw_n, edges=edges_envolvidas, tipo="exata"))

    kws_unicas = sorted({k for k, _, _ in todas_kws if len(k) >= 4})
    for kw_curta in kws_unicas:
        edges_sub: set[str] = set()
        paras_sub: set[str] = set()
        tem_superstring = False
        for kw_longa, para_l, eid_l in todas_kws:
            if kw_longa == kw_curta:
                edges_sub.add(eid_l)
                paras_sub.add(para_l)
            elif len(kw_longa) > len(kw_curta) and (
                f" {kw_curta} " in f" {kw_longa} " or kw_curta in kw_longa
            ):
                tem_superstring = True
                edges_sub.add(eid_l)
                paras_sub.add(para_l)
        if tem_superstring and len(paras_sub) >= 2 and len(edges_sub) >= 2:
            edges_tup = tuple(sorted(edges_sub))
            if (kw_curta, edges_tup, "exata") not in vistas and (kw_curta, edges_tup, "substring") not in vistas:
                vistas.add((kw_curta, edges_tup, "substring"))
                colisoes.append(ColisaoKws(keyword_norm=kw_curta, edges=edges_tup, tipo="substring"))

    colisoes.sort(key=lambda c: (c.keyword_norm, c.tipo, c.edges))
    return tuple(colisoes)


def _analisar_divergencia_router_md(
    snapshot: GrafoSnapshot,
    router_md_texto: str,
    rotas_observadas: set[str],
) -> DivergenciaRouterMd:
    texto_lower = (router_md_texto or "").lower()
    paras_validos = sorted({r.para for r in rotas_validas(snapshot)})

    nos_nao_citados: list[str] = []
    for no_para in paras_validos:
        no_l = no_para.lower()
        if f"@{no_l}" not in texto_lower and no_l not in texto_lower:
            nos_nao_citados.append(no_para)

    citados_no_md = {m.group(1).lower() for m in _REGEX_CITACAO_AGENTE.finditer(texto_lower)}
    nos_grafo_lower = {n.lower() for n in snapshot.nos}
    ignorados = {"agent-router", "param", "return", "example", "override"}
    citados_fora = sorted(c for c in citados_no_md if c not in nos_grafo_lower and c not in ignorados)

    fantasmas = sorted(
        obs
        for obs in rotas_observadas
        if obs and obs != "<unparseable>" and obs.lower() not in nos_grafo_lower
    )

    return DivergenciaRouterMd(
        nos_nao_citados=tuple(sorted(nos_nao_citados)),
        citados_fora_do_grafo=tuple(citados_fora),
        rotas_fantasma=tuple(fantasmas),
    )


def _extrair_ngrams_candidatos(textos: Sequence[str], kws_existentes: set[str]) -> list[str]:
    contagem: Counter[str] = Counter()
    for t in textos:
        tokens = [
            tok
            for tok in normalizar(t).split()
            if len(tok) >= 4 and tok not in _STOPWORDS_PT and not tok.isdigit()
        ]
        vistos_no_doc: set[str] = set()
        for tok in tokens:
            if tok not in kws_existentes:
                vistos_no_doc.add(tok)
        for i in range(len(tokens) - 1):
            bg = f"{tokens[i]} {tokens[i + 1]}"
            if bg not in kws_existentes:
                vistos_no_doc.add(bg)
        for item in vistos_no_doc:
            contagem[item] += 1

    ordenados = sorted(contagem.items(), key=lambda par: (-par[1], par[0]))
    return [termo for termo, freq in ordenados if freq >= 1][:3]


def diagnosticar_avaliacao(
    *,
    eval_run_id: str,
    run_info: dict[str, Any] | None,
    avaliacoes: Sequence[dict[str, Any]],
    snapshot: GrafoSnapshot,
    router_md_texto: str,
    router_agent_sha256: str,
    golden_seeds: Sequence[GoldenSeed] = (),
    golden_set_sha256: str = "",
    min_support: int = 2,
) -> DiagnosticoAssertividade:
    """Executa o oraculo deterministico offline cruzando avaliacoes, grafo e agent-router.agent.md."""
    if run_info is None or str(run_info.get("kind", "")) != "eval":
        raise SynthEvalRunInvalidoError(
            f"Run '{eval_run_id}' inexistente ou nao eh do tipo 'eval'."
        )

    finished_at = str(run_info.get("finished_at") or run_info.get("started_at") or "1970-01-01T00:00:00+00:00")
    validas = rotas_validas(snapshot)
    mapa_rotas: dict[str, RotaGrafo] = {r.edge_id: r for r in validas}

    cov_golden = calcular_cobertura_golden(golden_seeds, snapshot)
    uncoverable = identificar_arestas_uncoverable(snapshot)

    avs_ordenadas = sorted(
        avaliacoes,
        key=lambda a: (str(a.get("prompt_id", "")), str(a.get("eval_id", ""))),
    )

    suporte_manual: Counter[str] = Counter()
    suporte_graph: Counter[str] = Counter()
    tp_por_edge: Counter[str] = Counter()
    fn_por_edge: Counter[str] = Counter()
    unp_por_edge: Counter[str] = Counter()
    fp_por_para: Counter[str] = Counter()

    fn_textos_por_edge: dict[str, list[str]] = {}
    fn_pids_por_edge: dict[str, list[str]] = {}
    confusao_pares: dict[tuple[str, str], list[str]] = {}
    matriz: dict[str, Counter[str]] = {}
    rotas_observadas_set: set[str] = set()
    fantasma_pids: dict[str, list[str]] = {}

    total_avaliacoes = len(avs_ordenadas)
    total_passed = 0

    for ev in avs_ordenadas:
        pid = str(ev.get("prompt_id", ""))
        exp = str(ev.get("expected_route", "")).strip().lstrip("@").lower()
        obs_raw = ev.get("observed_route")
        obs = str(obs_raw).strip().lstrip("@").lower() if obs_raw else "<unparseable>"
        verdict = str(ev.get("verdict", ""))
        passed = int(ev.get("passed", 0)) == 1
        seed_src = str(ev.get("seed_source") or "manual")
        prompt_txt = str(ev.get("prompt_text") or ev.get("text") or "")

        if passed:
            total_passed += 1

        rotas_observadas_set.add(obs)
        matriz.setdefault(exp, Counter())[obs] += 1

        if obs != "<unparseable>" and obs not in {n.lower() for n in snapshot.nos}:
            fantasma_pids.setdefault(obs, []).append(pid)

        edge_id = ev.get("graph_edge_id")
        if not edge_id or str(edge_id) not in mapa_rotas:
            edge_id, _ = resolver_aresta(exp, normalizar(prompt_txt), snapshot)

        if edge_id and str(edge_id) in mapa_rotas:
            eid_str = str(edge_id)
            if seed_src == "routing_graph":
                suporte_graph[eid_str] += 1
            else:
                suporte_manual[eid_str] += 1

            if verdict == "unparseable" or obs == "<unparseable>":
                unp_por_edge[eid_str] += 1
                fn_por_edge[eid_str] += 1
                fn_textos_por_edge.setdefault(eid_str, []).append(prompt_txt)
                fn_pids_por_edge.setdefault(eid_str, []).append(pid)
            elif passed and obs == exp:
                tp_por_edge[eid_str] += 1
            else:
                fn_por_edge[eid_str] += 1
                fn_textos_por_edge.setdefault(eid_str, []).append(prompt_txt)
                fn_pids_por_edge.setdefault(eid_str, []).append(pid)

        if obs != "<unparseable>" and obs != exp:
            fp_por_para[obs] += 1
            confusao_pares.setdefault((exp, obs), []).append(pid)

    metricas_aresta: list[MetricaAresta] = []
    sem_avaliacao: list[str] = []
    sem_golden: list[str] = []

    for r in validas:
        eid = r.edge_id
        sup_m = int(suporte_manual.get(eid, 0))
        sup_g = int(suporte_graph.get(eid, 0))
        if cov_golden.get(eid, 0) == 0:
            sem_golden.append(eid)
        if (sup_m + sup_g) == 0:
            sem_avaliacao.append(eid)

        tp = int(tp_por_edge.get(eid, 0))
        fn = int(fn_por_edge.get(eid, 0))
        fp = int(fp_por_para.get(r.para.lower(), 0))
        unp = int(unp_por_edge.get(eid, 0))

        prec = _div_segura(tp, tp + fp)
        rec = _div_segura(tp, tp + fn)
        if prec is not None and rec is not None and (prec + rec) > 0:
            f1: float | None = _r6(2.0 * prec * rec / (prec + rec))
        else:
            f1 = None

        metricas_aresta.append(
            MetricaAresta(
                edge_id=eid,
                para=r.para,
                tipo=r.tipo,
                suporte=SuportePorFonte(manual=sup_m, routing_graph=sup_g),
                tp=tp,
                fp=fp,
                fn=fn,
                precision=prec,
                recall=rec,
                f1=f1,
                unparseable=unp,
            )
        )

    total_arestas_validas = len(validas)
    arestas_com_golden = sum(1 for r in validas if cov_golden.get(r.edge_id, 0) > 0)
    arestas_com_aval = sum(
        1 for m in metricas_aresta if (m.suporte.manual + m.suporte.routing_graph) > 0
    )

    resumo = ResumoDiagnostico(
        total_avaliacoes=total_avaliacoes,
        acuracia_global=_div_segura(total_passed, total_avaliacoes) or 0.0,
        cobertura_arestas_golden=_div_segura(arestas_com_golden, total_arestas_validas) or 0.0,
        cobertura_arestas_total=_div_segura(arestas_com_aval, total_arestas_validas) or 0.0,
    )

    matriz_ordenada: dict[str, dict[str, int]] = {
        exp_k: {obs_k: int(matriz[exp_k][obs_k]) for obs_k in sorted(matriz[exp_k].keys())}
        for exp_k in sorted(matriz.keys())
    }

    orfas = RotasOrfas(
        sem_golden=tuple(sorted(sem_golden)),
        sem_avaliacao=tuple(sorted(sem_avaliacao)),
        uncoverable=uncoverable,
    )

    colisoes = _detectar_colisoes_estaticas(validas)
    divergencias = _analisar_divergencia_router_md(snapshot, router_md_texto, rotas_observadas_set)

    sugestoes_brutas: list[tuple[str, Literal["alta", "media", "baixa"], str, str, tuple[str, ...], str, str]] = []

    for r in validas:
        eid = r.edge_id
        if fn_por_edge.get(eid, 0) > 0:
            kws_exist = set(r.keywords_norm)
            candidatos_kw = _extrair_ngrams_candidatos(fn_textos_por_edge.get(eid, []), kws_exist)
            pids_ev = tuple(sorted(set(fn_pids_por_edge.get(eid, [])))[:5])
            if candidatos_kw:
                sugestoes_brutas.append(
                    (
                        "SUG-KW-ADD",
                        "media",
                        ".github/agents/routing-graph.yaml",
                        f"arestas[{eid}:{r.para}]",
                        pids_ev,
                        f"Adicionar keywords candidatas {candidatos_kw} na aresta '{eid}' (para={r.para}).",
                        "CONFIDENCE_CALIBRATION",
                    )
                )

    for col in colisoes:
        sugestoes_brutas.append(
            (
                "SUG-KW-COLLISION",
                "media" if col.tipo == "exata" else "baixa",
                ".github/agents/routing-graph.yaml",
                f"keyword:{col.keyword_norm}",
                (),
                f"Resolver colisao {col.tipo} da keyword '{col.keyword_norm}' compartilhada entre arestas {list(col.edges)}.",
                "KEYWORD_COLLISION",
            )
        )

    limiar_sup = max(1, int(min_support))
    for (exp_r, obs_r), pids_lista in sorted(confusao_pares.items()):
        if len(pids_lista) >= limiar_sup:
            sugestoes_brutas.append(
                (
                    "SUG-DISAMBIG",
                    "alta",
                    ".github/agents/agent-router.agent.md",
                    f"disambig:{exp_r}->{obs_r}",
                    tuple(sorted(set(pids_lista))[:5]),
                    (
                        f"Adicionar regra de desambiguacao explicita entre '@{exp_r}' e '@{obs_r}' "
                        f"({len(pids_lista)} ocorrencias) e calibrar prioridade no routing-graph.yaml."
                    ),
                    "KEYWORD_COLLISION",
                )
            )

    for eid_orfa in orfas.sem_golden:
        r_orfa = mapa_rotas[eid_orfa]
        sugestoes_brutas.append(
            (
                "SUG-GOLDEN-GAP",
                "baixa",
                ".github/agents/evals/casos-roteamento.yaml",
                f"arestas[{eid_orfa}:{r_orfa.para}]",
                (),
                f"Curar e promover caso Silver via synth-export/synth-promote para cobrir a aresta orfa '{eid_orfa}' (para={r_orfa.para}).",
                "COVERAGE_GAP",
            )
        )

    for no_ausente in divergencias.nos_nao_citados:
        sugestoes_brutas.append(
            (
                "SUG-ROUTER-DOC",
                "media",
                ".github/agents/agent-router.agent.md",
                f"node:{no_ausente}",
                (),
                f"Documentar o agente '@{no_ausente}' nas instrucoes do agent-router.agent.md.",
                "PROMPT_DRIFT",
            )
        )
    for citado_fora in divergencias.citados_fora_do_grafo:
        sugestoes_brutas.append(
            (
                "SUG-ROUTER-DOC",
                "media",
                ".github/agents/routing-graph.yaml",
                f"nos:{citado_fora}",
                (),
                f"Alinhar agente '@{citado_fora}' citado em agent-router.agent.md mas ausente em routing-graph.yaml::nos.",
                "PROMPT_DRIFT",
            )
        )

    for fantasma in divergencias.rotas_fantasma:
        pids_f = tuple(sorted(set(fantasma_pids.get(fantasma, [])))[:5])
        sugestoes_brutas.append(
            (
                "SUG-GRAPH-PHANTOM",
                "alta",
                ".github/agents/agent-router.agent.md",
                f"phantom:{fantasma}",
                pids_f,
                f"Rota fantasma observada '{fantasma}' nao pertence a routing-graph.yaml::nos; restringir delegacao no prompt.",
                "PROMPT_DRIFT",
            )
        )

    sugestoes_ordenadas: list[SugestaoAcionavel] = []
    for idx, item in enumerate(sugestoes_brutas, start=1):
        cod, sev, alvo_arq, alvo_anc, evs, prop, cat = item
        sugestoes_ordenadas.append(
            SugestaoAcionavel(
                id=f"SUG-{idx:04d}",
                codigo=cod,
                severidade=sev,
                alvo_arquivo=alvo_arq,
                alvo_ancora=alvo_anc,
                evidencias=evs,
                proposta_texto=prop,
                categoria_divergencia=cat,
            )
        )

    diag_seed = f"{eval_run_id}:{snapshot.sha256}:{router_agent_sha256}:{golden_set_sha256}"
    diag_id = "diag-" + hashlib.sha256(diag_seed.encode("utf-8")).hexdigest()[:12]

    return DiagnosticoAssertividade(
        diagnostic_version=DIAGNOSTIC_VERSION,
        diagnostic_id=diag_id,
        eval_run_id=eval_run_id,
        finished_at=finished_at,
        hashes=HashesDiagnostico(
            routing_graph_sha256=snapshot.sha256,
            router_agent_sha256=router_agent_sha256,
            golden_set_sha256=golden_set_sha256,
        ),
        resumo=resumo,
        por_aresta=tuple(metricas_aresta),
        matriz_confusao=matriz_ordenada,
        orfas=orfas,
        colisoes=colisoes,
        divergencias_router_md=divergencias,
        sugestoes=tuple(sugestoes_ordenadas),
        aviso=AVISO_HITL,
    )
