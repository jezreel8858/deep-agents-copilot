---
name: governance-audit-patterns
description: >
  Catálogo consolidado de "agent/governance smells" — anti-padrões estruturais,
  gaps de conformidade com templates canônicos (agents, skills, prompts),
  desalinhamento contratual (perfil ↔ tools ↔ skills ↔ catálogo),
  violação do protocolo de batching (R-046 / Single-Turn Batching / limiar de 5 arquivos),
  desvios de sintaxe e variáveis de prompts, não conformidade com a spec de skills
  (progressive disclosure, gatilhos em 3ª pessoa), diretrizes redundantes,
  gaps de taxonomia, conflito de responsabilidade entre agents, prompts e skills
  (fronteira decisão vs conhecimento vs atalho) e hipertrofia instrucional e redundância de saída em runtime (output bloat, banners multicamada). Base de conhecimento normativa do agent-auditor.
tier: 1
category: governance
triggers:
  - "auditoria de governança"
  - "agent smell"
  - "anti-padrão de agent"
  - "gap de perfil"
  - "auditar tools"
  - "perfil vs tools"
  - "tools vs skills"
  - "diretriz redundante"
  - "cobertura de categoria"
  - "auditar templates"
  - "auditar prompts"
  - "auditar skills"
  - "auditar R-046"
  - "conformidade de catalogo"
  - "conflito de responsabilidade"
  - "sobreposição agent prompt skill"
  - "output bloat"
  - "redundância de saída em runtime"
  - "hipertrofia instrucional"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/agent-contracts/SKILL.md
  - .github/skills/code-review-patterns/SKILL.md
  - .github/skills/agent-safety-guardrails/SKILL.md
  - .github/skills/governance-factory-patterns/SKILL.md
  - .github/skills/efficient-batch-code-modification/SKILL.md
  - docs/plan/categorizacao-agents-mercado.md
tools: []
---

# Governance Audit Patterns

## 0) Propósito

Consolida, a partir de pesquisa de mercado (2025/2026), Anthropic Open Spec (dez/2025), padrões de extensibilidade do VS Code Copilot e regras normativas do repositório, um catálogo objetivo de "cheiros" (smells) de governança detectáveis em artefatos `.agent.md`, `SKILL.md` e `.prompt.md`. Evita que uma auditoria de catálogo (ex.: agent `agent-auditor`) invente critérios ad-hoc. Cada smell é definido por: **nome · sintoma observável · como detectar · severidade · remediação (agent executor a acionar)**.

## 1) Fundamentação de Mercado e Governança

| Fonte | O que aporta |
|---|---|
| `SpecDetect4LLM` (arXiv:2512.18020, 2026) | Padrão de catalogar "cheiros" de forma estática: nome, sintoma, efeito na qualidade, remediação — adaptado aqui para artefatos de governança |
| Anthropic Open Spec (dez/2025) & Skill Architecture | Padrão de *Progressive Disclosure* em 3 níveis (Metadados N1, Corpo N2, Recursos N3), descrições imperativas em 3ª pessoa e blocos de contraste ✅/❌ |
| VS Code Copilot Agent/Prompt Engine | Variáveis de contexto nativas (`${file}`, `${selection}`, `${workspaceFolder}`, `${input:param}`), convenção `argument-hint` e parsing estrito de display names em `model:` |
| TrustAgent taxonomy (KDD 2025) | Classifica origem do gap: **intrínseco** (brain/memory/tool do próprio agent) vs. **extrínseco** (user/other agents/environment) |
| Protocolo R-046 & `efficient-batch-code-modification` | Hierarquia estrita de batching: editor tools para 1-4 arquivos em *Single-Turn Batching*; sandbox `ctx_execute`/`ctx_execute_file`/`ctx_batch_execute` para 5+ arquivos ou operações repetitivas |
| Matriz Biparadigma (§9 de `governance-factory-patterns`) | Alocação pragmática de SLM vs LLM: **Procedural/Operacional** (`Gemini 3.8 Flash`) vs **Decompositivo/Raciocínio Guiado** (`Claude Sonnet 5`) |
| `code-review-patterns` (já existente) | Taxonomia de severidade tripla (**Bloqueador \| Alto \| Sugestão**) — reaproveitada nesta skill |
| `agent-contracts/SKILL.md` §8-9 | Baseline de formato de saída por perfil e tooling mínimo por perfil |

