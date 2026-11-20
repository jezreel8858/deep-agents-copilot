"""
diagnostics — Oraculo offline deterministico de assertividade de roteamento e utilidade de skills (B3-01 / CA-05 / P5).

Invariantes:
- Puramente deterministico e 100% offline (zero chamadas LLM / SDK).
- Timestamp unico derivado de synth_runs.finished_at (ou started_at se nulo) — nunca datetime.now().
- Ordenacao lexicografica estavel em todas as colecoes; floats arredondados com round(x, 6).
"""

from __future__ import annotations

import hashlib
import json
import re
from fnmatch import fnmatchcase
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Sequence

from governance_runner.synth.golden import GoldenSeed
from governance_runner.synth.normalize import normalizar
from governance_runner.synth.routing_graph import (
    GrafoSnapshot,
    RotaGrafo,
    WorkflowGrafo,
    resolver_aresta,
    rotas_validas,
)
from governance_runner.synth.seeds import (
    calcular_cobertura_golden,
    identificar_arestas_uncoverable,
    identificar_workflows_uncoverable,
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
    "MetricaWorkflow",
    "ColisaoWorkflow",
    "MetricaSkillAB",
    "SkillsOrfas",
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
    "SUG-WF-COLLISION",
    "SUG-WF-LOW-RECALL",
    "SUG-WF-LOW-PRECISION",
    "SUG-WF-INCONSISTENT-ROUTE",
    "SUG-WF-MISSING-BANNER",
    "SUG-WF-UNKNOWN-ID",
    "SUG-WF-UNCOVERABLE",
    "SUG-SKILL-REDUNDANT",
    "SUG-SKILL-COVERAGE-GAP",
    "SUG-SKILL-UNCOVERABLE",
)

LIMIAR_F1_WORKFLOW = 0.7

