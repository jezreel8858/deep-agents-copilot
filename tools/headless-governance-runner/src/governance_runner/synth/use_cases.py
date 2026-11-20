"""
use_cases — Orquestração dos comandos synth-generate, synth-eval, synth-export, synth-promote, synth-diagnose e synth-skill-ab (B1 / §4.1 / §5 / §7 / P5).
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml

import governance_runner.synth.dedup as _dedup_mod
import governance_runner.synth.generator as _gen_mod
import governance_runner.synth.golden as _golden_mod
import governance_runner.synth.normalize as _norm_mod
import governance_runner.synth.routing_graph as _rg_mod
import governance_runner.synth.seeds as _seeds_mod
import governance_runner.synth.taxonomy as _tax_mod
from governance_runner.runner.budget import Budget
from governance_runner.synth.dedup import DedupFunnel
from governance_runner.synth.evaluator import (
    SdkClientProtocol,
    avaliar_lote_prompts,
    avaliar_lote_skill_ab,
)
from governance_runner.synth.generator import (
    DEFAULT_MAX_ATTEMPTS,
    GeradorSDK,
    GeradorSintetico,
    GeradorTemplate,
    gerar_sinteticos,
)
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.taxonomy import Estrato, ItemAlocacao

__all__ = [
    "BudgetExceededError",
    "SynthOrcamentoInvalidoError",
    "RelatorioSynth",
    "validar_orcamento_synth",
    "executar_synth_generate",
    "executar_synth_eval",
    "executar_synth_export",
    "executar_synth_promote",
    "executar_synth_diagnose",
    "executar_synth_skill_ab",
]

DEFAULT_GOLDEN_REL_PATH = Path("tests") / "evals" / "routing_golden_set.yaml"
DEFAULT_ROUTER_AGENT_REL_PATH = Path(".github") / "agents" / "agent-router.agent.md"
DEFAULT_SILVER_REL_DIR = Path(".cache") / "synth_silver"
DEFAULT_GOLDEN_REGRESSAO_REL_PATH = Path("tests") / "evals" / "routing_golden_regressao.yaml"
DEFAULT_DIAGNOSTICS_REL_DIR = Path(".cache") / "synth_diagnostics"
DEFAULT_SKILL_AB_CASES_REL_PATH: Path = getattr(
    _seeds_mod,
    "DEFAULT_SKILL_AB_CASES_REL_PATH",
    Path("tests") / "evals" / "skill_ab_cases.yaml",
    )
DEFAULT_SKILLS_REL_DIR: Path = getattr(
    _seeds_mod,
    "DEFAULT_SKILLS_REL_DIR",
    Path(".github") / "skills",
    )

_DIMENSOES_PADRAO: tuple[str, ...] = (
    "parafrase",
    "ruido_ortografico",
    "code_switching_pt_en",
    "omissao_palavra_chave",
    "distrator_outro_agente",
    "multi_intencao",
    "comprimento_extremo",
    "registro_informal",
)


class BudgetExceededError(RuntimeError):
    """Excecao lancada quando o teto de premium requests do Budget e atingido."""


class SynthOrcamentoInvalidoError(ValueError):
    """Erro lancado quando --max-premium-requests e omitido, invalido ou <= 0 (exit code 2)."""

    exit_code: int = 2


@dataclass(frozen=True)
class RelatorioSynth:
    comando: str
    run_id: str | None
    status: str
    exit_code: int
    contadores: dict[str, int]
    caminhos_gerados: tuple[str, ...] = ()
    motivo: str | None = None
    mean_skill_delta_utility: float | None = None


class _BudgetAdapter:
    """Adaptador sobre governance_runner.runner.budget.Budget para consumo incremental."""

    def __init__(self, max_requests: int) -> None:
        self.max_requests = int(max_requests)
        self.consumidos = 0
        self._inner = Budget(max_premium_requests=self.max_requests)

    def consumir(self, qtd: int = 1) -> None:
        veredito = self._inner.registrar_custo(qtd)
        if veredito.excedido:
            raise BudgetExceededError(veredito.motivo or "budget_exhausted")
        self.consumidos += qtd


def _importar_primeiro_modulo(nomes_modulo: Sequence[str]) -> Any:
    ultimo_erro: Exception | None = None
    for nome in nomes_modulo:
        try:
            return importlib.import_module(nome)
        except ModuleNotFoundError as exc:
            ultimo_erro = exc
            continue
    raise ModuleNotFoundError(
        f"Nenhum dos modulos candidatos foi encontrado: {list(nomes_modulo)}"
    ) from ultimo_erro


def _resolver_callable_modulo(
        modulo: Any,
        candidatos: Sequence[str],
        *,
        prefixos: Sequence[str] = (),
        contem: Sequence[str] = (),
) -> Callable[..., Any]:
    for nome in candidatos:
        fn = getattr(modulo, nome, None)
        if callable(fn):
            return fn
    exportados = getattr(modulo, "__all__", ()) or dir(modulo)
    for nome in exportados:
        nome_str = str(nome)
        if nome_str.startswith("_"):
            continue
        if any(nome_str.startswith(p) for p in prefixos) or any(c in nome_str for c in contem):
            fn = getattr(modulo, nome_str, None)
            if callable(fn):
                return fn
    raise AttributeError(f"Nenhuma funcao compativel encontrada em {modulo.__name__}: {candidatos}")


def _invocar_com_kwargs_aceitos(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    sig = inspect.signature(fn)
    aceita_var_kw = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )
    if aceita_var_kw:
        return fn(*args, **kwargs)
    filtrados = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return fn(*args, **filtrados)


def _obter_dimensoes_perturbacao() -> tuple[str, ...]:
    for nome in (
            "DIMENSOES_PERTURBACAO",
            "DIMENSOES",
            "DIMENSOES_VALIDAS",
            "PERTURBATION_DIMENSIONS",
            "DIMENSIONS",
    ):
        val = getattr(_tax_mod, nome, None) or getattr(_gen_mod, nome, None)
        if isinstance(val, (tuple, list, set, frozenset)) and val:
            return tuple(str(x) for x in val)
    return _DIMENSOES_PADRAO


def validar_orcamento_synth(
        comando: str,
        max_premium_requests: int | float | str | None,
        generator_mode: str | None = None,
) -> int | None:
    """Valida --max-premium-requests antes de qualquer chamada ao SDK (§4.1 / B1 / P5)."""
    exige = (comando == "synth-eval") or (
            comando in ("synth-generate", "synth-skill-ab") and generator_mode == "sdk"
    )
    if not exige and max_premium_requests is None:
        return None
    if max_premium_requests is None:
        raise SynthOrcamentoInvalidoError(
            f"O argumento --max-premium-requests e obrigatorio para '{comando}'."
        )
    if isinstance(max_premium_requests, bool):
        raise SynthOrcamentoInvalidoError("Valor invalido para --max-premium-requests: booleano.")
    try:
        if isinstance(max_premium_requests, float):
            if not math.isfinite(max_premium_requests):
                raise SynthOrcamentoInvalidoError(
                    f"Valor nao finito para --max-premium-requests: {max_premium_requests!r}."
                )
            valor = int(max_premium_requests)
            if valor != max_premium_requests:
                raise SynthOrcamentoInvalidoError(
                    f"Valor nao inteiro para --max-premium-requests: {max_premium_requests!r}."
                )
        else:
            texto = str(max_premium_requests).strip()
            valor = int(texto)
    except SynthOrcamentoInvalidoError:
        raise
    except (ValueError, TypeError) as exc:
        raise SynthOrcamentoInvalidoError(
            f"Valor nao numerico para --max-premium-requests: {max_premium_requests!r}."
        ) from exc

    if valor <= 0:
        raise SynthOrcamentoInvalidoError(
            f"--max-premium-requests deve ser um inteiro positivo (> 0); recebido {valor}."
        )
    return valor


def _sha256_arquivo(caminho: Path) -> str | None:
    if not caminho.exists():
        return None
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _resolver_arquivo(caminho: str | Path | None, default_rel: Path, repo_root: Path | None) -> Path:
    base = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    if caminho is None:
        return (base / default_rel).resolve()
    p = Path(caminho)
    return p.resolve() if p.is_absolute() else (base / p).resolve()


def _resolver_caminho_grafo(routing_graph_path: str | Path | None, repo_root: Path | None) -> Path:
    fn = getattr(_rg_mod, "resolver_caminho_routing_graph", None)
    if callable(fn):
        return Path(fn(routing_graph_path, repo_root=repo_root))
    return _resolver_arquivo(
        routing_graph_path,
        Path(".github") / "agents" / "routing-graph.yaml",
        repo_root,
        )


def _carregar_grafo_routing(grafo_path: Path, *, repo_root: Path | None = None) -> Any:
    return _rg_mod.carregar_snapshot_grafo(grafo_path, repo_root=repo_root)


def _carregar_golden_set(golden_path: Path, *, permitir_ausente: bool = False) -> tuple[Any, ...]:
    if permitir_ausente and not golden_path.exists():
        return ()
    for attr in ("carregar_golden_seeds", "extrair_golden_seeds", "carregar_seeds_golden", "load_golden_seeds"):
        fn = getattr(_golden_mod, attr, None)
        if callable(fn):
            return tuple(fn(golden_path))
    bruto = _golden_mod.carregar_golden_bruto(golden_path)
    if isinstance(bruto, dict) and "cases" in bruto:
        from governance_runner.synth.seeds import GoldenSeed
        return tuple(
            GoldenSeed(
                seed_id=str(c.get("id") or f"gs-{i}"),
                prompt=str(c.get("prompt") or ""),
                expected_route=str(c.get("expected_agent_route") or c.get("expected_route") or ""),
            )
            for i, c in enumerate(bruto.get("cases") or [], start=1)
        )
    return ()


def _listar_alvos_elegiveis(seeds_golden: Sequence[Any], *, include_security: bool) -> list[str]:
    fn = getattr(_golden_mod, "listar_alvos_elegiveis", None)
    if callable(fn):
        return list(_invocar_com_kwargs_aceitos(fn, seeds_golden, include_security=include_security))
    rotas = sorted(
        {
            str(getattr(s, "agent_route", None) or getattr(s, "expected_route", "")).strip().lower()
            for s in seeds_golden
            if getattr(s, "agent_route", None) or getattr(s, "expected_route", None)
        }
    )
    if not include_security:
        rotas = [r for r in rotas if "security" not in r]
    return rotas


def _construir_dedup_funnel(
        seeds_golden: Sequence[Any],
        repo: SynthRepository,
        *,
        sim_threshold: float,
        dry_run: bool,
) -> DedupFunnel:
    fn_fabrica = (
            getattr(_dedup_mod, "construir_funnel", None)
            or getattr(_dedup_mod, "criar_funnel", None)
            or getattr(_golden_mod, "construir_indice_dedup", None)
    )
    if callable(fn_fabrica):
        candidato = _invocar_com_kwargs_aceitos(
            fn_fabrica,
            seeds_golden,
            repo=repo,
            sim_threshold=sim_threshold,
            threshold=sim_threshold,
        )
        if isinstance(candidato, DedupFunnel):
            return candidato

    funnel = _invocar_com_kwargs_aceitos(
        DedupFunnel,
        threshold=sim_threshold,
        sim_threshold=sim_threshold,
    )
    for idx, s in enumerate(seeds_golden):
        txt = str(getattr(s, "prompt", None) or getattr(s, "text", "") or "").strip()
        if not txt:
            continue
        ref_id = str(getattr(s, "id", None) or getattr(s, "seed_case_id", None) or f"golden:{idx}")
        funnel.adicionar_documento(ref_id, txt)

    if not dry_run:
        for p in repo.listar_prompts():
            txt_p = str(p.get("text") or "").strip()
            if txt_p:
                funnel.adicionar_documento(
                    str(p.get("prompt_id") or p.get("sha256") or "db"),
                    txt_p,
                    text_norm=p.get("text_norm"),
                    sha256=p.get("sha256"),
                )
    return funnel


def _seeds_para_grafo(
        seeds_golden: Sequence[Any],
        snapshot: Any | None,
        *,
        graph_seeding: str,
        graph_min_coverage: int,
        rng_seed: int,
        targets: Sequence[str] | None,
) -> tuple[tuple[Any, ...], tuple[Any, ...], dict[str, int], tuple[str, ...]]:
    if snapshot is None:
        return tuple(seeds_golden), (), {}, ()
    fn_enriq = getattr(_seeds_mod, "enriquecer_seeds_golden", None)
    enriquecidas = tuple(fn_enriq(seeds_golden, snapshot)) if callable(fn_enriq) else tuple(seeds_golden)

    fn_cob = getattr(_seeds_mod, "calcular_cobertura_golden", None)
    cobertura = dict(fn_cob(enriquecidas, snapshot)) if callable(fn_cob) else {}

    fn_uncov = getattr(_seeds_mod, "identificar_arestas_uncoverable", None)
    uncoverable = tuple(fn_uncov(snapshot)) if callable(fn_uncov) else ()

    fn_seeds = getattr(_seeds_mod, "gerar_seeds_grafo", None)
    seeds_grafo = (
        tuple(
            _invocar_com_kwargs_aceitos(
                fn_seeds,
                snapshot,
                cobertura,
                min_cobertura=graph_min_coverage,
                modo=graph_seeding,
                rng_seed=rng_seed,
                targets=targets,
            )
        )
        if callable(fn_seeds)
        else ()
    )
    return enriquecidas, seeds_grafo, cobertura, uncoverable


def _adaptar_cliente_sdk(cliente_sdk: Any) -> Any:
    """Garante compatibilidade entre clientes fakes com .avaliar() e CopilotSDKClient com .invoke()."""
    if hasattr(cliente_sdk, "invoke") and callable(getattr(cliente_sdk, "invoke")):
        return cliente_sdk

    class _SdkInvokeWrapper:
        def __init__(self, inner: Any) -> None:
            self._inner = inner

        def invoke(self, request: Any) -> Any:
            prompt = getattr(request, "prompt", str(request))
            modelo = getattr(request, "modelo", None)
            resp = self._inner.avaliar(prompt, modelo=modelo)
            if not hasattr(resp, "achados"):
                setattr(resp, "achados", ())
            if not hasattr(resp, "premium_requests_consumidas"):
                setattr(resp, "premium_requests_consumidas", 1)
            return resp

    return _SdkInvokeWrapper(cliente_sdk)


def executar_synth_generate(
        *,
        repo: SynthRepository,
        generator_mode: str = "template",
        max_premium_requests: int | str | None = None,
        cliente_factory: Callable[[], SdkClientProtocol] | None = None,
        golden_path: str | Path | None = None,
        router_agent_path: str | Path | None = None,
        routing_graph_path: str | Path | None = None,
        graph_seeding: str = "off",
        graph_min_coverage: int = 3,
        workflow_seeds: str = "off",
        skill_seeding: str = "off",
        skills_filtro: Sequence[str] | None = None,
        skills_dir: str | Path | None = None,
        skill_cases_path: str | Path | None = None,
        targets: Sequence[str] | None = None,
        dimensions: Sequence[str] | None = None,
        per_stratum: int = 2,
        rng_seed: int = 42,
        sim_threshold: float = 0.85,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        include_security: bool = False,
        dry_run: bool = False,
        modelo: str | None = None,
        repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa synth-generate gerando prompts por estrato, aresta, workflow e/ou skill A/B (B1 / B2 / §7 / P5)."""
    orc_int = validar_orcamento_synth("synth-generate", max_premium_requests, generator_mode)

    g_path = _resolver_arquivo(golden_path, DEFAULT_GOLDEN_REL_PATH, repo_root)
    grafo_path = _resolver_caminho_grafo(routing_graph_path, repo_root=repo_root)
    s_dir = _resolver_arquivo(skills_dir, DEFAULT_SKILLS_REL_DIR, repo_root)
    sc_path = _resolver_arquivo(skill_cases_path, DEFAULT_SKILL_AB_CASES_REL_PATH, repo_root)

    snapshot: Any | None = None
    if grafo_path.exists() or routing_graph_path is not None or graph_seeding != "off" or workflow_seeds != "off":
        snapshot = _carregar_grafo_routing(grafo_path, repo_root=repo_root)

    tem_seeding_alternativo = (
            graph_seeding != "off" or workflow_seeds != "off" or skill_seeding != "off"
    )
    seeds_golden_raw = _carregar_golden_set(
        g_path,
        permitir_ausente=tem_seeding_alternativo and golden_path is None,
    )
    seeds_golden, seeds_grafo, cobertura_inicial, arestas_uncoverable = _seeds_para_grafo(
        seeds_golden_raw,
        snapshot,
        graph_seeding=graph_seeding,
        graph_min_coverage=graph_min_coverage,
        rng_seed=rng_seed,
        targets=targets,
    )

    cobertura_wf_inicial: dict[str, int] = {}
    workflows_uncoverable: tuple[str, ...] = ()
    seeds_wf: tuple[Any, ...] = ()
    if snapshot is not None:
        fn_cob_wf = getattr(_seeds_mod, "calcular_cobertura_workflows_golden", None)
        if callable(fn_cob_wf):
            cobertura_wf_inicial = dict(fn_cob_wf(seeds_golden, snapshot))
        fn_uncov_wf = getattr(_seeds_mod, "identificar_workflows_uncoverable", None)
        if callable(fn_uncov_wf):
            workflows_uncoverable = tuple(fn_uncov_wf(snapshot))
        fn_seeds_wf = getattr(_seeds_mod, "gerar_seeds_workflows", None)
        if callable(fn_seeds_wf):
            seeds_wf = tuple(
                _invocar_com_kwargs_aceitos(
                    fn_seeds_wf,
                    snapshot,
                    cobertura=cobertura_wf_inicial,
                    modo=workflow_seeds,
                    rng_seed=rng_seed,
                )
            )

    fn_seeds_sk = getattr(_seeds_mod, "gerar_seeds_skills", None)
    seeds_skill: tuple[Any, ...] = (
        tuple(
            _invocar_com_kwargs_aceitos(
                fn_seeds_sk,
                modo=skill_seeding,
                skills_dir=s_dir,
                cases_path=sc_path,
                skills_filtro=skills_filtro,
                repo_root=repo_root,
            )
        )
        if callable(fn_seeds_sk)
        else ()
    )

    alvos_base = _listar_alvos_elegiveis(seeds_golden, include_security=include_security)
    if targets:
        filtro_alvos = {t.strip().lstrip("@").lower() for t in targets if t.strip()}
        alvos = [a for a in alvos_base if a in filtro_alvos]
    else:
        alvos = list(alvos_base)

    if snapshot is not None and graph_seeding != "off":
        fn_rotas = getattr(_rg_mod, "rotas_validas", None)
        rotas_iter = fn_rotas(snapshot) if callable(fn_rotas) else ()
        rotas_grafo_alvos = {
            str(getattr(r, "para", "")).lower() for r in rotas_iter if getattr(r, "para", None)
        }
        if targets:
            filtro_alvos = {t.strip().lstrip("@").lower() for t in targets if t.strip()}
            rotas_grafo_alvos &= filtro_alvos
        alvos = sorted(set(alvos) | rotas_grafo_alvos)

    if workflow_seeds != "off" and seeds_wf:
        rotas_wf_alvos = {
            str(getattr(s, "expected_route", "")).lower()
            for s in seeds_wf
            if getattr(s, "expected_route", None)
        }
        if targets:
            filtro_alvos = {t.strip().lstrip("@").lower() for t in targets if t.strip()}
            rotas_wf_alvos &= filtro_alvos
        alvos = sorted(set(alvos) | rotas_wf_alvos)

    if skill_seeding != "off" and seeds_skill:
        rotas_sk_alvos = {
            str(getattr(s, "expected_route", "")).lower()
            for s in seeds_skill
            if getattr(s, "expected_route", None)
        }
        if targets:
            filtro_alvos = {t.strip().lstrip("@").lower() for t in targets if t.strip()}
            rotas_sk_alvos &= filtro_alvos
        alvos = sorted(set(alvos) | rotas_sk_alvos)

    dimensoes_validas = _obter_dimensoes_perturbacao()
    dims = [d.strip() for d in dimensions if d.strip()] if dimensions else list(dimensoes_validas)
    for d in dims:
        if d not in dimensoes_validas:
            raise ValueError(f"Dimensao de perturbacao desconhecida: {d!r}.")

    seeds_por_alvo: dict[str, list[Any]] = {}
    for s in seeds_golden:
        rota_s = str(getattr(s, "agent_route", None) or getattr(s, "expected_route", "")).lower()
        if rota_s:
            seeds_por_alvo.setdefault(rota_s, []).append(s)
    for sg in seeds_grafo:
        rota_sg = str(getattr(sg, "expected_route", "")).lower()
        if rota_sg:
            seeds_por_alvo.setdefault(rota_sg, []).append(sg)
    for sw in seeds_wf:
        rota_sw = str(getattr(sw, "expected_route", "")).lower()
        if rota_sw:
            seeds_por_alvo.setdefault(rota_sw, []).append(sw)
    for sk in seeds_skill:
        rota_sk = str(getattr(sk, "expected_route", "")).lower()
        if rota_sk:
            seeds_por_alvo.setdefault(rota_sk, []).append(sk)

    cobertura_atual = repo.cobertura_por_estrato() if not dry_run else {}
    rng = random.Random(rng_seed)

    alocacoes: list[ItemAlocacao] = []
    for alvo in alvos:
        pool_seeds = seeds_por_alvo.get(alvo, [])
        if not pool_seeds:
            continue
        for dim in dims:
            ja_existem = cobertura_atual.get((alvo, dim), 0)
            faltam = max(0, per_stratum - ja_existem)
            for slot_idx in range(faltam):
                seed_escolhida = rng.choice(pool_seeds)
                estrato = Estrato(agente_alvo=alvo, dimensao=dim)
                alocacoes.append(
                    ItemAlocacao(
                        estrato=estrato,
                        seed=seed_escolhida,
                        indice_no_estrato=ja_existem + slot_idx,
                    )
                )

    funnel = _construir_dedup_funnel(
        seeds_golden,
        repo,
        sim_threshold=sim_threshold,
        dry_run=dry_run,
    )

    budget_obj: Budget | None = None
    gerador: GeradorSintetico
    if generator_mode == "sdk":
        if cliente_factory is None:
            raise ValueError("cliente_factory e obrigatorio quando generator_mode='sdk'.")
        budget_obj = Budget(max_premium_requests=int(orc_int or 1))
        cliente_adaptado = _adaptar_cliente_sdk(cliente_factory())
        gerador = GeradorSDK(cliente_adaptado, budget_obj, modelo=modelo)
    else:
        gerador = GeradorTemplate()

    rel_gen = gerar_sinteticos(
        repo=None if dry_run else repo,
        gerador=gerador,
        alocacoes=alocacoes,
        funnel=funnel,
        rng_seed=rng_seed,
        max_attempts=max_attempts,
        dry_run=dry_run,
        generator_mode=generator_mode,
        modelo=modelo,
        params={
            "targets": alvos,
            "dimensions": dims,
            "per_stratum": per_stratum,
            "sim_threshold": sim_threshold,
            "max_attempts": max_attempts,
            "include_security": include_security,
            "graph_seeding": graph_seeding,
            "graph_min_coverage": graph_min_coverage,
            "workflow_seeds": workflow_seeds,
            "skill_seeding": skill_seeding,
            "skills_filtro": list(skills_filtro) if skills_filtro else None,
        },
        golden_path=str(g_path) if g_path.exists() else None,
        budget=budget_obj,
        routing_graph_sha256=getattr(snapshot, "sha256", None) if snapshot is not None else None,
        snapshot_grafo=snapshot,
    )

    n_graph_seeds_used = sum(
        1 for item in alocacoes if getattr(item.seed, "seed_source", None) == "routing_graph"
    )
    n_wf_seeds_used = sum(
        1
        for item in alocacoes
        if getattr(item.seed, "seed_source", None) == "routing_graph"
        and getattr(item.seed, "graph_workflow_id", None) is not None
    )
    n_skill_seeds_used = sum(
        1 for item in alocacoes if getattr(item.seed, "seed_source", None) == "skill_ab"
    )
    premium_usados = (
        int(budget_obj.custo_atual["premium_requests"]) if budget_obj is not None else 0
    )

    exit_code = 1 if rel_gen.status == "failed" else 0
    contadores = {
        "n_candidates": rel_gen.n_candidates,
        "n_rejected_hash": rel_gen.n_rejected_hash,
        "n_rejected_similarity": rel_gen.n_rejected_similarity,
        "n_rejected_override": rel_gen.n_rejected_override,
        "n_accepted": rel_gen.n_accepted,
        "premium_requests_used": premium_usados,
        "n_graph_seeds_generated": len(seeds_grafo),
        "n_graph_seeds_used": n_graph_seeds_used,
        "n_arestas_uncoverable": len(arestas_uncoverable),
        "n_arestas_cobertas_golden": sum(1 for v in cobertura_inicial.values() if v > 0),
        "n_workflow_seeds_generated": len(seeds_wf),
        "n_workflow_seeds_used": n_wf_seeds_used,
        "n_workflows_uncoverable": len(workflows_uncoverable),
        "n_workflows_cobertos_golden": sum(1 for v in cobertura_wf_inicial.values() if v > 0),
        "n_skill_seeds_generated": len(seeds_skill),
        "n_skill_seeds_used": n_skill_seeds_used,
    }
    return RelatorioSynth(
        comando="synth-generate",
        run_id=rel_gen.run_id,
        status=rel_gen.status,
        exit_code=exit_code,
        contadores=contadores,
        motivo=rel_gen.motivo,
    )


