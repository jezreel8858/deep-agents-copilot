"""governance — wrapper fino de import/re-export tipado sobre `governance_runner`.

Este modulo NUNCA reimplementa logica de roteamento/governanca — apenas
repassa os simbolos publicos de `governance_runner.routing` e
`governance_runner.runner` para um unico ponto de import interno do
gateway (R-046). Validavel via:
    grep -r "def rotear" deploy/local-chat-gateway/src   # deve retornar vazio

`Catalogo` e `TabelaTransicao` sao reexportados diretamente da fachada
publica `governance_runner.routing` (Q-05), eliminando a necessidade de
import direto do submodulo interno `routing.model`.
"""

from __future__ import annotations

from governance_runner.routing import (
    Catalogo,
    DecisaoRota,
    Deriva,
    Evento,
    Fase,
    GraphValidationError,
    HandoffPayloadInvalidoError,
    NivelRouting,
    RoteamentoError,
    Sessao,
    TabelaTransicao,
    TipoEvento,
    TransicaoInvalidaError,
    Turno,
    Workflow,
    carregar_grafo,
    compilar_tabela_transicao,
    detectar_deriva,
    rotear,
    transicionar,
    validar_handoff,
)
from governance_runner.runner import TETO_TURNOS_R060, Budget, VeredictoOrcamento

__all__ = [
    "DecisaoRota",
    "Deriva",
    "Evento",
    "Fase",
    "GraphValidationError",
    "HandoffPayloadInvalidoError",
    "NivelRouting",
    "RoteamentoError",
    "Sessao",
    "TipoEvento",
    "TransicaoInvalidaError",
    "Turno",
    "Workflow",
    "Catalogo",
    "TabelaTransicao",
    "carregar_grafo",
    "compilar_tabela_transicao",
    "detectar_deriva",
    "rotear",
    "transicionar",
    "validar_handoff",
    "Budget",
    "TETO_TURNOS_R060",
    "VeredictoOrcamento",
]
