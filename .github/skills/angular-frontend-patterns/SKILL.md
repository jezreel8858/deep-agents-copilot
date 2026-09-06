---
name: angular-frontend-patterns
description: >-
  Boas práticas e patterns de codificação Angular para componentes modernos,
  templates, reatividade, segurança e consistência arquitetural.
tier: 2
category: quality
triggers:
  - "boas práticas angular"
  - "padrões de componente angular"
  - "standalone angular"
  - "signals e rxjs"
  - "template binding angular"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/angular/angular-router.agent.md
tools: []
---

# Angular Frontend Patterns

> Esta skill cobre o modo **Advisory** (análise/recomendação, sem código). Para o modo **Implementação** (codificar feature/bugfix), ver [`angular-implementation-patterns`](../angular-implementation-patterns/SKILL.md).

## Quando Usar

- Quando for necessário revisar qualidade e consistência de código Angular.
- Quando houver decisão de padrão entre componentes standalone, template e estado.
- Quando precisar de baseline para recomendações sem implementar código.

## Padrões Recomendados

| Pilar | Diretriz | Evidência mínima |
|---|---|---|
| Estrutura de componentes | Preferir componentes pequenos, coesos e standalone quando viável | Declaração de imports explícitos e fronteiras claras por feature |
| Consistência de estilo | Aplicar convenções de naming e organização do style guide | Nomes de arquivos previsíveis e aderência intra-arquivo |
| Template e binding | Usar binding explícito e evitar lógica complexa no template | Expressões simples e leitura clara de fluxo de dados |
| Reatividade | Definir regra de convivência entre Signals e RxJS por caso de uso | Critérios documentados para estado local, derivado e assíncrono |
| Segurança | Priorizar sanitização padrão do Angular e evitar bypass sem justificativa | Mapeamento de contexts de segurança e pontos com risco de XSS |
| Performance | Avaliar impacto em CWV (LCP/INP/CLS) antes de mudanças estruturais | Meta de métrica e hipótese de ganho/perda por decisão |

## Checklist de Revisão Angular

- [ ] Há consistência de padrões dentro de cada arquivo e feature.
- [ ] Componentes possuem responsabilidade clara e limites de dependência.
- [ ] Template não concentra regra de negócio complexa.
- [ ] Estratégia reativa (Signals/RxJS) foi escolhida com critério explícito.
- [ ] Pontos de segurança sensíveis foram analisados (XSS, sanitização, trust bypass).
- [ ] Recomendações incluem impacto esperado em performance e manutenibilidade.

## Anti-padrões

- ❌ Misturar múltiplos estilos de organização sem critério no mesmo módulo.
- ❌ Usar bypass de segurança como padrão para acelerar entrega.
- ❌ Centralizar estado e efeitos de forma opaca em componentes de UI.
- ❌ Produzir recomendações Angular sem declarar versão e restrições do contexto.

## Referências

- Angular Coding Style Guide: https://angular.dev/style-guide
- Angular Components Guide: https://angular.dev/guide/components
- Angular Template Binding: https://angular.dev/guide/templates/binding
- Angular Security Guide: https://angular.dev/guide/security
- Web.dev Core Web Vitals: https://web.dev/vitals/

