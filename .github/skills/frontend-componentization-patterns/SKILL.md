---
name: frontend-componentization-patterns
description: >-
  Padrões genéricos de componentização frontend para reduzir acoplamento, aumentar
  reutilização e melhorar manutenibilidade sem depender de framework específico.
tier: 2
category: process
triggers:
  - "componentização frontend"
  - "quebrar componente grande"
  - "design de componente reutilizável"
  - "contrato de componente"
  - "separação de responsabilidades UI"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/test-implementation-frontend/SKILL.md
tools: []
---

# Frontend Componentization Patterns

## Quando Usar

- Quando houver componentes monolíticos com múltiplas responsabilidades.
- Quando for necessário padronizar contratos de componente reutilizável.
- Quando a equipe precisar de critérios objetivos para modularização UI.

## Princípios de Componentização

| Princípio | Regra objetiva | Sinal de violação |
|---|---|---|
| Responsabilidade única | Cada componente deve resolver 1 capacidade principal da interface | Componente mistura layout, regra de negócio e orquestração externa |
| API explícita | Inputs, outputs e estados esperados devem ser claros e estáveis | Props/eventos implícitos ou side effects não documentados |
| Composição > herança | Reuso via composição de blocos pequenos e previsíveis | Cadeias longas de herança para variar comportamento visual |
| Fronteira de estado | Estado local de UI fica no componente; estado compartilhado sobe de nível | Estado duplicado em múltiplos filhos sem fonte única |
| Acessibilidade por padrão | Semântica, foco e navegação por teclado entram no contrato do componente | Acessibilidade tratada só após entrega funcional |

## Processo de Quebra de Componentes

1. Identificar responsabilidades misturadas no componente atual.
2. Definir fronteiras de estado (local, compartilhado, derivado).
3. Extrair subcomponentes por capacidade de interface.
4. Formalizar contrato de entrada/saída de cada subcomponente.
5. Validar consistência visual e comportamento com cenários críticos.

## Checklist Rápido

- [ ] Componente possui propósito único e nome orientado à capacidade.
- [ ] Contrato de entrada/saída está estável e previsível.
- [ ] Estado não está duplicado entre componentes irmãos.
- [ ] Reuso foi feito por composição, não por herança estrutural.
- [ ] Requisitos de acessibilidade foram incluídos no escopo funcional.

## Anti-padrões

- ❌ Criar “componente-coringa” com múltiplas variações acopladas.
- ❌ Embutir regra de domínio em componente puramente visual.
- ❌ Expor detalhes internos de estado como API pública.
- ❌ Usar estrutura de pasta por tipo técnico sem olhar coesão de feature.

## Referências

- Angular Style Guide: https://angular.dev/style-guide
- MDN Web Docs — Componentes e semântica HTML: https://developer.mozilla.org/
- W3C WAI-ARIA Overview: https://www.w3.org/WAI/standards-guidelines/aria/
