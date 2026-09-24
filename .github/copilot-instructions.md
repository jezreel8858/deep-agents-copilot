# Instruções de IA — Base de Governança Reutilizável

> Fonte de verdade operacional: [`CLAUDE.md`](../CLAUDE.md).
> Mapa do Repositório (Repo Map): [`docs/repo-map.md`](../docs/repo-map.md).
> Mapa de Adapters (compartilhado): [`.github/instructions/README.md`](../.github/instructions/README.md).
> Catálogo de Agents (Modelos e Metadados): [`.github/agents/catalog.yaml`](agents/catalog.yaml).
> Mapa de Projetos (LOCAL/gitignored, R-043): [`.github/projects.local.yaml`](../.github/projects.local.yaml).
> IDs normativos: consulte `CLAUDE.md`.

---

## 1) Diretriz de Governança

- Este arquivo define **execução operacional** e **roteamento rápido**.
- Regras globais devem ficar em `CLAUDE.md` para evitar duplicação.
- Em conflito, siga a hierarquia definida em `CLAUDE.md`.

### 📋 Separação Clara: Governança Global vs. Adapters

| Tipo | Arquivo | Escopo | Conteúdo Permitido | Exemplos / Referências |
|------|---------|--------|-------|---|
| **Governança Global** | `CLAUDE.md` | 🌍 Multi-projeto, desacoplado | Regras normativas globais (R-xxx), princípios, fluxos genéricos | ❌ Nenhum projeto/tech específicos |
| **Operacional** | `.github/copilot-instructions.md` | 🌍 Multi-projeto, desacoplado | Roteamento, agents, skills, estrutura genérica | ❌ Nenhum projeto/tech específicos (remeter a adapters) |
| **Adapters** | `.github/instructions/*.instructions.md` | 🔧 Stack/domínio específico | Convenções, padrões, tools, paradigmas de tech/domínio **excluivos** | ✅ Projeto, linguagem, framework **específicos permitidos** |
| **Contexto de Binding** | `.github/instructions/README.md` + `.github/instructions/README.md` | 🔗 Mapa de instâncias | Lista concreta de adapters, projetos, mapeamento stack → adapter | ✅ Dados de instância permitidos |

---

## 1.1) 🚀 **AGENT ROUTER FIRST — Ponto de Entrada Obrigatório** (R-037)

**SEM EXCEÇÃO:** Toda solicitação deve começar com `@agent-router`.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   PRIMEIRA AÇÃO: Invocar `@agent-router`               │
│                                                         │
│   Motivo:                                              │
│   - Classificação de intenção (triagem)                │
│   - Decisão de rota para agent correto                 │
│   - Prevenção de implementação direta sem triagem      │
│   - Garantia de governança agent-first                 │
│                                                         │
│   Proibido:                                            │
│   ❌ Pular router e ir direto para agent específico    │
│   ❌ Chamar múltiplos agents sem triagem               │
│   ❌ Implementar sem passar por roteamento             │
│   ❌ Ler .agent.md de agent p/ simular papel (R-062)   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Fluxo garantido:**

```
Solicitação (turno N)
    ↓
@agent-router (triagem inicial & Health Check R-034)
    ↓
Agent ativo de turno anterior? (R-042)
    ├─ Não -> triagem normal (OBRIGATÓRIO invocar @agent-router via run_subagent antes de qualquer tool — R-063; "ausência de agent ativo" NUNCA autoriza execução direta)
    └─ Sim -> checar deriva de intenção antes de responder
              ├─ Sem deriva -> devolve ao agent ativo (sem re-rotear)
              └─ Deriva -> handoff (motivo: "deriva_de_intencao") -> triagem completa
    ↓
[CLASSIFICAÇÃO DE WORKFLOW & FAST-PATH (R-041/R-050)]
    ├─ Fast-Path Determinístico (Bug / Layout / Refatoração com alvo / Análise direta / Governança)
    │   └─ Ingressa IMEDIATAMENTE no respectivo Workflow Canônico (R-050) — zero desvio
    └─ Caso Ambíguo / Feature Aberta / Pedido não estruturado
        └─ @prompt-structuring (R-041 — loop máx. 5 iterações) → retorno obrigatório a @agent-router
    ↓
[Execução Sequencial no Workflow Canônico (R-050)]
    ├─ WORKFLOW-BUG-FIX: @bug-triage (RCA 2 fontes + flaky/regressão) → red-test (baseline) → bug-fixer (blast radius & rollback) → green-test & mini mutation → quality-gate (canary)
    ├─ WORKFLOW-REFACTORING: rules (ground truth) → blast radius & contract testing (Pact) → @refactor-planner (Mikado DAG) → batch-exec → validation & redundância proporcional (rollback blast_radius_revertido)
    ├─ WORKFLOW-TECHNICAL-ANALYSIS: scope → deterministic analysis → report
    ├─ WORKFLOW-FEATURE-DEVELOPMENT: requirements → blueprint → test-strategy → TDD → gate
    ├─ WORKFLOW-GOVERNANCE-MAINTENANCE: audit → human approval → batch execution
    ├─ WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION: scan → blast-radius → bump → adapt → quality-gate
    ├─ WORKFLOW-FRAMEWORK-MIGRATION: assessment (5D + symbol exhaustion) → blueprint & matriz de-para → codemod anti-omission → dual-verification parity → quality-gate baseline → post-migration redundancy gate
    ├─ WORKFLOW-RELEASE-READINESS: contracts → db-rollout → security/hygiene → changelog → verdict
    └─ WORKFLOW-PROMPT-SYNTHESIS: elicitation (@requirements-analyst + ask_questions) → grounding (@code-knowledge-graph) → constraints → structured synthesis (cache-aware) → quality gate (.md code block)
    ↓ (toda resposta abre com "Agente Ativo: <name>" — visibilidade de fluxo, agent-contracts § 0)
Turno seguinte muda de fase/escopo? (R-042)
    ├─ Sim -> agent ativo retorna a @agent-router (handoff de deriva; resposta seguinte mostra "Handoff: <origem> → <destino>")
    └─ Não -> agent ativo continua respondendo no workflow (reafirma "Agente Ativo: <mesmo-name>")
```

---

