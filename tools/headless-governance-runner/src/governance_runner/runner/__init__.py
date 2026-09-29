"""
runner — Adaptador do Copilot SDK e casos de uso do runner headless.

Escopo (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.2): sessão SDK, custom
tool `delegar()`, permission handler (`sdk_adapter.py`), casos de uso
`agent_audit` (implementado — subtask 19) / `code_review` / `hygiene`
(`use_cases.py`, futuras subtasks) e teto de premium requests/turnos R-060
(`budget.py`).
"""

from __future__ import annotations

from governance_runner.runner.budget import Budget, TETO_TURNOS_R060, VeredictoOrcamento
from governance_runner.runner.sdk_adapter import (
    CopilotSDKClient,
    DelegacaoNaoAutorizadaError,
    DelegacaoResultado,
    PermissaoDecisao,
    SDKRequest,
    SDKResponse,
    construir_permission_handler_read_only,
    criar_cliente_sdk_real,
    criar_delegar_tool,
)
from governance_runner.runner.use_cases import (
    Achado,
    EtapaTrilha,
    RelatorioAuditoria,
    executar_agent_audit,
)

__all__ = [
    "Budget",
    "TETO_TURNOS_R060",
    "VeredictoOrcamento",
    "CopilotSDKClient",
    "SDKRequest",
    "SDKResponse",
    "PermissaoDecisao",
    "DelegacaoResultado",
    "DelegacaoNaoAutorizadaError",
    "criar_delegar_tool",
    "construir_permission_handler_read_only",
    "criar_cliente_sdk_real",
    "Achado",
    "EtapaTrilha",
    "RelatorioAuditoria",
    "executar_agent_audit",
]