## 2) Catálogo de Smells de Governança

### 2.1 — Anti-padrão Estrutural (Duplicação sem Skill Equivalente)

| Campo | Conteúdo |
|---|---|
| Sintoma | Bloco de conteúdo quase idêntico (>70% de sobreposição textual/estrutural) repetido em 3+ arquivos `.agent.md`/`SKILL.md` |
| Como detectar | `grep_search` por trechos característicos (títulos de seção, frases-chave) em `.github/agents/*.agent.md`; comparar contagem de ocorrências × ausência de skill equivalente em `.index.json` |
| Origem (TrustAgent) | Intrínseco — falta de reuso de conhecimento compartilhado entre agents |
| Severidade | Alta (custo de manutenção cresce linearmente com nº de agents afetados) |
| Remediação | Extrair para nova skill via `@governance-factory`; atualizar os agents consumidores para referenciar a skill (não duplicar) |

### 2.2 — Gap de Perfil (Agent Incompleto)

| Campo | Conteúdo |
|---|---|
| Sintoma | Agent sem `run_subagent` no frontmatter `tools:` (R-042); sem seção "Retorno ao Router"; sem banner "Agente Ativo" no Formato de Saída; sem "Docs Sempre Anexadas"; sem `version` quando outros agents do mesmo tier já declaram; ou falta de `description` válida (≤ 500 caracteres, conforme §10 de `governance-factory-patterns`) |
| Como detectar | Checklist de `agent-contracts/SKILL.md` §9 e `governance-factory-patterns` §3 aplicado retroativamente a todo `.agent.md` existente |
| Origem (TrustAgent) | Intrínseco — componente "tool"/"brain" do agent incompleto |
| Severidade | **Bloqueador** (se falta `run_subagent` — R-042 estruturalmente inviável) / **Alta** (demais gaps de perfil) |
| Remediação | `@governance-factory` revisa e completa o agent afetado |

### 2.3 — Gap de Diretriz (Regra Não Referenciada ou Sem Enforcement)

| Campo | Conteúdo |
|---|---|
| Sintoma | Regra normativa `R-001..R-046` declarada em `CLAUDE.md` mas nunca referenciada por nenhum agent/skill; ou referenciada em prosa mas sem nenhum checklist/mecanismo que a torne verificável |
| Como detectar | `grep_search` de cada `R-0XX` em `.github/agents/` + `.github/skills/`; contagem zero ou "referência solta sem checklist correspondente" |
| Origem (TrustAgent) | Extrínseco — desalinhamento entre política declarada (environment/governance) e comportamento do agent |
| Severidade | Alta (regra sem enforcement é regra decorativa) |
| Remediação | `@docs-engineer` avalia se a regra deve ganhar checklist explícito em skill/agent relevante, ou ser removida de `CLAUDE.md` por obsolescência |

### 2.4 — Diretriz Redundante (Duplicação entre Camadas de Governança)

| Campo | Conteúdo |
|---|---|
| Sintoma | Mesma regra/conteúdo normativo duplicado em `CLAUDE.md` **e** `copilot-instructions.md` **e/ou** uma skill — viola R-003 (sem duplicação entre camadas) |
| Como detectar | Comparação textual entre os 3 arquivos-fonte de governança global + skills candidatas; sobreposição >50% de uma seção inteira é sinal forte |
| Origem (TrustAgent) | Extrínseco — múltiplas fontes de verdade para a mesma política |
| Severidade | Média / Sugestão (risco de drift quando só 1 das cópias é atualizada) |
| Remediação | `@docs-engineer` consolida em 1 única fonte de verdade e substitui as demais por referência |

### 2.5 — Gap de Cobertura de Categoria (Taxonomia)

