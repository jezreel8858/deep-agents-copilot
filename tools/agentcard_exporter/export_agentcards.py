"""
AgentCard Exporter — A2A Standard (Linux Foundation v1.0.0 / IETF draft-aevum-agentcard-00)
Exporta metadados dos catálogos de agentes em .github/agents/ para o padrão aberto AgentCard.

Guard-rails de Execução (R-051 / R-040):
    python tools/agentcard_exporter/export_agentcards.py            # modo --check (default: fail-safe, exit code 1 se drift)
    python tools/agentcard_exporter/export_agentcards.py --check    # modo CI explícito
    python tools/agentcard_exporter/export_agentcards.py --dry-run  # simulação com visualização de diffs sem gravar em disco
    python tools/agentcard_exporter/export_agentcards.py --apply    # aplica gravação em .a2a/agentcards/
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import glob
import sys
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


def export_all_agentcards(mode: str = "apply") -> Dict[str, Any]:
    """
    Gera AgentCards a partir dos catálogos.
    Modos:
      - 'apply': grava arquivos em disco (.a2a/agentcards/)
      - 'check': apenas verifica drift e validade de schema sem gravar nada
      - 'dry-run': calcula e exibe diffs sem gravar nada
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    catalog_files = glob.glob(str(AGENTS_DIR / "**/*catalog*.yaml"), recursive=True)
    exported: Dict[str, Any] = {}
    validation_errors: List[str] = []
    drifted: List[str] = []
    diff_outputs: List[str] = []

    for cpath_str in catalog_files:
        cpath = Path(cpath_str)
        with open(cpath, "r", encoding="utf-8") as f:
            cdata = yaml.safe_load(f)
        agents = cdata.get("agents", {})
        for aid, adata in agents.items():
            if not isinstance(adata, dict):
                continue
            card = convert_agent_to_agentcard(aid, adata, cpath)

            try:
                jsonschema.validate(instance=card, schema=schema)
            except jsonschema.ValidationError as err:
                validation_errors.append(f"Agent {aid} validation failed: {err.message}")
                continue

            card_file = OUTPUT_DIR / f"{aid}.agentcard.json"
            new_content = json.dumps(card, indent=2, ensure_ascii=False) + "\n"

            if not card_file.is_file():
                drifted.append(f"{aid} (arquivo ausente em disco)")
                if mode == "dry-run":
                    diff_outputs.append(f"[NOVO] {card_file.name}")
            else:
                old_content = card_file.read_text(encoding="utf-8")
                # Comparação normalizada
                if json.loads(old_content) != card:
                    drifted.append(f"{aid} (conteúdo divergente)")
                    if mode == "dry-run":
                        diff = difflib.unified_diff(
                            old_content.splitlines(keepends=True),
                            new_content.splitlines(keepends=True),
                            fromfile=f"a/{card_file.name}",
                            tofile=f"b/{card_file.name}",
                        )
                        diff_outputs.append("".join(diff))

            if mode == "apply":
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                with open(card_file, "w", encoding="utf-8") as out:
                    out.write(new_content)

            exported[aid] = card

    # Validar index consolidado
    index_file = OUTPUT_DIR / "agentcards.index.json"
    index_data = {
        "protocol": "A2A/1.0.0",
        "total_agentcards": len(exported),
        "agents": {
            aid: {"name": c["name"], "role": c["role"], "domain": c["domain"], "version": c["version"]}
            for aid, c in sorted(exported.items())
        }
    }
    index_content = json.dumps(index_data, indent=2, ensure_ascii=False) + "\n"
    if not index_file.is_file():
        drifted.append("agentcards.index.json (ausente em disco)")
    else:
        old_idx = index_file.read_text(encoding="utf-8")
        if json.loads(old_idx) != index_data:
            drifted.append("agentcards.index.json (conteúdo divergente)")
            if mode == "dry-run":
                diff = difflib.unified_diff(
                    old_idx.splitlines(keepends=True),
                    index_content.splitlines(keepends=True),
                    fromfile="a/agentcards.index.json",
                    tofile="b/agentcards.index.json",
                )
                diff_outputs.append("".join(diff))

    if mode == "apply":
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(index_file, "w", encoding="utf-8") as out:
            out.write(index_content)

    return {
        "total_exported": len(exported),
        "output_dir": str(OUTPUT_DIR),
        "validation_errors": validation_errors,
        "drifted": drifted,
        "diff_outputs": diff_outputs,
        "mode": mode
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Aplica a gravação dos AgentCards atualizados em disco (.a2a/agentcards/).")
    parser.add_argument("--dry-run", action="store_true", help="Simula a exportação e exibe diffs sem gravar nada em disco.")
    parser.add_argument("--check", action="store_true", help="Modo CI fail-safe: exit code 1 se houver drift, não grava nada (default).")
    args = parser.parse_args()

    # Comportamento default: se nenhuma flag for informada, opera como --check (fail-safe)
    if args.apply:
        mode = "apply"
    elif args.dry_run:
        mode = "dry-run"
    else:
        mode = "check"

    result = export_all_agentcards(mode=mode)
    print(f"Modo: {mode}")
    print(f"Catálogos processados: {result['total_exported']} AgentCards mapeados")
    print(f"Drift detectado: {len(result['drifted'])}")

    if result["drifted"]:
        for d in result["drifted"]:
            print(f"  - {d}")

    if mode == "dry-run" and result["diff_outputs"]:
        print("\nDiffs detectados:")
        for diff in result["diff_outputs"]:
            print(diff)

    if result["validation_errors"]:
        print(f"\nErros de validação de schema ({len(result['validation_errors'])}):")
        for err in result["validation_errors"]:
            print(f"  - {err}")

    if mode == "check":
        if result["drifted"] or result["validation_errors"]:
            print("\nExecute 'python tools/agentcard_exporter/export_agentcards.py --apply' para sincronizar os AgentCards.")
            return 1
        print("AgentCards 100% em paridade com os catálogos (drift=0).")
        return 0

    if mode == "apply":
        print(f"AgentCards gravados com sucesso em {result['output_dir']}.")
        return 1 if result["validation_errors"] else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
