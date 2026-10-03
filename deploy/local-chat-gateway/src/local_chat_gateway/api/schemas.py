"""schemas — Pydantic v2, espelhando o contrato OpenAI da Secao 4 do blueprint.

`ChatMessage`, `ChatCompletionRequest`, `ChatCompletion`,
`ChatCompletionChunk`, `Error` (6 subtipos), alem de `Model`/`ModelList`
para `GET /v1/models`.
"""

from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, Field

_MODEL_ID: Final[Literal["deep-agents/router"]] = "deep-agents/router"

# "developer" aceito por compatibilidade com o OpenAIAdapter do CopilotKit
# (`keepSystemRole: false` reescreve "system" -> "developer"); tratado pelo
# gateway como sinonimo de "system" (ver routes.py / governance_pipeline).
ChatRole = Literal["system", "developer", "user", "assistant", "tool"]
FinishReason = Literal["stop", "length", "tool_calls", "content_filter"]

ErrorType = Literal[
    "authentication_error",
    "invalid_request_error",
    "rate_limit_error",
    "governance_error",
    "timeout_error",
    "server_error",
]


class ToolCallFunction(BaseModel):
    """Corpo `function` de uma `ToolCall` (nome + argumentos serializados em JSON)."""

    name: str
    arguments: str = "{}"


class ToolCall(BaseModel):
    """Uma chamada de tool solicitada pelo modelo (mensagens `assistant`)."""

    id: str
    type: Literal["function"] = "function"
    function: ToolCallFunction


class ToolFunctionSpec(BaseModel):
    """Especificacao de uma funcao exposta como tool (`tools[].function`)."""

    name: str
    description: str | None = None
    parameters: dict[str, object] | None = None


class ToolSpec(BaseModel):
    """Uma tool anunciada pelo cliente (`ChatCompletionRequest.tools[]`).

    Aceita pelo gateway para evitar `422` em requests do CopilotKit
    (`useCopilotAction`); o repasse real ao SDK do Copilot (invocacao
    efetiva da tool do lado do cliente) e trabalho de fase futura (B3 do
    blueprint de migracao LobeChat -> CopilotKit).
    """

    type: Literal["function"] = "function"
    function: ToolFunctionSpec


class ChatMessage(BaseModel):
    """Uma mensagem do historico de chat (formato OpenAI Chat Completions).

    `content` e opcional para suportar mensagens `assistant` com apenas
    `tool_calls` (sem texto) e mensagens `tool` (resultado de uma tool),
    que exigem `tool_call_id`.
    """

    role: ChatRole
    content: str | None = None
    name: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None


class ChatCompletionRequest(BaseModel):
    """Corpo de `POST /v1/chat/completions`."""

    model: Literal["deep-agents/router"] = _MODEL_ID
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    # Aceitos para compatibilidade com o OpenAIAdapter do CopilotKit
    # (useCopilotAction/generative UI). Nao-escopo desta fase: o gateway
    # ainda nao repassa `tools` ao SDK real nem emite `tool_calls` de volta
    # (ver event_mapper.py / sdk_session.py — fase futura B3).
    tools: list[ToolSpec] | None = None
    tool_choice: str | dict[str, object] | None = None
    parallel_tool_calls: bool | None = None


class Usage(BaseModel):
    """Contagem de tokens de uma resposta nao-streaming."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionChoice(BaseModel):
    """Uma escolha (choice) de uma resposta `ChatCompletion` nao-streaming."""

    index: int
    message: ChatMessage
    finish_reason: FinishReason | None = None


class ChatCompletion(BaseModel):
    """Resposta nao-streaming de `POST /v1/chat/completions`."""

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: Usage | None = None


class ChatCompletionChunkDelta(BaseModel):
    """Delta incremental de um chunk de streaming SSE."""

    role: Literal["assistant"] | None = None
    content: str | None = None
    # Reservado para repasse futuro de tool_calls incrementais (B3 do
    # blueprint de migracao LobeChat -> CopilotKit); nao emitido nesta fase.
    tool_calls: list[ToolCall] | None = None


class ChatCompletionChunkChoice(BaseModel):
    """Uma escolha (choice) de um chunk de streaming."""

    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: FinishReason | None = None


class ChatCompletionChunk(BaseModel):
    """Um chunk `data:` do streaming SSE de `POST /v1/chat/completions`."""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice]


class ErrorDetail(BaseModel):
    """Corpo do campo `error` do envelope de erro OpenAI-compatible."""

    message: str
    type: ErrorType
    code: str | None = None


class Error(BaseModel):
    """Envelope de erro OpenAI-compatible (`{"error": {...}}`)."""

    error: ErrorDetail


class Model(BaseModel):
    """Um modelo exposto por `GET /v1/models` — sempre `deep-agents/router` (R-037)."""

    id: Literal["deep-agents/router"] = _MODEL_ID
    object: Literal["model"] = "model"
    owned_by: str = Field(default="deep-agents")


class ModelList(BaseModel):
    """Corpo de resposta de `GET /v1/models`."""

    object: Literal["list"] = "list"
    data: list[Model]


class WorkspaceFileItem(BaseModel):
    """1 arquivo descoberto pelo picker `#` do composer (paridade com a IDE)."""

    path: str
    project: str
    name: str


class WorkspaceFilesResponse(BaseModel):
    """Corpo de resposta de `GET /v1/workspace/files`."""

    files: list[WorkspaceFileItem]
    truncated: bool = False


class AgentCatalogItem(BaseModel):
    """1 custom agent descoberto pelo picker `@` do composer (paridade com a IDE)."""

    name: str
    display_name: str | None = None
    description: str | None = None


class AgentCatalogResponse(BaseModel):
    """Corpo de resposta de `GET /v1/workspace/agents`."""

    agents: list[AgentCatalogItem]

class CommandCatalogItem(BaseModel):
    """1 prompt ou skill descoberto pelo picker `/` do composer (paridade com a IDE)."""

    name: str
    kind: Literal["prompt", "skill"]
    description: str | None = None


class CommandCatalogResponse(BaseModel):
    """Corpo de resposta de `GET /v1/workspace/commands`."""

    commands: list[CommandCatalogItem]
