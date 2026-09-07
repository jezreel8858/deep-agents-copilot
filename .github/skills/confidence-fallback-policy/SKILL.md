---
name: confidence-fallback-policy
description: >
  Política de confiança e fallback para decisões de roteamento e execução de agents.
  Define escala de score (0-1), thresholds de ação, estratégias de escalonamento e
  exemplos concretos de aplicação por agent.
tier: 1
category: governance
triggers:
  - "confiança"
  - "confianca"
  - "fallback"
  - "incerteza"
  - "baixa confiança"
  - "score de roteamento"
  - "escalonamento"
  - "ambiguidade"
  - "re-roteamento"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/README.md
tools: []
---

# Confidence & Fallback Policy

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description` em 3ª pessoa, `tier: 1`, `category: governance` e triggers.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` definindo fórmula de pontuação de confiança, faixas de threshold e protocolo de fallback.
> - **Nível 3 (Recursos Suplementares)**: Casos de teste de roteamento em `evals/casos-roteamento.yaml`.

Esta skill resolve o problema de **alucinação e deduções precipitadas ("solution-jumping")** por agentes de IA frente a pedidos ambíguos ou incompletos, estabelecendo uma métrica determinística de confiança (0.0 a 1.0) e protocolo compulsório de clarificação progressiva via `ask_questions` (R-027).

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- No `@agent-router` para calcular score de confiança da rota antes de delegar.
- Em qualquer agent downstream ao receber uma solicitação com escopo vago ou requisitos incompletos.
- Para definir o threshold mínimo de parada e disparo de perguntas objetivas (`ask_questions`).

### ❌ Quando NÃO Usar
- Em tarefas com intenção e escopo perfeitamente claros (score ≥ 0.90) — não criar atrito desnecessário.
- Para adiar indefinidamente a execução por excesso de cautela (máximo 3 perguntas, R-012).
- No agent `prompt-structuring`, que já possui seu próprio protocolo de loop controlado (R-041).

---

## 2) Escala de Confiança (0.0 – 1.0)

| Score | Nível | Ação do Agent |
|---|---|---|
| **0.90 – 1.00** | 🟢 Alta | Prosseguir diretamente — intenção clara |
| **0.70 – 0.89** | 🟡 Moderada | Prosseguir com aviso inline do que foi assumido |
| **0.50 – 0.69** | 🟠 Baixa | `ask_questions` com 2-3 opções antes de agir |
| **0.00 – 0.49** | 🔴 Crítica | Parar + `ask_questions` + não agir até confirmação |

**Regra de ouro**: em dúvida, `ask_questions`. Inferir silenciosamente é proibido (R-027).

---

## 2) Como Calcular o Score

```
Score = (sinal_de_intenção × 0.4) + (contexto_suficiente × 0.4) + (ausência_de_ambiguidade × 0.2)

Sinal de intenção:
  0.0 → nenhuma ação identificável ("melhore o código")
  0.5 → ação identificável mas scope vago ("refatore")
  1.0 → ação + escopo + contexto claros ("implemente testes unitários para UserService")

Contexto suficiente:
  0.0 → zero contexto técnico fornecido
  0.5 → stack ou projeto identificado
  1.0 → stack + arquivo + regra de negócio presentes

Ausência de ambiguidade:
  0.0 → múltiplas interpretações conflitantes
  0.5 → uma interpretação dominante, mas incerta
  1.0 → sem ambiguidade interpretável
```

---

## 3) Estratégias de Fallback por Cenário

### 3.1) Input ambíguo — múltiplas intenções

```
Cenário: "Teste e documente o serviço de pagamentos"
Score: 0.55 (duas intenções)

Fallback:
  → ask_questions:
    "Qual é a prioridade?"
    A) Testes primeiro → @test-strategy → @test-engineer
    B) Documentação primeiro → @docs-engineer
    C) Ambos em sequência → plano dividido em fases
```

### 3.2) Contexto insuficiente

```
Cenário: "Corrige o bug"
Score: 0.30 (sem reprodução, sem arquivo, sem stack)

Fallback obrigatório:
  → ask_questions:
    P1: Qual é o comportamento atual vs. esperado?
    P2: Em qual arquivo/endpoint ocorre?
    P3: Qual ambiente/stack?
```

### 3.3) Escopo irrecuperável

```
Cenário: Solicitação contradiz R-031 (commit autônomo solicitado explicitamente)
Score: irrelevante

Fallback absoluto:
  → Reportar conflito com normativa
  → Não prosseguir
  → Aguardar revisão do usuário
```

### 3.4) Tool com falha repetida

```
Cenário: ctx_search retorna 0 resultados por 2+ tentativas
Score: 0.60 → rebaixa para 0.40 após N tentativas

Fallback:
  → Tentar ferramenta alternativa (grep_search como fallback de ctx_search)
  → Se ainda falhar → reportar estado e aguardar orientação
```

