"""
cli — Entrypoint `governance-runner` do runner headless (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.3).

Uso:
    governance-runner --use-case agent-audit --base <ref> --report checks,pr-comment
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from governance_runner.reporters.checks import publicar_check
from governance_runner.reporters.pr_comment import publicar_comentario_sticky
from governance_runner.routing.graph_loader import GraphValidationError, carregar_grafo
from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import criar_cliente_sdk_real
from governance_runner.runner.use_cases import executar_agent_audit

__all__ = ["main", "construir_parser", "COPILOT_SDK_TOKEN_ENV"]

COPILOT_SDK_TOKEN_ENV = "COPILOT_SDK_TOKEN"

_USE_CASES_SUPORTADOS = (
    "agent-audit",
    "synth-generate",
    "synth-eval",
    "synth-export",
    "synth-promote",
    "synth-diagnose",
    "synth-skill-ab",
)

_SCHEMA_PADRAO = Path(__file__).parent / "routing" / "routing-graph.schema.json"
_GRAFO_PADRAO = Path(__file__).parents[4] / ".github" / "agents" / "routing-graph.yaml"


def construir_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos do entrypoint `governance-runner`."""
    parser = argparse.ArgumentParser(prog="governance-runner")
    parser.add_argument(
        "--use-case",
        required=True,
        choices=_USE_CASES_SUPORTADOS,
        help="Caso de uso do runner headless a executar.",
    )
    parser.add_argument("--base", default=None, help="Ref git base (obrigatorio apenas em agent-audit).")
    parser.add_argument(
        "--report",
        default="checks",
        help="Canais de relatorio separados por virgula (ex.: checks,pr-comment).",
    )
    parser.add_argument(
        "--diff-file",
        default=None,
        help=(
            "Caminho para um arquivo texto com a lista de arquivos alterados "
            "(um por linha). Se omitido, nenhum filtro de escopo por diff e aplicado."
        ),
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="Repositorio 'owner/nome' para publicacao no Checks API (default: $GITHUB_REPOSITORY).",
    )
    parser.add_argument(
        "--sha",
        default=os.environ.get("GITHUB_SHA"),
        help="SHA do commit alvo do Checks API (default: $GITHUB_SHA).",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        default=None,
        help="Numero do PR para publicacao do comentario sticky (canal 'pr-comment').",
    )
    sg = parser.add_argument_group("synth-*")
    sg.add_argument("--db", default=None, help="Caminho do SQLite synth (default: $GOV_SYNTH_DB).")
    sg.add_argument(
        "--generator-mode",
        "--generator",
        dest="generator_mode",
        choices=("sdk", "template"),
        default="template",
    )
    sg.add_argument("--max-premium-requests", default=None, help="Orcamento (obrigatorio em synth-eval e modo sdk).")
    sg.add_argument("--targets", default=None, help="Agentes alvo separados por virgula.")
    sg.add_argument("--dimensions", default=None, help="Dimensoes de perturbacao separadas por virgula.")
    sg.add_argument("--per-stratum", type=int, default=2)
    sg.add_argument("--rng-seed", type=int, default=42)
    sg.add_argument("--sim-threshold", type=float, default=0.85)
    sg.add_argument("--max-attempts", type=int, default=3)
    sg.add_argument("--include-security", action="store_true")
    sg.add_argument("--dry-run", action="store_true")
    sg.add_argument("--model", default=None)
    sg.add_argument("--router-agent", default=None)
    sg.add_argument("--routing-graph", default=None, help="Caminho para routing-graph.yaml (default: .github/agents/routing-graph.yaml).")
    sg.add_argument("--graph-seeding", choices=("off", "gaps", "all"), default="off", help="Modo de expansao via grafo (default: off).")
    sg.add_argument("--workflow-seeds", choices=("off", "gaps", "all"), default="off", help="Modo de geracao de seeds por gatilho de workflow (default: off).")
    sg.add_argument("--skill-seeding", choices=("off", "gaps", "all"), default="off", help="Modo de geracao de seeds pareadas A/B de skills (default: off).")
    sg.add_argument("--skills", default=None, help="Nomes de skills separados por virgula para filtro em synth-generate/synth-skill-ab.")
    sg.add_argument("--skill-cases", default=None, help="Caminho para YAML de casos A/B de skills (default: tests/evals/skill_ab_cases.yaml).")
    sg.add_argument("--include-skill-gaps", action="store_true", help="Inclui skills sem casos manuais via extracao de SKILL.md em synth-skill-ab.")
    sg.add_argument("--skill-ab-run-id", default=None, help="ID de run synth-skill-ab a cruzar no synth-diagnose (default: ultimo run completed).")
    sg.add_argument("--graph-min-coverage", type=int, default=3, help="Cobertura minima por aresta em --graph-seeding gaps|all (default: 3).")
    sg.add_argument("--run-id", default=None, help="eval: id do run; promote: id do arquivo promoted-<run_id>.yaml.")
    sg.add_argument("--source-run-id", default=None)
    sg.add_argument("--pending", action="store_true")
    sg.add_argument("--limit", type=int, default=None)
    sg.add_argument("--eval-run-id", default=None)
    sg.add_argument("--only-failures", action=argparse.BooleanOptionalAction, default=True)
    sg.add_argument("--include-near-boundary", action="store_true")
    sg.add_argument("--silver", default=None)
    sg.add_argument("--out", "--out-dir", dest="out", default=None)
    sg.add_argument("--min-support", type=int, default=2, help="Suporte minimo para sugestao de desambiguacao (default: 2).")
    sg.add_argument("--format", dest="format", choices=("yaml", "md", "both"), default="both")
    sg.add_argument("--allow-root", action="store_true", help="Permite escrita sob repo_root (respeitando denylist imutavel).")
    sg.add_argument("--stdout", action="store_true")
    sg.add_argument("--confirm", action="store_true")
    sg.add_argument("--suite", default="regressao")
    return parser