## 1.2) 📋 **Matriz de Decisão — Quando Pedir Contexto (R-006)**

**Vide** `.github/agents/agent-router.agent.md` § *R-006 (Pré-condições — Matriz de Decisão: Quando Pedir Contexto)*.

Esta matriz é **responsabilidade do roteador** — não é regra global.

**Regra de Ouro**: Se downstream consegue agir (ou pedir contexto iterativamente), não bloqueie com pré-voo.

---

## 2) 🛑 Regras de Autonomia (não negociáveis)

### ✅ Sempre

- **Agent Router First (R-037)**: TODA solicitação começa com `@agent-router`. Pular router é violação de governança. **Salvaguarda Anti-Duplicação**: Quando o `@agent-router` retornar a decisão de rota (`Delegado: @<agent>`), o Orquestrador Raiz despacha o agent downstream UMA ÚNICA VEZ em nível plano (Flat Delegation). Se a resposta do subagente já contiver o resultado de execução concluída do downstream, o Orquestrador NUNCA deve re-invocar o mesmo agent.
- **Re-triagem Obrigatória por Turno (R-042 — Anti Sticky-Session)**: R-037 aplica-se a CADA novo turno, não só ao primeiro. Agent downstream ativo deve checar deriva de intenção (mudança de verbo de ação, stack fora de competência, pedido de execução em agent read-only, ou nova solicitação após conclusão de workflow anterior — R-052) a cada mensagem; ao detectar deriva ou nova demanda, retorna IMEDIATAMENTE ao `@agent-router` (payload `handoff-governance` § 2.1, `motivo: "deriva_de_intencao"` ou `"conclusao_de_workflow_anterior"`) — nunca prossegue silenciosamente fora do escopo nem retém a sessão por mera afinidade de stack (*Anti Sticky-Agent*). *Exceção de ação in-scope*: refinamento imediato da mesma tarefa ou sub-rotina já prevista em "Quando Delegar" do agent ativo (ex.: pesquisa externa via `@deep-search` solicitada a `@tech-solution-architect` ativo; controle retorna ao agent ativo com call stack `origem_contexto.parent_agent`). Ao concluir a tarefa ou workflow, o controle reverte compulsoriamente ao router. **Visibilidade obrigatória**: TODO agent (não apenas o `agent-router`) abre toda resposta com `Agente Ativo: <name>`; se houve handoff/re-triagem neste turno, adiciona `Handoff: <origem> → <destino> (motivo: ...)` — padrão de mercado (OpenAI Agents SDK `HandoffOutputItem`, LangGraph `active_agent` streaming; detalhes em `agent-contracts/SKILL.md` § 0). **Pré-requisito de tooling**: o handoff só é efetivo via tool `run_subagent`; por isso `run_subagent` é obrigatório e bloqueante no frontmatter `tools:` de todo agent (`agent-contracts/SKILL.md` § 9). Persistência estruturada opcional do handoff (schema `handoff-governance` v1.1, campo `roteamento_grafo`) via `ctx_index` é permitida como camada auxiliar de auditoria/memória entre sessões, mas NUNCA substitui o banner nem é lida de forma bloqueante a cada turno do `@agent-router`.
- **Prompt Structuring & Fast-Path Determinístico (R-041)**: após o Health Check (R-034), o `@agent-router` avalia se a solicitação possui gatilho determinístico para Fast-Path (`WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-TECHNICAL-ANALYSIS`, `WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-PROMPT-SYNTHESIS`). Em caso positivo, o Fast-Path bypassa `@prompt-structuring` diretamente para a etapa 1 do workflow. Se o pedido for ambíguo, aberto ou uma feature de alto nível não estruturada, delega compulsoriamente ao `@prompt-structuring` (loop máx. 5 iterações), que SEMPRE retorna ao `@agent-router`.
- **Reset Mandatório pós-Conclusão de Workflow (R-052 — Anti Sticky-Agent)**: Ao finalizar qualquer um dos 9 workflows canônicos ou entrega de código, o ciclo é considerado concluído. O agente downstream ativo é **terminantemente proibido de assumir a próxima solicitação do usuário diretamente**, mesmo que pertença à mesma linguagem ou stack. Qualquer novo pedido, relato de defeito ou ajuste deve ser obrigatoriamente devolvido ao `@agent-router` para nova triagem e despacho pelo orquestrador raiz em nível plano (Flat Delegation).
- **Workflows Operacionais Determinísticos (R-050)**: toda tarefa de desenvolvimento segue rigorosamente a máquina de estados de um dos 9 Workflows Canônicos (`WORKFLOW-BUG-FIX`, `WORKFLOW-REFACTORING`, `WORKFLOW-TECHNICAL-ANALYSIS`, `WORKFLOW-FEATURE-DEVELOPMENT`, `WORKFLOW-GOVERNANCE-MAINTENANCE`, `WORKFLOW-DEPENDENCY-VULNERABILITY-REMEDIATION`, `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-RELEASE-READINESS`, `WORKFLOW-PROMPT-SYNTHESIS`). **Paridade de Rigor Determinístico**: Bugfix (`WORKFLOW-BUG-FIX`) e Refatoração (`WORKFLOW-REFACTORING`) operam sob as mesmas garantias determinísticas consolidadas para a migração — RCA com 2 fontes de evidência observável (*evidence before hypothesis*), classificação flaky vs regressão real, declaração antecipada de blast radius e rollback plan, mini mutation-check anti falso-verde e canary pós-fix em bugfix; contract testing formal (Pact-style consumer-driven), camada de redundância proporcional ao blast radius (auditoria reversa de símbolos, mini mutation gate e differential replay leve) e governança de rollback com registro de `blast_radius_revertido` em refatoração; e Painel de Evidências por Etapa obrigatório em síntese de prompt (`WORKFLOW-PROMPT-SYNTHESIS`), vedando terminantemente a execução blackbox que oculta os achados intermediários. **Visibilidade Obrigatória no Chat (Anti-Cegueira)**: toda resposta do router e avanço de etapa por downstream DEVE renderizar o bloco visual `### 🗺️ Pipeline de Execução do Workflow (<total> etapas)` com marcadores `[✅]` (Concluído), `[▶]` (Em Andamento), `[⏳]` (Pendente), mapeando explicitamente agentes e etapas até a conclusão. Proibido pular etapas, omitir testes de caracterização em refatoração ou gerar becos sem saída descritivos sem handoff ou aprovação humana (R-047).
- **Grafo de Roteamento (R-040)**: o roteamento de agents DEVE ser declarado como dado estruturado em `.github/agents/routing-graph.yaml`. A Decision Tree em prosa é documentação derivada. Toda nova rota exige: *(a)* entrada no grafo; *(b)* atualização da Decision Tree; *(c)* novo caso em `.github/agents/evals/casos-roteamento.yaml`.
- **Execução Obrigatória via Context Mode (R-008 — Think in Code)**: O uso de `context-mode` MCP (`ctx_execute`, `ctx_batch_execute`, etc.) é 100% OBRIGATÓRIO para leituras, modificações e criações sempre que disponível; ferramentas nativas de editor são fallback exclusivo de indisponibilidade comprovada (ver `CLAUDE.md` § R-008 e `.github/skills/context-mode/SKILL.md`).
- **Vinculação Compulsória de Governança de Terminal em Tooling & Zero-Noise Test Execution (R-049)**: Todo agent (`*.agent.md`), prompt (`*.prompt.md`) ou entrada de catálogo que declare a ferramenta `run_in_terminal` em `tools:` DEVE compulsoriamente referenciar `.github/skills/terminal-governance/SKILL.md` em `source_docs:` (ou na seção `skills:` em sub-catálogos locais). É expressamente vedada a concessão de execução em terminal desprovida de vinculação com a respectiva skill de governança. Adicionalmente, todo agent especialista que executa suítes de teste DEVE declarar compulsoriamente `context-mode/ctx_execute` em `tools:` e aplicar a **Zero-Noise Test Policy** de `terminal-governance`: priorizar execução no sandbox `ctx_execute` (Think-in-Code) ou suprimir ruído de terminal via flags silenciosas (`-q`, `-B`, `--silent`) combinadas com filtros `grep`/`Select-String`.
- **Localização Determinística de Arquivos (Zero Blind Searches — Governance Indices First)**: Consulte compulsoriamente os caminhos canônicos dos índices de governança (§ 7) antes de buscar. NUNCA execute buscas cegas/especulativas (`file_search` ou `grep_search`) para arquivos de governança cujos caminhos são canônicos (ex.: `.github/agents/catalog.yaml` para metadados de agents, `.github/instructions/README.md` para binding). Em caso de `file_search` indispensável, use sempre curinga inicial (`**/<nome>`) para compatibilidade com workspaces multi-root. Os arquivos `.ignore` e `.rgignore` na raiz desocultam `.github/` para que ripgrep indexe o repositório sem falhas de 0 matches.
- **Pre-fetch automático pelo agent**: ao selecionar um agent, carregue automaticamente os `source_docs` declarados no `catalog.yaml` e anuncie o que foi anexado via a linha `Skills Carregadas:` do banner universal (R-042, `agent-contracts/SKILL.md` § 0) — nunca em prosa solta ou omitido. Usuário pode rejeitar com "Sem pre-fetch".
- **Um comando por vez**: leia o output uma única vez.
- **`get_errors` consolidado**: chame `get_errors` uma única vez ao final do lote com o array completo `filePaths`, nunca arquivo por arquivo.
- **Edições Agrupadas e em Lote (R-046 — Single-Turn Batching)**: Todas as alterações devem ser consolidadas compulsoriamente via script em processo único no sandbox (`ctx_execute`) com diffs cirúrgicos; proibido tool chaining sequencial no chat (ver `CLAUDE.md` § R-046 e `.github/skills/efficient-batch-code-modification/SKILL.md`).
- **Proteção Anti-Corrupção em Arquivo Único Grande/Estruturado e Markdown com Âncoras Repetidas (R-051)**: Para QUALQUER arquivo com >200 linhas, formato `.yaml`/`.yml`/`.json`, OU **Markdown estruturado** (`.agent.md`, `.instructions.md`, arquivos de governança com frontmatter YAML ou tabelas com entradas parecidas), é terminantemente proibido o uso de `insert_edit_into_file` ou de `replace_string_in_file` com âncoras ambíguas. O agente deve aplicar o **Padrão de Edição Segura Verificada** (`efficient-batch-code-modification` § 5): verificar unicidade estrita da âncora em memória (`count === 1`), abortar se `count !== 1` (nunca confiar no fallback fuzzy de `replace_string_in_file`), executar escrita all-or-nothing no sandbox via `ctx_execute` e reler imediatamente do disco para validar se seções críticas (como frontmatter `---`, cabeçalhos canônicos e contagem de linhas) permanecem íntegras.
- **Governança Estrita de Routers (R-054 — Zero Discovery, Least Privilege e Delegação Plana)**: Todos os agentes com perfil de roteador (central e domain routers) são estritamente classificadores de intenção e despachantes. Devem possuir exclusivamente o baseline de 7 ferramentas de leitura/roteamento, sendo terminantemente proibidos de possuir ferramentas mutativas, de terminal ou de sandbox (`ctx_execute`), proibidos de fazer discovery ou rodar scripts para analisar dúvidas de código antes de rotear (Zero Discovery), e proibidos de invocar downstream via `run_subagent` (Flat Delegation). **Blindagem contra Discovery de Modelos (R-054)**: É TERMINANTEMENTE PROIBIDO ao `agent-router` e domain routers chamar ferramentas de busca ou leitura (`read_file`, `grep_search`, `file_search`, `list_dir`) em tempo de execução para inspecionar `catalog.yaml` ou `*.agent.md` em busca do modelo do agent delegado. O mapeamento modelo ↔ agent é estático ou de melhor esforço (injetado no próprio prompt ou baseado em convenção conhecida). Se o router não souber de memória, emite o nome do agente sem travar a resposta ou ler o disco. Zero Discovery é absoluto e inegociável.
- **Portão de Reúso e Generalização Sistêmica em Governança (R-055 — Anti-Silo Fix)**: Toda solicitação de melhoria ou correção em agents, prompts ou skills DEVE obrigatoriamente acionar o *Systemic Reuse Gate* como prioridade máxima no `WORKFLOW-GOVERNANCE-MAINTENANCE`. Proibido aplicar correções pontuais isoladas (em silo): o agente responsável (`@agent-auditor`, `@governance-factory`, `@governance-maintainer`) deve responder compulsoriamente a Q1 (Impacto em artefatos irmãos/peers), Q2 (Atualização de templates canônicos em `templates/`) e Q3 (Criação/atualização de testes determinísticos no pytest) antes de finalizar a entrega.
- **Precedência Mandatória de Context Mode (R-056 — Anti-Editor Tool Sprawl)**: Ferramentas nativas de editor e varredura em terminal são estritamente proibidas quando context-mode estiver acessível; processamento opera no sandbox para eliminar vazamento de bytes no chat (ver `CLAUDE.md` § R-056 e `.github/skills/context-mode/SKILL.md`).

