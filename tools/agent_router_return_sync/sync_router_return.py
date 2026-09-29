"""
Sincroniza e normaliza a seção 'Retorno ao Router (R-042 — Anti Sticky-Session)'
em todos os agents executores e especialistas não-roteadores.

Utiliza tools/governance_sync/core.py para ciclo de vida de flags, diffs e relatórios.

Uso:
    python tools/agent_router_return_sync/sync_router_return.py            # modo --check (default)
    python tools/agent_router_return_sync/sync_router_return.py --check    # modo CI
    python tools/agent_router_return_sync/sync_router_return.py --dry-run  # simulação e visualização de diffs
    python tools/agent_router_return_sync/sync_router_return.py --apply    # aplica gravação em lote nos arquivos
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance_sync.core import (
    create_sync_parser,
    parse_sync_options,
    SyncReport,
    compute_unified_diff,
)

FRAGMENT_PATH = Path(__file__).resolve().parent / "_router-return-fragment.md"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

ROUTER_SECTION_RE = re.compile(
    r"(##\s+[^\n]*(?:Retorno ao Router|R-042)[^\n]*\n)(.*?)(?=\n## |\Z)",
    re.DOTALL,
)


def load_canonical_templates() -> tuple[str, str]:
    text = FRAGMENT_PATH.read_text(encoding="utf-8")
    m_h = re.search(r"<!-- BEGIN:HEADING -->\s*\n(.*?)\n<!-- END:HEADING -->", text, re.DOTALL)
    m_b = re.search(r"<!-- BEGIN:BANNER -->\s*\n(.*?)\n<!-- END:BANNER -->", text, re.DOTALL)
    if not m_h or not m_b:
        raise ValueError(f"Fragmento canonico incompleto em {FRAGMENT_PATH}")
    return m_h.group(1).strip(), m_b.group(1).strip()


def load_canonical_telemetry() -> str:
    text = FRAGMENT_PATH.read_text(encoding="utf-8")
    m_t = re.search(r"<!-- BEGIN:TELEMETRY -->\s*\n(.*?)\n<!-- END:TELEMETRY -->", text, re.DOTALL)
    if not m_t:
        raise ValueError(f"Bloco TELEMETRY ausente em {FRAGMENT_PATH}")
    return m_t.group(1).strip()


def normalize_router_section(
    agent_id: str,
    current_heading: str,
    current_body: str,
    canonical_heading: str,
    canonical_banner_tmpl: str,
    canonical_telemetry: str | None = None,
) -> tuple[str, str]:
    """
    Substitui cirurgicamente o cabeçalho e o parágrafo de banner pelo padrão canônico,
    preservando regras específicas de handoff e gatilhos de deriva do agente.
    Para domain routers (*-router), injeta também o bloco canônico de telemetria após o banner.
    """
    if canonical_telemetry is None and agent_id.endswith("-router"):
        canonical_telemetry = load_canonical_telemetry()

    canonical_banner = canonical_banner_tmpl.format(AGENT_ID=agent_id)
    paras = [p.strip() for p in current_body.split("\n\n") if p.strip()]

    handoff_paras: list[str] = []
    has_post_impl_handoff: str | None = None

    for p in paras:
        if "Handoff Pós-Implementação Obrigatório" in p:
            lines = p.splitlines()
            post_impl_lines = [
                l for l in lines if not ("Banner" in l or "Agente Ativo:" in l)
            ]
            if post_impl_lines:
                has_post_impl_handoff = "\n".join(post_impl_lines).strip()
            continue

        if ("Banner" in p and "Agente Ativo" in p) or ("visibilidade de fluxo" in p):
            lines = p.splitlines()
            non_banner_lines = [
                l for l in lines
                if not any(k in l for k in ("Banner", "Agente Ativo", "OpenAI Agents SDK", "LangGraph", "visibilidade de fluxo"))
            ]
            if non_banner_lines:
                handoff_paras.append("\n".join(non_banner_lines).strip())
        elif "Telemetria de Handoff" in p or "telemetry_entry" in p:
            continue
        else:
            handoff_paras.append(p)

    body_parts: list[str] = []
    if has_post_impl_handoff:
        body_parts.append(has_post_impl_handoff)
    body_parts.append(canonical_banner)
    if agent_id.endswith("-router") and canonical_telemetry:
        body_parts.append(canonical_telemetry)
    if handoff_paras:
        body_parts.extend(handoff_paras)

    return canonical_heading, "\n\n".join(body_parts)


def sync_all_agents(mode: str) -> tuple[SyncReport, int]:
    canonical_heading, canonical_banner_tmpl = load_canonical_templates()
    canonical_telemetry = load_canonical_telemetry()
    report = SyncReport()

    agent_files = sorted(AGENTS_DIR.glob("**/*.agent.md"))
    for af in agent_files:
        # Pular o próprio agent-router (é o orquestrador raiz, não possui retorno a si mesmo)
        if af.name == "agent-router.agent.md":
            continue

        report.total_scanned += 1
        content = af.read_text(encoding="utf-8")
        aid = af.name.replace(".agent.md", "")

        m = ROUTER_SECTION_RE.search(content)
        if not m:
            report.errors.append(f"{af.name}: secao Retorno ao Router ausente")
            continue

        current_heading = m.group(1).strip()
        current_body = m.group(2).strip()

        norm_heading, norm_body = normalize_router_section(
            aid, current_heading, current_body, canonical_heading, canonical_banner_tmpl, canonical_telemetry
        )

        current_full = f"{current_heading}\n\n{current_body}"
        norm_full = f"{norm_heading}\n\n{norm_body}"

        if current_full != norm_full:
            report.drifted.append(af.name)
            new_file_content = ROUTER_SECTION_RE.sub(
                lambda _: f"{norm_heading}\n\n{norm_body}\n",
                content,
                count=1,
            )
            if mode == "dry-run":
                diff = compute_unified_diff(content, new_file_content, af.name)
                report.diffs.append(diff)
            elif mode == "apply":
                af.write_text(new_file_content, encoding="utf-8")
                report.updated.append(af.name)

    exit_code = report.compute_exit_code(mode)
    return report, exit_code


def main() -> int:
    parser = create_sync_parser(__doc__)
    options = parse_sync_options(parser)

    report, exit_code = sync_all_agents(options.mode)
    report.print_summary("Retorno ao Router (R-042) Sync", options.mode)

    if options.is_check and report.has_drift:
        print("\nPara aplicar a sincronizacao canonica, execute:")
        print("  python tools/agent_router_return_sync/sync_router_return.py --apply")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
