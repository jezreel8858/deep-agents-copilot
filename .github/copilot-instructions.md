# Instruções de IA — Base de Governança Reutilizável

## 1) Diretriz de Governança
Este repositório provê a infraestrutura de governança corporativa de IA. As regras normativas canônicas universais residem em [`CLAUDE.md`](../CLAUDE.md) (single source of truth). Este arquivo estabelece as diretrizes operacionais de runtime para o GitHub Copilot.

### 📋 Separação Clara: Governança Global vs. Adapters
- **Governança Global (`.github/agents/`, `.github/skills/`, `.github/prompts/`)**: Genérica, reutilizável e desacoplada de projetos e tecnologias exclusivas (R-038).
- **Adapters e Instruções Específicas (`.github/instructions/`)**: Convenções de ecossistema (`*.instructions.md`) e bindings de projeto em `local/` (gitignored, R-043).

## 1.1) 🚀 **AGENT ROUTER FIRST — Ponto de Entrada Obrigatório** (R-037)

**SEM EXCEÇÃO:** Toda solicitação deve começar com `@agent-router`.

```text
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
    ├─ Fast-Path Determinístico (Bug / Refatoração / Feature / Análise / Governança)
    │   └─ Ingressa IMEDIATAMENTE no respectivo Workflow Canônico (R-050)
    └─ Caso Ambíguo / Feature Aberta / Pedido não estruturado
        └─ @prompt-structuring (R-041 — loop máx. 5 iterações) → retorno obrigatório a @agent-router
    ↓
[Execução Sequencial no Workflow Canônico (R-050)]
    (Planos em docs/plans/ e docs/implementation-plans/ com aprovação humana R-064)
    ↓
Turno seguinte muda de fase/escopo? (R-042)
    ├─ Sim -> agent ativo retorna a @agent-router (handoff de deriva)
    └─ Não -> agent ativo continua respondendo no workflow ("Agente Ativo: <name>")
```

## 1.2) 📋 **Matriz de Decisão — Quando Pedir Contexto (R-006)**
Vide [`.github/agents/agent-router.agent.md`](agents/agent-router.agent.md) § *R-006 (Pré-condições — Matriz de Decisão: Quando Pedir Contexto)*. A pré-condição de contexto é responsabilidade do roteador, priorizando o avanço downstream sempre que o agente tiver condições operacionais de agir.

## 2) 🛑 Regras de Autonomia (não negociáveis)

