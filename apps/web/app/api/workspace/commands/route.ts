import { NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

/**
 * /api/workspace/commands — proxy server-side para `GET /v1/workspace/
 * commands` do gateway (picker `/` do composer, paridade com o picker de
 * slash commands/prompts do plugin Copilot da IDE -- pedido explicito do
 * usuario, 2026-10-02). `GATEWAY_API_KEY` nunca chega ao browser (mesmo
 * padrao de `app/api/workspace/agents/route.ts`).
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(): Promise<Response> {
  const env = getEnv();
  const resposta = await fetch(`${env.GATEWAY_BASE_URL}/v1/workspace/commands`, {
    headers: { Authorization: `Bearer ${env.GATEWAY_API_KEY}` },
    cache: "no-store",
  });
  const corpo = await resposta.text();
  return new NextResponse(corpo, {
    status: resposta.status,
    headers: { "content-type": "application/json" },
  });
}
