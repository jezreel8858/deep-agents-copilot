---
name: harness-engineering-patterns
description: >-
  Fornece diretrizes e heurísticas canônicas de Harness Engineering — o subconjunto de
  Context Engineering que trata do "arnês" ao redor do modelo (tools, system prompt,
  gestão de janela de contexto, permissões, hooks). Use quando precisar diagnosticar
  comportamento anômalo de agent (harness vs. modelo), podar instrução/contexto
  acumulado ("bloat"), aplicar o limiar prático de ~100k tokens de "zona inteligente"
  ou auditar minimalismo/progressive disclosure de arquivos AGENTS.md/CLAUDE.md/
  instructions. Não use para avaliação de qualidade de resposta do modelo em si
  (isso é `agent-evals-lab`) nem para estruturação do prompt de tarefa (isso é
  `prompt-engineering-patterns`).
tier: 1
category: process
triggers:
  - "harness engineering"
  - "diagnostico de harness"
  - "harness vs modelo"
  - "context bloat"
  - "podar contexto"
  - "delete e observe"
  - "zona inteligente de tokens"
  - "agents.md minimalista"
  - "progressive disclosure agents.md"
  - "reset de sessao"
  - "ralph loop"
  - "loop autonomo de agente"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/context-mode/SKILL.md
  - .github/skills/agent-evals-lab/SKILL.md
  - .github/skills/prompt-engineering-patterns/SKILL.md
tools: []
---

# Harness Engineering Patterns

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: frontmatter para descoberta e roteamento rápido.
> - **Nível 2 (Corpo Operacional)**: este arquivo com regras essenciais, heurísticas e checklist.

**Definição operacional**: *Harness* é tudo ao redor do modelo que o transforma em agent — tools disponíveis, system prompt, gestão da janela de contexto, permissões e hooks. Diferenças de comportamento entre dois agentes com o **mesmo modelo subjacente** quase sempre vêm do harness, não do modelo. *Harness Engineering* é o subconjunto de **Context Engineering** que usa os pontos de configuração do harness para gerenciar deliberadamente a janela de contexto de agentes de codificação (Context Engineering ⊃ Prompt Engineering + Harness Engineering).

Esta skill consolida heurísticas de mercado (2026) — práticas de Matt Pocock (AI Hero / `mattpocock/skills`) e o conceito de "harness engineering" (HumanLayer) — para diagnóstico de comportamento de agent, poda de instrução acumulada e minimalismo de arquivos de instrução (`AGENTS.md`/`CLAUDE.md`/adapters).

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao investigar comportamento inesperado de um agent/specialist (antes de suspeitar do modelo, auditar tools/system-prompt/permissões/hooks ativos).
- Ao perceber degradação de qualidade em sessão longa (respostas genéricas, esquecimento de instrução, contradição) — avaliar reset de sessão.
- Ao auditar `.github/agents/*.agent.md`, `.github/instructions/*.instructions.md` ou `AGENTS.md`/`CLAUDE.md` de projetos-alvo quanto a minimalismo e Progressive Disclosure.
- Ao desenhar um novo `SKILL.md` — para garantir triggers claros, escopo mínimo e poda de conteúdo redundante.
- Ao avaliar se um workflow deveria rodar em modo autônomo/desatendido (loop de execução baseado em estado em disco).

### ❌ Quando NÃO Usar
- Para avaliar se a **resposta do modelo** está correta/factual — isso é `agent-evals-lab` (métricas de faithfulness, hallucination, tool correctness).
- Para estruturar o prompt de uma tarefa específica no formato `<task>/<context>/<constraints>/<output_format>` — isso é `prompt-engineering-patterns`.
- Para o payload/portabilidade de handoff entre agents — isso é `handoff-governance`.

---

## 2) Diretrizes Operacionais e Processo Canônico

### 2.1) Diagnóstico Harness-vs-Modelo (Passo 0 obrigatório antes de culpar o modelo)

Antes de concluir "o modelo alucinou" ou "o modelo se recusou", verifique nesta ordem:

