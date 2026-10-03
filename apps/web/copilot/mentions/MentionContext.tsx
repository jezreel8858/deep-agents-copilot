"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { MentionChip } from "./types";

type MentionContextValue = {
  onMention: (chip: MentionChip) => void;
};

const SEM_CONTEXTO: MentionContextValue = {
  // Fallback no-op -- evita crash se `MentionTextArea` for renderizado fora
  // de `MentionChatInput` (ex.: storybook isolado); apenas desabilita chips.
  onMention: () => {},
};

const MentionContext = createContext<MentionContextValue>(SEM_CONTEXTO);

/**
 * MentionProvider — ponte entre `MentionChatInput` (dono do estado de chips,
 * no slot `input` COMPLETO de `<CopilotChat>`) e `MentionTextArea` (sub-slot
 * `textArea`, varios niveis abaixo via o componente real `CopilotChatInput`).
 * Evita prop-drilling atraves do componente real do CopilotKit (que so
 * repassa `TextareaHTMLAttributes` puros ao slot `textArea`, sem espaco para
 * props customizadas) e mantem `MentionTextArea` como referencia ESTAVEL de
 * componente (sem recriar a cada render, o que quebraria foco/estado).
 */
export function MentionProvider({
  value,
  children,
}: {
  value: MentionContextValue;
  children: ReactNode;
}) {
  return <MentionContext.Provider value={value}>{children}</MentionContext.Provider>;
}

export function useMentionContext(): MentionContextValue {
  return useContext(MentionContext);
}

