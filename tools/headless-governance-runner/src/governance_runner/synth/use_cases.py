"""use_cases — Casos de uso synth-generate / synth-eval / synth-export / synth-promote / synth-diagnose (B2-05 / B2-02 / B3-03)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from governance_runner.runner.budget import GOV_MAX_PREMIUM_REQUESTS_ENV, Budget
from governance_runner.runner.sdk_adapter import CopilotSDKClient
from governance_runner.synth.dedup import DEFAULT_SIM_THRESHOLD, DedupFunnel
from governance_runner.synth.diagnostic_exporter import (
    FormatoDiagnostico,
    exportar_diagnostico,
    serializar_diagnostico_dict,
)
from governance_runner.synth.diagnostics import diagnosticar_avaliacao
from governance_runner.synth.evaluator import avaliar_lote, carregar_router_agent
from governance_runner.synth.exporter import exportar_silver, promover_silver
from governance_runner.synth.generator import (
    DEFAULT_MAX_ATTEMPTS,
    GeradorSDK,
    GeradorSintetico,
    GeradorTemplate,
    gerar_sinteticos,
)
from governance_runner.synth.golden import (
    GoldenSeed,
    calcular_sha256_golden,
    carregar_seeds_golden,
)
from governance_runner.synth.routing_graph import (
    GrafoSnapshot,
    carregar_snapshot_grafo,
)
from governance_runner.synth.seeds import (
    MODOS_GRAPH_SEEDING,
    ModoGraphSeeding,
    SeedLike,
    calcular_cobertura_golden,
    enriquecer_seeds_golden,
    gerar_seeds_grafo,
)
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.taxonomy import alocar_estratos

__all__ = [
    "EXIT_ORCAMENTO_INVALIDO",
    "SynthOrcamentoInvalidoError",
    "RelatorioSynth",
    "validar_orcamento_synth",
    "executar_synth_generate",
    "executar_synth_eval",
    "executar_synth_export",
    "executar_synth_promote",
    "executar_synth_diagnose",
]

EXIT_ORCAMENTO_INVALIDO = 2
MODOS_GERADOR = ("sdk", "template")


class SynthOrcamentoInvalidoError(ValueError):
    """Orcamento ausente/invalido; a CLI deve sair com exit code 2."""

    exit_code = EXIT_ORCAMENTO_INVALIDO


@dataclass
class RelatorioSynth:
    comando: str
    run_id: str | None = None
    status: str = "completed"
    motivo: str | None = None
    contadores: dict[str, int] = field(default_factory=dict)
    exit_code: int = 0


def validar_orcamento_synth(
    comando: str,
    max_premium_requests: int | str | None = None,
    generator_mode: str | None = None,
    env: Mapping[str, str] | None = None,
) -> int | None:
    """Fail-fast: valida o orcamento ANTES de qualquer chamada/token SDK."""
    ambiente = os.environ if env is None else env
    if comando not in ("synth-eval", "synth-generate"):
        raise SynthOrcamentoInvalidoError(f"comando desconhecido: {comando}")
    if comando == "synth-generate" and generator_mode not in MODOS_GERADOR:
        raise SynthOrcamentoInvalidoError(f"--generator-mode invalido: {generator_mode!r}")
    exige = comando == "synth-eval" or generator_mode == "sdk"
    bruto: int | str | None = max_premium_requests
    if bruto is None:
        bruto = ambiente.get(GOV_MAX_PREMIUM_REQUESTS_ENV)
    if bruto is None or (isinstance(bruto, str) and not bruto.strip()):
        if exige:
            raise SynthOrcamentoInvalidoError(
                "--max-premium-requests (ou GOV_MAX_PREMIUM_REQUESTS) obrigatorio e > 0"
            )
        return None
    try:
        valor = int(bruto)
    except (TypeError, ValueError) as exc:
        if exige:
            raise SynthOrcamentoInvalidoError(f"orcamento nao numerico: {bruto!r}") from exc
        return None
    if valor <= 0:
        if exige:
            raise SynthOrcamentoInvalidoError(f"orcamento deve ser > 0, recebido {valor}")
        return None
    return valor


def executar_synth_generate(
    *,
    repo: SynthRepository,
    generator_mode: str = "template",
    max_premium_requests: int | str | None = None,
    cliente_factory: Callable[[], CopilotSDKClient] | None = None,
    targets: Sequence[str] | None = None,
    dimensions: Sequence[str] | None = None,
    per_stratum: int = 2,
    rng_seed: int = 42,
    sim_threshold: float = DEFAULT_SIM_THRESHOLD,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    include_security: bool = False,
    dry_run: bool = False,
    modelo: str | None = None,
    routing_graph_path: str | Path | None = None,
    graph_seeding: ModoGraphSeeding = "off",
    graph_min_coverage: int = 3,
    repo_root: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> RelatorioSynth:
    if graph_seeding not in MODOS_GRAPH_SEEDING:
        raise ValueError(f"--graph-seeding invalido: {graph_seeding!r}. Esperado um de {MODOS_GRAPH_SEEDING}.")
    teto = validar_orcamento_synth("synth-generate", max_premium_requests, generator_mode, env)

    snapshot: GrafoSnapshot | None = None
    if routing_graph_path is not None or graph_seeding != "off":
        snapshot = carregar_snapshot_grafo(routing_graph_path, repo_root=repo_root)
    else:
        try:
            snapshot = carregar_snapshot_grafo(None, repo_root=repo_root)
        except Exception:  # noqa: BLE001 - best-effort quando --routing-graph nao foi informado em modo off
            snapshot = None

    seeds_golden = carregar_seeds_golden(repo_root=repo_root, targets=targets, include_security=include_security)
    if snapshot is not None:
        seeds_golden = enriquecer_seeds_golden(seeds_golden, snapshot)

    seeds_totais: list[GoldenSeed | SeedLike] = list(seeds_golden)
    n_graph_seeds = 0
    if graph_seeding != "off" and snapshot is not None:
        todas_golden = carregar_seeds_golden(repo_root=repo_root, include_security=include_security)
        cov_golden = calcular_cobertura_golden(todas_golden, snapshot)
        seeds_grafo = gerar_seeds_grafo(
            snapshot,
            cov_golden,
            min_cobertura=graph_min_coverage,
            modo=graph_seeding,
            rng_seed=rng_seed,
            targets=targets,
        )
        n_graph_seeds = len(seeds_grafo)
        seeds_totais.extend(seeds_grafo)

    alocacoes = alocar_estratos(
        seeds_totais,
        per_stratum=per_stratum,
        targets=targets,
        dimensions=dimensions,
        cobertura_historica=repo.cobertura_por_estrato(),
        rng_seed=rng_seed,
    )
    funnel = DedupFunnel(
        sim_threshold=sim_threshold,
        documentos_iniciais=[(f"golden:{s.id}", s.prompt) for s in seeds_golden]
        + [(p["prompt_id"], p["text"]) for p in repo.listar_prompts()],
    )
    budget: Budget | None = None
    gerador: GeradorSintetico
    if generator_mode == "sdk":
        if cliente_factory is None or teto is None:
            raise SynthOrcamentoInvalidoError("modo sdk requer cliente e orcamento")
        budget = Budget(max_premium_requests=teto)
        gerador = GeradorSDK(cliente_factory(), budget, modelo=modelo)
    else:
        gerador = GeradorTemplate()
    params: dict[str, Any] = {
        "per_stratum": per_stratum,
        "targets": list(targets or []),
        "dimensions": list(dimensions or []),
        "sim_threshold": sim_threshold,
        "max_attempts": max_attempts,
        "graph_seeding": graph_seeding,
        "graph_min_coverage": graph_min_coverage,
    }
    rel = gerar_sinteticos(
        repo=repo,
        gerador=gerador,
        alocacoes=alocacoes,
        funnel=funnel,
        rng_seed=rng_seed,
        max_attempts=max_attempts,
        dry_run=dry_run,
        generator_mode=generator_mode,
        modelo=modelo,
        params=params,
        budget=budget,
        routing_graph_sha256=snapshot.sha256 if snapshot is not None else None,
        snapshot_grafo=snapshot,
    )
    return RelatorioSynth(
        comando="synth-generate",
        run_id=rel.run_id,
        status=rel.status,
        motivo=rel.motivo,
        contadores={
            "n_candidates": rel.n_candidates,
            "n_accepted": rel.n_accepted,
            "n_rejected_hash": rel.n_rejected_hash,
            "n_rejected_similarity": rel.n_rejected_similarity,
            "n_rejected_override": rel.n_rejected_override,
            "n_graph_seeds": n_graph_seeds,
        },
    )


def executar_synth_eval(
    *,
    repo: SynthRepository,
    cliente_factory: Callable[[], CopilotSDKClient],
    max_premium_requests: int | str | None = None,
    router_agent_path: str | Path | None = None,
    run_id: str | None = None,
    source_run_id: str | None = None,
    pending: bool = False,
    limit: int | None = None,
    modelo: str | None = None,
    repo_root: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> RelatorioSynth:
    teto = validar_orcamento_synth("synth-eval", max_premium_requests, None, env)
    assert teto is not None
    cliente = cliente_factory()  # somente APOS validar o orcamento
    rel = avaliar_lote(
        repo=repo,
        cliente=cliente,
        budget_lote=Budget(max_premium_requests=teto),
        router_agent_path=router_agent_path,
        repo_root=repo_root,
        run_id=run_id,
        source_run_id=source_run_id,
        pending=pending,
        limit=limit,
        modelo=modelo,
    )
    return RelatorioSynth(
        comando="synth-eval",
        run_id=rel.run_id,
        status=rel.status,
        motivo=rel.motivo,
        contadores={
            "n_avaliados": rel.n_avaliados,
            "n_passed": rel.n_passed,
            "n_unparseable": rel.n_unparseable,
            "n_errors": rel.n_errors,
            "premium_requests_used": rel.premium_requests_used,
        },
    )


def executar_synth_export(
    *,
    repo: SynthRepository,
    eval_run_id: str,
    only_failures: bool = True,
    include_near_boundary: bool = False,
    allow_root: Path | None = None,
) -> RelatorioSynth:
    res = exportar_silver(
        repo=repo,
        eval_run_id=eval_run_id,
        only_failures=only_failures,
        include_near_boundary=include_near_boundary,
        allow_root=allow_root,
    )
    return RelatorioSynth(
        comando="synth-export",
        run_id=eval_run_id,
        motivo=str(res.path),
        contadores={"n_exportados": res.n_itens},
    )


def executar_synth_promote(
    *,
    repo: SynthRepository | None,
    silver: str | Path,
    run_id: str,
    suite: str = "regressao",
    out: str | Path | None = None,
    stdout: bool = False,
    confirm: bool = False,
    allow_root: Path | None = None,
    repo_root: Path | None = None,
) -> RelatorioSynth:
    res = promover_silver(
        repo=repo,
        silver=silver,
        run_id=run_id,
        suite=suite,
        out=out,
        stdout=stdout,
        confirm=confirm,
        allow_root=allow_root,
        repo_root=repo_root,
    )
    return RelatorioSynth(
        comando="synth-promote",
        run_id=run_id,
        status="completed" if (res.gravado or not confirm) else "neutral",
        motivo=str(res.path),
        contadores={"n_promovidos": res.n_promovidos, "n_duplicados": res.n_duplicados},
    )


def executar_synth_diagnose(
    *,
    repo: SynthRepository,
    eval_run_id: str,
    routing_graph_path: str | Path | None = None,
    router_agent_path: str | Path | None = None,
    golden_path: str | Path | None = None,
    min_support: int = 2,
    out_dir: str | Path | None = None,
    formato: FormatoDiagnostico = "both",
    allow_root: bool | Path | str = False,
    repo_root: Path | None = None,
) -> RelatorioSynth:
    """Executa o diagnostico offline deterministico (zero chamadas LLM/SDK) sobre um eval_run_id."""
    snapshot = carregar_snapshot_grafo(routing_graph_path, repo_root=repo_root)
    repo.registrar_arestas_grafo(snapshot)

    run_info = repo.obter_run(eval_run_id)
    avaliacoes = repo.listar_avaliacoes(eval_run_id)

    router_texto, router_sha = carregar_router_agent(router_agent_path, repo_root=repo_root)
    try:
        golden_seeds = carregar_seeds_golden(golden_path, repo_root=repo_root, include_security=True)
        golden_sha = calcular_sha256_golden(golden_path, repo_root=repo_root)
    except Exception:  # noqa: BLE001 - best-effort em ambientes isolados de teste
        golden_seeds = ()
        golden_sha = str((run_info or {}).get("golden_set_sha256") or "")

    diag = diagnosticar_avaliacao(
        eval_run_id=eval_run_id,
        run_info=run_info,
        avaliacoes=avaliacoes,
        snapshot=snapshot,
        router_md_texto=router_texto,
        router_agent_sha256=router_sha,
        golden_seeds=golden_seeds,
        golden_set_sha256=golden_sha,
        min_support=min_support,
    )

    res_exp = exportar_diagnostico(
        diag,
        out_dir=out_dir,
        formato=formato,
        repo_root=repo_root,
        allow_root=allow_root,
    )

    repo.inserir_diagnostico(
        diagnostic_id=diag.diagnostic_id,
        eval_run_id=eval_run_id,
        routing_graph_sha256=diag.hashes.routing_graph_sha256,
        router_agent_sha256=diag.hashes.router_agent_sha256,
        golden_set_sha256=diag.hashes.golden_set_sha256,
        created_at=diag.finished_at,
        yaml_path=str(res_exp.yaml_path) if res_exp.yaml_path else None,
        md_path=str(res_exp.md_path) if res_exp.md_path else None,
        metrics=serializar_diagnostico_dict(diag)["resumo"],
        n_suggestions=len(diag.sugestoes),
    )

    motivo_path = str(res_exp.yaml_path or res_exp.md_path or "")
    return RelatorioSynth(
        comando="synth-diagnose",
        run_id=eval_run_id,
        status="completed",
        motivo=motivo_path,
        contadores={
            "total_avaliacoes": diag.resumo.total_avaliacoes,
            "n_suggestions": len(diag.sugestoes),
            "n_colisoes": len(diag.colisoes),
        },
    )
