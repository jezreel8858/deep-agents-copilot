from __future__ import annotations

import pytest

from governance_runner.synth.storage import SynthRepository
from governance_runner.synth.use_cases import (
    SynthOrcamentoInvalidoError,
    executar_synth_eval,
    executar_synth_generate,
    validar_orcamento_synth,
)

from .conftest import FakeSDKClient


def test_eval_sem_teto_falha_com_exit_2() -> None:
    with pytest.raises(SynthOrcamentoInvalidoError) as exc:
        validar_orcamento_synth("synth-eval", None, env={})
    assert exc.value.exit_code == 2


def test_generate_sdk_sem_teto_falha_mas_template_nao() -> None:
    with pytest.raises(SynthOrcamentoInvalidoError):
        validar_orcamento_synth("synth-generate", None, "sdk", env={})
    validar_orcamento_synth("synth-generate", None, "template", env={})


@pytest.mark.parametrize("valor", ["0", "-1", "abc", ""])
def test_valores_invalidos_de_teto_rejeitados(valor: str) -> None:
    with pytest.raises(SynthOrcamentoInvalidoError):
        validar_orcamento_synth("synth-eval", valor, env={})


@pytest.mark.parametrize("valor", [1, "1", 5, "15"])
def test_valores_validos_de_teto_aceitos(valor: int | str) -> None:
    assert validar_orcamento_synth("synth-eval", valor, env={}) == int(valor)


def test_eval_nao_cria_cliente_sem_orcamento(repo: SynthRepository) -> None:
    chamadas: list[int] = []

    def fabrica() -> FakeSDKClient:
        chamadas.append(1)
        return FakeSDKClient()

    with pytest.raises(SynthOrcamentoInvalidoError):
        executar_synth_eval(repo=repo, cliente_factory=fabrica, env={})
    assert chamadas == []


def test_generate_template_offline_sem_teto(repo: SynthRepository) -> None:
    rel = executar_synth_generate(repo=repo, generator_mode="template", dimensions=["distrator_outro_agente"],
                                  per_stratum=1, env={})
    assert rel.comando == "synth-generate" and rel.exit_code == 0 and rel.run_id
    assert rel.contadores.get("n_accepted", 0) > 0 or rel.contadores
