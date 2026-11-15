"""Testes de Blind Evaluation estrita para sementes do routing-graph (B2-03b / CA-06)."""
from __future__ import annotations

from pathlib import Path

from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.use_cases import executar_synth_eval, executar_synth_generate

from .conftest import FakeSDKClient, resposta_hook


def test_synth_eval_seed_routing_graph_recebe_apenas_prompt_text_e_system_prompt(
    repo: SynthRepository,
    router_md: Path,
) -> None:
    """CA-06: Em synth-eval sobre prompt oriundo de seed_source='routing_graph', SDKRequest não contém metadados do grafo."""
    rel_gen = executar_synth_generate(
        repo=repo,
        generator_mode="template",
        targets=["cybersecurity-advisor"],
        dimensions=["parafrase"],
        per_stratum=1,
        graph_seeding="all",
        graph_min_coverage=2,
        env={},
    )
    assert rel_gen.exit_code == 0 and rel_gen.run_id

    secret_route = "zz-blind-secret-agent"
    secret_edge = "e-deadbeef9999"
    repo.inserir_prompt(
        run_id=rel_gen.run_id,
        text="Preciso revisar cabecalhos de seguranca HTTP na API REST.",
        text_norm="preciso revisar cabecalhos de seguranca http na api rest",
        sha256="sha-blind-graph-1",
        expected_route=secret_route,
        agente_alvo="cybersecurity-advisor",
        dimensao_perturbacao="parafrase",
        seed_case_id="graph:e-deadbeef9999:0",
        seed_source="routing_graph",
        graph_edge_id=secret_edge,
        graph_edge_resolution="keyword",
        max_similarity=0.1,
    )

    prompts_banco = repo.listar_prompts(rel_gen.run_id)
    assert any(p["seed_source"] == "routing_graph" for p in prompts_banco)
    textos_validos = {p["text"] for p in prompts_banco}
    edge_ids = {p["graph_edge_id"] for p in prompts_banco if p["graph_edge_id"]}
    assert secret_edge in edge_ids

    cli = FakeSDKClient(default=resposta_hook("cybersecurity-advisor"))
    rel_eval = executar_synth_eval(
        repo=repo,
        cliente_factory=lambda: cli,
        max_premium_requests=50,
        router_agent_path=router_md,
        source_run_id=rel_gen.run_id,
        run_id="eval-blind-ca06",
        env={},
    )
    assert rel_eval.exit_code == 0
    assert len(cli.requests) == len(prompts_banco)

    conteudo_router = router_md.read_text(encoding="utf-8")
    proibidos = {
        secret_route,
        secret_edge,
        "seed_source",
        "routing_graph",
        "graph_edge_id",
        "graph_edge_resolution",
        "expected_route",
        "routing-graph.yaml",
        *edge_ids,
    }

    for req in cli.requests:
        assert req.prompt in textos_validos
        assert req.system_prompt and req.system_prompt.strip() == "Voce e o router."
        assert req.ferramentas_permitidas == ("delegar",)
        assert req.permission_handler is not None
        assert req.permission_handler("read_file", {"path": ".github/agents/routing-graph.yaml"}).permitido is False
        for termo in proibidos:
            assert termo not in req.prompt
            assert termo not in (req.system_prompt or "")

    avaliacoes = repo.listar_avaliacoes("eval-blind-ca06")
    assert len(avaliacoes) == len(prompts_banco)
    av_secreta = next(a for a in avaliacoes if a["expected_route"] == secret_route)
    assert av_secreta["verdict"] == "mismatched"
    assert av_secreta["seed_source"] == "routing_graph"
    assert av_secreta["graph_edge_id"] == secret_edge
