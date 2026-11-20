"""Testes determinísticos do Empacotador por Stack & Exportador Multi-Runtime (tools/export_bundle.py — P8)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.export_bundle import discover_available_stacks, export_bundle


def test_discover_available_stacks_finds_canonical_ecosystems() -> None:
    stacks = discover_available_stacks()
    for expected in ("spring-boot", "angular", "python", "react", "ejb", "struts", "database"):
        assert expected in stacks, f"Stack '{expected}' não descoberta em .github/agents/"


def test_export_spring_boot_bundle_for_all_runtimes(tmp_path: Path) -> None:
    # 1. Copilot
    copilot_out = tmp_path / "spring-copilot"
    res_copilot = export_bundle(stack="spring-boot", target="copilot", output_dir=copilot_out, create_zip=True)
    assert res_copilot["verdict"] == "PASS"
    assert (copilot_out / "bundle-manifest.json").exists()
    assert (copilot_out / ".github" / "agents" / "backend" / "spring-boot" / "spring-boot-router.agent.md").exists()
    assert (copilot_out / ".github" / "skills" / "spring-boot-implementation-patterns" / "SKILL.md").exists()
    assert Path(res_copilot["zip_archive"]).exists()

    # 2. Claude Code
    claude_out = tmp_path / "spring-claude"
    res_claude = export_bundle(stack="spring-boot", target="claude-code", output_dir=claude_out)
    assert res_claude["verdict"] == "PASS"
    assert (claude_out / "CLAUDE.md").exists()
    assert (claude_out / ".claude" / "agents" / "spring-boot-developer.md").exists()
    assert (claude_out / ".claude" / "skills" / "agent-contracts" / "SKILL.md").exists()

    # 3. Cursor (.mdc)
    cursor_out = tmp_path / "spring-cursor"
    res_cursor = export_bundle(stack="spring-boot", target="cursor", output_dir=cursor_out)
    assert res_cursor["verdict"] == "PASS"
    mdc_file = cursor_out / ".cursor" / "rules" / "agent-spring-boot-developer.mdc"
    assert mdc_file.exists()
    assert "alwaysApply: false" in mdc_file.read_text(encoding="utf-8")

    manifest = json.loads((copilot_out / "bundle-manifest.json").read_text(encoding="utf-8"))
    assert manifest["stack"] == "spring-boot"
    assert "spring-boot-developer" in manifest["agents_included"]