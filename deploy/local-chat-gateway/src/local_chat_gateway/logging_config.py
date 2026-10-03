"""logging_config — RotatingFileHandler em ADICAO ao stdout (nunca substitui).

Gap de observabilidade investigado em 2026-10-04: `logging.getLogger(__name__)`
e usado em varios modulos (`agent_catalog.py`, `auth.py`,
`governance_pipeline.py`, `permission_policy.py`, `projects_catalog.py`,
`prompts_catalog.py`, `sdk_session.py`, `telemetry.py`, `turn_recorder.py`,
`api/routes.py`), mas nenhum handler de arquivo era configurado -- logs
dependiam 100% do handler default do uvicorn (stdout), perdidos ao fechar o
terminal/sessao de dev_watch.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_FORMATO = "%(asctime)s %(levelname)s %(name)s: %(message)s"

#: Estado de modulo global -- garante idempotencia (`configurar_logging`
#: pode ser chamado mais de uma vez, ex.: reload do uvicorn, sem duplicar o
#: `RotatingFileHandler` no root logger).
_CONFIGURADO = False


def configurar_logging(
    log_file: str | Path,
    *,
    max_bytes: int = 5_242_880,
    backup_count: int = 3,
    level: int = logging.INFO,
) -> None:
    """Adiciona um `RotatingFileHandler` ao root logger (idempotente, aditivo).

    Nunca remove/substitui handlers ja existentes no root logger (ex.: o
    `StreamHandler` default do uvicorn) -- apenas adiciona o novo handler de
    arquivo, preservando o stdout.

    Args:
        log_file: Caminho do arquivo de log (diretorio-pai criado se ausente).
        max_bytes: Tamanho maximo do arquivo antes de rotacionar.
        backup_count: Quantidade de arquivos de backup rotacionados mantidos.
        level: Nivel minimo de log capturado pelo handler de arquivo.
    """
    global _CONFIGURADO
    if _CONFIGURADO:
        return

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        str(log_path), maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(_FORMATO))
    handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    if root_logger.level > level or root_logger.level == logging.NOTSET:
        root_logger.setLevel(level)

    _CONFIGURADO = True
