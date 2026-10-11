"""compute_diff: campos alterados, novos, ausentes, aposentadoria."""

from __future__ import annotations

import datetime as dt

from tools.model_allowlist import refresh as r


def _diff(allowlist_data, valid_html, today):
    return r.compute_diff(allowlist_data, r.parse_supported_models(valid_html), today)


def test_changed_fields_reported(allowlist_data, valid_html, today):
    d = _diff(allowlist_data, valid_html, today)
    got = {(c.model, c.field, c.old, c.new) for c in d.changes}
    assert got == {
        ("Claude Haiku 5.5", "retirement_date", None, "2026-10-20"),
        ("Gemini 3.8 Flash", "status", "ga", "preview"),
        ("Gemini 3.8 Flash", "retirement_date", None, "2026-12-31"),
    }
    assert d.has_changes


def test_new_models_listed_only_with_status_and_provider(allowlist_data, valid_html, today):
    d = _diff(allowlist_data, valid_html, today)
    assert sorted(m.name for m in d.added) == ["Brand New Model", "GPT Nova 1"]
    assert any("Mystery Model" in w for w in d.warnings)


def test_missing_on_page_only_reported_never_special(allowlist_data, load_html, today):
    page = r.parse_supported_models(load_html("reordered_columns.html"))  # sem Auto/Legacy
    d = r.compute_diff(allowlist_data, page, today)
    assert d.missing_on_page == ["Legacy Model 1"]
    assert "Auto" not in d.missing_on_page


def test_auto_special_status_is_intact(allowlist_data, valid_html, today):
    d = _diff(allowlist_data, valid_html, today)  # página traz Auto como GA
    assert all(c.model != "Auto" for c in d.changes)


def test_retiring_soon_and_overdue(allowlist_data, valid_html, today):
    d = _diff(allowlist_data, valid_html, today)
    by_name = {n: (date, days) for n, date, days in d.retiring_soon}
    assert by_name["Claude Haiku 5.5"] == ("2026-10-20", 5)
    assert by_name["Legacy Model 1"][1] < 0  # vencida (2026-09-01)
    assert "Gemini 3.8 Flash" not in by_name  # 77 dias
    report = r.render_report(d, "t", today, False)
    assert "VENCIDA" in report and "em 5 dia(s)" in report


def test_retirement_window_boundary_30_vs_31_days(today):
    def pm(date):
        return r.ParsedPage(models={"x": r.PageModel("X", "openai", "ga", date, "GA")})

    al = {"models": [{"name": "X", "status": "ga", "retirement_date": None}]}
    on = (today + dt.timedelta(days=30)).isoformat()
    off = (today + dt.timedelta(days=31)).isoformat()
    assert [t[2] for t in r.compute_diff(al, pm(on), today).retiring_soon] == [30]
    assert r.compute_diff(al, pm(off), today).retiring_soon == []


def test_invalid_retirement_date_warns(today):
    al = {"models": [{"name": "X", "status": "ga", "retirement_date": "garbage"}]}
    d = r.compute_diff(al, r.ParsedPage(), today)
    assert any("inválida" in w for w in d.warnings)


def test_no_changes_when_in_sync(today):
    al = {"models": [{"name": "X", "status": "ga", "retirement_date": None}]}
    page = r.ParsedPage(models={"x": r.PageModel("X", "openai", "ga", None, "GA")})
    d = r.compute_diff(al, page, today)
    assert not d.has_changes and d.missing_on_page == []


def test_check_mode_does_not_write(allowlist_file, valid_html, today, tmp_path):
    before = allowlist_file.read_bytes()
    report_path = tmp_path / "out" / "report.md"
    code, report = r.run(
        allowlist_path=allowlist_file, html=valid_html, source="fixture",
        write=False, report_path=report_path, today=today,
    )
    assert code == 0
    assert allowlist_file.read_bytes() == before
    assert report_path.read_text(encoding="utf-8") == report
    assert "somente relatório" in report
