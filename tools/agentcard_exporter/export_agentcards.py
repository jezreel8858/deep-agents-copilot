"""
AgentCard Exporter — A2A Standard (Linux Foundation v1.0.0 / IETF draft-aevum-agentcard-00)
Exporta metadados dos catálogos de agentes em .github/agents/ para o padrão aberto AgentCard.
"""

import json
import os
import glob
from pathlib import Path
from typing import Dict, Any, List
import yaml
import jsonschema

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = BASE_DIR / ".github" / "agents"
SCHEMA_PATH = BASE_DIR / "docs" / "schemas" / "agentcard.schema.json"
OUTPUT_DIR = BASE_DIR / ".a2a" / "agentcards"


def infer_role(agent_id: str, domain: str) -> str:
    """Classifica o role de acordo com a taxonomia do ecossistema."""
    aid = agent_id.lower()
    if "router" in aid:
        return "router"
    if "advisor" in aid:
        return "advisor"
    if "developer" in aid or "migration-dev" in aid or "maintainer" in aid or "factory" in aid:
        return "implementer"
    if "fixer" in aid or aid == "bug-triage":
        return "fixer"
    if "test" in aid or "tester" in aid:
        return "tester"
    if "auditor" in aid or "sentinel" in aid:
        return "auditor"
    if "planner" in aid or "mapper" in aid:
        return "planner"
    if "search" in aid:
        return "researcher"
    if "gatekeeper" in aid or "verifier" in aid:
        return "gatekeeper"
    return "specialist"


def infer_security_profile(role: str, tools: List[str]) -> Dict[str, Any]:
    """Define as zonas de ferramentas e nível de privilégio."""
    mutating_tools = {"replace_string_in_file", "insert_edit_into_file", "create_file", "edit_file"}
    exec_tools = {"run_in_terminal"}

    zones = ["read-only"]
    has_mutating = any(t in mutating_tools for t in tools)
    has_exec = any(t in exec_tools for t in tools)

    if has_mutating or role in ["implementer", "fixer"]:
        zones.append("mutating")
    if has_exec:
        zones.append("execution")

    least_priv = "strict" if role in ["advisor", "auditor", "gatekeeper", "researcher"] else "standard"
    if "execution" in zones:
        least_priv = "elevated"

    return {
        "tool_zones": zones,
        "least_privilege_level": least_priv,
        "data_sensitivity": "internal"
    }


def infer_cost_tier(model: str) -> str:
    m = model.lower()
    if "haiku" in m:
        return "0.33x"
    if "opus" in m:
        return "3x"
    return "1x"


def convert_agent_to_agentcard(agent_id: str, data: Dict[str, Any], catalog_path: Path) -> Dict[str, Any]:
    """Converte a entrada do catálogo para a especificação AgentCard v1.0.0."""
    role = infer_role(agent_id, data.get("domain", ""))
    tools = data.get("tools", ["read_file", "ask_questions", "run_subagent"])
    security_profile = infer_security_profile(role, tools)
    model = data.get("model", "Claude Sonnet 5")

    capabilities = data.get("keywords", [])
    if not capabilities:
        capabilities = [role, agent_id.replace("-", " ")]

    skills = data.get("related_skills", [])
    if not skills:
        skills = ["agent-contracts", "handoff-governance"]

    card = {
        "schemaVersion": "1.0.0",
        "protocol": "A2A/1.0.0",
        "id": agent_id,
        "name": data.get("name", agent_id.replace("-", " ").title()),
        "version": data.get("version", "1.0.0"),
        "description": data.get("description", f"AI Agent especializado em {data.get('domain', agent_id)}."),
        "domain": data.get("domain", "Engenharia de Software / Governança Multi-Agente"),
        "role": role,
        "capabilities": capabilities,
        "skills": skills,
        "tools": tools,
        "security_profile": security_profile,
        "model_preferences": {
            "recommended_model": model,
            "cost_tier": infer_cost_tier(model)
        },
        "input_contract": {
            "accepts_payload": "yaml / markdown",
            "required_fields": ["emissor", "contexto", "motivo"]
        },
        "output_contract": {
            "expected_format": "markdown estruturado com Agente Ativo e Handoff",
            "emits_handoff": True,
            "context_offloading_supported": True
        },
        "metadata": {
            "catalog_source": str(catalog_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "priority": data.get("priority", 10),
            "estimated_time_minutes": data.get("estimated_time_minutes", 15)
        }
    }
    return card


def export_all_agentcards() -> Dict[str, Any]:
    """Varre todos os catálogos e gera os arquivos AgentCard JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    catalog_files = glob.glob(str(AGENTS_DIR / "**/*catalog*.yaml"), recursive=True)
    exported = {}
    validation_errors = []

    for cpath_str in catalog_files:
        cpath = Path(cpath_str)
        with open(cpath, "r", encoding="utf-8") as f:
            cdata = yaml.safe_load(f)
        agents = cdata.get("agents", {})
        for aid, adata in agents.items():
            if not isinstance(adata, dict):
                continue
            card = convert_agent_to_agentcard(aid, adata, cpath)

            # Validar contra o schema
            try:
                jsonschema.validate(instance=card, schema=schema)
            except jsonschema.ValidationError as err:
                validation_errors.append(f"Agent {aid} validation failed: {err.message}")
                continue

            card_file = OUTPUT_DIR / f"{aid}.agentcard.json"
            with open(card_file, "w", encoding="utf-8") as out:
                json.dump(card, out, indent=2, ensure_ascii=False)
            exported[aid] = card

    # Gerar índice consolidado
    index_file = OUTPUT_DIR / "agentcards.index.json"
    index_data = {
        "protocol": "A2A/1.0.0",
        "total_agentcards": len(exported),
        "agents": {aid: {"name": c["name"], "role": c["role"], "domain": c["domain"], "version": c["version"]} for aid, c in exported.items()}
    }
    with open(index_file, "w", encoding="utf-8") as out:
        json.dump(index_data, out, indent=2, ensure_ascii=False)

    return {
        "total_exported": len(exported),
        "output_dir": str(OUTPUT_DIR),
        "validation_errors": validation_errors
    }


if __name__ == "__main__":
    result = export_all_agentcards()
    print(f"Exported {result['total_exported']} AgentCards to {result['output_dir']}")
    if result["validation_errors"]:
        print(f"Errors ({len(result['validation_errors'])}):")
        for e in result["validation_errors"]:
            print(" -", e)

