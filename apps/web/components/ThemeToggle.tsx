"use client";

import { Moon, Sun } from "lucide-react";
import { useSyncExternalStore } from "react";

/** Chave de persistencia no `localStorage` -- unico uso de localStorage
 * neste componente, exclusivamente para lembrar a preferencia de tema
 * entre visitas (nenhum dado sensivel). */
const CHAVE_TEMA_LOCALSTORAGE = "deep-agents-chat:tema";

type Tema = "claro" | "escuro";

function obterTemaDoDocumento(): Tema {
  return document.documentElement.classList.contains("dark") ? "escuro" : "claro";
}

/** Snapshot usado durante SSR/1o paint (sem acesso ao DOM real) -- o script
 * anti-FOUC em `app/layout.tsx` ja aplica a classe `.dark` real ANTES da
 * hidratacao, entao `useSyncExternalStore` resincroniza com o valor
 * correto no commit do client sem flicker visivel para o usuario. */
function obterTemaNoServidor(): Tema {
  return "claro";
}

/** Inscreve o componente em mudancas da classe `dark` de `<html>` via
 * `MutationObserver` -- fonte UNICA de verdade e' o proprio DOM (nenhum
 * estado React duplicado), entao alternancias feitas por QUALQUER outro
 * meio (ex.: devtools, extensao) tambem atualizam o icone automaticamente. */
function inscreverMudancaDeTema(notificarMudanca: () => void): () => void {
  const observer = new MutationObserver(notificarMudanca);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
  return () => observer.disconnect();
}

/**
 * ThemeToggle — icone de alternancia entre tema claro/escuro no header
 * (`AppShell.tsx`), pedido explicito do usuario (2026-10-03).
 *
 * Pesquisa prévia (nenhuma duplicacao/invencao de mecanismo proprio):
 * `@copilotkit/react-core` v2 **nao exporta** nenhum componente de toggle
 * de tema nem hook `useTheme` (confirmado por introspeccao do bundle
 * instalado, `node_modules/@copilotkit/react-core/dist/copilotkit-*.mjs`
 * -- a unica lib de icones importada e `lucide-react`, sem `Sun`/`Moon`).
 * O pacote, porem, JA suporta dark mode nativamente: seu CSS compilado
 * (`dist/v2/index.css`) usa a convencao padrao do Tailwind v4
 * `:is(.dark *)` (confirmado por introspeccao real) -- ou seja, QUALQUER
 * elemento com a classe `dark` em um ancestral (aqui, `<html>`) ja ativa
 * TODAS as variantes escuras do `<CopilotChat>`/Streamdown/prose
 * automaticamente, sem nenhuma configuracao adicional deste lado. Este
 * componente so precisa alternar essa MESMA classe `dark` em `<html>` --
 * nao reimplementa nada que o CopilotKit ja resolve.
 *
 * Nao ha design system proprio neste repositorio (ver comentario em
 * `AppShell.tsx`), entao o icone usa `lucide-react` (`Sun`/`Moon`) -- a
 * MESMA biblioteca de icones que o CopilotKit ja usa internamente
 * (`ThumbsUp`/`Copy`/`RefreshCw`/etc., ver `CopilotChatAssistantMessage`),
 * garantindo consistencia visual/peso de traco com o resto do chat.
 *
 * `useSyncExternalStore` (em vez de `useState`+`useEffect`, que violava a
 * regra `react-hooks/set-state-in-effect` do eslint-config-next 16 --
 * setState sincrono dentro de efeito): le o tema diretamente do DOM (fonte
 * unica de verdade), com snapshot SSR fixo em "claro" -- o script anti-FOUC
 * de `app/layout.tsx` garante que o client ja aplica a classe `.dark` real
 * ANTES da hidratacao, entao a resincronizacao do hook e' imperceptivel.
 */
export function ThemeToggle() {
  const tema = useSyncExternalStore(
    inscreverMudancaDeTema,
    obterTemaDoDocumento,
    obterTemaNoServidor
  );

  function alternarTema() {
    const novoTema: Tema = tema === "escuro" ? "claro" : "escuro";
    document.documentElement.classList.toggle("dark", novoTema === "escuro");
    try {
      localStorage.setItem(CHAVE_TEMA_LOCALSTORAGE, novoTema);
    } catch {
      // Storage indisponivel (modo privado/quota) -- degrada graciosamente:
      // a alternancia visual ainda funciona nesta sessao, so nao persiste.
    }
    // Nenhum setState manual aqui: o `MutationObserver` de
    // `inscreverMudancaDeTema` notifica o `useSyncExternalStore` assim que
    // a classe muda, re-renderizando este componente automaticamente.
  }

  const proximoTemaLabel =
    tema === "escuro" ? "Mudar para tema claro" : "Mudar para tema escuro";

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={alternarTema}
      aria-label={proximoTemaLabel}
      title={proximoTemaLabel}
    >
      {tema === "escuro" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}



