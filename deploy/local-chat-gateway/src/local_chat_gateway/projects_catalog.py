"""projects_catalog — descoberta automatica de projetos via `projects.local.yaml`.

Le o overlay local de projetos (R-043 -- `path_externo` por projeto,
formato Windows OU POSIX indiferente) e traduz cada path de HOST para o
path correspondente DENTRO do container do gateway.

Premissa de design (documentada explicitamente para o operador local):
TODOS os projetos registrados devem viver sob um UNICO diretorio-pai comum
no host (ex.: `D:\\workspace`), montado UMA UNICA VEZ em `/workspaces` via
`PROJECTS_ROOT_PATH` (`docker-compose.yml`). Com essa convencao, adicionar
um novo projeto ao `projects.local.yaml` (clonado sob o mesmo diretorio-pai
no host) o torna AUTOMATICAMENTE acessivel ao gateway/SDK real -- sem
qualquer edicao de `docker-compose.yml`/`.env`/codigo. Projetos cujo
`path_externo` fique FORA dessa raiz sao ignorados (logados como aviso),
pois nao ha bind mount correspondente dentro do container para eles.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_MOUNTPOINT_PADRAO = "/workspaces"


@dataclass(frozen=True)
class ProjetoRegistrado:
    """1 entrada de `projects.local.yaml` traduzida para o container."""

    id: str
    nome: str
    path_container: str


def _normalizar_para_posix(path_host: str) -> str:
    """Normaliza um path de host (Windows `C:\\...` ou POSIX `/...`) para POSIX.

    Deteccao heuristica: presenca de `\\` OU padrao de drive letter
    (`X:` na 2a posicao) indica path Windows; caso contrario, POSIX.
    """
    parece_windows = "\\" in path_host or (len(path_host) > 1 and path_host[1] == ":")
    if parece_windows:
        return PureWindowsPath(path_host).as_posix()
    return PurePosixPath(path_host).as_posix()


def carregar_projetos(
    *,
    projects_yaml_path: str,
    projects_root_path_host: str | None,
    mountpoint: str = _MOUNTPOINT_PADRAO,
) -> list[ProjetoRegistrado]:
    """Le `projects.local.yaml` e traduz `path_externo` -> path no container.

    Args:
        projects_yaml_path: Caminho (dentro do container) do
            `projects.local.yaml` -- default esperado:
            `/governance/.github/projects.local.yaml` (repositorio de
            governanca inteiro ja montado em `/governance:ro`).
        projects_root_path_host: Valor de `PROJECTS_ROOT_PATH` (path do HOST
            que foi montado em `mountpoint` dentro do container). Se `None`
            ou vazio, retorna lista vazia (nenhum projeto e traduzivel sem
            saber qual diretorio do host corresponde a `mountpoint`).
        mountpoint: Path dentro do container onde `projects_root_path_host`
            foi montado (default `/workspaces`, ver `docker-compose.yml`).

    Returns:
        list[ProjetoRegistrado]: 1 entrada por projeto cujo `path_externo`
        esta contido em `projects_root_path_host` (demais sao ignorados
        com `logger.warning`). Lista vazia se o YAML nao existir/estiver
        malformado ou `projects_root_path_host` nao estiver configurado --
        nunca levanta excecao (chamado no hot-path de cada request de chat).
    """
    if not projects_root_path_host:
        return []

    try:
        with open(projects_yaml_path, encoding="utf-8") as arquivo:
            dados: dict[str, Any] = yaml.safe_load(arquivo) or {}
    except (OSError, yaml.YAMLError) as exc:
        logger.warning(
            "projects_local_yaml_indisponivel: path=%s erro=%s",
            projects_yaml_path,
            exc,
        )
        return []

    raiz_posix = _normalizar_para_posix(projects_root_path_host).rstrip("/")
    mountpoint_normalizado = mountpoint.rstrip("/")
    resultado: list[ProjetoRegistrado] = []

    for projeto in dados.get("projetos") or []:
        path_externo = projeto.get("path_externo")
        projeto_id = str(projeto.get("id") or "")
        if not path_externo or not projeto_id:
            continue

        path_posix = _normalizar_para_posix(str(path_externo))
        dentro_da_raiz = path_posix == raiz_posix or path_posix.startswith(
            raiz_posix + "/"
        )
        if not dentro_da_raiz:
            logger.warning(
                "projeto_fora_da_raiz_montada: id=%s path_externo=%s "
                "projects_root_path=%s (sem bind mount correspondente)",
                projeto_id,
                path_externo,
                projects_root_path_host,
            )
            continue

        sufixo = path_posix[len(raiz_posix) :].lstrip("/")
        path_container = (
            f"{mountpoint_normalizado}/{sufixo}" if sufixo else mountpoint_normalizado
        )
        resultado.append(
            ProjetoRegistrado(
                id=projeto_id,
                nome=str(projeto.get("name") or projeto_id),
                path_container=path_container,
            )
        )

    return resultado
