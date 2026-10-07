"""Testes de integração para SessionStore (persistência SQLite via SQLAlchemy Core)."""

from __future__ import annotations

import time
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import insert

from local_chat_gateway.session_store import (
    SessionRecord,
    SessionStore,
    TurnRecord,
    sessions_table,
)


def test_session_store_schema_creation_idempotent(tmp_db_path: Path) -> None:
    """Criar SessionStore duas vezes no mesmo db_path não levanta erro
    (create_all idempotente)."""
    store1 = SessionStore(tmp_db_path)
    assert store1 is not None

    # Segunda inicialização sobre o mesmo banco SQLite existente
    store2 = SessionStore(tmp_db_path)
    assert store2 is not None


def test_create_and_get_session(tmp_db_path: Path) -> None:
    """create_session('s1') seguido de get_session('s1') retorna
    SessionRecord com fase='router'."""
    store = SessionStore(tmp_db_path)
    created = store.create_session("s1")
    assert isinstance(created, SessionRecord)
    assert created.session_id == "s1"
    assert created.fase == "router"

    retrieved = store.get_session("s1")
    assert retrieved is not None
    assert retrieved.session_id == "s1"
    assert retrieved.fase == "router"
    assert retrieved.created_at == created.created_at
    assert retrieved.last_seen_at == created.last_seen_at


def test_get_nonexistent_session_returns_none(tmp_db_path: Path) -> None:
    """get_session('inexistente') retorna None."""
    store = SessionStore(tmp_db_path)
    assert store.get_session("inexistente") is None


def test_session_ttl_expiration(tmp_db_path: Path) -> None:
    """TTL: expiração detectada quando delta excede session_ttl_s."""
    session_ttl_s = 60
    store = SessionStore(tmp_db_path, session_ttl_s=session_ttl_s)

    store.create_session("s2", now=1000)

    # Dentro do TTL: 1000 + 1 => delta 1s <= 60s -> False
    assert store.is_session_expired("s2", now=1000 + 1) is False

    # Exatamente no TTL: delta 60s <= 60s -> False (condição > session_ttl_s)
    assert store.is_session_expired("s2", now=1000 + session_ttl_s) is False

    # Acima do TTL: 1000 + session_ttl_s + 1 => delta 61s > 60s -> True
    assert store.is_session_expired("s2", now=1000 + session_ttl_s + 1) is True

    # Sessão inexistente é considerada expirada
    assert store.is_session_expired("s_desconhecida", now=1000) is True


def test_touch_session_renews_ttl(tmp_db_path: Path) -> None:
    """touch_session('s2', now=...) atualiza last_seen_at renovando o TTL."""
    session_ttl_s = 60
    store = SessionStore(tmp_db_path, session_ttl_s=session_ttl_s)

    store.create_session("s2", now=1000)
    # No instante 1061 estaria expirada se não houvesse touch
    assert store.is_session_expired("s2", now=1061) is True

    # Renovação via touch_session no instante 1050
    store.touch_session("s2", now=1050)

    # Agora em 1061 (delta = 11s <= 60s) não está mais expirada
    assert store.is_session_expired("s2", now=1061) is False

    record = store.get_session("s2")
    assert record is not None
    assert record.last_seen_at == 1050
    assert record.created_at == 1000


def test_checkpoints_lifecycle(tmp_db_path: Path) -> None:
    """Checkpoints: abertura, verificação e resolução."""
    store = SessionStore(tmp_db_path)

    # Inicialmente nenhum checkpoint aberto
    assert store.is_checkpoint_open("s1") is False

    # Registrar checkpoint aberto
    store.record_checkpoint("cp-0001", "s1", "pergunta?")
    assert store.is_checkpoint_open("s1") is True

    # Outra sessão permanece sem checkpoint aberto
    assert store.is_checkpoint_open("s2") is False

    # Resolver checkpoint
    store.resolve_checkpoint("cp-0001")
    assert store.is_checkpoint_open("s1") is False


