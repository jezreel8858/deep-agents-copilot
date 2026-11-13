---
name: structured-intake-patterns
description: "Define diretrizes e padrões para padrão canônico de coleta estruturada de contexto via ask_questions (P1..PN) com critério objetivo de 'mínimo necessário para prosseguir' e template de consolidação — evita reimplementação do mesmo bloco de intake em cada agent. Use quando atuar em coleta de contexto, pré-checklist, protocolo de detecção de contexto. Não use para tarefas fora do escopo de structured-intake-patterns ou implementação direta de código de negócio não relacionado."
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
  - .github/agents/test-strategy.agent.md
  - .github/agents/requirements-analyst.agent.md
  - .github/agents/bug-triage.agent.md
  - .github/agents/business-rules-extractor.agent.md
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: ['ask_questions']
---

# Structured Intake Patterns

## Quando Usar

- Ativação em cenários de coleta de contexto, pré-checklist, protocolo de detecção de contexto.

## Quando NÃO Usar

- Não usar para demandas fora do domínio de `structured-intake-patterns` ou quando outra skill específica cobrir integralmente o escopo.

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

## 2.1) Protocolo de Grilling Cético ("Grill Me" / Matt Pocock)

Inspirado nas práticas de AI Hero / `mattpocock/skills`, o agente não assume uma postura passiva de mero executor de ordens ou aceitador cego de premissas. Ele deve **interrogar ativamente o desenvolvedor/arquiteto** sobre premissas implícitas, casos de borda e modos de falha antes de qualquer geração de código ou alteração estrutural.

#### Dinâmica de Interrogação
O agente formula indagações cirúrgicas via `ask_questions`:
- *"O que acontece se o serviço/dependência X falhar ou retornar timeout?"*
- *"Qual é o comportamento esperado sob concorrência e condições de corrida?"*
- *"Qual trade-off arquitetural foi considerado para esta abordagem (ex.: latência vs. consistência)?"*
- *"Por que não adotar a alternativa Y (solução mais simples ou padrão existente no repositório)?"*
- *"Quais invariantes de negócio não podem ser violados em hipótese alguma?"*

#### Regra de Ouro da Responsabilidade
- **Humanos mantêm 100% da responsabilidade** pelas decisões de produto, requisitos e arquitetura final.
- **O agente expõe as ramificações, premissas implícitas e decisões ocultas** antes da codificação, forçando clareza e prevenindo retrabalho catastrófico.

---

## 2.2) State Machine de Triagem Formal (Issue Labels)

Inspirada no modelo de governança de `mattpocock/skills/triage`, a triagem formal opera como uma máquina de estados determinística orientada a rótulos (*labels* de issue/ticket). Ela assegura que nenhuma tarefa seja executada sem especificação suficiente e que agentes autônomos só atuem quando todas as ambiguidades tiverem sido eliminadas.

### Estados Canônicos de Triagem
- `needs-triage`: Estado inicial obrigatório para qualquer nova issue ou solicitação inbound. Nenhuma intervenção de código é permitida.
- `needs-info`: A solicitação carece de reprodução, logs, escopo ou parâmetros essenciais. Aguarda esclarecimento do autor.
- `ready-for-agent`: A demanda possui especificações completas, critérios de aceite claros, zero ambiguidade arquitetural e pode ser executada por agente de IA com guardrails.
- `ready-for-human`: A demanda envolve julgamento de produto, design sensível, decisões estratégicas de arquitetura, alto risco regulatório ou aprovação orçamentária.
- `wontfix`: Solicitação rejeitada por estar fora de escopo, duplicada, tecnicamente inviável ou refutada durante o grilling.

### Tabela de Transições da State Machine

| Estado Atual | Evento / Condição | Próximo Estado | Ação Automática Executada |
|---|---|---|---|
| *(Nova issue)* | Criação do ticket sem análise prévia | `needs-triage` | Aplicar label `needs-triage`; acionar `@agent-router` ou triagem inicial. |
| `needs-triage` | Dados incompletos, sem passos de reprodução ou sem critérios | `needs-info` | Aplicar `needs-info`; emitir perguntas cirúrgicas via `ask_questions` / template de intake. |
| `needs-info` | Autor responde com todos os dados e critérios validados | `needs-triage` | Remover `needs-info`; reavaliar elegibilidade de execução. |
| `needs-info` | Inatividade prolongada sem resposta (> 14 dias) | `wontfix` | Fechar issue com mensagem explicativa de expiração de contexto. |
| `needs-triage` | Escopo delimitado, reproduzível, puramente técnico e sem risco estrutural | `ready-for-agent` | Aplicar `ready-for-agent`; despachar para o especialista correspondente no grafo. |
| `needs-triage` | Envolve trade-off crítico de negócio, arquitetura core ou UX subjetiva | `ready-for-human` | Aplicar `ready-for-human`; notificar mantenedores humanos no PR/issue. |
| `needs-triage` | Fora de escopo, duplicada ou refutada no grilling cético | `wontfix` | Aplicar `wontfix`; registrar justificativa técnica e fechar ticket. |

