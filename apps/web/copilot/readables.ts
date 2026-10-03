"use client";

import { usePathname } from "next/navigation";
import { useAgentContext } from "@copilotkit/react-core/v2";
import { useWorkspaceStore } from "@/components/WorkspaceStoreContext";

/**
 * useDeepAgentsReadables — expoe contexto compartilhado ao assistente via
 * `useAgentContext` (v2, substitui `useCopilotReadable` — docs.copilotkit.ai/
 * migrate/v2): rota atual e nota de workspace do usuario.
 */
export function useDeepAgentsReadables() {
  const pathname = usePathname();
  const { nota } = useWorkspaceStore();

  useAgentContext({
    description: "Rota/pagina atualmente aberta pelo usuario na aplicacao.",
    value: pathname,
  });

  useAgentContext({
    description: "Nota de contexto que o usuario escreveu no painel do workspace.",
    value: nota || "(vazio)",
  });
}



