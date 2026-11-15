"""Sincronizador e auditor determinístico de contagens SSOT em Markdown e blocos Mermaid (R-015 / R-033 / R-055 / R-064)."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import yaml

from tools.governance_sync.core import (
    SyncOptions,
    SyncReport,
    compute_unified_diff,
    create_sync_parser,
    parse_sync_options,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

MONITORED_MARKDOWN_FILES: tuple[str, ...] = (
    "README.md",
    "docs/repo-map.md",
    "docs/README.md",
    ".github/agents/README.md",
    ".github/skills/README.md",
    ".github/instructions/README.md",
    "docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md",
    "tests/README.md",
)

EXCLUDED_HISTORICAL_PATHS: tuple[str, ...] = (
    "docs/plans/",
    "CHANGELOG.md",
    "docs/adr/",
)

CANONICAL_AGENT_COVERAGE_DOCS: tuple[str, ...] = (
    "README.md",
    ".github/agents/README.md",
)

REMOVED_GHOST_AGENTS: tuple[str, ...] = (
    "refactor-executor",
)

R064_PRE_HITL_WORKFLOW_MERMAID_FILES: tuple[str, ...] = (
    ".github/agents/workflows.md",
    ".github/agents/workflows/workflow-feature-development.md",
    ".github/agents/workflows/workflow-bug-fix.md",
    ".github/agents/workflows/workflow-refactoring.md",
    ".github/agents/workflows/workflow-ui-layout.md",
    ".github/agents/workflows/workflow-framework-migration.md",
    ".github/agents/workflows/workflow-dependency-vulnerability-remediation.md",
    ".github/agents/workflows/workflow-release-readiness.md",
    ".github/agents/workflows/workflow-technical-analysis.md",
    ".github/agents/workflows/workflow-governance-maintenance.md",
)

WORKFLOW_MERMAID_EXEMPTIONS: dict[str, str] = {
    ".github/agents/workflows/workflow-prompt-synthesis.md": (
        "Workflow read-only de síntese de prompt sem Gate R-064 de plano mutativo."
    ),
}

MERMAID_FENCE_RE = re.compile(r"```mermaid\s*\r?\n(.*?)\r?\n```", re.DOTALL)


@dataclass(frozen=True)
class SSOTCounts:
    """Contagens canônicas derivadas dinamicamente das fontes da verdade (SSOT)."""

    total_agent_files: int
    root_agent_files: int
    stack_agent_files: int
    catalog_root_entries: int
    routing_graph_nodes: int
    total_skills: int
    tier1_skills: int
    tier2_skills: int
    tier3_skills: int
    total_canonical_workflows: int
    generic_instructions: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def is_excluded_historical_path(rel_path: str) -> bool:
    """Verifica se o caminho relativo pertence a registros históricos imutáveis."""
    norm = rel_path.replace("\\", "/").lstrip("./")
    for prefix in EXCLUDED_HISTORICAL_PATHS:
        clean_prefix = prefix.replace("\\", "/").lstrip("./")
        if norm == clean_prefix or norm.startswith(clean_prefix):
            return True
    return False


def collect_ssot_counts(repo_root: Path = REPO_ROOT) -> SSOTCounts:
    """Deriva dinamicamente todas as contagens SSOT a partir do filesystem e catálogos."""
    agents_dir = repo_root / ".github" / "agents"
    all_agent_files = sorted(agents_dir.rglob("*.agent.md"))
    root_agent_files = sorted(agents_dir.glob("*.agent.md"))
    stack_agent_files = [p for p in all_agent_files if p.parent != agents_dir]

    catalog_path = agents_dir / "catalog.yaml"
    catalog_data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    catalog_agents = catalog_data.get("agents", {})
    catalog_root_entries = len(catalog_agents)

    routing_graph_path = agents_dir / "routing-graph.yaml"
    routing_data = yaml.safe_load(routing_graph_path.read_text(encoding="utf-8")) or {}
    routing_nodes = routing_data.get("nos", {})
    routing_graph_nodes = len(routing_nodes)

    skills_dir = repo_root / ".github" / "skills"
    index_path = skills_dir / ".index.json"
    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    skills_list = index_data.get("skills", [])
    skill_md_files = sorted(skills_dir.glob("*/SKILL.md"))
    total_skills = len(skills_list) if skills_list else len(skill_md_files)

    tier_counts = {1: 0, 2: 0, 3: 0}
    for item in skills_list:
        t = int(item.get("tier", 0))
        if t in tier_counts:
            tier_counts[t] += 1

    workflows_dir = agents_dir / "workflows"
    canonical_workflows = sorted(workflows_dir.glob("workflow-*.md"))

    instructions_dir = repo_root / ".github" / "instructions"
    generic_instructions = sorted(instructions_dir.glob("*.instructions.md"))

    return SSOTCounts(
        total_agent_files=len(all_agent_files),
        root_agent_files=len(root_agent_files),
        stack_agent_files=len(stack_agent_files),
        catalog_root_entries=catalog_root_entries,
        routing_graph_nodes=routing_graph_nodes,
        total_skills=total_skills,
        tier1_skills=tier_counts[1],
        tier2_skills=tier_counts[2],
        tier3_skills=tier_counts[3],
        total_canonical_workflows=len(canonical_workflows),
        generic_instructions=len(generic_instructions),
    )


def load_catalog_agent_names(repo_root: Path = REPO_ROOT) -> list[str]:
    """Retorna os identificadores de todos os agents listados em .github/agents/catalog.yaml."""
    catalog_path = repo_root / ".github" / "agents" / "catalog.yaml"
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", {})
    if isinstance(agents, dict):
        return sorted(str(k) for k in agents.keys())
    if isinstance(agents, list):
        return sorted(str(item.get("name") or item.get("id")) for item in agents if isinstance(item, dict))
    return []


def _build_count_rules(counts: SSOTCounts) -> list[tuple[str, re.Pattern[str], str]]:
    """Constrói regras contextualizadas (label, regex, replacement) para auditoria e sincronização."""
    return [
        (
            "total_agent_files (.agent.md)",
            re.compile(r"\b(?P<num>\d+)(?P<tail>\s+arquivos\s+`?\.agent\.md`?)"),
            f"{counts.total_agent_files}\\g<tail>",
        ),
        (
            "root_plus_stack_agents (raiz + stacks)",
            re.compile(
                r"\b(?P<root>\d+)(?P<mid>\s+na\s+raiz\s*\+\s*)(?P<stack>\d+)(?P<tail>\s+em\s+`?stacks/[^)\n]*)"
            ),
            f"{counts.root_agent_files}\\g<mid>{counts.stack_agent_files}\\g<tail>",
        ),
        (
            "catalog_root_entries (entradas em catalog.yaml)",
            re.compile(
                r"(?P<head>catalog\.yaml`?\s*\()(?P<num>\d+)(?P<tail>\s+entradas\))"
            ),
            f"\\g<head>{counts.catalog_root_entries}\\g<tail>",
        ),
        (
            "routing_graph_nodes (nós no routing-graph.yaml)",
            re.compile(
                r"\b(?P<num>\d+)(?P<tail>\s+nós\s+no\s+`?routing-graph\.yaml`?)"
            ),
            f"{counts.routing_graph_nodes}\\g<tail>",
        ),
        (
            "routing_graph_nodes_alt (routing-graph.yaml com N nós)",
            re.compile(
                r"(?P<head>routing-graph\.yaml`?\s*(?:\(|com\s+|—\s*|:\s*))(?P<num>\d+)(?P<tail>\s+nós\b)"
            ),
            f"\\g<head>{counts.routing_graph_nodes}\\g<tail>",
        ),
        (
            "total_skills (skills ativas/catalogadas)",
            re.compile(
                r"\b(?P<num>\d+)(?P<tail>\s+skills\s+(?:ativas|catalogadas|em\s+`?\.github/skills/))"
            ),
            f"{counts.total_skills}\\g<tail>",
        ),
        (
            "total_canonical_workflows (workflows canônicos)",
            re.compile(
                r"\b(?P<num>\d+)(?P<tail>\s+workflows\s+canônicos(?!\s+de\s+ponta\s+a\s+ponta)(?:\s+em\s+`?\.github/agents/workflows|\s*\(`?workflow-\*\.md`?\)|\.|,|\s+e\b))"
            ),
            f"{counts.total_canonical_workflows}\\g<tail>",
        ),
    ]


def check_or_sync_markdown_counts(
    repo_root: Path = REPO_ROOT,
    counts: SSOTCounts | None = None,
    apply: bool = False,
    monitored_files: Sequence[str] = MONITORED_MARKDOWN_FILES,
) -> tuple[list[str], list[str], list[str]]:
    """Verifica (e opcionalmente aplica correções em) arquivos Markdown monitorados."""
    if counts is None:
        counts = collect_ssot_counts(repo_root)

    rules = _build_count_rules(counts)
    checked: list[str] = []
    updated: list[str] = []
    issues: list[str] = []

    for rel_path in monitored_files:
        if is_excluded_historical_path(rel_path):
            continue
        file_path = repo_root / rel_path
        if not file_path.is_file():
            issues.append(f"{rel_path}: arquivo monitorado ausente.")
            continue

        checked.append(rel_path)
        original = file_path.read_text(encoding="utf-8")
        current = original

        for label, pattern, replacement in rules:
            for match in pattern.finditer(current):
                matched_text = match.group(0)
                replaced_text = pattern.sub(replacement, matched_text, count=1)
                if matched_text != replaced_text:
                    issues.append(
                        f"{rel_path}: contagem defasada em '{label}' -> encontrado '{matched_text}', esperado '{replaced_text}'."
                    )
            if apply:
                current = pattern.sub(replacement, current)

        for ghost in REMOVED_GHOST_AGENTS:
            if re.search(rf"\b{re.escape(ghost)}\b", current):
                issues.append(
                    f"{rel_path}: referência proibida a agent fantasma removido '{ghost}'."
                )

        if apply and current != original:
            file_path.write_text(current, encoding="utf-8")
            updated.append(rel_path)

    return checked, updated, issues


def check_catalog_agent_coverage(
    repo_root: Path = REPO_ROOT,
    coverage_docs: Sequence[str] = CANONICAL_AGENT_COVERAGE_DOCS,
) -> list[str]:
    """Garante que 100% dos agents de catalog.yaml constam nos mapas/tabelas canônicos."""
    catalog_agents = load_catalog_agent_names(repo_root)
    issues: list[str] = []

    for rel_path in coverage_docs:
        doc_path = repo_root / rel_path
        if not doc_path.is_file():
            issues.append(f"{rel_path}: documento de cobertura de agents ausente.")
            continue
        text = doc_path.read_text(encoding="utf-8")
        missing = [
            agent
            for agent in catalog_agents
            if not re.search(rf"(?<![\w-]){re.escape(agent)}(?![\w-])", text)
        ]
        if missing:
            issues.append(
                f"{rel_path}: agents de catalog.yaml ausentes na cobertura documental: {', '.join(missing)}"
            )
        for ghost in REMOVED_GHOST_AGENTS:
            if re.search(rf"(?<![\w-]){re.escape(ghost)}(?![\w-])", text):
                issues.append(
                    f"{rel_path}: agent fantasma removido '{ghost}' ainda listado."
                )

    return issues


def extract_mermaid_blocks(markdown_text: str) -> list[str]:
    """Extrai o conteúdo de todos os blocos ```mermaid ... ``` de um texto Markdown."""
    return [m.group(1) for m in MERMAID_FENCE_RE.finditer(markdown_text)]


def validate_mermaid_block_syntax(block: str) -> list[str]:
    """Executa validação sintática determinística básica sobre um bloco Mermaid."""
    errors: list[str] = []
    stripped = block.strip()
    if not stripped:
        errors.append("bloco Mermaid vazio.")
        return errors

    lines = [ln.strip() for ln in stripped.splitlines() if ln.strip() and not ln.strip().startswith("%%")]
    if not lines:
        errors.append("bloco Mermaid sem declarações válidas.")
        return errors

    header = lines[0]
    valid_headers = (
        "flowchart",
        "graph",
        "sequenceDiagram",
        "stateDiagram",
        "classDiagram",
        "erDiagram",
        "gantt",
        "journey",
        "mindmap",
    )
    if not header.startswith(valid_headers):
        errors.append(f"cabeçalho Mermaid inválido ou desconhecido: '{header}'.")

    if header.startswith(("flowchart", "graph")):
        subgraph_count = len(re.findall(r"^\s*subgraph\b", stripped, flags=re.MULTILINE))
        end_count = len(re.findall(r"^\s*end\b", stripped, flags=re.MULTILINE))
        if subgraph_count != end_count:
            errors.append(f"desbalanceamento subgraph/end: {subgraph_count} subgraph vs {end_count} end.")

    return errors


def check_workflow_mermaid_blocks(
    repo_root: Path = REPO_ROOT,
    workflow_files: Sequence[str] = R064_PRE_HITL_WORKFLOW_MERMAID_FILES,
) -> list[str]:
    """Verifica a presença de plan-critic e a integridade sintática nos blocos Mermaid dos workflows R-064."""
    issues: list[str] = []

    for rel_path in workflow_files:
        norm = rel_path.replace("\\", "/")
        if norm in WORKFLOW_MERMAID_EXEMPTIONS:
            continue

        file_path = repo_root / norm
        if not file_path.is_file():
            issues.append(f"{norm}: arquivo de workflow monitorado ausente.")
            continue

        text = file_path.read_text(encoding="utf-8")
        open_mermaid = len(re.findall(r"^```mermaid\b", text, flags=re.MULTILINE))
        blocks = extract_mermaid_blocks(text)
        if open_mermaid != len(blocks):
            issues.append(
                f"{norm}: fences ```mermaid desbalanceados ({open_mermaid} aberturas vs {len(blocks)} blocos fechados)."
            )
        if not blocks:
            issues.append(f"{norm}: nenhum bloco ```mermaid encontrado.")
            continue

        has_plan_critic = any("plan-critic" in b for b in blocks)
        if not has_plan_critic:
            issues.append(
                f"{norm}: '@plan-critic' / 'plan-critic' ausente nos blocos ```mermaid (Gate R-064 Pré-HITL)."
            )

        for idx, block in enumerate(blocks, start=1):
            syntax_errors = validate_mermaid_block_syntax(block)
            for err in syntax_errors:
                issues.append(f"{norm} (bloco mermaid #{idx}): {err}")

    return issues


def run_sync(
    options: SyncOptions | None = None,
    repo_root: Path = REPO_ROOT,
) -> SyncReport:
    """Executa a auditoria/sincronização completa e retorna um SyncReport compatível com tools.governance_sync.core."""
    if options is None:
        options = SyncOptions(mode="check")

    apply_mode = options.is_apply
    counts = collect_ssot_counts(repo_root)

    checked_md, updated_md, count_issues = check_or_sync_markdown_counts(
        repo_root=repo_root,
        counts=counts,
        apply=apply_mode,
    )
    coverage_issues = check_catalog_agent_coverage(repo_root=repo_root)
    mermaid_issues = check_workflow_mermaid_blocks(repo_root=repo_root)

    if apply_mode and updated_md:
        _, _, count_issues = check_or_sync_markdown_counts(
            repo_root=repo_root,
            counts=counts,
            apply=False,
        )

    all_issues = [*count_issues, *coverage_issues, *mermaid_issues]
    all_checked = list(dict.fromkeys([*checked_md, *R064_PRE_HITL_WORKFLOW_MERMAID_FILES]))

    report = SyncReport(
        total_scanned=len(all_checked),
        drifted=list(all_issues),
        updated=list(updated_md),
        errors=[],
        diffs=[],
    )
    setattr(report, "issues", list(all_issues))
    setattr(report, "checked_files", all_checked)
    setattr(report, "updated_files", updated_md)
    setattr(report, "ssot_counts", counts)
    setattr(report, "exit_code", report.compute_exit_code(options.mode))
    return report


sync_docs_counts_and_mermaid = run_sync


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada CLI para python -m tools.governance_sync."""
    parser = create_sync_parser(
        "Sincroniza e valida contagens SSOT em Markdown e diagramas Mermaid de workflows."
    )
    options = parse_sync_options(parser, argv)
    report = run_sync(options=options, repo_root=REPO_ROOT)
    report.print_summary("Governance Docs Counts & Mermaid Sync", options.mode)
    return report.compute_exit_code(options.mode)


if __name__ == "__main__":
    sys.exit(main())
