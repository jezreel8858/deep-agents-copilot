"""Testes unitários de autenticação e validação de configuração do gateway.

Valida `require_bearer_token` (dependência FastAPI) e `Settings.validate_startup`.
"""

from __future__ import annotations

import asyncio
import logging

import pytest
from fastapi import HTTPException

from local_chat_gateway.auth import require_bearer_token
from local_chat_gateway.config import (
    FORBIDDEN_GATEWAY_API_KEY,
    InvalidGatewayConfigurationError,
    Settings,
)


def test_deve_lancar_excecao_quando_api_key_for_placeholder_inseguro() -> None:
    # Arrange
    settings = Settings(gateway_api_key=FORBIDDEN_GATEWAY_API_KEY)

    # Act & Assert
    with pytest.raises(
        InvalidGatewayConfigurationError,
        match="GATEWAY_API_KEY nao pode ser 'change-me'",
    ):
        settings.validate_startup()


def test_nao_deve_lancar_excecao_quando_api_key_for_valida() -> None:
    # Arrange
    settings = Settings(gateway_api_key="minha-chave-segura-123")

    # Act & Assert
    settings.validate_startup()


def test_deve_lancar_401_quando_authorization_header_ausente() -> None:
    # Arrange
    settings = Settings(gateway_api_key="real-key")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_bearer_token(authorization=None, settings=settings))

    assert exc_info.value.status_code == 401
    assert "missing or malformed" in exc_info.value.detail


@pytest.mark.parametrize(
    "auth_header",
    [
        "Basic dXNlcjpwYXNz",
        "Token abcdef",
        "bearer real-key",  # Case-sensitive "Bearer "
        "Bearer",  # Sem token
        "Bearer   ",  # Apenas espaços
    ],
)
def test_deve_lancar_401_quando_authorization_header_malformado(
    auth_header: str,
) -> None:
    # Arrange
    settings = Settings(gateway_api_key="real-key")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_bearer_token(authorization=auth_header, settings=settings))

    assert exc_info.value.status_code == 401


def test_deve_lancar_401_quando_bearer_token_incorreto() -> None:
    # Arrange
    settings = Settings(gateway_api_key="real-key")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            require_bearer_token(authorization="Bearer wrong-key", settings=settings)
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "invalid bearer token"


def test_deve_autorizar_com_sucesso_quando_bearer_token_correto() -> None:
    # Arrange
    settings = Settings(gateway_api_key="real-key")

    # Act
    resultado = asyncio.run(
        require_bearer_token(authorization="Bearer real-key", settings=settings)
    )

    # Assert
    assert resultado is None


def test_deve_emitir_warning_sem_vazar_segredo_quando_header_ausente(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    segredo_real = "chave-super-secreta-gateway-xyz"
    settings = Settings(gateway_api_key=segredo_real)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(HTTPException):
            asyncio.run(require_bearer_token(authorization=None, settings=settings))

    # Assert
    assert "bearer_rejected: missing or malformed Authorization header" in caplog.text
    assert segredo_real not in caplog.text


def test_deve_emitir_warning_sem_vazar_segredo_quando_header_malformado(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    segredo_real = "chave-super-secreta-gateway-xyz"
    header_malformado = "Basic credencial_maliciosa_999"
    settings = Settings(gateway_api_key=segredo_real)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(HTTPException):
            asyncio.run(
                require_bearer_token(authorization=header_malformado, settings=settings)
            )

    # Assert
    assert "bearer_rejected: missing or malformed Authorization header" in caplog.text
    assert segredo_real not in caplog.text
    assert "credencial_maliciosa_999" not in caplog.text


def test_deve_emitir_warning_sem_vazar_segredo_quando_bearer_invalido(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    segredo_real = "chave-super-secreta-gateway-xyz"
    token_invalido = "token-atacante-completamente-errado-456"
    settings = Settings(gateway_api_key=segredo_real)

    # Act
    with caplog.at_level(logging.WARNING):
        with pytest.raises(HTTPException):
            asyncio.run(
                require_bearer_token(
                    authorization=f"Bearer {token_invalido}", settings=settings
                )
            )

    # Assert
    assert "bearer_rejected: invalid bearer token" in caplog.text
    assert segredo_real not in caplog.text
    assert token_invalido not in caplog.text
