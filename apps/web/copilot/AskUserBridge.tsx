"use client";

import { useAgent } from "@copilotkit/react-core/v2";
import { useEffect, useState } from "react";
import { jaFoiTratado, marcarComoTratado } from "@/copilot/respondedRequests";

/**
 * AskUserBridge — renderiza a tool nativa `ask_user` (mecanismo LEGADO do
 * Copilot SDK, confirmado por teste isolado via sandbox como o UNICO que
 * efetivamente faz o modelo invocar a tool como function-call real -- ver
 * nota RT-05 em `sdk_session.stream_chat_ag_ui`) como uma UI simples de
 * pergunta + opcoes clicaveis + campo de texto livre opcional.
 *
 * Schema FIXO e muito mais simples que a elicitation MCP generica
 * (`ElicitationBridge.tsx`, que usa RJSF sobre JSON Schema arbitrario):
 * `{question: string, choices: string[], allow_freeform: boolean}` ->
 * `{answer: string, was_freeform: boolean}`. Por isso este componente usa
 * UI nativa (botoes) em vez de RJSF -- nao ha necessidade de um form
 * generico para 1 unica pergunta de escolha simples.
 *
 * Mesmo motivo arquitetural de `ElicitationBridge.tsx` para NAO usar
 * `useHumanInTheLoop`/`useInterrupt`: o gateway mantem a sessao do Copilot
 * CLI viva durante toda a pausa (sem "fim de run + resume"), respondendo
 * via endpoint HTTP dedicado (`/api/ask-user/[requestId]`) em vez do fluxo
 * padrao de tool-result-via-novo-turno do CopilotKit.
 */
interface PerguntaPendente {
  requestId: string;
  question: string;
  choices: string[];
  allowFreeform: boolean;
}

async function responderPergunta(
  requestId: string,
  answer: string,
  wasFreeform: boolean
): Promise<boolean> {
  try {
    const resposta = await fetch(`/api/ask-user/${encodeURIComponent(requestId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer, was_freeform: wasFreeform }),
    });
    return resposta.ok;
  } catch {
    // Falha de rede (gateway fora do ar/timeout) -- mesmo tratamento de
    // "nao entregue" que um 404 (ver `erroEnvio` em `AskUserBridge`).
    return false;
  }
}

// Bug real corrigido (2026-10-02): em modo dev (`dev_watch.py --reload`),
// qualquer edicao de arquivo sob `src/` reinicia o processo do gateway e
// descarta o `asyncio.Future` pendente em memoria (`_PERGUNTAS_PENDENTES`).
// `responderPergunta` passava a resposta via `fetch` mas NUNCA checava
// `response.ok` -- um 404 (`resolver_pergunta_usuario` retornando `False`
// porque o `request_id` nao existe mais) era silenciosamente ignorado: o
// modal fechava como se a resposta tivesse sido entregue, mas o agente
// nunca a recebia, deixando o chat parado sem nenhum feedback ao usuario.
const MENSAGEM_ERRO_ENVIO =
  "Não foi possível entregar sua resposta ao agente (a pergunta expirou ou o gateway foi reiniciado — comum em modo dev após uma edição de código). Envie sua mensagem novamente no chat para retomar.";

export function AskUserBridge() {
  const { agent } = useAgent();
  const [pendente, setPendente] = useState<PerguntaPendente | null>(null);
  const [expirada, setExpirada] = useState(false);
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const [textoLivre, setTextoLivre] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    const { unsubscribe } = agent.subscribe({
      onCustomEvent: ({ event }) => {
        if (event.name === "ask_user_requested") {
          const valor = event.value as {
            request_id: string;
            question: string;
            choices: string[];
            allow_freeform: boolean;
          };
          // Ignora replay de uma pergunta ja respondida/fechada neste
          // browser (ver `respondedRequests.ts`) -- corrige bug real:
          // apos `reload` da pagina, o historico da thread e reidratado e
          // `onCustomEvent` recebe de novo o `*_requested` original.
          if (jaFoiTratado(valor.request_id)) return;
          setExpirada(false);
          setErroEnvio(null);
          setTextoLivre("");
          setPendente({
            requestId: valor.request_id,
            question: valor.question,
            choices: valor.choices,
            allowFreeform: valor.allow_freeform,
          });
        } else if (event.name === "ask_user_expired") {
          const valor = event.value as { request_id: string };
          setPendente((atual) =>
            atual?.requestId === valor.request_id ? null : atual
          );
          setExpirada(true);
        }
        // "ask_user_heartbeat": nenhuma acao de UI.
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

  const escolher = async (opcao: string) => {
    setEnviando(true);
    marcarComoTratado(pendente.requestId);
    const entregue = await responderPergunta(pendente.requestId, opcao, false);
    setPendente(null);
    setEnviando(false);
    if (!entregue) setErroEnvio(MENSAGEM_ERRO_ENVIO);
  };

  const enviarLivre = async () => {
    if (!textoLivre.trim()) return;
    setEnviando(true);
    marcarComoTratado(pendente.requestId);
    const entregue = await responderPergunta(
      pendente.requestId,
      textoLivre.trim(),
      true
    );
    setPendente(null);
    setEnviando(false);
    if (!entregue) setErroEnvio(MENSAGEM_ERRO_ENVIO);
  };

  const fecharSemResponder = async () => {
    setEnviando(true);
    marcarComoTratado(pendente.requestId);
    // `ask_user` nao tem conceito nativo de "decline"/"cancel" (diferente
    // da elicitation MCP generica) -- `UserInputResponse` exige sempre
    // `{answer, wasFreeform}`. Enviamos um texto explicito para o modelo
    // entender que o usuario optou por nao responder, em vez de travar a
    // sessao aguardando indefinidamente (ate o timeout de 30min). Falha de
    // entrega aqui NAO precisa de banner de erro -- o usuario ja optou por
    // nao continuar aguardando resposta.
    await responderPergunta(
      pendente.requestId,
      "(usuário fechou a pergunta sem responder)",
      true
    );
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
          onClick={fecharSemResponder}
        >
          ✕
        </button>
        <p className="elicitation-bridge__message">{pendente.question}</p>
        <div className="ask-user-bridge__choices">
          {pendente.choices.map((opcao) => (
            <button
              key={opcao}
              type="button"
              disabled={enviando}
              onClick={() => escolher(opcao)}
            >
              {opcao}
            </button>
          ))}
        </div>
        {pendente.allowFreeform && (
          <div className="ask-user-bridge__freeform">
            <input
              type="text"
              placeholder="Ou digite sua própria resposta…"
              value={textoLivre}
              disabled={enviando}
              onChange={(e) => setTextoLivre(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") enviarLivre();
              }}
            />
            <button type="button" disabled={enviando || !textoLivre.trim()} onClick={enviarLivre}>
              Enviar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

