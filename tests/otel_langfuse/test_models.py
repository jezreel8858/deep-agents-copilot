"""
Testes unitários para esquemas e DTOs (models.py e config.py).
"""

import pytest
from otel_langfuse.config import TraceConfig
from otel_langfuse.models import (
    GenerationData,
    ScoreData,
    SpanMetadata,
    TokenUsage,
)
from otel_langfuse.exceptions import ValidationException


def test_deve_criar_trace_config_valido_com_valores_padrao():
    cfg = TraceConfig()
    assert cfg.deploy_env == "development"
    assert cfg.service_name == "deep-agents-copilot"
    assert cfg.langfuse_host == "https://cloud.langfuse.com"
    assert cfg.is_enabled is False


def test_deve_gerar_auth_header_automaticamente_se_chaves_fornecidas():
    cfg = TraceConfig(
        langfuse_public_key="pk-lf-test",
        langfuse_secret_key="sk-lf-test",
    )
    assert cfg.is_enabled is True
    assert cfg.langfuse_otlp_auth is not None
    # pk-lf-test:sk-lf-test em base64 = cGstbGYtdGVzdDpzay1sZi10ZXN0
    assert cfg.langfuse_otlp_auth == "cGstbGYtdGVzdDpzay1sZi10ZXN0"


def test_deve_validar_geracao_llm_e_calculo_tokens():
    usage = TokenUsage(input_tokens=100, output_tokens=50)
    assert usage.total_tokens == 150

    gen = GenerationData(
        name="chat_generation",
        model="gpt-4o",
        input_data="Qual a capital?",
        output_data="Brasilia",
        usage=usage,
        cost_usd=0.002,
    )
    assert gen.model == "gpt-4o"
    assert gen.usage.total_tokens == 150


def test_deve_validar_score_com_limites_e_tipos():
    score = ScoreData(
        name="precisao",
        value=0.95,
        data_type="numeric",
        comment="Resposta correta e concisa",
    )
    assert score.value == 0.95
    assert score.data_type == "numeric"


def test_deve_lancar_validation_exception_quando_score_invalido():
    with pytest.raises(ValidationException):
        ScoreData(name="", value=1.0)
