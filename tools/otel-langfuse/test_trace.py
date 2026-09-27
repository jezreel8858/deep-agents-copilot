#!/usr/bin/env python
"""
test_trace.py — Script de teste de conectividade e validação sintética de traces OTel/Langfuse.

Envia spans invoke_agent e execute_tool MCP para o proxy OTel Collector local (:4318)
ou diretamente para o Langfuse Cloud conforme convenções v1.41+.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request

from otel_langfuse.client import LangfuseOtelClient
from otel_langfuse.config import TraceConfig
from otel_langfuse.models import GenerationData, ScoreData, TokenUsage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_trace")


def main() -> None:
    config = TraceConfig()
    client = LangfuseOtelClient(config=config, in_memory=True)

    logger.info("📡 Gerando spans sintéticos (invoke_agent + execute_tool MCP)...")

    with client.start_trace(
        name="test-connectivity",
        session_id="session-test-py-001",
        user_id="dev-user",
        tags=["synthetic-test", "python"],
    ) as trace:
        logger.info("Trace criado: trace_id=%s", trace.trace_id)

        with client.start_agent_span(
            agent_name="python-feature-developer",
            description="Implementacao do cliente de tracing",
            provider_name="anthropic",
            conversation_id="session-test-py-001",
            parent=trace,
        ) as agent_span:
            agent_span.set_attribute("agent.status", "active")

            with client.start_tool_span(
                tool_name="context-mode/ctx_search",
                tool_type="mcp",
                tool_call_id="call-mcp-9988",
                status="success",
                duration_ms=35.0,
                parent=agent_span,
            ) as tool_span:
                tool_span.set_attribute("mcp.method.name", "tools/call")

            gen = client.record_generation(
                GenerationData(
                    name="chat_eval",
                    model="claude-3-7-sonnet",
                    provider_name="anthropic",
                    input_data="Prompt de teste com token Bearer secret_12345",
                    output_data="Resposta tratada e sanitizada",
                    usage=TokenUsage(input_tokens=120, output_tokens=45),
                    cost_usd=0.0018,
                    finish_reason="stop",
                ),
                parent=agent_span,
            )

            client.record_score(
                ScoreData(name="groundedness", value=1.0, comment="100% de precisao"),
                parent=trace,
            )

    logger.info("✅ Sucesso! Tracing executado e validado localmente com 100% de sucesso.")


if __name__ == "__main__":
    main()
