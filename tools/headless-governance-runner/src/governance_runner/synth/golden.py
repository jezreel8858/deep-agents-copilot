"""
golden — Carregador somente-leitura do dataset Golden casos-roteamento.yaml (B1-03 / CA-01).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Sequence

import yaml

__all__ = [
    "GOLDEN_REL_PATH",
    "SUITES_GOLDEN_ORDEM",
    "CONTAGENS_ESPERADAS_POR_SUITE",
    "GoldenSeed",
    "resolver_caminho_golden",
    "calcular_sha256_golden",
    "carregar_golden_bruto",
    "carregar_seeds_golden",
    "contagens_por_suite",
]

GOLDEN_REL_PATH = Path(".github") / "agents" / "evals" / "casos-roteamento.yaml"
SUITES_GOLDEN_ORDEM: tuple[str, ...] = ("canonicos", "ambiguos", "regressao", "seguranca")
CONTAGENS_ESPERADAS_POR_SUITE: dict[str, int] = {
    "canonicos": 45,
    "ambiguos": 5,
    "regressao": 35,
    "seguranca": 4,
}


@dataclass(frozen=True)
class GoldenSeed:
    """Representa um caso semente extraido em modo somente-leitura do Golden Set."""

    id: str
    suite: str
    solicitacao: str
    agent_route: str
    descricao: str = ""
    critico: bool = False
    threshold: float = 0.8
    seed_source: Literal["manual", "routing_graph"] = "manual"
    graph_edge_id: str | None = None
    graph_edge_resolution: str | None = None
    keywords: tuple[str, ...] = ()

    @property
    def prompt(self) -> str:
        return self.solicitacao

    @property
    def expected_route(self) -> str:
        return self.agent_route

    @property
    def seed_case_id(self) -> str:
        return self.id


def resolver_caminho_golden(
    golden_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> Path:
    """Resolve o caminho do arquivo casos-roteamento.yaml."""
    if golden_path is not None:
        caminho = Path(golden_path)
        if caminho.is_absolute():
            return caminho
        if repo_root is not None:
            return (repo_root / caminho).resolve()
        return caminho.resolve()

    if repo_root is not None:
        return (repo_root / GOLDEN_REL_PATH).resolve()

    candidato_repo = Path(__file__).resolve().parents[5] / GOLDEN_REL_PATH
    if candidato_repo.exists():
        return candidato_repo
    return GOLDEN_REL_PATH.resolve()


def calcular_sha256_golden(
    golden_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> str:
    """Calcula o SHA-256 hexadecimal do arquivo casos-roteamento.yaml."""
    caminho = resolver_caminho_golden(golden_path, repo_root=repo_root)
    with open(caminho, "rb") as stream_bin:
        conteudo = stream_bin.read()
    return hashlib.sha256(conteudo).hexdigest()


def carregar_golden_bruto(
    golden_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Carrega a arvore YAML completa do Golden Set em modo somente-leitura."""
    caminho = resolver_caminho_golden(golden_path, repo_root=repo_root)
    with open(caminho, "r", encoding="utf-8") as stream_txt:
        dados = yaml.safe_load(stream_txt)
    if not isinstance(dados, dict):
        raise ValueError(f"Estrutura YAML invalida em {caminho}: esperado mapeamento no topo.")
    return dados


def contagens_por_suite(
    golden_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> dict[str, int]:
    """Retorna a contagem de casos por suite no arquivo casos-roteamento.yaml."""
    dados = carregar_golden_bruto(golden_path, repo_root=repo_root)
    suites_bruto = dados.get("suites")
    suites_container = suites_bruto if isinstance(suites_bruto, dict) else dados
    resultado: dict[str, int] = {}
    for nome_suite in SUITES_GOLDEN_ORDEM:
        itens = suites_container.get(nome_suite, [])
        if isinstance(itens, list):
            resultado[nome_suite] = len(itens)
    return resultado


def carregar_seeds_golden(
    golden_path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
    targets: Sequence[str] | None = None,
    include_security: bool = False,
) -> tuple[GoldenSeed, ...]:
    """Extrai as sementes de roteamento do Golden Set em modo somente-leitura."""
    dados = carregar_golden_bruto(golden_path, repo_root=repo_root)
    suites_bruto = dados.get("suites")
    suites_container = suites_bruto if isinstance(suites_bruto, dict) else dados

    alvos_normalizados: frozenset[str] | None = None
    if targets:
        alvos_normalizados = frozenset(
            t.strip().lstrip("@") for t in targets if t and t.strip()
        )

    seeds: list[GoldenSeed] = []
    for nome_suite in SUITES_GOLDEN_ORDEM:
        if nome_suite == "seguranca" and not include_security:
            continue
        itens = suites_container.get(nome_suite, [])
        if not isinstance(itens, list):
            continue
        for item in itens:
            if not isinstance(item, dict):
                continue
            case_id = str(item.get("id", "")).strip()
            bloco_input = item.get("input") or {}
            bloco_expected = item.get("expected") or {}
            solicitacao = str(
                bloco_input.get("solicitacao", "")
                if isinstance(bloco_input, dict)
                else ""
            ).strip()
            rota = ""
            if isinstance(bloco_expected, dict):
                rota_bruta = bloco_expected.get("agent_route") or bloco_expected.get("comportamento") or ""
                rota = str(rota_bruta).strip().lstrip("@")

            if not case_id or not solicitacao or not rota:
                continue
            if alvos_normalizados is not None and rota not in alvos_normalizados:
                continue

            seeds.append(
                GoldenSeed(
                    id=case_id,
                    suite=nome_suite,
                    solicitacao=solicitacao,
                    agent_route=rota,
                    descricao=str(item.get("descricao", "")),
                    critico=bool(item.get("critico", False)),
                    threshold=float(item.get("threshold", 0.8)),
                )
            )
    return tuple(seeds)
