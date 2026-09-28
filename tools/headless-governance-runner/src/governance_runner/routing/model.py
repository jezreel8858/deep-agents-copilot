"""
model — Tipos de domínio (Enums e dataclasses frozen) do motor de roteamento.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §6.2), expandido pela
subtask 2 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md conforme o
schema real de `routing-graph.yaml` incorporado por `graph_loader.py`.

Este módulo não contém lógica de negócio — apenas estruturas de dados
imutáveis (`frozen=True`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, NewType


class Workflow(StrEnum):
    """Os 9 workflows canônicos de governança (1:1 com `routing-graph.yaml`)."""

    BUG_FIX = "WORKFLOW-BUG-FIX"
    REFACTORING = "WORKFLOW-REFACTORING"
    TECHNICAL_ANALYSIS = "WORKFLOW-TECHNICAL-ANALYSIS"
    FEATURE_DEVELOPMENT = "WORKFLOW-FEATURE-DEVELOPMENT"
    GOVERNANCE_MAINTENANCE = "WORKFLOW-GOVERNANCE-MAINTENANCE"
    DEPENDENCY_VULN = "WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION"
    FRAMEWORK_MIGRATION = "WORKFLOW-FRAMEWORK-MIGRATION"
    RELEASE_READINESS = "WORKFLOW-RELEASE-READINESS"
    PROMPT_SYNTHESIS = "WORKFLOW-PROMPT-SYNTHESIS"


class Fase(StrEnum):
    """Fases da sessão de governança (máquina de estados de alto nível)."""

    ROUTER = "router"
    EM_WORKFLOW = "em_workflow"
    AGUARDANDO_HUMANO = "aguardando_humano"
    CONCLUIDO = "concluido"


class TipoNo(StrEnum):
    """Tipos de nó do grafo `routing-graph.yaml` (37 nós no total)."""

    ENTRY_POINT = "entry_point"
    HEALTH_CHECK = "health_check"
    MANDATORY_PRE_STEP = "mandatory_pre_step"
    DOMAIN_ROUTER = "domain_router"
    DOWNSTREAM = "downstream"
    FALLBACK = "fallback"


class NivelRouting(StrEnum):
    """Níveis da política de cascata (thresholds 0.9 / 0.7 / 0.5 / 0.0)."""

    RULE_BASED = "rule_based"
    SEMANTIC = "semantic"
    LLM_ASSISTED = "llm_assisted"
    OUT_OF_DOMAIN = "out_of_domain"


class TipoEvento(StrEnum):
    """Tipos de evento que podem disparar uma transição em `state_machine.transicionar`.

    Cada valor corresponde a uma categoria de guard clause do contrato
    (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §6.2 / subtask 3 do
    PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md):
        - `DECISAO_ROTEAMENTO`: decisão de `router.rotear` emitida a partir
          da `Fase.ROUTER` (única forma legal de originar um workflow, R-037).
        - `AVANCO_ETAPA`: avanço sequencial ou permanência dentro de um
          workflow já em curso (R-050).
        - `DERIVA_DETECTADA`: sinal de `drift.py` indicando deriva de
          intenção — força reset incondicional para o router (R-042).
        - `CONCLUSAO_WORKFLOW`: encerramento da última etapa de um workflow,
          com reset mandatório para `Fase.ROUTER` (R-052).
    """

    DECISAO_ROTEAMENTO = "decisao_roteamento"
    AVANCO_ETAPA = "avanco_etapa"
    DERIVA_DETECTADA = "deriva_detectada"
    CONCLUSAO_WORKFLOW = "conclusao_workflow"


@dataclass(frozen=True)
class Sessao:
    """Estado imutável de uma sessão de governança em andamento."""

    fase: Fase
    workflow: Workflow | None
    etapa: int  # 0 = ainda no router
    agente_ativo: str
    aprovacoes: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Turno:
    """Um turno de conversa (texto bruto do usuário) a ser classificado."""

    texto: str


@dataclass(frozen=True)
class Evento:
    """Evento de entrada que dispara uma possível transição de estado.

    Expandido pela subtask 3 (`state_machine.transicionar`) com os campos
    necessários para os guard clauses R-037/R-042/R-050/R-064 — todos os
    campos novos possuem defaults resilientes para preservar retrocompatibilidade
    com os construtores minimalistas usados por `drift.py`/testes existentes.
    """

    origem: str
    turno: Turno = field(default_factory=lambda: Turno(texto=""))
    tipo: TipoEvento = TipoEvento.AVANCO_ETAPA
    agente_solicitado: str | None = None
    etapa_solicitada: int | None = None
    aprovacao_concedida: bool = False
    workflow_solicitado: Workflow | None = None


@dataclass(frozen=True)
class Deriva:
    """Resultado da detecção de deriva de intenção (R-042)."""

    houve: bool
    motivos: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisaoRota:
    """Resultado de uma decisão de roteamento (`router.rotear`)."""

    escolhido: str
    workflow: Workflow | None
    nivel: NivelRouting
    score: float


@dataclass(frozen=True)
class No:
    """Um nó do grafo `routing-graph.yaml` (agent disponível para roteamento)."""

    id: str
    tipo: TipoNo
    descricao: str = ""


@dataclass(frozen=True)
class CondicaoAresta:
    """Condições declaradas de uma aresta de roteamento (`arestas[*].condicoes`).

    Campos ausentes no YAML recebem defaults resilientes (gaps RG-01/RG-03
    do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md):
        - `tipo`: default `"keyword_based"` quando não declarado (RG-01).
        - `politica_desvio`: default `"strict"` quando não declarado (RG-03).
    """

    tipo: str = "keyword_based"
    regra: str | None = None
    gatilho: str | None = None
    keywords: tuple[str, ...] = ()
    sinal: str | None = None
    sinal_r006: str | None = None
    nao_confundir_com: tuple[str, ...] = ()
    fast_path_bypass: tuple[str, ...] = ()
    loop_maximo: int | None = None
    retorno_obrigatorio: str | None = None
    proibido: str | None = None
    aplica_a: str | None = None
    acao: str | None = None
    politica_desvio: str = "strict"


@dataclass(frozen=True)
class Aresta:
    """Uma aresta dirigida do grafo de roteamento (`arestas[*]`).

    `de`/`para` preservam o valor bruto do YAML — incluindo wildcards de
    tipo (`"*downstream"`) e listas `|`-separadas de nós concretos — sem
    resolução em runtime (RG-04). Use `origens`/`destinos` para a forma
    tokenizada.
    """

    de: str
    para: str
    prioridade: float
    threshold_score: float
    nivel_routing: str
    condicoes: CondicaoAresta

    @property
    def origens(self) -> tuple[str, ...]:
        """Tokens de `de` separados por `|`, com espaços removidos."""
        return tuple(t.strip() for t in self.de.split("|"))

    @property
    def destinos(self) -> tuple[str, ...]:
        """Tokens de `para` separados por `|`, com espaços removidos."""
        return tuple(t.strip() for t in self.para.split("|"))


@dataclass(frozen=True)
class EtapaSpec:
    """Especificação de uma etapa de workflow na `TabelaTransicao`.

    `agent_permitidos` armazena todas as alternativas `|`-separadas do
    campo `agent`/`agents_permitidos` do YAML (RG-04) sem resolvê-las em
    runtime — a resolução de aliases `specialist-<papel>` cabe ao domain
    router ativo, nunca ao `graph_loader`.
    """

    agent_permitidos: frozenset[str]
    sub_rotinas_permitidas: frozenset[str] = field(default_factory=frozenset)
    requer_aprovacao: bool = False
    proxima: int | None = None


@dataclass(frozen=True)
class WorkflowSpec:
    """Especificação completa de um workflow canônico (`workflows[*]`)."""

    id: Workflow
    nome: str
    etapas: tuple[EtapaSpec, ...]


@dataclass(frozen=True)
class Catalogo:
    """Vista tipada de `catalog.yaml` (agentes, tools, competências)."""

    agentes: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Grafo:
    """Grafo dirigido compilado a partir de `routing-graph.yaml`.

    Todas as coleções são estruturas imutáveis (`frozenset`/`tuple`) para
    preservar `frozen=True` e permitir hashing/compartilhamento seguro
    entre sessões concorrentes do runner headless.
    """

    nos: frozenset[str] = field(default_factory=frozenset)
    nos_por_id: tuple[No, ...] = ()
    arestas: tuple[Aresta, ...] = ()
    workflows: tuple[WorkflowSpec, ...] = ()

    def no(self, id_no: str) -> No | None:
        """Retorna o `No` com o `id` informado, ou `None` se inexistente."""
        for n in self.nos_por_id:
            if n.id == id_no:
                return n
        return None


@dataclass(frozen=True)
class TabelaTransicao:
    """Tabela imutável `(Workflow, etapa) -> EtapaSpec`, emitida pelo graph_loader."""

    etapas: dict[tuple[Workflow, int], EtapaSpec]
    catalogo: Catalogo


HandoffPayload = NewType("HandoffPayload", dict[str, Any])
"""Payload validado de handoff entre agentes (schema handoff-governance/SKILL.md)."""
