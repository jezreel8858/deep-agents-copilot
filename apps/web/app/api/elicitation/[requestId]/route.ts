import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * /api/elicitation/[requestId] — proxy server-side para
 * `POST /v1/elicitation/{request_id}/respond` no gateway (ver
 * `local_chat_gateway.api.routes.elicitation_respond`).
 *
 * Mesmo padrao de autenticacao de `app/api/copilotkit/[[...path]]/route.ts`
 * (`GATEWAY_API_KEY` injetada aqui, no servidor — nunca chega ao browser).
 * NAO passa pelo `CopilotRuntime`/`HttpAgent`: esta e uma ponte DIRETA e
 * deliberadamente simples, pois resolve uma elicitation MCP pendente (ex.:
 * `ask_questions`) dentro do MESMO stream AG-UI ja aberto no browser — nao
 * inicia um novo turno/run (ver `copilot/ElicitationBridge.tsx` e a nota de
 * modulo em `sdk_session.stream_chat_ag_ui`, RT-05).
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ requestId: string }> }
): Promise<NextResponse> {
  const { requestId } = await params;
  const env = getEnv();
  const body = await request.text();

  const resposta = await fetch(
    `${env.GATEWAY_BASE_URL}/v1/elicitation/${encodeURIComponent(requestId)}/respond`,
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
