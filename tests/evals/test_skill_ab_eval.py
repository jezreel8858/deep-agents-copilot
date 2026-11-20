"""Testes determinísticos do Avaliador A/B de Utilidade de Skills (P5)."""

from __future__ import annotations

from pathlib import Path

from tests.evals.skill_ab_eval import evaluate_skill_ab_cases


def test_canonical_skills_achieve_positive_ab_delta() -> None:
    report = evaluate_skill_ab_cases()
    assert report["verdict"] == "PASS", f"Falha no Eval A/B: {report}"
    assert report["total_cases"] >= 4
    assert report["average_delta_utility"] >= 0.50
    assert report["redundant_skills"] == []


def test_ab_eval_flags_redundant_skill_with_zero_delta(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    dummy_skill = skills_dir / "dummy-noop-skill"
    dummy_skill.mkdir(parents=True)
    (dummy_skill / "SKILL.md").write_text(
        "---\nname: dummy-noop-skill\ndescription: Skill vazia sem regras úteis\n---\n# Dummy\n",
        encoding="utf-8",
    )

    cases_file = tmp_path / "cases.yaml"
    cases_file.write_text(
        "cases:\n"
        '  - id: "ab-noop-01"\n'
        '    skill: "dummy-noop-skill"\n'
        '    baseline_output: "Resposta genérica sem contrato"\n'
        "    required_clauses:\n"
        '      - "receipt"\n'
        '      - "allowed_files"\n'
        "    min_delta_utility: 0.25\n",
        encoding="utf-8",
    )

    report = evaluate_skill_ab_cases(cases_path=cases_file, skills_root=skills_dir)
    assert report["verdict"] == "FAIL"
    assert report["redundant_skills"] == ["dummy-noop-skill"]
    assert report["results"][0]["delta_utility"] == 0.0