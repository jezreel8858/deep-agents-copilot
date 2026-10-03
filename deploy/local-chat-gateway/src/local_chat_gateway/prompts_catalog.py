"""prompts_catalog — descoberta de prompts (`.github/prompts/*.prompt.md`) e
skills (`.github/skills/**/SKILL.md`) para o picker `/` do composer (paridade
com o picker de slash commands/prompts do plugin Copilot da IDE, pedido
explicito do usuario, 2026-10-02).

Mesma filosofia de `agent_catalog.py` (frontmatter YAML + corpo Markdown),
mas aqui so o frontmatter (`name`/`description`) importa -- o corpo NAO e
enviado ao SDK nem ao frontend (listagem e puramente para completar o texto
do composer; nao ha expansao server-side do conteudo do prompt/skill nesta
1a iteracao -- fora de escopo do pedido original).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Literal, TypedDict

import yaml

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_ORCAMENTO_BYTES_DESCRICAO = 300


class ComandoCatalogItem(TypedDict):
    """1 entrada do catalogo unificado de prompts + skills."""

    name: str
    kind: Literal["prompt", "skill"]
    description: str


def _parse_frontmatter(texto: str) -> dict[str, Any]:
    """Extrai so o frontmatter YAML (`--- ... ---`); descarta o corpo.

    Nunca propaga excecao -- frontmatter ausente/invalido retorna `{}`
    (item ignorado mais adiante por falta de `name`).
    """
    match = _FRONTMATTER_RE.match(texto)
    if not match:
        return {}
    bruto_frontmatter, _corpo = match.groups()
    try:
        frontmatter = yaml.safe_load(bruto_frontmatter) or {}
    except yaml.YAMLError as exc:
        logger.warning("prompts_catalog: frontmatter invalido ignorado: %s", exc)
        return {}
    return frontmatter if isinstance(frontmatter, dict) else {}


def _item_de_arquivo(
    caminho: Path,
    kind: Literal["prompt", "skill"],
    leitor_arquivo: Any,
    nome_fallback: str,
) -> ComandoCatalogItem | None:
    """Converte 1 arquivo (`.prompt.md` ou `SKILL.md`) em `ComandoCatalogItem`.

    `nome_fallback` (nome do arquivo sem extensao, ou nome da pasta da
    skill) e usado quando o frontmatter nao declara `name` -- nunca
    descarta um item so por falta desse campo opcional.
    """
    try:
        texto = leitor_arquivo(caminho)
    except OSError as exc:
        logger.warning("prompts_catalog: falha ao ler %s: %s", caminho, exc)
        return None

    frontmatter = _parse_frontmatter(texto)
    nome = str(frontmatter.get("name") or "").strip() or nome_fallback
    if not nome:
        return None

    descricao_bruta = str(frontmatter.get("description") or "").strip()
    descricao = " ".join(descricao_bruta.split())[:_ORCAMENTO_BYTES_DESCRICAO]
    return {"name": nome, "kind": kind, "description": descricao}


def descobrir_comandos(
    github_dir: Path, *, leitor_arquivo: Any | None = None
) -> list[ComandoCatalogItem]:
    """Descobre `.github/prompts/*.prompt.md` + `.github/skills/**/SKILL.md`.

    Args:
        github_dir: Raiz de `.github/` (ex.: `settings.governance_github_dir`).
        leitor_arquivo: `Callable[[Path], str]` injetavel para testes (mock
            sem tocar o filesystem); se omitido, usa `Path.read_text` real.

    Returns:
        list[ComandoCatalogItem]: catalogo ordenado deterministicamente
        (prompts primeiro em ordem alfabetica, depois skills em ordem
        alfabetica), nomes duplicados descartados (1a ocorrencia mantida) e
        arquivos invalidos ignorados -- nunca derruba o startup do gateway
        (mesma filosofia tolerante de `agent_catalog.descobrir_custom_agents`).
    """
    leitor = (
        leitor_arquivo
        if leitor_arquivo is not None
        else (lambda p: p.read_text(encoding="utf-8"))
    )

    itens: list[ComandoCatalogItem] = []
    nomes_vistos: set[str] = set()

    prompts_dir = github_dir / "prompts"
    if prompts_dir.is_dir():
        for caminho in sorted(prompts_dir.glob("*.prompt.md")):
            fallback = caminho.name.removesuffix(".prompt.md")
            item = _item_de_arquivo(caminho, "prompt", leitor, fallback)
            if item is None or item["name"] in nomes_vistos:
                continue
            nomes_vistos.add(item["name"])
            itens.append(item)
    else:
        logger.warning("prompts_catalog: diretorio de prompts nao encontrado: %s", prompts_dir)

    skills_dir = github_dir / "skills"
    if skills_dir.is_dir():
        for caminho in sorted(skills_dir.rglob("SKILL.md")):
            fallback = caminho.parent.name
            item = _item_de_arquivo(caminho, "skill", leitor, fallback)
            if item is None or item["name"] in nomes_vistos:
                continue
            nomes_vistos.add(item["name"])
            itens.append(item)
    else:
        logger.warning("prompts_catalog: diretorio de skills nao encontrado: %s", skills_dir)

    logger.info(
        "prompts_catalog: %d comandos descobertos em %s (prompts+skills)",
        len(itens),
        github_dir,
    )
    return itens