- **Proibição Estrita de Terceirização de Edição Manual ao Usuário por Agentes Analíticos / Read-Only (R-057 — Anti-Manual User Delegation & Automated Workflow Continuity)**: Agentes analíticos, auditores, advisors, supervisores e de triagem (read-only) são terminantemente proibidos de orientar o usuário a realizar alterações manuais no código ou em artefatos sob justificativa de ausência de ferramentas de mutação/edição em seu prompt. Identificada a necessidade de alteração, o agente analítico deve compulsoriamente avançar para a próxima etapa do workflow canônico (R-050) ou delegar a execução ao agente executor correspondente (Flat Delegation / handoff R-042/R-047), assegurando a continuidade autônoma do ciclo.
- **Blueprint Técnico e Decomposição Obrigatórios em Features Complexas (R-058 — Anti-Premature Implementation Bypass & Anti-Gap Dumping)**: Toda solicitação de nova feature que envolva criação/evolução de schema de banco (mesmo BaaS/Firestore), máquina de estados (3+ transições), concorrência/transações atômicas ou infraestrutura (push notifications, plugins nativos) NUNCA deve ser despachada diretamente para domain routers ou especialistas de código. O router DEVE encaminhar obrigatoriamente para `@tech-solution-architect` (WF4 Estado 3) para emissão de Technical Blueprint e aprovação no Checkpoint 3b. Se houver 3+ frentes de trabalho interdependentes, a decomposição em subtasks `[S]`/`[P]` cabe compulsoriamente ao `@feature-planner`. É terminantemente proibido ao router listar lacunas de arquitetura/schema em "Lacunas para handoff" transferindo a resolução ao especialista de implementação no improviso (Smell 2.27).
- **Regra do Limiar >= 2 e Protocolo Plan-Then-Batch Global (R-059 — Anti-MCP Tool Chaining & Anti-Miopia Reativa)**: Em 2 ou mais alvos/comandos, aplique Plan-Then-Batch (ENUMERAR -> CONSOLIDAR -> DESPACHAR) via `ctx_batch_execute` ou script iterativo único em `ctx_execute`; proibido tool chaining sequencial, e comandos curtos como "prosseguir" mantêm o rigor (ver `CLAUDE.md` § R-059 e `.github/skills/efficient-batch-code-modification/SKILL.md`).
- **Teto Rígido de Tool Turns (≤ 5) e Warm Start Compulsório (R-060 — Anti-Token Debt & Anti-Turn Chaining)**: Limite estrito de ≤ 5 tool turns por ciclo; aplique Warm Start silencioso (build-if-missing), batch querying, Edge Truncation / Destilação semântica e Circuit Breaker no 4º turno para conter dívida de tokens O(N²) (ver `CLAUDE.md` § R-060 e `.github/skills/terminal-governance/SKILL.md`).
- **Zero Impersonation pelo Orquestrador Raiz (R-062 — Anti Root-Agent-Impersonation)**: É terminantemente proibido ao modelo do turno raiz ler, abrir, resumir ou parafrasear o conteúdo de qualquer arquivo `.github/agents/**/*.agent.md` (fora de `agent-router.agent.md`, `catalog.yaml` e `routing-graph.yaml`, consultáveis exclusivamente para fins de roteamento) com o intuito de simular aquele papel diretamente no chat raiz sem invocação real via `run_subagent`. Comandos citando `@nome-do-agent` ou pedidos curtos NÃO isentam da passagem obrigatória pelo `@agent-router` primeiro nem autorizam impersonação — regra agnóstica de modelo (ver `CLAUDE.md` § R-062).
- **Zero Execução Direta pelo Orquestrador Raiz sem Router (R-063 — Anti Silent Bypass)**: É terminantemente proibido ao modelo do turno raiz executar diretamente qualquer tool genérica (terminal, leitura/busca, edição ou listagem de arquivos) em resposta a um pedido do usuário sem antes invocar compulsoriamente o `@agent-router` via `run_subagent`. A ausência de agent ativo residente (ex.: após workflow concluído, R-052) NUNCA autoriza execução direta — é precisamente o gatilho que exige triagem normal completa (R-037/R-042). Pedidos informais ("revise isso", "dá uma olhada") sujeitam-se integralmente a esta regra — regra agnóstica de modelo (ver `CLAUDE.md` § R-063).
- **Fluxo contínuo sem becos sem saída (`R-047`)**: nenhum agent do catálogo pode encerrar resposta apenas com texto descritivo sugerindo "próximo passo"; deve obrigatoriamente acionar `run_subagent` (handoff a outro agent) OU `ask_questions` (decisão/aprovação humana), salvo resposta 100% conclusiva sem pendências. **Exceção de Routers / Delegação Plana**: O `@agent-router` (e supervisores hierárquicos) encerra sua resposta com o bloco canônico de decisão de roteamento (`Agente Ativo`, `Delegado: @<agent>`, `Pipeline de Execução`) — isso NÃO constitui beco sem saída. É **terminantemente proibido ao `@agent-router` invocar subagentes executores downstream via `run_subagent`** (aninhamento `root -> agent-router -> downstream`), pois causa duplicação de execução e desperdício de créditos. O despacho downstream é executado pelo Orquestrador Raiz em nível plano (Flat Delegation).
- **Plano Auto-Implementável (R-031)**: plano aprovado → execução integral sem interrupção. Pré-voo: escopo + contingências inline `[fallback: X]` + critério de falha tolerável. Parada permitida APENAS por: commit autônomo, credencial exposta, ou estado irrecuperável. Relatório final substitui checkpoints intermediários.
- **Estrutura de Resposta (R-028)**: toda implementação abre com resumo em 5 seções (Abordagem · Componentes · Código · Passos Cruciais · Impacto).
- **Postura Senior Engineer (R-029)**: bullets/tabelas > parágrafos · código limpo sem narrativa inline · tom direto sem filler de IA.
- **Sem código inline em agents/skills/prompts (R-026)**: blocos com implementações > 8 linhas pertencem a `snippets/`, `templates/` ou `commands/`. Referencie por caminho ou declare em `source_docs:`.
- **Genericidade Obrigatória (R-038)**: toda documentação em `.github/` **DEVE ser genérica**. Sem projetos específicos, tecnologias exclusivas ou convenções de domínio. Se é específico → vai para `.github/instructions/*.instructions.md` (adapter). Teste: substitua projeto por `[PROJETO]` e tech por `[TECH]` — continua válido?
- **Anonimização de Evidência Real (R-044)**: agents que analisam repositórios reais (`code-knowledge-graph`, `business-rules-extractor`, `context-builder`, `project-scanner`) **NUNCA** persistem nomes de repositório/classe/método/pacote/caminho real em changelog, README ou `.agent.md` commitado — genericize (`[PROJETO-X]`, `ServicoExemploX`, `com.exemplo.*`) ANTES de escrever. Métricas numéricas agregadas podem permanecer reais. Evidência real crua só é permitida na resposta efêmera do chat. Ver checklist em `CLAUDE.md` § R-044.