### 3.5) Stack ou Linguagem não Suportada no Catálogo (Out-of-Domain / Fallback Determinístico)

```
Cenário: Solicitação de codificação em linguagem/framework ausente do catálogo (ex.: "Crie uma API REST em Rust com Axum")
Score de Execução: 0.10 (tecnologia fora das competências cadastradas no catálogo e adapters)

Anti-Padrão Proibido:
  - ❌ Criar ou invocar agente inline exclusivo para "gap detection" em runtime (adiciona round-trip de LLM, custo e latência desnecessários no caminho crítico).
  - ❌ Delegar implementação para especialista de stack distinta (ex.: mandar Rust para @spring-boot-engineer ou Flutter para @angular-engineer).
  - ❌ Tentar implementar código fora do padrão de governança estabelecido sem adapter de suporte.

Comportamento Obrigatório (Fallback Determinístico do Router):
  1. Recusa imediata e estruturada declarando ausência de especialista para a stack no catálogo.
  2. Oferecer caminhos válidos:
     - Dúvida conceitual ou documentação externa → delegar para @deep-search.
     - Suporte definitivo no repositório → orientar expansão de governança via @governance-factory (para criar novo agent/adapter) ou /add-project-context.
```

---

## 4) Re-roteamento

Quando o agent downstream identifica que a tarefa pertence a outro agent:

```yaml
# Contrato de re-roteamento
roteamento_de_volta:
  quando: agent identifica tarefa fora do seu não-escopo
  acao: reportar ao usuário com sugestão de agent correto
  formato: |
    ⚠️ Esta tarefa está fora do escopo de [agent-atual].
    → Sugestão: invocar @[agent-correto]
    Motivo: [1 linha explicando por quê]
  proibido: executar tarefa fora do escopo silenciosamente
```

---

## 5) Anti-padrões

- ❌ Inferir intenção silenciosamente quando score < 0.70
- ❌ Prosseguir com score crítico sem `ask_questions`
- ❌ Re-rotear sem explicar o motivo ao usuário
- ❌ Usar fallback de tool sem registrar que ocorreu
- ❌ Escalar para modelo mais caro sem tentar ferramentas MCP primeiro
- ❌ Bloquear execução por ambiguidade que o downstream pode resolver iterativamente
- ❌ Criar ou invocar agent LLM inline exclusivo para "gap detection" (anti-padrão de latência e custo; tratar via recusa determinística no router e governança sob demanda)
- ❌ Delegar codificação para especialista de outra stack quando a linguagem solicitada não constar no catálogo (ex.: mandar Rust para @spring-boot-engineer ou Flutter para @angular-engineer)

## 6) Routing em Cascata (Rule → Semantic → LLM-Based)

Para ecossistemas com muitos agents especializados, aplicar routing em cascata com threshold progressivo:

| Nível | Estratégia | Trigger | Custo | Latência |
|---|---|---|---|---|
| **1 — Rule-based** | Keywords + sinais R-006 | Score ≥ 0.90 | Mínimo | < 10ms |
| **2 — Semantic** | Similaridade por embedding | 0.70 ≤ score < 0.90 | Baixo | ~50-200ms |
| **3 — LLM-based** | LLM-as-judge (tiebreaker) | 0.50 ≤ score < 0.70 | Moderado | ~1-3s |
| **Escalonamento humano** | `ask_questions` | score < 0.50 | — | — |

**Ambiguity Zone**: quando top-1 e top-2 candidatos têm scores dentro de 0.05 entre si → aplicar nível 3 (LLM tiebreaker) independentemente do threshold absoluto.

**Logging obrigatório por request** para calibração contínua:

```yaml
routing_log:
  request_id: "<uuid>"
  timestamp: "<ISO-8601>"
  nivel_usado: "rule-based | semantic | llm-based | escalonamento"
  top_3_candidatos:
    - agent: "<nome>"
      score: 0.95
    - agent: "<nome>"
      score: 0.88
    - agent: "<nome>"
      score: 0.72
  rota_final: "<agent-escolhido>"
  confianca_final: "<alta|média|baixa>"
  score_numerico: 0.95
```

**Calibração de threshold**: deve ser orientada por `observed false-positive rates` dos logs reais — não por intuição. Revisar thresholds a cada 100 requests ou quando taxa de `ask_questions` ultrapassar 15%.

**Regra de output** (obrigatória para o `agent-router`): declarar `Confidence Score: X.XX` e nível de routing usado em toda saída de roteamento — não apenas o qualitativo `alta|média|baixa`.

---

## 6) Checklist de Conformidade

- [ ] Score de confiança calculado formalmente: (sinal × 0.4) + (contexto × 0.4) + (clareza × 0.2).
- [ ] Score declarado explicitamente no cabeçalho ou metadados da resposta do router.
- [ ] Fallback para `ask_questions` acionado compulsoriamente se score < 0.70.
- [ ] Proibição absoluta de inferir intenção do usuário no escuro (R-027).

