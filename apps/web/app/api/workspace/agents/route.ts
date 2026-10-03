import { NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

/**
 * /api/workspace/agents — proxy server-side para `GET /v1/workspace/agents`
 * do gateway (picker `@` do composer, paridade com a listagem de agents do
 * plugin Copilot da IDE). `GATEWAY_API_KEY` nunca chega ao browser (mesmo
 * padrao de `app/api/copilotkit/[[...path]]/route.ts`).
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(): Promise<Response> {
  const env = getEnv();
  const resposta = await fetch(`${env.GATEWAY_BASE_URL}/v1/workspace/agents`, {
    headers: { Authorization: `Bearer ${env.GATEWAY_API_KEY}` },
    cache: "no-store",
  });
  const corpo = await resposta.text();
  return new NextResponse(corpo, {
    status: resposta.status,
    headers: { "content-type": "application/json" },
  });
}

