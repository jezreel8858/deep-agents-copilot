"""
test_universal_plan_materialization_governance.py — Validação determinística da
Padronização e Materialização Universal de Planos em docs/plans/<tipo>/ (R-064 / CA-01..CA-06).

Valida:
- CA-01: Existência das 8 subpastas canônicas em docs/plans/{feature,refactor,architecture,
  implementation,test-strategy,bug-triage,requirements,governance}/, ausência dos diretórios
  legados (docs/implementation-plans, docs/plan, docs/requirements), ausência de planos .md
  soltos na raiz docs/plans/ (exceto README.md), e resolução de todos os related-planning-doc
  de planos em docs/plans/<tipo>/.
- CA-02: Existência dos templates especializados nas skills (plan-frontmatter-r064.md,
  plan-template-feature.md, plan-template-refactor.md, plan-template-requirements.md,
  plan-template-test-strategy.md, plan-template-implementation.md, plan-template-bug-triage.md,
  plan-template-governance.md) com os campos obrigatórios de frontmatter R-064 (status, approved,
  author, plan_type, created_at, allowed_files, related-planning-doc), e conformidade R-066
  (<= 300 linhas nos SKILL.md das skills de planejamento/governança de planos).
- CA-03: Os 14 agents planejadores/advisors/triagem/requisitos (feature-planner, refactor-planner,
  tech-solution-architect, test-strategy, bug-triage, requirements-analyst e os 8 *-arch-advisor)
  permanecem 100% Read-Only (sem create_file/replace_string_in_file no frontmatter tools:),
  referenciam o contrato de materialização em docs/plans/<tipo>/ + template de skill, e delegam a
  escrita física para @docs-engineer / @governance-maintainer.
- CA-04: @governance-factory, governance-factory-patterns e os templates .github/agents/templates/*.md
  contêm as regras de enforcement de materialização de planos em docs/plans/<tipo>/.
- CA-05: CLAUDE.md, .github/copilot-instructions.md, .github/agents/workflows.md e
  .github/agents/workflows/invariantes-e-protocolos.md (§ 10) refletem docs/plans/<tipo>/ e o Gate R-064.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
PLANS_ROOT = DOCS_DIR / "plans"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"

CANONICAL_PLAN_SUBFOLDERS = (
    "feature",
    "refactor",
    "architecture",
    "implementation",
    "test-strategy",
    "bug-triage",
    "requirements",
    "governance",
)

OBSOLETE_PLAN_DIRS = (
    DOCS_DIR / "implementation-plans",
    DOCS_DIR / "plan",
    DOCS_DIR / "requirements",
)

SPECIALIZED_TEMPLATES: dict[str, str] = {
    "plan-frontmatter-r064.md": ".github/skills/plan-conformance-patterns/references/plan-frontmatter-r064.md",
    "plan-template-feature.md": ".github/skills/task-decomposition-patterns/references/plan-template-feature.md",
    "plan-template-refactor.md": ".github/skills/refactoring-planning-patterns/references/plan-template-refactor.md",
    "plan-template-requirements.md": ".github/skills/requirements-engineering-patterns/references/plan-template-requirements.md",
    "plan-template-test-strategy.md": ".github/skills/test-coverage-governance/references/plan-template-test-strategy.md",
    "plan-template-implementation.md": ".github/skills/specialist-hybrid-advisory-implementation-patterns/references/plan-template-implementation.md",
    "plan-template-bug-triage.md": ".github/skills/code-tracing/references/plan-template-bug-triage.md",
    "plan-template-governance.md": ".github/skills/governance-audit-patterns/references/plan-template-governance.md",
}

REQUIRED_R064_FRONTMATTER_FIELDS = (
    "status",
    "approved",
    "author",
    "plan_type",
    "created_at",
    "allowed_files",
    "related-planning-doc",
)

FOURTEEN_PLANNER_AND_ADVISOR_AGENTS = (
    "feature-planner",
    "refactor-planner",
    "tech-solution-architect",
    "test-strategy",
    "bug-triage",
    "requirements-analyst",
    "ejb-arch-advisor",
    "python-arch-advisor",
    "spring-boot-arch-advisor",
    "spring-reactive-arch-advisor",
    "struts-arch-advisor",
    "angular-arch-advisor",
    "react-arch-advisor",
    "database-arch-advisor",
)

FORBIDDEN_WRITE_TOOLS = {
    "create_file",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "insert_edit_into_file",
    "edit",
    "write",
}


def _find_agent_file(agent_name: str) -> Path:
    matches = [
        p for p in AGENTS_DIR.glob(f"**/{agent_name}.agent.md")
        if "templates" not in p.parts
    ]
    assert len(matches) == 1, f"Agente '{agent_name}' não encontrado unicamente: {matches}"
    return matches[0]


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?\r?\n)---\r?\n?", text, re.DOTALL)
    if not m:
        return {}
    data = yaml.safe_load(m.group(1))
    return data if isinstance(data, dict) else {}


# ─────────────────────────────────────────────────────────────
# CA-01: Taxonomia docs/plans/<tipo>/, ausência de diretórios legados e resolução de related-planning-doc
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("sub", CANONICAL_PLAN_SUBFOLDERS)
def test_ca01_canonical_plan_subfolders_exist(sub: str):
    """CA-01: As 8 subpastas canônicas devem existir em docs/plans/<tipo>/."""
    target = PLANS_ROOT / sub
    assert target.is_dir(), remediation(
        f"Subpasta canônica ausente: {target.relative_to(REPO_ROOT).as_posix()}",
        fix_hint=f"Criar o diretório 'docs/plans/{sub}/' conforme taxonomia R-064.",
    )


@pytest.mark.parametrize("obsolete_dir", OBSOLETE_PLAN_DIRS)
def test_ca01_obsolete_plan_directories_do_not_exist(obsolete_dir: Path):
    """CA-01: Diretórios legados (docs/implementation-plans, docs/plan, docs/requirements) não devem existir."""
    assert not obsolete_dir.exists(), remediation(
        f"Diretório legado ainda existe: {obsolete_dir.relative_to(REPO_ROOT).as_posix()}",
        fix_hint=f"Migrar arquivos remanescentes para docs/plans/<tipo>/ e remover '{obsolete_dir.relative_to(REPO_ROOT).as_posix()}'.",
    )


def test_ca01_no_loose_markdown_plans_in_docs_plans_root():
    """CA-01: Nenhum plano .md solto deve existir na raiz de docs/plans/ (exceto README.md)."""
    loose_md = [
        p.name for p in PLANS_ROOT.glob("*.md")
        if p.name != "README.md"
    ]
    assert not loose_md, remediation(
        f"Planos .md soltos encontrados na raiz de docs/plans/: {loose_md}",
        fix_hint="Mover planos da raiz docs/plans/ para a subpasta tipada correspondente em docs/plans/<tipo>/.",
    )


def test_ca01_all_related_planning_docs_resolve():
    """CA-01: Todos os campos related-planning-doc em docs/plans/<tipo>/*.md devem resolver para arquivo existente ou N/A."""
    broken: list[str] = []
    plan_files = [
        p for p in sorted(PLANS_ROOT.rglob("*.md"))
        if p.name != "README.md"
    ]
    assert plan_files, "Devem existir planos em docs/plans/<tipo>/"

    for pf in plan_files:
        fm = _parse_frontmatter(pf)
        rel_doc = fm.get("related-planning-doc")
        if not rel_doc or not isinstance(rel_doc, str):
            continue
        val = rel_doc.strip()
        if val.upper().startswith("N/A") or "<" in val:
            continue
        target_path = REPO_ROOT / val
        if not target_path.is_file():
            broken.append(f"{pf.relative_to(REPO_ROOT).as_posix()} -> '{val}' (arquivo inexistente)")

    assert not broken, remediation(
        f"{len(broken)} plano(s) com related-planning-doc quebrado:\n" + "\n".join(f"  - {b}" for b in broken),
        fix_hint="Atualizar o campo 'related-planning-doc' para apontar para o caminho canônico em 'docs/plans/<tipo>/<arquivo>.md'.",
    )


# ─────────────────────────────────────────────────────────────
# CA-02: Templates especializados nas skills com frontmatter R-064 e conformidade R-066 (<= 300 linhas)
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("tpl_name,rel_path", list(SPECIALIZED_TEMPLATES.items()))
def test_ca02_specialized_templates_exist_and_have_r064_fields(tpl_name: str, rel_path: str):
    """CA-02: Todos os 8 templates especializados existem e declaram os 7 campos obrigatórios de frontmatter R-064."""
    tpl_path = REPO_ROOT / rel_path
    assert tpl_path.is_file(), remediation(
        f"Template especializado '{tpl_name}' não encontrado em '{rel_path}'",
        fix_hint=f"Criar o arquivo de referência '{rel_path}' com o template canônico R-064.",
    )
    content = tpl_path.read_text(encoding="utf-8")
    missing_fields = [f for f in REQUIRED_R064_FRONTMATTER_FIELDS if f not in content]
    assert not missing_fields, remediation(
        f"Template '{rel_path}' não contém os campos R-064 obrigatórios: {missing_fields}",
        fix_hint=f"Incluir {missing_fields} no bloco de frontmatter YAML de '{rel_path}'.",
    )


@pytest.mark.parametrize("tpl_name,rel_path", list(SPECIALIZED_TEMPLATES.items()))
def test_ca02_parent_skills_of_plan_templates_comply_with_r066_line_budget(tpl_name: str, rel_path: str):
    """CA-02: Todos os SKILL.md das skills detentoras de templates de plano respeitam <= 300 linhas (R-066)."""
    skill_md = (REPO_ROOT / rel_path).parent.parent / "SKILL.md"
    assert skill_md.is_file(), f"SKILL.md pai não encontrado para {rel_path}"
    line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    assert line_count <= 300, remediation(
        f"{skill_md.relative_to(REPO_ROOT).as_posix()} possui {line_count} linhas (teto R-066: <= 300 linhas)",
        fix_hint=f"Extrair seções detalhadas de {skill_md.relative_to(REPO_ROOT).as_posix()} para references/ mantendo SKILL.md <= 300 linhas.",
    )


# ─────────────────────────────────────────────────────────────
# CA-03: 14 Agents Planejadores/Advisors/Triagem/Requisitos 100% Read-Only + Contrato docs/plans/<tipo>/
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("agent_name", FOURTEEN_PLANNER_AND_ADVISOR_AGENTS)
def test_ca03_fourteen_agents_are_read_only_and_delegate_materialization(agent_name: str):
    """CA-03: Os 14 agents permanecem 100% Read-Only, referenciam docs/plans/<tipo>/ + template e delegam escrita."""
    agent_path = _find_agent_file(agent_name)
    fm = _parse_frontmatter(agent_path)
    tools = fm.get("tools") or []
    if isinstance(tools, str):
        tools = [tools]

    forbidden_found = [t for t in tools if t in FORBIDDEN_WRITE_TOOLS]
    assert not forbidden_found, remediation(
        f"Agente Read-Only '{agent_name}' declara tools de escrita proibidas no frontmatter: {forbidden_found}",
        fix_hint=f"Remover {forbidden_found} do frontmatter tools: de {agent_path.relative_to(REPO_ROOT).as_posix()} (R-025).",
    )

    content = agent_path.read_text(encoding="utf-8")
    assert "docs/plans/" in content, remediation(
        f"Agente '{agent_name}' não referencia o diretório canônico 'docs/plans/<tipo>/'",
        fix_hint=f"Atualizar {agent_path.relative_to(REPO_ROOT).as_posix()} para referenciar 'docs/plans/<tipo>/'.",
    )
    assert ("plan-template-" in content or "plan-frontmatter-r064.md" in content), remediation(
        f"Agente '{agent_name}' não referencia o template especializado de skill ('plan-template-*.md')",
        fix_hint=f"Referenciar o template canônico da skill em {agent_path.relative_to(REPO_ROOT).as_posix()}.",
    )
    assert ("docs-engineer" in content or "governance-maintainer" in content), remediation(
        f"Agente '{agent_name}' não declara delegação da escrita física para @docs-engineer / @governance-maintainer",
        fix_hint=f"Documentar a delegação de persistência física para @docs-engineer em {agent_path.relative_to(REPO_ROOT).as_posix()}.",
    )


# ─────────────────────────────────────────────────────────────
# CA-04: @governance-factory, governance-factory-patterns e templates .github/agents/templates/*.md
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "rel_path",
    [
        ".github/agents/governance-factory.agent.md",
        ".github/skills/governance-factory-patterns/SKILL.md",
        ".github/agents/templates/agent-template.md",
        ".github/agents/templates/operational-agent.md",
        ".github/agents/templates/research-agent.md",
        ".github/agents/templates/router-agent.md",
    ],
)
def test_ca04_factory_and_agent_templates_enforce_plan_materialization(rel_path: str):
    """CA-04: @governance-factory, governance-factory-patterns e templates de agent contêm enforcement de docs/plans/<tipo>/ e R-064."""
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"Arquivo obrigatório ausente: {rel_path}"
    content = path.read_text(encoding="utf-8")
    assert "docs/plans/" in content, remediation(
        f"'{rel_path}' não contém referência a 'docs/plans/<tipo>/'",
        fix_hint=f"Adicionar regra de materialização de planos em 'docs/plans/<tipo>/' em '{rel_path}'.",
    )
    assert "R-064" in content, remediation(
        f"'{rel_path}' não referencia a regra 'R-064'",
        fix_hint=f"Referenciar formalmente 'R-064' em '{rel_path}'.",
    )


# ─────────────────────────────────────────────────────────────
# CA-05: Instruções globais e workflows refletem docs/plans/<tipo>/ e Gate R-064
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "rel_path",
    [
        "CLAUDE.md",
        ".github/copilot-instructions.md",
        ".github/agents/workflows.md",
        ".github/agents/workflows/invariantes-e-protocolos.md",
    ],
)
def test_ca05_global_instructions_and_workflows_reflect_typed_plans_and_r064(rel_path: str):
    """CA-05: CLAUDE.md, copilot-instructions.md, workflows.md e invariantes-e-protocolos.md refletem docs/plans/<tipo>/ e R-064."""
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"Arquivo normativo ausente: {rel_path}"
    content = path.read_text(encoding="utf-8")
    assert "docs/plans/" in content, remediation(
        f"'{rel_path}' não referencia 'docs/plans/'",
        fix_hint=f"Atualizar '{rel_path}' para referenciar 'docs/plans/<tipo>/'.",
    )
    assert "R-064" in content, remediation(
        f"'{rel_path}' não referencia 'R-064'",
        fix_hint=f"Incluir referência ao Gate 'R-064' em '{rel_path}'.",
    )
    assert "docs/implementation-plans" not in content, remediation(
        f"'{rel_path}' ainda contém referência ao caminho legado 'docs/implementation-plans'",
        fix_hint=f"Substituir 'docs/implementation-plans' por 'docs/plans/implementation' em '{rel_path}'.",
    )


# ─────────────────────────────────────────────────────────────
# CA-06: Hard-Stop Fail-Closed R-064, Ordem de Workflow e Fechamento de Brechas (G1-G11)
# ─────────────────────────────────────────────────────────────

def test_agent_router_has_no_obsolete_implementation_plans_path():
    """Garante zero ocorrências de docs/implementation-plans/ em agent-router.agent.md e presença de docs/plans/governance/."""
    router_path = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
    content = router_path.read_text(encoding="utf-8")
    assert "docs/implementation-plans/" not in content, remediation(
        "agent-router.agent.md ainda contém caminho legado 'docs/implementation-plans/'.",
        fix_hint="Substituir 'docs/implementation-plans/' por 'docs/plans/<tipo>/' e 'docs/plans/governance/'.",
    )
    assert "docs/plans/governance/" in content, remediation(
        "agent-router.agent.md não referencia 'docs/plans/governance/' no Gate R-064.",
        fix_hint="Explicitar 'docs/plans/governance/' e vedação de 'docs_only' para '.github/**' no Gate R-064.",
    )


def test_workflows_governance_maintenance_orders_plan_before_checkpoint():
    """Garante que em workflows.md a materialização do Plano em docs/plans/governance/ precede o Checkpoint Humano R-064."""
    wf_path = REPO_ROOT / ".github" / "agents" / "workflows.md"
    content = wf_path.read_text(encoding="utf-8")
    gov_lines = [
        line for line in content.splitlines()
        if "WORKFLOW-GOVERNANCE-MAINTENANCE" in line and "|" in line
    ]
    assert gov_lines, "Linha de WORKFLOW-GOVERNANCE-MAINTENANCE não encontrada na tabela de workflows.md"
    row = gov_lines[0]
    idx_plan = row.find("docs/plans/governance/")
    idx_checkpoint = row.find("Checkpoint Humano")
    assert idx_plan != -1 and idx_checkpoint != -1 and idx_plan < idx_checkpoint, remediation(
        f"Em workflows.md, a materialização em docs/plans/governance/ deve preceder o Checkpoint Humano: {row}",
        fix_hint="Ordenar: 1. Diagnóstico -> 2. Materialização Física do Plano R-064 em docs/plans/governance/ -> 3. Checkpoint Humano R-064 -> 4. Execução em Lote.",
    )


def test_invariantes_r064_closes_docs_only_loophole_and_enforces_fail_closed():
    """Garante que invariantes-e-protocolos.md exclui .github/ de docs_only, aponta para docs/plans/governance/ e exige Fail-Closed."""
    inv_path = REPO_ROOT / ".github" / "agents" / "workflows" / "invariantes-e-protocolos.md"
    content = inv_path.read_text(encoding="utf-8")
    assert ".github/agents/**" in content and "docs_only" in content, remediation(
        "invariantes-e-protocolos.md não exclui explicitamente '.github/agents/**' da isenção 'docs_only'.",
        fix_hint="Explicitar na § 10.3(b) que 'docs_only' é estritamente proibida para '.github/agents/**', 'CLAUDE.md', 'tools/**' e 'tests/**'.",
    )
    assert "nunca é bloqueado por ausência" not in content, remediation(
        "invariantes-e-protocolos.md ainda contém cláusula fail-open ('nunca é bloqueado por ausência').",
        fix_hint="Substituir cláusula fail-open por modo Fail-Closed exigindo plan_ref físico aprovado em docs/plans/governance/.",
    )
    assert "Fail-Closed" in content and "docs/plans/governance/" in content, remediation(
        "invariantes-e-protocolos.md não exige modo Fail-Closed com persistência em docs/plans/governance/.",
        fix_hint="Incluir 'Fail-Closed' e 'docs/plans/governance/<AAAAMMDD-HHMMSS>-governance-maintenance-<slug>.md' na § 10.6.",
    )


def test_governance_maintainer_enforces_plan_ref_hard_stop():
    """Garante que governance-maintainer.agent.md contém o Hard-Stop Fail-Closed verificando plan_ref e approved: true em docs/plans/governance/."""
    gm_path = REPO_ROOT / ".github" / "agents" / "governance-maintainer.agent.md"
    content = gm_path.read_text(encoding="utf-8")
    assert "Hard-Stop Fail-Closed" in content and "plan_ref" in content and "approved: true" in content, remediation(
        "governance-maintainer.agent.md não contém Hard-Stop Fail-Closed verificando plan_ref e approved: true.",
        fix_hint="Adicionar Hard-Stop Fail-Closed de Pré-Condição (plan_ref) na seção R-064 de governance-maintainer.agent.md.",
    )


def test_craft_prompt_and_prompt_structuring_preserve_r064_plan_materialization():
    """Garante que prompt-structuring.agent.md e craft-prompt.prompt.md preservam a materialização em docs/plans/<tipo>/ (R-064)."""
    for rel in (".github/agents/prompt-structuring.agent.md", ".github/prompts/craft-prompt.prompt.md"):
        p = REPO_ROOT / rel
        content = p.read_text(encoding="utf-8")
        assert "docs/plans/<tipo>/" in content and "R-064" in content, remediation(
            f"'{rel}' não explicita a preservação da materialização física em 'docs/plans/<tipo>/' (R-064).",
            fix_hint=f"Adicionar cláusula de preservação do Gate R-064 em '{rel}'.",
        )


@pytest.mark.parametrize("sub", CANONICAL_PLAN_SUBFOLDERS)
def test_ca01_all_eight_subfolders_enforce_timestamp_hhmmss_and_forbid_plan_req_prefixes(sub: str):
    """CA-01 / R-064: Todos os planos nas 8 subpastas de docs/plans/<tipo>/ devem seguir ^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md$ (exceto README.md), proibindo prefixos PLAN- e REQ-."""
    pattern = re.compile(r"^\d{8}-\d{6}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
    forbidden_prefix = re.compile(r"^(PLAN|REQ)-", re.IGNORECASE)
    sub_dir = PLANS_ROOT / sub
    files = [p for p in sorted(sub_dir.glob("*.md")) if p.name != "README.md"]
    bad_prefix = [p.name for p in files if forbidden_prefix.match(p.name)]
    assert not bad_prefix, remediation(
        f"Planos em docs/plans/{sub}/ usam prefixo proibido PLAN- ou REQ-: {bad_prefix}",
        fix_hint=f"Renomear planos em docs/plans/{sub}/ para o padrão AAAAMMDD-HHMMSS-<slug>.md sem prefixos PLAN-/REQ-.",
    )
    invalid = [p.name for p in files if not pattern.match(p.name)]
    assert not invalid, remediation(
        f"Planos em docs/plans/{sub}/ fora do padrão AAAAMMDD-HHMMSS-<slug>.md: {invalid}",
        fix_hint=f"Renomear arquivos em docs/plans/{sub}/ para seguir ^\\d{{8}}-\\d{{6}}-[a-z0-9]+(-[a-z0-9]+)*\\.md$.",
    )


def test_ca07_specialized_templates_include_pre_hitl_skeptical_review():
    """CA-07: Os templates especializados R-064 e plan-frontmatter-r064.md incluem metadados e seção do Revisor Cético Pré-HITL (@plan-critic)."""
    fm_ref = (REPO_ROOT / SPECIALIZED_TEMPLATES["plan-frontmatter-r064.md"]).read_text(encoding="utf-8")
    for field in ("review_verdict", "review_rounds", "reviewer", "review_tier1"):
        assert field in fm_ref, f"Campo '{field}' ausente em plan-frontmatter-r064.md"
    for name, rel_path in SPECIALIZED_TEMPLATES.items():
        if name == "plan-frontmatter-r064.md":
            continue
        content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert "Parecer do Revisor Cético Pré-HITL (R-064)" in content, (
            f"Seção 'Parecer do Revisor Cético Pré-HITL (R-064)' ausente em {rel_path}"
        )
