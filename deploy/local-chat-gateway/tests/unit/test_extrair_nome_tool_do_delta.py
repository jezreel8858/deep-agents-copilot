"""Testes unitarios puros de `routes._extrair_nome_tool_do_delta`.

Cobre o parsing do texto emitido por `sdk_session.stream_chat` para
popular `tools_executed` na telemetria (`emit_chat_trace`) -- tanto o
padrao generico de tool quanto o marcador de delegacao de agent com o
NOME REAL do subagent invocado (`SubagentStartedData.agent_name`/
`agent_display_name`, RT-03 -- introspecao real confirmada via wheel
`github_copilot_sdk==1.0.15`), introduzido para dar visibilidade de
handoffs de agent no stream da LobeChat (pedido real do usuario:
paridade parcial com o painel nativo da IDE do GitHub Copilot).
"""

from __future__ import annotations

from local_chat_gateway.api.routes import (
    _PREFIXO_TELEMETRIA_SUBAGENT,
    _extrair_nome_tool_do_delta,
)


def test_deve_retornar_none_quando_delta_nao_contem_evento_de_tool() -> None:
    assert _extrair_nome_tool_do_delta("ola, como posso ajudar?") is None


def test_deve_extrair_nome_da_tool_generica_no_padrao_confirmado() -> None:
    delta = "\n> \U0001f527 tool: read_file (iniciando)\n"
    assert _extrair_nome_tool_do_delta(delta) == "read_file"


def test_deve_retornar_none_quando_delta_e_apenas_evento_de_conclusao() -> None:
    """`(concluido)` nao deve ser confundido com inicio de execucao."""
    delta = "\n> \U0001f527 tool: read_file concluido\n"
    assert _extrair_nome_tool_do_delta(delta) is None


def test_deve_extrair_nome_real_do_subagent_quando_marcador_presente() -> None:
    """Confirma extracao do NOME REAL do agent (`python-bug-fixer`), nao
    apenas o literal `run_subagent` -- ganho concreto do RT-03 em relacao
    a implementacao anterior (que so sabia dizer "houve uma delegacao")."""
    delta = "\n> \U0001f9ed **Subagent invocado:** `python-bug-fixer` (iniciando)\n"
    assert (
        _extrair_nome_tool_do_delta(delta)
        == f"{_PREFIXO_TELEMETRIA_SUBAGENT}python-bug-fixer"
    )
    assert _PREFIXO_TELEMETRIA_SUBAGENT == "subagent:"


def test_marcador_de_subagent_tem_precedencia_sobre_padrao_generico() -> None:
    """Mesmo que o texto contenha a substring "tool:" em outro ponto, o
    marcador de subagent deve ser priorizado (evita falso-negativo caso
    a mensagem venha acompanhada de outro texto)."""
    delta = (
        "\n> \U0001f9ed **Subagent invocado:** `python-feature-developer` (iniciando)\n"
        "\n> \U0001f527 tool: nao deveria ser lido (iniciando)\n"
    )
    assert (
        _extrair_nome_tool_do_delta(delta)
        == f"{_PREFIXO_TELEMETRIA_SUBAGENT}python-feature-developer"
    )


def test_deve_retornar_none_quando_marcador_de_subagent_tem_nome_vazio() -> None:
    """Defensivo: nome de agent vazio (campo `str` obrigatorio mas vazio no
    SDK real) nao deve gerar entrada invalida em `tools_executed`."""
    delta = "\n> \U0001f9ed **Subagent invocado:** `` (iniciando)\n"
    assert _extrair_nome_tool_do_delta(delta) is None

