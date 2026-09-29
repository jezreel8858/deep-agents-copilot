"""
pr_comment — Formatação e publicação de comentário sticky de PR via `gh pr comment` (mockável).
"""

from __future__ import annotations

import subprocess
from typing import Callable

from governance_runner.runner.use_cases import RelatorioAuditoria

__all__ = ["formatar_comentario", "publicar_comentario_sticky"]

_ExecutorGh = Callable[..., "subprocess.CompletedProcess[str]"]

_MARCADOR_STICKY = "<!-- governance-runner:agent-audit -->"


def formatar_comentario(relatorio: RelatorioAuditoria) -> str:
    """Formata o corpo Markdown do comentário sticky de PR a partir de um `RelatorioAuditoria`."""
    linhas = [
        _MARCADOR_STICKY,
        f"### Governance · {relatorio.use_case} — veredito `{relatorio.veredito}`",
        "",
        f"- **Trace**: `{relatorio.trace_id}`",
        f"- **Custo**: `{relatorio.custo}`",
    ]
    if relatorio.motivo:
        linhas.append(f"- **Motivo**: `{relatorio.motivo}`")
    linhas.append("")
    if relatorio.achados:
        linhas.append("| Arquivo | Linha | Regra | Severidade | Mensagem |")
        linhas.append("|---|---|---|---|---|")
        for achado in relatorio.achados:
            linhas.append(
                f"| {achado.arquivo} | {achado.linha or '-'} | {achado.regra} "
                f"| {achado.severidade} | {achado.mensagem} |"
            )
    else:
        linhas.append("Nenhum achado nesta execucao.")
    return "\n".join(linhas)


def publicar_comentario_sticky(
    relatorio: RelatorioAuditoria,
    *,
    pr_number: int,
    executor_gh: _ExecutorGh = subprocess.run,
) -> "subprocess.CompletedProcess[str]":
    """Publica (edita o último, se existente) o comentário sticky do PR via `gh pr comment`."""
    corpo = formatar_comentario(relatorio)
    comando = ["gh", "pr", "comment", str(pr_number), "--edit-last", "--body", corpo]
    return executor_gh(comando, check=True, capture_output=True, text=True)
