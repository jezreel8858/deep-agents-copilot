---
name: prompt-engineering-patterns
description: >
  Catálogo de técnicas consolidadas de prompt engineering (2024-2026) para estruturar,
  refinar e detectar ambiguidade em prompts antes da execução — base de conhecimento
  do agent prompt-structuring (exceção R-041).
tier: 2
category: process
triggers:
  - "estruturar prompt"
  - "refinar prompt"
  - "detectar ambiguidade"
  - "prompt engineering"
  - "meta-prompting"
  - "chain-of-thought"
  - "few-shot"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/prompt-structuring.agent.md
tools: []
---

# Prompt Engineering Patterns

> Técnicas consolidadas para estruturar e refinar prompts antes da execução por outro agent, com base em pesquisa sobre otimização de prompt (APE, OPRO, DSPy) e guias oficiais (Anthropic, OpenAI).

## Quando Usar

- Ao estruturar um prompt recebido no formato canônico `<task>/<context>/<constraints>/<output_format>`.
- Ao decidir se um prompt está ambíguo o suficiente para justificar 1 pergunta de clarificação.
- Ao revisar (self-critique) um prompt já estruturado antes de retornar ao `agent-router`.

## Veredito de Pesquisa (consolidado — pesquisa real via Tavily, 2026-08-29)

Estruturar/refinar o prompt antes da execução **eleva a qualidade do output** — evidência real e citável:

- **APE** — Zhou et al., "Large Language Models Are Human-Level Prompt Engineers", arXiv:2211.01910 (ICLR 2022). Trata a instrução como programa e otimiza via busca sobre candidatos propostos por um LLM.
- **OPRO** — Yang et al., "Large Language Models as Optimizers", arXiv:2309.03409 (Google DeepMind, 2023).
- **DSPy** — Khattab et al. (Stanford Hazy Research). DSPy 3 adicionou o otimizador **GEPA** ("Reflective Prompt Evolution Can Outperform Reinforcement Learning", jul/2025) e suporte nativo a tool calls.
- **CLAMBER** (arXiv:2405.12063, 2024) — benchmark que taxonomiza ambiguidade (lexical, semântica, contradição) e testa esquemas de prompting para identificá-la.
- **"Knowing but Not Showing"** (arXiv:2605.25284, 2026) — achado crítico: **LLMs reconhecem ambiguidade mas raramente perguntam por clarificação por padrão**. Valida a necessidade de um mecanismo explícito/obrigatório em vez de depender do comportamento espontâneo do modelo.
- **Meta-prompting "Conductor-Model"** (IBM, TrueFoundry, 2026) — um LLM "condutor" decompõe a tarefa em subtarefas atribuídas a agents especialistas com instruções específicas — corresponde à arquitetura `agent-router` (condutor) → `prompt-structuring` (meta-prompt) → agent especialista.
- Frameworks de produção 2026 (LangGraph, CrewAI, Microsoft Agent Framework/AutoGen) suportam workflows baseados em grafo com transições explícitas e human-in-the-loop — compatível com o `routing-graph.yaml` já usado neste ecossistema.

**Atualização de nuance:** a análise anterior (sem busca real) recomendava cautela quanto a loops obrigatórios, citando o padrão "single-pass + 1 pergunta" como dominante. A evidência real agora **reforça** o design atual: como LLMs não perguntam por padrão mesmo reconhecendo ambiguidade (achado de 2026), um passo **mandatório e limitado** (R-041, máx. 5 iterações, saída antecipada) é uma salvaguarda estrutural justificada — não over-engineering — desde que o cap rígido seja mantido.

## Técnicas Obrigatórias (checklist de estruturação)

| Técnica | Quando aplicar |
|---|---|
| Role/persona framing | Domínio da tarefa exige enquadramento de especialidade |
| Chain-of-thought elicitation | Tarefas multi-etapas ou que exigem raciocínio explícito |
| Few-shot exemplar (1-3) | Formato de saída ambíguo ou pouco usual |
| Output format specification | Sempre — nunca deixar `<output_format>` vazio |
| Constraint extraction (não-escopo) | Sempre — extrair explicitamente o que NÃO deve ser feito |
| Task decomposition | Pedido com 2+ intenções simultâneas (ex.: "teste e refatore") |
| Self-critique final | Antes de encerrar qualquer iteração do loop |
| Instruction hierarchy | Nunca contrariar System > Developer > User (`CLAUDE.md` § 2) |

