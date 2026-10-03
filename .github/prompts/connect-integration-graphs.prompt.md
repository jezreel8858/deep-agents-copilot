---
name: connect-integration-graphs
description: >-
  Audita integrações cross-repo entre projetos já registrados — levanta contratos/endpoints
  expostos e consumidos por projeto, varre o grafo de conhecimento existente restrito apenas
  aos arquivos do fluxo de integração, e aplica as fronteiras (`manifesto.boundaries`) que
  faltam em `.codegraphrc.json` até fechar todo gap identificado. Requer projetos já
  registrados via `/add-project-context`; nunca escreve em `catalog.yaml` (compartilhado).
agent: 'agent'
model: "Claude Sonnet 5"
tools: ['read_file', 'grep_search', 'file_search', 'list_dir', 'run_subagent', 'ask_questions', 'context-mode/ctx_search', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_index']
argument-hint: '[repositório-alvo]'
source_docs:
  - .github/instructions/README.md
  - .github/projects.local.yaml.example
  - .github/agents/tech-solution-architect.agent.md
  - .github/agents/codegraph-engine.agent.md
  - .github/skills/integration-contract-analysis/SKILL.md
  - .github/skills/codegraph-optave-usage/SKILL.md
  - .github/skills/efficient-batch-code-modification/SKILL.md
  - .github/skills/handoff-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
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
> escreve em `.github/instructions/README.md` (compartilhado, R-043); não é o fluxo de registro de
> um projeto novo (isso é `/add-project-context`, FASE 4.1) — este prompt roda **depois**, sobre o
> conjunto já registrado, para auditar/fechar o que a FASE 4.1 não perguntou/pegou naquele momento.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** mapear fronteiras de integração multi-repo (`manifesto.boundaries`) em `.codegraphrc.json`, consultando contratos/endpoints/grafo existentes e propondo/aplicando as fronteiras que fecham gaps reais.
- ✅ **SEMPRE** preservar isolamento local e respeitar o grafo construído pelo `@codegraph-engine`.
- ✅ **SEMPRE** delegar levantamento de contrato/integração a `@tech-solution-architect` e consulta/validação de grafo a `@codegraph-engine` via `run_subagent` — nunca duplicar a lógica desses agents aqui (R-003).
- ❌ **NÃO** implementar ou corrigir código nem alterar endpoints em serviços da aplicação nos projetos analisados.
- ❌ **NÃO** escrever em `.github/instructions/README.md` nem em `catalog.yaml` (compartilhados, R-043) — projetos vivem em `projects.local.yaml`; leitura apenas.
- ❌ **NÃO** reconstruir grafo do zero se já existir cache válido — sempre checar `code-graph:*` antes via `@codegraph-engine` (RNF-002).
- ❌ **NÃO** editar ou aplicar `.codegraphrc.json` de nenhum projeto sem confirmação explícita via `ask_questions` (R-009) — é mudança estrutural em projeto(s) externo(s).
- ❌ **NÃO** afirmar que uma integração existe sem evidência dupla: (a) declarada no levantamento de contrato (FASE 1) **e** (b) confirmada pela aresta real no grafo (FASE 2) — divergência é gap de evidência, não integração fechada.

---

## 🎯 Uso

```bash
/connect-integration-graphs                            → varre todos os projetos registrados (catalog.yaml + projects.local.yaml)
/connect-integration-graphs <projeto-A> <projeto-B>     → escopo restrito a um par/subconjunto de projetos
```

---

## 📋 Fluxo

### FASE 1 — Levantamento de Integrações (Survey)

1. Ler `.github/instructions/README.md` + `.github/projects.local.yaml` (merge em memória — nunca escrever no compartilhado) para obter a lista de projetos registrados no ecossistema.
2. Para cada projeto (ou apenas o subconjunto informado como argumento), delegar o levantamento detalhado:

```
run_subagent(
  agentName: "tech-solution-architect",
  description: "Levantar integrações expostas/consumidas do projeto <nome>",
  task: "Analisar contratos de integração (OpenAPI/AsyncAPI/gRPC/GraphQL, HTTP clients, filas)
         do projeto <nome> (path_externo em projects.local.yaml). Retornar lista estruturada:
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
  agentName: "codegraph-engine",
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
   - **Padrão de Edição Segura Verificada (R-051)**: a edição de `.codegraphrc.json` (arquivo JSON, sintaxe sensível a indentação) deve seguir o padrão R-051, verificando unicidade da âncora antes de escrever e revalidando a sintaxe após a escrita.
   - **Lote Consolidado (R-046)**: se houver 2+ projetos com gap de fronteira pendente, consolidar todas as edições em uma única chamada de lote via `ctx_execute`/`ctx_batch_execute` (R-046) — nunca projeto por projeto sequencialmente no chat.
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
  agentName: "codegraph-engine",
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

- [ ] Todos os projetos registrados (merge `catalog.yaml` + `projects.local.yaml`) foram considerados no levantamento — ou apenas o subconjunto explicitamente informado no argumento.
- [ ] Levantamento de integração delegado a `@tech-solution-architect` com evidência (arquivo:linha) por conclusão.
- [ ] Varredura de grafo restrita apenas aos arquivos/símbolos do fluxo de integração (nunca full-scan) e delegada a `@codegraph-engine`.
- [ ] Cache `code-graph:*` reaproveitado quando válido (sem reconstrução redundante — RNF-002).
- [ ] Gaps de fronteira (`manifesto.boundaries`) apresentados via `ask_questions` antes de qualquer escrita em `.codegraphrc.json`.
- [ ] Nenhuma escrita em `.github/instructions/README.md` (compartilhado — R-043).
- [ ] Relatório final declara: 0 gaps remanescentes, ou lista explícita dos que não puderam ser fechados + próximo passo mínimo.
- [ ] **Confirmado: nenhuma operação destrutiva (edição de `.codegraphrc.json`) executada sem confirmação.**

---

> Regras de autonomia consolidadas no bloco 🛑 CRÍTICO no topo deste arquivo.

---

## 🔄 Combina Com

```
/add-project-context → /connect-integration-graphs → /validate
```

- `/add-project-context` → pré-requisito: os projetos precisam estar registrados em `projects.local.yaml` antes desta varredura; a FASE 4.1 daquele prompt já cobre a pergunta de integração no momento do registro de **um** projeto novo — este prompt audita/fecha o que ficou pendente para **todo** o conjunto já registrado.
- `@tech-solution-architect` → consumido via `run_subagent` para o levantamento de contratos/integrações (FASE 1).
- `@codegraph-engine` → consumido via `run_subagent` para consulta e validação restrita do grafo já existente (FASE 2/3).
- `/validate` → depois de fechar as pontes, validar a conformidade estrutural do ecossistema como um todo.

---

> **Notas de manutenção**: este prompt não introduz lógica nova de análise de contrato nem de
> motor de grafo — apenas orquestra `@tech-solution-architect` e `@codegraph-engine`, já
> especializados nesses dois domínios, evitando duplicação (R-003). Projetos sem `path_externo`
> acessível no momento da execução são reportados como gap remanescente, nunca ignorados
> silenciosamente.
>
> **Escalonamento de modelo (R-021.1)**: este prompt é fixado em `Claude Sonnet 5` devido ao
> fan-out não limitado a priori sobre todos os projetos registrados no ecossistema e à
> necessidade de reconciliação analítica estrita entre duas fontes de evidência independentes
> (contratos/código via FASE 1 e arestas reais do grafo via FASE 2) antes de declarar qualquer
> integração fechada.

*v1.0 — connect-integration-graphs prompt — 2026-09-04*

<execution_protocol>
**Protocolo Plan-Then-Batch (Smell 2.26 / Smell 2.13 / R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`.
3. **DESPACHAR & VALIDAR**: Aplique todas as mutações ou leituras em processo único no sandbox (all-or-nothing verificado, R-051) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
4. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
5. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions, vedando loops investigativos de dívida de tokens O(N²).
6. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).
8. **Progressive Disclosure de `source_docs_lazy:` (R-066 — Anti Context Bloat Inicial)**: Se este agent declara `source_docs_lazy:` em seu próprio frontmatter, esses documentos (ex.: `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/agents/workflows.md`) **NÃO foram pré-carregados** — é TERMINANTEMENTE PROIBIDO usar `read_file` para carregá-los por inteiro. Consulte-os exclusivamente via `context-mode/ctx_search` com query pontual (ex.: número da regra `R-xxx` ou nome da seção) apenas quando precisar citá-los; nunca "só por garantia".
</execution_protocol>
