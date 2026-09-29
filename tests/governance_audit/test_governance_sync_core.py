"""
Testes unitários para o núcleo de sincronização de governança (tools/governance_sync/core.py).
"""

from __future__ import annotations

import pytest
from tools.governance_sync.core import (
    create_sync_parser,
    parse_sync_options,
    SyncOptions,
    SyncReport,
    compute_unified_diff,
)


def test_parser_default_is_check():
    parser = create_sync_parser("test")
    opts = parse_sync_options(parser, [])
    assert opts.mode == "check"
    assert opts.is_check is True
    assert opts.is_apply is False
    assert opts.is_dry_run is False


def test_parser_flags_resolution():
    parser = create_sync_parser("test")
    assert parse_sync_options(parser, ["--apply"]).is_apply is True
    assert parse_sync_options(parser, ["--dry-run"]).is_dry_run is True
    assert parse_sync_options(parser, ["--check"]).is_check is True


def test_sync_report_exit_codes():
    # Sem drift
    report_clean = SyncReport(total_scanned=10, drifted=[])
    assert report_clean.compute_exit_code("check") == 0
    assert report_clean.compute_exit_code("dry-run") == 0
    assert report_clean.compute_exit_code("apply") == 0

    # Com drift
    report_drift = SyncReport(total_scanned=10, drifted=["agent-x"])
    assert report_drift.compute_exit_code("check") == 1
    assert report_drift.compute_exit_code("dry-run") == 0
    assert report_drift.compute_exit_code("apply") == 0

    # Com erro
    report_err = SyncReport(total_scanned=10, errors=["Syntax Error"])
    assert report_err.compute_exit_code("check") == 1
    assert report_err.compute_exit_code("apply") == 1


def test_compute_unified_diff():
    orig = "line1\nline2\n"
    mod = "line1\nline2 modified\n"
    diff = compute_unified_diff(orig, mod, "test.md")
    assert "--- a/test.md" in diff
    assert "+++ b/test.md" in diff
    assert "-line2" in diff
    assert "+line2 modified" in diff
