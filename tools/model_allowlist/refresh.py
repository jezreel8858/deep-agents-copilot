"""Refresh da allowlist de modelos a partir da página oficial do GitHub Docs.

Garantias de segurança (plano 20261010, §9):
- URL FIXA (``OFFICIAL_URL``), HTTPS, sem parâmetro livre de URL;
- redirecionamentos só são seguidos dentro do mesmo host (``ALLOWED_HOST``);
- timeout e limite de tamanho da resposta; sem credenciais;
- ``yaml.safe_load`` e escrita atômica;
- layout inesperado => falha visível (exit != 0), nunca atualização silenciosa;
- nunca remove modelos nem altera ``cost_rank``/``cost``/``pinnable`` de existentes.

Códigos de saída: 0 ok; 2 layout da página alterado; 3 erro de rede/URL;
4 erro de arquivo/allowlist; 5 patch inválido (abortado sem escrever).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml

OFFICIAL_URL = "https://docs.github.com/copilot/reference/ai-models/supported-models"
ALLOWED_HOST = "docs.github.com"
TIMEOUT_SECONDS = 20
MAX_BYTES = 5 * 1024 * 1024
RETIREMENT_WARN_DAYS = 30
DEFAULT_ALLOWLIST = "model-allowlist.yaml"
DEFAULT_REPORT = ".model-profiles/allowlist-refresh.md"

EXIT_OK = 0
EXIT_LAYOUT = 2
EXIT_FETCH = 3
EXIT_FILE = 4
EXIT_PATCH = 5


class RefreshError(Exception):
    exit_code = EXIT_FILE


class LayoutChangedError(RefreshError):
    exit_code = EXIT_LAYOUT


class UrlNotAllowedError(RefreshError):
    exit_code = EXIT_FETCH


class FetchError(RefreshError):
    exit_code = EXIT_FETCH


class PatchError(RefreshError):
    exit_code = EXIT_PATCH


# --------------------------------------------------------------------------- fetch


def validate_url(url: str) -> None:
    """Aceita somente a URL oficial fixa (HTTPS + host permitido)."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise UrlNotAllowedError(
            f"URL recusada: apenas {OFFICIAL_URL} é permitida (recebido: {url!r})."
        )
    if url != OFFICIAL_URL:
        raise UrlNotAllowedError(
            f"URL recusada: apenas a URL fixa {OFFICIAL_URL} é permitida (recebido: {url!r})."
        )


class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        parsed = urllib.parse.urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
            raise UrlNotAllowedError(
                f"Redirecionamento para outro host/esquema recusado: {newurl!r}."
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_official_page(url: str = OFFICIAL_URL) -> str:
    """Baixa a página oficial. Rejeita qualquer URL diferente da fixa."""
    validate_url(url)
    opener = urllib.request.build_opener(_SameHostRedirect)
    request = urllib.request.Request(
        url, headers={"User-Agent": "model-allowlist-refresh/1", "Accept": "text/html"}
    )
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - URL validada
            final = response.geturl()
            parsed = urllib.parse.urlsplit(final)
            if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
                raise UrlNotAllowedError(f"Host final inesperado: {final!r}.")
            data = response.read(MAX_BYTES + 1)
    except UrlNotAllowedError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"Falha ao baixar a página oficial: {exc}") from exc
    if len(data) > MAX_BYTES:
        raise FetchError(f"Resposta maior que o limite de {MAX_BYTES} bytes.")
    return data.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------- parse


