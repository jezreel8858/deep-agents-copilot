"use client";

import { useAgent } from "@copilotkit/react-core/v2";
import { useEffect, useState } from "react";
import Form from "@rjsf/core";
import validator from "@rjsf/validator-ajv8";
import type { RJSFSchema } from "@rjsf/utils";
import { jaFoiTratado, marcarComoTratado } from "@/copilot/respondedRequests";

/**
 * ElicitationBridge — renderiza a elicitation MCP nativa (ex.: tool
 * `ask_questions`) como um formulario real, usando `react-jsonschema-form`
 * (RJSF) diretamente sobre o `requested_schema` (JSON Schema) recebido do
 * gateway — ZERO logica de traducao: o schema emitido pelo SDK do Copilot
 * (`UIElicitationSchema`, ver `sdk_session.py` RT-05) JA E JSON Schema
 * padrao (`enum`+`enumNames`, `oneOf` com `const`/`title`, arrays com
 * `items.enum` para multi-select, `minItems`/`maxItems`, `format`,
 * `minLength`/`maxLength`, `minimum`/`maximum`) -- exatamente o que o RJSF
 * consome nativamente.
 *
 * Por que NAO usar `useHumanInTheLoop`/`useInterrupt` (CopilotKit v2) aqui:
 * ambos assumem que resolver a pausa dispara uma NOVA chamada ao backend
 * (`RunAgentInput.resume`/continuacao do tool-call) para RETOMAR o agente —
 * modelo valido para backends com checkpoint externo (LangGraph etc.). O
 * Deep Agents Gateway envolve 1 sessao real do Copilot CLI por request
 * HTTP; a UNICA forma suportada pelo SDK de responder uma elicitation
 * pendente e MANTER o mesmo processo/stream vivo e resolver um
 * `asyncio.Future` em processo (ver `sdk_session._bridge_elicitacao`,
 * RT-05) -- por isso este componente ouve o `CustomEvent` bruto via
 * `agent.subscribe({ onCustomEvent })` e responde via um endpoint HTTP
 * dedicado (`/api/elicitation/[requestId]`), SEM iniciar um novo turno de
 * chat.
 */

interface ElicitationPendente {
  requestId: string;
  message: string;
  schema: RJSFSchema;
}

type AcaoElicitacao = "accept" | "decline" | "cancel";

async function responderElicitacao(
  requestId: string,
  acao: AcaoElicitacao,
  content?: Record<string, unknown>
): Promise<boolean> {
  try {
    const resposta = await fetch(`/api/elicitation/${encodeURIComponent(requestId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: acao, content: content ?? null }),
    });
    return resposta.ok;
  } catch {
    return false;
  }
}

// Bug real corrigido (2026-10-02, mesma classe de problema de
// `AskUserBridge`): a resposta HTTP nunca era checada -- um 404 (pergunta
// expirada/gateway reiniciado em modo dev apos edicao de codigo sob
// `src/`, que derruba o `asyncio.Future` em memoria) fechava o modal
// silenciosamente, deixando o chat parado sem feedback.
const MENSAGEM_ERRO_ENVIO =
  "Não foi possível entregar sua resposta ao agente (a pergunta expirou ou o gateway foi reiniciado — comum em modo dev após uma edição de código). Envie sua mensagem novamente no chat para retomar.";

export function ElicitationBridge() {
  const { agent } = useAgent();
  const [pendente, setPendente] = useState<ElicitationPendente | null>(null);
  const [expirada, setExpirada] = useState(false);
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    const { unsubscribe } = agent.subscribe({
      onCustomEvent: ({ event }) => {
        if (event.name === "elicitation_requested") {
          const valor = event.value as {
            request_id: string;
            message: string;
            requested_schema: RJSFSchema;
          };
          // Ignora replay de uma elicitation ja respondida/fechada neste
          // browser (ver `respondedRequests.ts`) -- corrige bug real:
          // apos `reload` da pagina, o historico da thread e reidratado e
          // `onCustomEvent` recebe de novo o `*_requested` original.
          if (jaFoiTratado(valor.request_id)) return;
          setExpirada(false);
          setErroEnvio(null);
          setPendente({
            requestId: valor.request_id,
            message: valor.message,
            schema: valor.requested_schema,
          });
        } else if (event.name === "elicitation_expired") {
          const valor = event.value as { request_id: string };
          setPendente((atual) =>
            atual?.requestId === valor.request_id ? null : atual
          );
          setExpirada(true);
        }
        // "elicitation_heartbeat": nenhuma acao de UI — apenas mantem o
        // stream SSE vivo no loop consumidor do gateway (ver sdk_session.py).
      },
    });
    return unsubscribe;
  }, [agent]);

  if (!pendente) {
    if (erroEnvio) {
      return (
        <div className="elicitation-bridge__expirada" role="alert">
          ⚠️ {erroEnvio}{" "}
          <button type="button" onClick={() => setErroEnvio(null)}>
            Dispensar
          </button>
        </div>
      );
    }
    return expirada ? (
      <div className="elicitation-bridge__expirada" role="status">
        ⏱️ A pergunta anterior expirou sem resposta.
      </div>
    ) : null;
  }

  const handleCancelar = async () => {
    setEnviando(true);
    marcarComoTratado(pendente.requestId);
    // Falha de entrega aqui NAO precisa de banner de erro -- o usuario ja
    // optou por nao continuar aguardando resposta.
    await responderElicitacao(pendente.requestId, "decline");
    setPendente(null);
    setEnviando(false);
  };

  return (
    <div className="elicitation-bridge__overlay" role="dialog" aria-modal="true">
      <div className="elicitation-bridge__card">
        <button
          type="button"
          className="elicitation-bridge__fechar"
          aria-label="Fechar sem responder"
          title="Fechar sem responder"
          disabled={enviando}
          onClick={handleCancelar}
        >
          ✕
        </button>
        <p className="elicitation-bridge__message">{pendente.message}</p>
        <Form
          schema={pendente.schema}
          validator={validator}
          disabled={enviando}
          onSubmit={async ({ formData }) => {
            setEnviando(true);
            marcarComoTratado(pendente.requestId);
            const entregue = await responderElicitacao(
              pendente.requestId,
              "accept",
              formData as Record<string, unknown>
            );
            setPendente(null);
            setEnviando(false);
            if (!entregue) setErroEnvio(MENSAGEM_ERRO_ENVIO);
          }}
        >
          <div className="elicitation-bridge__actions">
            <button type="submit" disabled={enviando}>
              {enviando ? "Enviando…" : "Responder"}
            </button>
            <button type="button" disabled={enviando} onClick={handleCancelar}>
              Cancelar
            </button>
          </div>
        </Form>
      </div>
    </div>
  );
}

