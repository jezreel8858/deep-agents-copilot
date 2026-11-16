from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

import pytest

from governance_runner.synth.storage import (
    GOV_SYNTH_DB_ENV,
    SCHEMA_VERSION,
    StoragePathError,
    SynthRepository,
    resolver_caminho_db,
)

Semear = Callable[..., str]


def _novo_run(repo: SynthRepository, kind: str = "generate") -> str:
    return repo.criar_run(kind=kind, generator="template" if kind == "generate" else None)


def test_ddl_tabelas_wal_e_fk(repo: SynthRepository) -> None:
    con = repo.connection
    tabelas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"schema_meta", "synth_runs", "synth_prompts", "synth_evaluations", "synth_exports"} <= tabelas
    assert str(con.execute("PRAGMA journal_mode").fetchone()[0]).lower() == "wal"
    assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert repo.obter_schema_version() == SCHEMA_VERSION


def test_migrar_idempotente(repo: SynthRepository) -> None:
    assert repo.migrar() == repo.migrar()
    assert repo.obter_schema_version() == SCHEMA_VERSION


def test_crud_run_e_finalizacao(repo: SynthRepository) -> None:
    rid = _novo_run(repo)
    assert repo.obter_run(rid) is not None
    assert repo.obter_run("inexistente") is None
    repo.finalizar_run(rid, status="completed", n_accepted=3, premium_requests_used=2)
    run = repo.obter_run(rid)
    assert run is not None
    assert run["status"] == "completed" and run["n_accepted"] == 3 and run["premium_requests_used"] == 2
    assert run["finished_at"] is not None


@pytest.mark.parametrize(
    "campos",
    [{"kind": "invalido"}, {"kind": "generate", "status": "xpto"}, {"kind": "generate", "generator": "gpt"}],
)
def test_constraints_de_run(repo: SynthRepository, campos: dict[str, str]) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.criar_run(**campos)


def test_prompt_crud_e_sha_unico(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    pid = semear(repo, rid, "texto um")
    prompt = repo.obter_prompt(pid)
    assert prompt is not None and prompt["text"] == "texto um"
    assert repo.obter_prompt("nao-existe") is None
    assert [p["prompt_id"] for p in repo.listar_prompts(rid)] == [pid]
    assert repo.listar_prompts("outro-run") == []
    with pytest.raises(sqlite3.IntegrityError):
        semear(repo, rid, "texto dois", sha="sha-texto um")


def test_prompt_exige_run_existente_fk(repo: SynthRepository, semear: Semear) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        semear(repo, "run-fantasma", "x")


def test_cobertura_por_estrato(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    semear(repo, rid, "a")
    semear(repo, rid, "b")
    assert repo.cobertura_por_estrato() == {("python-developer", "parafrase"): 2}


@pytest.mark.parametrize("fonte", ["tool_hook", "text_banner"])
def test_route_source_valido(repo: SynthRepository, semear: Semear, fonte: str) -> None:
    rid = _novo_run(repo)
    pid = semear(repo, rid, "a")
    ev = _novo_run(repo, "eval")
    repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route="x", route_source=fonte,
                           verdict="matched", passed=True)
    assert len(repo.listar_avaliacoes(ev)) == 1


def test_route_source_invalido_d2(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    pid = semear(repo, rid, "a")
    ev = _novo_run(repo, "eval")
    with pytest.raises(sqlite3.IntegrityError):
        repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route="x", route_source="regex_solto",
                               verdict="matched", passed=True)


def test_unparseable_aceita_route_source_nulo(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    pid = semear(repo, rid, "a")
    ev = _novo_run(repo, "eval")
    repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route=None, route_source=None,
                           verdict="unparseable", passed=False)
    linhas = repo.listar_avaliacoes(ev)
    assert linhas[0]["route_source"] is None and int(linhas[0]["passed"]) == 0


def test_avaliacao_constraints_verdict_e_unicidade(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    pid = semear(repo, rid, "a")
    ev = _novo_run(repo, "eval")
    with pytest.raises(sqlite3.IntegrityError):
        repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route=None, route_source=None,
                               verdict="talvez", passed=False)
    repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route="x", route_source="tool_hook",
                           verdict="mismatched", passed=False)
    with pytest.raises(sqlite3.IntegrityError):
        repo.inserir_avaliacao(run_id=ev, prompt_id=pid, observed_route="x", route_source="tool_hook",
                               verdict="mismatched", passed=False)


