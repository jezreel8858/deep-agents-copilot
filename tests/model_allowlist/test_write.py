"""--write: patch textual conservador, idempotência, EOL, patch inválido."""

from __future__ import annotations

import pytest
import yaml

from tools.model_allowlist import refresh as r

ALLOWED = {"status", "retirement_date"}


def _write(path, html, today, **kw):
    return r.run(
        allowlist_path=path, html=html, source="fixture", write=True,
        report_path=None, today=today, **kw,
    )


def _read(path) -> str:
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def test_write_updates_only_allowed_fields(allowlist_file, valid_html, today):
    before = yaml.safe_load(_read(allowlist_file))
    code, report = _write(allowlist_file, valid_html, today)
    assert code == 0 and "--write (aplicado)" in report
    after = yaml.safe_load(_read(allowlist_file))
    assert after["verified_at"] == today.isoformat()
    by = {m["name"]: m for m in after["models"]}
    assert by["Claude Haiku 5.5"]["retirement_date"] == "2026-10-20"
    assert by["Gemini 3.8 Flash"]["status"] == "preview"
    assert by["Gemini 3.8 Flash"]["retirement_date"] == "2026-12-31"
    for o in before["models"]:
        n = by[o["name"]]
        for key in set(o) | set(n):
            if key not in ALLOWED:
                assert o.get(key) == n.get(key), (o["name"], key)


def test_write_new_models_are_not_pinnable_and_without_cost(allowlist_file, valid_html, today):
    _write(allowlist_file, valid_html, today)
    by = {m["name"]: m for m in yaml.safe_load(_read(allowlist_file))["models"]}
    for name in ("Brand New Model", "GPT Nova 1"):
        m = by[name]
        assert m["pinnable"] is False and m["cost"] is None and m["cost_rank"] is None
    assert by["GPT Nova 1"]["status"] == "preview"
    assert by["Brand New Model"]["provider"] == "openai"


def test_write_never_removes_or_changes_cost_rank(allowlist_file, valid_html, today):
    before = {m["name"]: m["cost_rank"] for m in yaml.safe_load(_read(allowlist_file))["models"]}
    _write(allowlist_file, valid_html, today)
    after = {m["name"]: m["cost_rank"] for m in yaml.safe_load(_read(allowlist_file))["models"]}
    assert set(before) <= set(after)  # Legacy Model 1 ausente na página, mas preservado
    assert all(after[k] == v for k, v in before.items())


def test_write_auto_special_untouched(allowlist_file, valid_html, today):
    _write(allowlist_file, valid_html, today)
    auto = yaml.safe_load(_read(allowlist_file))["models"][0]
    assert (auto["name"], auto["status"], auto["pinnable"]) == ("Auto", "special", False)


def test_write_is_idempotent(allowlist_file, valid_html, today):
    _write(allowlist_file, valid_html, today)
    first = allowlist_file.read_bytes()
    code, report = _write(allowlist_file, valid_html, today)
    assert code == 0
    assert allowlist_file.read_bytes() == first
    assert "Nenhum" in report
    assert "novos modelos: 0" in report


def test_write_preserves_comments(allowlist_file, valid_html, today):
    _write(allowlist_file, valid_html, today)
    text = _read(allowlist_file)
    for marker in ("# comentário do Auto", "# seletor da IDE", "# sem data", "# comentário final", "# frescor global"):
        assert marker in text, marker


def test_write_preserves_lf_eol(allowlist_file, valid_html, today):
    _write(allowlist_file, valid_html, today)
    assert b"\r" not in allowlist_file.read_bytes()


def test_write_preserves_crlf_for_existing_entries(allowlist_file, allowlist_text, load_html, today):
    allowlist_file.write_bytes(allowlist_text.replace("\n", "\r\n").encode("utf-8"))
    # página só com mudanças em entradas existentes (sem novos modelos)
    html = load_html("reordered_columns.html")
    _write(allowlist_file, html, today)
    raw = allowlist_file.read_bytes()
    assert raw.count(b"\n") == raw.count(b"\r\n") > 0, "EOL misto"
    assert yaml.safe_load(raw.decode("utf-8"))["models"][2]["status"] == "preview"


def test_write_preserves_crlf_with_added_models(allowlist_file, allowlist_text, valid_html, today):
    allowlist_file.write_bytes(allowlist_text.replace("\n", "\r\n").encode("utf-8"))
    _write(allowlist_file, valid_html, today)
    raw = allowlist_file.read_bytes()
    assert raw.count(b"\n") == raw.count(b"\r\n"), "EOL misto após adicionar modelos"


def test_apply_diff_text_invalid_structure_raises_patch_error(allowlist_text, valid_html, today):
    flow = allowlist_text.replace(
        "  - name: Gemini 3.8 Flash\n    provider: google\n    status: ga\n    pinnable: true\n"
        "    retirement_date: null\n    cost:\n      label: low\n      input: 5\n    cost_rank: 2\n",
        "  - {name: Gemini 3.8 Flash, provider: google, status: ga, pinnable: true, retirement_date: null, cost_rank: 2}\n",
    )
    assert flow != allowlist_text
    diff = r.compute_diff(yaml.safe_load(flow), r.parse_supported_models(valid_html), today)
    with pytest.raises(r.PatchError):
        r.apply_diff_text(flow, diff, today)
    assert r.PatchError.exit_code == r.EXIT_PATCH == 5


def test_cli_invalid_patch_exit_5_without_writing(tmp_path, allowlist_text, valid_html, capsys):
    bad = allowlist_text.replace(
        "  - name: Legacy Model 1\n    provider: openai\n    status: ga\n    pinnable: true\n"
        "    retirement_date: \"2026-09-01\"\n    cost_rank: 3\n",
        "  - {name: Legacy Model 1, provider: openai, status: ga, pinnable: true, retirement_date: \"2026-09-01\", cost_rank: 3}\n",
    )
    assert bad != allowlist_text
    path = tmp_path / "al.yaml"
    path.write_bytes(bad.encode("utf-8"))
    html = tmp_path / "p.html"
    html.write_text(valid_html, encoding="utf-8")
    before = path.read_bytes()
    code = r.main(["--write", "--from-file", str(html), "--allowlist", str(path), "--no-report-file"])
    assert code == 5
    assert "ERRO" in capsys.readouterr().err
    assert path.read_bytes() == before
    assert list(tmp_path.glob("*.tmp")) == []


def test_missing_allowlist_exit_4(tmp_path, valid_html, today):
    with pytest.raises(r.RefreshError) as exc:
        r.run(allowlist_path=tmp_path / "nao-existe.yaml", html=valid_html, source="f",
              write=False, report_path=None, today=today)
    assert exc.value.exit_code == r.EXIT_FILE == 4


def test_cli_check_mode_default_report_stdout(allowlist_file, tmp_path, valid_html, capsys):
    html = tmp_path / "p.html"
    html.write_text(valid_html, encoding="utf-8")
    before = allowlist_file.read_bytes()
    code = r.main(["--from-file", str(html), "--allowlist", str(allowlist_file), "--no-report-file"])
    assert code == 0
    assert "# Refresh da allowlist de modelos" in capsys.readouterr().out
    assert allowlist_file.read_bytes() == before
