"""Testes unitários de `logging_config.configurar_logging` (Fix 3, 2026-10-04).

Gap de observabilidade: logs dependiam 100% do stdout do uvicorn, perdidos ao
fechar o terminal/sessão de `dev_watch.py`. `configurar_logging` adiciona um
`RotatingFileHandler` ADITIVO (nunca remove/substitui handlers existentes).

Nota de isolamento (R-059): `_CONFIGURADO` é estado de módulo global -- a
fixture `reset_logging_config` reseta o flag e limpa handlers do root logger
antes/depois de cada teste para evitar vazamento entre testes.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pytest

from local_chat_gateway import logging_config
from local_chat_gateway.logging_config import configurar_logging


@pytest.fixture(autouse=True)
def reset_logging_config() -> None:
    logging_config._CONFIGURADO = False
    root_logger = logging.getLogger()
    handlers_originais = list(root_logger.handlers)
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)
    yield
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)
    for h in handlers_originais:
        root_logger.addHandler(h)
    logging_config._CONFIGURADO = False


class TestConfigurarLogging:
    def test_configurar_logging_cria_diretorio_pai_se_ausente(
        self, tmp_path: Path
    ) -> None:
        log_file = tmp_path / "sub" / "gateway.log"
        assert not log_file.parent.exists()

        configurar_logging(log_file)

        assert log_file.parent.exists()

    def test_configurar_logging_adiciona_handler_sem_remover_stream_handler_existente(
        self, tmp_path: Path
    ) -> None:
        root_logger = logging.getLogger()
        stream_handler = logging.StreamHandler()
        root_logger.addHandler(stream_handler)

        configurar_logging(tmp_path / "gateway.log")

        assert stream_handler in root_logger.handlers
        assert any(
            isinstance(h, logging.handlers.RotatingFileHandler)
            for h in root_logger.handlers
        )

    def test_configurar_logging_e_idempotente_nao_duplica_handler(
        self, tmp_path: Path
    ) -> None:
        log_file = tmp_path / "gateway.log"

        configurar_logging(log_file)
        configurar_logging(log_file)

        root_logger = logging.getLogger()
        handlers_arquivo = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(handlers_arquivo) == 1

    def test_configurar_logging_formato_inclui_timestamp_nivel_modulo(
        self, tmp_path: Path
    ) -> None:
        log_file = tmp_path / "gateway.log"
        configurar_logging(log_file)

        logging.getLogger("local_chat_gateway.x").info("teste")
        for h in logging.getLogger().handlers:
            h.flush()

        conteudo = log_file.read_text(encoding="utf-8")
        assert re.search(
            r"\d{4}-\d{2}-\d{2}.*INFO.*local_chat_gateway\.x.*teste", conteudo
        )

    def test_configurar_logging_respeita_max_bytes_e_backup_count(
        self, tmp_path: Path
    ) -> None:
        log_file = tmp_path / "gateway.log"
        configurar_logging(log_file, max_bytes=1234, backup_count=7)

        handler = next(
            h
            for h in logging.getLogger().handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        )
        assert handler.maxBytes == 1234
        assert handler.backupCount == 7
