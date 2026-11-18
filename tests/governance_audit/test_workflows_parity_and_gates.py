"""
test_workflows_parity_and_gates.py — Testes determinísticos de paridade de workflows e gates (R-055 Q3 / CA-07 / CA-08).

Garante que:
1. Todos os 6 sub-arquivos de workflow com plano R-064 incluem o gate cético pré-HITL (@plan-critic / § 10.7).
2. WORKFLOW-GOVERNANCE-MAINTENANCE enumera Estados 1. a 5. sem duplicidade do Estado 3, mantém paridade
   com workflows.md (Regra 7 da § 1.5 -> Estado 5) e invariantes-e-protocolos.md (§ 6.2 -> 5 etapas),
   e referencia o range atualizado Smells 2.1 a 2.35.
3. WORKFLOW-FRAMEWORK-MIGRATION mantém paridade de etapas/estados entre workflows.md,
   workflow-framework-migration.md, invariantes-e-protocolos.md e routing-graph.yaml.
4. R-065 (Guard de Severidade Arquitetural) está referenciado em workflows.md (§ 1.5) e nos sub-arquivos
   com quality_review_loop (workflow-refactoring.md, workflow-feature-development.md,
   workflow-framework-migration.md), e workflow-framework-migration.md desambigua REQ-01 (EARS)
   da proibição de prefixos legados PLAN-/REQ- em caminhos de docs/plans/.
5. routing-graph.yaml declara "9 workflows canônicos (+ 3.A auxiliar)" e lista exatamente 9 workflows em workflows:.
6. Os artefatos de blindagem na origem (CA-08 / R-055 Q2 e Smell 2.35) existem e respeitam os limites e ponteiros canônicos.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
WORKFLOWS_DIR = AGENTS_DIR / "workflows"
WORKFLOWS_MD = AGENTS_DIR / "workflows.md"
INVARIANTES_MD = WORKFLOWS_DIR / "invariantes-e-protocolos.md"
ROUTING_GRAPH_YAML = AGENTS_DIR / "routing-graph.yaml"

R064_SUBWORKFLOW_FILES = (
    "workflow-bug-fix.md",
    "workflow-refactoring.md",
    "workflow-feature-development.md",
    "workflow-governance-maintenance.md",
    "workflow-dependency-vulnerability-remediation.md",
    "workflow-framework-migration.md",
)

QUALITY_REVIEW_LOOP_SUBWORKFLOWS = (
    "workflow-refactoring.md",
    "workflow-feature-development.md",
    "workflow-framework-migration.md",
)


@pytest.mark.parametrize("filename", R064_SUBWORKFLOW_FILES)
def test_subworkflows_with_r064_include_plan_critic_gate(filename: str) -> None:
    """Verifica que os 6 sub-arquivos com plano R-064 mencionam @plan-critic e § 10.7 antes do Gate HITL."""
    filepath = WORKFLOWS_DIR / filename
    assert filepath.exists(), remediation(
        f"Sub-arquivo de workflow ausente: {filepath.relative_to(REPO_ROOT)}",
        fix_hint="Restaurar o sub-arquivo canônico em .github/agents/workflows/.",
    )
    content = filepath.read_text(encoding="utf-8")
    assert "@plan-critic" in content, remediation(
        f"{filename} não referencia @plan-critic no fluxo pré-HITL (R-064).",
        fix_hint=f"Incluir o gate de revisão cética pré-HITL pelo @plan-critic em {filename}.",
    )
    assert "10.7" in content, remediation(
        f"{filename} não referencia a seção 10.7 de invariantes-e-protocolos.md para o gate do @plan-critic.",
        fix_hint=f"Referenciar explicitamente '§ 10.7' junto ao gate do @plan-critic em {filename}.",
    )
    pos_critic = content.find("@plan-critic")
    pos_last_hitl = content.rfind("ask_questions")
    assert pos_last_hitl != -1 and pos_critic < pos_last_hitl, remediation(
        f"Em {filename}, @plan-critic deve preceder o Gate de Aprovação Humana R-064 (ask_questions).",
        fix_hint=f"Posicionar a etapa do @plan-critic antes da chamada a ask_questions do Gate R-064 em {filename}.",
    )


def test_workflow_governance_maintenance_state_numbering_no_duplicates() -> None:
    """Verifica Estados 1 a 5 sem duplicar Estado 3 em workflow-governance-maintenance.md, paridade e Smells 2.1 a 2.35."""
    wf_gov_path = WORKFLOWS_DIR / "workflow-governance-maintenance.md"
    wf_gov = wf_gov_path.read_text(encoding="utf-8")

    state_matches = re.findall(r"^\d+\.\s+\*\*Estado\s+(\d+)\b", wf_gov, flags=re.MULTILINE)
    assert state_matches == ["1", "2", "3", "4", "5"], remediation(
        f"Numeração de estados principais inválida ou duplicada em workflow-governance-maintenance.md: {state_matches}",
        fix_hint="Numerar sequencialmente os estados principais de 1 a 5 (com 5b apenas como sub-ramificação) sem duplicar Estado 3.",
    )
    estado_3_headers = re.findall(r"\*\*Estado\s+3\s*[—–-]", wf_gov)
    assert len(estado_3_headers) == 1, remediation(
        f"Estado 3 aparece {len(estado_3_headers)} vezes em workflow-governance-maintenance.md.",
        fix_hint="Remover duplicidade de 'Estado 3' mantendo numeração monotônica de 1 a 5.",
    )
    assert "Smells 2.1 a 2.35" in wf_gov, remediation(
        "workflow-governance-maintenance.md não referencia o range atualizado 'Smells 2.1 a 2.35'.",
        fix_hint="Atualizar o range do catálogo de smells em workflow-governance-maintenance.md para 'Smells 2.1 a 2.35'.",
    )

    workflows_md = WORKFLOWS_MD.read_text(encoding="utf-8")
    assert re.search(r"`?WORKFLOW-GOVERNANCE-MAINTENANCE`?\s*\(Estado\s+5\)", workflows_md), remediation(
        "workflows.md (Regra 7 da § 1.5) não referencia 'WORKFLOW-GOVERNANCE-MAINTENANCE (Estado 5)'.",
        fix_hint="Atualizar a Regra 7 da § 1.5 em .github/agents/workflows.md para '`WORKFLOW-GOVERNANCE-MAINTENANCE` (Estado 5)'.",
    )

    invariantes_md = INVARIANTES_MD.read_text(encoding="utf-8")
    assert re.search(
        r"WORKFLOW-GOVERNANCE-MAINTENANCE`?\s*\(5\s+etapas\)",
        invariantes_md,
        flags=re.IGNORECASE,
    ), remediation(
        "invariantes-e-protocolos.md (§ 6.2) não declara 5 etapas para o Workflow 5 (WORKFLOW-GOVERNANCE-MAINTENANCE).",
        fix_hint="Alinhar a § 6.2 de .github/agents/workflows/invariantes-e-protocolos.md para refletir as 5 etapas do Workflow 5.",
    )


def test_workflow_framework_migration_stage_parity() -> None:
    """Verifica paridade de WORKFLOW-FRAMEWORK-MIGRATION entre workflows.md, workflow-framework-migration.md, invariantes e routing-graph."""
    workflows_md = WORKFLOWS_MD.read_text(encoding="utf-8")
    wf_mig = (WORKFLOWS_DIR / "workflow-framework-migration.md").read_text(encoding="utf-8")
    invariantes_md = INVARIANTES_MD.read_text(encoding="utf-8")
    routing_graph = yaml.safe_load(ROUTING_GRAPH_YAML.read_text(encoding="utf-8"))

    assert re.search(r"`?WORKFLOW-FRAMEWORK-MIGRATION`?\s*\(Estado\s+6", workflows_md), remediation(
        "workflows.md (§ 1.5 Regra 7) não referencia WORKFLOW-FRAMEWORK-MIGRATION no Estado 6.",
        fix_hint="Alinhar a referência do estado de WORKFLOW-FRAMEWORK-MIGRATION na Regra 7 da § 1.5 de workflows.md.",
    )
    assert "6 estados / 7 etapas com Gate R-064" in workflows_md or "Etapa 7" in workflows_md, remediation(
        "workflows.md não explicita a paridade (6 estados / 7 etapas com Gate R-064) para WORKFLOW-FRAMEWORK-MIGRATION.",
        fix_hint="Sincronizar a descrição de estados/etapas de WORKFLOW-FRAMEWORK-MIGRATION em .github/agents/workflows.md.",
    )

    mig_states = re.findall(r"Estado\s+([1-6])\b", wf_mig)
    for expected_state in ("1", "2", "3", "4", "5", "6"):
        assert expected_state in mig_states, remediation(
            f"Estado {expected_state} ausente em workflow-framework-migration.md.",
            fix_hint="Garantir que workflow-framework-migration.md enumere os Estados 1 a 6 em paridade com workflows.md.",
        )

    assert "WORKFLOW-FRAMEWORK-MIGRATION" in invariantes_md and (
        "6 estados" in invariantes_md or "7 etapas" in invariantes_md or "6 etapas" in invariantes_md
    ), remediation(
        "invariantes-e-protocolos.md não documenta as etapas de WORKFLOW-FRAMEWORK-MIGRATION.",
        fix_hint="Atualizar invariantes-e-protocolos.md (§ 6.2) com as etapas de WORKFLOW-FRAMEWORK-MIGRATION.",
    )

    workflows_list = routing_graph.get("workflows", [])
    mig_entry = next((w for w in workflows_list if w.get("id") == "WORKFLOW-FRAMEWORK-MIGRATION"), None)
    assert mig_entry is not None, remediation(
        "WORKFLOW-FRAMEWORK-MIGRATION ausente em routing-graph.yaml.",
        fix_hint="Declarar WORKFLOW-FRAMEWORK-MIGRATION na seção workflows: de .github/agents/routing-graph.yaml.",
    )
    estados = mig_entry.get("estados") or mig_entry.get("etapas") or mig_entry.get("stages") or []
    assert len(estados) in (6, 7), remediation(
        f"WORKFLOW-FRAMEWORK-MIGRATION possui {len(estados)} estados/etapas em routing-graph.yaml (esperado: 6 ou 7 com Gate 2 R-064).",
        fix_hint="Alinhar a lista estados: de WORKFLOW-FRAMEWORK-MIGRATION em .github/agents/routing-graph.yaml.",
    )


def test_r065_guard_referenced_in_quality_review_loop_subworkflows() -> None:
    """Verifica R-065 nos sub-arquivos com quality_review_loop e em workflows.md § 1.5, além da desambiguação REQ-01 vs PLAN-/REQ-."""
    workflows_md = WORKFLOWS_MD.read_text(encoding="utf-8")
    sec_1_5_match = re.search(r"###\s+1\.5\b.*?(?=\n##\s+|\n###\s+1\.6|\Z)", workflows_md, flags=re.DOTALL)
    assert sec_1_5_match is not None and "R-065" in sec_1_5_match.group(0), remediation(
        "A seção 1.5 de workflows.md não referencia R-065.",
        fix_hint="Documentar explicitamente o Guard de Severidade Arquitetural (R-065) na § 1.5 de .github/agents/workflows.md.",
    )

    for filename in QUALITY_REVIEW_LOOP_SUBWORKFLOWS:
        content = (WORKFLOWS_DIR / filename).read_text(encoding="utf-8")
        assert "R-065" in content, remediation(
            f"{filename} não referencia R-065 no estado de quality_review_loop.",
            fix_hint=f"Referenciar explicitamente o Guard de Severidade Arquitetural (R-065) em {filename}.",
        )

    wf_mig = (WORKFLOWS_DIR / "workflow-framework-migration.md").read_text(encoding="utf-8")
    assert "REQ-01" in wf_mig, remediation(
        "workflow-framework-migration.md deve preservar o identificador EARS REQ-01.",
        fix_hint="Manter o exemplo de identificador de requisito EARS (REQ-01) em workflow-framework-migration.md.",
    )
    assert re.search(r"PLAN-|REQ-", wf_mig) and re.search(r"docs/plans/", wf_mig), remediation(
        "workflow-framework-migration.md não desambigua REQ-01 (ID EARS) da proibição de prefixos PLAN-/REQ- em docs/plans/.",
        fix_hint="Adicionar nota desambiguadora sobre proibição de prefixos PLAN-/REQ- em arquivos de docs/plans/ em workflow-framework-migration.md.",
    )
    bad_plan_paths = re.findall(r"docs/plans/[a-z_-]+/(?:PLAN|REQ)-[^\s)\"]+", wf_mig)
    assert not bad_plan_paths, remediation(
        f"Caminho(s) inválido(s) com prefixo legado PLAN-/REQ- encontrado(s) em workflow-framework-migration.md: {bad_plan_paths}",
        fix_hint="Usar exclusivamente o padrão <AAAAMMDD-HHMMSS>-<slug>.md em caminhos de docs/plans/.",
    )


def test_r065_architectural_severity_guard_disambiguation_and_references() -> None:
    """Alias canônico (§ 2.8 item 4) para validação de desambiguação e referências do Guard R-065."""
    test_r065_guard_referenced_in_quality_review_loop_subworkflows()


def test_routing_graph_workflows_header_comment_is_current() -> None:
    """Verifica que routing-graph.yaml declara '9 workflows canônicos (+ 3.A auxiliar)' e possui 9 itens em workflows:."""
    raw_yaml = ROUTING_GRAPH_YAML.read_text(encoding="utf-8")
    assert "9 workflows canônicos (+ 3.A auxiliar)" in raw_yaml, remediation(
        "Comentário de cabeçalho da seção WORKFLOWS em routing-graph.yaml está desatualizado.",
        fix_hint="Atualizar o cabeçalho da seção WORKFLOWS em .github/agents/routing-graph.yaml para '9 workflows canônicos (+ 3.A auxiliar)'.",
    )
    parsed = yaml.safe_load(raw_yaml)
    workflows = parsed.get("workflows", [])
    assert len(workflows) == 9, remediation(
        f"routing-graph.yaml declara {len(workflows)} workflows na lista 'workflows:' (esperado: 9).",
        fix_hint="Manter exatamente os 9 workflows canônicos na chave 'workflows:' de .github/agents/routing-graph.yaml.",
    )


def test_origin_workflow_invariants_and_smell_2_35_exist() -> None:
    """Verifica CA-08: workflow-invariants.md (< 150 linhas, W-01..W-08), ponteiros na Factory/Maintainer e Smell 2.35."""
    invariants_ref = (
        REPO_ROOT / ".github" / "skills" / "governance-factory-patterns" / "references" / "workflow-invariants.md"
    )
    assert invariants_ref.exists(), remediation(
        "Arquivo lazy .github/skills/governance-factory-patterns/references/workflow-invariants.md não encontrado.",
        fix_hint="Criar workflow-invariants.md com as 8 invariantes de origem de workflow (< 150 linhas).",
    )
    inv_text = invariants_ref.read_text(encoding="utf-8")
    inv_lines = inv_text.splitlines()
    assert 0 < len(inv_lines) < 150, remediation(
        f"workflow-invariants.md possui {len(inv_lines)} linhas (limite máximo estrito: < 150 linhas).",
        fix_hint="Enxugar .github/skills/governance-factory-patterns/references/workflow-invariants.md para menos de 150 linhas.",
    )
    for idx in range(1, 9):
        code = f"W-0{idx}"
        alt = f"Invariante {idx}"
        assert code in inv_text or alt in inv_text, remediation(
            f"Regra {code} ({alt}) ausente em workflow-invariants.md.",
            fix_hint=f"Documentar {code} / {alt} em .github/skills/governance-factory-patterns/references/workflow-invariants.md.",
        )

    factory_skill = (REPO_ROOT / ".github" / "skills" / "governance-factory-patterns" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "workflow-invariants.md" in factory_skill, remediation(
        "Ponteiro para workflow-invariants.md ausente em .github/skills/governance-factory-patterns/SKILL.md.",
        fix_hint="Adicionar ponteiro enxuto para references/workflow-invariants.md em governance-factory-patterns/SKILL.md.",
    )

    factory_agent = (AGENTS_DIR / "governance-factory.agent.md").read_text(encoding="utf-8")
    assert "workflow-invariants.md" in factory_agent, remediation(
        "Ponteiro para workflow-invariants.md ausente em .github/agents/governance-factory.agent.md.",
        fix_hint="Adicionar ponteiro enxuto para workflow-invariants.md nas diretrizes de sincronização de governance-factory.agent.md.",
    )

    maintainer_agent = (AGENTS_DIR / "governance-maintainer.agent.md").read_text(encoding="utf-8")
    assert "workflow-invariants.md" in maintainer_agent, remediation(
        "Ponteiro para workflow-invariants.md ausente no Checklist de Sincronização de governance-maintainer.agent.md.",
        fix_hint="Adicionar validação contra workflow-invariants.md no Checklist de Sincronização de governance-maintainer.agent.md.",
    )

    audit_skill = (REPO_ROOT / ".github" / "skills" / "governance-audit-patterns" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "2.35" in audit_skill, remediation(
        "Smell 2.35 ausente em .github/skills/governance-audit-patterns/SKILL.md.",
        fix_hint="Documentar o Smell 2.35 (Drift de Paridade e Invariantes de Workflow) em governance-audit-patterns/SKILL.md.",
    )


CANONICAL_WORKFLOW_FILES = (
    "workflow-bug-fix.md",
    "workflow-dependency-vulnerability-remediation.md",
    "workflow-feature-development.md",
    "workflow-framework-migration.md",
    "workflow-governance-maintenance.md",
    "workflow-prompt-synthesis.md",
    "workflow-refactoring.md",
    "workflow-release-readiness.md",
    "workflow-technical-analysis.md",
    "workflow-ui-layout.md",
)

EXEMPT_FROM_R064_WORKFLOW = "workflow-prompt-synthesis.md"

WORKFLOWS_WITH_AUTOFIX_CB = (
    "workflow-governance-maintenance.md",
    "workflow-bug-fix.md",
    "workflow-dependency-vulnerability-remediation.md",
    "workflow-feature-development.md",
    "workflow-framework-migration.md",
    "workflow-refactoring.md",
)


def _extract_mermaid_blocks(text: str) -> str:
    """Isola apenas o conteúdo dentro dos blocos ```mermaid ... ``` de um arquivo Markdown."""
    blocks = re.findall(r"```mermaid\s*\n(.*?)```", text, flags=re.DOTALL)
    return "\n".join(blocks)


def test_workflows_mermaid_blocks_reflect_all_r064_r065_and_post_exec_states() -> None:
    """Garante paridade entre a prosa e os blocos Mermaid nos 10 workflows (R-064, R-065, 5a/5a-CB/5b)."""
    for wf_name in CANONICAL_WORKFLOW_FILES:
        wf_path = WORKFLOWS_DIR / wf_name
        text = wf_path.read_text(encoding="utf-8")
        mermaid = _extract_mermaid_blocks(text)
        assert mermaid.strip(), remediation(
            f"{wf_name} deve conter ao menos um bloco ```mermaid.",
            fix_hint=f"Adicionar diagrama Mermaid canônico em {wf_name}.",
        )

        if wf_name == EXEMPT_FROM_R064_WORKFLOW:
            for tier in ("Tier 1", "Tier 2", "Tier 3"):
                assert tier in mermaid, remediation(
                    f"{wf_name} (Mermaid) deve refletir o gate {tier} da taxonomia R-041.",
                    fix_hint=f"Incluir {tier} no bloco Mermaid de {wf_name}.",
                )
            assert "agent-router" in mermaid, remediation(
                f"{wf_name} (Mermaid) deve conter retorno explícito ao @agent-router.",
                fix_hint=f"Incluir @agent-router no bloco Mermaid de {wf_name}.",
            )
            continue

        for token in ("docs-engineer", "plan-critic", "NEEDS_REVISION", "ESCALATED_HITL", "agent-router"):
            assert token in mermaid, remediation(
                f"{wf_name} (Mermaid) deve conter '{token}' para paridade com a prosa.",
                fix_hint=f"Sincronizar o bloco Mermaid de {wf_name} incluindo '{token}'.",
            )

        for pattern, label in (
            (r"(?<!ESCALATED_)\bHITL\b", "HITL"),
            (r"\bREJECTED\b", "REJECTED"),
            (r"\b5a\b", "5a"),
            (r"\b5b\b", "5b"),
        ):
            assert re.search(pattern, mermaid), remediation(
                f"{wf_name} (Mermaid) deve conter o estado/etapa '{label}' (pattern: {pattern}).",
                fix_hint=f"Sincronizar o bloco Mermaid de {wf_name} com o estado/etapa '{label}'.",
            )

        if wf_name in WORKFLOWS_WITH_AUTOFIX_CB:
            assert re.search(r"\b5a-CB\b", mermaid), remediation(
                f"{wf_name} (Mermaid) deve conter '5a-CB' para o Circuit Breaker de Autofix sem colisão com 5b.",
                fix_hint=f"Adicionar nó 5a-CB no bloco Mermaid de {wf_name}.",
            )


def test_workflow_governance_maintenance_mermaid_fail_closed_and_roles() -> None:
    """Valida que o bloco Mermaid de workflow-governance-maintenance respeita Fail-Closed e papéis reais."""
    wf_path = WORKFLOWS_DIR / "workflow-governance-maintenance.md"
    mermaid = _extract_mermaid_blocks(wf_path.read_text(encoding="utf-8"))
    assert mermaid.strip(), remediation(
        "workflow-governance-maintenance.md deve possuir bloco Mermaid.",
        fix_hint="Adicionar bloco Mermaid em workflow-governance-maintenance.md.",
    )

    assert not re.search(r"docs-engineer[^\n]*Read-Only", mermaid, flags=re.IGNORECASE), remediation(
        "workflow-governance-maintenance.md (Mermaid) não deve rotular @docs-engineer como Read-Only.",
        fix_hint="Remover rótulo (Read-Only) de @docs-engineer no bloco Mermaid de workflow-governance-maintenance.md.",
    )

    assert "python-router" in mermaid, remediation(
        "workflow-governance-maintenance.md (Mermaid) deve exibir a bifurcação para @python-router.",
        fix_hint="Incluir bifurcação @python-router no bloco Mermaid de workflow-governance-maintenance.md.",
    )

    hitl_match = re.search(r"(?<!ESCALATED_)\bHITL\b", mermaid)
    exec_match = re.search(r"Etapa\s*4|Sincroniza|Cria/Atualiza|Execu", mermaid, flags=re.IGNORECASE)
    assert hitl_match is not None and exec_match is not None, remediation(
        "workflow-governance-maintenance.md (Mermaid) deve conter o gate HITL e a etapa de execução.",
        fix_hint="Garantir presença do Gate HITL e da etapa de execução/sincronização no Mermaid.",
    )
    assert hitl_match.start() < exec_match.start(), remediation(
        "Fail-Closed violado no Mermaid: o gate HITL deve preceder a execução/mutação.",
        fix_hint="Posicionar o Gate HITL antes de qualquer nó de execução/sincronização no Mermaid.",
    )


def test_invariantes_e_protocolos_mermaid_and_atomic_parity_rule() -> None:
    """Valida o diagrama Mermaid de invariantes-e-protocolos.md e a regra de blindagem Prosa <-> Mermaid na origem."""
    inv_path = WORKFLOWS_DIR / "invariantes-e-protocolos.md"
    inv_text = inv_path.read_text(encoding="utf-8")
    inv_mermaid = _extract_mermaid_blocks(inv_text)
    assert inv_mermaid.strip(), remediation(
        "invariantes-e-protocolos.md deve conter bloco Mermaid.",
        fix_hint="Adicionar bloco Mermaid em invariantes-e-protocolos.md.",
    )

    for token in ("docs-engineer", "plan-critic", "ESCALATED_HITL"):
        assert token in inv_mermaid, remediation(
            f"invariantes-e-protocolos.md (Mermaid) deve conter '{token}'.",
            fix_hint=f"Incluir '{token}' no bloco Mermaid de invariantes-e-protocolos.md.",
        )

    for pattern, label in (
        (r"(?<!ESCALATED_)\bHITL\b", "HITL"),
        (r"\bREJECTED\b", "REJECTED"),
        (r"\b5a\b", "5a"),
        (r"\b5a-CB\b", "5a-CB"),
        (r"\b5b\b", "5b"),
    ):
        assert re.search(pattern, inv_mermaid), remediation(
            f"invariantes-e-protocolos.md (Mermaid) deve conter '{label}' (pattern: {pattern}).",
            fix_hint=f"Incluir '{label}' no bloco Mermaid de invariantes-e-protocolos.md.",
        )

    assert "Paridade Atômica Prosa ↔ Mermaid" in inv_text, remediation(
        "invariantes-e-protocolos.md deve documentar a regra 'Paridade Atômica Prosa ↔ Mermaid'.",
        fix_hint="Documentar 'Paridade Atômica Prosa ↔ Mermaid' em invariantes-e-protocolos.md.",
    )

    gov_agent_path = AGENTS_DIR / "governance-maintainer.agent.md"
    gov_agent_text = gov_agent_path.read_text(encoding="utf-8")
    assert "Paridade Atômica Prosa ↔ Mermaid" in gov_agent_text, remediation(
        "governance-maintainer.agent.md deve exigir 'Paridade Atômica Prosa ↔ Mermaid'.",
        fix_hint="Incluir 'Paridade Atômica Prosa ↔ Mermaid' em governance-maintainer.agent.md.",
    )

    rubric_path = (
        REPO_ROOT
        / ".github"
        / "skills"
        / "plan-conformance-patterns"
        / "references"
        / "pre-hitl-skeptical-review-rubric.md"
    )
    rubric_text = rubric_path.read_text(encoding="utf-8")
    assert "Paridade Atômica Prosa ↔ Mermaid" in rubric_text, remediation(
        "pre-hitl-skeptical-review-rubric.md deve auditar 'Paridade Atômica Prosa ↔ Mermaid'.",
        fix_hint="Incluir 'Paridade Atômica Prosa ↔ Mermaid' em pre-hitl-skeptical-review-rubric.md.",
    )

    checklist_path = (
        REPO_ROOT
        / ".github"
        / "skills"
        / "plan-conformance-patterns"
        / "references"
        / "planner-preflight-checklist.md"
    )
    checklist_text = checklist_path.read_text(encoding="utf-8").replace("`", "")
    assert "paridade Prosa↔Mermaid em workflow-*.md" in checklist_text, remediation(
        "planner-preflight-checklist.md deve verificar 'paridade Prosa↔Mermaid em workflow-*.md'.",
        fix_hint="Incluir 'paridade Prosa↔Mermaid em workflow-*.md' em planner-preflight-checklist.md.",
    )


def test_routing_graph_every_workflow_state_declares_gate() -> None:
    """R-068: toda etapa (workflows[*].estados[*]) do routing-graph.yaml declara a chave 'gate' (presença, não valor)."""
    data = yaml.safe_load(ROUTING_GRAPH_YAML.read_text(encoding="utf-8"))
    workflows = data.get("workflows") or []
    assert workflows, remediation(
        "routing-graph.yaml deve declarar workflows.",
        fix_hint="Restaurar a seção 'workflows:' em routing-graph.yaml.",
    )
    checked = 0
    missing: list[str] = []
    for workflow in workflows:
        for estado in workflow.get("estados") or []:
            if not isinstance(estado, dict) or "nome" not in estado:
                continue
            checked += 1
            if "gate" not in estado:
                missing.append(f"{workflow.get('id')}:{estado['nome']}")
    assert checked > 0, remediation(
        "Nenhum estado com 'nome' encontrado em workflows[*].estados[*] do routing-graph.yaml.",
        fix_hint="Verificar a estrutura workflows[*].estados[*] em routing-graph.yaml.",
    )
    assert not missing, remediation(
        f"Estados sem chave 'gate' em routing-graph.yaml: {', '.join(missing)}.",
        fix_hint="Declarar 'gate:' (ex.: 'none') em cada estado listado.",
    )
