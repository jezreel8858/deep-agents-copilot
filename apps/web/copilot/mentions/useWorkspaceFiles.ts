"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type ArquivoWorkspace = {
  path: string;
  project: string;
  name: string;
};

type EstadoArquivos = {
  arquivos: ArquivoWorkspace[];
  carregando: boolean;
  truncado: boolean;
};

const DEBOUNCE_MS = 150;
const LIMITE_RESULTADOS = 30;

/**
 * useWorkspaceFiles — busca incremental de arquivos do workspace via
 * `/api/workspace/files` (proxy -> gateway `/v1/workspace/files`), para o
 * picker `#` do composer (paridade com "Select File, Folder or Tool" do
 * plugin Copilot da IDE). Debounced (150ms) para nao disparar 1 requisicao
 * por tecla; mantem apenas a ultima resposta valida (descarta respostas
 * fora de ordem via `AbortController`).
 */
export function useWorkspaceFiles() {
  const [estado, setEstado] = useState<EstadoArquivos>({
    arquivos: [],
    carregando: false,
    truncado: false,
  });
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const buscar = useCallback((query: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setEstado((anterior) => ({ ...anterior, carregando: true }));
      try {
        const params = new URLSearchParams({
          q: query,
          limit: String(LIMITE_RESULTADOS),
        });
        const resposta = await fetch(`/api/workspace/files?${params.toString()}`, {
          signal: controller.signal,
        });
        if (!resposta.ok) {
          setEstado({ arquivos: [], carregando: false, truncado: false });
          return;
        }
        const dados = (await resposta.json()) as {
          files: ArquivoWorkspace[];
          truncated?: boolean;
        };
        setEstado({
          arquivos: dados.files ?? [],
          carregando: false,
          truncado: Boolean(dados.truncated),
        });
      } catch (erro) {
        if ((erro as { name?: string }).name === "AbortError") return;
        setEstado({ arquivos: [], carregando: false, truncado: false });
      }
    }, DEBOUNCE_MS);
  }, []);

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      abortRef.current?.abort();
    };
  }, []);

  return { ...estado, buscar };
}

