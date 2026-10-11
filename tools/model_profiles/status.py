"""Subcomandos list, status e init."""
from __future__ import annotations

from pathlib import Path

from tools.model_profiles import allowlist, config, console, git, planning, state
from tools.model_profiles.errors import ModelProfilesError
from tools.model_profiles.findings import WARN, Finding, has_errors


def stale_finding(allow: allowlist.Allowlist) -> Finding | None:
    if not allow.is_stale():
        return None
    return Finding("ALLOWLIST_STALE", f"allowlist verificada ha {allow.age_days()} dias "
                                      f"(limite {allow.freshness_days})", WARN)


def _allowlist_stale(repo: Path) -> list[Finding]:
    try:
        found = stale_finding(allowlist.load(repo / planning.ALLOWLIST_FILE))
    except ModelProfilesError:
        return []
    return [found] if found else []


def run_list(repo: Path) -> int:
    cfg = config.load_yaml(repo / planning.PROFILES_FILE)
    active = state.active_profile(state.load_state(repo))
    for name, spec in (cfg.get("profiles") or {}).items():
        marker = "*" if name == active else " "
        console.say(f"{marker} {name} - {(spec or {}).get('description', '')}")
    return 0


def run_status(repo: Path) -> int:
    st = state.load_state(repo)
    phase = st.get("phase") if st else "n/a"
    suffix = f"; perfil suspenso: {st.get('profile')}" if phase == state.SUSPENDED else ""
    console.say(f"perfil ativo: {state.active_profile(st)} (phase: {phase}{suffix})")
    findings = state.state_findings(repo, st) + _allowlist_stale(repo)
    console.report(findings)
    return 1 if has_errors(findings) else 0


def run_init(repo: Path) -> int:
    (repo / state.STATE_DIR).mkdir(exist_ok=True)
    entry = f"{state.STATE_DIR}/"
    if git.is_ignored(repo, f"{entry}{state.STATE_FILE}"):
        console.say(f"{entry} ja esta ignorado pelo git")
        return 0
    exclude = git.git_dir(repo) / "info" / "exclude"
    exclude.parent.mkdir(exist_ok=True)
    current = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    prefix = "" if not current or current.endswith("\n") else "\n"
    exclude.write_text(f"{current}{prefix}{entry}\n", encoding="utf-8", newline="\n")
    console.say(f"{entry} adicionado a .git/info/exclude")
    return 0
