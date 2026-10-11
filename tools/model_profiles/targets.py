"""Descoberta e validacao de alvos (.github/agents/**/*.agent.md, .github/prompts/**/*.prompt.md)."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from tools.model_profiles import resolver, writer
from tools.model_profiles.errors import PathTraversalError

logger = logging.getLogger(__name__)

AGENTS_REL = ".github/agents"
PROMPTS_REL = ".github/prompts"
_SUFFIXES = (".agent.md", ".prompt.md")


@dataclass(frozen=True)
class Target:
    key: str
    rel: str
    path: Path
    data: bytes
    model: str
    exception: bool


def _inside(repo: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo.resolve())
    except ValueError:
        return False
    return True


def _is_link(path: Path) -> bool:
    junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(junction and junction())


def ensure_confined(repo: Path, path: Path) -> None:
    """Recusa symlink/junction (arquivo ou componente) e caminho fora de agents/prompts."""
    try:
        lexical = path.relative_to(repo)
    except ValueError:
        raise PathTraversalError(f"alvo fora do repositorio: {path}") from None
    cur = repo
    for part in lexical.parts:
        cur = cur / part
        if _is_link(cur):
            raise PathTraversalError(f"link simbolico recusado: {lexical.as_posix()!r}")
    resolved, root = path.resolve(), repo.resolve()
    for base in (AGENTS_REL, PROMPTS_REL):
        try:
            resolved.relative_to((root / base).resolve())
            return
        except ValueError:
            continue
    raise PathTraversalError(f"caminho fora de {AGENTS_REL} e {PROMPTS_REL}: {lexical.as_posix()!r}")


def _check_key(key: str) -> None:
    name = key.removeprefix("prompt:")
    parts = name.split("/")
    if (not name or "\\" in name or ":" in name
            or any(p in ("", ".", "..") for p in parts)):
        raise PathTraversalError(f"chave invalida no tier_map: {key!r}")


def validate_keys(tier_map: dict) -> None:
    for keys in tier_map.values():
        for key in keys or []:
            _check_key(str(key))


def validate_state_path(repo: Path, rel: str) -> Path:
    """Aceita somente caminhos relativos de agents/prompts dentro do repo."""
    posix = PurePosixPath(rel)
    prefixed = rel.startswith((f"{AGENTS_REL}/", f"{PROMPTS_REL}/"))
    if ("\\" in rel or ".." in posix.parts or posix.is_absolute()
            or not prefixed or not rel.endswith(_SUFFIXES)):
        raise PathTraversalError(f"caminho fora do escopo permitido: {rel!r}")
    path = repo / rel
    ensure_confined(repo, path)
    return path


def _load_target(repo: Path, path: Path, agents: Path, prompts: Path,
                 key_to_tier: dict[str, str]) -> Target | None:
    key = resolver.get_canonical_key(path, agents, prompts)
    if key not in key_to_tier:
        logger.debug("arquivo fora do tier_map ignorado: %s", key)
        return None
    ensure_confined(repo, path)
    data = path.read_bytes()
    model = writer.read_model(data)
    if model is None:
        logger.warning("sem linha model: em %s; ignorado", path)
        return None
    exception = writer.read_field(data, "model_exception_reason") is not None
    return Target(key, path.relative_to(repo).as_posix(), path, data, model, exception)


def discover(repo: Path, key_to_tier: dict[str, str]) -> list[Target]:
    agents, prompts = repo / AGENTS_REL, repo / PROMPTS_REL
    found: list[Target] = []
    for base, pattern in ((agents, "*.agent.md"), (prompts, "*.prompt.md")):
        for path in sorted(base.rglob(pattern)) if base.is_dir() else []:
            target = _load_target(repo, path, agents, prompts, key_to_tier)
            if target:
                found.append(target)
    return sorted(found, key=lambda t: t.rel)