CATEGORIAS_DIVERGENCIA: tuple[str, ...] = (
    "KEYWORD_COLLISION",
    "PROMPT_DRIFT",
    "COVERAGE_GAP",
    "CONFIDENCE_CALIBRATION",
    "SKILL_UTILITY",
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
    workflow_macro_f1: float | None = None
    workflow_accuracy: float | None = None
    workflow_route_consistency_rate: float | None = None
    banner_coverage: float | None = None
    skills_avaliadas: int = 0
    skills_redundantes: int = 0
    skills_sem_cobertura: int = 0
    mean_skill_delta_utility: float | None = None


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
class MetricaWorkflow:
    workflow_id: str
    suporte: int
    tp: int
    fp: int
    fn: int
    precision: float | None
    recall: float | None
    f1: float | None


@dataclass(frozen=True)
class ColisaoWorkflow:
    gatilho_norm: str
    workflows: tuple[str, ...]
    tipo: Literal["exata", "substring", "gatilho_aresta"]
    edges: tuple[str, ...] = ()


@dataclass(frozen=True)
class MetricaSkillAB:
    skill_name: str
    casos: int
    passed: int
    redundant_cases: int
    mean_baseline_score: float
    mean_treatment_score: float
    mean_delta_utility: float
    min_delta_utility: float
    redundant: bool
    missing_clauses: tuple[str, ...] = ()
    triggered_antipatterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillsOrfas:
    sem_cobertura_ab: tuple[str, ...] = ()
    uncoverable: tuple[str, ...] = ()


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
    por_workflow: tuple[MetricaWorkflow, ...] = ()
    matriz_confusao_workflow: dict[str, dict[str, int]] = field(default_factory=dict)
    colisoes_workflow: tuple[ColisaoWorkflow, ...] = ()
    skill_ab_run_id: str | None = None
    por_skill_ab: tuple[MetricaSkillAB, ...] = ()
    skills_orfas: SkillsOrfas = field(default_factory=SkillsOrfas)


def _r6(valor: float) -> float:
    return round(float(valor), 6)


def _div_segura(num: int | float, den: int | float) -> float | None:
    if den <= 0:
        return None
    return _r6(float(num) / float(den))


def _parse_json_str_list(raw: Any) -> tuple[str, ...]:
    if isinstance(raw, (list, tuple)):
        return tuple(str(x) for x in raw if str(x).strip())
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return tuple(str(x) for x in parsed if str(x).strip())
        except Exception:  # noqa: BLE001
            return ()
    return ()


def _calcular_metricas_skill_ab(
        *,
        skill_ab_evals: Sequence[Mapping[str, Any]],
        skills_cobertura: Mapping[str, int] | None,
        skills_uncoverable: Sequence[str],
) -> tuple[tuple[MetricaSkillAB, ...], SkillsOrfas, float | None]:
    """Agrega resultados pareados A/B por skill e identifica lacunas de cobertura."""
    por_skill: dict[str, list[Mapping[str, Any]]] = {}
    for item in skill_ab_evals:
        sk = str(item.get("skill_name") or "").strip()
        if sk:
            por_skill.setdefault(sk, []).append(item)

    metricas: list[MetricaSkillAB] = []
    todos_deltas: list[float] = []
    for sk in sorted(por_skill.keys()):
        itens = sorted(
            por_skill[sk],
            key=lambda x: (str(x.get("case_id", "")), str(x.get("skill_eval_id", ""))),
        )
        n_casos = len(itens)
        n_passed = sum(1 for x in itens if int(x.get("passed", 0)) == 1)
        n_red = sum(1 for x in itens if int(x.get("redundant", 0)) == 1)
        baselines = [float(x.get("baseline_score", 0.0)) for x in itens]
        treatments = [float(x.get("treatment_score", 0.0)) for x in itens]
        deltas = [float(x.get("delta_utility", 0.0)) for x in itens]
        min_deltas = [float(x.get("min_delta_utility", 0.05)) for x in itens]
        todos_deltas.extend(deltas)

        mean_base = _r6(sum(baselines) / n_casos)
        mean_treat = _r6(sum(treatments) / n_casos)
        mean_delta = _r6(sum(deltas) / n_casos)
        min_delta = _r6(max(min_deltas) if min_deltas else 0.05)

        missing_set: set[str] = set()
        anti_set: set[str] = set()
        for x in itens:
            missing_set.update(_parse_json_str_list(x.get("missing_clauses_json") or x.get("missing_clauses")))
            anti_set.update(_parse_json_str_list(x.get("triggered_anti_json") or x.get("triggered_antipatterns")))

        is_redundant = (n_red > 0) or (mean_delta < min_delta)
        metricas.append(
            MetricaSkillAB(
                skill_name=sk,
                casos=n_casos,
                passed=n_passed,
                redundant_cases=n_red,
                mean_baseline_score=mean_base,
                mean_treatment_score=mean_treat,
                mean_delta_utility=mean_delta,
                min_delta_utility=min_delta,
                redundant=is_redundant,
                missing_clauses=tuple(sorted(missing_set)),
                triggered_antipatterns=tuple(sorted(anti_set)),
            )
        )

    avaliadas_set = {m.skill_name for m in metricas}
    sem_cobertura: list[str] = []
    if skills_cobertura:
        for sk_name, qtd in sorted(skills_cobertura.items()):
            if int(qtd) <= 0 and sk_name not in avaliadas_set:
                sem_cobertura.append(sk_name)

    orfas_sk = SkillsOrfas(
        sem_cobertura_ab=tuple(sorted(set(sem_cobertura))),
        uncoverable=tuple(sorted(set(str(s) for s in skills_uncoverable if str(s).strip()))),
    )
    mean_global_delta = _r6(sum(todos_deltas) / len(todos_deltas)) if todos_deltas else None
    return tuple(metricas), orfas_sk, mean_global_delta


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


def _casa_padroes(rota: str, padroes: Sequence[str]) -> bool:
    alvo = (rota or "").strip().lstrip("@").lower()
    return any(fnmatchcase(alvo, p) for p in padroes)


def _detectar_colisoes_workflow(
        workflows: Sequence[WorkflowGrafo],
        rotas: Sequence[RotaGrafo],
) -> tuple[ColisaoWorkflow, ...]:
    """Detecta colisoes entre gatilhos de workflows distintos e entre gatilho x keyword de aresta incoerente."""
    colisoes: list[ColisaoWorkflow] = []
    vistos: set[tuple[str, tuple[str, ...], str]] = set()
    por_gatilho: dict[str, set[str]] = {}
    for wf in workflows:
        for g in wf.gatilhos_norm:
            if g:
                por_gatilho.setdefault(g, set()).add(wf.workflow_id)

    for g in sorted(por_gatilho):
        wfs = tuple(sorted(por_gatilho[g]))
        if len(wfs) >= 2 and (g, wfs, "exata") not in vistos:
            vistos.add((g, wfs, "exata"))
            colisoes.append(ColisaoWorkflow(gatilho_norm=g, workflows=wfs, tipo="exata"))

    for curto in sorted(g for g in por_gatilho if len(g) >= 4):
        wfs_sub: set[str] = set(por_gatilho[curto])
        tem_super = False
        for longo, ids in por_gatilho.items():
            if len(longo) > len(curto) and curto in longo and not ids <= por_gatilho[curto]:
                tem_super = True
                wfs_sub |= ids
        wfs_t = tuple(sorted(wfs_sub))
        if tem_super and len(wfs_t) >= 2 and (curto, wfs_t, "exata") not in vistos:
            if (curto, wfs_t, "substring") not in vistos:
                vistos.add((curto, wfs_t, "substring"))
                colisoes.append(ColisaoWorkflow(gatilho_norm=curto, workflows=wfs_t, tipo="substring"))

    for wf in workflows:
        for g in wf.gatilhos_norm:
            if len(g) < 4:
                continue
            edges: set[str] = set()
            for r in rotas:
                if _casa_padroes(r.para, wf.etapa1_padroes):
                    continue
                for kw in r.keywords_norm:
                    if len(kw) >= 4 and (kw == g or kw in g or g in kw):
                        edges.add(r.edge_id)
                        break
            if edges:
                colisoes.append(
                    ColisaoWorkflow(
                        gatilho_norm=g,
                        workflows=(wf.workflow_id,),
                        tipo="gatilho_aresta",
                        edges=tuple(sorted(edges)),
                    )
                )

    colisoes.sort(key=lambda c: (c.gatilho_norm, c.tipo, c.workflows, c.edges))
    return tuple(colisoes)


def _calcular_metricas_workflow(
        avaliacoes: Sequence[dict[str, Any]],
        snapshot: GrafoSnapshot,
) -> tuple[
    tuple[MetricaWorkflow, ...],
    dict[str, dict[str, int]],
    dict[str, float | None],
    dict[str, list[str]],
]:
    """Calcula P/R/F1 por workflow, macro-F1, acuracia, consistencia e banner_coverage (secao 4)."""
    ids = sorted({w.workflow_id for w in snapshot.workflows})
    tp: Counter[str] = Counter()
    fp: Counter[str] = Counter()
    fn: Counter[str] = Counter()
    sup: Counter[str] = Counter()
    matriz: dict[str, Counter[str]] = {}
    escopo = 0
    acertos = 0
    banner_validos = 0
    consist_validos = 0
    consist_ok = 0
    pids: dict[str, list[str]] = {
        "missing_banner": [],
        "unknown_id": [],
    }
    inconsistentes: dict[str, list[str]] = {}

    for ev in avaliacoes:
        pid = str(ev.get("prompt_id", ""))
        exp_raw = ev.get("expected_workflow")
        exp = str(exp_raw).strip() if exp_raw else ""
        obs_raw = ev.get("observed_workflow")
        obs = str(obs_raw).strip() if obs_raw else ""
        origem = str(ev.get("workflow_source") or "")
        cons = ev.get("workflow_route_consistent")
        if cons is not None:
            consist_validos += 1
            if int(cons) == 1:
                consist_ok += 1
            elif obs:
                chave = f"{obs}->{str(ev.get('observed_route') or '').strip().lstrip('@').lower()}"
                inconsistentes.setdefault(chave, []).append(pid)
        if origem == "invalid_id":
            pids["unknown_id"].append(pid)
        if not exp:
            continue
        escopo += 1
        sup[exp] += 1
        if obs:
            banner_validos += 1
        else:
            pids["missing_banner"].append(pid)
        matriz.setdefault(exp, Counter())[obs or "<none>"] += 1
        if obs == exp:
            tp[exp] += 1
            acertos += 1
        else:
            fn[exp] += 1
            if obs:
                fp[obs] += 1

    metricas: list[MetricaWorkflow] = []
    f1s: list[float] = []
    for wid in ids:
        prec = _div_segura(tp[wid], tp[wid] + fp[wid])
        rec = _div_segura(tp[wid], tp[wid] + fn[wid])
        f1: float | None = None
        if prec is not None and rec is not None and (prec + rec) > 0:
            f1 = _r6(2.0 * prec * rec / (prec + rec))
        if sup[wid] > 0 or fp[wid] > 0:
            f1s.append(f1 if f1 is not None else 0.0)
        metricas.append(
            MetricaWorkflow(
                workflow_id=wid,
                suporte=int(sup[wid]),
                tp=int(tp[wid]),
                fp=int(fp[wid]),
                fn=int(fn[wid]),
                precision=prec,
                recall=rec,
                f1=f1,
            )
        )
    matriz_ord = {
        k: {o: int(matriz[k][o]) for o in sorted(matriz[k])} for k in sorted(matriz)
    }
    agregados: dict[str, float | None] = {
        "macro_f1": _r6(sum(f1s) / len(f1s)) if f1s else None,
        "accuracy": _div_segura(acertos, escopo),
        "consistency": _div_segura(consist_ok, consist_validos),
        "banner_coverage": _div_segura(banner_validos, escopo),
    }
    pids_out: dict[str, list[str]] = {k: sorted(set(v)) for k, v in pids.items()}
    for chave, lista in inconsistentes.items():
        pids_out[f"inconsistent:{chave}"] = sorted(set(lista))
    return tuple(metricas), matriz_ord, agregados, pids_out


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
        citados_fora_do_grafo=tuple(sorted(citados_fora)),
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


_SugBruta = tuple[str, Literal["alta", "media", "baixa"], str, str, tuple[str, ...], str, str]


def _sugestoes_workflow(
        *,
        snapshot: GrafoSnapshot,
        colisoes: Sequence[ColisaoWorkflow],
        metricas: Sequence[MetricaWorkflow],
        pids: dict[str, list[str]],
        min_support: int,
) -> list[_SugBruta]:
    """Gera SUG-WF-* deterministicas em ordem estavel de codigo e ancora (secao 4)."""
    graph = ".github/agents/routing-graph.yaml"
    router = ".github/agents/agent-router.agent.md"
    saida: list[_SugBruta] = []
    limiar = max(1, int(min_support))

    for c in colisoes:
        saida.append(
            (
                "SUG-WF-COLLISION",
                "media" if c.tipo == "exata" else "baixa",
                graph,
                f"gatilho:{c.gatilho_norm}",
                (),
                f"Resolver colisao {c.tipo} do gatilho '{c.gatilho_norm}' entre workflows {list(c.workflows)}"
                + (f" e arestas {list(c.edges)}." if c.edges else "."),
                "KEYWORD_COLLISION",
            )
        )
    for m in metricas:
        if m.recall is not None and (m.tp + m.fn) >= limiar and m.recall < LIMIAR_F1_WORKFLOW:
            saida.append(
                (
                    "SUG-WF-LOW-RECALL",
                    "media",
                    graph,
                    f"workflows[{m.workflow_id}].gatilhos",
                    (),
                    f"Recall {m.recall:.6f} do workflow '{m.workflow_id}' abaixo de {LIMIAR_F1_WORKFLOW}; revisar gatilhos.",
                    "CONFIDENCE_CALIBRATION",
                )
            )
    for m in metricas:
        if m.precision is not None and (m.tp + m.fp) >= limiar and m.precision < LIMIAR_F1_WORKFLOW:
            saida.append(
                (
                    "SUG-WF-LOW-PRECISION",
                    "media",
                    graph,
                    f"workflows[{m.workflow_id}].gatilhos",
                    (),
                    f"Precisao {m.precision:.6f} do workflow '{m.workflow_id}' abaixo de {LIMIAR_F1_WORKFLOW}; restringir gatilhos.",
                    "CONFIDENCE_CALIBRATION",
                )
            )
    for chave in sorted(k for k in pids if k.startswith("inconsistent:")):
        lista = pids[chave]
        if len(lista) >= limiar:
            par = chave.split(":", 1)[1]
            saida.append(
                (
                    "SUG-WF-INCONSISTENT-ROUTE",
                    "media",
                    router,
                    f"wf-route:{par}",
                    tuple(lista[:5]),
                    f"Rota observada incoerente com a etapa 1 do workflow ({par}); alinhar delegacao com etapa 1.",
                    "PROMPT_DRIFT",
                )
            )
    if pids.get("missing_banner"):
        saida.append(
            (
                "SUG-WF-MISSING-BANNER",
                "baixa",
                router,
                "banner:workflow",
                tuple(pids["missing_banner"][:5]),
                "Respostas sem linha 'Workflow:' valida; reforcar o banner obrigatorio no agent-router.",
                "PROMPT_DRIFT",
            )
        )
    if pids.get("unknown_id"):
        saida.append(
            (
                "SUG-WF-UNKNOWN-ID",
                "media",
                router,
                "banner:workflow-id",
                tuple(pids["unknown_id"][:5]),
                "Workflow com ID fora do snapshot do grafo; alinhar IDs do banner aos workflows de routing-graph.yaml.",
                "PROMPT_DRIFT",
            )
        )
    for wid in identificar_workflows_uncoverable(snapshot):
        saida.append(
            (
                "SUG-WF-UNCOVERABLE",
                "baixa",
                graph,
                f"workflows[{wid}]",
                (),
                f"Workflow '{wid}' sem gatilhos validos ou sem padroes de etapa 1; nao eh possivel gerar seeds.",
                "COVERAGE_GAP",
            )
        )
    return saida


def _sugestoes_skill_ab(
        *,
        metricas_skill: Sequence[MetricaSkillAB],
        skills_orfas: SkillsOrfas,
        skill_ab_evals: Sequence[Mapping[str, Any]],
) -> list[_SugBruta]:
    """Gera sugestoes acionaveis (HITL) para skills redundantes ou sem cobertura A/B (P5)."""
    saida: list[_SugBruta] = []
    cases_por_skill: dict[str, list[str]] = {}
    for ev in skill_ab_evals:
        sk = str(ev.get("skill_name") or "").strip()
        cid = str(ev.get("case_id") or "").strip()
        if sk and cid and int(ev.get("redundant", 0)) == 1:
            cases_por_skill.setdefault(sk, []).append(cid)

    for m in metricas_skill:
        if m.redundant:
            detalhe_extra = ""
            if m.missing_clauses:
                detalhe_extra += f" Clausulas ausentes no tratamento: {list(m.missing_clauses)}."
            if m.triggered_antipatterns:
                detalhe_extra += f" Antipadrao disparado: {list(m.triggered_antipatterns)}."
            evidencias = tuple(sorted(set(cases_por_skill.get(m.skill_name, [])))[:5])
            saida.append(
                (
                    "SUG-SKILL-REDUNDANT",
                    "media",
                    f".github/skills/{m.skill_name}/SKILL.md",
                    f"skill:{m.skill_name}",
                    evidencias,
                    (
                        f"Skill '{m.skill_name}' redundante (delta_utility medio={m.mean_delta_utility:.6f} < "
                        f"min_delta_utility={m.min_delta_utility:.6f}); enxugar instrucoes ja cobertas pelo modelo "
                        f"base ou tornar regras verificaveis.{detalhe_extra}"
                    ),
                    "SKILL_UTILITY",
                )
            )

    uncov_set = set(skills_orfas.uncoverable)
    for sk_sem_cov in skills_orfas.sem_cobertura_ab:
        if sk_sem_cov in uncov_set:
            continue
        saida.append(
            (
                "SUG-SKILL-COVERAGE-GAP",
                "baixa",
                "tests/evals/skill_ab_cases.yaml",
                f"skill:{sk_sem_cov}",
                (),
                (
                    f"Skill '{sk_sem_cov}' catalogada em .github/skills/ sem casos pareados A/B; "
                    "adicionar caso em tests/evals/skill_ab_cases.yaml ou executar --skill-seeding gaps."
                ),
                "COVERAGE_GAP",
            )
        )

    for sk_uncov in skills_orfas.uncoverable:
        saida.append(
            (
                "SUG-SKILL-UNCOVERABLE",
                "baixa",
                f".github/skills/{sk_uncov}/SKILL.md",
                f"skill:{sk_uncov}",
                (),
                (
                    f"Skill '{sk_uncov}' sem clausulas normativas extrativeis (OBRIGATORIO/MUST/`codigo`/R-XXX); "
                    "explicitar criterios verificaveis ou cadastrar caso manual em skill_ab_cases.yaml."
                ),
                "COVERAGE_GAP",
            )
        )

    return saida


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
        skill_ab_evals: Sequence[Mapping[str, Any]] = (),
        skill_ab_run_id: str | None = None,
        skills_cobertura: Mapping[str, int] | None = None,
        skills_uncoverable: Sequence[str] = (),
) -> DiagnosticoAssertividade:
    """Executa o oraculo deterministico offline cruzando avaliacoes, grafo, agent-router.agent.md e skills A/B."""
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

    por_wf, matriz_wf, agg_wf, pids_wf = _calcular_metricas_workflow(avs_ordenadas, snapshot)
    macro_f1_wf = agg_wf["macro_f1"]

    por_skill_ab, skills_orfas, mean_skill_delta = _calcular_metricas_skill_ab(
        skill_ab_evals=skill_ab_evals,
        skills_cobertura=skills_cobertura,
        skills_uncoverable=skills_uncoverable,
    )
    n_skills_redundantes = sum(1 for m in por_skill_ab if m.redundant)

    resumo = ResumoDiagnostico(
        total_avaliacoes=total_avaliacoes,
        acuracia_global=_div_segura(total_passed, total_avaliacoes) or 0.0,
        cobertura_arestas_golden=_div_segura(arestas_com_golden, total_arestas_validas) or 0.0,
        cobertura_arestas_total=_div_segura(arestas_com_aval, total_arestas_validas) or 0.0,
        workflow_macro_f1=macro_f1_wf,
        workflow_accuracy=agg_wf["accuracy"],
        workflow_route_consistency_rate=agg_wf["consistency"],
        banner_coverage=agg_wf["banner_coverage"],
        skills_avaliadas=len(por_skill_ab),
        skills_redundantes=n_skills_redundantes,
        skills_sem_cobertura=len(skills_orfas.sem_cobertura_ab),
        mean_skill_delta_utility=mean_skill_delta,
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
    colisoes_wf = _detectar_colisoes_workflow(snapshot.workflows, validas)
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

    sugestoes_brutas.extend(
        _sugestoes_workflow(
            snapshot=snapshot,
            colisoes=colisoes_wf,
            metricas=por_wf,
            pids=pids_wf,
            min_support=min_support,
        )
    )
    sugestoes_brutas.extend(
        _sugestoes_skill_ab(
            metricas_skill=por_skill_ab,
            skills_orfas=skills_orfas,
            skill_ab_evals=skill_ab_evals,
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

    diag_seed = (
        f"{eval_run_id}:{skill_ab_run_id or ''}:{snapshot.sha256}:"
        f"{router_agent_sha256}:{golden_set_sha256}"
    )
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
        por_workflow=por_wf,
        matriz_confusao_workflow=matriz_wf,
        colisoes_workflow=colisoes_wf,
        skill_ab_run_id=skill_ab_run_id,
        por_skill_ab=por_skill_ab,
        skills_orfas=skills_orfas,
    )
