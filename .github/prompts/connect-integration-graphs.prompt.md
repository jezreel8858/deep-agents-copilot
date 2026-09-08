---
name: connect-integration-graphs
description:
  Audita integrações cross-repo entre projetos já registrados — levanta contratos/endpoints
  expostos e consumidos por projeto, varre o grafo de conhecimento existente restrito apenas
  aos arquivos do fluxo de integração, e aplica as fronteiras (`manifesto.boundaries`) que
  faltam em `.codegraphrc.json` até fechar todo gap identificado. Requer projetos já
  registrados via `/add-project-context`; nunca escreve em `catalog.yaml` (compartilhado).
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'grep_search', 'file_search', 'list_dir', 'run_subagent', 'ask_questions', 'context-mode/ctx_search', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_index']
argument-hint: '[repositório-alvo]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - docs/ai-context/catalog.yaml
  - docs/ai-context/catalog.local.yaml.example
  - .github/agents/tech-solution-architect.agent.md
  - .github/agents/code-knowledge-graph.agent.md
  - .github/skills/integration-contract-analysis/SKILL.md
  - .github/skills/codegraph-optave-usage/SKILL.md
---

# `/connect-integration-graphs`

> **Propósito**: fechar o ciclo de integração cross-repo entre projetos já registrados — (1) levantar
> em detalhe quais repositórios possuem integração (contratos, endpoints, filas), (2) confirmar
> estruturalmente essa integração varrendo o grafo de conhecimento **já existente**, restrito somente
> aos arquivos do fluxo de integração, e (3) aplicar as fronteiras (`manifesto.boundaries`) que
> ainda faltam, até que nenhum grafo do ecossistema tenha gap de integração pendente.
> **Workspace**: `${workspaceFolder}`
>
> **NÃO faz**: não implementa/corrige código de aplicação; não reconstrói grafo já cacheado; não
> escreve em `docs/ai-context/catalog.yaml` (compartilhado, R-043); não é o fluxo de registro de
> um projeto novo (isso é `/add-project-context`, FASE 4.1) — este prompt roda **depois**, sobre o
> conjunto já registrado, para auditar/fechar o que a FASE 4.1 não perguntou/pegou naquele momento.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** mapear fronteiras de integração multi-repo (`manifesto.boundaries`) em `.codegraphrc.json`.
- ✅ **SEMPRE** preservar isolamento local e respeitar o grafo construído pelo `@code-knowledge-graph`.
- ❌ **NÃO** implementar código ou alterar endpoints em serviços da aplicação.
- ❌ **NÃO** escrever em `docs/ai-context/catalog.yaml` (compartilhado, R-043).

---

---

## 🎯 Uso

```bash
/connect-integration-graphs                            → varre todos os projetos registrados (catalog.yaml + catalog.local.yaml)
/connect-integration-graphs <projeto-A> <projeto-B>     → escopo restrito a um par/subconjunto de projetos
```

---

## CRÍTICO

- ❌ NÃO implementar/corrigir código de aplicação nos projetos analisados.
- ❌ NÃO escrever em `docs/ai-context/catalog.yaml` (compartilhado) — projetos vivem em `catalog.local.yaml` (R-043); esta é leitura apenas.
- ❌ NÃO reconstruir grafo do zero se já existir cache válido — sempre delegar a `@code-knowledge-graph`, que verifica hash/cache antes de reprocessar (RNF-002).
- ❌ NÃO editar `.codegraphrc.json` de nenhum projeto sem confirmação explícita via `ask_questions` (R-009) — é mudança estrutural em projeto(s) externo(s).
- ❌ NÃO afirmar que uma integração existe sem evidência dupla: (a) declarada no levantamento de contrato (FASE 1) **e** (b) confirmada pela aresta real no grafo (FASE 2) — divergência é gap de evidência, não integração fechada.
- ✅ APENAS consultar contratos/endpoints/grafo existentes e propor/aplicar as fronteiras que fecham gaps reais.
- ✅ SEMPRE delegar levantamento de contrato/integração a `@tech-solution-architect` e consulta/validação de grafo a `@code-knowledge-graph` via `run_subagent` — nunca duplicar a lógica desses agents aqui (R-003).

---

## 📋 Fluxo

### FASE 1 — Levantamento de Integrações (Survey)

