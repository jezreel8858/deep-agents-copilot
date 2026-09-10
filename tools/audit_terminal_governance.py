#!/usr/bin/env python3
"""
audit_terminal_governance.py — Auditoria e Sincronização de Governança para Terminal Governance.

Objetivo:
Garantir que toda definição de agent (*.agent.md), prompt (*.prompt.md) e entrada de catálogo
(catalog.yaml e sub-catálogos de domínio) que declare a ferramenta 'run_in_terminal' em 'tools'
possua a referência obrigatória '.github/skills/terminal-governance/SKILL.md' em 'source_docs'.

Premissas e Regras:
- R-015 / R-040: Sincronização atômica de definições e integridade referencial.
- R-046: Single-Turn Batching e diffs cirúrgicos mínimos preservando formatação existente.
- Idempotência estrita: execuções repetidas não duplicam referências.
- Condicionalidade: arquivos sem 'run_in_terminal' permanecem 100% inalterados.

Uso:
    python tools/audit_terminal_governance.py --dry-run
    python tools/audit_terminal_governance.py --apply
"""
from __future__ import annotations

import argparse
import difflib
import glob
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

try:
    import yaml
except ImportError:
    yaml = None
    print("ERRO: PyYAML é obrigatório. Instale com 'pip install pyyaml'.", file=sys.stderr)
    sys.exit(1)

TARGET_SKILL = ".github/skills/terminal-governance/SKILL.md"


class ItemReport(NamedTuple):
    file_path: str
    target_type: str  # 'agent', 'prompt', 'catalog'
    status: str       # 'UPDATED', 'CONFORMING', 'IGNORED_NO_TERMINAL', 'NO_FRONTMATTER'
    details: str
    diff: str = ""


def clean_doc_entry(doc: any) -> str:
    """Normaliza caminhos declarados em source_docs removendo aspas e espaços."""
    return str(doc).strip().strip('"').strip("'")


def audit_and_update_markdown(file_path: Path, target_type: str, dry_run: bool = True) -> ItemReport:
    """Processa cirurgicamente arquivos Markdown frontmatter (*.agent.md e *.prompt.md)."""
    raw_content = file_path.read_text(encoding="utf-8")
    rel_path = file_path.as_posix()

    if not raw_content.startswith("---"):
        return ItemReport(rel_path, target_type, "NO_FRONTMATTER", "Sem bloco frontmatter inicial")

    parts = raw_content.split("---", 2)
    if len(parts) < 3:
        return ItemReport(rel_path, target_type, "NO_FRONTMATTER", "Frontmatter malformado (delimitadores insuficientes)")

    fm_raw = parts[1]
    body = parts[2]

    try:
        data = yaml.safe_load(fm_raw)
    except Exception as e:
        return ItemReport(rel_path, target_type, "NO_FRONTMATTER", f"Erro de sintaxe YAML: {e}")

    if not isinstance(data, dict):
        return ItemReport(rel_path, target_type, "NO_FRONTMATTER", "Frontmatter não é um dicionário YAML")

    tools = data.get("tools", [])
    if isinstance(tools, str):
        tools = [tools]
    elif not isinstance(tools, list):
        tools = []

    if "run_in_terminal" not in tools:
        return ItemReport(rel_path, target_type, "IGNORED_NO_TERMINAL", "Ferramenta 'run_in_terminal' ausente em tools")

    source_docs = data.get("source_docs", []) or []
    if isinstance(source_docs, str):
        source_docs = [source_docs]
    elif not isinstance(source_docs, list):
        source_docs = []

    cleaned_docs = [clean_doc_entry(d) for d in source_docs]
    if TARGET_SKILL in cleaned_docs:
        return ItemReport(rel_path, target_type, "CONFORMING", f"Já referencia '{TARGET_SKILL}' em source_docs")

    # Inserção cirúrgica na seção source_docs preservando comentários e identação
    fm_lines = fm_raw.splitlines(keepends=True)
    sd_idx = -1
    indent = "  "

    for idx, line in enumerate(fm_lines):
        m = re.match(r"^(\s*)source_docs:\s*(.*)$", line)
        if m:
            sd_idx = idx
            break

    if sd_idx != -1:
        last_item_idx = sd_idx
        for j in range(sd_idx + 1, len(fm_lines)):
            line = fm_lines[j]
            m_item = re.match(r"^(\s*)-\s+", line)
            if m_item:
                last_item_idx = j
                indent = m_item.group(1)
            elif re.match(r"^\s*$", line):
                continue
            elif re.match(r"^[a-zA-Z0-9_-]+:", line):
                break

        new_line = f"{indent}- {TARGET_SKILL}\n"
        fm_lines.insert(last_item_idx + 1, new_line)
    else:
        new_entry = f"source_docs:\n  - {TARGET_SKILL}\n"
        fm_lines.append(new_entry)

    new_content = f"---{''.join(fm_lines)}---{body}"

    diff = "".join(
        difflib.unified_diff(
            raw_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
            n=3,
        )
    )

    if not dry_run:
        file_path.write_text(new_content, encoding="utf-8")

    return ItemReport(rel_path, target_type, "UPDATED", f"Adicionada referência a {TARGET_SKILL}", diff)