def test_pendentes_exclui_avaliados_e_respeita_limit(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    ids = [semear(repo, rid, "t" + str(i)) for i in range(3)]
    ev = _novo_run(repo, "eval")
    assert len(repo.listar_pendentes_avaliacao(eval_run_id=ev)) == 3
    assert len(repo.listar_pendentes_avaliacao(eval_run_id=ev, limit=1)) == 1
    repo.inserir_avaliacao(run_id=ev, prompt_id=ids[0], observed_route="x", route_source="tool_hook",
                           verdict="matched", passed=True)
    pend = {p["prompt_id"] for p in repo.listar_pendentes_avaliacao(eval_run_id=ev)}
    assert pend == set(ids[1:])


def test_only_failures_e_near_boundary(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    ok = semear(repo, rid, "ok", similarity=0.10)
    ok_borda = semear(repo, rid, "borda", similarity=0.70)
    falha = semear(repo, rid, "falha", similarity=0.10)
    ev = _novo_run(repo, "eval")
    repo.inserir_avaliacao(run_id=ev, prompt_id=ok, observed_route="x", route_source="tool_hook", verdict="matched", passed=True)
    repo.inserir_avaliacao(run_id=ev, prompt_id=ok_borda, observed_route="x", route_source="tool_hook", verdict="matched", passed=True)
    repo.inserir_avaliacao(run_id=ev, prompt_id=falha, observed_route="y", route_source="tool_hook", verdict="mismatched", passed=False)
    assert {e["prompt_id"] for e in repo.listar_avaliacoes(ev, only_failures=True)} == {falha}
    com_borda = repo.listar_avaliacoes(ev, only_failures=True, include_near_boundary=True)
    assert {e["prompt_id"] for e in com_borda} == {falha, ok_borda}
    assert len(repo.listar_avaliacoes(ev)) == 3


def test_export_crud_e_status(repo: SynthRepository, semear: Semear) -> None:
    rid = _novo_run(repo)
    pid = semear(repo, rid, "a")
    repo.inserir_export(prompt_id=pid, eval_id=None, silver_path="s.yaml", silver_case_id="silver-1")
    assert [e["status"] for e in repo.listar_exports()] == ["silver"]
    repo.atualizar_status_export("silver-1", "promoted", promoted_path="p.yaml")
    assert repo.listar_exports(status="promoted")[0]["promoted_path"] == "p.yaml"
    assert repo.listar_exports(status="silver") == []
    with pytest.raises(sqlite3.IntegrityError):
        repo.inserir_export(prompt_id=pid, eval_id=None, silver_path="s.yaml", silver_case_id="silver-1")
    with pytest.raises(sqlite3.IntegrityError):
        repo.inserir_export(prompt_id=pid, eval_id=None, silver_path="s", silver_case_id="silver-2", status="invalido")


def test_resolver_caminho_env_e_explicito(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    alvo = tmp_path / "x.db"
    monkeypatch.setenv(GOV_SYNTH_DB_ENV, str(alvo))
    assert Path(resolver_caminho_db(repo_root=tmp_path)) == alvo.resolve()
    outro = tmp_path / "y.db"
    assert Path(resolver_caminho_db(outro, repo_root=tmp_path)) == outro.resolve()


def test_resolver_caminho_rejeita_dentro_de_github(tmp_path: Path) -> None:
    with pytest.raises(StoragePathError):
        resolver_caminho_db(tmp_path / ".github" / "x.db", repo_root=tmp_path)

def test_v2_arestas_grafo_e_diagnosticos(repo: SynthRepository) -> None:
    from governance_runner.synth.routing_graph import GrafoSnapshot, RotaGrafo

    r1 = RotaGrafo(
        edge_id="e-111111111111",
        de="agent-router",
        para="python-developer",
        tipo="keyword_based",
        regra=None,
        prioridade=1.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=("fastapi",),
        valida=True,
    )
    r2 = RotaGrafo(
        edge_id="e-222222222222",
        de="agent-router",
        para="SendTo-Verify",
        tipo="health_check",
        regra="hc",
        prioridade=0.0,
        threshold_score=1.0,
        nivel_routing="L0",
        keywords=(),
        valida=False,
    )
    snap = GrafoSnapshot(
        sha256="f" * 64,
        rotas=(r1,),
        nos=frozenset({"agent-router", "python-developer", "SendTo-Verify"}),
        todas_rotas=(r1, r2),
    )
    assert repo.registrar_arestas_grafo(snap) == 2
    assert len(repo.listar_arestas_grafo("f" * 64)) == 2
    assert len(repo.listar_arestas_grafo("f" * 64, apenas_validas=True)) == 1

    ev_run = _novo_run(repo, "eval")
    diag_id = repo.inserir_diagnostico(
        diagnostic_id="diag-test0001",
        eval_run_id=ev_run,
        routing_graph_sha256="f" * 64,
        router_agent_sha256="a" * 64,
        golden_set_sha256="b" * 64,
        yaml_path=".synth/diagnostic-ev.yaml",
        md_path=".synth/diagnostic-ev.md",
        metrics={"acuracia_global": 0.5},
        n_suggestions=3,
    )
    obtido = repo.obter_diagnostico(diag_id)
    assert obtido is not None
    assert obtido["eval_run_id"] == ev_run
    assert obtido["n_suggestions"] == 3


def test_deve_configurar_busy_timeout_e_wal_ao_abrir_repositorio(tmp_path: Path) -> None:
    repo = SynthRepository(tmp_path / "synth.db", repo_root=tmp_path)
    try:
        assert repo._conn.execute("PRAGMA busy_timeout;").fetchone()[0] == 30000
        assert str(repo._conn.execute("PRAGMA journal_mode;").fetchone()[0]).lower() == "wal"
    finally:
        repo.close()


def test_deve_reconciliar_runs_orfaos_em_status_running(repo: SynthRepository) -> None:
    # Cenario A: run generate em running com prompts persistidos
    run_gen_ok = _novo_run(repo, "generate")
    pid_1 = repo.inserir_prompt(
        run_id=run_gen_ok,
        text="prompt orfao 1",
        text_norm="prompt orfao 1",
        sha256="sha-orfao-1",
        expected_route="python-developer",
        agente_alvo="python-developer",
        dimensao_perturbacao="parafrase",
        max_similarity=0.15,
    )
    repo.inserir_prompt(
        run_id=run_gen_ok,
        text="prompt orfao 2",
        text_norm="prompt orfao 2",
        sha256="sha-orfao-2",
        expected_route="python-developer",
        agente_alvo="python-developer",
        dimensao_perturbacao="parafrase",
        max_similarity=0.20,
    )

    # Cenario B: run eval em running com avaliacao persistida
    run_eval_ok = _novo_run(repo, "eval")
    repo.inserir_avaliacao(
        run_id=run_eval_ok,
        prompt_id=pid_1,
        observed_route="python-developer",
        route_source="tool_hook",
        verdict="matched",
        passed=True,
        premium_requests=2,
    )

    # Cenario C: run eval em running vazio (sem prompts/avaliacoes)
    run_vazio = _novo_run(repo, "eval")

    # Cenario D: run ja completed (deve permanecer intocado)
    run_concluido = _novo_run(repo, "generate")
    repo.finalizar_run(run_concluido, status="completed", n_accepted=5, premium_requests_used=3)
    estado_concluido_antes = repo.obter_run(run_concluido)
    assert estado_concluido_antes is not None

    # Verifica filtro run_id: reconcilia apenas o run_id informado
    assert repo.reconciliar_runs_orfaos(run_id=run_gen_ok) == 1
    gen_apos = repo.obter_run(run_gen_ok)
    assert gen_apos is not None
    assert gen_apos["status"] == "completed"
    assert gen_apos["n_accepted"] == 2
    assert gen_apos["finished_at"] is not None

    # Os demais runs em running continuam aguardando reconciliacao geral
    eval_antes = repo.obter_run(run_eval_ok)
    vazio_antes = repo.obter_run(run_vazio)
    assert eval_antes is not None and eval_antes["status"] == "running"
    assert vazio_antes is not None and vazio_antes["status"] == "running"

    # Reconciliacao geral dos runs restantes (Cenarios B, C e D)
    assert repo.reconciliar_runs_orfaos() == 2

    eval_apos = repo.obter_run(run_eval_ok)
    assert eval_apos is not None
    assert eval_apos["status"] == "completed"
    assert eval_apos["n_candidates"] == 1
    assert eval_apos["n_accepted"] == 1
    assert eval_apos["premium_requests_used"] == 2
    assert eval_apos["finished_at"] is not None

    vazio_apos = repo.obter_run(run_vazio)
    assert vazio_apos is not None
    assert vazio_apos["status"] == "failed"
    assert vazio_apos["motivo"] == "interrompido_timeout_orfandade"
    assert vazio_apos["finished_at"] is not None

    concluido_apos = repo.obter_run(run_concluido)
    assert concluido_apos == estado_concluido_antes

    # Verifica idempotencia: 2a chamada consecutiva retorna 0
    assert repo.reconciliar_runs_orfaos() == 0
