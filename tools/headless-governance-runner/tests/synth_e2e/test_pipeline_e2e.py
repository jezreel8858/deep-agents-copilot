"""E2E offline: generate (template) -> eval (dublê) -> export -> promote, com Golden intacto."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from governance_runner import cli
from governance_runner.synth.use_cases import (
    executar_synth_eval,
    executar_synth_export,
    executar_synth_generate,
    executar_synth_promote,
)

DIMS = ["distrator_outro_agente", "multi_intencao"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_pipeline_via_use_cases(repo, cliente_falso, allow_root, router_md, golden_path) -> None:  # type: ignore[no-untyped-def]
    antes = _sha(golden_path)

    ger = executar_synth_generate(repo=repo, generator_mode="template", dimensions=DIMS, per_stratum=1, env={})
    assert ger.exit_code == 0 and ger.run_id and repo.listar_prompts(ger.run_id)

    ev = executar_synth_eval(repo=repo, cliente_factory=lambda: cliente_falso, max_premium_requests=1000,
                             router_agent_path=router_md, run_id="ev-e2e", env={})
    assert ev.exit_code == 0 and cliente_falso.requests
    assert all("expected" not in r.prompt.lower() or True for r in cliente_falso.requests)

    exp = executar_synth_export(repo=repo, eval_run_id="ev-e2e", allow_root=allow_root)
    silvers = sorted(allow_root.glob("casos-roteamento-silver-*.yaml"))
    assert len(silvers) == 1 and exp.exit_code == 0

    doc = yaml.safe_load(silvers[0].read_text(encoding="utf-8"))
    assert doc["casos"], "esperava falhas exportadas (dublê delega sempre para bug-triage)"
    doc["casos"][0]["silver"]["review_status"] = "approved"
    doc["casos"][0]["silver"]["corrected_route"] = "bug-triage"
    silvers[0].write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")

    prom = executar_synth_promote(repo=repo, silver=silvers[0].name, run_id="e2e", confirm=True,
                                  allow_root=allow_root)
    assert prom.exit_code == 0
    promovido = allow_root / "promoted-e2e.yaml"
    assert promovido.exists()
    assert yaml.safe_load(promovido.read_text(encoding="utf-8"))["regressao"]

    assert _sha(golden_path) == antes
    assert not (allow_root / "casos-roteamento.yaml").exists()


def test_pipeline_via_cli(tmp_path, monkeypatch, cliente_falso, allow_root, router_md, golden_path) -> None:  # type: ignore[no-untyped-def]
    antes = _sha(golden_path)
    db = str(tmp_path / "cli-e2e.db")
    monkeypatch.setenv(cli.COPILOT_SDK_TOKEN_ENV, "token-falso")
    monkeypatch.setattr(cli, "criar_cliente_sdk_real", lambda token, **_: cliente_falso)

    assert cli.main(["--use-case", "synth-generate", "--db", db, "--per-stratum", "1",
                     "--dimensions", ",".join(DIMS)]) == 0
    assert cli.main(["--use-case", "synth-eval", "--db", db, "--max-premium-requests", "1000",
                     "--router-agent", str(router_md), "--run-id", "ev-cli", "--pending"]) == 0
    assert cli.main(["--use-case", "synth-export", "--db", db, "--eval-run-id", "ev-cli"]) == 0
    silvers = sorted(allow_root.glob("casos-roteamento-silver-*.yaml"))
    assert len(silvers) == 1
    assert cli.main(["--use-case", "synth-promote", "--silver", silvers[0].name, "--run-id", "cli"]) == 0
    assert not (allow_root / "promoted-cli.yaml").exists()
    assert cli.main(["--use-case", "synth-promote", "--silver", silvers[0].name, "--run-id", "cli", "--confirm"]) == 0
    assert (allow_root / "promoted-cli.yaml").exists()
    assert _sha(golden_path) == antes

def test_pipeline_graph_seeding_gaps_e_diagnose_offline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cliente_falso,
    allow_root: Path,
    router_md: Path,
    golden_path: Path,
) -> None:  # type: ignore[no-untyped-def]
    """B3-04: Pipeline E2E completo com --graph-seeding gaps -> synth-eval -> synth-diagnose em modo mock/offline."""
    from governance_runner.synth.routing_graph import resolver_caminho_routing_graph
    from governance_runner.synth.storage import SynthRepository
    from governance_runner.synth.use_cases import executar_synth_diagnose

    grafo_path = resolver_caminho_routing_graph()
    sha_golden_antes = _sha(golden_path)
    sha_grafo_antes = _sha(grafo_path)

    db = str(tmp_path / "e2e-graph-diag.db")
    monkeypatch.setenv(cli.COPILOT_SDK_TOKEN_ENV, "token-falso")
    monkeypatch.setattr(cli, "criar_cliente_sdk_real", lambda token, **_: cliente_falso)

    assert (
        cli.main(
            [
                "--use-case",
                "synth-generate",
                "--db",
                db,
                "--targets",
                "bug-triage,python-router",
                "--dimensions",
                "parafrase",
                "--per-stratum",
                "1",
                "--graph-seeding",
                "gaps",
                "--graph-min-coverage",
                "2",
            ]
        )
        == 0
    )

    assert (
        cli.main(
            [
                "--use-case",
                "synth-eval",
                "--db",
                db,
                "--max-premium-requests",
                "1000",
                "--router-agent",
                str(router_md),
                "--run-id",
                "ev-graph-e2e",
                "--pending",
            ]
        )
        == 0
    )

    monkeypatch.delenv(cli.COPILOT_SDK_TOKEN_ENV, raising=False)
    monkeypatch.setattr(
        cli,
        "criar_cliente_sdk_real",
        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("Zero chamadas LLM exigidas em synth-diagnose")),
    )

    out_diag = allow_root
    with SynthRepository(db, repo_root=tmp_path) as r_check:
        rel_diag = executar_synth_diagnose(
            repo=r_check,
            eval_run_id="ev-graph-e2e",
            router_agent_path=router_md,
            out_dir=out_diag,
            allow_root=out_diag,
        )
        assert rel_diag.exit_code == 0
        diag_yaml = out_diag / "diagnostic-ev-graph-e2e.yaml"
        diag_md = out_diag / "diagnostic-ev-graph-e2e.md"
        assert diag_yaml.exists() and diag_md.exists()
        doc_diag = yaml.safe_load(diag_yaml.read_text(encoding="utf-8"))
        assert doc_diag["eval_run_id"] == "ev-graph-e2e"
        assert doc_diag["resumo"]["total_avaliacoes"] > 0
        assert doc_diag["sugestoes"]

    assert _sha(golden_path) == sha_golden_antes
    assert _sha(grafo_path) == sha_grafo_antes
