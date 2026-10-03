import type { CopilotChatLabels } from "@copilotkit/react-core/v2";

/**
 * LABELS_PT_BR — traducao completa dos textos padrao (em ingles) do widget
 * de chat do CopilotKit v2 (`CopilotChatDefaultLabels`), aplicada via prop
 * `labels` em `<CopilotChat>`/`<CopilotSidebar>` (docs.copilotkit.ai/
 * reference/v2/components). Mantido como `Partial<CopilotChatLabels>` —
 * qualquer chave nova adicionada pelo SDK cai de volta ao default em ingles
 * ate ser traduzida aqui.
 */
export const LABELS_PT_BR: Partial<CopilotChatLabels> = {
  chatInputPlaceholder: "Digite uma mensagem…",
  chatInputToolbarStartTranscribeButtonLabel: "Iniciar gravação de áudio",
  chatInputToolbarCancelTranscribeButtonLabel: "Cancelar gravação",
  chatInputToolbarFinishTranscribeButtonLabel: "Concluir gravação",
  chatInputToolbarAddButtonLabel: "Adicionar anexo",
  chatInputToolbarToolsButtonLabel: "Ferramentas",
  assistantMessageToolbarCopyCodeLabel: "Copiar código",
  assistantMessageToolbarCopyCodeCopiedLabel: "Código copiado",
  assistantMessageToolbarCopyMessageLabel: "Copiar mensagem",
  assistantMessageToolbarInspectorLabel: "Inspecionar",
  assistantMessageToolbarInspectorDescription: "Ver detalhes técnicos desta resposta",
  assistantMessageToolbarInspectorLocalOnlyLabel: "Somente local",
  assistantMessageToolbarInspectorLocalOnlyDescription:
    "Essas informações ficam apenas no seu navegador",
  assistantMessageToolbarInspectorTitle: "Detalhes da execução",
  assistantMessageToolbarInspectorHideLabel: "Ocultar",
  assistantMessageToolbarInspectorHideDescription: "Ocultar detalhes técnicos",
  assistantMessageToolbarThumbsUpLabel: "Boa resposta",
  assistantMessageToolbarThumbsDownLabel: "Resposta ruim",
  assistantMessageToolbarReadAloudLabel: "Ler em voz alta",
  assistantMessageToolbarRegenerateLabel: "Gerar novamente",
  userMessageToolbarCopyMessageLabel: "Copiar mensagem",
  userMessageToolbarEditMessageLabel: "Editar mensagem",
  chatDisclaimerText: "A IA pode cometer erros. Verifique informações importantes.",
  chatToggleOpenLabel: "Abrir chat",
  chatToggleCloseLabel: "Fechar chat",
  modalHeaderTitle: "Assistente",
  welcomeMessageText: "Como posso ajudar você hoje?",
};