def test_daily_budget_limit(tmp_db_path: Path) -> None:
    """Budget diário: controle de cota por dia e isolamento entre datas distintas."""
    store = SessionStore(tmp_db_path, max_premium_per_day=5)

    # Primeiro consumo: 3 unidades
    consumo_1 = store.register_premium_request("2026-01-01", 3)
    assert consumo_1 == 3
    assert store.is_daily_budget_exhausted("2026-01-01") is False

    # Segundo consumo: +3 unidades => total 6 >= 5 (esgotado)
    consumo_2 = store.register_premium_request("2026-01-01", 3)
    assert consumo_2 == 6
    assert store.is_daily_budget_exhausted("2026-01-01") is True

    # Novo dia começa zerado e não esgotado
    assert store.is_daily_budget_exhausted("2026-01-02") is False


def test_create_session_duplicada_e_idempotente(tmp_db_path: Path) -> None:
    """create_session duas vezes com o mesmo session_id nao lanca IntegrityError
    e atualiza os timestamps / reinicia a sessao."""
    store = SessionStore(tmp_db_path)
    s1 = store.create_session("sessao-repetida", now=1000)
    assert s1.created_at == 1000

    # Segunda chamada com o mesmo ID nao deve levantar sqlite3.IntegrityError
    s2 = store.create_session("sessao-repetida", now=2000)
    assert s2.session_id == "sessao-repetida"
    assert s2.created_at == 2000
    assert s2.last_seen_at == 2000


# ---------------------------------------------------------------------------
# T4/PR-4 — campos aditivos de estado de governanca (workflow/etapa/
# agente_ativo/aprovacoes). Os testes acima (oraculo RK-05) permanecem
# intocados; os testes abaixo sao os novos desta etapa.
# ---------------------------------------------------------------------------


def test_colunas_governanca_aditivas_existem_com_default_null(tmp_db_path: Path) -> None:
    """As colunas workflow/etapa/agente_ativo/aprovacoes existem na tabela
    `sessions`, sao nullable e uma sessao criada via create_session() as
    deixa com valor None (retrocompatibilidade aditiva, RK-05)."""
    store = SessionStore(tmp_db_path)

    colunas_novas = {"workflow", "etapa", "agente_ativo", "aprovacoes"}
    nomes_colunas = set(sessions_table.columns.keys())
    assert colunas_novas.issubset(nomes_colunas)
    for nome in colunas_novas:
        assert sessions_table.columns[nome].nullable is True

    store.create_session("s-governanca")
    record = store.get_session("s-governanca")
    assert record is not None
    assert record.workflow is None
    assert record.etapa is None
    assert record.agente_ativo is None
    assert record.aprovacoes is None


def test_sessao_legada_sem_campos_governanca_e_lida_sem_excecao(tmp_db_path: Path) -> None:
    """Uma linha gravada diretamente sem os campos aditivos de governanca
    (simulando dado legado pre-T4) e lida por get_session() sem excecao,
    com os novos campos retornando None."""
    store = SessionStore(tmp_db_path)

    with store._engine.begin() as conn:
        conn.execute(
            insert(sessions_table).values(
                session_id="legada-1",
                created_at=1000,
                last_seen_at=1000,
                fase="router",
            )
        )

    record = store.get_session("legada-1")
    assert record is not None
    assert record.session_id == "legada-1"
    assert record.fase == "router"
    assert record.workflow is None
    assert record.etapa is None
    assert record.agente_ativo is None
    assert record.aprovacoes is None


