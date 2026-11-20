"""
evaluator — Avaliador de rotas, workflows e utilidade marginal de skills (A/B) (B1 / §4 / §7 / P5).
"""

from __future__ import annotations

import fnmatch
import hashlib
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence


class SdkClientProtocol(Protocol):
    def avaliar(self, prompt: str, *, modelo: str | None = None) -> Any: ...


SdkResponse = Any

from governance_runner.synth.normalize import normalizar
from governance_runner.synth.routing_graph import GrafoSnapshot

try:
    from governance_runner.synth.routing_graph import (
        validar_consistencia_workflow_rota as _validar_wf_rota_externo,
    )
except ImportError:
    _validar_wf_rota_externo = None

__all__ = [
    "SdkClientProtocol",
    "SdkResponse",
    "ResultadoAvaliacao",
    "ResultadoCasoSkillAB",
    "RelatorioSkillAB",
    "extrair_rota_observada",
    "extrair_workflow_observado",
    "avaliar_prompt_item",
    "avaliar_lote_prompts",
    "pontuar_rubrica_skill",
    "avaliar_skill_ab_item",
    "avaliar_lote_skill_ab",
]

_MAX_RESPONSE_EXCERPT = 500

_REGEX_CABECALHO_ROTA = re.compile(
    r"(?:Rota|Delegado|Agente\s+Ativo)\s*:\s*`?@?([a-z0-9][a-z0-9\-_]*)`?",
    re.IGNORECASE,
)

_REGEX_CABECALHO_WORKFLOW = re.compile(
    r"Workflow:\s*(?P<wf>[a-z0-9\-_]+|nenhum)(?:\s*\(etapa\s+(?P<etapa>\d+)\))?",
    re.IGNORECASE,
)

_PREFIXOS_PROIBICAO_RE = re.compile(
    r"(?:nunca|jamais|n[aã]o|proibido(?:\s+de)?|evite|evitar|vedado|never|do\s+not|don't|avoid|must\s+not|shall\s+not|forbid(?:den)?)\s+(?:de\s+|a\s+|o\s+|os\s+|as\s+|to\s+)?$",
    re.IGNORECASE,
)


def _validar_consistencia_workflow_rota(
    obs_wf: str,
    obs_etapa: int | None,
    observed_route: str,
    snapshot: GrafoSnapshot,
) -> bool:
    if _validar_wf_rota_externo is not None:
        return bool(_validar_wf_rota_externo(obs_wf, obs_etapa, observed_route, snapshot))

    wf_obj = next(
        (
            w
            for w in getattr(snapshot, "workflows", ())
            if str(getattr(w, "workflow_id", "")).strip().lower() == obs_wf.strip().lower()
        ),
        None,
    )
    if wf_obj is None:
        return False

    if obs_etapa is None or obs_etapa == 1:
        padroes = tuple(getattr(wf_obj, "etapa1_padroes", ()) or ())
        if not padroes:
            return True
        rota_low = observed_route.strip().lstrip("@").lower()
        for padrao in padroes:
            p_low = str(padrao).strip().lstrip("@").lower()
            if not p_low:
                continue
            if p_low in ("*", "<stack>") or p_low == rota_low:
                return True
            glob_pat = p_low.replace("<stack>", "*")
            if fnmatch.fnmatch(rota_low, glob_pat):
                return True
        return False

    return True


@dataclass(frozen=True)
class ResultadoAvaliacao:
    prompt_id: str
    observed_route: str | None
    route_source: str | None
    verdict: str
    passed: bool
    response_excerpt: str | None
    latency_ms: int
    premium_requests: int
    error: str | None = None
    observed_workflow: str | None = None
    observed_etapa: int | None = None
    workflow_source: str | None = None
    workflow_route_consistent: int | None = None


