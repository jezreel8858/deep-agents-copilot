"""
Sincroniza o bloco <execution_protocol> de todos os agents executores nao-roteadores
a partir de uma fonte canonica unica.

Motivacao (ver docs/plan/... ou CHANGELOG [2.33.3]):
    O protocolo Plan-Then-Batch (R-059) + Teto de Tool Turns/Warm Start (R-060) estava
    duplicado manualmente em 77 arquivos .agent.md. Edicoes manuais em lote (regex/batch)
    causaram corrupcao de caracteres de controle reincidente. Este script formaliza o
    mesmo padrao ja usado por tools/agentcard_exporter/export_agentcards.py: uma fonte
    canonica unica gera/valida os artefatos derivados.

Fonte canonica:
    .github/agents/templates/_execution-protocol-fragment.md
    (contem os blocos MUTATING e READONLY delimitados por marcadores HTML)

Mapa de papeis:
    tools/agent_protocol_sync/protocol_roles.json
    { "<agent-id>": "MUTATING" | "READONLY" | "CUSTOM" }

Uso:
    python tools/agent_protocol_sync/sync_execution_protocol.py            # dry-run (mostra diffs)
    python tools/agent_protocol_sync/sync_execution_protocol.py --apply    # aplica as correcoes
    python tools/agent_protocol_sync/sync_execution_protocol.py --check    # exit code 1 se houver drift (uso em CI)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FRAGMENT_PATH = Path(__file__).resolve().parent / "_execution-protocol-fragment.md"
ROLES_PATH = Path(__file__).resolve().parent / "protocol_roles.json"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

BLOCK_RE = re.compile(r"<execution_protocol>([\s\S]*?)</execution_protocol>")


def load_canonical_blocks() -> dict[str, str]:
    """Extrai os blocos MUTATING/READONLY do arquivo de fragmento canonico."""
    text = FRAGMENT_PATH.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for role in ("MUTATING", "READONLY"):
        pattern = re.compile(
            rf"<!-- BEGIN:{role} -->\s*\n([\s\S]*?)\n<!-- END:{role} -->"
        )
        m = pattern.search(text)
        if not m:
            raise ValueError(f"Bloco canonico '{role}' nao encontrado em {FRAGMENT_PATH}")
        blocks[role] = m.group(1).strip()
    return blocks


def load_role_map() -> dict[str, str]:
    return json.loads(ROLES_PATH.read_text(encoding="utf-8"))


def find_agent_file(agent_id: str) -> Path | None:
    matches = list(AGENTS_DIR.glob(f"**/{agent_id}.agent.md"))
    return matches[0] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Aplica as correcoes de drift nos arquivos.")
    parser.add_argument("--check", action="store_true", help="Modo CI: exit code 1 se houver drift, nao aplica nada.")
    args = parser.parse_args()

    canonical = load_canonical_blocks()
    role_map = load_role_map()

    drifted: list[str] = []
    missing: list[str] = []
    custom_missing_r060: list[str] = []
    updated: list[str] = []

    for agent_id, role in role_map.items():
        af = find_agent_file(agent_id)
        if af is None:
            missing.append(agent_id)
            continue

        text = af.read_text(encoding="utf-8")
        m = BLOCK_RE.search(text)
        if not m:
            missing.append(agent_id)
            continue

        current_block = m.group(1).strip()

        if role == "CUSTOM":
            # Agents pinados (ex.: code-knowledge-graph) mantem texto proprio.
            # So validamos que a marca normativa R-060 ainda esta presente.
            if "R-060" not in current_block:
                custom_missing_r060.append(agent_id)
            continue

        if role not in canonical:
            drifted.append(f"{agent_id} (papel desconhecido: {role})")
            continue

        expected_block = canonical[role]
        if current_block == expected_block:
            continue  # em conformidade

        drifted.append(agent_id)
        if args.apply:
            new_text = BLOCK_RE.sub(
                lambda _: f"<execution_protocol>\n{expected_block}\n</execution_protocol>",
                text,
                count=1,
            )
            af.write_text(new_text, encoding="utf-8")
            updated.append(agent_id)

    print(f"Agents mapeados: {len(role_map)}")
    print(f"Agents com drift detectado: {len(drifted)}")
    if drifted:
        for d in drifted:
            print(f"  - {d}")
    if updated:
        print(f"\nAgents corrigidos nesta execucao: {len(updated)}")
        for u in updated:
            print(f"  - {u}")
    if missing:
        print(f"\nAVISO: agents nao encontrados ou sem bloco <execution_protocol>: {len(missing)}")
        for msg in missing:
            print(f"  - {msg}")
    if custom_missing_r060:
        print(f"\nERRO: agents CUSTOM sem marca R-060: {len(custom_missing_r060)}")
        for c in custom_missing_r060:
            print(f"  - {c}")

    if args.check:
        return 1 if (drifted or custom_missing_r060) else 0

    if drifted and not args.apply:
        print("\nExecute com --apply para corrigir o drift acima.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

