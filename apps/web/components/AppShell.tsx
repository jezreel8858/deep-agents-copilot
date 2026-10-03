"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";

const ITENS_NAV = [
  { href: "/", label: "Chat" },
  { href: "/workspace", label: "Espaço de Trabalho" },
];

/**
 * AppShell — navegacao principal (Chat | Workspace) e moldura visual da
 * aplicacao. Mantido deliberadamente simples (sem design system proprio
 * neste repositorio — ver blueprint F8). `<ThemeToggle>` (2026-10-03):
 * icone de alternancia claro/escuro no canto direito do header (ver
 * `components/ThemeToggle.tsx` para a pesquisa de suporte nativo do
 * CopilotKit v2 a dark mode via classe `.dark`).
 *
 * Bug real corrigido (2026-10-03, reportado pelo usuario via screenshot):
 * esta integracao havia sido aplicada em edicao anterior mas o arquivo
 * acabou revertido para a versao sem `<ThemeToggle>` antes do proximo
 * turno (confirmado via `git diff` -- `AppShell.tsx` aparecia identico ao
 * HEAD enquanto `globals.css`/`layout.tsx`/`package.json` mantinham as
 * mudancas) -- o icone nunca chegou a aparecer no header por causa disso.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <nav className="app-shell__nav">
        <strong>Deep Agents Chat</strong>
        {ITENS_NAV.map((item) => (
          <Link key={item.href} href={item.href} data-active={pathname === item.href}>
            {item.label}
          </Link>
        ))}
        <ThemeToggle />
      </nav>
      <main className="app-shell__main">{children}</main>
    </div>
  );
}

