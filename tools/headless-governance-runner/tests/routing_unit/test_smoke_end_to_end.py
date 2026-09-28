"""
Smoke test end-to-end do pacote `routing/` (subtask 7 do Bloco A —
Convergência do Eixo 2, PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md).

Exercita exclusivamente a API de fachada pública exportada por
`governance_runner.routing` (nunca os submódulos internos diretamente),
encadeando os 3 cenários exigidos pelo DoD da subtask 7:

    1. Caso feliz completo: carregar o `routing-graph.yaml` real →
       `rotear(...)` → `DecisaoRota` rule-based → `Sessao` inicial em
       `Fase.ROUTER` → `transicionar()` → nova `Sessao` em
       `Fase.EM_WORKFLOW`.
    2. Deriva detectada: turno com bypass explícito do agent-router em
       plena `Fase.EM_WORKFLOW` → `detectar_deriva` sinaliza o motivo →
       evento `DERIVA_DETECTADA` → `transicionar()` → reset incondicional
       para `Fase.ROUTER` (R-042).
    3. (Opcional) Validação de handoff com o payload gerado a partir da
       `DecisaoRota` do cenário 1.

Zero import de Copilot SDK, zero rede — 100% determinístico, executável
localmente (`pytest tests/routing_unit`) sem qualquer dependência externa
além de PyYAML/jsonschema já declaradas em `pyproject.toml`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from governance_runner.routing import (
    DecisaoRota,
    Deriva,
    Evento,
    Fase,
    Sessao,
    Turno,
    Workflow,
    carregar_grafo,
    compilar_tabela_transicao,
    detectar_deriva,
    rotear,
    transicionar,
    validar_handoff,
)
# TipoEvento não integra a lista fechada de exportações da subtask 7 —
# importado do submódulo de tipos apenas para construir os `Evento` de teste.
from governance_runner.routing.model import Grafo, TabelaTransicao, TipoEvento

SCHEMA_PATH = (
    Path(__file__).parents[2]
    / "src"
    / "governance_runner"
    / "routing"
    / "routing-graph.schema.json"
)
REAL_GRAPH_PATH = Path(__file__).parents[4] / ".github" / "agents" / "routing-graph.yaml"


@pytest.fixture(scope="module")
def grafo_real() -> object:
    if not REAL_GRAPH_PATH.exists():
        pytest.skip("routing-graph.yaml real não encontrado neste checkout")
    return carregar_grafo(REAL_GRAPH_PATH, SCHEMA_PATH)


@pytest.fixture(scope="module")
def tabela_real(grafo_real):  # type: ignore[no-untyped-def]
    return compilar_tabela_transicao(grafo_real)


class TestSmokeEndToEndCasoFeliz:
    """Cenário 1: grafo real → rotear → Sessao(ROUTER) → transicionar → EM_WORKFLOW."""

    def test_carregar_rotear_e_transicionar_para_em_workflow(
        self, grafo_real: Grafo, tabela_real: TabelaTransicao
    ) -> None:
        solicitacao = (
            "Isso é um bug, deu erro, é uma regressao, houve falha em producao, "
            "nao funciona, nao consigo acessar, quebrou, apareceu exception, NPE, "
            "erro 500 e um stack trace no log."
        )

        decisao = rotear(solicitacao, grafo_real)

        assert isinstance(decisao, DecisaoRota)
        assert decisao.escolhido == "bug-triage"
        assert decisao.workflow is Workflow.BUG_FIX

        sessao_inicial = Sessao(
            fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router"
        )
        evento = Evento(
            origem="usuario",
            tipo=TipoEvento.DECISAO_ROTEAMENTO,
            workflow_solicitado=decisao.workflow,
            agente_solicitado=decisao.escolhido,
        )

        nova_sessao = transicionar(sessao_inicial, evento, tabela_real)

        assert nova_sessao.fase is Fase.EM_WORKFLOW
        assert nova_sessao.workflow is Workflow.BUG_FIX
        assert nova_sessao.etapa == 1
        assert nova_sessao.agente_ativo == "bug-triage"


class TestSmokeEndToEndDerivaDetectada:
    """Cenário 2: bypass explícito do agent-router em workflow → reset para ROUTER (R-042)."""

    def test_deriva_detectada_forca_reset_incondicional_para_router(
        self, tabela_real: TabelaTransicao
    ) -> None:
        sessao_em_workflow = Sessao(
            fase=Fase.EM_WORKFLOW,
            workflow=Workflow.BUG_FIX,
            etapa=1,
            agente_ativo="bug-triage",
        )
        turno = Turno(texto="Chame direto o @security-reviewer, sem passar pelo router.")

        deriva = detectar_deriva(sessao_em_workflow, turno, tabela_real.catalogo)

        assert isinstance(deriva, Deriva)
        assert deriva.houve is True
        assert "bypass_agent_router" in deriva.motivos

        evento_deriva = Evento(origem="drift-detector", tipo=TipoEvento.DERIVA_DETECTADA)
        nova_sessao = transicionar(sessao_em_workflow, evento_deriva, tabela_real)

        assert nova_sessao.fase is Fase.ROUTER
        assert nova_sessao.workflow is None
        assert nova_sessao.etapa == 0
        assert nova_sessao.agente_ativo == "agent-router"


class TestSmokeEndToEndValidacaoHandoffOpcional:
    """Cenário 3 (opcional): valida o payload de handoff gerado a partir da DecisaoRota."""

    def test_validar_handoff_com_payload_derivado_da_decisao_de_roteamento(
        self, grafo_real: Grafo
    ) -> None:
        decisao = rotear(
            "Isso é um bug, deu erro, houve falha em producao, apareceu exception "
            "e um stack trace no log.",
            grafo_real,
        )
        assert decisao.workflow is not None

        payload = {
            "versao": "1.3",
            "para": decisao.escolhido,
            "motivo": "Roteamento automático — smoke test end-to-end (subtask 7).",
            "emissor": {"nome": "agent-router"},
            "contexto": {
                "solicitacao_original": "Isso é um bug, deu erro, houve falha em producao.",
                "trabalho_realizado": "Decisão de roteamento calculada via rotear().",
            },
            "roteamento_grafo": {
                "current_node": "agent-router",
                "next_node": decisao.escolhido,
            },
            "workflow_tracking": {
                "workflow_id": decisao.workflow.value,
                "politica_desvio": "strict",
            },
        }

        resultado = validar_handoff(payload)

        assert resultado["para"] == decisao.escolhido
        assert resultado["workflow_tracking"]["workflow_id"] == decisao.workflow.value