## Heurísticas Objetivas de Detecção de Ambiguidade

Considerar o prompt **incompleto** (justifica 1 pergunta) quando:
- [ ] Falta entidade/arquivo/módulo-alvo identificável.
- [ ] Falta critério de sucesso ou `output_format`.
- [ ] Duas ou mais intenções concorrentes sem ordem definida.
- [ ] Constraints conflitantes (ex.: "rápido" + "cobertura 100%") sem prioridade declarada.

Considerar o prompt **completo** (sair do loop) quando os 4 campos canônicos (`task`, `context`, `constraints`, `output_format`) puderem ser preenchidos sem inferência especulativa.

## Checklist

- [ ] `<task>` é uma frase objetiva e verificável.
- [ ] `<context>` cita artefatos/projeto ou declara "nenhum necessário".
- [ ] `<constraints>` inclui não-escopo explícito.
- [ ] `<output_format>` nunca fica implícito.
- [ ] Ambiguidade avaliada pelas heurísticas acima — não por julgamento subjetivo.
- [ ] Self-critique executado antes de encerrar a iteração.

## Escrever para Agentes (Writing-for-Agents vs. Task Prompts)

Ao redigir instruções persistentes para agentes (como arquivos de instrução de agentes, `.prompt.md` e `SKILL.md`), os princípios divergem dos prompts de tarefa efêmeros:

1. **Triggers Claros e Unívocos**: Agentes de roteamento e LLMs ativam skills baseando-se em gatilhos léxicos e semânticos. Evite termos genéricos que colidam com outras especialidades (ex.: use "migração de branch por abstração" em vez de "refatorar código").
2. **Steering Declarativo e Restrições Negativas**: Modelos agentic respondem melhor a limites explícitos de não-escopo (o que NÃO fazer) e contratos de entrada/saída padronizados do que a descrições prolixas de comportamento.
3. **Poda e Progressive Disclosure**: Documentos de instrução persistente devem ser compactos e orientados a índices/ponteiros. Conteúdo volumoso deve ser adiado para carregamento sob demanda (`context-mode`).
4. **Fronteira Arquitetural**:
   - **Prompt de Tarefa (Task Prompt)**: Escopo local, efêmero, focado na intenção do usuário corrente e na cadeia de raciocínio imediata (governado por esta skill `prompt-engineering-patterns`).
   - **Instrução de Harness (Persistent Instruction)**: Escopo global, duradouro, focado nas capacidades, ferramentas, permissões e boundaries do agente no ciclo de vida (governado por `harness-engineering-patterns`).

---

## Referências

- Zhou et al., "Large Language Models Are Human-Level Prompt Engineers" (APE), arXiv:2211.01910, ICLR 2022 — https://arxiv.org/abs/2211.01910
- Yang et al., "Large Language Models as Optimizers" (OPRO), arXiv:2309.03409, Google DeepMind, 2023 — https://arxiv.org/pdf/2309.03409
- Khattab et al., DSPy (Stanford Hazy Research) — https://github.com/stanfordnlp/dspy — GEPA optimizer, jul/2025
- CLAMBER Benchmark — taxonomia de ambiguidade, arXiv:2405.12063, 2024 — https://arxiv.org/html/2405.12063v2
- "Knowing but Not Showing: LLMs Recognize Ambiguity but Rarely Ask Clarifying Questions", arXiv:2605.25284, 2026 — https://arxiv.org/html/2605.25284v1
- "Conductor-Model Meta Prompting" — IBM (https://www.ibm.com/think/topics/meta-prompting) e TrueFoundry (https://www.truefoundry.com/glossary/meta-prompting)
- "The best AI agent frameworks in 2026" (LangGraph/CrewAI/AutoGen) — https://www.langchain.com/resources/ai-agent-frameworks
- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", 2022.
- [`.github/agents/prompt-structuring.agent.md`](../../agents/prompt-structuring.agent.md) — agent consumidor desta skill.
- `CLAUDE.md` § R-041 — exceção de loop controlado.