@dataclass(frozen=True)
class ResultadoCasoSkillAB:
    """Resultado pareado (baseline vs. treatment) de um caso de avaliacao A/B de skill (P5)."""

    case_id: str
    skill_name: str
    skill_sha256: str | None
    mode: str
    baseline_score: float
    treatment_score: float
    delta_utility: float
    min_delta_utility: float
    redundant: bool
    passed: bool
    missing_clauses: tuple[str, ...] = ()
    triggered_antipatterns: tuple[str, ...] = ()
    latency_ms: int = 0
    premium_requests: int = 0


@dataclass(frozen=True)
class RelatorioSkillAB:
    """Agregado consolidado de um lote de avaliacao pareada A/B de skills."""

    total_cases: int
    passed_cases: int
    redundant_cases: int
    mean_baseline_score: float
    mean_treatment_score: float
    mean_delta_utility: float
    premium_requests_used: int
    resultados: tuple[ResultadoCasoSkillAB, ...]


def extrair_rota_observada(
    resposta: SdkResponse | Mapping[str, Any] | str,
) -> tuple[str | None, str | None]:
    """Extrai (observed_route, route_source) com precedencia tool_hook > text_banner."""
    if isinstance(resposta, str):
        texto = resposta
        tool_calls: list[Any] = []
    elif not isinstance(resposta, Mapping):
        texto = str(getattr(resposta, "texto", None) or getattr(resposta, "text", None) or "")
        tool_calls = list(getattr(resposta, "tool_calls", None) or ())
    else:
        texto = str(resposta.get("texto") or resposta.get("text") or "")
        tool_calls = list(resposta.get("tool_calls") or ())

    for tc in tool_calls:
        if isinstance(tc, Mapping):
            nome_tool = str(tc.get("name") or tc.get("tool") or "").strip()
            args = tc.get("arguments") if isinstance(tc.get("arguments"), Mapping) else tc
            if nome_tool == "run_subagent" or (
                not nome_tool and isinstance(args, Mapping) and ("agentName" in args or "agent_name" in args)
            ):
                if isinstance(args, Mapping):
                    candidato = args.get("agentName") or args.get("agent_name") or args.get("agent")
                    if candidato is not None:
                        rota_limpa = str(candidato).strip().lstrip("@").lower()
                        if rota_limpa:
                            return rota_limpa, "tool_hook"

    if texto:
        match = _REGEX_CABECALHO_ROTA.search(texto)
        if match:
            rota_banner = match.group(1).strip().lstrip("@").lower()
            if rota_banner:
                return rota_banner, "text_banner"

    return None, None


def extrair_workflow_observado(
    resposta: SdkResponse | Mapping[str, Any] | str,
) -> tuple[str | None, int | None, str | None]:
    """Extrai (observed_workflow, observed_etapa, workflow_source) do banner da resposta."""
    if isinstance(resposta, str):
        texto = resposta
    elif not isinstance(resposta, Mapping):
        texto = str(getattr(resposta, "texto", None) or getattr(resposta, "text", None) or "")
    else:
        texto = str(resposta.get("texto") or resposta.get("text") or "")

    if not texto:
        return None, None, None

    match = _REGEX_CABECALHO_WORKFLOW.search(texto)
    if not match:
        return None, None, None

    wf_raw = match.group("wf").strip().lower()
    etapa_raw = match.group("etapa")
    etapa = int(etapa_raw) if etapa_raw is not None else None
    if wf_raw == "nenhum":
        return None, None, "text_banner"
    return wf_raw, etapa, "text_banner"


def _construir_prompt_avaliacao(prompt_texto: str, router_instructions: str | None) -> str:
    if not router_instructions:
        return prompt_texto
    return (
        "<system_router_instructions>\n"
        f"{router_instructions.strip()}\n"
        "</system_router_instructions>\n\n"
        f"<user_request>\n{prompt_texto}\n</user_request>"
    )