| Campo | Conteúdo |
|---|---|
| Sintoma | Grupo taxonômico de `categorizacao-agents-mercado.md` §2 sem nenhum agent correspondente no catálogo real; **ou** 2+ agents ocupando o mesmo papel taxonômico sem distinção clara de escopo (sobreposição funcional) |
| Como detectar | Cruzar `docs/plan/categorizacao-agents-mercado.md` §2 (grupos mapeados) contra `.github/agents/catalog.yaml` (agents reais) |
| Origem (TrustAgent) | Extrínseco — desenho do sistema multi-agent (arquitetura de orquestração) |
| Severidade | **Alta** se sobreposição ativa (2 agents competindo pelo mesmo papel); **Sugestão** se é apenas um gap de categoria intencionalmente não coberta |
| Remediação | Propor fusão/substituição via `@governance-factory` + atualização de `agent-router` ou registrar gap intencional |

### 2.6 — Vazamento de Evidência Real (R-044)

| Campo | Conteúdo |
|---|---|
| Sintoma | Arquivo commitado sob `.github/**` (exceto `local/`), `CLAUDE.md` ou `docs/ai-context/catalog.yaml` contém nome de repositório/classe/método/pacote/namespace/caminho de arquivo REAL derivado de análise de projeto do usuário (típico de agents analíticos como `code-knowledge-graph`, `business-rules-extractor`, `context-builder`, `project-scanner`) |
| Como detectar | `grep_search` por padrões de caminho absoluto (`[A-Za-z]:\\`, `/home/`, `/Users/`) e por identificadores específicos nos arquivos de governança; comparar com checklist de R-044 |
| Origem (TrustAgent) | Intrínseco — agent confunde evidência efêmera da conversa com evidência persistível em arquivo compartilhado |
| Severidade | **Bloqueador** (risco de privacidade e contaminação de workspace) |
| Remediação | Genericizar in-place (repositório → `[PROJETO-X]`, classe → `ServicoExemploX`, caminho → `<workspace>/[PROJETO-X]`) e acionar `@governance-factory` para adicionar guardrail no agent de origem |

### 2.7 — Desalinhamento Contratual (Perfil ↔ Tools ↔ Skills ↔ Catálogo)

| Campo | Conteúdo |
|---|---|
| Sintoma | Inconsistência entre papel/perfil declarado do agent e as ferramentas ou competências atribuídas: *(a)* agent Read-Only / Advisory contendo tools mutativas de escrita (`create_file`, `insert_edit_into_file`); *(b)* agent com `run_in_terminal` sem declarar skill mandatória `terminal-governance`; *(c)* agent com MCP `context-mode/*` sem declarar skill `context-mode`; *(d)* agent implementer/fixer/tester sem ferramentas de validação (`get_errors`); *(e)* agent sem `run_subagent` no frontmatter (viola R-042); *(f)* divergência atômica (R-015) onde `tools:` ou `skills:` do arquivo `.agent.md` divergem do `catalog.yaml` ou `<stack>-catalog.yaml`. |
| Como detectar | Execução da **Matriz Canônica de Conformidade (§2.7.1)** cruzando cada `.agent.md` contra seu catálogo e regras de `agent-contracts/SKILL.md` § 8-9 |
| Origem (TrustAgent) | Intrínseco — violação de integridade entre contrato do agente (brain/tools) e habilidades declaradas (skills/memory) |
| Severidade | **Bloqueador** se: tool mutativa em agent read-only; falta de `run_subagent` (R-042); ou uso de terminal sem `terminal-governance`.<br>**Alta** se: divergência entre `.agent.md` e `catalog.yaml` (R-015); falta de `get_errors` em agent implementer; ou MCP `context-mode` sem skill correspondente.<br>**Sugestão** se: skills de domínio complementares ausentes. |
| Remediação | `@governance-factory` revisa o `.agent.md` e sincroniza o `catalog.yaml` / sub-catálogo na mesma entrega (R-015) |

### 2.7.1 — Matriz Canônica de Conformidade (Perfil ↔ Tools ↔ Skills)

