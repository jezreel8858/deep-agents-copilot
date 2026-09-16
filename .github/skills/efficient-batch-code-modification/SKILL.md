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

## 0. Hierarquia de Decisão de Ferramenta (Antes de Tudo)

Antes de executar qualquer edição, o agente DEVE classificar o escopo da tarefa para escolher a ferramenta com menor custo de créditos:

| Escopo da Modificação | Ferramenta Obrigatória | Mecanismo de Execução | Custo de Créditos |
|---|---|---|:---:|
| **1 a 4 arquivos** (edição pontual, contextos heterogêneos) | `replace_string_in_file` ou `insert_edit_into_file` (Editor) | Single-Turn Batching (todas as tool calls na mesma rodada) | Baixo (~1 tool call por arquivo) |
| **5+ arquivos** OU **padrão repetitivo** em múltiplos arquivos (rename, atualização de campo, injeção de bullet em N agents/skills) | `ctx_execute`, `ctx_execute_file` ou `ctx_batch_execute` (Context-Mode) | Script inline (Node.js/Python) que lê, altera via regex/replace e salva em processo único no sandbox | **Mínimo (~zero créditos de LLM por arquivo, 1 única tool call)** |

> ⚠️ **INCIDENTE PREVENIDO**: Executar 20+ chamadas de editor sequenciais ou em lote no chat reenvia histórico massivo a cada retorno de tool, podendo drenar centenas de créditos por refactor. Em operações massivas (>= 5 arquivos) ou padrões repetitivos, o uso de script via `ctx_execute`/`ctx_execute_file`/`ctx_batch_execute` é **COMPULSÓRIO**.

---

## 1. Diagnóstico: Por que Alterações em Cascata Consomem Tantos Créditos?

Nos ambientes de AI Chat (VS Code / JetBrains Copilot):
- **A cada rodada de ferramenta (*tool call* unitária)**, o cliente reenvia **todo o histórico da conversa**, os prompts de governança (`CLAUDE.md`, `copilot-instructions.md`) e os outputs das ferramentas anteriores.
- Se uma tarefa toca 15 arquivos e o agente executa:
  `read_file (1)` → *turno* → `replace (1)` → *turno* → `read_file (2)` → *turno* → `replace (2)` ...
  O agente realiza **30+ turnos sequenciais**. Com um histórico médio de 25k tokens, são processados mais de **750.000 tokens de entrada**, drenando rapidamente centenas de créditos de modelos premium (Claude Sonnet / GPT-5).
- **A Solução Canônica:** Pré-análise em memória (Dry-Run) + Execução em Lote Paralela (*Single-Turn Batching*) + Diffs Cirúrgicos.

---

## 2. As 3 Diretrizes Fundamentais

### 2.1. Diretriz 1: Análise de Impacto Prévia (Dry-Run em Memória)

Antes de invocar ferramentas de escrita (`ctx_execute`, `replace_string_in_file`, `insert_edit_into_file`, `create_file`):
1. **Mapeamento Cirúrgico e Decisão de Ferramenta:** Inspecione a árvore e identifique de antemão todas as ocorrências necessárias (via `grep_search` focado ou leitura rápida dos arquivos conhecidos). **Decida automaticamente a ferramenta**: se >= 5 arquivos ou padrão repetitivo, prepare script para `ctx_execute`/`ctx_batch_execute`; se 1 a 4 arquivos pontuais, prepare tool calls do editor.
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

---

## 3. Matriz Comparativa: Execução Ingênua vs. Batch de Editor vs. Context-Mode Script

| Aspecto | Execução Ingênua (Anti-Padrão) | Batch de Editor (1 a 4 arquivos) | Context-Mode Script (>= 5 arquivos / Repetitivo) |
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
- [ ] **Hierarquia de Ferramenta**: Se >= 5 arquivos ou padrão repetitivo, usei `ctx_execute`/`ctx_batch_execute` com script em vez de tool calls de editor unitárias?
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

