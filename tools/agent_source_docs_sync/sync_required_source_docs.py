"""
Sincroniza determinística e atomicamente as referências obrigatórias de source_docs:
em todos os agents (.agent.md) com base em regras canônicas declarativas.

Motivação e Decisão Técnica:
    - Anteriormente, referências como '.github/skills/handoff-governance/SKILL.md' ou
      '.github/skills/agent-contracts/SKILL.md' eram inseridas via edições LLM manuais
      ou inspeções frágeis de regex de texto livre em testes.
    - Este script estabelece a Single Canonical Source em 'required_source_docs_rules.json'.
    - YAML-Aware: O script utiliza `yaml.safe_load` para inspecionar com precisão semântica
      as listas `tools:` e `source_docs:` do frontmatter.
    - Preservação Estrita de Formatação: Em vez de re-dump completo do YAML (que causaria perda
      de formatação de multiline strings, aspas e comentários), as entradas faltantes são inseridas
      cirurgicamente na lista `source_docs:` com a mesma indentação e estilo existentes.
    - R-051 (Double-Check): Toda escrita em modo `--apply` é imediatamente relida do disco e
      revalidada contra `yaml.safe_load` garantindo que os novos itens foram anexados sem alterar
      nenhum outro campo do frontmatter nem o corpo do arquivo.

Uso:
    python tools/agent_source_docs_sync/sync_required_source_docs.py            # modo --check (default: fail-safe)
    python tools/agent_source_docs_sync/sync_required_source_docs.py --check    # modo CI explícito (exit 1 se drift)
    python tools/agent_source_docs_sync/sync_required_source_docs.py --dry-run  # simula e exibe diffs unificados
    python tools/agent_source_docs_sync/sync_required_source_docs.py --apply    # aplica gravação atômica em disco
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governance_sync.core import (
    SyncReport,
    compute_unified_diff,
    create_sync_parser,
    parse_sync_options,
)

RULES_PATH = Path(__file__).resolve().parent / "required_source_docs_rules.json"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"


def load_rules() -> list[dict[str, Any]]:
    """Carrega as regras declarativas de required_source_docs_rules.json."""
    if not RULES_PATH.is_file():
        raise FileNotFoundError(f"Arquivo de regras canônicas não encontrado: {RULES_PATH}")
    payload = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return payload.get("rules", [])


def split_frontmatter_and_body(text: str) -> tuple[str, str, str, str] | None:
    """
    Divide o arquivo .agent.md em (delimitador_abertura, frontmatter_text, delimitador_fechamento, corpo).
    Retorna None se os delimitadores frontmatter '---' não forem encontrados no topo.
    """
    match = re.match(r"^(---\r?\n)(.*?\r?\n)(---\r?\n?)(.*)$", text, re.DOTALL)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3), match.group(4)


def evaluate_condition(condition: dict[str, Any], frontmatter_data: dict[str, Any]) -> bool:
    """
    Avalia predicados declarativos contra o frontmatter do agent.
    Suporta:
        - tools_contains: valor string esperado na lista tools
    """
    if "tools_contains" in condition:
        expected_tool = condition["tools_contains"]
        tools = frontmatter_data.get("tools", [])
        if isinstance(tools, str):
            tools = [tools]
        if expected_tool not in tools:
            return False

    return True


def insert_source_docs(frontmatter_text: str, missing_docs: list[str]) -> str:
    """
    Insere cirurgicamente os missing_docs na lista source_docs: do frontmatter,
    preservando indentação, quebras de linha e todas as demais chaves do YAML.
    """
    lines = frontmatter_text.splitlines(keepends=True)

    # Localizar a chave 'source_docs:'
    source_docs_idx = -1
    for idx, line in enumerate(lines):
        if re.match(r"^source_docs:\s*(?:#.*)?$", line.strip()):
            source_docs_idx = idx
            break

    line_end = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"

    # Se source_docs não existir, adiciona no final do frontmatter
    if source_docs_idx == -1:
        new_lines = list(lines)
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] += line_end
        new_lines.append(f"source_docs:{line_end}")
        for doc in missing_docs:
            new_lines.append(f"  - {doc}{line_end}")
        return "".join(new_lines)

    # Identificar indentação dos itens existentes e o ponto de inserção
    indent = "  "
    last_item_idx = source_docs_idx

    for idx in range(source_docs_idx + 1, len(lines)):
        line = lines[idx]
        if re.match(r"^[ \t]+-", line):
            last_item_idx = idx
            m_indent = re.match(r"^([ \t]+)-", line)
            if m_indent:
                indent = m_indent.group(1)
        elif line.strip() == "" or line.strip().startswith("#"):
            continue
        elif re.match(r"^[a-zA-Z0-9_-]+:", line):
            # Próxima chave top-level
            break
        elif re.match(r"^[ \t]+[a-zA-Z0-9_-]+:", line):
            # Próxima chave de bloco indentado
            break

    insert_idx = last_item_idx + 1
    items_to_add = [f"{indent}- {doc}{line_end}" for doc in missing_docs]
    new_lines = lines[:insert_idx] + items_to_add + lines[insert_idx:]
    return "".join(new_lines)


def get_agent_files() -> list[Path]:
    """Retorna todos os arquivos .agent.md sob .github/agents/, excluindo templates/."""
    all_files = sorted(AGENTS_DIR.glob("**/*.agent.md"))
    return [p for p in all_files if "templates" not in p.parts]


def sync_agent_source_docs(mode: str) -> tuple[SyncReport, int]:
    """Executa a varredura e sincronização de source_docs em conformidade com o modo solicitado."""
    rules = load_rules()
    report = SyncReport()

    agent_files = get_agent_files()
    for af in agent_files:
        report.total_scanned += 1
        content = af.read_text(encoding="utf-8")

        parts = split_frontmatter_and_body(content)
        if not parts:
            report.errors.append(f"{af.name}: delimitadores frontmatter '---' não encontrados")
            continue

        open_delim, fm_text, close_delim, body = parts
        try:
            fm_data = yaml.safe_load(fm_text) or {}
        except Exception as e:
            report.errors.append(f"{af.name}: erro de parse no frontmatter YAML: {e}")
            continue

        if not isinstance(fm_data, dict):
            report.errors.append(f"{af.name}: frontmatter YAML não é um mapeamento/dicionário")
            continue

        existing_source_docs = fm_data.get("source_docs", []) or []
        if isinstance(existing_source_docs, str):
            existing_source_docs = [existing_source_docs]

        # Avaliar regras aplicáveis
        missing_for_file: list[str] = []
        for rule in rules:
            rule_id = rule.get("id", "unknown_rule")
            exclude_files = rule.get("exclude_files", [])
            if af.name in exclude_files:
                continue

            condition = rule.get("condition", {})
            if not evaluate_condition(condition, fm_data):
                continue

            required_docs = rule.get("required_source_docs", [])
            for doc in required_docs:
                if doc not in existing_source_docs and doc not in missing_for_file:
                    missing_for_file.append(doc)

        if not missing_for_file:
            continue

        # Drift detectado
        rel_path = str(af.relative_to(REPO_ROOT))
        missing_desc = ", ".join(Path(d).parent.name for d in missing_for_file)
        report.drifted.append(f"{rel_path} (faltando: {missing_desc})")

        # Modificação cirúrgica
        new_fm_text = insert_source_docs(fm_text, missing_for_file)
        new_content = f"{open_delim}{new_fm_text}{close_delim}{body}"

        # Validação semântica em memória antes de qualquer ação
        try:
            new_fm_data = yaml.safe_load(new_fm_text)
            assert isinstance(new_fm_data, dict), "Frontmatter resultante inválido"
            expected_new_docs = existing_source_docs + missing_for_file
            assert new_fm_data.get("source_docs") == expected_new_docs, (
                f"Mismatch em source_docs após inserção em {af.name}"
            )
            # Garantir integridade de todos os outros campos
            for k, v in fm_data.items():
                if k != "source_docs":
                    assert new_fm_data.get(k) == v, f"Campo {k} foi corrompido em {af.name}"
        except Exception as e:
            report.errors.append(f"{af.name}: validação de inserção falhou: {e}")
            continue

        if mode == "dry-run":
            diff = compute_unified_diff(content, new_content, af.name)
            report.diffs.append(diff)
        elif mode == "apply":
            af.write_text(new_content, encoding="utf-8")

            # R-051 Double-Check: reler do disco e revalidar
            re_read_text = af.read_text(encoding="utf-8")
            re_parts = split_frontmatter_and_body(re_read_text)
            if not re_parts:
                report.errors.append(f"{af.name}: R-051 falhou ao ler delimitadores após gravação")
                continue
            re_fm_data = yaml.safe_load(re_parts[1])
            if re_fm_data.get("source_docs") != expected_new_docs:
                report.errors.append(f"{af.name}: R-051 falhou na verificação de source_docs pós-gravação")
                continue

            report.updated.append(rel_path)

    exit_code = report.compute_exit_code(mode)
    return report, exit_code


def main(args: list[str] | None = None) -> int:
    parser = create_sync_parser(__doc__)
    options = parse_sync_options(parser, args)

    report, exit_code = sync_agent_source_docs(options.mode)
    report.print_summary("Agent Required Source Docs Sync", options.mode)

    if options.is_check and report.has_drift:
        print("\nPara aplicar as correções canônicas de source_docs:, execute:")
        print("  python tools/agent_source_docs_sync/sync_required_source_docs.py --apply")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