### ⚠️ Pergunte primeiro

- **Clarificação Obrigatória (R-027)**: qualquer dúvida → `ask_questions` com opções descritivas + última opção aberta. **Proibido inferir ou deduzir** intenção.
- **Documentação Especulativa Proibida vs Sincronização Automática de Docs Vivos (R-033)**: nunca crie documentos `.md` avulsos/especulativos sem pedido. Por outro lado, a **atualização e sincronização da documentação viva existente** do projeto (`docs/`, `README.md`, ADRs, schemas, catálogos) é **obrigatória, automática e orientada por autorreflexão** em qualquer entrega técnica que altere regras, padrões, modelos ou contratos.
- **Sem instalação autônoma**: aponte a dependência e aguarde confirmação.

### 🚫 Nunca

- **Sem commits/push autônomos**: gere apenas a mensagem via `/commit`. Nunca `git add/commit/push`.
- **Sem loops de correção**: se falhar, PARE, explique e aguarde aprovação.
- **Não crie arquivos auxiliares** sem pedido explícito.
- **Não releia arquivos** já no contexto da conversa ou recém-editados.
- **Exclusividade do Motor de Grafo (@code-knowledge-graph — R-045 / RNF-004)**: O CLI `@optave/codegraph` e o banco `.codegraph/graph.db` são recursos de uso e execução **EXCLUSIVOS** do agent `@code-knowledge-graph`. NENHUM outro agent tem permissão para rodar comandos `codegraph *` diretamente no terminal ou varrer diretórios manualmente (`list_dir`, `read_dir`) para mapear arquitetura, camadas, chamadas ou dependências. Toda análise estrutural DEVE ser delegada compulsoriamente via `run_subagent(agentName: 'code-knowledge-graph', ...)`. Agents especialistas operam em modo Advisory de forma estritamente analítica e read-only — `run_in_terminal` é restrito ao modo Implementação (testing-first).
- **Terminal sem Governança (R-049)**: nunca declarar `run_in_terminal` em `tools:` de novos agents ou prompts sem incluir `.github/skills/terminal-governance/SKILL.md` em `source_docs:` (ou `skills:` nos sub-catálogos locais).

