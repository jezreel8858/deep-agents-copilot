"""Aceite B1 (plano §3.1): WorkflowSpec.gatilhos / fast_path no graph_loader."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from governance_runner.routing.graph_loader import GraphValidationError, carregar_grafo
from governance_runner.routing.model import WorkflowSpec

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMA = Path(__file__).parents[2] / "src" / "governance_runner" / "routing" / "routing-graph.schema.json"
REAL = Path(__file__).parents[4] / ".github" / "agents" / "routing-graph.yaml"


def _carregar_com(tmp_path: Path, mutar: Any) -> Any:
    """Copia o grafo real, aplica 'mutar(workflows)' e carrega."""
    doc = yaml.safe_load(REAL.read_text(encoding="utf-8"))
    mutar(doc["workflows"])
    alvo = tmp_path / "g.yaml"
    alvo.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return carregar_grafo(alvo, SCHEMA)


def test_defaults_do_dataclass() -> None:
    w = WorkflowSpec(id="X", nome="n", etapas=())  # type: ignore[arg-type]
    assert w.gatilhos == () and w.fast_path is False


def test_grafo_real_expoe_gatilhos_e_fast_path() -> None:
    g = carregar_grafo(REAL, SCHEMA)
    assert len(g.workflows) == 9
    por_id = {str(getattr(w.id, "value", w.id)): w for w in g.workflows}
    assert por_id["WORKFLOW-BUG-FIX"].fast_path is True
    assert por_id["WORKFLOW-FEATURE-DEVELOPMENT"].fast_path is False
    assert "bug" in por_id["WORKFLOW-BUG-FIX"].gatilhos
    assert all(isinstance(x, tuple) for x in (w.gatilhos for w in g.workflows))
    assert all(w.gatilhos for w in g.workflows)


def test_fixture_reduzida_expoe_gatilhos_declarados() -> None:
    g = carregar_grafo(FIXTURES_DIR / "valid_graph.yaml", SCHEMA)
    w = g.workflows[0]
    assert w.gatilhos == ("bug", "erro") and w.fast_path is True


def test_gatilhos_sao_strip_e_tupla(tmp_path: Path) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0]["gatilhos"] = ["  alfa  ", "beta"]

    g = _carregar_com(tmp_path, mut)
    assert g.workflows[0].gatilhos == ("alfa", "beta")


def test_gatilhos_lista_vazia_vira_tupla_vazia(tmp_path: Path) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0]["gatilhos"] = []

    assert _carregar_com(tmp_path, mut).workflows[0].gatilhos == ()


def test_gatilhos_nulo_e_rejeitado_pelo_schema(tmp_path: Path) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0]["gatilhos"] = None

    with pytest.raises(GraphValidationError, match="gatilhos"):
        _carregar_com(tmp_path, mut)


def test_gatilhos_ausente_vira_tupla_vazia(tmp_path: Path) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0].pop("gatilhos", None)

    assert _carregar_com(tmp_path, mut).workflows[0].gatilhos == ()


@pytest.mark.parametrize("invalido", ["texto solto", 5, {"a": 1}, [1, 2], ["ok", ""], ["ok", "   "], ["ok", None]])
def test_gatilhos_invalidos_levantam_erro_explicito(tmp_path: Path, invalido: Any) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0]["gatilhos"] = invalido

    with pytest.raises(GraphValidationError, match="gatilhos"):
        _carregar_com(tmp_path, mut)


@pytest.mark.parametrize("invalido", ["true", 1, 0, "sim", []])
def test_fast_path_nao_booleano_levanta_erro(tmp_path: Path, invalido: Any) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0]["fast_path"] = invalido

    with pytest.raises(GraphValidationError, match="fast_path"):
        _carregar_com(tmp_path, mut)


def test_fast_path_ausente_default_false(tmp_path: Path) -> None:
    def mut(ws: list[dict[str, Any]]) -> None:
        ws[0].pop("fast_path", None)

    assert _carregar_com(tmp_path, mut).workflows[0].fast_path is False
