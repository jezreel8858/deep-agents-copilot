"""Testes unitários de `governance_runner.routing.handoff` (subtask 6).

Cobre as 8 regras de validação do schema `handoff-governance/SKILL.md` §2.1
(v1.3): campos obrigatórios, retrocompatibilidade v1.0, consistência
`roteamento_grafo.next_node`, enums de `workflow_tracking`/`origem_contexto`,
sanitização fail-closed de segredos e a regra anti-loop trivial (`para` !=
`emissor.nome`).
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from governance_runner.routing.handoff import HandoffPayloadInvalidoError, validar_handoff


def _payload_minimo_v1_0() -> dict[str, Any]:
    """Payload v1.0 mínimo — apenas os 6 campos estritamente obrigatórios."""
    return {
        "versao": "1.0",
        "para": "python-feature-developer",
        "motivo": "Implementar subtask 6 conforme plano de decomposição.",
        "emissor": {"nome": "python-router"},
        "contexto": {
            "solicitacao_original": "Implementar validar_handoff conforme SKILL.md.",
            "trabalho_realizado": "Levantamento de contrato e schema de referência concluído.",
        },
    }


def _payload_completo_v1_3() -> dict[str, Any]:
    """Payload v1.3 completo — todos os blocos aditivos, consistentes entre si."""
    payload = _payload_minimo_v1_0()
    payload["versao"] = "1.3"
    payload["emissor"] = {
        "nome": "python-router",
        "versao": "2.4.0",
        "modelo_llm": "gpt-5",
        "timestamp": "2026-09-28T10:00:00Z",
    }
    payload["roteamento_grafo"] = {
        "current_node": "python-router",
        "next_node": "python-feature-developer",
        "shared_memory_keys": ["plano_decomposicao"],
    }
    payload["origem_contexto"] = {
        "parent_agent": "python-router",
        "task_id": "subtask-6",
        "call_type": "subroutine",
        "return_to_parent": True,
    }
    payload["workflow_tracking"] = {
        "workflow_id": "WORKFLOW-FEATURE-DEVELOPMENT",
        "etapa_atual": 3,
        "total_etapas": 7,
        "nome_etapa": "implementacao_tdd",
        "proximos_agentes_permitidos": ["python-feature-developer"],
        "politica_desvio": "strict",
        "projeto_alvo": {
            "id": "governance-core",
            "root_path": "D:/workspace/deep-agents-copilot",
            "adapter_ref": ".github/instructions/local/governance-core.instructions.md",
        },
        "chaining": {
            "origem_workflow_id": "WORKFLOW-TECHNICAL-ANALYSIS",
            "proposta_referenciada": "PROPOSTA-1",
            "carry_over_state": {
                "arquivos_afetados": ["src/governance_runner/routing/handoff.py"],
                "diagnostico_previo": "Stub identificado, contrato mapeado.",
            },
        },
    }
    payload["contexto"]["descobertas_chave"] = ["Schema v1.3 confirmado no SKILL.md."]
    payload["contexto"]["artefatos"] = ["handoff.py"]
    payload["contexto"]["restricoes"] = ["Não commitar automaticamente (R-031)."]
    payload["proximos_passos_sugeridos"] = ["Executar pytest em routing_unit."]
    payload["nao_retornar_para"] = False
    return payload


# ---------------------------------------------------------------------------
# DoD — payloads-base aceitos.
# ---------------------------------------------------------------------------


def test_payload_minimo_v1_0_e_aceito() -> None:
    resultado = validar_handoff(_payload_minimo_v1_0())
    assert resultado["para"] == "python-feature-developer"


def test_payload_completo_v1_3_consistente_e_aceito() -> None:
    resultado = validar_handoff(_payload_completo_v1_3())
    assert resultado["workflow_tracking"]["workflow_id"] == "WORKFLOW-FEATURE-DEVELOPMENT"


# ---------------------------------------------------------------------------
# Regra 1 — campos obrigatórios ausentes.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "chave_removida",
    ["versao", "para", "motivo"],
)
def test_regra1_campo_top_level_ausente_e_rejeitado(chave_removida: str) -> None:
    payload = _payload_minimo_v1_0()
    del payload[chave_removida]
    with pytest.raises(HandoffPayloadInvalidoError, match=chave_removida):
        validar_handoff(payload)


def test_regra1_emissor_nome_ausente_e_rejeitado() -> None:
    payload = _payload_minimo_v1_0()
    del payload["emissor"]["nome"]
    with pytest.raises(HandoffPayloadInvalidoError, match="emissor.nome"):
        validar_handoff(payload)


def test_regra1_contexto_solicitacao_original_ausente_e_rejeitado() -> None:
    payload = _payload_minimo_v1_0()
    del payload["contexto"]["solicitacao_original"]
    with pytest.raises(HandoffPayloadInvalidoError, match="solicitacao_original"):
        validar_handoff(payload)


def test_regra1_contexto_trabalho_realizado_ausente_e_rejeitado() -> None:
    payload = _payload_minimo_v1_0()
    del payload["contexto"]["trabalho_realizado"]
    with pytest.raises(HandoffPayloadInvalidoError, match="trabalho_realizado"):
        validar_handoff(payload)


# ---------------------------------------------------------------------------
# Regra 2 — retrocompatibilidade v1.0 (blocos aditivos ausentes não rejeitam).
# ---------------------------------------------------------------------------


def test_regra2_ausencia_de_blocos_aditivos_nao_rejeita() -> None:
    payload = _payload_minimo_v1_0()
    assert "roteamento_grafo" not in payload
    assert "origem_contexto" not in payload
    assert "workflow_tracking" not in payload
    resultado = validar_handoff(payload)
    assert resultado["versao"] == "1.0"


# ---------------------------------------------------------------------------
# Regra 3 — consistência roteamento_grafo.next_node == para.
# ---------------------------------------------------------------------------


def test_regra3_next_node_divergente_de_para_e_rejeitado() -> None:
    payload = _payload_completo_v1_3()
    payload["roteamento_grafo"]["next_node"] = "outro-agente-qualquer"
    with pytest.raises(HandoffPayloadInvalidoError, match="next_node"):
        validar_handoff(payload)


def test_regra3_next_node_identico_a_para_e_aceito() -> None:
    payload = _payload_completo_v1_3()
    payload["roteamento_grafo"]["next_node"] = payload["para"]
    resultado = validar_handoff(payload)
    assert resultado["roteamento_grafo"]["next_node"] == resultado["para"]


# ---------------------------------------------------------------------------
# Regra 4 — enum workflow_tracking.workflow_id.
# ---------------------------------------------------------------------------


def test_regra4_workflow_id_invalido_e_rejeitado() -> None:
    payload = _payload_completo_v1_3()
    payload["workflow_tracking"]["workflow_id"] = "WORKFLOW-INEXISTENTE"
    with pytest.raises(HandoffPayloadInvalidoError, match="workflow_id"):
        validar_handoff(payload)


def test_regra4_workflow_id_valido_e_aceito() -> None:
    payload = _payload_completo_v1_3()
    payload["workflow_tracking"]["workflow_id"] = "WORKFLOW-BUG-FIX"
    resultado = validar_handoff(payload)
    assert resultado["workflow_tracking"]["workflow_id"] == "WORKFLOW-BUG-FIX"


# ---------------------------------------------------------------------------
# Regra 5 — enum workflow_tracking.politica_desvio.
# ---------------------------------------------------------------------------


def test_regra5_politica_desvio_invalida_e_rejeitada() -> None:
    payload = _payload_completo_v1_3()
    payload["workflow_tracking"]["politica_desvio"] = "flexivel"
    with pytest.raises(HandoffPayloadInvalidoError, match="politica_desvio"):
        validar_handoff(payload)


def test_regra5_politica_desvio_adaptive_e_aceita() -> None:
    payload = _payload_completo_v1_3()
    payload["workflow_tracking"]["politica_desvio"] = "adaptive"
    resultado = validar_handoff(payload)
    assert resultado["workflow_tracking"]["politica_desvio"] == "adaptive"


# ---------------------------------------------------------------------------
# Regra 6 — enum origem_contexto.call_type.
# ---------------------------------------------------------------------------


def test_regra6_call_type_invalido_e_rejeitado() -> None:
    payload = _payload_completo_v1_3()
    payload["origem_contexto"]["call_type"] = "chamada_qualquer"
    with pytest.raises(HandoffPayloadInvalidoError, match="call_type"):
        validar_handoff(payload)


def test_regra6_call_type_permanent_transfer_e_aceito() -> None:
    payload = _payload_completo_v1_3()
    payload["origem_contexto"]["call_type"] = "permanent_transfer"
    resultado = validar_handoff(payload)
    assert resultado["origem_contexto"]["call_type"] == "permanent_transfer"


# ---------------------------------------------------------------------------
# Regra 7 — sanitização fail-closed de dados sensíveis.
# ---------------------------------------------------------------------------


def test_regra7_token_github_nao_mascarado_em_trabalho_realizado_e_rejeitado() -> None:
    payload = _payload_minimo_v1_0()
    payload["contexto"]["trabalho_realizado"] = (
        "Configurei o CI com o token ghp_1234567890abcdefABCDEFghij no workflow."
    )
    with pytest.raises(HandoffPayloadInvalidoError, match="[Ss]ensível"):
        validar_handoff(payload)


@pytest.mark.parametrize(
    "segredo",
    [
        "sk-abcdefghijklmnopqrstuvwxyz012345",
        "Bearer abcdef123456.token.jwt",
        "AKIAABCDEFGHIJKLMNOP",
        "-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n-----END RSA PRIVATE KEY-----",
    ],
)
def test_regra7_outros_padroes_de_segredo_nao_mascarados_sao_rejeitados(segredo: str) -> None:
    payload = _payload_completo_v1_3()
    payload["contexto"]["descobertas_chave"] = [f"Encontrado: {segredo}"]
    with pytest.raises(HandoffPayloadInvalidoError):
        validar_handoff(payload)


def test_regra7_segredo_ja_mascarado_com_redacted_e_aceito() -> None:
    payload = _payload_minimo_v1_0()
    payload["contexto"]["trabalho_realizado"] = (
        "Token do CI foi rotacionado e mascarado: ghp_***REDACTED*** no log de auditoria."
    )
    resultado = validar_handoff(payload)
    assert "***REDACTED" in resultado["contexto"]["trabalho_realizado"]


# ---------------------------------------------------------------------------
# Regra 8 — 'para' não vazio e diferente de 'emissor.nome'.
# ---------------------------------------------------------------------------


def test_regra8_para_vazio_e_rejeitado() -> None:
    payload = _payload_minimo_v1_0()
    payload["para"] = "   "
    with pytest.raises(HandoffPayloadInvalidoError, match="para"):
        validar_handoff(payload)


def test_regra8_para_identico_a_emissor_nome_e_rejeitado() -> None:
    payload = _payload_minimo_v1_0()
    payload["para"] = payload["emissor"]["nome"]
    with pytest.raises(HandoffPayloadInvalidoError, match="idêntico"):
        validar_handoff(payload)


def test_regra8_para_diferente_de_emissor_nome_e_aceito() -> None:
    payload = _payload_minimo_v1_0()
    assert payload["para"] != payload["emissor"]["nome"]
    resultado = validar_handoff(payload)
    assert resultado["para"] != resultado["emissor"]["nome"]


# ---------------------------------------------------------------------------
# Não-mutação defensiva — validar_handoff não deve alterar o payload de entrada.
# ---------------------------------------------------------------------------


def test_validar_handoff_nao_muta_payload_de_entrada() -> None:
    payload = _payload_completo_v1_3()
    copia = copy.deepcopy(payload)
    validar_handoff(payload)
    assert payload == copia
