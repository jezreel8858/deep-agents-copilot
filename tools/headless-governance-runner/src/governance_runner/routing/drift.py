"""
drift — Detec\u00E7\u00E3o de deriva de inten\u00E7\u00E3o (R-042) como fun\u00E7\u00E3o pura.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md \u00A76.6): fun\u00E7\u00E3o pura, sem
embeddings e sem chamada a LLM/rede, que classifica o turno atual contra o
estado da sess\u00E3o e o cat\u00E1logo de agentes, retornando os motivos de deriva
detectados.

Decis\u00E3o de design (subtask 4 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md):
o l\u00E9xico (verbos de muta\u00E7\u00E3o, palavras-chave de stack, frases de bypass e
frases de continuidade) \u00E9 mantido como CONSTANTES PYTHON INLINE neste
m\u00F3dulo, e n\u00E3o em um ``lexicon.yaml`` externo. Justificativa pragm\u00E1tica:
    - O l\u00E9xico \u00E9 pequeno (dezenas de entradas) e j\u00E1 \u00E9 versionado via git
      no pr\u00F3prio c\u00F3digo-fonte — um YAML externo n\u00E3o traria ganho de
      manutenibilidade proporcional ao custo de I/O de parsing adicional
      (mesmo que s\u00EDncrono e local, n\u00E3o-rede) dentro de um m\u00F3dulo cujo
      contrato expl\u00EDcito \u00E9 ser 100% puro e sem efeitos colaterais.
    - Caso o l\u00E9xico cres\u00E7a (m\u00FAltiplos idiomas, dezenas de stacks), a
      extra\u00E7\u00E3o para ``routing/lexicon.yaml`` pode ser feita depois sem
      alterar a assinatura p\u00FAblica ``detectar_deriva(sessao, turno,
      catalogo) -> Deriva``.

Os 4 motivos de deriva detectados (R-042):
    1. ``verbo_execucao_agente_read_only`` — verbo de muta\u00E7\u00E3o/execu\u00E7\u00E3o
       dirigido a um agente read-only (auditor/reviewer/gatekeeper)
       durante um workflow em curso.
    2. ``stack_fora_de_competencia:<stack>`` — turno menciona stack
       tecnol\u00F3gica incompat\u00EDvel com o dom\u00EDnio do agente ativo.
    3. ``nova_solicitacao_pos_conclusao`` — novo pedido de a\u00E7\u00E3o ap\u00F3s a
       sess\u00E3o j\u00E1 ter atingido ``Fase.CONCLUIDO`` (R-052).
    4. ``bypass_agent_router`` — pedido de execu\u00E7\u00E3o direta contornando o
       agent-router (men\u00E7\u00E3o expl\u00EDcita a ``@agente`` do cat\u00E1logo ou frase
       lexical de bypass).

Frases de continuidade (refinamento IN-SCOPE da mesma solicita\u00E7\u00E3o, ex.:
"sim", "prossiga", "continue", "aprovado") nunca disparam, por si s\u00F3, os
motivos 1 e 3 (que dependem de verbo de a\u00E7\u00E3o) — ver ``_is_continuidade``.
Os motivos 2 e 4 permanecem sens\u00EDveis mesmo em turnos de continuidade,
pois representam sinais fortes e independentes de mudan\u00E7a de escopo.
"""

from __future__ import annotations

import re
import unicodedata

from governance_runner.routing.model import Catalogo, Deriva, Fase, Sessao, Turno

# ---------------------------------------------------------------------------
# L\u00E9xico versionado (inline — ver docstring do m\u00F3dulo).
# ---------------------------------------------------------------------------

