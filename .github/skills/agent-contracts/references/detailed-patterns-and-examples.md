# Agent Contracts — Padrões Detalhados, Schemas e Exemplos

## 1) Exemplo Completo de Contrato YAML (`test-implementation`)

```yaml
# Exemplo de contrato — agent test-implementation

entrada_minima:
  obrigatorio:
    - estrategia: "matriz de cenários do test-strategy"
    - escopo: "lista de arquivos/classes a testar"
    - stack: "backend | frontend | fullstack"
  opcional:
    - framework: "junit5 | jasmine | vitest | pytest"
    - conversa_anterior: "referência a plano ou bug-triage"

saida_esperada:
  formato: markdown
  secoes:
    - resultado: "X testes implementados (Y unitários, Z integração/E2E)"
    - cobertura: "XX% linhas, XX% ramos"
    - status: "SUCESSO | BLOQUEANTE"
    - evidencias: "lista de arquivos criados/editados"
    - bloqueantes: "causa + local + ação sugerida (formato 3 linhas)"

nao_escopo:
  - alterar lógica de negócio (reportar bug, não corrigir)
  - definir estratégia de testes (usar @test-strategy antes)
  - ignorar testes falhando
  - instalar dependências sem confirmação

criterios_de_evidencia:
  - caminhos dos arquivos criados/editados
  - comando de coverage executado e resultado
  - link para relatório de cobertura gerado
```

## 7) Context Engineering por Agent (Detalhamento)

Todo agent deve seguir política de context assembly para otimizar custo, latência e qualidade:

**Estrutura XML canônica de system prompt** (Anthropic 2025):

```
<instructions>
  Regras operacionais e não-escopo do agent
</instructions>
<context>
  Documentos de referência e estado atual do repositório
</context>
<examples>
  Exemplos few-shot de entrada → saída esperada (se aplicável)
</examples>
<input>
  {solicitação_do_usuário}
</input>
```

**Política de prompt caching** — conteúdo estático deve preceder o variável:

| Ordem | Tipo | Exemplo |
|---|---|---|
| 1º (mais cacheável) | System instructions fixas | Regras do agent, não-escopo |
| 2º | Tools definitions | Lista de tools com schemas |
| 3º | Few-shot examples | Casos canônicos de I/O |
| 4º (menos cacheável) | User message | Solicitação atual |

**Context budget máximo por tier de agent:**

| Tier | Budget máximo | Justificativa |
|---|---|---|
| Roteamento (router, triagem) | 8K tokens | Decisão rápida, contexto mínimo |
| Análise / pesquisa | 32K tokens | Contexto amplo do repositório |
| Implementação | 64K tokens | Arquivos + histórico + decisões |

**Regra mínima**: conteúdo estático deve sempre preceder conteúdo variável — habilita prompt caching nativo dos providers (redução de custo de até 90%, latência de até 85% conforme Anthropic 2025).

---

## 10) Gestão de Modelos em Cadeias de Subagent (Cost-Tier Ceiling)

### Problema de Mercado (confirmado 2026)

O `model:` declarado no frontmatter de um `.agent.md` **é respeitado** pela plataforma (VS Code Copilot Chat) quando o agent é invocado — seja diretamente pelo picker, seja via `run_subagent`/`@agent`. Isso está documentado oficialmente: *"Custom agents can specify their own model, tools, and instructions. When used as a subagent, these settings override the defaults inherited from the main session."* (VS Code Docs, "Subagents in Visual Studio Code").

**Porém existe um teto de custo (cost-tier ceiling) que a plataforma aplica de forma independente e não documentada com clareza:** um subagent **nunca** pode resolver para um modelo com multiplicador de custo **maior** do que o modelo que está processando o turno/sessão que iniciou a cadeia de delegação. Se o `model:` do subagent (ou o parâmetro explícito passado no `run_subagent`) exceder esse teto, a plataforma faz **downgrade silencioso** para o modelo do turno pai — sem erro visível na maioria dos casos (builds mais recentes já expõem um erro explícito: `"Requested model 'X' exceeds the current model's cost tier"`).

> **Motivo documentado**: prevenir abuso — impedir que um modelo gratuito/barato dispare, via subagents, cadeias de execução em modelos caros sem custo adicional ao usuário (rate-limit e billing são ancorados no request do turno pai, não nos subagents).

### Prioridade de Resolução de Modelo (oficial, 3 níveis — dentro do teto acima)

