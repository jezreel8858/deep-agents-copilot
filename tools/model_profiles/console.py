"""Saida de CLI (stdout/stderr). Unico ponto com print."""
from __future__ import annotations
import re
import sys
from typing import Iterable
from tools.model_profiles.findings import Finding
_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?|\x1b[@-Z\\-_]")
_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
def sanitize(message: str) -> str:
    """Remove ANSI e caracteres de controle (exceto \\n e \\t): valores vindos de arquivos."""
    return _CTRL.sub("?", _ANSI.sub("", message))
def say(message: str) -> None:
    print(sanitize(message))
def fail(message: str) -> None:
    print(sanitize(message), file=sys.stderr)
def report(findings: Iterable[Finding]) -> None:
    for finding in findings:
        say(finding.render())
