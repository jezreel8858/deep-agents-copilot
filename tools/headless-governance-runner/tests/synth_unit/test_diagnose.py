"""Testes do motor offline synth-diagnose e determinismo bit-a-bit (B3-04 / CA-05)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from governance_runner import cli
from governance_runner.synth.diagnostic_exporter import (
    exportar_diagnostico,
    renderizar_diagnostico_md,
    renderizar_diagnostico_yaml,
    sanitizar_excerto_md,
)
from governance_runner.synth.diagnostics import (
    AVISO_HITL,
    CATEGORIAS_DIVERGENCIA,
    SynthEvalRunInvalidoError,
    diagnosticar_avaliacao,
)
from governance_runner.synth.golden import GoldenSeed
from governance_runner.synth.routing_graph import GrafoSnapshot, RotaGrafo
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.use_cases import executar_synth_diagnose


def _snapshot_sintetico() -> GrafoSnapshot:
    r_py = RotaGrafo(
        edge_id="e-aaaa00000001",
        de="agent-router",
        para="python-developer",
        tipo="keyword_based",
        regra=None,
        prioridade=1.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=("fastapi", "endpoint", "api rest"),
    )
    r_arch = RotaGrafo(
        edge_id="e-bbbb00000002",
        de="agent-router",
        para="python-arch-advisor",
        tipo="keyword_based",
        regra=None,
        prioridade=2.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=("endpoint", "arquitetura", "api rest"),
    )
    r_dba = RotaGrafo(
        edge_id="e-cccc00000003",
        de="agent-router",
        para="sql-dba",
        tipo="keyword_based",
        regra=None,
        prioridade=3.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=("postgres", "migracao"),
    )
    r_unp = RotaGrafo(
        edge_id="e-dddd00000004",
        de="agent-router",
        para="bug-triage",
        tipo="keyword_based",
        regra="regra_sem_kw",
        prioridade=4.0,
        threshold_score=0.7,
        nivel_routing="L1",
        keywords=(),
        descricao_no="",
    )
    return GrafoSnapshot(
        sha256="1" * 64,
        rotas=(r_py, r_arch, r_dba, r_unp),
        nos=frozenset({"agent-router", "python-developer", "python-arch-advisor", "sql-dba", "bug-triage"}),
        todas_rotas=(r_py, r_arch, r_dba, r_unp),
    )


def _avaliacoes_sinteticas() -> list[dict]:
    return [
        {
            "eval_id": "ev-1",
            "prompt_id": "p-1",
            "expected_route": "python-developer",
            "observed_route": "python-developer",
            "verdict": "matched",
            "passed": 1,
            "seed_source": "manual",
            "graph_edge_id": "e-aaaa00000001",
            "prompt_text": "Implementar endpoint fastapi assincrono",
        },
        {
            "eval_id": "ev-2",
            "prompt_id": "p-2",
            "expected_route": "python-developer",
            "observed_route": "python-arch-advisor",
            "verdict": "mismatched",
            "passed": 0,
            "seed_source": "routing_graph",
            "graph_edge_id": "e-aaaa00000001",
            "prompt_text": "Refatorar servico pydantic validacao",
        },
        {
            "eval_id": "ev-3",
            "prompt_id": "p-3",
            "expected_route": "python-developer",
            "observed_route": "python-arch-advisor",
            "verdict": "mismatched",
            "passed": 0,
            "seed_source": "routing_graph",
            "graph_edge_id": "e-aaaa00000001",
            "prompt_text": "Refatorar servico pydantic serializacao",
        },
        {
            "eval_id": "ev-4",
            "prompt_id": "p-4",
            "expected_route": "sql-dba",
            "observed_route": "ghost-agent-xyz",
            "verdict": "mismatched",
            "passed": 0,
            "seed_source": "manual",
            "graph_edge_id": "e-cccc00000003",
            "prompt_text": "Otimizar query lenta no postgres",
        },
        {
            "eval_id": "ev-5",
            "prompt_id": "p-5",
            "expected_route": "sql-dba",
            "observed_route": None,
            "verdict": "unparseable",
            "passed": 0,
            "seed_source": "manual",
            "graph_edge_id": "e-cccc00000003",
            "prompt_text": "Analisar indice composto",
        },
    ]


def test_classificacao_4_categorias_e_codigos_sugestao() -> None:
    """Valida que diagnosticar_avaliacao cobre as 4 categorias e gera sugestões acionáveis consultivas."""
    snap = _snapshot_sintetico()
    run_info = {"run_id": "run-eval-1", "kind": "eval", "finished_at": "2026-11-15T15:00:00+00:00"}
    router_md = "Voce delega para @python-developer, @python-arch-advisor, @bug-triage e @agente-fantasma-doc."
    golden = (
        GoldenSeed(
            id="G-001",
            suite="canonicos",
            solicitacao="Criar rota fastapi",
            agent_route="python-developer",
        ),
    )

    diag = diagnosticar_avaliacao(
        eval_run_id="run-eval-1",
        run_info=run_info,
        avaliacoes=_avaliacoes_sinteticas(),
        snapshot=snap,
        router_md_texto=router_md,
        router_agent_sha256="2" * 64,
        golden_seeds=golden,
        golden_set_sha256="3" * 64,
        min_support=2,
    )

    assert diag.aviso == AVISO_HITL
    assert diag.resumo.total_avaliacoes == 5
    assert diag.resumo.acuracia_global == pytest.approx(0.2)
    assert "e-dddd00000004" in diag.orfas.uncoverable
    assert "e-bbbb00000002" in diag.orfas.sem_golden
    assert "sql-dba" in diag.divergencias_router_md.nos_nao_citados
    assert "agente-fantasma-doc" in diag.divergencias_router_md.citados_fora_do_grafo
    assert "ghost-agent-xyz" in diag.divergencias_router_md.rotas_fantasma
    assert any(c.keyword_norm == "endpoint" and c.tipo == "exata" for c in diag.colisoes)

    codigos = {s.codigo for s in diag.sugestoes}
    categorias = {s.categoria_divergencia for s in diag.sugestoes}
    assert {"SUG-KW-ADD", "SUG-KW-COLLISION", "SUG-DISAMBIG", "SUG-GOLDEN-GAP", "SUG-ROUTER-DOC", "SUG-GRAPH-PHANTOM"}.issubset(codigos)
    assert categorias == set(CATEGORIAS_DIVERGENCIA)


def test_diagnostic_yaml_md_bit_a_bit_identicos_em_duas_execucoes(tmp_path: Path) -> None:
    """CA-05: Duas execuções sobre os mesmos dados produzem YAML e MD bit-a-bit idênticos."""
    snap = _snapshot_sintetico()
    run_info = {"run_id": "run-det", "kind": "eval", "finished_at": "2026-11-15T15:00:00+00:00"}
    avs = _avaliacoes_sinteticas()
    avs_invertidas = list(reversed(avs))

    d1 = diagnosticar_avaliacao(
        eval_run_id="run-det",
        run_info=run_info,
        avaliacoes=avs,
        snapshot=snap,
        router_md_texto="@python-developer",
        router_agent_sha256="a" * 64,
        golden_set_sha256="b" * 64,
    )
    d2 = diagnosticar_avaliacao(
        eval_run_id="run-det",
        run_info=run_info,
        avaliacoes=avs_invertidas,
        snapshot=snap,
        router_md_texto="@python-developer",
        router_agent_sha256="a" * 64,
        golden_set_sha256="b" * 64,
    )

    assert renderizar_diagnostico_yaml(d1) == renderizar_diagnostico_yaml(d2)
    assert renderizar_diagnostico_md(d1) == renderizar_diagnostico_md(d2)

    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"
    r1 = exportar_diagnostico(d1, out_dir=out1, repo_root=tmp_path, allow_root=out1)
    r2 = exportar_diagnostico(d2, out_dir=out2, repo_root=tmp_path, allow_root=out2)
    assert r1.yaml_path and r2.yaml_path and r1.md_path and r2.md_path
    assert r1.yaml_path.read_bytes() == r2.yaml_path.read_bytes()
    assert r1.md_path.read_bytes() == r2.md_path.read_bytes()


def test_newline_lf_no_windows(tmp_path: Path) -> None:
    """CA-05: Os arquivos diagnostic-*.yaml e diagnostic-*.md são gravados sempre com LF (sem CRLF)."""
    snap = _snapshot_sintetico()
    diag = diagnosticar_avaliacao(
        eval_run_id="run-lf",
        run_info={"run_id": "run-lf", "kind": "eval", "finished_at": "2026-11-15T15:00:00+00:00"},
        avaliacoes=_avaliacoes_sinteticas(),
        snapshot=snap,
        router_md_texto="@python-developer",
        router_agent_sha256="a" * 64,
    )
    out = tmp_path / ".synth"
    res = exportar_diagnostico(diag, out_dir=out, repo_root=tmp_path)
    assert res.yaml_path is not None and res.md_path is not None
    assert b"\r\n" not in res.yaml_path.read_bytes()
    assert b"\r\n" not in res.md_path.read_bytes()
    doc = yaml.safe_load(res.yaml_path.read_text(encoding="utf-8"))
    assert doc["eval_run_id"] == "run-lf"


def test_synth_diagnose_zero_chamadas_llm(tmp_path: Path, repo: SynthRepository, router_md: Path) -> None:
    """CA-05: executar_synth_diagnose e CLI synth-diagnose executam com zero chamadas ao SDK/LLM e sem exigir token."""
    gen_id = repo.criar_run(kind="generate", run_id="gen-0", status="completed")
    pid = repo.inserir_prompt(
        run_id=gen_id,
        text="Criar endpoint fastapi",
        text_norm="criar endpoint fastapi",
        sha256="sha-diag-1",
        expected_route="python-developer",
        agente_alvo="python-developer",
        dimensao_perturbacao="parafrase",
        max_similarity=0.1,
    )
    eval_id = repo.criar_run(kind="eval", run_id="eval-0", status="completed")
    repo.inserir_avaliacao(
        run_id=eval_id,
        prompt_id=pid,
        observed_route="bug-triage",
        route_source="tool_hook",
        verdict="mismatched",
        passed=False,
    )
    repo.finalizar_run(eval_id, status="completed")

    out_dir = tmp_path / ".synth"
    with patch.object(
        cli, "criar_cliente_sdk_real", side_effect=AssertionError("LLM jamais deve ser chamado em synth-diagnose")
    ):
        rel = executar_synth_diagnose(
            repo=repo,
            eval_run_id=eval_id,
            router_agent_path=router_md,
            out_dir=out_dir,
            repo_root=Path(__file__).resolve().parents[4],
            allow_root=out_dir,
        )
    assert rel.exit_code == 0
    assert (out_dir / f"diagnostic-{eval_id}.yaml").exists()
    assert (out_dir / f"diagnostic-{eval_id}.md").exists()


def test_exit_codes_diagnose_e_sanitizacao_markdown(repo: SynthRepository, router_md: Path) -> None:
    """Valida exit codes 3 (eval_run_id invalido/ausente) e sanitizacao Markdown (pipe, crase, menor-que, 240 chars)."""
    with pytest.raises(SynthEvalRunInvalidoError) as exc_info:
        executar_synth_diagnose(repo=repo, eval_run_id="inexistente", router_agent_path=router_md)
    assert exc_info.value.exit_code == 3

    gen_run = repo.criar_run(kind="generate", run_id="apenas-generate")
    with pytest.raises(SynthEvalRunInvalidoError) as exc_gen:
        executar_synth_diagnose(repo=repo, eval_run_id=gen_run, router_agent_path=router_md)
    assert exc_gen.value.exit_code == 3

    db_path = str(repo.db_path)
    assert cli.main(["--use-case", "synth-diagnose", "--db", db_path]) == 3
    assert cli.main(["--use-case", "synth-diagnose", "--db", db_path, "--eval-run-id", "nao-existe", "--router-agent", str(router_md)]) == 3

    crase = chr(96)
    sujo = " col1 | col2 " + crase + "code" + crase + " <script>alert(1)</script> " + ("x" * 300)
    limpo = sanitizar_excerto_md(sujo)
    assert len(limpo) == 240
    assert "\\|" in limpo and ("\\" + crase) in limpo and "&lt;script>" in limpo