| Perfil / Papel do Agent | Tools Permitidas | Tools Proibidas | Skills Mandatórias |
|---|---|---|---|
| **Read-Only / Advisor / Critic**<br>*(ex.: `*-arch-advisor`, `security-reviewer`, `performance-agent`, `compliance-guardrails`, `agent-auditor`)* | `read_file`, `grep_search`, `file_search`, `list_dir`, `ask_questions`, `run_subagent`, `context-mode/*` | ❌ `create_file`, `insert_edit_into_file`, `replace_string_in_file` | `agent-contracts`, skill da especialidade |
| **Implementer / Feature-Developer**<br>*(ex.: `*-feature-developer`)* | `read_file`, `create_file`, `insert_edit_into_file`, `get_errors`, `run_in_terminal`, `ask_questions`, `run_subagent`, `context-mode/*` | ❌ Ausência de `get_errors` | Skill de implementação da stack, `test-implementation-*` |
| **Fixer / Bug-Fixer / Test-Fixer**<br>*(ex.: `*-bug-fixer`, `*-test-fixer`)* | `read_file`, `insert_edit_into_file`, `get_errors`, `run_in_terminal`, `ask_questions`, `run_subagent`, `context-mode/*` | ❌ Ausência de `get_errors` | `code-tracing` (para bug-fixer), skill da stack |
| **Tester / Test-Writer**<br>*(ex.: `*-unit-test-writer`, `*-component-test-writer`, `*-integration-test-writer`, `*-e2e-writer`)* | `read_file`, `create_file`, `insert_edit_into_file`, `get_errors`, `run_in_terminal`, `ask_questions`, `run_subagent`, `context-mode/*` | ❌ Ausência de `get_errors` | `test-implementation-*` correspondente |
| **Domain Router / Supervisor**<br>*(ex.: `*-router`)* | `read_file`, `file_search`, `grep_search`, `list_dir`, `ask_questions`, `run_subagent`, `context-mode/ctx_search` | ❌ `create_file`, `insert_edit_into_file`, `run_in_terminal` | `agent-contracts`, `handoff-governance` |

#### Invariantes Transversais de Tooling:
1. **Tool `run_in_terminal` presente** ➔ **OBRIGATÓRIO** declarar a skill `terminal-governance` nas `skills:` e `source_docs:` do `.agent.md` e em `catalog.yaml`.
2. **Tools `context-mode/*` presentes** ➔ **OBRIGATÓRIO** declarar a skill `context-mode` nas `skills:` e `source_docs:` do `.agent.md` e em `catalog.yaml`.
3. **Tool `run_subagent`** ➔ **OBRIGATÓRIO E BLOQUEANTE** em 100% dos agents (R-042).
4. **Sincronismo R-015** ➔ As ferramentas declaradas no frontmatter `tools:` e as skills em `skills:` do `.agent.md` DEVEM ser idênticas às declaradas no `catalog.yaml` (ou `<stack>-catalog.yaml`).

---

### 2.8 — Violação de Batching e Limiar de Modificação (R-046)

| Campo | Conteúdo |
|---|---|
| Sintoma | Agent com capacidade de mutação/edição de código que *(a)* não declara em seu workflow ou regras o protocolo de *Single-Turn Batching* e a hierarquia de limiar (1-4 arquivos via editor tools vs 5+ arquivos ou operações repetitivas via `ctx_execute`/`ctx_execute_file`/`ctx_batch_execute`); *(b)* prevê ou executa edições sequenciais arquivo por arquivo gerando turnos redundantes de chat; *(c)* prevê releitura imediata pós-edição apenas para "conferir" se salvou; ou *(d)* executa ou instrui validação via `get_errors` dispersa por arquivo ao invés de chamada única com array agregado `filePaths: [...]`. |
| Como detectar | Inspecionar seções de Workflow/Regras em `.agent.md` executores e skills de implementação; checar presença de menção a Single-Turn Batching e R-046; verificar ausência da skill `efficient-batch-code-modification` em agents com escrita massiva |
| Origem (TrustAgent) | Intrínseco — protocolo de execução ineficiente gerando consumo desnecessário de tokens e créditos |
| Severidade | **Alta** (impacto direto de custo e latência na experiência do usuário) |
| Remediação | `@governance-factory` atualiza o workflow do agent incorporando o protocolo de *Single-Turn Batching*, limiar de 5 arquivos e validação única via `get_errors` agrupado |

