"use client";

import { createContext, useContext, useMemo, useState } from "react";

interface WorkspaceStoreValue {
  nota: string;
  setNota: (valor: string) => void;
}

const WorkspaceStoreContext = createContext<WorkspaceStoreValue | null>(null);

/**
 * WorkspaceStoreProvider — estado local minimo (sem persistencia) usado
 * como exemplo de `useCopilotReadable` (contexto compartilhado com o
 * assistente) e `useCopilotAction` (o assistente pode alterar a nota).
 */
export function WorkspaceStoreProvider({ children }: { children: React.ReactNode }) {
  const [nota, setNota] = useState("");
  const value = useMemo(() => ({ nota, setNota }), [nota]);
  return <WorkspaceStoreContext.Provider value={value}>{children}</WorkspaceStoreContext.Provider>;
}

export function useWorkspaceStore(): WorkspaceStoreValue {
  const ctx = useContext(WorkspaceStoreContext);
  if (!ctx) {
    throw new Error("useWorkspaceStore deve ser usado dentro de WorkspaceStoreProvider");
  }
  return ctx;
}

