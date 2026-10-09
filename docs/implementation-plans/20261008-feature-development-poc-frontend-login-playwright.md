---
status: approved
approved_by: "aprovado por humano em 2026-10-08 via ask_questions"
date: 2026-10-08
autor: angular-arch-advisor
workflow: workflow-ui-layout
related-planning-doc: docs/implementation-plans/20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md
tier: light
reversibility: T2
plan_ref: docs/implementation-plans/20261008-feature-development-poc-frontend-login-playwright.md
root_path: <raiz-do-projeto>
allowed_files:
  - <raiz-do-projeto>/e2e-playwright/auth.setup.ts
  - <raiz-do-projeto>/e2e-playwright/fixtures.ts
  - <raiz-do-projeto>/e2e-playwright/login-home.spec.ts
  - <raiz-do-projeto>/e2e-playwright/smoke.spec.ts
  - <raiz-do-projeto>/playwright.config.ts
  - <raiz-do-projeto>/.gitignore
amendments:
  - "2026-10-08: Emenda A (token em sessionStorage) aprovada por humano via chat (opcao A); status permanece approved; ver secao 11"
progress: 0
---

> **Status: APPROVED** — aprovado por humano em 2026-10-08 via `ask_questions`. Plano consultivo e GENERICO (anonimizado, R-038/R-043): sem codigo de producao nem specs; o projeto real e referido apenas como [PROJETO-ALVO].

Progresso: 0/11 tarefas concluidas (T1-T7 originais + T8-T11 da Emenda A)

## 1. Contexto e decisoes humanas registradas
- POC: login automatizado + navegacao + validacao em [PROJETO-ALVO] (Angular, `@playwright/test` ja instalado, dev server em `<URL_BASE>`).
- Root do projeto-alvo: `<raiz-do-projeto>` (resolvido a partir da configuracao local gitignored; nunca versionado).
- Decisoes humanas:
  1. Rota-alvo = home/dashboard pos-login (`<rota-alvo>`, descoberta em leitura).
  2. Validacao = elemento principal visivel + sem erro de console. Snapshot de acessibilidade padrao; screenshot somente sob demanda.
  3. Credenciais = env vars locais `<PROJETO>_TEST_USER` e `<PROJETO>_TEST_PASSWORD`, exportadas pelo usuario. Nunca em prompt, log, snapshot ou neste plano.
  4. Viewport unico 1440x900.
  5. App ja rodando em `<URL_BASE>` com backend de auth acessivel.
  6. Commit da POC SEPARADO do commit da consolidacao (`20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md`).
- Decisoes humanas de aprovacao (2026-10-08, via `ask_questions`):
  - P1 = validar apenas URL `<rota-alvo>` + shell de navegacao visivel via snapshot de acessibilidade (sem heading; sem alterar `src`).
  - P2 = usuario de teste interno (fluxo `<rota-login>`).
  - P3 = T2 corrige o `.gitignore` (storageState, `.auth/`, `test-results`, `playwright-report`, `.playwright-mcp`).
  - P4 = `<PROJETO>_STORAGE_STATE_PATH=.auth/storage-state.json` (gitignored).
  - P5 = aprovada a edicao de `playwright.config.ts` e `.gitignore` no projeto-alvo.
  - Smoke: aplicar `storageState` globalmente (sem projeto dedicado); risco R9 aceito.

## 2. Descoberta (somente leitura, evidencias)
- Router da aplicacao: rotas protegidas por guard de autenticacao; rota de login publica; rota curinga redireciona para `<rota-alvo>`.
- **Rota-alvo pos-login: `<rota-alvo>`** (shell de navegacao lateral + componente de home).
- O formulario de login usa botao `<button>` de submissao e campos localizaveis por label.
- O token de sessao e mantido em armazenamento de navegador cuja natureza foi investigada na Emenda A (secao 11).
- Config Playwright existente com projeto de navegador unico e spec de smoke previo; sem projeto `setup`.

