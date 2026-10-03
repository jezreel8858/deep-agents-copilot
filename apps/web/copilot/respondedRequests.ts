/**
 * respondedRequests — memoria client-side (localStorage) de `request_id`s de
 * elicitation/ask_user ja respondidos ou dispensados NESTE browser.
 *
 * Bug real corrigido (2026-10-02, reportado pelo usuario): apos um `reload`
 * da pagina, uma pergunta `ask_user` JA RESPONDIDA reaparecia no modal.
 * Causa: `agent.subscribe({ onCustomEvent })` recebe novamente o evento
 * `*_requested` ao reidratar o historico da thread (replay de eventos
 * persistidos, nao apenas eventos NOVOS de um stream ao vivo) -- nao ha
 * como `AskUserBridge`/`ElicitationBridge` distinguir, a partir do proprio
 * evento, "isto e uma pergunta nova" de "isto e um replay de algo que este
 * MESMO browser ja respondeu". A correcao e marcar cada `request_id`
 * resolvido (por resposta real ou por fechamento manual) localmente, e
 * ignorar silenciosamente qualquer `*_requested` cujo id ja conste aqui.
 *
 * Escopo deliberadamente de BROWSER (localStorage), nao de servidor: o
 * gateway ja resolve/descarta o `asyncio.Future` correspondente no momento
 * da resposta (`resolver_elicitacao`/`resolver_pergunta_usuario`) -- esta
 * memoria serve apenas para a CAMADA DE APRESENTACAO nao reabrir um modal
 * ja fechado quando o mesmo evento e reemitido pelo replay do SDK.
 */

const CHAVE_LOCALSTORAGE = "deep-agents:respostas-tratadas";
const LIMITE_IDS_RETIDOS = 200;

function lerConjunto(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const bruto = window.localStorage.getItem(CHAVE_LOCALSTORAGE);
    if (!bruto) return new Set();
    const lista = JSON.parse(bruto) as unknown;
    return Array.isArray(lista) ? new Set(lista.map(String)) : new Set();
  } catch {
    return new Set();
  }
}

function salvarConjunto(conjunto: Set<string>): void {
  if (typeof window === "undefined") return;
  try {
    // Mantem apenas os `LIMITE_IDS_RETIDOS` mais recentes (evita crescimento
    // ilimitado do localStorage ao longo de muitas sessoes de chat).
    const lista = Array.from(conjunto).slice(-LIMITE_IDS_RETIDOS);
    window.localStorage.setItem(CHAVE_LOCALSTORAGE, JSON.stringify(lista));
  } catch {
    // localStorage indisponivel (modo privado/quota excedida) -- degrada
    // graciosamente: a memoria so vale para a sessao de JS em memoria.
  }
}

/** Verifica se `requestId` ja foi tratado (respondido ou dispensado) antes. */
export function jaFoiTratado(requestId: string): boolean {
  return lerConjunto().has(requestId);
}

/** Marca `requestId` como tratado, para nao reabrir o modal em replays futuros. */
export function marcarComoTratado(requestId: string): void {
  const conjunto = lerConjunto();
  conjunto.add(requestId);
  salvarConjunto(conjunto);
}

