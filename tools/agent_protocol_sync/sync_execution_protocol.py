"""
Sincroniza o bloco <execution_protocol> de todos os agents executores nao-roteadores
e de todos os prompts (.github/prompts/*.prompt.md) a partir de uma fonte canonica unica.

Motivacao (ver docs/plan/... ou CHANGELOG [2.33.3] / [2.52.2]):
    O protocolo Plan-Then-Batch (R-059) + Teto de Tool Turns/Warm Start (R-060) estava
    duplicado manualmente em 77 arquivos .agent.md. Edicoes manuais em lote (regex/batch)
    causaram corrupcao de caracteres de controle reincidente. Este script formaliza o
    mesmo padrao ja usado por tools/agentcard_exporter/export_agentcards.py: uma fonte
    canonica unica gera/valida os artefatos derivados.

    [2.52.2] Extensao: os 22 arquivos .github/prompts/*.prompt.md declaram
    source_docs_lazy: (R-066) mas nao possuiam NENHUM bloco <execution_protocol> -
    gap de discovery identico ao corrigido para agents em [2.52.1]. Prompts nao tem
    distincao STANDARD/CUSTOM (todos recebem o mesmo bloco canonico, inserido ao final
    do corpo do arquivo).

    Elegibilidade Primaria por Tools (is_ctx_eligible):
    Apenas artefatos que declaram ferramentas 'context-mode/ctx_*' em seu frontmatter
    'tools:' sao elegiveis para receber o bloco <execution_protocol>. Arquivos sem ferramentas
    context-mode NUNCA recebem o bloco (prevenindo instrucao morta em prompts/agents utilitarios).
    Para agents, alem da elegibilidade por tools, respeita-se o mapeamento de protocol_roles.json.

Fonte canonica:
    tools/agent_protocol_sync/_execution-protocol-fragment.md
    (contem o bloco STANDARD delimitado por marcadores HTML; unificado em
    2026-09-23 apos constatar que a antiga divisao MUTATING/READONLY diferia
    em apenas 3 palavras cosmeticas no item 3 - ver CHANGELOG [2.33.4])

Mapa de papeis (apenas para .agent.md):
    tools/agent_protocol_sync/protocol_roles.json
    { "<agent-id>": "STANDARD" | "CUSTOM" }

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
try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
FRAGMENT_PATH = Path(__file__).resolve().parent / "_execution-protocol-fragment.md"
ROLES_PATH = Path(__file__).resolve().parent / "protocol_roles.json"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"

BLOCK_RE = re.compile(r"<execution_protocol>([\s\S]*?)</execution_protocol>")


def extract_tools(path: Path) -> list[str]:
    """Extrai a lista de ferramentas declaradas no frontmatter YAML do arquivo."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) >= 3:
        if yaml is not None:
            try:
                data = yaml.safe_load(parts[1]) or {}
                tools = data.get("tools", [])
                if isinstance(tools, list):
                    return [str(t) for t in tools]
                elif isinstance(tools, str):
                    return [tools]
            except Exception:
                pass
        tools: list[str] = []
        in_tools = False
        for line in parts[1].splitlines():
            if re.match(r"^tools:\s*$", line):
                in_tools = True
                continue
            elif in_tools and re.match(r"^\s+-\s+(.*)$", line):
                m = re.match(r"^\s+-\s+(.*)$", line)
                if m:
                    tools.append(m.group(1).strip().strip("'").strip('"'))
            elif in_tools and (line.startswith(" ") or line.startswith("	")):
                continue
            elif in_tools:
                in_tools = False
            inline_m = re.match(r"^tools:\s*\[(.*)\]", line)
            if inline_m:
                items = [x.strip().strip("'").strip('"') for x in inline_m.group(1).split(",") if x.strip()]
                tools.extend(items)
        return tools
    return []


def is_ctx_eligible(tools: list[str]) -> bool:
    """Retorna True se qualquer item da lista tools comecar com 'context-mode/ctx_'."""
    return any(isinstance(t, str) and t.startswith("context-mode/ctx_") for t in tools)


def remove_execution_protocol_block(text: str) -> str:
    """Remove o bloco <execution_protocol>...</execution_protocol> preservando a formatacao."""
    if "<execution_protocol>" not in text:
        return text
    if re.search(r"\n*<execution_protocol>[\s\S]*?</execution_protocol>\s*$", text):
        return re.sub(r"\n*<execution_protocol>[\s\S]*?</execution_protocol>\s*$", "\n", text)
    return re.sub(r"\n*<execution_protocol>[\s\S]*?</execution_protocol>\n*", "\n\n", text)


