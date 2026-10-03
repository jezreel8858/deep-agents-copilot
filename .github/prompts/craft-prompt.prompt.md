---
name: 'craft-prompt'
description: >-
  Aciona o WORKFLOW-PROMPT-SYNTHESIS para refinar, enriquecer com contexto determinístico e gerar o prompt perfeito em template Markdown para um novo chat
agent: 'agent'
model: "Gemini 3.8 Flash"
tools: ['read_file', 'get_errors', 'ask_questions', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search']
argument-hint: '[ideia-ou-requisito-inicial]'
source_docs:
  - .github/skills/prompt-engineering-patterns/SKILL.md
  - .github/skills/requirements-engineering-patterns/SKILL.md
  - .github/skills/structured-intake-patterns/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/workflows.md
---

# `/craft-prompt`

> **Propósito**: Acionar o `WORKFLOW-PROMPT-SYNTHESIS` para conduzir o refinamento estrutural de prompt, minerar contexto e dependências no codebase e sintetizar o prompt canônico perfeito em template Markdown pronto para inicializar um novo chat conduzido por agents ou workflows especialistas (consumo exclusivo downstream).
> **Arquivo Ativo**: `${file}`
> **Workspace**: `${workspaceFolder}`

---

## 🎯 Invocação e Variáveis Nativas

Este prompt utiliza as variáveis de contexto nativas do VS Code / JetBrains Copilot:

```bash
# Execução direta com base na ideia inicial:
/craft-prompt

# Execução passando objetivo, tarefa ou referência a arquivo:
/craft-prompt <ideia-ou-requisito-inicial>
```

### Variáveis Disponíveis no Template
- `${file}`: Caminho absoluto do arquivo aberto e em foco no editor (usado como referência contextual se aplicável).
- `${selection}`: Trecho de código, erro ou especificação atualmente selecionada pelo usuário.
- `${workspaceFolder}`: Diretório raiz do workspace ativo.
- `${input:descricaoTarefa}`: Descrição detalhada da funcionalidade, correção ou refatoração desejada.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** refinar requisitos, minerar contexto determinístico no codebase e sintetizar o prompt canônico final em bloco de código Markdown (`.md`).
- ✅ **SEMPRE** tratar o prompt sintetizado como de **consumo exclusivo downstream** por outros agents e workflows em uma nova sessão limpa, nunca como resposta ou solução final direta ao usuário.
- ✅ **SEMPRE** avaliar a natureza da solicitação no Passo 1: se envolver nova feature, regras de negócio ou demanda aberta, assumir compulsoriamente a postura de `@requirements-analyst` e disparar `ask_questions` para validar decisões e regras de domínio com o usuário antes de avançar (R-027 / Invariante 19).
- ✅ **SEMPRE** invocar compulsoriamente o subagente `@codegraph-engine` via `run_subagent` no Passo 2 para grounding determinístico de arquivos e dependências (R-045 / Invariante 18).
- ✅ **SEMPRE** garantir **Visibilidade Progressiva (Anti-Blackbox Execution)**: detalhar obrigatoriamente no chat os achados e decisões de cada uma das 5 etapas antes de emitir o prompt final.
- ✅ **SEMPRE** operar no **Problem Space** durante o refino, formalizando Critérios de Aceitação (DoD) e Não-Escopo antes da síntese.
- ✅ **SEMPRE** identificar e injetar caminhos reais de arquivos (seção `## Arquivos e Referências Grounded`) e componentes irmãos canônicos homologados.
- ❌ **NÃO** deduzir, supor ou inventar regras de negócio, telas, permissões ou fluxos de aprovação sem confirmação humana direta (proibição expressa de alucinação de requisitos).
- ❌ **NÃO** tratar checkpoints de validação humana como opcionais em demandas com ambiguidade de domínio ou múltiplos caminhos de negócio viáveis.
- ❌ **NÃO** realizar varredura manual de pastas, scripts exploratórios de diretório com `fs` no sandbox via `ctx_execute` ou MCP Tool Chaining sequencial (violação gravíssima de R-045 / RNF-004 e Smell 2.26). Toda análise estrutural pertence com exclusividade ao `@codegraph-engine`.
- ❌ **NÃO** simular ou fingir a chamada de `@codegraph-engine` no checklist sem tê-lo invocado de fato via `run_subagent`.
- ❌ **NÃO** executar o workflow em silêncio (blackbox) emitindo apenas checkboxes [✅] sem o Painel de Evidências das etapas.
- ❌ **NÃO** implementar código de aplicação, alterar arquivos de domínio ou executar correções de funcionalidade (responsabilidade do novo chat).
- ❌ **NÃO** fazer perguntas abertas ou desestruturadas — aplicar elicitação de 5 a 10 rodadas estruturadas de desambiguação via `ask_questions` com opções + campo livre (R-027 / Invariante 19), com teto estrito na 10ª rodada.
- ❌ **NÃO** gerar texto de prompt solto sem estrutura Markdown canônica ou fora de bloco de código copiável.
- ❌ **NÃO** apresentar o prompt como solução técnica implementada ou resposta final ao usuário (consumo estrito downstream).

---

## 📋 Fluxo de Execução Passo a Passo

O processamento segue rigorosamente as 5 etapas do **`WORKFLOW-PROMPT-SYNTHESIS`**, com **visibilidade total em cada etapa**:

### Passo 1 — Elicitação & Intake com Usuário (`@requirements-analyst` / `@prompt-structuring`)
- Analise a solicitação inicial do usuário (`${selection}`, `${file}` ou texto fornecido).
- **Via Funcional (Feature / Regras de Negócio / Demanda Aberta)**:
  - Assuma compulsoriamente a postura investigativa de `@requirements-analyst`.
  - Aplique *Five Whys* caso a solicitação venha com solução técnica prematura (*solution-jumping*).
  - Isole as ambiguidades fundamentais de negócio e formule de 5 a 10 rodadas estruturadas de desambiguação via `ask_questions` com opções claras + campo livre (padrão `structured-intake-patterns` e Invariante 19).
  - 🛑 **PARADA OBRIGATÓRIA**: Aguarde a resposta do usuário em cada rodada antes de avançar! É terminantemente proibido avançar para o Passo 2 ou alucinar regras de negócio sem confirmação do solicitante (R-027 / Invariante 19). Caso atinja a 10ª rodada com pontos ainda em aberto, aplique a cláusula de teto: declare as lacunas residuais formalmente na seção de restrições e prossiga.
  - Converta as definições validadas pelo usuário em Critérios de Aceitação (DoD em formato INVEST/Gherkin).
- **Via Técnica (Refactor / Bugfix / Tarefa Direta com Alvo Claro)**:
  - Conduza com `@prompt-structuring` diretamente no Problem Space técnico, delimitando o escopo sem inventar regras de negócio.
- Registre o resumo executivo desta etapa na seção `### 🔍 Etapa 1: Elicitação & Problem Space`.

### Passo 2 — Mineração Determinística no Codebase via `@codegraph-engine` (R-045 / Invariante 18)
- ⚠️ **INVOCAÇÃO OBRIGATÓRIA DE SUBAGENTE**:
  Você DEVE compulsoriamente invocar o subagente `@codegraph-engine` através da ferramenta `run_subagent`:
  `run_subagent(agentName: 'codegraph-engine', description: 'Mapear arquivos reais e dependências do módulo', task: 'Mapear arquivos reais, componentes, interfaces, DTOs e componentes irmãos canônicos no repositório alvo para a funcionalidade: <descricaoTarefa>')`.
- ❌ **TERMINANTEMENTE PROIBIDO**: Escrever scripts ad-hoc no sandbox (`ctx_execute` com `fs.readdirSync` / `fs.readFileSync`) ou fazer múltiplas chamadas manuais para simular o grafo (violação direta de R-045 e Smell 2.26).
- Aguarde o retorno estruturado do `@codegraph-engine` e utilize exclusivamente os caminhos verificados por ele.
- Se a tarefa envolver dependência externa nova, acione `run_subagent(agentName: 'deep-search', ...)` para obter versões e documentação oficial.
- Registre a lista completa retornada pelo subagente na seção `#### 🗺️ Etapa 2: Context Grounding & AST Mining`.

### Passo 3 — Mapeamento de Restrições e Não-Escopo (`@prompt-structuring`)
- Extraia explicitamente o que **NÃO** deve ser feito (não-escopo negativo, proibições de regressão, contratos imutáveis).
- Injete as convenções normativas obrigatórias do repositório (ex.: R-046 para modificações em lote cirúrgico, regras de modernização de framework, convenções de teste).
- Registre as restrições na seção `### 🛑 Etapa 3: Mapeamento de Restrições e Não-Escopo`.

### Passo 4 — Síntese Estruturada & Otimização de Caching (`@prompt-structuring`)
- Monte o prompt canônico final estruturado no template Markdown canônico (`templates/prompt-synthesis-output.md`):
  - `# [Papel Especialista / Stack Detectada]`
  - `## Contexto do Projeto`: Dados estáticos da aplicação e convenções para alinhamento e Prompt Caching.
  - `## Arquivos e Referências Grounded`: Caminhos reais dos arquivos alvo, interfaces e referências verificados.
  - `## Tarefa`: Descrição clara e concisa do objetivo.
  - `## Critérios de Aceitação`: Checklist de aceitação objetivo em formato INVEST/Gherkin.
  - `## Restrições e Não-Escopo`: Restrições negativas, diretrizes inegociáveis (R-046 / Single-Turn Batching) e eventuais lacunas residuais declaradas.
  - `## Protocolo de Execução Recomendado`: Passos operacionais recomendados para o agente executor na nova sessão.
  - `## Formato de Saída Esperado`: Formato conciso de entrega sem narrativa ociosa.
- Registre a estratégia de alinhamento para Prompt Caching na seção `### ⚡ Etapa 4: Síntese Estruturada & Caching`.

### Passo 5 — Quality Gate & Emissão do Bloco Markdown (`@prompt-structuring`)
- Execute um red-teaming analítico ativo contra o Solution Space avaliando os 4 critérios de corte excludentes:
  1. Classes ou métodos internos não solicitados;
  2. Bibliotecas, frameworks ou algoritmos não pedidos expressamente;
  3. Arquitetura interna ou design patterns prescritos no lugar de preservar a autonomia do especialista;
  4. Tecnologias não mencionadas na demanda original.
- Confirme ainda: zero alucinações de caminhos de arquivos (100% verificados via `@codegraph-engine`), zero ambiguidades nos critérios de aceite, eliminação de over-prompting prejudicial a modelos de raciocínio frontier e garantia de consumo exclusivo downstream por agents/workflows.
- Cláusula de bloqueio: qualquer violação reprova a emissão e força re-síntese cirúrgica no Passo 4.
- Registre o checklist de verificação na seção `### 🛡️ Etapa 5: Quality Gate & Validação Final`.
- Emita o bloco de código Markdown (`.md`) completo e autocontido, pronto para ser copiado e colado na primeira mensagem de uma sessão limpa.

---

## ✅ Checklist Antes de Apresentar

- [ ] Elicitação com usuário realizada via `ask_questions` para demandas abertas de negócio (zero alucinação de regras).
- [ ] Subagente `@codegraph-engine` invocado formalmente via `run_subagent` na Etapa 2 (zero scripts manuais no sandbox).
- [ ] Pipeline visual `### 🗺️ Pipeline de Execução: WORKFLOW-PROMPT-SYNTHESIS (5 etapas)` exibido no topo.
- [ ] Painel de Evidências com relatório individual de cada uma das 5 etapas renderizado no chat.
- [ ] Arquivos e referências mapeados com caminhos reais existentes no repositório (`## Arquivos e Referências Grounded`).
- [ ] Critérios de aceitação objetivos formulados em formato de checklist (`## Critérios de Aceitação`).
- [ ] Restrições negativas, governança de lote e eventuais lacunas residuais explicitadas (`## Restrições e Não-Escopo`).
- [ ] Red-teaming de Solution Space aprovado nos 4 critérios de corte.
- [ ] Finalidade de consumo exclusivo downstream garantida (não entregue como resposta final ao usuário).
- [ ] Bloco Markdown final renderizado em cerca de código pronta para cópia.
- [ ] Nenhuma alteração indevida realizada no codebase da aplicação.

---

## 📊 Formato de Saída

```markdown
### 🗺️ Pipeline de Execução: WORKFLOW-PROMPT-SYNTHESIS (5 etapas)
- [✅] Etapa 1: Elicitação de Requisitos e Problem Space (@requirements-analyst / ask_questions)
- [✅] Etapa 2: Mineração de Contexto e Grounding (@codegraph-engine)
- [✅] Etapa 3: Mapeamento de Restrições e Não-Escopo (@prompt-structuring)
- [✅] Etapa 4: Síntese Estruturada e Otimização para Caching (@prompt-structuring)
- [✅] Etapa 5: Quality Gate e Emissão do Bloco Markdown (@prompt-structuring)

---

### 📋 Painel de Evidências por Etapa (Rastreabilidade Operacional)

#### 🔍 Etapa 1: Elicitação & Problem Space
- **Problema de Negócio**: <descrição da necessidade sem invadir a solução técnica>
- **Atores & Papéis**: <usuários, papéis ou sistemas impactados>
- **Critérios de Aceitação Preliminares (DoD)**: <itens de verificação obrigatórios>

#### 🗺️ Etapa 2: Mineração de Contexto & Grounding no Codebase
- **Arquivos-Alvo Identificados no Repositório**:
  - `<caminho_real_1>`: <motivação de inclusão>
  - `<caminho_real_2>`: <motivação de inclusão>
- **Componente Irmão Canônico Homologado**: `<caminho_irmao_canonico>` (protocolo *Canonical Sibling First*)
- **Modelos/DTOs Existentes no Escopo**: `<caminho_models>`

#### 🛑 Etapa 3: Mapeamento de Restrições e Não-Escopo
- **Não-Escopo Negativo**: <o que expressamente NÃO deve ser alterado>
- **Convenções Obrigatórias Injetadas**: <R-046, Single-Turn Batching, regras inegociáveis da stack>

#### ⚡ Etapa 4: Síntese Estruturada & Caching
- **Segmentação Markdown**: Seções canônicas estruturadas (`## Contexto do Projeto`, `## Arquivos e Referências Grounded`, `## Tarefa`, `## Critérios de Aceitação`, `## Restrições e Não-Escopo`, `## Protocolo de Execução Recomendado`, `## Formato de Saída Esperado`).
- **Prompt Caching Alignment**: Instruções estáticas e regras posicionadas no topo; dados variáveis da task na cauda.

#### 🛡️ Etapa 5: Quality Gate & Validação Final
- [x] Zero invasão de Solution Space (red-teaming de 4 critérios aprovado).
- [x] Zero alucinações de caminhos de arquivos (100% verificados contra o workspace).
- [x] Zero ambiguidades nos critérios de aceite.
- [x] Zero over-prompting prejudicial a modelos com raciocínio nativo.
- [x] Consumo exclusivo downstream assegurado (destinado a inicializar novo chat com agent/workflow).
- [x] Bloco Markdown completo e autocontido.

---

### 📦 Prompt Sintetizado para Novo Chat
Copie o bloco de código abaixo e cole na mensagem inicial da sua nova sessão:

````markdown
# [Papel Especialista / Stack Detectada]

## Contexto do Projeto
<!-- Dados estáticos da aplicação e convenções para alinhamento e Prompt Caching -->
...

## Arquivos e Referências Grounded
<!-- Caminhos reais no repositório verificados via @codegraph-engine e componentes irmãos canônicos -->
- `caminho/do/arquivo_1`
- `caminho/do/arquivo_2`

## Tarefa
<!-- Descrição clara e concisa do objetivo a ser executado no novo chat -->
...

## Critérios de Aceitação
<!-- Checklist objetivo em formato INVEST/Gherkin -->
- [ ] Critério 1
- [ ] Critério 2

## Restrições e Não-Escopo
<!-- Restrições negativas, diretrizes inegociáveis (R-046 / Single-Turn Batching) e eventuais lacunas residuais -->
- **Não-Escopo Negativo**: ...
- **Governança de Lote**: R-046 aplicado
- **Lacunas Residuais**: ...

## Protocolo de Execução Recomendado
<!-- Passos operacionais recomendados para o agente executor na nova sessão -->
1. Inspecionar arquivos grounded em memória...

## Formato de Saída Esperado
<!-- Formato conciso de entrega sem narrativa ociosa -->
...
````
```

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** contornar a invocação do subagente `@codegraph-engine` utilizando scripts manuais `fs` em `ctx_execute` (violação estrita de R-045 / RNF-004 e Smell 2.26).
- ❌ **NUNCA** modificar arquivos de aplicação durante a execução deste prompt — sua saída exclusiva é a especificação e o prompt sintetizado.
- ❌ **NUNCA** apresentar o prompt sintetizado como solução final ao usuário — o artefato é de consumo exclusivo downstream para inicialização de uma nova sessão limpa.
- ❌ **NUNCA** emitir uma resposta "caixa-preta" ocultando o Painel de Evidências por Etapa.
- ❌ **NÃO** inferir intenções de negócio ou requisitos técnicos não fundamentados.
- ✅ **SEMPRE** priorizar caminhos de arquivos canônicos e contratos documentados.

---

## 🔄 Combina Com (Encadeamento)

```text
<solicitação-bruta> → /craft-prompt → [Novo Chat com Prompt Perfeito] → /plan ou @agent-router
```

- `<solicitação-bruta>`: Ideia inicial, bug report rascunhado ou requisito preliminar.
- `/craft-prompt`: Este prompt, sintetizando o artefato canônico com visibilidade total por etapa.
- `[Novo Chat]`: Sessão limpa onde o prompt sintetizado garante execução determinística e sem ruído de contexto anterior.

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
