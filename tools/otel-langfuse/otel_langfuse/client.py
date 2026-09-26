"""
Cliente de tracing com Langfuse e OpenTelemetry GenAI.

Implementa gerenciamento de contexto, fallback gracioso caso credenciais
estejam ausentes e sanitização automática de segredos.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Optional

from otel_langfuse.config import TraceConfig
from otel_langfuse.models import (
    GenerationData,
    ScoreData,
    SpanMetadata,
)
from otel_langfuse.sanitizer import scrub_data

logger = logging.getLogger(__name__)


def _generate_id(length: int = 16) -> str:
    """Gera identificadores hexadecimais aleatórios para traces e spans."""
    return uuid.uuid4().hex[:length]


class SpanContextManager:
    """Gerenciador de contexto para Spans e Traces."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str] = None,
        attributes: Optional[dict[str, Any]] = None,
        is_active: bool = True,
    ) -> None:
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.attributes: dict[str, Any] = attributes or {}
        self.is_active = is_active
        self.status_code = "OK"
        self.status_description: Optional[str] = None
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None

    def set_attribute(self, key: str, value: Any) -> SpanContextManager:
        """Define um atributo no span, aplicando sanitização."""
        self.attributes[key] = scrub_data(value)
        return self

    def __enter__(self) -> SpanContextManager:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> bool:
        self.end_time = time.time()
        if exc_val is not None:
            self.status_code = "ERROR"
            self.status_description = str(exc_val)
            self.attributes["error.type"] = exc_type.__name__ if exc_type else "Exception"
            self.attributes["error.message"] = scrub_data(str(exc_val))
            logger.error("Erro durante execução do span %s: %s", self.name, exc_val)
        return False  # Propaga exceções para o chamador


