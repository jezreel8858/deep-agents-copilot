from __future__ import annotations

from governance_runner.runner import sdk_adapter
from governance_runner.runner.sdk_adapter import (
    SDKRequest,
    SDKResponse,
    construir_permission_handler_read_only,
)

LEITURA = sdk_adapter._TOOLS_LEITURA_PERMITIDAS[0]
ESCRITA = sdk_adapter._PREFIXOS_TOOLS_NEGADAS[0]


def _handler_vazio(nome: str, params: object) -> sdk_adapter.PermissaoDecisao:
    return sdk_adapter.PermissaoDecisao(True, "ok")


def test_sdk_request_system_prompt_retrocompativel() -> None:
    legado = SDKRequest(prompt="p", ferramentas_permitidas=(), permission_handler=_handler_vazio)
    assert legado.system_prompt is None and legado.modelo is None
    novo = SDKRequest(prompt="p", ferramentas_permitidas=("delegar",), permission_handler=_handler_vazio,
                      system_prompt="sistema")
    assert novo.system_prompt == "sistema"


def test_sdk_response_defaults_retrocompativeis() -> None:
    r = SDKResponse(achados=(), premium_requests_consumidos=1)
    assert r.texto == "" and r.tool_events == () and r.turnos_consumidos == 1
    r2 = SDKResponse(achados=(), premium_requests_consumidos=0, texto="x",
                     tool_events=({"tool": "delegar", "para": "a"},))
    assert r2.tool_events[0]["para"] == "a"


def test_agent_audit_default_permite_leitura_com_escopo_vazio() -> None:
    h = construir_permission_handler_read_only([])
    assert h(LEITURA, {"path": "qualquer.py"}).permitido is True


def test_strict_empty_scope_false_explicito_equivale_ao_default() -> None:
    h = construir_permission_handler_read_only([], strict_empty_scope=False)
    assert h(LEITURA, {"path": "a.py"}).permitido is True


def test_strict_empty_scope_true_nega_leitura_vazia() -> None:
    h = construir_permission_handler_read_only([], strict_empty_scope=True)
    d = h(LEITURA, {"path": "a.py"})
    assert d.permitido is False and "strict" in d.motivo


def test_strict_nao_afeta_escopo_preenchido() -> None:
    h = construir_permission_handler_read_only(["a.py"], strict_empty_scope=True)
    assert h(LEITURA, {"path": "a.py"}).permitido is True
    assert h(LEITURA, {"path": "b.py"}).permitido is False


def test_delegar_sempre_permitido_e_escrita_sempre_negada() -> None:
    for strict in (False, True):
        h = construir_permission_handler_read_only([], strict_empty_scope=strict)
        assert h("delegar", {}).permitido is True
        assert h(ESCRITA + "_x", {}).permitido is False
        assert h("ferramenta_desconhecida", {}).permitido is False


def test_compor_prompt_com_e_sem_system_prompt() -> None:
    sem = SDKRequest(prompt="PEDIDO", ferramentas_permitidas=(), permission_handler=_handler_vazio)
    com = SDKRequest(prompt="PEDIDO", ferramentas_permitidas=(), permission_handler=_handler_vazio,
                     system_prompt="REGRAS")
    assert sdk_adapter._DELIM_SYSTEM_INICIO not in sdk_adapter._compor_prompt(sem)
    composto = sdk_adapter._compor_prompt(com)
    assert sdk_adapter._DELIM_SYSTEM_INICIO in composto and "REGRAS" in composto and "PEDIDO" in composto
