"""
Auditoria de Governança: Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance).

Verifica a conformidade contratual entre agents declarantes de 'run_subagent' e a
obrigatoriedade de emissão de 'telemetry_entry' (tag [HANDOFF], session_id, sequence_index).

Quality Gate Bloqueante (R-042 / R-046):
Garante que 100% dos agents com capacidade de delegação ('run_subagent') referenciem
formalmente a governança de handoff ('handoff-governance' e 'agent-contracts' em source_docs:),
impedindo merges que introduzam deriva silenciosa na telemetria de sessões de agents.
"""

from __future__ import annotations
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.agent_source_docs_sync.sync_required_source_docs import sync_agent_source_docs

HANDOFF_SKILL = REPO_ROOT / ".github" / "skills" / "handoff-governance" / "SKILL.md"
CONTRACTS_SKILL = REPO_ROOT / ".github" / "skills" / "agent-contracts" / "SKILL.md"
MEMORY_SKILL = REPO_ROOT / ".github" / "skills" / "agent-memory-policy" / "SKILL.md"
EVALS_SKILL = REPO_ROOT / ".github" / "skills" / "agent-evals-lab" / "SKILL.md"


def test_telemetry_schema_and_contracts_declared_in_governance_skills():
    """
    Garante que as skills estruturantes definem formalmente a obrigação de telemetria,
    os novos campos de sessão (session_id, sequence_index, call_stack_depth, outcome_summary)
    e a política de retenção condicional por tag.
    """
    handoff_text = HANDOFF_SKILL.read_text(encoding="utf-8")
    assert "telemetry_entry:" in handoff_text
    assert "session_id:" in handoff_text
    assert "sequence_index:" in handoff_text
    assert "call_stack_depth:" in handoff_text
    assert "outcome_summary:" in handoff_text
    assert "sessionStart" in handoff_text

    contracts_text = CONTRACTS_SKILL.read_text(encoding="utf-8")
    assert "Emissão Obrigatória de Telemetria de Handoff (R-042" in contracts_text
    assert "telemetry_entry" in contracts_text
    assert "session_id" in contracts_text

    memory_text = MEMORY_SKILL.read_text(encoding="utf-8")
    assert "handoff-telemetry:*" in memory_text
    assert "[SUCCESS]" in memory_text
    assert "[INTENT_DRIFT]" in memory_text
    assert "[LOOP_LIMIT]" in memory_text

    evals_text = EVALS_SKILL.read_text(encoding="utf-8")
    assert "session_id" in evals_text
    assert "outcome_summary" in evals_text
    assert "call_stack_depth" in evals_text


def test_agents_with_run_subagent_reference_handoff_governance():
    """
    Quality gate bloqueante determinístico:
    Invoca o motor de sincronização canônica de source_docs em modo check,
    validando que 100% dos agentes com 'run_subagent' referenciam formalmente
    'handoff-governance' e 'agent-contracts' em seu frontmatter YAML (drift = 0).
    """
    report, exit_code = sync_agent_source_docs(mode="check")

    assert not report.errors, (
        f"[GOVERNANCE QUALITY GATE / R-042] Erros de validação ao auditar source_docs:\n"
        + "\n".join(f"  - {e}" for e in report.errors)
    )

    assert exit_code == 0 and not report.has_drift, (
        f"[GOVERNANCE QUALITY GATE / R-042] {len(report.drifted)} agente(s) com 'run_subagent' "
        f"apresentam drift nas referências obrigatórias de source_docs:\n"
        + "\n".join(f"  - {d}" for d in report.drifted)
        + "\nRemediação determinística: execute 'python tools/agent_source_docs_sync/sync_required_source_docs.py --apply'."
    )

    assert report.total_scanned == 95, (
        f"Esperado 95 agentes auditados no catálogo, obtido {report.total_scanned}."
    )


def test_execution_protocol_and_router_declarations_for_telemetry_emission():
    """
    Quality Gate R-042 / R-054 / R-059:
    Garante que a emissão obrigatória de telemetria de handoff está embutida diretamente:
    1. No fragmento canônico do execution_protocol (STANDARD - item 7).
    2. No template canônico de novos agents executores (agent-template.md).
    3. No agent CUSTOM pinado com run_subagent (codegraph-engine.agent.md).
    4. Nos routers (router-agent.md template e agent-router.agent.md), formalizando
       a decisão arquitetural de baseline R-054 (Least Privilege: router sem ctx_index;
       emissão física a cargo do agent receptor/delegado).
    """
    frag_path = REPO_ROOT / "tools" / "agent_protocol_sync" / "_execution-protocol-fragment.md"
    frag_text = frag_path.read_text(encoding="utf-8")
    assert "Emissão Obrigatória de Telemetria de Handoff (R-042" in frag_text
    assert "telemetry_entry" in frag_text
    assert "[HANDOFF]" in frag_text
    assert "session_id" in frag_text
    assert "sequence_index" in frag_text

    tpl_path = REPO_ROOT / ".github" / "agents" / "templates" / "agent-template.md"
    tpl_text = tpl_path.read_text(encoding="utf-8")
    assert "Emissão Obrigatória de Telemetria de Handoff (R-042" in tpl_text
    assert "[HANDOFF]" in tpl_text

    ckg_path = REPO_ROOT / ".github" / "agents" / "codegraph-engine.agent.md"
    ckg_text = ckg_path.read_text(encoding="utf-8")
    assert "Emissão Obrigatória de Telemetria de Handoff (R-042" in ckg_text
    assert "[HANDOFF]" in ckg_text

    router_tpl_path = REPO_ROOT / ".github" / "agents" / "templates" / "router-agent.md"
    router_tpl_text = router_tpl_path.read_text(encoding="utf-8")
    assert "Telemetria de Handoff (Decisão de Baseline R-054" in router_tpl_text
    assert "AGENT RECEPTOR / DELEGADO" in router_tpl_text

    ar_path = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
    ar_text = ar_path.read_text(encoding="utf-8")
    assert "Telemetria de Handoff (Decisão de Baseline R-054" in ar_text
    assert "AGENT RECEPTOR / DELEGADO" in ar_text
