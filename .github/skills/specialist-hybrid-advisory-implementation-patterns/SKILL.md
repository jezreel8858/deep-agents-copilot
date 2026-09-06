---
name: specialist-hybrid-advisory-implementation-patterns
description: >
  Template canônico do "perfil híbrido" (Advisory + Implementação) para agents
  especialistas de stack técnico — critério de desambiguação de modo, formatos
  de saída de cada modo e checklist unificado "Antes de Analisar/Implementar",
  parametrizável por domínio técnico.
tier: 1
category: governance
triggers:
  - "perfil híbrido"
  - "modo advisory"
  - "modo implementação"
  - "specialist técnico"
  - "novo especialista de stack"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/angular/angular-router.agent.md
  - .github/agents/backend/spring-boot/spring-boot-router.agent.md
  - .github/agents/backend/spring-reactive/spring-reactive-router.agent.md
tools: []
---

# Specialist Hybrid Advisory + Implementation Patterns

## 0) Problema Resolvido

`angular`, `spring-boot` e `spring-reactive` (todos v2.0.0) compartilham ~90% da mesma estrutura de agent — variando apenas o domínio técnico. Sem esta skill, qualquer novo specialist híbrido (ex.: `python-django`, `nodejs-nestjs`, `react`) reescreveria do zero ~90 linhas de estrutura idêntica, com risco de pequenas divergências acumuladas entre agents que deveriam se comportar de forma consistente.

## 1) Modos de Operação (Tabela Canônica)

| Modo | Quando declarar | O que produz |
|---|---|---|
| **Advisory** | Pedido de análise/recomendação sem intenção explícita de codar agora (ex.: "avalie a arquitetura", "qual a melhor abordagem para X") | Relatório estruturado (§2) — nunca escreve código de aplicação |
| **Implementação** | Pedido explícito de feature nova ou correção de bug, com testing-first inegociável | Código + testes + relatório operacional compacto (§3) |

**Critério de desambiguação (frase padrão a adaptar por domínio):** se a solicitação não deixar claro se é análise ou implementação, usar `ask_questions` com a pergunta: *"Você quer uma análise/recomendação técnica (Advisory) ou a implementação direta da mudança (Implementação, testing-first)?"* — nunca inferir o modo (R-027).

## 2) Formato de Saída — Modo Advisory

```markdown
## Resumo
<1-3 linhas do que foi avaliado>

## Escopo
<o que foi analisado>

## Não-Escopo
<o que NÃO foi avaliado nesta análise>

## Entradas Consideradas
<arquivos/documentos/contexto usado>

## Análise por Pilar
| Pilar | Achado | Risco | Recomendação |
|---|---|---|---|
| <ex.: performance> | ... | ... | ... |
| <ex.: segurança> | ... | ... | ... |

## Riscos
<riscos técnicos identificados>

## Recomendação
<ação objetiva recomendada>

## Handoff
<próximo agent sugerido, se aplicável>

## Confiança
<score 0-1 + justificativa — ver `confidence-fallback-policy`>
```

## 3) Formato de Saída — Modo Implementação

```markdown
## Resultado
<o que foi implementado, em 1-2 linhas>

## Evidências
<arquivos criados/editados, caminhos completos>

## Testes Executados
<comando de teste rodado + resultado (SUCESSO/FALHA) + cobertura se aplicável>

## Validações
- [ ] Testing-first respeitado (teste escrito/ajustado antes ou junto da implementação)
- [ ] `get_errors` executado no(s) arquivo(s) editado(s)
- [ ] Convenções do adapter de stack aplicadas (ex.: `*-frontend.instructions.md`, `*-backend.instructions.md`)

## Próximo Passo Mínimo
<ação objetiva para avançar, se houver pendência>
```

## 4) Regra "Testing-First Inegociável" (Modo Implementação)

Toda implementação de feature/bugfix no modo Implementação **deve** ser acompanhada de teste correspondente, usando a ferramenta de teste do domínio:

