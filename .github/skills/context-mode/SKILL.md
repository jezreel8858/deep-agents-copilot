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
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# context-mode — Operação de alto rendimento

Skill para operar `ctx_*` com mínimo consumo de contexto: coletar em lote, processar em sandbox e responder apenas com sinal útil.

## 1) Objetivo

- Evitar flooding de contexto em tarefas de análise e investigação.
- Transformar saída bruta em resultado compacto e acionável.
- Preservar histórico consultável para sessões longas.
- Reduzir custo de créditos por chamada desnecessária ou redundante.

> **Princípio Arquitetural de Assimetria (Input vs. Output Context):**
> O `context-mode` soluciona a exaustão de contexto no lado do **output** (suprime o retorno de dados brutos de ferramentas, logs e inspeções). Ele **não** reduz o custo de tokens no lado do **input** (definições e schemas JSON de ferramentas carregadas no prompt do sistema). Para conter o overhead de input, combine esta skill com desativação seletiva de MCP servers não utilizados na sessão.

> **Framing Assimétrico Obrigatório entre `ctx_execute` e `ctx_batch_execute` (reforço comportamental, complementar ao hook de § 4.1.1):**
> Trate mentalmente `ctx_batch_execute` como a ferramenta **DEFAULT** para qualquer tarefa com 2+ alvos/comandos, e `ctx_execute` isolado como uma **exceção pontual de 1 único uso exploratório** por fase de tarefa — nunca uma rota alternativa igualmente válida. Pesquisa da própria Anthropic confirma que modelos (incl. os mais fortes) tendem a preferir o caminho mais simples disponível quando nada no enunciado da tarefa reforça explicitamente a simultaneidade; por isso, ao planejar, formule o objetivo internamente como "fazer X e Y e Z **simultaneamente em uma única chamada**", nunca como uma lista sequencial de passos.

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
| Mapear código-fonte de projeto para busca | Varredura com grep/find/cat no terminal | `ctx_index(path: "<projeto>/src", source: "code:<project-id>", exclude: [...])` |
| Chamada HTTP externa / consulta API | `curl`, `wget` ou fetch via terminal | `ctx_fetch_and_index` (HTML/docs) ou `fetch()` em `ctx_execute` |
| Snapshot de testes / dumps (ex.: Playwright) | Dump bruto no stdout/chat | Gravação em arquivo (`filename`) + `ctx_execute_file` |

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


## 3.3) Padrão `CONTEXT.md` (Glossário de Domínio Compartilhado para Compressão Semântica)

Recomenda-se manter um arquivo `CONTEXT.md` na raiz ou em `docs/` (baseado no template canônico `docs/agent-context/templates/CONTEXT.template.md`) em projetos gerenciados:
- **Objetivo**: Fixar termos canônicos, acrônimos, anti-termos e invariantes de negócio não-negociáveis.
- **Benefício**: Proporciona "compressão semântica de tokens", evitando que humanos precisem re-explicar conceitos de domínio complexos a cada sessão conversacional.
- **Uso com context-mode**: O arquivo deve ser indexado sob `source: "domain:context-glossary"` para que o agente utilize `ctx_search` para desambiguação rápida e instantânea de regras e terminologias de domínio antes de propor soluções ou blueprints.

## 3.4) Padrão para Snapshots e Payloads Volumosos de Terceiros (ex.: Playwright / Profilers)

Ferramentas de automação e observabilidade (como Playwright, profilers de memória e dumps de rede) geram dezenas de kilobytes de dados estruturais que degradam a janela conversacional se emitidos no stdout:

1. **Gravação Compulsória em Arquivo**: Ao disparar comandos dessas ferramentas, utilize parâmetros de persistência em disco (ex.: `--output`, `--filename` ou redirecionamento de stream).
2. **Processamento em Sandbox**: Inspecione o artefato resultante exclusivamente através de `ctx_execute_file`, extraindo métricas específicas (ex.: status de asserções, falhas de seletores, nós DOM críticos).
3. **Redução de Impacto**: Garante que capturas volumosas (ex.: snapshot de 56 KB) entrem no contexto do modelo resumidas a métricas pontuais (menos de 300 bytes), preservando a estabilidade da sessão.

## 4) Guardrails de economia (token budget)

