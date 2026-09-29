"""
Governance Sync Core Toolkit (R-051 / R-040 / R-059).

Fornece o núcleo fino e desacoplado para scripts de sincronização de governança:
- Parser padronizado de flags CLI (--check, --dry-run, --apply).
- Gerenciamento de ciclo de vida e cálculo de exit codes padronizados.
- Utilitários de diff cirúrgico unificado e formatação de relatórios.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


@dataclass
class SyncOptions:
    mode: str  # "check", "dry-run", "apply"

    @property
    def is_check(self) -> bool:
        return self.mode == "check"

    @property
    def is_dry_run(self) -> bool:
        return self.mode == "dry-run"

    @property
    def is_apply(self) -> bool:
        return self.mode == "apply"


@dataclass
class SyncReport:
    total_scanned: int = 0
    drifted: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    diffs: list[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return len(self.drifted) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def compute_exit_code(self, mode: str) -> int:
        if mode == "check":
            return 1 if (self.has_drift or self.has_errors) else 0
        if mode == "apply":
            return 1 if self.has_errors else 0
        return 0

    def print_summary(self, title: str, mode: str) -> None:
        print(f"=== {title} ===")
        print(f"Modo de execução: {mode}")
        print(f"Total de artefatos auditados: {self.total_scanned}")
        print(f"Drift detectado: {len(self.drifted)}")
        if self.drifted:
            for item in self.drifted:
                print(f"  - [DRIFT] {item}")
        if self.updated:
            print(f"Artefatos atualizados em disco: {len(self.updated)}")
            for item in self.updated:
                print(f"  - [ATUALIZADO] {item}")
        if self.errors:
            print(f"Erros de validação ({len(self.errors)}):")
            for err in self.errors:
                print(f"  - [ERRO] {err}")
        if mode == "dry-run" and self.diffs:
            print("\nDiffs calculados:")
            for d in self.diffs:
                print(d)


def create_sync_parser(description: str, default_mode: str = "check") -> argparse.ArgumentParser:
    """Cria o parser com as flags canônicas de governança: --apply, --dry-run e --check."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as correções de sincronização diretamente nos arquivos em disco.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula as alterações e exibe os diffs sem gravar nada em disco.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Modo CI fail-safe: retorna exit code 1 se houver drift, sem alterar arquivos.",
    )
    return parser


def parse_sync_options(parser: argparse.ArgumentParser, args: Sequence[str] | None = None) -> SyncOptions:
    """Extrai SyncOptions garantindo que o default (sem flags) seja fail-safe --check."""
    parsed = parser.parse_args(args)
    if parsed.apply:
        return SyncOptions(mode="apply")
    if parsed.dry_run:
        return SyncOptions(mode="dry-run")
    return SyncOptions(mode="check")


def compute_unified_diff(original: str, modified: str, filename: str) -> str:
    """Gera representação unified diff entre duas strings."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff)
