"""InPlaceWriter: edita SOMENTE o valor da linha `model:` do frontmatter (bytes preservados)."""
from __future__ import annotations
import contextlib
import hashlib
import logging
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any
from tools.model_profiles.errors import ModelProfilesError
logger = logging.getLogger(__name__)
BOM = b"\xef\xbb\xbf"
_RETRIES = 5
_BACKOFF = 0.1
_UNSAFE_UNQUOTED = re.compile(r"(^[\s\[\]{}&*!|>%@`'\"#-]|:\s|\s#|\s$)")
class WriterError(ModelProfilesError):
    code = "WRITER"
class WriteConflictError(ModelProfilesError):
    """Conteudo em disco difere do lido no planejamento (escrita recusada)."""
    code = "CONFLICT"
def _split(data: bytes) -> tuple[bytes, list[bytes]]:
    bom = BOM if data.startswith(BOM) else b""
    return bom, data[len(bom):].splitlines(keepends=True)
def _frontmatter_end(lines: list[bytes]) -> int | None:
    if not lines or lines[0].rstrip() != b"---":
        return None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == b"---":
            return i
    return None
def _field_re(name: str) -> re.Pattern[bytes]:
    key = re.escape(name.encode("utf-8"))
    return re.compile(
        rb"^(?P<pre>" + key + rb":[ \t]*)"
        rb"(?:(?P<q>[\"'])(?P<qv>.*?)(?P=q)|(?P<pv>[^\s#'\"][^#]*?))"
        rb"(?P<post>[ \t]*(?:#.*)?)$"
    )
def _find(lines: list[bytes], name: str) -> tuple[int, Any] | None:
    end = _frontmatter_end(lines)
    if end is None:
        return None
    rx = _field_re(name)
    for i in range(1, end):
        match = rx.match(lines[i].rstrip(b"\r\n"))
        if match:
            return i, match
    return None
def read_field(data: bytes, name: str) -> str | None:
    """Valor (sem aspas) do campo `name:` top-level do frontmatter, ou None."""
    _, lines = _split(data)
    hit = _find(lines, name)
    if hit is None:
        return None
    match = hit[1]
    raw = match["qv"] if match["q"] else match["pv"].strip()
    return raw.decode("utf-8", errors="replace")
def read_model(data: bytes) -> str | None:
    return read_field(data, "model")
def _check_value(new_model: str, quote: bytes | None) -> None:
    if "\r" in new_model or "\n" in new_model or not new_model.strip():
        raise WriterError("valor de model invalido (vazio ou com quebra de linha)")
    if quote and quote.decode() in new_model:
        raise WriterError("valor de model contem o caractere de aspas do arquivo")
    if not quote and _UNSAFE_UNQUOTED.search(new_model):
        raise WriterError("valor de model inseguro para escalar YAML sem aspas")
def set_model(data: bytes, new_model: str) -> bytes:
    """Troca apenas os bytes do valor de `model:`; BOM, EOL, aspas e espacos intactos."""
    bom, lines = _split(data)
    hit = _find(lines, "model")
    if hit is None:
        raise WriterError("linha model: ausente no frontmatter")
    idx, match = hit
    quote = match["q"]
    _check_value(new_model, quote)
    eol = lines[idx][len(lines[idx].rstrip(b"\r\n")):]
    q = quote or b""
    lines[idx] = match["pre"] + q + new_model.encode("utf-8") + q + match["post"] + eol
    return bom + b"".join(lines)
def _write_tmp(tmp: Path, data: bytes, target: Path) -> None:
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    with contextlib.suppress(OSError):
        shutil.copymode(target, tmp)
def _replace_with_retry(tmp: Path, target: Path) -> None:
    for attempt in range(_RETRIES):
        try:
            os.replace(tmp, target)
            return
        except PermissionError:
            if attempt == _RETRIES - 1:
                raise
            logger.warning("PermissionError ao substituir %s; nova tentativa", target.name)
            time.sleep(_BACKOFF * (attempt + 1))
def check_unchanged(path: Path | str, expected_sha: str) -> None:
    """Relê `path` e compara SHA-256 com `expected_sha`; divergencia => WriteConflictError."""
    target = Path(path)
    try:
        current = hashlib.sha256(target.read_bytes()).hexdigest()
    except OSError as exc:
        raise WriteConflictError(f"{target.name}: ilegivel ao revalidar ({type(exc).__name__}); "
                                 "nada foi escrito") from exc
    if current != expected_sha:
        raise WriteConflictError(f"{target.name}: conteudo alterado desde o planejamento; "
                                 "escrita recusada (nada foi escrito)")
def write_replace(path: Path | str, data: bytes, expected_sha: str | None = None) -> None:
    """tmp + os.replace com retry em PermissionError; `expected_sha` revalida o alvo logo antes."""
    target = Path(path)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        _write_tmp(tmp, data, target)
        if expected_sha is not None:
            check_unchanged(target, expected_sha)
        _replace_with_retry(tmp, target)
    finally:
        with contextlib.suppress(OSError):
            tmp.unlink(missing_ok=True)
def atomic_write(path: Path | str, data: bytes, expected_sha: str | None = None) -> None:
    """Escrita atomica de ALVOS (agents/prompts). Acessar sempre como `writer.atomic_write`."""
    write_replace(path, data, expected_sha)
