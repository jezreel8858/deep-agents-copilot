---
name: structured-intake-patterns
description: >
  Padrão canônico de coleta estruturada de contexto via ask_questions (P1..PN)
  com critério objetivo de "mínimo necessário para prosseguir" e template de
  consolidação — evita reimplementação do mesmo bloco de intake em cada agent.
tier: 2
category: process
triggers:
  - "coleta de contexto"
  - "pré-checklist"
  - "protocolo de detecção de contexto"
  - "ask_questions estruturado"
  - "intake de bug"
  - "pré-contexto validado"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/bug-triage.agent.md
  - .github/agents/test-strategy.agent.md
  - .github/agents/business-rules-extractor.agent.md
  - .github/agents/requirements-analyst.agent.md
tools: ['ask_questions']
---

# Structured Intake Patterns

## 0) Problema Resolvido

Vários agents deste catálogo (`bug-triage`, `test-engineer`, `business-rules-extractor`, `requirements-analyst`) precisam coletar contexto mínimo **antes** de agir, sob a regra R-027 (Clarificação Obrigatória — proibido inferir/deduzir intenção). Sem um padrão único, cada agent reimplementa do zero: (a) quantas perguntas fazer, (b) quando parar de perguntar, (c) como consolidar as respostas antes de prosseguir. Esta skill consolida o padrão em 1 lugar.

## 1) Estrutura Canônica de Bloco de Intake

Todo bloco de intake segue o formato `P1..PN`, cada pergunta com opções pré-definidas **e** campo aberto (R-027):

```yaml
intake:
  - id: P1
    pergunta: "<pergunta objetiva e específica ao domínio>"
    opcoes:
      - label: "<opção A>"
        descricao: "<quando escolher>"
      - label: "<opção B>"
        descricao: "<quando escolher>"
    permite_texto_livre: true
  - id: P2
    pergunta: "<...>"
    # ...
```

**Regra de ouro (R-027):** toda pergunta usa `ask_questions` com opções descritivas **+ última opção sempre aberta** (freeform). Nunca inferir a resposta mais provável e prosseguir sem perguntar.

## 2) Critério Objetivo de "Mínimo Necessário para Prosseguir"

Nem toda pergunta é bloqueante. Classificar cada campo do intake em:

| Classe | Critério | Ação se ausente |
|---|---|---|
| **Obrigatório (bloqueante)** | Sem essa informação, a próxima etapa produz resultado não confiável ou arriscado (ex.: escopo de arquivos a alterar, stack alvo) | Bloquear e perguntar via `ask_questions` — não prosseguir |
| **Recomendado (soft)** | Informação melhora precisão mas há default seguro (ex.: ambiente de teste, versão exata) | Perguntar 1 vez; se não respondido, registrar como "não informado — assumido default X" e prosseguir |
| **Opcional** | Contexto de conveniência (ex.: link de issue, referência externa) | Não bloquear; usar se fornecido |

**Anti-padrão:** perguntar tudo como bloqueante (fadiga de intake) ou nada como bloqueante (viola R-027).

## 3) Template de Consolidação

Após a coleta, todo agent que usa este padrão deve produzir um bloco de consolidação antes de agir, nomeado por domínio (ex.: `## PRÉ-CONTEXTO VALIDADO`, `## PROTOCOLO DE DETECÇÃO CONCLUÍDO`, `## CONTEXTO DE COLETA`):

```markdown
## <NOME DO BLOCO POR DOMÍNIO>

| Campo | Classe | Valor coletado | Fonte |
|---|---|---|---|
| <campo 1> | Obrigatório | <resposta> | ask_questions / relatório / código |
| <campo 2> | Recomendado | <resposta ou "não informado — default: X"> | ... |
| <campo 3> | Opcional | <resposta ou "—"> | ... |

**Pronto para prosseguir:** SIM/NÃO (todos os obrigatórios preenchidos).
```

## 4) Tabela de Mapeamento "Respostas → Estratégia"

Todo agent que usa este padrão deve declarar como cada combinação de resposta muda o comportamento subsequente — evita que o intake vire "perguntar por perguntar":

```markdown
| Resposta coletada | Estratégia adotada |
|---|---|
| <valor A em P1> | <ação/ramo do agent> |
| <valor B em P1> + <valor X em P2> | <ação/ramo combinado> |
| Nenhuma resposta (timeout/skip) | <fallback documentado, nunca "prosseguir arbitrariamente"> |
```

## 5) Execução em Lote (Coleta Ativa)

Quando não há relatório/fonte externa disponível (ex.: `test-engineer` sem relatório de falhas, `bug-triage` sem ticket), a coleta deve ocorrer via **execução em lote e ativa** dos comandos/queries necessários para preencher o máximo de campos automaticamente **antes** de perguntar ao usuário — perguntar apenas o que não pôde ser derivado (reduz fadiga de intake, alinhado ao playbook de roteamento de `context-mode/SKILL.md`).

## 6) Checklist de Conformidade

- [ ] Todas as perguntas usam `ask_questions` com opções + campo aberto (R-027).
- [ ] Campos classificados em Obrigatório/Recomendado/Opcional com critério explícito.
- [ ] Bloco de consolidação nomeado por domínio, produzido antes de agir.
- [ ] Tabela "Respostas → Estratégia" declarada (nem que seja mínima).
- [ ] Coleta ativa (lote) tentada antes de perguntar, quando há fonte derivável.
- [ ] Nenhuma inferência de resposta sem perguntar (R-027 — bloqueante).

## 7) Anti-padrões

- ❌ Perguntar tudo de uma vez sem classificar obrigatório/recomendado (fadiga de intake).
- ❌ Inferir resposta mais provável sem perguntar, violando R-027.
- ❌ Bloco de consolidação ausente — agente age sem registrar o que foi coletado.
- ❌ Reimplementar do zero o padrão P1..PN em vez de referenciar esta skill.
- ❌ Ignorar coleta ativa (lote) quando a fonte já está disponível (ex.: repositório, logs).

## 8) Consumidores Mapeados

- `bug-triage` — substitui bloco próprio "Pré-Checklist de Triagem" (P1-P8) por referência + especialização de domínio (sintomas, ambiente, reprodutibilidade).
- `test-engineer` — substitui "Protocolo de Detecção de Contexto" (P1-P3) por referência + especialização (relatório de falhas vs. coleta ativa).
- `business-rules-extractor` — substitui "Protocolo de Coleta de Contexto" (P1-P4) por referência + especialização (modo Extract vs. Validate).
- `requirements-analyst` — referencia como base do próprio processo de `ask_questions` para elicitação de requisitos.

## 9) Referências

- `CLAUDE.md` — R-027 (Clarificação Obrigatória).
- `.github/copilot-instructions.md` — R-027, formato de `ask_questions`.
- `.github/skills/context-mode/SKILL.md` — playbook de coleta ativa em lote antes de perguntar.

