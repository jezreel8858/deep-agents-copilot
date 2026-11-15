from __future__ import annotations

import hashlib

import pytest

from governance_runner.synth.dedup import DedupFunnel, calcular_sha256_normalizado, extrair_ngrams
from governance_runner.synth.golden import carregar_seeds_golden
from governance_runner.synth.normalize import normalizar

BASE = "corrigir o bug no endpoint de checkout em producao"


def test_sha256_normalizado_ignora_caixa_e_pontuacao() -> None:
    assert calcular_sha256_normalizado("Corrigir BUG!") == calcular_sha256_normalizado("corrigir bug")
    assert calcular_sha256_normalizado("a") == hashlib.sha256(normalizar("a").encode("utf-8")).hexdigest()
    assert calcular_sha256_normalizado("a") != calcular_sha256_normalizado("b")


def test_extrair_ngrams_vazio_e_nao_vazio() -> None:
    assert sum(extrair_ngrams("").values()) >= 0
    assert extrair_ngrams("abc def")


def test_corpus_vazio_aceita() -> None:
    res = DedupFunnel().avaliar(BASE)
    assert res.aceito and res.status == "accepted" and res.max_similarity == 0.0


def test_camada1_hash_exato_normalizado() -> None:
    f = DedupFunnel(documentos_iniciais=[("ref1", BASE)])
    res = f.avaliar("Corrigir o BUG, no endpoint de checkout em producao!!")
    assert res.status == "rejected_hash" and not res.aceito


def test_camada2_similaridade_acima_do_threshold() -> None:
    f = DedupFunnel(sim_threshold=0.5, documentos_iniciais=[("ref1", BASE)])
    res = f.avaliar(BASE + " hoje")
    assert res.status == "rejected_similarity"
    assert res.nearest_ref == "ref1" and res.max_similarity >= 0.5


def test_texto_distinto_aceito() -> None:
    f = DedupFunnel(documentos_iniciais=[("ref1", BASE)])
    res = f.avaliar("planejar a migracao do banco de dados para a nova regiao")
    assert res.aceito and res.max_similarity < 0.85


def test_threshold_alto_so_rejeita_por_hash() -> None:
    f = DedupFunnel(sim_threshold=1.0, documentos_iniciais=[("ref1", BASE)])
    assert f.avaliar(BASE + " hoje").aceito


def test_threshold_override_por_chamada() -> None:
    f = DedupFunnel(sim_threshold=1.0, documentos_iniciais=[("ref1", BASE)])
    assert f.avaliar(BASE + " hoje", sim_threshold=0.5).status == "rejected_similarity"


def test_registrar_se_aceito_alimenta_corpus() -> None:
    f = DedupFunnel()
    assert f.avaliar(BASE, registrar_se_aceito=True, ref_se_aceito="r1").aceito
    assert f.avaliar(BASE).status == "rejected_hash"
    assert f.avaliar("planejar migracao de banco de dados regional").aceito
    assert f.avaliar("planejar migracao de banco de dados regional", registrar_se_aceito=False).aceito


def test_adicionar_documento_entra_no_corpus() -> None:
    f = DedupFunnel()
    f.adicionar_documento("r1", BASE)
    assert f.avaliar(BASE).status == "rejected_hash"


def test_golden_set_como_corpus_rejeita_seed_exata() -> None:
    seeds = carregar_seeds_golden()
    f = DedupFunnel(documentos_iniciais=[("golden:" + s.id, s.prompt) for s in seeds])
    res = f.avaliar(seeds[0].prompt)
    assert res.status == "rejected_hash"
    assert res.nearest_ref is not None and res.nearest_ref.startswith("golden:")


@pytest.mark.parametrize("limiar", [0.0001, 0.85, 1.0])
def test_limiares_de_fronteira_nao_quebram(limiar: float) -> None:
    f = DedupFunnel(sim_threshold=limiar, documentos_iniciais=[("r", BASE)])
    assert f.avaliar("assunto totalmente diferente sobre infraestrutura").status in {
        "accepted", "rejected_similarity"
    }


@pytest.mark.parametrize("invalido", [0.0, -0.1, 1.01])
def test_threshold_fora_do_intervalo_levanta(invalido: float) -> None:
    with pytest.raises(ValueError):
        DedupFunnel(sim_threshold=invalido)