## 3. UI/Layout
- Estrategia de auth: `storage_state`. Projeto `setup` do Playwright (`auth.setup.ts`) faz login com env vars e grava `storageState` em caminho **gitignored** lido de `<PROJETO>_STORAGE_STATE_PATH`. O projeto de navegador depende de `setup` e usa esse `storageState`.
- MCP Playwright (loop interativo do executor): `--isolated --storage-state=<valor de <PROJETO>_STORAGE_STATE_PATH>`; versao fixada `@playwright/mcp@<x.y.z>` (sem `@latest`). Sem `--extension`. SSO/MFA nao aplicavel (login/senha).
- Ambiente e URL base: `<URL_BASE>` via `baseURL` do config; ambiente nao produtivo. Mesmo host na captura e na execucao (nao alternar `localhost`/`127.0.0.1`, para nao dividir storage/cookies — risco R6).
- Origens permitidas: somente `<URL_BASE>`. Navegacao a outra origem (IdP externo etc.) = falha, nao seguir.
- Viewport: 1440x900 unico (fonte unica: `frontend-visual-feedback-loop`).
- Projeto-alvo: [PROJETO-ALVO], projeto Playwright de navegador + `setup`.
- Credenciais: somente NOMES `<PROJETO>_TEST_USER`, `<PROJETO>_TEST_PASSWORD`, `<PROJETO>_STORAGE_STATE_PATH`. Nunca valores.
- Ordem de validacao: `browser_resize` 1440x900 -> `browser_navigate` `<rota-alvo>` -> `browser_snapshot` (padrao) -> `browser_console_messages` (nivel error) -> `browser_take_screenshot` somente sob demanda.
- Dicas de stack: dev server (`ng serve`) ja ativo; sem subir novo servidor.

## 4. Decisao de Design Pattern (mini-ADR)
- Contexto: reutilizar sessao autenticada entre specs sem relogar nem expor segredo.
- Decisao: Nenhum pattern GoF necessario — padrao oficial do Playwright (projeto `setup` + `storageState` + dependencias de projeto). Page Object nao adotado (1 spec, poucos seletores).
- Alternativas: login em `beforeEach` (lento, repete credenciais); `--user-data-dir` (reservado a SSO/MFA); `--extension` (proibido por padrao).
- Consequencias: +reuso e isolamento; -token expira e exige refazer setup; storageState e segredo e deve ficar fora do git.

## 5. Allowlist de arquivos (minima, em `<raiz-do-projeto>`)
| Arquivo | Acao |
|---|---|
| `e2e-playwright/auth.setup.ts` | criar |
| `e2e-playwright/login-home.spec.ts` | criar |
| `playwright.config.ts` | editar: projeto `setup` + `dependencies` + `storageState` + viewport 1440x900 no projeto de navegador |
| `.gitignore` | editar: adicionar `.auth/`, `playwright/.auth/`, `test-results/`, `playwright-report/`, `.playwright-mcp/` |
| `e2e-playwright/fixtures.ts` | criar (Emenda A): fixture que restaura sessionStorage |
| `e2e-playwright/smoke.spec.ts` | editar (Emenda A): passa a usar a fixture; unica alteracao permitida |
| `.auth/session.json` | gerado em runtime, NAO versionado (coberto por `.auth/`); tratado como segredo |

Fora da allowlist: `src/**`, specs legados de outro runner, `package.json` (sem nova dependencia). Arquivo extra exige nova aprovacao.
Nota: `smoke.spec.ts` deve continuar passando; como `fullyParallel` + `storageState` global afeta o smoke, **DECISAO HUMANA: aplicar `storageState` globalmente**; risco R9 aceito, mitigado por smoke antes/depois e backup do `playwright.config.ts`.