- **Single-Turn MCP Batching Compulsório (Smell 2.26)**: É terminantemente proibido encadear múltiplas chamadas unitárias de `ctx_execute` no chat para analisar múltiplos alvos; usar compulsoriamente `ctx_batch_execute(commands, queries)` em rodada única OU um script síncrono consolidado em `ctx_execute`.
- **Regra do Limiar >= 2 (Anti Tool Chaining — Smell 2.26 / R-059):** SE o escopo da tarefa exigir inspecionar, ler, comparar, editar ou executar 2 (DOIS) OU MAIS arquivos/comandos/alvos, é TERMINANTEMENTE PROIBIDO disparar `ctx_execute` isolado por alvo em chamadas/turnos sucessivos. É OBRIGATÓRIO: (a) `ctx_batch_execute(commands, queries)` com todos os alvos rotulados em uma única chamada, OU (b) um único script iterativo em `ctx_execute` que processe todos os alvos em loop interno e imprima o resumo consolidado de uma só vez. Antes de disparar a primeira chamada de ferramenta, o agente DEVE enumerar mentalmente TODOS os alvos necessários para completar a tarefa (Plan-Then-Batch, ver abaixo) — nunca descobrir o próximo alvo reativamente turno-a-turno.
- **Protocolo Plan-Then-Batch (Anti Miopia Reativa — Smell 2.13 / R-059):**
  1. **ENUMERAR**: antes de qualquer tool call, liste internamente todos os arquivos/comandos que compõem a tarefa completa (não apenas o próximo passo aparente).
  2. **CONSOLIDAR**: se a lista tiver >= 2 itens, agrupe tudo em uma única payload (`commands[]` em `ctx_batch_execute` ou loop único em `ctx_execute`).
  3. **DESPACHAR**: dispare apenas 1 chamada de ferramenta de leitura/processamento por fase da tarefa — nunca N chamadas sequenciais para N alvos previsíveis.
  4. **Comandos curtos não suspendem a regra**: prompts do usuário como "prosseguir", "continue", "pode seguir" NÃO isentam o agente da obrigatoriedade de context-mode nem do limiar >= 2 — a obrigação é da TAREFA em andamento, não do tamanho do prompt do turno atual.
  *(SSOT Normativa: `.github/copilot-instructions.md` § 2.1; diretrizes de batching em `.github/skills/efficient-batch-code-modification/SKILL.md`)*.
- **Concorrência Otimizada para I/O (`concurrency: 4-8`)**: Em operações I/O-bound (múltiplas requisições web em `ctx_fetch_and_index` ou consultas paralelas de rede em `ctx_batch_execute`), utilize `concurrency: 4` a `8`. Mantenha `concurrency: 1` para comandos com contenção de CPU, locks de pacotes ou escrita concorrente em disco.
- **Single-Turn Query Aggregation**: Ao consultar o índice persistente após uma coleta, consolide todas as dúvidas em um único array no parâmetro `queries: [...]`. É proibido disparar múltiplos turnos de `ctx_search` contendo uma única pergunta por turno.
- Sempre informar `source` quando houver múltiplas fontes indexadas.
- Em `ctx_batch_execute`, preferir `query_scope: "batch"` quando o foco for apenas a coleta atual.
- Não imprimir JSON bruto no stdout; imprimir resumo, contagem, IDs e evidência objetiva.
- Persistir saída extensa em arquivo e retornar somente caminho + 1 linha de descrição.

### 4.1) Circuit Breaker de Tool-Chaining Sequencial (Anti-Loop de `ctx_execute` no Chat)

Para conter a degradação de contexto e a queima descontrolada de créditos provocadas por tool-chaining sequencial (Smell 2.26 / incidente docs-engineer), todo agente que utilize o context-mode DEVE observar o seguinte mecanismo comportamental de corte:

- **Regra Objetiva de Corte**: Se o agente detectar em seu histórico de chamadas do turno/ciclo que já executou **2 (duas) chamadas consecutivas de `ctx_execute` ou `ctx_execute_file`** sem uma chamada interposta de `ctx_batch_execute`, o Circuit Breaker é compulsoriamente acionado (`state: OPEN`).
- **Ação Imediata (Interrupção & Consolidação)**: O agente DEVE interromper imediatamente a próxima chamada isolada e reconsolidar TODOS os alvos e comandos restantes em uma única chamada de `ctx_batch_execute(commands, queries)` (ou script unificado no sandbox) antes de prosseguir.
- **Transição de Estados**:
  - `CLOSED` (Operação Normal): Uso de `ctx_batch_execute` ou até 1 chamada exploratória pontual isolada.
  - `OPEN` (Disparado): 2 chamadas consecutivas de `ctx_execute`/`ctx_execute_file` sem lote interposto. É **terminantemente proibido** disparar a 3ª chamada unitária no chat. O agente deve reagrupar os alvos pendentes em lote ou emitir síntese conclusiva com o que foi coletado até então.
