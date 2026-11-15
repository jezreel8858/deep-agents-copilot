from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from governance_runner.synth.exporter import (
    GOLDEN_NOME,
    SynthExportPathError,
    exportar_silver,
    promover_silver,
)
from governance_runner.synth.golden import calcular_sha256_golden
from governance_runner.synth.storage import SynthRepository

AGORA = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
SILVER_NOME = "casos-roteamento-silver-20260101-120000.yaml"


@pytest.fixture
def raiz(tmp_path: Path) -> Path:
    return tmp_path / "synthetic"


def _semear_eval(repo: SynthRepository, semear, passou: bool, texto: str) -> str:  # type: ignore[no-untyped-def]
    rid = repo.criar_run(kind="generate", generator="template")
    pid = semear(repo, rid, texto, rota="python-developer")
    ev = repo.criar_run(kind="eval")
    repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route="bug-triage", route_source="tool_hook",
                           verdict="matched" if passou else "mismatched", passed=passou)
    return ev


def test_exporta_silver_somente_falhas(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    rid = repo.criar_run(kind="generate", generator="template")
    p_ok = semear(repo, rid, "caso que passou")
    p_ko = semear(repo, rid, "caso que falhou")
    ev = repo.criar_run(kind="eval")
    repo.inserir_avaliacao(run_id=ev, prompt_id=p_ok, observed_route="x", route_source="tool_hook", verdict="matched", passed=True)
    repo.inserir_avaliacao(run_id=ev, prompt_id=p_ko, observed_route="y", route_source="tool_hook", verdict="mismatched", passed=False)
    res = exportar_silver(repo=repo, eval_run_id=ev, allow_root=raiz, agora=AGORA)
    assert res.path is not None and res.path.name == SILVER_NOME and res.n_itens == 1
    doc = yaml.safe_load(res.path.read_text(encoding="utf-8"))
    caso = doc["casos"][0]
    assert caso["input"]["solicitacao"] == "caso que falhou"
    assert caso["silver"]["review_status"] == "pending" and caso["silver"]["corrected_route"] is None
    assert [e["status"] for e in repo.listar_exports()] == ["silver"]


def test_export_all_inclui_aprovados(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    rid = repo.criar_run(kind="generate", generator="template")
    p_ok = semear(repo, rid, "caso que passou")
    p_ko = semear(repo, rid, "caso que falhou")
    ev = repo.criar_run(kind="eval")
    repo.inserir_avaliacao(run_id=ev, prompt_id=p_ok, observed_route="x", route_source="tool_hook", verdict="matched", passed=True)
    repo.inserir_avaliacao(run_id=ev, prompt_id=p_ko, observed_route="y", route_source="tool_hook", verdict="mismatched", passed=False)
    todos = exportar_silver(repo=repo, eval_run_id=ev, only_failures=False, allow_root=raiz, agora=AGORA)
    assert todos.n_itens == 2


def test_export_sem_avaliacoes_gera_arquivo_vazio(repo, raiz) -> None:  # type: ignore[no-untyped-def]
    res = exportar_silver(repo=repo, eval_run_id="nada", allow_root=raiz, agora=AGORA)
    assert res.n_itens == 0 and res.path is not None and res.path.exists()


def test_export_nunca_toca_golden(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    antes = calcular_sha256_golden()
    ev = _semear_eval(repo, semear, False, "x")
    exportar_silver(repo=repo, eval_run_id=ev, allow_root=raiz, agora=AGORA)
    assert calcular_sha256_golden() == antes


def _silver_aprovado(repo, semear, raiz, texto: str = "migrar pipeline legado xyz para plataforma abc") -> Path:  # type: ignore[no-untyped-def]
    ev = _semear_eval(repo, semear, False, texto)
    res = exportar_silver(repo=repo, eval_run_id=ev, allow_root=raiz, agora=AGORA)
    assert res.path is not None
    doc = yaml.safe_load(res.path.read_text(encoding="utf-8"))
    doc["casos"][0]["silver"]["review_status"] = "approved"
    doc["casos"][0]["silver"]["corrected_route"] = "python-developer"
    res.path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return res.path


def test_promote_sem_confirm_nao_grava(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    silver = _silver_aprovado(repo, semear, raiz)
    res = promover_silver(repo=repo, silver=silver.name, run_id="r1", allow_root=raiz)
    assert res.n_promovidos == 1 and res.gravado is False
    assert not (raiz / "promoted-r1.yaml").exists()
    assert repo.listar_exports(status="promoted") == []


def test_promote_confirm_grava_candidata_e_atualiza_status(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    silver = _silver_aprovado(repo, semear, raiz)
    res = promover_silver(repo=repo, silver=silver.name, run_id="r1", confirm=True, allow_root=raiz)
    destino = raiz / "promoted-r1.yaml"
    assert res.gravado and destino.exists()
    doc = yaml.safe_load(destino.read_text(encoding="utf-8"))
    assert doc["regressao"][0]["expected"]["agent_route"] == "python-developer"
    assert len(repo.listar_exports(status="promoted")) == 1


def test_promote_stdout_nao_grava_mesmo_com_confirm(repo, semear, raiz, capsys) -> None:  # type: ignore[no-untyped-def]
    silver = _silver_aprovado(repo, semear, raiz)
    res = promover_silver(repo=repo, silver=silver.name, run_id="r1", stdout=True, confirm=True, allow_root=raiz)
    assert res.gravado is False and "regressao" in capsys.readouterr().out
    assert not (raiz / "promoted-r1.yaml").exists()


def test_promote_ignora_nao_aprovados(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    ev = _semear_eval(repo, semear, False, "texto pendente de revisao humana")
    res = exportar_silver(repo=repo, eval_run_id=ev, allow_root=raiz, agora=AGORA)
    assert res.path is not None
    out = promover_silver(repo=repo, silver=res.path.name, run_id="r2", confirm=True, allow_root=raiz)
    assert out.n_promovidos == 0


def test_promote_descarta_duplicata_do_golden(repo, semear, raiz) -> None:  # type: ignore[no-untyped-def]
    from governance_runner.synth.golden import carregar_seeds_golden

    texto = carregar_seeds_golden()[0].prompt
    silver = _silver_aprovado(repo, semear, raiz, texto)
    out = promover_silver(repo=repo, silver=silver.name, run_id="r3", allow_root=raiz)
    assert out.n_duplicados == 1 and out.n_promovidos == 0


@pytest.mark.parametrize(
    "silver",
    ["../" + SILVER_NOME, "sub/../" + SILVER_NOME, GOLDEN_NOME, "promoted-x.yaml", "qualquer.yaml",
     "casos-roteamento-silver-x.txt"],
)
def test_promote_rejeita_entradas_invalidas(repo, raiz, silver: str) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(SynthExportPathError) as exc:
        promover_silver(repo=repo, silver=silver, run_id="r", allow_root=raiz)
    assert exc.value.exit_code == 2


@pytest.mark.parametrize("out", ["../promoted-r.yaml", GOLDEN_NOME, "outro.yaml", "casos-roteamento-silver-1.yaml"])
def test_promote_rejeita_saidas_invalidas(repo, semear, raiz, out: str) -> None:  # type: ignore[no-untyped-def]
    silver = _silver_aprovado(repo, semear, raiz)
    with pytest.raises(SynthExportPathError):
        promover_silver(repo=repo, silver=silver.name, run_id="r", out=out, confirm=True, allow_root=raiz)


def test_promote_rejeita_caminho_absoluto_fora_do_root(repo, tmp_path: Path, raiz) -> None:  # type: ignore[no-untyped-def]
    fora = tmp_path / SILVER_NOME
    with pytest.raises(SynthExportPathError):
        promover_silver(repo=repo, silver=fora, run_id="r", allow_root=raiz)


def test_promote_rejeita_symlink_que_escapa(repo, tmp_path: Path, raiz) -> None:  # type: ignore[no-untyped-def]
    raiz.mkdir(parents=True)
    alvo = tmp_path / "fora.yaml"
    alvo.write_text("casos: []", encoding="utf-8")
    link = raiz / SILVER_NOME
    try:
        os.symlink(alvo, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink indisponivel neste ambiente")
    with pytest.raises(SynthExportPathError):
        promover_silver(repo=repo, silver=link.name, run_id="r", allow_root=raiz)
