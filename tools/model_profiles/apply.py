"""apply: resolve o perfil (resolver.py), valida allowlist + D6, journal write-ahead e escrita."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from tools.model_profiles import (console, git, hierarchy, resolver, restore, state, summary,
                                  targets, writer)
from tools.model_profiles.errors import RefusalError
from tools.model_profiles.findings import CONFIRM, ERROR, Finding, has_errors
from tools.model_profiles.planning import Change, Context, ProfilePlan, load_context

logger = logging.getLogger(__name__)


def _resolve(name: str, ctx: Context) -> tuple[dict[str, Any], dict[str, str]]:
    try:
        resolved = resolver.resolve_profile(name, ctx.cfg.get("profiles") or {})
        models: dict[str, str] = {}
        for target in ctx.targets:
            tier = resolver.get_tier_for_key(target.key, ctx.key_to_tier)
            models[target.key] = resolver.resolve_target_model(target.key, tier, resolved)
    except (KeyError, ValueError, TypeError) as exc:
        raise RefusalError(str(exc.args[0]) if exc.args else str(exc), "PROFILE") from exc
    return resolved, models


def _allowlist_findings(models: dict[str, str], ctx: Context) -> list[Finding]:
    return [f for model in sorted(set(models.values())) for f in ctx.allow.check(model)]


def _hierarchy_findings(models: dict[str, str], ctx: Context) -> list[Finding]:
    exceptions = {t.key for t in ctx.targets if t.exception}
    found = hierarchy.find_violations(ctx.edges, models, ctx.allow.rank_by_model(), exceptions)
    out = []
    for v in found:
        detail = f"{v.parent} ({models[v.parent]}) -> {v.child} ({models[v.child]})"
        if v.kind == hierarchy.COST_HIERARCHY:
            out.append(Finding("COST_HIERARCHY", f"filho mais caro que o pai: {detail}", ERROR))
        else:
            out.append(Finding("COST_RANK_NULL", f"hierarquia nao verificavel: {detail}", CONFIRM))
    return out


def plan_profile(name: str, ctx: Context) -> ProfilePlan:
    resolved, models = _resolve(name, ctx)
    plan = ProfilePlan(name, resolved, models)
    for target in ctx.targets:
        new = models[target.key]
        if new != target.model:
            plan.changes.append(Change(target, new, writer.set_model(target.data, new)))
    plan.findings = _allowlist_findings(models, ctx) + _hierarchy_findings(models, ctx)
    return plan


def _guard_state(repo: Path) -> None:
    st = state.load_state(repo)
    if state.is_orphan(st):
        raise RefusalError("journal orfao (apply interrompido); rode doctor --repair", "ORPHAN_JOURNAL")
    if st and st.get("phase") == state.SUSPENDED:
        raise RefusalError(f"perfil '{st.get('profile')}' suspenso; rode resume ou restore antes",
                           "SUSPENDED")
    if st and st.get("phase") == state.APPLIED:
        raise RefusalError(f"perfil '{st.get('profile')}' ativo; rode restore antes", "ACTIVE_PROFILE")


def _guard_git(repo: Path, ctx: Context) -> None:
    busy = git.in_progress(repo)
    if busy:
        raise RefusalError(f"operacao git em andamento: {', '.join(busy)}", "IN_PROGRESS")
    dirty = git.dirty_paths(repo, [t.rel for t in ctx.targets])
    if dirty:
        raise RefusalError(f"alvos com alteracoes locais: {', '.join(dirty)}", "DIRTY")


def _entry(change: Change, heads: dict[str, str]) -> dict[str, Any]:
    rel = change.target.rel
    if rel not in heads:
        raise RefusalError(f"{rel} nao esta versionado em HEAD", "UNTRACKED")
    return {"path": rel, "head_blob": heads[rel], "original_model": change.target.model,
            "variant_model": change.new_model,
            "eol": "crlf" if b"\r\n" in change.target.data else "lf",
            "sha256_after": hashlib.sha256(change.new_data).hexdigest()}


def _rollback(repo: Path, journal: dict[str, Any], exc: Exception) -> int:
    logger.exception("falha durante apply")
    console.fail(f"[APPLY_FAILED] {exc}; revertendo arquivos ja escritos")
    try:
        result = restore.restore_state(repo, journal, False)
        if not result.conflicts:
            restore.mark_restored(repo, journal)
            return 1
    except Exception:  # noqa: BLE001 - journal pendente permite doctor --repair
        logger.exception("rollback falhou")
    console.fail("[ORPHAN_JOURNAL] rollback incompleto; rode doctor --repair")
    return 1


def _planned_sha(change: Change) -> str:
    return hashlib.sha256(change.target.data).hexdigest()


def _verify_plan_unchanged(repo: Path, plan: ProfilePlan) -> None:
    """Pre-flight: nenhum alvo mudou/virou link desde o planejamento (senao [CONFLICT])."""
    for change in plan.changes:
        targets.ensure_confined(repo, change.target.path)
        writer.check_unchanged(change.target.path, _planned_sha(change))


def _execute(repo: Path, plan: ProfilePlan) -> int:
    _verify_plan_unchanged(repo, plan)
    heads = git.head_blobs(repo, [c.target.rel for c in plan.changes])
    files = [_entry(c, heads) for c in plan.changes]
    journal = state.new_state(plan.name, state.profile_hash(plan.resolved),
                              git.head_commit(repo), files)
    state.save_state(repo, journal)  # write-ahead: lista completa antes da 1a escrita
    try:
        for change in plan.changes:
            writer.atomic_write(change.target.path, change.new_data,
                                expected_sha=_planned_sha(change))
    except Exception as exc:  # noqa: BLE001 - BaseException (crash) propaga
        return _rollback(repo, journal, exc)
    state.save_state(repo, state.with_phase(journal, state.APPLIED))
    console.say(f"perfil '{plan.name}' aplicado em {len(plan.changes)} arquivos. "
                "Nao commitar; reverta com `restore`.")
    return 0


def run_apply(repo: Path, profile: str, dry_run: bool, assume_yes: bool) -> int:
    ctx = load_context(repo)
    plan = plan_profile(profile, ctx)
    _guard_state(repo)
    _guard_git(repo, ctx)
    console.report(plan.findings)
    if has_errors(plan.findings):
        return 1
    if not plan.changes:
        console.say(f"perfil '{profile}' ja esta refletido nos arquivos; nada a alterar")
        return 0
    summary.print_summary(plan)
    if dry_run:
        return 0
    if not summary.confirm(plan.findings, assume_yes):
        console.say("operacao cancelada; nada foi gravado")
        return 1
    return _execute(repo, plan)


# API reutilizada por suspend.py (resume reaplica sem duplicar a logica)
resolve_profile_models = _resolve
guard_git = _guard_git
execute_plan = _execute
