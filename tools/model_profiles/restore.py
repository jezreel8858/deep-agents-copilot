"""Restore por linha: `model:` volta ao valor de HEAD (`git show HEAD:<path>`)."""
from __future__ import annotations

import datetime as dt
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.model_profiles import console, git, state, targets, writer
from tools.model_profiles.errors import RefusalError
from tools.model_profiles.findings import WARN, Finding

logger = logging.getLogger(__name__)

NOOP, RESTORED, CONFLICT = "noop", "restored", "conflict"


@dataclass
class RestoreResult:
    restored: list[str] = field(default_factory=list)
    conflicts: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)


def _conflict(rel: str, current: str | None, variant: Any) -> Finding:
    return Finding("CONFLICT", f"{rel}: linha model: atual {current!r} difere da variante "
                               f"{variant!r}; use --force-line para sobrescrever")


def _restore_one(repo: Path, entry: dict[str, Any], force_line: bool,
                 heads: dict[str, bytes] | None = None) -> tuple[str, Finding | None]:
    rel = entry["path"]
    path = targets.validate_state_path(repo, rel)
    if not path.exists():
        return CONFLICT, Finding("CONFLICT", f"{rel}: arquivo ausente")
    current = path.read_bytes()
    current_sha = hashlib.sha256(current).hexdigest()
    head_model = writer.read_model(
        heads[rel] if heads and rel in heads else git.show_head(repo, rel))
    if head_model is None:
        raise RefusalError(f"HEAD sem linha model: em {rel}", "RESTORE")
    cur_model = writer.read_model(current)
    variant = entry.get("variant_model")
    if cur_model == head_model:
        if head_model == variant:  # variante commitada: restore nao tem o que desfazer
            return NOOP, Finding("HEAD_HAS_VARIANT", f"{rel}: HEAD ja contem a variante "
                                 f"{head_model!r}; nada restaurado (variante foi commitada?)", WARN)
        return NOOP, None
    if cur_model != variant and not force_line:
        return CONFLICT, _conflict(rel, cur_model, variant)
    if entry.get("sha256_after") not in (None, current_sha):
        logger.info("%s: conteudo difere de sha256_after (edicao de corpo preservada)", rel)
    try:
        writer.atomic_write(path, writer.set_model(current, head_model), expected_sha=current_sha)
    except writer.WriteConflictError as exc:
        return CONFLICT, Finding("CONFLICT", f"{rel}: {exc}")
    return RESTORED, None


def restore_state(repo: Path, st: dict[str, Any], force_line: bool) -> RestoreResult:
    entries = st.get("files", [])
    state.validate_entries(entries)
    for entry in entries:  # valida TODOS os caminhos antes de qualquer escrita
        targets.validate_state_path(repo, str(entry.get("path")))
    result = RestoreResult()
    existing = [str(e["path"]) for e in entries if targets.validate_state_path(repo, str(e["path"])).exists()]
    heads = git.show_heads(repo, existing) if len(existing) > 1 else None
    for entry in entries:
        status, finding = _restore_one(repo, entry, force_line, heads)
        if status == RESTORED:
            result.restored.append(entry["path"])
        elif status == NOOP and finding:
            result.warnings.append(finding)
        elif finding:
            result.conflicts.append(finding)
    return result


def mark_restored(repo: Path, st: dict[str, Any]) -> None:
    done = {**state.with_phase(st, state.RESTORED),
            "restored_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    state.save_state(repo, done)


def run_restore(repo: Path, force_line: bool) -> int:
    st = state.load_state(repo)
    if st is None or st.get("phase") == state.RESTORED:
        console.say("nenhum perfil ativo; nada a restaurar")
        return 0
    result = restore_state(repo, st, force_line)
    console.report(result.warnings)
    if result.conflicts:
        console.report(result.conflicts)
        console.say(f"{len(result.restored)} arquivo(s) restaurado(s); conflitos pendentes")
        return 1
    mark_restored(repo, st)
    console.say(f"perfil '{st.get('profile')}' revertido: {len(result.restored)} arquivo(s)")
    return 0