def audit_and_update_catalog(file_path: Path, dry_run: bool = True) -> list[ItemReport]:
    """Processa arquivos de catálogo YAML (*catalog*.yaml)."""
    raw_content = file_path.read_text(encoding="utf-8")
    rel_path = file_path.as_posix()

    try:
        data = yaml.safe_load(raw_content)
    except Exception as e:
        return [ItemReport(rel_path, "catalog", "NO_FRONTMATTER", f"Erro de sintaxe YAML: {e}")]

    if not isinstance(data, dict):
        return [ItemReport(rel_path, "catalog", "NO_FRONTMATTER", "Conteúdo do catálogo não é dicionário")]

    agents = data.get("agents", {})
    if not isinstance(agents, dict):
        return [ItemReport(rel_path, "catalog", "IGNORED_NO_TERMINAL", "Catálogo sem dicionário 'agents'")]

    reports: list[ItemReport] = []
    lines = raw_content.splitlines(keepends=True)
    file_modified = False

    for agent_id, agent_data in agents.items():
        if not isinstance(agent_data, dict):
            continue

        tools = agent_data.get("tools", [])
        if not isinstance(tools, list) or "run_in_terminal" not in tools:
            reports.append(ItemReport(f"{rel_path}#{agent_id}", "catalog", "IGNORED_NO_TERMINAL", "Sem run_in_terminal em tools"))
            continue

        source_docs = agent_data.get("source_docs")
        if source_docs is None:
            # Sub-catálogos locais seguem §11.2 de governance-factory-patterns (usam 'skills:', sem 'source_docs:')
            reports.append(
                ItemReport(
                    f"{rel_path}#{agent_id}",
                    "catalog",
                    "CONFORMING",
                    "Declara run_in_terminal; sub-catálogo local isolado sem campo source_docs",
                )
            )
            continue

        cleaned_docs = [clean_doc_entry(d) for d in source_docs]
        if TARGET_SKILL in cleaned_docs:
            reports.append(
                ItemReport(
                    f"{rel_path}#{agent_id}",
                    "catalog",
                    "CONFORMING",
                    f"Já referencia '{TARGET_SKILL}' em source_docs",
                )
            )
            continue

        # Inserção cirúrgica de source_docs para este agent no YAML
        agent_pattern = re.compile(rf"^  {re.escape(agent_id)}:\s*$")
        agent_idx = -1
        for idx, line in enumerate(lines):
            if agent_pattern.match(line):
                agent_idx = idx
                break

        if agent_idx == -1:
            continue

        next_agent_idx = len(lines)
        for j in range(agent_idx + 1, len(lines)):
            if re.match(r"^  [a-zA-Z0-9_-]+:\s*$", lines[j]) or re.match(r"^[a-zA-Z0-9_-]+:", lines[j]):
                next_agent_idx = j
                break

        sd_idx = -1
        for j in range(agent_idx, next_agent_idx):
            if re.match(r"^\s+source_docs:\s*$", lines[j]):
                sd_idx = j
                break

        if sd_idx != -1:
            last_item_idx = sd_idx
            indent = "      "
            for j in range(sd_idx + 1, next_agent_idx):
                m_item = re.match(r"^(\s+)-\s+", lines[j])
                if m_item:
                    last_item_idx = j
                    indent = m_item.group(1)
                elif re.match(r"^\s*$", lines[j]):
                    continue
                else:
                    break

            new_line = f'{indent}- "{TARGET_SKILL}"\n'
            lines.insert(last_item_idx + 1, new_line)
            file_modified = True
            reports.append(
                ItemReport(
                    f"{rel_path}#{agent_id}",
                    "catalog",
                    "UPDATED",
                    f"Adicionado {TARGET_SKILL} ao source_docs do agent '{agent_id}'",
                )
            )

    if file_modified:
        new_content = "".join(lines)
        diff = "".join(
            difflib.unified_diff(
                raw_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{rel_path}",
                tofile=f"b/{rel_path}",
                n=3,
            )
        )
        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")
        # Anexa diff ao primeiro report alterado
        for idx, r in enumerate(reports):
            if r.status == "UPDATED" and not r.diff:
                reports[idx] = ItemReport(r.file_path, r.target_type, r.status, r.details, diff)
                break

    return reports


