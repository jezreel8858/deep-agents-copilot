"""
Golden Master / Characterization Test: Seção 'Retorno ao Router' (R-042).

Captura e congela como snapshot o estado atual das variantes textuais da seção
'Retorno ao Router (R-042)' em todos os .agent.md do ecossistema.
Não normaliza o texto — documenta com precisão o ponto de partida para permitir
refatoração segura e com reversibilidade garantida.
"""

from __future__ import annotations

import re
from pathlib import Path
from collections import defaultdict
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

ROUTER_SECTION_RE = re.compile(
    r"(##\s+[^\n]*(?:Retorno ao Router|R-042)[^\n]*\n)(.*?)(?=\n## |\Z)",
    re.DOTALL,
)


def extract_router_return_section(file_path: Path) -> tuple[str | None, str | None]:
    """Retorna (heading, body) da seção de Retorno ao Router / R-042 se presente."""
    text = file_path.read_text(encoding="utf-8")
    m = ROUTER_SECTION_RE.search(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def test_router_return_section_golden_master_characterization():
    """
    Varre todos os agents, extrai a seção R-042 e valida os invariantes do snapshot atual:
    - 86 agents no total.
    - 85 possuem seção explícita de retorno ao router (apenas agent-router.agent.md não possui,
      pois é o próprio orquestrador raiz).
    - Mapeia variantes textuais e emite relatório estruturado.
    """
    agent_files = sorted(AGENTS_DIR.glob("**/*.agent.md"))
    assert len(agent_files) >= 86, f"Esperado >= 86 agents, encontrados {len(agent_files)}"

    variants: dict[str, list[str]] = defaultdict(list)
    missing: list[str] = []
    heading_counts: dict[str, int] = defaultdict(int)

    for af in agent_files:
        rel_path = str(af.relative_to(REPO_ROOT)).replace("\\", "/")
        heading, body = extract_router_return_section(af)
        if heading is None:
            missing.append(rel_path)
        else:
            full_section = f"{heading}\n\n{body}"
            variants[full_section].append(rel_path)
            heading_counts[heading] += 1

    # Invariantes do estado atual (Golden Master Snapshot)
    assert missing == [".github/agents/agent-router.agent.md"], (
        f"Apenas o agent-router não deve ter seção de retorno a si mesmo. Ausentes: {missing}"
    )

    # Todos os 85 agents não-roteadores têm seção
    assert len(agent_files) - len(missing) == 85

    # Relatório de variantes capturadas
    print(f"\n=== GOLDEN MASTER SNAPSHOT: R-042 RETORNO AO ROUTER ===")
    print(f"Total de agents auditados: {len(agent_files)}")
    print(f"Agents com seção R-042: {len(agent_files) - len(missing)}")
    print(f"Agents sem seção R-042 (esperado agent-router): {missing}")
    print(f"Total de variantes textuais distintas: {len(variants)}")
    print(f"Distribuição de cabeçalhos:")
    for h, cnt in heading_counts.items():
        print(f"  - [{cnt}x] {h}")
