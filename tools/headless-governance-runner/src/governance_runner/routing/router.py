"""
router — Roteamento rule-based com política de cascata.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §7.2 / `politica_cascata`):
aplica os thresholds 0.9 (rule-based) / 0.7 (semantic) / 0.5 (llm-assisted) /
0.0 (out-of-domain), com `ambiguity_zone` Δ≤0.05, para escolher o agente/
workflow de destino a partir de uma solicitação em texto livre.

Algoritmo de scoring (determinístico, sem LLM/embeddings), subtask 5 do
PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md:

1. Para cada `Aresta` cuja origem seja um nó `entry_point` (tipicamente
   `agent-router`) e que declare ao menos 1 keyword em `condicoes.keywords`,
   calcula-se `score = matches / total_keywords`, onde `matches` é o número
   de keywords da aresta encontradas como substring na solicitação
   normalizada (lowercase, sem acentuação). Arestas sem keywords (health
   check, mandatory pre-step, security gate, sinais semânticos puros) não
   são candidatas desta função — são tratadas por lógica de infraestrutura
   fora do router puro.
2. Escolhe-se a aresta de maior score; se as 2 melhores arestas tiverem
   score dentro de 0.05 uma da outra E ambas ultrapassarem 0.5
   (`ambiguity_zone`), o desempate é feito pela maior `prioridade`
   declarada nas arestas candidatas dessa zona. Em empate de prioridade,
   prevalece a ordem de declaração no YAML (primeira encontrada).
3. O score final é mapeado para `NivelRouting` pelos thresholds de
   cascata. Se `OUT_OF_DOMAIN`, o `escolhido` passa a ser o nó `fallback`
   do grafo (o de maior `prioridade` nas arestas que apontam para ele,
   quando houver mais de um fallback declarado).
4. Se o `escolhido` corresponder ao agente da etapa 1 de algum
   `WorkflowSpec`, o `Workflow` correspondente é associado à decisão.
"""

from __future__ import annotations

import unicodedata

from governance_runner.routing.model import (
    Aresta,
    DecisaoRota,
    Grafo,
    NivelRouting,
    TipoNo,
    Workflow,
)

_AMBIGUITY_DELTA = 0.05
_EPSILON = 1e-9  # tolerância de ponto flutuante para comparações de score
_AMBIGUITY_FLOOR = 0.5

_THRESHOLD_RULE_BASED = 0.9
_THRESHOLD_SEMANTIC = 0.7
_THRESHOLD_LLM_ASSISTED = 0.5


class RoteamentoError(Exception):
    """Erro de domínio: grafo não possui estrutura mínima para rotear (ex.: sem fallback)."""


