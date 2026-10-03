import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/env";

const COOKIE_NAME = "lcw_session";

/**
 * POST /api/login — valida o WEB_ACCESS_CODE e grava um cookie HttpOnly
 * (substitui o ACCESS_CODE do Lobe Chat). Nunca expoe o codigo esperado ao
 * cliente; compara em memoria do servidor.
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  const env = getEnv();
  const body = (await request.json().catch(() => null)) as { codigo?: string } | null;
  const codigo = body?.codigo ?? "";

  if (codigo !== env.WEB_ACCESS_CODE) {
    return NextResponse.json({ ok: false, erro: "Codigo de acesso invalido" }, { status: 401 });
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set(COOKIE_NAME, "ok", {
    httpOnly: true,
    sameSite: "strict",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}