- **Enforcement em Duas Camadas (Behavioral + Mecânico)**: Esta seção descreve a camada **comportamental** (prompt-level, probabilística). A partir de 2026-10, existe também uma camada **mecânica** real no harness — ver § 4.1.1. Agents devem obedecer a ambas; a camada comportamental continua sendo a primeira linha de defesa (evita até chegar a precisar do bloqueio mecânico).
- **Precedente Arquitetural**: Alinhado ao padrão de Circuit Breaker Stateful de subagentes formalizado em `.github/skills/handoff-governance/SKILL.md` § 2.4.

#### 4.1.1) Enforcement Mecânico via PreToolUse Hook (Complemento Determinístico ao Circuit Breaker)

Instrução prompt-only é **probabilística**, não determinística — nenhum nível de ênfase textual garante compliance de 100% dos modelos em 100% das tarefas (comportamento documentado também em modelos fortes, não só em modelos compactos). Por isso, além da regra comportamental acima, este repositório mantém uma camada **mecânica** real: um hook `PreToolUse` (`.github/hooks/ctx-sequence-guard.ps1` / `.sh`) que conta chamadas consecutivas de `ctx_execute`/`ctx_execute_file` e retorna `{"permissionDecision":"deny", ...}` ao atingir 2 chamadas sem `ctx_batch_execute` interposto — bloqueio real, independente da decisão do modelo.

- **Reação esperada a um `deny` deste hook**: tratar como feedback automatizado corrigível (equivalente a erro de lint/CI) — replanejar imediatamente com `ctx_batch_execute` e prosseguir, **nunca** parar ou pedir confirmação ao usuário.
- **Fail-open absoluto**: qualquer erro interno do hook sempre resulta em `allow` — a camada mecânica nunca é causa de bloqueio indevido.
- **Cobertura Conhecida e Incompleta (Escopo = agente raiz, não subagents)**: hosts com arquitetura de hooks derivada do padrão `preToolUse` têm precedente documentado de **não interceptar tool calls originadas de dentro de um subagent** (delegação via `run_subagent`/`task`), apenas as do agente principal do turno. Nesse caso, a camada mecânica **não cobre** subagents, e a camada comportamental (§ 4.1) permanece a **única linha de defesa real** para chamadas `ctx_execute` feitas a partir de um subagent delegado — reforce-a com atenção redobrada nesse contexto específico.
- **Detalhes de implementação, limitações por host e histórico de diagnóstico**: ver `.github/hooks/README.md` (documento técnico de operação dos hooks). Problemas específicos de IDE/host (ex.: JetBrains) ficam em `docs/context/setup-context-mode-intellij.md`.

### 4.2) Mitigação Mandatória de Diretório de Execução (`cwd` Explícito no Sandbox)

- **Declaração Obrigatória de `cwd`**: Ao invocar `ctx_batch_execute`, `ctx_execute` ou `ctx_execute_file` fora do diretório padrão do host (IDE), declare **sempre** o parâmetro `cwd` apontando explicitamente para a raiz do repositório-alvo (ex.: via `git rev-parse --show-toplevel` ou caminho absoluto conhecido).
- **Risco Mitigado (Anti-PathNotFound / Anti-Fallback)**: A omissão de `cwd` no payload pode fazer com que o sandbox resolva o comando relativo a partir do diretório de instalação do IDE (ex.: diretório de binários do editor no host) em vez da raiz do repositório de trabalho. Isso gera erros em cascata (`PathNotFound` / código de saída de falha), os quais induzem o agente erroneamente a assumir falha estrutural do comando em lote e incorrer em fallback indevido para chamadas sequenciais fragmentadas. Este padrão de falha foi reproduzido e comprovado em auditoria de governança sistêmica.

### 4.3) Few-Shot: Anti-Padrão vs Padrão Correto de Batching

