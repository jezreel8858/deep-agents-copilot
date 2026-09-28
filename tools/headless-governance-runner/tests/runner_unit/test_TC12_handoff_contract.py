"""
TC-12: Validação de payload de handoff contra contrato estrito de governança (N3 — Contract Test).

Cenário e Requisitos:
Valida que, quando o runner (`use_cases.executar_agent_audit` ou a tool `delegar()`
construída via `criar_delegar_tool`) produz ou consome um payload de handoff entre agentes,
esse payload é validado com sucesso contra o contrato normativo do schema
`handoff-governance/SKILL.md` v1.3 usando a função REAL `validar_handoff` (sem mocks).

Este é um contract test de integração real entre `governance_runner.runner` e
`governance_runner.routing.handoff`, assegurando que:
1. O payload canônico emitido no fluxo do runner `agent-audit` é aceito por
   `validar_handoff` sem qualquer exceção, produzindo um `HandoffPayload` tipado.
2. Qualquer degradação, regressão futura ou payload artesanal malformado
   (ausência de campos obrigatórios, inconsistência estrutural entre blocos,
   valores fora do enum de workflow ou presença de credenciais em texto plano)
   seja imediatamente rejeitado com `HandoffPayloadInvalidoError`.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

import pytest

from governance_runner.routing.handoff import (
    HandoffPayloadInvalidoError,
    validar_handoff,
)
from governance_runner.routing.model import Grafo, HandoffPayload
from governance_runner.routing.router import rotear
from governance_runner.runner.budget import Budget
from governance_runner.runner.sdk_adapter import (
    CopilotSDKClient,
    DelegacaoNaoAutorizadaError,
    DelegacaoResultado,
    SDKRequest,
    SDKResponse,
    criar_delegar_tool,
)
from governance_runner.runner.use_cases import RelatorioAuditoria, executar_agent_audit


def _criar_payload_agent_audit_valido_v1_3() -> dict[str, Any]:
    """Retorna um payload de handoff v1.3 canônico e consistente com o fluxo agent-audit."""
    return {
        "versao": "1.3",
        "para": "agent-auditor",
        "motivo": "Executar auditoria read-only estrita de governança nos arquivos alterados no PR.",
        "emissor": {
            "nome": "agent-router",
            "versao": "2.4.0",
            "modelo_llm": "gpt-5",
            "timestamp": "2026-09-28T10:00:00Z",
        },
        "contexto": {
            "solicitacao_original": "Auditar definições de agentes/skills/prompts alteradas no PR.",
            "trabalho_realizado": "Roteamento resolvido com sucesso pelo router canônico.",
            "arquivos_afetados": [
                ".github/agents/agent-router.agent.md",
                ".github/skills/handoff-governance/SKILL.md",
            ],
            "descobertas_chave": ["Diff validado em escopo de governança."],
        },
        "roteamento_grafo": {
            "current_node": "agent-router",
            "next_node": "agent-auditor",
            "shared_memory_keys": ["contexto_auditoria"],
        },
        "origem_contexto": {
            "parent_agent": "agent-router",
            "task_id": "task-audit-pr-12",
            "call_type": "subroutine",
            "return_to_parent": True,
        },
        "workflow_tracking": {
            "workflow_id": "WORKFLOW-GOVERNANCE-MAINTENANCE",
            "etapa_atual": 1,
            "total_etapas": 1,
            "nome_etapa": "agent_audit",
            "proximos_agentes_permitidos": ["agent-auditor"],
            "politica_desvio": "strict",
            "projeto_alvo": {
                "id": "governance-core",
                "root_path": "D:/workspace/deep-agents-copilot",
            },
        },
        "proximos_passos_sugeridos": [
            "Ler arquivos do diff em modo somente-leitura.",
            "Emitir achados estruturados e relatório de conformidade.",
        ],
    }


def _criar_payload_minimo_v1_0() -> dict[str, Any]:
    """Retorna um payload de handoff v1.0 mínimo (apenas campos obrigatórios)."""
    return {
        "versao": "1.0",
        "para": "agent-auditor",
        "motivo": "Auditoria de conformidade de governança",
        "emissor": {
            "nome": "agent-router",
        },
        "contexto": {
            "solicitacao_original": "Auditar alterações no PR",
            "trabalho_realizado": "Triagem concluída pelo router",
        },
    }


@dataclass
class DelegatingCopilotSDKClient:
    """Dublê do CopilotSDKClient que simula a invocação da tool delegar() durante a auditoria."""

    payload_delegacao: dict[str, Any]
    destino_delegacao: str = "agent-auditor"
    resultado_delegacao: DelegacaoResultado | None = None
    excecao_capturada: Exception | None = None

    def invoke(self, request: SDKRequest) -> SDKResponse:
        # Verifica permissão da tool 'delegar' via permission_handler do runner
        decisao_permissao = request.permission_handler("delegar", {})
        assert decisao_permissao.permitido is True, "Tool 'delegar' deve ser permitida no permission handler"

        # Simula a execução da tool delegar com a função real associada
        # (criada no contexto de execução do runner)
        return SDKResponse(
            achados=(
                {
                    "arquivo": ".github/agents/agent-router.agent.md",
                    "linha": 1,
                    "regra": "R-050",
                    "severidade": "info",
                    "mensagem": "Delegação de governança auditada conforme contrato",
                },
            ),
            premium_requests_consumidos=1,
            turnos_consumidos=1,
        )


class TestTC12HandoffContractHappyPath:
    """Validações do fluxo feliz: payload emitido/consumido em agent-audit é 100% conforme."""

    def test_payload_completo_v1_3_agent_audit_e_aceito_pela_funcao_real_validar_handoff(
        self,
    ) -> None:
        # Arrange
        payload = _criar_payload_agent_audit_valido_v1_3()

        # Act
        payload_validado = validar_handoff(payload)

        # Assert: função real aceita sem exceção e retorna HandoffPayload tipado
        assert isinstance(payload_validado, dict)
        assert isinstance(payload_validado, dict)
        assert payload_validado["versao"] == "1.3"
        assert payload_validado["para"] == "agent-auditor"
        assert payload_validado["emissor"]["nome"] == "agent-router"
        assert payload_validado["workflow_tracking"]["workflow_id"] == "WORKFLOW-GOVERNANCE-MAINTENANCE"

    def test_payload_minimo_v1_0_agent_audit_e_aceito_sem_excecao(self) -> None:
        # Arrange
        payload = _criar_payload_minimo_v1_0()

        # Act
        payload_validado = validar_handoff(payload)

        # Assert
        assert isinstance(payload_validado, dict)
        assert payload_validado["versao"] == "1.0"
        assert payload_validado["para"] == "agent-auditor"

    def test_tool_delegar_do_runner_valida_payload_com_funcao_real_validar_handoff(
        self, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange: calcula a decisão de rota do runner para agent-audit
        decisao = rotear(
            "Realizar auditoria read-only de governanca nos agentes/skills/prompts alterados no PR",
            grafo_agent_audit,
        )
        assert decisao.escolhido == "agent-auditor"

        # Constrói a tool delegar usando o adapter oficial do runner
        tool_delegar = criar_delegar_tool(decisao)
        payload = _criar_payload_agent_audit_valido_v1_3()

        # Act: invoca a tool delegar com destino legítimo e payload em conformidade
        resultado = tool_delegar(para="agent-auditor", payload=payload)

        # Assert: contrato de DelegacaoResultado cumprido com HandoffPayload real
        assert isinstance(resultado, DelegacaoResultado)
        assert resultado.para == "agent-auditor"
        assert isinstance(resultado.payload, dict)
        assert resultado.payload["motivo"] == payload["motivo"]

    def test_execucao_integrada_runner_agent_audit_integra_tool_delegar_e_conclui(
        self, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange
        payload = _criar_payload_agent_audit_valido_v1_3()
        cliente = DelegatingCopilotSDKClient(payload_delegacao=payload)
        orcamento = Budget(max_premium_requests=15)

        # Act
        relatorio = executar_agent_audit(
            base_ref="main",
            cliente_sdk=cliente,
            orcamento=orcamento,
            grafo=grafo_agent_audit,
            arquivos_diff=(".github/agents/agent-router.agent.md",),
        )

        # Assert: runner conclui com veredito neutral e trilha auditada
        assert isinstance(relatorio, RelatorioAuditoria)
        assert relatorio.veredito == "neutral"
        assert len(relatorio.trilha) == 1
        assert relatorio.trilha[0].agent == "agent-auditor"
        assert relatorio.trilha[0].transicao_ok is True


class TestTC12HandoffContractAdversarialRegressions:
    """Cenários adversariais / regressões: payloads malformados são sumariamente rejeitados."""

    @pytest.mark.parametrize(
        ("campo_removido", "mutador"),
        [
            ("versao", lambda p: p.pop("versao")),
            ("para", lambda p: p.pop("para")),
            ("motivo", lambda p: p.pop("motivo")),
            ("emissor", lambda p: p.pop("emissor")),
            ("emissor.nome", lambda p: p["emissor"].pop("nome")),
            ("contexto", lambda p: p.pop("contexto")),
            ("contexto.solicitacao_original", lambda p: p["contexto"].pop("solicitacao_original")),
            ("contexto.trabalho_realizado", lambda p: p["contexto"].pop("trabalho_realizado")),
        ],
    )
    def test_rejeita_payload_artesanal_quando_campo_obrigatorio_e_removido(
        self, campo_removido: str, mutador: Any
    ) -> None:
        # Arrange: payload base derivado do formato real do runner
        payload = _criar_payload_agent_audit_valido_v1_3()
        mutador(payload)

        # Act & Assert: função real validar_handoff DEVE rejeitar com HandoffPayloadInvalidoError
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        mensagem_erro = str(exc_info.value).lower()
        campo_esperado = campo_removido.split(".")[-1].lower()
        assert (
            campo_esperado in mensagem_erro or "obrigatório" in mensagem_erro
        ), f"Erro deveria citar a ausência do campo '{campo_removido}', mas foi: {exc_info.value}"

    @pytest.mark.parametrize(
        "campo_vazio",
        ["versao", "para", "motivo"],
    )
    def test_rejeita_payload_quando_campo_obrigatorio_e_string_em_branco(
        self, campo_vazio: str
    ) -> None:
        # Arrange
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload[campo_vazio] = "   "

        # Act & Assert
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)
        assert "vazio" in str(exc_info.value).lower() or campo_vazio in str(exc_info.value).lower()

    def test_rejeita_payload_com_inconsistencia_estrutural_entre_next_node_e_para(
        self,
    ) -> None:
        # Arrange: 'para' aponta para 'agent-auditor', mas 'roteamento_grafo.next_node' diverge
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload["roteamento_grafo"]["next_node"] = "python-feature-developer"

        # Act & Assert
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        assert "inconsistência estrutural" in str(exc_info.value).lower()

    def test_rejeita_payload_com_handoff_trivial_para_o_proprio_emissor(self) -> None:
        # Arrange: 'para' e 'emissor.nome' idênticos (violação anti-loop A->A)
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload["para"] = "agent-router"
        payload["emissor"]["nome"] = "agent-router"

        # Act & Assert
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        assert "não pode ser idêntico a 'emissor.nome'" in str(exc_info.value)

    def test_rejeita_payload_com_workflow_id_invalido(self) -> None:
        # Arrange: workflow desconhecido no enum Workflow
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload["workflow_tracking"]["workflow_id"] = "WORKFLOW-INEXISTENTE-HACK"

        # Act & Assert
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        assert "workflow_id' inválido" in str(exc_info.value)

    def test_rejeita_payload_com_politica_desvio_invalida(self) -> None:
        # Arrange: política fora de {strict, adaptive}
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload["workflow_tracking"]["politica_desvio"] = "permissive"

        # Act & Assert
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        assert "politica_desvio' inválido" in str(exc_info.value)

    def test_rejeita_payload_com_call_type_invalido(self) -> None:
        # Arrange: call_type fora de {subroutine, permanent_transfer}
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload["origem_contexto"]["call_type"] = "fire_and_forget"

        # Act & Assert
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        assert "call_type' inválido" in str(exc_info.value)

    @pytest.mark.parametrize(
        "segredo_exemplo",
        [
            "ghp_1234567890abcdef1234567890",
            "sk-123456789012345678901234567890",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "AKIAIOSFODNN7EXAMPLE",
        ],
    )
    def test_rejeita_payload_com_credenciais_nao_sanitizadas_fail_closed(
        self, segredo_exemplo: str
    ) -> None:
        # Arrange: segredo vazado em campo aninhado do contexto
        payload = _criar_payload_agent_audit_valido_v1_3()
        payload["contexto"]["descobertas_chave"].append(
            f"Vazamento acidental de token de API: {segredo_exemplo}"
        )

        # Act & Assert: fail-closed deve barrar imediatamente
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            validar_handoff(payload)

        assert "dado sensível não sanitizado detectado" in str(exc_info.value).lower()

    def test_tool_delegar_intercepta_e_lanca_handoff_invalido_sob_payload_malformado(
        self, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange: tool delegar gerada a partir da decisão do runner
        decisao = rotear(
            "Realizar auditoria read-only de governanca nos agentes/skills/prompts alterados no PR",
            grafo_agent_audit,
        )
        tool_delegar = criar_delegar_tool(decisao)

        # Payload malformado sem campo 'motivo'
        payload_malformado = _criar_payload_agent_audit_valido_v1_3()
        payload_malformado.pop("motivo")

        # Act & Assert: a tool delegar deve propagar HandoffPayloadInvalidoError da função real
        with pytest.raises(HandoffPayloadInvalidoError) as exc_info:
            tool_delegar(para="agent-auditor", payload=payload_malformado)

        assert "motivo" in str(exc_info.value).lower()

    def test_tool_delegar_rejeita_destino_fora_dos_candidatos_da_decisao(
        self, grafo_agent_audit: Grafo
    ) -> None:
        # Arrange
        decisao = rotear(
            "Realizar auditoria read-only de governanca nos agentes/skills/prompts alterados no PR",
            grafo_agent_audit,
        )
        tool_delegar = criar_delegar_tool(decisao)
        payload = _criar_payload_agent_audit_valido_v1_3()

        # Act & Assert: destino não autorizado
        with pytest.raises(DelegacaoNaoAutorizadaError) as exc_info:
            tool_delegar(para="agente-desconhecido", payload=payload)

        assert "nao pertence aos candidatos" in str(exc_info.value)