### ✅ Sempre
- **Agent Router First (R-037)**: Toda solicitação começa com `@agent-router`. O Orquestrador despacha o downstream uma única vez em nível plano (Flat Delegation).
- **Re-triagem Obrigatória por Turno (R-042 — Anti Sticky-Session)**: Reavaliar intenção a cada turno; detectada deriva ou nova demanda pós-conclusão de workflow anterior (R-052 / conclusao_de_workflow_anterior), retornar imediatamente a `@agent-router` (*Anti Sticky-Agent*).
- **Zero Execução Direta pelo Orquestrador Raiz sem Router (R-063 — Anti Silent Bypass)**: É terminantemente proibido ao modelo do turno raiz executar diretamente tarefas técnicas sem passar por `@agent-router`; o Orquestrador Raiz deve sempre invocar o router para triagem.
- **Zero Impersonation pelo Orquestrador Raiz (R-062 — Anti Root-Agent-Impersonation)**: O modelo do turno raiz nunca deve se autodenominar ou assinar como qualquer especialista antes de delegar via `run_subagent`.
- **Precedência Mandatória e 100% Obrigatória de Context Mode (R-008, R-056)**: O uso de `context-mode` MCP (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_search`, `ctx_index`) é 100% OBRIGATÓRIO para leitura, modificação e criação de arquivos; ferramentas nativas de editor são estritamente proibidas quando o context-mode estiver disponível (rebaixadas a fallback exclusivo de indisponibilidade).
- **Single-Turn MCP Batching e Protocolo Plan-Then-Batch (R-046, R-059 — Smell 2.26)**: Ao atingir o Limiar >= 2 alvos ou comandos, aplicar compulsoriamente o Protocolo Plan-Then-Batch (etapas: ENUMERAR arquivos/comandos, CONSOLIDAR em `ctx_batch_execute` ou script iterativo `ctx_execute`, DESPACHAR & VALIDAR com `get_errors` ao final). Comandos curtos do usuário ("prosseguir", "continue") mantêm o rigor do protocolo.
- **Teto Rígido de Tool Turns (≤ 5) e Warm Start Compulsório (R-060)**: Orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução; inicialização silenciosa de bases pré-computadas (Warm Start) no primeiro comando e consolidação de buscas em lote com Edge Truncation.
- **Portão de Reúso Sistêmico (R-055 / Anti-Silo Fix / Systemic Reuse Gate)**: Responder a Q1 (peers), Q2 (templates) e Q3 (testes no pytest) antes de finalizar melhorias de governança.
- **Blueprint Técnico e Decomposição Obrigatórios (R-058 / Anti-Premature Implementation Bypass)**: Elaboração mandatória de Blueprint Técnico antes de codificar features complexas.
- **Progressive Disclosure Compulsória de `source_docs:` (R-066)**: Documentos de governança volumosos (> 300 linhas) devem constar sob `source_docs_lazy:`, proibida a leitura integral via `read_file`.
- **Protocolo de Avaliação de Pertinência de Importação de Skills (R-067)**: Avaliar pertinência de skills externas antes de importação de skill no catálogo.

### ⚠️ Pergunte primeiro
- Alterações destrutivas ou irreversíveis no repositório.
- Decisões arquiteturais com impacto transversal não acordadas previamente.

### 🚫 Nunca
- **Proibição Estrita de Terceirização de Edição Manual ao Usuário (R-057 — Anti-Manual User Delegation)**: Agentes analíticos ou read-only nunca devem delegar edição manual de código ou governança ao usuário quando houver agentes executores aptos no catálogo.
- **Blindagem contra Discovery de Modelos (R-054)**: Zero Discovery é absoluto e inegociável; nunca vasculhe `catalog.yaml` ou `*.agent.md` em tempo de execução para descobrir modelos de terceiros.
- **Ferramentas Nativas de Editor com Context-Mode Ativo (R-008 / R-056)**: Ferramentas de editor (`read_file`, `create_file`, `replace_string_in_file`, `insert_edit_into_file`) são estritamente proibidas quando context-mode disponível (fallback exclusivo).

### 2.1) context-mode — Regras Obrigatórias de Roteamento (JetBrains Copilot / VS Code)

| Operação | Ferramenta Canônica | Quando Usar |
|---|---|---|
| Leitura / Inspeção em lote | `ctx_execute` / `ctx_execute_file` | Leitura filtrada, scripts de inspeção no sandbox |
| Modificação multi-arquivo | `ctx_execute` (script iterativo) | Gravação em lote com verificação atômica |
| Multi-comandos CLI em lote | `ctx_batch_execute` | Execução paralela de múltiplos comandos shell |
| Busca em base indexada | `ctx_search` | Consultas estruturadas na base de conhecimento |
| Indexação documental | `ctx_index` | Armazenamento de documentações e referências |

**Compact Error Reporting (R-020)**: Ao reportar erros, use o formato de 3 linhas:
`Causa: <causa raiz>` | `Local: <arquivo:linha>` | `Ação: <procedimento corretivo>`

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
| Arquitetura complexa · debug crítico · decisão crítica | Claude Opus 5.5 | 3× |
| Tarefa multi-arquivo/alto fan-out (≥ 10 alvos/arquivos/operações homogêneas) (R-021.1) | Claude Sonnet / GPT-5 / Gemini Pro | 1× |

- **Nota (R-021.1 — Fan-Out)**: Tarefas com ≥ 10 alvos/arquivos/operações homogêneas devem acionar escalonamento pontual para Claude Sonnet/GPT-5 para execução em lote confiável via `ctx_batch_execute`.
- **Nota (R-021.2 — Retry-Rate Escalation)**: Agents executores que implementam feature e rodam testes devem emitir o sinal de Retry-Rate Escalation quando o mesmo teste falhar 2 vezes consecutivas.

## 4) 🏥 Health Check — Binding Context (R-034)

Ao iniciar trabalho em novo repositório, o Copilot deve validar:
- `✓ Existe: `[.github/instructions/README.md](instructions/README.md) (single source of truth de adapters)
- `✓ Confinamento (R-034/R-043)`: Adapters genéricos residem na raiz de `.github/instructions/`; adapters e configurações de projeto residem exclusivamente em `local/` (`.github/instructions/local/` e `projects.local.yaml`), sendo expressamente gitignored.
- **Descoberta Progressiva de Catálogo (R-066)**: Para evitar context bloat, consulte agents e skills sob demanda via [`.github/agents/catalog.yaml`](agents/catalog.yaml) e [`.github/skills/.index.json`](skills/.index.json) ou pelos comandos de inspeção (`@agent list`, `@skill list`), sem carregar listagens manuais estáticas.

## 5) Binding de Adapters — Carregamento Hierárquico de Instruções
1. **Camada 1 (Global)**: `CLAUDE.md` + `.github/copilot-instructions.md` (regras e invariantes corporativos).
2. **Camada 2 (Stack/Adapter)**: `.github/instructions/*.instructions.md` (convenções com frontmatter `applyTo:`).
3. **Camada 3 (Projeto Local)**: `.github/instructions/local/*.instructions.md` e `projects.local.yaml` (gitignored, R-043).

## 6) Formato de Saída Padrão (R-028)
Toda resposta técnica deve iniciar com o banner de agente ativo e estruturar-se no resumo em 5 seções:
`Agente Ativo: <nome-do-agent>`
1. **Abordagem**: Estratégia de resolução e padrão aplicado.
2. **Artefatos Modificados**: Arquivos alterados/criados com caminhos exatos.
3. **Economia de Turnos**: Operações em lote consolidadas no sandbox.
4. **Riscos / Alinhamento**: Quality gates e invariantes preservados.
5. **Próximo Passo**: Conclusão ou recomendação imediata.