Regra textual abstrata sozinha é insuficiente para modelos de menor capacidade de raciocínio composicional (Gemini Flash e equivalentes) em cenários de alto fan-out. Use o exemplo concreto abaixo como âncora mental antes de despachar qualquer tarefa com N ≥ 2 alvos/arquivos.

**Cenário:** tarefa pede para atualizar um trecho repetido em 6 arquivos de documentação.

❌ **Anti-padrão (proibido — MCP Tool Chaining Sequencial, Smell 2.26):**
> `ctx_execute(arquivo-1.md)` → aguarda → `ctx_execute(arquivo-2.md)` → aguarda → `ctx_execute(arquivo-3.md)` → ... (6 chamadas isoladas em turnos sucessivos, cada uma reenviando o histórico acumulado do chat)

✅ **Padrão correto (obrigatório — Plan-Then-Batch, R-059):**
> 1. ENUMERAR mentalmente os 6 alvos antes de qualquer tool call.
> 2. Emitir **UMA única chamada**: `ctx_batch_execute(commands: [{label:"arquivo-1",...}, {label:"arquivo-2",...}, ..., {label:"arquivo-6",...}], queries: [...])`.
> 3. Processar os 6 resultados retornados na mesma resposta, sem nova rodada de tool calls por arquivo.

**Regra de decisão rápida**: se ao planejar a tarefa você identificar mentalmente a palavra "próximo arquivo" ou "e depois o outro", pare — isso é o sinal de que a tarefa exige `ctx_batch_execute` com todos os alvos enumerados no mesmo payload, não uma sequência de chamadas unitárias.

### 4.4) Health Check de Adapter e Prevenção de Rota Fantasma (ROI Negativo)

Divergências de versão ou falhas de vinculação de handlers no adapter MCP do host podem registrar ferramentas de instrução sem executores reais ativos. Isso gera custo recorrente de tokens no prompt do sistema sem retorno operacional (ROI negativo documentado):

- **Verificação Preventiva**: Se ferramentas `ctx_*` falharem silenciosamente ou não produzirem saída esperada no início de uma sessão em ambiente novo, execute `ctx doctor` para certificar o emparelhamento dos binários (`cli.js`).
- **Auditoria de Utilização**: Consulte periodicamente `ctx stats` para confirmar que as chamadas foram contabilizadas pelo subsistema do context-mode e que os índices SQLite FTS5 estão operacionais.

### 4.5) Degradação Graciosa em Runtimes com Serialização Rígida de Parâmetros

Determinados hosts ou adapters (ex.: variações do OpenCode) convertem internamente todos os argumentos JSON para strings puras antes do repasse ao servidor MCP, causando falhas de validação de schema (erros Zod ao esperar `array` ou `number` em `ctx_search` ou `ctx_batch_execute`):

- **Workaround de Compatibilidade**: Ao operar em ambientes que apresentem incompatibilidade de schema Zod com arrays, priorize ferramentas com payloads de texto plano (`ctx_execute` e `ctx_fetch_and_index`), encapsulando a iteração em código scriptado dentro do sandbox até a estabilização do adapter.

## 5) Terminal e fallback

