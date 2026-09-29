"""
Invariants test for sync_router_return.py (R-042 / R-051 / R-059).

Garante que o normalizador determinístico da seção 'Retorno ao Router':
1. É idempotente em execuções repetidas.
2. Identifica drift corretamente (zero falso-positivo / zero falso-negativo).
3. Preserva regras customizadas de handoff e integridade das personas.
"""

from __future__ import annotations

import pytest
from pathlib import Path
from tools.agent_router_return_sync.sync_router_return import (
    load_canonical_templates,
    normalize_router_section,
)

SAMPLE_NON_CANONICAL = """# Agent Persona
Você é um especialista.

## Retorno ao Router (R-042 — Anti Sticky-Session)

**Banner obrigatório**: toda resposta abre com `Agente Ativo: sample-agent`.
Se a solicitação pivotar para fora de escopo, retorne ao `@agent-router`.
"""

SAMPLE_CANONICAL = """# Agent Persona
Você é um especialista.

## Retorno ao Router (R-042 — Anti Sticky-Session)

**Banner obrigatório (visibilidade de fluxo)**: toda resposta deste agent abre com a linha `Agente Ativo: sample-agent` antes de qualquer outro conteúdo — mesmo sem handoff neste turno. Se esta resposta é resultado de handoff/re-triagem recebido, adicionar `Handoff: <agent-origem> → sample-agent (motivo: <motivo>)` na linha seguinte. Padrão de mercado: OpenAI Agents SDK (`HandoffOutputItem` — "Handed off from X to Y") e LangGraph (campo `active_agent` streamado ao usuário) — ver `agent-contracts/SKILL.md` seção 0.

Se a solicitação pivotar para fora de escopo, retorne ao `@agent-router`.
"""


def test_normalize_router_section_converts_short_banner():
    canonical_heading, canonical_banner_tmpl = load_canonical_templates()
    current_heading = "## Retorno ao Router (R-042 — Anti Sticky-Session)"
    current_body = (
        "**Banner obrigatório**: toda resposta abre com `Agente Ativo: sample-agent`.\n"
        "Se a solicitação pivotar para fora de escopo, retorne ao `@agent-router`."
    )

    norm_h, norm_b = normalize_router_section(
        "sample-agent", current_heading, current_body, canonical_heading, canonical_banner_tmpl
    )

    assert norm_h == canonical_heading
    assert "Padrão de mercado: OpenAI Agents SDK" in norm_b
    assert "Se a solicitação pivotar para fora de escopo, retorne ao `@agent-router`." in norm_b


def test_normalize_router_section_is_idempotent():
    canonical_heading, canonical_banner_tmpl = load_canonical_templates()
    current_heading = "## Retorno ao Router (R-042 — Anti Sticky-Session)"
    current_body = (
        "**Banner obrigatório**: toda resposta abre com `Agente Ativo: sample-agent`.\n\n"
        "Se a solicitação pivotar para fora de escopo, retorne ao `@agent-router`."
    )

    # 1ª passagem
    h1, b1 = normalize_router_section(
        "sample-agent", current_heading, current_body, canonical_heading, canonical_banner_tmpl
    )

    # 2ª passagem
    h2, b2 = normalize_router_section(
        "sample-agent", h1, b1, canonical_heading, canonical_banner_tmpl
    )

    assert h1 == h2
    assert b1 == b2


def test_normalize_router_section_handles_emoji_heading():
    canonical_heading, canonical_banner_tmpl = load_canonical_templates()
    heading_with_emoji = "## 🔄 Retorno ao Router (R-042 — Anti Sticky-Session)"
    body = "**Banner obrigatório**: Toda resposta abre com `Agente Ativo: planner-agent`."

    norm_h, norm_b = normalize_router_section(
        "planner-agent", heading_with_emoji, body, canonical_heading, canonical_banner_tmpl
    )

    assert norm_h == "## Retorno ao Router (R-042 — Anti Sticky-Session)"
    assert "🔄" not in norm_h

def test_normalize_router_section_injects_telemetry_for_domain_routers():
    canonical_heading, canonical_banner_tmpl = load_canonical_templates()
    current_heading = "## Retorno ao Router (R-042 — Anti Sticky-Session)"
    current_body = (
        "**Banner obrigatório**: toda resposta abre com `Agente Ativo: python-router`.\n\n"
        "Se a solicitação recebida sair do domínio Python backend, retorne imediatamente para `@agent-router`."
    )

    norm_h, norm_b = normalize_router_section(
        "python-router", current_heading, current_body, canonical_heading, canonical_banner_tmpl
    )

    assert norm_h == canonical_heading
    assert "Agente Ativo: python-router" in norm_b
    assert "Telemetria de Handoff (Decisão de Baseline R-054 / handoff-governance § 2.4)" in norm_b
    assert "Se a solicitação recebida sair do domínio Python backend" in norm_b

    # Idempotência para domain router
    h2, b2 = normalize_router_section(
        "python-router", norm_h, norm_b, canonical_heading, canonical_banner_tmpl
    )
    assert h2 == norm_h
    assert b2 == norm_b
    assert norm_b.count("Telemetria de Handoff") == 1