def test_atualizar_estado_governanca_round_trip(tmp_db_path: Path) -> None:
    """atualizar_estado_governanca grava e rele fase/workflow/etapa/
    agente_ativo/aprovacoes (dict) de forma simetrica (round-trip de
    serializacao JSON)."""
    store = SessionStore(tmp_db_path)
    store.create_session("s-estado")

    aprovacoes = {"fase_atual": True, "revisor": "python-feature-developer"}
    store.atualizar_estado_governanca(
        "s-estado",
        "aguardando_aprovacao",
        "WORKFLOW-FEATURE-DEVELOPMENT",
        5,
        "python-feature-developer",
        aprovacoes,
    )

    record = store.get_session("s-estado")
    assert record is not None
    assert record.fase == "aguardando_aprovacao"
    assert record.workflow == "WORKFLOW-FEATURE-DEVELOPMENT"
    assert record.etapa == 5
    assert record.agente_ativo == "python-feature-developer"
    assert record.aprovacoes == aprovacoes


def test_atualizar_estado_governanca_atualizacao_parcial_preserva_campos_nao_informados(
    tmp_db_path: Path,
) -> None:
    """Parametros `None` em atualizar_estado_governanca preservam o valor ja
    persistido (atualizacao parcial), sem violar a constraint NOT NULL de
    `fase` nem sobrescrever campos nao informados."""
    store = SessionStore(tmp_db_path)
    store.create_session("s-parcial")
    store.atualizar_estado_governanca(
        "s-parcial", None, "WORKFLOW-X", 1, "agente-x", {"a": 1}
    )

    # Segunda chamada so atualiza etapa; demais campos devem ser preservados
    store.atualizar_estado_governanca("s-parcial", None, None, 2, None, None)

    record = store.get_session("s-parcial")
    assert record is not None
    assert record.fase == "router"  # preservado (create_session define "router")
    assert record.workflow == "WORKFLOW-X"  # preservado
    assert record.etapa == 2  # atualizado
    assert record.agente_ativo == "agente-x"  # preservado
    assert record.aprovacoes == {"a": 1}  # preservado


# ---------------------------------------------------------------------------
# Bug real de producao (2026-10-01): volume Docker `gateway-data` persistido
# ANTES de T4/PR-4 contem uma tabela `sessions` com apenas as colunas
# originais (session_id/created_at/last_seen_at/fase). `metadata.create_all`
# e idempotente apenas para CRIAR tabelas ausentes -- nao adiciona colunas
# a uma tabela ja existente. Resultado real: `sqlalchemy.exc.OperationalError:
# no such column: sessions.workflow` ao processar qualquer request via
# `docker compose --profile lobe --profile otel up` com volume reutilizado de
# sessao Fase <5. Os testes de T4 acima nao cobriam este cenario porque
# sempre usam `tmp_db_path` novo (1a instanciacao == tabela ja criada
# completa). Este teste reproduz o schema ANTIGO manualmente antes de
# instanciar `SessionStore`, validando a migracao aditiva real (ALTER TABLE
# ADD COLUMN) agora aplicada em `SessionStore.__init__`.
# ---------------------------------------------------------------------------


def test_banco_com_schema_antigo_pre_t4_e_migrado_automaticamente(
    tmp_db_path: Path,
) -> None:
    """Um banco SQLite com a tabela `sessions` no schema ANTERIOR a T4/PR-4
    (sem workflow/etapa/agente_ativo/aprovacoes) deve ser migrado
    automaticamente (ALTER TABLE ADD COLUMN) ao instanciar `SessionStore`,
    sem levantar `OperationalError: no such column`."""
    engine_legado = sa.create_engine(f"sqlite:///{tmp_db_path}", future=True)
    metadata_legada = sa.MetaData()
    sessions_table_legada = sa.Table(
        "sessions",
        metadata_legada,
        sa.Column("session_id", sa.String, primary_key=True),
        sa.Column("created_at", sa.Integer, nullable=False),
        sa.Column("last_seen_at", sa.Integer, nullable=False),
        sa.Column("fase", sa.String, nullable=False, default="router"),
    )
    metadata_legada.create_all(engine_legado)
    with engine_legado.begin() as conn:
        conn.execute(
            insert(sessions_table_legada).values(
                session_id="sessao-pre-t4", created_at=1000, last_seen_at=1000, fase="router"
            )
        )
    engine_legado.dispose()

    # Instanciar SessionStore sobre o banco LEGADO nao deve lancar excecao,
    # e o registro pre-existente deve ser legivel com os campos novos em None.
    store = SessionStore(tmp_db_path)
    record = store.get_session("sessao-pre-t4")
    assert record is not None
    assert record.session_id == "sessao-pre-t4"
    assert record.fase == "router"
    assert record.workflow is None
    assert record.etapa is None
    assert record.agente_ativo is None
    assert record.aprovacoes is None

    # E o fluxo normal (create/atualizar_estado_governanca) continua operando
    # normalmente apos a migracao.
    store.create_session("sessao-nova-pos-migracao")
    store.atualizar_estado_governanca(
        "sessao-nova-pos-migracao", None, "WORKFLOW-BUG-FIX", 1, "bug-triage", None
    )
    record_novo = store.get_session("sessao-nova-pos-migracao")
    assert record_novo is not None
    assert record_novo.workflow == "WORKFLOW-BUG-FIX"