class LangfuseOtelClient:
    """Cliente unificado para observabilidade com Langfuse e OpenTelemetry."""

    def __init__(
        self,
        config: Optional[TraceConfig] = None,
        in_memory: bool = False,
    ) -> None:
        """Inicializa o cliente de tracing.

        Args:
            config: Configuração do cliente. Se None, inicializa padrão do ambiente.
            in_memory: Se True, simula tracing em memória para testes sem emitir I/O de rede.
        """
        self.config = config or TraceConfig()
        self.in_memory = in_memory
        self.is_active = self.config.is_enabled or self.in_memory

        if not self.is_active:
            logger.info("LangfuseOtelClient operando em modo FALLBACK GRACIOSO (desativado).")
        else:
            logger.debug(
                "LangfuseOtelClient ativo: service=%s env=%s in_memory=%s",
                self.config.service_name,
                self.config.deploy_env,
                self.in_memory,
            )

    def start_trace(
        self,
        name: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> SpanContextManager:
        """Inicia um novo Trace raiz.

        Args:
            name: Nome do trace representando a operação de negócio.
            session_id: Identificador da sessão multi-turn.
            user_id: Identificador do usuário para troubleshooting.
            tags: Lista de tags categóricas.
            metadata: Dicionário adicional de metadados.

        Returns:
            SpanContextManager representando o trace raiz.
        """
        trace_id = _generate_id(32)
        span_id = _generate_id(16)

        attrs: dict[str, Any] = {
            "service.name": self.config.service_name,
            "deployment.environment": self.config.deploy_env,
        }
        if session_id:
            attrs["session_id"] = session_id
            attrs["langfuse.session.id"] = session_id
            attrs["gen_ai.conversation.id"] = session_id
        if user_id:
            attrs["user_id"] = user_id
        if tags:
            attrs["tags"] = tags
        if metadata:
            attrs["metadata"] = scrub_data(metadata)

        return SpanContextManager(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            attributes=attrs,
            is_active=self.is_active,
        )

    def start_span(
        self,
        name: str,
        parent: Optional[SpanContextManager] = None,
        operation_name: Optional[str] = None,
        attributes: Optional[dict[str, Any]] = None,
    ) -> SpanContextManager:
        """Inicia um novo Span filho dentro de um trace.

        Args:
            name: Nome descritivo da etapa.
            parent: Span pai ou trace raiz.
            operation_name: Nome da operação semântica GenAI.
            attributes: Atributos iniciais.

        Returns:
            SpanContextManager para o novo span.
        """
        trace_id = parent.trace_id if parent else _generate_id(32)
        parent_id = parent.span_id if parent else None
        span_id = _generate_id(16)

        attrs: dict[str, Any] = attributes or {}
        if operation_name:
            attrs["gen_ai.operation.name"] = operation_name

        sanitized_attrs = scrub_data(attrs)

        return SpanContextManager(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_id,
            attributes=sanitized_attrs,
            is_active=self.is_active,
        )

    def start_agent_span(
        self,
        agent_name: str,
        description: Optional[str] = None,
        provider_name: Optional[str] = None,
        conversation_id: Optional[str] = None,
        parent: Optional[SpanContextManager] = None,
    ) -> SpanContextManager:
        """Inicia um Span do tipo invoke_agent conforme Semconv v1.41+."""
        span_name = f"invoke_agent: {agent_name}"
        span = self.start_span(name=span_name, parent=parent, operation_name="invoke_agent")
        span.set_attribute("gen_ai.agent.name", agent_name)

        if description:
            span.set_attribute("gen_ai.agent.description", description)
        if provider_name:
            span.set_attribute("gen_ai.provider.name", provider_name)
        if conversation_id:
            span.set_attribute("gen_ai.conversation.id", conversation_id)
            span.set_attribute("langfuse.session.id", conversation_id)

        return span

    def start_tool_span(
        self,
        tool_name: str,
        tool_type: str = "mcp",
        tool_call_id: Optional[str] = None,
        status: str = "success",
        duration_ms: Optional[float] = None,
        parent: Optional[SpanContextManager] = None,
    ) -> SpanContextManager:
        """Inicia um Span do tipo execute_tool conforme Semconv v1.41+."""
        span_name = f"execute_tool: {tool_name}"
        span = self.start_span(name=span_name, parent=parent, operation_name="execute_tool")
        span.set_attribute("gen_ai.tool.name", tool_name)
        span.set_attribute("gen_ai.tool.type", tool_type)
        span.set_attribute("tool.execution.status", status)

        if tool_call_id:
            span.set_attribute("gen_ai.tool.call.id", tool_call_id)
        if duration_ms is not None:
            span.set_attribute("tool.execution.duration_ms", duration_ms)

        return span

    def record_generation(
        self,
        data: GenerationData,
        parent: Optional[SpanContextManager] = None,
    ) -> GenerationData:
        """Registra uma geração LLM (Generation Observation) com sanitização."""
        sanitized_input = scrub_data(data.input_data)
        sanitized_output = scrub_data(data.output_data)

        gen_attrs = dict(data.attributes)
        gen_attrs["gen_ai.operation.name"] = "chat"
        gen_attrs["gen_ai.provider.name"] = data.provider_name
        gen_attrs["gen_ai.request.model"] = data.model

        if data.usage:
            gen_attrs["gen_ai.usage.input_tokens"] = data.usage.input_tokens
            gen_attrs["gen_ai.usage.output_tokens"] = data.usage.output_tokens
        if data.cost_usd is not None:
            gen_attrs["gen_ai.usage.cost_usd"] = data.cost_usd
        if data.finish_reason:
            gen_attrs["gen_ai.response.finish_reason"] = data.finish_reason
        if data.prompt_name:
            gen_attrs["langfuse.prompt.name"] = data.prompt_name
        if data.prompt_version:
            gen_attrs["langfuse.prompt.version"] = data.prompt_version

        cleaned_gen = GenerationData(
            name=data.name,
            model=data.model,
            provider_name=data.provider_name,
            input_data=sanitized_input,
            output_data=sanitized_output,
            usage=data.usage,
            cost_usd=data.cost_usd,
            finish_reason=data.finish_reason,
            prompt_name=data.prompt_name,
            prompt_version=data.prompt_version,
            attributes=gen_attrs,
        )

        if parent:
            parent.set_attribute(f"generation.{data.name}", gen_attrs)

        return cleaned_gen

    def record_score(
        self,
        score: ScoreData,
        parent: Optional[SpanContextManager] = None,
    ) -> ScoreData:
        """Registra uma avaliação ou pontuação de qualidade no trace ou span."""
        if parent:
            parent.set_attribute(f"score.{score.name}", score.model_dump())
        return score