_MUTATION_VERBS: frozenset[str] = frozenset(
    {
        "implementar", "implemente", "implementa",
        "corrigir", "corrija", "corrige",
        "aplicar", "aplique", "aplica",
        "executar", "execute", "executa",
        "criar", "crie", "cria",
        "deletar", "delete", "deleta",
        "apagar", "apague", "apaga",
        "commitar", "commit", "commite",
        "publicar", "publique", "publica",
        "mesclar", "merge",
        "sobrescrever", "sobrescreva",
        "refatorar", "refatore",
        "gerar", "gere",
        "rodar", "rode",
        "alterar", "altere",
        "modificar", "modifique",
        "adicionar", "adicione",
        "remover", "remova",
    }
)

_REQUEST_STARTERS: frozenset[str] = frozenset(
    {
        "quero", "preciso", "gostaria", "novo", "nova", "outro", "outra",
        "poderia fazer", "vamos fazer", "agora quero",
    }
)

_STACK_KEYWORDS: dict[str, tuple[str, ...]] = {
    "angular": ("angular",),
    "spring-boot": ("spring boot", "spring-boot", "springboot"),
    "spring-reactive": ("spring reactive", "webflux"),
    "ejb": ("ejb", "jakarta ee", "java ee"),
    "python": ("python", "fastapi", "django", "flask", "pydantic"),
    "struts": ("struts",),
    "database": ("oracle", "informix", "pl-sql", "plsql"),
    "kotlin": ("kotlin",),
}

_READ_ONLY_MARKERS: frozenset[str] = frozenset(
    {"auditor", "review", "reviewer", "gatekeeper", "audit"}
)

_BYPASS_PHRASES: frozenset[str] = frozenset(
    {
        "chame direto", "chama direto", "chamar direto",
        "sem passar pelo router", "sem passar pelo agent-router",
        "ignore o router", "ignora o router",
        "pula o router", "pule o router",
        "direto no agente", "bypass do router",
        "va direto para", "vai direto para",
    }
)

_CONTINUITY_PHRASES: frozenset[str] = frozenset(
    {
        "ok", "sim", "prossiga", "continue", "continuar",
        "aprovado", "pode seguir", "pode continuar",
        "pode prosseguir", "confirmo", "confirmado",
        "de acordo", "concordo", "isso mesmo", "exatamente", "correto",
    }
)

_ROUTER_AGENT_NAMES: frozenset[str] = frozenset({"agent-router", "router"})


# ---------------------------------------------------------------------------
# Helpers puros de normaliza\u00E7\u00E3o/classifica\u00E7\u00E3o l\u00E9xica.
# ---------------------------------------------------------------------------


