"""doctor: diagnostico (allowlist, D6 de todos os perfis, git, journal, lock) e --repair."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from tools.model_profiles import apply, console, git, lock, planning, restore, state, status
from tools.model_profiles.errors import ModelProfilesError
from tools.model_profiles.findings import WARN, Finding, has_errors


def _profile_findings(ctx: planning.Context) -> list[Finding]:
    out: list[Finding] = []
    for name in ctx.cfg.get("profiles") or {}:
        try:
            found = apply.plan_profile(name, ctx).findings
        except ModelProfilesError as exc:
            out.append(Finding(exc.code, f"perfil '{name}': {exc}"))
            continue
        out += [replace(f.downgraded(), message=f"perfil '{name}': {f.message}") for f in found]
    return out


def _config_findings(repo: Path) -> list[Finding]:
    try:
        ctx = planning.load_context(repo)
    except ModelProfilesError as exc:
        return [Finding(exc.code, str(exc))]
    stale = status.stale_finding(ctx.allow)
    return _profile_findings(ctx) + ([stale] if stale else [])


def _git_findings(repo: Path) -> list[Finding]:
    out = [Finding("SKIP_WORKTREE", f"skip-worktree residual: {p}") for p in git.skip_worktree(repo)]
    hooks = git.config_get(repo, "core.hooksPath")
    if hooks != ".githooks" or not (repo / ".githooks" / "pre-commit").exists():
        out.append(Finding("HOOKS_PATH", "core.hooksPath != .githooks ou pre-commit ausente "
                                         "(guard de commit nao instalado)", WARN))
    return out


def _lock_findings(repo: Path) -> list[Finding]:
    current = lock.lock_state(repo)
    if current == "stale":
        return [Finding("STALE_LOCK", "lock obsoleto em .model-profiles/lock; use doctor --repair")]
    if current == "live":
        return [Finding("LOCKED", "outra instancia mantem .model-profiles/lock")]
    return []


def diagnose(repo: Path) -> list[Finding]:
    try:
        state_found = state.state_findings(repo, state.load_state(repo))
    except ModelProfilesError as exc:
        state_found = [Finding(exc.code, str(exc))]
    return _config_findings(repo) + _git_findings(repo) + state_found + _lock_findings(repo)


def repair_journal(repo: Path) -> int:
    st = state.load_state(repo)
    if not state.is_orphan(st):
        return 0
    assert st is not None
    result = restore.restore_state(repo, st, False)
    if result.conflicts:
        console.report(result.conflicts)
        return 1
    restore.mark_restored(repo, st)
    console.say(f"journal orfao do perfil '{st.get('profile')}' revertido")
    return 0


def run_doctor(repo: Path, repair: bool) -> int:
    if repair:
        with lock.exclusive_lock(repo):  # retoma lock obsoleto; LockError => [LOCKED]
            if repair_journal(repo):
                return 1
    findings = diagnose(repo)
    console.report(findings)
    console.say("doctor: " + ("problemas encontrados" if has_errors(findings) else "ok"))
    return 1 if has_errors(findings) else 0
