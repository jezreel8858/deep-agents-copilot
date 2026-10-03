"use client";

import { useDefaultRenderTool, useFrontendTool, useHumanInTheLoop } from "@copilotkit/react-core/v2";
import { z } from "zod";
import { useWorkspaceStore } from "@/components/WorkspaceStoreContext";
import { rotularTool } from "@/copilot/toolLabels";

/**
 * useDeepAgentsActions — registra as tools/renderers v2 disponiveis ao
 * assistente nesta aplicacao (docs.copilotkit.ai/reference/v2/hooks).
 * Cada tool so e efetivamente *chamada* pelo modelo quando o gateway
 * repassar `tools` ao SDK e devolver `tool_calls` (fase futura do backend)
 * — o registro no frontend ja fica pronto para quando isso acontecer.
 */
/**
 * Valores triviais devolvidos por tools simples (ex.: `{ ok: true }` ou a
 * string "concluido") nao agregam nada ao usuario dentro de "detalhes" --
 * mostrar um `<details>` vazio/so-com-"concluido" e ruido puro. So exibe o
 * bloco de detalhes quando o resultado tiver conteudo realmente util.
 */
const TEXTOS_TRIVIAIS = new Set(["concluido", "concluído", "ok", "sucesso", "true", "done"]);

function resultadoEUtil(result: unknown): boolean {
  if (result === null || result === undefined) return false;
  if (typeof result === "string") {
    const normalizado = result.trim().toLowerCase();
    return normalizado.length > 0 && !TEXTOS_TRIVIAIS.has(normalizado);
  }
  if (typeof result === "boolean") return false;
  if (typeof result === "object") {
    const chaves = Object.keys(result as Record<string, unknown>);
    if (chaves.length === 0) return false;
    // `{ ok: true }` (unica chave "ok"/"status" booleana) tambem e trivial.
    return !(chaves.length === 1 && (chaves[0] === "ok" || chaves[0] === "status"));
  }
  return true;
}

export function useDeepAgentsActions() {
  const { setNota } = useWorkspaceStore();

  useFrontendTool({
    name: "mostrarNotificacao",
    description: "Exibe uma notificacao transiente para o usuario na UI.",
    parameters: z.object({
      mensagem: z.string().describe("Texto da notificacao"),
      tipo: z.enum(["info", "sucesso", "erro"]).optional(),
    }),
    handler: async ({ mensagem, tipo }) => {
      // MVP: sem sistema de toast proprio ainda; console.info e aceitavel aqui.
      console.info(`[notificacao:${tipo ?? "info"}] ${mensagem}`);
      return { ok: true };
    },
  });

  useFrontendTool({
    name: "copiarParaAreaDeTransferencia",
    description: "Copia um texto para a area de transferencia do usuario.",
    parameters: z.object({ texto: z.string() }),
    handler: async ({ texto }) => {
      await navigator.clipboard.writeText(texto);
      return { ok: true };
    },
  });

  useFrontendTool({
    name: "definirNotaDoWorkspace",
    description: "Atualiza a nota de contexto do workspace exibida na tela.",
    parameters: z.object({ conteudo: z.string() }),
    handler: async ({ conteudo }) => {
      setNota(conteudo);
      return { ok: true };
    },
  });

  useHumanInTheLoop({
    name: "confirmarAcao",
    description: "Pede confirmacao explicita do usuario antes de prosseguir com uma acao sensivel.",
    parameters: z.object({ pergunta: z.string() }),
    render: ({ args, status, respond }) => (
      <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: 12 }}>
        <p>{args.pergunta}</p>
        <div style={{ display: "flex", gap: 8 }}>
          <button disabled={status !== "executing"} onClick={() => respond?.("aprovado")}>
            Aprovar
          </button>
          <button disabled={status !== "executing"} onClick={() => respond?.("recusado")}>
            Recusar
          </button>
        </div>
      </div>
    ),
  });

  useDefaultRenderTool({
    // Rotulo amigavel (PT-BR) + icone por tool (`copilot/toolLabels.ts`) --
    // pesquisado em docs.copilotkit.ai/generative-ui/tool-rendering e
    // padrao de mercado (Cursor/Claude Code: verbo + alvo em vez do nome
    // tecnico cru da tool, ex.: "🔍 Procurando arquivos" em vez de "glob").
    // Layout em caixa (pouco arredondada, estilo "Tavily box" do plugin
    // Copilot na IDE) em vez do chip pill anterior -- o texto verboso de
    // status ("✓ concluído" / "⏳ em execução…") foi removido por ser
    // irrelevante (status ja e sinalizado pelo icone compacto + cor da
    // borda via `data-status`).
    render: ({ name, status, result }) => {
      const { icone, rotulo } = rotularTool(name);
      const concluido = status === "complete";
      const mostrarDetalhes = concluido && resultadoEUtil(result);
      return (
        <div className="tool-call-box" data-status={concluido ? "concluido" : "executando"}>
          <div className="tool-call-box__header">
            <span className="tool-call-box__icone" aria-hidden="true">
              {icone}
            </span>
            <span className="tool-call-box__rotulo">{rotulo}</span>
            <span className="tool-call-box__indicador" aria-hidden="true">
              {concluido ? "✓" : "⏳"}
            </span>
          </div>
          {mostrarDetalhes ? (
            <details className="tool-call-box__detalhes">
              <summary>detalhes</summary>
              <pre>{typeof result === "string" ? result : JSON.stringify(result, null, 2)}</pre>
            </details>
          ) : null}
        </div>
      );
    },
  });
}





