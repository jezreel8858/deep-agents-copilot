"""
routing — Motor de roteamento/governança PURO (sem import de SDK, sem rede).

Compila `routing-graph.yaml` em uma state machine em código e aplica os
guard clauses de R-037 (entrada sem router), R-042 (deriva de intenção) e
R-050 (transição ilegal entre etapas de workflow).

Submódulos (contratos completos em BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §6):
    model: Enums e dataclasses frozen do domínio de roteamento.
    graph_loader: parser + validação de `routing-graph.yaml` (subtask 2).
    state_machine: transições dos 9 workflows canônicos (subtask 3).
    drift: detecção de deriva de intenção — R-042 (subtask 4).
    router: roteamento rule-based + política de cascata (subtask 5).
    handoff: contrato de payload entre agentes (subtask 6).

API de fachada pública (subtask 7 — Convergência do Eixo 2):
    Funções: `carregar_grafo`, `compilar_tabela_transicao`, `rotear`,
    `transicionar`, `detectar_deriva`, `validar_handoff`.
    Tipos/Erros: `Sessao`, `Evento`, `Turno`, `Fase`, `Workflow`,
    `DecisaoRota`, `Deriva`, `Catalogo`, `TabelaTransicao`, `NivelRouting`,
    `TransicaoInvalidaError`, `GraphValidationError`, `RoteamentoError`,
    `HandoffPayloadInvalidoError`.

Todo consumidor externo (runner headless, testes de integração) deve
importar exclusivamente a partir deste pacote (`governance_runner.routing`)
— nunca dos submódulos internos diretamente — para preservar a
possibilidade de reorganização interna sem quebra de contrato (R-046).
"""

from __future__ import annotations

from governance_runner.routing.drift import detectar_deriva
from governance_runner.routing.graph_loader import (
    GraphValidationError,
    carregar_grafo,
    compilar_tabela_transicao,
)
from governance_runner.routing.handoff import HandoffPayloadInvalidoError, validar_handoff
from governance_runner.routing.model import (
    Catalogo,
    DecisaoRota,
    Deriva,
    Evento,
    Fase,
    NivelRouting,
    Sessao,
    TabelaTransicao,
    TipoEvento,
    Turno,
    Workflow,
)
from governance_runner.routing.router import RoteamentoError, rotear
from governance_runner.routing.state_machine import TransicaoInvalidaError, transicionar

__all__ = [
    # Funções
    "carregar_grafo",
    "compilar_tabela_transicao",
    "rotear",
    "transicionar",
    "detectar_deriva",
    "validar_handoff",
    # Tipos / Erros
    "Sessao",
    "Evento",
    "Turno",
    "Fase",
    "Workflow",
    "DecisaoRota",
    "Deriva",
    "Catalogo",
    "TabelaTransicao",
    "TipoEvento",
    "NivelRouting",
    "TransicaoInvalidaError",
    "GraphValidationError",
    "RoteamentoError",
    "HandoffPayloadInvalidoError",
]
