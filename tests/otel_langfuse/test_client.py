"""
Testes unitários para o cliente de tracing (client.py).
"""

from unittest.mock import MagicMock
import pytest

from otel_langfuse.client import LangfuseOtelClient
from otel_langfuse.config import TraceConfig
from otel_langfuse.models import GenerationData, ScoreData, TokenUsage


def test_deve_funcionar_em_fallback_gracioso_quando_sem_credenciais():
    cfg = TraceConfig()  # is_enabled = False
    client = LangfuseOtelClient(config=cfg)

    assert client.is_active is False

    # Operações em fallback não devem lançar exceção
    with client.start_trace("trace-fallback", session_id="s1") as trace:
        with client.start_span("span-fallback", parent=trace) as span:
            span.set_attribute("chave", "valor")

        gen_data = GenerationData(
            name="gen-fallback",
            model="claude-3-7-sonnet",
            input_data="ping",
            output_data="pong",
            usage=TokenUsage(input_tokens=10, output_tokens=5),
        )
        client.record_generation(gen_data, parent=trace)
        client.record_score(ScoreData(name="test_score", value=1.0), parent=trace)


def test_deve_criar_trace_com_session_id_e_user_id():
    cfg = TraceConfig(
        langfuse_public_key="pk-lf-mock",
        langfuse_secret_key="sk-lf-mock",
    )
    client = LangfuseOtelClient(config=cfg, in_memory=True)

    with client.start_trace(
        name="test-operation",
        session_id="session-42",
        user_id="user-99",
        tags=["teste", "unitario"],
    ) as trace:
        assert trace is not None
        assert trace.attributes.get("session_id") == "session-42"
        assert trace.attributes.get("user_id") == "user-99"
        assert trace.attributes.get("deployment.environment") == "development"


def test_deve_criar_span_invoke_agent_com_atributos_semconv():
    cfg = TraceConfig(langfuse_public_key="pk-lf-mock", langfuse_secret_key="sk-lf-mock")
    client = LangfuseOtelClient(config=cfg, in_memory=True)

    with client.start_trace("agente-root", session_id="sess-1") as trace:
        with client.start_agent_span(
            agent_name="python-feature-developer",
            description="Implementa tracing",
            provider_name="anthropic",
            parent=trace,
        ) as span:
            assert span.attributes.get("gen_ai.operation.name") == "invoke_agent"
            assert span.attributes.get("gen_ai.agent.name") == "python-feature-developer"
            assert span.attributes.get("gen_ai.provider.name") == "anthropic"


def test_deve_criar_span_execute_tool_mcp_com_status():
    cfg = TraceConfig(langfuse_public_key="pk-lf-mock", langfuse_secret_key="sk-lf-mock")
    client = LangfuseOtelClient(config=cfg, in_memory=True)

    with client.start_trace("tool-exec", session_id="sess-1") as trace:
        with client.start_tool_span(
            tool_name="context-mode/ctx_search",
            tool_type="mcp",
            tool_call_id="call-1234",
            status="success",
            duration_ms=45.5,
            parent=trace,
        ) as span:
            assert span.attributes.get("gen_ai.operation.name") == "execute_tool"
            assert span.attributes.get("gen_ai.tool.name") == "context-mode/ctx_search"
            assert span.attributes.get("gen_ai.tool.type") == "mcp"
            assert span.attributes.get("gen_ai.tool.call.id") == "call-1234"
            assert span.attributes.get("tool.execution.status") == "success"
            assert span.attributes.get("tool.execution.duration_ms") == 45.5


def test_deve_registrar_generation_com_tokens_e_sanitizacao():
    cfg = TraceConfig(langfuse_public_key="pk-lf-mock", langfuse_secret_key="sk-lf-mock")
    client = LangfuseOtelClient(config=cfg, in_memory=True)

    with client.start_trace("gen-test") as trace:
        gen = GenerationData(
            name="llm_chat",
            model="gpt-4o",
            provider_name="openai",
            input_data="Meu token eh ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            output_data="Recebido com secret sk-lf-12345-secret",
            usage=TokenUsage(input_tokens=100, output_tokens=50),
            finish_reason="stop",
            cost_usd=0.0015,
        )
        record = client.record_generation(gen, parent=trace)
        assert record is not None
        assert "***REDACTED_GH***" in record.input_data
        assert "ghp_" not in record.input_data
        assert "***REDACTED_LF***" in record.output_data
        assert "sk-lf-" not in record.output_data
        assert record.attributes.get("gen_ai.usage.input_tokens") == 100
        assert record.attributes.get("gen_ai.usage.output_tokens") == 50


def test_deve_registrar_score_associado_ao_trace():
    cfg = TraceConfig(langfuse_public_key="pk-lf-mock", langfuse_secret_key="sk-lf-mock")
    client = LangfuseOtelClient(config=cfg, in_memory=True)

    with client.start_trace("score-test") as trace:
        score = ScoreData(
            name="relevancia",
            value=0.98,
            data_type="numeric",
            comment="Perfeito",
        )
        recorded = client.record_score(score, parent=trace)
        assert recorded.name == "relevancia"
        assert recorded.value == 0.98
        assert recorded.comment == "Perfeito"


def test_deve_capturar_excecoes_no_span_sem_quebrar_fluxo():
    cfg = TraceConfig(langfuse_public_key="pk-lf-mock", langfuse_secret_key="sk-lf-mock")
    client = LangfuseOtelClient(config=cfg, in_memory=True)

    with pytest.raises(ValueError, match="Erro simulado"):
        with client.start_trace("error-trace") as trace:
            with client.start_span("span-error", parent=trace) as span:
                raise ValueError("Erro simulado")

    # Verifica que o span registrou o status de erro
    assert span.status_code == "ERROR"
    assert "Erro simulado" in span.status_description
