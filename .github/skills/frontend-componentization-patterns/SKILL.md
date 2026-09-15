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
  - .github/skills/frontend-visual-feedback-loop/SKILL.md
tools: []
---

# Frontend Componentization Patterns

## Quando Usar

- Quando houver componentes monolíticos com múltiplas responsabilidades.
- Quando for necessário padronizar contratos de componente reutilizável.
- Quando a equipe precisar de critérios objetivos para modularização UI.
- **Antes de criar qualquer componente/elemento visual novo** — para decidir se já existe equivalente reutilizável no projeto.

## Reuso-First: Antes de Criar Componente Novo

Regra objetiva, aplicável a qualquer stack com camada de UI: **buscar antes de construir**.

1. Inventariar `shared/components/` e seu barrel/index — verificar se já existe componente cobrindo a mesma capacidade (card, filtro, badge, diálogo, form field, empty state, avatar).
2. Consultar a documentação interna de design system do projeto quando existir (referenciada pelo adapter local `.github/instructions/local/<projeto>.instructions.md` — ex.: `docs/*componentes*`, `docs/*padrao*`, `STYLEGUIDE.md`).
3. Se existir componente/pattern equivalente: ler a definição TypeScript (`.ts`) para confirmar inputs/outputs reais e reaproveitar, nunca recriar em HTML/CSS customizado (Smell 2.19 / Smell 2.21).
4. **Protocolo "Canonical Sibling First"**: antes de criar qualquer tela ou diálogo novo, inspecionar um componente irmão homologado no repositório para mapear tags, grids de formulário e classes utilitárias de scroll.
5. Se não existir componente equivalente: implementar o novo elemento e avaliar explicitamente se deve ser promovido para `shared/` (critério: será reutilizado em 2+ telas).
6. Se o projeto tiver script de auditoria de padrão de UI (ex.: `npm run <lint-de-padrao-ui>`), executá-lo antes de reportar conclusão.

## Princípios de Componentização

| Princípio | Regra objetiva | Sinal de violação |
|---|---|---|
| Responsabilidade única | Cada componente deve resolver 1 capacidade principal da interface | Componente mistura layout, regra de negócio e orquestração externa |
| API explícita | Inputs, outputs e estados esperados devem ser claros e estáveis | Props/eventos implícitos ou side effects não documentados |
| Composição > herança | Reuso via composição de blocos pequenos e previsíveis | Cadeias longas de herança para variar comportamento visual |
| Fronteira de estado | Estado local de UI fica no componente; estado compartilhado sobe de nível | Estado duplicado em múltiplos filhos sem fonte única |
| Acessibilidade por padrão | Semântica, foco e navegação por teclado entram no contrato do componente | Acessibilidade tratada só após entrega funcional |
| Reuso antes de criação (Reuse-First) | Buscar componente/design system compartilhado equivalente antes de criar HTML/CSS customizado | Novo card/filtro/badge/diálogo criado sem consultar `shared/` ou docs internos do projeto |

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
- [ ] Buscou por componente/padrão equivalente em `shared/`/design system do projeto antes de criar um novo (Smell 2.19).

## Anti-padrões

- ❌ Criar “componente-coringa” com múltiplas variações acopladas.
- ❌ Embutir regra de domínio em componente puramente visual.
- ❌ Expor detalhes internos de estado como API pública.
- ❌ Usar estrutura de pasta por tipo técnico sem olhar coesão de feature.
- ❌ Criar HTML/CSS customizado (cards, filtros, badges, diálogos) quando o projeto já possui componente compartilhado documentado para a mesma capacidade.

## Referências

- Angular Style Guide: https://angular.dev/style-guide
- MDN Web Docs — Componentes e semântica HTML: https://developer.mozilla.org/
- W3C WAI-ARIA Overview: https://www.w3.org/WAI/standards-guidelines/aria/