# ---------------------------------------------------------------------------
# Bug real de producao (2026-10-01, Addendum 6): Lobe Chat reportou
# `[GOVERNANCA] Nao foi possivel avancar o turno de governanca ...
# R-037: a partir da Fase.ROUTER so e aceita uma decisao de roteamento
# explicita ... evento recebido tem tipo=<TipoEvento.AVANCO_ETAPA>`.
#
# Causa raiz: `create_session()` reinicia uma sessao EXPIRADA (TTL,
# GATEWAY_SESSION_TTL_S) voltando `fase="router"`, mas preservava
# `workflow`/`etapa`/`agente_ativo`/`aprovacoes` do turno anterior (apenas
# a branch de UPDATE, nao a de INSERT). `_sessao_atual` (routes.py) entao
# reconstroi uma `Sessao` com `fase=ROUTER` + `workflow` residual nao-nulo;
# `preparar_turno` (governance_pipeline.py) usa `sessao.workflow is None`
# para decidir se re-roteia -- como o workflow residual NAO e None, o turno
# gera `TipoEvento.AVANCO_ETAPA` em vez de `DECISAO_ROTEAMENTO`, que a state
# machine rejeita (R-037) por estar em `Fase.ROUTER`. Este teste reproduz o
# estado inconsistente diretamente no `SessionStore`, sem precisar do
# roteador completo.
# ---------------------------------------------------------------------------


def test_create_session_em_sessao_expirada_reseta_campos_de_governanca(
    tmp_db_path: Path,
) -> None:
    """create_session() chamado sobre uma sessao EXISTENTE (TTL expirado,
    `routes.py` linha ~524) deve resetar workflow/etapa/agente_ativo/
    aprovacoes para None junto com fase='router' -- nunca deixar
    `fase=ROUTER` com `workflow` residual de um turno anterior (bug real
    de producao 2026-10-01, Addendum 6)."""
    store = SessionStore(tmp_db_path)
    store.create_session("sessao-ttl-expirado", now=1000)
    store.atualizar_estado_governanca(
        "sessao-ttl-expirado",
        "em_workflow",
        "WORKFLOW-FEATURE-DEVELOPMENT",
        3,
        "python-feature-developer",
        {"2": True},
    )

    # Simula o reset de sessao expirada (routes.py: is_session_expired=True)
    store.create_session("sessao-ttl-expirado", now=5000)

    record = store.get_session("sessao-ttl-expirado")
    assert record is not None
    assert record.fase == "router"
    assert record.workflow is None
    assert record.etapa is None
    assert record.agente_ativo is None
    assert record.aprovacoes is None


