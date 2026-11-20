"""Testes determinísticos dos Boundary Quality Gates no Git (.githooks/pre-commit e pre-push — P3)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PRE_COMMIT_SRC = REPO_ROOT / ".githooks" / "pre-commit"
PRE_PUSH_SRC = REPO_ROOT / ".githooks" / "pre-push"


def _resolve_git_bash() -> str | None:
    git_bin = shutil.which("git")
    if git_bin:
        git_path = Path(git_bin).resolve()
        for candidate in (
            git_path.parents[1] / "bin" / "bash.exe",
            git_path.parents[1] / "usr" / "bin" / "bash.exe",
        ):
            if candidate.exists():
                return str(candidate)
    return shutil.which("bash")


GIT_BASH = _resolve_git_bash()


def _setup_git_repo_with_hooks(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=tmp_path, check=True)

    hooks_dir = tmp_path / ".githooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "pre-commit").write_bytes(PRE_COMMIT_SRC.read_bytes())
    (hooks_dir / "pre-push").write_bytes(PRE_PUSH_SRC.read_bytes())

    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: init"], cwd=tmp_path, check=True)
    return tmp_path


def _run_pre_commit(repo: Path) -> subprocess.CompletedProcess[str]:
    assert GIT_BASH is not None
    return subprocess.run(
        [GIT_BASH, ".githooks/pre-commit"],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


@pytest.mark.skipif(GIT_BASH is None, reason="Git Bash não disponível")
def test_pre_commit_blocks_invalid_plan_filename_and_rejected_status(tmp_path: Path) -> None:
    repo = _setup_git_repo_with_hooks(tmp_path)
    bad_plan = repo / "docs" / "plans" / "feature" / "PLAN-sem-timestamp.md"
    bad_plan.parent.mkdir(parents=True, exist_ok=True)
    bad_plan.write_text('---\nstatus: "REJECTED"\n---\n# Bad\n', encoding="utf-8")

    subprocess.run(["git", "add", str(bad_plan.relative_to(repo))], cwd=repo, check=True)
    res = _run_pre_commit(repo)
    combined = (res.stdout or "") + (res.stderr or "")
    assert res.returncode == 1
    assert "[R-064]" in combined


@pytest.mark.skipif(GIT_BASH is None, reason="Git Bash não disponível")
def test_pre_commit_blocks_agent_exceeding_instruction_budget(tmp_path: Path) -> None:
    repo = _setup_git_repo_with_hooks(tmp_path)
    bloated_agent = repo / ".github" / "agents" / "bloated.agent.md"
    bloated_agent.parent.mkdir(parents=True, exist_ok=True)
    bloated_agent.write_text("\n".join([f"linha {i}" for i in range(470)]), encoding="utf-8")

    subprocess.run(["git", "add", str(bloated_agent.relative_to(repo))], cwd=repo, check=True)
    res = _run_pre_commit(repo)
    combined = (res.stdout or "") + (res.stderr or "")
    assert res.returncode == 1
    assert "[R-066]" in combined


@pytest.mark.skipif(GIT_BASH is None, reason="Git Bash não disponível")
def test_pre_commit_approves_valid_r064_plan(tmp_path: Path) -> None:
    repo = _setup_git_repo_with_hooks(tmp_path)
    good_plan = repo / "docs" / "plans" / "feature" / "20261120-030000-valid-feature.md"
    good_plan.parent.mkdir(parents=True, exist_ok=True)
    good_plan.write_text(
        '---\nstatus: "APPROVED"\napproved: true\nallowed_files:\n  - "src/app.py"\n---\n# Valid\n',
        encoding="utf-8",
    )

    subprocess.run(["git", "add", str(good_plan.relative_to(repo))], cwd=repo, check=True)
    res = _run_pre_commit(repo)
    assert res.returncode == 0
