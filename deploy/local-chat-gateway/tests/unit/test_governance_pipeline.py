"""Testes unitarios puros de `governance_pipeline` (T3/PR-3).

Sem FastAPI, sem SDK -- apenas composicao sobre `governance.py`, validada
via mocks de `governance.rotear`/`governance.transicionar`/
`governance.detectar_deriva` (CA-01: nenhuma logica de roteamento propria
e reimplementada neste modulo).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from governance_runner.routing.model import EtapaSpec, NivelRouting

from local_chat_gateway import governance_pipeline
from local_chat_gateway.governance import (
    DecisaoRota,
    Deriva,
    Evento,
    Fase,
    Sessao,
    TransicaoInvalidaError,
    Workflow,
)
from local_chat_gateway.governance_pipeline import (
    _AGENTE_FALLBACK_AMBIGUO,
    _WORKFLOW_FALLBACK_AMBIGUO,
)


def _sessao(
    *,
    fase: Fase = Fase.EM_WORKFLOW,
    workflow: Workflow | None = Workflow.FEATURE_DEVELOPMENT,
    etapa: int = 1,
    agente_ativo: str = "python-feature-developer",
) -> Sessao:
    return Sessao(fase=fase, workflow=workflow, etapa=etapa, agente_ativo=agente_ativo)


# ---------------------------------------------------------------------------
# preparar_turno
# ---------------------------------------------------------------------------


def test_preparar_turno_chama_rotear_quando_sessao_sem_workflow() -> None:
    # Arrange
    sessao = _sessao(fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router")
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(name="tabela", catalogo=MagicMock(name="catalogo"))
    decisao_rota = DecisaoRota(
        escolhido="python-feature-developer",
        workflow=Workflow.FEATURE_DEVELOPMENT,
        nivel=NivelRouting.RULE_BASED,
        score=0.95,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ) as mock_rotear,
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva"
        ) as mock_detectar_deriva,
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(sessao, "implemente X", grafo, tabela)

    # Assert
    mock_rotear.assert_called_once_with("implemente X", grafo)
    mock_detectar_deriva.assert_not_called()
    assert resultado.roteou_novamente is True
    assert resultado.workflow is Workflow.FEATURE_DEVELOPMENT
    assert resultado.agente_escolhido == "python-feature-developer"


def test_preparar_turno_saudacao_permanece_no_router_sem_workflow() -> None:
    """Saudacao ou pergunta geral ao router ("oi", "oi, o que vc faz?") NAO deve
    iniciar workflow prematuramente -- permanece no agent-router em Fase.ROUTER
    aguardando a demanda real do usuario.
    """
    # Arrange
    sessao = _sessao(fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router")
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(name="tabela", catalogo=MagicMock(name="catalogo"))

    with (
        patch("local_chat_gateway.governance_pipeline.governance.rotear") as mock_rotear,
        patch("local_chat_gateway.governance_pipeline.governance.detectar_deriva") as mock_deriva,
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(sessao, "oi, o que vc faz?", grafo, tabela)

    # Assert
    mock_rotear.assert_not_called()
    mock_deriva.assert_not_called()
    assert resultado.workflow is None
    assert resultado.agente_escolhido == "agent-router"
    assert resultado.agente_exibido == "agent-router"
    assert resultado.roteou_novamente is False
    assert resultado.handoff_origem is None


def test_preparar_turno_out_of_domain_no_turno_inicial_permanece_no_router() -> None:
    """Bug real de producao (2026-10-02): mensagem ambigua/meta ao proprio
    router no turno INICIAL (ex.: "qual a sua funcao?") classificada
    `OUT_OF_DOMAIN` (nenhuma keyword tecnica casa) NAO deve mais ser forcada
    para um especialista fixo (`prompt-structuring`) -- deve permanecer no
    `agent-router`, deixando o MODELO REAL (persona + tool `run_subagent` +
    custom_agents, RT-04) decidir se/para onde delegar, exatamente como no
    plugin Copilot da IDE (ver pesquisa Tavily citada em
    `_resolver_decisao_rota`).
    """
    # Arrange
    sessao = _sessao(fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router")
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(
        name="tabela",
        catalogo=MagicMock(name="catalogo"),
        etapas={
            (_WORKFLOW_FALLBACK_AMBIGUO, 1): EtapaSpec(
                agent_permitidos=frozenset({"requirements-analyst", _AGENTE_FALLBACK_AMBIGUO})
            )
        },
    )
    decisao_rota = DecisaoRota(
        escolhido="tech-solution-architect",
        workflow=Workflow.TECHNICAL_ANALYSIS,
        nivel=NivelRouting.OUT_OF_DOMAIN,
        score=0.0,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ) as mock_rotear,
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva"
        ) as mock_detectar_deriva,
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(sessao, "qual a sua funcao?", grafo, tabela)

    # Assert
    mock_rotear.assert_called_once_with("qual a sua funcao?", grafo)
    mock_detectar_deriva.assert_not_called()
    assert resultado.roteou_novamente is False
    assert resultado.workflow is None
    assert resultado.agente_escolhido == "agent-router"
    assert resultado.agente_exibido == "agent-router"
    assert resultado.nivel == "out_of_domain"
    assert resultado.handoff_origem is None
    assert resultado.handoff_motivo is None


def test_preparar_turno_out_of_domain_mid_workflow_preserva_fallback_prompt_structuring() -> None:
    """Fallback histórico (`prompt-structuring`) preservado APENAS quando a
    origem NÃO é o `agent-router` (drift detectado a partir de um
    especialista já ativo, sem reclassificação confiável) -- retornar ao
    `agent-router` nesse ponto exigiria modelar uma transição de "abort"
    ainda não coberta pela máquina de estados R-050 (fora de escopo desta
    correção cirúrgica).
    """
    # Arrange
    sessao = _sessao(
        fase=Fase.EM_WORKFLOW,
        workflow=Workflow.FEATURE_DEVELOPMENT,
        etapa=2,
        agente_ativo="python-feature-developer",
    )
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(
        name="tabela",
        catalogo=MagicMock(name="catalogo"),
        etapas={
            (_WORKFLOW_FALLBACK_AMBIGUO, 1): EtapaSpec(
                agent_permitidos=frozenset({"requirements-analyst", _AGENTE_FALLBACK_AMBIGUO})
            )
        },
    )
    decisao_rota = DecisaoRota(
        escolhido="tech-solution-architect",
        workflow=Workflow.TECHNICAL_ANALYSIS,
        nivel=NivelRouting.OUT_OF_DOMAIN,
        score=0.0,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ),
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva",
            return_value=Deriva(houve=True, motivos=("mudanca_verbo_acao",)),
        ),
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(sessao, "faca uma analise ampla", grafo, tabela)

    # Assert
    assert resultado.roteou_novamente is True
    assert resultado.workflow is _WORKFLOW_FALLBACK_AMBIGUO
    assert resultado.agente_escolhido == _AGENTE_FALLBACK_AMBIGUO
    assert resultado.nivel == "out_of_domain"
    assert resultado.handoff_origem == "python-feature-developer"
    assert resultado.handoff_motivo is not None


def test_preparar_turno_out_of_domain_preserva_fallback_antigo_quando_grafo_nao_modela_prompt_synthesis() -> None:
    """Defensivo: se a `TabelaTransicao` compilada NAO declarar
    `WORKFLOW-PROMPT-SYNTHESIS`/`prompt-structuring` (ex.: fixtures reduzidas
    de teste como `tests/fixtures/valid_graph.yaml`, que modelam apenas um
    subconjunto dos 9 workflows canônicos), o override de ambiguidade é
    pulado -- `decisao_rota.escolhido`/`.workflow` originais (resolvidos por
    `_escolher_fallback`) são preservados, evitando `TransicaoInvalidaError`
    contra um workflow inexistente naquele grafo. Cenário mid-workflow
    (origem != agent-router), unico caminho onde o override ainda se aplica.
    """
    # Arrange
    sessao = _sessao(
        fase=Fase.EM_WORKFLOW,
        workflow=Workflow.FEATURE_DEVELOPMENT,
        etapa=2,
        agente_ativo="python-feature-developer",
    )
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(name="tabela", catalogo=MagicMock(name="catalogo"), etapas={})
    decisao_rota = DecisaoRota(
        escolhido="deep-search",
        workflow=Workflow.TECHNICAL_ANALYSIS,
        nivel=NivelRouting.OUT_OF_DOMAIN,
        score=0.0,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ),
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva",
            return_value=Deriva(houve=True, motivos=("mudanca_verbo_acao",)),
        ),
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(sessao, "faca uma analise ampla", grafo, tabela)

    # Assert
    assert resultado.workflow is Workflow.TECHNICAL_ANALYSIS
    assert resultado.agente_escolhido == "deep-search"



def test_preparar_turno_nao_rerroteia_quando_sem_drift() -> None:
    # Arrange
    sessao = _sessao()
    grafo = MagicMock(name="grafo")
    catalogo = MagicMock(name="catalogo")
    tabela = MagicMock(name="tabela", catalogo=catalogo)

    with (
        patch("local_chat_gateway.governance_pipeline.governance.rotear") as mock_rotear,
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva",
            return_value=Deriva(houve=False),
        ) as mock_detectar_deriva,
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(
            sessao, "continue", grafo, tabela
        )

    # Assert
    mock_rotear.assert_not_called()
    mock_detectar_deriva.assert_called_once()
    args, _ = mock_detectar_deriva.call_args
    assert args[0] == sessao
    assert args[1].texto == "continue"
    assert args[2] is catalogo
    assert resultado.roteou_novamente is False
    assert resultado.workflow == sessao.workflow
    assert resultado.agente_escolhido == sessao.agente_ativo


def test_preparar_turno_rerroteia_quando_drift_detectado() -> None:
    # Arrange
    sessao = _sessao()
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(name="tabela", catalogo=MagicMock(name="catalogo"))
    decisao_rota = DecisaoRota(
        escolhido="security-reviewer",
        workflow=Workflow.TECHNICAL_ANALYSIS,
        nivel=NivelRouting.SEMANTIC,
        score=0.8,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ) as mock_rotear,
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva",
            return_value=Deriva(houve=True, motivos=("mudanca_verbo_acao",)),
        ),
    ):
        # Act
        resultado = governance_pipeline.preparar_turno(
            sessao, "agora implemente a correcao", grafo, tabela
        )

    # Assert
    mock_rotear.assert_called_once_with("agora implemente a correcao", grafo)
    assert resultado.roteou_novamente is True
    assert resultado.workflow is Workflow.TECHNICAL_ANALYSIS
    assert resultado.agente_escolhido == "security-reviewer"


# ---------------------------------------------------------------------------
# avaliar_transicao
# ---------------------------------------------------------------------------


def test_avaliar_transicao_retorna_sucesso_com_sessao_atualizada() -> None:
    # Arrange
    sessao = _sessao()
    evento = MagicMock(name="evento", spec=Evento)
    tabela = MagicMock(name="tabela")
    nova_sessao = _sessao(etapa=2)

    with patch(
        "local_chat_gateway.governance_pipeline.governance.transicionar",
        return_value=nova_sessao,
    ) as mock_transicionar:
        # Act
        resultado = governance_pipeline.avaliar_transicao(sessao, evento, tabela)

    # Assert
    mock_transicionar.assert_called_once_with(sessao, evento, tabela)
    assert resultado.sucesso is True
    assert resultado.sessao_atualizada == nova_sessao
    assert resultado.erro is None


def test_avaliar_transicao_captura_transicao_invalida_sem_propagar() -> None:
    # Arrange
    sessao = _sessao()
    evento = MagicMock(name="evento", spec=Evento)
    tabela = MagicMock(name="tabela")

    with patch(
        "local_chat_gateway.governance_pipeline.governance.transicionar",
        side_effect=TransicaoInvalidaError("R-050: transicao nao permitida"),
    ):
        # Act
        resultado = governance_pipeline.avaliar_transicao(sessao, evento, tabela)

    # Assert
    assert resultado.sucesso is False
    assert resultado.sessao_atualizada is None
    assert resultado.erro == "R-050: transicao nao permitida"


# ---------------------------------------------------------------------------
# montar_contexto
# ---------------------------------------------------------------------------


def _leitor_fake(conteudos: dict[str, str]) -> Callable[[Path], str]:
    def _leitor(caminho: Path) -> str:
        chave = caminho.name
        if chave not in conteudos:
            raise FileNotFoundError(str(caminho))
        return conteudos[chave]

    return _leitor


def test_montar_contexto_inclui_banner_e_persona() -> None:
    # Arrange
    leitor = _leitor_fake(
        {
            "python-feature-developer.agent.md": "PERSONA-CONTEUDO",
            "copilot-instructions.md": "NUCLEO-CONTEUDO",
        }
    )

    # Act
    resultado = governance_pipeline.montar_contexto(
        "python-feature-developer",
        Workflow.FEATURE_DEVELOPMENT,
        3,
        leitor_arquivo=leitor,
    )

    # Assert
    banner_esperado = (
        "Agente Ativo: python-feature-developer\n"
        "[WORKFLOW: WORKFLOW-FEATURE-DEVELOPMENT / ETAPA: 3]\n\n"
    )
    assert resultado.startswith(banner_esperado)
    assert "PERSONA-CONTEUDO" in resultado
    assert "NUCLEO-CONTEUDO" in resultado


def test_montar_contexto_trunca_em_32kb_preservando_banner() -> None:
    # Arrange
    persona_gigante = "X" * (40 * 1024)
    leitor = _leitor_fake(
        {
            "python-feature-developer.agent.md": persona_gigante,
            "copilot-instructions.md": "NUCLEO-CONTEUDO",
        }
    )

    # Act
    resultado = governance_pipeline.montar_contexto(
        "python-feature-developer",
        Workflow.FEATURE_DEVELOPMENT,
        1,
        leitor_arquivo=leitor,
    )

    # Assert
    assert len(resultado.encode("utf-8")) <= 32 * 1024
    assert resultado.startswith("Agente Ativo: python-feature-developer")
    assert "[... truncado por orcamento de contexto ...]" in resultado


def test_montar_contexto_nunca_chama_leitor_para_caminho_com_hooks() -> None:
    # Arrange: agente malicioso tenta path traversal para dentro de hooks/.
    agente_malicioso = "../hooks/malicious"
    spy = MagicMock(side_effect=FileNotFoundError("nao deveria ser chamado"))
    # Permite leitura legitima do nucleo para nao poluir o teste de foco.
    leitor = _leitor_fake({"copilot-instructions.md": "NUCLEO-CONTEUDO"})

    def leitor_espiao(caminho: Path) -> str:
        spy(caminho)
        return leitor(caminho)

    # Act
    governance_pipeline.montar_contexto(
        agente_malicioso, Workflow.FEATURE_DEVELOPMENT, 1, leitor_arquivo=leitor_espiao
    )

    # Assert: nenhuma chamada ao leitor injetavel contem "hooks" no caminho.
    assert spy.call_args_list, "leitor deveria ter sido chamado ao menos para o nucleo"
    for chamada in spy.call_args_list:
        caminho_chamado = str(chamada.args[0])
        assert "hooks" not in caminho_chamado


# ---------------------------------------------------------------------------
# Bug real de producao (2026-10-01, Addendum 5): `_RAIZ_REPOSITORIO = Path(
# __file__).resolve().parents[4]` calculava a raiz do repositorio relativa ao
# LOCAL DE INSTALACAO do arquivo-fonte -- funciona em dev local (instalacao
# editavel, `__file__` aponta para o repositorio real), mas dentro do
# container Docker o pacote e instalado via `pip install` em site-packages
# (`/usr/local/lib/python3.12/site-packages/local_chat_gateway/
# governance_pipeline.py`), fazendo `parents[4]` resolver para `/usr/local`
# em vez do volume real `/governance:ro`. Resultado real observado nos logs
# de producao: "montar_contexto: artefato nao encontrado: /usr/local/
# .github/agents/<agente>.agent.md" -- o `system_message` injetado no SDK
# ficava permanentemente vazio de persona/nucleo (apenas o banner). Corrigido
# tornando o diretorio base explicitamente configuravel via parametro
# `github_dir` (propagado de `settings.governance_github_dir` em
# `routes.py`), com o calculo antigo preservado apenas como fallback de
# ultimo recurso quando nenhum override e fornecido.
# ---------------------------------------------------------------------------


def test_montar_contexto_usa_github_dir_explicito_quando_fornecido(
    tmp_path: Path,
) -> None:
    """Quando `github_dir` e passado explicitamente, `montar_contexto` monta
    os caminhos de persona/nucleo relativos a ELE -- nunca ao local de
    instalacao do pacote (`_RAIZ_REPOSITORIO` calculado de `__file__`)."""
    github_dir_real = tmp_path / ".github"
    (github_dir_real / "agents").mkdir(parents=True)
    (github_dir_real / "agents" / "bug-triage.agent.md").write_text(
        "PERSONA-REAL", encoding="utf-8"
    )
    (github_dir_real / "copilot-instructions.md").write_text(
        "NUCLEO-REAL", encoding="utf-8"
    )

    resultado = governance_pipeline.montar_contexto(
        "bug-triage",
        Workflow.BUG_FIX,
        1,
        github_dir=github_dir_real,
    )

    assert "PERSONA-REAL" in resultado
    assert "NUCLEO-REAL" in resultado


def test_montar_contexto_allowlist_respeita_github_dir_customizado(
    tmp_path: Path,
) -> None:
    """A guarda RK-03 (bloqueio de `hooks/`) continua valida mesmo com
    `github_dir` customizado -- a allowlist e sempre relativa ao
    `github_dir` efetivamente usado, nunca ao default hard-coded."""
    github_dir_real = tmp_path / ".github"
    github_dir_real.mkdir(parents=True)
    spy = MagicMock(return_value="NAO-DEVERIA-IMPORTAR")

    governance_pipeline.montar_contexto(
        "../hooks/malicious",
        Workflow.BUG_FIX,
        1,
        leitor_arquivo=spy,
        github_dir=github_dir_real,
    )

    for chamada in spy.call_args_list:
        assert "hooks" not in str(chamada.args[0])


# ---------------------------------------------------------------------------
# T7/PR-7 — telemetria: nivel/score/drift_detectado (DecisaoTurno) e
# erro_tipo (ResultadoTransicao), consumidos pelos novos spans customizados
# `governance.route`/`governance.workflow_transition` (telemetry.py).
# ---------------------------------------------------------------------------


def test_preparar_turno_expoe_nivel_score_quando_sessao_sem_workflow() -> None:
    sessao = _sessao(
        fase=Fase.ROUTER, workflow=None, etapa=0, agente_ativo="agent-router"
    )
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(name="tabela", catalogo=MagicMock(name="catalogo"))
    decisao_rota = DecisaoRota(
        escolhido="python-feature-developer",
        workflow=Workflow.FEATURE_DEVELOPMENT,
        nivel=NivelRouting.RULE_BASED,
        score=0.95,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ),
        patch("local_chat_gateway.governance_pipeline.governance.detectar_deriva"),
    ):
        resultado = governance_pipeline.preparar_turno(
            sessao, "implemente X", grafo, tabela
        )

    assert resultado.nivel == "rule_based"
    assert resultado.score == 0.95
    assert resultado.drift_detectado is False


def test_preparar_turno_marca_drift_detectado_quando_deriva_houve() -> None:
    sessao = _sessao()
    grafo = MagicMock(name="grafo")
    tabela = MagicMock(name="tabela", catalogo=MagicMock(name="catalogo"))
    decisao_rota = DecisaoRota(
        escolhido="security-reviewer",
        workflow=Workflow.TECHNICAL_ANALYSIS,
        nivel=NivelRouting.SEMANTIC,
        score=0.8,
    )

    with (
        patch(
            "local_chat_gateway.governance_pipeline.governance.rotear",
            return_value=decisao_rota,
        ),
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva",
            return_value=Deriva(houve=True, motivos=("mudanca_verbo_acao",)),
        ),
    ):
        resultado = governance_pipeline.preparar_turno(
            sessao, "agora implemente a correcao", grafo, tabela
        )

    assert resultado.nivel == "semantic"
    assert resultado.score == 0.8
    assert resultado.drift_detectado is True


def test_preparar_turno_nivel_score_none_quando_reaproveita_workflow() -> None:
    sessao = _sessao()
    grafo = MagicMock(name="grafo")
    catalogo = MagicMock(name="catalogo")
    tabela = MagicMock(name="tabela", catalogo=catalogo)

    with (
        patch("local_chat_gateway.governance_pipeline.governance.rotear"),
        patch(
            "local_chat_gateway.governance_pipeline.governance.detectar_deriva",
            return_value=Deriva(houve=False),
        ),
    ):
        resultado = governance_pipeline.preparar_turno(
            sessao, "continue", grafo, tabela
        )

    assert resultado.nivel is None
    assert resultado.score is None
    assert resultado.drift_detectado is False


def test_avaliar_transicao_sucesso_tem_erro_tipo_none() -> None:
    sessao = _sessao()
    evento = MagicMock(name="evento", spec=Evento)
    tabela = MagicMock(name="tabela")
    nova_sessao = _sessao(etapa=2)

    with patch(
        "local_chat_gateway.governance_pipeline.governance.transicionar",
        return_value=nova_sessao,
    ):
        resultado = governance_pipeline.avaliar_transicao(sessao, evento, tabela)

    assert resultado.erro_tipo is None


def test_avaliar_transicao_falha_expoe_erro_tipo_da_excecao() -> None:
    sessao = _sessao()
    evento = MagicMock(name="evento", spec=Evento)
    tabela = MagicMock(name="tabela")

    with patch(
        "local_chat_gateway.governance_pipeline.governance.transicionar",
        side_effect=TransicaoInvalidaError("R-050: transicao nao permitida"),
    ):
        resultado = governance_pipeline.avaliar_transicao(sessao, evento, tabela)

    assert resultado.erro_tipo == "TransicaoInvalidaError"