def executar_synth_eval(
        *,
        repo: SynthRepository,
        cliente_factory: Callable[[], SdkClientProtocol],
        max_premium_requests: int | str | None,
        router_agent_path: str | Path | None = None,
        routing_graph_path: str | Path | None = None,
        run_id: str | None = None,
        source_run_id: str | None = None,
        pending: bool = False,
        limit: int | None = None,
        modelo: str | None = None,
        repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa synth-eval com orcamento estrito e suporte a retomada idempotente via --run-id (B1 / §4.1 / §7)."""
    orc_int = validar_orcamento_synth("synth-eval", max_premium_requests)
    assert orc_int is not None

    r_path = _resolver_arquivo(router_agent_path, DEFAULT_ROUTER_AGENT_REL_PATH, repo_root)
    router_instructions = r_path.read_text(encoding="utf-8") if r_path.exists() else None
    router_sha = _sha256_arquivo(r_path)

    grafo_path = _resolver_caminho_grafo(routing_graph_path, repo_root=repo_root)
    snapshot: Any | None = (
        _carregar_grafo_routing(grafo_path, repo_root=repo_root)
        if (grafo_path.exists() or routing_graph_path is not None)
        else None
    )

    if run_id is not None:
        existente = repo.obter_run(run_id)
        if existente is None:
            eval_run_id = repo.criar_run(
                kind="eval",
                run_id=run_id,
                parent_run_id=source_run_id,
                status="running",
                model=modelo,
                params={"source_run_id": source_run_id, "pending": pending, "limit": limit},
                router_agent_sha256=router_sha,
                routing_graph_sha256=getattr(snapshot, "sha256", None) if snapshot is not None else None,
            )
        else:
            eval_run_id = run_id
    else:
        eval_run_id = repo.criar_run(
            kind="eval",
            parent_run_id=source_run_id,
            status="running",
            model=modelo,
            params={"source_run_id": source_run_id, "pending": pending, "limit": limit},
            router_agent_sha256=router_sha,
            routing_graph_sha256=getattr(snapshot, "sha256", None) if snapshot is not None else None,
        )

    pendentes = repo.listar_pendentes_avaliacao(
        eval_run_id=eval_run_id,
        source_run_id=source_run_id,
        only_untested_globally=pending,
        limit=limit,
    )

    budget = _BudgetAdapter(max_requests=orc_int)
    cliente_sdk = cliente_factory()

    avaliados = 0
    matched = 0
    mismatched = 0
    unparseable = 0
    erros = 0
    status_final = "completed"
    motivo_final: str | None = None

    for item in pendentes:
        try:
            budget.consumir(1)
        except BudgetExceededError as exc:
            status_final = "neutral" if avaliados == 0 else "completed"
            motivo_final = str(exc)
            break

        res = avaliar_lote_prompts(
            [item],
            cliente_sdk=cliente_sdk,
            router_instructions=router_instructions,
            modelo=modelo,
            snapshot=snapshot,
        )[0]
        repo.inserir_avaliacao(
            run_id=eval_run_id,
            prompt_id=res.prompt_id,
            observed_route=res.observed_route,
            route_source=res.route_source,
            observed_workflow=res.observed_workflow,
            observed_etapa=res.observed_etapa,
            workflow_source=res.workflow_source,
            workflow_route_consistent=res.workflow_route_consistent,
            verdict=res.verdict,
            passed=res.passed,
            response_excerpt=res.response_excerpt,
            latency_ms=res.latency_ms,
            premium_requests=res.premium_requests,
            error=res.error,
        )
        avaliados += 1
        if res.verdict == "matched":
            matched += 1
        elif res.verdict == "mismatched":
            mismatched += 1
        elif res.verdict == "unparseable":
            unparseable += 1
        else:
            erros += 1

    repo.finalizar_run(
        eval_run_id,
        status=status_final,
        motivo=motivo_final,
        premium_requests_used=budget.consumidos,
        n_candidates=avaliados,
        n_accepted=matched,
        router_agent_sha256=router_sha,
    )

    return RelatorioSynth(
        comando="synth-eval",
        run_id=eval_run_id,
        status=status_final,
        exit_code=0,
        contadores={
            "avaliados": avaliados,
            "matched": matched,
            "mismatched": mismatched,
            "unparseable": unparseable,
            "errors": erros,
            "premium_requests_used": budget.consumidos,
        },
        motivo=motivo_final,
    )


def executar_synth_skill_ab(
        *,
        repo: SynthRepository,
        cases_path: str | Path | None = None,
        skills_dir: str | Path | None = None,
        skills_filtro: Sequence[str] | None = None,
        include_gap_seeds: bool = False,
        generator_mode: str = "template",
        max_premium_requests: int | str | None = None,
        cliente_factory: Callable[[], SdkClientProtocol] | None = None,
        modelo: str | None = None,
        run_id: str | None = None,
        repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa avaliacao pareada A/B (baseline vs. treatment) de skills (P5 + synth)."""
    orc_int = validar_orcamento_synth("synth-skill-ab", max_premium_requests, generator_mode)

    c_path = _resolver_arquivo(cases_path, DEFAULT_SKILL_AB_CASES_REL_PATH, repo_root)
    s_dir = _resolver_arquivo(skills_dir, DEFAULT_SKILLS_REL_DIR, repo_root)

    casos: list[dict[str, Any]] = []
    if c_path.exists():
        raw = yaml.safe_load(c_path.read_text(encoding="utf-8")) or {}
        if isinstance(raw, dict) and isinstance(raw.get("cases"), list):
            for c in raw["cases"]:
                if not isinstance(c, dict):
                    continue
                item = dict(c)
                item.setdefault("case_id", item.get("id", ""))
                item.setdefault("skill_name", item.get("skill", ""))
                item.setdefault("baseline_prompt", item.get("baseline_output") or item.get("task", ""))
                casos.append(item)

    filtro_set: frozenset[str] | None = None
    if skills_filtro:
        filtro_set = frozenset(s.strip() for s in skills_filtro if s and s.strip())
        casos = [c for c in casos if str(c.get("skill_name") or "").strip() in filtro_set]

    if include_gap_seeds or not casos:
        fn_seeds_sk = getattr(_seeds_mod, "gerar_seeds_skills", None)
        seeds_gap = (
            tuple(
                _invocar_com_kwargs_aceitos(
                    fn_seeds_sk,
                    modo="gaps" if casos else "all",
                    skills_dir=s_dir,
                    cases_path=c_path,
                    skills_filtro=skills_filtro,
                    repo_root=repo_root,
                )
            )
            if callable(fn_seeds_sk)
            else ()
        )
        for sg in seeds_gap:
            casos.append(
                {
                    "case_id": getattr(sg, "seed_case_id", None) or getattr(sg, "id", ""),
                    "skill_name": getattr(sg, "skill_name", ""),
                    "baseline_prompt": getattr(sg, "baseline_prompt", None) or getattr(sg, "text", ""),
                    "required_clauses": list(getattr(sg, "required_clauses", ()) or ()),
                    "forbidden_antipatterns": list(getattr(sg, "forbidden_antipatterns", ()) or ()),
                    "min_delta_utility": float(getattr(sg, "min_delta_utility", 0.05) or 0.05),
                }
            )

    if run_id is not None and repo.obter_run(run_id) is not None:
        ab_run_id = run_id
    else:
        ab_run_id = repo.criar_run(
            kind="skill_ab",
            run_id=run_id,
            status="running",
            generator=generator_mode,
            model=modelo,
            params={
                "cases_path": str(c_path),
                "skills_filtro": sorted(filtro_set) if filtro_set else None,
                "include_gap_seeds": include_gap_seeds,
                "n_cases_planned": len(casos),
            },
        )

    cliente_sdk: SdkClientProtocol | None = None
    budget: _BudgetAdapter | None = None
    if generator_mode == "sdk":
        if cliente_factory is None:
            raise ValueError("cliente_factory e obrigatorio quando generator_mode='sdk'.")
        cliente_sdk = cliente_factory()
        budget = _BudgetAdapter(max_requests=int(orc_int or 1))

    def _consumir_budget(qtd: int) -> None:
        if budget is not None:
            budget.consumir(qtd)

    status_final = "completed"
    motivo_final: str | None = None
    casos_executados = list(casos)
    if budget is not None:
        max_casos_orcamento = max(0, budget.max_requests // 2)
        if max_casos_orcamento < len(casos_executados):
            casos_executados = casos_executados[:max_casos_orcamento]
            status_final = "neutral" if max_casos_orcamento == 0 else "completed"
            motivo_final = (
                f"Orcamento de {budget.max_requests} premium requests limita execucao a "
                f"{max_casos_orcamento} casos pareados (2 requests/caso)."
            )

    rel_ab = avaliar_lote_skill_ab(
        casos_executados,
        skills_dir=s_dir,
        cliente_sdk=cliente_sdk,
        modelo=modelo,
        budget_callback=_consumir_budget,
    )

    for r in rel_ab.resultados:
        repo.inserir_avaliacao_skill_ab(
            run_id=ab_run_id,
            case_id=r.case_id,
            skill_name=r.skill_name,
            skill_sha256=r.skill_sha256,
            mode=r.mode,
            baseline_score=r.baseline_score,
            treatment_score=r.treatment_score,
            delta_utility=r.delta_utility,
            min_delta_utility=r.min_delta_utility,
            redundant=r.redundant,
            passed=r.passed,
            missing_clauses=r.missing_clauses,
            triggered_antipatterns=r.triggered_antipatterns,
            latency_ms=r.latency_ms,
            premium_requests=r.premium_requests,
        )

    premium_usados = budget.consumidos if budget is not None else rel_ab.premium_requests_used
    repo.finalizar_run(
        ab_run_id,
        status=status_final,
        motivo=motivo_final,
        premium_requests_used=premium_usados,
        n_candidates=rel_ab.total_cases,
        n_accepted=rel_ab.passed_cases,
    )

    return RelatorioSynth(
        comando="synth-skill-ab",
        run_id=ab_run_id,
        status=status_final,
        exit_code=0,
        contadores={
            "total_cases": rel_ab.total_cases,
            "passed_cases": rel_ab.passed_cases,
            "redundant_cases": rel_ab.redundant_cases,
            "premium_requests_used": premium_usados,
        },
        motivo=motivo_final,
        mean_skill_delta_utility=rel_ab.mean_delta_utility,
    )


def executar_synth_export(
        *,
        repo: SynthRepository,
        eval_run_id: str,
        silver_dir: str | Path | None = None,
        only_failures: bool = True,
        include_near_boundary: bool = False,
        repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa synth-export gravando exclusivamente em .cache/synth_silver/ (B1 / §4.1)."""
    s_dir = _resolver_arquivo(silver_dir, DEFAULT_SILVER_REL_DIR, repo_root)
    export_run_id = repo.criar_run(
        kind="export",
        parent_run_id=eval_run_id,
        status="running",
        params={"only_failures": only_failures, "include_near_boundary": include_near_boundary},
    )
    exp_mod = _importar_primeiro_modulo(
        (
            "governance_runner.synth.exporter",
            "governance_runner.synth.silver_exporter",
            "governance_runner.synth.export",
        )
    )
    fn_export = _resolver_callable_modulo(
        exp_mod,
        ("export_eval_run", "exportar_eval_run", "exportar_silver", "export_silver"),
        prefixos=("export",),
    )
    res = _invocar_com_kwargs_aceitos(
        fn_export,
        repo,
        eval_run_id,
        silver_dir=s_dir,
        out_dir=s_dir,
        only_failures=only_failures,
        include_near_boundary=include_near_boundary,
        repo_root=repo_root,
    )
    exportados = int(getattr(res, "exportados", 0) or 0)
    ignorados = int(getattr(res, "ignorados_duplicados", 0) or 0)
    arq_yaml = getattr(res, "arquivo_yaml", None) or getattr(res, "yaml_path", None)
    repo.finalizar_run(
        export_run_id,
        status="completed",
        n_candidates=exportados,
        n_accepted=exportados,
    )
    caminhos = (str(arq_yaml),) if arq_yaml is not None else ()
    return RelatorioSynth(
        comando="synth-export",
        run_id=export_run_id,
        status="completed",
        exit_code=0,
        contadores={"exportados": exportados, "ignorados_duplicados": ignorados},
        caminhos_gerados=caminhos,
    )


def executar_synth_promote(
        *,
        repo: SynthRepository | None = None,
        silver: str | Path,
        run_id: str,
        suite: str = "regressao",
        out: str | Path | None = None,
        stdout: bool = False,
        confirm: bool = False,
        repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa synth-promote em modo preview por padrao e promove apenas com --confirm + --out (B1 / §4.1)."""
    out_path = _resolver_arquivo(out, DEFAULT_GOLDEN_REGRESSAO_REL_PATH, repo_root) if out is not None else None
    prom_mod = _importar_primeiro_modulo(
        (
            "governance_runner.synth.promoter",
            "governance_runner.synth.silver_promoter",
            "governance_runner.synth.promote",
        )
    )
    fn_promote = _resolver_callable_modulo(
        prom_mod,
        ("promote_silver_cases", "promover_casos_silver", "promover_silver", "promote_cases"),
        prefixos=("promot", "promov"),
    )
    res = _invocar_com_kwargs_aceitos(
        fn_promote,
        silver,
        run_id=run_id,
        suite=suite,
        out_path=out_path,
        out=out_path,
        stdout=stdout,
        confirm=confirm,
        repo=repo,
        repo_root=repo_root,
    )
    arq_dest = getattr(res, "arquivo_destino", None) or getattr(res, "out_path", None)
    modo_res = str(getattr(res, "modo", None) or ("promoted" if confirm else "preview"))
    selecionados = int(getattr(res, "selecionados", 0) or 0)
    promovidos = int(getattr(res, "promovidos", 0) or 0)
    preview_txt = getattr(res, "yaml_preview", None)
    caminhos = (str(arq_dest),) if arq_dest is not None else ()
    return RelatorioSynth(
        comando="synth-promote",
        run_id=run_id,
        status=modo_res,
        exit_code=0,
        contadores={"selecionados": selecionados, "promovidos": promovidos},
        caminhos_gerados=caminhos,
        motivo=preview_txt if stdout else None,
    )


def executar_synth_diagnose(
        *,
        repo: SynthRepository,
        eval_run_id: str,
        skill_ab_run_id: str | None = None,
        routing_graph_path: str | Path | None = None,
        router_agent_path: str | Path | None = None,
        golden_path: str | Path | None = None,
        skills_dir: str | Path | None = None,
        skill_cases_path: str | Path | None = None,
        min_support: int = 2,
        out_dir: str | Path | None = None,
        formato: str = "both",
        allow_root: bool = False,
        repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa synth-diagnose cruzando synth-eval, grafo, router.md e telemetria A/B de skills (B2 / §5 / §7 / P5)."""
    if formato not in ("yaml", "md", "both"):
        raise ValueError(f"Formato invalido para synth-diagnose: {formato!r}. Esperado yaml|md|both.")

    grafo_path = _resolver_caminho_grafo(routing_graph_path, repo_root=repo_root)
    snapshot = _carregar_grafo_routing(grafo_path, repo_root=repo_root)
    r_path = _resolver_arquivo(router_agent_path, DEFAULT_ROUTER_AGENT_REL_PATH, repo_root)
    g_path = _resolver_arquivo(golden_path, DEFAULT_GOLDEN_REL_PATH, repo_root)
    s_dir = _resolver_arquivo(skills_dir, DEFAULT_SKILLS_REL_DIR, repo_root)
    sc_path = _resolver_arquivo(skill_cases_path, DEFAULT_SKILL_AB_CASES_REL_PATH, repo_root)
    destino = (
        _resolver_arquivo(out_dir, DEFAULT_DIAGNOSTICS_REL_DIR, repo_root)
        if out_dir is not None
        else None
    )

    golden_seeds = _carregar_golden_set(g_path, permitir_ausente=True)
    router_md_texto = r_path.read_text(encoding="utf-8") if r_path.exists() else ""
    router_sha = _sha256_arquivo(r_path) or ""
    golden_sha = _sha256_arquivo(g_path) or ""

    run_info = repo.obter_run(eval_run_id)
    avaliacoes = repo.listar_avaliacoes(eval_run_id) if run_info is not None else []

    resolved_skill_ab_run_id = skill_ab_run_id
    if resolved_skill_ab_run_id is None and hasattr(repo, "obter_ultimo_run_id"):
        resolved_skill_ab_run_id = repo.obter_ultimo_run_id(kind="skill_ab", status="completed")

    skill_ab_evals: list[dict[str, Any]] = []
    if resolved_skill_ab_run_id is not None and hasattr(repo, "listar_avaliacoes_skill_ab"):
        skill_ab_evals = repo.listar_avaliacoes_skill_ab(run_id=resolved_skill_ab_run_id)

    skills_cobertura: dict[str, int] = {}
    skills_uncoverable: tuple[str, ...] = ()
    if s_dir.exists():
        fn_cob_sk = getattr(_seeds_mod, "calcular_cobertura_skills", None)
        if callable(fn_cob_sk):
            skills_cobertura = dict(
                _invocar_com_kwargs_aceitos(
                    fn_cob_sk,
                    skills_dir=s_dir,
                    cases_path=sc_path,
                    repo_root=repo_root,
                )
            )
        fn_uncov_sk = getattr(_seeds_mod, "identificar_skills_uncoverable", None)
        if callable(fn_uncov_sk):
            skills_uncoverable = tuple(
                _invocar_com_kwargs_aceitos(
                    fn_uncov_sk,
                    skills_dir=s_dir,
                    repo_root=repo_root,
                )
            )

    diag_mod = _importar_primeiro_modulo(
        (
            "governance_runner.synth.diagnostics",
            "governance_runner.synth.diagnostic",
        )
    )
    diag_exp_mod = _importar_primeiro_modulo(
        ("governance_runner.synth.diagnostic_exporter",)
    )

    fn_diag = _resolver_callable_modulo(
        diag_mod,
        (
            "diagnosticar_avaliacao",
            "executar_diagnostico",
            "diagnosticar_eval_run",
            "gerar_diagnostico",
            "diagnosticar_run",
            "diagnosticar",
        ),
        prefixos=("diag", "gerar_diag", "executar_diag"),
    )
    res_diag = _invocar_com_kwargs_aceitos(
        fn_diag,
        eval_run_id=eval_run_id,
        run_info=run_info,
        avaliacoes=avaliacoes,
        snapshot=snapshot,
        router_md_texto=router_md_texto,
        router_agent_sha256=router_sha,
        golden_seeds=golden_seeds,
        golden_set_sha256=golden_sha,
        min_support=min_support,
        skill_ab_evals=skill_ab_evals,
        skill_ab_run_id=resolved_skill_ab_run_id,
        skills_cobertura=skills_cobertura,
        skills_uncoverable=skills_uncoverable,
    )

    res_export = diag_exp_mod.exportar_diagnostico(
        res_diag,
        out_dir=destino,
        formato=formato,
        allow_root=allow_root,
        repo_root=repo_root,
    )

    caminhos_gerados: list[Path] = []
    if res_export.yaml_path is not None:
        caminhos_gerados.append(res_export.yaml_path)
    if res_export.md_path is not None:
        caminhos_gerados.append(res_export.md_path)

    yaml_str = str(res_export.yaml_path) if res_export.yaml_path is not None else None
    md_str = str(res_export.md_path) if res_export.md_path is not None else None

    diag_id = str(getattr(res_diag, "diagnostic_id", f"diag-{eval_run_id}"))
    created_at = str(getattr(res_diag, "finished_at", None) or getattr(res_diag, "created_at", ""))
    sugestoes = tuple(getattr(res_diag, "sugestoes", None) or getattr(res_diag, "suggestions", None) or ())
    orfas = getattr(res_diag, "orfas", None)
    arestas_mortas = tuple(
        getattr(orfas, "sem_avaliacao", None) or getattr(res_diag, "dead_edges", None) or ()
    )
    arestas_uncov = tuple(
        getattr(orfas, "uncoverable", None) or getattr(res_diag, "uncoverable_edges", None) or ()
    )
    por_wf = tuple(getattr(res_diag, "por_workflow", None) or ())
    wf_mortos = tuple(m.workflow_id for m in por_wf if int(getattr(m, "suporte", 0)) == 0)
    wf_uncov = tuple(
        _invocar_com_kwargs_aceitos(
            getattr(_seeds_mod, "identificar_workflows_uncoverable", lambda _: ()),
            snapshot,
        )
    )
    wf_inconsist = tuple(s for s in sugestoes if getattr(s, "codigo", "") == "SUG-WF-INCONSISTENT-ROUTE")
    skills_orfas_obj = getattr(res_diag, "skills_orfas", None)
    skills_sem_cov = tuple(getattr(skills_orfas_obj, "sem_cobertura_ab", None) or ())
    resumo_obj = getattr(res_diag, "resumo", None)
    n_skills_red = int(getattr(resumo_obj, "skills_redundantes", 0) or 0)
    mean_skill_delta = getattr(resumo_obj, "mean_skill_delta_utility", None)

    metrics_dict = (
        diag_exp_mod.serializar_diagnostico_dict(res_diag)
        if hasattr(res_diag, "resumo")
        else dict(getattr(res_diag, "metrics", None) or {})
    )

    repo.inserir_diagnostico(
        diagnostic_id=diag_id,
        eval_run_id=eval_run_id,
        routing_graph_sha256=getattr(snapshot, "sha256", ""),
        router_agent_sha256=router_sha or None,
        golden_set_sha256=golden_sha or None,
        created_at=created_at,
        yaml_path=yaml_str,
        md_path=md_str,
        metrics=metrics_dict,
        n_suggestions=len(sugestoes),
    )

    return RelatorioSynth(
        comando="synth-diagnose",
        run_id=diag_id,
        status="completed",
        exit_code=0,
        contadores={
            "n_sugestoes": len(sugestoes),
            "n_arestas_mortas": len(arestas_mortas),
            "n_arestas_uncoverable": len(arestas_uncov),
            "n_workflows_mortos": len(wf_mortos),
            "n_workflows_uncoverable": len(wf_uncov),
            "n_workflow_route_inconsistencies": len(wf_inconsist),
            "n_skills_redundantes": n_skills_red,
            "n_skills_sem_cobertura": len(skills_sem_cov),
        },
        caminhos_gerados=tuple(str(p) for p in caminhos_gerados),
        mean_skill_delta_utility=mean_skill_delta,
    )