def _normalizar(texto: str) -> str:
    """Normaliza texto para comparação determinística: lowercase, sem acentuação."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.lower()


def _nos_entry_point(grafo: Grafo) -> frozenset[str]:
    return frozenset(n.id for n in grafo.nos_por_id if n.tipo is TipoNo.ENTRY_POINT)


def _e_candidata(aresta: Aresta, origens_validas: frozenset[str]) -> bool:
    if not set(aresta.origens) & origens_validas:
        return False
    return len(aresta.condicoes.keywords) > 0


def _score_aresta(aresta: Aresta, solicitacao_normalizada: str) -> float:
    keywords = aresta.condicoes.keywords
    total = len(keywords)
    matches = sum(
        1 for kw in keywords if _normalizar(kw) in solicitacao_normalizada
    )
    if matches == 0:
        return 0.0
    return matches / total


def _escolher_melhor_aresta(
    candidatos: list[tuple[float, Aresta]],
) -> tuple[float, Aresta | None]:
    if not candidatos:
        return 0.0, None
    if len(candidatos) == 1:
        return candidatos[0]

    # Ordenação estável por score desc — preserva ordem de declaração em empates.
    ordenados = sorted(candidatos, key=lambda item: item[0], reverse=True)
    melhor_score = ordenados[0][0]
    segundo_score = ordenados[1][0]

    zona_ambiguidade = (
        (melhor_score - segundo_score) <= _AMBIGUITY_DELTA + _EPSILON
        and segundo_score > _AMBIGUITY_FLOOR - _EPSILON
    )
    if not zona_ambiguidade:
        return ordenados[0]

    zona = [
        item
        for item in ordenados
        if (melhor_score - item[0]) <= _AMBIGUITY_DELTA + _EPSILON
        and item[0] > _AMBIGUITY_FLOOR - _EPSILON
    ]
    # max() com stable sort preserva a primeira aresta declarada em empate de prioridade.
    return max(zona, key=lambda item: item[1].prioridade)


def _nivel_para_score(score: float) -> NivelRouting:
    if score >= _THRESHOLD_RULE_BASED:
        return NivelRouting.RULE_BASED
    if score >= _THRESHOLD_SEMANTIC:
        return NivelRouting.SEMANTIC
    if score >= _THRESHOLD_LLM_ASSISTED:
        return NivelRouting.LLM_ASSISTED
    return NivelRouting.OUT_OF_DOMAIN


def _escolher_fallback(grafo: Grafo) -> str:
    fallback_ids = [n.id for n in grafo.nos_por_id if n.tipo is TipoNo.FALLBACK]
    if not fallback_ids:
        raise RoteamentoError("Grafo não possui nó 'fallback' declarado — roteamento impossível")
    if len(fallback_ids) == 1:
        return fallback_ids[0]

    origens_validas = _nos_entry_point(grafo)
    melhor_id = fallback_ids[0]
    melhor_prioridade: float | None = None
    for fid in fallback_ids:
        prioridades = [
            a.prioridade
            for a in grafo.arestas
            if a.para == fid and set(a.origens) & origens_validas
        ]
        if not prioridades:
            continue
        prioridade_max = max(prioridades)
        if melhor_prioridade is None or prioridade_max > melhor_prioridade:
            melhor_prioridade = prioridade_max
            melhor_id = fid
    return melhor_id


def _workflow_para_agente(grafo: Grafo, escolhido: str) -> Workflow | None:
    for workflow_spec in grafo.workflows:
        if not workflow_spec.etapas:
            continue
        if escolhido in workflow_spec.etapas[0].agent_permitidos:
            return workflow_spec.id
    return None


def rotear(solicitacao: str, grafo: Grafo) -> DecisaoRota:
    """Roteia uma solicitação em texto livre para um agente/workflow, aplicando a política de cascata.

    Args:
        solicitacao: Texto bruto da solicitação do usuário a ser roteada.
        grafo: Grafo dirigido compilado por `graph_loader.carregar_grafo`.

    Returns:
        DecisaoRota: Decisão de roteamento contendo o agente escolhido, o
        workflow associado (quando aplicável), o nível de roteamento
        aplicado (`NivelRouting`) e o score calculado.

    Raises:
        ValueError: Se `solicitacao` for string vazia.
    """
    if not solicitacao or not solicitacao.strip():
        raise ValueError("'solicitacao' não pode ser vazia")

    solicitacao_normalizada = _normalizar(solicitacao)
    origens_validas = _nos_entry_point(grafo)

    candidatos = [
        (_score_aresta(aresta, solicitacao_normalizada), aresta)
        for aresta in grafo.arestas
        if _e_candidata(aresta, origens_validas)
    ]
    candidatos = [item for item in candidatos if item[0] > 0.0]

    melhor_score, melhor_aresta = _escolher_melhor_aresta(candidatos)
    nivel = _nivel_para_score(melhor_score)

    if nivel is NivelRouting.OUT_OF_DOMAIN:
        escolhido = _escolher_fallback(grafo)
        workflow = _workflow_para_agente(grafo, escolhido)
        return DecisaoRota(
            escolhido=escolhido, workflow=workflow, nivel=nivel, score=melhor_score
        )

    assert melhor_aresta is not None  # nivel != OUT_OF_DOMAIN implica candidato existente
    escolhido = melhor_aresta.para
    workflow = _workflow_para_agente(grafo, escolhido)
    return DecisaoRota(escolhido=escolhido, workflow=workflow, nivel=nivel, score=melhor_score)
