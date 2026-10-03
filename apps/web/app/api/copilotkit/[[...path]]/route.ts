import {
  CopilotRuntime,
  createCopilotRuntimeHandler,
} from "@copilotkit/runtime/v2";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";
import { getEnv } from "@/lib/env";
import { sanitizeThreadId } from "@/lib/session";

// Execucoes de agent/tools podem levar ate GATEWAY_REQUEST_TIMEOUT_S (300s
// no gateway); alinhar o teto desta rota evita corte prematuro do stream.
export const maxDuration = 300;
export const runtime = "nodejs";
// Handlers GET/POST/PATCH/DELETE abaixo nao podem ser pre-renderizados
// estaticamente (dependem de headers por requisicao).
export const dynamic = "force-dynamic";

/**
 * /api/copilotkit/[[...path]] — hospeda o `CopilotRuntime` (API v2 —
 * "Migrate from v1 to v2", docs.copilotkit.ai/migrate/v2) usando `HttpAgent`
 * (`@ag-ui/client`) apontando DIRETO para o endpoint AG-UI nativo do gateway
 * (`POST /v2/agent`, `local_chat_gateway.api.routes.agui_run`) -- Fase 2
 * (2026-10-01), substitui o `BuiltInAgent` + provider OpenAI-compatible
 * (`@ai-sdk/openai`) usado ate entao.
 *
 * Motivo da troca (paridade visual com o plugin Copilot da IDE): o
 * `BuiltInAgent` consumia `/v1/chat/completions` (texto puro, OpenAI-
 * compativel) e o gateway tinha que ACHATAR eventos ricos do SDK (subagent,
 * tool call) em markdown dentro do texto (`"> 🧭 Subagent invocado: ..."`),
 * que o CopilotKit so conseguia renderizar como texto literal no balao do
 * chat -- divergente da UI nativa da IDE (cards de subagent, tool calls
 * estruturados). O novo endpoint `/v2/agent` fala o protocolo AG-UI NATIVO
 * (`RunStartedEvent`/`TextMessageStart|Content|EndEvent`/
 * `ToolCallStart|End|ResultEvent`/`SubagentStarted|Finished|ErrorEvent` --
 * AG-UI 1.0, docs.ag-ui.com) -- o CopilotKit entende esses eventos
 * NATIVAMENTE e renderiza subagent como card proprio (AG-UI 1.0 "subagent
 * support") sem renderer customizado (docs.copilotkit.ai/backend/ag-ui,
 * "Connecting to an AG-UI agent directly" / "Path 3: Your own backend").
 *
 * `BuiltInAgent` NAO suporta Human-in-the-Loop Interrupts (confirmado em
 * docs.copilotkit.ai/human-in-the-loop: "Not supported on CopilotKit's
 * Built-in Agent") -- outro motivo estrutural para a troca, alem de
 * paridade visual (a Fase 3 futura de `ask_questions` real via
 * `useHumanInTheLoop` so e possivel com esta arquitetura).
 *
 * Rota catch-all opcional (`[[...path]]`): o handler v2 (`mode:
 * "multi-route"`, default) despacha para subcaminhos como `GET /info`,
 * `POST /agent/:agentId/run` etc. sob `basePath` — um `route.ts` de match
 * exato (sem segmento dinamico) so responde a `/api/copilotkit` em si e
 * devolve 404 para todo o resto.
 *
 * O runtime/agent e construido POR REQUISICAO (nao em module scope): permite
 * repassar `X-Thread-Id`/`Authorization` por turno ao `HttpAgent` (a chave
 * do gateway, `GATEWAY_API_KEY`, so existe neste processo servidor — nunca
 * chega ao browser).
 */
function construirHandler(request: NextRequest) {
  const env = getEnv();
  const threadId = sanitizeThreadId(request.headers.get("x-thread-id"));

  const agent = new HttpAgent({
    url: `${env.GATEWAY_BASE_URL}/v2/agent`,
    headers: {
      Authorization: `Bearer ${env.GATEWAY_API_KEY}`,
      ...(threadId ? { "X-Thread-Id": threadId } : {}),
    },
  });

  const copilotRuntime = new CopilotRuntime({
    agents: {
      // Registrado como "default": componentes prontos (CopilotChat/
      // CopilotSidebar/CopilotPopup) o usam automaticamente sem precisar
      // de `agentId` explicito no frontend.
      default: agent,
    },
  });

  return createCopilotRuntimeHandler({
    runtime: copilotRuntime,
    basePath: "/api/copilotkit",
  });
}

async function handleRequest(request: NextRequest): Promise<Response> {
  const handler = construirHandler(request);
  return handler(request);
}

export const GET = handleRequest;
export const POST = handleRequest;
export const PATCH = handleRequest;
export const DELETE = handleRequest;


