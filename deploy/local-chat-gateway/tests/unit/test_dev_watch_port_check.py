"""Testes unitários de `dev_watch._porta_ocupada` e do fail-fast de `main()`.

Bug real investigado (2026-10-04): reexecuções rápidas de `dev_watch.py`
falhavam com um traceback cru do `OSError`/`[WinError 10048]` do próprio
uvicorn quando a porta já estava em uso, sem nenhuma orientação de como
liberá-la.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_GATEWAY_ROOT = Path(__file__).resolve().parents[2]
if str(_GATEWAY_ROOT) not in sys.path:
    sys.path.insert(0, str(_GATEWAY_ROOT))

import dev_watch  # noqa: E402


class TestPortaOcupada:
    def test_deve_considerar_porta_ocupada_quando_ja_vinculada(self) -> None:
        # Arrange: ocupa uma porta efêmera real antes de checar.
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(("127.0.0.1", 0))
        servidor.listen(1)
        porta = servidor.getsockname()[1]

        try:
            # Act & Assert
            assert dev_watch._porta_ocupada("127.0.0.1", porta) is True
        finally:
            servidor.close()

    def test_deve_considerar_porta_livre_quando_nao_vinculada(self) -> None:
        # Arrange: obtém uma porta efêmera livre e a libera imediatamente.
        sonda = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sonda.bind(("127.0.0.1", 0))
        porta = sonda.getsockname()[1]
        sonda.close()

        # Act & Assert
        assert dev_watch._porta_ocupada("127.0.0.1", porta) is False


class TestMainFailFastPortaOcupada:
    def test_main_falha_fast_com_mensagem_clara_quando_porta_ocupada(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange: evita qualquer efeito colateral real de bootstrap/rede.
        monkeypatch.setattr(sys, "argv", ["dev_watch.py", "--no-bootstrap"])
        monkeypatch.setattr(dev_watch, "_venv_python_path", lambda: Path("fake-python"))
        monkeypatch.setattr(
            dev_watch.Path, "exists", lambda self: False, raising=False
        )
        monkeypatch.setattr(dev_watch, "_garantir_dot_env", MagicMock())
        monkeypatch.setattr(dev_watch, "_resolver_env_local", MagicMock())
        monkeypatch.setattr(dev_watch, "_verificar_secret_token", MagicMock())
        monkeypatch.setattr(dev_watch, "_validar_pre_requisitos", MagicMock())
        monkeypatch.setattr(dev_watch, "_porta_ocupada", lambda host, port: True)

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            dev_watch.main()
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "ja esta em uso" in captured.err
