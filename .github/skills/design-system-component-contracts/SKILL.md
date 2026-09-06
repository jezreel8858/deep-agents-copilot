---
name: design-system-component-contracts
description: >-
  Diretrizes enterprise para definir e evoluir contratos de componentes em design systems,
  com governança de breaking change, compatibilidade retroativa, acessibilidade e semver.
tier: 2
category: governance
triggers:
  - "contrato de componente"
  - "design tokens e variantes"
  - "breaking change em biblioteca UI"
  - "versionamento semver de componentes"
  - "depreciação de API de componente"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/frontend/angular/angular-router.agent.md
tools: []
---

# Design System Component Contracts

## Quando usar

- Quando for necessário definir ou revisar API pública de componentes reutilizáveis.
- Quando houver mudança em `Inputs/Outputs`, estados, variantes ou tokens visuais.
- Quando a biblioteca de componentes precisar de regra objetiva para versionamento e depreciação.
- Quando o time precisar classificar mudanças como **breaking** ou **non-breaking**.

## Princípios

| Princípio | Diretriz objetiva | Critério verificável |
|---|---|---|
| Tokens como contrato | Cor, tipografia, espaçamento e elevação devem ser consumidos por design tokens versionados | Existe inventário de tokens com nome estável, fallback e histórico de mudança |
| API explícita de componente | `Inputs` e `Outputs` devem ser tipados, documentados e com comportamento previsível | Cada propriedade/evento possui tipo, valor padrão, obrigatoriedade e efeito descritos |
| Variantes e estados controlados | Variantes visuais e estados interativos devem ser finitos e auditáveis | Matriz de variantes/estados publicada (default, hover, focus, disabled, error etc.) |
| Compatibilidade retroativa por padrão | Mudanças devem preservar contratos existentes até janela formal de remoção | Alterações incompatíveis só entram com major + plano de migração |
| Acessibilidade como requisito de contrato | Componente deve atender critérios WCAG/WAI-ARIA relevantes ao seu papel | Nome acessível, foco visível, navegação por teclado e roles/aria validados |
| Documentação como artefato de release | Toda mudança de contrato deve atualizar documentação e changelog no mesmo ciclo | Release bloqueada se API docs, notas de versão e impacto ao consumidor não estiverem atualizados |

## Checklist (critérios verificáveis)

- [ ] Design tokens alterados possuem impacto mapeado (consumidores, fallback, risco visual).
- [ ] Matriz de variantes/estados foi revisada e mantém consistência comportamental.
- [ ] Contrato de `Inputs/Outputs` inclui tipo, default, obrigatoriedade e compatibilidade.
- [ ] Mudança foi classificada em semver (`major`, `minor`, `patch`) com justificativa.
- [ ] Política de depreciação foi aplicada (aviso, janela de suporte, alternativa de migração).
- [ ] Critérios de breaking change foram validados antes de aprovar release.
- [ ] Requisitos de acessibilidade (WCAG/WAI-ARIA) foram checados com evidência objetiva.
- [ ] Documentação de API de componente e changelog foram atualizados na mesma entrega.

## Matriz de decisão: Breaking vs Non-Breaking

| Tipo de mudança | Classificação | SemVer recomendado | Exemplo típico | Ação obrigatória |
|---|---|---|---|---|
| Remover `Input`/`Output` público | Breaking | **major** | evento de seleção deixa de existir | Plano de migração + depreciação prévia |
| Alterar tipo/semântica de `Input` existente | Breaking | **major** | `size: string` passa a `size: number` | Guia de conversão e janela de adoção |
| Mudar valor default com impacto funcional | Breaking (na prática) | **major** | `disabled=false` passa para `true` | Nota de impacto + flag de transição |
| Adicionar nova variante opcional | Non-breaking | **minor** | variante `compact` adicional | Atualizar docs e exemplos |
| Adicionar `Input` opcional sem efeito colateral | Non-breaking | **minor** | `ariaLabel` opcional | Documentar uso e valor default |
| Correção interna sem alterar contrato público | Non-breaking | **patch** | ajuste de estilo interno sem mudança de API | Registrar no changelog técnico |
| Ajuste visual via token mantendo semântica | Geralmente non-breaking | **patch/minor** | refinamento de cor mantendo contraste e papel | Validar impacto de contraste e consistência |

## Política de depreciação (mínimo)

1. Marcar item como **deprecated** na documentação de API.
2. Informar alternativa suportada e prazo de remoção.
3. Garantir pelo menos 1 ciclo de release estável antes de remover.
4. Publicar changelog com impacto, risco e passo de migração.

## Anti-padrões

- ❌ Alterar API pública de componente sem classificar impacto semver.
- ❌ Quebrar compatibilidade por mudança de default sem aviso formal.
- ❌ Tratar acessibilidade como ajuste posterior fora do contrato.
- ❌ Introduzir variantes sem governança de tokens e estados.
- ❌ Publicar release sem atualizar documentação de API e política de depreciação.

## Referências oficiais

- Semantic Versioning 2.0.0: https://semver.org/
- W3C WCAG (overview): https://www.w3.org/WAI/standards-guidelines/wcag/
- W3C WAI-ARIA (overview): https://www.w3.org/WAI/standards-guidelines/aria/
- W3C Design Tokens Community Group: https://www.w3.org/community/design-tokens/
- Material Design — Design Tokens: https://m3.material.io/foundations/design-tokens/overview
- Material Design — Accessibility: https://m3.material.io/foundations/accessible-design/overview
- Angular Components (guidance aplicável): https://angular.dev/guide/components
- Angular Style Guide (guidance aplicável): https://angular.dev/style-guide