### 2.1) context-mode — Regras Obrigatórias de Roteamento (JetBrains Copilot)

O uso de `context-mode` MCP é 100% OBRIGATÓRIO para leituras, modificações e criações de arquivos sempre que disponível (Think-in-Code, Limiar >= 2, Plan-Then-Batch, Teto de 5 tool turns, Warm Start). Regras normativas completas: `CLAUDE.md` § R-008, § R-046, § R-056, § R-059, § R-060 e skills `.github/skills/context-mode/SKILL.md`, `.github/skills/efficient-batch-code-modification/SKILL.md`, `.github/skills/terminal-governance/SKILL.md`.

**Playbook de roteamento (ordem fixa):**
1. `MEMORY` → `ctx_search(..., sort: "timeline")` antes de perguntar contexto ao usuário.
2. `GATHER` → `ctx_batch_execute(commands, queries)` com comandos rotulados.
3. `FOLLOW-UP` → `ctx_search(queries: [...])` com todas as perguntas no mesmo array.
4. `PROCESSING` → `ctx_execute` / `ctx_execute_file` para derivação de dados.
5. `WEB` → `ctx_fetch_and_index` e depois `ctx_search`.
6. `INDEX` → `ctx_index(path: ..., source: ...)` para conteúdo reutilizável.

**Concorrência padrão:**
- I/O de rede/API: `concurrency: 4-8` em `ctx_batch_execute`/`ctx_fetch_and_index`.
- CPU-bound (build/test/lint): `concurrency: 1`.
- `gh` CLI: máximo `4`.

**Terminal (`run_in_terminal`) apenas para:** `git` (`--no-pager` MANDATÓRIO em `diff`/`log`/`show`/`branch` — R-035), `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`.

**Continuidade de sessão e memória:**
- Em retomada, consultar memória antes de perguntar contexto ao usuário.
- Se `ctx_search` retornar 0 resultados, tratar como sessão nova.
- **Retomada de Sessão (Anti-Ancoragem R-042)**: A reidratação de sessões anteriores é estritamente **SOB DEMANDA** (acionada explicitamente via `/ctx-resume` ou intenção declarada do usuário como "retomar [tarefa]"). É **terminantemente proibida** a reidratação compulsória de contexto/memória no Turno 1, evitando viés de ancoragem em objetivos de sessões encerradas.

