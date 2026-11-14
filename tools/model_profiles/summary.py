"""Resumo do apply e confirmacao interativa."""
from __future__ import annotations

from tools.model_profiles import console
from tools.model_profiles.findings import Finding
from tools.model_profiles.planning import ProfilePlan

_YES = {"s", "sim", "y", "yes"}
_STRONG = "CONFIRMAR"


def print_summary(plan: ProfilePlan) -> None:
    console.say(f"Perfil: {plan.name} - {plan.resolved.get('description') or ''}")
    console.say(f"Arquivos a alterar: {len(plan.changes)} arquivos")
    for change in plan.changes:
        console.say(f"  {change.target.rel}: {change.target.model} -> {change.new_model}")
    warning = plan.resolved.get("quality_warning")
    if warning:
        console.say(f"AVISO DE QUALIDADE: {warning}")
    console.say("ATENCAO: nao commitar estas alteracoes; rode `restore` antes de commitar.")


def _ask(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, OSError):
        return ""


def needs_strong_confirmation(findings: list[Finding]) -> bool:
    return any(f.code == "COST_RANK_NULL" for f in findings)


def confirm_action(prompt: str, assume_yes: bool) -> bool:
    """Confirmacao simples de acao destrutiva; `--yes` dispensa; nao interativo => recusa."""
    if assume_yes:
        return True
    return _ask(f"{prompt} Continuar? [s/N] ").strip().lower() in _YES


def confirm(findings: list[Finding], assume_yes: bool) -> bool:
    """--yes NAO dispensa a confirmacao reforcada quando ha COST_RANK_NULL."""
    if needs_strong_confirmation(findings):
        return _ask(f"cost_rank nulo: digite {_STRONG} para prosseguir: ").strip() == _STRONG
    if assume_yes:
        return True
    return _ask("Aplicar? [s/N] ").strip().lower() in _YES