def avaliar_prompt_item(
    prompt_row: Mapping[str, Any],
    *,
    cliente_sdk: SdkClientProtocol,
    router_instructions: str | None = None,
    modelo: str | None = None,
    snapshot: GrafoSnapshot | None = None,
    budget_callback: Callable[[int], None] | None = None,
) -> ResultadoAvaliacao:
    prompt_id = str(prompt_row["prompt_id"])
    prompt_texto = str(prompt_row["text"])
    expected_route = str(prompt_row.get("expected_route") or "").strip().lstrip("@").lower()
    expected_workflow_raw = prompt_row.get("expected_workflow")
    expected_workflow = (
        str(expected_workflow_raw).strip().lower()
        if expected_workflow_raw is not None and str(expected_workflow_raw).strip()
        else None
    )

    payload = _construir_prompt_avaliacao(prompt_texto, router_instructions)
    t0 = time.perf_counter()
    try:
        resp = cliente_sdk.avaliar(payload, modelo=modelo)
    except Exception as exc:  # noqa: BLE001
        lat_ms = int((time.perf_counter() - t0) * 1000)
        if budget_callback is not None:
            budget_callback(1)
        return ResultadoAvaliacao(
            prompt_id=prompt_id,
            observed_route=None,
            route_source=None,
            verdict="error",
            passed=False,
            response_excerpt=None,
            latency_ms=lat_ms,
            premium_requests=1,
            error=f"{exc.__class__.__name__}: {exc}",
        )

    lat_ms = int((time.perf_counter() - t0) * 1000)
    premium_usado = int(getattr(resp, "premium_requests_consumidas", None) or 1)
    if budget_callback is not None:
        budget_callback(premium_usado)

    observed, source = extrair_rota_observada(resp)
    obs_wf, obs_etapa, wf_source = extrair_workflow_observado(resp)
    trecho = (str(getattr(resp, "texto", None) or ""))[:_MAX_RESPONSE_EXCERPT]

    if observed is None or source is None:
        return ResultadoAvaliacao(
            prompt_id=prompt_id,
            observed_route=None,
            route_source=None,
            verdict="unparseable",
            passed=False,
            response_excerpt=trecho,
            latency_ms=lat_ms,
            premium_requests=premium_usado,
            error=None,
            observed_workflow=obs_wf,
            observed_etapa=obs_etapa,
            workflow_source=wf_source,
            workflow_route_consistent=None,
        )

    consist_wf_rota: int | None = None
    if snapshot is not None and obs_wf is not None:
        consist_wf_rota = (
            1 if _validar_consistencia_workflow_rota(obs_wf, obs_etapa, observed, snapshot) else 0
        )

    rota_bateu = observed == expected_route
    wf_bateu = True if expected_workflow is None else (obs_wf == expected_workflow)
    consist_ok = True if consist_wf_rota is None else (consist_wf_rota == 1)

    bateu = rota_bateu and wf_bateu and consist_ok
    verdict = "matched" if bateu else "mismatched"
    return ResultadoAvaliacao(
        prompt_id=prompt_id,
        observed_route=observed,
        route_source=source,
        verdict=verdict,
        passed=bateu,
        response_excerpt=trecho,
        latency_ms=lat_ms,
        premium_requests=premium_usado,
        error=None,
        observed_workflow=obs_wf,
        observed_etapa=obs_etapa,
        workflow_source=wf_source,
        workflow_route_consistent=consist_wf_rota,
    )


def avaliar_lote_prompts(
    prompts: Sequence[Mapping[str, Any]],
    *,
    cliente_sdk: SdkClientProtocol,
    router_instructions: str | None = None,
    modelo: str | None = None,
    snapshot: GrafoSnapshot | None = None,
    budget_callback: Callable[[int], None] | None = None,
) -> list[ResultadoAvaliacao]:
    resultados: list[ResultadoAvaliacao] = []
    for item in prompts:
        res = avaliar_prompt_item(
            item,
            cliente_sdk=cliente_sdk,
            router_instructions=router_instructions,
            modelo=modelo,
            snapshot=snapshot,
            budget_callback=budget_callback,
        )
        resultados.append(res)
    return resultados