## 6. Checklist de Execucao Tecnica (GFM Unificado)
- [ ] T1 Validar `<rota-alvo>` (URL) e shell de navegacao visivel via snapshot de acessibilidade (leitura/MCP, sem heading, sem editar `src`) e confirmar o `<button>` de submissao do login; registrar P1 no PR `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T2 Atualizar `.gitignore` (entradas da secao 5) ANTES de gerar qualquer storageState; conferir com `git check-ignore -v` `{paralelizavel: false, responsavel: "@angular-developer"}`
- [ ] T3 Backup de `playwright.config.ts`; rodar smoke ANTES; editar config com projeto `setup` (`testMatch: auth.setup.ts`), `dependencies: ['setup']` e `storageState` GLOBAL em `use` lido de `process.env.<PROJETO>_STORAGE_STATE_PATH` (falhar claramente se ausente), viewport 1440x900, `baseURL` `<URL_BASE>`; rodar smoke DEPOIS e reportar diferencas (rollback via backup) `{paralelizavel: false, responsavel: "@angular-developer"}`
- [ ] T4 Criar `e2e-playwright/auth.setup.ts`: le `<PROJETO>_TEST_USER`/`<PROJETO>_TEST_PASSWORD` do ambiente (falha se ausentes, sem ecoar valores), `goto('<rota-login>')`, preenche por label, clica no botao de submissao, aguarda a rota-alvo (`waitForURL` na rota-alvo, nao apenas "sair do login"), grava storageState; sem `console.log` de credenciais; trace desabilitado no setup `{paralelizavel: false, responsavel: "@angular-developer"}`
- [ ] T5 Criar `e2e-playwright/login-home.spec.ts`: `goto('<rota-alvo>')`; assert URL nao e de login/auth/redirect; shell de navegacao visivel (sem heading); coletar `page.on('console')` e falhar em erro `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T6 Validar via MCP Playwright (`--isolated --storage-state`): resize -> navigate -> snapshot -> console; reportar sem expor token `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T7 Rodar `@playwright/test` (setup + login-home + smoke); `git diff --stat` restrito a allowlist; `git status` sem storageState/trace/`.playwright-mcp` `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T8 (Emenda A) No `auth.setup.ts`, apos o login, salvar o conteudo de `sessionStorage` em `.auth/session.json` (gitignorado) alem do storageState; sem logar valores `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T9 (Emenda A) Criar `e2e-playwright/fixtures.ts`: fixture que le `.auth/session.json` e restaura `sessionStorage` via `context.addInitScript` antes de qualquer navegacao `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T10 (Emenda A) `login-home.spec.ts` e `smoke.spec.ts` passam a importar `test` da fixture; reverter qualquer timeout elevado ao padrao do config; reforcar asserção: `toHaveURL` na rota-alvo e formulario de login com `toHaveCount(0)` (ou `not.toBeVisible`), alem do shell de navegacao visivel `{paralelizavel: false, responsavel: "@angular-test-engineer"}`
- [ ] T11 (Emenda A) Rodar setup + `login-home.spec.ts` + `smoke.spec.ts`; `git status` confirmando que `.auth/session.json` nao aparece e `git diff --stat` sem `src/**` `{paralelizavel: false, responsavel: "@angular-test-engineer"}`

## 7. Criterios de pronto
- Setup autentica com env vars e grava storageState em caminho gitignored; spec passa sem relogin.
- `<rota-alvo>` carrega sem redirect para login/auth; shell de navegacao visivel (snapshot de acessibilidade); sem heading; zero erros de console.
- Snapshot MCP sem credenciais/tokens; sem screenshot salvo, exceto sob demanda e fora do git.
- `smoke.spec.ts` continua verde; nenhum arquivo fora da allowlist alterado; `git status` sem storageState/trace/`.playwright-mcp`.
- Commit da POC separado do da consolidacao.
- (Emenda A) `<rota-alvo>` carrega autenticada com URL correta e sem formulario de login; specs verdes via fixture; sem timeout elevado; `.auth/session.json` gitignorado e ausente de `git status`; `src/**` inalterado; nenhum valor de token em logs/traces/PR.

