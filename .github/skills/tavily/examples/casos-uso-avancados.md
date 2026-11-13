# Tavily — Casos de uso avançados (genéricos)

## Investigar breaking change em versão específica

```
tavily_search({
  query: "<biblioteca> <versão> breaking changes migration guide",
  include_domains: ["docs.<vendor>.com", "github.com/<org>/<repo>"],
  search_depth: "advanced",
  time_range: "year"
})
```

## Verificar compatibilidade de pacote

```
tavily_search({
  query: "<biblioteca A> <versão> compatibility with <biblioteca B>",
  include_domains: ["docs.<vendor>.com", "github.com", "stackoverflow.com"],
  time_range: "year"
})
```

## Pesquisa aprofundada sobre padrão arquitetural

```
tavily_research({
  input: "best practices <tema arquitetural> with <stack alvo>",
  model: "pro"
})
```

## Extrair documentação oficial de múltiplas URLs

```
tavily_extract({
  urls: [
    "https://docs.<vendor>.com/<topic-1>",
    "https://docs.<vendor>.com/<topic-2>"
  ],
  query: "<pergunta objetiva>"
})
```

## Buscar issue/PR com workaround

```
tavily_search({
  query: "site:github.com <biblioteca> <erro> workaround",
  search_depth: "advanced"
})
```

## Verificar CVE de dependência conhecida

```
// Opção 1 — visão geral web
tavily_search({
  query: "<dependência> CVE vulnerability security",
  time_range: "year"
})

// Opção 2 — validação precisa de versão
validate_cves({
  dependencies: ["<pacote>@<versão>"],
  ecosystem: "npm"
})
```

## Padrão: buscar + indexar para não rebuscar

```
tavily_extract({
  urls: ["https://docs.<vendor>.com/<topic>"],
  query: "<conceito chave>"
})

ctx_index({ url: "https://docs.<vendor>.com/<topic>" })

ctx_search({ queries: ["<conceito chave>"] })
```

## Anti-padrões a evitar

```
// ❌ Rebuscar a mesma URL duas vezes na sessão
tavily_extract({ urls: ["https://docs.<vendor>.com/<topic>"] })
// ... mais tarde ...
tavily_extract({ urls: ["https://docs.<vendor>.com/<topic>"] }) // ← use ctx_search

// ❌ Usar tavily para conteúdo do próprio codebase
tavily_search({ query: "como funciona UserService no meu projeto" }) // ← use ctx_search ou grep_search

// ❌ crawl em portal com autenticação restrita
tavily_crawl({ url: "https://intranet.exemplo.com" })
```