| Prioridade | Fonte | Observação |
|---|---|---|
| 1 (mais alta) | Parâmetro explícito de modelo passado na própria invocação do `run_subagent` (linguagem natural: *"invoque X com o modelo Gemini 3.8 Flash"*) | Único mecanismo de **reforço ativo** disponível para o agent chamador |
| 2 | `model:` no frontmatter do `.agent.md` do subagent — aceita nome único **ou lista priorizada** (`["Gemini 3.8 Flash", "GPT-5.1"]`) para fallback em caso de indisponibilidade | O que este projeto já declara em todo agent |
| 3 (fallback) | Modelo da conversa pai (sessão) | Aplicado quando 1 e 2 falham/excedem o teto |

**Nenhuma das 3 prioridades acima escapa do cost-tier ceiling.** Mesmo a prioridade 1 (explícita) é descartada se exceder o multiplicador do turno pai.

### Por que "Auto" é o principal risco (não apenas um detalhe)

O modo `Auto` do model picker resolve, **a cada turno**, para um modelo real (faixa 0×–1×: GPT-5 mini, GPT-4.1, Sonnet 4, Sonnet 3.5, etc.) com base em disponibilidade/saúde do sistema — **não** na complexidade da tarefa. Se a cota de requests premium do usuário se esgota, `Auto` **sempre** cai para um modelo 0×. Isso significa que o teto de custo da cadeia inteira de subagents fica **não determinístico por turno** — o mesmo fluxo `@agent-router → security-reviewer` pode funcionar corretamente em um turno (Auto resolveu para Sonnet 4, 1×) e silenciosamente rebaixar `security-reviewer` (declarado `Gemini 3.8 Flash`, 1×) em outro turno (Auto resolveu para GPT-5 mini, 0×).

### Mitigação Obrigatória (checklist — nenhuma resolve tecnicamente o teto, apenas evitam cair nele)

- [ ] **Nunca iniciar o fluxo `@agent-router` com `Auto` selecionado.** Selecionar manualmente, antes do primeiro turno, um modelo cujo tier ≥ o maior tier usado por qualquer agent do catálogo que possa ser alcançado na cadeia de roteamento (neste projeto: `Gemini 3.8 Flash`, 1×).
- [ ] Verificar que `chat.customAgentInSubagent.enabled` está habilitado nas configurações do VS Code — sem essa flag, agents customizados podem nem ser honrados como subagents (comportamento gated desde a v1.109).
- [ ] Ao criar/revisar um agent que delegará para outro de tier mais alto via `run_subagent`, instruir explicitamente no corpo do agent chamador para **solicitar o modelo por nome na própria invocação** (prioridade 1 da tabela acima) — reforço, não substituto do `model:` do subagent.
- [ ] Preferir `model:` como **lista priorizada** (ex.: `["Gemini 3.8 Flash", "Claude Sonnet 4.5"]`) em vez de string única, quando o agent tiver alternativas aceitáveis — evita fallback direto ao modelo do turno pai por indisponibilidade pontual do modelo primário.

### Model Gate via `ask_questions` — Tentado e Confirmado Inviável (2026-09-01)

Este projeto tentou responder "dá para automatizar isso com uma trava ativa, em vez de só documentar?" implementando um Model Gate em `agent-router.agent.md` (v1.6.0/v1.7.0): comparar o tier do modelo declarado para o agent-alvo (`catalog.yaml`) contra o tier "da sessão atual", bloqueando via `ask_questions` em caso de mismatch. **Testado 2× em produção real e removido (v1.8.0) — a abordagem é tecnicamente inviável, não apenas mal instruída.**

**Causa raiz confirmada por pesquisa (não é bug de prompt, é ausência de dado):**

