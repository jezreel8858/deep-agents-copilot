from __future__ import annotations

import pytest

from governance_runner.synth.normalize import (
    DIRETIVAS_OVERRIDE,
    OVERRIDE_DIRECTIVE_REASON,
    contem_override,
    detectar_override,
    normalizar,
    normalizar_texto,
    sanitizar_prompt,
)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("ÁÇÃO  Olá!!", "acao ola"),
        ("  Bug_no   Checkout  ", "bug no checkout"),
        ("", ""),
        ("   ", ""),
        ("a", "a"),
    ],
)
def test_normalizar_casos_borda(entrada: str, esperado: str) -> None:
    assert normalizar(entrada) == esperado


def test_normalizar_idempotente_e_alias() -> None:
    texto = "Corrigir o BUG do Checkout, por favor!"
    uma = normalizar(texto)
    assert normalizar(uma) == uma
    assert normalizar_texto(texto) == uma


def test_normalizar_equivale_variantes_unicode() -> None:
    assert normalizar("ação") == normalizar("acao")
    assert normalizar("ＡＢＣ") == "abc"


@pytest.mark.parametrize("diretiva", list(DIRETIVAS_OVERRIDE))
def test_detectar_override_para_cada_diretiva(diretiva: str) -> None:
    assert detectar_override("por favor " + diretiva + " agora") is not None
    assert contem_override(diretiva) is True


def test_texto_limpo_nao_e_override() -> None:
    texto = "Corrigir bug no endpoint de checkout"
    assert detectar_override(texto) is None
    assert contem_override(texto) is False


def test_sanitizar_prompt_limpo_vs_override() -> None:
    ok_limpo, motivo_limpo = sanitizar_prompt("Escrever testes para o servico de pedidos")
    assert motivo_limpo is None
    ok_sujo, motivo_sujo = sanitizar_prompt(DIRETIVAS_OVERRIDE[0])
    assert motivo_sujo == OVERRIDE_DIRECTIVE_REASON
    assert ok_limpo != ok_sujo
