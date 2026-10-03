"""
Testes unitários da fachada pública `governance_runner.routing` (Q-05).

Garante que `Catalogo` e `TabelaTransicao` — hoje definidos em
`governance_runner.routing.model` — sejam importáveis diretamente a
partir do pacote de fachada `governance_runner.routing`, eliminando a
necessidade de consumidores externos (ex.: `local-chat-gateway`)
importarem o submódulo interno `routing.model` diretamente (R-046).
"""

from __future__ import annotations


class TestFachadaPublicaExportaTiposDeCatalogo:
    """Cobertura de exposição de `Catalogo`/`TabelaTransicao` no `__all__`."""

    def test_catalogo_e_tabela_transicao_importaveis_da_fachada(self) -> None:
        from governance_runner.routing import Catalogo, TabelaTransicao

        assert Catalogo is not None
        assert TabelaTransicao is not None

    def test_catalogo_e_tabela_transicao_constam_do_all_publico(self) -> None:
        import governance_runner.routing as routing

        assert "Catalogo" in routing.__all__
        assert "TabelaTransicao" in routing.__all__
