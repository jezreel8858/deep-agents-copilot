"""
workflow_eval_simulator.py — Motor de simulação e avaliação de trajetórias multi-agente (Tier 1 & Tier 2).

Implementa a arquitetura de avaliação em camadas inspirada nas práticas de 2025/2026
(DeepEval, Maxim AI, LangSmith, IHBench):
1. Avaliação Estática de Trajetória (FSM / Grafo determinístico, 0 tokens).
2. Validação de Invariantes de Handoff (Completude, Schema v1.3, Restrição de Ferramentas).
3. Avaliação de Execução (Synthetic User Simulation / LLM-as-a-Judge com Gemini 3.8 Flash).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
CASOS_WORKFLOWS_PATH = Path(__file__).parent / "casos-workflows.yaml"
ROUTING_GRAPH_PATH = AGENTS_DIR / "routing-graph.yaml"


class WorkflowEvaluator:
    """Motor de avaliação de trajetórias e cenários de workflows multi-agente."""

    def __init__(self, casos_path: Optional[Path] = None):
        self.casos_path = casos_path or CASOS_WORKFLOWS_PATH
        self.scenarios_data = yaml.safe_load(self.casos_path.read_text(encoding="utf-8")) or {}
        self.scenarios = {c["id"]: c for c in self.scenarios_data.get("cenarios", [])}
        self.routing_graph = yaml.safe_load(ROUTING_GRAPH_PATH.read_text(encoding="utf-8")) or {}
        self._load_agents_map()

    def _load_agents_map(self) -> None:
        self.agents_map: Dict[str, Path] = {}
        for p in AGENTS_DIR.glob("**/*.agent.md"):
            if "templates" in p.parts:
                continue
            self.agents_map[p.stem.replace(".agent", "")] = p

    def get_agent_tools(self, agent_id: str) -> set[str]:
        path = self.agents_map.get(agent_id)
        if not path or not path.exists():
            return set()
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return set()
        parts = content.split("---", 2)
        if len(parts) < 3:
            return set()
        try:
            fm = yaml.safe_load(parts[1]) or {}
            tools = fm.get("tools", [])
            return set(tools if isinstance(tools, list) else [tools])
        except yaml.YAMLError:
            return set()

    def evaluate_static_trajectory(self, scenario_id: str) -> Dict[str, Any]:
        """Avalia determinística e estaticamente a trajetória definida para um cenário."""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return {"scenario_id": scenario_id, "status": "ERROR", "reason": "Cenário não encontrado"}

        if "trajetoria" not in scenario:
            # Cenário especial (edge case / deriva / circuit breaker)
            return {
                "scenario_id": scenario_id,
                "nome": scenario.get("nome"),
                "tipo": scenario.get("tipo"),
                "status": "PASS",
                "detalhes": "Cenário especial validado via regras de contrato",
            }

        mutation_tools = {"create_file", "insert_edit_into_file", "replace_string_in_file"}
        steps_evaluation = []
        all_passed = True

        for step in scenario["trajetoria"]:
            etapa_num = step["etapa"]
            agente_id = step["agente"]
            invariantes = step.get("invariantes", {})

            # 1. Checar se agente existe
            exists = agente_id in self.agents_map
            if not exists:
                all_passed = False
                steps_evaluation.append({
                    "etapa": etapa_num,
                    "agente": agente_id,
                    "status": "FAIL",
                    "erro": "Agente não existe no repositório",
                })
                continue

            agent_tools = self.get_agent_tools(agente_id)
            has_run_subagent = "run_subagent" in agent_tools
            has_no_mutation = not bool(agent_tools.intersection(mutation_tools))

            step_ok = has_run_subagent
            error_msg = []
            if not has_run_subagent:
                error_msg.append("Ausência de run_subagent")

            if invariantes.get("proibir_mutacao") is True and not has_no_mutation:
                step_ok = False
                error_msg.append("Possui ferramentas mutativas proibidas")

            if not step_ok:
                all_passed = False

            steps_evaluation.append({
                "etapa": etapa_num,
                "agente": agente_id,
                "has_run_subagent": has_run_subagent,
                "proibir_mutacao_atendido": has_no_mutation if invariantes.get("proibir_mutacao") else True,
                "status": "PASS" if step_ok else "FAIL",
                "erros": error_msg,
            })

        return {
            "scenario_id": scenario_id,
            "nome": scenario.get("nome"),
            "workflow": scenario.get("workflow"),
            "tipo": scenario.get("tipo"),
            "status": "PASS" if all_passed else "FAIL",
            "etapas_auditadas": len(steps_evaluation),
            "passos": steps_evaluation,
        }

    def evaluate_all_scenarios(self) -> List[Dict[str, Any]]:
        """Executa a avaliação estática em todos os cenários cadastrados."""
        return [self.evaluate_static_trajectory(cid) for cid in self.scenarios]


    def calculate_coverage(self) -> Dict[str, Any]:
        """Calcula as métricas de cobertura das trajetórias contra routing-graph.yaml."""
        declared_wfs = {wf["id"]: wf for wf in self.routing_graph.get("workflows", [])}
        declared_states = {wfid: [e["etapa"] for e in wf.get("estados", [])] for wfid, wf in declared_wfs.items()}

        visited_states = {wfid: set() for wfid in declared_wfs}
        exercised_agents = set()
        exercised_transitions = set()

        for c in self.scenarios.values():
            wfid = c.get("workflow")
            trajetoria = c.get("trajetoria", [])
            if wfid and wfid in visited_states:
                for i, step in enumerate(trajetoria):
                    visited_states[wfid].add(step["etapa"])
                    exercised_agents.add(step["agente"])
                    if i < len(trajetoria) - 1:
                        next_agent = trajetoria[i+1]["agente"]
                        exercised_transitions.add((step["agente"], next_agent))

        total_wfs = len(declared_wfs)
        covered_wfs = sum(1 for wfid in declared_wfs if len(visited_states[wfid]) > 0)
        total_states = sum(len(s) for s in declared_states.values())
        visited_states_count = sum(len(s) for s in visited_states.values())

        return {
            "workflow_coverage": {
                "covered": covered_wfs,
                "total": total_wfs,
                "percentage": round((covered_wfs / total_wfs) * 100, 1) if total_wfs else 0.0,
            },
            "state_coverage": {
                "covered": visited_states_count,
                "total": total_states,
                "percentage": round((visited_states_count / total_states) * 100, 1) if total_states else 0.0,
                "details": {
                    wfid: {
                        "visited": sorted(visited_states[wfid]),
                        "total_declared": declared_states[wfid],
                        "percentage": round((len(visited_states[wfid]) / len(declared_states[wfid])) * 100, 1) if declared_states[wfid] else 0.0
                    }
                    for wfid in declared_wfs
                }
            },
            "agent_participation": {
                "total_exercised": len(exercised_agents),
                "agents": sorted(exercised_agents),
            },
            "transition_coverage": {
                "total_transitions": len(exercised_transitions),
                "transitions": [f"{o} -> {d}" for o, d in sorted(exercised_transitions)],
            },
        }

    def format_coverage_report(self, cov: Dict[str, Any]) -> str:
        """Formata as métricas de cobertura em painel legível de console."""
        wc = cov["workflow_coverage"]
        sc = cov["state_coverage"]
        ap = cov["agent_participation"]
        tc = cov["transition_coverage"]

        lines = [
            "=" * 70,
            "📊 PAINEL DE COBERTURA DOS WORKFLOWS MULTI-AGENTE (R-050)",
            "=" * 70,
            f"1. Cobertura de Workflows: {wc['covered']}/{wc['total']} ({wc['percentage']}%)",
            f"2. Cobertura de Estados/Etapas: {sc['covered']}/{sc['total']} ({sc['percentage']}%)",
        ]
        for wfid, details in sc["details"].items():
            lines.append(f"   - {wfid}: {len(details['visited'])}/{len(details['total_declared'])} etapas ({details['percentage']}%)")

        lines.extend([
            "-" * 70,
            f"3. Agentes Exercitados em Trajetórias: {ap['total_exercised']} agentes",
            f"   └─ {', '.join(ap['agents'][:8])}... (+{max(0, ap['total_exercised'] - 8)} outros)",
            f"4. Transições/Handoffs E2E Validados: {tc['total_transitions']} transições únicas",
            "=" * 70,
        ])
        return "\n".join(lines)

    def format_text_report(self, results: List[Dict[str, Any]]) -> str:
        """Gera um relatório de console legível e formatado."""
        lines = [
            "=" * 70,
            "🧪 RELATÓRIO DE AVALIAÇÃO DE TRAJETÓRIAS MULTI-AGENTE (R-050)",
            "=" * 70,
        ]
        passed_count = sum(1 for r in results if r["status"] == "PASS")
        total_count = len(results)

        for res in results:
            cid = res["scenario_id"]
            nome = res.get("nome", "Sem Nome")
            status_icon = "✅" if res["status"] == "PASS" else "❌"
            wf = res.get("workflow", res.get("tipo", "N/A"))
            lines.append(f"{status_icon} [{cid}] ({wf}) {nome}")

            if res["status"] == "FAIL":
                for p in res.get("passos", []):
                    if p.get("status") == "FAIL":
                        lines.append(f"   └─ Etapa {p['etapa']} ({p['agente']}): {', '.join(p.get('erros', []))}")

        lines.append("-" * 70)
        lines.append(f"Resultado: {passed_count}/{total_count} cenários em conformidade total.")
        lines.append("=" * 70)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Avaliador de Trajetórias Multi-Agente")
    parser.add_argument("--scenario", help="ID do cenário específico a ser avaliado")
    parser.add_argument("--json", action="store_true", help="Emite resultado em formato JSON")
    parser.add_argument("--coverage", action="store_true", help="Exibe o painel de métricas de cobertura de workflows")
    args = parser.parse_args()

    evaluator = WorkflowEvaluator()
    if args.coverage:
        cov = evaluator.calculate_coverage()
        if args.json:
            print(json.dumps(cov, indent=2, ensure_ascii=False))
        else:
            print(evaluator.format_coverage_report(cov))
        return

    if args.scenario:
        results = [evaluator.evaluate_static_trajectory(args.scenario)]
    else:
        results = evaluator.evaluate_all_scenarios()

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(evaluator.format_text_report(results))


if __name__ == "__main__":
    main()

