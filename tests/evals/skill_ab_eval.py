"""Avaliador A/B de Utilidade de Skills (Treatment vs. Baseline — P5).

Calcula o ganho marginal (delta_utility = score_treatment - score_baseline)
de cada skill frente a tarefas reais do ecossistema, sinalizando skills
redundantes (delta_utility <= 0) para poda ou refatoração.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = Path(__file__).resolve().parent / "skill_ab_cases.yaml"
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"


@dataclass
class SkillABResult:
    case_id: str
    skill: str
    skill_exists: bool
    baseline_score: float
    treatment_score: float
    delta_utility: float
    min_delta_utility: float
    passed: bool
    redundant_signal: bool
    missing_in_baseline: list[str]
    missing_in_treatment: list[str]
    skill_line_count: int


def load_skill_corpus(skill_name: str, skills_root: Path = SKILLS_ROOT) -> tuple[bool, str, int]:
    """Carrega o SKILL.md e suas referências imediatas para compor o contexto Treatment."""
    skill_dir = skills_root / skill_name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "", 0

    parts: list[str] = [skill_md.read_text(encoding="utf-8", errors="replace")]
    line_count = len(parts[0].splitlines())

    refs_dir = skill_dir / "references"
    if refs_dir.exists() and refs_dir.is_dir():
        for ref_file in sorted(refs_dir.glob("*")):
            if ref_file.is_file() and ref_file.suffix.lower() in {".md", ".yaml", ".yml", ".json"}:
                parts.append(ref_file.read_text(encoding="utf-8", errors="replace"))

    return True, "\n\n".join(parts), line_count


def score_corpus_against_rubric(
    text: str,
    required_clauses: list[str],
    forbidden_antipatterns: list[str],
) -> tuple[float, list[str]]:
    """Pontua um texto/contexto entre 0.0 e 1.0 contra cláusulas obrigatórias e anti-padrões."""
    if not required_clauses:
        return 1.0, []

    lowered = text.lower()
    missing = [clause for clause in required_clauses if clause.lower() not in lowered]
    matched = len(required_clauses) - len(missing)
    raw_score = matched / len(required_clauses)

    penalties = sum(0.25 for anti in forbidden_antipatterns if anti.lower() in lowered)
    final_score = max(0.0, round(raw_score - penalties, 4))
    return final_score, missing


def evaluate_skill_ab_cases(
    cases_path: Path = DEFAULT_CASES_PATH,
    skills_root: Path = SKILLS_ROOT,
) -> dict[str, Any]:
    """Executa todos os pares Baseline vs. Treatment e retorna relatório estruturado."""
    payload = yaml.safe_load(cases_path.read_text(encoding="utf-8")) or {}
    raw_cases = payload.get("cases") or []

    results: list[SkillABResult] = []
    for case in raw_cases:
        case_id = str(case["id"])
        skill_name = str(case["skill"])
        baseline_text = str(case.get("baseline_output") or "")
        required_clauses = [str(c) for c in (case.get("required_clauses") or [])]
        forbidden_antipatterns = [str(a) for a in (case.get("forbidden_antipatterns") or [])]
        min_delta = float(case.get("min_delta_utility", 0.25))

        skill_exists, skill_corpus, line_count = load_skill_corpus(skill_name, skills_root=skills_root)
        treatment_text = f"{baseline_text}\n\n{skill_corpus}" if skill_exists else baseline_text

        base_score, missing_base = score_corpus_against_rubric(
            baseline_text, required_clauses, forbidden_antipatterns
        )
        treat_score, missing_treat = score_corpus_against_rubric(
            treatment_text, required_clauses, forbidden_antipatterns
        )
        delta = round(treat_score - base_score, 4)
        redundant = delta <= 0.0
        passed = skill_exists and (delta >= min_delta) and (len(missing_treat) == 0)

        results.append(
            SkillABResult(
                case_id=case_id,
                skill=skill_name,
                skill_exists=skill_exists,
                baseline_score=base_score,
                treatment_score=treat_score,
                delta_utility=delta,
                min_delta_utility=min_delta,
                passed=passed,
                redundant_signal=redundant,
                missing_in_baseline=missing_base,
                missing_in_treatment=missing_treat,
                skill_line_count=line_count,
            )
        )

    passed_count = sum(1 for r in results if r.passed)
    redundant_skills = sorted({r.skill for r in results if r.redundant_signal})
    avg_delta = (
        round(sum(r.delta_utility for r in results) / len(results), 4) if results else 0.0
    )

    return {
        "verdict": "PASS" if passed_count == len(results) else "FAIL",
        "total_cases": len(results),
        "passed_cases": passed_count,
        "average_delta_utility": avg_delta,
        "redundant_skills": redundant_skills,
        "results": [asdict(r) for r in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Eval A/B de Utilidade de Skills (Treatment vs. Baseline - P5)."
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Caminho para o arquivo YAML de casos A/B.",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=SKILLS_ROOT,
        help="Diretório raiz das skills (.github/skills).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emite relatório completo em JSON.",
    )
    args = parser.parse_args(argv)

    report = evaluate_skill_ab_cases(
        cases_path=args.cases.resolve(),
        skills_root=args.skills_root.resolve(),
    )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"Skill A/B Eval Verdict: {report['verdict']} "
            f"({report['passed_cases']}/{report['total_cases']} casos | "
            f"delta medio: +{report['average_delta_utility']:.2f})"
        )
        for item in report["results"]:
            status = "PASS" if item["passed"] else "FAIL"
            print(
                f"  [{status}] {item['skill']} ({item['case_id']}): "
                f"baseline={item['baseline_score']:.2f} -> treatment={item['treatment_score']:.2f} "
                f"(delta={item['delta_utility']:+.2f})"
            )
            if item["redundant_signal"]:
                print(f"         [REDUNDANT_SKILL_WARNING] delta <= 0 para '{item['skill']}'")

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(main())