def _normalizar(texto: str) -> str:
    """Normaliza texto para compara\u00E7\u00E3o l\u00E9xica: min\u00FAsculo, sem acentos, sem pontua\u00E7\u00E3o."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    minusculo = sem_acentos.lower()
    limpo = re.sub(r"[^a-z0-9@\-\s]", " ", minusculo)
    return re.sub(r"\s+", " ", limpo).strip()


def _contem_termo(texto_norm: str, termo: str) -> bool:
    """Checa presen\u00E7a de ``termo`` (palavra ou frase) com fronteira de palavra."""
    return re.search(rf"(?<![a-z0-9]){re.escape(termo)}(?![a-z0-9])", texto_norm) is not None


def _is_continuidade(texto_norm: str) -> bool:
    """True se o turno \u00E9 uma frase de continuidade (refinamento in-scope, R-042 TC-03)."""
    if texto_norm in _CONTINUITY_PHRASES:
        return True
    return any(texto_norm.startswith(f"{frase} ") for frase in _CONTINUITY_PHRASES)


def _tem_verbo_mutacao(texto_norm: str) -> bool:
    return any(_contem_termo(texto_norm, verbo) for verbo in _MUTATION_VERBS)


def _tem_marcador_nova_solicitacao(texto_norm: str) -> bool:
    return _tem_verbo_mutacao(texto_norm) or any(
        _contem_termo(texto_norm, marcador) for marcador in _REQUEST_STARTERS
    )


def _agente_e_read_only(agente_ativo: str) -> bool:
    agente_norm = _normalizar(agente_ativo)
    return any(marcador in agente_norm for marcador in _READ_ONLY_MARKERS)


def _stack_do_agente(agente_ativo: str) -> str | None:
    agente_norm = _normalizar(agente_ativo)
    for stack, palavras in _STACK_KEYWORDS.items():
        if any(_contem_termo(agente_norm, palavra) for palavra in palavras):
            return stack
    return None


def _stack_conflitante(texto_norm: str, stack_do_agente: str | None) -> str | None:
    for stack, palavras in _STACK_KEYWORDS.items():
        if stack == stack_do_agente:
            continue
        if any(_contem_termo(texto_norm, palavra) for palavra in palavras):
            return stack
    return None


def _tem_pedido_bypass(texto_norm: str, catalogo: Catalogo) -> bool:
    if any(frase in texto_norm for frase in _BYPASS_PHRASES):
        return True
    agentes_conhecidos = {_normalizar(agente) for agente in catalogo.agentes}
    for mencao in re.findall(r"@([a-z0-9\-]+)", texto_norm):
        if mencao in _ROUTER_AGENT_NAMES:
            continue
        if mencao in agentes_conhecidos:
            return True
    return False


# ---------------------------------------------------------------------------
# API p\u00FAblica.
# ---------------------------------------------------------------------------


def detectar_deriva(sessao: Sessao, turno: Turno, catalogo: Catalogo) -> Deriva:
    """Detecta deriva de inten\u00E7\u00E3o (R-042) comparando o turno atual ao estado da sess\u00E3o.

    Fun\u00E7\u00E3o pura: nenhuma chamada de rede, LLM ou embeddings — apenas
    checagens l\u00E9xicas determin\u00EDsticas sobre ``turno.texto``, ``sessao`` e
    ``catalogo``.

    Args:
        sessao: Estado imut\u00E1vel atual da sess\u00E3o de governan\u00E7a.
        turno: Turno de conversa (texto bruto) a ser classificado.
        catalogo: Vista tipada de ``catalog.yaml`` com agentes conhecidos.

    Returns:
        Deriva: ``houve=True`` e a tupla de motivos quando pelo menos um dos
        4 gatilhos de deriva (verbo de execu\u00E7\u00E3o em agente read-only, stack
        fora de compet\u00EAncia, nova solicita\u00E7\u00E3o p\u00F3s-conclus\u00E3o, bypass do
        agent-router) for detectado; ``houve=False`` com motivos vazios
        caso contr\u00E1rio.
    """
    texto_norm = _normalizar(turno.texto)
    is_continuidade = _is_continuidade(texto_norm)
    motivos: list[str] = []

    # Motivo 1: verbo de execu\u00E7\u00E3o/muta\u00E7\u00E3o dirigido a agente read-only em workflow.
    if (
        not is_continuidade
        and sessao.fase == Fase.EM_WORKFLOW
        and _agente_e_read_only(sessao.agente_ativo)
        and _tem_verbo_mutacao(texto_norm)
    ):
        motivos.append("verbo_execucao_agente_read_only")

    # Motivo 2: stack fora de compet\u00EAncia do agente ativo.
    stack_agente = _stack_do_agente(sessao.agente_ativo)
    stack_conflito = _stack_conflitante(texto_norm, stack_agente) if stack_agente else None
    if stack_conflito is not None:
        motivos.append(f"stack_fora_de_competencia:{stack_conflito}")

    # Motivo 3: nova solicita\u00E7\u00E3o de a\u00E7\u00E3o ap\u00F3s conclus\u00E3o de workflow (R-052).
    if (
        not is_continuidade
        and sessao.fase == Fase.CONCLUIDO
        and _tem_marcador_nova_solicitacao(texto_norm)
    ):
        motivos.append("nova_solicitacao_pos_conclusao")

    # Motivo 4: pedido de execu\u00E7\u00E3o direta contornando o agent-router.
    if _tem_pedido_bypass(texto_norm, catalogo):
        motivos.append("bypass_agent_router")

    return Deriva(houve=bool(motivos), motivos=tuple(motivos))
