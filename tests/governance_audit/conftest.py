"""Fail-fast: perfil de modelos ativo no repo REAL invalida os testes de tier/fanout/R-015/paridade.

Com `.model-profiles/state.json` em phase applied/suspended/pending, os arquivos de agentes podem
divergir do canonico e gerar falsos negativos. Em CI nao bloqueia. Apenas os modulos listados em
GUARDED_MODULES (e `test_r015_*` de test_governance_smells) sao afetados.
"""
from __future__ import annotations

import json
import warnings
from collections.abc import Mapping
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCKING_PHASES = frozenset({"applied", "suspended", "pending"})
GUARDED_MODULES = frozenset({
    "test_agent_model_tier_governance", "test_router_model_tier_fanout",
    "test_hybrid_model_routing_and_zero_noise_governance", "test_model_profiles_parity",
    "test_model_allowlist_governance",
})
SMELLS_MODULE, SMELLS_PREFIX = "test_governance_smells", "test_r015_"
_CACHE: dict[str, str | None] = {}


def is_ci(env: Mapping[str, str]) -> bool:
    return env.get("CI", "").lower() in {"true", "1"} or env.get("GITHUB_ACTIONS", "").lower() == "true"


def is_guarded(nodeid: str) -> bool:
    """True para os modulos de tier/fanout/paridade/allowlist e para `test_r015_*` dos smells."""
    path, _, name = nodeid.replace("\\", "/").partition("::")
    module = path.rsplit("/", 1)[-1].removesuffix(".py")
    if module in GUARDED_MODULES:
        return True
    return module == SMELLS_MODULE and name.split("[", 1)[0].split("::")[-1].startswith(SMELLS_PREFIX)


def evaluate_state_guard(repo_root: Path, env: Mapping[str, str]) -> str | None:
    """Funcao pura: mensagem de bloqueio ou None. JSON ilegivel/malformado => aviso, sem bloqueio."""
    if is_ci(env):
        return None
    state_file = repo_root / ".model-profiles" / "state.json"
    if not state_file.is_file():
        return None
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        phase = data.get("phase") if isinstance(data, dict) else None
    except (OSError, ValueError) as exc:
        warnings.warn(f"state.json de perfis ilegivel ({type(exc).__name__}); guarda ignorada",
                      stacklevel=2)
        return None
    if phase not in BLOCKING_PHASES:
        return None
    return (f"perfil de modelos ativo (phase={phase}) no repositorio: os testes de tier/fanout/R-015/"
            "paridade/allowlist ficariam inconsistentes. Rode `python -m tools.model_profiles restore` "
            "e execute novamente.")


@pytest.fixture(autouse=True)
def _model_profile_state_guard(request: pytest.FixtureRequest) -> None:
    if not is_guarded(request.node.nodeid):
        return
    if "msg" not in _CACHE:
        import os
        _CACHE["msg"] = evaluate_state_guard(REPO_ROOT, os.environ)
    if _CACHE["msg"]:
        pytest.exit(_CACHE["msg"], returncode=2)
