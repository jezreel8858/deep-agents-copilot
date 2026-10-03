"use client";

import { useAgent } from "@copilotkit/react-core/v2";
import { useEffect, useMemo, useRef, useState } from "react";
import { jaFoiTratado, marcarComoTratado } from "@/copilot/respondedRequests";
import { converterLinhasBackend, parsearDiff, resumirDiff, type LinhaDiffBruta } from "@/copilot/diffParser";

/**
 * FileEditBridge — visualizacao de DIFF COMPLETO (TODAS as linhas do
 * arquivo, nao apenas um recorte de poucas linhas de contexto) +
 * aprovacao/rejeicao de uma escrita de arquivo proposta pelo agent, ANTES
 * da escrita real ocorrer no disco -- paridade com o plugin Copilot da IDE
 * (pedido explicito do usuario, 2026-10-02). Prioriza as `lines` ja
 * calculadas pelo backend (`sdk_session._gerar_linhas_diff_completo`, via
 * `difflib` sobre o conteudo ATUAL do arquivo vs `new_file_contents`),
 * caindo para o parsing do `diff` truncado (unified diff hunks) do proprio
 * SDK apenas como fallback quando o backend nao tiver conteudo completo
 * disponivel.
 *
 * So existem 2 acoes possiveis POR ARQUIVO (pedido explicito do usuario):
 * "Aplicar alterações" (aprova TODAS as linhas do diff daquele arquivo de
 * uma vez -- nao ha aprovacao parcial linha-a-linha) ou "Ignorar" (rejeita
 * e a escrita daquele arquivo NUNCA ocorre). Enquanto nenhuma das duas for
 * escolhida, o arquivo permanece intocado no disco -- a intencao fica
 * APENAS no componente do front, como pedido.
 *
 * FILA de multiplos arquivos (pedido explicito do usuario, 2026-10-02): se
 * o agent propuser alteracoes em VARIOS arquivos (sequencialmente, 1
 * `PermissionRequestWrite`/`file_edit_requested` por vez -- o backend ja
 * serializa isso aguardando a resposta de cada arquivo antes do proximo),
 * cada novo pedido entra numa fila em vez de sobrescrever o anterior; o
 * usuario revisa e decide arquivo por arquivo, com indicador "Arquivo X de
 * N" no cabecalho quando houver mais de 1 pendente.
 *
 * Mesmo motivo arquitetural de `ElicitationBridge.tsx`/`AskUserBridge.tsx`
 * para NAO usar `useHumanInTheLoop`/`useInterrupt`: o gateway mantem a
 * sessao real do Copilot CLI viva durante toda a pausa (sem "fim de run +
 * resume"), respondendo via endpoint HTTP dedicado
 * (`/api/file-edit/[requestId]`) em vez do fluxo padrao de
 * tool-result-via-novo-turno do CopilotKit (ver
 * `sdk_session.stream_chat_ag_ui`, bloco `_bridge_edicao_arquivo`).
 */

interface EdicaoPendente {
  requestId: string;
  fileName: string;
  resolvedPath: string;
  diff: string;
  lines: LinhaDiffBruta[];
  intention: string;
}

/** Item ja decidido pelo usuario (aprovado ou ignorado), guardado em
 * `historico` para permitir navegacao "Voltar"/"Avançar" entre os arquivos
 * da fila sem perder o registro do que ja foi decidido. */
interface EdicaoHistorico extends EdicaoPendente {
  decisao: AcaoEdicao;
}

type AcaoEdicao = "approve" | "reject";

