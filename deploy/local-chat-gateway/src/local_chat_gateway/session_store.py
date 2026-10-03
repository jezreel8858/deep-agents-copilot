"""session_store — persistencia SQLite (SQLAlchemy Core, sem ORM) do gateway.

3 tabelas (BLUEPRINT_LOCAL_CHAT_GATEWAY.md Secao 4.1 / plano Secao 1):
`sessions`, `checkpoints`, `budget_daily`. Sem ORM — schema simples,
queries via `sqlalchemy.select`/`insert`/`update` parametrizadas
(nunca concatenacao de string em SQL).

T4/PR-4 (20261001-feature-development-governance-runner-sdk-integration.md):
campos aditivos de estado de governanca em `sessions` (`workflow`, `etapa`,
`agente_ativo`, `aprovacoes`) — todos `nullable=True`/default `None`, para
preservar retrocompatibilidade com sessoes gravadas antes desta mudanca
(RK-05, oraculo em `test_session_store.py`).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    insert,
    inspect,
    select,
    text,
    update,
)
from sqlalchemy.engine import Engine

metadata = MetaData()

sessions_table = Table(
    "sessions",
    metadata,
    Column("session_id", String, primary_key=True),
    Column("created_at", Integer, nullable=False),
    Column("last_seen_at", Integer, nullable=False),
    Column("fase", String, nullable=False, default="router"),
    # --- Campos aditivos de estado de governanca (T4/PR-4) ---
    # Todos nullable=True/default=None: sessoes legadas (gravadas antes
    # desta mudanca) continuam legiveis sem excecao (RK-05).
    Column("workflow", String, nullable=True, default=None),
    Column("etapa", Integer, nullable=True, default=None),
    Column("agente_ativo", String, nullable=True, default=None),
    Column("aprovacoes", JSON, nullable=True, default=None),
)

checkpoints_table = Table(
    "checkpoints",
    metadata,
    Column("checkpoint_id", String, primary_key=True),
    Column("session_id", String, nullable=False),
    Column("question", String, nullable=False),
    Column("resolved", Integer, nullable=False, default=0),
)

budget_daily_table = Table(
    "budget_daily",
    metadata,
    Column("day", String, primary_key=True),
    Column("premium_requests_consumed", Integer, nullable=False, default=0),
)

# Historico IMUTAVEL por turno (1 linha por prompt completo, do inicio ao
# fim -- com ou sem workflow/subagents), pedido explicito do usuario
# (2026-10-02): insumo de analise continua de melhoria de workflow/agent.
# Diferente de `sessions_table` (estado ATUAL sobrescrito a cada turno),
# esta tabela e so-insercao (`record_turn`, sempre INSERT, nunca UPDATE) --
# cada turno fica permanentemente auditavel. Populada por
# `turn_recorder.persistir` a partir dos eventos reais do SDK Copilot
# (`sdk_session.stream_chat_ag_ui`), complementar ao export OTel/Langfuse
# best-effort de `telemetry.py` (que depende de um Collector externo estar
# rodando) -- esta tabela SEMPRE persiste localmente, independente de
# qualquer observability stack externo.
turns_table = Table(
    "turns",
    metadata,
    Column("turn_id", String, primary_key=True),
    Column("session_id", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("ended_at", Integer, nullable=True),
    Column("duration_ms", Integer, nullable=True),
    Column("prompt", String, nullable=True),
    Column("response_text", String, nullable=True),
    Column("agent_name", String, nullable=True),
    Column("agent_model", String, nullable=True),
    Column("workflow", String, nullable=True),
    Column("etapa", Integer, nullable=True),
    Column("score_roteamento", Float, nullable=True),
    Column("drift_detectado", Integer, nullable=True),  # bool como 0/1
    Column("handoff_origem", String, nullable=True),
    Column("handoff_motivo", String, nullable=True),
    Column("checkpoint_aberto", Integer, nullable=True),  # bool como 0/1
    Column("trace_id", String, nullable=True),
    Column("detected_intent", String, nullable=True),
    Column("tools_executados", JSON, nullable=True),
    Column("subagents_executados", JSON, nullable=True),
    Column("retries_count", Integer, nullable=True, default=0),
    Column("retry_reasons", JSON, nullable=True),
    Column("model_call_failures", JSON, nullable=True),
    Column("tokens_input", Integer, nullable=True, default=0),
    Column("tokens_output", Integer, nullable=True, default=0),
    Column("tokens_reasoning", Integer, nullable=True, default=0),
    Column("tokens_cache_read", Integer, nullable=True, default=0),
    Column("tokens_cache_write", Integer, nullable=True, default=0),
    Column("cost_nano_aiu", Float, nullable=True),
    Column("time_to_first_token_ms", Integer, nullable=True),
    Column("stop_reason", String, nullable=True),
    Column("successful_tool_count", Integer, nullable=True),
    Column("failed_tool_count", Integer, nullable=True),
    Column("context_truncado", Integer, nullable=True),  # bool como 0/1
    Column("tokens_removidos_truncamento", Integer, nullable=True, default=0),
    Column("compaction_disparada", Integer, nullable=True),  # bool como 0/1
    Column("error_type", String, nullable=True),
)


# idempotente em `_migrar_colunas_aditivas_sessions` (ver docstring abaixo).
_COLUNAS_ADITIVAS_SESSIONS: tuple[Column[Any], ...] = (
    sessions_table.c.workflow,
    sessions_table.c.etapa,
    sessions_table.c.agente_ativo,
    sessions_table.c.aprovacoes,
)


def _migrar_colunas_aditivas_sessions(engine: Engine) -> None:
    """Migracao idempotente (`ALTER TABLE ... ADD COLUMN`) das colunas
    aditivas de estado de governanca (T4/PR-4) em bancos SQLite ja existentes.

    Bug real de producao encontrado em 2026-10-01: `metadata.create_all()`
    (chamado em `SessionStore.__init__`) e idempotente apenas para CRIAR
    tabelas ausentes -- ele NUNCA adiciona colunas a uma tabela `sessions`
    ja existente no disco. Um volume Docker (`gateway-data`) persistido
    ANTES de T4/PR-4 contem uma tabela `sessions` com apenas as colunas
    originais (`session_id`/`created_at`/`last_seen_at`/`fase`), causando
    `sqlalchemy.exc.OperationalError: no such column: sessions.workflow` em
    toda query via `get_session`/`is_session_expired`/`atualizar_estado_
    governanca` apos o deploy da Fase 5 sobre um volume reutilizado.

    Esta funcao inspeciona as colunas reais da tabela `sessions` no banco
    e aplica `ALTER TABLE ADD COLUMN` apenas para as que estiverem
    ausentes -- seguro para chamar a cada startup (idempotente) e sem
    efeito quando a tabela ja foi criada do zero com o schema completo
    (caso coberto por `metadata.create_all`).

    Args:
        engine: Engine SQLAlchemy ja conectada ao banco SQLite do gateway.
    """
    inspector = inspect(engine)
    if "sessions" not in inspector.get_table_names():
        return
    colunas_existentes = {coluna["name"] for coluna in inspector.get_columns("sessions")}
    with engine.begin() as conn:
        for coluna in _COLUNAS_ADITIVAS_SESSIONS:
            if coluna.name in colunas_existentes:
                continue
            tipo_sql = coluna.type.compile(dialect=engine.dialect)
            conn.execute(text(f"ALTER TABLE sessions ADD COLUMN {coluna.name} {tipo_sql}"))


@dataclass(frozen=True)
class SessionRecord:
    """Registro imutavel de uma linha da tabela `sessions`.

    Os campos `workflow`, `etapa`, `agente_ativo` e `aprovacoes` sao
    aditivos (T4/PR-4) e persistem o estado de governanca do turno (ver
    `governance_pipeline.DecisaoTurno`/`governance.Sessao`). Sessoes
    legadas (gravadas antes desta mudanca) retornam `None` nesses campos
    (retrocompatibilidade, RK-05).
    """

    session_id: str
    created_at: int
    last_seen_at: int
    fase: str
    workflow: str | None = None
    etapa: int | None = None
    agente_ativo: str | None = None
    aprovacoes: dict[str, Any] | None = None


@dataclass(frozen=True)
class CheckpointRecord:
    """Registro imutavel de uma linha da tabela `checkpoints`."""

    checkpoint_id: str
    session_id: str
    question: str
    resolved: int


@dataclass(frozen=True)
class TurnRecord:
    """Registro imutavel de 1 turno completo (1 linha de `turns`).

    Populado por `turn_recorder.persistir` a partir dos eventos reais do
    SDK Copilot acumulados durante `sdk_session.stream_chat_ag_ui` -- ver
    docstring de `turns_table` acima. Todos os campos alem de
    `turn_id`/`session_id`/`created_at` sao opcionais (degradam
    graciosamente quando o SDK nao emitir o evento correspondente nesta
    versao/sessao).
    """

    turn_id: str
    session_id: str
    created_at: int
    ended_at: int | None = None
    duration_ms: int | None = None
    prompt: str | None = None
    response_text: str | None = None
    agent_name: str | None = None
    agent_model: str | None = None
    workflow: str | None = None
    etapa: int | None = None
    score_roteamento: float | None = None
    drift_detectado: bool | None = None
    handoff_origem: str | None = None
    handoff_motivo: str | None = None
    checkpoint_aberto: bool | None = None
    trace_id: str | None = None
    detected_intent: str | None = None
    tools_executados: list[dict[str, Any]] | None = None
    subagents_executados: list[dict[str, Any]] | None = None
    retries_count: int | None = None
    retry_reasons: list[str] | None = None
    model_call_failures: list[dict[str, Any]] | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None
    tokens_reasoning: int | None = None
    tokens_cache_read: int | None = None
    tokens_cache_write: int | None = None
    cost_nano_aiu: float | None = None
    time_to_first_token_ms: int | None = None
    stop_reason: str | None = None
    successful_tool_count: int | None = None
    failed_tool_count: int | None = None
    context_truncado: bool | None = None
    tokens_removidos_truncamento: int | None = None
    compaction_disparada: bool | None = None
    error_type: str | None = None


class SessionStore:
    """Persistencia de sessoes/checkpoints/budget diario em SQLite.

    Cria o schema (idempotente via `metadata.create_all`) na inicializacao,
    e migra bancos pre-existentes que ainda nao possuem as colunas aditivas
    de governanca (T4/PR-4) via `_migrar_colunas_aditivas_sessions` (ALTER
    TABLE ADD COLUMN idempotente).
    """

    def __init__(
        self,
        db_path: str | Path,
        *,
        session_ttl_s: int = 1800,
        max_premium_per_day: int = 100,
    ) -> None:
        """Inicializa a engine SQLite e cria o schema, se ausente.

        Args:
            db_path: Caminho do arquivo SQLite (ex.: `tmp_path / "gw.db"`).
            session_ttl_s: TTL de sessao em segundos (`GATEWAY_SESSION_TTL_S`).
            max_premium_per_day: Teto diario de premium requests
                (`GATEWAY_MAX_PREMIUM_PER_DAY`).
        """
        self._engine: Engine = create_engine(f"sqlite:///{db_path}", future=True)
        self._session_ttl_s = session_ttl_s
        self._max_premium_per_day = max_premium_per_day
        metadata.create_all(self._engine)
        _migrar_colunas_aditivas_sessions(self._engine)

    def create_session(
        self, session_id: str, *, now: int | None = None
    ) -> SessionRecord:
        """Insere ou reinicia uma sessao com `fase="router"` de forma idempotente.

        Bug real de producao (2026-10-01, Addendum 6): quando `session_id` ja
        existe (sessao expirada por TTL -- `routes.py` chama `create_session`
        apenas quando `is_session_expired` e `True`), a branch de UPDATE
        reiniciava `fase="router"` mas preservava os campos aditivos de
        governanca (`workflow`/`etapa`/`agente_ativo`/`aprovacoes`) do turno
        anterior. Isso deixava a sessao em um estado inconsistente --
        `fase=ROUTER` com `workflow` residual nao-nulo -- que fazia
        `governance_pipeline.preparar_turno` reaproveitar o workflow antigo
        (pois `sessao.workflow is not None`) e gerar `TipoEvento.AVANCO_ETAPA`
        em vez de `DECISAO_ROTEAMENTO`, rejeitado pela state machine com
        `TransicaoInvalidaError: R-037: a partir da Fase.ROUTER so e aceita
        uma decisao de roteamento explicita`. Corrigido resetando TODOS os
        campos de governanca para `None`/0 junto com `fase="router"` -- uma
        sessao reiniciada por expiracao de TTL deve comecar 100% do zero no
        router, igual a uma sessao nova (RK-06).
        """
        ts = now if now is not None else int(time.time())
        existing = self.get_session(session_id)
        with self._engine.begin() as conn:
            if existing is None:
                conn.execute(
                    insert(sessions_table).values(
                        session_id=session_id,
                        created_at=ts,
                        last_seen_at=ts,
                        fase="router",
                    )
                )
            else:
                conn.execute(
                    update(sessions_table)
                    .where(sessions_table.c.session_id == session_id)
                    .values(
                        created_at=ts,
                        last_seen_at=ts,
                        fase="router",
                        workflow=None,
                        etapa=None,
                        agente_ativo=None,
                        aprovacoes=None,
                    )
                )
        return SessionRecord(
            session_id=session_id, created_at=ts, last_seen_at=ts, fase="router"
        )

    def get_session(self, session_id: str) -> SessionRecord | None:
        """Busca uma sessao por ID; `None` se nao existir."""
        with self._engine.connect() as conn:
            row = conn.execute(
                select(sessions_table).where(sessions_table.c.session_id == session_id)
            ).first()
        if row is None:
            return None
        return SessionRecord(
            session_id=row.session_id,
            created_at=row.created_at,
            last_seen_at=row.last_seen_at,
            fase=row.fase,
            workflow=row.workflow,
            etapa=row.etapa,
            agente_ativo=row.agente_ativo,
            aprovacoes=row.aprovacoes,
        )

    def is_session_expired(self, session_id: str, *, now: int | None = None) -> bool:
        """`True` se a sessao nao existir ou o TTL desde `last_seen_at`
        tiver expirado."""
        record = self.get_session(session_id)
        if record is None:
            return True
        ts = now if now is not None else int(time.time())
        return (ts - record.last_seen_at) > self._session_ttl_s

    def touch_session(self, session_id: str, *, now: int | None = None) -> None:
        """Atualiza `last_seen_at` da sessao (renovacao de TTL)."""
        ts = now if now is not None else int(time.time())
        with self._engine.begin() as conn:
            conn.execute(
                update(sessions_table)
                .where(sessions_table.c.session_id == session_id)
                .values(last_seen_at=ts)
            )

    def atualizar_estado_governanca(
        self,
        session_id: str,
        fase: str | None,
        workflow: str | None,
        etapa: int | None,
        agente_ativo: str | None,
        aprovacoes: dict[str, Any] | None,
    ) -> None:
        """Atualiza os campos de estado de governanca de uma sessao existente.

        Atualizacao parcial: cada parametro `None` significa "nao alterar
        este campo" (preserva o valor ja persistido). Essa semantica evita
        violar a constraint `NOT NULL` da coluna `fase` (preexistente a
        T4) e permite que o chamador (`governance_pipeline`/`routes.py`)
        atualize apenas os campos conhecidos a cada turno.

        Args:
            session_id: Identificador da sessao ja existente (ver
                `create_session`).
            fase: Nova fase do turno de governanca, ou `None` para manter a
                fase ja persistida.
            workflow: Workflow ativo a persistir, ou `None` para manter o
                valor ja persistido.
            etapa: Indice da etapa corrente no workflow, ou `None` para
                manter o valor ja persistido.
            agente_ativo: Nome do agente ativo (R-042), ou `None` para
                manter o valor ja persistido.
            aprovacoes: Mapa de aprovacoes concedidas (dict serializado via
                coluna `JSON`), ou `None` para manter o valor ja
                persistido.
        """
        valores: dict[str, Any] = {}
        if fase is not None:
            valores["fase"] = fase
        if workflow is not None:
            valores["workflow"] = workflow
        if etapa is not None:
            valores["etapa"] = etapa
        if agente_ativo is not None:
            valores["agente_ativo"] = agente_ativo
        if aprovacoes is not None:
            valores["aprovacoes"] = aprovacoes
        if not valores:
            return
        with self._engine.begin() as conn:
            conn.execute(
                update(sessions_table)
                .where(sessions_table.c.session_id == session_id)
                .values(**valores)
            )

    def record_checkpoint(
        self, checkpoint_id: str, session_id: str, question: str
    ) -> None:
        """Registra um novo checkpoint aberto (`resolved=0`)."""
        with self._engine.begin() as conn:
            conn.execute(
                insert(checkpoints_table).values(
                    checkpoint_id=checkpoint_id,
                    session_id=session_id,
                    question=question,
                    resolved=0,
                )
            )

    def resolve_checkpoint(self, checkpoint_id: str) -> None:
        """Marca um checkpoint como resolvido."""
        with self._engine.begin() as conn:
            conn.execute(
                update(checkpoints_table)
                .where(checkpoints_table.c.checkpoint_id == checkpoint_id)
                .values(resolved=1)
            )

    def is_checkpoint_open(self, session_id: str) -> bool:
        """`True` se existir ao menos 1 checkpoint nao resolvido para a sessao."""
        with self._engine.connect() as conn:
            count = conn.execute(
                select(func.count())
                .select_from(checkpoints_table)
                .where(
                    checkpoints_table.c.session_id == session_id,
                    checkpoints_table.c.resolved == 0,
                )
            ).scalar_one()
        return bool(count)

    def get_open_checkpoint(self, session_id: str) -> CheckpointRecord | None:
        """Retorna o primeiro checkpoint aberto (nao resolvido) da sessao."""
        with self._engine.connect() as conn:
            row = conn.execute(
                select(checkpoints_table)
                .where(
                    checkpoints_table.c.session_id == session_id,
                    checkpoints_table.c.resolved == 0,
                )
                .order_by(checkpoints_table.c.checkpoint_id.asc())
            ).first()
        if row is None:
            return None
        return CheckpointRecord(
            checkpoint_id=row.checkpoint_id,
            session_id=row.session_id,
            question=row.question,
            resolved=row.resolved,
        )

    def register_premium_request(self, day: str, amount: int = 1) -> int:
        """Incrementa o consumo diario de premium requests; retorna o total do dia."""
        with self._engine.begin() as conn:
            row = conn.execute(
                select(budget_daily_table).where(budget_daily_table.c.day == day)
            ).first()
            if row is None:
                conn.execute(
                    insert(budget_daily_table).values(
                        day=day, premium_requests_consumed=amount
                    )
                )
                return amount
            novo_total = int(row.premium_requests_consumed) + amount
            conn.execute(
                update(budget_daily_table)
                .where(budget_daily_table.c.day == day)
                .values(premium_requests_consumed=novo_total)
            )
            return novo_total

    def is_daily_budget_exhausted(self, day: str) -> bool:
        """`True` se o consumo do dia atingiu/ultrapassou o teto diario."""
        with self._engine.connect() as conn:
            row = conn.execute(
                select(budget_daily_table).where(budget_daily_table.c.day == day)
            ).first()
        consumido = row.premium_requests_consumed if row is not None else 0
        return consumido >= self._max_premium_per_day

    def record_turn(self, record: TurnRecord) -> None:
        """Insere 1 linha IMUTAVEL em `turns` (sempre INSERT, nunca UPDATE).

        Pedido explicito do usuario (2026-10-02): historico permanente e
        auditavel por turno, independente de qualquer observability stack
        externo (OTel Collector/Langfuse) estar configurado/rodando --
        contraste deliberado com `atualizar_estado_governanca` (UPDATE, so
        preserva o estado ATUAL da sessao).

        `turn_id` ja deve ser unico (reaproveita o `run_id` do protocolo
        AG-UI, 1 por turno) -- `INSERT` duplicado levanta
        `IntegrityError` propagado ao chamador (`turn_recorder.persistir`
        ja captura qualquer excecao aqui, NUNCA deve derrubar o turno de
        chat real por uma falha de persistencia de analytics).
        """
        with self._engine.begin() as conn:
            conn.execute(
                insert(turns_table).values(
                    turn_id=record.turn_id,
                    session_id=record.session_id,
                    created_at=record.created_at,
                    ended_at=record.ended_at,
                    duration_ms=record.duration_ms,
                    prompt=record.prompt,
                    response_text=record.response_text,
                    agent_name=record.agent_name,
                    agent_model=record.agent_model,
                    workflow=record.workflow,
                    etapa=record.etapa,
                    score_roteamento=record.score_roteamento,
                    drift_detectado=(
                        int(record.drift_detectado)
                        if record.drift_detectado is not None
                        else None
                    ),
                    handoff_origem=record.handoff_origem,
                    handoff_motivo=record.handoff_motivo,
                    checkpoint_aberto=(
                        int(record.checkpoint_aberto)
                        if record.checkpoint_aberto is not None
                        else None
                    ),
                    trace_id=record.trace_id,
                    detected_intent=record.detected_intent,
                    tools_executados=record.tools_executados,
                    subagents_executados=record.subagents_executados,
                    retries_count=record.retries_count,
                    retry_reasons=record.retry_reasons,
                    model_call_failures=record.model_call_failures,
                    tokens_input=record.tokens_input,
                    tokens_output=record.tokens_output,
                    tokens_reasoning=record.tokens_reasoning,
                    tokens_cache_read=record.tokens_cache_read,
                    tokens_cache_write=record.tokens_cache_write,
                    cost_nano_aiu=record.cost_nano_aiu,
                    time_to_first_token_ms=record.time_to_first_token_ms,
                    stop_reason=record.stop_reason,
                    successful_tool_count=record.successful_tool_count,
                    failed_tool_count=record.failed_tool_count,
                    context_truncado=(
                        int(record.context_truncado)
                        if record.context_truncado is not None
                        else None
                    ),
                    tokens_removidos_truncamento=record.tokens_removidos_truncamento,
                    compaction_disparada=(
                        int(record.compaction_disparada)
                        if record.compaction_disparada is not None
                        else None
                    ),
                    error_type=record.error_type,
                )
            )

    @staticmethod
    def _row_para_turn_record(row: Any) -> TurnRecord:
        return TurnRecord(
            turn_id=row.turn_id,
            session_id=row.session_id,
            created_at=row.created_at,
            ended_at=row.ended_at,
            duration_ms=row.duration_ms,
            prompt=row.prompt,
            response_text=row.response_text,
            agent_name=row.agent_name,
            agent_model=row.agent_model,
            workflow=row.workflow,
            etapa=row.etapa,
            score_roteamento=row.score_roteamento,
            drift_detectado=(
                bool(row.drift_detectado) if row.drift_detectado is not None else None
            ),
            handoff_origem=row.handoff_origem,
            handoff_motivo=row.handoff_motivo,
            checkpoint_aberto=(
                bool(row.checkpoint_aberto) if row.checkpoint_aberto is not None else None
            ),
            trace_id=row.trace_id,
            detected_intent=row.detected_intent,
            tools_executados=row.tools_executados,
            subagents_executados=row.subagents_executados,
            retries_count=row.retries_count,
            retry_reasons=row.retry_reasons,
            model_call_failures=row.model_call_failures,
            tokens_input=row.tokens_input,
            tokens_output=row.tokens_output,
            tokens_reasoning=row.tokens_reasoning,
            tokens_cache_read=row.tokens_cache_read,
            tokens_cache_write=row.tokens_cache_write,
            cost_nano_aiu=row.cost_nano_aiu,
            time_to_first_token_ms=row.time_to_first_token_ms,
            stop_reason=row.stop_reason,
            successful_tool_count=row.successful_tool_count,
            failed_tool_count=row.failed_tool_count,
            context_truncado=(
                bool(row.context_truncado) if row.context_truncado is not None else None
            ),
            tokens_removidos_truncamento=row.tokens_removidos_truncamento,
            compaction_disparada=(
                bool(row.compaction_disparada)
                if row.compaction_disparada is not None
                else None
            ),
            error_type=row.error_type,
        )

    def get_turns(
        self, session_id: str | None = None, *, limit: int = 100
    ) -> list[TurnRecord]:
        """Lista turnos (mais recentes primeiro), opcionalmente filtrados
        por `session_id` -- consumido pelo endpoint read-only `GET
        /v1/turns` e por `tests/evals`/`agent-evals-lab` para fechar o loop
        de melhoria continua (trace real -> dataset de avaliacao)."""
        query = select(turns_table).order_by(turns_table.c.created_at.desc()).limit(limit)
        if session_id is not None:
            query = query.where(turns_table.c.session_id == session_id)
        with self._engine.connect() as conn:
            rows = conn.execute(query).all()
        return [self._row_para_turn_record(row) for row in rows]

    def get_turn(self, turn_id: str) -> TurnRecord | None:
        """Busca 1 turno por `turn_id`; `None` se nao existir."""
        with self._engine.connect() as conn:
            row = conn.execute(
                select(turns_table).where(turns_table.c.turn_id == turn_id)
            ).first()
        if row is None:
            return None
        return self._row_para_turn_record(row)


_session_store_instance: SessionStore | None = None
_session_store_db_path: str | None = None


def get_session_store(
    db_path: str | Path | None = None,
    *,
    session_ttl_s: int = 1800,
    max_premium_per_day: int = 100,
) -> SessionStore:
    """Retorna instancia singleton do `SessionStore`, criando schema se necessario.

    Args:
        db_path: Caminho do SQLite (se None, usa `/app/data/gateway.db`).
        session_ttl_s: TTL da sessao em segundos.
        max_premium_per_day: Teto diario de requests.
    """
    global _session_store_instance, _session_store_db_path
    resolved_path = str(db_path or "/app/data/gateway.db")
    if _session_store_instance is None or _session_store_db_path != resolved_path:
        Path(resolved_path).parent.mkdir(parents=True, exist_ok=True)
        _session_store_instance = SessionStore(
            resolved_path,
            session_ttl_s=session_ttl_s,
            max_premium_per_day=max_premium_per_day,
        )
        _session_store_db_path = resolved_path
    return _session_store_instance
