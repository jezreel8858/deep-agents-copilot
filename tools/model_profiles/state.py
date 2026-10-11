"""state.json v1 com journal write-ahead (pending -> applied -> restored)."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from tools.model_profiles import targets, writer
from tools.model_profiles.errors import ModelProfilesError, PathTraversalError
from tools.model_profiles.findings import WARN, Finding

STATE_DIR = ".model-profiles"
STATE_FILE = "state.json"
SCHEMA_VERSION = 1
PENDING, APPLIED, RESTORED, SUSPENDED = "pending", "applied", "restored", "suspended"


_SHA = re.compile(r"[0-9a-f]{64}")
_BLOB = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


def _corrupt(detail: str) -> ModelProfilesError:
    return ModelProfilesError(f"state.json com schema invalido: {detail}", "STATE_CORRUPT")


def validate_entries(files: Any) -> None:
    """Schema por entrada: dict, path/variant_model str, shas hex; valores nao sao ecoados."""
    if not isinstance(files, list):
        raise _corrupt("'files' nao e lista")
    for idx, entry in enumerate(files):
        if not isinstance(entry, dict):
            raise _corrupt(f"files[{idx}] nao e objeto")
        for key in ("path", "variant_model"):
            if not isinstance(entry.get(key), str):
                raise _corrupt(f"files[{idx}].{key} ausente ou nao-texto")
        for key in ("original_model", "eol"):
            if key in entry and not isinstance(entry[key], str):
                raise _corrupt(f"files[{idx}].{key} nao-texto")
        for key, rx in (("sha256_after", _SHA), ("head_blob", _BLOB)):
            if key in entry and not (isinstance(entry[key], str) and rx.fullmatch(entry[key])):
                raise _corrupt(f"files[{idx}].{key} invalido")


def state_path(repo: Path) -> Path:
    return repo / STATE_DIR / STATE_FILE


def load_state(repo: Path) -> dict[str, Any] | None:
    path = state_path(repo)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ModelProfilesError(f"state.json ilegivel: {exc}", "STATE_CORRUPT") from exc
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ModelProfilesError("state.json com schema invalido", "STATE_CORRUPT")
    if data.get("phase") not in (PENDING, APPLIED, RESTORED, SUSPENDED):
        raise _corrupt("phase desconhecida")
    validate_entries(data.get("files", []))
    return data


def save_state(repo: Path, state: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(exist_ok=True)
    writer.write_replace(path, json.dumps(state, indent=2, ensure_ascii=False).encode("utf-8"))


def profile_hash(resolved: dict[str, Any]) -> str:
    canonical = json.dumps(resolved, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def new_state(profile: str, phash: str, head: str, files: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "profile": profile, "profile_hash": phash,
            "phase": PENDING, "head_commit": head,
            "applied_at": dt.datetime.now(dt.timezone.utc).isoformat(), "files": files}


def with_phase(state: dict[str, Any], phase: str) -> dict[str, Any]:
    return {**state, "phase": phase}


def active_profile(state: dict[str, Any] | None) -> str:
    if state and state.get("phase") in (PENDING, APPLIED):
        return str(state.get("profile", "default"))
    return "default"


def is_orphan(state: dict[str, Any] | None) -> bool:
    return bool(state) and state.get("phase") == PENDING  # type: ignore[union-attr]


def _drift_finding(repo: Path, entry: dict[str, Any]) -> Finding | None:
    rel = str(entry.get("path"))
    try:
        path = targets.validate_state_path(repo, rel)
    except PathTraversalError as exc:
        return Finding("PATH_TRAVERSAL", str(exc))
    current = writer.read_model(path.read_bytes()) if path.exists() else None
    if current == entry.get("variant_model"):
        return None
    return Finding("DRIFT", f"{rel}: model atual {current!r} != variante {entry.get('variant_model')!r}")


def state_findings(repo: Path, state: dict[str, Any] | None) -> list[Finding]:
    if state is None:
        return []
    if is_orphan(state):
        return [Finding("ORPHAN_JOURNAL",
                        f"apply do perfil '{state.get('profile')}' interrompido; rode doctor --repair")]
    if state.get("phase") == SUSPENDED:  # arquivos em HEAD de proposito: sem falso drift
        return [Finding("SUSPENDED", f"perfil '{state.get('profile')}' suspenso; "
                                     "rode resume para reaplicar ou restore para descartar", WARN)]
    if state.get("phase") != APPLIED:
        return []
    found = (_drift_finding(repo, e) for e in state.get("files", []))
    return [f for f in found if f]