### Regras de Automação e Governança de Labels
1. **SSOT da Triagem**: Apenas um label de estado (`needs-*` ou `ready-*`) deve estar ativo por vez no artefato.
2. **Portão de Entrada do Agente**: Agentes executores (`refactor-planner`, `backend-developer`, `test-engineer`, etc.) DEVEM recusar execução imediata se a issue estiver com label `needs-triage` ou `needs-info`.
3. **Escalonamento Transparente**: Se durante a execução um agente detectar complexidade imprevista que rompe o contrato inicial, ele deve transicionar o estado de `ready-for-agent` para `ready-for-human` e suspender a automação.

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

- Matt Pocock / AI Hero: *triage skill* (https://github.com/mattpocock/skills)
- `CLAUDE.md` — R-027 (Clarificação Obrigatória).
- `.github/copilot-instructions.md` — R-027, formato de `ask_questions`.
- `.github/skills/context-mode/SKILL.md` — playbook de coleta ativa em lote antes de perguntar.

## Contrato de Qualidade e UX do `ask_questions` (CA-03, CA-04, CA-05 / R-027)

Toda invocação da ferramenta `ask_questions` em intake estruturado, desambiguação ou checkpoints HITL DEVE obedecer estritamente aos três contratos canônicos abaixo:

### 1. CA-03 — Padrão Obrigatório do Campo `description`
- Toda opção em `options` DEVE possuir o campo `description` preenchido em formato estruturado enxuto (1 a 2 frases):
  `[Consequência prática / O que faz] + [Trade-off principal ou quando escolher]`.
- **Proibido**: emitir `options` apenas com `label` (sem `description`) ou preencher um `description` redundante que apenas repete as palavras do `label`.

### 2. CA-04 — Regra da Opção Recomendada (`Default Effect`)
- Quando houver melhor prática técnica ou arquitetural clara, posicioná-la obrigatoriamente como a **1ª opção** da lista com o sufixo `(Recomendado)` no `label` e a justificativa técnica no `description`.
- **Exceção explícita**: Decisões puramente de negócio/produto sem alternativa técnica superior NÃO devem forçar `(Recomendado)` artificialmente.

### 3. CA-05 — Anti-Strawman & Limites Ergonômicos da Rodada
- **Anti-Strawman (Proibição de Opções Espantalho)**: Proibido criar alternativas artificiais, inviáveis ou absurdas apenas para compor lista. Cada pergunta com opções deve ter entre **2 e 4 alternativas reais, viáveis, mutuamente exclusivas e defensáveis**.
- **Ergonomia da Rodada**:
  - Limite de **1 a 4 perguntas por chamada** de `ask_questions` (carrossel enxuto).
  - `header` curto e identificável (**máx. 25 caracteres**).
  - `allowFreeformInput: true` habilitado como padrão (proibido criar opção artificial `"Outro (especificar)"` quando o campo livre nativo já está ativo).

### Exemplo Canônico: Bom vs. Ruim (JSON)

```json
{
  "_comment_ruim": "❌ RUIM: Sem description, sem (Recomendado) em decisão técnica, opção espantalho e opção dummy 'Outro'",
  "questions_bad": [
    {
      "header": "Estrategia de persistencia de dados do servico de pedidos",
      "question": "Qual banco usar?",
      "options": [
        { "label": "Salvar em arquivo TXT local sem lock" },
        { "label": "PostgreSQL" },
        { "label": "Outro (especificar)" }
      ]
    }
  ],
  "_comment_bom": "✅ BOM: CA-03 (description = Consequência + Trade-off), CA-04 (1ª opção Recomendado), CA-05 (2-4 opções reais, header <= 25 chars, allowFreeformInput: true)",
  "questions_good": [
    {
      "header": "Banco de Pedidos",
      "question": "Qual estratégia de persistência devemos adotar para o serviço transacional de pedidos?",
      "allowFreeformInput": true,
      "options": [
        {
          "label": "PostgreSQL com ACID (Recomendado)",
          "description": "Garante consistência transacional forte e integridade referencial nativa. Ideal para fluxos financeiros/pedidos, exigindo gestão de migrações relacionais."
        },
        {
          "label": "DynamoDB Single-Table",
          "description": "Oferece latência previsível em escala massiva com modelo serverless. Escolha apenas se os padrões de acesso forem fixos e não exigirem joins complexos."
        }
      ]
    }
  ]
}
```

## Checklist de Qualidade
- [ ] **CA-03 (`description` estruturado)**: `[Consequência prática / O que faz] + [Trade-off principal ou quando escolher]`.
- [ ] **CA-04 (`(Recomendado)` na 1ª opção)**: 1ª opção `(Recomendado)` para melhor prática técnica (exceção para decisão puramente de negócio).
- [ ] **CA-05 (Anti-Strawman e Ergonomia)**: 2–4 opções reais, 1–4 perguntas/chamada, `header` ≤ 25 chars e `allowFreeformInput: true`.
