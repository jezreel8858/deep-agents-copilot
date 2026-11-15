from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from governance_runner.synth.golden import (
    CONTAGENS_ESPERADAS_POR_SUITE,
    calcular_sha256_golden,
    carregar_golden_bruto,
    carregar_seeds_golden,
    contagens_por_suite,
    resolver_caminho_golden,
)


def _golden_tmp(tmp_path: Path) -> Path:
    doc = {
        "canonicos": [
            {"id": "c-1", "descricao": "d", "input": {"solicitacao": "Corrigir bug no checkout"},
             "expected": {"agent_route": "@bug-triage"}},
            {"id": "c-2", "descricao": "d", "input": {"solicitacao": "Criar endpoint de pedidos"},
             "expected": {"agent_route": "@python-developer"}},
        ],
        "seguranca": [
            {"id": "s-1", "descricao": "d", "input": {"solicitacao": "Revisar vazamento de segredo"},
             "expected": {"agent_route": "@security-auditor"}},
        ],
    }
    p = tmp_path / "golden.yaml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return p


def test_golden_real_existe_e_contagens_batem() -> None:
    caminho = resolver_caminho_golden()
    assert caminho.exists()
    contagens = contagens_por_suite()
    assert contagens == CONTAGENS_ESPERADAS_POR_SUITE


def test_loader_e_somente_leitura() -> None:
    antes = calcular_sha256_golden()
    carregar_golden_bruto()
    carregar_seeds_golden(include_security=True)
    assert calcular_sha256_golden() == antes
    assert len(antes) == 64


def test_seguranca_excluida_por_default_e_incluida_sob_flag() -> None:
    default = carregar_seeds_golden()
    com_seg = carregar_seeds_golden(include_security=True)
    assert {s.suite for s in default}.isdisjoint({"seguranca"})
    assert len(com_seg) > len(default)
    assert all(s.prompt and s.expected_route for s in com_seg)


def test_filtro_targets_tmp(tmp_path: Path) -> None:
    p = _golden_tmp(tmp_path)
    todos = carregar_seeds_golden(golden_path=p)
    assert {s.id for s in todos} == {"c-1", "c-2"}
    filtrados = carregar_seeds_golden(golden_path=p, targets=["python-developer"])
    assert [s.id for s in filtrados] == ["c-2"]
    assert len(carregar_seeds_golden(golden_path=p, targets=["inexistente"])) == 0
    assert {s.id for s in carregar_seeds_golden(golden_path=p, include_security=True)} == {"c-1", "c-2", "s-1"}


def test_golden_inexistente_falha(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        carregar_seeds_golden(golden_path=tmp_path / "nao-existe.yaml")