1. Ler `docs/ai-context/catalog.yaml` + `docs/ai-context/catalog.local.yaml` (merge em memória — nunca escrever no compartilhado) para obter a lista de projetos registrados no ecossistema.
2. Para cada projeto (ou apenas o subconjunto informado como argumento), delegar o levantamento detalhado:

```
run_subagent(
  agentName: "tech-solution-architect",
  description: "Levantar integrações expostas/consumidas do projeto <nome>",
  task: "Analisar contratos de integração (OpenAPI/AsyncAPI/gRPC/GraphQL, HTTP clients, filas)
         do projeto <nome> (path_externo em catalog.local.yaml). Retornar lista estruturada:
         endpoints/tópicos expostos, endpoints/tópicos consumidos, projeto(s) contraparte
         identificado(s) por evidência (arquivo:linha), e classificação BREAKING|COMPATIBLE|N-A
         quando houver contrato versionado."
)
```

3. Consolidar o resultado em uma matriz de integração por par de projetos (quem expõe → quem consome) — este é o "máximo de informação" exigido, com evidência rastreável por linha.

### FASE 2 — Varredura Restrita via Grafo Existente

1. A partir da matriz da FASE 1, extrair somente os arquivos/símbolos identificados como ponto real de integração (controller/client que expõe ou consome o contrato) — nunca todo o projeto.
2. Delegar a consulta ao grafo **já construído** (nunca reconstruir sem necessidade real):

```
run_subagent(
  agentName: "code-knowledge-graph",
  description: "Consultar grafo existente restrito ao fluxo de integração de <nome>",
  task: "RF-002 (sob demanda). project-id=<nome>. Verificar cache code-graph:<nome>:* antes de
         reprocessar. Consultar apenas os símbolos/arquivos levantados na FASE 1 (fn-impact/
         query/dataflow -T) para confirmar a aresta estrutural real entre os pontos de
         integração informados. Não varrer o projeto inteiro — escopo restrito à lista de
         arquivos informada."
)
```

3. Reter apenas o resultado que confirme (ou refute) a integração declarada na FASE 1 — se o grafo não confirmar a aresta esperada, sinalizar como **gap de evidência** (diferente do gap de fronteira tratado na FASE 3), nunca assumir a integração como fechada só pela FASE 1.

### FASE 3 — Fechar as Pontes Faltantes (`manifesto.boundaries`)

1. Cruzar a matriz confirmada (FASE 1 + FASE 2) com o estado atual de `.codegraphrc.json` de cada projeto envolvido (`read_file` se o arquivo existir).
2. Para cada par de projetos com integração confirmada e **sem** `manifesto.boundaries` correspondente em `.codegraphrc.json` → é um gap de fronteira.
3. Apresentar via `ask_questions` a lista de gaps encontrados, com a opção de aplicar automaticamente cada ponte (`modules` + `rules`) — mesma estrutura de `.codegraphrc.json` já usada em `/add-project-context` FASE 4.1:

```json
{
  "manifesto": {
    "boundaries": {
      "modules": {
        "<projeto-consumidor>": "src/**",
        "<projeto-provedor>": "<path_externo-do-outro-projeto>/src/**"
      },
      "rules": [
        { "from": "<projeto-consumidor>", "onlyTo": ["<projeto-provedor>"] }
      ]
    }
  }
}
```

4. Se confirmado, aplicar a edição em `.codegraphrc.json` do(s) projeto(s) envolvido(s) e validar:

```
run_subagent(
  agentName: "code-knowledge-graph",
  description: "Validar fronteiras aplicadas para <nome>",
  task: "RF-002. Rodar codegraph check --staged --boundaries no projeto <nome> após atualização
  de .codegraphrc.json; reportar resultado do gate."
)
```

5. Repetir para todos os pares até que nenhum gap remanescente exista — reportar explicitamente se algum gap não pôde ser fechado (ex.: projeto sem `path_externo` acessível) e qual é o próximo passo mínimo para fechá-lo depois.

### FASE 4 — Geração do Visualizador Interativo Unificado (Material 3)

