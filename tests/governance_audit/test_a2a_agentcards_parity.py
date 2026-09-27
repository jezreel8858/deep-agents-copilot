"""
Teste de Paridade e Integridade do Ecossistema A2A AgentCards (R-051 / R-015 / R-040).
Garante 100% de paridade entre arquivos *.agent.md em .github/agents/ e os AgentCards em .a2a/agentcards/.
"""

import json
from pathlib import Path
import pytest
import jsonschema
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = BASE_DIR / ".github" / "agents"
AGENTCARDS_DIR = BASE_DIR / ".a2a" / "agentcards"
SCHEMA_PATH = BASE_DIR / "docs" / "schemas" / "agentcard.schema.json"


@pytest.fixture(scope="session")
def agentcard_schema():
    """Carrega o schema oficial A2A AgentCard v1.0.0."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_agent_md_files():
    """Descobre recursivamente todos os arquivos *.agent.md do ecossistema."""
    files = list(AGENTS_DIR.glob("**/*.agent.md"))
    assert len(files) > 0, "Nenhum arquivo *.agent.md encontrado em .github/agents/"
    return sorted(files, key=lambda p: p.name)


def extract_frontmatter(file_path: Path):
    """Extrai e parseia o frontmatter YAML de um arquivo .agent.md."""
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            return yaml.safe_load(parts[1]) or {}
        except Exception:
            return {}
    return {}


def test_every_agent_md_has_matching_agentcard(all_agent_md_files):
    """Garante que todo arquivo *.agent.md (recursivo) possui um <agent_name>.agentcard.json correspondente."""
    missing_cards = []
    for agent_file in all_agent_md_files:
        agent_id = agent_file.name.replace(".agent.md", "")
        card_file = AGENTCARDS_DIR / f"{agent_id}.agentcard.json"
        if not card_file.is_file():
            missing_cards.append({
                "agent_id": agent_id,
                "agent_file": str(agent_file.relative_to(BASE_DIR)),
                "expected_card": str(card_file.relative_to(BASE_DIR))
            })

    assert len(missing_cards) == 0, (
        f"Detectados {len(missing_cards)} agents sem AgentCard correspondente em .a2a/agentcards/:\n"
        + "\n".join(f" - {m['agent_id']} ({m['agent_file']}) -> ausente {m['expected_card']}" for m in missing_cards)
    )


def test_each_agentcard_has_valid_json_and_required_fields(all_agent_md_files, agentcard_schema):
    """Garante que cada agentcard possui JSON válido, semântica correta e campos obrigatórios preenchidos."""
    for agent_file in all_agent_md_files:
        agent_id = agent_file.name.replace(".agent.md", "")
        card_file = AGENTCARDS_DIR / f"{agent_id}.agentcard.json"
        assert card_file.is_file(), f"Agentcard ausente para {agent_id}"

        with open(card_file, "r", encoding="utf-8") as f:
            card = json.load(f)

        # Validação formal contra o schema canônico A2A
        jsonschema.validate(instance=card, schema=agentcard_schema)

        # Validação semântica adicional de preenchimento dos campos obrigatórios
        assert card["schemaVersion"] == "1.0.0"
        assert card["protocol"] == "A2A/1.0.0"
        assert card["id"] == agent_id
        assert bool(card.get("name")), f"Campo 'name' vazio no card {agent_id}"
        assert bool(card.get("version")), f"Campo 'version' vazio no card {agent_id}"
        assert bool(card.get("description")), f"Campo 'description' vazio no card {agent_id}"
        assert bool(card.get("domain")), f"Campo 'domain' vazio no card {agent_id}"
        assert bool(card.get("role")), f"Campo 'role' vazio no card {agent_id}"
        assert isinstance(card.get("capabilities"), list) and len(card["capabilities"]) > 0
        assert isinstance(card.get("tools"), list) and len(card["tools"]) > 0
        assert isinstance(card.get("security_profile"), dict)
        assert len(card["security_profile"].get("tool_zones", [])) > 0
        assert card["security_profile"].get("least_privilege_level") in ["strict", "standard", "elevated"]
        assert isinstance(card.get("input_contract"), dict)
        assert bool(card["input_contract"].get("accepts_payload"))
        assert len(card["input_contract"].get("required_fields", [])) > 0
        assert isinstance(card.get("output_contract"), dict)
        assert bool(card["output_contract"].get("expected_format"))


def test_agentcard_name_matches_agent_md_frontmatter(all_agent_md_files):
    """Garante que o name/id do agentcard corresponde exatamente ao name definido no frontmatter do .agent.md."""
    mismatches = []
    for agent_file in all_agent_md_files:
        agent_id = agent_file.name.replace(".agent.md", "")
        card_file = AGENTCARDS_DIR / f"{agent_id}.agentcard.json"
        assert card_file.is_file(), f"Agentcard ausente para {agent_id}"

        fm = extract_frontmatter(agent_file)
        fm_name = fm.get("name")
        assert fm_name, f"Arquivo {agent_file.name} sem campo 'name' no frontmatter"

        with open(card_file, "r", encoding="utf-8") as f:
            card = json.load(f)

        card_id = card.get("id")
        card_name = card.get("name", "")

        # O id técnico kebab-case do card DEVE ser idêntico ao name do frontmatter
        if card_id != fm_name:
            mismatches.append(f"Agent {agent_file.name}: card.id ('{card_id}') != fm.name ('{fm_name}')")

        # O name do card deve corresponder ao name do frontmatter (diretamente ou via formatação legível display name)
        normalized_card_name = card_name.lower().replace(" ", "-")
        if not (card_name == fm_name or normalized_card_name == fm_name):
            mismatches.append(f"Agent {agent_file.name}: card.name ('{card_name}') não corresponde ao fm.name ('{fm_name}')")

    assert len(mismatches) == 0, (
        f"Detectadas {len(mismatches)} divergências de nome entre .agent.md e agentcard.json:\n"
        + "\n".join(f" - {m}" for m in mismatches)
    )
