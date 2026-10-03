import { CopilotProviderShell } from "@/components/CopilotProviderShell";

/**
 * Layout do grupo de rotas protegidas (chat + workspace) — monta o
 * provider `<CopilotKit>` (via CopilotProviderShell) apenas para estas
 * paginas; `/login` fica fora deste grupo e nao precisa do provider.
 */
export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return <CopilotProviderShell>{children}</CopilotProviderShell>;
}