### 2.9 — Não Conformidade com Template Canônico de Agent e Matriz de Modelo

| Campo | Conteúdo |
|---|---|
| Sintoma | Arquivo `.agent.md` que diverge dos templates canônicos (`.github/agents/templates/agent-template.md`, `operational-agent.md`, `research-agent.md`): *(a)* ausência dos blocos contrastantes obrigatórios `## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO` com sub-seções `### ✅ O que este agente FAZ` e `### ❌ O que este agente NUNCA faz`; *(b)* ausência de workflow sequencial numerado; *(c)* ausência de Contrato Operacional com entradas mínimas e formato de saída estruturado; *(d)* modelo configurado em desacordo com a Matriz Biparadigma (`"Gemini 3.8 Flash"` para procedural/operacional vs `"Claude Sonnet 5"` para deliberativo/decompositivo); *(e)* `model:` declarado como array ou kebab-case sem validação via `get_errors`; ou *(f)* `description` > 500 caracteres ou com changelog embutido (§10). |
| Como detectar | Comparação estrutural contra os templates de referência em `.github/agents/templates/` e validação de `model:` via `get_errors` |
| Origem (TrustAgent) | Intrínseco — inconsistência estrutural e instrucional do agente |
| Severidade | **Bloqueador** se `model:` inválido (`Unknown model`) ou ausência de escopo delimitado; **Alta** para ausência de blocos ✅/❌ ou workflow numerado; **Sugestão** para pequenos desvios de formatação |
| Remediação | `@governance-factory` reestrutura o `.agent.md` alinhando-o estritamente ao template correspondente de seu paradigma |

### 2.10 — Desvio de Sintaxe e Variáveis em Prompts (`.prompt.md`)

| Campo | Conteúdo |
|---|---|
| Sintoma | Arquivo `.prompt.md` que diverge de `.github/prompts/templates/prompt-template.md`: *(a)* ausência de `argument-hint` no frontmatter quando o comando aceita parâmetros dinâmicos; *(b)* uso de variáveis ad-hoc ou incorretas em vez das variáveis nativas do VS Code Copilot (`${file}`, `${selection}`, `${workspaceFolder}`, `${input:param}`); *(c)* ausência do bloco delimitador `## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO`; *(d)* ausência de checklist de pré-apresentação ou formato de saída estruturado; *(e)* nomenclatura fora do padrão kebab-case `<verbo>-<objeto>.prompt.md`. |
| Como detectar | Inspeção do frontmatter e corpo dos prompts em `.github/prompts/*.prompt.md` contra o template canônico |
| Origem (TrustAgent) | Intrínseco — quebra de compatibilidade com a runtime de prompts do VS Code Copilot |
| Severidade | **Alta** se ausência de variáveis nativas onde esperado ou falta de escopo estrito; **Sugestão** se falta de `argument-hint` ou detalhamento cosmético |
| Remediação | `@governance-factory` refatora o `.prompt.md` aplicando as variáveis nativas e o template oficial |

### 2.11 — Não Conformidade com a Spec de Skills (Progressive Disclosure)

| Campo | Conteúdo |
|---|---|
| Sintoma | Arquivo `SKILL.md` que diverge de `.github/skills/templates/skill-template.md` ou dos princípios da Anthropic Open Spec: *(a)* quebra de *Progressive Disclosure* — Nível 1 ausente ou incompleto no frontmatter (`name`, `description` em 3ª pessoa com gatilho e limite negativo, `tier`, `category`, `triggers` em PT-BR); *(b)* Nível 2 ausente ou com seções obrigatórias faltantes (`## 0) Problema Resolvido`, `## 1) Quando Usar vs Quando NÃO Usar` com blocos contrastantes ✅/❌, `## 2) Diretrizes Operacionais`, `## 3) Padrões Canônicos com Exemplos Contrastantes ✅/❌`, `## 4) Checklist`); *(c)* código inline excedendo 8 linhas violando R-026 (deveria residir em `snippets/` ou `templates/` no Nível 3); *(d)* `description` redigida em 1ª pessoa ou sem declarar quando usar e quando NÃO usar; ou *(e)* falta de sincronização atômica em `.github/skills/.index.json` e `README.md` (R-015). |
| Como detectar | Inspeção das skills em `.github/skills/*/SKILL.md` contra `skill-template.md` e contagem de linhas em blocos de código inline |
| Origem (TrustAgent) | Intrínseco — degradação da clareza instrucional e consumo ineficiente de contexto |
| Severidade | **Bloqueador** se ausência de frontmatter N1 ou quebra de R-015 no índice; **Alta** se código inline > 8 linhas (R-026) ou ausência de blocos ✅/❌; **Sugestão** se refinamento estilístico de gatilhos |
| Remediação | `@governance-factory` reestrutura a skill conformando-a aos 3 níveis de *Progressive Disclosure* e extraindo códigos longos para snippets |

