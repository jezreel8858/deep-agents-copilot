"""Testes unitários de local_chat_gateway.checkpoint_engine.

Valida a interpretação pura de respostas a checkpoints humanos segundo
a gramática de R-027/R-064 e a Invariante 11 (custo zero para respostas vagas).
"""

from __future__ import annotations

import pytest

from local_chat_gateway.checkpoint_engine import (
    VAGUE_RESPONSES,
    CheckpointResolution,
    parse_checkpoint_response,
)


def test_deve_resolver_com_sucesso_quando_resposta_simples_valida():
    # Arrange
    entrada = "1"

    # Act
    resultado = parse_checkpoint_response(entrada)

    # Assert
    assert resultado == CheckpointResolution(
        resolved=True,
        checkpoint_id=None,
        option=1,
        free_text=None,
        reason=None,
    )


def test_deve_resolver_com_checkpoint_id_quando_id_informado_na_resposta():
    # Arrange
    entrada = "cp-7f3a 2"

    # Act
    resultado = parse_checkpoint_response(entrada)

    # Assert
    assert resultado == CheckpointResolution(
        resolved=True,
        checkpoint_id="cp-7f3a",
        option=2,
        free_text=None,
        reason=None,
    )


def test_deve_resolver_com_texto_livre_quando_resposta_contem_delimitador_dois_pontos():
    # Arrange
    entrada = "0: ajustar escopo para X"

    # Act
    resultado = parse_checkpoint_response(entrada)

    # Assert
    assert resultado == CheckpointResolution(
        resolved=True,
        checkpoint_id=None,
        option=0,
        free_text="ajustar escopo para X",
        reason=None,
    )


@pytest.mark.parametrize(
    "resposta_vaga",
    sorted(VAGUE_RESPONSES)
    + [
        " PROSSIGA ",
        "Continue",
        "  OK  ",
        "SIM",
        "  yes  ",
        "BeLeZa",
        "CERTO",
        "  vai  ",
    ],
)
def test_deve_rejeitar_como_vague_response_quando_resposta_vaga_invariante_11(
    resposta_vaga: str,
):
    # Arrange & Act
    # Invariante 11 (obrigatória): respostas vagas conhecidas
    # ("prossiga", "continue", "ok", "sim", etc.)
    # nunca resolvem o checkpoint; a pergunta é reemitida sem mudança
    # de estado, a custo zero.
    resultado = parse_checkpoint_response(resposta_vaga)

    # Assert
    assert resultado.resolved is False
    assert resultado.reason == "vague_response"


@pytest.mark.parametrize(
    "resposta_invalida",
    [
        "talvez",
        "",
        "   ",
        "abc",
        "1.5",
        "opcao 1",
        "cp-123 1",  # hash precisa de 4 hexadecimais
        "cp-zzzz 1",  # caracteres não-hexadecimais
    ],
)
def test_deve_rejeitar_como_invalid_grammar_quando_fora_da_gramatica(
    resposta_invalida: str,
):
    # Arrange & Act
    resultado = parse_checkpoint_response(resposta_invalida)

    # Assert
    assert resultado.resolved is False
    assert resultado.reason == "invalid_grammar"


def test_deve_rejeitar_quando_checkpoint_id_da_resposta_diverge_do_aberto():
    # Arrange
    entrada = "cp-bbbb 1"
    checkpoint_aberto = "cp-aaaa"

    # Act
    resultado = parse_checkpoint_response(
        entrada, checkpoint_id_aberto=checkpoint_aberto
    )

    # Assert
    assert resultado.resolved is False
    assert resultado.reason == "checkpoint_id_mismatch"
    assert resultado.checkpoint_id == "cp-bbbb"
    assert resultado.option == 1


def test_deve_preencher_checkpoint_id_aberto_quando_resposta_valida_nao_traz_id():
    # Arrange
    entrada = "1"
    checkpoint_aberto = "cp-aaaa"

    # Act
    resultado = parse_checkpoint_response(
        entrada, checkpoint_id_aberto=checkpoint_aberto
    )

    # Assert
    assert resultado == CheckpointResolution(
        resolved=True,
        checkpoint_id="cp-aaaa",
        option=1,
        free_text=None,
        reason=None,
    )


def test_deve_resolver_com_sucesso_quando_checkpoint_id_coincide_com_o_aberto():
    # Arrange
    entrada = "cp-aaaa 3: detalhe"
    checkpoint_aberto = "cp-aaaa"

    # Act
    resultado = parse_checkpoint_response(
        entrada, checkpoint_id_aberto=checkpoint_aberto
    )

    # Assert
    assert resultado == CheckpointResolution(
        resolved=True,
        checkpoint_id="cp-aaaa",
        option=3,
        free_text="detalhe",
        reason=None,
    )
