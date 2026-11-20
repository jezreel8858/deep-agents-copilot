"""
seeds — Coverage-Guided Seeding para arestas, workflows do routing-graph e skills A/B (B2 / §3.1 / §7 / P5).
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal, Mapping, Protocol, Sequence, runtime_checkable

import yaml

from governance_runner.synth.golden import GoldenSeed
from governance_runner.synth.normalize import normalizar, sanitizar_prompt
from governance_runner.synth.routing_graph import (
    GrafoSnapshot,
    RotaGrafo,
    WorkflowGrafo,
    resolver_aresta,
    resolver_workflow,
    rotas_validas,
)

__all__ = [
    "MODOS_GRAPH_SEEDING",
    "MODOS_WORKFLOW_SEEDING",
    "MODOS_SKILL_SEEDING",
    "ModoGraphSeeding",
    "ModoWorkflowSeeding",
    "ModoSkillSeeding",
    "SeedLike",
    "SeedRef",
    "SkillSeedRef",
    "calcular_cobertura_golden",
    "calcular_cobertura_workflows_golden",
    "calcular_cobertura_skills",
    "enriquecer_seeds_golden",
    "identificar_arestas_uncoverable",
    "identificar_workflows_uncoverable",
    "identificar_skills_uncoverable",
    "gerar_seeds_grafo",
    "gerar_seeds_workflows",
    "gerar_seeds_skills",
]

ModoGraphSeeding = Literal["off", "gaps", "all"]
MODOS_GRAPH_SEEDING: tuple[ModoGraphSeeding, ...] = ("off", "gaps", "all")
ModoWorkflowSeeding = Literal["off", "gaps", "all"]
MODOS_WORKFLOW_SEEDING: tuple[ModoWorkflowSeeding, ...] = ("off", "gaps", "all")
ModoSkillSeeding = Literal["off", "gaps", "all"]
MODOS_SKILL_SEEDING: tuple[ModoSkillSeeding, ...] = ("off", "gaps", "all")

DEFAULT_SKILLS_REL_DIR = Path(".github") / "skills"
DEFAULT_SKILL_AB_CASES_REL_PATH = Path("tests") / "evals" / "skill_ab_cases.yaml"

_MAX_LEN_TOKEN = 120
_MAX_LEN_PROMPT = 360
_REGEX_CONTROLES = re.compile(r"[\x00-\x1f\x7f]+")
_REGEX_MENCAO_AGENTE = re.compile(r"@[A-Za-z0-9_\-]+")
_REGEX_CLAUSULA_OBRIGATORIA = re.compile(
    r"(?:OBRIGAT[ÓO]RIO|MUST|EXIG[EI]|R-\d{3}|`[^`]{3,60}`)",
    re.IGNORECASE,
)
_REGEX_ANTIPADRAO = re.compile(
    r"(?:NUNCA|PROIBIDO|NEVER|FORBIDDEN|ANTI-?PATTERN)\s*[:\-]?\s*([^\n.;]{6,90})",
    re.IGNORECASE,
)


@runtime_checkable
class SeedLike(Protocol):
    @property
    def id(self) -> str: ...

    @property
    def prompt(self) -> str: ...

    @property
    def expected_route(self) -> str | None: ...

    @property
    def agent_route(self) -> str: ...

    @property
    def seed_case_id(self) -> str: ...

    @property
    def seed_source(self) -> Literal["manual", "routing_graph", "skill_ab"]: ...

    @property
    def graph_edge_id(self) -> str | None: ...

    @property
    def graph_edge_resolution(self) -> str | None: ...

    @property
    def keywords(self) -> tuple[str, ...]: ...


@dataclass(frozen=True)
class SeedRef:
    """Referencia de semente gerada a partir de aresta, gatilho de workflow ou lacuna de skill."""

    prompt: str
    expected_route: str | None
    seed_case_id: str
    seed_source: Literal["manual", "routing_graph", "skill_ab"] = "routing_graph"
    graph_edge_id: str | None = None
    keywords: tuple[str, ...] = ()
    graph_edge_resolution: str | None = "keyword"
    expected_workflow: str | None = None
    graph_workflow_id: str | None = None

    @property
    def id(self) -> str:
        return self.seed_case_id

    @property
    def solicitacao(self) -> str:
        return self.prompt

    @property
    def agent_route(self) -> str:
        return self.expected_route or self.expected_workflow or "agent-router"


@dataclass(frozen=True)
class SkillSeedRef(SeedRef):
    """Semente pareada (baseline vs. treatment) derivada de SKILL.md ou skill_ab_cases.yaml (P5)."""

    skill_name: str = ""
    baseline_prompt: str = ""
    required_clauses: tuple[str, ...] = ()
    forbidden_antipatterns: tuple[str, ...] = ()
    min_delta_utility: float = 0.05


def _limpar_fragmento_inerte(texto: str, *, ids_nos: frozenset[str] = frozenset()) -> str:
    if not texto:
        return ""
    limpo = _REGEX_CONTROLES.sub(" ", str(texto))
    limpo = _REGEX_MENCAO_AGENTE.sub("", limpo)
    for no_id in ids_nos:
        if no_id and len(no_id) >= 4:
            limpo = re.sub(re.escape(no_id), "sistema", limpo, flags=re.IGNORECASE)
    for proibido in (
        "Rota:",
        "Delegado:",
        "Agente Ativo:",
        "Workflow:",
        "Etapa do Workflow:",
        "expected_agent_route",
        "run_subagent",
    ):
        limpo = re.sub(re.escape(proibido), "", limpo, flags=re.IGNORECASE)
    limpo = " ".join(limpo.split()).strip(" -:;,.?!")
    return limpo[:_MAX_LEN_TOKEN].strip()


def calcular_cobertura_golden(
    golden_seeds: Sequence[GoldenSeed | SeedLike],
    snapshot: GrafoSnapshot,
) -> dict[str, int]:
    cobertura: dict[str, int] = {r.edge_id: 0 for r in rotas_validas(snapshot)}
    for seed in golden_seeds:
        rota = seed.expected_route or ""
        edge_id, _ = resolver_aresta(rota, normalizar(seed.prompt), snapshot)
        if edge_id is not None and edge_id in cobertura:
            cobertura[edge_id] += 1
    return cobertura


def calcular_cobertura_workflows_golden(
    golden_seeds: Sequence[GoldenSeed | SeedLike],
    snapshot: GrafoSnapshot,
) -> dict[str, int]:
    """Calcula quantas seeds do golden set cobrem cada workflow declarado no snapshot."""
    cobertura: dict[str, int] = {w.workflow_id: 0 for w in snapshot.workflows}
    for seed in golden_seeds:
        wf_exp = getattr(seed, "expected_workflow", None) or getattr(seed, "graph_workflow_id", None)
        wf_id = resolver_workflow(wf_exp, normalizar(seed.prompt), snapshot)
        if wf_id is not None and wf_id in cobertura:
            cobertura[wf_id] += 1
    return cobertura


def enriquecer_seeds_golden(
    golden_seeds: Sequence[GoldenSeed],
    snapshot: GrafoSnapshot,
) -> tuple[GoldenSeed, ...]:
    enriquecidas: list[GoldenSeed] = []
    ids_wf = {w.workflow_id for w in snapshot.workflows}
    for seed in golden_seeds:
        edge_id, res_kind = resolver_aresta(seed.expected_route, normalizar(seed.prompt), snapshot)
        wf_id = seed.expected_workflow if (seed.expected_workflow and seed.expected_workflow in ids_wf) else None
        enriquecidas.append(
            replace(
                seed,
                seed_source="manual",
                graph_edge_id=edge_id,
                graph_edge_resolution=res_kind,
                graph_workflow_id=wf_id,
            )
        )
    return tuple(enriquecidas)


def _extrair_termos_rota(rota: RotaGrafo, ids_nos: frozenset[str]) -> tuple[list[str], str]:
    kws_limpas = [
        _limpar_fragmento_inerte(k, ids_nos=ids_nos)
        for k in rota.keywords
        if _limpar_fragmento_inerte(k, ids_nos=ids_nos)
    ]
    contexto_bruto = rota.sinal_r006 or rota.sinal or rota.gatilho or rota.descricao_no or ""
    contexto_limpo = _limpar_fragmento_inerte(contexto_bruto, ids_nos=ids_nos)
    return kws_limpas, contexto_limpo


def identificar_arestas_uncoverable(snapshot: GrafoSnapshot) -> tuple[str, ...]:
    uncoverable: list[str] = []
    for rota in rotas_validas(snapshot):
        kws, ctx = _extrair_termos_rota(rota, snapshot.nos)
        if not kws and not ctx:
            uncoverable.append(rota.edge_id)
    return tuple(sorted(uncoverable))


def identificar_workflows_uncoverable(snapshot: GrafoSnapshot) -> tuple[str, ...]:
    """Retorna os workflow_ids sem gatilhos validos ou sem padroes de etapa 1."""
    uncoverable: list[str] = []
    for wf in snapshot.workflows:
        gatilhos_limpos = [
            _limpar_fragmento_inerte(g, ids_nos=snapshot.nos)
            for g in (wf.gatilhos or wf.gatilhos_norm)
            if _limpar_fragmento_inerte(g, ids_nos=snapshot.nos)
        ]
        if not gatilhos_limpos or not wf.etapa1_padroes:
            uncoverable.append(wf.workflow_id)
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
        else:
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


def _resolver_rota_etapa1(
    wf: WorkflowGrafo,
    gatilho: str | None = None,
    snapshot: GrafoSnapshot | None = None,
) -> str | None:
    """Retorna o padrao concreto da etapa 1 aderente ao gatilho ou o 1o padrao concreto."""
    concretos = [
        p.strip()
        for p in wf.etapa1_padroes
        if p.strip() and "*" not in p and "<stack>" not in p
    ]
    if not concretos:
        return None
    if len(concretos) > 2 and gatilho and snapshot is not None:
        gat_norm = normalizar(gatilho)
        concretos_set = frozenset(concretos)
        melhor_rota: str | None = None
        melhor_score = 0
        for rota in rotas_validas(snapshot):
            if rota.para.lower() not in concretos_set:
                continue
            score = sum(1 for kw in rota.keywords_norm if kw and (kw in gat_norm or gat_norm in kw))
            if score > melhor_score:
                melhor_score = score
                melhor_rota = rota.para.lower()
        if melhor_rota is not None:
            return melhor_rota
    return concretos[0]


def gerar_seeds_workflows(
    snapshot: GrafoSnapshot,
    modo_ou_cobertura: ModoWorkflowSeeding | Mapping[str, int] | None = "off",
    *,
    modo: ModoWorkflowSeeding | None = None,
    cobertura: Mapping[str, int] | None = None,
    golden_seeds: Sequence[GoldenSeed | SeedLike] = (),
    min_cobertura: int = 1,
    rng_seed: int = 42,
    max_seeds_por_workflow: int = 25,
) -> tuple[SeedRef, ...]:
    """Gera 1 seed por gatilho de workflow e seeds de fronteira para pares colidentes (B2 / §7)."""
    if isinstance(modo_ou_cobertura, Mapping):
        cov_arg: Mapping[str, int] | None = modo_ou_cobertura
        modo_efetivo: str = modo if modo is not None else "off"
    else:
        cov_arg = cobertura
        modo_efetivo = modo if modo is not None else (modo_ou_cobertura or "off")

    if modo_efetivo not in MODOS_WORKFLOW_SEEDING:
        raise ValueError(
            f"Modo --workflow-seeds invalido: {modo_efetivo!r}. Esperado um de {MODOS_WORKFLOW_SEEDING}."
        )
    if modo_efetivo == "off" or not snapshot.workflows:
        return ()

    if cov_arg is not None:
        cov_map = dict(cov_arg)
    elif golden_seeds:
        cov_map = calcular_cobertura_workflows_golden(golden_seeds, snapshot)
    else:
        cov_map = {w.workflow_id: 0 for w in snapshot.workflows}

    rng = random.Random(rng_seed)
    geradas: list[SeedRef] = []
    workflows_ativos: set[str] = set()

    for wf in snapshot.workflows:
        cov_atual = int(cov_map.get(wf.workflow_id, 0))
        if modo_efetivo == "gaps" and cov_atual >= min_cobertura:
            continue
        workflows_ativos.add(wf.workflow_id)
        rota_esp = _resolver_rota_etapa1(wf)
        edge_id: str | None = None
        edge_res: str | None = None
        gatilhos_fonte = wf.gatilhos if wf.gatilhos else wf.gatilhos_norm
        nome_limpo = _limpar_fragmento_inerte(wf.nome, ids_nos=snapshot.nos)

        for idx, gat_bruto in enumerate(gatilhos_fonte[: max(1, max_seeds_por_workflow)]):
            gat_limpo = _limpar_fragmento_inerte(gat_bruto, ids_nos=snapshot.nos)
            if not gat_limpo:
                continue
            complemento = f" no contexto de {nome_limpo.lower()}" if nome_limpo else ""
            molde = _TEMPLATES_NEUTROS[(idx + rng.randint(0, len(_TEMPLATES_NEUTROS) - 1)) % len(_TEMPLATES_NEUTROS)]
            prompt_bruto = molde.format(termo_principal=gat_limpo, complemento=complemento)
            prompt_final = " ".join(prompt_bruto.split())[:_MAX_LEN_PROMPT].strip()
            ok, _ = sanitizar_prompt(prompt_final)
            if not ok:
                prompt_final = f"Preciso de auxilio tecnico sobre {gat_limpo} no sistema ({idx + 1})."
                ok2, _ = sanitizar_prompt(prompt_final)
                if not ok2:
                    continue
            rota_gat = _resolver_rota_etapa1(wf, gat_limpo, snapshot) or rota_esp
            if rota_gat is not None:
                edge_id, edge_res = resolver_aresta(rota_gat, normalizar(prompt_final), snapshot)
            geradas.append(
                SeedRef(
                    prompt=prompt_final,
                    expected_route=rota_gat,
                    seed_case_id=f"wf:{wf.workflow_id}:{idx}",
                    seed_source="routing_graph",
                    graph_edge_id=edge_id,
                    keywords=(gat_limpo,),
                    graph_edge_resolution=edge_res or "keyword",
                    expected_workflow=wf.workflow_id,
                    graph_workflow_id=wf.workflow_id,
                )
            )

    mapa_gatilhos: dict[str, list[WorkflowGrafo]] = {}
    for wf in snapshot.workflows:
        for gn in wf.gatilhos_norm:
            if gn:
                mapa_gatilhos.setdefault(gn, []).append(wf)

    pares_vistos: set[tuple[str, str, str]] = set()
    for gn in sorted(mapa_gatilhos.keys()):
        wfs = mapa_gatilhos[gn]
        if len(wfs) >= 2:
            for i in range(len(wfs)):
                for j in range(i + 1, len(wfs)):
                    wa, wb = wfs[i], wfs[j]
                    if wa.workflow_id == wb.workflow_id:
                        continue
                    if modo_efetivo == "gaps" and wa.workflow_id not in workflows_ativos and wb.workflow_id not in workflows_ativos:
                        continue
                    chave_par = (min(wa.workflow_id, wb.workflow_id), max(wa.workflow_id, wb.workflow_id), gn)
                    if chave_par in pares_vistos:
                        continue
                    pares_vistos.add(chave_par)
                    rota_a = _resolver_rota_etapa1(wa)
                    nome_a = _limpar_fragmento_inerte(wa.nome, ids_nos=snapshot.nos)
                    prompt_front = (
                        f"Solicito analise focada em {gn} especificamente para {nome_a.lower() or 'a demanda principal'}."
                    )[:_MAX_LEN_PROMPT].strip()
                    ok_f, _ = sanitizar_prompt(prompt_front)
                    if ok_f:
                        geradas.append(
                            SeedRef(
                                prompt=prompt_front,
                                expected_route=rota_a,
                                seed_case_id=f"wf-boundary:{wa.workflow_id}:{wb.workflow_id}:{gn}",
                                seed_source="routing_graph",
                                graph_edge_id=None,
                                keywords=(gn,),
                                graph_edge_resolution="keyword",
                                expected_workflow=wa.workflow_id,
                                graph_workflow_id=wa.workflow_id,
                            )
                        )

    return tuple(geradas)


def _listar_skills_catalogadas(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        return []
    index_file = skills_dir / ".index.json"
    if index_file.exists():
        try:
            payload = json.loads(index_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("skills"), list):
                nomes = [
                    str(item.get("name") or item.get("id") or "").strip()
                    for item in payload["skills"]
                    if isinstance(item, dict)
                ]
                filtrados = [n for n in nomes if n and (skills_dir / n / "SKILL.md").exists()]
                if filtrados:
                    return sorted(dict.fromkeys(filtrados))
        except Exception:  # noqa: BLE001
            pass
    return sorted(
        d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
    )


def _carregar_casos_ab_existentes(cases_path: Path) -> list[dict[str, Any]]:
    if not cases_path.exists():
        return []
    try:
        raw = yaml.safe_load(cases_path.read_text(encoding="utf-8")) or {}
        if isinstance(raw, dict) and isinstance(raw.get("cases"), list):
            return [c for c in raw["cases"] if isinstance(c, dict)]
    except Exception:  # noqa: BLE001
        return []
    return []


def calcular_cobertura_skills(
    skills_dir: Path | None = None,
    cases_path: Path | None = None,
    *,
    repo_root: Path | None = None,
) -> dict[str, int]:
    """Calcula quantos casos pareados A/B cobrem cada skill catalogada em .github/skills/."""
    base = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    s_dir = skills_dir if skills_dir is not None else (base / DEFAULT_SKILLS_REL_DIR)
    c_path = cases_path if cases_path is not None else (base / DEFAULT_SKILL_AB_CASES_REL_PATH)
    skills = _listar_skills_catalogadas(s_dir)
    cobertura: dict[str, int] = {s: 0 for s in skills}
    for caso in _carregar_casos_ab_existentes(c_path):
        sk = str(caso.get("skill_name") or "").strip()
        if sk in cobertura:
            cobertura[sk] += 1
    return cobertura


def _extrair_rubrica_de_skill_md(skill_md_path: Path) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """Extrai (descricao, required_clauses, forbidden_antipatterns) a partir do SKILL.md."""
    texto = skill_md_path.read_text(encoding="utf-8", errors="replace")
    descricao = ""
    corpo = texto
    if texto.lstrip().startswith("---"):
        partes = texto.lstrip().split("---", 2)
        if len(partes) == 3:
            try:
                fm = yaml.safe_load(partes[1]) or {}
                if isinstance(fm, dict):
                    descricao = str(fm.get("description") or "").strip()
            except Exception:  # noqa: BLE001
                descricao = ""
            corpo = partes[2]

    clausulas: list[str] = []
    for linha in corpo.splitlines():
        l_strip = linha.strip()
        if not l_strip or l_strip.startswith("#"):
            continue
        if _REGEX_CLAUSULA_OBRIGATORIA.search(l_strip):
            ticks = re.findall(r"`([^`]{3,60})`", l_strip)
            for t in ticks:
                if t not in clausulas and not t.startswith("http"):
                    clausulas.append(t)
                    if len(clausulas) >= 4:
                        break
            if len(clausulas) < 4:
                regras = re.findall(r"\bR-\d{3}\b", l_strip)
                for r in regras:
                    if r not in clausulas:
                        clausulas.append(r)
                        if len(clausulas) >= 4:
                            break
        if len(clausulas) >= 4:
            break

    antipadroes: list[str] = []
    for m in _REGEX_ANTIPADRAO.finditer(corpo):
        trecho = " ".join(m.group(1).split()).strip(" `*:-")
        if 6 <= len(trecho) <= 80 and trecho not in antipadroes:
            antipadroes.append(trecho)
            if len(antipadroes) >= 2:
                break

    return descricao, tuple(clausulas), tuple(antipadroes)


def identificar_skills_uncoverable(
    skills_dir: Path | None = None,
    *,
    repo_root: Path | None = None,
) -> tuple[str, ...]:
    """Retorna skills catalogadas cujo SKILL.md nao possui clausulas normativas extrativeis."""
    base = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    s_dir = skills_dir if skills_dir is not None else (base / DEFAULT_SKILLS_REL_DIR)
    uncoverable: list[str] = []
    for skill_name in _listar_skills_catalogadas(s_dir):
        _, clausulas, _ = _extrair_rubrica_de_skill_md(s_dir / skill_name / "SKILL.md")
        if not clausulas:
            uncoverable.append(skill_name)
    return tuple(sorted(uncoverable))


def gerar_seeds_skills(
    *,
    modo: ModoSkillSeeding = "off",
    skills_dir: Path | None = None,
    cases_path: Path | None = None,
    skills_filtro: Sequence[str] | None = None,
    expected_route_padrao: str = "governance-maintainer",
    repo_root: Path | None = None,
) -> tuple[SkillSeedRef, ...]:
    """Gera seeds pareadas A/B para skills descobertas em .github/skills/ (P5 + synth)."""
    if modo not in MODOS_SKILL_SEEDING:
        raise ValueError(
            f"Modo --skill-seeding invalido: {modo!r}. Esperado um de {MODOS_SKILL_SEEDING}."
        )
    if modo == "off":
        return ()

    base = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    s_dir = skills_dir if skills_dir is not None else (base / DEFAULT_SKILLS_REL_DIR)
    c_path = cases_path if cases_path is not None else (base / DEFAULT_SKILL_AB_CASES_REL_PATH)

    filtro_set: frozenset[str] | None = None
    if skills_filtro:
        filtro_set = frozenset(s.strip() for s in skills_filtro if s and s.strip())

    casos_existentes = _carregar_casos_ab_existentes(c_path)
    casos_por_skill: dict[str, list[dict[str, Any]]] = {}
    for c in casos_existentes:
        sk = str(c.get("skill_name") or "").strip()
        if sk:
            casos_por_skill.setdefault(sk, []).append(c)

    geradas: list[SkillSeedRef] = []
    for skill_name in _listar_skills_catalogadas(s_dir):
        if filtro_set is not None and skill_name not in filtro_set:
            continue
        existentes = casos_por_skill.get(skill_name, [])
        if modo == "gaps" and existentes:
            continue

        if existentes:
            for idx, c in enumerate(existentes):
                cid = str(c.get("case_id") or f"skill-ab:{skill_name}:{idx}")
                b_prompt = str(c.get("baseline_prompt") or f"Executar tarefa de {skill_name}.").strip()
                req = tuple(str(x) for x in (c.get("required_clauses") or ()) if str(x).strip())
                anti = tuple(str(x) for x in (c.get("forbidden_antipatterns") or ()) if str(x).strip())
                min_d = float(c.get("min_delta_utility") or 0.05)
                geradas.append(
                    SkillSeedRef(
                        prompt=b_prompt,
                        expected_route=expected_route_padrao,
                        seed_case_id=cid,
                        seed_source="skill_ab",
                        keywords=(skill_name,) + req[:2],
                        skill_name=skill_name,
                        baseline_prompt=b_prompt,
                        required_clauses=req,
                        forbidden_antipatterns=anti,
                        min_delta_utility=min_d,
                    )
                )
            continue

        skill_md = s_dir / skill_name / "SKILL.md"
        desc, clausulas, antipadroes = _extrair_rubrica_de_skill_md(skill_md)
        if not clausulas:
            continue
        tema = _limpar_fragmento_inerte(desc) or skill_name.replace("-", " ")
        prompt_neutro = (
            f"Preciso aplicar as praticas canonicas de {skill_name} para {tema.lower()}."
        )[:_MAX_LEN_PROMPT].strip()
        ok, _ = sanitizar_prompt(prompt_neutro)
        if not ok:
            prompt_neutro = f"Preciso aplicar as diretrizes tecnicas da skill {skill_name}."
        geradas.append(
            SkillSeedRef(
                prompt=prompt_neutro,
                expected_route=expected_route_padrao,
                seed_case_id=f"skill-gap:{skill_name}:0",
                seed_source="skill_ab",
                keywords=(skill_name,) + clausulas[:2],
                skill_name=skill_name,
                baseline_prompt=prompt_neutro,
                required_clauses=clausulas,
                forbidden_antipatterns=antipadroes,
                min_delta_utility=0.05,
            )
        )

    return tuple(geradas)