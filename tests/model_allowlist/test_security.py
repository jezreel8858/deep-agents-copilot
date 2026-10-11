"""URL fixa, esquema, redirecionamento, --from-file e ausência de rede real."""

from __future__ import annotations

import socket
import urllib.error

import pytest

from tools.model_allowlist import refresh as r


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example/copilot/reference/ai-models/supported-models",
        "http://docs.github.com/copilot/reference/ai-models/supported-models",
        "ftp://docs.github.com/copilot/reference/ai-models/supported-models",
        "https://docs.github.com.evil.example/copilot/reference/ai-models/supported-models",
        "https://docs.github.com/outro/caminho",
        "https://docs.github.com/copilot/reference/ai-models/supported-models?x=1",
        "file:///etc/passwd",
        "",
    ],
)
def test_validate_url_rejects(url):
    with pytest.raises(r.UrlNotAllowedError):
        r.validate_url(url)
    assert r.UrlNotAllowedError.exit_code == r.EXIT_FETCH == 3


def test_validate_url_accepts_official():
    r.validate_url(r.OFFICIAL_URL)


@pytest.mark.parametrize("src", ["https://docs.github.com/x", "http://a/b", "file://x", "HTTPS://A/b"])
def test_from_file_rejects_url(src, allowlist_file, capsys):
    code = r.main(["--from-file", src, "--allowlist", str(allowlist_file), "--no-report-file"])
    assert code == 3
    assert "caminho local" in capsys.readouterr().err


def test_from_file_missing_path_is_error(tmp_path, allowlist_file):
    code = r.main(["--from-file", str(tmp_path / "nao.html"), "--allowlist", str(allowlist_file), "--no-report-file"])
    assert code != 0


def test_fetch_rejects_other_url_before_any_network():
    with pytest.raises(r.UrlNotAllowedError):
        r.fetch_official_page("https://evil.example/")


class _FakeResponse:
    def __init__(self, final_url, payload=b"<html></html>"):
        self._final, self._payload = final_url, payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def geturl(self):
        return self._final

    def read(self, n=-1):
        return self._payload if n < 0 else self._payload[:n]


class _FakeOpener:
    def __init__(self, behavior):
        self._behavior = behavior
        self.calls = 0

    def open(self, request, timeout=None):
        self.calls += 1
        assert timeout == r.TIMEOUT_SECONDS
        if isinstance(self._behavior, Exception):
            raise self._behavior
        return self._behavior


def _patch_opener(monkeypatch, behavior):
    opener = _FakeOpener(behavior)
    monkeypatch.setattr(r.urllib.request, "build_opener", lambda *h: opener)
    return opener


def test_fetch_ok_with_mock_opener(monkeypatch):
    opener = _patch_opener(monkeypatch, _FakeResponse(r.OFFICIAL_URL, "olá".encode()))
    assert r.fetch_official_page() == "olá"
    assert opener.calls == 1


def test_fetch_final_host_other_is_refused(monkeypatch):
    _patch_opener(monkeypatch, _FakeResponse("https://evil.example/x"))
    with pytest.raises(r.UrlNotAllowedError):
        r.fetch_official_page()


def test_fetch_final_scheme_http_is_refused(monkeypatch):
    _patch_opener(monkeypatch, _FakeResponse("http://docs.github.com/x"))
    with pytest.raises(r.UrlNotAllowedError):
        r.fetch_official_page()


def test_fetch_redirect_error_propagates_as_url_not_allowed(monkeypatch):
    _patch_opener(monkeypatch, r.UrlNotAllowedError("redirect"))
    with pytest.raises(r.UrlNotAllowedError):
        r.fetch_official_page()


@pytest.mark.parametrize("exc", [urllib.error.URLError("x"), TimeoutError("t"), OSError("o")])
def test_fetch_network_errors_become_fetch_error(monkeypatch, exc):
    _patch_opener(monkeypatch, exc)
    with pytest.raises(r.FetchError) as e:
        r.fetch_official_page()
    assert e.value.exit_code == 3


def test_fetch_size_limit_boundary(monkeypatch):
    _patch_opener(monkeypatch, _FakeResponse(r.OFFICIAL_URL, b"a" * r.MAX_BYTES))
    assert len(r.fetch_official_page()) == r.MAX_BYTES
    _patch_opener(monkeypatch, _FakeResponse(r.OFFICIAL_URL, b"a" * (r.MAX_BYTES + 1)))
    with pytest.raises(r.FetchError):
        r.fetch_official_page()


@pytest.mark.parametrize(
    "newurl",
    [
        "https://evil.example/x",
        "http://docs.github.com/x",
        "https://docs.github.com.evil.example/x",
    ],
)
def test_redirect_handler_refuses_other_host_or_scheme(newurl):
    handler = r._SameHostRedirect()
    req = r.urllib.request.Request(r.OFFICIAL_URL)
    with pytest.raises(r.UrlNotAllowedError):
        handler.redirect_request(req, None, 302, "Found", {}, newurl)


def test_redirect_handler_allows_same_host():
    handler = r._SameHostRedirect()
    req = r.urllib.request.Request(r.OFFICIAL_URL)
    new = handler.redirect_request(req, None, 302, "Found", {}, "https://docs.github.com/novo")
    assert new is not None and new.full_url == "https://docs.github.com/novo"


def test_main_without_from_file_uses_fetch_and_maps_exit_3(monkeypatch, allowlist_file, capsys):
    def _fail(url=r.OFFICIAL_URL):
        raise r.FetchError("sem rede")

    monkeypatch.setattr(r, "fetch_official_page", _fail)
    code = r.main(["--allowlist", str(allowlist_file), "--no-report-file"])
    assert code == 3
    assert "sem rede" in capsys.readouterr().err


def test_network_guard_blocks_real_sockets():
    with pytest.raises(AssertionError):
        socket.create_connection(("docs.github.com", 443))
    with pytest.raises(AssertionError):
        socket.getaddrinfo("docs.github.com", 443)


def test_real_allowlist_and_profiles_untouched(allowlist_file, valid_html, today):
    from pathlib import Path

    real = Path(__file__).resolve().parents[2] / "model-allowlist.yaml"
    snapshot = real.read_bytes() if real.exists() else None
    r.run(allowlist_path=allowlist_file, html=valid_html, source="f", write=True, report_path=None, today=today)
    assert (real.read_bytes() if real.exists() else None) == snapshot
    assert allowlist_file.parent != real.parent
