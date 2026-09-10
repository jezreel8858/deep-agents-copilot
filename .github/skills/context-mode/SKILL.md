---
name: context-mode
description: >
  Boas práticas de uso do context-mode MCP em ambientes multi-projeto para reduzir
  poluição de contexto, preservar memória de sessão e otimizar custo de créditos.
  Prioriza processamento em sandbox e busca indexada.
tier: 1
category: process
triggers:
  - "ctx"
  - "contexto"
  - "economizar tokens"
  - "reduzir custo"
  - "pesquisar no projeto"
  - "buscar no codigo"
  - "arquivo grande"
  - "ler logs"
  - "analisar classe"
  - "mapear repositorio"
  - "historico da sessao"
tools:
  - "context-mode/ctx_search"
  - "context-mode/ctx_batch_execute"
  - "context-mode/ctx_execute"
  - "context-mode/ctx_execute_file"
  - "context-mode/ctx_index"
  - "context-mode/ctx_fetch_and_index"
  - "context-mode/ctx_stats"
  - "context-mode/ctx_doctor"
  - "context-mode/ctx_upgrade"
  - "context-mode/ctx_purge"
  - "context-mode/ctx_insight"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
---

# context-mode — Operação de alto rendimento

Skill para operar `ctx_*` com mínimo consumo de contexto: coletar em lote, processar em sandbox e responder apenas com sinal útil.

## 1) Objetivo

- Evitar flooding de contexto em tarefas de análise e investigação.
- Transformar saída bruta em resultado compacto e acionável.
- Preservar histórico consultável para sessões longas.
- Reduzir custo de créditos por chamada desnecessária ou redundante.

## 2) Ordem obrigatória de roteamento

| Ordem | Etapa | Tool | Resultado esperado |
|---|---|---|---|
| 0 | MEMORY | `ctx_search(..., sort: "timeline")` | retomada sem perguntar contexto já conhecido |
| 1 | GATHER | `ctx_batch_execute(commands, queries)` | coleta e resposta em uma única rodada |
| 2 | FOLLOW-UP | `ctx_search(queries: [...])` | perguntas adicionais sem releitura bruta |
| 3 | PROCESS | `ctx_execute` / `ctx_execute_file` | derivação com saída mínima |
| 4 | WEB | `ctx_fetch_and_index` → `ctx_search` | documentação externa sem HTML bruto no chat |
| 5 | INDEX | `ctx_index(path: ..., source: ...)` | base persistente para reuso |

## 3) Regras de substituição (mandatórias)

| Situação | Em vez de | Use |
|---|---|---|
| Releitura repetitiva | `read_file` várias vezes | `ctx_search` |
| Busca ampla em código | `grep_search` + múltiplos reads | `ctx_batch_execute` + `queries` |
| Arquivo grande para análise | `read_file` completo | `ctx_execute_file` |
| Docs/web externa | fetch/manual | `ctx_fetch_and_index` + `ctx_search` |
| Indexação de payload grande | `ctx_index(content: ...)` | `ctx_index(path: ...)` |
| Arquivo-fonte > 300 linhas OU > 20KB, para reduzir contexto | Ler/anexar conteúdo bruto ao chat | `run_subagent(agentName: "code-summarizer")`, depois anexar o resumo retornado |
| Mapear código-fonte de projeto para busca | Varredura com grep/find/cat no terminal | `ctx_index(path: "<projeto>/src", source: "code:<project-id>", exclude: [...])` |

## 3.1) Padrão de Indexação de Código-Fonte de Projetos (`code:<project-id>`)

Para evitar que agents leiam arquivos repetidamente ou recorram ao terminal (`find`, `grep`, scripts Node), projetos registrados devem ter sua pasta de código (`src/` ou equivalente) indexada no Knowledge Base (FTS5):

- **Chave canônica (`source`)**: `code:<project-id>` (ex.: `code:deep-agents-copilot`).
- **Caminho (`path`)**: subpasta de código real (ex.: `<raiz>/src`), **nunca a raiz cega do projeto** (para evitar `.git`, `node_modules`, `dist`, `.angular`).
- **Exclusões obrigatórias (`exclude`)**: `["**/*.spec.ts", "**/*Test.java", "**/assets/**", "**/environments/**", "**/dist/**", "**/node_modules/**"]`.
- **Hard cap de arquivos (`maxFiles`)**: padrão seguro `200` para proteger contra blow-up do FTS5.
- **Consumo posterior**: qualquer busca de código semântica ou estrutural usa:
  ```javascript
  ctx_search({
    source: "code:<project-id>",
    queries: ["nomeDaClasse", "padrao arquitetural", "metodo"]
  })
  ```
