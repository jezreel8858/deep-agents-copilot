"""Subcomandos list, status e init."""
from __future__ import annotations

from pathlib import Path

from tools.model_profiles import allowlist, console, git, planning, state
from tools.model_profiles.errors import ModelProfilesError, RefusalError
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


def _local_mark(name: str, local_names: frozenset[str]) -> str:
    return " (local)" if name in local_names else ""


def run_list(repo: Path) -> int:
    cfg, local_names = planning.load_merged(repo)
    active = state.active_profile(state.load_state(repo))
    for name, spec in (cfg.get("profiles") or {}).items():
        marker = "*" if name == active else " "
        console.say(f"{marker} {name}{_local_mark(name, local_names)} - "
                    f"{(spec or {}).get('description', '')}")
    return 0


def run_status(repo: Path) -> int:
    st = state.load_state(repo)
    _, local_names = planning.load_merged(repo)
    phase = st.get("phase") if st else "n/a"
    suffix = f"; perfil suspenso: {st.get('profile')}" if phase == state.SUSPENDED else ""
    active = state.active_profile(st)
    console.say(f"perfil ativo: {active}{_local_mark(active, local_names)} (phase: {phase}{suffix})")
    if local_names:
        listed = ", ".join(f"{name} (local)" for name in sorted(local_names))
        console.say(f"perfis locais: {listed}")
    findings = state.state_findings(repo, st) + _allowlist_stale(repo)
    console.report(findings)
    return 1 if has_errors(findings) else 0


def _copy_local_example(repo: Path) -> None:
    """Copia o example para o yaml local. Nunca sobrescreve arquivo existente."""
    dest = repo / planning.LOCAL_PROFILES_FILE
    example = repo / planning.LOCAL_PROFILES_EXAMPLE
    if dest.is_symlink() or example.is_symlink():
        raise RefusalError(f"link simbolico recusado: {planning.LOCAL_PROFILES_FILE}", "PATH_TRAVERSAL")
    if dest.exists():
        console.say(f"{planning.LOCAL_PROFILES_FILE} ja existe; nao sobrescrito")
        return
    if not example.is_file():
        return
    dest.write_bytes(example.read_bytes())
    console.say(f"{planning.LOCAL_PROFILES_FILE} criado a partir de {planning.LOCAL_PROFILES_EXAMPLE}")


def run_init(repo: Path) -> int:
    _copy_local_example(repo)
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