## 8. Riscos
| # | Risco | Mitigacao |
|---|---|---|
| R1 | Segredo em log/snapshot/trace (campo senha preenchido aparece em trace/snapshot) | sem `console.log`; `trace: off` no setup; nao anexar traces/snapshots ao PR; revisar artefatos antes de commit |
| R2 | storageState versionado (`.gitignore` sem entradas) | T2 antes de qualquer execucao; `git check-ignore` |
| R3 | Usuario nao-interno cai em fluxo de IdP externo em vez do login local | **P2**: confirmar usuario interno/ambiente de desenvolvimento; senao parar e replanejar |
| R4 | Campo de login exige formato/mascara especifico | usuario de teste valido; preencher apenas o formato esperado |
| R5 | Token expira / guard de home abre popup | refazer setup; falha clara de auth |
| R6 | `127.0.0.1` vs `localhost` divergem entre webServer e baseURL | usar `baseURL` unico e servidor ja ativo |
| R7 | `fullyParallel` e `retries` repetem login | setup unico; retries nao aplicam a setup com credenciais |
| R8 | Heading inexistente no template | Resolvido: P1 sem heading, shell via snapshot |
| R9 | **Risco aceito (decisao humana):** `storageState` global afeta `smoke.spec.ts` (passa a rodar autenticado; pode mascarar fluxos nao autenticados e depende do setup) | rodar smoke antes/depois e reportar; rollback via backup do `playwright.config.ts` |
| R10 | (Emenda A) Token em `.auth/session.json` e credencial viva em arquivo local | gitignorado via `.auth/`; tratado como segredo; nunca logar/anexar; apagar apos uso; rotacionar senha se suspeita de vazamento |
| R11 | (Emenda A) Refresh/validacao de token no backend invalida o token restaurado (redirect para login) | Alternativa B: login por teste (setup por spec) |

## 9. Validacao e rollback
- Validacao: T6 (MCP) + T7 (`@playwright/test`); `git diff --stat` restrito a allowlist.
- Rollback: `git restore playwright.config.ts .gitignore` e remover `auth.setup.ts` e `login-home.spec.ts` (ou `git revert` do commit isolado da POC); apagar o arquivo de storageState local; rotacionar a senha se houver suspeita de vazamento.
- Rollback (Emenda A): `git restore e2e-playwright/auth.setup.ts e2e-playwright/login-home.spec.ts e2e-playwright/smoke.spec.ts`, remover `e2e-playwright/fixtures.ts`, apagar `.auth/session.json` local (ou `git revert`); `src/**` nao e tocado.

## 10. Pendencias para aprovacao humana
Todas resolvidas em 2026-10-08 (P1–P5 e decisao de smoke; ver secao 1).

### Checklist Defensivo Pre-Code-Review
- [ ] Sanitizacao/validacao de inputs nas bordas (env vars obrigatorias validadas)
- [ ] Ausencia de segredos/tokens em hardcode e logging sem PII
- [ ] Tratamento defensivo de excecoes e autorizacao validado (redirect = falha)
- [ ] Testes defensivos atendendo aos quality gates

## 11. Emenda A (2026-10-08) - sessionStorage
- Aprovacao: humano, 2026-10-08, chat, "opcao A". Status permanece `approved`.
- Causa-raiz (bug-triage): o token da aplicacao fica em `sessionStorage`; o guard de autenticacao redireciona para o login; o `storageState` do Playwright nao persiste `sessionStorage`.
- Correcao A (somente e2e, sem alterar `src/**`): T8 (salvar), T9 (fixture), T10 (specs + timeout + asserção), T11 (validacao). Executor: `@angular-test-engineer`.
- Alternativa B (fallback): login por teste, se R11 ocorrer.
