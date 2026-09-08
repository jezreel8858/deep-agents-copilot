---
name: agent-memory-policy
description: >
  Política de memória long-term para agents de IA: define os 3 tipos (episódica,
  semântica, procedimental) e orienta quando e como implementar cada um, com foco
  especial em memória procedimental (agents auto-adaptativos via atualização controlada
  de prompts), guardrails de segurança e aprovação humana obrigatória.
tier: 3
category: governance
triggers:
  - "memória de agent"
  - "agent memory"
  - "memória procedimental"
  - "procedural memory"
  - "agent aprende com feedback"
  - "agent se adapta"
  - "atualizar system prompt"
  - "memória entre sessões"
  - "long-term memory agent"
  - "agent memory policy"
  - "memória episódica"
  - "memória semântica"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/context-mode/SKILL.md
  - .github/skills/agent-safety-guardrails/SKILL.md
  - .github/skills/agent-observability-otel/SKILL.md
tools: []
---

# Agent Memory Policy

> Política de memória long-term para agents de IA. Define os 3 tipos de memória, quando usar cada um e como implementar memória procedimental (agents auto-adaptativos) com segurança.

> ⚠️ **Tier 3 — Experimental**: use somente com validação explícita de caso de uso. Memória procedimental (agents atualizando seus próprios prompts) é uma capacidade avançada com risco de drift comportamental. Não aplique sem critério de rollback definido e baseline de evals.

---

## 1) Os 3 Tipos de Memória Long-Term

| Tipo | O que armazena | Exemplo | Frequência de mudança |
|---|---|---|---|
| **Episódica** | Interações passadas — o que aconteceu | "Na sessão anterior, o usuário aprovou a abordagem X" | Alta — acumula por sessão |
| **Semântica** | Fatos e preferências estáveis do projeto | "Este projeto usa Spring Boot 3.x + Jakarta EE" | Baixa — estável, atualizar quando projeto mudar |
| **Procedimental** | Como o agent deve se comportar | "Sempre perguntar o módulo antes de implementar testes" | Muito baixa — só com feedback explícito e aprovação |

**Relação com `context-mode` (skill Tier 1):**

| Tipo de memória | Implementação atual | Camada `ctx_*` |
|---|---|---|
| Episódica | `ctx_search(sort: "timeline")` — memória de sessão | Short-term (nativa) |
| Semântica | `ctx_index(path, source: "<projeto>")` — persistente | Long-term (com `source` declarado) |
| Procedimental | ❌ Não existe — requer política formal | Esta skill |

---

## 2) Memória Episódica — Boas Práticas

Armazena histórico de interações para continuidade entre sessões:

```yaml
episodica:
  source: "episodica-<nome-projeto>"
  ttl: "30d"          # expirar após 30 dias sem acesso
  escopo: "projeto"   # não compartilhar entre projetos distintos
  o_que_indexar:
    - decisoes_aprovadas_pelo_usuario
    - abordagens_rejeitadas_com_motivo
    - preferencias_de_formato_confirmadas
  o_que_nao_indexar:
    - conteudo_bruto_de_sessao_sem_filtro  # polui memória com ruído
    - dados_sensiveis_ou_credenciais       # R-010
```

### Tabela de Retenção e Pruning (TTL)

| Namespace / Source | TTL | Estratégia de Pruning | Finalidade |
|---|---|---|---|
| `episodica-<projeto>` | 30 dias | Expirar entradas sem acesso recente | Decisões arquiteturais e preferências confirmadas |
| `handoff-telemetry:*` | 7 dias | Pruning automático após 7 dias | Telemetria de transição, detecção de deriva e loops |
| `session-cache:*` | 24 horas | Invalidação ao término da sessão | Contexto efêmero e dados intermediários de tool |

---

## 3) Memória Semântica — Boas Práticas

Armazena fatos estáveis do projeto, stack e domínio:

```yaml
semantica:
  source: "<nome-projeto>"
  ttl: null           # sem expiração — atualizar manualmente ao mudar o projeto
  escopo: "projeto"
  o_que_indexar:
    - stack_tecnica_e_versoes
    - regras_de_negocio_documentadas
    - convencoes_de_codigo_do_projeto
    - decisoes_arquiteturais_registradas
```

**Atalho**: declarar `source_docs` nos agents do catálogo é a forma mais simples de memória semântica — já é o padrão do ecossistema.

### 3.1) Pipeline de Consolidação Semântica por Marco (/ctx-checkpoint)

Para evitar que decisões de design críticas sejam descartadas pelo TTL de 7 dias da telemetria episódica, o sistema adota um pipeline de consolidação disparado por marcos explícitos (ex.: via prompt `/ctx-checkpoint`, ao concluir planos com `@refactor-planner`, ou fechamento de Technical Blueprint com `@tech-solution-architect`):

1. **Gatilho de Marco**: O agent `@agentic-memory-manager` é acionado para revisar a telemetria recente (`source: "handoff-telemetry:<projeto>"`).
2. **Filtro Anti-Poisoning**: Apenas registros marcados com tags de decisão aprovada (`[DECISION]`, `[SUCCESS]`) ou itens com validação explícita do usuário são candidatos a consolidação. Tentativas falhas (`[LOOP_LIMIT]`), desvios (`[INTENT_DRIFT]`) e código intermediário são descartados.
3. **Deduplicação & Destilação**: Os fragmentos aprovados são resumidos em *átomos semânticos permanentes* (invariantes de arquitetura, contratos de integração e regras de domínio confirmadas).
4. **Persistência Permanente**:
   ```yaml
   ctx_index:
     source: "semantic:<projeto>"
     ttl: null  # Permanente — sobrevive a múltiplos ciclos de TTL episódico
     content: |
       [DECISAO_CANONICA] <titulo-da-decisao>
       - Contexto: <contexto-conciso>
       - Decisao: <o-que-foi-adotado>
       - Rationale: <por-que-foi-escolhido>
       - AprovadoEm: <ISO-8601>
   ```

