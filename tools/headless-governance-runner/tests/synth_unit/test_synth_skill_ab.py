"""
test_synth_skill_ab — Cobertura da integração P5 + synth (schema v4, seeds, evaluator, diagnostics e CLI synth-skill-ab).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from governance_runner.cli import construir_parser, main
from governance_runner.synth.diagnostic_exporter import (
    renderizar_diagnostico_md,
    renderizar_diagnostico_yaml,
)
from governance_runner.synth.diagnostics import diagnosticar_avaliacao
from governance_runner.synth.evaluator import avaliar_lote_skill_ab, pontuar_rubrica_skill
from governance_runner.synth.routing_graph import carregar_snapshot_grafo
from governance_runner.synth.seeds import (
    calcular_cobertura_skills,
    gerar_seeds_skills,
    identificar_skills_uncoverable,
)
from governance_runner.synth.storage import SCHEMA_VERSION, SynthRepository, migrar_conexao
from governance_runner.synth.use_cases import (
    executar_synth_diagnose,
    executar_synth_generate,
    executar_synth_skill_ab,
)


def _criar_workspace_skill_ab(tmp_path: Path) -> tuple[Path, Path, Path]:
    skills_dir = tmp_path / ".github" / "skills"
    s1 = skills_dir / "code-review-governed"
    s1.mkdir(parents=True)
    (s1 / "SKILL.md").write_text(
        "---\n"
        "name: code-review-governed\n"
        "description: Revisao tecnica com rastreabilidade R-004\n"
        "---\n"
        "# Regra\n"
        "OBRIGATORIO citar `R-004` e verificar `CHANGELOG.md`.\n"
        "NUNCA aprovar sem evidencia objetiva.\n",
        encoding="utf-8",
    )

    s2 = skills_dir / "skill-sem-clausula"
    s2.mkdir(parents=True)
    (s2 / "SKILL.md").write_text(
        "---\nname: skill-sem-clausula\ndescription: Texto livre sem clausulas\n---\nApenas orientacao geral.\n",
        encoding="utf-8",
    )

    cases_path = tmp_path / "tests" / "evals" / "skill_ab_cases.yaml"
    cases_path.parent.mkdir(parents=True)
    cases_path.write_text(
        "version: 1\n"
        "cases:\n"
        "  - case_id: ab-cr-01\n"
        "    skill_name: code-review-governed\n"
        "    baseline_prompt: Revise este diff de autenticacao.\n"
        "    required_clauses:\n"
        "      - R-004\n"
        "      - CHANGELOG.md\n"
        "    forbidden_antipatterns:\n"
        "      - aprovar sem evidencia objetiva\n"
        "    min_delta_utility: 0.25\n",
        encoding="utf-8",
    )

    golden_path = tmp_path / "tests" / "evals" / "routing_golden_set.yaml"
    golden_path.write_text(
        "version: 1\n"
        "cases:\n"
        "  - id: gs-01\n"
        "    prompt: Preciso revisar um pull request no backend.\n"
        "    expected_agent_route: code-reviewer\n",
        encoding="utf-8",
    )
    return skills_dir, cases_path, golden_path


def _criar_grafo_e_router_minimos(tmp_path: Path) -> tuple[Path, Path]:
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    grafo_path = agents_dir / "routing-graph.yaml"
    grafo_path.write_text(
        "version: '1.0'\n"
        "nos:\n"
        "  - id: agent-router\n"
        "    tipo: entry_point\n"
        "    descricao: Roteador central\n"
        "  - id: code-reviewer\n"
        "    tipo: downstream\n"
        "    descricao: Revisor de codigo\n"
        "arestas:\n"
        "  - de: agent-router\n"
        "    para: code-reviewer\n"
        "    prioridade: 1\n"
        "    nivel_routing: L1\n"
        "    threshold_score: 0.5\n"
        "    condicoes:\n"
        "      tipo: keyword_based\n"
        "      keywords:\n"
        "        - pull request\n"
        "        - revisar\n"
        "workflows: []\n",
        encoding="utf-8",
    )
    router_path = agents_dir / "agent-router.agent.md"
    router_path.write_text(
        "# Agent Router\nDelegar revisoes de pull request para @code-reviewer.\n",
        encoding="utf-8",
    )
    return grafo_path, router_path

def test_migracao_v3_para_v4_e_persistencia_skill_ab(tmp_path: Path) -> None:
    assert SCHEMA_VERSION == "4"
    db_file = tmp_path / "synth_v3.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA user_version = 3")
    conn.execute(
        """
        CREATE TABLE synth_runs (
                                    run_id                 TEXT PRIMARY KEY,
                                    kind                   TEXT NOT NULL CHECK (kind IN ('generate','eval','export','promote')),
                                    parent_run_id          TEXT,
                                    started_at             TEXT NOT NULL,
                                    finished_at            TEXT,
                                    status                 TEXT NOT NULL CHECK (status IN ('running','completed','neutral','failed')),
                                    motivo                 TEXT,
                                    generator              TEXT,
                                    model                  TEXT,
                                    rng_seed               INTEGER,
                                    params_json            TEXT NOT NULL DEFAULT '{}',
                                    router_agent_sha256    TEXT,
                                    golden_set_sha256      TEXT,
                                    routing_graph_sha256   TEXT,
                                    premium_requests_used  INTEGER NOT NULL DEFAULT 0,
                                    n_candidates           INTEGER NOT NULL DEFAULT 0,
                                    n_rejected_hash        INTEGER NOT NULL DEFAULT 0,
                                    n_rejected_similarity  INTEGER NOT NULL DEFAULT 0,
                                    n_rejected_override    INTEGER NOT NULL DEFAULT 0,
                                    n_accepted             INTEGER NOT NULL DEFAULT 0,
                                    trace_id               TEXT
        )
        """
    )
    conn.commit()
    versao = migrar_conexao(conn)
    assert versao == "4"
    assert int(conn.execute("PRAGMA user_version").fetchone()[0]) == 4
    conn.close()

    with SynthRepository(db_file) as repo:
        rid = repo.criar_run(kind="skill_ab", status="running")
        repo.inserir_avaliacao_skill_ab(
            run_id=rid,
            case_id="ab-01",
            skill_name="code-review-governed",
            baseline_score=0.25,
            treatment_score=0.90,
            delta_utility=0.65,
            min_delta_utility=0.10,
            redundant=False,
            passed=True,
        )
        assert repo.reconciliar_runs_orfaos(rid) == 1
        run_row = repo.obter_run(rid)
        assert run_row is not None and run_row["status"] == "completed"
        itens = repo.listar_avaliacoes_skill_ab(run_id=rid)
        assert len(itens) == 1
        assert itens[0]["delta_utility"] == pytest.approx(0.65)


def test_seeds_skills_cobertura_e_uncoverable(tmp_path: Path) -> None:
    skills_dir, cases_path, _ = _criar_workspace_skill_ab(tmp_path)
    cov = calcular_cobertura_skills(skills_dir=skills_dir, cases_path=cases_path, repo_root=tmp_path)
    assert cov == {"code-review-governed": 1, "skill-sem-clausula": 0}

    uncoverable = identificar_skills_uncoverable(skills_dir=skills_dir, repo_root=tmp_path)
    assert uncoverable == ("skill-sem-clausula",)

    seeds_all = gerar_seeds_skills(
        modo="all",
        skills_dir=skills_dir,
        cases_path=cases_path,
        repo_root=tmp_path,
    )
    assert len(seeds_all) == 1
    assert seeds_all[0].skill_name == "code-review-governed"
    assert seeds_all[0].seed_source == "skill_ab"


def test_avaliador_rubrica_e_lote_ab(tmp_path: Path) -> None:
    skills_dir, _, _ = _criar_workspace_skill_ab(tmp_path)
    score_ok, missing, triggered = pontuar_rubrica_skill(
        "Validacao conforme R-004 registrada no CHANGELOG.md.",
        required_clauses=("R-004", "CHANGELOG.md"),
        forbidden_antipatterns=("aprovar sem evidencia objetiva",),
    )
    assert score_ok == pytest.approx(1.0)
    assert missing == ()
    assert triggered == ()

    rel = avaliar_lote_skill_ab(
        [
            {
                "case_id": "ab-cr-01",
                "skill_name": "code-review-governed",
                "baseline_prompt": "Revise este diff.",
                "required_clauses": ["R-004", "CHANGELOG.md"],
                "min_delta_utility": 0.25,
            }
        ],
        skills_dir=skills_dir,
    )
    assert rel.total_cases == 1
    assert rel.passed_cases == 1
    assert rel.redundant_cases == 0
    assert rel.mean_delta_utility == pytest.approx(1.0)


def test_use_case_synth_skill_ab_e_generate_com_skill_seeding(tmp_path: Path) -> None:
    skills_dir, cases_path, golden_path = _criar_workspace_skill_ab(tmp_path)
    db_path = tmp_path / ".cache" / "synth.db"

    with SynthRepository(db_path, repo_root=tmp_path) as repo:
        rel_gen = executar_synth_generate(
            repo=repo,
            generator_mode="template",
            golden_path=golden_path,
            skill_seeding="all",
            skills_dir=skills_dir,
            skill_cases_path=cases_path,
            per_stratum=1,
            repo_root=tmp_path,
        )
        assert rel_gen.exit_code == 0
        assert rel_gen.contadores["n_skill_seeds_generated"] == 1

        rel_ab = executar_synth_skill_ab(
            repo=repo,
            cases_path=cases_path,
            skills_dir=skills_dir,
            generator_mode="template",
            repo_root=tmp_path,
        )
        assert rel_ab.exit_code == 0
        assert rel_ab.contadores["total_cases"] == 1
        assert rel_ab.contadores["passed_cases"] == 1
        assert rel_ab.mean_skill_delta_utility == pytest.approx(1.0)


def test_cli_synth_skill_ab_flags_e_execucao(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    parser = construir_parser()
    args = parser.parse_args(
        [
            "--use-case",
            "synth-skill-ab",
            "--skill-seeding",
            "gaps",
            "--skills",
            "code-review-governed",
            "--include-skill-gaps",
            "--skill-ab-run-id",
            "ab-run-123",
        ]
    )
    assert args.use_case == "synth-skill-ab"
    assert args.skill_seeding == "gaps"
    assert args.skills == "code-review-governed"
    assert args.include_skill_gaps is True
    assert args.skill_ab_run_id == "ab-run-123"

    _, cases_path, _ = _criar_workspace_skill_ab(tmp_path)
    db_path = tmp_path / ".cache" / "cli_synth.db"
    monkeypatch.chdir(tmp_path)

    rc = main(
        [
            "--use-case",
            "synth-skill-ab",
            "--db",
            str(db_path),
            "--skill-cases",
            str(cases_path),
            "--generator-mode",
            "template",
        ]
    )
    assert rc == 0


class _ClienteSdkFake:
    def avaliar(self, prompt: str, *, modelo: str | None = None) -> SimpleNamespace:
        if "<active_skill" in prompt:
            return SimpleNamespace(
                texto="Rota: code-reviewer\nAplicado R-004 e atualizado CHANGELOG.md.",
                premium_requests_consumidas=1,
            )
        return SimpleNamespace(texto="Rota: code-reviewer\nDiff revisado.", premium_requests_consumidas=1)


def test_executar_synth_skill_ab_modo_sdk(tmp_path: Path) -> None:
    skills_dir, cases_path, _ = _criar_workspace_skill_ab(tmp_path)
    db_path = tmp_path / ".cache" / "sdk_synth.db"
    with SynthRepository(db_path, repo_root=tmp_path) as repo:
        rel = executar_synth_skill_ab(
            repo=repo,
            cases_path=cases_path,
            skills_dir=skills_dir,
            generator_mode="sdk",
            max_premium_requests=4,
            cliente_factory=lambda: _ClienteSdkFake(),
            repo_root=tmp_path,
        )
        assert rel.exit_code == 0
        assert rel.contadores["premium_requests_used"] == 2
        assert rel.contadores["passed_cases"] == 1


def test_diagnostics_emite_sugestoes_skill_redundante_e_lacunas_cobertura(tmp_path: Path) -> None:
    grafo_path, _ = _criar_grafo_e_router_minimos(tmp_path)
    snapshot = carregar_snapshot_grafo(grafo_path, repo_root=tmp_path)

    diag = diagnosticar_avaliacao(
        eval_run_id="eval-01",
        run_info={"run_id": "eval-01", "kind": "eval", "finished_at": "2026-11-20T12:00:00+00:00"},
        avaliacoes=[
            {
                "eval_id": "ev-1",
                "prompt_id": "p-1",
                "prompt_text": "Preciso revisar um pull request.",
                "expected_route": "code-reviewer",
                "observed_route": "code-reviewer",
                "verdict": "matched",
                "passed": 1,
                "seed_source": "manual",
            }
        ],
        snapshot=snapshot,
        router_md_texto="Delegar para @code-reviewer.",
        router_agent_sha256="sha-router",
        skill_ab_run_id="ab-run-01",
        skill_ab_evals=[
            {
                "skill_eval_id": "se-1",
                "case_id": "ab-red-01",
                "skill_name": "skill-redundante",
                "baseline_score": 0.80,
                "treatment_score": 0.82,
                "delta_utility": 0.02,
                "min_delta_utility": 0.15,
                "redundant": 1,
                "passed": 0,
                "missing_clauses_json": '["R-009"]',
                "triggered_anti_json": "[]",
            }
        ],
        skills_cobertura={
            "skill-redundante": 1,
            "skill-sem-caso": 0,
            "skill-sem-clausula": 0,
        },
        skills_uncoverable=("skill-sem-clausula",),
    )

    assert diag.resumo.skills_avaliadas == 1
    assert diag.resumo.skills_redundantes == 1
    assert diag.resumo.skills_sem_cobertura == 2
    assert diag.resumo.mean_skill_delta_utility == pytest.approx(0.02)

    codigos = {s.codigo: s for s in diag.sugestoes}
    assert "SUG-SKILL-REDUNDANT" in codigos
    assert codigos["SUG-SKILL-REDUNDANT"].alvo_ancora == "skill:skill-redundante"
    assert codigos["SUG-SKILL-REDUNDANT"].evidencias == ("ab-red-01",)
    assert "R-009" in codigos["SUG-SKILL-REDUNDANT"].proposta_texto

    assert "SUG-SKILL-COVERAGE-GAP" in codigos
    assert codigos["SUG-SKILL-COVERAGE-GAP"].alvo_ancora == "skill:skill-sem-caso"

    assert "SUG-SKILL-UNCOVERABLE" in codigos
    assert codigos["SUG-SKILL-UNCOVERABLE"].alvo_ancora == "skill:skill-sem-clausula"

    yaml_txt = renderizar_diagnostico_yaml(diag)
    payload = yaml.safe_load(yaml_txt)
    assert payload["skills_ab"]["skill_ab_run_id"] == "ab-run-01"
    assert payload["skills_ab"]["metricas"][0]["redundant"] is True
    assert payload["skills_ab"]["orfas"]["sem_cobertura_ab"] == ["skill-sem-caso", "skill-sem-clausula"]
    assert payload["skills_ab"]["orfas"]["uncoverable"] == ["skill-sem-clausula"]

    md_txt = renderizar_diagnostico_md(diag)
    assert "## Avaliação Pareada de Skills (A/B)" in md_txt
    assert "SUG-SKILL-REDUNDANT" in md_txt
    assert "SUG-SKILL-COVERAGE-GAP" in md_txt
    assert "SUG-SKILL-UNCOVERABLE" in md_txt


def test_executar_synth_diagnose_integra_ultimo_run_skill_ab_e_cobertura(tmp_path: Path) -> None:
    skills_dir, cases_path, golden_path = _criar_workspace_skill_ab(tmp_path)
    grafo_path, router_path = _criar_grafo_e_router_minimos(tmp_path)
    s3 = skills_dir / "skill-gap-cobertura"
    s3.mkdir(parents=True)
    (s3 / "SKILL.md").write_text(
        "---\nname: skill-gap-cobertura\ndescription: Skill sem caso AB\n---\nOBRIGATORIO validar `R-010`.\n",
        encoding="utf-8",
    )

    db_path = tmp_path / ".cache" / "diag_skill_ab.db"
    out_dir = tmp_path / ".synth" / "diag"

    with SynthRepository(db_path, repo_root=tmp_path) as repo:
        ab_run_id = repo.criar_run(kind="skill_ab", status="running")
        repo.inserir_avaliacao_skill_ab(
            run_id=ab_run_id,
            case_id="ab-cr-01",
            skill_name="code-review-governed",
            baseline_score=0.70,
            treatment_score=0.72,
            delta_utility=0.02,
            min_delta_utility=0.25,
            redundant=True,
            passed=False,
            missing_clauses=("CHANGELOG.md",),
        )
        repo.finalizar_run(ab_run_id, status="completed", n_candidates=1, n_accepted=0)

        eval_run_id = repo.criar_run(kind="eval", status="running")
        pid = repo.inserir_prompt(
            run_id=eval_run_id,
            text="Revisar pull request",
            text_norm="revisar pull request",
            sha256="hash-p1",
            expected_route="code-reviewer",
            agente_alvo="code-reviewer",
            dimensao_perturbacao="parafrase",
        )
        repo.inserir_avaliacao(
            run_id=eval_run_id,
            prompt_id=pid,
            observed_route="code-reviewer",
            route_source="tool_hook",
            verdict="matched",
            passed=True,
        )
        repo.finalizar_run(eval_run_id, status="completed", n_candidates=1, n_accepted=1)

        rel_diag = executar_synth_diagnose(
            repo=repo,
            eval_run_id=eval_run_id,
            routing_graph_path=grafo_path,
            router_agent_path=router_path,
            golden_path=golden_path,
            skills_dir=skills_dir,
            skill_cases_path=cases_path,
            out_dir=out_dir,
            formato="both",
            repo_root=tmp_path,
        )

        assert rel_diag.exit_code == 0
        assert rel_diag.contadores["n_skills_redundantes"] == 1
        assert rel_diag.contadores["n_skills_sem_cobertura"] == 2
        assert rel_diag.mean_skill_delta_utility == pytest.approx(0.02)
        assert len(rel_diag.caminhos_gerados) == 2

        yaml_gerado = Path(rel_diag.caminhos_gerados[0]).read_text(encoding="utf-8")
        md_gerado = Path(rel_diag.caminhos_gerados[1]).read_text(encoding="utf-8")
        assert "SUG-SKILL-REDUNDANT" in yaml_gerado
        assert "SUG-SKILL-COVERAGE-GAP" in yaml_gerado
        assert "SUG-SKILL-UNCOVERABLE" in yaml_gerado
        assert "## Avaliação Pareada de Skills (A/B)" in md_gerado
