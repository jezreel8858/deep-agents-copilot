"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";
import { LABELS_PT_BR } from "@/copilot/labels";
import { MentionChatInput } from "@/copilot/mentions/MentionChatInput";

/**
 * Pagina inicial — chat embutido em tela cheia (`<CopilotChat>`). Removido
 * o `<CopilotPopup>` que antes era renderizado junto (causava duas caixas
 * de chat simultaneas na mesma tela — bug visual real, 2026-10-01).
 * `labels={LABELS_PT_BR}` traduz os textos padrao (em ingles) do widget
 * (placeholder, disclaimer, tooltips etc. — ver copilot/labels.ts).
 * `attachments={{ enabled: true }}` habilita o botao de anexo + drag-and-drop
 * (imagens, PDFs, audio, video, documentos) no composer, com paridade ao
 * chat do Copilot na IDE -- CopilotKit v2 le cada arquivo como base64 e
 * monta o `content` multimodal AG-UI (`ImagePart`/`DocumentPart`/etc.),
 * repassado pelo gateway ao Copilot SDK via `session.send(attachments=...)`
 * (ver `routes._extrair_texto_e_anexos`/`sdk_session.stream_chat_ag_ui`).
 *
 * `input={MentionChatInput}` substitui o slot RAIZ `input` inteiro (ver
 * docs.copilotkit.ai/custom-look-and-feel/slots — "Available Slots") por
 * uma versao com picker `#` (arquivos do workspace) e `@` (agents
 * disponiveis) que renderiza as mencoes escolhidas como CHIPS removiveis
 * acima do campo de texto, paridade com o composer do plugin Copilot da
 * IDE (ver `copilot/mentions/MentionChatInput.tsx`).
 */
export default function ChatPage() {
  return (
    <div className="chat-page">
      <CopilotChat
        className="deep-agents-chat"
        labels={LABELS_PT_BR}
        attachments={{ enabled: true }}
        input={MentionChatInput}
      />
    </div>
  );
}