async function responderEdicaoArquivo(
  requestId: string,
  acao: AcaoEdicao
): Promise<boolean> {
  try {
    const resposta = await fetch(`/api/file-edit/${encodeURIComponent(requestId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: acao }),
    });
    return resposta.ok;
  } catch {
    return false;
  }
}

// Bug real corrigido (2026-10-02, mesma classe de problema de
// `AskUserBridge`/`ElicitationBridge`): a resposta HTTP nunca era checada
// -- um 404 (pedido de edicao expirado/gateway reiniciado em modo dev apos
// edicao de codigo sob `src/`) deixava o usuario crendo que "Aplicar
// alterações" funcionou, quando na verdade a escrita NUNCA ocorreu no disco.
const MENSAGEM_ERRO_ENVIO =
  "Não foi possível confirmar esta decisão com o agente (o pedido expirou ou o gateway foi reiniciado — comum em modo dev após uma edição de código). A alteração pode NÃO ter sido aplicada — envie sua mensagem novamente no chat para retomar.";

export function FileEditBridge() {
  const { agent } = useAgent();
  const [fila, setFila] = useState<EdicaoPendente[]>([]);
  const [historico, setHistorico] = useState<EdicaoHistorico[]>([]);
  // `null` = exibindo o item ATUAL (topo vivo da fila); numero = indice de
  // `historico` sendo revisado via navegacao "Voltar" (somente leitura).
  const [visualizandoIndice, setVisualizandoIndice] = useState<number | null>(null);
  const [expirada, setExpirada] = useState(false);
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [maximizado, setMaximizado] = useState(false);

  // Espelha `historico` num ref para o handler de evento (closure antiga do
  // `useEffect`) sempre ler o valor mais recente, sem precisar recriar a
  // subscricao a cada decisao do usuario.
  const historicoRef = useRef<EdicaoHistorico[]>([]);
  useEffect(() => {
    historicoRef.current = historico;
  }, [historico]);

  const pendenteAtual = fila[0] ?? null;
  const emHistorico = visualizandoIndice !== null;
  const itemExibido: EdicaoPendente | null = emHistorico
    ? historico[visualizandoIndice as number] ?? null
    : pendenteAtual;

  useEffect(() => {
    const { unsubscribe } = agent.subscribe({
      onCustomEvent: ({ event }) => {
        if (event.name === "file_edit_requested") {
          const valor = event.value as {
            request_id: string;
            file_name: string;
            resolved_path: string;
            diff: string;
            lines?: LinhaDiffBruta[];
            intention: string;
          };
          // Ignora replay de uma edicao ja respondida/dispensada neste
          // browser (ver `respondedRequests.ts`) -- mesmo bug real corrigido
          // em `AskUserBridge`/`ElicitationBridge`: reload reidrata a thread
          // e reemite o `*_requested` original.
          if (jaFoiTratado(valor.request_id)) return;

          // Bug real corrigido (2026-10-02, reportado pelo usuario): se o
          // agent tentar escrever o MESMO caminho de arquivo novamente apos
          // o usuario ja ter decidido (aprovar/ignorar) para esse caminho
          // nesta sessao de browser, o SDK gera um `request_id` NOVO -- o
          // dedup por id sozinho nao pega isso, reabrindo o modal e fazendo
          // a fila parecer "alternar" entre arquivos para sempre. Correcao:
          // honra automaticamente a MESMA decisao anterior para aquele
          // caminho, sem reabrir o modal.
          const decisaoAnterior = historicoRef.current.find(
            (item) => item.resolvedPath === valor.resolved_path
          );
          if (decisaoAnterior) {
            marcarComoTratado(valor.request_id);
            void responderEdicaoArquivo(valor.request_id, decisaoAnterior.decisao);
            return;
          }

          setExpirada(false);
          setErroEnvio(null);
          setFila((atual) => {
            if (atual.some((item) => item.requestId === valor.request_id)) {
              return atual; // Ja esta na fila -- evita duplicata.
            }
            return [
              ...atual,
              {
                requestId: valor.request_id,
                fileName: valor.file_name,
                resolvedPath: valor.resolved_path,
                diff: valor.diff,
                lines: valor.lines ?? [],
                intention: valor.intention,
              },
            ];
          });
        } else if (event.name === "file_edit_expired") {
          const valor = event.value as { request_id: string };
          setFila((atual) => atual.filter((item) => item.requestId !== valor.request_id));
          setExpirada(true);
        }
        // "file_edit_heartbeat": nenhuma acao de UI.
      },
    });
    return unsubscribe;
  }, [agent]);


  const linhasDiff = useMemo(() => {
    if (!itemExibido) return [];
    if (itemExibido.lines.length > 0) return converterLinhasBackend(itemExibido.lines);
    return parsearDiff(itemExibido.diff); // Fallback: hunks truncados do SDK.
  }, [itemExibido]);
  const resumo = useMemo(() => resumirDiff(linhasDiff), [linhasDiff]);

  if (!itemExibido) {
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
        ⏱️ A proposta de alteração anterior expirou sem resposta — o arquivo
        NÃO foi modificado.
      </div>
    ) : null;
  }

  const totalArquivos = historico.length + fila.length;
  const posicaoAtual = emHistorico ? (visualizandoIndice as number) + 1 : historico.length + 1;
  const podeVoltar = emHistorico ? (visualizandoIndice as number) > 0 : historico.length > 0;
  const podeAvancar = emHistorico;
  const decisaoExibida = emHistorico ? (historico[visualizandoIndice as number]?.decisao ?? null) : null;

  const voltar = () => {
    if (emHistorico) {
      setVisualizandoIndice((atual) => Math.max(0, (atual as number) - 1));
    } else if (historico.length > 0) {
      setVisualizandoIndice(historico.length - 1);
    }
  };

  const avancar = () => {
    if (!emHistorico) return;
    const indice = visualizandoIndice as number;
    if (indice < historico.length - 1) {
      setVisualizandoIndice(indice + 1);
    } else {
      setVisualizandoIndice(null); // Volta ao item atual (vivo) da fila.
    }
  };

  const responder = async (acao: AcaoEdicao) => {
    if (!pendenteAtual || emHistorico) return; // So decide o item ATUAL, nunca um do historico.
    setEnviando(true);
    marcarComoTratado(pendenteAtual.requestId);
    const entregue = await responderEdicaoArquivo(pendenteAtual.requestId, acao);
    // Registra a decisao no historico (permite "Voltar" revisar depois) e
    // SO ENTAO avanca a fila -- se este era o ultimo item, `fila` fica
    // vazia e o componente fecha definitivamente (retorna `null` acima),
    // sem reabrir, conforme pedido do usuario.
    setHistorico((atual) => [...atual, { ...pendenteAtual, decisao: acao }]);
    setFila((atual) => atual.slice(1));
    setMaximizado(false); // Nao faz sentido reter o tamanho expandido do arquivo anterior.
    setEnviando(false);
    // So alerta em "approve" -- se o usuario rejeitou, a nao-entrega e
    // inofensiva (o arquivo ja nao seria escrito de qualquer forma).
    if (!entregue && acao === "approve") setErroEnvio(MENSAGEM_ERRO_ENVIO);
  };

  return (
    <div className="elicitation-bridge__overlay" role="dialog" aria-modal="true">
      <div className="file-edit-bridge__card" data-maximizado={maximizado}>
        <div className="file-edit-bridge__header-actions">
          <button
            type="button"
            className="file-edit-bridge__maximizar"
            aria-label={maximizado ? "Restaurar tamanho" : "Maximizar"}
            title={maximizado ? "Restaurar tamanho" : "Maximizar"}
            onClick={() => setMaximizado((atual) => !atual)}
          >
            {maximizado ? (
              <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
                <path
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.4"
                  d="M6 2H2v4M10 14h4v-4M14 2l-5 5M2 14l5-5"
                />
              </svg>
            ) : (
              <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
                <rect
                  x="2.2"
                  y="2.2"
                  width="11.6"
                  height="11.6"
                  rx="1.2"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.4"
                />
              </svg>
            )}
          </button>
          <button
            type="button"
            className="elicitation-bridge__fechar"
            aria-label={emHistorico ? "Voltar ao arquivo atual" : "Ignorar (não aplicar)"}
            title={emHistorico ? "Voltar ao arquivo atual" : "Ignorar (não aplicar)"}
            disabled={enviando}
            onClick={() => (emHistorico ? setVisualizandoIndice(null) : responder("reject"))}
          >
            ✕
          </button>
        </div>

        <div className="file-edit-bridge__header">
          <span className="file-edit-bridge__icone" aria-hidden="true">
            📝
          </span>
          <div className="file-edit-bridge__titulo">
            <strong className="file-edit-bridge__arquivo">{itemExibido.fileName}</strong>
            {itemExibido.intention ? (
              <span className="file-edit-bridge__intencao">{itemExibido.intention}</span>
            ) : null}
          </div>
          <span className="file-edit-bridge__resumo">
            <span className="file-edit-bridge__resumo-add">+{resumo.adicionadas}</span>{" "}
            <span className="file-edit-bridge__resumo-rem">-{resumo.removidas}</span>
          </span>
        </div>

        {totalArquivos > 1 ? (
          <div className="file-edit-bridge__fila" role="status">
            <span>
              📂 Arquivo {posicaoAtual} de {totalArquivos}
              {emHistorico ? " — revisão de decisão já tomada" : " — decida para avançar"}
            </span>
            <span className="file-edit-bridge__fila-nav">
              <button type="button" disabled={!podeVoltar} onClick={voltar}>
                ← Voltar
              </button>
              <button type="button" disabled={!podeAvancar} onClick={avancar}>
                Avançar →
              </button>
            </span>
          </div>
        ) : null}

        <div className="file-edit-bridge__diff" role="group" aria-label="Diff proposto">
          {linhasDiff.length === 0 ? (
            <p className="file-edit-bridge__sem-diff">
              Sem preview de diff disponível para esta alteração.
            </p>
          ) : (
            <table className="file-edit-bridge__tabela">
              <tbody>
                {linhasDiff.map((linha, indice) =>
                  linha.tipo === "cabecalho" ? (
                    <tr key={indice} className="file-edit-bridge__linha-hunk">
                      <td colSpan={3}>{linha.conteudo}</td>
                    </tr>
                  ) : (
                    <tr key={indice} data-tipo={linha.tipo}>
                      <td className="file-edit-bridge__num">{linha.numeroAntigo ?? ""}</td>
                      <td className="file-edit-bridge__num">{linha.numeroNovo ?? ""}</td>
                      <td className="file-edit-bridge__conteudo">
                        <span className="file-edit-bridge__marcador">
                          {linha.tipo === "adicionada" ? "+" : linha.tipo === "removida" ? "-" : " "}
                        </span>
                        {linha.conteudo}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          )}
        </div>

        {emHistorico ? (
          <div className="elicitation-bridge__actions">
            <span className="file-edit-bridge__decisao-badge" data-decisao={decisaoExibida}>
              {decisaoExibida === "approve"
                ? "✅ Alterações já aplicadas neste arquivo"
                : "🚫 Alteração já ignorada neste arquivo"}
            </span>
            <button type="button" className="file-edit-bridge__aprovar" onClick={avancar}>
              Avançar →
            </button>
          </div>
        ) : (
          <div className="elicitation-bridge__actions">
            <button
              type="button"
              className="file-edit-bridge__ignorar"
              disabled={enviando}
              onClick={() => responder("reject")}
            >
              🚫 Ignorar
            </button>
            <button
              type="button"
              className="file-edit-bridge__aprovar"
              disabled={enviando}
              onClick={() => responder("approve")}
            >
              {enviando
                ? "Aplicando…"
                : fila.length > 1
                  ? "✅ Aplicar e ir para o próximo"
                  : "✅ Aplicar alterações"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}