def _ler_arquivos_diff(caminho: str | None) -> tuple[str, ...]:
    if not caminho:
        return ()
    return tuple(
        linha.strip()
        for linha in Path(caminho).read_text(encoding="utf-8").splitlines()
        if linha.strip()
    )


def _publicar_relatorio(
        relatorio: object,
        *,
        canais: str,
        repo: str | None,
        sha: str | None,
        pr_number: int | None,
) -> None:
    canais_solicitados = {c.strip() for c in canais.split(",") if c.strip()}

    if "checks" in canais_solicitados:
        if not repo or not sha:
            print(
                "AVISO [governance-runner]: --repo/--sha ausentes; canal 'checks' ignorado.",
                file=sys.stderr,
            )
        else:
            try:
                publicar_check(relatorio, repo=repo, sha=sha)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                print(f"AVISO [governance-runner]: falha ao publicar Checks API: {exc}", file=sys.stderr)

    if "pr-comment" in canais_solicitados:
        if pr_number is None:
            print(
                "AVISO [governance-runner]: --pr-number ausente; canal 'pr-comment' ignorado.",
                file=sys.stderr,
            )
        else:
            try:
                publicar_comentario_sticky(relatorio, pr_number=pr_number)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                print(f"AVISO [governance-runner]: falha ao publicar comentario de PR: {exc}", file=sys.stderr)


def _csv(valor: str | None) -> list[str] | None:
    return [v.strip() for v in valor.split(",") if v.strip()] if valor else None


