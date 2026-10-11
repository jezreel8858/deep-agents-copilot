"""Helpers compartilhados dos testes de tests/model_profiles (sem testes aqui).

Nenhum helper toca o repositorio real: tudo ocorre em repositorios git temporarios.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

BOM = b"\xef\xbb\xbf"
STATE_REL = ".model-profiles/state.json"
LOCK_REL = ".model-profiles/lock"

OPUS = "Claude Opus 5.5"
SONNET = "Claude Sonnet 5.5"
HAIKU = "Claude Haiku 5.5"
FLASH = "Gemini 3.8 Flash"

ECON_WARNING = "Roteamento e codigo podem perder precisao."


class SimulatedCrash(BaseException):
    """Simula kill do processo (BaseException: nao e capturada por `except Exception`)."""


def load(name: str):
    """Import tardio: a ausencia da implementacao falha o TESTE (red), nao a coleta."""
    return importlib.import_module(f"tools.model_profiles.{name}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8"
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"git {args} falhou: {proc.stderr}")
    return proc.stdout


def run_cli(capsys, repo: Path, *args: str) -> tuple[int, str]:
    """Executa cli.main(['--repo', repo, *args]) e devolve (exit_code, stdout+stderr)."""
    cli = load("cli")
    capsys.readouterr()
    try:
        code = cli.main(["--repo", str(repo), *args])
    except SystemExit as exc:  # argparse
        code = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return code, captured.out + captured.err


def read_state(repo: Path) -> dict:
    return json.loads((repo / STATE_REL).read_text(encoding="utf-8"))


def write_lock(repo: Path, pid: int, timestamp: float) -> None:
    path = repo / LOCK_REL
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"pid": pid, "timestamp": timestamp}), encoding="utf-8")


_DEAD_PID: list[int] = []
def dead_pid() -> int:
    """PID de processo ja encerrado; spawn (~0.6s no Windows) feito UMA vez por sessao."""
    if not _DEAD_PID:
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        _DEAD_PID.append(proc.pid)
    return _DEAD_PID[0]


@contextlib.contextmanager
def crash_after_writes(n: int):
    """Apos `n` escritas bem-sucedidas, a (n+1)-esima `writer.atomic_write` simula crash."""
    writer = load("writer")
    real = writer.atomic_write
    calls = {"n": 0}

    def fake(path, data, *a, **k):
        if calls["n"] >= n:
            raise SimulatedCrash()
        calls["n"] += 1
        return real(path, data, *a, **k)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(writer, "atomic_write", fake)
        yield


@contextlib.contextmanager
def record_writes():
    """Registra todos os caminhos passados a writer.atomic_write (e ainda grava)."""
    writer = load("writer")
    real = writer.atomic_write
    paths: list[Path] = []

    def spy(path, data, *a, **k):
        paths.append(Path(path))
        return real(path, data, *a, **k)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(writer, "atomic_write", spy)
        yield paths


# ---------------------------------------------------------------- fixture repo
def agent_text(name: str, model: str, *, eol: str = "\n", bom: bool = False,
               exception: str | None = None) -> bytes:
    lines = ["---", f"name: {name}", "description: >-", f"  Agente sintetico {name}.",
             f'model: "{model}"']
    if exception:
        lines.append(f'model_exception_reason: "{exception}"')
    lines += ["tools: ['file_search']", "handoffs:", "  - label: x",
              '    model: "decoy-nested"', "---", f"# Corpo de {name}",
              'model: "decoy-body"', "texto final", ""]
    data = eol.join(lines).encode("utf-8")
    return (BOM + data) if bom else data


def prompt_text(name: str, model: str, *, eol: str = "\n") -> bytes:
    lines = ["---", f"name: {name}", "description: prompt sintetico", "agent: 'agent'",
             f'model: "{model}"', "---", f"corpo {name}", 'model: "decoy-body"', ""]
    return eol.join(lines).encode("utf-8")


# relpath -> (chave canonica, bytes)
def build_targets() -> dict[str, tuple[str, bytes]]:
    return {
        ".github/agents/agent-router.agent.md": ("agent-router", agent_text("agent-router", SONNET)),
        ".github/agents/tech-solution-architect.agent.md": (
            "tech-solution-architect",
            agent_text("tech-solution-architect", OPUS,
                       exception="R-021: raciocinio critico avancado")),
        ".github/agents/python-developer.agent.md": (
            "python-developer", agent_text("python-developer", SONNET, eol="\r\n")),
        ".github/agents/docs-engineer.agent.md": (
            "docs-engineer", agent_text("docs-engineer", FLASH, eol="\r\n", bom=True)),
        ".github/prompts/commit.prompt.md": ("prompt:commit", prompt_text("commit", FLASH)),
        ".github/prompts/plan.prompt.md": (
            "prompt:plan", prompt_text("plan", SONNET, eol="\r\n")),
    }


# mudancas esperadas ao aplicar `economico` (relpath -> (original, variante))
ECON_CHANGES = {
    ".github/agents/agent-router.agent.md": (SONNET, HAIKU),
    ".github/agents/tech-solution-architect.agent.md": (OPUS, SONNET),
    ".github/agents/python-developer.agent.md": (SONNET, HAIKU),
    ".github/prompts/plan.prompt.md": (SONNET, HAIKU),
}
ECON_UNCHANGED = [
    ".github/agents/docs-engineer.agent.md",
    ".github/prompts/commit.prompt.md",
]
BALANCEADO_CHANGES = {
    ".github/agents/tech-solution-architect.agent.md": (OPUS, SONNET),
}


def expected_bytes(original: bytes, old: str, new: str) -> bytes:
    return original.replace(f'model: "{old}"'.encode(), f'model: "{new}"'.encode(), 1)


def allowlist_dict() -> dict:
    today = dt.date.today()

    def m(name, status="ga", pinnable=True, rank=None, retirement=None, provider="x"):
        return {"name": name, "provider": provider, "status": status, "pinnable": pinnable,
                "retirement_date": retirement, "cost": {"label": "n/a"}, "cost_rank": rank}

    return {
        "schema_version": 1,
        "verified_at": today.isoformat(),
        "freshness_days": 30,
        "source": "fixture",
        "models": [
            m("Auto", status="special", pinnable=False),
            m(HAIKU, rank=1), m(FLASH, rank=2), m("Grok 4.7", rank=3),
            m(SONNET, rank=4), m("GPT-6.1 Sol", rank=5), m(OPUS, rank=6),
            m("Retired Model 1", status="retired", rank=2),
            m("Deprecated Model 1", status="deprecated", rank=2),
            m("Sunset Model 1", rank=2, retirement=(today + dt.timedelta(days=10)).isoformat()),
            m("NoRank Model 1", rank=None),
        ],
    }


def profiles_dict() -> dict:
    return {
        "schema_version": 1,
        "tier_map": {
            "premium": ["tech-solution-architect"],
            "orchestration": ["agent-router"],
            "standard": ["python-developer", "prompt:plan"],
            "light": ["docs-engineer", "prompt:commit"],
        },
        "profiles": {
            "default": {"description": "Canonico", "tiers": {
                "premium": OPUS, "orchestration": SONNET, "standard": SONNET, "light": FLASH}},
            "balanceado": {"extends": "default", "description": "Premium em Sonnet",
                           "quality_warning": "Arquitetura perde raciocinio premium.",
                           "tiers": {"premium": SONNET}},
            "economico": {"extends": "balanceado", "description": "Rebaixa orquestracao e standard",
                          "quality_warning": ECON_WARNING,
                          "tiers": {"orchestration": HAIKU, "standard": HAIKU}},
        },
    }


def graph_dict() -> dict:
    nodes = ["agent-router", "tech-solution-architect", "python-developer",
             "docs-engineer", "prompt-structuring"]
    edges = [("agent-router", "python-developer"), ("agent-router", "tech-solution-architect"),
             ("agent-router", "prompt-structuring")]
    return {"version": "1.0", "nos": [{"id": n, "tipo": "downstream"} for n in nodes],
            "arestas": [{"de": a, "para": b, "prioridade": 1} for a, b in edges]}


def _dump(path: Path, data: dict) -> None:
    path.write_bytes(yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode("utf-8"))


def commit_all(repo: Path, msg: str = "chore: fixture") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def make_repo(root: Path, *, ignore_state_dir: bool = True) -> Path:
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "--template=")  # sem hooks .sample (menos arquivos)
    with (repo / ".git" / "config").open("a", encoding="utf-8", newline="\n") as fh:  # 1 chamada git a menos por chave
        fh.write("[user]\n\tname = T\n\temail = t@t\n[commit]\n\tgpgsign = false\n"
                 "[core]\n\tautocrlf = false\n\tsafecrlf = false\n")
    for rel, (_, data) in build_targets().items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    _dump(repo / ".github/agents/catalog.yaml", {"version": "1.0", "agents": {
        "agent-router": {"model": SONNET}}})
    _dump(repo / ".github/agents/routing-graph.yaml", graph_dict())
    _dump(repo / "model-allowlist.yaml", allowlist_dict())
    _dump(repo / "model-profiles.yaml", profiles_dict())
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    if ignore_state_dir:
        (repo / ".gitignore").write_text(".model-profiles/\n", encoding="utf-8")
    commit_all(repo, "initial")
    return repo


def add_profile(repo: Path, name: str, spec: dict) -> None:
    path = repo / "model-profiles.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["profiles"][name] = spec
    _dump(path, data)
    git(repo, "commit", "-qam", f"profile {name}")  # arquivo ja rastreado: 1 spawn em vez de 2


def edit_allowlist(repo: Path, fn) -> None:
    path = repo / "model-allowlist.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    fn(data)
    _dump(path, data)
    git(repo, "commit", "-qam", "allowlist")  # arquivo ja rastreado: 1 spawn em vez de 2


def head_bytes(repo: Path, rel: str) -> bytes:
    return subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=repo, capture_output=True,
                          check=True).stdout


def protected_hashes(repo: Path) -> dict[str, str]:
    rels = (".github/agents/catalog.yaml", ".github/agents/routing-graph.yaml")
    return {r: sha256((repo / r).read_bytes()) for r in rels}


def now() -> float:
    return time.time()

def fast_clone(template: Path, dest: Path) -> Path:
    """Clona o repo template SEM copytree do .git/objects: copia so os poucos arquivos de
    metadados do .git (HEAD, config, index, refs) + worktree e liga os objetos por
    `objects/info/alternates` (sem git spawn; ~10x mais barato que copytree no Windows)."""
    dest.mkdir(parents=True)
    t_git = template / ".git"
    for src in template.rglob("*"):
        rel = src.relative_to(template)
        if rel.parts[0] == ".git" and (rel.parts[1:2] == ("objects",)):
            continue
        out = dest / rel
        if src.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(src.read_bytes())
    info = dest / ".git" / "objects" / "info"
    info.mkdir(parents=True)
    (dest / ".git" / "objects" / "pack").mkdir()
    (info / "alternates").write_bytes(((t_git / "objects").as_posix() + "\n").encode())  # LF: git rejeita CRLF
    return dest
