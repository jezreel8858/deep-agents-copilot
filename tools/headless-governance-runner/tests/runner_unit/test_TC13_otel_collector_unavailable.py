"""
TC-13: Resiliência e graceful degradation quando o coletor OTel estiver indisponível (N2).

Cenário:
Simular que o exportador OTel (`telemetry/otel.py`) não consegue conectar ao
collector (ex.: `ConnectionRefusedError`, timeout simulado ou erro de rede).
O runner deve continuar funcionando normalmente e completar a auditoria
(fail-open de telemetria — observabilidade nunca pode bloquear a governança).
O `RelatorioAuditoria` final deve ser produzido normalmente, com o `trace_id`
definido como o valor sentinela `TRACE_ID_INDISPONIVEL` ("telemetry_unavailable")
ou None.
"""

from __future__ import annotations

import urllib.error
from dataclasses import dataclass

import pytest

from governance_runner.routing.model import Grafo
from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import SDKRequest, SDKResponse
from governance_runner.runner.use_cases import RelatorioAuditoria, executar_agent_audit
from governance_runner.telemetry.otel import (
    OTEL_EXPORTER_OTLP_ENDPOINT_ENV,
    TRACE_ID_INDISPONIVEL,
    obter_trace_id_auditoria,
    verificar_disponibilidade_collector,
)


@dataclass
class DummyCopilotSDKClient:
    """Dublê do SDK para o teste de telemetria."""

    def invoke(self, request: SDKRequest) -> SDKResponse:
        return SDKResponse(
            achados=({"arquivo": ".github/agents/test.md", "severidade": "info"},),
            premium_requests_consumidos=1,
        )


class TestTC13OTelCollectorUnavailable:
    """Testes para o caso de teste TC-13 (fail-open ante indisponibilidade do OTel Collector)."""

    def test_deve_completar_auditoria_com_fail_open_quando_coletor_otel_estiver_indisponivel(
        self, monkeypatch: pytest.MonkeyPatch, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange: força simulação de coletor inacessível (ConnectionRefusedError)
        monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT_ENV, "http://localhost:4318/v1/traces")
        monkeypatch.setattr(
            "governance_runner.telemetry.otel.verificar_disponibilidade_collector",
            lambda *args, **kwargs: False,
        )

        cliente = DummyCopilotSDKClient()
        orcamento = Budget(max_premium_requests=15)

        # Act: executar agent audit sem passar trace_id explícito
        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        # Assert: auditoria deve completar com sucesso, sem exceções
        assert isinstance(relatorio, RelatorioAuditoria)
        assert relatorio.veredito == "neutral"
        assert relatorio.use_case == "agent-audit"
        assert len(relatorio.achados) == 1

        # trace_id deve refletir a sentinela de falha de telemetria (fail-open)
        assert relatorio.trace_id == TRACE_ID_INDISPONIVEL

    def test_deve_produzir_trace_id_valido_quando_coletor_estiver_disponivel(
        self, monkeypatch: pytest.MonkeyPatch, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange
        monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT_ENV, "http://localhost:4318/v1/traces")
        monkeypatch.setattr(
            "governance_runner.telemetry.otel.verificar_disponibilidade_collector",
            lambda *args, **kwargs: True,
        )

        cliente = DummyCopilotSDKClient()
        orcamento = Budget(max_premium_requests=15)

        # Act
        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        # Assert
        assert relatorio.trace_id != TRACE_ID_INDISPONIVEL
        assert relatorio.trace_id is not None
        assert len(relatorio.trace_id) == 32  # uuid4 hex

    def test_verificar_disponibilidade_coletor_retorna_false_sob_connection_refused_sem_lancar_excecao(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange: simula erro de conexão real do urllib
        def _mock_urlopen(*args: object, **kwargs: object) -> object:
            raise urllib.error.URLError(ConnectionRefusedError(10061, "Connection refused"))

        monkeypatch.setattr("urllib.request.urlopen", _mock_urlopen)

        # Act & Assert
        disponivel = verificar_disponibilidade_collector("http://127.0.0.1:4318")
        assert disponivel is False

        # obter_trace_id_auditoria deve retornar sentinela sem quebrar
        trace_id = obter_trace_id_auditoria("http://127.0.0.1:4318", force_probe=True)
        assert trace_id == TRACE_ID_INDISPONIVEL

    def test_verificar_disponibilidade_retorna_true_quando_sem_endpoint_configurado(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.delenv(OTEL_EXPORTER_OTLP_ENDPOINT_ENV, raising=False)

        # Act & Assert
        assert verificar_disponibilidade_collector(None) is True
        trace_id = obter_trace_id_auditoria(None)
        assert trace_id != TRACE_ID_INDISPONIVEL
        assert len(trace_id) == 32
