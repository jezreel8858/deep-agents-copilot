"use client";

import { CopilotKit } from "@copilotkit/react-core/v2";
import { useEffect, useState } from "react";
import { obterOuCriarThreadAtiva } from "@/lib/threads";
import { AppShell } from "@/components/AppShell";
import { WorkspaceStoreProvider } from "@/components/WorkspaceStoreContext";
import { CopilotFeatures } from "@/components/CopilotFeatures";

/**
 * CopilotProviderShell — client component que resolve/cria a thread ativa
 * (persistida em localStorage, ver lib/threads.ts) e monta o provider
 * `<CopilotKit>` (API v2 — docs.copilotkit.ai/migrate/v2) apontando para a
 * API route local `/api/copilotkit`.
 *
 * `headers={{ "X-Thread-Id": threadId }}` e repassado pela API route ao
 * gateway como `X-Session-Id` (ver app/api/copilotkit/route.ts), permitindo
 * que a mesma conversa reaproveite a sessao de governanca multi-turno do
 * gateway mesmo com varias threads abertas em paralelo.
 *
 * `useSingleEndpoint={false}`: obrigatorio ao usar o handler v2
 * (`createCopilotRuntimeHandler`), que expoe multiplas rotas sob
 * `/api/copilotkit` em vez da rota unica do handler legado v1.
 */
export function CopilotProviderShell({ children }: { children: React.ReactNode }) {
  // Estado inicial SEMPRE null (igual no servidor e no 1o render do client)
  // para a hidratacao bater byte-a-byte. A lazy initializer anterior
  // (`useState(() => typeof window !== "undefined" ? ... : null)`) resolvia
  // o valor real JA no 1o render do client (window existe no browser mesmo
  // durante a hidratacao), divergindo do `null` renderizado no servidor —
  // bug real: "Hydration failed... AppShell (components/AppShell.tsx:20:5)"
  // com o servidor emitindo um placeholder `<script id="_R_">` e o client
  // emitindo `<div className="app-shell">` no mesmo slot.
  const [threadId, setThreadId] = useState<string | null>(null);

  // Leitura de localStorage (API exclusiva do browser) nao pode ser
  // calculada durante o render; o padrao "mounted flag" e a forma correta
  // de adiar o valor client-only para DEPOIS da hidratacao (1o render do
  // client bate com o SSR — ambos `null`; so este effect pos-montagem
  // atualiza o estado real, sem causar mismatch de hidratacao).
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- ver justificativa acima
    setThreadId(obterOuCriarThreadAtiva().id);
  }, []);


  if (!threadId) {
    return null;
  }

  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      threadId={threadId}
      headers={{ "X-Thread-Id": threadId }}
      useSingleEndpoint={false}
    >
      <WorkspaceStoreProvider>
        <CopilotFeatures />
        <AppShell>{children}</AppShell>
      </WorkspaceStoreProvider>
    </CopilotKit>
  );
}