def _executar_synth(args: argparse.Namespace) -> int:
    from governance_runner.synth.diagnostic_exporter import SynthDiagnosticPathError
    from governance_runner.synth.diagnostics import SynthEvalRunInvalidoError
    from governance_runner.synth.exporter import SynthExportPathError
    from governance_runner.synth.routing_graph import (
        EXIT_ROUTING_GRAPH_INVALIDO,
        RoutingGraphPathError,
    )
    from governance_runner.synth.storage import SynthRepository, resolver_caminho_db
    from governance_runner.synth.use_cases import (
        SynthOrcamentoInvalidoError,
        executar_synth_diagnose,
        executar_synth_eval,
        executar_synth_export,
        executar_synth_generate,
        executar_synth_promote,
        executar_synth_skill_ab,
        validar_orcamento_synth,
    )

    uc = args.use_case
    try:
        if uc == "synth-eval":
            validar_orcamento_synth(uc, args.max_premium_requests)
        elif uc in ("synth-generate", "synth-skill-ab"):
            validar_orcamento_synth(uc, args.max_premium_requests, args.generator_mode)
        token = os.environ.get(COPILOT_SDK_TOKEN_ENV)
        precisa_token = uc == "synth-eval" or (
                uc in ("synth-generate", "synth-skill-ab") and args.generator_mode == "sdk"
        )
        if precisa_token and not token:
            print(f"ERRO: variavel de ambiente '{COPILOT_SDK_TOKEN_ENV}' ausente.", file=sys.stderr)
            return 2
        if uc == "synth-promote":
            if not args.silver or not args.run_id:
                print("ERRO: synth-promote exige --silver e --run-id.", file=sys.stderr)
                return 2
            rel = executar_synth_promote(
                repo=None,
                silver=args.silver,
                run_id=args.run_id,
                suite=args.suite,
                out=args.out,
                stdout=args.stdout,
                confirm=args.confirm,
            )
            print(f"{rel.comando}: {rel.contadores} -> {rel.motivo}")
            return 0
        with SynthRepository(resolver_caminho_db(args.db)) as repo:
            if uc == "synth-generate":
                rel = executar_synth_generate(
                    repo=repo,
                    generator_mode=args.generator_mode,
                    max_premium_requests=args.max_premium_requests,
                    cliente_factory=(lambda: criar_cliente_sdk_real(str(token))) if token else None,
                    targets=_csv(args.targets),
                    dimensions=_csv(args.dimensions),
                    per_stratum=args.per_stratum,
                    rng_seed=args.rng_seed,
                    sim_threshold=args.sim_threshold,
                    max_attempts=args.max_attempts,
                    include_security=args.include_security,
                    dry_run=args.dry_run,
                    modelo=args.model,
                    routing_graph_path=args.routing_graph,
                    graph_seeding=args.graph_seeding,
                    graph_min_coverage=args.graph_min_coverage,
                    workflow_seeds=args.workflow_seeds,
                    skill_seeding=args.skill_seeding,
                    skills_filtro=_csv(args.skills),
                    skill_cases_path=args.skill_cases,
                )
            elif uc == "synth-eval":
                rel = executar_synth_eval(
                    repo=repo,
                    cliente_factory=lambda: criar_cliente_sdk_real(str(token)),
                    max_premium_requests=args.max_premium_requests,
                    router_agent_path=args.router_agent,
                    run_id=args.run_id,
                    source_run_id=args.source_run_id,
                    pending=args.pending,
                    limit=args.limit,
                    modelo=args.model,
                )
            elif uc == "synth-skill-ab":
                rel = executar_synth_skill_ab(
                    repo=repo,
                    cases_path=args.skill_cases,
                    skills_filtro=_csv(args.skills),
                    include_gap_seeds=bool(args.include_skill_gaps),
                    generator_mode=args.generator_mode,
                    max_premium_requests=args.max_premium_requests,
                    cliente_factory=(lambda: criar_cliente_sdk_real(str(token))) if token else None,
                    modelo=args.model,
                    run_id=args.run_id,
                )
            elif uc == "synth-diagnose":
                if not args.eval_run_id:
                    print("ERRO: synth-diagnose exige --eval-run-id.", file=sys.stderr)
                    return 3
                rel = executar_synth_diagnose(
                    repo=repo,
                    eval_run_id=args.eval_run_id,
                    skill_ab_run_id=args.skill_ab_run_id,
                    routing_graph_path=args.routing_graph,
                    router_agent_path=args.router_agent,
                    skill_cases_path=args.skill_cases,
                    min_support=args.min_support,
                    out_dir=args.out,
                    formato=args.format,
                    allow_root=bool(args.allow_root),
                )
            else:
                if not args.eval_run_id:
                    print("ERRO: synth-export exige --eval-run-id.", file=sys.stderr)
                    return 2
                rel = executar_synth_export(
                    repo=repo,
                    eval_run_id=args.eval_run_id,
                    only_failures=args.only_failures,
                    include_near_boundary=args.include_near_boundary,
                )
        extra_delta = (
            f" mean_delta={rel.mean_skill_delta_utility:.4f}"
            if rel.mean_skill_delta_utility is not None
            else ""
        )
        print(f"{rel.comando}: run_id={rel.run_id} status={rel.status} {rel.contadores}{extra_delta}")
        return rel.exit_code
    except (
            SynthOrcamentoInvalidoError,
            SynthExportPathError,
            SynthEvalRunInvalidoError,
            SynthDiagnosticPathError,
            RoutingGraphPathError,
    ) as exc:
        print(f"ERRO [governance-runner]: {exc}", file=sys.stderr)
        return int(exc.exit_code)
    except GraphValidationError as exc:
        print(f"ERRO [governance-runner]: routing-graph invalido: {exc}", file=sys.stderr)
        return EXIT_ROUTING_GRAPH_INVALIDO


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada do CLI `governance-runner`. Retorna o exit code do processo."""
    try:
        parser = construir_parser()
        args = parser.parse_args(argv)

        if args.use_case.startswith("synth-"):
            return _executar_synth(args)
        if not args.base:
            print("ERRO: --base e obrigatorio em agent-audit.", file=sys.stderr)
            return 2
        token = os.environ.get(COPILOT_SDK_TOKEN_ENV)
        if not token:
            print(
                f"ERRO: variavel de ambiente '{COPILOT_SDK_TOKEN_ENV}' ausente. "
                "Configure um token dedicado (GitHub App / fine-grained PAT com "
                "licenca Copilot) ou BYOK antes de executar o runner headless "
                "(BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md Q-01).",
                file=sys.stderr,
            )
            return 2

        if args.use_case == "agent-audit":
            grafo = carregar_grafo(_GRAFO_PADRAO, _SCHEMA_PADRAO)
            cliente_sdk = criar_cliente_sdk_real(token)
            orcamento = Budget()
            arquivos_diff = _ler_arquivos_diff(args.diff_file)
            relatorio = executar_agent_audit(
                base_ref=args.base,
                cliente_sdk=cliente_sdk,
                orcamento=orcamento,
                grafo=grafo,
                arquivos_diff=arquivos_diff,
            )
            print(relatorio)
            _publicar_relatorio(
                relatorio,
                canais=args.report,
                repo=args.repo,
                sha=args.sha,
                pr_number=args.pr_number,
            )
            return 0

        print(f"ERRO: use-case '{args.use_case}' nao suportado nesta fase PoC.", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERRO FATAL [governance-runner]: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
