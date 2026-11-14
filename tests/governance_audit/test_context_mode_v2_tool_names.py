from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_V2_CTX_TOOLS = {
    "context-mode/ctx_execute",
    "context-mode/ctx_batch",
    "context-mode/ctx_index",
    "context-mode/ctx_search",
    "context-mode/ctx_resume",
    "context-mode/ctx_stats",
    "context-mode/ctx_doctor",
    "context-mode/ctx_upgrade",
    "context-mode/ctx_purge",
}

LEGACY_PATTERN = re.compile(
    r"\b(ctx_execute_file|ctx_batch_execute|ctx_fetch_and_index|CONTEXT_MODE_DIR|INSIGHT_SESSION_DIR|INSIGHT_CONTENT_DIR)\b"
)


def _iter_governed_files() -> list[Path]:
    targets: list[Path] = []
    scan_dirs = [
        REPO_ROOT / ".github" / "agents",
        REPO_ROOT / ".github" / "prompts",
        REPO_ROOT / ".github" / "skills",
        REPO_ROOT / ".github" / "hooks",
        REPO_ROOT / ".aiassistant",
        REPO_ROOT / ".config",
    ]
    for d in scan_dirs:
        if d.exists():
            for p in d.rglob("*"):
                if p.is_file() and p.suffix in {".md", ".json", ".ps1", ".sh", ".yaml", ".yml"}:
                    targets.append(p)
    for root_doc in ["CLAUDE.md", "AGENTS.md", "README.md", ".github/copilot-instructions.md"]:
        p = REPO_ROOT / root_doc
        if p.exists():
            targets.append(p)
    return targets


def _extract_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def test_no_legacy_v1_tokens_in_governed_artifacts() -> None:
    offenders: list[str] = []
    for path in _iter_governed_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith("docs/plans/") or rel == "CHANGELOG.md":
            continue
        content = path.read_text(encoding="utf-8")
        matches = sorted(set(LEGACY_PATTERN.findall(content)))
        if matches:
            offenders.append(f"{rel}: {matches}")
    assert not offenders, f"Tokens legados v1 encontrados:\n" + "\n".join(offenders)


def test_agent_and_prompt_tools_in_v2_allowlist() -> None:
    invalid: list[str] = []
    files = list((REPO_ROOT / ".github" / "agents").glob("*.agent.md")) + list(
        (REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")
    )
    for path in files:
        fm = _extract_frontmatter(path)
        tools = fm.get("tools") or []
        for tool in tools:
            if isinstance(tool, str) and tool.startswith("context-mode/"):
                if tool not in ALLOWED_V2_CTX_TOOLS:
                    invalid.append(f"{path.name}: {tool}")
    assert not invalid, f"Tools context-mode fora da allowlist v2 (9 tools): {invalid}"


def test_agents_with_ctx_execute_also_declare_ctx_batch() -> None:
    missing_batch: list[str] = []
    for path in sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")):
        fm = _extract_frontmatter(path)
        tools = set(fm.get("tools") or [])
        if "context-mode/ctx_execute" in tools and "context-mode/ctx_batch" not in tools:
            missing_batch.append(path.name)
    assert not missing_batch, f"Agents com ctx_execute devem declarar ctx_batch: {missing_batch}"


def test_intellij_setup_doc_has_v2_agent_flag_and_data_dir() -> None:
    setup_doc = REPO_ROOT / "docs" / "context" / "setup-context-mode-intellij.md"
    content = setup_doc.read_text(encoding="utf-8")
    assert "--agent copilot-cli" in content, "setup doc deve conter --agent copilot-cli"
    assert "CONTEXT_MODE_DATA_DIR" in content, "setup doc deve conter CONTEXT_MODE_DATA_DIR"
    assert not LEGACY_PATTERN.search(content), "setup doc não deve conter variáveis/tools v1 legadas"

def test_mcp_config_files_have_v2_agent_flag_and_no_legacy_env() -> None:
    mcp_files = [
        REPO_ROOT / ".config" / "idea_mcp.json",
        REPO_ROOT / ".config" / "cline_mcp_settings.json",
    ]
    for mcp_path in mcp_files:
        assert mcp_path.exists(), f"{mcp_path.relative_to(REPO_ROOT)} deve existir"
        raw = mcp_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        servers = data.get("servers") or data.get("mcpServers") or {}
        ctx_cfg = servers.get("context-mode") or {}
        args_joined = " ".join(str(a) for a in (ctx_cfg.get("args") or []))
        assert "--agent copilot-cli" in args_joined, (
            f"{mcp_path.name} deve passar '--agent copilot-cli' no context-mode v2"
        )
        env = ctx_cfg.get("env") or {}
        assert "CONTEXT_MODE_DATA_DIR" in env, (
            f"{mcp_path.name} deve definir CONTEXT_MODE_DATA_DIR no context-mode v2"
        )
        for legacy_key in (
            "SOURCE",
            "CONTEXT_MODE_IDLE_TIMEOUT_MS",
            "CONTEXT_MODE_DIR",
            "INSIGHT_SESSION_DIR",
            "INSIGHT_CONTENT_DIR",
        ):
            assert legacy_key not in env, (
                f"{mcp_path.name} não deve conter variável legada v1: {legacy_key}"
            )
        assert not LEGACY_PATTERN.search(raw), f"{mcp_path.name} não deve conter tokens v1 legados"
