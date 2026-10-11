"""Funcao pura de decisao do conftest de tests/governance_audit (fail-fast com perfil ativo)."""
from __future__ import annotations

import json
import warnings

import pytest

from tests.governance_audit.conftest import evaluate_state_guard, is_ci, is_guarded


def _state(root, content):
    d = root / ".model-profiles"
    d.mkdir()
    (d / "state.json").write_text(content if isinstance(content, str) else json.dumps(content),
                                  encoding="utf-8")


def test_sem_state_json_nao_bloqueia(tmp_path):
    assert evaluate_state_guard(tmp_path, {}) is None


@pytest.mark.parametrize("phase", ["applied", "suspended", "pending"])
def test_fases_ativas_bloqueiam_com_mensagem_acionavel(tmp_path, phase):
    _state(tmp_path, {"phase": phase})
    msg = evaluate_state_guard(tmp_path, {})
    assert msg and "python -m tools.model_profiles restore" in msg and phase in msg


def test_phase_restored_nao_bloqueia(tmp_path):
    _state(tmp_path, {"phase": "restored"})
    assert evaluate_state_guard(tmp_path, {}) is None


@pytest.mark.parametrize("env", [{"CI": "true"}, {"GITHUB_ACTIONS": "true"}])
def test_ci_nao_bloqueia(tmp_path, env):
    _state(tmp_path, {"phase": "applied"})
    assert is_ci(env) and evaluate_state_guard(tmp_path, env) is None


@pytest.mark.parametrize("content", ["{nao e json", "[1, 2]", '"x"'])
def test_json_malformado_ou_inesperado_nao_crasha(tmp_path, content):
    _state(tmp_path, content)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        assert evaluate_state_guard(tmp_path, {}) is None


def test_json_malformado_emite_aviso(tmp_path):
    _state(tmp_path, "{x")
    with pytest.warns(UserWarning):
        evaluate_state_guard(tmp_path, {})


@pytest.mark.parametrize("nodeid,expected", [
    ("tests/governance_audit/test_agent_model_tier_governance.py::test_a", True),
    ("tests/governance_audit/test_router_model_tier_fanout.py::test_a", True),
    ("tests/governance_audit/test_model_profiles_parity.py::test_a[x]", True),
    ("tests/governance_audit/test_model_allowlist_governance.py::test_a", True),
    ("tests/governance_audit/test_hybrid_model_routing_and_zero_noise_governance.py::t", True),
    ("tests/governance_audit/test_governance_smells.py::test_r015_algo", True),
    ("tests/governance_audit/test_governance_smells.py::test_r015_algo[p1]", True),
    ("tests/governance_audit/test_governance_smells.py::test_r016_outro", False),
    ("tests/governance_audit/test_changelog_integrity.py::test_a", False),
])
def test_escopo_da_guarda(nodeid, expected):
    assert is_guarded(nodeid) is expected
