"""Testes do CLI governance-runner: modos synth-* e nao-regressao de agent-audit."""
from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner import cli
from governance_runner.synth import exporter


@pytest.fixture(autouse=True)
def _sem_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(cli.COPILOT_SDK_TOKEN_ENV, raising=False)
    monkeypatch.delenv("GOV_MAX_PREMIUM_REQUESTS", raising=False)


@pytest.fixture
def db(tmp_path: Path) -> str:
    return str(tmp_path / "cli.db")


@pytest.fixture
def allow_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    raiz = tmp_path / "synthetic"
    monkeypatch.setattr(exporter, "_allow_root_padrao", lambda: raiz)
    return raiz


def test_parser_aceita_todos_os_use_cases() -> None:
    parser = cli.construir_parser()
    for uc in ("agent-audit", "synth-generate", "synth-eval", "synth-export", "synth-promote"):
        assert parser.parse_args(["--use-case", uc]).use_case == uc


def test_parser_defaults_synth() -> None:
    args = cli.construir_parser().parse_args(["--use-case", "synth-generate"])
    assert args.generator_mode == "template" and args.max_premium_requests is None
    assert args.only_failures is True and args.confirm is False and args.per_stratum == 2


def test_synth_eval_sem_max_premium_requests_exit_2(db: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["--use-case", "synth-eval", "--db", db]) == 2
    assert "ERRO" in capsys.readouterr().err


def test_synth_generate_sdk_sem_max_premium_requests_exit_2(db: str) -> None:
    assert cli.main(["--use-case", "synth-generate", "--generator-mode", "sdk", "--db", db]) == 2


@pytest.mark.parametrize("valor", ["0", "-3", "abc"])
def test_synth_eval_teto_invalido_exit_2(db: str, valor: str) -> None:
    assert cli.main(["--use-case", "synth-eval", "--db", db, "--max-premium-requests", valor]) == 2


def test_synth_eval_sem_token_exit_2(db: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["--use-case", "synth-eval", "--db", db, "--max-premium-requests", "3"]) == 2
    assert cli.COPILOT_SDK_TOKEN_ENV in capsys.readouterr().err


def test_synth_generate_template_offline_exit_0(db: str, capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli.main(["--use-case", "synth-generate", "--db", db, "--per-stratum", "1",
                   "--dimensions", "distrator_outro_agente"])
    assert rc == 0
    assert "synth-generate" in capsys.readouterr().out


def test_synth_generate_dry_run_nao_cria_prompts(db: str) -> None:
    from governance_runner.synth.storage import SynthRepository

    assert cli.main(["--use-case", "synth-generate", "--db", db, "--dry-run", "--per-stratum", "1",
                     "--dimensions", "distrator_outro_agente"]) == 0
    with SynthRepository(db) as repo:
        assert repo.listar_prompts() == []


def test_synth_export_sem_eval_run_id_exit_2(db: str) -> None:
    assert cli.main(["--use-case", "synth-export", "--db", db]) == 2


def test_synth_export_gera_silver_em_allow_root(db: str, allow_root: Path) -> None:
    assert cli.main(["--use-case", "synth-export", "--db", db, "--eval-run-id", "inexistente"]) == 0
    assert list(allow_root.glob("casos-roteamento-silver-*.yaml"))


@pytest.mark.parametrize("args", [[], ["--silver", "x.yaml"], ["--run-id", "r"]])
def test_synth_promote_sem_argumentos_obrigatorios_exit_2(args: list[str]) -> None:
    assert cli.main(["--use-case", "synth-promote", *args]) == 2


@pytest.mark.parametrize(
    "silver", ["../casos-roteamento-silver-x.yaml", "casos-roteamento.yaml", "promoted-a.yaml"]
)
def test_synth_promote_path_invalido_exit_2(allow_root: Path, silver: str) -> None:
    assert cli.main(["--use-case", "synth-promote", "--silver", silver, "--run-id", "r", "--confirm"]) == 2


def test_agent_audit_sem_base_exit_2() -> None:
    assert cli.main(["--use-case", "agent-audit"]) == 2


def test_agent_audit_sem_token_exit_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["--use-case", "agent-audit", "--base", "main"]) == 2
    assert cli.COPILOT_SDK_TOKEN_ENV in capsys.readouterr().err
