"use client";

/**
 * threads — persistencia LOCAL (localStorage do browser) de metadados de
 * threads/conversas do CopilotKit. Nao ha Copilot Cloud configurado nesta
 * entrega (R9 do blueprint), entao o historico de conversas e mantido no
 * cliente — cada thread e identificada por um `threadId` (uuid) repassado
 * ao `<CopilotKit threadId=... headers={{ "X-Thread-Id": threadId }}>`.
 */

export interface ThreadMeta {
  id: string;
  titulo: string;
  criadoEm: string;
}

// Chave renomeada de "local-chat-web:threads" para "deep-agents-chat:threads"
// (consolidacao de nome do produto, 2026-10-02) -- sessoes de threads ja
// salvas no localStorage de um browser com a chave antiga ficam orfas
// (nunca lidas novamente), risco aceito: e so o historico local de threads,
// nao dado de sessao do backend.
const STORAGE_KEY = "deep-agents-chat:threads";

function lerThreads(): ThreadMeta[] {
  if (typeof window === "undefined") return [];
  try {
    const bruto = window.localStorage.getItem(STORAGE_KEY);
    if (!bruto) return [];
    const parsed = JSON.parse(bruto) as ThreadMeta[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function salvarThreads(threads: ThreadMeta[]): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(threads));
}

export function listarThreads(): ThreadMeta[] {
  return lerThreads().sort((a, b) => b.criadoEm.localeCompare(a.criadoEm));
}

export function criarThread(titulo = "Nova conversa"): ThreadMeta {
  const nova: ThreadMeta = {
    id: crypto.randomUUID(),
    titulo,
    criadoEm: new Date().toISOString(),
  };
  salvarThreads([nova, ...lerThreads()]);
  return nova;
}

export function renomearThread(id: string, titulo: string): void {
  salvarThreads(lerThreads().map((t) => (t.id === id ? { ...t, titulo } : t)));
}

export function removerThread(id: string): void {
  salvarThreads(lerThreads().filter((t) => t.id !== id));
}

export function obterOuCriarThreadAtiva(): ThreadMeta {
  const existentes = listarThreads();
  if (existentes.length > 0) return existentes[0]!;
  return criarThread();
}