**Comandos `ctx` (atalhos operacionais):**
- `ctx stats` → chamar `ctx_stats` e exibir saída completa.
- `ctx doctor` → chamar `ctx_doctor`, executar comando retornado e reportar checklist.
- `ctx upgrade` → chamar `ctx_upgrade`, executar comando retornado e reportar checklist.
- `ctx purge` → chamar `ctx_purge(confirm: true)` com aviso explícito de operação destrutiva.

### Compact Error Reporting

Ao reportar falhas, use o formato 3 linhas:

```
- Causa: <descrição em ≤ 1 linha>
- Local: <arquivo:linha ou comando>
- Ação sugerida: <o que fazer; aguarda aprovação>
```

**Proibido sem pedido**: stack trace completo, output integral, diff > 20 linhas.
Se múltiplos erros: agrupe, liste no máximo 5; resto: `(+N erros similares)`.

---

## 3) 🧠 Model Routing Signal (R-021)

Avalie o tipo da tarefa e emita o sinal abaixo quando exigir modelo **1× ou superior**:

> 🧠 **Modelo recomendado: `<Claude Sonnet / GPT-5>`**
> **Motivo:** `<razão em 1 linha>`
> Troque o modelo e continue neste mesmo chat.

| Tipo de tarefa | Modelo | Custo |
|---|---|---|
| Exploração · contexto · Q&A · confirmação · MCP fetch | **Claude Haiku** | **0×** |
| Edições pequenas · respostas rápidas | Claude Haiku | 0.33× |
| Implementação padrão · refactor | Claude Sonnet / GPT-5 | 1× |
| Arquitetura complexa · debug crítico · decisão crítica | Claude Opus | 3× |

**Regra**: emita o sinal **antes** de codar. MCP tools (`ctx_search`, Tavily) amplificam qualquer modelo — use-os antes de escalar.

---

## 4) 🏥 Health Check — Binding Context (R-034)

**GATILHO AUTOMÁTICO**: Ao iniciar trabalho em novo repositório, Copilot DEVE verificar:

```
✓ Existe: .github/instructions/README.md  ← NESTE repositório de governança
✓ Existe: .github/instructions/README.md    ← NESTE repositório de governança
```

> ⛔ **GUARDRAIL DE CONFINAMENTO (R-034 + R-043)**:
> - `catalog.yaml` e `binding.md` existem APENAS neste repositório (compartilhados/commitados).
> - Adapters GENÉRICOS existem APENAS em `.github/instructions/<stack>.instructions.md` (raiz, compartilhados).
> - Adapters POR-PROJETO existem em `.github/instructions/local/<projeto>.instructions.md` — **gitignored, nunca commitados** (R-043).
> - Projetos são registrados exclusivamente em `.github/projects.local.yaml` (gitignored) — **nunca** em `catalog.yaml`.
> - Projetos externos (ex.: `custom-project-app`) são referenciados no overlay local,
>   mas **NUNCA recebem arquivos de governança** criados por estes agents.
> - O `adapter-generator` faz SCANNER dos projetos externos (read-only), mas cria
>   arquivos somente neste repositório, sempre em `local/` (gitignored).

**Se FALTAREM arquivos:**

1. ⚠️ **ALERTA ao usuário:**
   ```
   ⚠️ Binding context não detectado!

   Este repositório não possui:
   - .github/instructions/README.md
   - .github/instructions/README.md

   → Vou disparar o agent `binding-initializer` para criá-los NESTE repositório
   → Responda 1 pergunta (nome do ecossistema) e o esqueleto será criado aqui
   → Projetos são adicionados depois via /add-project-context (grava em projects.local.yaml, gitignored)
   ```

2. **DISPARAR AGENT** `binding-initializer` com `ask_questions`:
   - P1: Nome do ecossistema/organização (kebab-case) — única pergunta obrigatória

3. **GERAR AUTOMATICAMENTE — TODOS NESTE REPOSITÓRIO:**
   - `.github/instructions/README.md` — via `binding-initializer` ← NESTE repo
   - `.github/projects.local.yaml.example` — via `binding-initializer` ← NESTE repo (template tracked, sem dados reais)
   - `.github/projects.local.yaml` — via `binding-initializer` ← NESTE repo (overlay local privado, gitignored)
   - `.github/instructions/local/<projeto>.instructions.md` — via `adapter-generator` após `/add-project-context` (gitignored)
   - Préview antes de criar

**Sem exceções** — binding + adapters são pré-requisitos para descoberta de convenções (R-034).
Nenhum desses arquivos deve ser criado nos projetos externos.
Projetos e adapters por-projeto NUNCA são commitados no repositório compartilhado (R-043).

---


### Agents atuais

**⭐ PONTO DE ENTRADA OBRIGATÓRIO:**
- `agent-router` → **SEMPRE INVOCAR PRIMEIRO** (triagem + roteamento para downstream)

**Passo mandatório pós-router (R-041):**
- `prompt-structuring` → ⚠️ **SEMPRE acionado pelo `agent-router`** logo após o Health Check (R-034) e antes de qualquer classificação de intenção. Refina o prompt em loop controlado (máx. 5 iterações) e retorna sempre ao `agent-router`.

