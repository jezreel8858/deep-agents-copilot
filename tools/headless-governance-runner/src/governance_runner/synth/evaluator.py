"""evaluator — Avaliacao cega do agent-router (B2-04).

Blind: o request enviado ao SDK contem APENAS prompt_text + system_prompt;
`expected_route` so e usado no scorer pos-resposta.
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import (
    CopilotSDKClient,
    SDKRequest,
    SDKResponse,
    construir_permission_handler_read_only,
)
from governance_runner.synth.storage import SynthRepository

__all__ = [
    "DEFAULT_ROUTER_AGENT",
    "carregar_router_agent",
    "capturar_rota",
    "pontuar",
    "RelatorioAvaliacao",
    "avaliar_lote",
]

DEFAULT_ROUTER_AGENT = Path(".github") / "agents" / "agent-router.agent.md"

_REGEX_BANNER = {
    "Delegado": re.compile(r"^\s*Delegado\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "Rota": re.compile(r"^\s*Rota\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "Agente Ativo": re.compile(r"^\s*Agente Ativo\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
}
_REGEX_TOKEN = re.compile(r"@?([A-Za-z0-9][\w\-]*)")
_ROUTER_ATIVO = "agent-router"


def carregar_router_agent(caminho: str | Path | None = None, repo_root: Path | None = None) -> tuple[str, str]:
    """Retorna (corpo sem frontmatter, sha256 do arquivo completo)."""
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
    """Captura a rota observada: tool_hook -> text_banner -> unparseable.

    Retorna (rota, route_source); (None, None) quando nao parseavel (nunca inventa rota).
    """
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


def pontuar(observada: str | None, expected_route: str) -> tuple[str, bool]:
    """Scorer pos-resposta (unico ponto que ve expected_route)."""
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
) -> RelatorioAvaliacao:
    """Avalia em lote (retomavel): itens ja gravados em `run_id` nao sao reavaliados."""
    system_prompt, sha = carregar_router_agent(router_agent_path, repo_root)
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
        eval_run_id=rid, source_run_id=source_run_id, only_untested_globally=pending, limit=limit
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
                run_id=rid, prompt_id=item["prompt_id"], observed_route=None, route_source=None,
                verdict="error", passed=False, error=str(exc)[:500],
            )
            rel.n_errors += 1
            rel.n_avaliados += 1
            continue
        latencia = int((time.monotonic() - inicio) * 1000)
        custo = resposta.premium_requests_consumidos
        estourou = budget_lote.registrar_custo(custo).excedido
        rel.premium_requests_used += custo
        rota, fonte = capturar_rota(resposta)
        verdict, passou = pontuar(rota, str(item["expected_route"]))
        repo.inserir_avaliacao(
            run_id=rid, prompt_id=item["prompt_id"], observed_route=rota, route_source=fonte,
            verdict=verdict, passed=passou,
            response_excerpt=(resposta.texto or "")[:500] or None,
            latency_ms=latencia, premium_requests=custo,
        )
        rel.n_avaliados += 1
        rel.n_passed += int(passou)
        rel.n_unparseable += int(verdict == "unparseable")
        if estourou:
            rel.status, rel.motivo = "neutral", "budget_exhausted"
            break
    repo.finalizar_run(
        rid, status=rel.status, motivo=rel.motivo, premium_requests_used=rel.premium_requests_used,
        router_agent_sha256=sha,
    )
    return rel
