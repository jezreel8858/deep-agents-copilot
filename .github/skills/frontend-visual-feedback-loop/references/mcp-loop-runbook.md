# Runbook — Loop VFL via Playwright MCP (N3 / References)

> Complemento de `../SKILL.md` (§ 2 e § 2.5). Exemplos > 8 linhas movidos para cá (R-026). Nenhum valor secreto: apenas **nomes** de variáveis de ambiente.

## 1. Sequência por viewport

```text
browser_navigate        url=<URL base lida da variável de ambiente APP_BASE_URL>
browser_resize          width=375  height=667      # repetir 768x1024 e 1440x900
browser_snapshot                                   # AOM: fonte primária de verdade
browser_console_messages level=error               # ignorar ruído de HMR/StrictMode
browser_take_screenshot filename=<output-dir>/<tela>-375.png   # SOMENTE sob demanda
browser_close                                      # cleanup obrigatório ao final
```

## 2. Projeto `setup` do Playwright Test (storageState)

```ts
// auth.setup.ts — credenciais exclusivamente via process.env
import { test as setup } from '@playwright/test';

const authFile = 'playwright/.auth/user.json'; // fora do versionamento (.gitignore)

setup('autenticar usuário de teste', async ({ page }) => {
  await page.goto(`${process.env.APP_BASE_URL}/login`);
  await page.getByLabel('Usuário').fill(process.env.APP_E2E_USER ?? '');
  await page.getByLabel('Senha').fill(process.env.APP_E2E_PASSWORD ?? '');
  await page.getByRole('button', { name: 'Entrar' }).click();
  await page.waitForURL('**/home');
  await page.context().storageState({ path: authFile });
});
```

Em `playwright.config.ts`, declarar o projeto `setup` (`testMatch: /.*\.setup\.ts/`) e fazer os demais projetos dependerem dele (`dependencies: ['setup']`, `use: { storageState: authFile }`).

## 3. Servidor MCP com sessão autenticada

```json
{
  "playwright": {
    "command": "npx",
    "args": [
      "-y", "@playwright/mcp@0.0.83", "--isolated",
      "--storage-state=playwright/.auth/user.json",
      "--viewport-size=1440x900", "--output-dir=.playwright-mcp"
    ]
  }
}
```

## 4. Falhas comuns

| Sintoma | Causa provável | Ação |
| :--- | :--- | :--- |
| Snapshot mostra `/login` | `storageState` expirado ou host diferente (`localhost` vs `127.0.0.1`) | Regenerar via projeto `setup` usando o mesmo host. |
| Snapshot vazio em Next/RSC | Hidratação pendente | `browser_wait_for` (texto esperado) antes do snapshot. |
| Erros de console duplicados | StrictMode/HMR em dev | Não tratar como bug de UI. |
| SSO/MFA bloqueia o setup | Fluxo interativo | `--user-data-dir` com perfil dedicado fora do repo (humano faz o login). |
