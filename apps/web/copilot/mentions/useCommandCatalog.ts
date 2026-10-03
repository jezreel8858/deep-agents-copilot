"use client";

import { useEffect, useState } from "react";

export type ComandoCatalogo = {
  name: string;
  kind: "prompt" | "skill";
  description: string | null;
};

/**
 * useCommandCatalog — carrega 1 unica vez (por montagem do composer) o
 * catalogo de prompts (`.github/prompts/*.prompt.md`) + skills
 * (`.github/skills/.../SKILL.md`) via `/api/workspace/commands` (proxy ->
 * gateway `/v1/workspace/commands`, ver `prompts_catalog.py`), para o
 * picker `/` do composer -- paridade com o picker de slash commands/
 * prompts do plugin Copilot da IDE (pedido explicito do usuario,
 * 2026-10-02). Mesmo padrao de `useAgentCatalog`: catalogo pequeno,
 * filtragem por substring feita no client (`MentionTextArea`).
 */
export function useCommandCatalog() {
  const [comandos, setComandos] = useState<ComandoCatalogo[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let cancelado = false;
    (async () => {
      try {
        const resposta = await fetch("/api/workspace/commands", { cache: "no-store" });
        if (!resposta.ok) return;
        const dados = (await resposta.json()) as { commands: ComandoCatalogo[] };
        if (!cancelado) setComandos(dados.commands ?? []);
      } catch {
        if (!cancelado) setComandos([]);
      } finally {
        if (!cancelado) setCarregando(false);
      }
    })();
    return () => {
      cancelado = true;
    };
  }, []);

  return { comandos, carregando };
}
