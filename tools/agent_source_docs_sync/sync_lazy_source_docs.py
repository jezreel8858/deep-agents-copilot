"""
Migra determinística e atomicamente CLAUDE.md / .github/copilot-instructions.md
(e qualquer doc > LAZY_LINE_THRESHOLD linhas) da chave `source_docs:` para a nova
chave `source_docs_lazy:` em todos os artefatos de governança (.agent.md, SKILL.md,
*.prompt.md), conforme R-066 (Progressive Disclosure Compulsória).

Motivação e Decisão Técnica (R-066 / Smell 2.31 / docs/implementation-plans/
20261003-governance-maintenance-progressive-disclosure-source-docs.md):
    - CLAUDE.md (~353 linhas) e .github/copilot-instructions.md (~465 linhas) eram
      declarados em `source_docs:` (full-load) de ~79/75 artefatos respectivamente,
      inflando o contexto inicial de cada spawn de agent em dezenas de milhares de
      tokens antes de qualquer trabalho útil começar.
    - Esta migração move essas entradas para `source_docs_lazy:`, sinalizando que o
      consumo correto é via `context-mode/ctx_search` sob demanda, nunca `read_file`
      integral (ver R-066(c) em CLAUDE.md para a ressalva de enforcement
      textual/CI-estático, não mecânico-runtime).
    - Preservação Estrita de Formatação: segue o mesmo padrão cirúrgico de
      `sync_required_source_docs.py` — nunca re-dump completo do YAML.

Escopo de arquivos:
    - .github/agents/**/*.agent.md (exclui templates/)
    - .github/skills/**/SKILL.md
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

# Allowlist fixa de docs sempre classificados como lazy (alto fan-in, alto custo de
# contexto inicial), independente de contagem de linhas. Escopo R-066 restrito a
# documentação normativa CENTRAL (CLAUDE.md/copilot-instructions.md/workflows.md) —
# NÃO inclui skills operacionais mandatoriamente exigidas em source_docs (full) por
# outras regras (ex. handoff-governance/agent-contracts via R-042; terminal-governance
# via R-049), mesmo que excedam 300 linhas. Expandir este escopo é um ciclo de
# governança separado (ver docs/implementation-plans/..., §0.3).
LAZY_ALLOWLIST = {
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/agents/workflows.md",
}


def _is_lazy(doc_path: str) -> bool:
    """Classifica um doc como lazy via allowlist fixa (escopo R-066 desta rodada)."""
    return doc_path in LAZY_ALLOWLIST

# Diretórios varridos nesta migração (R-066 / Smell 2.31).
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
        if re.match(rf"^{re.escape(key)}:\s*(?:#.*)?$", line.strip()):
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


def migrate_frontmatter(frontmatter_text: str) -> tuple[str, list[str]] | None:
    """
    Remove entradas lazy (allowlist) de `source_docs:` e as move para `source_docs_lazy:`.
    Retorna (novo_frontmatter_text, itens_migrados) ou None se nada precisou mudar.
    """
    lines = frontmatter_text.splitlines(keepends=True)
    line_end = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"

    source_docs_range = _find_block_range(lines, "source_docs")
    if source_docs_range is None:
        return None

    start, end = source_docs_range
    migrated: list[str] = []
    kept_items: list[str] = []
    indent = "  "

    for idx in range(start + 1, end):
        line = lines[idx]
        m = re.match(r"^([ \t]+)-\s*(.+?)\s*$", line)
        if not m:
            continue
        indent = m.group(1)
        value = m.group(2).strip().strip('"').strip("'")
        if _is_lazy(value):
            migrated.append(value)
        else:
            kept_items.append(value)

    if not migrated:
        return None

    # Reconstrói o bloco source_docs (cabeçalho + itens remanescentes, ou remove a
    # chave inteiramente se não sobrar nenhum item).
    if kept_items:
        new_source_docs_block = [f"source_docs:{line_end}"] + [
            f"{indent}- {item}{line_end}" for item in kept_items
        ]
    else:
        new_source_docs_block = []

    new_lines = lines[:start] + new_source_docs_block + lines[end:]

    # Localiza (ou cria) o bloco source_docs_lazy: logo após o novo bloco source_docs
    # (ou no ponto onde source_docs estava, se foi removido).
    insertion_point = start + len(new_source_docs_block)
    lazy_range = _find_block_range(new_lines, "source_docs_lazy")

    if lazy_range is not None:
        lz_start, lz_end = lazy_range
        existing_lazy: list[str] = []
        for idx in range(lz_start + 1, lz_end):
            m = re.match(r"^[ \t]+-\s*(.+?)\s*$", new_lines[idx])
            if m:
                existing_lazy.append(m.group(1).strip().strip('"').strip("'"))
        to_add = [item for item in migrated if item not in existing_lazy]
        if to_add:
            add_lines = [f"{indent}- {item}{line_end}" for item in to_add]
            new_lines = new_lines[:lz_end] + add_lines + new_lines[lz_end:]
    else:
        lazy_block = [f"source_docs_lazy:{line_end}"] + [
            f"{indent}- {item}{line_end}" for item in migrated
        ]
        new_lines = (
            new_lines[:insertion_point] + lazy_block + new_lines[insertion_point:]
        )

    return "".join(new_lines), migrated


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
            new_lazy = new_fm_data.get("source_docs_lazy", []) or []
            for item in migrated_items:
                assert item in new_lazy, f"{item} não migrado corretamente para source_docs_lazy"
            new_full = new_fm_data.get("source_docs", []) or []
            for item in migrated_items:
                assert item not in new_full, f"{item} ainda presente em source_docs (full)"
            # Garantir integridade de todos os outros campos
            for k, v in fm_data.items():
                if k not in ("source_docs", "source_docs_lazy"):
                    assert new_fm_data.get(k) == v, f"Campo {k} foi corrompido em {tf.name}"
        except Exception as e:  # noqa: BLE001
            report.errors.append(f"{tf.name}: validação de migração falhou: {e}")
            continue

        rel_path = str(tf.relative_to(REPO_ROOT))
        report.drifted.append(f"{rel_path} (migrando para lazy: {', '.join(migrated_items)})")

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
            re_lazy = re_fm_data.get("source_docs_lazy", []) or []
            if not all(item in re_lazy for item in migrated_items):
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
        print("\nPara aplicar a migração canônica de source_docs_lazy:, execute:")
        print("  python tools/agent_source_docs_sync/sync_lazy_source_docs.py --apply")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

