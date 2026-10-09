---
name: auth-token-storage-patterns
description: Templates genéricos de autenticação Playwright por local do token (cookie/localStorage/sessionStorage/backend), loader de .env e gitignore.
parent_skill: playwright-mcp
---

# Padrões de Autenticação por Local do Token

> Referência da skill `playwright-mcp` (§ 7.4). **Genérico (R-038/R-043/R-044)**: somente placeholders `[PROJETO-ALVO]`, `<PROJETO>_TEST_USER`, `<PROJETO>_TEST_PASSWORD`, `<PROJETO>_STORAGE_STATE_PATH`, `<rota-alvo>`, `<raiz-do-projeto>`. Valores NUNCA em arquivo versionado.

## 1) Escolha da estratégia

| `token_storage` | Estratégia | Template |
| :--- | :--- | :--- |
| `cookie` / `localStorage` | `storageState` | § 2 |
| `sessionStorage` | fixture `addInitScript` | § 3 |
| token validado/renovado no backend | login por teste | § 2 sem `storageState` global; chamar o login no `beforeEach` |

## 2) `auth.setup.ts` (storageState)

```ts
import { test as setup, expect } from '@playwright/test';

const authFile = process.env['<PROJETO>_STORAGE_STATE_PATH'] ?? 'playwright/.auth/user.json';

setup('autenticar', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Usuário').fill(process.env['<PROJETO>_TEST_USER']!);
  await page.getByLabel('Senha').fill(process.env['<PROJETO>_TEST_PASSWORD']!);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await page.waitForURL('**/<rota-alvo>', { timeout: 30_000 }); // rota-alvo, não "sair do login"
  await expect(page).toHaveURL(/<rota-alvo>/);
  await page.context().storageState({ path: authFile });
});
```

`playwright.config.ts`: projeto `setup` (`testMatch: /auth\.setup\.ts/`) + projetos de teste com `dependencies: ['setup']` e `use.storageState: authFile`. Rodar o smoke existente antes/depois (o `storageState` global afeta todas as specs).

## 3) Fixture `sessionStorage` (`addInitScript`)

`storageState` não persiste `sessionStorage`. O setup grava o par chave/valor em arquivo de sessão gitignorado e a fixture o injeta antes da hidratação:

```ts
import { test as base } from '@playwright/test';
import { readFileSync } from 'node:fs';

export const test = base.extend({
  page: async ({ page }, use) => {
    const session = JSON.parse(readFileSync('playwright/.auth/session.json', 'utf8')) as Record<string, string>;
    await page.addInitScript((data) => {
      for (const [k, v] of Object.entries(data)) window.sessionStorage.setItem(k, v);
    }, session);
    await use(page);
  },
});
```

## 4) Loader mínimo de `.env`

Usar quando não há `dotenv` e `@types/node` não tipa `process.loadEnvFile`. Não sobrescreve variáveis já definidas:

```ts
import { existsSync, readFileSync } from 'node:fs';

export function loadEnv(file = '.env'): void {
  if (!existsSync(file)) return;
  for (const line of readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/.exec(line);
    if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
}
```

## 5) `.gitignore` mínimo

```gitignore
playwright/.auth/
.auth/
test-results/
playwright-report/
.playwright-mcp/
.env
```

## 6) Checklist

- [ ] `token_storage` identificado (grep do código de auth) antes de escolher a estratégia.
- [ ] Credenciais apenas por `<PROJETO>_TEST_USER`/`<PROJETO>_TEST_PASSWORD` (nomes; valores fora do repositório).
- [ ] `waitForURL` aguarda `<rota-alvo>`; timeout maior em HML.
- [ ] `gitignore` cobre sessão, traces, relatórios e `.playwright-mcp/`.
- [ ] Diagnóstico de falha: snapshot pós-falha → código de auth → causa-raiz.
