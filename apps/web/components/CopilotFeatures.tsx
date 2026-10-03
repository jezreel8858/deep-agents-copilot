"use client";

import { useDeepAgentsActions } from "@/copilot/actions";
import { useDeepAgentsReadables } from "@/copilot/readables";
import { useDeepAgentsSuggestions } from "@/copilot/suggestions";
import { useDeepAgentsInstructions } from "@/copilot/instructions";
import { ElicitationBridge } from "@/copilot/ElicitationBridge";
import { AskUserBridge } from "@/copilot/AskUserBridge";
import { FileEditBridge } from "@/copilot/FileEditBridge";

/**
 * CopilotFeatures — componente "invisivel" (sem UI propria, exceto os
 * overlays condicionais de `AskUserBridge`/`ElicitationBridge`/
 * `FileEditBridge`) que registra todos os hooks
 * `useCopilotAction`/`useCopilotReadable`/`useCopilotChatSuggestions`/
 * `useCopilotAdditionalInstructions` dentro do provider `<CopilotKit>`.
 * Precisa estar DENTRO do provider (ver CopilotProviderShell) e DENTRO do
 * WorkspaceStoreProvider.
 *
 * `AskUserBridge` (mecanismo LEGADO `ask_user`, o que de fato funciona --
 * RT-05), `ElicitationBridge` (mecanismo MCP Elicitation generico, mantido
 * para compatibilidade futura) e `FileEditBridge` (diff de arquivo pendente
 * de aprovacao, pedido do usuario 2026-10-02) podem coexistir sem conflito:
 * cada um ouve um `CustomEvent` de nome distinto (`ask_user_requested` vs
 * `elicitation_requested` vs `file_edit_requested`).
 */
export function CopilotFeatures() {
  useDeepAgentsActions();
  useDeepAgentsReadables();
  useDeepAgentsSuggestions();
  useDeepAgentsInstructions();
  return (
    <>
      <AskUserBridge />
      <ElicitationBridge />
      <FileEditBridge />
    </>
  );
}

