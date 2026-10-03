# Deep Agents Chat

Frontend React (Next.js 16 App Router + [CopilotKit v2](https://docs.copilotkit.ai))
do Deep Agents Gateway. Substitui o Lobe Chat (decisao D4-rev — ver
`docs/architecture/BLUEPRINT_LOCAL_CHAT_GATEWAY.md`).

> **CopilotKit v2**: este projeto usa a API v2 (`@copilotkit/react-core/v2`,
> `@copilotkit/runtime/v2`). A v1 esta deprecada mas ainda funcional
> (coexistencia garantida por "pelo menos 2 releases minor" — ver
> [migrate/v2](https://docs.copilotkit.ai/migrate/v2)); todo o codigo aqui
> ja usa a API v2 desde o inicio.

## Arquitetura

```
Browser (CopilotChat/CopilotSidebar/CopilotPopup — @copilotkit/react-core/v2)
  -> POST|GET|PATCH|DELETE /api/copilotkit (Next.js Route Handler, servidor)
     -> CopilotRuntime v2 + BuiltInAgent (@copilotkit/runtime/v2)
        -> AI SDK createOpenAI({ baseURL: GATEWAY_BASE_URL/v1 }) — provider custom
           -> gateway FastAPI (Deep Agents Gateway, deploy/local-chat-gateway) — OpenAI-compatible
```

A chave do gateway (`GATEWAY_API_KEY`) nunca sai do processo servidor —
o browser so fala com `/api/copilotkit` (mesma origem).

## Desenvolvimento local

```bash
cd apps/web
npm install
cp .env.example .env.local   # ajuste GATEWAY_API_KEY e WEB_ACCESS_CODE
npm run dev
```

Pre-requisito: o gateway (Deep Agents Gateway, `deploy/local-chat-gateway`) precisa estar
rodando em `GATEWAY_BASE_URL` (default `http://127.0.0.1:8080`).

## Docker (via docker-compose do gateway)

```bash
cd deploy/local-chat-gateway
cp .env.example .env   # ajuste GATEWAY_API_KEY e WEB_ACCESS_CODE
docker compose up --build
```

UI disponivel em `http://127.0.0.1:3000` (exige `WEB_ACCESS_CODE`).

## Features do CopilotKit (v2) utilizadas

| Feature (v2) | Onde |
|---|---|
| `<CopilotChat>` (chat embutido em tela cheia) | `app/(chat)/page.tsx` |
| `<CopilotSidebar>` | `app/(chat)/workspace/page.tsx` |
| `<CopilotPopup>` (atalho global) | `app/(chat)/page.tsx` |
| `useFrontendTool` (handler simples) | `copilot/actions.tsx` — `mostrarNotificacao`, `copiarParaAreaDeTransferencia`, `definirNotaDoWorkspace` |
| `useHumanInTheLoop` (pausa + `respond`) | `copilot/actions.tsx` — `confirmarAcao` |
| `useRenderTool` (generative UI de tool do backend) | `copilot/actions.tsx` — `renderizarTraceDeFerramenta` |
| `useAgentContext` (contexto compartilhado, substitui `useCopilotReadable`) | `copilot/readables.ts` |
| `useConfigureSuggestions` (substitui `useCopilotChatSuggestions`) | `copilot/suggestions.ts` |
| `useAgentContext` (substitui `useCopilotAdditionalInstructions` — ver ressalva no arquivo) | `copilot/instructions.ts` |
| `BuiltInAgent` + `createOpenAI` custom provider (substitui `OpenAIAdapter`) | `app/api/copilotkit/route.ts` |
| `createCopilotRuntimeHandler` (substitui `copilotRuntimeNextJSAppRouterEndpoint`) | `app/api/copilotkit/route.ts` |
| Persistencia de threads (sem Copilot Cloud) | `lib/threads.ts` (localStorage) |

## Nao-escopo desta fase

- Execucao real de `tool_calls` pelo SDK do Copilot no gateway: as tools
  acima ja estao registradas no frontend, mas so serao de fato *chamadas*
  pelo modelo quando o gateway repassar `tools`/`tool_calls` ao SDK real
  (ver `deploy/local-chat-gateway/src/local_chat_gateway/sdk_session.py`,
  trabalho futuro "B3" do blueprint de migracao).
- Historico de threads sincronizado entre dispositivos (depende de
  Copilot Cloud — deliberadamente nao usado nesta fase).
- `useAgentContext` para instrucoes comportamentais rigidas tem paridade
  parcial com o antigo `useCopilotAdditionalInstructions` v1 (ver
  GitHub Discussion CopilotKit/CopilotKit#4791) — regras de negocio
  obrigatorias devem ficar no system prompt do backend.


