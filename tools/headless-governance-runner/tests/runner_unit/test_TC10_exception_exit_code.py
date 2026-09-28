"""
TC-10: Mapeamento estrito de códigos de saída sob exceção não tratada (N2).

Cenário:
Simular uma exceção NÃO esperada (ex.: `RuntimeError` genérico) durante a
execução do `executar_agent_audit`. O `cli.py` (entrypoint) deve capturar isso
no nível mais externo e retornar um exit code não-zero explícito (2) SEM vazar
stack trace completo para stdout/stderr do CI (log estruturado, mensagem curta)
— nunca deixar o processo Python quebrar com traceback cru de 50 linhas no log.
"""

from __future__ import annotations

import pytest

from governance_runner.cli import COPILOT_SDK_TOKEN_ENV, main


class TestTC10ExceptionExitCode:
    """Testes para o caso de teste TC-10 (mapeamento estrito de exit code sob exceções)."""

    def test_deve_retornar_exit_code_2_sem_stack_trace_quando_excecao_inesperada_ocorrer(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        monkeypatch.setenv(COPILOT_SDK_TOKEN_ENV, "dummy-test-token")

        def _mock_executar_agent_audit(*args: object, **kwargs: object) -> object:
            raise RuntimeError("Falha critica inesperada de I/O no runner de governanca")

        monkeypatch.setattr(
            "governance_runner.cli.executar_agent_audit",
            _mock_executar_agent_audit,
        )
        monkeypatch.setattr(
            "governance_runner.cli.carregar_grafo",
            lambda *args, **kwargs: object(),
        )
        monkeypatch.setattr(
            "governance_runner.cli.criar_cliente_sdk_real",
            lambda *args, **kwargs: object(),
        )

        # Act
        exit_code = main(["--use-case", "agent-audit", "--base", "develop"])

        # Assert
        captured = capsys.readouterr()
        assert exit_code == 2

        # Mensagem estruturada curta no stderr
        assert "ERRO FATAL [governance-runner]: RuntimeError" in captured.err
        assert "Falha critica inesperada de I/O" in captured.err

        # Zero vazamento de stack trace longo no stdout ou stderr
        assert "Traceback (most recent call last)" not in captured.out
        assert "Traceback (most recent call last)" not in captured.err

    def test_deve_retornar_exit_code_2_quando_token_sdk_estiver_ausente(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        monkeypatch.delenv(COPILOT_SDK_TOKEN_ENV, raising=False)

        # Act
        exit_code = main(["--use-case", "agent-audit", "--base", "develop"])

        # Assert
        captured = capsys.readouterr()
        assert exit_code == 2
        assert f"ERRO: variavel de ambiente '{COPILOT_SDK_TOKEN_ENV}' ausente" in captured.err
        assert "Traceback (most recent call last)" not in captured.err

    def test_deve_retornar_exit_code_2_quando_caso_de_uso_for_desconhecido(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange: argparse rejeita choices inválidos com SystemExit (exit code 2)
        monkeypatch.setenv(COPILOT_SDK_TOKEN_ENV, "dummy-token")

        with pytest.raises(SystemExit) as exc_info:
            main(["--use-case", "caso-inexistente", "--base", "develop"])

        assert exc_info.value.code == 2