| Domínio | Ferramenta de teste |
|---|---|
| Angular | Vitest (novo padrão) ou Jasmine/Karma (legado) |
| Spring Boot | JUnit 5 + Mockito |
| Spring WebFlux/Reactor | StepVerifier + WebTestClient |
| **Futuro domínio** | Declarar aqui a ferramenta padrão antes de operar em modo Implementação |

**Regra de ouro:** nenhuma implementação é reportada como concluída sem evidência de teste executado (comando + resultado) no bloco "Testes Executados" do Formato de Saída (§3).

## 4.1) Separação de Papéis: Mapeamento Estrutural vs. Especialização de Domínio (R-045 / RNF-004)

- **Modo Advisory é estritamente analítico (read-only)**: specialists NUNCA executam `run_in_terminal` em modo Advisory. O uso de terminal é restrito exclusivamente ao modo Implementação para execução de testes (testing-first) e linter.
- **Exclusividade do `@code-knowledge-graph`**: o CLI `@optave/codegraph` e a extração determinística de chamadas, blast radius, ciclos e dependências pertencem com exclusividade ao `@code-knowledge-graph`.
- **Proibição de usurpação de papel**: specialists NUNCA executam comandos do CLI `codegraph` diretamente nem realizam varreduras exploratórias de diretórios (`list_dir`, `read_dir`) para mapear arquitetura ou dependências.
- **Fluxo de delegação obrigatório**: quando a análise exigir relações entre camadas, fluxo de chamadas ou dependências de módulos/serviços, o specialist DEVE invocar `@code-knowledge-graph` via `run_subagent(agentName: 'code-knowledge-graph', ...)`. O papel do specialist é interpretar tecnicamente o resultado do grafo sob a ótica das melhores práticas do seu framework (Angular, Spring, etc.).

## 5) Checklist Unificado — Antes de Analisar/Implementar

- [ ] Modo desambiguado explicitamente (Advisory vs. Implementação) — via pergunta direta ou intenção inequívoca do pedido.
- [ ] Adapter de stack específico do projeto consultado, se existir (`.github/instructions/<projeto>-<stack>.instructions.md`).
- [ ] Skill de análise do domínio consultada (ex.: `spring-boot-backend-patterns`) no modo Advisory.
- [ ] Skill de implementação do domínio consultada (ex.: `spring-boot-implementation-patterns`) no modo Implementação.
- [ ] Placeholder de pilar técnico do domínio preenchido (ex.: performance, segurança, observabilidade, compatibilidade de versão).
- [ ] Testing-first aplicado sem exceção no modo Implementação.

## 6) Anti-padrões

- ❌ Implementar código sem antes desambiguar o modo (risco de agir fora da intenção real do usuário — viola R-027).
- ❌ Modo Implementação sem teste correspondente (viola testing-first inegociável).
- ❌ Reescrever a estrutura completa de Formato de Saída por domínio, em vez de reutilizar os templates desta skill com o placeholder de pilar técnico.
- ❌ Confundir Advisory com Implementação parcial (ex.: escrever trecho de código "de exemplo" dentro de um relatório Advisory — Advisory nunca escreve código de aplicação).

## 7) Consumidores Mapeados

- `angular`, `spring-boot`, `spring-reactive` — os 3 specialists híbridos atuais.
- **Futuro:** qualquer novo specialist híbrido (ex.: `python-django`, `nodejs-nestjs`, `react`) herda o padrão via `@governance-factory`, que deve referenciar esta skill como template adicional ao criar novos specialists de stack.

## 8) Referências

- `CLAUDE.md` — R-027 (Clarificação Obrigatória), R-029 (Postura Senior Engineer).
- `.github/skills/agent-contracts/SKILL.md` §8 — Camada 2 de Formato de Saída por perfil ("Especialista de Recomendação").
- `.github/skills/confidence-fallback-policy/SKILL.md` — escala de confiança usada no bloco Advisory.

