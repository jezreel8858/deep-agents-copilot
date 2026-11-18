"""Testes da isenção de agents raiz em sync_router_return.sync_all_agents."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.agent_router_return_sync import sync_router_return as mod

STUB_NO_SECTION = "# Stub\nSem a secao de retorno.\n"


def _run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str):
    (tmp_path / name).write_text(STUB_NO_SECTION, encoding="utf-8")
    monkeypatch.setattr(mod, "AGENTS_DIR", tmp_path)
    report, _ = mod.sync_all_agents("check")
    return report


def test_agent_root_is_exempt(tmp_path, monkeypatch):
    report = _run(tmp_path, monkeypatch, "agent-root.agent.md")
    assert report.errors == []
    assert report.total_scanned == 0


def test_agent_router_remains_exempt(tmp_path, monkeypatch):
    report = _run(tmp_path, monkeypatch, "agent-router.agent.md")
    assert report.errors == []
    assert report.total_scanned == 0


def test_regular_agent_is_not_exempt(tmp_path, monkeypatch):
    report = _run(tmp_path, monkeypatch, "some-agent.agent.md")
    assert report.total_scanned == 1
    assert len(report.errors) == 1
    assert "some-agent.agent.md" in report.errors[0]


def test_exemption_matches_exact_name(tmp_path, monkeypatch):
    report = _run(tmp_path, monkeypatch, "my-agent-root.agent.md")
    assert report.total_scanned == 1
    assert len(report.errors) == 1


def test_exempt_constant_value():
    assert mod.ROUTER_RETURN_EXEMPT_AGENTS == frozenset(
        {"agent-router.agent.md", "agent-root.agent.md"}
    )
