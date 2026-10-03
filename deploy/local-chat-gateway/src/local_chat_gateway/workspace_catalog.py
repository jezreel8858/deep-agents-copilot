"""workspace_catalog — descoberta de arquivos do workspace para o picker `#`
do composer (paridade com o plugin Copilot da IDE, ver screenshots do
pedido original: "Select File, Folder or Tool").

Reaproveita a mesma fonte de verdade de `projects_catalog.carregar_projetos`
(1 raiz por projeto registrado em `projects.local.yaml`, ja traduzida para o
path dentro do container) -- nenhuma nova configuracao e necessaria. Quando
nenhum projeto esta registrado, cai para a raiz unica `gateway_workspace_dir`
(mesmo fallback historico de `routes._diretorios_de_projetos_registrados`).

Convencao de ignore -- paridade com o picker nativo da IDE (pesquisa externa,
2026-10-02): o picker de arquivos do plugin Copilot (e o `file_search`/
`grep_search` do proprio editor) e baseado em ripgrep, que aplica 2 regras
independentes:
1. Oculta por padrao qualquer entrada "dot-prefixed" (`.foo`), INDEPENDENTE
   de `.gitignore` (git em si NUNCA oculta dotfiles por padrao -- isso e um
   comportamento exclusivo do ripgrep/editor).
2. Aplica os padroes de `.gitignore` + `.ignore` + `.rgignore` (sintaxe
   gitignore, com suporte a negacao `!padrao`), nesta ordem de precedencia
   (mais especifico por ultimo) -- e crucialmente, uma regra de NEGACAO em
   `.ignore`/`.rgignore` tambem e o unico mecanismo capaz de "desocultar"
   uma entrada dot-prefixed da regra 1.

Este repositorio ja depende exatamente deste comportamento: a raiz tem
`.ignore`/`.rgignore` com `!.github/` + `!.github/**` especificamente para
que `.github/` (que NUNCA aparece em `.gitignore` -- git rastreia o
diretorio normalmente) volte a ser visivel para ferramentas baseadas em
ripgrep (ver `.github/copilot-instructions.md`, secao de Localizacao
Deterministica de Arquivos). Sem replicar as 2 regras acima, `.github/`
ficaria permanentemente invisivel neste picker (bug real corrigido aqui).
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pathspec

# Diretorio jamais exibido, independente de qualquer regra de negacao --
# ripgrep tambem trata `.git/` como caso especial incondicional.
_DIRETORIO_SEMPRE_IGNORADO = ".git"

# Baseline aplicada quando o projeto NAO declara seu proprio `.gitignore`/
# `.ignore`/`.rgignore` (ou quando estes nao cobrem ruido comum de
# ferramentas) -- evita que a varredura fique lenta/ruidosa em projetos sem
# convencao propria de ignore. Combinada (nao substituida) com os arquivos
# reais do projeto, se existirem.
_PADROES_BASELINE: tuple[str, ...] = (
    "node_modules/",
    "__pycache__/",
    ".next/",
    ".nuxt/",
    "dist/",
    "build/",
    "out/",
    ".venv/",
    "venv/",
    "target/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".turbo/",
    ".cache/",
    "coverage/",
    ".angular/",
    ".parcel-cache/",
)

_ARQUIVOS_IGNORE_SUPORTADOS: tuple[str, ...] = (".gitignore", ".ignore", ".rgignore")

_ORCAMENTO_VARREDURA_PADRAO = 20_000
_LIMITE_PADRAO = 30
_LIMITE_MAXIMO = 200
# Folga antes de ordenar e cortar no `limit` final -- evita que o primeiro
# diretorio visitado monopolize os resultados antes de varrer os demais.
_FATOR_FOLGA_PRE_CORTE = 8


@dataclass(frozen=True)
class ArquivoWorkspace:
    """1 arquivo descoberto, pronto para serializar em `WorkspaceFileItem`."""

    path: str
    project: str
    name: str


@dataclass(frozen=True)
class _RegrasIgnore:
    """Regras de ignore resolvidas para 1 raiz de projeto (cacheadas por
    chamada de `listar_arquivos_workspace` -- nunca releem disco por arquivo).
    """

    spec: pathspec.PathSpec
    desocultados: frozenset[str]


def _carregar_regras_ignore(raiz: Path) -> _RegrasIgnore:
    """Le `.gitignore` + `.ignore` + `.rgignore` da raiz (se existirem) e
    monta o `PathSpec` combinado (sintaxe `gitwildmatch`, suporta negacao),
    alem do conjunto de nomes dot-prefixed explicitamente "desocultados" por
    uma regra `!`.

    Args:
        raiz: diretorio raiz do projeto sendo varrido.

    Returns:
        _RegrasIgnore: nunca levanta excecao -- arquivo ausente ou ilegivel
        e tratado como "sem regras adicionais" (apenas a baseline aplica).
    """
    linhas: list[str] = list(_PADROES_BASELINE)
    desocultados: set[str] = set()

    for nome_arquivo in _ARQUIVOS_IGNORE_SUPORTADOS:
        caminho = raiz / nome_arquivo
        if not caminho.is_file():
            continue
        try:
            conteudo = caminho.read_text(encoding="utf-8")
        except OSError:
            continue
        for linha_bruta in conteudo.splitlines():
            linha = linha_bruta.strip()
            if not linha or linha.startswith("#"):
                continue
            linhas.append(linha)
            if linha.startswith("!"):
                alvo = linha[1:].strip().lstrip("/")
                primeiro_segmento = alvo.split("/", 1)[0]
                if primeiro_segmento.startswith("."):
                    desocultados.add(primeiro_segmento)

    spec = pathspec.PathSpec.from_lines("gitwildmatch", linhas)
    return _RegrasIgnore(spec=spec, desocultados=frozenset(desocultados))


def _deve_ignorar_dir(nome_dir: str, caminho_relativo: str, regras: _RegrasIgnore) -> bool:
    """Decide se um diretorio deve ser podado da varredura (`os.walk`).

    Replica as 2 regras do ripgrep descritas no docstring do modulo: oculto
    por padrao se dot-prefixed (exceto se explicitamente desocultado via
    negacao), OU ignorado pelos padroes combinados de
    `.gitignore`/`.ignore`/`.rgignore`.
    """
    if nome_dir == _DIRETORIO_SEMPRE_IGNORADO:
        return True
    if nome_dir.startswith(".") and nome_dir not in regras.desocultados:
        return True
    return regras.spec.match_file(f"{caminho_relativo}/")


def _deve_ignorar_arquivo(caminho_relativo: str, nome_arquivo: str, regras: _RegrasIgnore) -> bool:
    """Decide se um arquivo deve ser excluido do resultado (mesma politica
    de `_deve_ignorar_dir`, aplicada ao arquivo em si -- cobre padroes tipo
    `*.log`/`*.pyc` que nao sao nomes de diretorio)."""
    if nome_arquivo.startswith(".") and nome_arquivo not in regras.desocultados:
        return True
    return regras.spec.match_file(caminho_relativo)


def listar_arquivos_workspace(
    *,
    raizes: Sequence[tuple[str, Path]],
    query: str = "",
    limit: int = _LIMITE_PADRAO,
    orcamento_varredura: int = _ORCAMENTO_VARREDURA_PADRAO,
) -> tuple[list[ArquivoWorkspace], bool]:
    """Varre `raizes` (1 por projeto) e devolve arquivos cujo path relativo
    contem `query` (case-insensitive, substring simples -- mesma heuristica
    do picker nativo da IDE), respeitando `.gitignore`/`.ignore`/`.rgignore`
    de cada raiz (ver docstring do modulo).

    Args:
        raizes: lista de `(nome_projeto, path_absoluto_no_container)`.
        query: substring de filtro (vazio = lista completa, ate o limite).
        limit: maximo de itens retornados (sempre normalizado para
            `[1, _LIMITE_MAXIMO]` pelo chamador -- este modulo nao valida).
        orcamento_varredura: teto de arquivos VISITADOS (nao apenas
            retornados) antes de abortar a varredura por seguranca de
            latencia -- resulta em `truncated=True`.

    Returns:
        tuple[list[ArquivoWorkspace], bool]: itens ordenados por
        (comprimento do path, path alfabetico) -- arquivos mais "proximos
        da raiz" aparecem primeiro, igual ao picker da IDE -- e uma flag
        `truncated` (`True` se o orcamento de varredura estourou OU se havia
        mais correspondencias do que `limit`).
    """
    query_normalizada = query.strip().lower()
    encontrados: list[ArquivoWorkspace] = []
    truncado = False
    visitados = 0
    teto_pre_corte = max(limit, 1) * _FATOR_FOLGA_PRE_CORTE

    for nome_projeto, raiz in raizes:
        if truncado:
            break
        if not raiz.is_dir():
            continue
        regras = _carregar_regras_ignore(raiz)
        for dirpath, dirnames, filenames in os.walk(raiz):
            dir_relativo = Path(dirpath).relative_to(raiz).as_posix()
            dirnames[:] = [
                d
                for d in dirnames
                if not _deve_ignorar_dir(
                    d, f"{dir_relativo}/{d}" if dir_relativo != "." else d, regras
                )
            ]
            for filename in filenames:
                visitados += 1
                if visitados > orcamento_varredura:
                    truncado = True
                    break
                caminho_relativo = (Path(dirpath) / filename).relative_to(raiz).as_posix()
                if _deve_ignorar_arquivo(caminho_relativo, filename, regras):
                    continue
                if query_normalizada and query_normalizada not in caminho_relativo.lower():
                    continue
                encontrados.append(
                    ArquivoWorkspace(path=caminho_relativo, project=nome_projeto, name=filename)
                )
                if len(encontrados) >= teto_pre_corte:
                    truncado = True
                    break
            if truncado:
                break

    encontrados.sort(key=lambda item: (len(item.path), item.path))
    if len(encontrados) > limit:
        truncado = True
    return encontrados[:limit], truncado
