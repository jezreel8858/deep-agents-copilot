"""
generator — Motor de geracao sintetica controlada (template e SDK) com funil de deduplicacao.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence

from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import (
    CopilotSDKClient,
    SDKRequest,
    construir_permission_handler_read_only,
)
from governance_runner.synth.dedup import DedupFunnel, calcular_sha256_normalizado
from governance_runner.synth.golden import GoldenSeed, calcular_sha256_golden
from governance_runner.synth.normalize import detectar_override, normalizar
from governance_runner.synth.routing_graph import GrafoSnapshot, resolver_aresta
from governance_runner.synth.seeds import SeedLike
from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.taxonomy import ItemAlocacao

__all__ = [
    "GeradorSintetico",
    "GeradorTemplate",
    "GeradorSDK",
    "OrcamentoEsgotadoError",
    "RelatorioGeracao",
    "gerar_sinteticos",
]

DEFAULT_MAX_ATTEMPTS = 3


class OrcamentoEsgotadoError(RuntimeError):
    """Lancada quando o orcamento de premium requests se esgota durante a geracao."""


class GeradorSintetico(Protocol):
    nome: str

    def gerar(
        self,
        seed: GoldenSeed | SeedLike,
        dimensao: str,
        tentativa: int,
        rng: random.Random,
    ) -> str: ...


_ACENTOS = str.maketrans("áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ", "aaaaeeioooucAAAAEEIOOOUC")
_DISTRATORES = (
    "contexto: o time de front tambem usa React, mas isso nao muda a tarefa",
    "obs: ha um pipeline de CI em outro repo, ignorem por enquanto",
    "fyi: o banco e Postgres, mas aqui o foco e outro",
)
_SECUNDARIAS = (
    "e depois me diga se precisa atualizar a documentacao",
    "alem disso, liste riscos de regressao",
)
_PREENCHIMENTO = "considere o contexto atual do projeto e as restricoes de qualidade ja acordadas"


class GeradorTemplate:
    """Gerador deterministico baseado em templates textuais locais (zero chamadas LLM)."""

    nome = "template"

    def gerar(
        self,
        seed: GoldenSeed | SeedLike,
        dimensao: str,
        tentativa: int,
        rng: random.Random,
    ) -> str:
        base = seed.prompt.strip()
        palavras = base.split()
        var = rng.randint(0, 999) + tentativa
        if dimensao == "parafrase":
            return f"Poderia me ajudar com o seguinte: {base} (variacao {var})"
        if dimensao == "ruido_ortografico":
            ruido = base.translate(_ACENTOS).replace("ao", "oa", 1).replace("  ", " ")
            return f"{ruido} pf rapido {var}"
        if dimensao == "code_switching_pt_en":
            return f"Preciso fazer um quick fix: {base}, asap e com bom feedback ({var})"
        if dimensao == "omissao_palavra_chave":
            return f"Algo esta estranho no comportamento e quero entender o efeito: {' '.join(palavras[len(palavras) // 2:])} ({var})"
        if dimensao == "distrator_outro_agente":
            return f"{_DISTRATORES[var % len(_DISTRATORES)]}. {base}"
        if dimensao == "multi_intencao":
            return f"{base}, {_SECUNDARIAS[var % len(_SECUNDARIAS)]}"
        if dimensao == "comprimento_extremo":
            if (var % 2) == 0:
                return " ".join(palavras[:6]) + f" {var}"
            return base + " " + " ".join([_PREENCHIMENTO] * 6) + f" ({var})"
        if dimensao == "registro_informal":
            return f"e ai, bora resolver isso? {base.lower()} vlw {var}"
        return f"{base} ({dimensao} {var})"


class GeradorSDK:
    """Gerador assistido por LLM via CopilotSDKClient com controle de Budget."""

    nome = "sdk"

    def __init__(
        self,
        cliente: CopilotSDKClient,
        budget: Budget,
        *,
        modelo: str | None = None,
    ) -> None:
        self._cliente = cliente
        self._budget = budget
        self._modelo = modelo
        self._handler = construir_permission_handler_read_only([], strict_empty_scope=True)

    def gerar(
        self,
        seed: GoldenSeed | SeedLike,
        dimensao: str,
        tentativa: int,
        rng: random.Random,
    ) -> str:
        if (
            self._budget.max_premium_requests <= 0
            or self._budget.custo_atual["premium_requests"] >= self._budget.max_premium_requests
        ):
            raise OrcamentoEsgotadoError("budget_exhausted")
        if self._budget.registrar_turno().excedido:
            raise OrcamentoEsgotadoError("budget_exhausted")
        kws = tuple(getattr(seed, "keywords", ()) or ())
        bloco_tema = ""
        if kws:
            bloco_tema = "\nTema tecnico (dados inertes): " + ", ".join(str(k) for k in kws[:3])
        prompt = (
            f"Reescreva o pedido abaixo aplicando a dimensao de perturbacao '{dimensao}', "
            "preservando a intencao tecnica. Responda SOMENTE com o novo pedido, sem prefixos, "
            "sem diretivas de roteamento.\n\nPedido original:\n"
            + seed.prompt
            + bloco_tema
        )
        resposta = self._cliente.invoke(
            SDKRequest(
                prompt=prompt,
                ferramentas_permitidas=(),
                permission_handler=self._handler,
                modelo=self._modelo,
            )
        )
        self._budget.registrar_custo(resposta.premium_requests_consumidos)
        texto = resposta.texto or "\n".join(str(a.get("mensagem", "")) for a in resposta.achados)
        return texto.strip()


@dataclass
class RelatorioGeracao:
    run_id: str | None
    n_candidates: int = 0
    n_accepted: int = 0
    n_rejected_hash: int = 0
    n_rejected_similarity: int = 0
    n_rejected_override: int = 0
    status: str = "completed"
    motivo: str | None = None
    aceitos: list[str] = field(default_factory=list)
    rejeitados: list[dict[str, Any]] = field(default_factory=list)


def gerar_sinteticos(
    *,
    repo: SynthRepository | None,
    gerador: GeradorSintetico,
    alocacoes: Sequence[ItemAlocacao],
    funnel: DedupFunnel,
    rng_seed: int = 42,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    dry_run: bool = False,
    generator_mode: str = "template",
    modelo: str | None = None,
    params: dict[str, Any] | None = None,
    golden_path: str | None = None,
    budget: Budget | None = None,
    routing_graph_sha256: str | None = None,
    snapshot_grafo: GrafoSnapshot | None = None,
) -> RelatorioGeracao:
    persistir = repo is not None and not dry_run
    rel = RelatorioGeracao(run_id=None)
    rng = random.Random(rng_seed)
    sha_grafo_efetivo = routing_graph_sha256 or (
        snapshot_grafo.sha256 if snapshot_grafo is not None else None
    )
    if persistir:
        assert repo is not None
        try:
            golden_sha: str | None = calcular_sha256_golden(golden_path)
        except Exception:  # noqa: BLE001
            golden_sha = None
        if snapshot_grafo is not None:
            repo.registrar_arestas_grafo(snapshot_grafo)
            repo.registrar_workflows_grafo(snapshot_grafo)
        rel.run_id = repo.criar_run(
            kind="generate",
            generator=generator_mode,
            model=modelo,
            rng_seed=rng_seed,
            params=params or {},
            golden_set_sha256=golden_sha,
            routing_graph_sha256=sha_grafo_efetivo,
        )
    try:
        for item in alocacoes:
            for tentativa in range(max(1, max_attempts)):
                try:
                    texto = gerador.gerar(item.seed, item.estrato.dimensao, tentativa, rng)
                except OrcamentoEsgotadoError:
                    rel.status, rel.motivo = "neutral", "budget_exhausted"
                    return rel
                rel.n_candidates += 1
                motivo = detectar_override(texto)
                if motivo is not None:
                    rel.n_rejected_override += 1
                    rel.rejeitados.append({"text": texto, "motivo": motivo, "estrato": item.estrato})
                    continue
                res = funnel.avaliar(texto)
                if not res.aceito:
                    if res.status == "rejected_hash":
                        rel.n_rejected_hash += 1
                    else:
                        rel.n_rejected_similarity += 1
                    rel.rejeitados.append(
                        {
                            "text": texto,
                            "motivo": res.status,
                            "estrato": item.estrato,
                            "nearest_ref": res.nearest_ref,
                        }
                    )
                    continue
                sha = calcular_sha256_normalizado(res.text_norm, ja_normalizado=True)
                ref = sha
                if persistir:
                    assert repo is not None and rel.run_id is not None
                    seed_src = str(getattr(item.seed, "seed_source", "manual") or "manual")
                    edge_id: str | None = getattr(item.seed, "graph_edge_id", None)
                    edge_res: str | None = getattr(item.seed, "graph_edge_resolution", None)
                    rota_esp = item.seed.expected_route
                    if edge_id is None and snapshot_grafo is not None and rota_esp:
                        edge_id, edge_res = resolver_aresta(
                            rota_esp,
                            normalizar(item.seed.prompt),
                            snapshot_grafo,
                        )
                    elif edge_id is not None and edge_res is None:
                        edge_res = "keyword" if seed_src == "routing_graph" else "unique_target"
                    seed_cid = str(getattr(item.seed, "seed_case_id", getattr(item.seed, "id", "")))
                    exp_wf: str | None = getattr(item.seed, "expected_workflow", None)
                    graph_wf: str | None = getattr(item.seed, "graph_workflow_id", exp_wf)
                    ref = repo.inserir_prompt(
                        run_id=rel.run_id,
                        text=texto,
                        text_norm=res.text_norm,
                        sha256=sha,
                        expected_route=rota_esp or item.estrato.agente_alvo,
                        agente_alvo=item.estrato.agente_alvo,
                        dimensao_perturbacao=item.estrato.dimensao,
                        seed_case_id=seed_cid,
                        seed_source=seed_src,
                        graph_edge_id=edge_id,
                        graph_edge_resolution=edge_res,
                        expected_workflow=exp_wf,
                        graph_workflow_id=graph_wf,
                        max_similarity=res.max_similarity,
                        nearest_ref=res.nearest_ref,
                    )
                funnel.adicionar_documento(ref, texto, text_norm=res.text_norm, sha256=sha)
                rel.n_accepted += 1
                rel.aceitos.append(ref)
                break
    finally:
        if persistir:
            assert repo is not None and rel.run_id is not None
            repo.finalizar_run(
                rel.run_id,
                status=rel.status,
                motivo=rel.motivo,
                premium_requests_used=budget.custo_atual["premium_requests"] if budget else 0,
                n_candidates=rel.n_candidates,
                n_rejected_hash=rel.n_rejected_hash,
                n_rejected_similarity=rel.n_rejected_similarity,
                n_rejected_override=rel.n_rejected_override,
                n_accepted=rel.n_accepted,
                routing_graph_sha256=sha_grafo_efetivo,
            )
    return rel