**Downstream (conforme rota do router):**
- `bug-triage` -> triagem de bugs e regressões.
- `code-review` -> revisão de código (diff/PR) antes do merge, por severidade (read-only).
- `requirements-analyst` -> elicitação e estruturação de requisitos funcionais e não-funcionais a partir de pedido de negócio ambíguo.
- `test-strategy` -> estratégia de testes, cobertura por risco e matriz de cenários de teste.
- `business-rules-extractor` -> extração de regras de negócio de código-fonte e documentação em `.md`; validação de refatorações contra regras documentadas.
- `refactor-planner` -> planejamento e decomposição macro de refatoração estrutural (delega execução aos especialistas de stack).
- `docs-engineer` -> autoria e curadoria de documentação técnica em `.md` — modos `author`/`curate` (fusão de docs-writer + docs-curator).
- `deep-search` -> triagem e roteamento de pesquisa interna e externa.
- `tech-solution-architect` -> arquiteto de solução técnica: viabilidade, Technical Blueprint, contratos de API (OpenAPI), modelo de dados e divisão de tarefas por stack ([BACKEND_TASKS], [FRONTEND_TASKS]).
- `angular-router` -> supervisor hierárquico e roteador do domínio Angular — orquestra os 8 especialistas em `.github/agents/frontend/angular/` (arch-advisor, feature-developer, bug-fixer, ui-stylist, unit-test, component-test, test-fixer, e2e-writer).
- `spring-boot-router` -> supervisor hierárquico e roteador do domínio Spring Boot — orquestra os 7 especialistas em `.github/agents/backend/spring-boot/` (arch-advisor, feature-developer, bug-fixer, perf-tuner, unit-test-writer, integration-test-writer, test-fixer).
- `spring-reactive-router` -> supervisor hierárquico e roteador do domínio Spring Reactive — orquestra os 7 especialistas em `.github/agents/backend/spring-reactive/` (arch-advisor, feature-developer, bug-fixer, resilience-tuner, unit-test-writer, integration-test-writer, test-fixer).
- `ejb-router` -> supervisor hierárquico e roteador do domínio Java legado EJB — orquestra os 7 especialistas em `.github/agents/backend/ejb/` (arch-advisor, feature-developer, bug-fixer, perf-tuner, unit-test-writer, integration-test-writer, test-fixer).
- `python-router` -> supervisor hierárquico e roteador do domínio Python backend — orquestra os 7 especialistas em `.github/agents/backend/python/` (arch-advisor, feature-developer, bug-fixer, perf-tuner, unit-test-writer, integration-test-writer, test-fixer).
- `struts-router` -> supervisor hierárquico e roteador do domínio Java legado Struts — orquestra os 7 especialistas em `.github/agents/backend/struts/` (arch-advisor, feature-developer, bug-fixer, perf-tuner, unit-test-writer, integration-test-writer, test-fixer).
- `database-router` -> supervisor hierárquico e roteador do domínio de Banco de Dados — orquestra os 6 especialistas em `.github/agents/backend/database/` (oracle-migration-dev, oracle-plsql-expert, oracle-query-tuner, informix-migration-dev, informix-spl-expert, informix-query-tuner).
- `governance-factory` -> criar/revisar agent, skill, prompt ou nova stack via parâmetro `type` (na criação, delega compulsoriamente pesquisa prévia de mercado/skills ao `deep-search`).
- `governance-maintainer` -> manutenção atômica, refatoração em cascata e sincronização em lote de artefatos de governança via context-mode e diffs cirúrgicos.
- `binding-initializer` -> ⚡ inicializar `catalog.yaml` + `binding.md` + `projects.local.yaml.example` para novo repositório (1 pergunta — R-034)
- `adapter-generator` -> ⚡ gerar automaticamente adapters por-projeto em `.github/instructions/local/` (gitignored, R-043) via `/add-project-context`
- `runtime-verifier` -> verificação de saúde do ambiente (build/dependências/serviços) antes de testes/codificadores; read-only.
- `pr-gatekeeper` -> preparação de PR pós-aprovação (diff, commit semântico, matriz de risco, changelog); nunca commit/push autônomo.
- `database-specialist` -> migrações de schema, otimização de query e integridade referencial.
- `ddd-bounded-context-mapper` -> mapeamento semântico de domínios de negócio por nomenclatura, Bounded Contexts e God Classes (read-only).
- `adr-sentinel` -> auditoria de propostas técnicas, blueprints e diffs contra Architectural Decision Records (ADRs) documentados (read-only).
- `repo-hygiene-auditor` -> auditoria de higiene estrutural, documentação essencial (README/CONTRIBUTING) e práticas de CI/CD (read-only).

### Skills atuais

**Contexto e Processo:**
- `context-mode` -> organização de contexto e pesquisa sobre conteúdo já indexado/lido.
- `context-compact` -> compactação pós-leitura e geração de resumos executáveis.
- `refactoring-planning-patterns` -> planejamento de refatoração estrutural (Mikado, Branch by Abstraction, Strangler Fig, safety net).
- `efficient-batch-code-modification` -> edição em lote, dry-run e diffs cirúrgicos para economia de tokens e créditos Copilot.
- `harness-engineering-patterns` -> diretrizes de harness engineering, diagnóstico harness vs modelo, heurística da zona inteligente (~100k tokens), poda de contexto e Ralph Loop.

**Pesquisa e Documentação:**
- `tavily` -> pesquisa externa e documentação atualizada.
- `mermaid-diagrams` -> criação de diagramas Mermaid legíveis em Markdown, ADRs e documentação técnica.

**Tooling e Qualidade:**
- `sonarqube-governance` -> monitoramento de métricas de qualidade via SonarQube.
- `yaml-governance` -> boas práticas para leitura, geração e validação de arquivos YAML/YML.
- `git-governance` -> convenções de git workflow, branch naming e commit standards.
- `git-worktree-governance` -> diretrizes de ciclo de vida e isolamento para execução de agentes paralelos via Git Worktrees.
- `performance-engineering-patterns` -> revisão especializada de performance (Core Web Vitals, N+1, latência, profiling).
- `angular-performance-patterns` -> engenharia de performance Angular (Zoneless, Signals, @defer, SSR incremental, CWV).
- `spring-boot-performance-patterns` -> engenharia de performance Spring Boot (Virtual Threads, pinning, HikariCP, N+1, cache, ZGC).
- `spring-reactive-performance-patterns` -> engenharia de performance reativa (event-loop, BlockHound, flatMap tuning, backpressure, Netty).
- `frontend-visual-feedback-loop` -> execução do Visual Feedback Loop agnóstico via Storybook/dev-server, snapshots multi-viewport (375/768/1440px), AOM e Playwright.

**Testes — Genéricos (agnósticos de stack):**
- `test-implementation-backend` -> padrões agnósticos de testes para qualquer backend.
- `test-implementation-frontend` -> padrões agnósticos de testes para qualquer frontend.
- `test-coverage-governance` -> governança de cobertura de testes e métricas por risco.

**Testes — Específicos por Stack:**
- `test-implementation-spring-boot` -> padrões de testes em Spring Boot com JUnit 5 e Mockito.
- `test-implementation-angular-jasmine` -> padrões de testes em Angular com Jasmine/Karma (legado).
- `test-implementation-angular-vitest` -> padrões de testes em Angular 20/21+ com Vitest (recomendado).
- `test-implementation-python` -> padrões de testes em Python com pytest.

