"""suspend/resume: desfaz temporariamente o perfil (linhas model: = HEAD) e o reaplica depois.

Reutiliza restore (conflito por linha, expected_sha) e apply (allowlist/D6, journal, escrita).
"""
from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path
from typing import Any

from tools.model_profiles import apply, console, git, restore, state, summary
from tools.model_profiles.errors import RefusalError
from tools.model_profiles.findings import has_errors
from tools.model_profiles.planning import load_context

logger = logging.getLogger(__name__)


def _require_applied(st: dict[str, Any] | None) -> dict[str, Any]:
    if st is None or st.get("phase") == state.RESTORED:
        raise RefusalError("nenhum perfil ativo; nada a suspender", "NO_ACTIVE_PROFILE")
    if state.is_orphan(st):
        raise RefusalError("journal orfao (apply interrompido); rode doctor --repair", "ORPHAN_JOURNAL")
    if st.get("phase") == state.SUSPENDED:
        raise RefusalError(f"perfil '{st.get('profile')}' ja esta suspenso; rode resume", "SUSPENDED")
    return st


def run_suspend(repo: Path, assume_yes: bool) -> int:
    st = _require_applied(state.load_state(repo))
    if not summary.confirm_action(
            f"suspend restaura as linhas model: do perfil '{st.get('profile')}' ao valor de HEAD.",
            assume_yes):
        console.say("operacao cancelada; nada foi gravado")
        return 1
    result = restore.restore_state(repo, st, False)
    console.report(result.warnings)
    if result.conflicts:
        console.report(result.conflicts)
        console.say(f"{len(result.restored)} arquivo(s) restaurado(s); conflitos pendentes; "
                    "perfil continua applied")
        return 1
    suspended = {**state.with_phase(st, state.SUSPENDED),
                 "suspended_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    state.save_state(repo, suspended)
    console.say(f"perfil '{st.get('profile')}' suspenso: {len(result.restored)} arquivo(s) em HEAD; "
                "reaplique com `resume`")
    return 0


def run_resume(repo: Path, force: bool, assume_yes: bool) -> int:
    st = state.load_state(repo)
    if st is None or st.get("phase") != state.SUSPENDED:
        raise RefusalError("nenhum perfil suspenso; nada a retomar", "NOT_SUSPENDED")
    profile = str(st.get("profile"))
    ctx = load_context(repo)
    resolved, _ = apply.resolve_profile_models(profile, ctx)
    if state.profile_hash(resolved) != st.get("profile_hash") and not force:
        raise RefusalError(f"perfil '{profile}' mudou desde o suspend (hash diferente); "
                           "revise e use --force para reaplicar", "PROFILE_CHANGED")
    apply.guard_git(repo, ctx)  # IN_PROGRESS / DIRTY
    plan = apply.plan_profile(profile, ctx)
    console.report(plan.findings)
    if has_errors(plan.findings):
        return 1
    summary.print_summary(plan)
    if not summary.confirm(plan.findings, assume_yes):
        console.say("operacao cancelada; nada foi gravado")
        return 1
    return apply.execute_plan(repo, plan)
