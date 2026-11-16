from __future__ import annotations

import re
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = REPO_ROOT / ".github" / "prompts" / "synth-waves.prompt.md"
_PRECOMMIT_R044_PATH_RE = re.compile(
    r"([A-Za-z]:\\(Users|workspace)|/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/)"
)


def _read_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _parse_frontmatter(content: str) -> dict:
    assert content.startswith("---\n"), "Frontmatter YAML ausente no inicio do prompt"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Delimitador de fechamento do frontmatter YAML ausente"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict), "Frontmatter YAML deve ser um mapeamento"
    return data


def test_deve_proibir_run_in_terminal_no_frontmatter_synth_waves() -> None:
    content = _read_prompt()
    frontmatter = _parse_frontmatter(content)
    tools = frontmatter.get("tools", [])
    assert isinstance(tools, list) and len(tools) > 0
    assert "run_in_terminal" not in tools
    assert "context-mode/ctx_execute" in tools


def test_deve_exigir_particionamento_anti_timeout_e_background() -> None:
    content = _read_prompt()
    assert "--pending" in content
    assert "--limit 3" in content
    assert "background: true" in content


def test_deve_exigir_cwd_explicito_e_resolucao_token_sdk() -> None:
    content = _read_prompt()
    assert "cwd" in content
    assert "${workspaceFolder}" in content or "WORKSPACE_ROOT" in content
    assert "COPILOT_SDK_TOKEN" in content
    assert "gh auth token" in content
    assert not _PRECOMMIT_R044_PATH_RE.search(content), (
        "synth-waves.prompt.md nao pode conter caminhos locais absolutos (R-044)"
    )

def test_deve_exigir_reconciliacao_de_runs_orfaos_antes_de_synth_diagnose() -> None:
    content = _read_prompt()
    assert "reconciliar_runs_orfaos" in content
    assert "--use-case synth-diagnose" in content
    idx_reconcile = content.index("reconciliar_runs_orfaos")
    idx_diagnose = content.index("--use-case synth-diagnose")
    assert idx_reconcile < idx_diagnose
