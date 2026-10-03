"use client";

import { CopilotSidebar } from "@copilotkit/react-core/v2";
import { useWorkspaceStore } from "@/components/WorkspaceStoreContext";
import { LABELS_PT_BR } from "@/copilot/labels";

/**
 * /workspace — layout com `<CopilotSidebar>` + painel de notas do usuario
 * (demonstra `useAgentContext`/`useFrontendTool` lendo e escrevendo
 * `nota` — ver copilot/readables.ts e copilot/actions.tsx).
 * `labels={LABELS_PT_BR}` traduz os textos padrao do widget (ver copilot/labels.ts).
 * `attachments={{ enabled: true }}` habilita anexar imagens/arquivos no chat
 * (mesma config de `app/(chat)/page.tsx` — `CopilotSidebar` herda todas as
 * props de `CopilotChatProps`).
 */
export default function WorkspacePage() {
  const { nota, setNota } = useWorkspaceStore();

  return (
    <>
      <CopilotSidebar
        defaultOpen
        labels={LABELS_PT_BR}
        attachments={{ enabled: true }}
      />
      <div className="workspace-page">
        <h1>Espaço de Trabalho</h1>
        <p>
          Esta nota e compartilhada com o assistente via <code>useAgentContext</code>; peca para
          ele atualizar via a action <code>definirNotaDoWorkspace</code>.
        </p>
        <textarea
          value={nota}
          onChange={(e) => setNota(e.target.value)}
          rows={10}
          placeholder="Escreva uma nota de contexto para o assistente…"
        />
      </div>
    </>
  );
}