### 2.12 — Conflito de Responsabilidade Cross-Artefato (Agents vs Prompts vs Skills)

| Campo | Conteúdo |
|---|---|
| Sintoma | Sobreposição de responsabilidade funcional entre um `.agent.md`, uma `SKILL.md` e/ou um `.prompt.md` que tratam do MESMO domínio/ação sem fronteira clara de papel: *(a)* um `.prompt.md` reimplementa lógica de decisão/fluxo que deveria pertencer ao agent (deixando de ser um "alias fino" que apenas invoca `@agent`); *(b)* uma `SKILL.md` contém instruções de orquestração/roteamento/decisão (verbos como "delegar", "rotear", "decidir entre X ou Y") em vez de conhecimento declarativo reutilizável — skills não devem tomar decisão de fluxo; *(c)* um `.agent.md` embute bloco extenso de conhecimento de domínio que deveria estar extraído como skill reutilizável (relacionado mas distinto do smell 2.1, que é duplicação entre agents — aqui é agent carregando peso que é papel de skill); *(d)* dois ou mais artefatos de tipos DIFERENTES (agent + skill, ou agent + prompt, ou skill + prompt) descrevem a MESMA responsabilidade com fronteiras redundantes, deixando ambíguo qual arquivo é a fonte de verdade operacional para aquele domínio. |
| Como detectar | Cruzar o propósito declarado (`description`) do `.agent.md` contra as skills que ele referencia em `skills:`/`source_docs:` e contra os `.prompt.md` que o invocam (`agent: '<nome>'` no frontmatter do prompt ou lógica duplicada no corpo); `grep_search` por verbos de fluxo/decisão ("delegar", "rotear", "decidir", "classificar intenção") dentro de `SKILL.md` — presença desses verbos como instrução operacional (não como exemplo) é sinal de invasão de papel; comparar percentual de lógica decisória duplicada entre prompt e agent (>30% de sobreposição de fluxo é sinal forte de que o prompt deixou de ser alias fino). |
| Origem (TrustAgent) | Extrínseco — desenho arquitetural do sistema multi-agent (fronteiras de papel mal definidas entre as 3 camadas de artefato: agent=decisão, skill=conhecimento, prompt=atalho de invocação) |
| Severidade | **Alta** se a sobreposição ativa gera ambiguidade real sobre qual artefato é a fonte de verdade operacional (2 artefatos podem ser invocados para o mesmo efeito com comportamento potencialmente divergente); **Sugestão** se é apenas duplicação leve de descrição/propósito sem impacto funcional comprovado. |
| Remediação | `@governance-factory` redefine a fronteira de responsabilidade: prompt volta a ser "alias fino" (apenas invoca o agent, sem lógica própria); skill perde qualquer instrução de fluxo/decisão e vira puro conhecimento declarativo; agent mantém a decisão/orquestração. Consolidar ou remover o artefato redundante quando a sobreposição for total. |

### 2.13 — Hipertrofia Instrucional e Redundância de Saída em Runtime (Output Bloat / Multi-Layer Redundancy)

