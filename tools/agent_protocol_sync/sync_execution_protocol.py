# Sincronizacao de execution_protocol
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

BLOCK_RE = re.compile(
    r"(?:^## ⚙️ Protocolo de Execução Obrigatório\s*\n+)?<execution_protocol>([\s\S]*?)</execution_protocol>",
    re.MULTILINE,
)


def extract_frontmatter_dict(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) >= 3:
        if yaml is not None:
            try:
                data = yaml.safe_load(parts[1])
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        data: dict = {}
        if re.search(r"^source_docs_lazy:", parts[1], re.MULTILINE):
            data["source_docs_lazy"] = True
        return data
    return {}


def extract_tools(path: Path) -> list[str]:
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
            elif in_tools and (line.startswith(" ") or line.startswith("\t")):
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
    return any(isinstance(t, str) and t.startswith("context-mode/ctx_") for t in tools)


def remove_execution_protocol_block(text: str) -> str:
    pattern_end = re.compile(
        r"\n*(?:^## ⚙️ Protocolo de Execução Obrigatório\s*\n+)?<execution_protocol>[\s\S]*?</execution_protocol>\s*$",
        re.MULTILINE,
    )
    if pattern_end.search(text):
        return pattern_end.sub("\n", text)
    pattern_mid = re.compile(
        r"\n*(?:^## ⚙️ Protocolo de Execução Obrigatório\s*\n+)?<execution_protocol>[\s\S]*?</execution_protocol>\n*",
        re.MULTILINE,
    )
    return pattern_mid.sub("\n\n", text)


def insert_execution_protocol_block(text: str, full_block: str) -> str:
    router_match = re.search(r"\n*(##\s*(?:[^\w\s]\s*)?Retorno ao Router\b[^\n]*)", text)
    if router_match:
        idx = router_match.start()
        before = text[:idx].rstrip()
        after = text[idx:].lstrip("\n")
        return f"{before}\n\n{full_block}\n\n{after}\n"
    else:
        before = text.rstrip()
        return f"{before}\n\n{full_block}\n"


def load_canonical_fragments() -> dict[str, str]:
    text = FRAGMENT_PATH.read_text(encoding="utf-8")
    fragments: dict[str, str] = {}
    sections = ("CORE", "CLAUSE_MUTATION", "CLAUSE_HANDOFF", "CLAUSE_LAZY_DOCS")
    for sec in sections:
        pattern = re.compile(
            rf"<!-- BEGIN:{sec} -->\s*\n([\s\S]*?)\n<!-- END:{sec} -->"
        )
        m = pattern.search(text)
        if not m:
            raise ValueError(f"Fragmento canonico '{sec}' nao encontrado em {FRAGMENT_PATH}")
        fragments[sec] = m.group(1).strip()
    return fragments


def load_role_map() -> dict[str, str]:
    return json.loads(ROLES_PATH.read_text(encoding="utf-8"))


def find_agent_file(agent_id: str) -> Path | None:
    matches = list(AGENTS_DIR.glob(f"**/{agent_id}.agent.md"))
    return matches[0] if matches else None


def get_prompt_files() -> list[Path]:
    all_files = sorted(PROMPTS_DIR.glob("**/*.prompt.md"))
    return [p for p in all_files if "templates" not in p.parts]


def build_execution_protocol_block(path: Path, fragments: dict[str, str]) -> str:
    tools = extract_tools(path)
    fm_data = extract_frontmatter_dict(path)

    has_mutation = (
        any(t in tools for t in ["replace_string_in_file", "create_file", "insert_edit_into_file", "get_errors"])
        or any(t in tools for t in ["context-mode/ctx_execute", "context-mode/ctx_execute_file"])
    )
    has_subagent = "run_subagent" in tools
    has_lazy = bool(fm_data.get("source_docs_lazy"))

    items = [fragments["CORE"]]
    next_idx = 6

    if has_mutation:
        items.append(f"{next_idx}. {fragments['CLAUSE_MUTATION']}")
        next_idx += 1

    if has_subagent:
        items.append(f"{next_idx}. {fragments['CLAUSE_HANDOFF']}")
        next_idx += 1

    if has_lazy:
        items.append(f"{next_idx}. {fragments['CLAUSE_LAZY_DOCS']}")
        next_idx += 1

    body = "\n".join(items).strip()
    return f"## ⚙️ Protocolo de Execução Obrigatório\n\n<execution_protocol>\n\n{body}\n\n</execution_protocol>"


def sync_prompts(fragments: dict[str, str], apply: bool) -> tuple[list[str], list[str]]:
    drifted: list[str] = []
    updated: list[str] = []

    for pf in get_prompt_files():
        text = pf.read_text(encoding="utf-8")
        tools = extract_tools(pf)
        eligible = is_ctx_eligible(tools)
        m = BLOCK_RE.search(text)

        if not eligible:
            if m is not None:
                drifted.append(f"{pf.name} (remover: nao-elegivel por tools)")
                if apply:
                    new_text = remove_execution_protocol_block(text)
                    pf.write_text(new_text, encoding="utf-8")
                    updated.append(pf.name)
            continue

        expected_block = build_execution_protocol_block(pf, fragments)

        if m is None:
            drifted.append(pf.name)
            if apply:
                new_text = insert_execution_protocol_block(text, expected_block)
                pf.write_text(new_text, encoding="utf-8")
                updated.append(pf.name)
            continue

        current_full_block = m.group(0).strip()
        if current_full_block == expected_block.strip():
            continue

        drifted.append(pf.name)
        if apply:
            new_text = BLOCK_RE.sub(
                lambda _: expected_block,
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

    fragments = load_canonical_fragments()
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

        current_inner_block = m.group(1).strip()
        current_full_block = m.group(0).strip()

        if role == "CUSTOM":
            if "R-060" not in current_inner_block:
                custom_missing_r060.append(agent_id)
            expected_custom = (
                f"## ⚙️ Protocolo de Execução Obrigatório\n\n"
                f"<execution_protocol>\n\n{current_inner_block}\n\n</execution_protocol>"
            )
            if current_full_block != expected_custom:
                drifted.append(f"{agent_id} (atualizar: cabecalho H2 / formatacao CommonMark)")
                if args.apply:
                    new_text = BLOCK_RE.sub(
                        lambda _: expected_custom,
                        text,
                        count=1,
                    )
                    af.write_text(new_text, encoding="utf-8")
                    updated.append(agent_id)
            continue

        expected_block = build_execution_protocol_block(af, fragments)
        if current_full_block == expected_block.strip():
            continue

        drifted.append(agent_id)
        if args.apply:
            new_text = BLOCK_RE.sub(
                lambda _: expected_block,
                text,
                count=1,
            )
            af.write_text(new_text, encoding="utf-8")
            updated.append(agent_id)

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

    prompt_files = get_prompt_files()
    prompts_drifted, prompts_updated = sync_prompts(fragments, apply=args.apply)

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
