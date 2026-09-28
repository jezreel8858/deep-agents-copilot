"""
checks — Formatação e emissão de status check (Checks API) via `gh api` (mockável).

Escopo (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.4): canal primário do
caso de uso `agent-audit` — conclusão `neutral` na PoC.
"""

from __future__ import annotations

import subprocess
from typing import Callable

from governance_runner.runner.use_cases import RelatorioAuditoria

__all__ = ["formatar_check", "publicar_check"]

_CONCLUSOES_VALIDAS = frozenset({"neutral", "success", "failure", "action_required"})

_ExecutorGh = Callable[..., "subprocess.CompletedProcess[str]"]


def formatar_check(relatorio: RelatorioAuditoria) -> dict[str, object]:
    """Formata o payload mínimo do Checks API a partir de um `RelatorioAuditoria`."""
    conclusao = relatorio.veredito if relatorio.veredito in _CONCLUSOES_VALIDAS else "neutral"
    resumo_linhas = [
        f"Caso de uso: {relatorio.use_case}",
        f"Veredito: {relatorio.veredito}",
        f"Custo: {relatorio.custo}",
        f"Trace: {relatorio.trace_id}",
    ]
    if relatorio.motivo:
        resumo_linhas.append(f"Motivo: {relatorio.motivo}")
    return {
        "name": f"governance/{relatorio.use_case}",
        "conclusion": conclusao,
        "output": {
            "title": f"Governance · {relatorio.use_case} ({relatorio.veredito})",
            "summary": "\n".join(resumo_linhas),
            "annotations": [
                {
                    "path": achado.arquivo,
                    "start_line": achado.linha or 1,
                    "end_line": achado.linha or 1,
                    "annotation_level": "notice",
                    "message": achado.mensagem,
                    "title": achado.regra,
                }
                for achado in relatorio.achados
            ],
        },
    }


def publicar_check(
    relatorio: RelatorioAuditoria,
    *,
    repo: str,
    sha: str,
    executor_gh: _ExecutorGh = subprocess.run,
) -> "subprocess.CompletedProcess[str]":
    """Publica o check no repositório via `gh api` (executor injetável para testes).

    Args:
        relatorio: Relatório estruturado a publicar.
        repo: Repositório `owner/name`.
        sha: SHA do commit alvo do check.
        executor_gh: Função executora de subprocess (mockável em testes).
    """
    payload = formatar_check(relatorio)
    comando = [
        "gh",
        "api",
        f"repos/{repo}/check-runs",
        "-f",
        f"name={payload['name']}",
        "-f",
        f"head_sha={sha}",
        "-f",
        f"conclusion={payload['conclusion']}",
        "-f",
        "status=completed",
    ]
    return executor_gh(comando, check=True, capture_output=True, text=True)