---

## 4) Memória Procedimental — Como Implementar com Segurança

Capacidade mais avançada: o agent atualiza instruções comportamentais com base em feedback acumulado.

**Pré-requisitos obrigatórios antes de ativar:**

- [ ] **Rollback definido**: como reverter para versão anterior se o comportamento regredir? (Git tag ou arquivo `SKILL.md.bak`)
- [ ] **Escopo delimitado**: quais seções do prompt o agent pode modificar? (ex.: apenas `<examples>` e `triggers:`, nunca o bloco `CRÍTICO` ou `Regras Herdadas`)
- [ ] **Aprovação humana obrigatória** (R-027): toda atualização procedimental requer confirmação explícita via `ask_questions` — nunca automática
- [ ] **Baseline de evals**: ao menos 1 caso no `.github/agents/evals/casos-roteamento.yaml` cobrindo o comportamento atual como ground truth pré-atualização

**Ciclo de atualização procedimental:**

```
Feedback explícito do usuário (nunca inferido)
         ↓
Agent identifica padrão de melhoria comportamental
         ↓
Propõe atualização via ask_questions com diff claro
         ↓
Usuário aprova (R-027 — obrigatório)
         ↓
Atualização aplicada + commit Git separado e rastreável
         ↓
Novo caso de eval adicionado como baseline pós-mudança
         ↓
Monitoramento via agent-observability-otel (span: invoke_agent)
```

**O que pode ser atualizado (permitido com aprovação):**

| Seção | Tipo de mudança permitida |
|---|---|
| `<examples>` no system prompt | Adicionar exemplos de I/O bem-sucedidos |
| `triggers:` no frontmatter | Adicionar palavras-chave de reconhecimento |
| Seção "Quando Usar" de skills | Expandir cenários documentados |
| `source_docs:` de um agent | Adicionar novo documento de referência |

**O que NUNCA pode ser atualizado automaticamente (proibido):**

| Seção | Razão |
|---|---|
| Regras normativas R-001..R-040 em `CLAUDE.md` | Governança global — requer decisão explícita |
| Bloco `CRÍTICO` de qualquer `.agent.md` | Define escopo do agent — mudança é breaking change |
| Seção `Regras Herdadas` de agents | Garante rastreabilidade para `CLAUDE.md` |
| Qualquer regra de segurança ou autonomia | Previne violação de R-010 e `agent-safety-guardrails` |

---

## 5) Guardrails de Segurança

| Guardrail | Regra associada |
|---|---|
| Toda atualização procedimental requer `ask_questions` | R-027 — proibido inferir intenção |
| Atualização versionada como commit Git separado e descritivo | R-004 (rastreabilidade) |
| Nunca modificar regras de autonomia ou segurança automaticamente | R-010 + `agent-safety-guardrails` |
| Limite de 1 nível de auto-modificação por ciclo | Previne cascata de auto-atualizações não auditáveis |
| Adicionar caso de eval após cada atualização procedimental | R-015 aplicado à memória |
| Monitorar drift comportamental via OTel (span `invoke_agent`) | `agent-observability-otel` |

---

## 6) Quando NÃO Usar Memória Procedimental

- Agent já segue consistentemente o comportamento esperado → não há sinal de melhoria necessária
- A mudança desejada é uma **regra global** → editar `CLAUDE.md` diretamente com aprovação
- O caso de uso é **preferência de formatação** (não comportamento) → usar `<examples>` no prompt
- Não há baseline de evals que capture o comportamento atual → criar baseline primeiro
- A mudança pode ser feita editando `source_docs:` ou um adapter → usar essa alternativa mais simples

---

## Checklist

- [ ] Tipo de memória identificado: episódica | semântica | procedimental
- [ ] Para procedimental: 4 pré-requisitos atendidos (rollback, escopo, aprovação, baseline de evals)
- [ ] Atualização proposta via `ask_questions` com diff explícito antes de aplicar
- [ ] Versão anterior preservada via Git (commit de backup antes da mudança)
- [ ] Caso de eval adicionado em `.github/agents/evals/casos-roteamento.yaml`
- [ ] Monitoramento ativo em `agent-observability-otel` para detectar drift de comportamento

---

## Referências

- LangMem SDK — memória episódica, semântica e procedimental: https://www.langchain.com/blog/langmem-sdk-launch
- Mem0 — API de memória vendor-neutral (alternativa sem lock-in): https://mem0.ai/
- Best AI Agent Memory Frameworks 2026: https://atlan.com/know/best-ai-agent-memory-frameworks-2026
- `context-mode/SKILL.md` seção 10 — short-term vs long-term: `.github/skills/context-mode/SKILL.md`
- `agent-observability-otel/SKILL.md` — rastreamento de drift comportamental: `.github/skills/agent-observability-otel/SKILL.md`
- `agent-safety-guardrails/SKILL.md` — guardrails de segurança: `.github/skills/agent-safety-guardrails/SKILL.md`
- `.github/agents/evals/casos-roteamento.yaml` — baseline de casos de teste: fonte de verdade para regressão
