"""TC-03: Disparo de deriva de intenção (R-042).

Cobre os 4 motivos canônicos de deriva de intenção e os cenários de continuidade
in-scope que NÃO devem ser classificados como deriva:
    1. Verbo de execução em agente read-only (ex.: agent-auditor, security-reviewer).
    2. Stack fora de competência do agente ativo.
    3. Nova solicitação após conclusão de workflow (Fase.CONCLUIDO, R-052).
    4. Bypass explícito do agent-router (menção a outro especialista ou comando).
Inclui guard de pureza estrutural (zero import de rede/LLM).
Subtask 10 do PLANO_DECOMPOSICAO_COPILOT_SDK_HEADLESS_RUNNER.md.
"""

from __future__ import annotations

import ast
import inspect

import pytest

from governance_runner.routing import drift
from governance_runner.routing.drift import detectar_deriva
from governance_runner.routing.model import Catalogo, Fase, Sessao, Turno, Workflow

_MODULOS_PROIBIDOS = frozenset(
    {
        "requests", "httpx", "urllib", "urllib.request", "socket",
        "openai", "anthropic", "aiohttp", "grpc", "boto3",
        "sentence_transformers", "torch", "tensorflow", "numpy",
    }
)

_CATALOGO = Catalogo(
    agentes=frozenset(
        {
            "agent-router", "agent-auditor", "security-reviewer",
            "python-feature-developer", "angular-feature-developer",
            "spring-boot-feature-developer", "code-review", "pr-gatekeeper",
        }
    )
)


def _sessao(
    fase: Fase = Fase.EM_WORKFLOW,
    workflow: Workflow | None = Workflow.FEATURE_DEVELOPMENT,
    etapa: int = 1,
    agente_ativo: str = "python-feature-developer",
) -> Sessao:
    return Sessao(
        fase=fase,
        workflow=workflow,
        etapa=etapa,
        agente_ativo=agente_ativo,
    )


class TestTC03IntentDriftTrigger:
    """Testes do caso canônico TC-03: detecção de deriva de intenção (R-042)."""

    def test_deve_disparar_deriva_motivo1_quando_verbo_execucao_em_agente_read_only(self) -> None:
        """Agente read-only recebendo comando imperativo de alteração dispara deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="security-reviewer")
        turno = Turno(texto="Implemente a correção agora mesmo, sem esperar aprovação.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is True
        assert "verbo_execucao_agente_read_only" in resultado.motivos

    def test_deve_disparar_deriva_motivo1_quando_agent_auditor_receber_pedido_de_criacao(self) -> None:
        """agent-auditor é estritamente read-only; criar arquivo gera deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="agent-auditor")
        turno = Turno(texto="Crie o arquivo de configuração corrigido e aplique o patch.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is True
        assert "verbo_execucao_agente_read_only" in resultado.motivos

    def test_deve_disparar_deriva_motivo2_quando_stack_fora_de_competencia(self) -> None:
        """Agente especializado em Python recebendo pedido para Angular/Spring Boot gera deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="python-feature-developer")
        turno = Turno(texto="Na verdade, migre esse componente para Angular com Spring Boot.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is True
        assert any(m.startswith("stack_fora_de_competencia:") for m in resultado.motivos)

    def test_nao_deve_disparar_deriva_motivo2_quando_mesma_stack_do_agente(self) -> None:
        """Instruções que mencionam a stack de competência do agente ativo não geram deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="python-feature-developer")
        turno = Turno(texto="Ajuste o schema Pydantic e o repositório SQLAlchemy em Python.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert not any(m.startswith("stack_fora_de_competencia:") for m in resultado.motivos)

    def test_deve_disparar_deriva_motivo3_quando_nova_solicitacao_pos_conclusao(self) -> None:
        """Quando a sessão já está concluída, uma nova demanda substantiva gera deriva (R-052)."""
        # Arrange
        sessao = _sessao(fase=Fase.CONCLUIDO, workflow=None, etapa=0)
        turno = Turno(texto="Quero implementar agora uma nova funcionalidade de exportação CSV.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is True
        assert "nova_solicitacao_pos_conclusao" in resultado.motivos

    def test_nao_deve_disparar_deriva_motivo3_quando_confirmacao_simples_pos_conclusao(self) -> None:
        """Tokens de confirmação/agradecimento ('ok', 'obrigado') após conclusão não geram deriva."""
        # Arrange
        sessao = _sessao(fase=Fase.CONCLUIDO, workflow=None, etapa=0)
        turno = Turno(texto="ok, entendido. Obrigado!")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is False
        assert resultado.motivos == ()

    def test_deve_disparar_deriva_motivo4_quando_bypass_explicito_do_agent_router(self) -> None:
        """Menção direta para invocar especialista sem passar pelo router gera deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="python-feature-developer")
        turno = Turno(texto="Chame direto o @security-reviewer, sem passar pelo router.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is True
        assert "bypass_agent_router" in resultado.motivos

    def test_deve_disparar_deriva_motivo4_quando_frase_lexical_de_bypass(self) -> None:
        """Expressões lexicais como 'ignore o router' disparam deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="pr-gatekeeper")
        turno = Turno(texto="Ignore o router e vá direto para a aprovação final.")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is True
        assert "bypass_agent_router" in resultado.motivos

    def test_nao_deve_disparar_deriva_motivo4_quando_mencao_ao_proprio_agent_router(self) -> None:
        """Perguntar ou mencionar o próprio @agent-router não é bypass."""
        # Arrange
        sessao = _sessao(agente_ativo="python-feature-developer")
        turno = Turno(texto="Confirma se o @agent-router já despachou esse fluxo?")

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert not any(m == "bypass_agent_router" for m in resultado.motivos)

    @pytest.mark.parametrize(
        "texto_continuidade",
        [
            "Pode continuar com a implementação da classe de serviço.",
            "Acho que faltou cobrir o caso em que o payload vem vazio.",
            "Ajuste também o retorno da função para tratar None.",
            "Prossiga para a próxima etapa do plano.",
            "Refatore esse método para reduzir a complexidade ciclomática.",
        ],
    )
    def test_nao_deve_disparar_deriva_quando_refinamento_in_scope_continuidade(
        self, texto_continuidade: str
    ) -> None:
        """Refinamentos normais durante a execução da tarefa ativa não configuram deriva."""
        # Arrange
        sessao = _sessao(agente_ativo="python-feature-developer")
        turno = Turno(texto=texto_continuidade)

        # Act
        resultado = detectar_deriva(sessao, turno, _CATALOGO)

        # Assert
        assert resultado.houve is False
        assert resultado.motivos == ()

    def test_deve_garantir_pureza_estrutural_sem_imports_de_rede_ou_llm(self) -> None:
        """Valida estaticamente via AST que drift.py não importa nenhuma biblioteca proibida."""
        # Arrange
        codigo_fonte = inspect.getsource(drift)
        arvore = ast.parse(codigo_fonte)

        # Act
        modulos_importados: set[str] = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    modulos_importados.add(alias.name.split(".")[0])
            elif isinstance(no, ast.ImportFrom) and no.module:
                modulos_importados.add(no.module.split(".")[0])

        intersecao = modulos_importados & _MODULOS_PROIBIDOS

        # Assert
        assert not intersecao, f"Import proibido detectado em drift.py: {intersecao}"
