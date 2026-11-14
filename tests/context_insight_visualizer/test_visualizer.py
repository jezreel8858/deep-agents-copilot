import json
import sqlite3
import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
GEN_DIR = ROOT_DIR / "tools" / "context-insight-visualizer" / "generator"
if str(GEN_DIR) in sys.path:
    sys.path.remove(str(GEN_DIR))
sys.path.insert(0, str(GEN_DIR))
for _mod in ("extractor", "insights_engine", "template_bundler"):
    sys.modules.pop(_mod, None)

from extractor import ContextDataExtractor, discover_v2_databases, _epoch_to_iso, _is_doctor_synthetic  # noqa: E402
from insights_engine import InsightsEngine  # noqa: E402
from template_bundler import TemplateBundler  # noqa: E402


def test_v2_discovery_env_and_backup_exclusion(v2_data_root: Path, monkeypatch: pytest.MonkeyPatch):
    """Valida descoberta via CONTEXT_MODE_DATA_DIR e exclusão de backups/v1-aside-*."""
    monkeypatch.setenv("CONTEXT_MODE_DATA_DIR", str(v2_data_root))
    roots, dbs = discover_v2_databases()
    assert len(roots) == 1
    assert roots[0] == v2_data_root
    assert len(dbs) == 1
    assert dbs[0].parent.name == "a1b2c3d4e5f60718"
    assert not any("backups" in str(p) for p in dbs)


def test_v2_extraction_events_cost_and_doctor_filter(v2_data_root: Path, monkeypatch: pytest.MonkeyPatch):
    """Valida extração completa v2.1.10: sessões, filtro do doctor, decisões, MCP tools, savings e chunks FTS5."""
    monkeypatch.setenv("CONTEXT_MODE_DATA_DIR", str(v2_data_root))
    extractor = ContextDataExtractor()
    data = extractor.extract_all()

    meta = data["meta"]
    assert meta["contextModeVersion"] == "2.1.10"
    assert meta["schemaVersion"] == 6
    assert meta["sessionDbsCount"] == 1
    assert meta["doctorEventsFiltered"] == 1
    assert "a1b2c3d4e5f60718" in meta["projectKeys"]

    # Doctor session must be filtered out
    sessions = data["sessions"]
    assert len(sessions) == 1
    s = sessions[0]
    assert s["sessionId"] == "sess-real-001"
    assert s["eventCount"] == 6
    assert s["compactCount"] == 0
    assert s["durationMin"] == 1.0  # 60,000 ms = 1.0 min

    # Events summary
    ev = data["eventsSummary"]
    assert ev["totalEvents"] == 6
    assert ev["totalPrompts"] == 1
    assert ev["totalErrors"] == 1
    assert ev["totalWrites"] == 1
    assert ev["totalReads"] >= 2
    assert len(ev["decisions"]) == 1
    assert "Aprovar e Executar" in ev["decisions"][0]["text"]
    assert any(m["tool"] == "ctx_execute" for m in ev["mcpTools"])

    # Cost / savings calculation: (48000 - 1200) + (8000 - 800) = 54000 bytes -> 13500 tokens
    stats = data["statsPid"]
    assert stats["sandboxBytes"] == 56000
    assert stats["bytesReturned"] == 2000
    assert stats["bytesSaved"] == 54000
    assert stats["tokensSavedLifetime"] == 13500

    # Content / FTS5 chunks
    content = data["content"]
    assert content["totalSources"] == 1
    assert content["totalChunks"] == 2
    assert content["totalSizeBytes"] == 4096
    assert len(content["sources"]) == 1
    src_id = content["sources"][0]["id"]
    assert src_id in content["chunksBySource"]
    assert content["chunksBySource"][src_id][0]["title"] == "Architecture Overview"


def test_v2_insights_engine_and_html_bundle(v2_data_root: Path, tmp_path: Path):
    """Valida que InsightsEngine gera KPIs e cards v2 sem falso-positivo de compactação e empacota HTML standalone."""
    extractor = ContextDataExtractor(data_dir=str(v2_data_root))
    raw = extractor.extract_all()
    engine = InsightsEngine(raw)
    payload = engine.build_payload()

    kpis = payload["kpis"]
    assert kpis["totalSessions"] == 1
    assert kpis["tokensSaved"] == 13500
    assert any(c["id"] == "v2-sandbox-offloading" for c in payload["insightsActions"])

    template_dir = ROOT_DIR / "tools" / "context-insight-visualizer" / "template"
    html_text = TemplateBundler.bundle_standalone_html(template_dir, payload)
    out_html = tmp_path / "context-insight.html"
    out_html.write_text(html_text, encoding="utf-8")
    assert out_html.is_file()
    assert "AppState" in html_text
    assert "sess-real-001" in html_text
    assert "context-mode-doctor-hook-runs" not in html_text


def test_legacy_v1_fallback(tmp_path: Path):
    """Garante que a flag legacy_v1=True continua lendo bancos v1 (session_meta, session_events, stats-pid)."""
    sessions_dir = tmp_path / "sessions"
    content_dir = tmp_path / "content"
    sessions_dir.mkdir()
    content_dir.mkdir()

    db_file = sessions_dir / "sess1.db"
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE session_meta (session_id TEXT, project_dir TEXT, started_at TEXT, last_event_at TEXT, event_count INT, compact_count INT)"
    )
    cur.execute(
        "INSERT INTO session_meta VALUES ('v1-sess-01', '/repo/demo', '2026-05-01T10:00:00Z', '2026-05-01T10:30:00Z', 5, 2)"
    )
    cur.execute(
        "CREATE TABLE session_events (id INTEGER PRIMARY KEY, session_id TEXT, type TEXT, category TEXT, priority INT, data TEXT, timestamp TEXT)"
    )
    cur.execute(
        "INSERT INTO session_events (session_id, type, category, priority, data, timestamp) VALUES ('v1-sess-01', 'user_prompt', 'prompt', 1, 'hello', '2026-05-01T10:00:00Z')"
    )
    conn.commit()
    conn.close()

    stats_file = sessions_dir / "stats-pid-1234.json"
    stats_file.write_text(
        json.dumps({"total_calls": 3, "bytes_returned": 900, "tokens_saved_lifetime": 4500, "dollars_saved_lifetime": 0.05, "by_tool": {"ctx_execute": {"calls": 3, "bytes": 900}}}),
        encoding="utf-8",
    )

    extractor = ContextDataExtractor(
        sessions_dir=str(sessions_dir),
        content_dir=str(content_dir),
        legacy_v1=True,
    )
    data = extractor.extract_all()
    assert data["meta"]["contextModeVersion"] == "legacy"
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["sessionId"] == "v1-sess-01"
    assert data["sessions"][0]["compactCount"] == 2
    assert data["statsPid"]["tokensSavedLifetime"] == 4500
