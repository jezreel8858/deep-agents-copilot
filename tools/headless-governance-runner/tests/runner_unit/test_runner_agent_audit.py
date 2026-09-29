"""
Testes unitários (N2 — integração do runner com dublê do SDK) para o caso de
uso `agent-audit` (subtask 19 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from governance_runner.routing.model import Grafo
from governance_runner.routing.router import rotear
from governance_runner.runner.budget import TETO_TURNOS_R060, Budget
from governance_runner.runner.sdk_adapter import (
    PermissaoDecisao,
    SDKRequest,
    SDKResponse,
    construir_permission_handler_read_only,
)
from governance_runner.runner.use_cases import RelatorioAuditoria, executar_agent_audit


@dataclass
class FakeCopilotSDKClient:
    """Dublê determinístico de `CopilotSDKClient` para testes N2 (sem instalar o SDK real)."""

    achados: tuple[dict[str, object], ...] = ()
    premium_requests_consumidos: int = 3
    ultima_requisicao: SDKRequest | None = field(default=None)

    def invoke(self, request: SDKRequest) -> SDKResponse:
        self.ultima_requisicao = request
        return SDKResponse(
            achados=self.achados,
            premium_requests_consumidos=self.premium_requests_consumidos,
        )


class TestExecutarAgentAuditFluxoFeliz:
    """Fluxo feliz: FakeCopilotSDKClient -> RelatorioAuditoria com veredito 'neutral'."""

    def test_retorna_relatorio_com_veredito_neutral(self, grafo_agent_audit: Grafo) -> None:
        cliente = FakeCopilotSDKClient(
            achados=(
                {
                    "arquivo": ".github/agents/agent-router.agent.md",
                    "linha": 10,
                    "regra": "R-050",
                    "severidade": "info",
                    "mensagem": "ok",
                },
            )
        )
        orcamento = Budget(max_premium_requests=15)

        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
            arquivos_diff=(".github/agents/agent-router.agent.md",),
        )

        assert isinstance(relatorio, RelatorioAuditoria)
        assert relatorio.use_case == "agent-audit"
        assert relatorio.veredito == "neutral"
        assert relatorio.motivo is None
        assert len(relatorio.achados) == 1
        assert relatorio.achados[0].arquivo == ".github/agents/agent-router.agent.md"
        assert relatorio.custo == {"premium_requests": 3, "turnos": 1}
        assert relatorio.trace_id

    def test_invoca_sdk_com_permission_handler_e_ferramentas_restritas(
        self, grafo_agent_audit: Grafo
    ) -> None:
        cliente = FakeCopilotSDKClient()
        orcamento = Budget(max_premium_requests=15)

        executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        assert cliente.ultima_requisicao is not None
        assert "ler_arquivo" in cliente.ultima_requisicao.ferramentas_permitidas
        assert "delegar" in cliente.ultima_requisicao.ferramentas_permitidas
        assert callable(cliente.ultima_requisicao.permission_handler)


class TestOrcamentoExaurido:
    """Budget exhausted -> neutral / budget_exhausted (nunca crash, nunca sucesso silencioso)."""

    def test_turno_excedido_retorna_neutral_budget_exhausted(self, grafo_agent_audit: Grafo) -> None:
        cliente = FakeCopilotSDKClient()
        orcamento = Budget(max_premium_requests=15)
        for _ in range(TETO_TURNOS_R060):
            orcamento.registrar_turno()

        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        assert relatorio.veredito == "neutral"
        assert relatorio.motivo == "budget_exhausted"
        assert relatorio.achados == ()
        assert cliente.ultima_requisicao is None  # nao deve nem invocar o SDK

    def test_premium_requests_excedido_retorna_neutral_budget_exhausted(
        self, grafo_agent_audit: Grafo
    ) -> None:
        cliente = FakeCopilotSDKClient(premium_requests_consumidos=999)
        orcamento = Budget(max_premium_requests=1)

        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        assert relatorio.veredito == "neutral"
        assert relatorio.motivo == "budget_exhausted"
        assert relatorio.custo["premium_requests"] == 999

    def test_budget_nunca_retorna_success_silencioso_apos_exaustao_reiterada(
        self, grafo_agent_audit: Grafo
    ) -> None:
        cliente = FakeCopilotSDKClient()
        orcamento = Budget(max_premium_requests=15)
        relatorio = None
        for _ in range(TETO_TURNOS_R060 + 3):
            relatorio = executar_agent_audit(
                base_ref="develop",
                cliente_sdk=cliente,
                orcamento=orcamento,
                grafo=grafo_agent_audit,
            )
        assert relatorio is not None
        assert relatorio.veredito == "neutral"
        assert relatorio.motivo == "budget_exhausted"


class TestPermissionHandlerReadOnly:
    """Permission handler read-only estrito: nega escrita/shell/rede; permite leitura em escopo e delegar."""

    def test_nega_tool_de_escrita(self) -> None:
        handler = construir_permission_handler_read_only((".github/agents/agent-router.agent.md",))
        decisao = handler("write_file", {"path": ".github/agents/agent-router.agent.md"})
        assert isinstance(decisao, PermissaoDecisao)
        assert decisao.permitido is False

    def test_nega_tool_de_shell(self) -> None:
        handler = construir_permission_handler_read_only(())
        decisao = handler("run_in_terminal", {"command": "rm -rf /"})
        assert decisao.permitido is False

    def test_nega_tool_de_rede(self) -> None:
        handler = construir_permission_handler_read_only(())
        decisao = handler("network_request", {"url": "https://evil.example"})
        assert decisao.permitido is False

    def test_permite_leitura_de_arquivo_em_escopo(self) -> None:
        arquivo = ".github/skills/handoff-governance/SKILL.md"
        handler = construir_permission_handler_read_only((arquivo,))
        decisao = handler("read_file", {"path": arquivo})
        assert decisao.permitido is True

    def test_nega_leitura_de_arquivo_fora_do_escopo(self) -> None:
        handler = construir_permission_handler_read_only((".github/skills/handoff-governance/SKILL.md",))
        decisao = handler("read_file", {"path": "/etc/passwd"})
        assert decisao.permitido is False

    def test_permite_tool_delegar(self) -> None:
        handler = construir_permission_handler_read_only(())
        decisao = handler("delegar", {"para": "agent-auditor"})
        assert decisao.permitido is True


class TestIntegracaoComRoteamentoReal:
    """rotear() real de routing/ consultado e comprovado (sem mock do motor de roteamento)."""

    def test_rotear_real_resolve_agent_auditor(self, grafo_agent_audit: Grafo) -> None:
        decisao = rotear(
            "Realizar auditoria read-only de governanca nos agentes/skills/prompts alterados no PR",
            grafo_agent_audit,
        )
        assert decisao.escolhido == "agent-auditor"

    def test_trilha_do_relatorio_reflete_decisao_de_roteamento_real(
        self, grafo_agent_audit: Grafo
    ) -> None:
        cliente = FakeCopilotSDKClient()
        orcamento = Budget(max_premium_requests=15)

        relatorio = executar_agent_audit(
            base_ref="develop",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
        )

        assert len(relatorio.trilha) == 1
        etapa = relatorio.trilha[0]
        assert etapa.agent == "agent-auditor"
        assert etapa.transicao_ok is True
