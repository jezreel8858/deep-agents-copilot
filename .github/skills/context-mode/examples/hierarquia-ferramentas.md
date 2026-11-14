# Hierarquia de Ferramentas — Exemplos Genéricos

Este arquivo mostra exemplos de uso do `context-mode` em qualquer codebase com foco em baixo consumo de contexto.

## Exemplo 1 — Coleta + resposta em lote

```js
ctx_batch({
  commands: [
    { label: "services", command: "rg -n \"class .*Service\" src" },
    { label: "business-errors", command: "rg -n \"BusinessError|BusinessException\" src" }
  ],
  queries: ["serviços encontrados", "pontos de validação e erro"],
  query_scope: "batch"
})
```

## Exemplo 2 — Follow-up sem nova coleta

```js
ctx_search({
  source: "services",
  queries: ["métodos públicos", "dependências críticas", "riscos de regressão"]
})
```

## Exemplo 3 — Processar arquivo grande em sandbox

```js
ctx_execute({
  path: "logs/app.log",
  language: "javascript",
  code: "const e=FILE_CONTENT.split('\\n').filter(l=>l.includes('ERROR')); console.log(`erros=${e.length}`);"
})
```

## Exemplo 4 — Web docs sem HTML bruto no chat

```js
ctx_index({
  requests: [{ url: "https://angular.dev/guide/styleguide", source: "angular-styleguide" }],
  concurrency: 4
})
```

```js
ctx_search({
  source: "angular-styleguide",
  queries: ["change detection", "signals", "best practices"],
  limit: 5
})
```

### Política Anti-Timeout, Runtime Preferencial JavaScript (`fs` nativo) e Circuit Breaker Fail-Fast (`ctx_execute` / `ctx_batch`)

1. **Runtime Obrigatório `language: "javascript"` no `ctx_execute` (Anti-Defender/AMSI Hang)**:
   - No Windows, a invocação de `python.exe` (`language: "python"` ou `python -c`) ou cadeias pesadas de subshells a partir do processo Node.js do servidor MCP `context-mode` sofre interceptação síncrona pelo Windows Defender (`MsMpEng.exe` / Behavior Monitoring / AMSI), causando bloqueios severos de I/O e timeouts (`ETIMEDOUT` / `taskkill /F /T`).
   - Portanto, `language: "javascript"` (com módulos nativos `fs` e `path` do Node.js) é o **runtime obrigatório** no `ctx_execute` para leitura, inspeção, busca, parsing JSON/texto e modificação em lote de arquivos.
   - É **terminantemente proibido** invocar `language: "python"`, `python -c` ou subshells aninhados para I/O de arquivos. (A execução de binários Python via `child_process` é restrita exclusivamente a ferramentas CLI do ecossistema, como `pytest` ou scripts de sincronização canônicos, nunca para ler/editar arquivos).
2. **Higiene de Comandos em `ctx_batch`**:
   - Os comandos shell em `ctx_batch` devem ser leves, atômicos e com escopo de diretório estritamente restrito.
   - É **proibido** disparar `python -c` inline em lote ou varreduras recursivas irrestritas na raiz do workspace sem filtro de pasta/extensão (evitando estourar o orçamento de tempo do batch).
3. **Política Fail-Fast & Circuit Breaker de Timeout (Máx. 1 Retry com Troca de Estratégia)**:
   - Em caso de erro de timeout (`ETIMEDOUT`, `timed out`, `taskkill`) em `ctx_execute` ou `ctx_batch`, o agente tem **tolerância zero para repetir a mesma chamada/runtime**.
   - É permitido no **máximo 1 retry**, contanto que haja **troca obrigatória de estratégia** (migrar de `python`/`shell` para `language: "javascript"` puro com `fs` nativo, ou dividir o lote em comandos menores/escopo restrito).
   - Se ocorrer um **2º timeout**, o **Circuit Breaker Fail-Fast** abre imediatamente: o agente deve abortar novas tentativas de spawn, registrar a evidência e acionar o fallback canônico ou reportar o bloqueio em formato Compact Error Reporting (R-020).
