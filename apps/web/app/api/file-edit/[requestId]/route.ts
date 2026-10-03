import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * /api/file-edit/[requestId] — proxy server-side para
 * `POST /v1/file-edit/{request_id}/respond` no gateway (ver
 * `local_chat_gateway.api.routes.file_edit_respond`).
 *
 * Mesmo padrao de `app/api/elicitation/[requestId]/route.ts` e
 * `app/api/ask-user/[requestId]/route.ts`: ponte DIRETA (fora do
 * `CopilotRuntime`/`HttpAgent`) que resolve uma edicao de arquivo pendente
 * de aprovacao humana (diff visualizado em `copilot/FileEditBridge.tsx`)
 * dentro do MESMO stream AG-UI ja aberto no browser, sem iniciar um novo
 * turno/run (ver nota de modulo em `sdk_session.stream_chat_ag_ui`, bloco
 * `_bridge_edicao_arquivo`).
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ requestId: string }> }
): Promise<NextResponse> {
  const { requestId } = await params;
  const env = getEnv();
  const body = await request.text();

  const resposta = await fetch(
    `${env.GATEWAY_BASE_URL}/v1/file-edit/${encodeURIComponent(requestId)}/respond`,
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