| Campo | Conteúdo |
|---|---|
| Sintoma | Artefato (`.agent.md`, `.prompt.md` ou `SKILL.md`) que prescreve instruções prolixas ou formato de saída inflado em tempo de execução: *(a)* **Redundância Multicamada:** fluxo que instrui o modelo a imprimir os mesmos dados em múltiplas seções consecutivas (ex.: banner repetido, resumo preliminar, tabela detalhada e re-resumo final contendo os mesmos atributos); *(b)* **Overhead Cosmético:** prescrição de decorações ASCII pesadas, caixas de diálogo decorativas ou múltiplos banners visuais que poluem o histórico de chat e consomem janela de contexto desnecessariamente; *(c)* **Mismatch de Perfil (`agent-contracts` § 8):** agent do tipo Router ou Operacional instruído a emitir relatórios narrativos longos em vez de payload determinístico/compacto, ou agent Analista instruído a emitir prosa antes/depois de tabelas sem valor analítico novo; *(d)* **Violação de Postura Sênior (`R-029`):** prompts instruindo introduções genéricas ("Com certeza, vou analisar..."), conclusões redundantes ("Espero ter ajudado...") ou eco integral do contexto lido; *(e)* **Tamanho Desproporcional do Artefato:** prompt/agent com mais de 300 linhas de diretrizes cuja complexidade operacional real não justifica a densidade instrucional (prompt bloat). |
| Como detectar | Inspecionar a seção `Formato de Saída` de `.agent.md` e `.prompt.md`; contar blocos de exibição previstos; verificar repetição de variáveis/dados em mais de um bloco de saída; cruzar o perfil taxonômico do agent contra a tabela de templates de `agent-contracts` § 8; verificar presença de instruções mandatórias de ASCII art ou introduções de cortesia. |
| Origem (TrustAgent) | Intrínseco — falha no design instrucional do artefato, resultando em poluição de contexto, alta latência de streaming e consumo ineficiente de tokens/créditos de chat. |
| Severidade | **Alta** se há redundância multicamada grave (mesmos dados repetidos 3+ vezes) ou saída inflada que degrade sensivelmente a janela de contexto da sessão; **Sugestão** para pequenos ajustes de concisão, eliminação de frases de cortesia ou refinamento estético de saída. |
| Remediação | `@governance-factory` refatora a seção `Formato de Saída` e as diretrizes do artefato: consolida saídas dispersas em uma única apresentação densa (tabela ou checklist compacto), remove decorações cosméticas redundantes e alinha o template estritamente ao perfil correspondente em `agent-contracts` § 8 e `R-029`. |

**Matriz de Fronteiras §2.13 (Anti-Sobreposição):**

```text
[Smell 2.1]  --> Duplicação ESTÁTICA de texto ENTRE 3+ arquivos do repositório.
[Smell 2.4]  --> Duplicação de REGRA NORMATIVA entre CLAUDE.md e copilot-instructions.
[Smell 2.8]  --> Ineficiência de TOOL CALLS no FILESYSTEM (R-046 / Single-Turn Batching).
[Smell 2.9]  --> Ausência ESTRUTURAL da seção "Formato de Saída" no .agent.md (presença do bloco).
[Smell 2.10] --> Erro de SINTAXE em variáveis de prompt (${file}, argument-hint).
[Smell 2.11] --> Limite de CÓDIGO INLINE no corpo da skill (≤ 8 linhas via R-026).
[Smell 2.12] --> Fronteira de AUTORIDADE/PAPEL funcional (decisão vs conhecimento vs atalho).
-----------------------------------------------------------------------------------------
[Smell 2.13] --> QUALIDADE, CONCISÃO E ECONOMIA DE TOKENS DO PAYLOAD DE CHAT (runtime output).
```

---

## 3) Severidade — Reaproveitamento da Taxonomia Existente

Esta skill **reaproveita** (não recria) a taxonomia de `code-review-patterns`:

| Severidade | Critério Objetivo de Enquadramento |
|---|---|
| **Bloqueador** | Gap que impede o funcionamento técnico ou a governança do artefato: falta de `run_subagent` (R-042); `model:` inválido ou desconhecido (`Unknown model`); tool de escrita em agent read-only; uso de terminal sem `terminal-governance`; vazamento de evidência real de projeto (R-044); ou dessincronização crítica no catálogo (R-015). |
| **Alto** | Gap que gera desperdício severo de tokens/créditos, duplicação de manutenção ou risco de drift: violação de batching (R-046); divergência de templates canônicos (ausência de escopo ✅/❌ ou workflow); falta de variáveis nativas em prompts; código inline > 8 linhas em skills (R-026); ou sobreposição funcional ativa entre 2 agents. |
| **Sugestão** | Melhoria técnica não urgente ou cosmética: refinamento de `argument-hint`; ajuste fino de `description` dentro do limite; ou gap taxonômico de categoria intencionalmente não coberta. |

