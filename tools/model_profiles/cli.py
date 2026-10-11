"""CLI do gerador de perfis de modelos: list | status | apply | restore | suspend | resume | doctor | init."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable

from tools.model_profiles import apply, console, doctor, git, lock, restore, status, summary, suspend
from tools.model_profiles.errors import ModelProfilesError

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="model-profiles")
    parser.add_argument("--repo", help="raiz do repositorio (default: git toplevel do cwd)")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "status", "init"):
        sub.add_parser(name)
    ap = sub.add_parser("apply")
    ap.add_argument("profile")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    rp = sub.add_parser("restore")
    rp.add_argument("--force-line", action="store_true")
    rp.add_argument("--yes", action="store_true")
    sp = sub.add_parser("suspend")
    sp.add_argument("--yes", action="store_true")
    ep = sub.add_parser("resume")
    ep.add_argument("--force", action="store_true")
    ep.add_argument("--yes", action="store_true")
    dp = sub.add_parser("doctor")
    dp.add_argument("--repair", action="store_true")
    dp.add_argument("--yes", action="store_true")
    return parser


def _apply(repo: Path, args: argparse.Namespace) -> int:
    if args.dry_run:
        return apply.run_apply(repo, args.profile, True, args.yes)
    with lock.exclusive_lock(repo):
        return apply.run_apply(repo, args.profile, False, args.yes)


def _cancelled() -> int:
    console.say("operacao cancelada; nada foi gravado")
    return 1


def _restore(repo: Path, args: argparse.Namespace) -> int:
    if args.force_line and not summary.confirm_action(
            "--force-line sobrescreve a linha model: mesmo divergente da variante.", args.yes):
        return _cancelled()
    with lock.exclusive_lock(repo):
        return restore.run_restore(repo, args.force_line)


def _suspend(repo: Path, args: argparse.Namespace) -> int:
    with lock.exclusive_lock(repo):
        return suspend.run_suspend(repo, args.yes)


def _resume(repo: Path, args: argparse.Namespace) -> int:
    if args.force and not summary.confirm_action(
            "--force reaplica o perfil mesmo com o hash alterado desde o suspend.", args.yes):
        return _cancelled()
    with lock.exclusive_lock(repo):
        return suspend.run_resume(repo, args.force, args.yes)


def _doctor(repo: Path, args: argparse.Namespace) -> int:
    if args.repair and not summary.confirm_action(
            "--repair reverte arquivos do journal e remove lock obsoleto.", args.yes):
        return _cancelled()
    return doctor.run_doctor(repo, args.repair)


HANDLERS: dict[str, Callable[[Path, argparse.Namespace], int]] = {
    "list": lambda repo, a: status.run_list(repo),
    "status": lambda repo, a: status.run_status(repo),
    "init": lambda repo, a: status.run_init(repo),
    "apply": _apply,
    "restore": _restore,
    "suspend": _suspend,
    "resume": _resume,
    "doctor": _doctor,
}


def _parse(argv: list[str]) -> argparse.Namespace | int:
    try:
        return build_parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)


def main(argv: list[str]) -> int:
    args = _parse(argv)
    if isinstance(args, int):
        return args
    try:
        repo = git.require_root(Path(args.repo)) if args.repo else git.toplevel(Path.cwd())
        return HANDLERS[args.command](repo, args)
    except ModelProfilesError as exc:
        console.fail(f"[{exc.code}] {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001 - nunca lancar Exception ao usuario
        logger.exception("erro inesperado")
        console.fail(f"[ERROR] {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
