import { NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

export const dynamic = "force-dynamic";

/**
 * GET /api/healthz — usado pelo healthcheck do Docker (docker-compose.yml,
 * servico `web`). NAO exige sessao (rota publica no middleware). Faz um
 * probe raso ao `/healthz` do gateway para refletir o status upstream.
 */
export async function GET(): Promise<NextResponse> {
  try {
    const env = getEnv();
    const resposta = await fetch(`${env.GATEWAY_BASE_URL}/healthz`, {
      signal: AbortSignal.timeout(3000),
    });
    return NextResponse.json(
      { status: "ok", gateway: resposta.ok ? "ok" : "down" },
      { status: resposta.ok ? 200 : 503 }
    );
  } catch {
    return NextResponse.json({ status: "ok", gateway: "down" }, { status: 503 });
  }
}

