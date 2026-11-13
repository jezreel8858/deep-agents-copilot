# Context-Mode — Playbooks Detalhados, Indexação e Memória

## 7) Playbooks Curtos (Exemplos Práticos)

**Retomada de sessão**

```javascript
ctx_search({
  queries: ["summary", "decision", "blocker"],
  sort: "timeline"
})
```

**Coleta + resposta em lote**

```javascript
ctx_batch({
  commands: [{ label: "service", command: "rg -n \"class .*Service\" src" }],
  queries: ["serviços críticos", "pontos de risco"],
  query_scope: "batch",
  cwd: "/caminho/raiz/do/repositorio"
})
```

**Análise de arquivo grande**

```javascript
ctx_execute({
  path: "logs/app.log",
  language: "javascript",
  code: "const errs=FILE_CONTENT.split('\\n').filter(l=>l.includes('ERROR')); console.log(errs.length);"
})
```

## 9) Dimensões de Memória: Short-Term vs Long-Term

O `context-mode` gerencia dois tipos distintos de memória com semântica diferente:

| Dimensão | Short-term (sessão) | Long-term (cross-sessão) |
|---|---|---|
| **Duração** | Vida da sessão de chat | Persiste entre sessões |
| **Tipo de informação** | Estado atual, coletas brutas, decisões da sessão | Fatos do projeto, regras de negócio, decisões arquiteturais |
| **Escopo** | Thread/conversa atual | Projeto, ecossistema ou organização |
| **Estratégia de atualização** | Sobrescreve a cada sessão | Acumulativa — novas informações enriquecem sem apagar |
| **Mecanismo de retrieval** | `ctx_search` sem `source` | `ctx_search(source: "projeto-x")` com source declarado |
| **Permissão de escrita** | Qualquer agent na sessão | Apenas agents com escopo de escrita declarado no catálogo |

**Padrões de uso:**

```javascript
// Short-term — coleta local da sessão (padrão)
ctx_search({ queries: ["decisão atual", "estado da tarefa"] })

// Long-term — busca em fonte persistente nomeada
ctx_search({ queries: ["regra de negócio X"], source: "projeto-alpha" })

// Indexação long-term — requer source explícito
ctx_index({ path: "docs/context/decisoes-arquiteturais.md", source: "projeto-alpha" })
```

**Anti-padrões:**
- ❌ Indexar dados de sessão em fonte persistente sem intenção explícita (polui memória long-term)
- ❌ Buscar memória long-term sem `source` declarado (retorna mistura ambígua de sessões)
- ❌ Tratar `ctx_index` sem `source` como memória permanente (comportamento não garantido entre sessões)

> **Memória procedimental** (avançado): capacidade de agents atualizarem seus próprios system prompts com base em feedback acumulado. Consulte a skill [`agent-memory-policy`](./../agent-memory-policy/SKILL.md) (Tier 3 — Experimental) para política completa, guardrails e ciclo de atualização controlada.
