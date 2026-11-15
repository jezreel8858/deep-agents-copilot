"""
dedup — Funil de deduplicacao em 2 camadas (L1 SHA-256 + L2 TF-IDF cosseno) em stdlib pura (B1-05).
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from dataclasses import dataclass
from typing import Literal, Sequence

from governance_runner.synth.normalize import normalizar

__all__ = [
    "DEFAULT_SIM_THRESHOLD",
    "StatusDedup",
    "DocumentoCorpus",
    "ResultadoDedup",
    "calcular_sha256_normalizado",
    "extrair_ngrams",
    "DedupFunnel",
]

DEFAULT_SIM_THRESHOLD = 0.85
StatusDedup = Literal["accepted", "rejected_hash", "rejected_similarity"]


@dataclass(frozen=True)
class DocumentoCorpus:
    """Documento de referencia no corpus de deduplicacao (Golden ou SQLite)."""

    ref: str
    text: str
    text_norm: str
    sha256: str


@dataclass(frozen=True)
class ResultadoDedup:
    """Resultado da avaliacao de um candidato pelo funil L1/L2."""

    status: StatusDedup
    sha256: str
    text_norm: str
    max_similarity: float
    nearest_ref: str | None

    @property
    def aceito(self) -> bool:
        return self.status == "accepted"


def calcular_sha256_normalizado(texto_ou_norm: str, *, ja_normalizado: bool = False) -> str:
    """Calcula o SHA-256 hexadecimal sobre o texto normalizado canonico."""
    norm = texto_ou_norm if ja_normalizado else normalizar(texto_ou_norm)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def extrair_ngrams(text_norm: str) -> Counter[str]:
    """Extrai word 1-2-gramas e char 3-5-gramas (com bordas) do texto normalizado."""
    contagem: Counter[str] = Counter()
    if not text_norm:
        return contagem

    tokens = text_norm.split()
    for tok in tokens:
        contagem[f"w1:{tok}"] += 1
    for i in range(len(tokens) - 1):
        contagem[f"w2:{tokens[i]}_{tokens[i + 1]}"] += 1

    com_bordas = f"^{text_norm}$"
    tamanho = len(com_bordas)
    for n in (3, 4, 5):
        if tamanho < n:
            continue
        for i in range(tamanho - n + 1):
            contagem[f"c{n}:{com_bordas[i : i + n]}"] += 1

    return contagem


class DedupFunnel:
    """Funil de deduplicacao em 2 camadas (L1 SHA-256 + L2 TF-IDF cosseno com indice invertido)."""

    def __init__(
        self,
        *,
        sim_threshold: float = DEFAULT_SIM_THRESHOLD,
        documentos_iniciais: Sequence[tuple[str, str]] | None = None,
    ) -> None:
        if not (0.0 < sim_threshold <= 1.0):
            raise ValueError(f"sim_threshold deve estar em (0.0, 1.0]; recebido: {sim_threshold}")
        self._sim_threshold = float(sim_threshold)
        self._docs: list[DocumentoCorpus] = []
        self._doc_term_counts: list[Counter[str]] = []
        self._hash_to_ref: dict[str, str] = {}
        self._df: Counter[str] = Counter()
        self._inverted_index: dict[str, list[int]] = {}
        self._vetores_normalizados: list[dict[str, float]] = []
        self._dirty = False

        if documentos_iniciais:
            for ref, texto in documentos_iniciais:
                self.adicionar_documento(ref, texto)

    @property
    def sim_threshold(self) -> float:
        return self._sim_threshold

    @property
    def tamanho_corpus(self) -> int:
        return len(self._docs)

    def adicionar_documento(
        self,
        ref: str,
        texto: str,
        *,
        text_norm: str | None = None,
        sha256: str | None = None,
    ) -> None:
        norm = text_norm if text_norm is not None else normalizar(texto)
        digest = sha256 if sha256 is not None else calcular_sha256_normalizado(norm, ja_normalizado=True)
        if digest not in self._hash_to_ref:
            self._hash_to_ref[digest] = ref

        termos = extrair_ngrams(norm)
        doc_idx = len(self._docs)
        self._docs.append(DocumentoCorpus(ref=ref, text=texto, text_norm=norm, sha256=digest))
        self._doc_term_counts.append(termos)
        for termo in termos:
            self._df[termo] += 1
            self._inverted_index.setdefault(termo, []).append(doc_idx)
        self._dirty = True

    def _recomputar_vetores_se_necessario(self) -> None:
        if not self._dirty:
            return
        n_docs = len(self._docs)
        self._vetores_normalizados = []
        for termos in self._doc_term_counts:
            self._vetores_normalizados.append(self._vetorizar_normalizado(termos, n_docs))
        self._dirty = False

    def _vetorizar_normalizado(self, termos: Counter[str], n_docs: int) -> dict[str, float]:
        if not termos:
            return {}
        pesos: dict[str, float] = {}
        soma_quadrados = 0.0
        for termo, cnt in termos.items():
            if cnt <= 0:
                continue
            tf = 1.0 + math.log(cnt)
            df = self._df.get(termo, 0)
            idf = math.log((1.0 + n_docs) / (1.0 + df)) + 1.0
            w = tf * idf
            pesos[termo] = w
            soma_quadrados += w * w

        if soma_quadrados <= 0.0:
            return {}
        norma = math.sqrt(soma_quadrados)
        return {termo: peso / norma for termo, peso in pesos.items()}

    def avaliar(
        self,
        texto: str,
        *,
        registrar_se_aceito: bool = False,
        ref_se_aceito: str | None = None,
        sim_threshold: float | None = None,
    ) -> ResultadoDedup:
        limiar = float(sim_threshold) if sim_threshold is not None else self._sim_threshold
        norm = normalizar(texto)
        digest = calcular_sha256_normalizado(norm, ja_normalizado=True)

        if digest in self._hash_to_ref:
            return ResultadoDedup(
                status="rejected_hash",
                sha256=digest,
                text_norm=norm,
                max_similarity=1.0,
                nearest_ref=self._hash_to_ref[digest],
            )

        if not self._docs:
            if registrar_se_aceito:
                self.adicionar_documento(ref_se_aceito or f"synth:{digest[:12]}", texto, text_norm=norm, sha256=digest)
            return ResultadoDedup(
                status="accepted",
                sha256=digest,
                text_norm=norm,
                max_similarity=0.0,
                nearest_ref=None,
            )

        self._recomputar_vetores_se_necessario()
        termos_cand = extrair_ngrams(norm)
        vetor_cand = self._vetorizar_normalizado(termos_cand, len(self._docs))

        scores_por_doc: dict[int, float] = {}
        for termo, peso_q in vetor_cand.items():
            postings = self._inverted_index.get(termo)
            if not postings:
                continue
            for doc_idx in postings:
                peso_d = self._vetores_normalizados[doc_idx].get(termo, 0.0)
                if peso_d > 0.0:
                    scores_por_doc[doc_idx] = scores_por_doc.get(doc_idx, 0.0) + (peso_q * peso_d)

        max_sim = 0.0
        nearest: str | None = None
        for doc_idx, score in scores_por_doc.items():
            score_clamped = max(0.0, min(1.0, score))
            ref_doc = self._docs[doc_idx].ref
            if round(score_clamped, 12) > round(max_sim, 12) or (
                round(score_clamped, 12) == round(max_sim, 12) and (nearest is None or ref_doc < nearest)
            ):
                max_sim = score_clamped
                nearest = ref_doc

        if max_sim >= limiar:
            return ResultadoDedup(
                status="rejected_similarity",
                sha256=digest,
                text_norm=norm,
                max_similarity=round(max_sim, 6),
                nearest_ref=nearest,
            )

        if registrar_se_aceito:
            self.adicionar_documento(ref_se_aceito or f"synth:{digest[:12]}", texto, text_norm=norm, sha256=digest)

        return ResultadoDedup(
            status="accepted",
            sha256=digest,
            text_norm=norm,
            max_similarity=round(max_sim, 6),
            nearest_ref=nearest,
        )
