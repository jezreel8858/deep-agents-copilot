"""
Configurações do cliente de tracing e integração Langfuse/OTel.
"""

from __future__ import annotations

import base64
import os
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class TraceConfig(BaseModel):
    """Modelo de configuração do cliente de tracing."""

    langfuse_public_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY")
    )
    langfuse_secret_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY")
    )
    langfuse_host: str = Field(
        default_factory=lambda: os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    langfuse_otlp_auth: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGFUSE_OTLP_AUTH")
    )
    deploy_env: str = Field(
        default_factory=lambda: os.getenv("DEPLOY_ENV", "development")
    )
    service_name: str = Field(
        default_factory=lambda: os.getenv("OTEL_SERVICE_NAME", "deep-agents-copilot")
    )
    otlp_endpoint: Optional[str] = Field(
        default_factory=lambda: os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    )
    is_enabled: bool = False

    @model_validator(mode="after")
    def compute_auth_and_enabled(self) -> TraceConfig:
        """Calcula o token basic auth e define se o cliente está ativo."""
        # Se temos public e secret key mas não temos otlp_auth, gera em base64
        if self.langfuse_public_key and self.langfuse_secret_key:
            if not self.langfuse_otlp_auth:
                raw_token = f"{self.langfuse_public_key}:{self.langfuse_secret_key}"
                self.langfuse_otlp_auth = base64.b64encode(raw_token.encode("utf-8")).decode("utf-8")
            self.is_enabled = True
        elif self.langfuse_otlp_auth or self.otlp_endpoint:
            self.is_enabled = True

        return self
