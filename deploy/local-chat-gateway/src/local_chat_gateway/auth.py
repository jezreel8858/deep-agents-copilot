"""auth — Bearer local via `GATEWAY_API_KEY` (sem OAuth/JWT nesta fase).

Contrato: header `Authorization` ausente ou malformado -> 401; token que
nao bate com `Settings.gateway_api_key` -> 401. O startup recusa subir se
`gateway_api_key == "change-me"` (ver `config.Settings.validate_startup`).
"""

from __future__ import annotations

import logging
import secrets

from fastapi import Depends, Header, HTTPException, status

from local_chat_gateway.config import Settings, get_settings

logger = logging.getLogger(__name__)

_BEARER_PREFIX = "Bearer "


async def require_bearer_token(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Dependencia FastAPI que valida o Bearer local em rotas autenticadas.

    Args:
        authorization: Valor bruto do header `Authorization`.
        settings: Configuracao injetada (override em testes via
            `app.dependency_overrides[get_settings]`).

    Raises:
        HTTPException: 401 se o header estiver ausente, malformado, vazio
            ou nao corresponder a `settings.gateway_api_key`.
    """
    if authorization is None or not authorization.startswith(_BEARER_PREFIX):
        logger.warning("bearer_rejected: missing or malformed Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or malformed Authorization header",
        )
    token = authorization[len(_BEARER_PREFIX) :].strip()
    if not token or not secrets.compare_digest(token, settings.gateway_api_key):
        logger.warning("bearer_rejected: invalid bearer token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid bearer token",
        )