- **Detecção de alteração (Staleness / Frescor de cache)**:
  - O `context-mode` armazena o hash SHA-256 de cada arquivo indexado. Se você alterar o arquivo no disco, o `ctx_search` sinaliza o trecho com a flag `[STALE / OUTDATED]`.
  - **Regra de Ouro (Search para Descobrir, Read para Editar)**: O `ctx_search` serve como mapa de localização. Antes de editar qualquer arquivo, o agent deve obrigatoriamente reler o arquivo real com `read_file` para garantir que está aplicando a mudança sobre a versão mais recente em disco.
  - Para reindexar após grandes alterações: basta chamar `ctx_index` novamente sobre a mesma subpasta e `source` (recalculo incremental rápido).

## 3.2) Leitura Cirúrgica vs. Agregação em Sandbox (R-048)

A regra **R-048** estabelece critérios objetivos para evitar o tráfego desnecessário de conteúdo bruto na memória conversacional:
- **`read_file(offset, limit)` (Leitura Pontual/Pequena)**: Utilize quando o objetivo for inspecionar ou preparar uma edição localizada após encontrar a linha via `grep_search`. A janela útil recomendada é de 60 a 80 linhas. Nunca leia o arquivo integralmente (>100 linhas) apenas para editar uma função ou método isolado.
- **`ctx_execute_file` (Agregação/Processamento de Arquivo Grande)**: Utilize quando o arquivo for extenso (>300 linhas ou logs) e o objetivo for sumarizar, extrair métricas, filtrar padrões ou responder perguntas analíticas sem necessidade de edição direta no editor. O arquivo é processado dentro do sandbox e apenas o resultado sintetizado retorna ao chat.

## 4) Guardrails de economia (token budget)

- Sempre agrupar perguntas no mesmo `queries: [...]`.
- Sempre informar `source` quando houver múltiplas fontes indexadas.
- Em `ctx_batch_execute`, preferir `query_scope: "batch"` quando o foco for apenas a coleta atual.
- Não imprimir JSON bruto no stdout; imprimir resumo, contagem, IDs e evidência objetiva.
- Persistir saída extensa em arquivo e retornar somente caminho + 1 linha de descrição.

## 5) Terminal e fallback

- Terminal só para: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`.
- Se MCP estiver indisponível: reportar falha compacta e aguardar aprovação antes de fallback amplo.

## 6) Anti-padrões (proibidos)

- Rodar comando verboso em terminal só para "ver rapidamente".
- Fazer várias chamadas `ctx_search` unitárias para perguntas relacionadas.
- Passar dados grandes em `ctx_index(content)`.
- Reindexar no `ctx_index(content)` uma resposta já recebida por outra tool.
- Ler arquivo grande com `read_file` quando a intenção é apenas analisar.

> **Exceção ao guardrail de `ctx_index(content)`:** resumos gerados por `@code-summarizer` podem ser indexados via `ctx_index(content: "<resumo>", source: "summary:<projeto>/<caminho>")` — o guardrail acima proíbe indexar *payload bruto grande*, não o resumo em si (pequeno por definição). Consumo via `ctx_search(source: "summary:<projeto>", queries: [...])`.

## 7) Playbooks curtos

**Retomada de sessão**

```javascript
ctx_search({
  queries: ["summary", "decision", "blocker"],
  sort: "timeline"
})
```

**Coleta + resposta em lote**

```javascript
ctx_batch_execute({
  commands: [{ label: "service", command: "rg -n \"class .*Service\" src" }],
  queries: ["serviços críticos", "pontos de risco"],
  query_scope: "batch"
})
```

**Análise de arquivo grande**

```javascript
ctx_execute_file({
  path: "logs/app.log",
  language: "javascript",
  code: "const errs=FILE_CONTENT.split('\\n').filter(l=>l.includes('ERROR')); console.log(errs.length);"
})
```

## 8) Comandos ctx (atalhos)

| Comando | Ação |
|---|---|
| `ctx stats` | chamar `ctx_stats` e exibir saída completa |
| `ctx doctor` | chamar `ctx_doctor`, executar comando retornado e reportar checklist |
| `ctx upgrade` | chamar `ctx_upgrade`, executar comando retornado e reportar checklist |
| `ctx purge` | chamar `ctx_purge(confirm: true)` com aviso explícito de destruição |

## 9) Recursos

- `./examples/hierarquia-ferramentas.md`
- `docs/agent-context/context-mode.md`
- Context Engineering (Sourcegraph, 2026): https://sourcegraph.com/blog/context-engineering
- Long Context Management (Zylos, 2026): https://zylos.ai/research/2026-01-19-llm-context-management

## 10) Dimensões de Memória: Short-Term vs Long-Term

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
