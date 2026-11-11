"""
Sincroniza determinística e atomicamente `source_docs:` e `source_docs_lazy:` em todos
os artefatos de governança (.agent.md, SKILL.md, *.prompt.md), conforme R-066
(Progressive Disclosure Compulsória por limiar de 300 linhas).

Regras (R-066 / LAZY_LINE_THRESHOLD = 300):
    - Documentos com > 300 linhas pertencentes à LAZY_ALLOWLIST devem residir em
      `source_docs_lazy:` (consulta exclusiva via `context-mode/ctx_search` sob demanda).
    - Documentos presentes em `source_docs_lazy:` que possuam <= 300 linhas devem ser
      migrados para `source_docs:` (removendo a chave `source_docs_lazy:` quando vazia).
    - Preservação Estrita de Formatação: manipulação cirúrgica de linhas sem re-dump global do YAML.

Escopo de arquivos:
    - .github/agents/**/*.agent.md (exclui templates/)
    - .github/skills/**/SKILL.md (exclui templates/)
    - .github/prompts/**/*.prompt.md (exclui templates/)

Uso:
    python tools/agent_source_docs_sync/sync_lazy_source_docs.py            # --check (default)
    python tools/agent_source_docs_sync/sync_lazy_source_docs.py --dry-run  # mostra diffs
    python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply    # aplica gravação atômica
"""

from __future__ import annotations

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

LAZY_LINE_THRESHOLD = 300

LAZY_ALLOWLIST = {
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/agents/workflows.md",
}


def get_doc_line_count(doc_path: str) -> int:
    """Retorna a contagem de linhas de um documento relativo a REPO_ROOT."""
    p = REPO_ROOT / doc_path
    if not p.is_file():
        return 0
    return len(p.read_text(encoding="utf-8").splitlines())


def _is_lazy(doc_path: str) -> bool:
    """Classifica um doc como lazy se estiver na allowlist E possuir > 300 linhas (R-066)."""
    return doc_path in LAZY_ALLOWLIST and get_doc_line_count(doc_path) > LAZY_LINE_THRESHOLD


def _should_migrate_to_full(doc_path: str) -> bool:
    """Todo documento em source_docs_lazy com <= 300 linhas deve migrar para source_docs."""
    p = REPO_ROOT / doc_path
    if not p.is_file():
        return False
    return get_doc_line_count(doc_path) <= LAZY_LINE_THRESHOLD


TARGET_GLOBS: list[tuple[Path, str]] = [
    (REPO_ROOT / ".github" / "agents", "**/*.agent.md"),
    (REPO_ROOT / ".github" / "skills", "**/SKILL.md"),
    (REPO_ROOT / ".github" / "prompts", "**/*.prompt.md"),
]


def get_target_files() -> list[Path]:
    """Retorna todos os artefatos .agent.md / SKILL.md / *.prompt.md, excluindo templates/."""
    files: list[Path] = []
    for base_dir, pattern in TARGET_GLOBS:
        if not base_dir.is_dir():
            continue
        for p in sorted(base_dir.glob(pattern)):
            if "templates" in p.parts:
                continue
            files.append(p)
    return files


def split_frontmatter_and_body(text: str) -> tuple[str, str, str, str] | None:
    """Divide o arquivo em (delimitador_abertura, frontmatter_text, delimitador_fechamento, corpo)."""
    match = re.match(r"^(---\r?\n)(.*?\r?\n)(---\r?\n?)(.*)$", text, re.DOTALL)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3), match.group(4)


def _find_block_range(lines: list[str], key: str) -> tuple[int, int] | None:
    """
    Localiza o range [start, end) das linhas pertencentes ao bloco `key:` (linha do
    cabeçalho até a última linha de item `- ...` antes da próxima chave top-level).
    Retorna None se a chave não existir.
    """
    key_idx = -1
    for idx, line in enumerate(lines):
        if re.match(rf"^{re.escape(key)}:\s*(?:\[\s*\])?\s*(?:#.*)?$", line.strip()):
            key_idx = idx
            break
    if key_idx == -1:
        return None

    end_idx = key_idx + 1
    for idx in range(key_idx + 1, len(lines)):
        line = lines[idx]
        if re.match(r"^[ \t]+-", line):
            end_idx = idx + 1
        elif line.strip() == "" or line.strip().startswith("#"):
            continue
        elif re.match(r"^[a-zA-Z0-9_-]+:", line):
            break
        else:
            break
    return key_idx, end_idx


def _extract_block_items(lines: list[str], start: int, end: int) -> tuple[list[str], str]:
    items: list[str] = []
    indent = "  "
    for idx in range(start + 1, end):
        line = lines[idx]
        m = re.match(r"^([ \t]+)-\s*(.+?)\s*$", line)
        if not m:
            continue
        indent = m.group(1)
        value = m.group(2).strip().strip('"').strip("'")
        items.append(value)
    return items, indent


