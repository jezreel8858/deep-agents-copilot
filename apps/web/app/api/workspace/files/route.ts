import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

/**
 * /api/workspace/files — proxy server-side para `GET /v1/workspace/files`
 * do gateway (picker `#` do composer, paridade com "Select File, Folder or
 * Tool" do plugin Copilot da IDE). `GATEWAY_API_KEY` nunca chega ao browser
 * (mesmo padrao de `app/api/copilotkit/[[...path]]/route.ts`).
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: NextRequest): Promise<Response> {
  const env = getEnv();
  const q = request.nextUrl.searchParams.get("q") ?? "";
  const limit = request.nextUrl.searchParams.get("limit") ?? "30";

  const url = new URL(`${env.GATEWAY_BASE_URL}/v1/workspace/files`);
  if (q) url.searchParams.set("q", q);
  url.searchParams.set("limit", limit);

  const resposta = await fetch(url, {
    headers: { Authorization: `Bearer ${env.GATEWAY_API_KEY}` },
    cache: "no-store",
  });
  const corpo = await resposta.text();
  return new NextResponse(corpo, {
    status: resposta.status,
    headers: { "content-type": "application/json" },
  });
}

