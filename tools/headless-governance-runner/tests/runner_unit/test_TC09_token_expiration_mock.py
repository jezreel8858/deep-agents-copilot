"""
TC-09: Mock de expiração de token em tempo de execução (N2).

Cenário:
Simular que o dublê de `CopilotSDKClient` levanta uma exceção de autenticação
(401/403 — `SDKAuthenticationError`) no meio da execução (ex.: durante a análise
de arquivos do diff). O runner deve capturar a exceção e retornar um `RelatorioAuditoria`
estruturado com `veredito="neutral"` (nunca crash sem report) e um achado/motivo
explícito citando falha de autenticação — nunca travar o processo pai silenciosamente.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from governance_runner.routing.model import Grafo
from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import (
    CopilotSDKClient,
    SDKAuthenticationError,
    SDKRequest,
    SDKResponse,
)
from governance_runner.runner.use_cases import RelatorioAuditoria, executar_agent_audit


@dataclass
class TokenExpiringCopilotClient:
    """Dublê do CopilotSDKClient que simula expiração de token durante o processamento."""

    falhar_apos_chamadas: int = 1
    chamadas_realizadas: int = 0
    ultima_requisicao: SDKRequest | None = field(default=None)

    def invoke(self, request: SDKRequest) -> SDKResponse:
        self.ultima_requisicao = request
        self.chamadas_realizadas += 1
        if self.chamadas_realizadas >= self.falhar_apos_chamadas:
            raise SDKAuthenticationError(
                "401 Unauthorized: token do Copilot SDK expirado no meio da execucao"
            )
        return SDKResponse(
            achados=({"arquivo": ".github/agents/agent-router.agent.md", "severidade": "info"},),
            premium_requests_consumidos=1,
        )


class TestTC09TokenExpirationMock:
    """Testes para o caso de teste TC-09 (expiração de token / falha 401-403)."""

    def test_deve_retornar_relatorio_neutral_quando_sdk_levanta_autenticacao_expirada(
        self, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange
        cliente = TokenExpiringCopilotClient(falhar_apos_chamadas=1)
        orcamento = Budget(max_premium_requests=15)
        diff = (
            ".github/agents/agent-router.agent.md",
            ".github/skills/handoff-governance/SKILL.md",
        )

        # Act
        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
            arquivos_diff=diff,
        )

        # Assert
        assert isinstance(relatorio, RelatorioAuditoria)
        assert relatorio.veredito == "neutral"
        assert relatorio.motivo is not None
        assert "sdk_auth_error" in relatorio.motivo
        assert "401 Unauthorized" in relatorio.motivo

        # Deve conter um achado explícito de erro de autenticação
        assert len(relatorio.achados) == 1
        achado = relatorio.achados[0]
        assert achado.regra == "SDK_AUTH_FAILURE"
        assert achado.severidade == "error"
        assert "401 Unauthorized" in achado.mensagem

        # Trace id e trilha devem estar preservados
        assert relatorio.trace_id is not None
        assert len(relatorio.trilha) == 1
        assert relatorio.trilha[0].agent == "agent-auditor"

    def test_deve_capturar_expiracao_403_e_preservar_custo_consumido_ate_o_momento(
        self, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange
        @dataclass
        class Client403:
            def invoke(self, request: SDKRequest) -> SDKResponse:
                raise SDKAuthenticationError("403 Forbidden: permissao revogada pelo GitHub App")

        cliente = Client403()
        orcamento = Budget(max_premium_requests=15)

        # Act
        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        # Assert
        assert relatorio.veredito == "neutral"
        assert "403 Forbidden" in str(relatorio.motivo)
        assert relatorio.achados[0].severidade == "error"
        assert relatorio.custo["turnos"] == 1
