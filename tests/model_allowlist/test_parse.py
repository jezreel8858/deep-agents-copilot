"""Parse do HTML da página oficial."""

from __future__ import annotations

import pytest

from tools.model_allowlist import refresh as r


def test_parse_valid_page_main_and_retirement_tables(valid_html):
    page = r.parse_supported_models(valid_html)
    haiku = page.models["claude haiku 5.5"]
    assert (haiku.provider, haiku.status) == ("anthropic", "ga")
    assert haiku.retirement_date == "2026-10-20"
    assert page.retirement_table_found is True


def test_parse_status_ga_preview_and_long_forms(valid_html):
    models = r.parse_supported_models(valid_html).models
    assert models["gemini 3.8 flash"].status == "preview"
    assert models["brand new model"].status == "ga"  # "Generally available"
    assert models["auto"].status == "ga"


def test_parse_footnote_markers_and_suffix_are_stripped(valid_html):
    models = r.parse_supported_models(valid_html).models
    assert models["gemini 3.8 flash"].name == "Gemini 3.8 Flash"  # [1]
    assert models["brand new model"].name == "Brand New Model"  # dagger
    # status vindo do sufixo "(preview)" quando a coluna é "—"
    assert models["gpt nova 1"].status == "preview"
    assert models["gpt nova 1"].name == "GPT Nova 1"


def test_parse_unrecognized_status_warns_and_keeps_none(valid_html):
    page = r.parse_supported_models(valid_html)
    assert page.models["mystery model"].status is None
    assert any("Mystery Model" in w for w in page.warnings)


def test_parse_retirement_without_main_row_warns(valid_html):
    page = r.parse_supported_models(valid_html)
    assert page.models["fantasma 9"].retirement_date == "2026-11-01"
    assert page.models["fantasma 9"].status is None
    assert any("Fantasma 9" in w for w in page.warnings)


def test_parse_ignores_tables_inside_script(valid_html):
    page = r.parse_supported_models(valid_html)
    assert "model" not in page.models  # cabeçalho dentro de <script> nunca vira modelo


def test_parse_reordered_columns(load_html):
    page = r.parse_supported_models(load_html("reordered_columns.html"))
    assert set(page.models) == {"claude haiku 5.5", "gemini 3.8 flash"}
    assert page.models["claude haiku 5.5"].provider == "anthropic"
    assert page.models["gemini 3.8 flash"].status == "preview"
    assert page.models["gemini 3.8 flash"].name == "Gemini 3.8 Flash"
    assert page.retirement_table_found is False


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("GA", "ga"),
        ("Generally available", "ga"),
        ("Public preview", "preview"),
        ("Beta", "preview"),
        ("", None),
        (None, None),
        ("Coming soon", None),
    ],
)
def test_normalize_status_boundaries(raw, expected):
    assert r.normalize_status(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2026-10-20", "2026-10-20"),
        ("October 20, 2026", "2026-10-20"),
        ("Oct 20, 2026", "2026-10-20"),
        ("20 October 2026", "2026-10-20"),
        pytest.param("2026-02-30", None),
        ("sem data", None),
        ("", None),
    ],
)
def test_parse_date_formats(raw, expected):
    assert r.parse_date(raw) == expected


def test_layout_changed_lists_headers(load_html):
    with pytest.raises(r.LayoutChangedError) as exc:
        r.parse_supported_models(load_html("layout_changed.html"))
    msg = str(exc.value)
    assert "[Foo, Bar, Baz]" in msg
    assert r.LayoutChangedError.exit_code == r.EXIT_LAYOUT == 2


def test_layout_changed_missing_status_column(load_html):
    with pytest.raises(r.LayoutChangedError) as exc:
        r.parse_supported_models(load_html("missing_status_column.html"))
    assert "[Model, Provider]" in str(exc.value)


@pytest.mark.parametrize("html", ["", "<html></html>"])
def test_layout_changed_without_tables(html, load_html):
    with pytest.raises(r.LayoutChangedError):
        r.parse_supported_models(html)
    with pytest.raises(r.LayoutChangedError):
        r.parse_supported_models(load_html("no_tables.html"))


def test_cli_layout_changed_exit_2(tmp_path, allowlist_file, capsys):
    html = tmp_path / "bad.html"
    html.write_text("<table><tr><th>Foo</th><th>Bar</th></tr></table>", encoding="utf-8")
    before = allowlist_file.read_bytes()
    code = r.main(
        ["--write", "--from-file", str(html), "--allowlist", str(allowlist_file), "--no-report-file"]
    )
    assert code == 2
    assert "Foo, Bar" in capsys.readouterr().err
    assert allowlist_file.read_bytes() == before