1. **LLMs não têm acesso confiável a "qual modelo está realmente me executando agora".** Identidade de modelo só existe se injetada explicitamente no system prompt pela plataforma — o nome/versão é atribuído *depois* do treino, não aprendido durante ele. Um usuário documentou tentando forçar essa informação do Copilot: *"recusou-se a responder, alegou que era segredo... disse que estava além do seu conhecimento"* (GitHub Community Discussion #168899, jan/2026).
2. **VS Code Copilot Chat não injeta essa informação para custom agents.** Não existe tool/API pública que exponha "modelo real de execução desta invocação" a um `.agent.md`. A única forma documentada de descobrir é via debug log/trace de rede da extensão — inacessível ao próprio modelo.
3. **`ask_questions` não altera o picker de modelo da UI.** É um canal de texto para coletar preferência do usuário; a troca real do modelo exige clique manual no dropdown — fora do loop de tool-calling do agent.
4. **Mesmo o canal de maior prioridade (parâmetro explícito no `run_subagent`) não é uma API garantida.** `microsoft/vscode#298380` ("Allow runSubagent tool to specify a language model") confirma que suporte formal e estruturado a esse parâmetro no schema da tool é **feature request ainda aberta** em 2026 — hoje funciona apenas como interpretação de linguagem natural pelo modelo (melhor esforço, não determinístico).
5. **Evidência empírica reforça (mas não é a causa principal)**: em Haiku 4.5, o Gate nunca disparou (router ignorou a lógica condicional). Após upgrade para Gemini 3.8 Flash, o Gate **ainda** não disparou — confirmando que o problema não era tier/instruction-following, era ausência estrutural do dado necessário para a comparação.

**O que substitui o Gate (v1.8.0 — "Model Awareness", best-effort, honesto sobre suas limitações):**

- Router menciona o modelo declarado do agent-alvo (`catalog.yaml`) na própria frase de invocação do `run_subagent` — reforça a prioridade 1 de resolução, mas não garante nem verifica.
- Responsabilidade de garantir tier ≥ maior tier do catálogo antes do 1º turno é **explicitamente do usuário**, documentada, **não enforçável pelo agent**.

**Lição para novos agents**: se a lógica de um agent depender de "saber em qual modelo estou rodando" ou "qual modelo está rodando outro componente da cadeia", **pare e valide se esse dado existe antes de prometer enforcement** — reforçar o texto da instrução não resolve ausência de dado, por mais alto que seja o tier do modelo usado.

### Referências

- VS Code Docs (oficial), "Subagents in Visual Studio Code" — https://code.visualstudio.com/docs/agents/run/subagents — seção "Select the model for a subagent".
- VS Code Docs (oficial), "AI settings reference" — https://code.visualstudio.com/docs/agents/reference/ai-settings — `chat.agentFilesLocations`, `chat.exploreAgent.defaultModel`.
- VS Code Release Notes, "January 2026 (v1.109)" — https://code.visualstudio.com/updates/v1_109 — `chat.customAgentInSubagent.enabled`, `user-invocable`, `disable-model-invocation`.
- GitHub Community Discussion #191450, "Custom subagent model in VS Code Copilot seems to fall back to parent model" — confirma prioridade de resolução e comportamento de fallback silencioso.
- microsoft/vscode#275855, #307572, #296111 — feature requests em aberto (2026) para override de modelo por invocação de subagent, confirmando que o teto de custo **não** tem opt-out suportado atualmente.
- github/copilot-cli#2758 — feature request equivalente na CLI, mesmo mecanismo subjacente (cost-multiplier guard).
- powerofbi.org, "How Initial Model Selection Affects Subagents in GitHub Copilot" (mar/2026) — análise detalhada do teto de multiplicador.
- GitHub Community Discussion #168899, "Feedback on Auto model selection for vscode copilot agent mode" (jan/2026) — evidência de que o Copilot se recusa/não sabe informar qual modelo está de fato executando a sessão.
- eval.16x.engineer, "The Identity Crisis: Why LLMs Don't Know Who They Are" — explica por que identidade de modelo não é conhecimento nativo do LLM, apenas configuração de system prompt.
- microsoft/vscode#298380, "Allow runSubagent tool to specify a language model" — confirma que suporte estruturado a parâmetro de modelo explícito no `runSubagent` é feature request aberta, não API garantida.
- VS Code Docs (oficial), "Custom agents in VS Code" — https://code.visualstudio.com/docs/agent-customization/custom-agents — frontmatter `handoffs.model` (mecanismo nativo alternativo, baseado em botão de UI, não em texto/`ask_questions`).
- Visual Studio Magazine, "Why Copilot's Auto Mode for AI Models Ignores Your Actual Task" (fev/2026) — comportamento do `Auto` sob esgotamento de cota.

## 6) Limites de Delegação e Execução (Detalhamento)

Todo agent pode declarar limites opcionais de execução para prevenir loops e recursão não controlada:

```yaml
limites_execucao:
  max_delegation_depth: 2          # int — máx. camadas de delegação antes de parar
  max_execution_time_min: 15       # int — tempo máximo em minutos por execução
  allow_redelegation: false        # bool — agent receptor pode redelegar?
  circuit_breaker:
    trigger: "2 falhas consecutivas de tool"
    acao: "parar e reportar estado ao usuário"
```

**Defaults recomendados** (quando não declarado explicitamente):

| Campo | Default | Justificativa |
|---|---|---|
| `max_delegation_depth` | 3 | router → agent → subagent: profundidade típica |
| `max_execution_time_min` | 30 | margem para análise + implementação simples |
| `allow_redelegation` | false | previne loops por padrão |
| `circuit_breaker` | ativo após 3 falhas | interrompe antes de esgotar token budget |

**Anti-padrões:**
- ❌ Loop de delegação (A → B → A) sem circuit breaker declarado
- ❌ `allow_redelegation: true` sem `max_delegation_depth` (recursão irrestrita)
- ❌ Agent que chama ferramentas externas sem `max_execution_time_min`