class _TableParser(HTMLParser):
    """Extrai tabelas como listas de linhas; cada célula = (texto, é_th)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[tuple[str, bool]]]] = []
        self._depth = 0
        self._row: list[tuple[str, bool]] | None = None
        self._cell: list[str] | None = None
        self._cell_is_th = False
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "table":
            self._depth += 1
            if self._depth == 1:
                self.tables.append([])
        elif self._depth >= 1:
            if tag == "tr" and self._depth == 1:
                self._row = []
            elif tag in ("td", "th") and self._depth == 1 and self._row is not None:
                self._cell = []
                self._cell_is_th = tag == "th"
            elif tag == "br" and self._cell is not None:
                self._cell.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag == "table" and self._depth:
            self._depth -= 1
        elif self._depth == 1:
            if tag in ("td", "th") and self._cell is not None and self._row is not None:
                text = re.sub(r"\s+", " ", "".join(self._cell)).strip()
                self._row.append((text, self._cell_is_th))
                self._cell = None
            elif tag == "tr" and self._row is not None:
                if self._row:
                    self.tables[-1].append(self._row)
                self._row = None

    def handle_data(self, data: str) -> None:
        if self._cell is not None and not self._skip:
            self._cell.append(data)


@dataclass(frozen=True)
class PageModel:
    name: str
    provider: str | None = None
    status: str | None = None  # ga | preview | None (não reconhecido)
    retirement_date: str | None = None  # ISO
    raw_status: str | None = None


@dataclass
class ParsedPage:
    models: dict[str, PageModel] = field(default_factory=dict)  # chave = match_key
    retirement_table_found: bool = False
    warnings: list[str] = field(default_factory=list)


_NOTE_RE = re.compile(r"\s*(\[\w+\]|[*†‡¹²³⁴⁵⁶⁷⁸⁹⁰]+)\s*$")
_PAREN_RE = re.compile(r"\s*\(([^)]*)\)\s*$")


def match_key(name: str) -> str:
    """Chave de comparação tolerante: casefold, sem notas/parênteses finais."""
    text = re.sub(r"\s+", " ", name).strip()
    prev = None
    while prev != text:
        prev = text
        text = _NOTE_RE.sub("", text)
        text = _PAREN_RE.sub("", text)
    return text.casefold().strip()


def _clean_name(name: str) -> str:
    text = re.sub(r"\s+", " ", name).strip()
    prev = None
    while prev != text:
        prev = text
        text = _NOTE_RE.sub("", text)
        text = _PAREN_RE.sub("", text)
    return text.strip()


def normalize_status(raw: str | None) -> str | None:
    if not raw:
        return None
    text = raw.casefold()
    if "preview" in text or "beta" in text:
        return "preview"
    if text.strip() in {"ga", "generally available"} or "generally available" in text or re.search(r"\bga\b", text):
        return "ga"
    return None


def normalize_provider(raw: str | None) -> str | None:
    if not raw:
        return None
    return re.sub(r"[^a-z0-9]+", "-", raw.casefold()).strip("-") or None


_DATE_FORMATS = ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%B %d %Y", "%Y/%m/%d")


def parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    text = re.sub(r"\s+", " ", raw).strip().strip(".")
    text = _NOTE_RE.sub("", text)
    for fmt in _DATE_FORMATS:
        try:
            return dt.datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(0)).isoformat()
    except ValueError:
        return None


def _column_map(headers: list[str]) -> dict[str, int]:
    cols: dict[str, int] = {}
    for idx, header in enumerate(h.casefold() for h in headers):
        if any(k in header for k in ("retire", "deprecat", "sunset")):
            cols.setdefault("retirement", idx)
        elif "provider" in header:
            cols.setdefault("provider", idx)
        elif "status" in header:
            cols.setdefault("status", idx)
        elif header in {"model", "model name", "name"} or header.startswith("model"):
            cols.setdefault("name", idx)
    return cols


def parse_supported_models(html: str) -> ParsedPage:
    """Parser tolerante. Levanta ``LayoutChangedError`` se faltarem tabelas/headers esperados."""
    parser = _TableParser()
    parser.feed(html)
    parser.close()
    if not parser.tables:
        raise LayoutChangedError(
            "Layout alterado: nenhuma <table> encontrada na página de modelos suportados."
        )

    page = ParsedPage()
    main_tables = 0
    retirement_only: list[tuple[dict[str, int], list[list[tuple[str, bool]]]]] = []
    seen_headers: list[list[str]] = []

    for table in parser.tables:
        if not table:
            continue
        first = table[0]
        if all(is_th for _, is_th in first) or not any(is_th for row in table for _, is_th in row):
            headers = [text for text, _ in first]
            body = table[1:]
        else:
            headers = [text for text, is_th in first if is_th]
            body = table[1:]
        seen_headers.append(headers)
        cols = _column_map(headers)
        if "name" not in cols:
            continue
        if "provider" in cols and "status" in cols:
            main_tables += 1
            for row in body:
                cells = [t for t, _ in row]
                if len(cells) <= max(cols.values()):
                    continue
                name = _clean_name(cells[cols["name"]])
                if not name:
                    continue
                raw_status = cells[cols["status"]]
                status = normalize_status(raw_status)
                if status is None:
                    suffix = _PAREN_RE.search(cells[cols["name"]])
                    status = normalize_status(suffix.group(1)) if suffix else None
                retirement = (
                    parse_date(cells[cols["retirement"]]) if "retirement" in cols else None
                )
                if status is None:
                    page.warnings.append(
                        f"Status não reconhecido para '{name}': {raw_status!r} (ignorado)."
                    )
                page.models[match_key(name)] = PageModel(
                    name=name,
                    provider=normalize_provider(cells[cols["provider"]]),
                    status=status,
                    retirement_date=retirement,
                    raw_status=raw_status,
                )
        elif "retirement" in cols:
            retirement_only.append((cols, body))

    if main_tables == 0 or not page.models:
        raise LayoutChangedError(
            "Layout alterado: nenhuma tabela com colunas esperadas "
            "('Model', 'Provider', 'Status'); headers vistos: "
            + "; ".join("[" + ", ".join(h) + "]" for h in seen_headers[:6])
        )

    for cols, body in retirement_only:
        page.retirement_table_found = True
        for row in body:
            cells = [t for t, _ in row]
            if len(cells) <= max(cols.values()):
                continue
            name = _clean_name(cells[cols["name"]])
            date = parse_date(cells[cols["retirement"]])
            if not name or date is None:
                continue
            key = match_key(name)
            existing = page.models.get(key)
            if existing is not None:
                page.models[key] = PageModel(
                    existing.name, existing.provider, existing.status, date, existing.raw_status
                )
            else:
                page.warnings.append(
                    f"Aposentadoria de '{name}' ({date}) sem linha correspondente na tabela principal."
                )
                page.models[key] = PageModel(name, None, None, date, None)
    if any("retirement" in _column_map(h) for h in seen_headers):
        page.retirement_table_found = True
    return page


# --------------------------------------------------------------------------- diff


@dataclass(frozen=True)
class FieldChange:
    model: str
    field: str
    old: str | None
    new: str | None


@dataclass
class DiffResult:
    changes: list[FieldChange] = field(default_factory=list)
    added: list[PageModel] = field(default_factory=list)
    missing_on_page: list[str] = field(default_factory=list)
    retiring_soon: list[tuple[str, str, int]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes or self.added)


def _s(value: Any) -> str | None:
    return None if value is None else str(value)


def compute_diff(
    allowlist: dict[str, Any], page: ParsedPage, today: dt.date | None = None
) -> DiffResult:
    today = today or dt.date.today()
    result = DiffResult(warnings=list(page.warnings))
    models = allowlist.get("models") or []
    known: dict[str, dict[str, Any]] = {match_key(str(m["name"])): m for m in models}

    for key, entry in known.items():
        pm = page.models.get(key)
        name = str(entry["name"])
        if pm is None:
            if entry.get("status") != "special":
                result.missing_on_page.append(name)
        else:
            if pm.status and entry.get("status") != "special" and pm.status != entry.get("status"):
                result.changes.append(FieldChange(name, "status", _s(entry.get("status")), pm.status))
            if pm.retirement_date and pm.retirement_date != _s(entry.get("retirement_date")):
                result.changes.append(
                    FieldChange(name, "retirement_date", _s(entry.get("retirement_date")), pm.retirement_date)
                )
        effective = (pm.retirement_date if pm and pm.retirement_date else None) or _s(
            entry.get("retirement_date")
        )
        _maybe_retiring(result, name, effective, today)

    for key, pm in page.models.items():
        if key not in known and pm.status is not None and pm.provider is not None:
            result.added.append(pm)
            _maybe_retiring(result, pm.name, pm.retirement_date, today)
        elif key not in known:
            result.warnings.append(f"Modelo '{pm.name}' na página sem dados suficientes; ignorado.")
    return result


def _maybe_retiring(result: DiffResult, name: str, date: str | None, today: dt.date) -> None:
    if not date:
        return
    try:
        days = (dt.date.fromisoformat(date) - today).days
    except ValueError:
        result.warnings.append(f"Data de aposentadoria inválida para '{name}': {date!r}.")
        return
    if days <= RETIREMENT_WARN_DAYS:
        result.retiring_soon.append((name, date, days))


# --------------------------------------------------------------------------- report


def render_report(diff: DiffResult, source: str, today: dt.date, written: bool) -> str:
    lines = [
        "# Refresh da allowlist de modelos",
        "",
        f"- Data: {today.isoformat()}",
        f"- Fonte: {source}",
        f"- Modo: {'--write (aplicado)' if written else 'somente relatório'}",
        f"- Alterações propostas: {len(diff.changes)} campo(s); novos modelos: {len(diff.added)}",
        "",
        "> Atualização da allowlist é revisada via PR humano; novos modelos entram "
        "como `pinnable: false`, `cost: null`, `cost_rank: null`.",
        "",
    ]
    lines.append("## Aposentadorias em <= 30 dias (ou já vencidas)")
    if diff.retiring_soon:
        for name, date, days in sorted(diff.retiring_soon, key=lambda x: x[2]):
            state = "VENCIDA" if days < 0 else f"em {days} dia(s)"
            lines.append(f"- **{name}**: {date} ({state})")
    else:
        lines.append("- Nenhuma.")
    lines += ["", "## Campos alterados"]
    if diff.changes:
        for c in diff.changes:
            lines.append(f"- {c.model} · `{c.field}`: `{c.old}` → `{c.new}`")
    else:
        lines.append("- Nenhum.")
    lines += ["", "## Novos modelos (candidatos)"]
    if diff.added:
        for m in diff.added:
            lines.append(
                f"- {m.name} (provider: {m.provider}, status: {m.status}, "
                f"retirement_date: {m.retirement_date})"
            )
    else:
        lines.append("- Nenhum.")
    lines += ["", "## Presentes na allowlist e ausentes na página (revisão manual; nunca removidos)"]
    lines += [f"- {n}" for n in diff.missing_on_page] or ["- Nenhum."]
    if diff.warnings:
        lines += ["", "## Avisos"] + [f"- {w}" for w in diff.warnings]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- write


_START_RE = re.compile(r"^  - name:")


def _scalar(value: str | None) -> str:
    return "null" if value is None else json.dumps(value, ensure_ascii=False)


def _set_scalar(block: list[str], key: str, value: str | None, after_key: str = "status", default_eol: str = "\n") -> None:
    pattern = re.compile(rf"^(    {key}:[ \t]*)([^#\r\n]*?)([ \t]*#[^\r\n]*)?(\r?\n)?$")
    for i, line in enumerate(block):
        m = pattern.match(line)
        if m:
            eol = m.group(4) or default_eol
            block[i] = f"{m.group(1)}{_scalar(value) if key != 'status' else (value or 'null')}{m.group(3) or ''}{eol}"
            return
    anchor = re.compile(rf"^    {after_key}:")
    for i, line in enumerate(block):
        if anchor.match(line):
            rendered = _scalar(value) if key != "status" else (value or "null")
            block.insert(i + 1, f"    {key}: {rendered}{default_eol}")
            return
    rendered = _scalar(value) if key != "status" else (value or "null")
    block.append(f"    {key}: {rendered}{default_eol}")


def apply_diff_text(text: str, diff: DiffResult, today: dt.date) -> str:
    """Aplica só verified_at/status/retirement_date em existentes e acrescenta novos modelos."""
    data = yaml.safe_load(text)
    models = data.get("models") or []
    lines = text.splitlines(keepends=True)
    crlf, lf = text.count("\r\n"), text.count("\n") - text.count("\r\n")
    eol = "\r\n" if crlf > lf else "\n"
    starts = [i for i, ln in enumerate(lines) if _START_RE.match(ln)]
    if len(starts) != len(models):
        raise PatchError("Estrutura do YAML inesperada (blocos de modelo != entradas); patch abortado.")
    index_by_key = {match_key(str(m["name"])): k for k, m in enumerate(models)}
    bounds = [(s, starts[k + 1] if k + 1 < len(starts) else len(lines)) for k, s in enumerate(starts)]

    per_model: dict[int, dict[str, str | None]] = {}
    for c in diff.changes:
        k = index_by_key[match_key(c.model)]
        per_model.setdefault(k, {})[c.field] = c.new

    for k in sorted(per_model, reverse=True):
        start, end = bounds[k]
        block = lines[start:end]
        # preserva linhas em branco/comentários finais fora do bloco de campos
        for field_name, new in per_model[k].items():
            _set_scalar(block, field_name, new, default_eol=eol)
        lines[start:end] = block

    new_text = "".join(lines)
    if diff.added:
        if not new_text.endswith("\n"):
            new_text += eol
        for pm in diff.added:
            new_text += eol.join(
                [
                    "",
                    f"  # Adicionado por tools.model_allowlist em {today.isoformat()}; revisar antes de pinar.",
                    f"  - name: {json.dumps(pm.name, ensure_ascii=False)}",
                    f"    provider: {pm.provider}",
                    f"    status: {pm.status}",
                    "    pinnable: false",
                    f"    retirement_date: {_scalar(pm.retirement_date)}",
                    "    cost: null",
                    "    cost_rank: null",
                    "",
                ]
            )
    if diff.has_changes:
        new_text = re.sub(
            r'^(verified_at:[ \t]*)("?)[^\s#"]*("?)', rf'\g<1>"{today.isoformat()}"', new_text, count=1, flags=re.M
        )
    _verify_patch(text, new_text, diff)
    return new_text


def _verify_patch(old: str, new: str, diff: DiffResult) -> None:
    before, after = yaml.safe_load(old), yaml.safe_load(new)
    old_models, new_models = before["models"], after["models"]
    if len(new_models) != len(old_models) + len(diff.added):
        raise PatchError("Patch alteraria a quantidade de modelos de forma inesperada; abortado.")
    names = [m["name"] for m in new_models]
    if len(set(names)) != len(names):
        raise PatchError("Patch geraria nomes duplicados; abortado.")
    allowed = {"status", "retirement_date"}
    for o, n in zip(old_models, new_models[: len(old_models)]):
        for key in set(o) | set(n):
            if key in allowed:
                continue
            if o.get(key) != n.get(key):
                raise PatchError(f"Patch alteraria campo proibido '{key}' de '{o['name']}'; abortado.")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------- CLI


def run(
    *,
    allowlist_path: Path,
    html: str,
    source: str,
    write: bool,
    report_path: Path | None,
    today: dt.date | None = None,
) -> tuple[int, str]:
    today = today or dt.date.today()
    page = parse_supported_models(html)
    try:
        with open(allowlist_path, encoding="utf-8", newline="") as fh:  # preserva EOL
            text = fh.read()
        allowlist = yaml.safe_load(text)
    except (OSError, yaml.YAMLError) as exc:
        raise RefreshError(f"Falha ao ler allowlist {allowlist_path}: {exc}") from exc
    if not isinstance(allowlist, dict) or not isinstance(allowlist.get("models"), list):
        raise RefreshError(f"Allowlist inválida: {allowlist_path} sem lista 'models'.")
    diff = compute_diff(allowlist, page, today)
    written = False
    if write and diff.has_changes:
        atomic_write(allowlist_path, apply_diff_text(text, diff, today))
        written = True
    report = render_report(diff, source, today, written)
    if report_path is not None:
        atomic_write(report_path, report)
    return EXIT_OK, report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools.model_allowlist.refresh",
        description="Compara a allowlist com a página oficial de modelos do Copilot (URL fixa).",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Somente relatório (padrão).")
    mode.add_argument("--write", action="store_true", help="Atualiza verified_at/status/retirement_date e adiciona novos (pinnable: false).")
    p.add_argument("--from-file", metavar="HTML", help="Lê HTML local em vez da rede (testes).")
    p.add_argument("--allowlist", default=DEFAULT_ALLOWLIST, help=argparse.SUPPRESS)
    p.add_argument("--report", default=DEFAULT_REPORT, help="Arquivo do relatório Markdown.")
    p.add_argument("--no-report-file", action="store_true", help="Só stdout.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.from_file:
            if re.match(r"^[a-z][a-z0-9+.-]*://", args.from_file, re.I):
                raise UrlNotAllowedError("--from-file aceita apenas caminho local, não URL.")
            try:
                html = Path(args.from_file).read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                raise RefreshError(f"Falha ao ler {args.from_file}: {exc}") from exc
            source = f"arquivo local {args.from_file}"
        else:
            html = fetch_official_page(OFFICIAL_URL)
            source = OFFICIAL_URL
        _, report = run(
            allowlist_path=Path(args.allowlist),
            html=html,
            source=source,
            write=bool(args.write),
            report_path=None if args.no_report_file else Path(args.report),
        )
    except RefreshError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return exc.exit_code
    sys.stdout.write(report)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