1. **Tools ativas**: a tool necessária estava de fato declarada em `tools:`/disponível na sessão (R-024 Least-Tools)?
2. **System prompt / instrução carregada**: o `AGENTS.md`/`CLAUDE.md`/instruction ativo contradiz ou sobrescreve silenciosamente a intenção do usuário?
3. **Permissões/hooks**: alguma permissão ou hook do harness bloqueou a ação (ex.: modo read-only, allowlist de MCP)?
4. **Gestão de contexto**: a sessão já ultrapassou a "zona inteligente" (§ 2.2) — o problema é volume de contexto, não capacidade do modelo?

Só depois de eliminar as 4 hipóteses acima é válido tratar o problema como limitação do modelo em si (candidato a Model Routing Signal, R-021).

### 2.2) Heurística da "Zona Inteligente" (~100k Tokens) e Reset de Sessão

- A confiabilidade prática de um LLM em tarefas de codificação degrada de forma não-linear (atenção escala aproximadamente quadraticamente com o número de tokens) — independente do tamanho anunciado da janela de contexto (mesmo 1M tokens).
- **Heurística objetiva**: trate ~100k tokens acumulados de contexto ativo (histórico + arquivos + tool outputs) como o limiar prático de "zona inteligente"; além disso, a sessão entra em "zona burra" — respostas mais genéricas, esquecimento de restrições anteriores, contradição.
- **Ação recomendada ao aproximar do limiar**: preferir **sessão curta com reset de contexto limpo** a compactação indefinida do histórico. Use a skill `handoff-governance` (payload sucinto e portátil) para transferir apenas o essencial para a próxima sessão/agent, em vez de arrastar o histórico bruto.
- **System prompt deve ser mínimo**: um `AGENTS.md`/instruction volumoso consome o orçamento de "zona inteligente" antes mesmo do trabalho útil começar — ver checklist de minimalismo (§ 2.3).

### 2.3) Minimalismo e Progressive Disclosure em Arquivos de Instrução

Ao auditar ou criar `AGENTS.md`/`CLAUDE.md`/`*.instructions.md`, aplique o critério de minimalismo no arquivo-raiz:

| Conteúdo | Pertence ao arquivo-raiz? |
|---|---|
| Descrição do projeto em 1 frase | ✅ Sim |
| Gerenciador de pacotes/build (se não-padrão) | ✅ Sim |
| Comandos de build/test/typecheck não-óbvios | ✅ Sim |
| Regra verdadeiramente aplicável a **toda** tarefa | ✅ Sim |
| Convenção específica de uma linguagem/módulo | ❌ Não — arquivo separado linkado (progressive disclosure) |
| Exemplo de código extenso (> 8 linhas, R-026) | ❌ Não — `snippets/`/`templates/` referenciado por caminho |
| Regra usada raramente ou só por 1 sub-domínio | ❌ Não — adapter específico (`.github/instructions/<stack>.instructions.md`) |

**Processo de auditoria de poda ("Delete e Observe")**: quando um agent apresentar comportamento inconsistente ou lento e a causa não for óbvia, teste a hipótese de bloat de contexto: identifique instruções redundantes/vagas/obsoletas no arquivo ativo, proponha remoção cirúrgica (nunca silenciosa — declarar o diff) e observe se o comportamento normaliza antes de reconstruir incrementalmente. Nunca remover regra normativa (R-xxx) sem aprovação humana explícita (`ask_questions`) — esta técnica aplica-se a bloat acumulado (exemplos redundantes, repetição entre camadas, instrução vaga), não a guardrails de segurança/governança.

### 2.4) Modo de Execução Autônoma Assistida por Estado em Disco (Ralph Loop)

Para tarefas longas e bem delimitadas com critério de saída objetivo (ex.: implementar lista de itens já decompostos em `[S]`/`[P]` por `@feature-planner`, ou aplicar um lote de correções já aprovado), é um padrão de mercado válido operar em loop: ler o estado pendente de um artefato em disco (ex.: checklist `.md`), implementar o próximo item, validar (testes/lint), registrar o item como concluído e repetir até o estado ficar vazio ou o Circuit Breaker (R-050.2 / `handoff-governance` § 2.4) disparar.

