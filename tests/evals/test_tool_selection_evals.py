from __future__ import annotations
import pytest
from pathlib import Path

def test_scn_tool_01_context_mode_precedence_in_governance(repo_root):
    """SCN-TOOL-01: Garante que CLAUDE.md e copilot-instructions determinam precedência estrita de context-mode (R-008/R-056)."""
    claude_md = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    assert "R-008" in claude_md, "CLAUDE.md deve consolidar R-008 (Think in Code via context-mode)."
    assert "R-056" in claude_md, "CLAUDE.md deve consolidar R-056 (Precedência Mandatória de Context Mode)."
    assert "ctx_execute" in claude_md, "CLAUDE.md deve determinar uso de ctx_execute."

def test_scn_tool_02_single_turn_batching_rule_in_governance(repo_root):
    """SCN-TOOL-01: Garante que a governança proíbe tool chaining sequencial (R-046 / R-059)."""
    claude_md = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    assert "R-046" in claude_md, "CLAUDE.md deve consolidar R-046 (Single-Turn Batching)."
    assert "R-059" in claude_md, "CLAUDE.md deve consolidar R-059 (Plan-Then-Batch Global e Limiar >= 2)."

def test_scn_tool_03_turn_budget_limit_compliance(repo_root):
    """SCN-TOOL-03: Garante que o teto de 5 tool turns com Circuit Breaker no 4º turno é normatizado (R-060)."""
    claude_md = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")
    assert "R-060" in claude_md, "CLAUDE.md deve consolidar R-060 (Teto Rígido de Tool Turns <= 5)."
    assert "Circuit Breaker" in claude_md, "CLAUDE.md deve estabelecer acionamento de Circuit Breaker."
