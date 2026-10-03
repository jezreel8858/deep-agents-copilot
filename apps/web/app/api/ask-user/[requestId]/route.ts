import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * /api/ask-user/[requestId] — proxy server-side para
 * `POST /v1/ask-user/{request_id}/respond` no gateway (ver
 * `local_chat_gateway.api.routes.ask_user_respond`).
 *
 * Mesmo padrao de `app/api/elicitation/[requestId]/route.ts`: ponte DIRETA
 * (fora do `CopilotRuntime`/`HttpAgent`) que resolve a pergunta `ask_user`
 * pendente dentro do MESMO stream AG-UI ja aberto no browser, sem iniciar
 * um novo turno/run (ver `copilot/AskUserBridge.tsx` e a nota de modulo em
 * `sdk_session.stream_chat_ag_ui`, RT-05).
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ requestId: string }> }
): Promise<NextResponse> {
  const { requestId } = await params;
  const env = getEnv();
  const body = await request.text();

  const resposta = await fetch(
    `${env.GATEWAY_BASE_URL}/v1/ask-user/${encodeURIComponent(requestId)}/respond`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${env.GATEWAY_API_KEY}`,
      },
      body,
    }
  );

  const texto = await resposta.text();
  return new NextResponse(texto, {
    status: resposta.status,
    headers: { "Content-Type": "application/json" },
  });
}

