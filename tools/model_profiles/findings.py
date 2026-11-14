"""Achados de validacao (allowlist, hierarquia, estado) com codigos estaveis."""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Iterable
ERROR = "error"
WARN = "warn"
CONFIRM = "confirm"  # exige confirmacao reforcada no apply; aviso no doctor
@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: str = ERROR
    def render(self) -> str:
        return f"[{self.code}] {self.message}"
    def downgraded(self) -> "Finding":
        """CONFIRM vira WARN (contexto de diagnostico)."""
        return replace(self, severity=WARN) if self.severity == CONFIRM else self
def has_errors(findings: Iterable[Finding]) -> bool:
    return any(f.severity == ERROR for f in findings)
