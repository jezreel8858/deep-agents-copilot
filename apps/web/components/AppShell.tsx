"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ITENS_NAV = [
  { href: "/", label: "Chat" },
  { href: "/workspace", label: "Espaço de Trabalho" },
];

/**
 * AppShell — navegacao principal (Chat | Workspace) e moldura visual da
 * aplicacao. Mantido deliberadamente simples (sem design system proprio
 * neste repositorio — ver blueprint F8).
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
      </nav>
      <main className="app-shell__main">{children}</main>
    </div>
  );
}