## 4) Cross-check de Segurança (Referência, Não Duplicação)

Para riscos de segurança (excessive agency, tool sprawl, goal hijacking), referenciar diretamente `agent-safety-guardrails/SKILL.md` — esta skill **não duplica** aquele conteúdo, apenas sinaliza quando um smell estrutural (ex.: agent com tools muito além do necessário para seu escopo declarado) deve ser cruzado com o checklist de segurança daquela skill.

## 5) Formato de Saída Recomendado (para o agent consumidor)

```markdown
## Relatório de Auditoria de Governança

| Smell | Local(is) afetado(s) | Severidade | Remediação sugerida | Agent a acionar |
|---|---|---|---|---|
| <2.1..2.13> | <arquivo(s)> | Bloqueador/Alto/Sugestão | <ação objetiva> | <@governance-factory/@docs-engineer> |

## Resumo por Severidade
- Bloqueador: N
- Alto: N
- Sugestão: N

## Próximo Passo Mínimo
<aguardar aprovação item a item antes de qualquer remediação — R-033/R-031>
```

## 6) Checklist de Conformidade da Auditoria

- [ ] Todo achado classificado estritamente em uma das 13 categorias de smell (§2.1..§2.13).
- [ ] Severidade reaproveitada de `code-review-patterns` (Bloqueador/Alto/Sugestão).
- [ ] Origem classificada como intrínseca ou extrínseca (TrustAgent) quando relevante.
- [ ] Remediação aponta agent executor real do catálogo (nunca "corrigir diretamente" — agent de auditoria é estritamente read-only).
- [ ] Achados de segurança cruzados com `agent-safety-guardrails`, não recriados.
- [ ] Validações de tooling e perfil cruzadas com a Matriz Canônica de Conformidade (§2.7.1).
- [ ] Protocolo de Single-Turn Batching e limiar de 5 arquivos (R-046) verificado nos executores (§2.8).
- [ ] Conformidade de templates de Agent (§2.9), Prompt (§2.10) e Skill (§2.11) validada.
- [ ] Conflito de responsabilidade cross-artefato (agents vs prompts vs skills) verificado — fronteira decisão/conhecimento/atalho respeitada (§2.12).
- [ ] Hipertrofia instrucional e redundância de saída em runtime verificada — sem banners multicamada, overhead cosmético ou mismatch de perfil vs `agent-contracts` §8 (§2.13).

## 7) Anti-padrões

- ❌ Agent de auditoria aplicar a correção diretamente (deve ser read-only — só análise e recomendação).
- ❌ Inventar categoria de smell fora das 13 catalogadas nesta skill.
- ❌ Duplicar taxonomia de severidade ou checklist de segurança já existentes em outras skills.
- ❌ Reportar achado sem apontar agent executor de remediação (relatório inacionável).
- ❌ Classificar achados como Bloqueadores sem critério estrutural comprovado.

## 8) Consumidor Mapeado

- `agent-auditor` (único consumidor inicial — Critic/Analyst de meta-nível sobre o próprio catálogo de governança).

## 9) Referências

- Anthropic Open Spec & Claude Prompt Engineering Guidelines (dez/2025).
- GitHub Copilot Documentation: Prompt files & Native context variables (2025/2026).
- arXiv:2512.18020, "Specification and Detection of LLM Code Smells" (2026).
- EmergentMind, "Prompt Pattern Catalog".
- KDD 2025, "A Survey on Trustworthy LLM Agents" (TrustAgent taxonomy).
- OWASP GenAI Security Project, "Top 10 for Agentic Applications" (2026).
- Lumenova AI, "Governance Frameworks for Multi-Agent Systems" (2026).
- `docs/plan/plano-otimizacao-catalogo-agents.md` §D — origem desta skill.