1. Após fechar e validar as fronteiras, invocar automaticamente o generator visual no diretório central de ferramentas:
```bash
python tools/codegraph-visualizer/generator/generate-graph.py --output "tools/codegraph-visualizer/dist/index.html"
```
2. O generator carrega as pontes REST registradas em `tools/codegraph-visualizer/bridges.json`, compila a visualização 2D/3D em Angular Material 3 com filtros de conectividade (isolados, papéis, camadas e multi-select de repositórios).
3. Entregar o link e caminho absoluto do artefato HTML centralizado (`tools/codegraph-visualizer/dist/index.html`) ao usuário como evidência visual interativa.

### Formato de Saída

```
Levantamento (FASE 1):
- Projetos considerados: <lista>
- Matriz de integração: <par> — <expõe>/<consome> — evidência: <arquivo:linha>

Varredura restrita (FASE 2):
- Arestas confirmadas no grafo: <par> ✅ | gap de evidência: <par> ⚠️

Pontes fechadas (FASE 3):
- <par> — manifesto.boundaries aplicado em .codegraphrc.json ✅ | pendente (motivo) ⚠️
- codegraph check --boundaries: ✅/❌ por projeto

Visualização Unificada (FASE 4):
- Artefato interativo gerado: <caminho-absoluto-do-html> ✅
- Estatísticas do Grafo: <N> nós | <N> arestas | <N> pontes REST mapeadas

Resultado final: <N> gaps fechados / <N> gaps remanescentes (com próximo passo mínimo)
```

---

## ✅ Checklist Antes de Apresentar

- [ ] Todos os projetos registrados (merge `catalog.yaml` + `catalog.local.yaml`) foram considerados no levantamento — ou apenas o subconjunto explicitamente informado no argumento.
- [ ] Levantamento de integração delegado a `@tech-solution-architect` com evidência (arquivo:linha) por conclusão.
- [ ] Varredura de grafo restrita apenas aos arquivos/símbolos do fluxo de integração (nunca full-scan) e delegada a `@code-knowledge-graph`.
- [ ] Cache `code-graph:*` reaproveitado quando válido (sem reconstrução redundante — RNF-002).
- [ ] Gaps de fronteira (`manifesto.boundaries`) apresentados via `ask_questions` antes de qualquer escrita em `.codegraphrc.json`.
- [ ] Nenhuma escrita em `docs/ai-context/catalog.yaml` (compartilhado — R-043).
- [ ] Relatório final declara: 0 gaps remanescentes, ou lista explícita dos que não puderam ser fechados + próximo passo mínimo.
- [ ] **Confirmado: nenhuma operação destrutiva (edição de `.codegraphrc.json`) executada sem confirmação.**

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** aplicar `.codegraphrc.json` sem confirmação explícita via `ask_questions` — mudança estrutural em projeto(s) externo(s).
- ❌ **NUNCA** reconstruir grafo já cacheado — sempre checar `code-graph:*` antes (delegado a `@code-knowledge-graph`).
- ❌ **NUNCA** escrever em `catalog.yaml` compartilhado (R-043) — apenas leitura.
- ❌ **NUNCA** declarar integração "confirmada" apoiado só na FASE 1 (contrato) sem a confirmação estrutural da FASE 2 (grafo).
- ✅ **APENAS** reportar e aplicar pontes após aprovação explícita do usuário.

---

## 🔄 Combina Com

```
/add-project-context → /connect-integration-graphs → /validate
```

- `/add-project-context` → pré-requisito: os projetos precisam estar registrados em `catalog.local.yaml` antes desta varredura; a FASE 4.1 daquele prompt já cobre a pergunta de integração no momento do registro de **um** projeto novo — este prompt audita/fecha o que ficou pendente para **todo** o conjunto já registrado.
- `@tech-solution-architect` → consumido via `run_subagent` para o levantamento de contratos/integrações (FASE 1).
- `@code-knowledge-graph` → consumido via `run_subagent` para consulta e validação restrita do grafo já existente (FASE 2/3).
- `/validate` → depois de fechar as pontes, validar a conformidade estrutural do ecossistema como um todo.

---

> **Notas de manutenção**: este prompt não introduz lógica nova de análise de contrato nem de
> motor de grafo — apenas orquestra `@tech-solution-architect` e `@code-knowledge-graph`, já
> especializados nesses dois domínios, evitando duplicação (R-003). Projetos sem `path_externo`
> acessível no momento da execução são reportados como gap remanescente, nunca ignorados
> silenciosamente.

*v1.0 — connect-integration-graphs prompt — 2026-09-04*

