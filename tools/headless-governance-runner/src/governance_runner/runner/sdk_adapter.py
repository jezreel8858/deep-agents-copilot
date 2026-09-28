"""
sdk_adapter — Adaptador do Copilot SDK: sessão, custom tool `delegar()` e
permission handler read-only para o caso de uso `agent-audit`.

Contrato (BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.2 / §9 RK-01, RK-05):
este módulo NUNCA importa o pacote real do Copilot SDK no escopo do módulo
(top-level) — o import é feito de forma tardia (lazy) dentro de
`criar_cliente_sdk_real`, permitindo que testes injetem um dublê/mock de
`CopilotSDKClient` sem que o SDK real esteja instalado.

Permission handler read-only (RK-05 — prompt injection): nega
categoricamente qualquer tool de escrita, shell ou rede; permite apenas
leitura de arquivos dentro do escopo do diff auditado e a tool customizada
`delegar()`.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, Sequence

from governance_runner.routing.handoff import HandoffPayloadInvalidoError, validar_handoff
from governance_runner.routing.model import DecisaoRota, HandoffPayload

__all__ = [
    "SDKRequest",
    "SDKResponse",
    "CopilotSDKClient",
    "SDKAuthenticationError",
    "PermissaoDecisao",
    "DelegacaoResultado",
    "DelegacaoNaoAutorizadaError",
    "criar_delegar_tool",
    "construir_permission_handler_read_only",
    "criar_cliente_sdk_real",
]

# Timeout de segurança para uma sessão do Copilot SDK real (evita hang
# indefinido em CI caso o evento `SessionIdleData` nunca seja emitido —
# API confirmada via @deep-search, mas sem SLA documentado de latência).
_TIMEOUT_SESSAO_SEGUNDOS = 120.0

# Marcadores textuais de falha de autenticação (401/403/token invalido).
# Fallback pragmático: a API real ainda não expõe (confirmado via
# @deep-search) uma classe de exceção dedicada para 401/403 no SDK Python.
_MARCADORES_ERRO_AUTENTICACAO: tuple[str, ...] = (
    "401",
    "403",
    "unauthorized",
    "forbidden",
    "invalid token",
    "invalid_token",
    "authentication",
    "expired",
)


def _parece_erro_autenticacao(exc: BaseException) -> bool:
    """Heurística textual para classificar uma exceção do SDK como falha de autenticação."""
    texto = str(exc).lower()
    return any(marcador in texto for marcador in _MARCADORES_ERRO_AUTENTICACAO)


class SDKAuthenticationError(Exception):
    """Levantada quando a autenticação do Copilot SDK falha (401/403/token expirado)."""


# Nomes de tools categoricamente negados no permission handler read-only
# (RK-05): qualquer escrita em disco, execução de shell ou acesso de rede.
_PREFIXOS_TOOLS_NEGADAS: tuple[str, ...] = (
    "write_",
    "edit_",
    "create_",
    "delete_",
    "shell",
    "run_",
    "exec_",
    "network_",
    "http_",
    "fetch_",
    "subprocess",
    "escrever_",
    "gravar_",
    "criar_",
    "apagar_",
    "deletar_",
    "executar_",
)

_TOOLS_LEITURA_PERMITIDAS: tuple[str, ...] = (
    "read_file",
    "ler_arquivo",
    "grep_search",
    "list_dir",
    "file_search",
)


@dataclass(frozen=True)
class PermissaoDecisao:
    """Decisão binária do permission handler para uma chamada de tool."""

    permitido: bool
    motivo: str


@dataclass(frozen=True)
class SDKRequest:
    """Requisição enviada à sessão do Copilot SDK para um caso de uso do runner."""

    prompt: str
    ferramentas_permitidas: tuple[str, ...]
    permission_handler: Callable[[str, Mapping[str, Any]], PermissaoDecisao]
    modelo: str | None = None


@dataclass(frozen=True)
class SDKResponse:
    """Resposta estruturada da sessão do Copilot SDK.

    `achados` segue o contrato de item de achado descrito em
    BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md §5.4:
    `{arquivo, linha, regra, severidade, mensagem}`.
    """

    achados: tuple[dict[str, Any], ...]
    premium_requests_consumidos: int
    turnos_consumidos: int = 1


class CopilotSDKClient(Protocol):
    """Porta (Protocol) do cliente do Copilot SDK — permite injeção de dublê/mock.

    Nenhuma implementação real do SDK é importada por este módulo; apenas o
    contrato estrutural. A implementação real deve ser obtida via
    `criar_cliente_sdk_real` (import tardio) e nunca no topo do módulo
    (RK-01 — vendor lock-in / testabilidade sem o pacote instalado).
    """

    def invoke(self, request: SDKRequest) -> SDKResponse:
        """Invoca a sessão do SDK com a requisição informada e retorna a resposta estruturada."""
        ...


@dataclass(frozen=True)
class DelegacaoResultado:
    """Resultado de uma delegação aceita pela tool customizada `delegar()`."""

    para: str
    payload: HandoffPayload


class DelegacaoNaoAutorizadaError(Exception):
    """Levantada quando `delegar()` recebe um destino fora dos candidatos da `DecisaoRota`."""


def criar_delegar_tool(
    decisao: DecisaoRota,
) -> Callable[[str, Mapping[str, Any]], DelegacaoResultado]:
    """Cria a tool customizada `delegar(para, payload)`, restrita aos candidatos de `decisao`.

    Integra com `governance_runner.routing`: o destino só é aceito se
    pertencer aos candidatos (ou ao escolhido) da `DecisaoRota` produzida por
    `rotear()`, e o payload é validado por `routing.handoff.validar_handoff`
    (contrato normativo `handoff-governance/SKILL.md`).

    Args:
        decisao: Decisão de roteamento previamente calculada por `rotear()`.

    Returns:
        Callable que implementa a tool `delegar`.
    """
    destinos_validos = {decisao.escolhido}

    def delegar(para: str, payload: Mapping[str, Any]) -> DelegacaoResultado:
        if para not in destinos_validos:
            raise DelegacaoNaoAutorizadaError(
                f"destino '{para}' nao pertence aos candidatos da DecisaoRota: {sorted(destinos_validos)}"
            )
        handoff_validado = validar_handoff(dict(payload))
        return DelegacaoResultado(para=para, payload=handoff_validado)

    return delegar


def construir_permission_handler_read_only(
    arquivos_em_escopo: Sequence[str],
) -> Callable[[str, Mapping[str, Any]], PermissaoDecisao]:
    """Constrói o permission handler read-only estrito do caso de uso `agent-audit`.

    Nega categoricamente qualquer tool de escrita/shell/rede (RK-05); permite
    apenas leitura de arquivos pertencentes a `arquivos_em_escopo` (o diff
    auditado) e a tool customizada `delegar`.

    Args:
        arquivos_em_escopo: Caminhos (relativos ao repositório) dos arquivos
            do diff auditado — únicos alvos de leitura permitidos.

    Returns:
        Callable(tool_name, parametros) -> PermissaoDecisao.
    """
    escopo = frozenset(arquivos_em_escopo)

    def handler(tool_name: str, parametros: Mapping[str, Any]) -> PermissaoDecisao:
        nome_normalizado = tool_name.lower()

        if nome_normalizado == "delegar":
            return PermissaoDecisao(True, "tool de delegacao permitida (read-only)")

        if any(nome_normalizado.startswith(prefixo) for prefixo in _PREFIXOS_TOOLS_NEGADAS):
            return PermissaoDecisao(False, "tool de escrita/shell/rede negada em agent-audit (read-only)")

        if nome_normalizado in _TOOLS_LEITURA_PERMITIDAS:
            caminho = str(parametros.get("path") or parametros.get("arquivo") or "")
            if caminho and escopo and caminho not in escopo:
                return PermissaoDecisao(False, f"arquivo '{caminho}' fora do escopo do diff auditado")
            return PermissaoDecisao(True, "leitura de arquivo em escopo permitida")

        return PermissaoDecisao(False, f"tool '{tool_name}' nao reconhecida/nao permitida em agent-audit")

    return handler


def criar_cliente_sdk_real(token: str, *, modelo: str | None = None) -> CopilotSDKClient:
    """Cria o cliente real do Copilot SDK (import tardio, RK-01/RK-06).

    API confirmada via @deep-search (github/copilot-sdk, pacote PyPI
    `github-copilot-sdk`, módulo importável `copilot`) nesta sessão —
    ver BLUEPRINT_COPILOT_SDK_HEADLESS_RUNNER.md, nota de pendencia de
    verificacao externa (agora resolvida).

    Args:
        token: Token de autenticação (`COPILOT_SDK_TOKEN`).
        modelo: Override opcional de modelo (menor multiplicador de custo).

    Raises:
        RuntimeError: Se o pacote do SDK não estiver instalado no extra
            `[sdk]` (mensagem descritiva, nunca falha silenciosa).
    """
    try:
        import copilot  # type: ignore[import-not-found]  # noqa: F401  (import tardio proposital)
    except ImportError as exc:  # pragma: no cover - depende de dependencia externa opcional
        raise RuntimeError(
            "Pacote do Copilot SDK nao instalado. Instale o extra "
            "'tools/headless-governance-runner[sdk]' ou injete um duble de "
            "CopilotSDKClient para testes locais."
        ) from exc

    return _ClienteSDKReal(token=token, modelo=modelo)


class _ClienteSDKReal:
    """Ponte síncrona (`CopilotSDKClient.invoke`) sobre a API assíncrona nativa
    do pacote `github-copilot-sdk` (`copilot.CopilotClient`).

    Escopo PoC (subtask 26): 1 sessão descartável por chamada `invoke()`,
    sem streaming, com timeout de segurança `_TIMEOUT_SESSAO_SEGUNDOS`.
    `premium_requests_consumidos` é aproximado como `1` por turno nesta
    fase — a API do SDK ainda não expõe (confirmado via @deep-search) um
    contador de uso/billing granular por resposta.
    """

    def __init__(self, token: str, *, modelo: str | None = None) -> None:
        self._token = token
        self._modelo = modelo

    def invoke(self, request: SDKRequest) -> SDKResponse:
        try:
            return asyncio.run(self._invoke_async(request))
        except SDKAuthenticationError:
            raise
        except Exception as exc:  # noqa: BLE001 - reclassifica ou repropaga
            if _parece_erro_autenticacao(exc):
                raise SDKAuthenticationError(str(exc)) from exc
            raise

    async def _invoke_async(self, request: SDKRequest) -> SDKResponse:
        import copilot
        from copilot.session_events import AssistantMessageData, SessionIdleData  # type: ignore[import-not-found]

        def _bridge_permissao(perm_request: Any, invocation: Mapping[str, Any]) -> dict[str, str]:
            tool_name = str(
                getattr(perm_request, "tool_name", None)
                or invocation.get("toolName")
                or invocation.get("tool_name")
                or ""
            )
            decisao = request.permission_handler(tool_name, dict(invocation))
            return {"permissionDecision": "allow" if decisao.permitido else "deny"}

        fragmentos_resposta: list[str] = []
        concluido = asyncio.Event()

        def _on_event(event: Any) -> None:
            dado = getattr(event, "data", None)
            if isinstance(dado, AssistantMessageData):
                fragmentos_resposta.append(str(dado.content))
            elif isinstance(dado, SessionIdleData):
                concluido.set()

        async with copilot.CopilotClient(github_token=self._token) as client:
            async with await client.create_session(
                on_permission_request=_bridge_permissao,
                model=request.modelo or self._modelo,
            ) as session:
                session.on(_on_event)
                await session.send(request.prompt)
                try:
                    await asyncio.wait_for(concluido.wait(), timeout=_TIMEOUT_SESSAO_SEGUNDOS)
                except asyncio.TimeoutError as exc:
                    raise RuntimeError(
                        f"Sessao do Copilot SDK nao concluiu em {_TIMEOUT_SESSAO_SEGUNDOS}s "
                        "(timeout de seguranca — possivel travamento de rede/runtime)."
                    ) from exc

        return SDKResponse(
            achados=_parsear_achados("\n".join(fragmentos_resposta)),
            premium_requests_consumidos=1,
            turnos_consumidos=1,
        )


def _parsear_achados(resposta_bruta: str) -> tuple[dict[str, Any], ...]:
    """Extrai achados estruturados da resposta textual do SDK (best-effort).

    Contrato esperado (BLUEPRINT §5.4): lista JSON de objetos
    `{arquivo, linha, regra, severidade, mensagem}`. Se a resposta não for
    JSON válido (agente não seguiu o formato solicitado no prompt), retorna
    um único achado informativo envolvendo o texto bruto — nunca lança
    exceção nem descarta silenciosamente o conteúdo da resposta.
    """
    texto = resposta_bruta.strip()
    if not texto:
        return ()
    try:
        dados = json.loads(texto)
    except (json.JSONDecodeError, ValueError):
        return (
            {
                "arquivo": "",
                "linha": None,
                "regra": "RESPOSTA_NAO_ESTRUTURADA",
                "severidade": "info",
                "mensagem": texto[:2000],
            },
        )
    if isinstance(dados, dict):
        dados = [dados]
    if not isinstance(dados, list):
        return ()
    return tuple(item for item in dados if isinstance(item, dict))

