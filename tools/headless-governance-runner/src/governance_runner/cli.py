"""
cli — Entrypoint `governance-runner` do runner headless (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.3).

Uso:
    governance-runner --use-case agent-audit --base <ref> --report checks,pr-comment

Falha explicitamente (mensagem descritiva, código 2) se `COPILOT_SDK_TOKEN` estiver
ausente para o caso de uso `agent-audit` ou sob exceção não esperada em runtime,
sem vazar stack trace cru no stdout/stderr do CI.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from governance_runner.routing.graph_loader import carregar_grafo
from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import criar_cliente_sdk_real
from governance_runner.runner.use_cases import executar_agent_audit

__all__ = ["main", "construir_parser", "COPILOT_SDK_TOKEN_ENV"]

COPILOT_SDK_TOKEN_ENV = "COPILOT_SDK_TOKEN"

_USE_CASES_SUPORTADOS = ("agent-audit",)

_SCHEMA_PADRAO = Path(__file__).parent / "routing" / "routing-graph.schema.json"
_GRAFO_PADRAO = Path(__file__).parents[3] / ".github" / "agents" / "routing-graph.yaml"


def construir_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos do entrypoint `governance-runner`."""
    parser = argparse.ArgumentParser(prog="governance-runner")
    parser.add_argument(
        "--use-case",
        required=True,
        choices=_USE_CASES_SUPORTADOS,
        help="Caso de uso do runner headless a executar.",
    )
    parser.add_argument("--base", required=True, help="Ref git base da comparacao (ex.: github.base_ref).")
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
    return parser


def _ler_arquivos_diff(caminho: str | None) -> tuple[str, ...]:
    if not caminho:
        return ()
    return tuple(
        linha.strip()
        for linha in Path(caminho).read_text(encoding="utf-8").splitlines()
        if linha.strip()
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada do CLI `governance-runner`. Retorna o exit code do processo.

    Captura exceções no nível mais externo e retorna exit code não-zero (2) com
    mensagem curta e estruturada em stderr, sem vazar stack trace longo para CI.
    """
    try:
        parser = construir_parser()
        args = parser.parse_args(argv)

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
            return 0

        print(f"ERRO: use-case '{args.use_case}' nao suportado nesta fase PoC.", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERRO FATAL [governance-runner]: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
