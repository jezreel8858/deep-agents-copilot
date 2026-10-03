import { NextRequest, NextResponse } from "next/server";

/**
 * proxy — gate de acesso por WEB_ACCESS_CODE (substitui o ACCESS_CODE
 * do Lobe Chat). Protege toda rota exceto /login, /api/login e
 * /api/healthz (healthcheck do Docker nao pode exigir sessao).
 *
 * Renomeado de `middleware.ts` para `proxy.ts` (convencao do Next.js 16 —
 * `middleware` esta deprecado em favor de `proxy`). Exporta tambem
 * `middleware` como alias retrocompativel.
 */
const ROTAS_PUBLICAS = ["/login", "/api/login", "/api/healthz"];

const COOKIE_NAME = "lcw_session";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (ROTAS_PUBLICAS.some((rota) => pathname.startsWith(rota))) {
    return NextResponse.next();
  }

  const autenticado = request.cookies.get(COOKIE_NAME)?.value === "ok";
  if (!autenticado) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const middleware = proxy;

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};

