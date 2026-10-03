"use client";

import { useAgentContext } from "@copilotkit/react-core/v2";

/**
 * useDeepAgentsInstructions — instrucoes adicionais injetadas no prompt do
 * assistente a partir do frontend. Migrado de `useCopilotAdditionalInstructions`
 * (v1) para `useAgentContext` (v2, docs.copilotkit.ai/migrate/v2).
 *
 * Ressalva documentada (GitHub Discussion #4791, CopilotKit/CopilotKit):
 * `useAgentContext` injeta DADOS/contexto no prompt, nao instrucoes
 * comportamentais rigidas (nao ha garantia de precedencia de system prompt
 * como no v1). Para regras de negocio obrigatorias (ex.: "sempre chamar a
 * tool X antes de responder"), mover para o system prompt do backend
 * (`governance_pipeline.montar_contexto`) em vez de depender deste hook.
 */
export function useDeepAgentsInstructions() {
  useAgentContext({
    description: "Instrucoes adicionais de estilo de resposta do assistente.",
    value:
      "Responda sempre em Portugues do Brasil. Quando sugerir codigo, " +
      "use blocos de codigo com a linguagem identificada.",
  });
}


