---
name: efficient-batch-code-modification
description: >
  Diretrizes e padrões para execução de alterações de código em lote otimizadas
  para consumo mínimo de tokens e créditos em sessões de AI Copilot — análise prévia
  de impacto (dry-run), batching de tool calls em uma única rodada, minimal diffs cirúrgicos,
  prevenção de loops de re-submissão de contexto e proteção anti-corrupção em edição de
  arquivo único grande/estruturado via padrão verificado (R-051).
tier: 1
category: process
triggers:
  - "efficient batch code modification"
  - "edição em lote"
  - "batch modification"
  - "diff cirúrgico"
  - "minimal diffs"
  - "economia de créditos"
  - "otimizar consumo de tokens"
  - "dry-run de edição"
  - "alterar múltiplos arquivos"
  - "reduzir tool calls"
  - "token budget"
tools:
  - "replace_string_in_file"
  - "insert_edit_into_file"
  - "create_file"
  - "read_file"
  - "grep_search"
  - "get_errors"
  - "context-mode/ctx_execute"
  - "context-mode/ctx_execute_file"
  - "context-mode/ctx_batch_execute"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
---

# Efficient Batch Code Modification (Edição em Lote com Economia de Tokens)

Esta skill estabelece o protocolo operacional obrigatório para execução de alterações de código otimizadas para consumo de tokens e diffs mínimos em assistentes de IA (GitHub Copilot, Claude, Cursor). O objetivo principal é **eliminar o desperdício de créditos e evitar a re-submissão recursiva do contexto** durante tarefas multi-arquivo.

---

## 0. Hierarquia e Precedência de Ferramentas (R-056 — Context-Mode First)