**Scanner e Adapters:**
- `project-scanner` -> análise automática de repositórios e detecção de stack e arquitetura.
- `project-context-builder` -> scanner automático de projetos para geração de adapters via `/add-project-context`.

**Governança de Agents:**
- `agent-contracts` -> padronização de contratos operacionais de agents.
- `handoff-governance` -> padrões de delegação entre agents.
- `confidence-fallback-policy` -> política de confiança e fallback.
- `agent-safety-guardrails` -> guardrails de segurança para agents.
- `agent-observability-otel` -> rastreabilidade e telemetria de agents.
- `agent-evals-lab` -> avaliação contínua e regressão de agents.
- `agent-memory-policy` -> política de memória long-term (episódica, semântica, procedimental) para agents auto-adaptativos.

### Pre-fetch recomendado (antes de tarefas não triviais)
- `CLAUDE.md`
- `.github/instructions/README.md`
- `.github/copilot-instructions.md`
- `.github/agents/README.md`
- `.github/skills/README.md`
- `.github/instructions/README.md`

### Docs de convenções consolidadas

- Instructions específicas por projeto/stack: `.github/instructions/*.instructions.md`
- Índice de instructions (adapters): `.github/instructions/README.md`
- Novos arquivos de documentação `.md` devem seguir `kebab-case`, conforme diretriz do `CLAUDE.md`.

### 🔍 Descoberta Progressiva de Agents e Skills

- `@agent list` — lista todos os agents + capacidades
- `@agent search <tema>` — busca semântica por relevância
- `@skill list` — lista todas as skills por tier
- `@skill search "<termo>"` — busca semântica de skills

**Pre-fetch Automático:** ao selecionar um agent, o Copilot carrega automaticamente os `source_docs` declarados no `catalog.yaml`. Rejeite com "Sem pre-fetch" se desejar.

---

## 5) Binding de Adapters — Carregamento Hierárquico de Instruções

### Mecanismo de Binding (Consolidado no Mercado)

Este repositório adota o **padrão consolidado GitHub Copilot** de binding hierárquico:

```
Camada 1 (Global)      → CLAUDE.md + .github/copilot-instructions.md
                           ↓
Camada 2 (Stack/Adapter) → .github/instructions/*.instructions.md (com applyTo glob)
                           ↓
Camada 3 (Projeto)      → Local Overlay (projects.local.yaml + .github/instructions/local/, gitignored, R-043)
```

### Manifest de Binding

**Arquivo:** `.github/instructions/README.md` (single source of truth — adapters/global, **nunca projetos**)

- Define ordem de carregamento de adapters
- Mapeia `applyTo` glob patterns → instruções específicas
- Documenta escopo e audiência de cada adapter genérico
- Garante não-duplicação (R-003)

> Projetos: `.github/projects.local.yaml` (gitignored, R-043) — nunca em `catalog.yaml`.

### Adapters: Estrutura Genérica

Cada adapter na raiz de `.github/instructions/` deve:
- Ser **independente** de outros adapters
- Declarar seus `applyTo` glob patterns via YAML frontmatter
- **Nunca referenciar projetos específicos ou tecnologias exclusivas** (R-038)
- Estar registrado em `.github/instructions/README.md` como single source of truth
- **Nunca ser** um adapter por-projeto (esses vivem em `.github/instructions/local/`, gitignored — R-043)

**Para exemplos concretos de adapters registrados**, consulte `.github/instructions/README.md` (binding context).

- **GitHub Copilot** (VS Code, JetBrains): carrega `.github/copilot-instructions.md` (global) + adapters via YAML frontmatter `applyTo`
- **Cursor IDE**, **Claude Code**: suporta o mesmo mecanismo
- **Custom tooling**: use `.github/instructions/README.md` como manifesto de discovery

### Adicionar Novo Adapter (genérico/compartilhado)

1. Criar arquivo `.github/instructions/<nome>.instructions.md`
2. Adicionar frontmatter YAML com `applyTo`:
   ```yaml
   ---
   applyTo: ["src/**/*.ext"]
   ---
   ```
3. Atualizar `.github/instructions/README.md` com novo entry
4. Sincronizar `.github/instructions/README.md`

> Adapter **por-projeto** (gerado por `/add-project-context`) segue fluxo diferente — vai em
> `.github/instructions/local/<projeto>.instructions.md` (gitignored) e é registrado em
> `projects.local.yaml`, nunca aqui (R-043).

---

## 6) Formato de Saída Padrão

- **Resultado:** o que foi feito.
- **Evidências:** caminhos e artefatos alterados.
- **Próximo passo mínimo:** ação objetiva para avançar.

## 7) Índices de Governança

- **Mapa do Repositório (Repo Map):** `docs/repo-map.md` (fonte de verdade de navegação determinística de arquivos)
- **Catálogo de Agents:** `.github/agents/catalog.yaml` (único catalog.yaml do repositório — metadados e modelos)
- **Adapters/Binding:** `.github/instructions/README.md` (manifest de carregamento hierárquico — NUNCA buscar agents aqui)
- **Grafo de Roteamento (R-040):** `.github/agents/routing-graph.yaml` (fonte estrutural — nós, arestas, cascata)
- **Suíte de Evals:** `.github/agents/evals/casos-roteamento.yaml` (quality gate de regressão de roteamento)
- **Instructions:** `.github/instructions/README.md` + `.github/instructions/*.instructions.md`
- **Agents:** `.github/agents/README.md` + `.github/agents/catalog.yaml`
- **Skills:** `.github/skills/README.md` + `.github/skills/.index.json`
- **Prompts Workflow:** `/deep-search` `/plan` `/implement` `/validate` `/commit` `/review` `/connect-integration-graphs` `/visualize-graph`
- **Prompts Context Mode:** `/ctx-checkpoint` `/ctx-resume` `/ctx-doctor` `/ctx-status` `/ctx-insight`
- **Índice completo:** `.github/prompts/README.md`
- **Hooks:** `.github/hooks/README.md` + `.github/hooks/context-mode.json`

---
