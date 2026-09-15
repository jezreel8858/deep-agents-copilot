"""
Validação de Conformidade do Padrão A2A AgentCard (Linux Foundation v1.0.0 / IETF draft-aevum-agentcard-00)
Garante que todos os agentes registrados no ecossistema possuem AgentCards válidos e compatíveis.
"""

import json
from pathlib import Path
import pytest
import jsonschema

from tools.agentcard_exporter.export_agentcards import (
    export_all_agentcards,
    convert_agent_to_agentcard,
    infer_role,
    infer_security_profile
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = BASE_DIR / "docs" / "schemas" / "agentcard.schema.json"


@pytest.fixture
def agentcard_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_agentcard_schema_is_valid(agentcard_schema):
    """Garante que o schema JSON do AgentCard é sintaticamente válido."""
    assert agentcard_schema["$id"] == "https://deep-agents-copilot/schemas/agentcard.schema.json"
    assert "required" in agentcard_schema
    assert "properties" in agentcard_schema
    assert "security_profile" in agentcard_schema["properties"]


def test_export_all_agentcards_generates_valid_cards(agentcard_schema):
    """Verifica se todos os 65 agentes dos catálogos exportam AgentCards válidos sem erro de schema."""
    result = export_all_agentcards()
    assert result["total_exported"] >= 65
    assert len(result["validation_errors"]) == 0

    output_dir = Path(result["output_dir"])
    card_files = list(output_dir.glob("*.agentcard.json"))
    assert len(card_files) == result["total_exported"]

    # Validar uma amostra profunda de cards gerados
    for cfile in card_files:
        with open(cfile, "r", encoding="utf-8") as f:
            card_data = json.load(f)
        jsonschema.validate(instance=card_data, schema=agentcard_schema)
        assert card_data["protocol"] == "A2A/1.0.0"
        assert len(card_data["capabilities"]) > 0
        assert len(card_data["security_profile"]["tool_zones"]) > 0


def test_least_privilege_mcp_scoping_for_advisory_agents(agentcard_schema):
    """Garante conformidade com NSA CSI MCP Security: agentes consultivos/advisors não recebem zona 'mutating'."""
    advisory_agents = [
        "agent-auditor",
        "adr-sentinel",
        "repo-hygiene-auditor",
        "angular-arch-advisor",
        "spring-boot-arch-advisor",
        "ejb-arch-advisor"
    ]
    result = export_all_agentcards()
    output_dir = Path(result["output_dir"])

    for aid in advisory_agents:
        cfile = output_dir / f"{aid}.agentcard.json"
        if cfile.exists():
            with open(cfile, "r", encoding="utf-8") as f:
                card = json.load(f)
            assert "mutating" not in card["security_profile"]["tool_zones"], (
                f"Agente consultivo {aid} não deve conter zona 'mutating' no seu perfil MCP!"
            )
            assert card["security_profile"]["least_privilege_level"] == "strict"