O uso de `context-mode` (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_index`, `ctx_search`) é **100% OBRIGATÓRIO tanto para LEITURAS quanto para MODIFICAÇÃO/CRIAÇÃO de arquivos** SEMPRE que a ferramenta context-mode estiver disponível no ambiente, eliminando categoricamente o anti-padrão de editor tool sprawl (Smell 2.24):

| Nível de Precedência | Escopo / Cenário | Ferramenta Obrigatória | Mecanismo de Execução | Custo de Créditos |
|---|---|---|---|:---:|
| **Nível 1 (Primário / 100% Compulsório)** | **Qualquer leitura, busca, inspeção, modificação ou criação de arquivos** sempre que a ferramenta context-mode estiver disponível no ambiente | `ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_index` ou `ctx_search` (Context-Mode) | Script inline (Node.js/Python) que lê, valida unicidade em memória e salva em processo único all-or-nothing no sandbox (R-051 / R-056) | **Mínimo (~1 única tool call, zero overhead de chat)** |
| **Nível 2 (Fallback Exclusivo quando Context-Mode Indisponível)** | **Estritamente proibidas quando context-mode estiver disponível**. Permitidas única e exclusivamente como fallback quando o servidor MCP context-mode estiver comprovadamente indisponível ou desconectado | `read_file`, `replace_string_in_file`, `insert_edit_into_file`, `create_file` (Editor) | Single-Turn Batching cirúrgico com 2-3 linhas de contexto exclusivo. **Proibido encadear múltiplas chamadas em série no chat.** | Baixo (~1 tool call) |

> ⚠️ **REGRA NORMATIVA INEGOCIÁVEL (R-008 / R-056)**: Ferramentas nativas de editor (`read_file`, `replace_string_in_file`, `insert_edit_into_file`, `create_file`) e terminal são **estritamente proibidas quando o context-mode estiver disponível no ambiente**, sendo rebaixadas a **fallback exclusivo** para quando o servidor MCP context-mode estiver comprovadamente indisponível ou desconectado. Executar chamadas manuais de editor reenvia histórico massivo e arrisca corrupção por truncamento/fuzzy match.

---

## 1. Diagnóstico: Por que Alterações em Cascata Consomem Tantos Créditos?

Nos ambientes de AI Chat (VS Code / JetBrains Copilot):
- **A cada rodada de ferramenta (*tool call* unitária)**, o cliente reenvia **todo o histórico da conversa**, os prompts de governança (`CLAUDE.md`, `copilot-instructions.md`) e os outputs das ferramentas anteriores.
- Se uma tarefa toca 15 arquivos e o agente executa:
  `read_file (1)` → *turno* → `replace (1)` → *turno* → `read_file (2)` → *turno* → `replace (2)` ...
  O agente realiza **30+ turnos sequenciais**. Com um histórico médio de 25k tokens, são processados mais de **750.000 tokens de entrada**, drenando rapidamente centenas de créditos de modelos premium (Claude Sonnet / GPT-5).
- **O Anti-Padrão MCP Tool Chaining Sequencial no Chat (Smell 2.26)**: O mesmo dreno ocorre quando o agente substitui ferramentas de editor por `ctx_execute`, mas o invoca de forma sequencial turno a turno no chat (ex.: 10+ turnos sucessivos disparando um `ctx_execute` para cada arquivo/diff). Cada turno reenvia todo o histórico acumulado da conversa.
- **A Solução Canônica:** Pré-análise em memória (Dry-Run) + Execução em Lote Único (*Single-Turn Batching* via `ctx_batch_execute` ou script consolidado em `ctx_execute`) + Diffs Cirúrgicos.

---

## 2. As 3 Diretrizes Fundamentais

### 2.1. Diretriz 1: Análise de Impacto Prévia (Dry-Run em Memória)

Antes de invocar ferramentas de escrita (`ctx_execute`, `replace_string_in_file`, `insert_edit_into_file`, `create_file`):
1. **Mapeamento Cirúrgico e Decisão de Ferramenta:** Inspecione a árvore e identifique de antemão todas as ocorrências necessárias (via `ctx_execute` ou busca programática no sandbox). Se context-mode estiver disponível, o uso de `ctx_execute`/`ctx_batch_execute` com script é **100% obrigatório**; ferramentas nativas de editor são reservadas exclusivamente como fallback se o MCP estiver comprovadamente indisponível.
2. **Resumo Compacto:** No planejamento mental ou resposta inicial, estruture a lista de arquivos afetados e os blocos específicos antes de tocar no disco.
3. **Validação de Precondição:** Certifique-se de que os arquivos existem e não possuem conflitos óbvios antes de iniciar a primeira edição.

### 2.1.1. Leitura Prévia Cirúrgica (R-048)

Antes de qualquer dry-run ou inspeção para batch edit, o agente NÃO DEVE ler arquivos inteiros (>100 linhas). O ciclo de vida acopla-se diretamente ao R-046:
1. **Localização Exata**: Localize as âncoras e alvos via `grep_search`.
2. **Leitura Paginada**: Utilize `read_file` informando `offset` e `limit` restritos à janela de modificação (60-80 linhas).
3. **Processamento em Sandbox**: Se a inspeção for analítica/estrutural e o arquivo tiver mais de 300 linhas, delegue a derivação a `ctx_execute_file` sem trafegar o arquivo bruto na memória conversacional.

### 2.2. Diretriz 2: Aplicação em Lote (Batch Tool Calls)

1. **Paralelização de Edições:** Agrupe todas as edições necessárias de múltiplos arquivos na **mesma rodada de resposta** (*tool calls* simultâneas).
   - ❌ **Anti-padrão (Sequencial):** Editar `arquivo1.ts`, esperar o output da tool no próximo turno, para só então chamar o editor para `arquivo2.ts`.
   - ✅ **Padrão Canônico (Batch):** Emitir `replace_string_in_file(arquivo1)` E `replace_string_in_file(arquivo2)` E `replace_string_in_file(arquivo3)` na mesma mensagem.
2. **Validação Agrupada (`get_errors` em lote):**
   - ❌ **Anti-padrão:** Chamar `get_errors(arquivo1)`, depois `get_errors(arquivo2)`, depois `get_errors(arquivo3)` em turnos separados.
   - ✅ **Padrão Canônico:** Chamar `get_errors(filePaths: [arquivo1, arquivo2, arquivo3, ...])` **uma única vez** ao final de todo o lote.
3. **Zero Releitura Redundante:**
   - Nunca use `read_file` imediatamente após um `replace_string_in_file` com o único intuito de "ver se ficou bom". O retorno da ferramenta de replace já confirma o sucesso ou falha da operação.

### 2.3. Diretriz 3: Diffs Cirúrgicos (Minimal Diffs)

1. **Escopo Mínimo de Substituição:**
   - Substitua apenas o método, anotação, linha de import ou bloco específico.
   - Contexto de busca (`oldString`): forneça de 2 a 3 linhas acima e abaixo para garantir unicidade, sem carregar blocos de 100 linhas desnecessárias.
2. **Proibição de Reescrita Integral:**
   - **NUNCA** reescreva arquivos inteiros do zero via `create_file` ou replace integral se a alteração afeta apenas 10% a 30% do arquivo.
   - Reescrita total só é justificável se o arquivo for novo ou se >80% do seu conteúdo foi descartado.

### 2.4. Diretriz 4: Single-Turn MCP Batching Compulsório (Anti-MCP Tool Chaining / Smell 2.26)

Toda inspeção, análise, validação ou modificação envolvendo múltiplos alvos (diffs, arquivos, status, branches) DEVE ser consolidada em **UMA ÚNICA chamada de ferramenta MCP**:

1. **Via A — Múltiplos comandos shell/leituras:** Usar compulsoriamente `ctx_batch_execute` com comandos rotulados e queries unificadas em uma única rodada:
   ```javascript
   ctx_batch_execute({
     commands: [
       { label: "git-diff", command: "git --no-pager diff --stat" },
       { label: "git-log", command: "git --no-pager log -n 3 --oneline" },
       { label: "status", command: "git status -s" }
     ],
     queries: ["arquivos modificados", "mensagens de commit recentes"],
     concurrency: 2
   })
   ```
2. **Via B — Múltiplos arquivos no filesystem:** Usar um único script síncrono em `ctx_execute` que itere por todos os alvos e emita um resumo consolidado:
   ```javascript
   ctx_execute({
     language: "javascript",
     code: `
       const fs = require('fs');
       const targets = ['src/a.ts', 'src/b.ts', 'src/c.ts'];
       const summary = targets.map(f => ({ file: f, lines: fs.readFileSync(f, 'utf8').split('\\n').length }));
       console.log(JSON.stringify(summary, null, 2));
     `
   })
   ```
3. **Proibição Absoluta**: É terminantemente proibido disparar turnos separados no chat chamando `ctx_execute` para cada arquivo/comando individualmente.

#### Regra do Limiar >= 2 (Anti Tool Chaining — Smell 2.26 / R-059)

> **Regra do Limiar >= 2 (inegociável):** SE o escopo da tarefa exigir inspecionar, ler, comparar, editar ou executar 2 (DOIS) OU MAIS arquivos/comandos/alvos, é TERMINANTEMENTE PROIBIDO disparar `ctx_execute` isolado por alvo em chamadas/turnos sucessivos. É OBRIGATÓRIO: (a) `ctx_batch_execute(commands, queries)` com todos os alvos rotulados em uma única chamada, OU (b) um único script iterativo em `ctx_execute` que processe todos os alvos em loop interno e imprima o resumo consolidado de uma só vez. Antes de disparar a primeira chamada de ferramenta, o agente DEVE enumerar mentalmente TODOS os alvos necessários para completar a tarefa (Plan-Then-Batch, ver abaixo) — nunca descobrir o próximo alvo reativamente turno-a-turno.

#### Protocolo Plan-Then-Batch (Anti Miopia Reativa — Smell 2.13 / R-059)

> 1. **ENUMERAR**: antes de qualquer tool call, liste internamente todos os arquivos/comandos que compõem a tarefa completa (não apenas o próximo passo aparente).
> 2. **CONSOLIDAR**: se a lista tiver >= 2 itens, agrupe tudo em uma única payload (`commands[]` em `ctx_batch_execute` ou loop único em `ctx_execute`).
> 3. **DESPACHAR**: dispare apenas 1 chamada de ferramenta de leitura/processamento por fase da tarefa — nunca N chamadas sequenciais para N alvos previsíveis.
> 4. **Comandos curtos não suspendem a regra**: prompts do usuário como "prosseguir", "continue", "pode seguir" NÃO isentam o agente da obrigatoriedade de context-mode nem do limiar >= 2 — a obrigação é da TAREFA em andamento, não do tamanho do prompt do turno atual.
>
> *(SSOT Normativa: `.github/copilot-instructions.md` § 2.1; alinhamento operacional em `.github/skills/context-mode/SKILL.md`)*.

---

## 3. Matriz Comparativa: Execução Ingênua vs. Batch de Editor vs. Context-Mode Script

| Aspecto | Execução Ingênua (Anti-Padrão) | Fallback de Editor (Apenas se Context-Mode Indisponível) | Context-Mode Script (100% Obrigatório quando disponível) |
|---|---|---|---|
| **Mecanismo** | `replace` sequencial (1 por turno) | `replace` paralelo em lote único | Script Node/Python via `ctx_execute` |
| **Tool Calls de Editor** | 20 a 50 chamadas sequenciais | 1 a 4 chamadas no mesmo turno | **0 chamadas de editor** (1 chamada MCP) |
| **Turnos de Chat** | 20 a 30 turnos | 1 a 2 turnos | **1 único turno** |
| **Consumo de Tokens** | 500k – 800k tokens (re-envio contínuo) | 60k – 100k tokens | **< 15k tokens** (processamento off-chat) |
| **Consumo de Créditos** | 200 a 400 créditos (ou >900 em 25+ files) | 20 a 50 créditos | **~Zero créditos extras** por arquivo |
| **Latência Total** | 3 a 5 minutos esperando turnos | 30 a 60 segundos | **< 5 segundos** |
| **Risco de Erro/Alucinação** | Alto (contexto satura no caminho) | Baixo | **Mínimo** (determinístico via script) |

---

## 4. Checklist de Auto-Verificação para Agentes

Antes de iniciar a gravação de alterações:
- [ ] O mapeamento de todos os arquivos impactados já está claro na memória?
- [ ] **Hierarquia de Ferramenta**: Utilizei `ctx_execute`/`ctx_batch_execute` com script inline no sandbox (100% obrigatório quando context-mode disponível), evitando ferramentas manuais de editor?
- [ ] Se < 5 arquivos pontuais, todas as chamadas de substituição para arquivos independentes foram agrupadas no mesmo turno (Single-Turn Batching)?
- [ ] O `oldString` contém apenas o contexto estrito para ser unívoco (2-3 linhas)?
- [ ] Evitei releituras desnecessárias de arquivos que eu mesmo acabei de editar?
- [ ] O `get_errors` final foi consolidado em uma única chamada com o array completo `filePaths`?
- [ ] Arquivo-alvo > 200 linhas, `.yaml`/`.yml`/`.json`, **Markdown estruturado** (`.agent.md`/`.instructions.md`) ou consumido por CI? Se sim, apliquei o padrão verificado da § 5 (R-051) com checagem de unicidade da âncora (`count === 1`)?

---

## 5. Proteção Anti-Corrupção em Arquivo Único Grande/Estruturado e Markdown com Âncoras Repetidas (R-051)

> ⚠️ **INCIDENTES REAIS PREVENIDOS (2026-09)**:
> 1. **Truncamento por `insert_edit_into_file`**: durante uma auditoria de workflows, `insert_edit_into_file` foi usado para inserir um pequeno bloco em `workflows.md` (~600 linhas, Markdown+Mermaid) e em `routing-graph.yaml` (~1200 linhas, YAML). Em três ocasiões distintas, a tool truncou o arquivo para menos de 20 linhas — descartando quase todo o conteúdo — sem aviso confiável.
> 2. **Corrupção e Wiping por `replace_string_in_file` com Fuzzy Matching**: durante a inclusão de co-agentes em `code-knowledge-graph.agent.md`, `replace_string_in_file` foi invocado com um trecho-âncora que colidia com seções repetidas e tabelas similares. O motor do editor ativou estratégias de fallback de correspondência aproximada (fuzzy/multiple matching), casando no ponto errado, apagando o frontmatter YAML e as primeiras 70 linhas do arquivo, além de duplicar linhas de tabela no final.

### 5.1 Regra (R-051): Escopo de Proteção Obrigatória

Independentemente do número de arquivos (mesmo 1 único arquivo), se o **arquivo-alvo** atender a QUALQUER destes critérios:

| Critério | Gatilho |
|---|---|
| Tamanho | Mais de **200 linhas** |
| Formato | Extensão `.yaml`, `.yml` ou `.json` (sintaxe sensível a indentação/estrutura) |
| Estrutura | **Markdown estruturado** (`.agent.md`, `.instructions.md`, arquivos `.md` com frontmatter YAML, seções repetitivas ou tabelas com entradas parecidas) |
| Consumo | Arquivo lido/parseado diretamente por testes automatizados ou pipeline de CI |

...então `insert_edit_into_file` é **ANTI-PADRÃO BLOQUEANTE** e `replace_string_in_file` NUNCA deve ser invocado sem garantia prévia de unicidade estrita da âncora (`count === 1`). O agente DEVE priorizar o **Padrão de Edição Segura Verificada** via `context-mode` (`ctx_execute`): ler o arquivo inteiro do disco → contar ocorrências exatas do texto-âncora em memória (`content.split(oldStr).length - 1`) → abortar compulsoriamente se `count !== 1` (nunca adivinhar ou deixar o editor aplicar fuzzy matching) → só então escrever (`fs.writeFileSync`) → reler do disco e validar que seções críticas (como frontmatter `---`, cabeçalhos `#` e contagem de linhas) permanecem íntegras. Template de referência (R-026 — código real fora do corpo da skill): [`snippets/safe-single-file-edit-pattern.js`](snippets/safe-single-file-edit-pattern.js).

### 5.2 O Perigo do Fallback Fuzzy de `replace_string_in_file` e a Regra de Unicidade Estrita

Por que `replace_string_in_file` falha em Markdown estruturado?
A documentação da ferramenta explicita: *"The system will try multiple matching strategies if exact matching fails"*. Quando o agente passa um `oldString` curto ou com poucas linhas de contexto em arquivos que possuem tabelas repetidas, títulos similares (ex.: `### 3.7` e `#### 3.7.1`), ou múltiplos blocos com texto parecido, o matching exato falha e o motor tenta correspondência aproximada (fuzzy). O resultado é desastroso: o editor casa no primeiro ponto similar que encontrar, substituindo blocos enormes anteriores (apagando frontmatter e títulos) ou duplicando trechos no final do arquivo.

Regras inegociáveis para edição segura:
1. **Verificação de Unicidade de Âncora Obrigatória**: conte as ocorrências do âncora em memória antes de invocar qualquer tool de substituição (`count = content.split(oldStr).length - 1`). Se `count !== 1` (0 ou >1), **ABORTAR imediatamente**; nunca deixar a tool tentar casamento aproximado. Forneça de 3 a 5 linhas de contexto inequívoco acima e abaixo ou aplique o script via `ctx_execute`.
2. **NÃO presumir sucesso nem falha pelo retorno da tool**: confirme o estado real do arquivo após a escrita via `read_file`, `ctx_execute` ou `get_errors`.
3. **Validação Pós-Escrita de Integridade Estrutural**: confirme imediatamente que o arquivo mantém suas seções essenciais (`---` no início se for agent/adapter, contagem de linhas próxima do esperado, ausência de duplicatas em tabelas) e rode validação sintática (`yaml.safe_load`, etc.) antes de considerar a edição concluída.

### 5.3 Checklist Rápido

- [ ] Arquivo-alvo tem > 200 linhas OU é `.yaml`/`.yml`/`.json` OU é **Markdown estruturado** (`.agent.md`, `.instructions.md`) OU é consumido por testes/CI?
  - [ ] **Sim** → aplicar o padrão verificado (`ctx_execute` + `snippets/safe-single-file-edit-pattern.js`) com contagem de unicidade (`count === 1`); `insert_edit_into_file` proibido e `replace_string_in_file` só com contexto estrito e validação imediata.
  - [ ] **Não** → `replace_string_in_file` permitido, mas ainda verificando unicidade de âncora e seguindo 5.2.
- [ ] Contei ocorrências da âncora em memória e confirmei que `count === 1` antes de substituir?
- [ ] Após escrever, reli o arquivo (ou rodei validação de sintaxe/integridade de seções) para confirmar o resultado real?

## 6. Teto Rígido de Tool Turns (≤ 5) e Prevenção de Dívida de Tokens O(N^2) (R-060)

### 6.1. A Dinâmica do Custo Quadrático de Contexto

Em arquiteturas agentic baseadas em tool-calling, o LLM reenvia todo o histórico cumulativo a cada novo turno:

Total Tokens approx Sum(k=1..N) [Prompt Base + Sum(i=1..k) Tool Output_i]

Uma sessão ingênua com 20 tool turns pode inflar o volume de tokens processados de 10.000 para mais de 350.000 tokens de entrada, elevando os custos de créditos em até 10x-50x.

### 6.2. Estratégia de Warm Start e Destilação na Borda (Edge Truncation)

1. **Warm Start Compulsório**: Recursos locais (caches, grafos, compilações) nunca devem falhar no primeiro turno exigindo auto-recuperação reativa. Devem ser inicializados silenciosamente em lote (*build-if-missing*).
2. **Batch Querying**: Agrupar todas as interrogações em uma única chamada agregada (ctx_batch_execute, batch_query ou script iterativo em sandbox).
3. **Edge Truncation (Destilação Semântica)**: Truncar e filtrar dados volumosos *dentro da ferramenta/sandbox*. O chat recebe apenas métricas, anomalias e achados conclusivos.

### 6.3. Protocolo de Circuit Breaker no 4º Turno

- **Turno 1**: Levantamento consolidado (Batch Gather) + Warm Start.
- **Turno 2**: Execução/processamento unificado em lote (All-or-Nothing / Batch Processing).
- **Turno 3**: Validação consolidada (Quality Gate).
- **Turno 4 (Threshold)**: Se a tarefa não convergir, acionar compulsoriamente o **Circuit Breaker**:
  - Salvar evidências parciais em ctx_index;
  - Emitir parecer técnico com o estado alcançado;
  - Delegar ao próximo agente via handoff ou acionar intervenção humana via ask_questions.

