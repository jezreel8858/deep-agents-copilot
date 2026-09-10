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
- [ ] Arquivo-alvo > 200 linhas, `.yaml`/`.yml`/`.json`, ou consumido por CI? Se sim, apliquei o padrão verificado da § 5 (R-051) em vez de `insert_edit_into_file`?

---

## 5. Proteção Anti-Corrupção em Arquivo Único Grande/Estruturado (R-051)

> ⚠️ **INCIDENTE REAL (2026-09)**: durante uma auditoria de workflows, `insert_edit_into_file` foi usado para inserir um pequeno bloco em `workflows.md` (~600 linhas, Markdown+Mermaid) e em `routing-graph.yaml` (~1200 linhas, YAML). Em três ocasiões distintas, a tool truncou o arquivo para menos de 20 linhas — descartando quase todo o conteúdo — sem que a mensagem de retorno indicasse falha de forma confiável. Isso exigiu rollback manual via IDE (Local History/git) pelo desenvolvedor, gerando custo real de créditos e retrabalho.

### 5.1 Regra (R-051): Quando `insert_edit_into_file` é Proibido

Independentemente do número de arquivos (mesmo 1 único arquivo), se o **arquivo-alvo** atender a QUALQUER destes critérios:

| Critério | Gatilho |
|---|---|
| Tamanho | Mais de **200 linhas** |
| Formato | Extensão `.yaml`, `.yml` ou `.json` (sintaxe sensível a indentação/estrutura) |
| Consumo | Arquivo lido/parseado diretamente por testes automatizados ou pipeline de CI |

...então `insert_edit_into_file` é **ANTI-PADRÃO BLOQUEANTE**. O agente DEVE usar o **Padrão de Edição Segura Verificada** via `context-mode` (`ctx_execute`): ler o arquivo inteiro → contar ocorrências exatas do texto-âncora em memória → abortar se != 1 → só então escrever (`fs.writeFileSync`) → reler do disco para confirmar. Template de referência (R-026 — código real fora do corpo da skill): [`snippets/safe-single-file-edit-pattern.js`](snippets/safe-single-file-edit-pattern.js).

### 5.2 Regra Complementar: Nunca Confiar Cegamente no Retorno da Tool

Mesmo com `replace_string_in_file` (fora do escopo de proibição acima), o agente:
1. **NÃO deve presumir sucesso** só porque a tool não reportou erro — para arquivos consumidos por CI/testes, confirme com uma leitura independente (`read_file`, `ctx_execute` ou `get_errors`) antes de prosseguir para a próxima edição.
2. **NÃO deve presumir falha** só porque a tool reportou erro — verifique o estado real do arquivo antes de tentar novamente; foram observados falsos-negativos (a edição aplicou corretamente apesar da mensagem de "não encontrado").
3. Após qualquer sequência de edições em arquivo grande/estruturado, rode uma validação estrutural mínima antes de considerar a tarefa concluída: `yaml.safe_load` para YAML, contagem de colchetes/chaves balanceados para blocos Mermaid, ou equivalente para o formato do arquivo.

### 5.3 Checklist Rápido

- [ ] Arquivo-alvo tem > 200 linhas OU é `.yaml`/`.yml`/`.json` OU é consumido por testes/CI?
  - [ ] **Sim** → usar exclusivamente o padrão verificado (`ctx_execute` + `snippets/safe-single-file-edit-pattern.js`); `insert_edit_into_file` proibido.
  - [ ] **Não** → `replace_string_in_file`/`insert_edit_into_file` permitidos, mas ainda seguindo 5.2.
- [ ] Após escrever, reli o arquivo (ou rodei validação de sintaxe) para confirmar o resultado real?