- Terminal restrito a operações de infraestrutura local: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`.
- **Proibição de Requisições Inline**: É terminantemente proibido executar `curl`, `wget` ou requisições HTTP arbitrárias via linha de comando no terminal. Utilize `ctx_fetch_and_index` para páginas/documentação ou execute `fetch()` programático dentro de `ctx_execute`.
- Se MCP estiver indisponível: reportar falha compacta e aguardar aprovação antes de fallback amplo.

## 6) Anti-padrões (proibidos)

- **MCP Tool Chaining Sequencial no Chat (Smell 2.26)**: disparar múltiplas chamadas individuais de `ctx_execute` em turnos sucessivos para investigar arquivos, diffs ou logs um a um, reenviando todo o histórico do chat a cada turno em vez de consolidar em `ctx_batch_execute` ou script único no sandbox.
- Rodar comando verboso em terminal só para "ver rapidamente".
- Fazer várias chamadas `ctx_search` unitárias para perguntas relacionadas.
- Passar dados grandes em `ctx_index(content)`.
- Reindexar no `ctx_index(content)` uma resposta já recebida por outra tool.
- Ler arquivo grande com `read_file` quando a intenção é apenas analisar.

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
  query_scope: "batch",
  cwd: "/caminho/raiz/do/repositorio"
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
| `ctx purge` | chamar `ctx_purge(confirm: true)` — Ação destrutiva irreversível. Limpa a base FTS5 SQLite e estatísticas. **Nota**: O banco do context-mode sobrevive a comandos `/clear` ou `/compact`; `ctx_purge` é a única via de reinicialização completa. |

### 8.1) Governança de Telemetria e Dashboard Organizacional (Insight)

Quando conectado a coletores ou dashboards analíticos organizacionais (ex.: Insight):

- **Política de Metadados Exclusivos (Zero-Leakage)**: O rastreamento deve coletar estritamente metadados estruturais de processo (nomes de ferramentas invocadas, caminhos de arquivo, códigos de erro e durações).
- **Proteção de Código e Conteúdo**: É vedado o envio de trechos de código-fonte, prompts do usuário, argumentos de texto livre ou conteúdos lidos de arquivos para plataformas de observabilidade externas.

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

## 10) Trade-offs Arquiteturais e Limitações Conhecidas

A transição de chamadas diretas de ferramentas (tool-calling declarativo) para execução de código intermediada por sandbox impõe compromissos operacionais:

| Dimensão | Vantagem com `context-mode` | Trade-off / Limitação |
|---|---|---|
| **Janela de Contexto** | Redução drástica de tokens (até ~98% em saídas volumosas). | Apenas suprime tokens de saída; schemas de entrada continuam pesando no prompt. |
| **Flexibilidade Analítica** | Filtragem e derivação arbitrária via código em sandbox. | Requer ambiente capaz de spawnar subprocessos locais (incompatível com runtimes restritos tipo Cloudflare Workers puros). |
| **Segurança e Isolamento** | Código é executado localmente sem vazar payloads para APIs externas. | Demanda superfície confiável de execução de comandos locais na máquina do desenvolvedor. |
| **Persistência de Memória** | Base SQLite FTS5 indexada mantém dados entre comandos `/compact`. | Exige disciplina de indexação estruturada (`source:` explícito) para evitar fragmentação de índices. |

## 11) Recursos

- `./examples/hierarquia-ferramentas.md`
- `docs/agent-context/context-mode.md`
- Context Engineering (Sourcegraph, 2026): https://sourcegraph.com/blog/context-engineering
- Long Context Management (Zylos, 2026): https://zylos.ai/research/2026-01-19-llm-context-management
- Repositório oficial `context-mode` (README, SKILL.md, SYSTEM.md): https://github.com/mksglu/context-mode
- Landing oficial / Insight dashboard: https://context-mode.com
- Post do autor (arquitetura FTS5/BM25, métricas de economia): https://mksg.lu/blog/context-mode
- Code execution with MCP (Anthropic, fundamentação do padrão "Think in Code"): https://www.anthropic.com/engineering/code-execution-with-mcp
- Discussão da comunidade (Hacker News, autor presente): https://news.ycombinator.com/item?id=47193064

### 11.1) Fontes da Pesquisa de Enforcement Mecânico (§ 4.1.1 — 2026-10)

- Parallel tool use — Claude Platform Docs (troubleshooting, "weak prompting", formatação de tool results): https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use
- Claude Cookbook — "Parallel tool calls on Claude 3.7 Sonnet" (padrão `batch_tool` meta-tool, origem conceitual de `ctx_batch_execute`): https://platform.claude.com/cookbook/tool-use-parallel-tools
- GitHub issue `anthropic-sdk-typescript#956` — regressão de parallel tool calling em Opus/Sonnet 4.6 mesmo com prompt agressivo ("You MUST call ALL 46 tools"): https://github.com/anthropics/anthropic-sdk-typescript/issues/956
- GitHub Copilot Hooks Reference (contrato `preToolUse`, `permissionDecision: deny`, fail-closed): https://docs.github.com/en/copilot/reference/hooks-reference
- Claude Code Hooks Complete Guide — "hooks make the enforcement deterministic where the prompt makes it probabilistic": https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html
- `anthropics/claude-code#24327` — risco de o modelo parar/desistir ao interpretar um `deny` de hook como negação do usuário em vez de feedback corrigível: https://github.com/anthropics/claude-code/issues/24327
- `microsoft/copilot-intellij-feedback#1819` — limitação conhecida: JetBrains Copilot honra apenas `deny`, não reescreve input (`updatedInput`/`modifiedArgs`) como VS Code/Copilot CLI: https://github.com/microsoft/copilot-intellij-feedback/issues/1819