class TestTurnsTable:
    """Testes da tabela `turns` (historico DURAVEL por turno, pedido
    explicito do usuario 2026-10-02 -- insumo de analise continua de
    melhoria de workflow/agent). Diferente de `sessions` (estado ATUAL
    sobrescrito), `turns` e so-insercao: cada turno fica permanentemente
    auditavel."""

    def test_record_turn_minimo_e_recuperavel_por_get_turn(
        self, tmp_db_path: Path
    ) -> None:
        store = SessionStore(tmp_db_path)
        store.record_turn(
            TurnRecord(
                turn_id="turn-1",
                session_id="sess-1",
                created_at=1000,
            )
        )

        recuperado = store.get_turn("turn-1")
        assert recuperado is not None
        assert recuperado.turn_id == "turn-1"
        assert recuperado.session_id == "sess-1"
        assert recuperado.created_at == 1000
        # Campos opcionais nao informados ficam None (degrada graciosamente).
        assert recuperado.prompt is None
        assert recuperado.tokens_input is None

    def test_get_turn_inexistente_retorna_none(self, tmp_db_path: Path) -> None:
        store = SessionStore(tmp_db_path)
        assert store.get_turn("nao-existe") is None

    def test_record_turn_persiste_todos_os_campos_de_turn_recorder(
        self, tmp_db_path: Path
    ) -> None:
        """Round-trip completo com TODOS os campos populados (incluindo
        JSON de tools/subagents/retries/falhas de model call e os booleans
        convertidos para 0/1 no SQLite) -- prova que nenhum campo de
        `turn_recorder.AcumuladorDeTurno` se perde na persistencia."""
        store = SessionStore(tmp_db_path)
        registro = TurnRecord(
            turn_id="turn-completo",
            session_id="sess-2",
            created_at=1000,
            ended_at=1005,
            duration_ms=5000,
            prompt="altere 5 linhas do README",
            response_text="Agente Ativo: bug-triage\n\nFeito.",
            agent_name="bug-triage",
            agent_model="Claude Sonnet 5.5",
            workflow="WORKFLOW-BUG-FIX",
            etapa=2,
            score_roteamento=0.93,
            drift_detectado=False,
            handoff_origem="agent-router",
            handoff_motivo="deriva_de_intencao",
            checkpoint_aberto=True,
            trace_id="trace-abc",
            detected_intent="fix_bug",
            tools_executados=[{"nome": "read_file", "duracao_ms": 120}],
            subagents_executados=[
                {"nome": "bug-triage", "duracao_ms": 4300, "outcome": "sucesso"}
            ],
            retries_count=2,
            retry_reasons=["timeout", "rate_limit"],
            model_call_failures=[{"model": "gpt-5", "error_type": "timeout"}],
            tokens_input=1200,
            tokens_output=340,
            tokens_reasoning=50,
            tokens_cache_read=800,
            tokens_cache_write=100,
            cost_nano_aiu=12.5,
            time_to_first_token_ms=450,
            stop_reason="completed",
            successful_tool_count=3,
            failed_tool_count=1,
            context_truncado=True,
            tokens_removidos_truncamento=2000,
            compaction_disparada=True,
            error_type=None,
        )
        store.record_turn(registro)

        recuperado = store.get_turn("turn-completo")
        assert recuperado is not None
        assert recuperado.prompt == "altere 5 linhas do README"
        assert recuperado.agent_name == "bug-triage"
        assert recuperado.workflow == "WORKFLOW-BUG-FIX"
        assert recuperado.score_roteamento == 0.93
        assert recuperado.drift_detectado is False
        assert recuperado.checkpoint_aberto is True
        assert recuperado.tools_executados == [{"nome": "read_file", "duracao_ms": 120}]
        assert recuperado.subagents_executados == [
            {"nome": "bug-triage", "duracao_ms": 4300, "outcome": "sucesso"}
        ]
        assert recuperado.retries_count == 2
        assert recuperado.retry_reasons == ["timeout", "rate_limit"]
        assert recuperado.model_call_failures == [
            {"model": "gpt-5", "error_type": "timeout"}
        ]
        assert recuperado.tokens_input == 1200
        assert recuperado.cost_nano_aiu == 12.5
        assert recuperado.context_truncado is True
        assert recuperado.compaction_disparada is True

    def test_get_turns_ordena_mais_recentes_primeiro(self, tmp_db_path: Path) -> None:
        store = SessionStore(tmp_db_path)
        store.record_turn(TurnRecord(turn_id="t-antigo", session_id="s", created_at=1000))
        store.record_turn(TurnRecord(turn_id="t-recente", session_id="s", created_at=2000))

        turnos = store.get_turns("s")
        assert [t.turn_id for t in turnos] == ["t-recente", "t-antigo"]

    def test_get_turns_filtra_por_session_id(self, tmp_db_path: Path) -> None:
        store = SessionStore(tmp_db_path)
        store.record_turn(TurnRecord(turn_id="t-a", session_id="sessao-a", created_at=1000))
        store.record_turn(TurnRecord(turn_id="t-b", session_id="sessao-b", created_at=1000))

        turnos_a = store.get_turns("sessao-a")
        assert [t.turn_id for t in turnos_a] == ["t-a"]

    def test_get_turns_sem_session_id_lista_de_todas_as_sessoes(
        self, tmp_db_path: Path
    ) -> None:
        store = SessionStore(tmp_db_path)
        store.record_turn(TurnRecord(turn_id="t-a", session_id="sessao-a", created_at=1000))
        store.record_turn(TurnRecord(turn_id="t-b", session_id="sessao-b", created_at=2000))

        turnos = store.get_turns()
        assert {t.turn_id for t in turnos} == {"t-a", "t-b"}

    def test_get_turns_respeita_limit(self, tmp_db_path: Path) -> None:
        store = SessionStore(tmp_db_path)
        for i in range(5):
            store.record_turn(
                TurnRecord(turn_id=f"t-{i}", session_id="s", created_at=1000 + i)
            )

        turnos = store.get_turns("s", limit=2)
        assert len(turnos) == 2
        # Mais recentes primeiro: t-4, t-3.
        assert [t.turn_id for t in turnos] == ["t-4", "t-3"]

    def test_purge_old_turns_remove_apenas_registros_mais_antigos_que_retention(
        self, tmp_db_path: Path
    ) -> None:
        store = SessionStore(tmp_db_path)
        agora = int(time.time())
        trinta_e_um_dias_atras = agora - (31 * 86400)
        vinte_e_nove_dias_atras = agora - (29 * 86400)
        store.record_turn(
            TurnRecord(turn_id="t-velho", session_id="s", created_at=trinta_e_um_dias_atras)
        )
        store.record_turn(
            TurnRecord(turn_id="t-recente", session_id="s", created_at=vinte_e_nove_dias_atras)
        )

        removidos = store.purge_old_turns(retention_days=30)

        assert removidos == 1
        assert store.get_turn("t-velho") is None
        assert store.get_turn("t-recente") is not None

    def test_purge_old_turns_com_retention_days_zero_ou_negativo_nao_remove_nada(
        self, tmp_db_path: Path
    ) -> None:
        store = SessionStore(tmp_db_path)
        muito_antigo = int(time.time()) - (365 * 86400)
        store.record_turn(
            TurnRecord(turn_id="t-antigo", session_id="s", created_at=muito_antigo)
        )

        assert store.purge_old_turns(retention_days=0) == 0
        assert store.purge_old_turns(retention_days=-5) == 0
        assert store.get_turn("t-antigo") is not None

    def test_purge_old_turns_sem_registros_antigos_retorna_zero(
        self, tmp_db_path: Path
    ) -> None:
        store = SessionStore(tmp_db_path)
        store.record_turn(
            TurnRecord(turn_id="t-novo", session_id="s", created_at=int(time.time()))
        )

        assert store.purge_old_turns(retention_days=30) == 0
        assert store.get_turn("t-novo") is not None


