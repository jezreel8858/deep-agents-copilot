"""
test_agent_invocations.py — Testes Unitários de Invocação de Agentes e Subagentes
================================================================================
Valida a extração, cálculo de métricas e empacotamento do gráfico de barras de agentes
espelhado no estilo When You Code para o context-insight-visualizer.
"""

import json
import re
import sys
from pathlib import Path
import pytest

# Adiciona diretório do gerador ao path
tools_dir = Path(__file__).resolve().parent.parent.parent / "tools" / "context-insight-visualizer"
generator_dir = tools_dir / "generator"
if str(generator_dir) not in sys.path:
    sys.path.insert(0, str(generator_dir))

from extractor import (
    ContextDataExtractor,
    load_known_agents,
    DIRECT_PATTERNS,
    SUBAGENT_PATTERNS,
)
from insights_engine import InsightsEngine
import importlib.util
_spec = importlib.util.spec_from_file_location("context_insight_template_bundler", generator_dir / "template_bundler.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TemplateBundler = _mod.TemplateBundler


def test_load_known_agents_contains_canonical():
    """Valida que o catálogo de agentes conhecidos carrega agentes fundamentais."""
    agents = load_known_agents()
    assert "agent-router" in agents
    assert "feature-planner" in agents
    assert "codegraph-engine" in agents
    assert "prompt-structuring" in agents
    assert "deep-search" in agents
    assert "test-strategy" in agents


def test_subagent_pattern_detection():
    """Valida detecção de invocações de subagentes por múltiplos padrões."""
    samples = [
        ('run_subagent(agentName="feature-planner", task="planejar")', "feature-planner"),
        ('run_subagent(agentName: "Search", task="buscar")', "Search"),
        ('agentName: "codegraph-engine"', "codegraph-engine"),
        ('This is what has been accomplished by Custom Agent "agent-router":', "agent-router"),
        ('Delegando para @prompt-structuring — modelo solicitado', "prompt-structuring"),
        ('Delegado: @angular-router', "angular-router"),
        ('Handoff: @agent-router → @feature-planner (motivo: feature_planning)', "feature-planner"),
        ('subagent: @deep-search', "deep-search"),
    ]

    for text, expected_agent in samples:
        found = []
        for p in SUBAGENT_PATTERNS:
            for m in p.finditer(text):
                found.append(m.group(1).lower())
        assert expected_agent.lower() in found, f"Falha ao detectar subagente '{expected_agent}' em: {text}"


def test_direct_pattern_detection():
    """Valida detecção de invocações diretas de agentes por múltiplos padrões."""
    samples = [
        ("@agent-router analise este componente", "agent-router"),
        ("invoque o agent-router para decompor", "agent-router"),
        ("chame o agent angular-router", "angular-router"),
        ("Follow instructions in [commit](file:///d%3A/workspace/deep-agents-copilot/.github/prompts/commit.prompt.md).", "commit"),
        ("/agent-router como estruturar", "agent-router"),
        ("Agente Ativo: @codegraph-engine", "codegraph-engine"),
    ]

    for text, expected_agent in samples:
        found = []
        for p in DIRECT_PATTERNS:
            for m in p.finditer(text):
                found.append(m.group(1).lower())
        assert expected_agent.lower() in found, f"Falha ao detectar agente direto '{expected_agent}' em: {text}"


def test_insights_engine_agent_invocations():
    """Valida que o InsightsEngine propaga agentInvocations e calcula KPIs."""
    mock_extracted = {
        "meta": {"generatedAt": "2026-09-06T00:00:00Z", "sourcePaths": [], "warnings": []},
        "sessions": [{"sessionId": "s1", "eventCount": 5}],
        "eventsSummary": {
            "totalEvents": 10,
            "totalErrors": 0,
            "totalPrompts": 3,
            "totalReads": 5,
            "totalWrites": 5,
            "hourlyPattern": [{"hour": h, "count": 1} for h in range(24)],
            "agentInvocations": [
                {"agent": "agent-router", "total": 20, "direct": 15, "subagent": 5, "percentage": 100.0},
                {"agent": "feature-planner", "total": 10, "direct": 2, "subagent": 8, "percentage": 50.0},
            ],
        },
        "statsPid": {},
        "content": {},
    }

    engine = InsightsEngine(mock_extracted)
    payload = engine.build_payload()

    assert "agentInvocations" in payload
    assert len(payload["agentInvocations"]) == 2
    assert payload["agentInvocations"][0]["agent"] == "agent-router"
    assert payload["agentInvocations"][0]["total"] == 20

    kpis = payload["kpis"]
    assert kpis["totalAgentInvocations"] == 30
    assert kpis["subagentInvocations"] == 13
    assert kpis["topAgent"] == "agent-router"


def test_template_bundler_includes_agent_blocks():
    """Valida que o template empacotado contém os seletores e containers do gráfico de agentes."""
    template_dir = tools_dir / "template"
    mock_payload = {
        "version": "1.0.0",
        "meta": {"generatedAt": "2026-09-06T00:00:00Z", "sourcePaths": [], "warnings": []},
        "kpis": {"totalSessions": 1, "readWriteRatio": 1.0, "compactRate": 0.0, "errorRatePct": 0.0, "promptsPerSession": 1.0},
        "sessions": [],
        "agentInvocations": [
            {"agent": "agent-router", "total": 10, "direct": 8, "subagent": 2, "percentage": 100.0}
        ],
        "insightsActions": [],
    }

    html = TemplateBundler.bundle_standalone_html(template_dir, mock_payload)
    assert 'id="agentInvocationsBars"' in html
    assert "agent-blocks-container" in html
    assert "statTopAgent" in html
    assert "statTotalAgentInvocations" in html
    assert "statSubagentInvocations" in html
    assert "renderAgentInvocations" in html
    assert '"agent": "agent-router"' in html


def test_declarative_hook_jsonl_recording(tmp_path):
    """Valida gravação e leitura da telemetria declarativa de subagentes em JSONL."""
    log_file = tmp_path / "subagent-telemetry.jsonl"
    entry = {
        "timestamp": "2026-09-06T10:00:00.000Z",
        "agent": "runtime-verifier",
        "description": "Verificação",
        "task": "Checar ambiente",
        "sessionId": "test-session"
    }
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        loaded = json.loads(f.readline().strip())
    assert loaded["agent"] == "runtime-verifier"
    assert loaded["sessionId"] == "test-session"


def test_jira_mcp_capability_matrix_and_catalog_parity():
    """Valida R-024/R-054: paridade Jira-MCP entre .agent.md e catalog.yaml, Least-Tools e Matriz no agent-router."""
    import yaml
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    if not (root / ".github/agents/catalog.yaml").exists():
        root = Path.cwd()
    catalog = yaml.safe_load((root / ".github/agents/catalog.yaml").read_text(encoding="utf-8"))
    cat_agents = catalog.get("agents", {})

    expected_jira_agents = {
        "requirements-analyst": {"mcp-atlassian/jira_get_issue", "mcp-atlassian/jira_search"},
        "bug-triage": {"mcp-atlassian/jira_get_issue", "mcp-atlassian/jira_search"},
        "business-rules-extractor": {"mcp-atlassian/jira_get_issue", "mcp-atlassian/jira_search"},
        "tech-solution-architect": {"mcp-atlassian/jira_get_issue", "mcp-atlassian/jira_search"},
        "refactor-planner": {"mcp-atlassian/jira_get_issue", "mcp-atlassian/jira_search"},
        "feature-planner": {
            "mcp-atlassian/jira_get_issue",
            "mcp-atlassian/jira_search",
            "mcp-atlassian/jira_create_issue",
            "mcp-atlassian/jira_update_issue",
            "mcp-atlassian/jira_add_comment",
            "mcp-atlassian/jira_transition_issue",
        },
        "pr-gatekeeper": {
            "mcp-atlassian/jira_get_issue",
            "mcp-atlassian/jira_search",
            "mcp-atlassian/jira_add_comment",
            "mcp-atlassian/jira_transition_issue",
        },
    }

    for md_path in root.glob(".github/agents/**/*.agent.md"):
        parts = md_path.read_text(encoding="utf-8").split("---", 2)
        fm = yaml.safe_load(parts[1])
        aid = fm["name"]
        md_jira_tools = {t for t in fm.get("tools", []) if t.startswith("mcp-atlassian/jira_")}
        if aid in cat_agents and "tools" in cat_agents[aid]:
            cat_jira_tools = {t for t in cat_agents[aid].get("tools", []) if t.startswith("mcp-atlassian/jira_")}
            assert md_jira_tools == cat_jira_tools, f"Desalinhamento Jira tools em {aid}: md={md_jira_tools} vs catalog={cat_jira_tools}"

        if aid == "docs-engineer":
            assert not md_jira_tools, "docs-engineer NAO deve possuir tools mcp-atlassian/jira_*"
        if aid in expected_jira_agents:
            assert md_jira_tools == expected_jira_agents[aid], f"Tools Jira inesperadas para {aid}: {md_jira_tools}"
        else:
            assert not md_jira_tools, f"Agent fora da matriz ({aid}) nao pode ter tools Jira: {md_jira_tools}"

        if "mcp-atlassian/jira_create_issue" in md_jira_tools or "mcp-atlassian/jira_update_issue" in md_jira_tools:
            assert aid == "feature-planner", f"Apenas feature-planner pode criar/atualizar issues Jira, encontrado em {aid}"
        if "mcp-atlassian/jira_add_comment" in md_jira_tools or "mcp-atlassian/jira_transition_issue" in md_jira_tools:
            assert aid in {"feature-planner", "pr-gatekeeper"}, f"Apenas feature-planner e pr-gatekeeper podem comentar/transicionar issues Jira, encontrado em {aid}"

    router_text = (root / ".github/agents/agent-router.agent.md").read_text(encoding="utf-8")
    assert "Matriz Estática de Capabilities Jira-MCP" in router_text
    for aid in expected_jira_agents:
        assert f"@{aid}" in router_text, f"agent-router deve documentar @{aid} na Matriz Jira-MCP"

