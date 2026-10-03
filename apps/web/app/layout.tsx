import type { Metadata } from "next";
import "@copilotkit/react-core/v2/styles.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Deep Agents Chat",
  description: "Frontend React (CopilotKit) do Deep Agents Gateway.",
};

/**
 * Script anti-FOUC (Flash Of Unstyled Content) do tema claro/escuro
 * (2026-10-03, ver `components/ThemeToggle.tsx`): aplica a classe `dark`
 * em `<html>` ANTES da hidratacao do React, lendo a preferencia salva em
 * `localStorage` (`deep-agents-chat:tema`) ou, na ausencia dela (1a
 * visita), o `prefers-color-scheme` do sistema operacional. Sem isto, a
 * pagina sempre renderizaria em tema claro no primeiro paint e "piscaria"
 * para escuro so depois que o `useEffect` do `ThemeToggle` rodasse.
 * Padrao documentado pelo proprio Next.js para theme-flash prevention
 * (script inline em `<head>`, `suppressHydrationWarning` em `<html>` para
 * silenciar o aviso esperado de mismatch -- o atributo `class` so existe
 * no DOM real, nunca no HTML renderizado pelo servidor).
 */
const SCRIPT_ANTI_FOUC_TEMA = `(function(){try{var t=localStorage.getItem("deep-agents-chat:tema");var escuro=t?t==="escuro":window.matchMedia("(prefers-color-scheme: dark)").matches;if(escuro){document.documentElement.classList.add("dark");}}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: SCRIPT_ANTI_FOUC_TEMA }} />
      </head>
      <body>{children}</body>
    </html>
  );
}



