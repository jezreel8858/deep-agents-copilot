# Guia de Contribuição

Obrigado por considerar contribuir com este repositório. Este projeto adota uma
base de governança agent-first reutilizável (ver [`CLAUDE.md`](CLAUDE.md) e
[`AGENTS.md`](AGENTS.md)) combinada com dois sub-projetos aplicativos
(`apps/web` e `deploy/local-chat-gateway`).

## Estrutura do Repositório

- **Governança global** (`CLAUDE.md`, `.github/copilot-instructions.md`,
  `.github/agents/`, `.github/skills/`, `.github/prompts/`) — regras
  normativas e agentes de IA reutilizáveis, desacoplados de stack.
- **`apps/web`** — frontend Next.js + CopilotKit (Deep Agents Chat).
- **`deploy/local-chat-gateway`** — backend Python/FastAPI (Deep Agents
  Gateway).

Consulte [`docs/repo-map.md`](docs/repo-map.md) para navegação detalhada.

## Como Contribuir

1. **Abra uma issue** descrevendo o problema ou a melhoria antes de iniciar
   trabalho significativo.
2. **Crie um branch** a partir de `develop` com nome descritivo
   (`feat/...`, `fix/...`, `docs/...`, `refactor/...`).
3. **Siga as convenções de cada sub-projeto**:
   - `apps/web`: ver `apps/web/README.md` e
     `.github/instructions/react-frontend.instructions.md`.
   - `deploy/local-chat-gateway`: ver `deploy/local-chat-gateway/README.md` e
     `.github/instructions/python-backend.instructions.md`.
4. **Rode os testes localmente** antes de abrir o Pull Request:
   - `apps/web`: `npm run lint && npm run build`.
   - `deploy/local-chat-gateway`: `pytest`.
5. **Commits semânticos** (Conventional Commits): `feat:`, `fix:`, `docs:`,
   `refactor:`, `test:`, `chore:`.
6. **Nunca commitar segredos** (`.env`, `secrets/`, chaves/tokens) — todos os
   `.gitignore` do monorepo já cobrem esses padrões; o hook
   `.githooks/pre-commit` bloqueia vazamento de nomes de projetos externos
   (R-043/R-044).
7. **Abra o Pull Request** para `develop` com descrição clara do que mudou e
   por quê. PRs para `main` são restritos a releases.

## Governança de IA (Agent-First)

Alterações em `.github/agents/`, `.github/skills/` ou `.github/prompts/`
devem seguir o fluxo `@agent-router` → workflow canônico (ver
`.github/copilot-instructions.md` § 1). Novas regras normativas vão em
`CLAUDE.md`; documentação de stack específica vai em
`.github/instructions/*.instructions.md`.

## Código de Conduta

Seja respeitoso e construtivo nas discussões. Issues e PRs fora de escopo ou
com tom inadequado podem ser fechados sem aviso prévio.

## Licença

Este projeto é licenciado sob os termos do arquivo [`LICENSE`](LICENSE) (MIT).
