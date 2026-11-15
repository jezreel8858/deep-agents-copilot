"""
exporter — Exportacao Silver e promocao controlada para suites de regressao (§3.3).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from governance_runner.synth.dedup import DEFAULT_SIM_THRESHOLD, DedupFunnel
from governance_runner.synth.golden import carregar_seeds_golden
from governance_runner.synth.storage import SynthRepository

__all__ = [
    "SILVER_DIR",
    "SILVER_PREFIX",
    "PROMOTED_PREFIX",
    "EXIT_CAMINHO_INVALIDO",
    "SynthExportPathError",
    "ResultadoExport",
    "ResultadoPromote",
    "exportar_silver",
    "promover_silver",
]

SILVER_DIR = Path(".github") / "agents" / "evals" / "synthetic"
SILVER_PREFIX = "casos-roteamento-silver-"
PROMOTED_PREFIX = "promoted-"
GOLDEN_NOME = "casos-roteamento.yaml"
EXIT_CAMINHO_INVALIDO = 2

_REPO_ROOT = Path(__file__).resolve().parents[5]


class SynthExportPathError(ValueError):
    exit_code = EXIT_CAMINHO_INVALIDO


class ResultadoExport:
    def __init__(self, path: Path | None, n_itens: int, export_ids: list[str]) -> None:
        self.path = path
        self.n_itens = n_itens
        self.export_ids = export_ids


class ResultadoPromote:
    def __init__(
        self,
        path: Path | None,
        n_promovidos: int,
        n_duplicados: int,
        conteudo: str,
        gravado: bool,
    ) -> None:
        self.path = path
        self.n_promovidos = n_promovidos
        self.n_duplicados = n_duplicados
        self.conteudo = conteudo
        self.gravado = gravado


def _allow_root_padrao() -> Path:
    return (_REPO_ROOT / SILVER_DIR).resolve()


def _validar_sob_root(caminho: Path, allow_root: Path) -> Path:
    raiz = allow_root.resolve()
    if ".." in caminho.parts:
        raise SynthExportPathError(f"traversal rejeitado: {caminho}")
    alvo = (caminho if caminho.is_absolute() else raiz / caminho).resolve()
    if alvo != raiz and raiz not in alvo.parents:
        raise SynthExportPathError(f"caminho fora de allow_root: {alvo}")
    if alvo.name == GOLDEN_NOME:
        raise SynthExportPathError("escrita/leitura de casos-roteamento.yaml proibida")
    return alvo


def exportar_silver(
    *,
    repo: SynthRepository,
    eval_run_id: str,
    only_failures: bool = True,
    include_near_boundary: bool = False,
    allow_root: Path | None = None,
    agora: datetime | None = None,
) -> ResultadoExport:
    raiz = allow_root if allow_root is not None else _allow_root_padrao()
    avaliacoes = repo.listar_avaliacoes(
        eval_run_id,
        only_failures=only_failures,
        include_near_boundary=include_near_boundary,
    )
    momento = agora or datetime.now(timezone.utc)
    nome = f"{SILVER_PREFIX}{momento.strftime('%Y%m%d-%H%M%S')}.yaml"
    if nome.startswith(PROMOTED_PREFIX):
        raise SynthExportPathError("prefixo promoted-* proibido no Silver")
    destino = _validar_sob_root(Path(nome), raiz)
    if destino.exists() and destino.is_symlink():
        raise SynthExportPathError(f"symlink rejeitado: {destino}")
    casos: list[dict[str, Any]] = []
    for ev in avaliacoes:
        case_id = f"silver-{str(ev['prompt_id'])[:12]}"
        expected_bloco: dict[str, Any] = {"agent_route": ev["expected_route"]}
        exp_wf = ev.get("expected_workflow")
        if exp_wf is not None and str(exp_wf).strip():
            expected_bloco["workflow"] = str(exp_wf).strip()

        silver_bloco: dict[str, Any] = {
            "prompt_id": ev["prompt_id"],
            "eval_id": ev["eval_id"],
            "observed_route": ev["observed_route"],
            "verdict": ev["verdict"],
            "max_similarity": ev["max_similarity"],
            "review_status": "pending",
            "corrected_route": None,
        }
        obs_wf = ev.get("observed_workflow")
        if obs_wf is not None and str(obs_wf).strip():
            silver_bloco["observed_workflow"] = str(obs_wf).strip()

        item_caso: dict[str, Any] = {
            "id": case_id,
            "descricao": f"{ev['agente_alvo']} / {ev['dimensao_perturbacao']}",
            "input": {"solicitacao": ev["prompt_text"]},
            "expected": expected_bloco,
            "silver": silver_bloco,
        }
        if obs_wf is not None and str(obs_wf).strip():
            item_caso["observed"] = {
                "observed_route": ev["observed_route"],
                "observed_workflow": str(obs_wf).strip(),
            }
        casos.append(item_caso)

    raiz.mkdir(parents=True, exist_ok=True)
    doc = {"version": "1.0", "origem": "synth-export", "eval_run_id": eval_run_id, "casos": casos}
    destino.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    ids = [
        repo.inserir_export(
            prompt_id=str(ev["prompt_id"]),
            eval_id=str(ev["eval_id"]),
            silver_path=str(destino),
            silver_case_id=c["id"],
        )
        for ev, c in zip(avaliacoes, casos)
    ]
    return ResultadoExport(destino, len(casos), ids)


def promover_silver(
    *,
    repo: SynthRepository | None,
    silver: str | Path,
    run_id: str,
    suite: str = "regressao",
    out: str | Path | None = None,
    stdout: bool = False,
    confirm: bool = False,
    allow_root: Path | None = None,
    repo_root: Path | None = None,
    sim_threshold: float = DEFAULT_SIM_THRESHOLD,
) -> ResultadoPromote:
    raiz = allow_root if allow_root is not None else _allow_root_padrao()
    entrada = _validar_sob_root(Path(silver), raiz)
    if not entrada.name.startswith(SILVER_PREFIX) or entrada.suffix != ".yaml":
        raise SynthExportPathError(f"entrada deve casar '{SILVER_PREFIX}*.yaml': {entrada.name}")
    destino = _validar_sob_root(Path(out) if out else Path(f"{PROMOTED_PREFIX}{run_id}.yaml"), raiz)
    if not destino.name.startswith(PROMOTED_PREFIX):
        raise SynthExportPathError(f"saida deve usar prefixo '{PROMOTED_PREFIX}': {destino.name}")
    dados = yaml.safe_load(entrada.read_text(encoding="utf-8")) or {}
    seeds = carregar_seeds_golden(repo_root=repo_root)
    funnel = DedupFunnel(
        sim_threshold=sim_threshold,
        documentos_iniciais=[(f"golden:{s.id}", s.prompt) for s in seeds],
    )
    aprovados: list[dict[str, Any]] = []
    duplicados = 0
    for caso in dados.get("casos", []):
        meta = caso.get("silver", {})
        rota = meta.get("corrected_route")
        if meta.get("review_status") != "approved" or not rota:
            continue
        texto = str(caso["input"]["solicitacao"])
        if not funnel.avaliar(texto, registrar_se_aceito=True, ref_se_aceito=str(caso["id"])).aceito:
            duplicados += 1
            continue
        expected_prom: dict[str, Any] = {"agent_route": rota}
        wf_corr = meta.get("corrected_workflow") or (caso.get("expected") or {}).get("workflow")
        if wf_corr and str(wf_corr).strip():
            expected_prom["workflow"] = str(wf_corr).strip()
        aprovados.append(
            {
                "id": f"promoted-{caso['id']}",
                "descricao": caso.get("descricao", ""),
                "input": {"solicitacao": texto},
                "expected": expected_prom,
            }
        )
    conteudo = yaml.safe_dump({suite: aprovados}, allow_unicode=True, sort_keys=False)
    gravado = False
    if stdout:
        sys.stdout.write(conteudo)
    if confirm and not stdout:
        destino.write_text(conteudo, encoding="utf-8")
        gravado = True
        if repo is not None:
            for caso in dados.get("casos", []):
                if f"promoted-{caso['id']}" in {a["id"] for a in aprovados}:
                    repo.atualizar_status_export(caso["id"], "promoted", promoted_path=str(destino))
    return ResultadoPromote(destino, len(aprovados), duplicados, conteudo, gravado)