def migrate_frontmatter(frontmatter_text: str) -> tuple[str, list[str]] | None:
    """
    Sincroniza `source_docs:` e `source_docs_lazy:` conforme o limiar de 300 linhas (R-066):
    1. Move itens de `source_docs:` com _is_lazy(doc) == True (> 300 linhas) para `source_docs_lazy:`.
    2. Move itens de `source_docs_lazy:` com <= 300 linhas para `source_docs:`.
    Retorna (novo_frontmatter_text, itens_migrados) ou None se nada precisou mudar.
    """
    lines = frontmatter_text.splitlines(keepends=True)
    line_end = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"

    sd_range = _find_block_range(lines, "source_docs")
    lazy_range = _find_block_range(lines, "source_docs_lazy")

    if sd_range is None and lazy_range is None:
        return None

    sd_items, sd_indent = _extract_block_items(lines, *sd_range) if sd_range else ([], "  ")
    lazy_items, lazy_indent = _extract_block_items(lines, *lazy_range) if lazy_range else ([], "  ")
    indent = sd_indent if sd_range else lazy_indent

    to_lazy = [x for x in sd_items if _is_lazy(x)]
    to_full = [x for x in lazy_items if _should_migrate_to_full(x)]

    if not to_lazy and not to_full and not (lazy_range is not None and len(lazy_items) == 0):
        return None

    new_sd_items = [x for x in sd_items if x not in to_lazy]
    for x in to_full:
        if x not in new_sd_items:
            new_sd_items.append(x)

    new_lazy_items = [x for x in lazy_items if x not in to_full]
    for x in to_lazy:
        if x not in new_lazy_items:
            new_lazy_items.append(x)

    migrated = to_lazy + to_full

    # Atualiza os blocos preservando a posição original no frontmatter
    # Primeiro determina o ponto de inserção principal (onde source_docs ou source_docs_lazy iniciava)
    blocks_to_replace: list[tuple[int, int, str]] = []
    if sd_range:
        blocks_to_replace.append((sd_range[0], sd_range[1], "source_docs"))
    if lazy_range:
        blocks_to_replace.append((lazy_range[0], lazy_range[1], "source_docs_lazy"))
    blocks_to_replace.sort(key=lambda b: b[0])

    first_start = blocks_to_replace[0][0]
    # Remove os blocos antigos de trás para frente
    work_lines = list(lines)
    for b_start, b_end, _ in reversed(blocks_to_replace):
        del work_lines[b_start:b_end]

    # Ajusta first_start caso blocos anteriores tenham sido removidos (first_start é o menor índice, então permanece exato)
    replacement_lines: list[str] = []
    if new_sd_items:
        replacement_lines.append(f"source_docs:{line_end}")
        for item in new_sd_items:
            replacement_lines.append(f"{indent}- {item}{line_end}")
    if new_lazy_items:
        replacement_lines.append(f"source_docs_lazy:{line_end}")
        for item in new_lazy_items:
            replacement_lines.append(f"{indent}- {item}{line_end}")

    new_lines = work_lines[:first_start] + replacement_lines + work_lines[first_start:]
    new_fm_text = "".join(new_lines)
    if new_fm_text == frontmatter_text:
        return None
    return new_fm_text, migrated


def sync_lazy_source_docs(mode: str) -> tuple[SyncReport, int]:
    report = SyncReport()
    target_files = get_target_files()

    for tf in target_files:
        report.total_scanned += 1
        content = tf.read_text(encoding="utf-8")

        parts = split_frontmatter_and_body(content)
        if not parts:
            report.errors.append(f"{tf.name}: delimitadores frontmatter '---' não encontrados")
            continue

        open_delim, fm_text, close_delim, body = parts
        try:
            fm_data: Any = yaml.safe_load(fm_text) or {}
        except Exception as e:  # noqa: BLE001
            report.errors.append(f"{tf.name}: erro de parse no frontmatter YAML: {e}")
            continue

        if not isinstance(fm_data, dict):
            report.errors.append(f"{tf.name}: frontmatter YAML não é um mapeamento/dicionário")
            continue

        result = migrate_frontmatter(fm_text)
        if result is None:
            continue

        new_fm_text, migrated_items = result
        new_content = f"{open_delim}{new_fm_text}{close_delim}{body}"

        # Validação semântica em memória antes de qualquer ação
        try:
            new_fm_data = yaml.safe_load(new_fm_text)
            assert isinstance(new_fm_data, dict), "Frontmatter resultante inválido"
            for k, v in fm_data.items():
                if k not in ("source_docs", "source_docs_lazy"):
                    assert new_fm_data.get(k) == v, f"Campo {k} foi corrompido em {tf.name}"
        except Exception as e:  # noqa: BLE001
            report.errors.append(f"{tf.name}: validação de migração falhou: {e}")
            continue

        rel_path = str(tf.relative_to(REPO_ROOT))
        report.drifted.append(f"{rel_path} (sincronizado: {', '.join(migrated_items)})")

        if mode == "dry-run":
            diff = compute_unified_diff(content, new_content, tf.name)
            report.diffs.append(diff)
        elif mode == "apply":
            tf.write_text(new_content, encoding="utf-8")

            # R-051 Double-Check: reler do disco e revalidar
            re_read_text = tf.read_text(encoding="utf-8")
            re_parts = split_frontmatter_and_body(re_read_text)
            if not re_parts:
                report.errors.append(f"{tf.name}: R-051 falhou ao ler delimitadores após gravação")
                continue
            re_fm_data = yaml.safe_load(re_parts[1])
            if not isinstance(re_fm_data, dict):
                report.errors.append(f"{tf.name}: R-051 falhou na verificação pós-gravação")
                continue

            report.updated.append(rel_path)

    exit_code = report.compute_exit_code(mode)
    return report, exit_code


def main(args: list[str] | None = None) -> int:
    parser = create_sync_parser(__doc__)
    options = parse_sync_options(parser, args)

    report, exit_code = sync_lazy_source_docs(options.mode)
    report.print_summary("Progressive Disclosure Lazy Source Docs Sync (R-066)", options.mode)

    if options.is_check and report.has_drift:
        print("\nPara aplicar a sincronização canônica de source_docs / source_docs_lazy:, execute:")
        print("  python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
