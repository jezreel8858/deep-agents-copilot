# CONTEXT.md — Glossário de Domínio Compartilhado para Compressão Semântica

> **Objetivo:** Estabelecer um vocabulário de domínio unificado e compartilhado entre humanos e agentes de IA, evitando a necessidade de re-explicar conceitos complexos em múltiplos parágrafos a cada nova sessão ("compressão semântica de tokens"). Serve como SSOT (Single Source of Truth) para indexação no `context-mode` (`ctx_index` / `ctx_search`) e desambiguação rápida de requisitos e regras de negócio.

---

## 1) Termos de Domínio e Definições Canônicas

| Termo Canônico | Definição Precisa de Negócio | Entidade / Contexto no Código |
|---|---|---|
| `<Termo 1>` | Definição formal sem ambiguidades da regra ou conceito | `packages/core/...` ou `models/...` |
| `<Termo 2>` | Definição formal sem ambiguidades da regra ou conceito | `services/...` |

---

## 2) Invariantes de Negócio Não-Negociáveis

Regras fundamentais que o software **NUNCA** pode violar, independentemente de refatorações ou novas funcionalidades:

1. **Invariante 1:** <Descrição exata da regra não negociável, ex.: "Todo débito exige contrapartida imediata de crédito no mesmo ledger">.
2. **Invariante 2:** <Descrição exata, ex.: "O estado 'PUBLICADO' não pode sofrer mutação destrutiva sem versionamento">.
3. **Invariante 3:** <Descrição exata, ex.: "Nenhuma operação de escrita é autorizada sem locatário (tenant_id) validado no token JWT">.

---

## 3) Mapeamento de Acrônimos e Siglas

| Acrônimo / Sigla | Significado Completo | Escopo / Utilização |
|---|---|---|
| `<SIGLA>` | <Significado por extenso> | <Onde e quando se aplica> |
| `SSOT` | Single Source of Truth | Fonte única e canônica da verdade |
| `SLA` | Service Level Agreement | Acordo de nível de serviço com tolerância máxima |

---

## 4) Anti-Termos (O Que NÃO Chamar de X)

Desambiguação explícita de falsos cognatos e termos confusos comumente misturados por humanos ou LLMs:

| Termo Incorreto / Proibido | Termo Canônico Correto | Justificativa / Risco de Confusão |
|---|---|---|
| `<Termo Errado A>` | `<Termo Correto>` | Não confundir a entidade X com o processo transitório Y |
| `Cliente` (quando no contexto de parceiro) | `Parceiro Credenciado` | `Cliente` é restrito ao consumidor final B2C |
| `Job` (quando no contexto de workflow) | `Pipeline de Governança` | `Job` refere-se estritamente à execução em background do worker |

---

## 5) Como Consumir no Context-Mode

```javascript
// Indexar o glossário para busca semântica rápida
ctx_index({
  path: "docs/agent-context/CONTEXT.md",
  source: "domain:context-glossary"
});

// Desambiguar termos durante a execução
ctx_search({
  source: "domain:context-glossary",
  queries: ["invariantes de negocio", "termo canônico"]
});
```