def load_canonical_blocks() -> dict[str, str]:
    """Extrai o bloco STANDARD do arquivo de fragmento canonico."""
    text = FRAGMENT_PATH.read_text(encoding="utf-8")
    blocks: dict[str, str] = {}
    for role in ("STANDARD",):
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


def get_prompt_files() -> list[Path]:
    """Retorna todos os arquivos *.prompt.md sob .github/prompts/, excluindo templates/."""
    all_files = sorted(PROMPTS_DIR.glob("**/*.prompt.md"))
    return [p for p in all_files if "templates" not in p.parts]


def sync_prompts(expected_block: str, apply: bool) -> tuple[list[str], list[str]]:
    """Sincroniza o bloco STANDARD em todos os prompts. Prompts elegiveis
    (com context-mode/ctx_* em tools:) recebem o bloco. Prompts nao-elegiveis
    tem qualquer bloco <execution_protocol> residual removido."""
    drifted: list[str] = []
    updated: list[str] = []

    for pf in get_prompt_files():
        text = pf.read_text(encoding="utf-8")
        tools = extract_tools(pf)
        eligible = is_ctx_eligible(tools)
        m = BLOCK_RE.search(text)

        if not eligible:
            # Arquivo nao-elegivel: NUNCA deve conter o bloco
            if m is not None:
                drifted.append(f"{pf.name} (remover: nao-elegivel por tools)")
                if apply:
                    new_text = remove_execution_protocol_block(text)
                    pf.write_text(new_text, encoding="utf-8")
                    updated.append(pf.name)
            continue

        # Arquivo elegivel: deve conter o bloco canonico
        if m is None:
            drifted.append(pf.name)
            if apply:
                sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
                new_text = f"{text}{sep}<execution_protocol>\n{expected_block}\n</execution_protocol>\n"
                pf.write_text(new_text, encoding="utf-8")
                updated.append(pf.name)
            continue

        current_block = m.group(1).strip()
        if current_block == expected_block:
            continue  # em conformidade

        drifted.append(pf.name)
        if apply:
            new_text = BLOCK_RE.sub(
                lambda _: f"<execution_protocol>\n{expected_block}\n</execution_protocol>",
                text,
                count=1,
            )
            pf.write_text(new_text, encoding="utf-8")
            updated.append(pf.name)

    return drifted, updated


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
        tools = extract_tools(af)
        eligible = is_ctx_eligible(tools)
        m = BLOCK_RE.search(text)

        if not eligible:
            # Regra: arquivos SEM ctx_* NUNCA recebem o bloco, mesmo que em role_map
            if m is not None:
                drifted.append(f"{agent_id} (remover: nao-elegivel por tools)")
                if args.apply:
                    new_text = remove_execution_protocol_block(text)
                    af.write_text(new_text, encoding="utf-8")
                    updated.append(agent_id)
            continue

        if not m:
            missing.append(agent_id)
            continue

        current_block = m.group(1).strip()

        if role == "CUSTOM":
            # Agents pinados (ex.: codegraph-engine) mantem texto proprio.
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

    # Validacao de agentes fora do role_map (ex.: routers, prompt-structuring):
    # se algum contiver o bloco indevidamente, sinaliza drift para remocao
    for af in AGENTS_DIR.glob("**/*.agent.md"):
        if "templates" in af.parts:
            continue
        agent_id = af.name.replace(".agent.md", "")
        if agent_id in role_map:
            continue
        text = af.read_text(encoding="utf-8")
        if BLOCK_RE.search(text):
            drifted.append(f"{agent_id} (remover: fora do role_map)")
            if args.apply:
                new_text = remove_execution_protocol_block(text)
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

    # --- Prompts (.github/prompts/*.prompt.md) ---
    prompt_files = get_prompt_files()
    prompts_drifted, prompts_updated = sync_prompts(canonical["STANDARD"], apply=args.apply)

    print(f"\nPrompts mapeados: {len(prompt_files)}")
    print(f"Prompts com drift detectado: {len(prompts_drifted)}")
    if prompts_drifted:
        for d in prompts_drifted:
            print(f"  - {d}")
    if prompts_updated:
        print(f"\nPrompts corrigidos nesta execucao: {len(prompts_updated)}")
        for u in prompts_updated:
            print(f"  - {u}")

    if args.check:
        return 1 if (drifted or custom_missing_r060 or prompts_drifted) else 0

    if (drifted or prompts_drifted) and not args.apply:
        print("\nExecute com --apply para corrigir o drift acima.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