def _normalizar_para_rubrica(texto: str) -> str:
    return normalizar(texto)


def _antipadrao_disparado(norm_resp: str, anti_norm: str) -> bool:
    """Verifica se o antipadrao ocorre de forma afirmativa (nao precedido por proibicao explicita)."""
    if not anti_norm:
        return False
    pos = 0
    while True:
        idx = norm_resp.find(anti_norm, pos)
        if idx == -1:
            return False
        janela_antes = norm_resp[max(0, idx - 32) : idx]
        if not _PREFIXOS_PROIBICAO_RE.search(janela_antes):
            return True
        pos = idx + len(anti_norm)


def pontuar_rubrica_skill(
    texto_resposta: str,
    *,
    required_clauses: Sequence[str] = (),
    forbidden_antipatterns: Sequence[str] = (),
) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    """Calcula score deterministico [0.0, 1.0] de aderencia a rubrica da skill (P5)."""
    norm_resp = _normalizar_para_rubrica(texto_resposta or "")
    missing: list[str] = []
    presentes = 0
    for cl in required_clauses:
        cl_str = str(cl).strip()
        if not cl_str:
            continue
        cl_norm = _normalizar_para_rubrica(cl_str)
        if cl_norm and cl_norm in norm_resp:
            presentes += 1
        else:
            missing.append(cl_str)

    triggered: list[str] = []
    for anti in forbidden_antipatterns:
        anti_str = str(anti).strip()
        if not anti_str:
            continue
        anti_norm = _normalizar_para_rubrica(anti_str)
        if _antipadrao_disparado(norm_resp, anti_norm):
            triggered.append(anti_str)

    total_req = presentes + len(missing)
    base_ratio = (presentes / total_req) if total_req > 0 else (1.0 if norm_resp else 0.0)
    penalidade = 0.25 * len(triggered)
    score = max(0.0, min(1.0, round(base_ratio - penalidade, 4)))
    return score, tuple(missing), tuple(triggered)


def _carregar_skill_md(skill_name: str, skills_dir: Path | None) -> tuple[str, str | None]:
    if skills_dir is None:
        return "", None
    skill_md = skills_dir / skill_name / "SKILL.md"
    if not skill_md.exists():
        return "", None
    conteudo = skill_md.read_text(encoding="utf-8", errors="replace")
    sha = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
    return conteudo, sha


def avaliar_skill_ab_item(
    caso: Mapping[str, Any],
    *,
    skills_dir: Path | None = None,
    cliente_sdk: SdkClientProtocol | None = None,
    modelo: str | None = None,
    budget_callback: Callable[[int], None] | None = None,
) -> ResultadoCasoSkillAB:
    """Executa avaliacao pareada A/B (baseline sem skill vs. treatment com SKILL.md)."""
    case_id = str(caso.get("case_id") or "skill-ab-case")
    skill_name = str(caso.get("skill_name") or "").strip()
    baseline_prompt = str(caso.get("baseline_prompt") or caso.get("prompt") or "").strip()
    required_clauses = tuple(str(x) for x in (caso.get("required_clauses") or ()) if str(x).strip())
    forbidden_antipatterns = tuple(
        str(x) for x in (caso.get("forbidden_antipatterns") or ()) if str(x).strip()
    )
    min_delta = float(caso.get("min_delta_utility") if caso.get("min_delta_utility") is not None else 0.05)

    skill_conteudo, skill_sha = _carregar_skill_md(skill_name, skills_dir)
    t0 = time.perf_counter()

    if cliente_sdk is not None:
        mode = "sdk"
        resp_base = cliente_sdk.avaliar(baseline_prompt, modelo=modelo)
        p_base = int(getattr(resp_base, "premium_requests_consumidas", None) or 1)
        if budget_callback is not None:
            budget_callback(p_base)
        texto_base = str(getattr(resp_base, "texto", None) or "")

        prompt_treatment = (
            f"<active_skill name=\"{skill_name}\">\n{skill_conteudo.strip()}\n</active_skill>\n\n"
            f"{baseline_prompt}"
            if skill_conteudo
            else baseline_prompt
        )
        resp_treat = cliente_sdk.avaliar(prompt_treatment, modelo=modelo)
        p_treat = int(getattr(resp_treat, "premium_requests_consumidas", None) or 1)
        if budget_callback is not None:
            budget_callback(p_treat)
        texto_treat = str(getattr(resp_treat, "texto", None) or "")
        premium_total = p_base + p_treat
    else:
        mode = "offline"
        texto_base = str(caso.get("baseline_response") or baseline_prompt)
        if caso.get("treatment_response") is not None:
            texto_treat = str(caso["treatment_response"])
        else:
            texto_treat = f"{baseline_prompt}\n\n{skill_conteudo}".strip()
        premium_total = 0

    lat_ms = int((time.perf_counter() - t0) * 1000)

    baseline_score, _, _ = pontuar_rubrica_skill(
        texto_base,
        required_clauses=required_clauses,
        forbidden_antipatterns=forbidden_antipatterns,
    )
    treatment_score, missing_treat, triggered_treat = pontuar_rubrica_skill(
        texto_treat,
        required_clauses=required_clauses,
        forbidden_antipatterns=forbidden_antipatterns,
    )
    delta_utility = round(treatment_score - baseline_score, 4)
    redundant = delta_utility < min_delta
    passed = (not redundant) and (len(triggered_treat) == 0) and (treatment_score >= baseline_score)

    return ResultadoCasoSkillAB(
        case_id=case_id,
        skill_name=skill_name,
        skill_sha256=skill_sha,
        mode=mode,
        baseline_score=baseline_score,
        treatment_score=treatment_score,
        delta_utility=delta_utility,
        min_delta_utility=min_delta,
        redundant=redundant,
        passed=passed,
        missing_clauses=missing_treat,
        triggered_antipatterns=triggered_treat,
        latency_ms=lat_ms,
        premium_requests=premium_total,
    )


def avaliar_lote_skill_ab(
    casos: Sequence[Mapping[str, Any]],
    *,
    skills_dir: Path | None = None,
    cliente_sdk: SdkClientProtocol | None = None,
    modelo: str | None = None,
    budget_callback: Callable[[int], None] | None = None,
) -> RelatorioSkillAB:
    """Avalia um lote de casos pareados A/B de skills e consolida metricas agregadas."""
    resultados: list[ResultadoCasoSkillAB] = []
    for caso in casos:
        resultados.append(
            avaliar_skill_ab_item(
                caso,
                skills_dir=skills_dir,
                cliente_sdk=cliente_sdk,
                modelo=modelo,
                budget_callback=budget_callback,
            )
        )
    total = len(resultados)
    if total == 0:
        return RelatorioSkillAB(
            total_cases=0,
            passed_cases=0,
            redundant_cases=0,
            mean_baseline_score=0.0,
            mean_treatment_score=0.0,
            mean_delta_utility=0.0,
            premium_requests_used=0,
            resultados=(),
        )
    passed_count = sum(1 for r in resultados if r.passed)
    redundant_count = sum(1 for r in resultados if r.redundant)
    mean_base = round(sum(r.baseline_score for r in resultados) / total, 4)
    mean_treat = round(sum(r.treatment_score for r in resultados) / total, 4)
    mean_delta = round(sum(r.delta_utility for r in resultados) / total, 4)
    premium_used = sum(r.premium_requests for r in resultados)
    return RelatorioSkillAB(
        total_cases=total,
        passed_cases=passed_count,
        redundant_cases=redundant_count,
        mean_baseline_score=mean_base,
        mean_treatment_score=mean_treat,
        mean_delta_utility=mean_delta,
        premium_requests_used=premium_used,
        resultados=tuple(resultados),
    )