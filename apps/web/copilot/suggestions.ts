"use client";

import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

/**
 * useDeepAgentsSuggestions — sugestoes dinamicas de proxima mensagem.
 * `useConfigureSuggestions` e o hook v2 (substitui o `useCopilotChatSuggestions`
 * v1, antes importado de `@copilotkit/react-ui` — docs.copilotkit.ai/
 * reference/v2/hooks/useConfigureSuggestions).
 */
export function useDeepAgentsSuggestions() {
  useConfigureSuggestions({
    instructions:
      "Sugira ate 3 proximas perguntas curtas e uteis em portugues (Brasil), " +
      "relacionadas ao ultimo assunto discutido no repositorio deep-agents-copilot.",
    minSuggestions: 1,
    maxSuggestions: 3,
  });
}