def run_audit(workspace_dir: Path, dry_run: bool = True) -> list[ItemReport]:
    """Executa a varredura e auditoria completa no repositório."""
    all_reports: list[ItemReport] = []

    # 1. Agents (*.agent.md)
    agent_paths = sorted(workspace_dir.glob(".github/agents/**/*.agent.md"))
    for path in agent_paths:
        all_reports.append(audit_and_update_markdown(path, "agent", dry_run=dry_run))

    # 2. Prompts (*.prompt.md)
    prompt_paths = sorted(workspace_dir.glob(".github/prompts/**/*.prompt.md"))
    for path in prompt_paths:
        all_reports.append(audit_and_update_markdown(path, "prompt", dry_run=dry_run))

    # 3. Catálogos (*catalog*.yaml em .github/agents/**)
    catalog_paths = sorted(workspace_dir.glob(".github/agents/**/*catalog*.yaml"))
    for path in catalog_paths:
        all_reports.extend(audit_and_update_catalog(path, dry_run=dry_run))

    return all_reports


def format_report(reports: list[ItemReport], dry_run: bool, workspace_dir: Path) -> str:
    """Formata relatório de auditoria e execução em formato estruturado."""
    updated = [r for r in reports if r.status == "UPDATED"]
    conforming = [r for r in reports if r.status == "CONFORMING"]
    ignored = [r for r in reports if r.status == "IGNORED_NO_TERMINAL"]
    errors = [r for r in reports if r.status == "NO_FRONTMATTER"]

    output = []
    output.append("=" * 80)
    output.append(f"RELATÓRIO DE AUDITORIA E SINCRONIZAÇÃO: TERMINAL-GOVERNANCE")
    output.append(f"Modo: {'DRY-RUN (Simulação)' if dry_run else 'APPLY (Execução Real)'}")
    output.append(f"Workspace: {workspace_dir.resolve().as_posix()}")
    output.append(f"Skill Referenciada: {TARGET_SKILL}")
    output.append("=" * 80)
    output.append("")
    output.append(f"MÉTRICAS GERAIS:")
    output.append(f"  Total de Itens Auditados:     {len(reports)}")
    output.append(f"  Itens a Atualizar / Alterados: {len(updated)}")
    output.append(f"  Itens Já Conformes:           {len(conforming)}")
    output.append(f"  Itens Ignorados (sem tool):   {len(ignored)}")
    output.append(f"  Erros / Sintaxe Inválida:     {len(errors)}")
    output.append("")

    if updated:
        output.append("-" * 80)
        output.append(f"1. ARQUIVOS/ITENS ALTERADOS ({len(updated)}):")
        output.append("-" * 80)
        for r in updated:
            rel = os.path.relpath(r.file_path, workspace_dir.as_posix()) if os.path.exists(r.file_path) else r.file_path
            output.append(f"  [+] [{r.target_type.upper()}] {rel} -> {r.details}")
        output.append("")

    if conforming:
        output.append("-" * 80)
        output.append(f"2. ARQUIVOS/ITENS JÁ CONFORMES ({len(conforming)}):")
        output.append("-" * 80)
        for r in conforming:
            rel = os.path.relpath(r.file_path, workspace_dir.as_posix()) if os.path.exists(r.file_path) else r.file_path
            output.append(f"  [OK] [{r.target_type.upper()}] {rel} -> {r.details}")
        output.append("")

    if ignored:
        output.append("-" * 80)
        output.append(f"3. ARQUIVOS/ITENS IGNORADOS (Sem 'run_in_terminal') ({len(ignored)}):")
        output.append("-" * 80)
        for r in ignored:
            rel = os.path.relpath(r.file_path, workspace_dir.as_posix()) if os.path.exists(r.file_path) else r.file_path
            output.append(f"  [-] [{r.target_type.upper()}] {rel}")
        output.append("")

    if updated and any(r.diff for r in updated):
        output.append("-" * 80)
        output.append("4. DIFFS CIRÚRGICOS GERADOS:")
        output.append("-" * 80)
        for r in updated:
            if r.diff:
                output.append(f"--- Diff para: {r.file_path} ---")
                output.append(r.diff)
                output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Auditoria e Sincronização de 'terminal-governance' em source_docs para agents, prompts e catálogos."
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Caminho raiz do repositório workspace (padrão: raiz relativa ao script)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Executa auditoria em modo dry-run sem gravar arquivos no disco (padrão)",
    )
    group.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as modificações cirúrgicas diretamente nos arquivos do repositório",
    )

    args = parser.parse_args()
    dry_run = not args.apply

    workspace_dir = args.workspace.resolve()
    if not workspace_dir.exists():
        print(f"ERRO: Diretório workspace não encontrado: {workspace_dir}", file=sys.stderr)
        sys.exit(1)

    reports = run_audit(workspace_dir, dry_run=dry_run)
    report_text = format_report(reports, dry_run=dry_run, workspace_dir=workspace_dir)
    print(report_text)


if __name__ == "__main__":
    main()

