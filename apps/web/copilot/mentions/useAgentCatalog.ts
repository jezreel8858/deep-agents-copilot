"use client";

import { useEffect, useState } from "react";

export type AgenteCatalogo = {
  name: string;
  display_name: string | null;
  description: string | null;
};

/**
 * useAgentCatalog — carrega 1 unica vez (por montagem do composer) o
 * catalogo de custom agents via `/api/workspace/agents` (proxy -> gateway
 * `/v1/workspace/agents`, mesma fonte usada por `custom_agents=` no SDK real
 * -- ver `agent_catalog.py`), para o picker `@` do composer. Catalogo tem
 * ordem de grandeza de ~100 agents -- filtragem por substring e feita no
 * client (`MentionTextArea`), sem necessidade de busca incremental no
 * servidor como em `useWorkspaceFiles`.
 */
export function useAgentCatalog() {
  const [agentes, setAgentes] = useState<AgenteCatalogo[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let cancelado = false;
    (async () => {
      try {
        const resposta = await fetch("/api/workspace/agents", { cache: "no-store" });
        if (!resposta.ok) return;
        const dados = (await resposta.json()) as { agents: AgenteCatalogo[] };
        if (!cancelado) setAgentes(dados.agents ?? []);
      } catch {
        if (!cancelado) setAgentes([]);
      } finally {
        if (!cancelado) setCarregando(false);
      }
    })();
    return () => {
      cancelado = true;
    };
  }, []);

  return { agentes, carregando };
}