- **Pré-requisitos obrigatórios antes de habilitar este modo**: plano já aprovado (R-031), critério de saída objetivo declarado, e teto de tentativas por item (`MAX_RETRIES_PER_STEP`, já normatizado em `handoff-governance` § 2.4) para evitar consumo descontrolado de créditos.
- **Não é um Workflow Canônico adicional** (R-050) — é uma **técnica de execução** aplicável dentro de `WORKFLOW-REFACTORING`, `WORKFLOW-BUG-FIX` ou `WORKFLOW-FEATURE-DEVELOPMENT` já existentes, quando o plano tiver múltiplos itens homogêneos e independentes.

---

## 3) Padrões Canônicos com Exemplos Contrastantes

### Padrão: Diagnóstico Antes de Escalar Modelo

#### ❌ Anti-padrão (Incorreto)
Observar que o agent não editou um arquivo e concluir "o modelo é fraco, preciso trocar para um modelo mais caro" (R-021) sem antes verificar se a tool de edição estava sequer disponível na sessão ou se uma permissão/hook bloqueou a ação.

#### ✅ Padrão Canônico (Correto)
Seguir o Diagnóstico Harness-vs-Modelo (§ 2.1): confirmar tools/permissões/instrução/volume de contexto primeiro; só then tratar como limitação real de capacidade do modelo.

---

## 4) Checklist de Auto-Verificação

- [ ] Ao investigar comportamento anômalo, as 4 hipóteses de harness (tools, instrução, permissões, contexto) foram descartadas antes de suspeitar do modelo.
- [ ] Sessões longas foram avaliadas contra a heurística de ~100k tokens antes de compactar indefinidamente o histórico.
- [ ] Arquivo de instrução auditado segue o critério de minimalismo de raiz + progressive disclosure (§ 2.3).
- [ ] Nenhuma remoção de regra normativa (R-xxx) foi feita sem `ask_questions` explícito.
- [ ] Modo de execução autônoma (§ 2.4), se usado, tem critério de saída objetivo e teto de tentativas declarado.

---

## 5) Consumidores Mapeados e Integrações

| Consumidor | Papel na Relação | Momento de Uso |
|---|---|---|
| `@agent-router` | Diagnóstico rápido de deriva/degradação antes de re-rotear | Suspeita de comportamento anômalo de agent ativo |
| `@agent-auditor` | Auditoria de minimalismo/bloat em agents/skills/instructions | `WORKFLOW-GOVERNANCE-MAINTENANCE` |
| `@governance-maintainer` | Poda cirúrgica de instrução redundante identificada | Execução da remediação aprovada |
| `@tech-solution-architect` | Decisão sobre uso de modo de execução autônoma (§ 2.4) | Blueprint de tarefas longas homogêneas |
| `agent-evals-lab` (skill) | Separar métricas de "qualidade do harness" vs "qualidade do modelo" | Desenho de suíte de evals |

---

## 6) Referências e Documentação Conexa

- `CLAUDE.md` § R-061 — regra normativa de Diagnóstico de Harness e Poda Anti-Bloat.
- `.github/skills/context-mode/SKILL.md` — gestão operacional de janela de contexto no dia a dia.
- `.github/skills/agent-evals-lab/SKILL.md` — separação de métricas harness vs. modelo.
- `.github/skills/prompt-engineering-patterns/SKILL.md` — estruturação do prompt de tarefa (fronteira distinta).
- `.github/skills/handoff-governance/SKILL.md` — payload portátil de handoff entre sessões/agents.
- Matt Pocock, AI Coding Dictionary — verbete "Harness": https://www.aihero.dev/ai-coding-dictionary/harness
- Matt Pocock, "A Complete Guide to AGENTS.md": https://www.aihero.dev/a-complete-guide-to-agents-md
- Matt Pocock, `mattpocock/skills` (repositório open-source de skills): https://github.com/mattpocock/skills
- HumanLayer, "Skill Issue: Harness Engineering for Coding Agents": https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents

