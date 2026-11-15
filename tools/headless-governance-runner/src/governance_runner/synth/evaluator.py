"""
evaluator — Avaliacao cega do agent-router, captura de rota e workflow + coerencia etapa 1 (B2 / §3.4 / §3.5).
"""

from __future__ import annotations

import fnmatch
import hashlib
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from governance_runner.routing.model import Workflow
from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import (
    CopilotSDKClient,
    SDKRequest,
    SDKResponse,
    construir_permission_handler_read_only,
)
from governance_runner.synth.routing_graph import (
    GrafoSnapshot,
    WorkflowGrafo,
    carregar_snapshot_grafo,
)
from governance_runner.synth.storage import SynthRepository

__all__ = [
    "DEFAULT_ROUTER_AGENT",
    "PRE_ETAPAS_WORKFLOW",
    "carregar_router_agent",
    "capturar_rota",
    "capturar_workflow",
    "avaliar_consistencia_workflow_rota",
    "validar_coerencia_workflow",
    "pontuar",
    "RelatorioAvaliacao",
    "avaliar_lote",
]

DEFAULT_ROUTER_AGENT = Path(".github") / "agents" / "agent-router.agent.md"
PRE_ETAPAS_WORKFLOW: frozenset[str] = frozenset({"binding-initializer", "prompt-structuring"})

_REGEX_BANNER = {
    "Delegado": re.compile(r"^\s*Delegado\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "Rota": re.compile(r"^\s*Rota\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "Agente Ativo": re.compile(r"^\s*Agente Ativo\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
}
_REGEX_WORKFLOW_STRICT = re.compile(
    r"^\s*(?i:workflow)\s*:\s*(WORKFLOW-[A-Z]+(?:-[A-Z]+)*|N/A)\s*$",
    re.MULTILINE,
)
_REGEX_WORKFLOW_LINHA = re.compile(
    r"^\s*(?i:workflow)\s*:\s*(.+?)\s*$",
    re.MULTILINE,
)
_REGEX_ETAPA_WORKFLOW = re.compile(
    r"^\s*(?i:etapa do workflow)\s*:\s*(\d+)",
    re.MULTILINE,
)
_REGEX_TOKEN = re.compile(r"@?([A-Za-z0-9][\w\-]*)")
_ROUTER_ATIVO = "agent-router"
_IDS_WORKFLOW_CANONICOS: frozenset[str] = frozenset(w.value for w in Workflow)


def carregar_router_agent(
    caminho: str | Path | None = None,
    repo_root: Path | None = None,
) -> tuple[str, str]:
    p = Path(caminho) if caminho else DEFAULT_ROUTER_AGENT
    if not p.is_absolute() and repo_root is not None:
        p = repo_root / p
    bruto = p.read_bytes()
    texto = bruto.decode("utf-8")
    corpo = texto
    if texto.lstrip().startswith("---"):
        partes = texto.lstrip().split("---", 2)
        if len(partes) == 3:
            corpo = partes[2].lstrip("\r\n")
    return corpo, hashlib.sha256(bruto).hexdigest()


def _normalizar_rota(valor: str) -> str | None:
    m = _REGEX_TOKEN.search(valor)
    return m.group(1).lower() if m else None


def capturar_rota(resposta: SDKResponse) -> tuple[str | None, str | None]:
    """Captura a rota delegada via tool_hook ('delegar') ou text_banner."""
    for ev in resposta.tool_events:
        if str(ev.get("tool", "")).lower() == "delegar":
            destino = ev.get("para")
            if destino is None and isinstance(ev.get("arguments"), dict):
                destino = ev["arguments"].get("para")
            rota = _normalizar_rota(str(destino)) if destino else None
            if rota:
                return rota, "tool_hook"
    texto = resposta.texto or "\n".join(str(a.get("mensagem", "")) for a in resposta.achados)
    for chave in ("Delegado", "Rota", "Agente Ativo"):
        for m in _REGEX_BANNER[chave].finditer(texto):
            rota = _normalizar_rota(m.group(1))
            if rota and not (chave == "Agente Ativo" and rota == _ROUTER_ATIVO):
                return rota, "text_banner"
    return None, None


def capturar_workflow(
    texto_ou_resposta: str | SDKResponse,
    ids_validos: Iterable[str] | GrafoSnapshot | None = None,
) -> tuple[str | None, int | None, str]:
    """Extrai (observed_workflow, observed_etapa, workflow_source) do banner textual (§3.4)."""
    if isinstance(texto_ou_resposta, SDKResponse):
        texto = texto_ou_resposta.texto or "\n".join(
            str(a.get("mensagem", "")) for a in texto_ou_resposta.achados
        )
    else:
        texto = str(texto_ou_resposta or "")

    if isinstance(ids_validos, GrafoSnapshot):
        validos_set = frozenset(w.workflow_id for w in ids_validos.workflows) or _IDS_WORKFLOW_CANONICOS
    elif ids_validos is not None:
        validos_set = frozenset(str(x).strip() for x in ids_validos if str(x).strip())
    else:
        validos_set = _IDS_WORKFLOW_CANONICOS

    m_etapa = _REGEX_ETAPA_WORKFLOW.search(texto)
    etapa_obs: int | None = int(m_etapa.group(1)) if m_etapa else None

    m_linha = _REGEX_WORKFLOW_LINHA.search(texto)
    if m_linha is None:
        return None, etapa_obs, "none"

    m_strict = _REGEX_WORKFLOW_STRICT.search(texto)
    if m_strict is None:
        return None, etapa_obs, "invalid_id"

    valor_wf = m_strict.group(1).strip()
    if valor_wf == "N/A":
        return None, etapa_obs, "text_banner"

    if valor_wf not in validos_set:
        return None, etapa_obs, "invalid_id"

    return valor_wf, etapa_obs, "text_banner"


def _extrair_padroes_etapa1(
    observed_workflow: str,
    etapa1_padroes: Sequence[str] | WorkflowGrafo | Mapping[str, Any] | GrafoSnapshot | None,
) -> tuple[str, ...]:
    if isinstance(etapa1_padroes, WorkflowGrafo):
        return etapa1_padroes.etapa1_padroes
    if isinstance(etapa1_padroes, GrafoSnapshot):
        for wf in etapa1_padroes.workflows:
            if wf.workflow_id == observed_workflow:
                return wf.etapa1_padroes
        return ()
    if isinstance(etapa1_padroes, Mapping):
        item = etapa1_padroes.get(observed_workflow)
        if isinstance(item, WorkflowGrafo):
            return item.etapa1_padroes
        if isinstance(item, (list, tuple, set, frozenset)):
            return tuple(str(x) for x in item)
        return ()
    if isinstance(etapa1_padroes, (list, tuple, set, frozenset)):
        return tuple(str(x) for x in etapa1_padroes)
    return ()


def _normalizar_padrao_comparacao(padrao: str) -> list[str]:
    res: list[str] = []
    for p in str(padrao).split("|"):
        s = p.strip().lstrip("@").lower()
        if not s:
            continue
        if "<stack>" in s:
            s = s.replace("<stack>", "*")
        elif s == "domain-router" or s.startswith("domain-router-"):
            s = "*-router"
        res.append(s)
    return res


def avaliar_consistencia_workflow_rota(
    observed_workflow: str | None,
    observed_route: str | None,
    etapa1_padroes: Sequence[str] | WorkflowGrafo | Mapping[str, Any] | GrafoSnapshot | None = None,
) -> int | None:
    """Valida coerencia entre workflow observado e rota da etapa 1 sem penalizar pre-etapas (§3.5)."""
    if not observed_workflow or not observed_route:
        return None
    rota_norm = _normalizar_rota(observed_route) or observed_route.strip().lstrip("@").lower()
    if not rota_norm:
        return None

    # binding-initializer eh pre-etapa de health check (R-034) e retorna NULL em qualquer workflow (§3.5)
    if rota_norm == "binding-initializer":
        return None

    padroes_brutos = _extrair_padroes_etapa1(observed_workflow, etapa1_padroes)
    padroes_expandidos: list[str] = []
    for pb in padroes_brutos:
        padroes_expandidos.extend(_normalizar_padrao_comparacao(pb))

    # Se prompt-structuring for pré-etapa legítima (workflow != WORKFLOW-FEATURE-DEVELOPMENT e nao casa etapa 1)
    # Ordem de §3.5: PROMPT-SYNTHESIS e FEATURE-DEVELOPMENT casam como 1; demais workflows viram NULL
    if rota_norm in PRE_ETAPAS_WORKFLOW and observed_workflow != "WORKFLOW-FEATURE-DEVELOPMENT":
        if any(fnmatch.fnmatchcase(rota_norm, pat) for pat in padroes_expandidos):
            return 1
        return None

    if not padroes_expandidos:
        if observed_workflow == "WORKFLOW-FEATURE-DEVELOPMENT" and rota_norm == "prompt-structuring":
            return 1
        return None

    for pat in padroes_expandidos:
        if fnmatch.fnmatchcase(rota_norm, pat):
            return 1
    return 0


validar_coerencia_workflow = avaliar_consistencia_workflow_rota


def pontuar(observada: str | None, expected_route: str) -> tuple[str, bool]:
    if observada is None:
        return "unparseable", False
    ok = observada == (_normalizar_rota(expected_route) or expected_route.lower())
    return ("matched", True) if ok else ("mismatched", False)


@dataclass
class RelatorioAvaliacao:
    run_id: str
    n_avaliados: int = 0
    n_passed: int = 0
    n_unparseable: int = 0
    n_errors: int = 0
    premium_requests_used: int = 0
    status: str = "completed"
    motivo: str | None = None


def avaliar_lote(
    *,
    repo: SynthRepository,
    cliente: CopilotSDKClient,
    budget_lote: Budget,
    router_agent_path: str | Path | None = None,
    repo_root: Path | None = None,
    run_id: str | None = None,
    source_run_id: str | None = None,
    pending: bool = False,
    limit: int | None = None,
    modelo: str | None = None,
    snapshot: GrafoSnapshot | None = None,
) -> RelatorioAvaliacao:
    system_prompt, sha = carregar_router_agent(router_agent_path, repo_root)
    snap_efetivo = snapshot
    if snap_efetivo is None:
        try:
            snap_efetivo = carregar_snapshot_grafo(None, repo_root=repo_root)
        except Exception:  # noqa: BLE001
            snap_efetivo = None

    ids_wf_validos: frozenset[str] = (
        frozenset(w.workflow_id for w in snap_efetivo.workflows)
        if snap_efetivo is not None and snap_efetivo.workflows
        else _IDS_WORKFLOW_CANONICOS
    )
    mapa_padroes_wf: dict[str, tuple[str, ...]] = (
        {w.workflow_id: w.etapa1_padroes for w in snap_efetivo.workflows}
        if snap_efetivo is not None
        else {}
    )

    rid = run_id or str(uuid.uuid4())
    if repo.obter_run(rid) is None:
        repo.criar_run(
            kind="eval",
            run_id=rid,
            model=modelo,
            router_agent_sha256=sha,
            params={"pending": pending, "limit": limit, "source_run_id": source_run_id},
        )
    rel = RelatorioAvaliacao(run_id=rid)
    handler = construir_permission_handler_read_only([], strict_empty_scope=True)
    itens: list[dict[str, Any]] = repo.listar_pendentes_avaliacao(
        eval_run_id=rid,
        source_run_id=source_run_id,
        only_untested_globally=pending,
        limit=limit,
    )
    for item in itens:
        if (
            budget_lote.max_premium_requests <= 0
            or budget_lote.custo_atual["premium_requests"] >= budget_lote.max_premium_requests
        ):
            rel.status, rel.motivo = "neutral", "budget_exhausted"
            break
        budget_item = Budget(max_premium_requests=budget_lote.max_premium_requests)
        if budget_item.registrar_turno().excedido:
            rel.status, rel.motivo = "neutral", "budget_exhausted"
            break
        request = SDKRequest(
            prompt=str(item["text"]),
            ferramentas_permitidas=("delegar",),
            permission_handler=handler,
            modelo=modelo,
            system_prompt=system_prompt,
        )
        inicio = time.monotonic()
        try:
            resposta = cliente.invoke(request)
        except Exception as exc:  # noqa: BLE001 - falha por item nao aborta o lote
            repo.inserir_avaliacao(
                run_id=rid,
                prompt_id=item["prompt_id"],
                observed_route=None,
                route_source=None,
                verdict="error",
                passed=False,
                error=str(exc)[:500],
            )
            rel.n_errors += 1
            rel.n_avaliados += 1
            continue
        latencia = int((time.monotonic() - inicio) * 1000)
        custo = resposta.premium_requests_consumidos
        estourou = budget_lote.registrar_custo(custo).excedido
        rel.premium_requests_used += custo
        rota, fonte = capturar_rota(resposta)
        obs_wf, obs_etapa, wf_src = capturar_workflow(resposta, ids_wf_validos)
        consist = avaliar_consistencia_workflow_rota(obs_wf, rota, mapa_padroes_wf)
        verdict, passou = pontuar(rota, str(item["expected_route"]))
        repo.inserir_avaliacao(
            run_id=rid,
            prompt_id=item["prompt_id"],
            observed_route=rota,
            route_source=fonte,
            observed_workflow=obs_wf,
            observed_etapa=obs_etapa,
            workflow_source=wf_src,
            workflow_route_consistent=consist,
            verdict=verdict,
            passed=passou,
            response_excerpt=(resposta.texto or "")[:500] or None,
            latency_ms=latencia,
            premium_requests=custo,
        )
        rel.n_avaliados += 1
        rel.n_passed += int(passou)
        rel.n_unparseable += int(verdict == "unparseable")
        if estourou:
            rel.status, rel.motivo = "neutral", "budget_exhausted"
            break
    repo.finalizar_run(
        rid,
        status=rel.status,
        motivo=rel.motivo,
        premium_requests_used=rel.premium_requests_used,
        router_agent_sha256=sha,
    )
    return rel
