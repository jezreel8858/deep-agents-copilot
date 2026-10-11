"""Wrapper fino de git (subprocess) usado por apply/restore/doctor/status."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from tools.model_profiles.errors import RefusalError

_IN_PROGRESS = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply")


_HARDEN = ("-c", "core.fsmonitor=false", "-c", f"core.hooksPath={os.devnull}")


def _argv(*args: str, harden: bool = True) -> list[str]:
    """git sem fsmonitor/hooks do repo alvo (config maliciosa nao executa codigo)."""
    return ["git", "--no-optional-locks", *(_HARDEN if harden else ()), *args]


def run(repo: Path, *args: str, check: bool = True,
        harden: bool = True) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(_argv(*args, harden=harden), cwd=repo, capture_output=True)
    if check and proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RefusalError(f"git {args[0]} falhou: {detail}", "GIT")
    return proc


def text(repo: Path, *args: str) -> str:
    return run(repo, *args).stdout.decode("utf-8", errors="replace").strip()


def toplevel(cwd: Path) -> Path:
    return Path(text(cwd, "rev-parse", "--show-toplevel"))


def require_root(repo: Path) -> Path:
    """--repo deve ser a raiz git (rev-parse --show-toplevel), nao subdiretorio/pasta qualquer."""
    if not repo.is_dir():
        raise RefusalError(f"--repo {repo} nao e um diretorio", "REPO")
    proc = run(repo, "rev-parse", "--show-toplevel", check=False)
    if proc.returncode != 0:
        raise RefusalError(f"--repo {repo} nao e um repositorio git", "REPO")
    top = Path(proc.stdout.decode("utf-8", errors="replace").strip())
    try:
        same = os.path.samefile(top, repo)
    except OSError:
        same = False
    if not same:
        raise RefusalError(f"--repo {repo} nao e a raiz do repositorio git (raiz: {top}); "
                           "aponte --repo para a raiz", "REPO")
    return repo


_HEX = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
def _read_head_file(repo: Path) -> str | None:
    """HEAD resolvido lendo .git (sem spawn); None => usar fallback `rev-parse`."""
    dot_git = repo / ".git"
    if not dot_git.is_dir():
        return None
    try:
        head = (dot_git / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref: "):
            return head if _HEX.fullmatch(head) else None
        ref = head[5:].strip()
        if not ref.startswith("refs/") or ".." in ref:
            return None
        loose = dot_git / ref
        if loose.is_file():
            sha = loose.read_text(encoding="utf-8").strip()
            return sha if _HEX.fullmatch(sha) else None
        packed = dot_git / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="utf-8").splitlines():
                sha, _, name = line.partition(" ")
                if name == ref and _HEX.fullmatch(sha):
                    return sha
    except (OSError, UnicodeDecodeError):
        return None
    return None
def head_commit(repo: Path) -> str:
    return _read_head_file(repo) or text(repo, "rev-parse", "HEAD")


def dirty_paths(repo: Path, rels: list[str]) -> list[str]:
    """Alvos com alteracao em worktree OU index (staged)."""
    out = run(repo, "status", "--porcelain", "-z", "--untracked-files=no", "--", *rels).stdout
    return [e[3:].decode("utf-8", errors="replace") for e in out.split(b"\0") if len(e) > 3]


def head_blobs(repo: Path, rels: list[str]) -> dict[str, str]:
    """relpath -> sha do blob em HEAD (um unico `git ls-tree`)."""
    out = run(repo, "ls-tree", "-z", "HEAD", "--", *rels).stdout
    blobs: dict[str, str] = {}
    for entry in filter(None, out.split(b"\0")):
        meta, _, path = entry.partition(b"\t")
        blobs[path.decode("utf-8", errors="replace")] = meta.split()[2].decode()
    return blobs


def show_head(repo: Path, rel: str) -> bytes:
    return run(repo, "show", f"HEAD:{rel}").stdout


def show_heads(repo: Path, rels: list[str]) -> dict[str, bytes]:
    """relpath -> conteudo em HEAD (um unico `git cat-file --batch`); ausentes/invalidos omitidos."""
    wanted = [r for r in dict.fromkeys(rels) if r and "\n" not in r and "\0" not in r]
    if not wanted:
        return {}
    request = "".join(f"HEAD:{r}\n" for r in wanted).encode("utf-8")
    proc = subprocess.run(_argv("cat-file", "--batch"), cwd=repo,
                          input=request, capture_output=True)
    if proc.returncode != 0:
        return {}
    out, pos, blobs = proc.stdout, 0, {}
    for rel in wanted:
        end = out.find(b"\n", pos)
        if end < 0:
            break
        header = out[pos:end].split()
        pos = end + 1
        if len(header) == 3 and header[1] == b"blob":
            size = int(header[2])
            blobs[rel] = out[pos:pos + size]
            pos += size + 1
    return blobs
def git_dir(repo: Path) -> Path:
    dot_git = repo / ".git"
    return dot_git if dot_git.is_dir() else Path(text(repo, "rev-parse", "--absolute-git-dir"))


def in_progress(repo: Path) -> list[str]:
    base = git_dir(repo)
    return [name for name in _IN_PROGRESS if (base / name).exists()]


def is_ignored(repo: Path, rel: str) -> bool:
    return run(repo, "check-ignore", "-q", rel, check=False).returncode == 0


def config_get(repo: Path, key: str) -> str | None:
    proc = run(repo, "config", "--get", key, check=False, harden=False)
    value = proc.stdout.decode("utf-8", errors="replace").strip()
    return value if proc.returncode == 0 and value else None


def skip_worktree(repo: Path) -> list[str]:
    out = run(repo, "ls-files", "-v", "--", ".github").stdout.decode("utf-8", errors="replace")
    return [ln[2:] for ln in out.splitlines() if ln.startswith("S ")]
