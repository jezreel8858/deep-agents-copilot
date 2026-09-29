"""
budget — Teto de premium requests e de turnos (R-060) do runner headless.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.5): ao atingir
qualquer um dos tetos, o runner encerra com veredito estruturado
`status="neutral"` e `motivo="budget_exhausted"` — nunca crasha e nunca
retorna sucesso silencioso.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

__all__ = [
    "VeredictoOrcamento",
    "Budget",
    "GOV_MAX_PREMIUM_REQUESTS_ENV",
    "TETO_TURNOS_R060",
]

GOV_MAX_PREMIUM_REQUESTS_ENV = "GOV_MAX_PREMIUM_REQUESTS"
_DEFAULT_MAX_PREMIUM_REQUESTS = 15

# R-060: teto rigido de tool turns por ciclo — hardcoded, nao configuravel
# via env/prompt, para evitar loops O(N^2).
TETO_TURNOS_R060 = 5


@dataclass(frozen=True)
class VeredictoOrcamento:
    """Veredito estruturado de uma checagem de orçamento."""

    excedido: bool
    motivo: str | None = None


class Budget:
    """Controla o teto de premium requests e o teto de turnos (R-060) de um ciclo do runner."""

    def __init__(self, max_premium_requests: int | None = None) -> None:
        """Inicializa o orçamento do ciclo.

        Args:
            max_premium_requests: Teto de premium requests. Se omitido, lê
                de `GOV_MAX_PREMIUM_REQUESTS` (env), com default de 15.
        """
        if max_premium_requests is None:
            max_premium_requests = int(
                os.environ.get(GOV_MAX_PREMIUM_REQUESTS_ENV, str(_DEFAULT_MAX_PREMIUM_REQUESTS))
            )
        self._max_premium_requests = max_premium_requests
        self._max_turnos = TETO_TURNOS_R060
        self._premium_requests_consumidos = 0
        self._turnos_executados = 0

    @property
    def max_premium_requests(self) -> int:
        return self._max_premium_requests

    @property
    def max_turnos(self) -> int:
        return self._max_turnos

    def registrar_turno(self) -> VeredictoOrcamento:
        """Registra o início de um novo turno; retorna veredito de exaustão se aplicável."""
        self._turnos_executados += 1
        if self._turnos_executados > self._max_turnos:
            return VeredictoOrcamento(excedido=True, motivo="budget_exhausted")
        return VeredictoOrcamento(excedido=False)

    def registrar_custo(self, premium_requests: int) -> VeredictoOrcamento:
        """Registra o custo de premium requests consumido; retorna veredito de exaustão se aplicável."""
        self._premium_requests_consumidos += premium_requests
        if self._premium_requests_consumidos > self._max_premium_requests:
            return VeredictoOrcamento(excedido=True, motivo="budget_exhausted")
        return VeredictoOrcamento(excedido=False)

    @property
    def custo_atual(self) -> dict[str, int]:
        """Contrato mínimo `custo:{premium_requests, turnos}` (BLUEPRINT §5.4)."""
        return {
            "premium_requests": self._premium_requests_consumidos,
            "turnos": self._turnos_executados,
        }
